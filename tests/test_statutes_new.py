"""Test file for the GovInfo MCP server statutes tools."""

import json
from typing import Any

from fastmcp import Client
from loguru import logger
import pytest

# Import the actual server instance after setup has run
from app.server import mcp


@pytest.fixture
def client() -> Client[Any]:
    """Create a test client connected to the real server.

    Returns:
        Client: FastMCP client instance connected to the server.

    """
    return Client(mcp)


@pytest.mark.asyncio
async def test_statute_collections(client: Client[Any]) -> None:
    """Test listing statute collections."""
    async with client:
        result = await client.call_tool("statutes_list_statute_collections", {})

        assert len(result) == 1
        response = result[0].text  # type: ignore[attr-defined]
        data = json.loads(response)

        # Should have statute collections data
        assert "statute_collections" in data
        assert isinstance(data["statute_collections"], list)
        assert len(data["statute_collections"]) > 0

        # Check that expected collections are present
        collection_codes = [coll["code"] for coll in data["statute_collections"]]
        assert "USCODE" in collection_codes
        assert "PLAW" in collection_codes

        logger.info(f"Found {len(data['statute_collections'])} statute collections")


@pytest.mark.asyncio
async def test_search_statutes(client: Client[Any]) -> None:
    """Test searching within US statute collections."""
    async with client:
        result = await client.call_tool(
            "statutes_search_statutes",
            {"query": "civil rights", "page_size": 5},
        )

        assert len(result) == 1
        response = result[0].text  # type: ignore[attr-defined]
        data = json.loads(response)

        # Should have results data
        assert "results" in data
        assert isinstance(data["results"], list)

        logger.info("Search statutes tool test passed")


@pytest.mark.asyncio
async def test_get_uscode_title(client: Client[Any]) -> None:
    """Test getting USC title information."""
    async with client:
        result = await client.call_tool(
            "statutes_get_uscode_title",
            {"title_number": "42", "page_size": 5},  # Title 42 - Public Health
        )

        assert len(result) == 1
        response = result[0].text  # type: ignore[attr-defined]
        data = json.loads(response)

        # Should have results data
        assert "results" in data
        assert isinstance(data["results"], list)

        logger.info("USC title tool test passed")


@pytest.mark.asyncio
async def test_get_public_laws_by_congress(client: Client[Any]) -> None:
    """Test getting public laws by Congress."""
    async with client:
        result = await client.call_tool(
            "statutes_get_public_laws_by_congress",
            {"congress": 117, "page_size": 5},  # 117th Congress
        )

        assert len(result) == 1
        response = result[0].text  # type: ignore[attr-defined]
        data = json.loads(response)

        # Should have results data
        assert "results" in data
        assert isinstance(data["results"], list)

        logger.info("Public laws by Congress tool test passed")


@pytest.mark.asyncio
async def test_get_statutes_at_large(client: Client[Any]) -> None:
    """Test getting Statutes at Large by volume."""
    async with client:
        result = await client.call_tool(
            "statutes_get_statutes_at_large",
            {"volume": "135", "page_size": 5},  # Recent volume
        )

        assert len(result) == 1
        response = result[0].text  # type: ignore[attr-defined]
        data = json.loads(response)

        # Should have results data
        assert "results" in data
        assert isinstance(data["results"], list)

        logger.info("Statutes at Large tool test passed")
