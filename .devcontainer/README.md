# Development Container Configuration

This directory contains all the development-specific Docker configurations for the GovInfo MCP Server project.

## Files

- `devcontainer.json` - VS Code Dev Container configuration
- `Dockerfile` - Development container image for VS Code
- `Dockerfile.dev` - Alternative development image with hot reload
- `docker-compose.yml` - Development services
- `.env.example` - Example environment variables for development

## Usage

### VS Code Dev Container (Recommended)

1. Open the project in VS Code
2. Press `Ctrl+Shift+P` and select "Dev Containers: Reopen in Container"
3. VS Code will build and start the container automatically

### Docker Compose Development

For development without VS Code:

```bash
# Start development services
cd .devcontainer
docker-compose up court-listener-mcp-dev

# Or run in background
docker-compose up -d court-listener-mcp-dev
```

### Environment Setup

1. Copy the example environment file:

   ```bash
   cp .devcontainer/.env.example .env
   ```

2. Modify `.env` as needed for your development environment

## Port Mapping

- `8785` - Production MCP server
- `8786` - Development MCP server (when using docker-compose)

## Development Features

- Hot reload for code changes
- Debug logging enabled
- Full workspace mounted for easy editing
- Docker-in-Docker support for testing
- Poetry environment configured for containers
