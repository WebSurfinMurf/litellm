#!/usr/bin/env python3
"""
MCP Function Handler for LiteLLM
Routes function calls to MCP services via the SSE proxy
"""

import requests
import json
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

MCP_ADAPTER_URL = "http://mcp-litellm-adapter:3333"
MCP_PROXY_URL = "http://mcp-proxy-sse:8080"

# Map function names to MCP services
FUNCTION_MAP = {
    "query_postgresql": {
        "service": "postgres",
        "tool": "query",
        "param_map": {"query": "query"}
    },
    "fetch_web_content": {
        "service": "fetch",
        "tool": "fetch",
        "param_map": {"url": "url"}
    },
    "search_logs": {
        "service": "monitoring",
        "tool": "search_logs",
        "param_map": {"query": "query", "hours": "hours"}
    },
    "list_workflows": {
        "service": "n8n",
        "tool": "list_workflows",
        "param_map": {}
    },
    "query_timescaledb": {
        "service": "timescaledb",
        "tool": "query",
        "param_map": {"query": "query"}
    }
}

def execute_mcp_function(function_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
    """
    Execute an MCP function through the adapter
    """
    try:
        if function_name not in FUNCTION_MAP:
            return {
                "error": f"Unknown function: {function_name}",
                "success": False
            }
        
        func_config = FUNCTION_MAP[function_name]
        
        # Map arguments
        mcp_args = {}
        for param, mcp_param in func_config["param_map"].items():
            if param in arguments:
                mcp_args[mcp_param] = arguments[param]
        
        # Call MCP adapter
        mcp_function_name = f"{func_config['service']}_{func_config['tool']}"
        
        response = requests.post(
            f"{MCP_ADAPTER_URL}/v1/functions/{mcp_function_name}/execute",
            json={"arguments": mcp_args},
            timeout=30
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            return {
                "error": f"MCP call failed: {response.status_code}",
                "details": response.text,
                "success": False
            }
            
    except Exception as e:
        logger.error(f"Error executing MCP function {function_name}: {e}")
        return {
            "error": str(e),
            "success": False
        }

def handle_function_call(data: Dict[str, Any]) -> Any:
    """
    LiteLLM callback handler for function calls
    """
    function_name = data.get("function_name")
    arguments = data.get("arguments", {})
    
    if function_name and function_name in FUNCTION_MAP:
        result = execute_mcp_function(function_name, arguments)
        return json.dumps(result)
    
    return None

# For direct testing
if __name__ == "__main__":
    # Test query_postgresql
    result = execute_mcp_function(
        "query_postgresql",
        {"query": "SELECT datname FROM pg_database;"}
    )
    print("PostgreSQL query result:", result)
    
    # Test fetch_web_content
    result = execute_mcp_function(
        "fetch_web_content",
        {"url": "https://httpbin.org/json"}
    )
    print("Fetch result:", result)