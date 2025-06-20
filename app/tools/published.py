"""Published tools for GovInfo MCP server."""

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

# Create the published server
published_server = FastMCP("PublishedServer")


@published_server.tool()
async def get_published_packages(
    date_issued: Annotated[
        str, Field(description="Date to get published packages for (YYYY-MM-DD)")
    ],
    collection: Annotated[
        str, Field(description="Filter by collection code (e.g., 'BILLS', 'PLAW')")
    ] = "",
    doc_class: Annotated[str, Field(description="Filter by document class")] = "",
    page_size: Annotated[
        int, Field(description="Number of results per page", ge=1, le=100)
    ] = 50,
    offset_mark: Annotated[
        str, Field(description="Pagination offset mark for next page")
    ] = "*",
    ctx: Context | None = None,
) -> dict:
    """Get packages published on a specific date.

    Returns a list of packages that were published or issued on the specified date,
    optionally filtered by collection and document class.

    Returns:
        A dictionary containing the published packages data from the GovInfo API,
        including a 'packages' key with the list of published packages.

    Raises:
        ValueError: If GOVINFO_API_KEY is not found in environment variables.

    """
    if ctx:
        await ctx.info(f"Fetching packages published on: {date_issued}")
    else:
        logger.info(f"Fetching packages published on: {date_issued}")

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

    # Add optional filters
    if collection:
        params["collection"] = collection
    if doc_class:
        params["docClass"] = doc_class

    headers = {"X-Api-Key": API_KEY}

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"https://api.govinfo.gov/published/{date_issued}",
                params=params,
                headers=headers,
                timeout=30.0,
            )
            response.raise_for_status()

            data = response.json()

            if ctx:
                await ctx.info(
                    f"Found {len(data.get('packages', []))} packages published on {date_issued}"
                )
            else:
                logger.info(
                    f"Found {len(data.get('packages', []))} packages published on {date_issued}"
                )

            return data

    except httpx.HTTPStatusError as e:
        error_msg = f"HTTP error: {e}"
        if ctx:
            await ctx.error(error_msg)
        else:
            logger.error(error_msg)
        raise e
    except Exception as e:
        error_msg = f"Published packages fetch error: {e}"
        if ctx:
            await ctx.error(error_msg)
        else:
            logger.error(error_msg)
        raise e


@published_server.tool()
async def get_published_range(
    start_date: Annotated[str, Field(description="Start date for range (YYYY-MM-DD)")],
    end_date: Annotated[str, Field(description="End date for range (YYYY-MM-DD)")],
    collection: Annotated[
        str,
        Field(description="Filter by collection code (e.g., 'BILLS', 'PLAW', 'CFR')"),
    ],
    doc_class: Annotated[str, Field(description="Filter by document class")] = "",
    modified_since: Annotated[
        str,
        Field(description="Only return packages modified since this date (YYYY-MM-DD)"),
    ] = "",
    page_size: Annotated[
        int, Field(description="Number of results per page", ge=1, le=100)
    ] = 50,
    offset_mark: Annotated[
        str, Field(description="Pagination offset mark for next page")
    ] = "*",
    ctx: Context | None = None,
) -> dict:
    """Get packages published within a date range.

    Returns a list of packages that were published between the specified start
    and end dates, optionally filtered by collection and document class.

    Returns:
        A dictionary containing the published packages data from the GovInfo API,
        including a 'packages' key with the list of published packages.

    Raises:
        ValueError: If GOVINFO_API_KEY is not found in environment variables.

    """
    if ctx:
        await ctx.info(
            f"Fetching packages published between {start_date} and {end_date}"
        )
    else:
        logger.info(f"Fetching packages published between {start_date} and {end_date}")

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
        "collection": collection,  # Always required
    }

    # Add optional filters
    if doc_class:
        params["docClass"] = doc_class
    if modified_since:
        params["modifiedSince"] = modified_since

    headers = {"X-Api-Key": API_KEY}

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"https://api.govinfo.gov/published/{start_date}/{end_date}",
                params=params,
                headers=headers,
                timeout=30.0,
            )
            response.raise_for_status()

            data = response.json()

            if ctx:
                await ctx.info(
                    f"Found {len(data.get('packages', []))} packages in date range"
                )
            else:
                logger.info(
                    f"Found {len(data.get('packages', []))} packages in date range"
                )

            return data

    except httpx.HTTPStatusError as e:
        error_msg = f"HTTP error: {e}"
        if ctx:
            await ctx.error(error_msg)
        else:
            logger.error(error_msg)
        raise e
    except Exception as e:
        error_msg = f"Published range fetch error: {e}"
        if ctx:
            await ctx.error(error_msg)
        else:
            logger.error(error_msg)
        raise e
