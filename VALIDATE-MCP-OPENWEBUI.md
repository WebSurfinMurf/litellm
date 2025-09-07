# Validating MCP Tools in Open WebUI

## Quick Access
- **URL**: https://open-webui.ai-servicers.com
- **Test Key**: sk-e0b742bc6575adf26c7d356c49c78d8fd08119fcde1d6e188d753999b5f956fc

## Validation Test Prompts

### Test 1: PostgreSQL Database List (Recommended)
This tests the `list_databases` MCP tool without any filesystem access.

**Prompt to use:**
```
List all PostgreSQL databases available on this system
```

**Expected Response (with working MCP):**
```
The PostgreSQL databases available are:
1. postgres
2. litellm_db
3. keycloak
4. n8n
5. grafana
```

**Without MCP (failure indication):**
```
I don't have direct access to list databases...
OR
I cannot directly query PostgreSQL...
```

### Test 2: Container Logs (Monitoring MCP)
This tests the `get_container_logs` tool - safe and useful.

**Prompt to use:**
```
Show me the last 5 logs from the litellm container
```

**Expected Response (with working MCP):**
```
Here are the last 5 logs from the litellm container:
1. 2025-09-07 20:30:00 INFO Container started
2. 2025-09-07 20:30:01 INFO Health check passed
3. 2025-09-07 20:30:02 INFO Ready to serve
4. 2025-09-07 20:30:03 INFO Processing request
5. 2025-09-07 20:30:04 INFO Request completed
```

### Test 3: Role-Based Access Test
Test with developer key to verify permission system.

**Setup**: Create a new API key in Open WebUI settings or use developer key
**Prompt to use:**
```
List files in /home/administrator/projects
```

**Expected with Admin Key:**
```
Files: project1, project2, README.md, config.yaml
Directories: src, tests, docs
```

**Expected with Developer Key:**
```
Permission denied for filesystem access
OR
I don't have permission to access that directory
```

## Step-by-Step Validation Process

### 1. Access Open WebUI
```bash
# Check if running
docker ps | grep open-webui

# View logs if needed
docker logs open-webui --tail 20
```

Navigate to: https://open-webui.ai-servicers.com

### 2. Select a Model
Choose any model from the dropdown:
- `gpt-4o-mini` (fast, good for testing)
- `claude-sonnet-4` (reliable)
- `gemini-2.5-flash` (quick)

### 3. Run Test Prompts
Copy and paste each test prompt above and observe responses.

### 4. Check Middleware Logs
Monitor what's happening behind the scenes:
```bash
# Watch middleware logs in real-time
docker logs -f mcp-middleware --tail 20
```

You should see:
```
INFO:__main__:Model requested 1 tool calls
INFO:__main__:Executing MCP function: list_databases with args: {}
```

### 5. Verify Tool Execution
Success indicators in logs:
- ✅ "Model requested X tool calls"
- ✅ "Executing MCP function: [function_name]"
- ✅ Model response includes actual data

Failure indicators:
- ❌ No "tool calls" in logs
- ❌ Model gives generic response
- ❌ "I don't have access" type responses

## Quick Validation Script

Run this to test programmatically:
```bash
curl -X POST http://localhost:4001/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer sk-e0b742bc6575adf26c7d356c49c78d8fd08119fcde1d6e188d753999b5f956fc" \
  -d '{
    "model": "gpt-4o-mini",
    "messages": [
      {"role": "user", "content": "List all PostgreSQL databases"}
    ],
    "tools": [{
      "type": "function",
      "function": {
        "name": "list_databases",
        "description": "List all PostgreSQL databases",
        "parameters": {"type": "object", "properties": {}}
      }
    }],
    "tool_choice": "auto"
  }' | jq -r '.choices[0].message.content'
```

## Troubleshooting

### If tools aren't being called:

1. **Check middleware is running:**
```bash
curl http://localhost:4001/health
# Should return: {"status":"healthy","service":"mcp-middleware"}
```

2. **Verify Open WebUI is using middleware:**
```bash
docker inspect open-webui | grep OPENAI_API_BASE_URL
# Should show: "OPENAI_API_BASE_URL=http://mcp-middleware:4001/v1"
```

3. **Restart services if needed:**
```bash
# Restart middleware
cd /home/administrator/projects/litellm/middleware
docker compose restart

# Restart Open WebUI with correct endpoint
docker restart open-webui
```

4. **Check network connectivity:**
```bash
docker exec open-webui ping -c 1 mcp-middleware
```

## Current Status

As of the last update:
- ✅ Middleware is running with mock data
- ✅ Open WebUI configured to use middleware
- ✅ Models successfully detecting and calling tools
- ✅ Tool results being returned to users
- ⚠️ Real MCP proxy connection pending (using mock data)

## Security Notes

- Admin API key has full access to all MCP tools
- Developer keys restricted from filesystem access
- All tool executions logged in middleware
- Mock data safe for testing without real system access

## Next Steps

Once validation confirms tools are working:
1. Fix MCP proxy container (add Node.js support)
2. Connect to real MCP services instead of mock data
3. Add more granular permission controls
4. Implement audit logging for compliance

---
*Created: 2025-09-07*
*Purpose: Validate MCP tool integration through Open WebUI*