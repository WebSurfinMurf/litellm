#!/bin/bash
# Deploy LiteLLM with MCP callback handler

echo "=== Deploying LiteLLM with MCP Integration ==="

# Stop existing container
echo "Stopping existing LiteLLM container..."
docker stop litellm 2>/dev/null && docker rm litellm 2>/dev/null

# Create custom Dockerfile for LiteLLM with MCP handler
cat > /tmp/Dockerfile.litellm-mcp << 'DOCKERFILE'
FROM ghcr.io/berriai/litellm:main-stable

# Install additional Python packages needed for MCP
RUN pip install aiohttp pyyaml

# Copy MCP handler and functions config
COPY litellm_mcp_handler.py /app/litellm_mcp_handler.py
COPY mcp-functions.yaml /app/mcp-functions.yaml

# Set Python path to include app directory
ENV PYTHONPATH=/app:$PYTHONPATH
ENV MCP_ADMIN_KEYS="sk-pFgey4HPR9qDvyT-N_7yVQ"

WORKDIR /app
DOCKERFILE

# Build custom image
echo "Building custom LiteLLM image with MCP support..."
cd /home/administrator/projects/litellm
docker build -f /tmp/Dockerfile.litellm-mcp -t litellm-mcp:latest .

# Source environment variables
source /home/administrator/secrets/litellm.env

# Run with MCP-enabled configuration
echo "Starting LiteLLM with MCP integration..."
docker run -d \
  --name litellm \
  --hostname litellm \
  --network litellm-net \
  --restart unless-stopped \
  -p 127.0.0.1:4000:4000 \
  -v /home/administrator/projects/litellm/config-mcp-enabled.yaml:/app/config.yaml:ro \
  --env-file /home/administrator/secrets/litellm.env \
  -e MCP_ADMIN_KEYS="sk-pFgey4HPR9qDvyT-N_7yVQ" \
  -e PYTHONPATH="/app" \
  --label "traefik.enable=true" \
  --label "traefik.http.routers.litellm.rule=Host(\`litellm.ai-servicers.com\`)" \
  --label "traefik.http.routers.litellm.entrypoints=websecure" \
  --label "traefik.http.routers.litellm.tls=true" \
  --label "traefik.http.routers.litellm.tls.certresolver=letsencrypt" \
  --label "traefik.http.services.litellm.loadbalancer.server.port=4000" \
  litellm-mcp:latest \
  --config /app/config.yaml --port 4000

# Connect to additional networks
echo "Connecting to additional networks..."
docker network connect traefik-proxy litellm 2>/dev/null || true
docker network connect postgres-net litellm 2>/dev/null || true
docker network connect redis-net litellm 2>/dev/null || true

echo "Waiting for LiteLLM to start..."
sleep 10

# Check if running
if docker ps | grep -q litellm; then
    echo "✓ LiteLLM is running"
    
    # Test health endpoint
    if curl -s http://localhost:4000/health | grep -q "healthy"; then
        echo "✓ Health check passed"
    else
        echo "✗ Health check failed"
    fi
    
    # Test MCP connectivity
    if docker exec litellm wget -qO- --timeout=2 http://mcp-proxy-sse:8080/servers 2>/dev/null | grep -q "filesystem"; then
        echo "✓ MCP proxy is reachable"
    else
        echo "✗ Cannot reach MCP proxy"
    fi
else
    echo "✗ LiteLLM failed to start"
    echo "Check logs: docker logs litellm"
    exit 1
fi

echo ""
echo "=== Deployment Complete ==="
echo "LiteLLM with MCP integration is now running!"
echo ""
echo "Test with: python3 /home/administrator/projects/litellm/test-mcp-integration.py"