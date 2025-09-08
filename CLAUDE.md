# Project: LiteLLM

## Overview
- Purpose: Unified LLM API Gateway for Claude, ChatGPT, and Gemini (100+ providers supported)
- URL: https://litellm.ai-servicers.com/ui/ (requires trailing slash)
- Repository: /home/administrator/projects/litellm
- Created: 2025-01-11
- Updated: 2025-09-07
- Models Configured: 17 active (7 GPT, 4 Claude, 6 Gemini)
- Status: ✅ Running with MCP middleware for tool execution

## Configuration
- Keycloak Client: litellm (pending full SSO integration)
- Environment: /home/administrator/secrets/litellm.env
- Database: litellm_db (PostgreSQL with admin user)
- Container: litellm (ghcr.io/berriai/litellm-database:main-stable)
- Config File: /home/administrator/projects/litellm/config.yaml

## Services & Ports
- Application: Port 4000 (internal)
- External: https://litellm.ai-servicers.com
- Networks: traefik-proxy, postgres-net, redis-net

## Key Features
- Unified OpenAI-compatible API for all LLM providers
- Load balancing with "least-busy" routing strategy
- Automatic fallback chains between models
- Cost tracking and usage analytics (PostgreSQL)
- Rate limiting and quota management
- Virtual key generation for team/user management
- Database persistence for keys, logs, and usage

## Access Credentials
- UI URL: https://litellm.ai-servicers.com/ui
- Admin Username: admin
- Admin Password: LiteLLMAdmin2025!
- Master Key: sk-e0b742bc6575adf26c7d356c49c78d8fd08119fcde1d6e188d753999b5f956fc

## Available Models (19 total)
### OpenAI/ChatGPT (7 models)
- `gpt-5` - GPT-5 (reasoning model, brief responses)
- `gpt-5-chat-latest` - GPT-5 Chat (shows detailed work)
- `gpt-5-mini` - GPT-5 Mini (smaller, faster)
- `gpt-5-nano` - GPT-5 Nano (smallest, fastest)
- `gpt-4.1` - GPT-4.1
- `gpt-4o` - GPT-4 Omni
- `gpt-4o-mini` - GPT-4 Omni Mini

### Anthropic/Claude (4 models)
- `claude-opus-4.1` - Claude Opus 4.1 (latest, most capable)
- `claude-opus-4` - Claude Opus 4
- `claude-thinking` - Claude Opus 4.1 with extended thinking
- `claude-sonnet-4` - Claude 3.5 Sonnet (fast, balanced)

### Google/Gemini (8 models)
- `gemini-2.5-pro` - Gemini 2.5 Pro (advanced reasoning)
- `gemini-2.5-flash` - Gemini 2.5 Flash (fast)
- `gemini-2.5-flash-lite` - Gemini 2.5 Flash Lite (lightweight)
- `gemini-2.5-flash-image-preview` - Gemini 2.5 Flash Image (multimodal)
- `gemini-2.5-flash-preview-tts` - Gemini 2.5 TTS Flash
- `gemini-2.5-pro-preview-tts` - Gemini 2.5 TTS Pro
- `gemini-1.5-pro` - Gemini 1.5 Pro (legacy)
- `gemini-1.5-flash` - Gemini 1.5 Flash (legacy)

## API Usage Examples

### List Available Models
```bash
curl https://litellm.ai-servicers.com/v1/models \
  -H "Authorization: Bearer sk-e0b742bc6575adf26c7d356c49c78d8fd08119fcde1d6e188d753999b5f956fc"
```

### Test GPT-5
```bash
curl https://litellm.ai-servicers.com/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer sk-e0b742bc6575adf26c7d356c49c78d8fd08119fcde1d6e188d753999b5f956fc" \
  -d '{
    "model": "gpt-5",
    "messages": [{"role": "user", "content": "Say hello"}]
  }'
```

