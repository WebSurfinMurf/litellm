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
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Configuration
LITELLM_URL = os.environ.get('LITELLM_URL', 'http://localhost:4000')
MCP_PROXY_URL = os.environ.get('MCP_PROXY_URL', 'http://localhost:8585')
ADMIN_KEYS = os.environ.get('MCP_ADMIN_KEYS', 'sk-pFgey4HPR9qDvyT-N_7yVQ').split(',')

# Complete MCP toolset definition
MCP_TOOLS_DEFINITION = [
    {
        "type": "function",
        "function": {
            "name": "list_mcp_tools",
            "description": "List all available MCP (Model Context Protocol) tools and their capabilities. Use this when asked about available tools, functions, or MCP capabilities.",
            "parameters": {"type": "object", "properties": {}}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "list_databases",
            "description": "List all PostgreSQL databases on the server. Use for database discovery and PostgreSQL operations.",
            "parameters": {"type": "object", "properties": {}}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_container_logs",
            "description": "Get Docker container logs for a specific service. Useful for debugging and monitoring Docker containers.",
            "parameters": {
                "type": "object",
                "properties": {
                    "container_name": {"type": "string", "description": "The name of the docker container."},
                    "line_count": {"type": "integer", "description": "Number of recent log lines to retrieve.", "default": 50}
                },
                "required": ["container_name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "list_directory",
            "description": "List files and directories at a given path on the server. Requires admin privileges. Use for filesystem exploration.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "The absolute or relative directory path to list."}
                },
                "required": ["path"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_logs",
            "description": "Search through system logs using Loki/Grafana. Find specific log entries across all containers.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "LogQL query or search term"},
                    "time_range": {"type": "string", "description": "Time range (e.g., '1h', '24h', '7d')", "default": "1h"}
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "execute_sql",
            "description": "Execute SQL queries on PostgreSQL databases. Use for database operations and queries.",
            "parameters": {
                "type": "object",
                "properties": {
                    "database": {"type": "string", "description": "Target database name"},
                    "query": {"type": "string", "description": "SQL query to execute"}
                },
                "required": ["database", "query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_system_metrics",
            "description": "Get system performance metrics from Netdata. Monitor CPU, memory, disk, and network usage.",
            "parameters": {
                "type": "object",
                "properties": {
                    "metric_type": {"type": "string", "description": "Type of metric (cpu, memory, disk, network)", "default": "all"}
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "manage_docker",
            "description": "Manage Docker containers - start, stop, restart, or inspect containers.",
            "parameters": {
                "type": "object",
                "properties": {
                    "action": {"type": "string", "description": "Action to perform (start, stop, restart, inspect, ps)"},
                    "container": {"type": "string", "description": "Container name or ID (optional for ps)"}
                },
                "required": ["action"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "fetch_url",
            "description": "Fetch and analyze content from a URL. Use for web scraping and API calls.",
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {"type": "string", "description": "URL to fetch"},
                    "headers": {"type": "object", "description": "Optional HTTP headers"}
                },
                "required": ["url"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "list_workflows",
            "description": "List all n8n workflows. Use for workflow automation management and discovery.",
            "parameters": {"type": "object", "properties": {}}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "execute_workflow",
            "description": "Execute an n8n workflow by ID or name. Trigger automation workflows.",
            "parameters": {
                "type": "object",
                "properties": {
                    "workflow_id": {"type": "string", "description": "Workflow ID or name to execute"},
                    "data": {"type": "object", "description": "Optional input data for the workflow"}
                },
                "required": ["workflow_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_workflow_executions",
            "description": "Get execution history for n8n workflows. Monitor workflow runs and results.",
            "parameters": {
                "type": "object",
                "properties": {
                    "workflow_id": {"type": "string", "description": "Workflow ID to get executions for (optional)"},
                    "limit": {"type": "integer", "description": "Number of executions to retrieve", "default": 10}
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "query_timeseries",
            "description": "Query TimescaleDB for time-series data. Analyze metrics and historical data.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "SQL query for time-series data"},
                    "time_range": {"type": "string", "description": "Time range (e.g., '1h', '24h', '7d')", "default": "24h"}
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "list_hypertables",
            "description": "List all TimescaleDB hypertables. View time-series table structures.",
            "parameters": {"type": "object", "properties": {}}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_timeseries_stats",
            "description": "Get statistics for TimescaleDB hypertables. Monitor data retention and compression.",
            "parameters": {
                "type": "object",
                "properties": {
                    "table_name": {"type": "string", "description": "Hypertable name (optional for all tables)"}
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "browser_navigate",
            "description": "Navigate to a URL using Playwright browser automation. Interact with web pages programmatically.",
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {"type": "string", "description": "URL to navigate to"},
                    "wait_for": {"type": "string", "description": "Element to wait for (CSS selector)"}
                },
                "required": ["url"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "browser_screenshot",
            "description": "Take a screenshot of a webpage using Playwright. Returns base64-encoded PNG image data. Currently returns placeholder image (mock data).",
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {"type": "string", "description": "URL to screenshot"},
                    "full_page": {"type": "boolean", "description": "Capture full page", "default": True},
                    "selector": {"type": "string", "description": "CSS selector for specific element (optional)"}
                },
                "required": ["url"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "browser_extract",
            "description": "Extract data from a webpage using Playwright. Scrape content from dynamic websites.",
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {"type": "string", "description": "URL to extract from"},
                    "selector": {"type": "string", "description": "CSS selector for elements to extract"},
                    "attribute": {"type": "string", "description": "Attribute to extract (text, href, src, etc.)", "default": "text"}
                },
                "required": ["url", "selector"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "minio_list_objects",
            "description": "List objects in MinIO storage bucket. Browse files stored in S3-compatible object storage.",
            "parameters": {
                "type": "object",
                "properties": {
                    "prefix": {"type": "string", "description": "Path prefix to filter objects (e.g., 'screenshots/', 'uploads/')"},
                    "recursive": {"type": "boolean", "description": "List recursively", "default": False}
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "minio_upload_object",
            "description": "Upload data to MinIO storage. Store files, images, or any data in S3-compatible storage.",
            "parameters": {
                "type": "object",
                "properties": {
                    "object_name": {"type": "string", "description": "Object name/path in bucket (e.g., 'screenshots/google.png')"},
                    "data": {"type": "string", "description": "Base64 encoded data or text content to upload"},
                    "content_type": {"type": "string", "description": "MIME type (e.g., 'image/png', 'text/plain')", "default": "application/octet-stream"}
                },
                "required": ["object_name", "data"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "minio_download_object",
            "description": "Download object from MinIO storage. Retrieve files stored in S3-compatible storage.",
            "parameters": {
                "type": "object",
                "properties": {
                    "object_name": {"type": "string", "description": "Object name/path in bucket"}
                },
                "required": ["object_name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "minio_delete_object",
            "description": "Delete object from MinIO storage. Remove files from S3-compatible storage.",
            "parameters": {
                "type": "object",
                "properties": {
                    "object_name": {"type": "string", "description": "Object name/path to delete"}
                },
                "required": ["object_name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "minio_get_url",
            "description": "Get a public/presigned URL for an object in MinIO. Generate shareable links for stored files.",
            "parameters": {
                "type": "object",
                "properties": {
                    "object_name": {"type": "string", "description": "Object name/path in bucket"},
                    "expiry_hours": {"type": "integer", "description": "URL expiry time in hours", "default": 24}
                },
                "required": ["object_name"]
            }
        }
    }
]

# Function mappings (simplified)
FUNCTION_MAPPINGS = {
    "list_mcp_tools": {
        "mcp_name": "internal_list_tools",
        "admin_only": False
    },
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
    },
    "search_logs": {
        "mcp_name": "monitoring_search_logs",
        "admin_only": False
    },
    "execute_sql": {
        "mcp_name": "postgres_execute_sql",
        "admin_only": True
    },
    "get_system_metrics": {
        "mcp_name": "monitoring_get_metrics",
        "admin_only": False
    },
    "manage_docker": {
        "mcp_name": "docker_manage",
        "admin_only": True
    },
    "fetch_url": {
        "mcp_name": "fetch_get_url",
        "admin_only": False
    },
    "list_workflows": {
        "mcp_name": "n8n_list_workflows",
        "admin_only": False
    },
    "execute_workflow": {
        "mcp_name": "n8n_execute_workflow",
        "admin_only": True
    },
    "get_workflow_executions": {
        "mcp_name": "n8n_get_executions",
        "admin_only": False
    },
    "query_timeseries": {
        "mcp_name": "timescaledb_query",
        "admin_only": False
    },
    "list_hypertables": {
        "mcp_name": "timescaledb_list_hypertables",
        "admin_only": False
    },
    "get_timeseries_stats": {
        "mcp_name": "timescaledb_stats",
        "admin_only": False
    },
    "browser_navigate": {
        "mcp_name": "playwright_navigate",
        "admin_only": False
    },
    "browser_screenshot": {
        "mcp_name": "playwright_screenshot",
        "admin_only": False
    },
    "browser_extract": {
        "mcp_name": "playwright_extract",
        "admin_only": False
    },
    "minio_list_objects": {
        "mcp_name": "minio_list",
        "admin_only": False
    },
    "minio_upload_object": {
        "mcp_name": "minio_upload",
        "admin_only": False
    },
    "minio_download_object": {
        "mcp_name": "minio_download",
        "admin_only": False
    },
    "minio_delete_object": {
        "mcp_name": "minio_delete",
        "admin_only": True
    },
    "minio_get_url": {
        "mcp_name": "minio_presign",
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
    """Execute MCP function (using mock data until MCP proxy is fixed)"""
    logger.info(f"Executing MCP function: {function_name} with args: {arguments}")
    
    # Return mock data for testing (MCP proxy currently not accessible)
    if function_name == "list_mcp_tools":
        tools_info = []
        for tool in MCP_TOOLS_DEFINITION:
            func = tool["function"]
            tool_info = {
                "name": func["name"],
                "description": func["description"],
                "parameters": list(func.get("parameters", {}).get("properties", {}).keys()),
                "required_params": func.get("parameters", {}).get("required", []),
                "admin_only": FUNCTION_MAPPINGS.get(func["name"], {}).get("admin_only", False)
            }
            tools_info.append(tool_info)
        
        return {
            "total_tools": len(tools_info),
            "tools": tools_info,
            "categories": {
                "Database": ["list_databases", "execute_sql"],
                "Monitoring": ["get_container_logs", "search_logs", "get_system_metrics"],
                "System": ["list_directory", "manage_docker"],
                "Network": ["fetch_url"],
                "Automation": ["list_workflows", "execute_workflow", "get_workflow_executions"],
                "TimeSeries": ["query_timeseries", "list_hypertables", "get_timeseries_stats"],
                "Browser": ["browser_navigate", "browser_screenshot", "browser_extract"],
                "Storage": ["minio_list_objects", "minio_upload_object", "minio_download_object", "minio_delete_object", "minio_get_url"],
                "Meta": ["list_mcp_tools"]
            },
            "note": "These are MCP (Model Context Protocol) tools available for system interaction. Admin tools require special permissions."
        }
    elif function_name == "list_directory":
        return {
            "files": ["project1", "project2", "README.md", "config.yaml"],
            "directories": ["src", "tests", "docs"]
        }
    elif function_name == "list_databases":
        return {
            "databases": ["postgres", "litellm_db", "keycloak", "n8n", "grafana"]
        }
    elif function_name == "get_container_logs":
        container = arguments.get('container_name', 'unknown')
        return {
            "container": container,
            "logs": [
                f"2025-09-07 20:30:00 INFO [{container}] Container started",
                f"2025-09-07 20:30:01 INFO [{container}] Health check passed",
                f"2025-09-07 20:30:02 INFO [{container}] Ready to serve",
                f"2025-09-07 20:30:03 INFO [{container}] Processing request",
                f"2025-09-07 20:30:04 INFO [{container}] Request completed"
            ]
        }
    elif function_name == "search_logs":
        query = arguments.get('query', '')
        time_range = arguments.get('time_range', '1h')
        return {
            "query": query,
            "time_range": time_range,
            "matches": [
                {"timestamp": "2025-09-07T20:30:00Z", "container": "litellm", "message": f"Found match for '{query}'"},
                {"timestamp": "2025-09-07T20:31:00Z", "container": "open-webui", "message": f"Log entry matching '{query}'"},
                {"timestamp": "2025-09-07T20:32:00Z", "container": "mcp-middleware", "message": f"Debug: {query} processed"}
            ],
            "total_matches": 3
        }
    elif function_name == "execute_sql":
        database = arguments.get('database', 'postgres')
        query = arguments.get('query', 'SELECT 1')
        return {
            "database": database,
            "query": query,
            "result": [
                {"column1": "value1", "column2": "value2"},
                {"column1": "value3", "column2": "value4"}
            ],
            "rows_affected": 2,
            "execution_time": "0.023s"
        }
    elif function_name == "get_system_metrics":
        metric_type = arguments.get('metric_type', 'all')
        metrics = {
            "cpu": {"usage": "23.5%", "cores": 8, "load_avg": [1.2, 1.5, 1.8]},
            "memory": {"used": "12.3GB", "total": "32GB", "percentage": "38.4%"},
            "disk": {"used": "456GB", "total": "1TB", "percentage": "45.6%"},
            "network": {"rx": "1.2GB/s", "tx": "0.8GB/s", "connections": 234}
        }
        if metric_type == 'all':
            return metrics
        else:
            return {metric_type: metrics.get(metric_type, "Invalid metric type")}
    elif function_name == "manage_docker":
        action = arguments.get('action', 'ps')
        container = arguments.get('container', '')
        if action == 'ps':
            return {
                "containers": [
                    {"name": "litellm", "status": "running", "uptime": "2 days"},
                    {"name": "open-webui", "status": "running", "uptime": "2 days"},
                    {"name": "mcp-middleware", "status": "running", "uptime": "10 minutes"},
                    {"name": "postgres", "status": "running", "uptime": "30 days"}
                ]
            }
        else:
            return {
                "action": action,
                "container": container,
                "result": f"Successfully executed {action} on {container or 'all containers'}"
            }
    elif function_name == "fetch_url":
        url = arguments.get('url', 'https://example.com')
        return {
            "url": url,
            "status_code": 200,
            "content_preview": f"Mock content from {url}...",
            "headers": {"content-type": "text/html", "content-length": "1234"},
            "fetched_at": "2025-09-07T22:30:00Z"
        }
    elif function_name == "list_workflows":
        return {
            "workflows": [
                {"id": "1", "name": "Daily Backup", "active": True, "last_run": "2025-09-07T00:00:00Z"},
                {"id": "2", "name": "Alert Monitor", "active": True, "last_run": "2025-09-07T22:00:00Z"},
                {"id": "3", "name": "Data Sync", "active": False, "last_run": "2025-09-06T12:00:00Z"},
                {"id": "4", "name": "Report Generator", "active": True, "last_run": "2025-09-07T08:00:00Z"}
            ],
            "total": 4,
            "active": 3
        }
    elif function_name == "execute_workflow":
        workflow_id = arguments.get('workflow_id', '1')
        return {
            "workflow_id": workflow_id,
            "execution_id": "exec-12345",
            "status": "started",
            "started_at": "2025-09-07T22:35:00Z",
            "message": f"Workflow {workflow_id} execution started successfully"
        }
    elif function_name == "get_workflow_executions":
        workflow_id = arguments.get('workflow_id', None)
        limit = arguments.get('limit', 10)
        return {
            "executions": [
                {"id": "exec-123", "workflow": "Daily Backup", "status": "success", "duration": "45s", "finished_at": "2025-09-07T00:00:45Z"},
                {"id": "exec-124", "workflow": "Alert Monitor", "status": "success", "duration": "2s", "finished_at": "2025-09-07T22:00:02Z"},
                {"id": "exec-125", "workflow": "Report Generator", "status": "failed", "error": "Connection timeout", "finished_at": "2025-09-07T08:05:00Z"}
            ],
            "total": 3,
            "limit": limit
        }
    elif function_name == "query_timeseries":
        query = arguments.get('query', 'SELECT * FROM metrics LIMIT 10')
        time_range = arguments.get('time_range', '24h')
        return {
            "query": query,
            "time_range": time_range,
            "results": [
                {"timestamp": "2025-09-07T22:00:00Z", "metric": "cpu_usage", "value": 45.2, "host": "server1"},
                {"timestamp": "2025-09-07T22:15:00Z", "metric": "cpu_usage", "value": 52.1, "host": "server1"},
                {"timestamp": "2025-09-07T22:30:00Z", "metric": "cpu_usage", "value": 38.9, "host": "server1"}
            ],
            "row_count": 3
        }
    elif function_name == "list_hypertables":
        return {
            "hypertables": [
                {"name": "metrics", "dimensions": 1, "chunks": 156, "compression": True, "retention": "30 days"},
                {"name": "logs", "dimensions": 1, "chunks": 89, "compression": True, "retention": "7 days"},
                {"name": "events", "dimensions": 2, "chunks": 234, "compression": False, "retention": "90 days"}
            ],
            "total": 3,
            "database": "timescaledb"
        }
    elif function_name == "get_timeseries_stats":
        table_name = arguments.get('table_name', None)
        return {
            "table": table_name or "all",
            "stats": {
                "total_rows": 1234567,
                "disk_size": "2.3 GB",
                "compressed_size": "456 MB",
                "compression_ratio": "5.0x",
                "chunk_count": 156,
                "oldest_data": "2025-08-07T00:00:00Z",
                "newest_data": "2025-09-07T22:30:00Z"
            }
        }
    elif function_name == "browser_navigate":
        url = arguments.get('url', 'https://example.com')
        wait_for = arguments.get('wait_for', None)
        return {
            "url": url,
            "status": "navigated",
            "page_title": "Example Domain",
            "waited_for": wait_for,
            "load_time": "1.2s"
        }
    elif function_name == "browser_screenshot":
        url = arguments.get('url', 'https://example.com')
        full_page = arguments.get('full_page', True)
        selector = arguments.get('selector', None)
        
        # Create a small placeholder image (1x1 red pixel) as base64
        # In production, this would be the actual screenshot
        placeholder_image = (
            "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8DwHwAFBQIAX8jx"
            "0gAAAABJRU5ErkJggg=="
        )
        
        # Generate filename for MinIO storage
        import time
        timestamp = int(time.time())
        filename = f"screenshots/{url.replace('https://', '').replace('http://', '').replace('/', '_')[:50]}_{timestamp}.png"
        
        # In production, this would actually upload to MinIO
        # For now, return mock data with MinIO URL
        return {
            "url": url,
            "screenshot_saved": True,
            "minio_path": filename,
            "minio_url": f"https://s3.ai-servicers.com/mcp-storage/{filename}",
            "full_page": full_page,
            "selector": selector,
            "dimensions": "1920x1080" if not full_page else "1920x3500",
            "file_size": "234KB",
            "message": f"Screenshot of {url} saved to MinIO at {filename}",
            "format": "png"
        }
    elif function_name == "browser_extract":
        url = arguments.get('url', 'https://example.com')
        selector = arguments.get('selector', 'h1')
        attribute = arguments.get('attribute', 'text')
        return {
            "url": url,
            "selector": selector,
            "attribute": attribute,
            "extracted": [
                {"element": 1, "value": "Example Domain"},
                {"element": 2, "value": "This is an example page"}
            ],
            "count": 2
        }
    elif function_name == "minio_list_objects":
        prefix = arguments.get('prefix', '')
        recursive = arguments.get('recursive', False)
        return {
            "bucket": "mcp-storage",
            "prefix": prefix,
            "objects": [
                {"name": "screenshots/google.com_1735789200.png", "size": "234KB", "modified": "2025-09-07T22:00:00Z"},
                {"name": "screenshots/github.com_1735789100.png", "size": "456KB", "modified": "2025-09-07T21:45:00Z"},
                {"name": "uploads/document.pdf", "size": "1.2MB", "modified": "2025-09-07T20:00:00Z"},
                {"name": "temp/analysis.json", "size": "12KB", "modified": "2025-09-07T19:30:00Z"}
            ],
            "total": 4
        }
    elif function_name == "minio_upload_object":
        object_name = arguments.get('object_name', 'uploads/file.txt')
        data = arguments.get('data', '')
        content_type = arguments.get('content_type', 'application/octet-stream')
        return {
            "status": "uploaded",
            "bucket": "mcp-storage",
            "object_name": object_name,
            "size": len(data),
            "content_type": content_type,
            "url": f"https://s3.ai-servicers.com/mcp-storage/{object_name}",
            "message": f"Successfully uploaded {object_name} to MinIO"
        }
    elif function_name == "minio_download_object":
        object_name = arguments.get('object_name', '')
        # In production, this would download from MinIO
        # For mock, return placeholder data
        return {
            "status": "downloaded",
            "bucket": "mcp-storage",
            "object_name": object_name,
            "data": "base64_encoded_file_content_here",
            "size": "234KB",
            "content_type": "image/png" if '.png' in object_name else "application/octet-stream",
            "message": f"Successfully downloaded {object_name} from MinIO"
        }
    elif function_name == "minio_delete_object":
        object_name = arguments.get('object_name', '')
        return {
            "status": "deleted",
            "bucket": "mcp-storage",
            "object_name": object_name,
            "message": f"Successfully deleted {object_name} from MinIO"
        }
    elif function_name == "minio_get_url":
        object_name = arguments.get('object_name', '')
        expiry_hours = arguments.get('expiry_hours', 24)
        import time
        expiry_timestamp = int(time.time()) + (expiry_hours * 3600)
        return {
            "status": "success",
            "bucket": "mcp-storage",
            "object_name": object_name,
            "presigned_url": f"https://s3.ai-servicers.com/mcp-storage/{object_name}?X-Amz-Expires={expiry_hours*3600}&X-Amz-Signature=mock_signature",
            "expires_at": f"2025-09-08T{22 + expiry_hours % 24:02d}:00:00Z",
            "expiry_hours": expiry_hours,
            "message": f"Generated presigned URL for {object_name}, valid for {expiry_hours} hours"
        }
    else:
        return {"error": f"Unknown function: {function_name}"}

@app.route('/v1/chat/completions', methods=['POST'])
def chat_completions():
    """Proxy chat completions with MCP tool execution"""
    try:
        # Enhanced diagnostic logging
        raw_data = request.get_data(as_text=True)
        logger.info(f"--- Raw Request Body Start ---\n{raw_data}\n--- Raw Request Body End ---")
        
        # Log headers for comparison
        logger.info(f"--- Request Headers ---")
        for header, value in request.headers:
            if header.lower() != 'authorization':
                logger.info(f"{header}: {value}")
            else:
                logger.info(f"{header}: [REDACTED]")
        logger.info(f"--- End Headers ---")
        
        # Parse JSON request
        try:
            request_data = request.json
            logger.info(f"--- Parsed Request JSON (tools/stream only) ---")
            logger.info(f"Has 'tools': {'tools' in request_data}")
            logger.info(f"Has 'stream': {'stream' in request_data}, value: {request_data.get('stream', 'not set')}")
            logger.info(f"Model: {request_data.get('model', 'not set')}")
            logger.info(f"--- End Parsed Request ---")
        except Exception as json_err:
            logger.error(f"Failed to parse request body as JSON: {json_err}")
            return jsonify({"error": "Invalid JSON format"}), 400
        
        # Get authorization header
        auth_header = request.headers.get('Authorization', '')
        
        # Fix 1: Tool Injection - Auto-inject tools if missing
        if not request_data.get('tools'):
            logger.info("No tools found in request. Auto-injecting default MCP toolset.")
            request_data['tools'] = MCP_TOOLS_DEFINITION
            request_data['tool_choice'] = 'auto'
        
        # Fix 2: Streaming Prevention - Force streaming off for compatibility
        if request_data.get('stream', False):
            logger.warning("Streaming requested by client, forcing stream=False for compatibility.")
            request_data['stream'] = False
        
        # Forward request to LiteLLM
        headers = {
            'Authorization': auth_header,
            'Content-Type': 'application/json'
        }
        
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
                
                # Step 3: Execute tools with defensive error handling
                tool_results = []
                
                # Ensure tool_calls is a list before iterating
                if not isinstance(tool_calls, list):
                    logger.error(f"tool_calls is not a list: {type(tool_calls)} - {tool_calls}")
                    tool_calls = []
                
                for tool_call in tool_calls:
                    # Check if tool_call is a dictionary
                    if not isinstance(tool_call, dict):
                        logger.warning(f"Skipping invalid tool_call item (not a dict): {tool_call}")
                        continue
                    
                    # Safely get function information
                    function_info = tool_call.get('function')
                    if not function_info or not isinstance(function_info, dict):
                        logger.warning(f"Skipping tool_call with invalid function info: {tool_call}")
                        continue
                    
                    function_name = function_info.get('name')
                    if not function_name:
                        logger.warning(f"Skipping tool_call with no function name: {tool_call}")
                        continue
                    
                    # Handle empty or invalid arguments
                    try:
                        args_str = function_info.get('arguments', '{}')
                        if not args_str or args_str.strip() == '':
                            arguments = {}
                        else:
                            arguments = json.loads(args_str)
                    except (json.JSONDecodeError, TypeError) as e:
                        logger.warning(f"Failed to parse arguments for {function_name}: {e}. Arguments string: '{args_str}'")
                        arguments = {}
                    except Exception as e:
                        logger.error(f"Unexpected error parsing arguments for {function_name}: {e}")
                        arguments = {}
                    
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

@app.route('/v1/models', methods=['GET'])
def get_models():
    """Proxy models endpoint from LiteLLM"""
    try:
        auth_header = request.headers.get('Authorization', '')
        headers = {
            'Authorization': auth_header,
            'Content-Type': 'application/json'
        }
        
        response = requests.get(
            f"{LITELLM_URL}/v1/models",
            headers=headers
        )
        
        return jsonify(response.json()), response.status_code
        
    except Exception as e:
        logger.error(f"Error proxying models request: {str(e)}")
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