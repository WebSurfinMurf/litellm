# MCP-LiteLLM Integration Plan

## Overview
This document outlines the integration plan for connecting all 10 MCP servers to LiteLLM, enabling AI models accessed through LiteLLM to use MCP tools. Once validated, Claude Code will be reconfigured to use LiteLLM as its backend with full tool access.

## Current MCP Servers Status

### 1. **mcp-filesystem** (Docker-based)
- **Location**: `/home/administrator/projects/mcp/filesystem`
- **Transport**: stdio via Docker container
- **Current Setup**: Runs as Docker container `mcp-filesystem`
- **Tools**: 10 tools (read_file, write_file, list_directory, etc.)
- **LiteLLM Config**:
```yaml
mcp_servers:
  filesystem:
    transport: "stdio"
    command: "docker"
    args: ["run", "--rm", "-i", "-v", "/workspace:/workspace", "-v", "/projects:/projects", "mcp-filesystem"]
    description: "File system operations for workspace and projects"
```

### 2. **mcp-memory-postgres** (Node.js)
- **Location**: `/home/administrator/projects/mcp/memory-postgres`
- **Transport**: stdio via Node.js
- **Current Setup**: Node.js application connecting to PostgreSQL
- **Tools**: 3 tools (memory_create, memory_search, memory_list)
- **LiteLLM Config**:
```yaml
mcp_servers:
  memory:
    transport: "stdio"
    command: "node"
    args: ["/home/administrator/projects/mcp/memory-postgres/index.js"]
    env:
      POSTGRES_URL: "postgresql://admin:Pass123qp@localhost:5432/postgres"
    description: "Memory storage and retrieval system"
```

### 3. **mcp-fetch** (Docker-based)
- **Location**: `/home/administrator/projects/mcp/fetch`
- **Transport**: stdio via Docker container
- **Current Setup**: Runs as Docker container `mcp-fetch`
- **Tools**: 1 tool (fetch)
- **LiteLLM Config**:
```yaml
mcp_servers:
  fetch:
    transport: "stdio"
    command: "docker"
    args: ["run", "--rm", "-i", "mcp-fetch"]
    description: "Web content fetching and extraction"
```

### 4. **mcp-monitoring** (Node.js)
- **Location**: `/home/administrator/projects/mcp/monitoring`
- **Transport**: stdio via Node.js
- **Current Setup**: Node.js app connecting to Loki/Netdata
- **Tools**: 5 tools (search_logs, get_recent_errors, get_container_logs, etc.)
- **LiteLLM Config**:
```yaml
mcp_servers:
  monitoring:
    transport: "stdio"
    command: "node"
    args: ["/home/administrator/projects/mcp/monitoring/src/index.js"]
    env:
      LOKI_URL: "http://localhost:3100"
      NETDATA_URL: "http://localhost:19999"
    description: "System monitoring, logs, and metrics"
```

### 5. **mcp-github** (NPM package)
- **Location**: NPM package `@modelcontextprotocol/server-github`
- **Transport**: stdio via npx
- **Current Setup**: NPM package
- **Tools**: 20+ tools (search_repositories, create_issue, create_pull_request, etc.)
- **LiteLLM Config**:
```yaml
mcp_servers:
  github:
    transport: "stdio"
    command: "npx"
    args: ["-y", "@modelcontextprotocol/server-github"]
    env:
      GITHUB_TOKEN: "${GITHUB_TOKEN}"
    description: "GitHub repository operations and management"
```

### 6. **mcp-postgres** (Node.js)
- **Location**: `/home/administrator/projects/mcp/postgres`
- **Transport**: stdio via Node.js
- **Current Setup**: Node.js app for PostgreSQL operations
- **Tools**: 10 tools (list_schemas, execute_sql, explain_query, etc.)
- **LiteLLM Config**:
```yaml
mcp_servers:
  postgres:
    transport: "stdio"
    command: "node"
    args: ["/home/administrator/projects/mcp/postgres/build/index.js"]
    env:
      PGHOST: "localhost"
      PGPORT: "5432"
      PGUSER: "admin"
      PGPASSWORD: "Pass123qp"
      PGDATABASE: "postgres"
    description: "PostgreSQL database operations"
```

