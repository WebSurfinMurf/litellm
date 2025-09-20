# LiteLLM Ops Notes (Codex Session)

## Traefik Routing
- External host: `https://litellm.ai-servicers.com` served via Traefik router `litellm` (entrypoint `websecure`).
- LAN host: `http://litellm.linuxserver.lan` mapped to Traefik router `litellm-internal` (entrypoint `web`).
- Compose labels confirmed on 2025-09-18 in `docker-compose.yml`.

## LAN Access Check (2025-09-18)
- Attempted SSE catalog pull using curl with `Authorization: Bearer <master>` and `x-mcp-servers: mcp_postgres,mcp_filesystem` headers.
- Codex sandbox cannot resolve `litellm.linuxserver.lan`; manual `--resolve` to `192.168.1.13` also failed (connection refused). See `evaluation/lan-mcp-tools-2025-09-18.log`.
- LinuxServer validation succeeded via `test-lan-mcp-tools.sh`; log stored at `evaluation/lan-mcp-tools-2025-09-18-075003.log` shows SSE heartbeat pings (tool catalog still pending middleware support).

## Quick Test Command (once DNS fixed)
```
source /home/administrator/secrets/litellm.env
curl -sS -N -H "Authorization: Bearer $LITELLM_MASTER_KEY" \
     -H 'x-mcp-servers: mcp_postgres,mcp_filesystem' \
     -H 'Accept: text/event-stream' \
     http://litellm.linuxserver.lan/mcp/tools | tee projects/litellm/evaluation/lan-mcp-tools-$(date +%F).log
```
- Expect SSE stream with `data:` entries describing tools from `mcp_postgres` and `mcp_filesystem`.
- Replace LAN host with reachable fallback (`http://localhost:4000`) only for troubleshooting; official validation requires Traefik route.

## Next Steps
- Coordinate with Traefik/DNS maintainers to expose `litellm.linuxserver.lan` on the Codex CLI host.
- Re-run curl test and update `projects/litellm/evaluation/` log once connectivity is restored.

## MCP Server & Secret Audit (2025-09-18)
- `config.yaml` registers stdio transports for `mcp_postgres` (`postgres-mcp`) and `mcp_filesystem` (`mcp-server-filesystem`) with descriptions and environment variables.
- `secrets/litellm.env` supplies `LITELLM_MASTER_KEY`, `POSTGRES_MCP_URL`, and filesystem allowlist; `secrets/mcp-postgres.env` backs the upstream binary.
- Restart procedure: `cd /home/administrator/projects/litellm && docker compose up -d litellm` after updating config or secrets. No rebuild required unless Dockerfile changes.

## Codex CLI Validation (2025-09-18)
- `~/.codex/config.toml` already defines `mcp_servers.litellm` pointing at `http://litellm.linuxserver.lan/mcp/` with authorization + `x-mcp-servers` headers.
- `codex mcp list` enumerates the configured server, but CLI lacks a direct tooling command; further validation requires an interactive Codex session issuing MCP tool calls.
- Next action: coordinate with Codex CLI maintainers for a non-interactive MCP test pathway or capture an interactive transcript for audit.

## Open WebUI Validation (2025-09-18)
- `OPENAI_API_BASE_URL` in `secrets/open-webui-internal.env` targets `http://litellm.linuxserver.lan/v1` and must send `Authorization` + `x-mcp-servers` headers when hitting `/mcp/tools`.
- `archive/test-openwebui-mcp.sh` executed against localhost:4000 returned `Error or no response` for all probes (log: `evaluation/test-openwebui-mcp-2025-09-18.log`). This matches LiteLLM's current behavior of surfacing tool calls without auto-executing them.
- Document limitation in Open WebUI runbooks and await LiteLLM middleware capable of fulfilling tool execution chains.
