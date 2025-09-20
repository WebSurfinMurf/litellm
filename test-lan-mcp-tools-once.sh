#!/usr/bin/env bash
# Fetch a short snapshot of the LiteLLM MCP tool stream.
# Usage:
#   ./test-lan-mcp-tools-once.sh [hostname] [ip]
# Examples:
#   ./test-lan-mcp-tools-once.sh                     # default host, DNS lookup
#   ./test-lan-mcp-tools-once.sh litellm.linuxserver.lan 192.168.1.13
# Environment:
#   Set TIMEOUT_SECONDS to change stream duration (default: 15 seconds).

set -euo pipefail

HOSTNAME="${1:-litellm.linuxserver.lan}"
IP_OVERRIDE="${2:-}"
TIMEOUT_SECONDS="${TIMEOUT_SECONDS:-15}"
LOG_DIR="/home/administrator/projects/litellm/evaluation"
TIMESTAMP="$(date +%F-%H%M%S)"
LOG_FILE="${LOG_DIR}/lan-mcp-tools-${TIMESTAMP}.log"

mkdir -p "$LOG_DIR"
source /home/administrator/secrets/litellm.env

CURL_CMD=(curl -sS -N
  -H "Authorization: Bearer ${LITELLM_MASTER_KEY}"
  -H "x-mcp-servers: mcp_postgres,mcp_filesystem"
  -H "Accept: text/event-stream"
)

if [[ -n "$IP_OVERRIDE" ]]; then
  CURL_CMD+=(--resolve "${HOSTNAME}:80:${IP_OVERRIDE}")
fi

CURL_CMD+=("http://${HOSTNAME}/mcp/tools")

echo "[info] Capturing ${TIMEOUT_SECONDS}s of /mcp/tools stream from ${HOSTNAME} (IP override: ${IP_OVERRIDE:-none})" | tee "$LOG_FILE"
{
  printf '\n[command]\n%s\n\n' "timeout ${TIMEOUT_SECONDS} ${CURL_CMD[*]}"
  printf '[output]\n'
  timeout "$TIMEOUT_SECONDS" "${CURL_CMD[@]}"
} | tee -a "$LOG_FILE"

echo "\n[info] Done. Output stored at ${LOG_FILE}" | tee -a "$LOG_FILE"
