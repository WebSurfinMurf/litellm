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

# The entrypoint and configuration are inherited from base image
WORKDIR /app