### 7. **mcp-n8n** (Node.js)
- **Location**: `/home/administrator/projects/mcp/n8n`
- **Transport**: stdio via wrapper script
- **Current Setup**: Node.js app with wrapper script
- **Tools**: 8 tools (list_workflows, execute_workflow, activate_workflow, etc.)
- **LiteLLM Config**:
```yaml
mcp_servers:
  n8n:
    transport: "stdio"
    command: "/home/administrator/projects/mcp/n8n/mcp-wrapper.sh"
    env:
      N8N_API_URL: "http://localhost:5678"
      N8N_API_KEY: "${N8N_API_KEY}"
    description: "n8n workflow automation"
```

### 8. **mcp-playwright** (Node.js)
- **Location**: `/home/administrator/projects/mcp/playwright`
- **Transport**: stdio via Node.js
- **Current Setup**: Node.js app connecting to Playwright service
- **Tools**: 7 tools (run_browser_test, navigate_and_screenshot, extract_page_data, etc.)
- **LiteLLM Config**:
```yaml
mcp_servers:
  playwright:
    transport: "stdio"
    command: "node"
    args: ["/home/administrator/projects/mcp/playwright/dist/index.js"]
    env:
      PLAYWRIGHT_API_URL: "http://localhost:3000"
    description: "Browser automation and testing"
```

### 9. **mcp-timescaledb** (Node.js)
- **Location**: `/home/administrator/projects/mcp/timescaledb`
- **Transport**: stdio via Node.js
- **Current Setup**: Node.js app for TimescaleDB operations
- **Tools**: 10 tools (tsdb_query, tsdb_create_hypertable, tsdb_database_stats, etc.)
- **LiteLLM Config**:
```yaml
mcp_servers:
  timescaledb:
    transport: "stdio"
    command: "node"
    args: ["/home/administrator/projects/mcp/timescaledb/build/index.js"]
    env:
      PGHOST: "localhost"
      PGPORT: "5433"
      PGUSER: "admin"
      PGPASSWORD: "TimescaleSecure2025"
      PGDATABASE: "postgres"
    description: "TimescaleDB time-series operations"
```

### 10. **OpenRouter MCP Servers** (Special Case)
These are AI model proxies, not traditional MCP tool servers:
- **mcp-openrouter-gpt5**: GPT-5 access via OpenRouter
- **mcp-openrouter-gemini**: Gemini access via OpenRouter
- **mcp-openrouter-claude**: Claude access via OpenRouter

**Note**: These don't need to be added as MCP servers in LiteLLM since LiteLLM already has these models configured directly.

## Implementation Steps

### Phase 1: Update LiteLLM Configuration
1. **Backup current config**: `cp config.yaml config.yaml.backup`
2. **Add MCP servers section** to `/home/administrator/projects/litellm/config.yaml`
3. **Add environment variables** to `/home/administrator/secrets/litellm.env`
4. **Restart LiteLLM** with new configuration

### Phase 2: Environment Setup
Create/update `/home/administrator/secrets/litellm.env`:
```bash
# Existing LiteLLM variables
DATABASE_URL=postgresql://admin:Pass123qp@postgres:5432/litellm_db
LITELLM_MASTER_KEY=sk-e0b742bc6575adf26c7d356c49c78d8fd08119fcde1d6e188d753999b5f956fc
UI_USERNAME=admin
UI_PASSWORD=LiteLLMAdmin2025!

# MCP-specific variables
GITHUB_TOKEN=<github_token>
N8N_API_KEY=<n8n_api_key>
POSTGRES_PASSWORD=Pass123qp
TIMESCALE_PASSWORD=TimescaleSecure2025
```

