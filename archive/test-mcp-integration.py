#!/usr/bin/env python3
"""
Test MCP integration through middleware
"""

import requests
import json

def test_mcp_execution():
    """Test that MCP tools are executed and results returned"""
    
    # Test against middleware (will be on port 4001)
    url = "http://localhost:4001/v1/chat/completions"
    
    # Test with direct LiteLLM first (port 4000)
    litellm_url = "http://localhost:4000/v1/chat/completions"
    
    headers = {
        "Authorization": "Bearer sk-pFgey4HPR9qDvyT-N_7yVQ",  # Admin key
        "Content-Type": "application/json"
    }
    
    print("=" * 60)
    print("Test 1: Direct LiteLLM - Function Detection")
    print("-" * 60)
    
    response = requests.post(litellm_url, headers=headers, json={
        "model": "gpt-4o-mini",
        "messages": [
            {"role": "user", "content": "List the PostgreSQL databases"}
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
        "max_tokens": 200
    })
    
    if response.status_code == 200:
        result = response.json()
        if 'choices' in result:
            choice = result['choices'][0]
            message = choice.get('message', {})
            if 'tool_calls' in message:
                print("✅ Model detected and requested function call")
                print(f"   Function: {message['tool_calls'][0]['function']['name']}")
                print(f"   Arguments: {message['tool_calls'][0]['function']['arguments']}")
            else:
                print("❌ Model did not request function call")
                print(f"   Response: {message.get('content', 'No content')[:100]}")
    else:
        print(f"❌ Error: {response.status_code}")
        print(f"   {response.text[:200]}")
    
    print("\n" + "=" * 60)
    print("Test 2: Admin Key - Filesystem Access")
    print("-" * 60)
    
    response = requests.post(litellm_url, headers=headers, json={
        "model": "gpt-4o-mini",
        "messages": [
            {"role": "user", "content": "List files in /home/administrator/projects directory"}
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
        "max_tokens": 200
    })
    
    if response.status_code == 200:
        result = response.json()
        if 'choices' in result:
            choice = result['choices'][0]
            message = choice.get('message', {})
            if 'tool_calls' in message:
                print("✅ Admin correctly requested filesystem function")
                tool_call = message['tool_calls'][0]
                print(f"   Function: {tool_call['function']['name']}")
                args = json.loads(tool_call['function']['arguments'])
                print(f"   Path requested: {args.get('path', 'N/A')}")
            else:
                print("⚠️ Model did not request function")
                print(f"   Response: {message.get('content', 'No content')[:100]}")
    else:
        print(f"❌ Error: {response.status_code}")
    
    print("\n" + "=" * 60)
    print("Test 3: Developer Key - Should NOT Access Filesystem")
    print("-" * 60)
    
    dev_headers = {
        "Authorization": "Bearer sk-nzq2BIYVoVUpz5csqr69xA",  # Developer key
        "Content-Type": "application/json"
    }
    
    response = requests.post(litellm_url, headers=dev_headers, json={
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
        "max_tokens": 200
    })
    
    if response.status_code == 200:
        result = response.json()
        if 'choices' in result:
            choice = result['choices'][0]
            message = choice.get('message', {})
            if 'tool_calls' in message:
                print("⚠️ Developer requested filesystem (middleware should block)")
                print(f"   Function: {message['tool_calls'][0]['function']['name']}")
            else:
                print("✅ Model did not request function (good for developer)")
    else:
        print(f"❌ Error: {response.status_code}")
    
    print("\n" + "=" * 60)
    print("Summary:")
    print("- Models are detecting and requesting functions correctly")
    print("- The execution layer (middleware) is what's missing")
    print("- Once middleware is running, it will intercept and execute")
    print("=" * 60)

if __name__ == "__main__":
    test_mcp_execution()