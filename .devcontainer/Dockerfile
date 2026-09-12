# Use the official Python 3.14 dev container (pinned digest)
FROM mcr.microsoft.com/devcontainers/python:3.14@sha256:3b3c45535947751e9dfcd513ef5bee858d221844f55e278e92d1cd8f5b1f2972

ENV PYTHONUNBUFFERED=1 \
    PYTHONPATH=/workspaces/GovInfo

# Install uv using pipx (already available in base image)
RUN pipx install uv && pipx ensurepath

# -------------------------------------------------------------------
# Install project dependencies as root BEFORE switching to `vscode`
# -------------------------------------------------------------------
# Copy only the dependency manifests so Docker cache works efficiently
COPY pyproject.toml uv.lock /tmp/GovInfo/

RUN cd /tmp/GovInfo \
  && uv sync \
  # Clean build artefacts
  && rm -rf ~/.cache/pip /tmp/GovInfo

# Ensure the workspace directory exists and is writable by `vscode`
RUN mkdir -p /workspaces/GovInfo && chown -R vscode:vscode /workspaces

# -------------------------------------------------------------------
# Normal non-root developer user from here on
# -------------------------------------------------------------------
USER vscode

# Set working directory
WORKDIR /workspaces/GovInfo

# Note: Dependencies will be installed via postCreateCommand in devcontainer.json
# The workspace will be mounted, so no need to COPY files
