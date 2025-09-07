#!/usr/bin/env python3
"""
Test MCP tools through LiteLLM API
This demonstrates how to call MCP functions via LiteLLM
"""

import requests
import json

# Configuration
LITELLM_URL = "http://localhost:4000"  # Using local since HTTPS has issues
ADMIN_KEY = "sk-pFgey4HPR9qDvyT-N_7yVQ"  # Has filesystem access
DEV_KEY = "sk-nzq2BIYVoVUpz5csqr69xA"    # No filesystem access

def test_chat_with_tools(api_key, test_name, prompt):
    """Test chat completion with tool calling"""
    print(f"\n{'='*60}")
    print(f"Test: {test_name}")
    print(f"Using: {'Admin' if 'pFgey' in api_key else 'Developer'} key")
    print(f"Prompt: {prompt}")
    print('-'*60)
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    # Define available MCP tools (these should match what's configured)
    tools = [
        {
            "type": "function",
            "function": {
                "name": "mcp_filesystem_list",
                "description": "List files in a directory",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "path": {
                            "type": "string",
                            "description": "Directory path to list"
                        }
                    },
                    "required": ["path"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "mcp_postgres_query",
                "description": "Execute a PostgreSQL query",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "SQL query to execute"
                        }
                    },
                    "required": ["query"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "mcp_monitoring_logs",
                "description": "Get recent logs from monitoring system",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "service": {
                            "type": "string",
                            "description": "Service name to get logs for"
                        },
                        "lines": {
                            "type": "integer",
                            "description": "Number of log lines to retrieve",
                            "default": 10
                        }
                    },
                    "required": ["service"]
                }
            }
        }
    ]
    
    # Make the request with tools
    response = requests.post(
        f"{LITELLM_URL}/v1/chat/completions",
        headers=headers,
        json={
            "model": "gpt-4o-mini",
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "tools": tools,
            "tool_choice": "auto",
            "max_tokens": 200
        }
    )
    
    if response.status_code == 200:
        result = response.json()
        
        # Check if model wants to use tools
        if result.get("choices", [{}])[0].get("message", {}).get("tool_calls"):
            tool_calls = result["choices"][0]["message"]["tool_calls"]
            print("🔧 Model wants to use tools:")
            for call in tool_calls:
                print(f"  - Function: {call['function']['name']}")
                print(f"    Arguments: {call['function']['arguments']}")
        else:
            # Regular response
            content = result.get("choices", [{}])[0].get("message", {}).get("content", "")
            print(f"Response: {content}")
    else:
        print(f"❌ Error {response.status_code}: {response.text[:200]}")

def main():
    print("=== LiteLLM MCP Tools Testing ===")
    print("\nNote: MCP tools are typically exposed as function calls in LiteLLM")
    print("The model will decide whether to use tools based on the prompt\n")
    
    # Test 1: Admin trying to access filesystem
    test_chat_with_tools(
        ADMIN_KEY,
        "Admin accessing filesystem",
        "List the files in /home/administrator/projects directory"
    )
    
    # Test 2: Developer trying to access filesystem (should fail or not call tool)
    test_chat_with_tools(
        DEV_KEY,
        "Developer accessing filesystem",
        "List the files in /home/administrator/projects directory"
    )
    
    # Test 3: Developer accessing allowed service (postgres)
    test_chat_with_tools(
        DEV_KEY,
        "Developer accessing PostgreSQL",
        "Show me the list of databases in PostgreSQL"
    )
    
    # Test 4: Admin accessing monitoring
    test_chat_with_tools(
        ADMIN_KEY,
        "Admin accessing monitoring logs",
        "Show me recent logs from the litellm service"
    )

if __name__ == "__main__":
    main()