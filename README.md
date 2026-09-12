# GovInfo MCP Server

[![Buy Me A Coffee](https://img.shields.io/badge/Buy_Me_A_Coffee-FFDD00?style=flat-square&logo=buy-me-a-coffee&logoColor=black)](https://www.buymeacoffee.com/travisprall)
[![Python 3.14+](https://img.shields.io/badge/python-3.14%2B-blue.svg)](https://www.python.org/downloads/)
[![FastMCP](https://img.shields.io/badge/FastMCP-4.x-6f42c1.svg)](https://gofastmcp.com)
[![License: PolyForm Noncommercial](https://img.shields.io/badge/license-PolyForm%20Noncommercial%201.0.0-orange.svg)](LICENSE.md)

A Model Context Protocol (MCP) server that provides LLM-friendly access to the official GovInfo API v4. This server enables searching and retrieving U.S. government documents, including bills, laws, regulations, and other official publications, for precise legal research and citation verification.

## 🎯 Purpose

The GovInfo MCP Server provides comprehensive access to **federal regulations, statutes, and government documents** through the GovInfo API. It is designed for LLMs and legal research tools to programmatically access up-to-date U.S. government information.

## 📦 Key Features

- Access to bills, statutes, regulations (CFR), and more
- Real-time updates from the official GovInfo API
- Retrieve full document text and metadata in HTML, XML, PDF, or plain text
- Search by keyword, collection, date, and more
- Explore related documents and cross-references

## 🛠️ Available MCP Tools

| Tool Name                    | Description                                      | Example Call |
|-----------------------------|--------------------------------------------------|--------------|
| `get_collections`            | List all available GovInfo collections           | `get_collections(page_size=10)` |
| `get_collection_details`     | Get details for a specific collection            | `get_collection_details(collection_code="CFR")` |
| `search_packages`            | Search packages by query and filters             | `search_packages(query="discovery procedures", collection="CFR", page_size=5)` |
| `advanced_search`            | Advanced search with Lucene syntax and filters   | `advanced_search(query="title:discovery AND collection:CFR", sort_by="relevance")` |
| `get_packages_by_collection` | List packages from a collection                  | `get_packages_by_collection(collection="BILLS", congress=118, page_size=5)` |
| `get_package_summary`        | Get metadata for a specific package              | `get_package_summary(package_id="CFR-2023-title5-vol3")` |
| `get_package_content`        | Download package content in various formats      | `get_package_content(package_id="CFR-2023-title5-vol3", content_type="html")` |
| `get_published_packages`     | Get packages published on a specific date        | `get_published_packages(date_issued="2024-01-15", collection="CFR")` |
| `get_published_range`        | Get packages published within a date range       | `get_published_range(start_date="2024-01-01", end_date="2024-01-31", collection="PLAW")` |
| `get_related_packages`       | Find packages related to a specific package      | `get_related_packages(package_id="BILLS-118hr1234-ih")` |
| `get_granule_related`        | Find items related to a specific granule         | `get_granule_related(package_id="CFR-2023-title5-vol3", granule_id="CFR-2023-title5-vol3-sec1201-72")` |
| `search_statutes`            | Search US statutes across statute collections    | `search_statutes(query="civil rights", collection="USCODE", page_size=5)` |
| `get_public_laws_by_congress`| List public laws from a specific Congress        | `get_public_laws_by_congress(congress=117, page_size=5)` |
| `get_statutes_at_large`      | Search Statutes at Large by volume               | `get_statutes_at_large(volume="137", page_size=5)` |
| `get_uscode_title`           | Search US Code sections within a title           | `get_uscode_title(title_number="42", page_size=5)` |
| `list_statute_collections`   | List all statute-related collections             | `list_statute_collections()` |

See [app/README.md](app/README.md) for full tool parameter documentation.

## 🚀 Setup

### Prerequisites

- Python 3.14+
- [uv](https://github.com/astral-sh/uv) for dependency management (Poetry is NOT used)
- Internet connection for GovInfo API access
- GovInfo API key (set `GOVINFO_API_KEY` in your environment)
- Ubuntu/Linux recommended (all commands below are for bash)

### Installation

1. Clone the repository and navigate to the GovInfo project directory:

   ```bash
   git clone <repository-url>
   cd GovInfo
   ```

2. Install dependencies (creates a project-local `.venv` from the committed `uv.lock`):

   ```bash
   uv sync
   ```

3. Set your GovInfo API key:

   ```bash
   export GOVINFO_API_KEY=your_api_key_here
   ```

4. (Optional) Copy `.env.example` to `.env` and edit as needed.

### Running the Server

By default the server speaks STDIO, which is what most local MCP clients expect:

```bash
uv run python -m app.server
```

Or use the VS Code task "Run MCP Server".

#### Streamable HTTP (standalone Linux service)

To run the server as a networked ASGI service, either start the exported app
with Uvicorn:

```bash
uv run uvicorn app.server:app --host 0.0.0.0 --port 8775
```

or let the entry point select the transport:

```bash
MCP_TRANSPORT=http MCP_HOST=0.0.0.0 MCP_PORT=8775 uv run python -m app.server
```

The MCP endpoint is then `http://<host>:8775/mcp` and the operational health
probe is `http://<host>:8775/health`. For horizontally scaled deployments set
`FASTMCP_STATELESS_HTTP=true` (or `MCP_STATELESS_HTTP=true`); to enable
Host/Origin request protection set `MCP_ALLOWED_HOSTS`/`MCP_ALLOWED_ORIGINS`,
and to allow specific browser origins set `MCP_CORS_ALLOW_ORIGINS`.

#### Docker

```bash
docker compose up --build
```

The container serves Streamable HTTP on port `8775` and exposes `/health` for
its `HEALTHCHECK`.

### Running Tests

See [tests/README.md](tests/README.md) for details. Typical usage:

```bash
uv run pytest
```

### API Usage

See [app/README.md](app/README.md) for detailed tool documentation and usage examples.

## 🔗 Links

- [GovInfo API Documentation](https://api.govinfo.gov/docs/)
- [FastMCP Documentation](https://gofastmcp.com)
- [FastMCP Repository](https://github.com/PrefectHQ/fastmcp)
- [Project Source](.)
- [Source Documentation](app/README.md)
- [Test Suite](tests/README.md)

## 📝 Notes

- All code examples are tested and working.
- File paths use relative references from the project root.
- All commands use `uv run` where needed.
- For Ubuntu/Linux. For Windows, adapt commands as needed.

## 💖 Support

This project is maintained by [travisprall](https://github.com/travisprall). It is free to use, and support is always optional — but if it saves you time, a coffee is very much appreciated:

[![Buy Me A Coffee](https://img.shields.io/badge/Buy_Me_A_Coffee-FFDD00?style=flat-square&logo=buy-me-a-coffee&logoColor=black)](https://www.buymeacoffee.com/travisprall)

- ☕ [Buy me a coffee](https://www.buymeacoffee.com/travisprall)
- 💜 [Sponsor on GitHub](https://github.com/sponsors/travisprall)

## 📄 License

Copyright © travisprall.

Released under the [PolyForm Noncommercial License 1.0.0](LICENSE.md) (SPDX: `PolyForm-Noncommercial-1.0.0`). Noncommercial use is permitted; commercial use requires a separate license.

## 📚 Citation

If you use this software in research, please cite it using the metadata in [CITATION.cff](CITATION.cff).

