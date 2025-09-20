# LiteLLM MCP Integration Status (2025-09-18)

## Network & Gateway
- Traefik labels now split UI/docs vs API routing using `HeaderRegexp` (Traefik v3). `/ui`, `/swagger`, `/docs`, `/openapi.json` stay open; everything else requires `Authorization: Bearer …`. Added a dedicated status router with a header-injection middleware so `/schedule/model_cost_map_reload/status` carries the admin Bearer key automatically; UI health checks succeed and LiteLLM auth warnings stopped. Swap the master key for a scoped token once available.
- Codex sandbox cannot reach `litellm.linuxserver.lan` (DNS + TCP failures). LAN validation executed directly on LinuxServer captured SSE heartbeat pings at `projects/litellm/evaluation/lan-mcp-tools-2025-09-18-075003.log`.
- Action: keep sandbox limitation noted; LAN host can be used for future `/mcp/tools` captures until network access policy changes.

## MCP Servers & Secrets
- `config.yaml` retains stdio registrations for `mcp_postgres` and `mcp_filesystem`; no local binary modifications.
- Secrets sourced from `/home/administrator/secrets/litellm.env` and `/home/administrator/secrets/mcp-postgres.env`; restart via `docker compose up -d litellm` after updates.

## Client Matrix
- **Codex CLI**: `~/.codex/config.toml` includes HTTP transport with Authorization + `x-mcp-servers`. `codex mcp list` succeeds (see `evaluation/codex-cli-mcp-2025-09-18.txt`). Tool catalog invocation requires interactive CLI support—pending product guidance.
- **Open WebUI**: Internal `.env` targets LAN base URL. `archive/test-openwebui-mcp.sh` output (`evaluation/test-openwebui-mcp-2025-09-18.log`) shows "Error or no response" across probes, consistent with LiteLLM pass-through behaviour; document limitation.
- **VS Code / MCP IDEs**: Added example `projects/claude/config/mcp_servers.litellm.example.json` with internal/external endpoints and Windows secret storage guidance in `projects/claude/CLAUDE.md`.

## Outstanding Items
1. Restore LAN DNS/ingress so `/mcp/tools` SSE catalog can be captured successfully.
2. Obtain or implement non-interactive Codex CLI MCP test workflow to verify tool listings.
3. Coordinate on scoped API keys and firewall documentation per `projects/mcp/CODEXMCP.md` outstanding questions.
4. Update runbooks (`projects/litellm/CLAUDE.md`, Open WebUI docs) once network issues resolved and new validation artifacts are available.
