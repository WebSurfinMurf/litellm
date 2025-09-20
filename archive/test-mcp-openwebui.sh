#!/bin/bash
# Quick test script to verify MCP tools through Open WebUI's backend

echo "=== Testing MCP Tools via Open WebUI Backend ==="
echo ""

# Test 1: Admin key - filesystem access
echo "Test 1: Admin trying to list files (should work)"
echo "---"
curl -s -X POST http://localhost:4000/v1/chat/completions \
  -H "Authorization: Bearer sk-pFgey4HPR9qDvyT-N_7yVQ" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gpt-4o-mini",
    "messages": [
      {
        "role": "system",
        "content": "You have access to MCP tools including filesystem. Use them when asked about files."
      },
      {
        "role": "user",
        "content": "List exactly 3 files from /home/administrator/projects directory. Just list the names, nothing else."
      }
    ],
    "max_tokens": 100,
    "temperature": 0
  }' | jq -r '.choices[0].message.content'

echo ""
echo ""

# Test 2: Developer key - filesystem access  
echo "Test 2: Developer trying to list files (should fail or give generic response)"
echo "---"
curl -s -X POST http://localhost:4000/v1/chat/completions \
  -H "Authorization: Bearer sk-nzq2BIYVoVUpz5csqr69xA" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gpt-4o-mini",
    "messages": [
      {
        "role": "system",
        "content": "You have access to MCP tools. Use them when asked."
      },
      {
        "role": "user",
        "content": "List exactly 3 files from /home/administrator/projects directory. Just list the names, nothing else."
      }
    ],
    "max_tokens": 100,
    "temperature": 0
  }' | jq -r '.choices[0].message.content'

echo ""
echo ""

# Test 3: Developer key - PostgreSQL access
echo "Test 3: Developer accessing PostgreSQL (should work)"
echo "---"
curl -s -X POST http://localhost:4000/v1/chat/completions \
  -H "Authorization: Bearer sk-nzq2BIYVoVUpz5csqr69xA" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gpt-4o-mini",
    "messages": [
      {
        "role": "system",
        "content": "You have access to PostgreSQL via MCP tools. Use them to query databases."
      },
      {
        "role": "user",
        "content": "How many databases are in PostgreSQL? Give me just a number."
      }
    ],
    "max_tokens": 50,
    "temperature": 0
  }' | jq -r '.choices[0].message.content'

echo ""