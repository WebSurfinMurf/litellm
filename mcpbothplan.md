# Unified MCP Tool System Implementation Plan
## Define Once, Use Everywhere Architecture

*Created: 2025-09-07*
*Author: Claude Code*
*Goal: Create a centralized MCP tool definition system that works with both Claude Code and LiteLLM*

## Executive Summary

We will create a unified tool management system where MCP tools are defined once in a central registry and made accessible to:
1. **Claude Code** - Via a custom MCP server adapter using JSON-RPC over stdio
2. **LiteLLM** - Via the existing middleware or a new adapter that formats tools for OpenAI-compatible API

This approach eliminates duplication, ensures consistency, and allows us to leverage the existing MCP infrastructure while making it accessible to both platforms.

## Current State Analysis

### What We Have
1. **7 Working MCP Services** via SSE Proxy Gateway (port 8585):
   - filesystem, fetch, postgres, timescaledb, monitoring, n8n, playwright
   - All containerized with standardized naming (`mcp-{service}`)
   - Accessible via HTTP/SSE endpoints

2. **LiteLLM MCP Middleware** (port 4001):
   - 23 mock tool implementations
   - Auto-injection capability
   - Works with Open WebUI

3. **Claude Code Configuration**:
   - Can launch MCP servers via stdio
   - Configured in `~/.config/claude/claude_desktop_config.json`
   - Currently not using our MCP services

### The Gap
- Claude Code and LiteLLM use different protocols
- No shared tool definitions
- Mock implementations in middleware don't connect to real MCP services
- Need a bridge between SSE proxy and both platforms

## Proposed Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                   Central Tool Registry                      │
│              /projects/mcp/unified-registry/                 │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │          tool_definitions.py                          │  │
│  │  - Single source of truth for all tool definitions    │  │
│  │  - Maps to actual MCP service endpoints               │  │
│  │  - Includes schemas, descriptions, parameters         │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────┬───────────────────────┬──────────────────┘
                  │                       │
         ┌────────▼────────┐     ┌───────▼────────┐
         │ Claude Adapter  │     │ LiteLLM Adapter│
         │ (stdio/JSON-RPC)│     │ (HTTP/OpenAI)  │
         └────────┬────────┘     └───────┬────────┘
                  │                       │
         ┌────────▼────────┐     ┌───────▼────────┐
         │  Claude Code    │     │    LiteLLM     │
         └─────────────────┘     └────────────────┘
                  │                       │
                  └───────────┬───────────┘
                              │
                  ┌───────────▼───────────┐
                  │   MCP SSE Proxy       │
                  │   (Port 8585)         │
                  └───────────┬───────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │         Real MCP Services                  │
        │  filesystem, postgres, monitoring, etc.    │
        └────────────────────────────────────────────┘
```

## Implementation Plan

### Phase 1: Central Tool Registry (Day 1)
**Location**: `/home/administrator/projects/mcp/unified-registry/`

#### 1.1 Create Tool Definition Structure
```python
# tool_definitions.py
TOOL_DEFINITIONS = {
    "filesystem": {
        "service": "filesystem",
        "endpoint": "http://localhost:8585/servers/filesystem/sse",
        "tools": [
            {
                "name": "read_file",
                "description": "Read contents of a file",
                "parameters_schema": {...},
                "mcp_method": "tools/call",
                "mcp_tool_name": "read_file"
            }
        ]
    },
    "postgres": {
        "service": "postgres",
        "endpoint": "http://localhost:8585/servers/postgres/sse",
        "tools": [...]
    }
    # ... other services
}
```

#### 1.2 Create Tool Implementation Bridge
```python
# tool_bridge.py
class MCPToolBridge:
    """Handles actual communication with MCP services via SSE proxy"""
    
    def execute_tool(self, service: str, tool_name: str, params: dict):
        """Execute a tool on the specified MCP service"""
        # Connect to SSE endpoint
        # Send JSON-RPC request
        # Parse response
        # Return result
```

### Phase 2: Claude Code Adapter (Day 1-2)
**Location**: `/home/administrator/projects/mcp/unified-registry/claude_adapter.py`

#### 2.1 MCP Server Implementation
```python
# claude_adapter.py
import sys
import json
from tool_definitions import TOOL_DEFINITIONS
from tool_bridge import MCPToolBridge

class ClaudeMCPAdapter:
    """MCP server that Claude Code can launch via stdio"""
    
    def handle_tools_list(self):
        """Return all tools in MCP format"""
        
    def handle_tools_call(self, tool_name, arguments):
        """Execute tool and return result"""
        
    def run_stdio_loop(self):
        """Main JSON-RPC over stdio loop"""
```

#### 2.2 Claude Configuration Update
```json
// ~/.config/claude/claude_desktop_config.json
{
  "mcpServers": {
    "unified-tools": {
      "command": "python3",
      "args": ["/home/administrator/projects/mcp/unified-registry/claude_adapter.py"]
    }
  }
}
```

### Phase 3: LiteLLM Adapter (Day 2)
**Location**: `/home/administrator/projects/mcp/unified-registry/litellm_adapter.py`

#### 3.1 Option A: Direct Integration
```python
# litellm_adapter.py
def get_litellm_tools():
    """Convert tool definitions to OpenAI function calling format"""
    tools = []
    for service in TOOL_DEFINITIONS.values():
        for tool in service["tools"]:
            tools.append({
                "type": "function",
                "function": {
                    "name": tool["name"],
                    "description": tool["description"],
                    "parameters": tool["parameters_schema"]
                }
            })
    return tools

