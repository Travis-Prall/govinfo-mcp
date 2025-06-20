"""US Statutes search and lookup tools for GovInfo MCP server."""

import os
from typing import Annotated, Any

from dotenv import load_dotenv
from fastmcp import Context, FastMCP
import httpx
from loguru import logger
from pydantic import Field

# Load environment variables
load_dotenv()

# Get API key from environment
API_KEY = os.getenv("GOVINFO_API_KEY")

# Create the statutes server
statutes: FastMCP = FastMCP(
    name="StatutesServer",
    instructions="""This server provides access to US statutes and related legal materials.
""",
)

# Statute-related collection codes
STATUTE_COLLECTIONS = {
    "USCODE": "United States Code",
    "STATUTE": "Statutes at Large",
    "PLAW": "Public and Private Laws",
    "COMPS": "Statutes Compilations",
}


@statutes.tool()
async def search_statutes(
    query: Annotated[str, Field(description="Search query text for US statutes")],
    *,
    collection: Annotated[
        str,
        Field(
            description="Statute collection to search: 'USCODE', 'STATUTE', 'PLAW', 'COMPS', or leave empty for all statute collections"
        ),
    ] = "",
    congress: Annotated[
        int | None,
        Field(
            description="Filter by Congress number (for PLAW collection)", ge=1, le=200
        ),
    ] = None,
    title_number: Annotated[
        str, Field(description="Filter by USC title number (for USCODE collection)")
    ] = "",
    section: Annotated[str, Field(description="Filter by section number")] = "",
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
) -> dict[str, Any]:
    """Search for US statutes across statute-related collections.

    Searches within United States Code (USCODE), Statutes at Large (STATUTE),
    Public and Private Laws (PLAW), and Statutes Compilations (COMPS).

    Returns:
        Dict containing search results with statute packages and metadata.

    Raises:
        ValueError: If GOVINFO_API_KEY is not found in environment variables.
        ValueError: If invalid collection code is provided.

    """
    log = ctx.info if ctx else logger.info
    err = ctx.error if ctx else logger.error

    log(f"Searching US statutes with query: {query}")

    if not API_KEY:
        msg = "GOVINFO_API_KEY not found in environment variables"
        err(msg)
        raise ValueError(msg)

    # Validate collection if specified
    if collection and collection not in STATUTE_COLLECTIONS:
        msg = f"Invalid collection '{collection}'. Must be one of: {', '.join(STATUTE_COLLECTIONS.keys())}"
        err(msg)
        raise ValueError(msg)

    # Build search query
    search_query = query

    # If specific collection requested, filter to that collection
    if collection:
        search_query = f"collection:{collection} AND ({query})"
    else:
        # Search across all statute collections
        collections_query = " OR ".join([
            f"collection:{code}" for code in STATUTE_COLLECTIONS
        ])
        search_query = f"({collections_query}) AND ({query})"

    # Add congress filter if specified
    if congress is not None:
        search_query = f"{search_query} AND congress:{congress}"

    # Add title filter if specified (for USCODE)
    if title_number:
        search_query = f"{search_query} AND title:{title_number}"

    # Add section filter if specified
    if section:
        search_query = f"{search_query} AND section:{section}"

    # Add date filters if specified
    if start_date:
        search_query = f"{search_query} AND publishdate:[{start_date} TO *]"
    if end_date:
        search_query = f"{search_query} AND publishdate:[* TO {end_date}]"

    # Prepare JSON request body
    request_body = {
        "query": search_query,
        "pageSize": page_size,
        "offsetMark": offset_mark,
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

            # Filter results to only statute collections if no specific collection was requested
            if not collection and "results" in data:
                data["results"] = [
                    result
                    for result in data.get("results", [])
                    if result.get("collectionCode") in STATUTE_COLLECTIONS
                ]
                data["count"] = len(data["results"])

            log(f"Found {data.get('count', 0)} statute results for query: {query}")

            return data

    except httpx.HTTPStatusError as e:
        msg = f"HTTP error: {e.response.status_code} - {e.response.text}"
        err(msg)
        raise e
    except Exception as e:
        msg = f"Search error: {e}"
        err(msg)
        raise e


@statutes.tool()
async def get_uscode_title(
    title_number: Annotated[
        str, Field(description="USC title number (e.g., '42' for Title 42)")
    ],
    *,
    edition: Annotated[
        str,
        Field(description="USC edition year (e.g., '2022'; leave empty for latest)"),
    ] = "",
    chapter: Annotated[str, Field(description="Filter by chapter number")] = "",
    section: Annotated[str, Field(description="Filter by section number")] = "",
    page_size: Annotated[int, Field(ge=1, le=100)] = 50,
    offset_mark: Annotated[str, Field(description="Pagination offset mark")] = "*",
    ctx: Context | None = None,
) -> dict[str, Any]:
    """Search for United States Code sections within a specific title.

    Uses the GovInfo search API to find USC sections, chapters, and subchapters
    for a given title number.

    Returns:
        Dict containing search results with USC packages and metadata.

    Raises:
        ValueError: If GOVINFO_API_KEY is not found in environment variables.

    """
    log = ctx.info if ctx else logger.info
    err = ctx.error if ctx else logger.error
    log(f"Searching USC Title {title_number}")

    if not API_KEY:
        msg = "GOVINFO_API_KEY not set"
        err(msg)
        raise ValueError(msg)

    # Build search query for USC title
    # Use title field operator and collection filter
    search_query = f"collection:USCODE AND title:{title_number}"

    # Add edition filter if specified
    if edition:
        search_query += f" AND publishdate:{edition}"

    # Add chapter filter if specified
    if chapter:
        search_query += f" AND chapter:{chapter}"

    # Add section filter if specified
    if section:
        search_query += f" AND section:{section}"

    request_body = {
        "query": search_query,
        "pageSize": page_size,
        "offsetMark": offset_mark,
        "sorts": [{"field": "title", "sortOrder": "ASC"}],
    }

    headers = {"X-Api-Key": API_KEY, "Content-Type": "application/json"}

    try:
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                "https://api.govinfo.gov/search",
                json=request_body,
                headers=headers,
                timeout=30.0,
            )
            resp.raise_for_status()
            data = resp.json()

            log(f"Found {data.get('count', 0)} results for USC Title {title_number}")
            return data

    except httpx.HTTPStatusError as exc:
        msg = f"HTTP error: {exc.response.status_code} - {exc.response.text}"
        err(msg)
        raise exc
    except Exception as exc:
        msg = f"USC title search error: {exc}"
        err(msg)
        raise exc