### Phase 3: Complete LiteLLM Config Addition
Add to `/home/administrator/projects/litellm/config.yaml`:
```yaml
# MCP Server Configuration
mcp_servers:
  filesystem:
    transport: "stdio"
    command: "docker"
    args: ["run", "--rm", "-i", "-v", "/workspace:/workspace", "-v", "/projects:/projects", "mcp-filesystem"]
    description: "File system operations"
    
  memory:
    transport: "stdio"
    command: "node"
    args: ["/home/administrator/projects/mcp/memory-postgres/index.js"]
    env:
      POSTGRES_URL: "postgresql://admin:Pass123qp@localhost:5432/postgres"
    description: "Memory storage system"
    
  fetch:
    transport: "stdio"
    command: "docker"
    args: ["run", "--rm", "-i", "mcp-fetch"]
    description: "Web content fetching"
    
  monitoring:
    transport: "stdio"
    command: "node"
    args: ["/home/administrator/projects/mcp/monitoring/src/index.js"]
    env:
      LOKI_URL: "http://localhost:3100"
      NETDATA_URL: "http://localhost:19999"
    description: "System monitoring"
    
  github:
    transport: "stdio"
    command: "npx"
    args: ["-y", "@modelcontextprotocol/server-github"]
    env:
      GITHUB_TOKEN: os.environ/GITHUB_TOKEN
    description: "GitHub operations"
    
  postgres:
    transport: "stdio"
    command: "node"
    args: ["/home/administrator/projects/mcp/postgres/build/index.js"]
    env:
      PGHOST: "localhost"
      PGPORT: "5432"
      PGUSER: "admin"
      PGPASSWORD: os.environ/POSTGRES_PASSWORD
      PGDATABASE: "postgres"
    description: "PostgreSQL operations"
    
  n8n:
    transport: "stdio"
    command: "/home/administrator/projects/mcp/n8n/mcp-wrapper.sh"
    env:
      N8N_API_URL: "http://localhost:5678"
      N8N_API_KEY: os.environ/N8N_API_KEY
    description: "Workflow automation"
    
  playwright:
    transport: "stdio"
    command: "node"
    args: ["/home/administrator/projects/mcp/playwright/dist/index.js"]
    env:
      PLAYWRIGHT_API_URL: "http://localhost:3000"
    description: "Browser automation"
    
  timescaledb:
    transport: "stdio"
    command: "node"
    args: ["/home/administrator/projects/mcp/timescaledb/build/index.js"]
    env:
      PGHOST: "localhost"
      PGPORT: "5433"
      PGUSER: "admin"
      PGPASSWORD: os.environ/TIMESCALE_PASSWORD
      PGDATABASE: "postgres"
    description: "TimescaleDB operations"

# Optional: MCP Aliases for easier access
litellm_settings:
  mcp_aliases:
    "fs": "filesystem"
    "mem": "memory"
    "web": "fetch"
    "logs": "monitoring"
    "gh": "github"
    "pg": "postgres"
    "wf": "n8n"
    "browser": "playwright"
    "tsdb": "timescaledb"
```

### Phase 4: Testing Strategy

#### 4.1 Individual MCP Server Tests
Test each MCP server individually through LiteLLM API:
```bash
# Test filesystem MCP
curl -X POST https://litellm.ai-servicers.com/v1/chat/completions \
  -H "Authorization: Bearer $LITELLM_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gpt-4o",
    "messages": [{"role": "user", "content": "List files in /workspace"}],
    "tools": "auto",
    "tool_choice": "auto"
  }'
```

#### 4.2 Cross-MCP Integration Test
Test multiple MCP servers in one request:
```bash
# Read file, search logs, and check database
curl -X POST https://litellm.ai-servicers.com/v1/chat/completions \
  -H "Authorization: Bearer $LITELLM_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "claude-opus-4.1",
    "messages": [{"role": "user", "content": "Read /workspace/config.yaml, search for errors in logs, and list database schemas"}],
    "tools": "auto"
  }'
```

### Phase 5: Claude Code Reconfiguration

Once MCP integration is validated in LiteLLM:

