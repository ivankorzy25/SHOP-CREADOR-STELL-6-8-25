"""
Test directo de Flask sin HTTP
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Importar la app Flask
from main import app, ai_handler

# Configurar el contexto de prueba
with app.test_client() as client:
    # Primero validar API key
    print("1. Validando API key...")
    response = client.post('/api/ai-generator/validate-api-key', 
                          json={"api_key": "AIzaSyBYjaWimtWtTk3m_4SjFgLQRWPkiu0suiw"})
    print(f"Validación: {response.get_json()}")
    
    # Ahora probar el asistente
    print("\n2. Probando asistente IA...")
    data = {
        "prompt": "Genera una descripción HTML bien estructurada con:\n- Un título atractivo\n- Secciones claramente definidas",
        "request": "Cambia el color del título a verde",
        "product_type": "grupo_electrogeno",
        "api_key": "AIzaSyBYjaWimtWtTk3m_4SjFgLQRWPkiu0suiw"
    }
    
    response = client.post('/api/ai-generator/ai-assistant', json=data)
    result = response.get_json()
    
    print(f"\nRespuesta del endpoint:")
    print(f"Claves principales: {list(result.keys())}")
    
    if 'suggestion' in result:
        print(f"⚠️ Encontrado campo 'suggestion' anidado")
        print(f"Claves en suggestion: {list(result['suggestion'].keys())}")
    
    if 'explicacion' in result:
        print(f"✅ Campo 'explicacion' en raíz: {result['explicacion']}")
    
    if 'diff' in result:
        print(f"✅ Campo 'diff' en raíz con {len(result['diff'])} cambios")
