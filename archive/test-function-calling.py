#!/usr/bin/env python3
"""
Test OpenAI function calling through LiteLLM
This verifies that models can use functions and get responses
"""

import requests
import json

def test_function_call():
    """Test function calling with a simple math function"""
    
    url = "http://localhost:4000/v1/chat/completions"
    headers = {
        "Authorization": "Bearer sk-pFgey4HPR9qDvyT-N_7yVQ",  # Admin key
        "Content-Type": "application/json"
    }
    
    # Step 1: Send a message that should trigger a function call
    request_data = {
        "model": "gpt-4o-mini",
        "messages": [
            {
                "role": "user",
                "content": "What's the weather like in San Francisco?"
            }
        ],
        "tools": [
            {
                "type": "function",
                "function": {
                    "name": "get_weather",
                    "description": "Get the current weather in a location",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "location": {
                                "type": "string",
                                "description": "The city and state, e.g. San Francisco, CA"
                            },
                            "unit": {
                                "type": "string",
                                "enum": ["celsius", "fahrenheit"],
                                "description": "The unit of temperature"
                            }
                        },
                        "required": ["location"]
                    }
                }
            }
        ],
        "tool_choice": "auto"
    }
    
    print("Step 1: Sending initial request with function definitions...")
    response = requests.post(url, headers=headers, json=request_data)
    
    if response.status_code != 200:
        print(f"Error: {response.status_code}")
        print(response.text)
        return
    
    result = response.json()
    message = result["choices"][0]["message"]
    
    if "tool_calls" in message:
        print("✓ Model wants to call a function!")
        tool_call = message["tool_calls"][0]
        print(f"  Function: {tool_call['function']['name']}")
        print(f"  Arguments: {tool_call['function']['arguments']}")
        
        # Step 2: Simulate function execution
        function_result = {
            "temperature": "72",
            "unit": "fahrenheit",
            "description": "Sunny"
        }
        
        # Step 3: Send function result back to model
        print("\nStep 2: Sending function result back to model...")
        follow_up_request = {
            "model": "gpt-4o-mini",
            "messages": [
                {
                    "role": "user",
                    "content": "What's the weather like in San Francisco?"
                },
                message,  # Include the assistant's message with tool_calls
                {
                    "role": "tool",
                    "tool_call_id": tool_call["id"],
                    "content": json.dumps(function_result)
                }
            ]
        }
        
        response2 = requests.post(url, headers=headers, json=follow_up_request)
        
        if response2.status_code == 200:
            result2 = response2.json()
            final_message = result2["choices"][0]["message"]["content"]
            print("✓ Model's final response:")
            print(f"  {final_message}")
        else:
            print(f"Error in follow-up: {response2.status_code}")
            print(response2.text)
    else:
        print("Model didn't call a function. Response:")
        print(message.get("content", "No content"))

if __name__ == "__main__":
    test_function_call()