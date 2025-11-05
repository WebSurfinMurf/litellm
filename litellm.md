# LiteLLM MCP & Aggregation Reference

## Overview
LiteLLM is a lightweight gateway that normalizes access to multiple large language models (LLMs) and tool providers behind a single OpenAI-compatible API surface. The same process can also act as a Model Context Protocol (MCP) hub, launching upstream MCP servers (stdio or HTTP) and exposing them via `/mcp/*` endpoints. This document summarizes the capabilities that matter when LiteLLM is used to aggregate LLMs, surface MCP tools, and serve remote clients such as Codex CLI, Open WebUI, or VS Code running on the same network (including Windows hosts).

## LLM Aggregation Capabilities
- Wraps dozens of vendors (OpenAI, Anthropic, Google, Azure, open-source runtimes) behind the OpenAI REST schema (`/v1/chat/completions`, `/v1/responses`).
- Supports per-model configuration: API keys, request/response transforms, temperature limits, max tokens, and provider-specific parameters (e.g., Anthropic `thinking`, Google `safety_settings`).
- Routing strategies include round-robin (`simple-shuffle`), least-busy, latency-aware, or custom Python hooks; fallbacks and cascading retries may be enabled per model group.
- Provides cost tracking, rate limiting, caching (Redis/Postgres), streaming responses, and structured logging (JSON) for observability pipelines.
- Accepts a `master_key` (or scoped API keys) enforced via the `Authorization: Bearer <key>` header for every API call.

## MCP Gateway Functionality
- Registers upstream servers under `mcp_servers` in `config.yaml` with transports `stdio` (spawn a subprocess) or `http` (delegate to remote URL).
- Launches each server with optional `env`, `args`, and human-readable `description` fields; secrets are injected through environment variables or LiteLLM’s secret store.
- Maintains alias mappings (`litellm_settings.mcp_aliases`) so clients can reference tools by friendly names.
- Exposes two primary endpoints:
  - `POST /mcp/tools` – Server-Sent Events (SSE) stream that returns tool catalogs for the MCP servers listed in the `x-mcp-servers` header.
  - `POST /mcp/invoke` – Streams tool call execution payloads back to the client once LiteLLM is wired to an execution layer (planned extension). Currently LiteLLM forwards tool responses but does not execute nested actions for you.
- Enforces the same auth model as standard LLM traffic; requests lacking the `Bearer` prefix or the `x-mcp-servers` selector are rejected.

## Configuration Surfaces (key sections in `config.yaml`)
- `model_list`: declarative map of logical model names to provider-specific parameters.
- `litellm_settings`: global behavior (retry budget, timeout, log format, parameter dropping, MCP alias definitions).
- `router_settings`: choose routing or fallbacks for aggregated providers.
- `general_settings`: authentication, persistence, admin UI credentials, telemetry, CORS origins.
- `mcp_servers`: stdio/HTTP registrations for MCP tool backends, including command path, arguments, allowed filesystem paths, and future HTTP services.

## Authentication & Security
- API keys are supplied via environment (`os.environ/VARIABLE`) or secret files; LiteLLM validates every REST and MCP request against the configured keys.
- Supports per-client keys (`scoped_key=true`) with rate limits and quota tracking; master keys remain for administrative traffic.
- CORS controls allow explicit origins for browser-based clients (e.g., Open WebUI, custom dashboards).
- When exposing MCP endpoints, ensure TLS termination (Traefik/NGINX) and network ACLs restrict access to trusted subnets.

## Client Connectors & Remote Access
### Codex CLI
- Configure `~/.codex/config.toml` (Linux/macOS) or `%APPDATA%\codex\config.toml` (Windows) to point `api_base` at `http://<litellm-host>/mcp/` and include `Authorization = "Bearer <key>"` as well as `extra_headers = { "x-mcp-servers" = "mcp_postgres,mcp_filesystem" }`.
- For Windows machines on the same LAN, ensure the host name (e.g., `litellm.linuxserver.lan`) resolves via DNS or hosts file and that local firewalls allow outbound HTTP/HTTPS.

