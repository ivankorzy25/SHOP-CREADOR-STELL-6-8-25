#!/bin/bash

echo "Probando endpoint con curl..."

curl -X POST http://localhost:5002/api/ai-generator/ai-assistant \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Test prompt",
    "request": "Test request", 
    "product_type": "test",
    "api_key": "AIzaSyBYjaWimtWtTk3m_4SjFgLQRWPkiu0suiw"
  }' | python3 -m json.tool
