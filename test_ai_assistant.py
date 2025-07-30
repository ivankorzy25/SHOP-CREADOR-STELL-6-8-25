"""
Script de prueba para verificar el funcionamiento del asistente IA
"""

import requests
import json

# URL base del servidor
BASE_URL = "http://localhost:5002"

# API key de prueba (la misma que está en el código)
API_KEY = "AIzaSyBYjaWimtWtTk3m_4SjFgLQRWPkiu0suiw"

# Prompt de ejemplo
PROMPT_EJEMPLO = """
Eres un experto en redacción de descripciones comerciales para productos industriales.

Genera una descripción profesional y persuasiva para el siguiente producto:

Tipo de producto: {product_type}
Información del producto:
- Nombre: {nombre}
- Marca: {marca}
- Modelo: {modelo}
- Potencia: {potencia_kva} KVA
- Motor: {motor}
- Características técnicas: {tech_specs}

INSTRUCCIONES ESPECÍFICAS:
1. La descripción debe ser profesional y orientada a la venta
2. Destaca los beneficios principales y ventajas competitivas
3. Menciona las aplicaciones típicas del producto ({applications})
4. Enfócate especialmente en: {focus_areas}

Genera una descripción HTML bien estructurada con:
- Un título atractivo
- Secciones claramente definidas
- Información técnica relevante
- Llamadas a la acción
"""

def test_ai_assistant():
    """Prueba el asistente IA con una solicitud de cambio de estilo"""
    
    print("🧪 Probando el asistente IA...")
    
    # Primero, validar la API key
    print("\n1. Validando API key...")
    response = requests.post(f"{BASE_URL}/api/ai-generator/validate-api-key", 
                           json={"api_key": API_KEY})
    
    if response.status_code == 200:
        result = response.json()
        if result.get('success'):
            print("✅ API key válida")
        else:
            print("❌ API key inválida:", result.get('error'))
            return
    else:
        print("❌ Error validando API key:", response.status_code)
        return
    
    # Ahora probar el asistente
    print("\n2. Probando asistente IA...")
    
    # Solicitud de prueba: cambiar el color del título
    assistant_request = {
        "prompt": PROMPT_EJEMPLO,
        "request": "Cambia el color del título a verde con fondo amarillo y hazlo más grande",
        "product_type": "grupo_electrogeno",
        "api_key": API_KEY
    }
    
    print("📝 Solicitud:", assistant_request["request"])
    
    response = requests.post(f"{BASE_URL}/api/ai-generator/ai-assistant", 
                           json=assistant_request)
    
    if response.status_code == 200:
        # Primero ver el texto raw
        print("\n[DEBUG] Respuesta raw del servidor:")
        print(response.text[:500])
        
        result = response.json()
        
        if result.get('success'):
            # Los datos ahora deberían estar en la raíz
            explicacion = result.get('explicacion')
            diff = result.get('diff', [])
            
            print("\n✅ Respuesta del asistente:")
            print("Explicación:", explicacion)
            print("\nCambios sugeridos:")
            
            if diff:
                for i, change in enumerate(diff, 1):
                    print(f"\nCambio {i}:")
                    search_text = change.get('search', '')[:100]
                    replace_text = change.get('replace', '')[:100]
                    print(f"  Buscar: {search_text}...")
                    print(f"  Reemplazar: {replace_text}...")
            else:
                print("  (No se recibieron cambios)")
            
            # Debug: mostrar la respuesta completa
            print("\n[DEBUG] Respuesta completa:")
            print(json.dumps(result, indent=2, ensure_ascii=False))
            
            # Verificar estructura
            print("\n[DEBUG] Verificación de estructura:")
            print(f"  - 'success' presente: {'success' in result}")
            print(f"  - 'explicacion' presente: {'explicacion' in result}")
            print(f"  - 'diff' presente: {'diff' in result}")
            print(f"  - Número de cambios en diff: {len(result.get('diff', []))}")
        else:
            print("❌ Error:", result.get('error'))
            print("Explicación:", result.get('explicacion'))
    else:
        print("❌ Error en la solicitud:", response.status_code)
        print("Respuesta:", response.text)

if __name__ == "__main__":
    test_ai_assistant()
