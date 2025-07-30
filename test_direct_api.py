"""
Prueba directa del endpoint del asistente IA
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ai_generator.ai_handler import AIHandler
from ai_generator.prompt_assistant import PromptAssistant

# Inicializar
ai_handler = AIHandler()
ai_handler.initialize_model("AIzaSyBYjaWimtWtTk3m_4SjFgLQRWPkiu0suiw")

# Crear asistente
assistant = PromptAssistant(ai_handler.model)

# Prompt de prueba
current_prompt = """
Genera una descripción HTML bien estructurada con:
- Un título atractivo
- Secciones claramente definidas
- Información técnica relevante
- Llamadas a la acción
"""

# Solicitud
user_request = "Cambia el color del título a verde con fondo amarillo y hazlo más grande"

# Obtener sugerencia
print("Obteniendo sugerencia del asistente...")
suggestion = assistant.suggest_improvements(
    current_prompt=current_prompt,
    user_request=user_request,
    product_type="grupo_electrogeno"
)

print("\nSugerencia obtenida:")
print(f"Tipo: {type(suggestion)}")
print(f"Claves: {list(suggestion.keys())}")
print(f"Explicación: {suggestion.get('explicacion')}")
print(f"Número de cambios: {len(suggestion.get('diff', []))}")

# Simular la respuesta del endpoint
response_data = {
    'success': True,
    'explicacion': suggestion.get('explicacion', 'Cambios aplicados al prompt'),
    'diff': suggestion.get('diff', []),
    'error': suggestion.get('error', False)
}

print("\nRespuesta formateada para el frontend:")
print(f"Claves: {list(response_data.keys())}")
print(f"Explicación: {response_data.get('explicacion')}")
print(f"Número de cambios: {len(response_data.get('diff', []))}")
