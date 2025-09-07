#!/bin/bash
# Deploy LiteLLM with network isolation for MCP security
# MCP proxy only accessible via litellm-net Docker network

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "=== LiteLLM Secure Deployment ==="
echo "Mode: Network Isolated MCP Access"
echo "Security: MCP proxy only accessible via Docker network"
echo ""

# Ensure networks exist
echo "Creating required networks..."
docker network create litellm-net 2>/dev/null || echo "Network litellm-net already exists"
docker network create traefik-proxy 2>/dev/null || echo "Network traefik-proxy already exists"
docker network create postgres-net 2>/dev/null || echo "Network postgres-net already exists"
docker network create redis-net 2>/dev/null || echo "Network redis-net already exists"
docker network create keycloak-net 2>/dev/null || echo "Network keycloak-net already exists"

# Check if config file exists
if [ ! -f "${SCRIPT_DIR}/config.yaml" ]; then
    echo "ERROR: config.yaml not found!"
    echo "Please ensure config.yaml exists in ${SCRIPT_DIR}"
    exit 1
fi

# Check if env file exists
if [ ! -f "/home/administrator/secrets/litellm.env" ]; then
    echo "ERROR: litellm.env not found!"
    echo "Please ensure litellm.env exists in /home/administrator/secrets/"
    exit 1
fi

# Deploy using docker compose
echo "Deploying LiteLLM with docker compose..."
cd ${SCRIPT_DIR}
docker compose down 2>/dev/null || true
docker compose up -d

# Wait for container to be healthy
echo "Waiting for LiteLLM to be healthy..."
for i in {1..30}; do
    if docker exec litellm curl -f http://localhost:4000/health >/dev/null 2>&1; then
        echo "✓ LiteLLM is healthy"
        break
    fi
    echo -n "."
    sleep 2
done

# Check final status
if docker ps | grep -q litellm; then
    echo ""
    echo "========================================="
    echo "LiteLLM deployed successfully!"
    echo "========================================="
    echo ""
    echo "🔒 SECURITY: Network Isolated Configuration"
    echo "   - MCP proxy accessible via internal network only"
    echo "   - No direct port exposure for MCP services"
    echo ""
    echo "📡 Access Points:"
    echo "   - Public: https://litellm.ai-servicers.com"
    echo "   - Admin: http://localhost:4000 (local only)"
    echo "   - UI: https://litellm.ai-servicers.com/ui"
    echo ""
    echo "🔑 Credentials:"
    echo "   - Admin: admin / LiteLLMAdmin2025!"
    echo "   - Admin API Key: sk-pFgey4HPR9qDvyT-N_7yVQ"
    echo "   - Dev API Key: sk-nzq2BIYVoVUpz5csqr69xA"
    echo ""
    echo "📦 MCP Configuration:"
    echo "   MCP services are accessible at:"
    echo "   http://mcp-proxy-sse:8080/servers/{service}/sse"
    echo ""
    echo "   Available services:"
    echo "   - filesystem (admin only)"
    echo "   - postgres, fetch, monitoring, n8n, playwright, timescaledb"
    echo ""
    echo "⚠️  IMPORTANT:"
    echo "   1. Update MCP URLs in LiteLLM UI to use mcp-proxy-sse:8080"
    echo "   2. MCP proxy MUST be running on litellm-net"
    echo "   3. Port 8585 is no longer exposed for security"
    
    # Show container networks
    echo ""
    echo "📊 Container Networks:"
    docker inspect litellm --format '{{range $key, $value := .NetworkSettings.Networks}}  - {{$key}}{{end}}'
    
else
    echo "✗ LiteLLM failed to start"
    docker logs litellm --tail 30
    exit 1
fi