async def execute_litellm_tool(name: str, arguments: dict):
    """Execute tool for LiteLLM"""
    bridge = MCPToolBridge()
    # Find tool in registry
    # Execute via bridge
    # Return formatted response
```

#### 3.2 Option B: Update Existing Middleware
Modify `/home/administrator/projects/litellm/middleware/` to:
1. Import unified tool definitions
2. Replace mock implementations with real MCP calls
3. Keep auto-injection and error handling

### Phase 4: Testing & Validation (Day 2-3)

#### 4.1 Test Matrix
| Platform | Tool | Expected Result | Status |
|----------|------|-----------------|--------|
| Claude Code | filesystem.read_file | File contents | ⏳ |
| Claude Code | postgres.list_databases | Database list | ⏳ |
| LiteLLM | filesystem.read_file | File contents | ⏳ |
| LiteLLM | postgres.list_databases | Database list | ⏳ |

#### 4.2 Test Scripts
```bash
# test_claude.sh
echo "Testing Claude Code integration..."
# Send test request to Claude

# test_litellm.sh
echo "Testing LiteLLM integration..."
curl -X POST http://localhost:4001/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gpt-4",
    "messages": [{"role": "user", "content": "List all databases"}],
    "tools": "auto"
  }'
```

### Phase 5: Production Deployment (Day 3)

#### 5.1 Deployment Checklist
- [ ] All 7 MCP services mapped in registry
- [ ] Claude adapter tested with all tools
- [ ] LiteLLM adapter integrated
- [ ] Documentation updated
- [ ] Monitoring configured
- [ ] Backup of existing configurations

#### 5.2 Deployment Script
```bash
#!/bin/bash
# deploy_unified_mcp.sh

# 1. Stop existing services
docker stop mcp-middleware

# 2. Deploy new adapters
cd /home/administrator/projects/mcp/unified-registry
./deploy.sh

# 3. Update Claude configuration
cp claude_config.json ~/.config/claude/claude_desktop_config.json

# 4. Restart services
systemctl restart claude-code
docker restart litellm

# 5. Run validation tests
./test_all.sh
```

## File Structure

```
/home/administrator/projects/mcp/unified-registry/
├── tool_definitions.py      # Central tool registry
├── tool_bridge.py           # MCP service communication
├── claude_adapter.py        # Claude Code MCP server
├── litellm_adapter.py       # LiteLLM adapter
├── requirements.txt         # Python dependencies
├── deploy.sh               # Deployment script
├── test_claude.sh          # Claude testing
├── test_litellm.sh         # LiteLLM testing
├── test_all.sh            # Full test suite
└── README.md              # Documentation
```

## Key Benefits

1. **Single Source of Truth**: One place to define all tools
2. **No Duplication**: Same tools work everywhere
3. **Easy Maintenance**: Update once, deploy everywhere
4. **Cost Efficient**: Claude Code uses local execution
5. **Scalable**: Easy to add new MCP services
6. **Production Ready**: Leverages existing infrastructure

## Risk Mitigation

| Risk | Mitigation |
|------|------------|
| Breaking existing integrations | Keep backups, test thoroughly |
| Performance overhead | Use connection pooling, caching |
| SSE proxy failures | Implement retry logic, health checks |
| Tool discovery issues | Comprehensive logging, debugging mode |

## Success Metrics

- ✅ All 7 MCP services accessible from Claude Code
- ✅ All 7 MCP services accessible from LiteLLM
- ✅ Zero duplicate tool definitions
- ✅ < 100ms tool discovery latency
- ✅ < 500ms tool execution latency
- ✅ 100% test coverage

## Next Steps

1. **Immediate** (Today):
   - Create `/home/administrator/projects/mcp/unified-registry/` directory
   - Start with 2 example tools (filesystem.read_file, postgres.list_databases)
   - Implement basic Claude adapter

2. **Short Term** (This Week):
   - Complete all 7 service integrations
   - Full testing suite
   - Production deployment

3. **Long Term** (Next Month):
   - Add remaining MCP services
   - Performance optimization
   - Monitoring dashboard
   - Auto-discovery of new MCP services

## Questions to Resolve

1. Should we keep the existing middleware or replace it entirely?
2. Do we want to support streaming responses?
3. Should tool definitions be in Python or JSON?
4. How do we handle authentication for different services?
5. Should we implement caching for frequently used tools?

## Implementation Commands

```bash
# Create project structure
mkdir -p /home/administrator/projects/mcp/unified-registry
cd /home/administrator/projects/mcp/unified-registry

# Start implementation
touch tool_definitions.py tool_bridge.py claude_adapter.py litellm_adapter.py
touch requirements.txt deploy.sh test_all.sh README.md

# Begin with Phase 1
vim tool_definitions.py
```

---
*This plan provides a clear path to unified MCP tool management across both Claude Code and LiteLLM platforms.*