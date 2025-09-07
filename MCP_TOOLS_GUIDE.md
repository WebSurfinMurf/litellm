# MCP Tools Guide for Open WebUI

## Quick Reference: How to Use MCP Tools

### To List Available Tools
Ask any of these questions in Open WebUI:
- "What tools do you have available?"
- "List all MCP tools"
- "What functions can you use?"
- "Show me available functions"
- "What system capabilities do you have?"
- "List available functions"

### Available MCP Tools (9 Total)

#### 1. **list_mcp_tools**
- **Purpose**: Lists all available MCP tools and their capabilities
- **Example prompts**: 
  - "What MCP tools are available?"
  - "List all functions"

#### 2. **list_databases**
- **Purpose**: List all PostgreSQL databases
- **Example prompts**:
  - "List all PostgreSQL databases"
  - "Show me the databases"
  - "What databases are available?"

#### 3. **get_container_logs**
- **Purpose**: Get Docker container logs
- **Example prompts**:
  - "Show me the logs for litellm container"
  - "Get logs for open-webui"
  - "Check container logs for mcp-middleware"

#### 4. **list_directory** (Admin Only)
- **Purpose**: List files and directories
- **Example prompts**:
  - "List files in /home/administrator/projects"
  - "Show me what's in the current directory"
  - "Browse the /tmp folder"

#### 5. **search_logs**
- **Purpose**: Search system logs across all containers
- **Example prompts**:
  - "Search logs for errors in the last hour"
  - "Find log entries containing 'WARNING'"
  - "Search for authentication failures"

#### 6. **execute_sql** (Admin Only)
- **Purpose**: Execute SQL queries on databases
- **Example prompts**:
  - "Run SELECT * FROM users on litellm_db"
  - "Show tables in postgres database"
  - "Execute a count query on keycloak database"

#### 7. **get_system_metrics**
- **Purpose**: Get system performance metrics
- **Example prompts**:
  - "Show me system metrics"
  - "What's the CPU usage?"
  - "Check memory consumption"
  - "Get network statistics"

#### 8. **manage_docker** (Admin Only)
- **Purpose**: Manage Docker containers
- **Example prompts**:
  - "List all running containers"
  - "Restart the litellm container"
  - "Stop mcp-middleware"
  - "Show docker ps output"

#### 9. **fetch_url**
- **Purpose**: Fetch and analyze web content
- **Example prompts**:
  - "Fetch content from https://example.com"
  - "Get the webpage at https://api.github.com/status"
  - "Check if https://google.com is accessible"

## Tool Categories

### Database Tools
- `list_databases` - List PostgreSQL databases
- `execute_sql` - Run SQL queries (Admin)

### Monitoring Tools
- `get_container_logs` - Docker container logs
- `search_logs` - Search across all logs
- `get_system_metrics` - System performance data

### System Tools
- `list_directory` - Browse filesystem (Admin)
- `manage_docker` - Control containers (Admin)

### Network Tools
- `fetch_url` - Web content fetching

### Meta Tools
- `list_mcp_tools` - List all available tools

## Permission Levels

### Standard User Access
- list_mcp_tools
- list_databases
- get_container_logs
- search_logs
- get_system_metrics
- fetch_url

### Admin Only (Requires Special API Key)
- list_directory
- execute_sql
- manage_docker

## Tips for Using MCP Tools

1. **Be specific**: The more specific your request, the better the tool selection
2. **Chain operations**: You can ask for multiple operations in sequence
3. **Check permissions**: Admin tools won't work without proper API key
4. **Use natural language**: The AI understands context and intent

## Example Conversations

### Example 1: Database Investigation
```
User: "What databases do we have?"
AI: [Lists databases using list_databases]

User: "Can you check the tables in litellm_db?"
AI: [Uses execute_sql to show tables - requires admin]
```

### Example 2: System Monitoring
```
User: "How's the system performing?"
AI: [Uses get_system_metrics to show CPU, memory, disk, network]

User: "Show me recent errors in the logs"
AI: [Uses search_logs to find error entries]
```

### Example 3: Container Management
```
User: "List all containers and their status"
AI: [Uses manage_docker with 'ps' action]

User: "Show me the last 20 lines of litellm logs"
AI: [Uses get_container_logs with container_name='litellm']
```

## Current Status

- **Total Tools**: 9 MCP functions
- **Mock Data**: Currently using mock responses (real MCP proxy pending)
- **Auto-Injection**: Tools automatically added to all requests
- **Streaming**: Disabled for compatibility

## Testing in Open WebUI

1. Go to https://open-webui.ai-servicers.com/
2. Select any model (gpt-5-mini recommended for speed)
3. Try any of the example prompts above
4. Tools will be automatically executed when relevant

---
*Last Updated: 2025-09-07*
*Status: All tools operational with mock data*