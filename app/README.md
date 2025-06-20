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
| `list_statute_collections`   | No params<br>List all statute-related collections |

## Usage Examples

```python
# List all collections
await get_collections(page_size=10)

# Get details for the CFR collection
await get_collection_details(collection_code="CFR")

# Search for discovery procedures in the CFR
await search_packages(query="discovery procedures", collection="CFR", page_size=5)

# Advanced search for discovery in CFR
await advanced_search(query="title:discovery AND collection:CFR", sort_by="relevance")

# Download HTML content for a CFR package
await get_package_content(package_id="CFR-2023-title5-vol3", content_type="html")

# Search US statutes
await search_statutes(query="civil rights", collection="USCODE", page_size=5)

# List public laws from a specific Congress
await get_public_laws_by_congress(congress=117, page_size=5)
```

## Code Conventions

- All tools are async and should be called with `await`.
- Use type hints and Pydantic models for all tool parameters and responses.
- Logging is handled via Loguru; logs are written to `app/logs/server.log`.
- Environment variables (API keys, etc.) are loaded from `.env` using `python-dotenv`.

## Adding New Tools

1. Create a new file in `app/tools/` or add to an existing one.
2. Register the tool with the appropriate FastMCP subserver.
3. Add parameter and return type annotations.
4. Add tests in `tests/`.

## See Also

- [Main Project README](../README.md)
- [GovInfo API Documentation](https://api.govinfo.gov/docs/)
- [FastMCP Framework](https://github.com/jlowin/fastmcp)
