#!/usr/bin/env python3
"""GovInfo MCP Server - FastMCP implementation.

The server exposes the GovInfo tools over two transports:

* **STDIO** (default) - for local MCP clients such as Claude Desktop, Cursor,
  or the VS Code MCP integration.
* **Streamable HTTP** - as a standalone Linux service. Import ``app`` for an
  ASGI deployment (``uvicorn app.server:app``) or set ``MCP_TRANSPORT=http``
  to let ``main()`` start the HTTP server directly.

Deployment environment variables
---------------------------------
``MCP_TRANSPORT``
    ``stdio`` (default) or ``http``.
``MCP_HOST`` / ``MCP_PORT``
    Bind address for the HTTP transport (defaults ``0.0.0.0`` / ``8775``).
``MCP_ALLOWED_HOSTS`` / ``MCP_ALLOWED_ORIGINS``
    Comma-separated allow-lists enabling Host/Origin request protection.
``MCP_CORS_ALLOW_ORIGINS``
    Comma-separated browser origins; enables CORS for browser-based clients.
``FASTMCP_STATELESS_HTTP``
    ``true`` for horizontally scaled deployments (no session affinity).
"""

from __future__ import annotations

from datetime import UTC, datetime
import os
from pathlib import Path
import sys
from typing import TYPE_CHECKING, Any

from dotenv import load_dotenv
from fastmcp import FastMCP
import httpx
from loguru import logger
import psutil
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse

from app import __version__
from app.tools import (
    collections_server,
    packages,
    published_server,
    related_server,
    search_server,
    statutes,
)

if TYPE_CHECKING:
    from starlette.applications import Starlette
    from starlette.requests import Request

load_dotenv()
# Configure logging
log_path = Path(__file__).parent / "logs" / "server.log"
log_path.parent.mkdir(exist_ok=True)
logger.add(log_path, rotation="1 MB", retention="1 day")

# Create main server instance with detailed instructions
mcp: FastMCP = FastMCP(
    "GovInfo",
    instructions="""This server provides access to the GovInfo API for searching and retrieving
    U.S. government documents including bills, laws, regulations, and other official publications.

    Available tool categories:
    - Collections: Browse and get details about document collections
    - Packages: Access specific documents and their content
    - Published: Find recently published documents by date
    - Related: Discover related documents and cross-references
    - Search: Full-text search across all government documents

    All tools require a GOVINFO_API_KEY environment variable to be set.
    Date formats should be YYYY-MM-DD. Collection codes include BILLS, PLAW, CFR, FR, and others.""",
)


@mcp.tool()
async def status() -> dict[str, Any]:
    """Check the status of the GovInfo MCP server.

    Returns:
        A dictionary containing server status, system metrics, API health, and available tools.

    """
    logger.info("Status check requested")

    # System info using psutil
    process = psutil.Process()
    process_start = datetime.fromtimestamp(process.create_time(), tz=UTC)

    # API health check
    api_health = await check_api_health()

    return {
        "status": "healthy" if api_health["is_healthy"] else "degraded",
        "service": "GovInfo MCP Server",
        "version": __version__,
        "timestamp": datetime.now(UTC).isoformat(),
        "system": {
            "uptime": str(datetime.now(UTC) - process_start).split(".")[0],
            "memory_mb": process.memory_info().rss / 1024 / 1024,
            "cpu_percent": process.cpu_percent(interval=0.1),
            "python_version": sys.version.split()[0],
        },
        "api": api_health,
    }


async def check_api_health() -> dict[str, Any]:
    """Check GovInfo API health.

    Returns:
        A dictionary containing API health status, including is_healthy flag,
        status message, response time (if successful), and error details (if failed).

    """
    api_key = os.getenv("GOVINFO_API_KEY")
    if not api_key:
        return {"is_healthy": False, "status": "no_api_key"}

    try:
        start = datetime.now(UTC)
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://api.govinfo.gov/collections",
                headers={"X-Api-Key": api_key},
                timeout=5.0,
            )
            response.raise_for_status()

        return {
            "is_healthy": True,
            "status": "connected",
            "response_time_ms": int((datetime.now(UTC) - start).total_seconds() * 1000),
        }
    except Exception as e:
        return {
            "is_healthy": False,
            "status": f"error: {type(e).__name__}",
            "error": str(e),
        }


