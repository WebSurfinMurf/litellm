#!/usr/bin/env bash
# Collect LiteLLM MCP tool catalog over LAN and store output under projects/litellm/evaluation.
# Usage: ./test-lan-mcp-tools.sh

set -euo pipefail
LOG_DIR="/home/administrator/projects/litellm/evaluation"
TIMESTAMP="$(date +%F-%H%M%S)"
LOG_FILE="${LOG_DIR}/lan-mcp-tools-${TIMESTAMP}.log"

mkdir -p "$LOG_DIR"

# Load LiteLLM secrets (provides LITELLM_MASTER_KEY)
source /home/administrator/secrets/litellm.env

CURL_CMD=(
  curl -sS -N \
    -H "Authorization: Bearer ${LITELLM_MASTER_KEY}" \
    -H "x-mcp-servers: mcp_postgres,mcp_filesystem" \
    -H "Accept: text/event-stream" \
    http://litellm.linuxserver.lan/mcp/tools
)

echo "[info] Writing SSE stream to ${LOG_FILE}" | tee "$LOG_FILE"
{
  printf '\n[command]\n%s\n\n' "${CURL_CMD[*]}"
  printf '[output]\n'
  "${CURL_CMD[@]}"
} | tee -a "$LOG_FILE"

echo "\n[info] Done. Output stored at ${LOG_FILE}" | tee -a "$LOG_FILE"