1. **Create new MCP server config** for Claude Code to use LiteLLM:
```json
{
  "mcpServers": {
    "litellm-gateway": {
      "command": "node",
      "args": ["/home/administrator/projects/litellm-mcp-bridge/index.js"],
      "env": {
        "LITELLM_API_URL": "https://litellm.ai-servicers.com",
        "LITELLM_API_KEY": "sk-e0b742bc6575adf26c7d356c49c78d8fd08119fcde1d6e188d753999b5f956fc"
      }
    }
  }
}
```

2. **Create bridge service** that translates Claude Code MCP requests to LiteLLM API calls

3. **Test Claude Code** with LiteLLM backend

## Current Status (2025-09-06)

### Completed
- ✅ All 9 MCP servers configured in LiteLLM config.yaml
- ✅ Environment variables set in litellm.env
- ✅ LiteLLM restarted with new configuration
- ✅ Deploy script updated with volume mounts
- ✅ Host references updated to host.docker.internal

### Issues Discovered
- ❌ Node.js not available in LiteLLM container
- ❌ MCP stdio servers cannot execute without Node.js
- ❌ Docker-based MCP servers need Docker-in-Docker setup
- ❌ Path resolution issues between container and host

### Solution Required
The current LiteLLM Docker image (ghcr.io/berriai/litellm-database:main-stable) doesn't include Node.js, which is required for stdio MCP servers. Options:

1. **Build Custom LiteLLM Image**
   ```dockerfile
   FROM ghcr.io/berriai/litellm-database:main-stable
   RUN apk add --no-cache nodejs npm
   ```

2. **Create MCP-HTTP Bridge**
   - Deploy service on host that exposes MCP tools as HTTP endpoints
   - Configure LiteLLM to use HTTP transport instead of stdio

3. **Use Host Network Mode**
   - Run LiteLLM with `--network host`
   - Security implications need evaluation

## Validation Checklist

- ✅ All 9 MCP servers configured in LiteLLM config.yaml
- ✅ Environment variables set in litellm.env
- ✅ LiteLLM restarted with new configuration
- ⚠️ Each MCP server configured but not executable (Node.js missing)
- ❌ Cross-MCP functionality tested
- ❌ Tool discovery working (`GET /v1/tools`)
- ❌ Tool execution working via chat completions
- ❌ Error handling tested (invalid tools, failed executions)
- ❌ Claude Code bridge created and tested
- ✅ Documentation updated

## Benefits of This Integration

1. **Unified API**: Single endpoint for all AI models and tools
2. **Model Flexibility**: Any model can use any MCP tool
3. **Cost Tracking**: LiteLLM tracks usage across models and tools
4. **Load Balancing**: Automatic routing and failover
5. **Monitoring**: Centralized logging and metrics
6. **Access Control**: Fine-grained permissions per API key
7. **Standardization**: OpenAI-compatible API for everything

## Troubleshooting Guide

### Common Issues and Solutions

1. **MCP server not responding**
   - Check if the underlying service is running
   - Verify environment variables are set
   - Check file paths are absolute
   - Review LiteLLM logs: `docker logs litellm`

2. **Tool not found**
   - Verify MCP server is configured in config.yaml
   - Check tool name format: `server_name.tool_name`
   - Ensure LiteLLM was restarted after config change

3. **Permission denied**
   - Check Docker socket permissions for Docker-based MCPs
   - Verify file permissions for stdio executables
   - Ensure LiteLLM container has necessary network access

4. **Environment variable issues**
   - Verify variables are in litellm.env
   - Check `os.environ/` prefix in config.yaml
   - Restart LiteLLM after env changes

## Next Steps

1. **Immediate**: Implement Phase 1-3 (configuration)
2. **Today**: Complete Phase 4 (testing)
3. **Tomorrow**: Begin Phase 5 (Claude Code integration)
4. **This Week**: Full production deployment
5. **Future**: Add more MCP servers as needed

## Notes

- OpenRouter MCP servers (GPT5, Gemini, Claude) are AI model proxies, not tool servers
- These models are already configured in LiteLLM's model_list
- Focus is on the 9 tool-providing MCP servers
- Consider adding cost tracking for MCP tool usage

---
*Created: 2025-09-06*
*Purpose: Integration plan for MCP servers with LiteLLM*
*Status: Ready for implementation*