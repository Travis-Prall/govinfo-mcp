"""Search tools for GovInfo MCP server."""

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

# Create the search server
search_server = FastMCP("SearchServer")


@search_server.tool()
async def search_packages(
    query: Annotated[str, Field(description="Search query text")],
    *,
    collection: Annotated[
        str,
        Field(description="Filter by collection code (e.g., 'BILLS', 'PLAW', 'CFR')"),
    ] = "",
    congress: Annotated[
        int | None, Field(description="Filter by Congress number", ge=1, le=200)
    ] = None,
    doc_class: Annotated[str, Field(description="Filter by document class")] = "",
    title: Annotated[str, Field(description="Filter by title")] = "",
    start_date: Annotated[
        str, Field(description="Filter results after this date (YYYY-MM-DD)")
    ] = "",
    end_date: Annotated[
        str, Field(description="Filter results before this date (YYYY-MM-DD)")
    ] = "",
    page_size: Annotated[
        int, Field(description="Number of results per page", ge=1, le=100)
    ] = 50,
    offset_mark: Annotated[
        str, Field(description="Pagination offset mark for next page")
    ] = "*",
    ctx: Context | None = None,
) -> dict:
    """Search for packages across all GovInfo collections.

    Performs a full-text search across government documents and returns
    matching packages with relevance scores and metadata.

    Returns:
        Dict containing search results with packages and metadata.

    Raises:
        ValueError: If GOVINFO_API_KEY is not found in environment variables.

    """
    if ctx:
        await ctx.info(f"Searching packages with query: {query}")
    else:
        logger.info(f"Searching packages with query: {query}")

    if not API_KEY:
        error_msg = "GOVINFO_API_KEY not found in environment variables"
        if ctx:
            await ctx.error(error_msg)
        else:
            logger.error(error_msg)
        raise ValueError(error_msg)

    # Build search query with field operators based on parameters
    search_query = query

    # Add collection filter to query if specified
    if collection:
        search_query = f"collection:{collection} AND {search_query}"

    # Add congress filter to query if specified
    if congress is not None:
        search_query = f"congress:{congress} AND {search_query}"

    # Add doc_class filter to query if specified
    if doc_class:
        search_query = f"docClass:{doc_class} AND {search_query}"

    # Add title filter to query if specified
    if title:
        search_query = f'title:"{title}" AND {search_query}'

    # Add date filters if specified
    if start_date:
        search_query = f"publishdate:>={start_date} AND {search_query}"
    if end_date:
        search_query = f"publishdate:<={end_date} AND {search_query}"

    # Prepare JSON request body
    request_body = {
        "query": search_query,
        "pageSize": page_size,
        "offsetMark": offset_mark,
        "resultLevel": "default",
        "sorts": [{"field": "score", "sortOrder": "DESC"}],
    }

    headers = {"X-Api-Key": API_KEY, "Content-Type": "application/json"}

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.govinfo.gov/search",
                json=request_body,
                headers=headers,
                timeout=30.0,
            )
            response.raise_for_status()

            data = response.json()

            if ctx:
                await ctx.info(
                    f"Found {data.get('count', 0)} results for query: {query}"
                )
            else:
                logger.info(f"Found {data.get('count', 0)} results for query: {query}")

            return data

    except httpx.HTTPStatusError as e:
        error_msg = f"HTTP error: {e}"
        if ctx:
            await ctx.error(error_msg)
        else:
            logger.error(error_msg)
        raise e
    except Exception as e:
        error_msg = f"Search error: {e}"
        if ctx:
            await ctx.error(error_msg)
        else:
            logger.error(error_msg)
        raise e


@search_server.tool()
async def advanced_search(
    query: Annotated[str, Field(description="Search query with Lucene syntax support")],
    collections: Annotated[
        list[str], Field(description="List of collection codes to search within")
    ] = [],
    congress: Annotated[
        list[int], Field(description="List of Congress numbers to filter by")
    ] = [],
    doc_class: Annotated[
        list[str], Field(description="List of document classes to filter by")
    ] = [],
    committees: Annotated[
        list[str], Field(description="List of committees to filter by")
    ] = [],
    date_issued_start: Annotated[
        str, Field(description="Start date for date issued filter (YYYY-MM-DD)")
    ] = "",
    date_issued_end: Annotated[
        str, Field(description="End date for date issued filter (YYYY-MM-DD)")
    ] = "",
    last_modified_start: Annotated[
        str, Field(description="Start date for last modified filter (YYYY-MM-DD)")
    ] = "",
    last_modified_end: Annotated[
        str, Field(description="End date for last modified filter (YYYY-MM-DD)")
    ] = "",
    package_count: Annotated[
        int | None, Field(description="Filter by number of packages", ge=1)
    ] = None,
    granule_count: Annotated[
        int | None, Field(description="Filter by number of granules", ge=1)
    ] = None,
    sort_by: Annotated[
        str,
        Field(
            description="Sort field: 'relevance', 'dateIssued', 'title', or 'packageId'"
        ),
    ] = "relevance",
    sort_order: Annotated[
        str, Field(description="Sort order: 'asc' or 'desc'")
    ] = "desc",
    page_size: Annotated[
        int, Field(description="Number of results per page", ge=1, le=100)
    ] = 50,
    offset_mark: Annotated[
        str, Field(description="Pagination offset mark for next page")
    ] = "*",
    ctx: Context | None = None,
) -> dict:
    """Perform an advanced search with multiple filters and Lucene query syntax.

    Supports complex queries with boolean operators (AND, OR, NOT), wildcards (*),
    phrase searches ("exact phrase"), and field-specific searches (field:value).

    Returns:
        Dict containing search results with packages and metadata.

    Raises:
        ValueError: If GOVINFO_API_KEY is not found in environment variables.

    """
    if ctx:
        await ctx.info(f"Performing advanced search with query: {query}")
    else:
        logger.info(f"Performing advanced search with query: {query}")

    if not API_KEY:
        error_msg = "GOVINFO_API_KEY not found in environment variables"
        if ctx:
            await ctx.error(error_msg)
        else:
            logger.error(error_msg)
        raise ValueError(error_msg)

    # Create JSON body for POST request
    body = {
        "query": query,
        "pageSize": str(page_size),
        "offsetMark": offset_mark,
        "sorts": [
            {
                "field": "score" if sort_by == "relevance" else sort_by,
                "sortOrder": sort_order.upper(),
            }
        ],
        "resultLevel": "default",
    }

    headers = {
        "X-Api-Key": API_KEY,
        "Content-Type": "application/json",
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.govinfo.gov/search",
                json=body,
                headers=headers,
                timeout=30.0,
            )
            response.raise_for_status()

            data = response.json()

            if ctx:
                await ctx.info(
                    f"Advanced search returned {data.get('count', 0)} results"
                )
            else:
                logger.info(f"Advanced search returned {data.get('count', 0)} results")

            return data

    except httpx.HTTPStatusError as e:
        error_msg = f"HTTP error: {e}"
        if ctx:
            await ctx.error(error_msg)
        else:
            logger.error(error_msg)
        raise e
    except Exception as e:
        error_msg = f"Advanced search error: {e}"
        if ctx:
            await ctx.error(error_msg)
        else:
            logger.error(error_msg)
        raise e
