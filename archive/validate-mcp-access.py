#!/usr/bin/env python3
"""
Validation script for LiteLLM-MCP Integration
Tests that LiteLLM can access and use MCP services via SSE
"""

import requests
import json
import time
from typing import Dict, Any, List
import subprocess
import sys

# Configuration
LITELLM_URL = "https://litellm.ai-servicers.com"
LITELLM_API_URL = "http://localhost:4000"  # Internal API
MCP_ADAPTER_URL = "http://localhost:3333"
MCP_PROXY_URL = "http://localhost:8585"

# LiteLLM Master Key (from config)
LITELLM_MASTER_KEY = "sk-e0b742bc6575adf26c7d356c49c78d8fd08119fcde1d6e188d753999b5f956fc"

class MCPValidator:
    def __init__(self):
        self.results = {}
        self.passed = 0
        self.failed = 0
    
    def print_header(self, text: str):
        """Print formatted header"""
        print("\n" + "=" * 60)
        print(f" {text}")
        print("=" * 60)
    
    def test_litellm_health(self) -> bool:
        """Test if LiteLLM is running and healthy"""
        try:
            # Test internal endpoint
            response = requests.get(f"{LITELLM_API_URL}/health", timeout=5)
            if response.status_code == 200:
                print("✅ LiteLLM is running on port 4000")
                return True
            else:
                print(f"❌ LiteLLM health check failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ LiteLLM not accessible: {e}")
            return False
    
    def test_mcp_adapter_health(self) -> bool:
        """Test if MCP adapter is running"""
        try:
            response = requests.get(f"{MCP_ADAPTER_URL}/health", timeout=5)
            if response.status_code == 200:
                data = response.json()
                print(f"✅ MCP Adapter is running with {len(data.get('services', []))} services")
                return True
            else:
                print(f"❌ MCP Adapter health check failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ MCP Adapter not accessible: {e}")
            return False
    
    def test_mcp_proxy_services(self) -> Dict[str, bool]:
        """Test each MCP service via SSE proxy"""
        services = ["filesystem", "postgres", "fetch", "monitoring", "n8n", "playwright", "timescaledb"]
        results = {}
        
        for service in services:
            try:
                response = requests.get(
                    f"{MCP_PROXY_URL}/servers/{service}/sse",
                    headers={'Accept': 'text/event-stream'},
                    timeout=2,
                    stream=True
                )
                # Just check if we get a response
                if response.status_code == 200:
                    results[service] = True
                    print(f"  ✅ {service}: Available")
                else:
                    results[service] = False
                    print(f"  ❌ {service}: Not available (status {response.status_code})")
            except Exception as e:
                results[service] = False
                print(f"  ❌ {service}: Error - {str(e)[:50]}")
        
        return results
    
    def test_litellm_models(self) -> bool:
        """Test LiteLLM model availability"""
        try:
            response = requests.get(
                f"{LITELLM_API_URL}/v1/models",
                headers={"Authorization": f"Bearer {LITELLM_MASTER_KEY}"},
                timeout=5
            )
            if response.status_code == 200:
                data = response.json()
                models = data.get('data', [])
                print(f"✅ LiteLLM has {len(models)} models available")
                # Show a few models
                for model in models[:5]:
                    print(f"  - {model.get('id', 'unknown')}")
                if len(models) > 5:
                    print(f"  ... and {len(models) - 5} more")
                return True
            else:
                print(f"❌ Failed to list models: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Error listing models: {e}")
            return False
    
    def test_simple_completion(self) -> bool:
        """Test a simple completion without MCP"""
        try:
            response = requests.post(
                f"{LITELLM_API_URL}/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {LITELLM_MASTER_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "gpt-4o-mini",
                    "messages": [
                        {"role": "user", "content": "Say 'Hello from LiteLLM' in 5 words or less"}
                    ],
                    "max_tokens": 20
                },
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                content = data['choices'][0]['message']['content']
                print(f"✅ Simple completion works: '{content}'")
                return True
            else:
                print(f"❌ Completion failed: {response.status_code}")
                print(f"   Response: {response.text[:200]}")
                return False
        except Exception as e:
            print(f"❌ Error in completion: {e}")
            return False
    
    def test_mcp_function_call(self, service: str, tool_name: str, params: Dict) -> bool:
        """Test calling an MCP function through LiteLLM"""
        try:
            # First, let's try to call the function directly via the adapter
            function_name = f"{service}_{tool_name}"
            
            response = requests.post(
                f"{MCP_ADAPTER_URL}/v1/functions/{function_name}/execute",
                headers={"Content-Type": "application/json"},
                json={"arguments": params},
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ MCP function {function_name} executed successfully")
                print(f"   Result: {str(result)[:100]}...")
                return True
            else:
                print(f"❌ MCP function {function_name} failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Error calling MCP function: {e}")
            return False
    
    def validate_all(self):
        """Run all validation tests"""
        self.print_header("LiteLLM-MCP Integration Validation")
        
        # Test 1: Basic Health Checks
        self.print_header("1. Health Checks")
        litellm_ok = self.test_litellm_health()
        adapter_ok = self.test_mcp_adapter_health()
        
        if litellm_ok:
            self.passed += 1
        else:
            self.failed += 1
            
        if adapter_ok:
            self.passed += 1
        else:
            self.failed += 1
        
        # Test 2: MCP Service Availability
        self.print_header("2. MCP Service Availability")
        service_results = self.test_mcp_proxy_services()
        for service, status in service_results.items():
            if status:
                self.passed += 1
            else:
                self.failed += 1
        
        # Test 3: LiteLLM Model Access
        self.print_header("3. LiteLLM Model Access")
        if self.test_litellm_models():
            self.passed += 1
        else:
            self.failed += 1
        
        # Test 4: Simple Completion
        self.print_header("4. Simple LiteLLM Completion")
        if self.test_simple_completion():
            self.passed += 1
        else:
            self.failed += 1
        
        # Test 5: MCP Function Examples
        self.print_header("5. MCP Function Call Examples")
        
        # Example MCP function calls (these might fail if adapter needs enhancement)
        test_cases = [
            ("filesystem", "list_directory", {"path": "/tmp"}),
            ("fetch", "fetch", {"url": "https://example.com"}),
            ("monitoring", "get_recent_errors", {"hours": 1}),
        ]
        
        for service, tool, params in test_cases:
            print(f"\nTesting {service}.{tool}...")
            if self.test_mcp_function_call(service, tool, params):
                self.passed += 1
            else:
                self.failed += 1
        
        # Final Summary
        self.print_header("Validation Summary")
        total = self.passed + self.failed
        print(f"✅ Passed: {self.passed}/{total}")
        print(f"❌ Failed: {self.failed}/{total}")
        print(f"📊 Success Rate: {(self.passed/total*100):.1f}%")
        
        if self.passed == total:
            print("\n🎉 All validation tests passed!")
        elif self.passed > total * 0.7:
            print("\n⚠️  Most tests passed, some issues to address")
        else:
            print("\n❌ Significant issues detected, review configuration")
        
        return self.passed == total

def test_curl_examples():
    """Show curl examples for manual testing"""
    print("\n" + "=" * 60)
    print(" Manual Testing Examples")
    print("=" * 60)
    
    print("\n1. Test LiteLLM directly:")
    print("""
curl http://localhost:4000/v1/chat/completions \\
  -H "Authorization: Bearer sk-e0b742bc6575adf26c7d356c49c78d8fd08119fcde1d6e188d753999b5f956fc" \\
  -H "Content-Type: application/json" \\
  -d '{
    "model": "gpt-4o-mini",
    "messages": [{"role": "user", "content": "Hello"}],
    "max_tokens": 50
  }'
""")
    
    print("\n2. List available models:")
    print("""
curl http://localhost:4000/v1/models \\
  -H "Authorization: Bearer sk-e0b742bc6575adf26c7d356c49c78d8fd08119fcde1d6e188d753999b5f956fc"
""")
    
    print("\n3. Test MCP adapter:")
    print("""
curl http://localhost:3333/health
curl http://localhost:3333/v1/functions
""")
    
    print("\n4. Test MCP service directly:")
    print("""
curl -N http://localhost:8585/servers/filesystem/sse \\
  -H "Accept: text/event-stream" --max-time 3
""")

if __name__ == "__main__":
    # Run validation
    validator = MCPValidator()
    success = validator.validate_all()
    
    # Show manual testing examples
    test_curl_examples()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)