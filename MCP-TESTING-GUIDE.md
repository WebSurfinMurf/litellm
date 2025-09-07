# MCP Testing Guide for LiteLLM

## Testing in Open WebUI (Recommended)

Open WebUI provides the best interface for testing MCP tools interactively.

### Access Open WebUI
1. Go to: https://open-webui.ai-servicers.com
2. Login with your credentials
3. Select a model (e.g., gpt-4o-mini)

### Test Commands to Try

#### 1. Test Filesystem Access (Admin Only)
```
List all files in /home/administrator/projects
```
Expected: Admin users see file list, Developer users get error or fallback response

```
Show me the contents of /home/administrator/projects/litellm/config.yaml
```
Expected: Admin can read file, Developer cannot

#### 2. Test PostgreSQL Access (Both Admin & Developer)
```
Show me all databases in PostgreSQL
```
Expected: Both roles should see database list

```
List all tables in the postgres database
```
Expected: Both roles can query

#### 3. Test Monitoring Access (Both Roles)
```
Show me recent error logs from any service
```
Expected: Both can see logs

```
Check the health status of running containers
```
Expected: Both can check status

#### 4. Test Fetch/Web Access (Both Roles)
```
Fetch the content from https://example.com
```
Expected: Both can fetch web content

#### 5. Test n8n Workflows (Both Roles)
```
List all available n8n workflows
```
Expected: Both can see workflows

## Testing via API/curl

### With Admin Key (has filesystem access):
```bash
curl -X POST http://localhost:4000/v1/chat/completions \
  -H "Authorization: Bearer sk-pFgey4HPR9qDvyT-N_7yVQ" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gpt-4o-mini",
    "messages": [
      {
        "role": "user",
        "content": "List files in /home/administrator/projects"
      }
    ],
    "stream": false
  }'
```

### With Developer Key (no filesystem access):
```bash
curl -X POST http://localhost:4000/v1/chat/completions \
  -H "Authorization: Bearer sk-nzq2BIYVoVUpz5csqr69xA" \
  -H "Content-Type": "application/json" \
  -d '{
    "model": "gpt-4o-mini",
    "messages": [
      {
        "role": "user",
        "content": "List files in /home/administrator/projects"
      }
    ],
    "stream": false
  }'
```

## Expected Behaviors

### Admin Key (sk-pFgey4HPR9qDvyT-N_7yVQ)
✅ Can access:
- filesystem (full /home/administrator access)
- postgres (database queries)
- fetch (web content)
- monitoring (logs and metrics)
- n8n (workflows)
- playwright (browser automation)
- timescaledb (time-series data)

### Developer Key (sk-nzq2BIYVoVUpz5csqr69xA)
✅ Can access:
- postgres (database queries)
- fetch (web content)
- monitoring (logs and metrics)
- n8n (workflows)
- playwright (browser automation)
- timescaledb (time-series data)

❌ Cannot access:
- filesystem (blocked for security)

## How MCP Tools Work

MCP tools are exposed as "function calling" capabilities in LLMs. When you ask something like "list files in a directory", the model:

1. Recognizes it needs to use a tool
2. Calls the appropriate MCP function (e.g., filesystem.list)
3. Receives the result
4. Formats it into a human-readable response

## Troubleshooting

### If MCP tools aren't working:

1. **Check MCP proxy is running:**
```bash
docker ps | grep mcp-proxy-sse
```

2. **Verify network connectivity:**
```bash
docker exec litellm ping -c 1 mcp-proxy-sse
```

3. **Check MCP endpoints from LiteLLM:**
```bash
docker exec litellm wget -qO- --timeout=2 http://mcp-proxy-sse:8080/servers/filesystem/sse
```

4. **Review LiteLLM logs:**
```bash
docker logs litellm --tail 50
```

5. **Check MCP configuration in config.yaml:**
```bash
docker exec litellm grep -A5 mcp_servers /app/config.yaml
```

## Important Notes

1. **MCP tools are not explicitly visible** in the UI - they work behind the scenes
2. **The model decides** when to use tools based on your prompt
3. **Role-based access** is enforced at the API key level
4. **Network isolation** ensures MCP proxy is only accessible from LiteLLM

## Security Validation

To verify the security model is working:

1. **From host (should fail):**
```bash
curl http://localhost:8585/servers/filesystem/sse
# Expected: Connection refused
```

2. **From LiteLLM container (should work):**
```bash
docker exec litellm wget -qO- --timeout=1 http://mcp-proxy-sse:8080/servers/filesystem/sse
# Expected: SSE connection (timeout is normal)
```

---
*Created: 2025-09-07*
*Architecture: LiteLLM → Docker Network → MCP Proxy → MCP Services*