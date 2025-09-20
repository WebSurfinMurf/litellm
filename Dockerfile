# Custom LiteLLM image with MCP runtime support
FROM ghcr.io/berriai/litellm-database:main-stable

# Install runtimes needed for MCP servers
RUN apk add --no-cache \
    nodejs \
    npm \
    docker-cli \
    git \
    bash

# Install global npm packages that some MCP servers need
RUN npm install -g npx

# Preinstall frequently used MCP servers to avoid runtime downloads
RUN npm install -g @henkey/postgres-mcp-server @modelcontextprotocol/server-filesystem

# Ensure LiteLLM includes the latest MCP Gateway features
RUN python -m pip install --no-cache-dir --upgrade "litellm>=1.77.1" colorama

# The entrypoint and configuration are inherited from base image
WORKDIR /app
