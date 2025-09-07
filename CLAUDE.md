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

## MCP Integration Status (2025-09-06)

### Configuration Added
- Added 9 MCP servers to config.yaml (filesystem, memory, fetch, monitoring, github, postgres, n8n, playwright, timescaledb)
- Added MCP aliases for easier access (fs, mem, web, logs, gh, pg, wf, browser, tsdb)
- Updated environment variables in litellm.env with required passwords
- Modified deploy.sh to mount necessary volumes and Docker socket

### Current MCP Servers (All STDIO-based)

**Docker Containers (3):**
1. **mcp-filesystem** - Docker container for file operations
2. **mcp-fetch** - Docker container for web fetching
3. **mcp-postgres** - Docker container for PostgreSQL operations

**Node.js Applications (5):**
4. **mcp-memory-postgres** - Node.js app for memory storage
5. **mcp-monitoring** - Node.js app for Loki/Netdata monitoring
6. **mcp-n8n** - Shell wrapper → Node.js for workflow automation
7. **mcp-playwright** - Node.js app for browser automation
8. **mcp-timescaledb** - Node.js app for time-series DB

**NPM Package (1):**
9. **mcp-github** - NPM package via npx

### Current Limitations
- **Docker-in-Docker Required**: LiteLLM container can't run Docker commands (3 MCPs need it)
- **Node.js Missing**: LiteLLM container doesn't have Node.js installed (5 MCPs need it)
- **NPX Missing**: LiteLLM container doesn't have npx (1 MCP needs it)
- **Connection Errors**: All MCP client connections failing with "No such file or directory"

### Industry Best Practices (2025)
Based on research, the top 3 approaches used in production:

1. **HTTP/SSE Gateway Pattern** (Most Popular)
   - Convert MCP servers to HTTP/SSE endpoints
   - Examples: Zapier, DeepWiki use HTTPS endpoints
   - No runtime dependencies in LiteLLM container

2. **Docker MCP Catalog** (Docker's Solution)
   - Use Docker's official MCP Catalog (100+ servers)
   - Each MCP runs in separate container
   - Managed through Docker Desktop MCP Toolkit

3. **Custom LiteLLM Image** (DIY Approach)
   - Build custom image with Node.js: `FROM litellm:stable + RUN apk add nodejs npm`
   - Supports all STDIO servers directly
   - Requires maintenance of custom image

### Recommended Solution
**Option 1: HTTP Gateway Pattern** - Most aligned with cloud-native architecture
- Create HTTP wrapper service for each MCP
- Deploy as separate microservices
- Configure LiteLLM to use HTTP transport instead of STDIO
- No modifications to LiteLLM container needed

### Alternative Solutions
**Option 2: Custom LiteLLM Image**
```dockerfile
FROM ghcr.io/berriai/litellm:main-stable
RUN apk add --no-cache nodejs npm docker-cli
COPY package.json .
RUN npm install
```

**Option 3: Sidecar Pattern**
- Run MCP servers as separate containers
- Use shared volume for communication
- Network them together in docker-compose

### Next Steps
1. Choose approach (recommend HTTP Gateway)
2. Implement solution for one MCP as proof of concept
3. Test MCP tool calling through LiteLLM API
4. Roll out to all 9 MCP servers
5. Configure Claude Code to use LiteLLM backend
6. Production deployment with monitoring

## Documentation
- Official Docs: https://docs.litellm.ai/
- API Reference: https://litellm.ai-servicers.com/docs
- GitHub: https://github.com/BerriAI/litellm