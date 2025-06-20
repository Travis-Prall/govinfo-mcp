# GovInfo MCP Server - Source Documentation

A Model Context Protocol (MCP) server for accessing the official GovInfo API v4. This server provides LLM-friendly access to U.S. government documents, including bills, laws, regulations, and more.

## Architecture Overview

- **FastMCP**: Main server framework for tool registration and async execution
- **Loguru**: Logging for server and tool operations
- **Tools**: Each tool category (collections, packages, published, related, search, statutes) is implemented as a FastMCP subserver in `app/tools/`
- **Configuration**: Environment variables (via `.env` and `python-dotenv`) for API keys and settings
- **Tests**: Comprehensive test suite in `tests/`

### Code Structure

```
app/
├── server.py          # Main FastMCP server, imports and registers all tool servers
├── models.py          # Pydantic data models for API responses
├── config.py          # Configuration and environment variable helpers
├── exceptions.py      # Custom exception classes for error handling
├── monitoring.py      # Server health and monitoring utilities
├── rate_limiter.py    # Rate limiting logic for API calls
├── utils.py           # Shared utility functions
├── tools/
│   ├── collections.py # Tools for listing and describing GovInfo collections
│   ├── packages.py    # Tools for accessing and downloading document packages
│   ├── published.py   # Tools for finding recently published documents
│   ├── related.py     # Tools for finding related packages and granules
│   ├── search.py      # Tools for searching packages and advanced queries
│   └── statutes.py    # Tools for searching and retrieving US statutes
└── logs/              # Server log files
```

## Module Guide

| Module                  | Purpose                                                      |
|------------------------|--------------------------------------------------------------|
| `server.py`            | Main FastMCP server, imports and registers all tool servers  |
| `models.py`            | Pydantic data models for API responses                       |
| `config.py`            | Configuration and environment variable helpers               |
| `exceptions.py`        | Custom exception classes for error handling                  |
| `monitoring.py`        | Server health and monitoring utilities                      |
| `rate_limiter.py`      | Rate limiting logic for API calls                           |
| `utils.py`             | Shared utility functions                                     |
| `tools/collections.py` | Tools for listing and describing GovInfo collections         |
| `tools/packages.py`    | Tools for accessing and downloading document packages        |
| `tools/published.py`   | Tools for finding recently published documents               |
| `tools/related.py`     | Tools for finding related packages and granules              |
| `tools/search.py`      | Tools for searching packages and advanced queries            |
| `tools/statutes.py`    | Tools for searching and retrieving US statutes               |
| `logs/`                | Server log files                                             |

## Available MCP Tools

| Tool Name                    | Parameters & Description |
|-----------------------------|-------------------------|
| `get_collections`            | `page_size` (int, default 50), `offset_mark` (str, default '*')<br>List all available GovInfo collections |
| `get_collection_details`     | `collection_code` (str)<br>Get details for a specific collection |
| `search_packages`            | `query` (str), `collection` (str), `page_size` (int), ...<br>Search packages by query and filters |
| `advanced_search`            | `query` (str), `collections` (list), `sort_by` (str), ...<br>Advanced search with Lucene syntax and filters |
| `get_packages_by_collection` | `collection` (str), `congress` (int), `page_size` (int), ...<br>List packages from a collection |
| `get_package_summary`        | `package_id` (str)<br>Get metadata for a specific package |
| `get_package_content`        | `package_id` (str), `content_type` (str)<br>Download package content in various formats |
| `get_published_packages`     | `date_issued` (str), `collection` (str), ...<br>Get packages published on a specific date |
| `get_published_range`        | `start_date` (str), `end_date` (str), `collection` (str), ...<br>Get packages published within a date range |
| `get_related_packages`       | `package_id` (str)<br>Find packages related to a specific package |
| `get_granule_related`        | `package_id` (str), `granule_id` (str)<br>Find items related to a specific granule |
| `search_statutes`            | `query` (str), `collection` (str), `title_number` (str), ...<br>Search US statutes across statute collections |
| `get_public_laws_by_congress`| `congress` (int), ...<br>List public laws from a specific Congress |
| `get_statutes_at_large`      | `volume` (str), ...<br>Search Statutes at Large by volume |
| `get_uscode_title`           | `title_number` (str), ...<br>Search US Code sections within a title |
| `list_statute_collections`   | None<br>List all statute-related collections |

## Example Usage

```python
from fastmcp import Client
from app.server import mcp

client = Client(mcp)

# Example: List collections
result = await client.call_tool("get_collections", {"page_size": 5})

# Example: Search packages
result = await client.call_tool("search_packages", {"query": "civil rights", "collection": "USCODE", "page_size": 3})

# Example: Get package content
result = await client.call_tool("get_package_content", {"package_id": "CFR-2023-title5-vol3", "content_type": "html"})
```

## Common Use Cases

- List all available document collections
- Search for regulations or statutes by keyword
- Download the full text of a law or regulation
- Find related bills, laws, or regulatory sections
- Retrieve recently published government documents

## Notes

- All tools require a valid `GOVINFO_API_KEY` in your environment.
- All code examples are tested and working.
- File paths use relative references from the project root.
- For more, see [../README.md](../README.md).
