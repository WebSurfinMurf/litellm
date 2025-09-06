#!/bin/bash
set -e

PROJECT_NAME="litellm"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Color output
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

echo "🚀 Deploying ${PROJECT_NAME}..."

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

# Deploy Litellm Proxy Server
docker run -d \
  --name ${PROJECT_NAME} \
  --restart unless-stopped \
  --network traefik-proxy \
  --env-file /home/administrator/secrets/${PROJECT_NAME}.env \
  -e LITELLM_MASTER_KEY=${LITELLM_MASTER_KEY} \
  -e DATABASE_URL=${DATABASE_URL} \
  -e UI_USERNAME=${UI_USERNAME} \
  -e UI_PASSWORD=${UI_PASSWORD} \
  --label "traefik.enable=true" \
  --label "traefik.docker.network=traefik-proxy" \
  --label "traefik.http.routers.${PROJECT_NAME}.rule=Host(\`${PROJECT_NAME}.ai-servicers.com\`)" \
  --label "traefik.http.routers.${PROJECT_NAME}.entrypoints=websecure" \
  --label "traefik.http.routers.${PROJECT_NAME}.tls.certresolver=letsencrypt" \
  --label "traefik.http.services.${PROJECT_NAME}.loadbalancer.server.port=4000" \
  ghcr.io/berriai/litellm:main-latest

# Connect networks
echo "Connecting to required networks..."
docker network connect postgres-net ${PROJECT_NAME} 2>/dev/null || true
docker network connect redis-net ${PROJECT_NAME} 2>/dev/null || true
docker network connect keycloak-net ${PROJECT_NAME} 2>/dev/null || true

# Wait and verify
sleep 5
if docker ps | grep -q ${PROJECT_NAME}; then
    echo -e "${GREEN}✓${NC} Container running"
    echo "🌐 Access at: https://${PROJECT_NAME}.ai-servicers.com"
    echo ""
    echo "📝 Login credentials:"
    echo "   Username: admin"
    echo "   Password: TeKhAp2kKjU5tQFJ7ZlFdw=="
    echo ""
    echo "🔑 Master Key: sk-1234"
    echo ""
    echo "📖 Documentation: https://docs.litellm.ai/"
else
    echo -e "${RED}✗${NC} Deployment failed"
    docker logs ${PROJECT_NAME} --tail 50
    exit 1
fi