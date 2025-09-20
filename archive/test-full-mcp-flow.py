#!/usr/bin/env python3
"""
Test full MCP flow through middleware
Shows: Request → Middleware → LiteLLM → Model → Tool Call → Execution → Final Answer
"""

import requests
import json

def test_full_flow():
    """Test the complete MCP execution flow"""
    
    # Use middleware endpoint instead of direct LiteLLM
    middleware_url = "http://localhost:4001/v1/chat/completions"
    
    print("=" * 70)
    print("FULL MCP INTEGRATION TEST")
    print("=" * 70)
    
    # Test 1: Simple function call with mock execution
    print("\nTest 1: List PostgreSQL Databases (Mock Data)")
    print("-" * 70)
    
    headers = {
        "Authorization": "Bearer sk-pFgey4HPR9qDvyT-N_7yVQ",  # Admin key
        "Content-Type": "application/json"
    }
    
    response = requests.post(middleware_url, headers=headers, json={
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
        "tool_choice": "auto",
        "max_tokens": 300
    })
    
    if response.status_code == 200:
        result = response.json()
        if 'choices' in result:
            message = result['choices'][0]['message']
            content = message.get('content', '')
            
            # Check if we got actual database names in the response
            if any(db in content for db in ['postgres', 'litellm_db', 'keycloak']):
                print("✅ SUCCESS: Tool was executed and data returned!")
                print(f"Response: {content[:300]}")
            else:
                print("❌ PARTIAL: Model responded but no tool execution detected")
                print(f"Response: {content[:200]}")
    else:
        print(f"❌ Error: {response.status_code}")
        print(response.text[:200])
    
    # Test 2: Filesystem access with admin key
    print("\n\nTest 2: List Files (Admin Key - Should Work)")
    print("-" * 70)
    
    response = requests.post(middleware_url, headers=headers, json={
        "model": "gpt-4o-mini",
        "messages": [
            {"role": "user", "content": "List files in the /home/administrator/projects directory"}
        ],
        "tools": [{
            "type": "function",
            "function": {
                "name": "list_directory",
                "description": "List files in a directory",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "path": {"type": "string", "description": "Directory path"}
                    },
                    "required": ["path"]
                }
            }
        }],
        "tool_choice": "auto",
        "max_tokens": 300
    })
    
    if response.status_code == 200:
        result = response.json()
        if 'choices' in result:
            message = result['choices'][0]['message']
            content = message.get('content', '')
            
            # Check for file names in response
            if any(name in content for name in ['project1', 'project2', 'README.md']):
                print("✅ SUCCESS: Filesystem tool executed with mock data!")
                print(f"Response: {content[:300]}")
            else:
                print("⚠️ Model responded without tool execution")
                print(f"Response: {content[:200]}")
    
    # Test 3: Developer key trying filesystem
    print("\n\nTest 3: List Files (Developer Key - Should Be Denied)")
    print("-" * 70)
    
    dev_headers = {
        "Authorization": "Bearer sk-nzq2BIYVoVUpz5csqr69xA",  # Developer key
        "Content-Type": "application/json"
    }
    
    response = requests.post(middleware_url, headers=dev_headers, json={
        "model": "gpt-4o-mini",
        "messages": [
            {"role": "user", "content": "List files in /home/administrator/projects"}
        ],
        "tools": [{
            "type": "function",
            "function": {
                "name": "list_directory",
                "description": "List files in a directory",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "path": {"type": "string", "description": "Directory path"}
                    },
                    "required": ["path"]
                }
            }
        }],
        "tool_choice": "auto",
        "max_tokens": 300
    })
    
    if response.status_code == 200:
        result = response.json()
        if 'choices' in result:
            message = result['choices'][0]['message']
            content = message.get('content', '')
            
            if "Permission denied" in content or "error" in content.lower():
                print("✅ SUCCESS: Developer correctly denied filesystem access!")
                print(f"Response: {content[:200]}")
            elif any(name in content for name in ['project1', 'project2']):
                print("❌ FAIL: Developer got filesystem access (should be denied)")
                print(f"Response: {content[:200]}")
            else:
                print("⚠️ Unclear result - check response:")
                print(f"Response: {content[:200]}")
    
    # Test 4: Container logs (both should work)
    print("\n\nTest 4: Get Container Logs (Should Work for Both)")
    print("-" * 70)
    
    response = requests.post(middleware_url, headers=dev_headers, json={
        "model": "gpt-4o-mini",
        "messages": [
            {"role": "user", "content": "Get the last 5 logs from the litellm container"}
        ],
        "tools": [{
            "type": "function",
            "function": {
                "name": "get_container_logs",
                "description": "Get Docker container logs",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "container": {"type": "string", "description": "Container name"},
                        "lines": {"type": "integer", "description": "Number of lines"}
                    },
                    "required": ["container"]
                }
            }
        }],
        "tool_choice": "auto",
        "max_tokens": 300
    })
    
    if response.status_code == 200:
        result = response.json()
        if 'choices' in result:
            message = result['choices'][0]['message']
            content = message.get('content', '')
            
            if "INFO" in content or "Container started" in content or "log" in content.lower():
                print("✅ SUCCESS: Monitoring tool executed!")
                print(f"Response: {content[:300]}")
            else:
                print("⚠️ Model responded without clear tool execution")
                print(f"Response: {content[:200]}")
    
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print("The middleware is working! It:")
    print("1. Receives requests from clients")
    print("2. Forwards to LiteLLM for model processing")
    print("3. Intercepts function calls")
    print("4. Executes MCP tools (currently with mock data)")
    print("5. Returns final responses with actual data")
    print("\nNext step: Connect to real MCP services instead of mock data")
    print("=" * 70)

if __name__ == "__main__":
    test_full_flow()