### Test Claude Opus 4.1
```bash
curl https://litellm.ai-servicers.com/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer sk-e0b742bc6575adf26c7d356c49c78d8fd08119fcde1d6e188d753999b5f956fc" \
  -d '{
    "model": "claude-opus-4.1",
    "messages": [{"role": "user", "content": "Say hello"}]
  }'
```

### Test Gemini 2.5 Pro
```bash
curl https://litellm.ai-servicers.com/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer sk-e0b742bc6575adf26c7d356c49c78d8fd08119fcde1d6e188d753999b5f956fc" \
  -d '{
    "model": "gemini-2.5-pro",
    "messages": [{"role": "user", "content": "Say hello"}]
  }'
```

## Deployment
```bash
cd /home/administrator/projects/litellm
./deploy.sh
```

## Configuration Management
- Add LLM provider API keys via UI or environment variables
- Configure model routing and fallbacks in UI
- Set rate limits and quotas per key

## Troubleshooting
- Logs: `docker logs litellm --tail 50`
- Shell: `docker exec -it litellm /bin/sh`
- Database: `PGPASSWORD='Pass123qp' psql -h localhost -p 5432 -U admin -d litellm_db`
- Health check: `curl https://litellm.ai-servicers.com/health -H "Authorization: Bearer sk-e0b742bc6575adf26c7d356c49c78d8fd08119fcde1d6e188d753999b5f956fc"`

## Network Connections
- traefik-proxy: For HTTPS ingress
- postgres-net: Database access
- redis-net: Caching layer
- keycloak-net: Future SSO integration

## MCP Middleware Integration (2025-09-07) ✅ FIXED

### Architecture
```
Open WebUI → MCP Middleware (4001) → LiteLLM (4000) → AI Models
                    ↓
            Executes MCP Tools → MinIO Storage
```

### Middleware Service
- **Location**: `/home/administrator/projects/litellm/middleware/`
- **Container**: mcp-middleware
- **Port**: 4001
- **Network**: litellm-net
- **Purpose**: Intercepts and executes MCP tool calls from models

### Current Status
- ✅ Middleware deployed and running
- ✅ Models detected by Open WebUI (19 models)
- ✅ Basic chat functionality working
- ✅ Tool detection and execution working
- ✅ Auto-injection of tools when missing from request
- ✅ 23 MCP tools available (mock implementations)

### Available MCP Tools (23 Total)

#### Categories:
1. **Database** (2): list_databases, execute_sql
2. **Monitoring** (3): get_container_logs, search_logs, get_system_metrics
3. **System** (2): list_directory, manage_docker
4. **Network** (1): fetch_url
5. **Automation** (3): list_workflows, execute_workflow, get_workflow_executions
6. **TimeSeries** (3): query_timeseries, list_hypertables, get_timeseries_stats
7. **Browser** (3): browser_navigate, browser_screenshot, browser_extract
8. **Storage** (5): minio_list_objects, minio_upload_object, minio_download_object, minio_delete_object, minio_get_url
9. **Meta** (1): list_mcp_tools

### Key Fixes Applied
1. **Tool Auto-Injection**: Automatically adds MCP tools to requests missing them
2. **Streaming Prevention**: Forces `stream=false` for compatibility
3. **Defensive Error Handling**: Safely processes malformed responses
4. **Enhanced Logging**: Diagnostic logging for debugging

### MinIO Integration
- Screenshots and files saved to MinIO bucket `mcp-storage`
- Files require Keycloak authentication to access
- AI generates presigned URLs for sharing (24-hour expiry)

## Unified MCP Registry Status (2025-09-08) ✅

### Architecture: Unified Tool Registry
```
┌─────────────────────────────────────────┐
│         Unified MCP Registry             │
│     24 tools from 7 MCP services        │
└─────────────┬───────────┬────────────────┘
              │           │
     ┌────────▼───────┐  ▼─────────────┐
     │ Claude Adapter │  │LiteLLM Adapter│
     │  (stdio)       │  │  (HTTP - TODO) │
     └────────┬───────┘  └──────────────┘
              │
     ┌────────▼───────────────────┐
     │   MCP Services (7 Active)    │
     │ • filesystem (4 tools)       │
     │ • postgres (2 tools)         │
     │ • github (3 tools)           │
     │ • monitoring (5 tools)       │
     │ • n8n (3 tools)              │
     │ • playwright (4 tools)       │
     │ • timescaledb (3 tools)      │
     └──────────────────────────────┘
```

