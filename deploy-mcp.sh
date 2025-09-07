#!/bin/bash
# Deploy LiteLLM with MCP integration

echo "=== Deploying LiteLLM with MCP Integration ==="
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Stop existing container
echo -e "${YELLOW}Stopping existing LiteLLM container...${NC}"
docker stop litellm 2>/dev/null || true
docker rm litellm 2>/dev/null || true

# Copy MCP handler into container build context
echo -e "${YELLOW}Preparing MCP handler...${NC}"
cp litellm_mcp_handler.py /tmp/litellm_mcp_handler.py 2>/dev/null || true
cp mcp-functions.yaml /tmp/mcp-functions.yaml 2>/dev/null || true

# Create a custom entrypoint script
cat > /tmp/litellm-entrypoint.sh << 'EOF'
#!/bin/sh
# Custom entrypoint for LiteLLM with MCP

# Copy MCP handler if it exists
if [ -f /tmp/litellm_mcp_handler.py ]; then
    cp /tmp/litellm_mcp_handler.py /app/litellm_mcp_handler.py
fi

if [ -f /tmp/mcp-functions.yaml ]; then
    cp /tmp/mcp-functions.yaml /app/mcp-functions.yaml
fi

# Set Python path to include app directory
export PYTHONPATH=/app:$PYTHONPATH

# Add admin keys to environment
export MCP_ADMIN_KEYS="sk-pFgey4HPR9qDvyT-N_7yVQ"

# Start LiteLLM with config
exec litellm --config /app/config.yaml --port 4000
EOF

chmod +x /tmp/litellm-entrypoint.sh

# Load environment variables
source /home/administrator/secrets/litellm.env

# Start new container with MCP support
echo -e "${YELLOW}Starting LiteLLM with MCP integration...${NC}"
docker run -d \
  --name litellm \
  --hostname litellm \
  --network litellm-net \
  --restart unless-stopped \
  -p 127.0.0.1:4000:4000 \
  -v /home/administrator/projects/litellm/config-mcp-enabled.yaml:/app/config.yaml:ro \
  -v /tmp/litellm_mcp_handler.py:/tmp/litellm_mcp_handler.py:ro \
  -v /tmp/mcp-functions.yaml:/tmp/mcp-functions.yaml:ro \
  -v /tmp/litellm-entrypoint.sh:/entrypoint.sh:ro \
  --env-file /home/administrator/secrets/litellm.env \
  -e MCP_ADMIN_KEYS="sk-pFgey4HPR9qDvyT-N_7yVQ" \
  -e PYTHONPATH="/app" \
  --entrypoint /entrypoint.sh \
  --label "traefik.enable=true" \
  --label "traefik.http.routers.litellm.rule=Host(\`litellm.ai-servicers.com\`)" \
  --label "traefik.http.routers.litellm.entrypoints=websecure" \
  --label "traefik.http.routers.litellm.tls=true" \
  --label "traefik.http.routers.litellm.tls.certresolver=letsencrypt" \
  --label "traefik.http.services.litellm.loadbalancer.server.port=4000" \
  ghcr.io/berriai/litellm:main-stable

# Connect to additional networks
echo -e "${YELLOW}Connecting to additional networks...${NC}"
docker network connect traefik-proxy litellm 2>/dev/null || true
docker network connect postgres-net litellm 2>/dev/null || true
docker network connect redis-net litellm 2>/dev/null || true

# Wait for startup
echo -e "${YELLOW}Waiting for LiteLLM to start...${NC}"
sleep 10

# Check if running
if docker ps | grep -q litellm; then
    echo -e "${GREEN}✓ LiteLLM is running${NC}"
    
    # Check logs for errors
    echo ""
    echo -e "${YELLOW}Recent logs:${NC}"
    docker logs litellm --tail 20
    
    # Test health endpoint
    echo ""
    echo -e "${YELLOW}Testing health endpoint...${NC}"
    if curl -s http://localhost:4000/health | grep -q "healthy"; then
        echo -e "${GREEN}✓ Health check passed${NC}"
    else
        echo -e "${RED}✗ Health check failed${NC}"
    fi
    
    # Test MCP connectivity
    echo ""
    echo -e "${YELLOW}Testing MCP proxy connectivity...${NC}"
    if docker exec litellm wget -qO- --timeout=2 http://mcp-proxy-sse:8080/servers 2>/dev/null | grep -q "filesystem"; then
        echo -e "${GREEN}✓ MCP proxy is reachable${NC}"
    else
        echo -e "${RED}✗ Cannot reach MCP proxy${NC}"
    fi
    
else
    echo -e "${RED}✗ LiteLLM failed to start${NC}"
    echo "Check logs: docker logs litellm"
    exit 1
fi

echo ""
echo -e "${GREEN}=== Deployment Complete ===${NC}"
echo ""
echo "LiteLLM with MCP integration is now running!"
echo ""
echo "Test MCP tools:"
echo "  ./test-openwebui-mcp.sh"
echo ""
echo "Or test in Open WebUI:"
echo "  1. Go to https://open-webui.ai-servicers.com"
echo "  2. Select a model (e.g., gpt-4o-mini)"
echo "  3. Try: 'List PostgreSQL databases' or 'Get logs from litellm container'"