### Open WebUI
- Set `OPENAI_API_BASE_URL` (or UI equivalent) to `http://<litellm-host>/v1` so chat requests flow through LiteLLM.
- Provide the LiteLLM API key in `OPENAI_API_KEY`; Open WebUI can then call `/mcp/tools` by passing the same key and `x-mcp-servers` header when MCP support is enabled in the UI.

### VS Code (or other MCP-aware IDEs)
- Populate an `mcp_servers.json` (MCP extension convention) with entries targeting LiteLLM’s `/mcp/` endpoint, specifying the Authorization header and desired server aliases.
- On Windows, store secrets in Credential Manager or the VS Code `settings.json` secret store; avoid embedding keys directly in repo files.
- Remote tunnels must allow SSE traffic; ensure enterprise proxies do not strip the `x-mcp-servers` header.

## Tool Call Flow & Limitations
1. Client authenticates via Bearer token and lists desired backends in `x-mcp-servers`.
2. LiteLLM streams the tool catalog (SSE) gathered from each upstream MCP server.
3. Client selects a tool; invocation currently relays request/response payloads but assumes the client (or a downstream orchestrator) handles side-effectful execution.
4. Future enhancements add automatic execution, richer error propagation, and multi-hop tool orchestration.

## Operational Considerations
- Deploy LiteLLM behind Traefik/NGINX for TLS, hostname routing (internet vs LAN), and optional OAuth2 proxies.
- Persist usage data to Postgres by setting `general_settings.database_url`; enables dashboards and audit trails.
- Log aggregation: enable `json_logs` to integrate with Loki/ELK; adjust `log_level` per environment.
- Monitor performance (requests/sec, latency, error rate) to tune routing strategies or spin up additional replicas.
- Keep upstream MCP binaries unmodified; upgrades are handled by updating the package versions outside of LiteLLM.

This reference should serve as the starting point for configuring LiteLLM as a unified LLM and MCP gateway and for onboarding remote tools or clients on the same network.

---

## Implementation Experience & Lessons Learned (2025-09-21)

### Successfully Implemented Features

#### ✅ Environment Variable Substitution
**Issue:** LiteLLM config files don't support standard `${VAR}` environment variable syntax.
**Solution:** Use LiteLLM's native `os.environ/VARIABLE_NAME` syntax instead.

**Example:**
```yaml
# ❌ This doesn't work:
api_key: ${ANTHROPIC_API_KEY}

# ✅ This works:
api_key: os.environ/ANTHROPIC_API_KEY
```

**Applied to:**
- `litellm_settings.master_key: os.environ/LITELLM_MASTER_KEY`
- `litellm_settings.database_url: os.environ/DATABASE_URL`
- `model_list[].litellm_params.api_key: os.environ/ANTHROPIC_API_KEY`
- `virtual_keys[].api_key: os.environ/LITELLM_VIRTUAL_KEY_TEST`
- `mcp_servers[].api_keys: [os.environ/LITELLM_VIRTUAL_KEY_TEST]`

#### ✅ Database Authentication Fix
**Issue:** PostgreSQL SCRAM-SHA-256 authentication failure after database recreation.
**Root Cause:** When database was recreated to fix connectivity, it used MD5 password hashing but PostgreSQL required SCRAM-SHA-256.
**Solution:**
```sql
-- Set encryption method before changing password
SET password_encryption = 'scram-sha-256';
ALTER USER litellm_user PASSWORD 'LiteLLMPass2025';
```

#### ✅ Virtual Key Authentication Recovery
**Issue:** Virtual keys stopped working after database recreation.
**Root Cause:** Database DROP/CREATE wiped `LiteLLM_VerificationToken` table.
**Solution:** Manually insert virtual key with correct SHA256 hash:
```sql
INSERT INTO "LiteLLM_VerificationToken"
(token, key_alias, models, user_id)
VALUES
('d1fc78fe0a825d4d19685e9ec9f445cb8c584353e2d4838e202e80947738d763',
 'test-virtual-key',
 '{"claude-3-haiku-orchestrator", "gpt-4o-mock"}',
 'mcp-test-user');
```

