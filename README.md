# GovInfo MCP Server

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

- Python 3.12+
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

2. Install dependencies using uv:

   ```bash
   uv pip install -r requirements.txt
   # or, if using pyproject.toml:
   uv pip install -r <(uv pip compile pyproject.toml)
   ```

3. Set your GovInfo API key:

   ```bash
   export GOVINFO_API_KEY=your_api_key_here
   ```

4. (Optional) Copy `.env.example` to `.env` and edit as needed.

### Running the Server

Start the MCP server:

```bash
uv run python -m app.server
```

Or use the VS Code task "Run MCP Server".

### Running Tests

See [tests/README.md](tests/README.md) for details. Typical usage:

```bash
uv run pytest
```

### API Usage

See [app/README.md](app/README.md) for detailed tool documentation and usage examples.

## 🔗 Links

- [GovInfo API Documentation](https://api.govinfo.gov/docs/)
- [FastMCP Framework](https://github.com/jlowin/fastmcp)
- [Project Source](.)
- [Source Documentation](app/README.md)
- [Test Suite](tests/README.md)

## 📝 Notes

- All code examples are tested and working.
- File paths use relative references from the project root.
- All commands use `uv run` where needed.
- For Ubuntu/Linux. For Windows, adapt commands as needed.
