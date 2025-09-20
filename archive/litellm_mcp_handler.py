#!/usr/bin/env python3
"""
LiteLLM Custom Callback Handler for MCP Integration
This handler intercepts function calls and routes them to MCP servers
"""

import os
import json
import requests
import logging
from typing import Dict, Any, List, Optional
from litellm.integrations.custom_logger import CustomLogger

logger = logging.getLogger(__name__)

class MCPHandler(CustomLogger):
    """Custom handler that processes MCP function calls"""
    
    def __init__(self):
        super().__init__()
        self.mcp_base_url = "http://mcp-proxy-sse:8080"
        self.admin_keys = os.environ.get('MCP_ADMIN_KEYS', 'sk-pFgey4HPR9qDvyT-N_7yVQ').split(',')
        self.function_mappings = self.load_function_mappings()
        
    def load_function_mappings(self) -> Dict:
        """Load MCP function mappings"""
        return {
            # Filesystem functions (admin only)
            "list_directory": {
                "server": "filesystem",
                "tool": "list_allowed_directories",
                "admin_only": True
            },
            "read_file": {
                "server": "filesystem", 
                "tool": "read_file",
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
            },
            "search_logs": {
                "server": "monitoring",
                "tool": "search_logs",
                "admin_only": False
            },
            # N8n functions
            "list_workflows": {
                "server": "n8n",
                "tool": "list_workflows",
                "admin_only": False
            },
            # Playwright functions
            "check_browser_health": {
                "server": "playwright",
                "tool": "check_service_health",
                "admin_only": False
            },
            # TimescaleDB functions
            "show_hypertables": {
                "server": "timescaledb",
                "tool": "tsdb_show_hypertables",
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
    
    def call_mcp_tool(self, server: str, tool: str, params: Dict) -> Dict:
        """Execute MCP tool via proxy"""
        try:
            # First, get tool info
            info_url = f"{self.mcp_base_url}/servers/{server}/tools"
            response = requests.get(info_url, timeout=5)
            
            if response.status_code != 200:
                return {"error": f"Failed to get tool info: {response.text}"}
            
            # Now execute the tool
            exec_url = f"{self.mcp_base_url}/servers/{server}/tools/{tool}/run"
            response = requests.post(
                exec_url,
                json={"arguments": params},
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return {"error": f"MCP execution failed: {response.text}"}
                
        except requests.exceptions.RequestException as e:
            return {"error": f"MCP connection error: {str(e)}"}
        except Exception as e:
            return {"error": f"Unexpected error: {str(e)}"}
    
    def log_pre_api_call(self, model, messages, kwargs):
        """Called before API call - inject MCP functions if needed"""
        api_key = kwargs.get('api_key', '')
        
        # Check if tools are requested
        if 'tools' not in kwargs or not kwargs['tools']:
            # Auto-inject available MCP tools based on permissions
            available_tools = []
            for func_name, mapping in self.function_mappings.items():
                if self.check_permission(api_key, func_name):
                    # Add tool definition
                    tool_def = self.get_tool_definition(func_name)
                    if tool_def:
                        available_tools.append(tool_def)
            
            if available_tools:
                kwargs['tools'] = available_tools
                kwargs['tool_choice'] = 'auto'
                logger.info(f"Injected {len(available_tools)} MCP tools")
        
        return model, messages, kwargs
    
    def log_post_api_call(self, kwargs, response_obj, start_time, end_time):
        """Called after API call - process any tool calls"""
        if not response_obj or 'choices' not in response_obj:
            return
            
        api_key = kwargs.get('api_key', '')
        
        for choice in response_obj.get('choices', []):
            message = choice.get('message', {})
            tool_calls = message.get('tool_calls', [])
            
            if tool_calls:
                logger.info(f"Processing {len(tool_calls)} tool calls")
                tool_results = []
                
                for call in tool_calls:
                    function_name = call['function']['name']
                    arguments = json.loads(call['function']['arguments'])
                    
                    # Check permission
                    if not self.check_permission(api_key, function_name):
                        result = {"error": f"Permission denied for {function_name}"}
                    else:
                        # Execute MCP tool
                        mapping = self.function_mappings.get(function_name)
                        if mapping:
                            result = self.call_mcp_tool(
                                mapping['server'],
                                mapping['tool'],
                                arguments
                            )
                        else:
                            result = {"error": f"Unknown function: {function_name}"}
                    
                    tool_results.append({
                        "tool_call_id": call['id'],
                        "result": result
                    })
                
                # Store results for next message (would need additional handling)
                logger.info(f"Tool results: {tool_results}")
    
    def get_tool_definition(self, func_name: str) -> Optional[Dict]:
        """Get OpenAI-format tool definition"""
        definitions = {
            "list_directory": {
                "type": "function",
                "function": {
                    "name": "list_directory",
                    "description": "List files and directories in a path",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "path": {"type": "string", "description": "Directory path"}
                        },
                        "required": ["path"]
                    }
                }
            },
            "list_databases": {
                "type": "function",
                "function": {
                    "name": "list_databases",
                    "description": "List all PostgreSQL databases",
                    "parameters": {
                        "type": "object",
                        "properties": {}
                    }
                }
            },
            "execute_sql": {
                "type": "function",
                "function": {
                    "name": "execute_sql",
                    "description": "Execute a PostgreSQL query",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {"type": "string", "description": "SQL query"}
                        },
                        "required": ["query"]
                    }
                }
            },
            "fetch_url": {
                "type": "function",
                "function": {
                    "name": "fetch_url",
                    "description": "Fetch webpage content",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "url": {"type": "string", "description": "URL to fetch"}
                        },
                        "required": ["url"]
                    }
                }
            },
            "get_container_logs": {
                "type": "function",
                "function": {
                    "name": "get_container_logs",
                    "description": "Get Docker container logs",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "container": {"type": "string", "description": "Container name"},
                            "lines": {"type": "integer", "description": "Number of lines", "default": 50}
                        },
                        "required": ["container"]
                    }
                }
            },
            "search_logs": {
                "type": "function",
                "function": {
                    "name": "search_logs",
                    "description": "Search logs for patterns",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {"type": "string", "description": "Search query"},
                            "service": {"type": "string", "description": "Service name (optional)"}
                        },
                        "required": ["query"]
                    }
                }
            },
            "list_workflows": {
                "type": "function",
                "function": {
                    "name": "list_workflows",
                    "description": "List n8n workflows",
                    "parameters": {
                        "type": "object",
                        "properties": {}
                    }
                }
            },
            "check_browser_health": {
                "type": "function",
                "function": {
                    "name": "check_browser_health",
                    "description": "Check browser automation health",
                    "parameters": {
                        "type": "object",
                        "properties": {}
                    }
                }
            },
            "show_hypertables": {
                "type": "function",
                "function": {
                    "name": "show_hypertables",
                    "description": "List TimescaleDB hypertables",
                    "parameters": {
                        "type": "object",
                        "properties": {}
                    }
                }
            }
        }
        return definitions.get(func_name)

# Export the handler
mcp_handler = MCPHandler()