def _register_tools() -> None:
    """Mount the focused tool servers under stable namespaces.

    FastMCP 4 replaced ``import_server`` with ``mount``. Mounting keeps a live
    link to each child server (unlike the v2 static snapshot) and prefixes the
    exposed tool names with the given namespace, e.g. ``collections_<tool>``.
    """
    mcp.mount(collections_server, namespace="collections")
    mcp.mount(packages, namespace="packages")
    mcp.mount(published_server, namespace="published")
    mcp.mount(related_server, namespace="related")
    mcp.mount(search_server, namespace="search")
    mcp.mount(statutes, namespace="statutes")
    logger.info("Mounted collections, packages, published, related, search, statutes")


def _csv_env(name: str) -> list[str]:
    """Return a comma-separated environment variable as a clean list.

    Returns:
        The non-empty, whitespace-stripped values from the variable.

    """
    return [value.strip() for value in os.getenv(name, "").split(",") if value.strip()]


def _env_flag(name: str) -> bool:
    """Return ``True`` when an environment variable is set to a truthy value.

    Returns:
        Whether the variable holds one of ``1``, ``true``, ``yes``, or ``on``.

    """
    return os.getenv(name, "").strip().lower() in {"1", "true", "yes", "on"}


@mcp.custom_route("/health", methods=["GET"])
def health_check(_request: Request) -> JSONResponse:
    """Liveness/readiness probe for load balancers and container health checks.

    Returns:
        A JSON response describing service health and version.

    """
    return JSONResponse({
        "status": "healthy",
        "service": "GovInfo MCP Server",
        "version": __version__,
    })


def build_http_app() -> Starlette:
    """Build the Streamable HTTP ASGI application.

    Returns:
        A Starlette ASGI application exposing the MCP endpoint at ``/mcp`` and
        the operational ``/health`` route.

    """
    allowed_hosts = _csv_env("MCP_ALLOWED_HOSTS")
    allowed_origins = _csv_env("MCP_ALLOWED_ORIGINS")
    cors_origins = _csv_env("MCP_CORS_ALLOW_ORIGINS")

    kwargs: dict[str, Any] = {
        "stateless_http": _env_flag("MCP_STATELESS_HTTP")
        or _env_flag("FASTMCP_STATELESS_HTTP"),
    }

    if cors_origins:
        kwargs["middleware"] = [
            Middleware(
                CORSMiddleware,
                allow_origins=cors_origins,
                allow_methods=["GET", "POST", "DELETE", "OPTIONS"],
                allow_headers=[
                    "mcp-protocol-version",
                    "mcp-session-id",
                    "Authorization",
                    "Content-Type",
                ],
                expose_headers=["mcp-session-id"],
            )
        ]

    if allowed_hosts or allowed_origins:
        kwargs["host_origin_protection"] = True
        kwargs["allowed_hosts"] = allowed_hosts or None
        kwargs["allowed_origins"] = allowed_origins or None

    return mcp.http_app(**kwargs)


# Register tools at import time so ``from app.server import mcp`` is ready to use
# for both the STDIO transport and the ASGI ``app`` below.
_register_tools()

# ASGI application for ``uvicorn app.server:app`` deployments.
app = build_http_app()


def main() -> None:
    """Run the GovInfo MCP server using the transport selected by the environment."""
    transport = os.getenv("MCP_TRANSPORT", "stdio").strip().lower()

    if transport in {"http", "streamable-http", "streamable_http"}:
        host = os.getenv("MCP_HOST", "0.0.0.0")
        port = int(os.getenv("MCP_PORT", "8775"))
        logger.info(
            f"Starting GovInfo MCP server over Streamable HTTP on {host}:{port}"
        )
        mcp.run(transport="http", host=host, port=port)
    else:
        logger.info("Starting GovInfo MCP server over STDIO")
        mcp.run()


if __name__ == "__main__":
    main()
