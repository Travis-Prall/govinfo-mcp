"""Packages tools for GovInfo MCP server."""

import base64
from datetime import UTC, datetime, timedelta
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

# Create the packages server
packages: FastMCP = FastMCP(
    "PackagesServer",
    instructions="""The PackagesServer provides access to government document packages through the GovInfo API.

Key capabilities:
- Search and list packages from specific collections (BILLS, PLAW, CFR, etc.)
- Retrieve package summaries with metadata
- Download package content in multiple formats (HTML, XML, PDF, text)

Common collections:
- BILLS: Congressional bills
- PLAW: Public laws
- CFR: Code of Federal Regulations
- FR: Federal Register
- STATUTE: Statutes at Large
- USCOURTS: Court opinions
- CZIC: Coastal Zone Information Center

When searching packages:
- Use appropriate date ranges to limit results
- Congress numbers are only applicable to certain collections (BILLS, PLAW)
- Page size can be adjusted (1-100) for pagination
- Use offset_mark from response for pagination

Content formats and availability:
- HTML: Best for reading and displaying (most widely available)
- XML: Best for parsing and data extraction (most widely available)
- PDF: Original formatted document (limited availability)
- Text: Plain text version (limited availability)

IMPORTANT for get_package_content:
- Not all content types are available for every package
- The API returns 400 Bad Request if format is not available
- Always use get_package_summary() first to check available formats in 'download' field
- Default to 'html' or 'xml' formats for maximum compatibility
- Handle HTTPStatusError gracefully when requesting unavailable formats

Best practice workflow:
1. Use get_package_summary() to check available formats
2. Choose format based on availability and needs
3. Use get_package_content() with error handling

Note: PDF content is returned as base64 encoded data.""",
)


@packages.tool()
async def get_packages_by_collection(
    collection: Annotated[
        str, Field(description="Collection code (e.g., 'BILLS', 'PLAW', 'CFR')")
    ],
    congress: Annotated[
        int | None, Field(description="Congress number for filtering", ge=1, le=200)
    ] = None,
    doc_class: Annotated[str, Field(description="Document class for filtering")] = "",
    start_date: Annotated[
        str, Field(description="Start date for filtering (YYYY-MM-DD)")
    ] = "",
    end_date: Annotated[
        str, Field(description="End date for filtering (YYYY-MM-DD)")
    ] = "",
    page_size: Annotated[
        int, Field(description="Number of results per page", ge=1, le=100)
    ] = 50,
    offset_mark: Annotated[
        str, Field(description="Pagination offset mark for next page")
    ] = "*",
    ctx: Context | None = None,
) -> dict:
    """Get a list of packages from a specific collection.

    Returns package summaries including package IDs, titles, and metadata
    for packages within the specified collection.

    Returns:
        dict: A dictionary containing the packages list and pagination information.

    Raises:
        ValueError: If the GOVINFO_API_KEY environment variable is not set.

    """
    if ctx:
        await ctx.info(f"Fetching packages from collection: {collection}")
    else:
        logger.info(f"Fetching packages from collection: {collection}")

    if not API_KEY:
        error_msg = "GOVINFO_API_KEY not found in environment variables"
        if ctx:
            await ctx.error(error_msg)
        else:
            logger.error(error_msg)
        raise ValueError(error_msg)

    # Use a default lastModifiedStartDate if not provided (1 year ago)

    if not start_date:
        default_date = datetime.now(UTC) - timedelta(days=365)
        last_modified_start = default_date.strftime("%Y-%m-%dT%H:%M:%SZ")
    else:
        # Convert YYYY-MM-DD to ISO 8601 format
        last_modified_start = f"{start_date}T00:00:00Z"

    params = {
        "pageSize": page_size,
        "offsetMark": offset_mark,
    }

    # Add optional filters
    if congress is not None:
        params["congress"] = congress
    if doc_class:
        params["docClass"] = doc_class

    headers = {"X-Api-Key": API_KEY}

    try:
        async with httpx.AsyncClient() as client:
            if end_date:
                # Use date range endpoint
                last_modified_end = f"{end_date}T23:59:59Z"
                url = f"https://api.govinfo.gov/collections/{collection}/{last_modified_start}/{last_modified_end}"
            else:
                # Use single date endpoint
                url = f"https://api.govinfo.gov/collections/{collection}/{last_modified_start}"

            response = await client.get(
                url,
                params=params,
                headers=headers,
                timeout=30.0,
            )
            response.raise_for_status()

            data = response.json()

            if ctx:
                await ctx.info(f"Found {len(data.get('packages', []))} packages")
            else:
                logger.info(f"Found {len(data.get('packages', []))} packages")

            return data

    except httpx.HTTPStatusError as e:
        error_msg = f"HTTP error: {e}"
        if ctx:
            await ctx.error(error_msg)
        else:
            logger.error(error_msg)
        raise e
    except Exception as e:
        error_msg = f"Packages fetch error: {e}"
        if ctx:
            await ctx.error(error_msg)
        else:
            logger.error(error_msg)
        raise e


