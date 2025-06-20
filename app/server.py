#!/usr/bin/env python3
"""GovInfo MCP Server - FastMCP Implementation."""

import asyncio
from datetime import UTC, datetime
import os
from pathlib import Path
import sys
from typing import Any

from dotenv import load_dotenv
from fastmcp import FastMCP
import httpx
from loguru import logger
import psutil

from app.tools import (
    collections_server,
    packages,
    published_server,
    related_server,
    search_server,
    statutes,
)

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
        "version": "0.1.0",
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


async def setup() -> None:
    """Set up the server by importing all tool servers."""
    logger.info("Setting up GovInfo MCP server")

    # Import all tool servers with descriptive prefixes
    await mcp.import_server("collections", collections_server)
    logger.info("Imported collections server tools")

    await mcp.import_server("packages", packages)
    logger.info("Imported packages server tools")

    await mcp.import_server("published", published_server)
    logger.info("Imported published server tools")

    await mcp.import_server("related", related_server)
    logger.info("Imported related server tools")

    await mcp.import_server("search", search_server)
    logger.info("Imported search server tools")

    await mcp.import_server("statutes", statutes)
    logger.info("Imported statutes server tools")

    logger.info("Server setup complete - all tool servers imported")


# Run setup when module is imported
asyncio.run(setup())


def main() -> None:
    """Run the GovInfo MCP server asynchronously."""
    logger.info("Starting GovInfo MCP server")
    mcp.run()


if __name__ == "__main__":
    main()
