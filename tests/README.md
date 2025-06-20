# GovInfo MCP Server - Test Suite Documentation

This directory contains all tests for the GovInfo MCP Server. The test suite ensures all MCP tools and server features work as expected.

## Running Tests

- **With uv (recommended):**
  ```bash
  uv run pytest
  ```
- **With coverage:**
  ```bash
  uv run pytest --cov=app --cov-report=term-missing
  ```
- **Run a specific test file:**
  ```bash
  uv run pytest tests/test_govinfo_server.py
  ```

> **Note:** Poetry is NOT used. All commands assume Ubuntu/Linux and the [uv](https://github.com/astral-sh/uv) package manager.

## Test Structure

- `test_govinfo_server.py` - Main unit and integration tests for the MCP server and tools
- `test_statutes.py` - Statutes tool tests (unit and async)
- `test_statutes_integration.py` - Integration tests for statutes tools
- `test_statutes_new.py` - Additional/experimental statutes tool tests
- `test_packages_comprehensive.py` - Comprehensive tests for packages and related tools
- `test_config.py` - Pytest configuration and fixtures
- `test_runner.py` - Script for running all tests with logging and coverage
- `test_logs/` - Test log output

## Coverage Requirements

- All MCP tools must have at least one test
- Target: 90%+ code coverage (see coverage report after running tests)
- Remove any duplicate test cases
- Test names must be descriptive and use `test_*` convention
- All async tools must be tested with `pytest-asyncio`
- Mock data should match current GovInfo API responses

## Troubleshooting

- **Import errors:**
  - Ensure you are running tests with `uv run pytest` so dependencies are available
- **API/network errors:**
  - Check your `GOVINFO_API_KEY` and internet connection
- **Test failures:**
  - Run with `-s -vv` for verbose output: `uv run pytest -s -vv`
  - Check logs in `tests/logs/test.log`
- **Coverage not reported:**
  - Ensure you use `--cov=app` and that `pytest-cov` is installed
- **Async test issues:**
  - Make sure `pytest-asyncio` is installed and used for async tests
- **Duplicate tests:**
  - Remove or consolidate any duplicate test cases

For more details, see the main [README.md](../README.md).
