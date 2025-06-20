# mypy: disable-error-code=reportUnknownVariableType,reportUnknownParameterType,reportMissingTypeArgument,reportUnknownMemberType,reportUnknownArgumentType,reportAttributeAccessIssue
"""Tests for the GovInfo MCP server."""

import json
from typing import Any

from fastmcp import Client
from fastmcp.exceptions import ToolError
from loguru import logger
import pytest

# Import the actual server instance after setup has run
from app.server import mcp  # type: ignore[reportUnknownVariableType]


@pytest.fixture
def client() -> Client[Any]:
    """Create a test client connected to the real server.

    Returns:
        Client: FastMCP client instance connected to the server.

    """
    return Client(mcp)


@pytest.mark.asyncio
async def test_status_tool(client: Client[Any]) -> None:
    """Test the status tool returns expected server information."""
    async with client:
        result = await client.call_tool("status", {})

        # Check response structure
        assert len(result) == 1
        response = result[0].text  # type: ignore[attr-defined,union-attr]

        # Parse JSON response
        data = json.loads(str(response))  # type: ignore[arg-type]

        # Verify expected fields
        assert data["status"] in {
            "healthy",
            "degraded",
        }  # Updated to match actual response
        assert (
            data["service"] == "GovInfo MCP Server"
        )  # Updated to match actual service
        assert data["version"] == "0.1.0"

        logger.info(f"Status tool test passed: {data}")


@pytest.mark.asyncio
async def test_list_available_tools(client: Client[Any]) -> None:
    """Test listing all available tools."""
    async with client:
        tools = await client.list_tools()
        tool_names = [tool.name for tool in tools]

        logger.info(f"Available tools: {tool_names}")

        # Check that core expected tools are available
        expected_tools = [
            "status",
            "collections_get_collections",
            "packages_get_packages_by_collection",
            "packages_get_package_summary",
            "packages_get_package_content",
            "published_get_published_packages",
            "published_get_published_range",
            "related_get_related_packages",
            "related_get_granule_related",
            "search_search_packages",
            "search_advanced_search",
            "statutes_search_statutes",
            "statutes_get_uscode_title",
            "statutes_get_public_laws_by_congress",
            "statutes_get_statutes_at_large",
            "statutes_get_statute_content",
            "statutes_list_statute_collections",
        ]

        for tool in expected_tools:
            assert tool in tool_names, f"Expected tool {tool} not found in {tool_names}"

        logger.info(f"All expected tools found: {len(expected_tools)} tools verified")


@pytest.mark.asyncio
async def test_collections_tool(client: Client[Any]) -> None:
    """Test the collections tool."""
    async with client:
        result = await client.call_tool("collections_get_collections", {})

        assert len(result) == 1
        response = result[0].text  # type: ignore[attr-defined,union-attr]
        data = json.loads(str(response))  # type: ignore[arg-type]

        # Should have collections data
        assert "collections" in data
        assert isinstance(data["collections"], list)

        logger.info(
            f"Collections tool test passed: found {len(data['collections'])} collections"
        )


@pytest.mark.asyncio
async def test_search_packages_tool(client: Client[Any]) -> None:
    """Test the search packages tool."""
    async with client:
        result = await client.call_tool(
            "search_search_packages", {"query": "federal register", "page_size": 5}
        )

        assert len(result) == 1
        response = result[0].text  # type: ignore[attr-defined,union-attr]
        data = json.loads(str(response))  # type: ignore[arg-type]

        # Should have results data (not "packages")
        assert "results" in data
        assert isinstance(data["results"], list)

        logger.info("Search packages tool test passed")


@pytest.mark.asyncio
async def test_statutes_list_collections(client: Client[Any]) -> None:
    """Test the statutes list collections tool."""
    async with client:
        result = await client.call_tool("statutes_list_statute_collections", {})

        assert len(result) == 1
        response = result[0].text  # type: ignore[attr-defined,union-attr]
        data = json.loads(str(response))  # type: ignore[arg-type]

        # Should have statute collections data
        assert "statute_collections" in data
        assert isinstance(data["statute_collections"], list)

        logger.info("Statutes list collections tool test passed")


@pytest.mark.asyncio
async def test_error_handling_invalid_tool(client: Client[Any]) -> None:
    """Test error handling for invalid tool names."""
    async with client:
        with pytest.raises(ToolError, match="Unknown tool"):
            await client.call_tool("nonexistent_tool", {})

        logger.info("Error handling test passed")
