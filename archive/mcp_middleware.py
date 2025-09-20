#!/usr/bin/env python3
"""
MCP Middleware for LiteLLM
Handles function calling by routing to MCP servers via SSE proxy
"""

import os
import json
import yaml
import asyncio
import aiohttp
from typing import Dict, Any, Optional, List
from datetime import datetime

class MCPMiddleware:
    def __init__(self, config_path: str = "/app/mcp-functions.yaml"):
        """Initialize MCP middleware with function definitions"""
        self.config_path = config_path
        self.functions = {}
        self.mcp_base_url = "http://mcp-proxy-sse:8080"
        self.load_functions()
        
    def load_functions(self):
        """Load function definitions from YAML config"""
        try:
            with open(self.config_path, 'r') as f:
                config = yaml.safe_load(f)
                for func in config.get('functions', []):
                    self.functions[func['name']] = func
            print(f"Loaded {len(self.functions)} MCP function definitions")
        except Exception as e:
            print(f"Error loading MCP functions: {e}")
            
    def get_openai_functions(self) -> List[Dict]:
        """Get function definitions in OpenAI format"""
        openai_funcs = []
        for name, func in self.functions.items():
            openai_func = {
                "type": "function",
                "function": {
                    "name": name,
                    "description": func['description'],
                    "parameters": func['parameters']
                }
            }
            openai_funcs.append(openai_func)
        return openai_funcs
    
    def check_admin_permission(self, api_key: str, function_name: str) -> bool:
        """Check if API key has permission to use this function"""
        func = self.functions.get(function_name)
        if not func:
            return False
            
        # If function requires admin, check API key
        if func.get('admin_only', False):
            # Admin key pattern (customize based on your keys)
            admin_keys = os.environ.get('ADMIN_API_KEYS', 'sk-pFgey4HPR9qDvyT-N_7yVQ').split(',')
            return api_key in admin_keys
            
        return True
    
    async def call_mcp_tool(self, server: str, tool: str, params: Dict) -> Dict:
        """Call an MCP tool via the SSE proxy"""
        url = f"{self.mcp_base_url}/servers/{server}/tools/{tool}/run"
        
        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(url, json={"arguments": params}) as response:
                    if response.status == 200:
                        result = await response.json()
                        return {"success": True, "result": result}
                    else:
                        error = await response.text()
                        return {"success": False, "error": f"MCP call failed: {error}"}
            except Exception as e:
                return {"success": False, "error": f"MCP connection error: {str(e)}"}
    
    async def execute_function(self, function_name: str, arguments: Dict, api_key: str) -> Dict:
        """Execute an MCP function call"""
        # Check if function exists
        if function_name not in self.functions:
            return {
                "error": f"Function '{function_name}' not found",
                "available_functions": list(self.functions.keys())
            }
        
        # Check permissions
        if not self.check_admin_permission(api_key, function_name):
            return {
                "error": f"Permission denied: Function '{function_name}' requires admin access"
            }
        
        # Get function config
        func = self.functions[function_name]
        mcp_server = func['mcp_server']
        mcp_tool = func['mcp_tool']
        
        # Call MCP tool
        result = await self.call_mcp_tool(mcp_server, mcp_tool, arguments)
        
        return result
    
    def inject_functions_into_request(self, request_data: Dict, api_key: str) -> Dict:
        """Inject available MCP functions into the request based on permissions"""
        # Get functions available to this API key
        available_functions = []
        for name, func in self.functions.items():
            if self.check_admin_permission(api_key, name):
                available_functions.append({
                    "type": "function",
                    "function": {
                        "name": name,
                        "description": func['description'],
                        "parameters": func['parameters']
                    }
                })
        
        # Add functions to request if not already present
        if available_functions and 'tools' not in request_data:
            request_data['tools'] = available_functions
            request_data['tool_choice'] = 'auto'
        
        return request_data
    
    async def handle_tool_calls(self, tool_calls: List[Dict], api_key: str) -> List[Dict]:
        """Handle tool calls from the model response"""
        results = []
        for call in tool_calls:
            function_name = call['function']['name']
            arguments = json.loads(call['function']['arguments'])
            
            result = await self.execute_function(function_name, arguments, api_key)
            
            results.append({
                "tool_call_id": call['id'],
                "output": json.dumps(result)
            })
        
        return results

# Example usage for testing
async def test_middleware():
    """Test the MCP middleware"""
    middleware = MCPMiddleware()
    
    # Test getting OpenAI functions
    functions = middleware.get_openai_functions()
    print(f"Available functions: {[f['function']['name'] for f in functions]}")
    
    # Test executing a function (as admin)
    admin_key = "sk-pFgey4HPR9qDvyT-N_7yVQ"
    result = await middleware.execute_function(
        "list_databases",
        {},
        admin_key
    )
    print(f"Database list result: {result}")
    
    # Test permission check (as developer)
    dev_key = "sk-nzq2BIYVoVUpz5csqr69xA"
    result = await middleware.execute_function(
        "list_directory",
        {"path": "/home"},
        dev_key
    )
    print(f"Directory list result (dev): {result}")

if __name__ == "__main__":
    asyncio.run(test_middleware())