#!/usr/bin/env bash
HOSTNAME="${1:-linuxserver.lan}"
IP="${2:-$(hostname -I | awk '{print $1}') }"
PORT="${PORT:-4100}"
source /home/administrator/secrets/litellm.env
curl -sS -N -X POST \
  --resolve "${HOSTNAME}:${PORT}:${IP}" \
  -H "Authorization: Bearer ${LITELLM_MASTER_KEY}" \
  -H "x-mcp-servers: mcp_postgres,mcp_filesystem" \
  -H "Accept: application/json, text/event-stream" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":"tools-list","method":"tools/list","params":{}}' \
  "http://${HOSTNAME}:${PORT}/mcp/tools"