@statutes.tool()
async def get_public_laws_by_congress(
    congress: Annotated[
        int,
        Field(
            description="Congress number (e.g., 117 for 117th Congress)", ge=1, le=200
        ),
    ],
    *,
    law_type: Annotated[
        str, Field(description="Law type: 'public' or 'private' (leave empty for both)")
    ] = "",
    law_number: Annotated[
        str, Field(description="Specific public/private law number")
    ] = "",
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
) -> dict[str, Any]:
    """Search for Public and Private Laws from a specific Congress.

    Uses the GovInfo search API to find laws enacted by the specified Congress.

    Returns:
        Dict containing law packages and metadata.

    Raises:
        ValueError: If GOVINFO_API_KEY is not found in environment variables.

    """
    log = ctx.info if ctx else logger.info
    err = ctx.error if ctx else logger.error

    log(f"Searching laws from {congress}th Congress")

    if not API_KEY:
        msg = "GOVINFO_API_KEY not found in environment variables"
        err(msg)
        raise ValueError(msg)

    # Build query for Congress laws
    search_query = f"collection:PLAW AND congress:{congress}"

    # Add law type filter if specified
    if law_type:
        if law_type.lower() == "public":
            search_query += " AND (docClass:public OR title:public)"
        elif law_type.lower() == "private":
            search_query += " AND (docClass:private OR title:private)"
        else:
            msg = f"Invalid law_type '{law_type}'. Must be 'public' or 'private'"
            err(msg)
            raise ValueError(msg)

    # Add law number filter if specified
    if law_number:
        search_query += f" AND {law_number}"

    # Add date filters if specified
    if start_date:
        search_query += f" AND publishdate:[{start_date} TO *]"
    if end_date:
        search_query += f" AND publishdate:[* TO {end_date}]"

    request_body = {
        "query": search_query,
        "pageSize": page_size,
        "offsetMark": offset_mark,
        "sorts": [{"field": "publishdate", "sortOrder": "DESC"}],
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

            log(f"Found {data.get('count', 0)} laws from {congress}th Congress")

            return data

    except httpx.HTTPStatusError as e:
        msg = f"HTTP error: {e.response.status_code} - {e.response.text}"
        err(msg)
        raise e
    except Exception as e:
        msg = f"Congress laws search error: {e}"
        err(msg)
        raise e


@statutes.tool()
async def get_statutes_at_large(
    volume: Annotated[str, Field(description="Statutes at Large volume number")],
    *,
    page: Annotated[str, Field(description="Filter by specific page number")] = "",
    congress: Annotated[
        int | None, Field(description="Filter by Congress number", ge=1, le=200)
    ] = None,
    page_size: Annotated[
        int, Field(description="Number of results per page", ge=1, le=100)
    ] = 50,
    offset_mark: Annotated[
        str, Field(description="Pagination offset mark for next page")
    ] = "*",
    ctx: Context | None = None,
) -> dict[str, Any]:
    """Search Statutes at Large by volume.

    Uses the GovInfo search API to find statutes from a specific volume
    of the Statutes at Large.

    Returns:
        Dict containing Statutes at Large packages and metadata.

    Raises:
        ValueError: If GOVINFO_API_KEY is not found in environment variables.

    """
    log = ctx.info if ctx else logger.info
    err = ctx.error if ctx else logger.error

    log(f"Searching Statutes at Large Volume {volume}")

    if not API_KEY:
        msg = "GOVINFO_API_KEY not found in environment variables"
        err(msg)
        raise ValueError(msg)

    # Build query for Statutes at Large volume
    # Search for the volume number in the text
    search_query = f"collection:STATUTE AND {volume}"

    # Add page filter if specified
    if page:
        search_query += f" AND {page}"

    # Add congress filter if specified
    if congress is not None:
        search_query += f" AND congress:{congress}"

    request_body = {
        "query": search_query,
        "pageSize": page_size,
        "offsetMark": offset_mark,
        "sorts": [{"field": "title", "sortOrder": "ASC"}],
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

            log(f"Found {data.get('count', 0)} statutes in Volume {volume}")

            return data

    except httpx.HTTPStatusError as e:
        msg = f"HTTP error: {e.response.status_code} - {e.response.text}"
        err(msg)
        raise e
    except Exception as e:
        msg = f"Statutes at Large search error: {e}"
        err(msg)
        raise e


@statutes.tool()
async def get_statute_content(
    package_id: Annotated[
        str, Field(description="Package ID (e.g., 'PLAW-117publ58')")
    ],
    *,
    content_type: Annotated[
        str, Field(description="Content type: 'summary', 'xml', 'pdf', or 'text'")
    ] = "summary",
    granule_id: Annotated[
        str, Field(description="Optional granule ID for specific section")
    ] = "",
    ctx: Context | None = None,
) -> dict[str, Any]:
    """Get content or metadata for a specific statute package.

    Retrieves package summary or downloads content in various formats.

    Note: For content downloads (xml, pdf, text), the API returns download URLs
    rather than the actual content.

    Returns:
        Dict containing the package/granule summary or download links.

    Raises:
        ValueError: If GOVINFO_API_KEY is not found in environment variables.

    """
    log = ctx.info if ctx else logger.info
    err = ctx.error if ctx else logger.error

    log(f"Getting {content_type} for package: {package_id}")

    if not API_KEY:
        msg = "GOVINFO_API_KEY not found in environment variables"
        err(msg)
        raise ValueError(msg)

    # Validate content type
    valid_types = ["summary", "xml", "pdf", "text"]
    if content_type not in valid_types:
        msg = f"Invalid content_type '{content_type}'. Must be one of: {', '.join(valid_types)}"
        err(msg)
        raise ValueError(msg)

    headers = {"X-Api-Key": API_KEY}

    try:
        async with httpx.AsyncClient() as client:
            if granule_id:
                # Get granule summary
                url = f"https://api.govinfo.gov/packages/{package_id}/granules/{granule_id}/summary"
            else:
                # Get package summary
                url = f"https://api.govinfo.gov/packages/{package_id}/summary"

            response = await client.get(
                url,
                headers=headers,
                timeout=30.0,
            )
            response.raise_for_status()

            data = response.json()

            # If content type is not summary, extract the download URL
            if content_type != "summary" and "download" in data:
                download_links = data.get("download", {})

                # Map our content types to API response keys
                content_key_map = {
                    "xml": "xmlLink",
                    "pdf": "pdfLink",
                    "text": "txtLink",
                }

                content_key = content_key_map.get(content_type)
                if content_key and content_key in download_links:
                    data["requested_content_url"] = download_links[content_key]
                    data["content_type"] = content_type
                    log(f"Found {content_type} download link for {package_id}")
                else:
                    log(f"No {content_type} content available for {package_id}")

            return data

    except httpx.HTTPStatusError as e:
        msg = f"HTTP error: {e.response.status_code} - {e.response.text}"
        err(msg)
        raise e
    except Exception as e:
        msg = f"Content retrieval error: {e}"
        err(msg)
        raise e


@statutes.tool()
async def list_statute_collections(
    ctx: Context | None = None,
) -> dict[str, Any]:
    """List all available statute-related collections with descriptions.

    Returns information about the statute collections available for search.

    Returns:
        Dict containing statute collections and their descriptions.

    """
    log = ctx.info if ctx else logger.info

    log("Listing available statute collections")

    return {
        "statute_collections": [
            {
                "code": code,
                "name": name,
                "description": _get_collection_description(code),
            }
            for code, name in STATUTE_COLLECTIONS.items()
        ],
        "total_collections": len(STATUTE_COLLECTIONS),
    }


def _get_collection_description(collection_code: str) -> str:
    """Get detailed description for a statute collection.

    Args:
        collection_code: The collection code to get description for.

    Returns:
        Detailed description of the statute collection.

    """
    descriptions = {
        "USCODE": "The United States Code (USC) is the official codification of the general and permanent laws of the United States. It is organized into 54 titles covering broad subject areas.",
        "STATUTE": "The Statutes at Large is the official record of laws enacted by Congress. It contains the text of public and private laws, joint resolutions, and concurrent resolutions.",
        "PLAW": "Public and Private Laws are the individual laws enacted by Congress before they are codified into the United States Code. Public laws affect the general public, while private laws affect specific individuals or entities.",
        "COMPS": "Statutes Compilations contain various compilations and collections of statutes, including subject-specific compilations and historical collections.",
    }
    return descriptions.get(collection_code, "No description available.")
