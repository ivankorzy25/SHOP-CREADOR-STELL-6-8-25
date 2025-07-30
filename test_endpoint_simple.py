"""
Test simple del endpoint
"""

import requests
import json

# Hacer la petición directamente
url = "http://localhost:5002/api/ai-generator/ai-assistant"
data = {
    "prompt": "Genera una descripción HTML bien estructurada con:\n- Un título atractivo\n- Secciones claramente definidas",
    "request": "Cambia el color del título a verde",
    "product_type": "grupo_electrogeno",
    "api_key": "AIzaSyBYjaWimtWtTk3m_4SjFgLQRWPkiu0suiw"
}

print("Enviando petición...")
response = requests.post(url, json=data)

print(f"\nCódigo de estado: {response.status_code}")
print(f"Headers: {dict(response.headers)}")
print(f"\nRespuesta raw: {response.text[:500]}...")

try:
    json_data = response.json()
    print(f"\nJSON parseado - claves principales: {list(json_data.keys())}")
    
    # Si hay 'suggestion' anidado, mostrarlo
    if 'suggestion' in json_data:
        print(f"Encontrado 'suggestion' anidado con claves: {list(json_data['suggestion'].keys())}")
except Exception as e:
    print(f"Error parseando JSON: {e}")
