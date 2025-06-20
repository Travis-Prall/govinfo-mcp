"""Collections tools for GovInfo MCP server."""

import os
from typing import Annotated

from dotenv import load_dotenv
from fastmcp import Context, FastMCP
import httpx
from loguru import logger
from pydantic import Field

# Load environment variables
load_dotenv()

# Get API key from environment
API_KEY = os.getenv("GOVINFO_API_KEY")

# Create the collections server
collections_server = FastMCP("CollectionsServer")


@collections_server.tool()
async def get_collections(
    page_size: Annotated[
        int, Field(description="Number of results per page", ge=1, le=100)
    ] = 50,
    offset_mark: Annotated[
        str, Field(description="Pagination offset mark for next page")
    ] = "*",
    ctx: Context | None = None,
) -> dict:
    """Get a list of collections available in GovInfo.

    Returns information about all available collections including their codes,
    names, and the number of packages in each collection.

    Returns:
        Dict containing collections list and metadata.

    Raises:
        ValueError: If GOVINFO_API_KEY is not found in environment variables.

    """
    if ctx:
        await ctx.info("Fetching GovInfo collections")
    else:
        logger.info("Fetching GovInfo collections")

    if not API_KEY:
        error_msg = "GOVINFO_API_KEY not found in environment variables"
        if ctx:
            await ctx.error(error_msg)
        else:
            logger.error(error_msg)
        raise ValueError(error_msg)

    params = {
        "pageSize": page_size,
        "offsetMark": offset_mark,
    }

    headers = {"X-Api-Key": API_KEY}

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://api.govinfo.gov/collections",
                params=params,
                headers=headers,
                timeout=30.0,
            )
            response.raise_for_status()

            data = response.json()

            if ctx:
                await ctx.info(f"Found {len(data.get('collections', []))} collections")
            else:
                logger.info(f"Found {len(data.get('collections', []))} collections")

            return data

    except httpx.HTTPStatusError as e:
        error_msg = f"HTTP error: {e}"
        if ctx:
            await ctx.error(error_msg)
        else:
            logger.error(error_msg)
        raise e
    except Exception as e:
        error_msg = f"Collections fetch error: {e}"
        if ctx:
            await ctx.error(error_msg)
        else:
            logger.error(error_msg)
        raise e
