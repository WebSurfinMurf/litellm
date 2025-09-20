#!/usr/bin/env python3
"""
MCP Middleware Service
Sits between Open WebUI and LiteLLM to execute MCP tools
"""

from flask import Flask, request, jsonify
import requests
import json
import logging
import os

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
LITELLM_URL = "http://localhost:4000"
MCP_ADAPTER_URL = "http://localhost:3333"
ADMIN_KEYS = os.environ.get('MCP_ADMIN_KEYS', 'sk-pFgey4HPR9qDvyT-N_7yVQ').split(',')

# Function mappings (simplified)
FUNCTION_MAPPINGS = {
    "list_directory": {
        "mcp_name": "filesystem_list",
        "admin_only": True
    },
    "list_databases": {
        "mcp_name": "postgres_list_schemas",
        "admin_only": False
    },
    "get_container_logs": {
        "mcp_name": "monitoring_get_container_logs",
        "admin_only": False
    }
}

def check_permission(api_key, function_name):
    """Check if API key has permission for function"""
    func = FUNCTION_MAPPINGS.get(function_name)
    if not func:
        return False
    if func.get('admin_only', False):
        # Extract actual key from Bearer token
        if api_key.startswith('Bearer '):
            api_key = api_key[7:]
        return api_key in ADMIN_KEYS
    return True

def execute_mcp_function(function_name, arguments):
    """Execute MCP function (mock for now)"""
    # In production, this would call the MCP adapter or proxy
    logger.info(f"Executing MCP function: {function_name} with args: {arguments}")
    
    # Return mock data for testing
    if function_name == "list_directory":
        return {
            "files": ["project1", "project2", "README.md", "config.yaml"],
            "directories": ["src", "tests", "docs"]
        }
    elif function_name == "list_databases":
        return {
            "databases": ["postgres", "litellm_db", "keycloak", "n8n", "grafana"]
        }
    elif function_name == "get_container_logs":
        return {
            "logs": [
                "2025-09-07 20:30:00 INFO Container started",
                "2025-09-07 20:30:01 INFO Health check passed",
                "2025-09-07 20:30:02 INFO Ready to serve",
                "2025-09-07 20:30:03 INFO Processing request",
                "2025-09-07 20:30:04 INFO Request completed"
            ]
        }
    else:
        return {"error": f"Unknown function: {function_name}"}

@app.route('/v1/chat/completions', methods=['POST'])
def chat_completions():
    """Proxy chat completions with MCP tool execution"""
    try:
        # Get authorization header
        auth_header = request.headers.get('Authorization', '')
        
        # Forward request to LiteLLM
        headers = {
            'Authorization': auth_header,
            'Content-Type': 'application/json'
        }
        
        # Get request data
        request_data = request.json
        
        # Step 1: Forward to LiteLLM
        response = requests.post(
            f"{LITELLM_URL}/v1/chat/completions",
            headers=headers,
            json=request_data
        )
        
        if response.status_code != 200:
            return jsonify(response.json()), response.status_code
        
        result = response.json()
        
        # Step 2: Check if model requested tool calls
        if 'choices' in result and len(result['choices']) > 0:
            choice = result['choices'][0]
            message = choice.get('message', {})
            tool_calls = message.get('tool_calls', [])
            
            if tool_calls:
                logger.info(f"Model requested {len(tool_calls)} tool calls")
                
                # Step 3: Execute tools
                tool_results = []
                for tool_call in tool_calls:
                    function_name = tool_call['function']['name']
                    arguments = json.loads(tool_call['function']['arguments'])
                    
                    # Check permission
                    if not check_permission(auth_header, function_name):
                        tool_result = {"error": f"Permission denied for {function_name}"}
                    else:
                        # Execute function
                        tool_result = execute_mcp_function(function_name, arguments)
                    
                    tool_results.append({
                        "role": "tool",
                        "tool_call_id": tool_call['id'],
                        "content": json.dumps(tool_result)
                    })
                
                # Step 4: Send back to model with tool results
                messages = request_data.get('messages', []).copy()
                messages.append(message)  # Add assistant's tool call message
                messages.extend(tool_results)  # Add tool results
                
                # Get final response
                final_request = {
                    **request_data,
                    'messages': messages
                }
                
                final_response = requests.post(
                    f"{LITELLM_URL}/v1/chat/completions",
                    headers=headers,
                    json=final_request
                )
                
                if final_response.status_code == 200:
                    return jsonify(final_response.json())
                else:
                    return jsonify(final_response.json()), final_response.status_code
        
        # No tool calls, return original response
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error in middleware: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "service": "mcp-middleware"})

if __name__ == '__main__':
    logger.info("Starting MCP Middleware Service on port 4001")
    logger.info(f"Proxying to LiteLLM at {LITELLM_URL}")
    logger.info(f"Admin keys configured: {len(ADMIN_KEYS)}")
    app.run(host='0.0.0.0', port=4001, debug=False)