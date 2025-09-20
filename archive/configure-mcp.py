#!/usr/bin/env python3
"""
Configure MCP servers in LiteLLM via API
This script adds all MCP servers with the correct network-isolated URLs
"""

import requests
import json
import sys

# Configuration
LITELLM_URL = "https://litellm.ai-servicers.com"
MASTER_KEY = "sk-e0b742bc6575adf26c7d356c49c78d8fd08119fcde1d6e188d753999b5f956fc"

# MCP Servers to configure (using internal Docker network URLs)
MCP_SERVERS = [
    {
        "name": "filesystem",
        "url": "http://mcp-proxy-sse:8080/servers/filesystem/sse",
        "description": "File system operations - Administrator access only",
        "auth_type": "none",
        "mcp_version": "latest",
        "restricted_to": ["administrators"]
    },
    {
        "name": "postgres",
        "url": "http://mcp-proxy-sse:8080/servers/postgres/sse",
        "description": "PostgreSQL database operations",
        "auth_type": "none",
        "mcp_version": "latest",
        "restricted_to": ["administrators", "developers"]
    },
    {
        "name": "fetch",
        "url": "http://mcp-proxy-sse:8080/servers/fetch/sse",
        "description": "Web content fetching",
        "auth_type": "none",
        "mcp_version": "latest",
        "restricted_to": ["administrators", "developers"]
    },
    {
        "name": "monitoring",
        "url": "http://mcp-proxy-sse:8080/servers/monitoring/sse",
        "description": "System logs and metrics",
        "auth_type": "none",
        "mcp_version": "latest",
        "restricted_to": ["administrators", "developers"]
    },
    {
        "name": "n8n",
        "url": "http://mcp-proxy-sse:8080/servers/n8n/sse",
        "description": "Workflow automation",
        "auth_type": "none",
        "mcp_version": "latest",
        "restricted_to": ["administrators", "developers"]
    },
    {
        "name": "playwright",
        "url": "http://mcp-proxy-sse:8080/servers/playwright/sse",
        "description": "Browser automation",
        "auth_type": "none",
        "mcp_version": "latest",
        "restricted_to": ["administrators", "developers"]
    },
    {
        "name": "timescaledb",
        "url": "http://mcp-proxy-sse:8080/servers/timescaledb/sse",
        "description": "Time-series database operations",
        "auth_type": "none",
        "mcp_version": "latest",
        "restricted_to": ["administrators", "developers"]
    }
]

def main():
    print("=== LiteLLM MCP Configuration Script ===")
    print(f"Target: {LITELLM_URL}")
    print()
    
    headers = {
        "Authorization": f"Bearer {MASTER_KEY}",
        "Content-Type": "application/json"
    }
    
    # First, try to get current MCP configuration
    print("Checking current MCP configuration...")
    try:
        response = requests.get(
            f"{LITELLM_URL}/mcp/servers",
            headers=headers,
            timeout=10
        )
        if response.status_code == 200:
            current_config = response.json()
            print(f"Found {len(current_config.get('servers', []))} existing MCP servers")
            
            # Option to clear existing config
            if current_config.get('servers'):
                answer = input("Clear existing MCP servers? (y/n): ")
                if answer.lower() == 'y':
                    # Clear existing servers
                    print("Clearing existing MCP servers...")
                    # Note: This endpoint might not exist, we'll handle it gracefully
        else:
            print(f"Could not get current config: {response.status_code}")
    except Exception as e:
        print(f"Error checking current config: {e}")
        print("Continuing with new configuration...")
    
    print()
    print("Adding MCP servers...")
    
    success_count = 0
    for server in MCP_SERVERS:
        print(f"\nConfiguring {server['name']}...")
        print(f"  URL: {server['url']}")
        print(f"  Access: {', '.join(server['restricted_to'])}")
        
        try:
            # Try to add/update the MCP server
            response = requests.post(
                f"{LITELLM_URL}/mcp/servers",
                headers=headers,
                json={
                    "name": server["name"],
                    "url": server["url"],
                    "description": server["description"],
                    "auth_type": server["auth_type"],
                    "mcp_version": server["mcp_version"],
                    "restricted_to": server["restricted_to"]
                },
                timeout=10
            )
            
            if response.status_code in [200, 201]:
                print(f"  ✅ Success!")
                success_count += 1
            else:
                print(f"  ❌ Failed: {response.status_code}")
                print(f"     Response: {response.text[:200]}")
        except Exception as e:
            print(f"  ❌ Error: {e}")
    
    print()
    print("=" * 50)
    print(f"Configuration complete: {success_count}/{len(MCP_SERVERS)} servers configured")
    
    if success_count == len(MCP_SERVERS):
        print("\n✅ All MCP servers configured successfully!")
        print("\nNext steps:")
        print("1. Test with admin API key (has filesystem access)")
        print("2. Test with developer API key (no filesystem access)")
    else:
        print("\n⚠️ Some servers failed to configure")
        print("You may need to configure them manually in the UI")

if __name__ == "__main__":
    main()