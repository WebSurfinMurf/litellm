#!/bin/bash
set -e

PROJECT_NAME="litellm"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Color output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "🚀 Deploying LiteLLM - Unified LLM API Gateway..."

# Load environment
if [ -f "/home/administrator/secrets/${PROJECT_NAME}.env" ]; then
    source /home/administrator/secrets/${PROJECT_NAME}.env
    echo -e "${GREEN}✓${NC} Environment loaded"
else
    echo -e "${RED}✗${NC} Environment file not found"
    exit 1
fi

# Stop existing
docker stop ${PROJECT_NAME} 2>/dev/null || true
docker rm ${PROJECT_NAME} 2>/dev/null || true

# Pull latest image with database support
echo "Pulling latest LiteLLM database image..."
docker pull ghcr.io/berriai/litellm-database:main-stable

# Deploy LiteLLM with database and MCP support
docker run -d \
  --name ${PROJECT_NAME} \
  --restart unless-stopped \
  --network traefik-proxy \
  --env-file /home/administrator/secrets/${PROJECT_NAME}.env \
  -v ${SCRIPT_DIR}/config.yaml:/app/config.yaml:ro \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -v /home/administrator/projects:/home/administrator/projects:ro \
  -v /workspace:/workspace \
  --add-host=host.docker.internal:host-gateway \
  --label "traefik.enable=true" \
  --label "traefik.docker.network=traefik-proxy" \
  --label "traefik.http.routers.${PROJECT_NAME}.rule=Host(\`${PROJECT_NAME}.ai-servicers.com\`)" \
  --label "traefik.http.routers.${PROJECT_NAME}.entrypoints=websecure" \
  --label "traefik.http.routers.${PROJECT_NAME}.tls.certresolver=letsencrypt" \
  --label "traefik.http.services.${PROJECT_NAME}.loadbalancer.server.port=4000" \
  ghcr.io/berriai/litellm-database:main-stable \
  --config /app/config.yaml

# Connect networks
echo "Connecting to required networks..."
docker network connect postgres-net ${PROJECT_NAME} 2>/dev/null || true
docker network connect redis-net ${PROJECT_NAME} 2>/dev/null || true
docker network connect litellm-net ${PROJECT_NAME} 2>/dev/null || true

# Wait and verify
sleep 10
if docker ps | grep -q ${PROJECT_NAME}; then
    echo -e "${GREEN}✓${NC} Container running"
    echo ""
    echo "========================================="
    echo -e "${GREEN}LiteLLM deployed successfully!${NC}"
    echo "========================================="
    echo ""
    echo "🌐 Access Points:"
    echo "   - API: https://${PROJECT_NAME}.ai-servicers.com/v1"
    echo "   - UI: https://${PROJECT_NAME}.ai-servicers.com/ui"
    echo "   - Health: https://${PROJECT_NAME}.ai-servicers.com/health"
    echo ""
    echo "🔑 Authentication:"
    echo "   - Master Key: ${LITELLM_MASTER_KEY}"
    echo "   - Admin UI: ${UI_USERNAME} / ${UI_PASSWORD}"
    echo ""
    echo "📖 Documentation: https://docs.litellm.ai/"
else
    echo -e "${RED}✗${NC} Deployment failed"
    docker logs ${PROJECT_NAME} --tail 50
    exit 1
fi