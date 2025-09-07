#!/usr/bin/env python3
"""
MCP Router for LiteLLM
Custom router that intercepts function calls and executes them via MCP
"""

import os
import json
import asyncio
import aiohttp
from typing import Dict, Any, List, Optional
from litellm import completion
import logging

logger = logging.getLogger(__name__)

class MCPRouter:
    """Router that handles MCP tool execution"""
    
    def __init__(self):
        self.mcp_base_url = "http://mcp-proxy-sse:8080"
        self.admin_keys = os.environ.get('MCP_ADMIN_KEYS', 'sk-pFgey4HPR9qDvyT-N_7yVQ').split(',')
        self.function_mappings = self.load_function_mappings()
        
    def load_function_mappings(self) -> Dict:
        """Load MCP function mappings"""
        return {
            # Filesystem functions (admin only)
            "list_directory": {
                "server": "filesystem",
                "tool": "list",
                "admin_only": True
            },
            "read_file": {
                "server": "filesystem", 
                "tool": "read",
                "admin_only": True
            },
            # PostgreSQL functions
            "list_databases": {
                "server": "postgres",
                "tool": "list_schemas",
                "admin_only": False
            },
            "execute_sql": {
                "server": "postgres",
                "tool": "execute_sql",
                "admin_only": False
            },
            # Fetch functions
            "fetch_url": {
                "server": "fetch",
                "tool": "fetch",
                "admin_only": False
            },
            # Monitoring functions
            "get_container_logs": {
                "server": "monitoring",
                "tool": "get_container_logs", 
                "admin_only": False
            }
        }
    
    def check_permission(self, api_key: str, function_name: str) -> bool:
        """Check if API key has permission to use function"""
        mapping = self.function_mappings.get(function_name)
        if not mapping:
            return False
            
        if mapping.get('admin_only', False):
            return api_key in self.admin_keys
            
        return True
    
    async def call_mcp_tool_direct(self, server: str, tool: str, params: Dict) -> Dict:
        """Call MCP tool directly via HTTP (simpler approach)"""
        # For now, return mock data to test the flow
        # In production, this would actually call the MCP proxy
        
        if server == "filesystem" and tool == "list":
            return {
                "success": True,
                "files": ["project1", "project2", "project3", "README.md"]
            }
        elif server == "postgres" and tool == "list_schemas":
            return {
                "success": True,
                "databases": ["postgres", "litellm_db", "keycloak", "n8n"]
            }
        elif server == "monitoring" and tool == "get_container_logs":
            return {
                "success": True,
                "logs": [
                    "2025-09-07 20:00:00 Container started",
                    "2025-09-07 20:00:01 Health check passed",
                    "2025-09-07 20:00:02 Ready to serve requests"
                ]
            }
        else:
            return {"success": False, "error": f"Unknown tool: {server}.{tool}"}
    
    async def handle_completion_with_tools(self, request_data: Dict, api_key: str) -> Dict:
        """Handle completion request with tool execution"""
        
        # Step 1: Get initial response from model
        response = await completion(**request_data)
        
        # Step 2: Check if model wants to use tools
        if hasattr(response, 'choices') and len(response.choices) > 0:
            message = response.choices[0].message
            
            if hasattr(message, 'tool_calls') and message.tool_calls:
                logger.info(f"Model requested {len(message.tool_calls)} tool calls")
                
                # Step 3: Execute tools
                tool_results = []
                for tool_call in message.tool_calls:
                    function_name = tool_call.function.name
                    arguments = json.loads(tool_call.function.arguments)
                    
                    # Check permission
                    if not self.check_permission(api_key, function_name):
                        result = {"error": f"Permission denied for {function_name}"}
                    else:
                        # Execute MCP tool
                        mapping = self.function_mappings.get(function_name)
                        if mapping:
                            result = await self.call_mcp_tool_direct(
                                mapping['server'],
                                mapping['tool'],
                                arguments
                            )
                        else:
                            result = {"error": f"Unknown function: {function_name}"}
                    
                    tool_results.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": json.dumps(result)
                    })
                
                # Step 4: Send tool results back to model for final response
                messages = request_data['messages'].copy()
                messages.append(message.dict())  # Add assistant's tool call message
                messages.extend(tool_results)  # Add tool results
                
                # Get final response from model
                request_data['messages'] = messages
                final_response = await completion(**request_data)
                
                return final_response
        
        return response

# Create global router instance
mcp_router = MCPRouter()

async def handle_chat_completion(request_data: Dict, api_key: str) -> Dict:
    """Main entry point for chat completions with MCP tools"""
    return await mcp_router.handle_completion_with_tools(request_data, api_key)