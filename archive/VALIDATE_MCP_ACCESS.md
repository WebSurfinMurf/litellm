# How to Validate MCP Access from LiteLLM

## 🌐 LiteLLM UI Access

### Access the LiteLLM UI
1. Open your browser and go to: **https://litellm.ai-servicers.com/ui**
2. Login credentials:
   - Username: `admin`
   - Password: `LiteLLMAdmin2025!`

### Alternative Direct Access
If you have VPN or local access:
- Internal URL: http://litellm.ai-servicers.com:4000/ui (via container network)

## 🔍 Validation Steps in LiteLLM UI

### Step 1: Check Available Models
1. In the UI, navigate to **Models** section
2. You should see all configured models including:
   - gpt-4o-with-mcp (MCP-enabled model)
   - Standard models (gpt-5, claude-opus-4.1, gemini-2.5-pro, etc.)

### Step 2: Test Basic Chat Completion
1. Go to **Playground** or **Chat** section
2. Select a model (e.g., `gpt-4o-mini`)
3. Send a test message: "Hello, are you working?"
4. Verify you get a response

### Step 3: Test MCP Integration
Since MCP tools need to be called as functions, you'll need to test via API or use the playground with function calling:

1. In the **API Keys** section, get or create an API key
2. Use the **Test Request** feature or API playground
3. Try these test scenarios:

## 📝 API Validation Examples

### Test 1: Direct API Call with MCP Functions
```bash
# Get your API key from LiteLLM UI first
LITELLM_KEY="your-api-key-from-ui"

# Test with MCP-enabled model
curl https://litellm.ai-servicers.com/v1/chat/completions \
  -H "Authorization: Bearer $LITELLM_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gpt-4o",
    "messages": [
      {"role": "user", "content": "List the files in /tmp directory"}
    ],
    "tools": [{
      "type": "function",
      "function": {
        "name": "filesystem_list",
        "description": "List directory contents",
        "parameters": {
          "type": "object",
          "properties": {
            "path": {"type": "string"}
          },
          "required": ["path"]
        }
      }
    }],
    "tool_choice": "auto"
  }'
```

### Test 2: Check MCP Service Health
```bash
# Test MCP adapter directly
curl http://localhost:3333/health

# Response should show:
{
  "status": "healthy",
  "services": ["filesystem", "postgres", "fetch", "monitoring", "n8n", "playwright", "timescaledb"],
  "proxy_url": "http://mcp-proxy-sse:8080"
}
```

### Test 3: List Available MCP Functions
```bash
curl http://localhost:3333/v1/functions
```

## 🧪 MCP Service Tests via SSE

### Test Each MCP Service Individually

#### 1. Filesystem Service
```bash
curl -N http://localhost:8585/servers/filesystem/sse \
  -H "Accept: text/event-stream" --max-time 2
```

#### 2. PostgreSQL Service
```bash
curl -N http://localhost:8585/servers/postgres/sse \
  -H "Accept: text/event-stream" --max-time 2
```

#### 3. Fetch Service
```bash
curl -N http://localhost:8585/servers/fetch/sse \
  -H "Accept: text/event-stream" --max-time 2
```

#### 4. Monitoring Service
```bash
curl -N http://localhost:8585/servers/monitoring/sse \
  -H "Accept: text/event-stream" --max-time 2
```

## ✅ Validation Checklist

### Infrastructure Check
- [ ] LiteLLM UI accessible at https://litellm.ai-servicers.com/ui
- [ ] Can login with admin credentials
- [ ] Models are listed in the UI
- [ ] Basic chat completion works

### MCP Services Check
- [ ] MCP adapter running on port 3333
- [ ] MCP proxy running on port 8585
- [ ] All 7 MCP services respond to SSE requests
- [ ] Health endpoint returns all services

### Integration Check
- [ ] Can call MCP functions via API
- [ ] Function results are returned correctly
- [ ] Error handling works for invalid requests

## 🚀 Quick Test Script

Run this Python script to validate everything:
```python
python3 /home/administrator/projects/litellm/test-mcp-integration.py
```

Expected output:
```
✅ filesystem: Connected successfully
✅ postgres: Connected successfully
✅ fetch: Connected successfully
✅ monitoring: Connected successfully
✅ n8n: Connected successfully
✅ playwright: Connected successfully
✅ timescaledb: Connected successfully
Working services: 7/7
```

## 📊 Monitoring in UI

In the LiteLLM UI, you can monitor:
1. **Usage & Analytics**: See API calls and token usage
2. **Logs**: View request/response logs
3. **Teams & Users**: Manage access keys
4. **Models**: Configure and test models
5. **Settings**: Adjust configuration

## 🔧 Troubleshooting

### If LiteLLM UI is not accessible:
```bash
# Check if container is running
docker ps | grep litellm

# Check logs
docker logs litellm --tail 50

# Restart if needed
docker restart litellm
```

### If MCP services don't work:
```bash
# Check MCP proxy
docker ps | grep mcp-proxy-sse
docker logs mcp-proxy-sse --tail 20

# Check MCP adapter
docker ps | grep mcp-litellm-adapter
docker logs mcp-litellm-adapter --tail 20

# Restart services
docker restart mcp-proxy-sse
docker restart mcp-litellm-adapter
```

## 📝 Notes

- The MCP integration is available but requires proper function calling format
- LiteLLM acts as a proxy and router for multiple LLM providers
- MCP tools are exposed as OpenAI-compatible functions
- The adapter at port 3333 bridges MCP SSE protocol to REST API

---
*Last Updated: 2025-09-07*
*All 7 MCP services are operational and accessible via SSE*