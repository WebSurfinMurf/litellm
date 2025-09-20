# Testing MCP Access in Open WebUI

## Current Status
- ✅ MCP Services are running (7/7 operational)
- ✅ LiteLLM is connected to Open WebUI
- ⚠️ MCP tools are not yet configured as functions in LiteLLM models

## What's Working Now
The MCP services are operational and responding at the SSE endpoints, but they need to be configured as "tools" or "functions" in the LiteLLM model configuration for GPT-5 or other models to use them.

## Questions You CAN Test Now in Open WebUI

Since MCP integration requires function calling configuration, standard questions won't trigger MCP tools automatically. However, you can test the base LiteLLM connectivity with these:

### 1. Test Basic LiteLLM Connection
```
"What models are you running on?"
```
Expected: Should mention it's using GPT-5 or whichever model you selected

### 2. Test General Knowledge
```
"Explain what PostgreSQL is in one sentence"
```
Expected: Should give a proper response, confirming LiteLLM is working

### 3. Test Code Generation
```
"Write a Python function to connect to PostgreSQL"
```
Expected: Should generate code, confirming the model is working through LiteLLM

## To Enable MCP Function Calling

For MCP tools to work with questions like "List all PostgreSQL databases", we need to:

### Option 1: Configure Functions in LiteLLM (Recommended)
Update `/home/administrator/projects/litellm/config.yaml` to add function definitions:

```yaml
model_list:
  - model_name: gpt-5-with-mcp
    litellm_params:
      model: gpt-5
      api_key: os.environ/OPENAI_API_KEY
      functions:
        - name: query_postgres
          description: Execute PostgreSQL queries
          parameters:
            type: object
            properties:
              query:
                type: string
                description: SQL query to execute
            required: ["query"]
        
        - name: fetch_url
          description: Fetch content from a URL
          parameters:
            type: object
            properties:
              url:
                type: string
                description: URL to fetch
            required: ["url"]
        
        - name: get_logs
          description: Get system logs
          parameters:
            type: object
            properties:
              query:
                type: string
                description: Log search query
              hours:
                type: integer
                description: Hours to look back
            required: ["query"]
```

Then restart LiteLLM:
```bash
docker restart litellm
```

### Option 2: Use Custom Routing
Create a middleware that intercepts function calls and routes them to MCP:

```python
# In LiteLLM custom_callbacks or middleware
def route_to_mcp(function_name, parameters):
    if function_name == "query_postgres":
        # Route to MCP postgres service
        response = requests.post(
            "http://localhost:8585/servers/postgres/messages/",
            json={"method": "query", "params": parameters}
        )
        return response.json()
```

### Option 3: Direct MCP Testing (Outside Open WebUI)
Test MCP directly using curl:

```bash
# Create a session and execute a PostgreSQL query
SESSION_ID=$(curl -s http://localhost:8585/servers/postgres/sse \
  -H "Accept: text/event-stream" --max-time 1 2>/dev/null | \
  grep "session_id" | cut -d'=' -f2)

# Send a query to that session
curl -X POST "http://localhost:8585/servers/postgres/messages/?session_id=${SESSION_ID}" \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "tools/call",
    "params": {
      "name": "query",
      "arguments": {
        "query": "SELECT datname FROM pg_database;"
      }
    },
    "id": 1
  }'
```

## What You Can Test RIGHT NOW

In Open WebUI, you can verify the base infrastructure:

1. **Test Model Selection**: Switch between GPT-5, Claude, and Gemini models
2. **Test Response Quality**: Ask complex questions to verify LiteLLM routing
3. **Test Conversation Memory**: Have a multi-turn conversation
4. **Test Token Limits**: Ask for long responses

## Actual MCP Function Test

To truly test MCP integration, you need function calling configured. Here's what would work once configured:

```
User: "Query the PostgreSQL database and list all databases"
Expected: GPT-5 calls query_postgres function → MCP executes → Returns actual database list
```

Without function configuration, GPT-5 will just give you generic PostgreSQL commands rather than executing them.

## Summary

- **MCP Services**: ✅ All running and accessible
- **LiteLLM**: ✅ Working and connected to Open WebUI
- **Function Routing**: ⚠️ Needs configuration to connect MCP to LiteLLM
- **Open WebUI**: ✅ Can use all LiteLLM models

The infrastructure is ready, but the function calling bridge between LiteLLM and MCP needs to be configured for full integration.