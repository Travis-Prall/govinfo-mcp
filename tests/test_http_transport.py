"""HTTP transport tests for the GovInfo MCP server.

These tests validate the Streamable HTTP deployment shape used by the
standalone Linux service: the operational ``/health`` route and a real MCP
request dispatched through the full HTTP stack (sessions, SSE framing,
serialization) using FastMCP's in-process ASGI test utilities.
"""

# mypy: disable-error-code=reportUnknownVariableType,reportUnknownParameterType,reportMissingTypeArgument,reportUnknownMemberType,reportUnknownArgumentType,reportAttributeAccessIssue,reportReturnType,reportGeneralTypeIssues
from __future__ import annotations

from typing import TYPE_CHECKING

from fastmcp.utilities.tests import asgi_server
import httpx
import pytest

from app import __version__
from app.server import app, mcp

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator

    from fastmcp.utilities.tests import ASGIServer


@pytest.fixture
async def http_server() -> AsyncGenerator[ASGIServer]:
    """Yield an in-process HTTP server bound to the GovInfo MCP server.

    Yields:
        A running in-process ASGI server for Streamable HTTP assertions.

    """
    async with asgi_server(mcp) as server:
        yield server


async def test_health_route_exported_app() -> None:
    """The exported ASGI ``app`` answers the operational health probe."""
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(
        transport=transport, base_url="http://testserver"
    ) as client:
        response = await client.get("/health")

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "healthy"
    assert body["service"] == "GovInfo MCP Server"
    assert body["version"] == __version__


async def test_tool_call_over_http(http_server: ASGIServer) -> None:
    """A tool call succeeds over the Streamable HTTP transport."""
    async with http_server.client() as client:
        tools = await client.list_tools()
        tool_names = [tool.name for tool in tools]
        assert "status" in tool_names
        assert "collections_get_collections" in tool_names

        result = await client.call_tool("status", {})
        assert result.data["service"] == "GovInfo MCP Server"
        assert result.data["version"] == __version__


async def test_health_route_over_in_process_server(http_server: ASGIServer) -> None:
    """The health route is also served by the composed in-process HTTP app."""
    base_url = http_server.url.removesuffix("/mcp")
    async with http_server.http_client() as http:
        response = await http.get(f"{base_url}/health")

    assert response.status_code == 200
    assert response.json()["service"] == "GovInfo MCP Server"
