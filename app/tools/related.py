"""Related tools for GovInfo MCP server."""

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

# Create the related server
related_server = FastMCP("RelatedServer")


@related_server.tool()
async def get_related_packages(
    package_id: Annotated[
        str,
        Field(
            description="Package ID to find related packages for (e.g., 'BILLS-116hr1-ih')"
        ),
    ],
    ctx: Context | None = None,
) -> dict:
    """Get packages related to a specific package.

    Returns a list of packages that are related to the specified package,
    such as different versions of a bill, related congressional reports,
    or other associated documents.

    Returns:
        Dictionary containing related packages information, or an error dict if API key is missing.

    """
    if ctx:
        await ctx.info(f"Fetching related packages for: {package_id}")
    else:
        logger.info(f"Fetching related packages for: {package_id}")

    if not API_KEY:
        error_msg = "GOVINFO_API_KEY not found in environment variables"
        if ctx:
            await ctx.error(error_msg)
        else:
            logger.error(error_msg)
        return {"error": error_msg}

    headers = {"X-Api-Key": API_KEY}

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"https://api.govinfo.gov/related/{package_id}",
                headers=headers,
                timeout=30.0,
            )
            response.raise_for_status()

            data = response.json()

            if ctx:
                await ctx.info(
                    f"Found {len(data.get('relatedPackages', []))} related packages"
                )
            else:
                logger.info(
                    f"Found {len(data.get('relatedPackages', []))} related packages"
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
        error_msg = f"Related packages fetch error: {e}"
        if ctx:
            await ctx.error(error_msg)
        else:
            logger.error(error_msg)
        raise e


@related_server.tool()
async def get_granule_related(
    package_id: Annotated[
        str, Field(description="Package ID (e.g., 'CFR-2023-title12-vol1')")
    ],
    granule_id: Annotated[str, Field(description="Granule ID within the package")],
    ctx: Context | None = None,
) -> dict:
    """Get related items for a specific granule within a package.

    Returns related granules or documents that are associated with the specified
    granule, such as related sections, amendments, or cross-references.

    Returns:
        Dictionary containing related items for the specified granule.

    """
    if ctx:
        await ctx.info(
            f"Fetching related items for granule {granule_id} in package {package_id}"
        )
    else:
        logger.info(
            f"Fetching related items for granule {granule_id} in package {package_id}"
        )

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
                f"https://api.govinfo.gov/related/{granule_id}",
                headers=headers,
                timeout=30.0,
            )
            response.raise_for_status()

            data = response.json()

            if ctx:
                await ctx.info(f"Retrieved related items for granule {granule_id}")
            else:
                logger.info(f"Retrieved related items for granule {granule_id}")

            return data

    except httpx.HTTPStatusError as e:
        error_msg = f"HTTP error: {e}"
        if ctx:
            await ctx.error(error_msg)
        else:
            logger.error(error_msg)
        raise e
    except Exception as e:
        error_msg = f"Granule related fetch error: {e}"
        if ctx:
            await ctx.error(error_msg)
        else:
            logger.error(error_msg)
        raise e