**Hash calculation:** `echo -n "sk-litellm-test-9768ce8475df0a3c5aa0d2f52571505b2ef09f3a21ec1af73859749fff4bb7cd" | sha256sum`

#### ✅ Model Configuration & Health
**Current Status:** Claude-3-haiku-20240307 model healthy and responding correctly.
**Configuration:**
```yaml
model_list:
  - model_name: claude-3-haiku-orchestrator
    litellm_params:
      model: claude-3-haiku-20240307
      api_key: os.environ/ANTHROPIC_API_KEY
```

### Partially Working Features

#### ⚠️ MCP Function Calling - Generation Working, Execution Failing
**What Works:**
- Claude correctly generates function calls with proper JSON structure
- Virtual key authentication successful
- MCP postgres service running and receiving connections
- Network connectivity confirmed between litellm and mcp-postgres containers

**What Doesn't Work:**
- Function calls stop at `"finish_reason":"tool_calls"`
- No actual function execution or result return
- Missing execution phase of MCP workflow

**Response Example:**
```json
{
  "choices": [{
    "finish_reason": "tool_calls",
    "message": {
      "role": "assistant",
      "tool_calls": [{
        "function": {
          "arguments": "{\"properties\": {}}",
          "name": "postgres_list_databases"
        },
        "id": "toolu_01Wcn2AxkPYpUH2TgP9BSfAS",
        "type": "function"
      }]
    }
  }]
}
```

**Expected:** Follow-up with function results and `"finish_reason":"stop"`

### Critical Knowledge Gaps & Unresolved Issues

#### 🔴 MCP Server Registration & Association
**Problem:** MCP servers not properly registered in database for function execution.

**Database State:**
- `LiteLLM_MCPServerTable`: ✅ Contains db_main server entry
- `LiteLLM_VerificationToken`: ✅ Virtual key exists with correct hash
- **Missing:** Proper association between virtual keys and MCP servers

**Attempted Solutions:**
1. ✅ Added `require_approval: "never"` to MCP config - No effect
2. ✅ Manually inserted MCP server into database - No effect
3. ✅ Updated virtual key config with MCP access - No effect
4. ✅ Multiple docker compose down/up cycles - No effect

