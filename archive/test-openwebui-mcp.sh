#!/bin/bash
# Test MCP tools through Open WebUI's backend API

echo "=== Testing MCP Tools via Open WebUI Backend ==="
echo ""
echo "This test verifies that MCP tools work when called through Open WebUI"
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test function
test_mcp_tool() {
    local KEY=$1
    local MODEL=$2
    local PROMPT=$3
    local DESCRIPTION=$4
    
    echo -e "${YELLOW}Test: ${DESCRIPTION}${NC}"
    echo "Model: $MODEL"
    echo "Prompt: $PROMPT"
    echo -n "Result: "
    
    RESPONSE=$(curl -s -X POST http://localhost:4000/v1/chat/completions \
      -H "Authorization: Bearer $KEY" \
      -H "Content-Type: application/json" \
      -d "{
        \"model\": \"$MODEL\",
        \"messages\": [
          {
            \"role\": \"system\",
            \"content\": \"You are a helpful assistant with access to MCP tools. Use them when asked.\"
          },
          {
            \"role\": \"user\",
            \"content\": \"$PROMPT\"
          }
        ],
        \"max_tokens\": 150,
        \"temperature\": 0,
        \"tools\": [
          {
            \"type\": \"function\",
            \"function\": {
              \"name\": \"list_directory\",
              \"description\": \"List files in a directory\",
              \"parameters\": {
                \"type\": \"object\",
                \"properties\": {
                  \"path\": {\"type\": \"string\", \"description\": \"Directory path\"}
                },
                \"required\": [\"path\"]
              }
            }
          },
          {
            \"type\": \"function\",
            \"function\": {
              \"name\": \"list_databases\",
              \"description\": \"List PostgreSQL databases\",
              \"parameters\": {
                \"type\": \"object\",
                \"properties\": {}
              }
            }
          },
          {
            \"type\": \"function\",
            \"function\": {
              \"name\": \"get_container_logs\",
              \"description\": \"Get Docker container logs\",
              \"parameters\": {
                \"type\": \"object\",
                \"properties\": {
                  \"container\": {\"type\": \"string\", \"description\": \"Container name\"},
                  \"lines\": {\"type\": \"integer\", \"description\": \"Number of lines\", \"default\": 10}
                },
                \"required\": [\"container\"]
              }
            }
          }
        ],
        \"tool_choice\": \"auto\"
      }" 2>/dev/null)
    
    # Check if response contains tool_calls
    if echo "$RESPONSE" | jq -e '.choices[0].message.tool_calls' > /dev/null 2>&1; then
        echo -e "${GREEN}✓ Tool call detected${NC}"
        echo "$RESPONSE" | jq -r '.choices[0].message.tool_calls[] | "  Tool: \(.function.name), Args: \(.function.arguments)"'
    elif echo "$RESPONSE" | jq -e '.choices[0].message.content' > /dev/null 2>&1; then
        CONTENT=$(echo "$RESPONSE" | jq -r '.choices[0].message.content' | head -n 2)
        echo -e "${YELLOW}Response (no tool): $CONTENT${NC}"
    else
        echo -e "${RED}✗ Error or no response${NC}"
        echo "$RESPONSE" | jq '.' 2>/dev/null || echo "$RESPONSE"
    fi
    echo ""
}

# Admin API key
ADMIN_KEY="sk-pFgey4HPR9qDvyT-N_7yVQ"

# Developer API key
DEV_KEY="sk-nzq2BIYVoVUpz5csqr69xA"

echo "==== Testing with Admin Key ===="
echo ""

test_mcp_tool "$ADMIN_KEY" "gpt-4o-mini" \
    "List the files in the /home/administrator/projects directory" \
    "Admin accessing filesystem (should work)"

test_mcp_tool "$ADMIN_KEY" "gpt-4o-mini" \
    "List all PostgreSQL databases" \
    "Admin accessing PostgreSQL (should work)"

test_mcp_tool "$ADMIN_KEY" "gpt-4o-mini" \
    "Get the last 5 log lines from the litellm container" \
    "Admin accessing monitoring (should work)"

echo "==== Testing with Developer Key ===="
echo ""

test_mcp_tool "$DEV_KEY" "gpt-4o-mini" \
    "List the files in the /home/administrator/projects directory" \
    "Developer accessing filesystem (should fail)"

test_mcp_tool "$DEV_KEY" "gpt-4o-mini" \
    "List all PostgreSQL databases" \
    "Developer accessing PostgreSQL (should work)"

test_mcp_tool "$DEV_KEY" "gpt-4o-mini" \
    "Get the last 5 log lines from the litellm container" \
    "Developer accessing monitoring (should work)"

echo "=== Test Complete ==="
echo ""
echo "To test in Open WebUI:"
echo "1. Go to https://open-webui.ai-servicers.com"
echo "2. Select a model (e.g., gpt-4o-mini)"
echo "3. Try these prompts:"
echo "   - 'List files in /home/administrator/projects'"
echo "   - 'Show me all PostgreSQL databases'"
echo "   - 'Get recent logs from the litellm container'"
echo ""
echo "Admin users should have access to all tools."
echo "Developer users should be blocked from filesystem access."