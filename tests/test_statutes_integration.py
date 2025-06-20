"""Integration test for the US Statutes MCP server to validate the tools work properly."""

import asyncio
import os

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Test the underlying function implementations directly
import sys

sys.path.append("/workspaces/GovInfo")

# Import the functions directly (not the decorated tools)
from app.tools.statutes import (
    _get_collection_description,
    get_public_laws_by_congress,
    get_statutes_at_large,
    get_uscode_title,
    list_statute_collections,
    search_statutes,
)


async def main():
    """Test the statutes functions directly."""
    print("Testing US Statutes Server Functions")
    print("=" * 50)

    # Check API key
    if not os.getenv("GOVINFO_API_KEY"):
        print("ERROR: GOVINFO_API_KEY not found.")
        return

    try:
        # Test list_statute_collections (synchronous function)
        print("1. Testing list_statute_collections...")
        collections = await list_statute_collections()
        print(f"   Collections found: {len(collections['statute_collections'])}")
        for collection in collections["statute_collections"]:
            print(f"   - {collection['code']}: {collection['name']}")

        # Test search_statutes
        print("\n2. Testing search_statutes...")
        results = await search_statutes("civil rights", page_size=3)
        print(f"   Search results: {results.get('count', 0)} total")
        if results.get("packages"):
            print(f"   First result: {results['packages'][0].get('packageId', 'N/A')}")

        # Test search with specific collection
        print("\n3. Testing search_statutes with USCODE collection...")
        uscode_results = await search_statutes(
            "civil rights", collection="USCODE", page_size=3
        )
        print(f"   USCODE results: {uscode_results.get('count', 0)} total")

        # Test get_uscode_title
        print("\n4. Testing get_uscode_title...")
        title_results = await get_uscode_title("42", page_size=3)
        print(f"   Title 42 results: {title_results.get('count', 0)} total")

        # Test get_public_laws_by_congress
        print("\n5. Testing get_public_laws_by_congress...")
        law_results = await get_public_laws_by_congress(117, page_size=3)
        print(f"   117th Congress laws: {law_results.get('count', 0)} total")

        # Test get_statutes_at_large
        print("\n6. Testing get_statutes_at_large...")
        stat_results = await get_statutes_at_large("137", page_size=3)
        print(f"   Statutes at Large Vol 137: {stat_results.get('count', 0)} total")

        # Test helper function
        print("\n7. Testing _get_collection_description...")
        desc = _get_collection_description("USCODE")
        print(f"   USCODE description: {desc[:100]}...")

        print("\n" + "=" * 50)
        print("All function tests completed successfully! ✓")

    except Exception as e:
        print(f"\n❌ Error during testing: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