@packages.tool()
async def get_package_summary(
    package_id: Annotated[
        str, Field(description="Package ID (e.g., 'BILLS-116hr1-ih')")
    ],
    ctx: Context | None = None,
) -> dict:
    """Get summary information for a specific package.

    Returns metadata about a package including its title, dates, collection,
    and available download formats.

    Returns:
        dict: A dictionary containing package metadata such as title, dates,
            collection information, and available download formats.

    Raises:
        ValueError: If the GOVINFO_API_KEY environment variable is not set.

    """
    if ctx:
        await ctx.info(f"Fetching summary for package: {package_id}")
    else:
        logger.info(f"Fetching summary for package: {package_id}")

    if not API_KEY:
        error_msg = "GOVINFO_API_KEY not found in environment variables"
        if ctx:
            await ctx.error(error_msg)
        else:
            logger.error(error_msg)
        raise ValueError(error_msg)

    headers = {"X-Api-Key": API_KEY}

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"https://api.govinfo.gov/packages/{package_id}/summary",
                headers=headers,
                timeout=30.0,
            )
            response.raise_for_status()

            data = response.json()

            if ctx:
                await ctx.info(f"Retrieved summary for package: {package_id}")
            else:
                logger.info(f"Retrieved summary for package: {package_id}")

            return data

    except httpx.HTTPStatusError as e:
        error_msg = f"HTTP error: {e}"
        if ctx:
            await ctx.error(error_msg)
        else:
            logger.error(error_msg)
        raise e
    except Exception as e:
        error_msg = f"Package summary fetch error: {e}"
        if ctx:
            await ctx.error(error_msg)
        else:
            logger.error(error_msg)
        raise e


@packages.tool()
async def get_package_content(
    package_id: Annotated[
        str, Field(description="Package ID (e.g., 'BILLS-116hr1-ih')")
    ],
    content_type: Annotated[
        str, Field(description="Content type: 'html', 'xml', 'pdf', or 'text'")
    ] = "html",
    ctx: Context | None = None,
) -> dict[str, str] | str:
    """Get the content of a specific package in the requested format.

    Returns the actual document content in the specified format (HTML, XML, PDF, or text).

    IMPORTANT: Not all content types are available for every package. The GovInfo API
    returns a 400 Bad Request error if the requested format is not available for a
    specific package. To avoid errors:

    1. First call get_package_summary() to check available formats in the 'download' field
    2. Start with 'html' or 'xml' as these are most commonly available
    3. Handle HTTPStatusError exceptions gracefully for unsupported formats

    Content Type Availability by Collection:
    - BILLS: html, xml commonly available; text, pdf may be limited
    - PLAW: html, xml commonly available; text, pdf availability varies
    - CFR: html, xml typically available; text format often not available
    - FR: html, xml commonly available; pdf often available

    Best Practices:
    - Use get_package_summary() first to check the 'download' field for available formats
    - Always handle HTTPStatusError (400) which indicates format not available
    - Default to 'html' format for maximum compatibility
    - Use 'xml' for structured data parsing
    - Only request 'pdf' or 'text' after verifying availability

    Args:
        package_id: Package ID (e.g., 'BILLS-116hr1-ih')
        content_type: Content format - 'html' (default), 'xml', 'pdf', or 'text'
        ctx: Optional context for logging

    Returns:
        For text-based formats (HTML, XML, text): The raw content as a string.
        For binary formats (PDF): A dictionary with 'content_type' and 'base64_content' keys.

    Raises:
        ValueError: If GOVINFO_API_KEY is not found in environment variables.

    Example:
        # Safe approach - check available formats first
        summary = await get_package_summary("BILLS-116hr1-ih")
        available_formats = [dl.get('type') for dl in summary.get('download', [])]

        if 'pdf' in available_formats:
            content = await get_package_content("BILLS-116hr1-ih", "pdf")
        else:
            content = await get_package_content("BILLS-116hr1-ih", "html")

    """
    if ctx:
        await ctx.info(f"Fetching {content_type} content for package: {package_id}")
    else:
        logger.info(f"Fetching {content_type} content for package: {package_id}")

    if not API_KEY:
        error_msg = "GOVINFO_API_KEY not found in environment variables"
        if ctx:
            await ctx.error(error_msg)
        else:
            logger.error(error_msg)
        raise ValueError(error_msg)

    headers = {"X-Api-Key": API_KEY}

    # Map content type to appropriate endpoint
    content_endpoints = {"html": "htm", "xml": "xml", "pdf": "pdf", "text": "txt"}

    endpoint = content_endpoints.get(content_type.lower(), "htm")

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"https://api.govinfo.gov/packages/{package_id}/{endpoint}",
                headers=headers,
                timeout=60.0,  # Longer timeout for content downloads
            )
            response.raise_for_status()

            # Return raw content for text-based formats
            if content_type.lower() in {"html", "xml", "text"}:
                content = response.text
                if ctx:
                    await ctx.info(
                        f"Retrieved {content_type} content for package: {package_id}"
                    )
                else:
                    logger.info(
                        f"Retrieved {content_type} content for package: {package_id}"
                    )
                return content
            # For binary formats like PDF, return as base64 encoded
            content = base64.b64encode(response.content).decode("utf-8")
            if ctx:
                await ctx.info(
                    f"Retrieved {content_type} content for package: {package_id}"
                )
            else:
                logger.info(
                    f"Retrieved {content_type} content for package: {package_id}"
                )
            return {"content_type": content_type, "base64_content": content}

    except httpx.HTTPStatusError as e:
        if e.response.status_code == 400:
            error_msg = (
                f"Content type '{content_type}' is not available for package '{package_id}'. "
                f"Use get_package_summary() to check available formats in the 'download' field. "
                f"HTTP error: {e}"
            )
        else:
            error_msg = f"HTTP error: {e}"

        if ctx:
            await ctx.error(error_msg)
        else:
            logger.error(error_msg)
        raise e
    except Exception as e:
        error_msg = f"Package content fetch error: {e}"
        if ctx:
            await ctx.error(error_msg)
        else:
            logger.error(error_msg)
        raise e