**Research Findings:**
Common LiteLLM MCP issues include:
- GitHub Issue #16688: "MCP tool call parsed, but sometimes not executed"
- Missing `require_approval: "never"` setting (tried, didn't fix)
- Virtual key authentication problems (fixed, but execution still fails)
- SSE transport connection issues (connections work, but no execution)

#### 🔴 MCP Configuration Loading from YAML
**Problem:** MCP servers defined in config.yaml don't automatically populate database tables.

**Config vs Database Mismatch:**
```yaml
# config.yaml has this:
mcp_servers:
  db_main:
    transport: sse
    url: http://mcp-postgres:8080/sse
    api_keys: [os.environ/LITELLM_VIRTUAL_KEY_TEST]
    require_approval: "never"

# But LiteLLM_MCPServerTable was empty until manually inserted
```

**Unknowns:**
- Does LiteLLM auto-load MCP servers from config on startup?
- Is there a specific startup command or API call needed?
- Are there additional database tables/associations required?

#### 🔴 Function Execution Architecture
**Unknown:** How LiteLLM routes function calls to MCP servers for execution.

**Observed Behavior:**
- Claude generates valid function calls
- LiteLLM accepts the calls (no authentication errors)
- MCP postgres service receives SSE connections and ListToolsRequest
- No actual function execution requests reach MCP service
- Response stops at tool_calls generation phase

**Missing Understanding:**
- What triggers the execution phase after tool_calls generation?
- How does LiteLLM map function names to MCP servers?
- Is there a missing middleware or configuration for execution routing?
- Should virtual keys have additional permissions or associations?

### Debugging Commands & Verification

#### Database Verification
```bash
# Check virtual keys
docker exec -e PGPASSWORD='LiteLLMPass2025' postgres psql -U litellm_user -d litellm_db -c "SELECT token, key_alias, models FROM \"LiteLLM_VerificationToken\";"

# Check MCP servers
docker exec -e PGPASSWORD='LiteLLMPass2025' postgres psql -U litellm_user -d litellm_db -c "SELECT server_name, url, transport, status FROM \"LiteLLM_MCPServerTable\";"

# Check for other MCP-related tables
docker exec -e PGPASSWORD='LiteLLMPass2025' postgres psql -U litellm_user -d litellm_db -c "\dt" | grep -i mcp
```

#### Network & Service Verification
```bash
# Test container connectivity
docker exec litellm ping -c 1 mcp-postgres

# Check MCP service logs
docker logs mcp-postgres --tail 10

# Test LiteLLM health
curl -H "Authorization: Bearer sk-litellm-cecca390f610603ff5180ba0ba2674afc8f7689716daf25343de027d10c32404" http://localhost:4000/health
```

#### Function Calling Test
```bash
# Test MCP function generation
curl -H "Authorization: Bearer sk-litellm-test-9768ce8475df0a3c5aa0d2f52571505b2ef09f3a21ec1af73859749fff4bb7cd" \
     -H "Content-Type: application/json" \
     -d '{
       "model": "claude-3-haiku-orchestrator",
       "messages": [{"role": "user", "content": "Use postgres_list_databases to show databases"}],
       "tools": [{"type": "function", "function": {"name": "postgres_list_databases", "description": "List PostgreSQL databases", "parameters": {"type": "object", "properties": {}}}}],
       "tool_choice": "auto"
     }' \
     http://localhost:4000/chat/completions
```

### Deployment Configuration

#### Working Docker Compose Setup
```yaml
version: "3.9"
services:
  litellm:
    image: ghcr.io/berriai/litellm:main-latest
    container_name: litellm
    restart: unless-stopped
    command: ["--port", "4000", "--host", "0.0.0.0", "--config", "/app/config/config.yaml"]
    env_file: $HOME/projects/secrets/litellm.env
    environment:
      - PYTHONUNBUFFERED=1
    volumes:
      - ./config:/app/config:ro
      - ./tmp:/app/tmp
    ports:
      - "4000:4000"
    networks:
      - postgres-net      # Required for database access
      - litellm-mcp-net   # Required for MCP service access
```

#### Environment File Structure
```bash
# $HOME/projects/secrets/litellm.env
LITELLM_MASTER_KEY=sk-litellm-[hash]
LITELLM_VIRTUAL_KEY_TEST=sk-litellm-test-[hash]
ANTHROPIC_API_KEY=sk-ant-api03-[key]
DATABASE_URL=postgresql://litellm_user:LiteLLMPass2025@postgres:5432/litellm_db
```

### Next Steps for Resolution

1. **Investigate LiteLLM MCP execution architecture**
   - Study LiteLLM source code for function execution routing
   - Identify missing database associations or configuration
   - Research LiteLLM MCP examples and working implementations

2. **Test alternative configurations**
   - Try HTTP transport instead of SSE
   - Test with master key instead of virtual key for MCP access
   - Experiment with different MCP server registration methods

3. **Database schema analysis**
   - Identify all MCP-related database tables and relationships
   - Compare working vs broken database states
   - Document required database associations for MCP execution

4. **LiteLLM community resources**
   - Review LiteLLM GitHub discussions for MCP integration patterns
   - Check LiteLLM documentation for MCP execution requirements
   - Test with simpler MCP configurations or examples

The current implementation successfully handles authentication, environment variables, database connectivity, and function call generation, but the critical MCP execution phase remains unresolved.
