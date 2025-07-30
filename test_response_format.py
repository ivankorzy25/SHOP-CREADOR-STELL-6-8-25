"""
Test para verificar el formato exacto de la respuesta
"""

import requests
import json

# Hacer petición directa
url = "http://localhost:5002/api/ai-generator/ai-assistant"
data = {
    "prompt": "Test prompt",
    "request": "Test request",
    "product_type": "test",
    "api_key": "AIzaSyBYjaWimtWtTk3m_4SjFgLQRWPkiu0suiw"
}

print("Enviando petición...")
response = requests.post(url, json=data)

print(f"\nStatus Code: {response.status_code}")
print(f"\nHeaders:")
for key, value in response.headers.items():
    print(f"  {key}: {value}")

print(f"\nRaw Response Text:")
print(response.text)

print(f"\nParsed JSON:")
try:
    json_data = response.json()
    print(json.dumps(json_data, indent=2, ensure_ascii=False))
except Exception as e:
    print(f"Error parsing JSON: {e}")
