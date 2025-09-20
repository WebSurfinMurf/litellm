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

# Rebuild custom image
echo "Building LiteLLM container image..."
docker compose -f ${SCRIPT_DIR}/docker-compose.yml build

# Redeploy via docker compose
echo "Restarting LiteLLM stack..."
docker rm -f ${PROJECT_NAME} 2>/dev/null || true
docker compose -f ${SCRIPT_DIR}/docker-compose.yml down
docker compose -f ${SCRIPT_DIR}/docker-compose.yml up -d

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