### Deployed Services in Unified Registry

**Total: 24 tools from 7 services**

1. **filesystem** (4 tools) - File operations via Docker
   - `filesystem_read_file`
   - `filesystem_list_directory`
   - `filesystem_write_file`
   - `filesystem_create_directory`

2. **postgres** (2 tools) - PostgreSQL operations via Docker
   - `postgres_list_databases`
   - `postgres_execute_sql`

3. **github** (3 tools) - GitHub API via npx
   - `github_search_repositories`
   - `github_get_repository`
   - `github_create_issue`

4. **monitoring** (5 tools) - Loki/Netdata via Node.js
   - `monitoring_search_logs`
   - `monitoring_get_recent_errors`
   - `monitoring_get_container_logs`
   - `monitoring_get_system_metrics`
   - `monitoring_check_service_health`

5. **n8n** (3 tools) - Workflow automation via wrapper
   - `n8n_list_workflows`
   - `n8n_get_workflow`
   - `n8n_execute_workflow`

6. **playwright** (4 tools) - Browser automation via Node.js
   - `playwright_navigate`
   - `playwright_screenshot`
   - `playwright_click`
   - `playwright_fill`

7. **timescaledb** (3 tools) - Time-series DB via Docker
   - `timescaledb_list_hypertables`
   - `timescaledb_query_timeseries`
   - `timescaledb_create_hypertable`

### Services NOT Deployed (Skipped)

1. **fetch** - Skipped (functionality covered by WebFetch in Claude Code)
2. **memory** - Skipped (broken - onnxruntime-node dependency issues)
3. **docker-hub** - Skipped (never worked, authentication issues)

### Integration Points

**Claude Code Access:**
- Location: `/home/administrator/projects/mcp/unified-registry/`
- Command: `run_claude_adapter.sh`
- Config: Add to `~/.config/claude/mcp_servers.json` as "unified-tools"

**LiteLLM Integration (TODO):**
- Need to create HTTP/SSE adapter for LiteLLM middleware
- Will replace mock tools with real MCP execution
- Target: Port 4001 (MCP middleware)

### Testing Commands

```bash
# List all available tools
echo '{"jsonrpc":"2.0","method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"test","version":"1.0.0"}},"id":1}
{"jsonrpc":"2.0","method":"tools/list","params":{},"id":2}' | \
python3 /home/administrator/projects/mcp/unified-registry/claude_adapter.py 2>/dev/null | \
jq -r '.result.tools[].name'

# Count tools by service
python3 -c "from tool_definitions import TOOL_DEFINITIONS; \
[print(f'{s}: {len(sd[\"tools\"])} tools') for s, sd in TOOL_DEFINITIONS.items()]"
```

### Key Benefits of Unified Registry

1. **Single Source of Truth** - One place to define all MCP tools
2. **No Duplication** - Tools defined once, used everywhere
3. **Consistent Naming** - `service_tool` format prevents conflicts
4. **Easy Maintenance** - Update tool definitions in one file
5. **Platform Agnostic** - Works with both stdio (Claude) and HTTP (LiteLLM)

### Next Steps for Full Integration

1. ✅ Unified registry with 7 MCP services (24 tools)
2. ✅ Claude Code adapter working
3. ⏳ Create LiteLLM HTTP adapter
4. ⏳ Connect to MCP middleware at port 4001
5. ⏳ Replace mock tools with real execution
6. ⏳ Test end-to-end with Open WebUI

## Documentation
- Official Docs: https://docs.litellm.ai/
- API Reference: https://litellm.ai-servicers.com/docs
- GitHub: https://github.com/BerriAI/litellm