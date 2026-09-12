# syntax=docker/dockerfile:1.7

# ---------------------------------------------------------------------------
# Stage 1: build the virtual environment with uv
# ---------------------------------------------------------------------------
FROM python:3.14-slim@sha256:cad9a2c871761c413caa6fdd6441c783451e740a48aaeba60ae62a8b53525ef6 AS builder

# Pin uv to a known-good release for reproducible dependency resolution.
ARG UV_VERSION=0.12.12

WORKDIR /app

# build-essential + libffi-dev are only needed when a dependency (e.g. cffi)
# must be compiled from source and never ship in the final image.
RUN apt-get update \
    && apt-get install --no-install-recommends -y build-essential libffi-dev \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir "uv==${UV_VERSION}"

# Copy dependency manifests first so the dependency layer is cached.
COPY pyproject.toml uv.lock ./

# Install runtime dependencies only - the project itself is copied into the
# final stage. The lockfile is respected exactly (--frozen).
RUN uv sync --frozen --no-dev --no-install-project

# ---------------------------------------------------------------------------
# Stage 2: minimal, hardened runtime image
# ---------------------------------------------------------------------------
FROM python:3.14-slim@sha256:cad9a2c871761c413caa6fdd6441c783451e740a48aaeba60ae62a8b53525ef6 AS runtime

# OCI image metadata
LABEL org.opencontainers.image.title="GovInfo MCP Server" \
      org.opencontainers.image.description="Model Context Protocol server for the GovInfo API v4" \
      org.opencontainers.image.version="0.2.0" \
      org.opencontainers.image.licenses="PolyForm-Noncommercial-1.0.0" \
      org.opencontainers.image.source="https://github.com/Travis-Prall/GovInfo" \
      org.opencontainers.image.authors="Travis-Prall"

# Create an unprivileged user before copying anything into the image.
RUN groupadd --system --gid 1001 govinfo \
    && useradd --system --uid 1001 --gid govinfo --create-home govinfo

# Copy the pre-built virtual environment and dependency manifests.
COPY --from=builder --chown=govinfo:govinfo /app/.venv /app/.venv
COPY --from=builder --chown=govinfo:govinfo /app/pyproject.toml /app/uv.lock /app/

# Application code and license.
WORKDIR /src
COPY --chown=govinfo:govinfo app /src/app
COPY --chown=govinfo:govinfo LICENSE.md /src/LICENSE.md

# Runtime configuration. The default transport is Streamable HTTP so the
# container behaves as a networked service out of the box.
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/src \
    PATH="/app/.venv/bin:$PATH" \
    LOG_LEVEL=INFO \
    LOG_FORMAT=json \
    API_BASE_URL=https://www.govinfo.gov/api/rest/v4 \
    MCP_TRANSPORT=http \
    MCP_HOST=0.0.0.0 \
    MCP_PORT=8775

# Run as the non-root user.
USER govinfo

# Streamable HTTP endpoint (/mcp) plus the operational /health route.
EXPOSE 8775

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import sys, urllib.request; sys.exit(0 if urllib.request.urlopen('http://127.0.0.1:8775/health', timeout=3).status == 200 else 1)"

# Serve the FastMCP Streamable HTTP ASGI app from the locked virtualenv
# (equivalent to: uvicorn app.server:app --host 0.0.0.0 --port 8775).
CMD ["python", "-m", "app.server"]

