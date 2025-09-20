#!/usr/bin/env python3
"""
Script to enable MCP functions in LiteLLM
This will allow GPT-5 and other models to actually call MCP services
"""

import yaml
import json
import os
import shutil
from datetime import datetime

# Backup current config
config_path = "/home/administrator/projects/litellm/config.yaml"
backup_path = f"/home/administrator/projects/litellm/config.yaml.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}"

print("Enabling MCP Functions in LiteLLM...")
print(f"Backing up current config to {backup_path}")
shutil.copy(config_path, backup_path)

# Load current config
with open(config_path, 'r') as f:
    config = yaml.safe_load(f)

# Define MCP functions that will be available to all models
mcp_functions = [
    {
        "type": "function",
        "function": {
            "name": "query_postgresql",
            "description": "Execute a PostgreSQL query on the main database",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The SQL query to execute"
                    }
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "fetch_web_content",
            "description": "Fetch content from a URL",
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "The URL to fetch"
                    }
                },
                "required": ["url"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_logs",
            "description": "Search system logs for errors or patterns",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The search query or pattern"
                    },
                    "hours": {
                        "type": "integer",
                        "description": "Number of hours to look back",
                        "default": 1
                    }
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "list_workflows",
            "description": "List all n8n automation workflows",
            "parameters": {
                "type": "object",
                "properties": {}
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "query_timescaledb",
            "description": "Query the TimescaleDB time-series database",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The SQL query for time-series data"
                    }
                },
                "required": ["query"]
            }
        }
    }
]

# Add a new model configuration with MCP functions enabled
mcp_enabled_models = [
    {
        "model_name": "gpt-5-mcp",
        "litellm_params": {
            "model": "gpt-5",
            "api_key": "os.environ/OPENAI_API_KEY",
            "tools": mcp_functions,
            "tool_choice": "auto"
        }
    },
    {
        "model_name": "gpt-4o-mcp",
        "litellm_params": {
            "model": "gpt-4o",
            "api_key": "os.environ/OPENAI_API_KEY",
            "tools": mcp_functions,
            "tool_choice": "auto"
        }
    },
    {
        "model_name": "claude-mcp",
        "litellm_params": {
            "model": "anthropic/claude-opus-4-1",
            "api_key": "os.environ/ANTHROPIC_API_KEY",
            "tools": mcp_functions,
            "tool_choice": "auto"
        }
    }
]

# Add MCP-enabled models to the config
if 'model_list' not in config:
    config['model_list'] = []

# Remove any existing MCP models to avoid duplicates
config['model_list'] = [m for m in config['model_list'] if '-mcp' not in m.get('model_name', '')]

# Add the new MCP-enabled models
config['model_list'].extend(mcp_enabled_models)

# Add function routing configuration
if 'litellm_settings' not in config:
    config['litellm_settings'] = {}

config['litellm_settings']['enable_function_calling'] = True

# Add custom callback for MCP function execution
config['litellm_settings']['function_callback'] = {
    "module": "mcp_function_handler",
    "endpoint": "http://mcp-litellm-adapter:3333/v1/functions"
}

# Save the updated config
with open(config_path, 'w') as f:
    yaml.dump(config, f, default_flow_style=False, sort_keys=False)

print("✅ MCP functions have been added to LiteLLM config")
print("\nNew MCP-enabled models available:")
print("  - gpt-5-mcp (GPT-5 with MCP functions)")
print("  - gpt-4o-mcp (GPT-4o with MCP functions)")
print("  - claude-mcp (Claude Opus 4.1 with MCP functions)")
print("\nAvailable functions:")
for func in mcp_functions:
    print(f"  - {func['function']['name']}: {func['function']['description']}")

print("\n⚠️  To apply changes, restart LiteLLM:")
print("  docker restart litellm")
print("\nThen in Open WebUI, select one of the '-mcp' models to use MCP functions!"