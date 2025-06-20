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

| Tool Name                | Description                                      | Example Call |
|-------------------------|--------------------------------------------------|--------------|
| `get_collections`       | List all available GovInfo collections           | `get_collections(page_size=10)` |
| `get_collection_details`| Get details for a specific collection            | `get_collection_details(collection_code="CFR")` |
| `search_packages`       | Search packages by query and filters             | `search_packages(query="discovery procedures", collection="CFR", page_size=5)` |
| `advanced_search`       | Advanced search with Lucene syntax and filters   | `advanced_search(query="title:discovery AND collection:CFR", sort_by="relevance")` |
| `get_packages_by_collection` | List packages from a collection              | `get_packages_by_collection(collection="BILLS", congress=118, page_size=5)` |
| `get_package_summary`   | Get metadata for a specific package              | `get_package_summary(package_id="CFR-2023-title5-vol3")` |
| `get_package_content`   | Download package content in various formats      | `get_package_content(package_id="CFR-2023-title5-vol3", content_type="html")` |
| `get_published_packages`| Get packages published on a specific date        | `get_published_packages(date_issued="2024-01-15", collection="CFR")` |
| `get_published_range`   | Get packages published within a date range       | `get_published_range(start_date="2024-01-01", end_date="2024-01-31", collection="PLAW")` |
| `get_related_packages`  | Find packages related to a specific package      | `get_related_packages(package_id="BILLS-118hr1234-ih")` |
| `get_granule_related`   | Find items related to a specific granule         | `get_granule_related(package_id="CFR-2023-title5-vol3", granule_id="CFR-2023-title5-vol3-sec1201-72")` |
| `search_statutes`       | Search US statutes across statute collections    | `search_statutes(query="civil rights", collection="USCODE", page_size=5)` |
| `get_public_laws_by_congress` | List public laws from a specific Congress   | `get_public_laws_by_congress(congress=117, page_size=5)` |
| `get_statutes_at_large` | Search Statutes at Large by volume               | `get_statutes_at_large(volume="137", page_size=5)` |
| `get_uscode_title`      | Search US Code sections within a title           | `get_uscode_title(title_number="42", page_size=5)` |
| `list_statute_collections` | List all statute-related collections           | `list_statute_collections()` |

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
   uv sync
   ```

3. (Optional) Activate the uv shell:

   ```bash
   uv shell
   ```

### Environment Configuration

Create a `.env` file in the project root and set your GovInfo API key:

```env
GOVINFO_API_KEY=your_api_key_here
```

## 💡 Usage Examples

```python
# List all collections
get_collections(page_size=10)

# Get details for the CFR collection
get_collection_details(collection_code="CFR")

# Search for discovery procedures in the CFR
search_packages(query="discovery procedures", collection="CFR", page_size=5)

# Advanced search for discovery in CFR
advanced_search(query="title:discovery AND collection:CFR", sort_by="relevance")

# Download HTML content for a CFR package
get_package_content(package_id="CFR-2023-title5-vol3", content_type="html")
```

## 🐳 Docker Setup

### Quick Start with Docker

```bash
# Production mode
docker-compose up -d

# Development mode with hot reload
docker-compose --profile dev up --build
```

## 🧪 Testing

### Running Tests

```bash
uv run pytest
uv run pytest --cov=app --cov-report=term-missing
uv run pytest tests/test_govinfo_server.py
```

See [`tests/README.md`](tests/README.md) for detailed testing documentation.

## 🔧 Development

### Project Structure

```
GovInfo/
├── app/                    # Source code
│   ├── server.py          # FastMCP server with all tools
│   ├── models.py          # Pydantic data models
│   ├── __init__.py        # Package initialization
│   └── logs/              # Server logs
├── tests/                 # Test suite
│   ├── test_govinfo_server.py # Unit tests
│   ├── test_statutes.py   # Statutes tool tests
│   ├── test_statutes_integration.py # Statutes integration tests
│   ├── test_config.py     # Test configuration
│   ├── test_runner.py     # Test runner script
│   └── logs/              # Test logs
├── docker-compose.yml     # Docker orchestration
├── Dockerfile*            # Docker configurations
├── pyproject.toml         # uv dependencies
├── context.json           # Project metadata
└── README.md              # This file
```

### Code Quality

```bash
uv run ruff format .
uv run ruff check .
uv run mypy app/
uv run pip-audit
```

## 🚨 Troubleshooting

- **Import errors:** Ensure you are running tests with `uv run pytest` so dependencies are available
- **API/network errors:** Check your `GOVINFO_API_KEY` and internet connection
- **Test failures:** Run with `-s -vv` for verbose output: `uv run pytest -s -vv`
- **Coverage not reported:** Ensure you use `--cov=app` and that `pytest-cov` is installed

## 📚 Additional Resources

- **[Source Code Documentation](app/README.md)** - Detailed code architecture
- **[Test Documentation](tests/README.md)** - Testing guide and coverage
- **[Project Context](context.json)** - Machine-readable project metadata
- **[GovInfo API Documentation](https://api.govinfo.gov/docs/)** - Official GovInfo API docs
- **[FastMCP Framework](https://github.com/jlowin/fastmcp)** - MCP server framework

## 📄 License

This project is open source. See license information in the repository.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Run the test suite
6. Submit a pull request

---

**🎯 Ready to use!** The GovInfo MCP Server provides production-ready access to federal regulations and statutes through comprehensive MCP tools.
