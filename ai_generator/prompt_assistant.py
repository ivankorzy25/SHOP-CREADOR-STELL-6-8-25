"""
Asistente IA para mejorar prompts de generación
"""

import json
from typing import Dict, Optional

class PromptAssistant:
    """Asistente que ayuda a mejorar prompts usando IA"""
    
    def __init__(self, ai_model):
        self.model = ai_model
        self.conversation_history = []
    
    def suggest_improvements(self, current_prompt: str, user_request: str, product_type: str = None) -> Dict:
        """
        Reimagines el prompt basándose en la solicitud del usuario, devolviendo el prompt completo modificado.
        """
        
        system_prompt = """Eres un asistente experto en ingeniería de prompts para la generación de HTML con IA. Tu tarea es modificar un prompt base según las solicitudes del usuario para ajustar estilos y contenido.

IMPORTANTE: Tu respuesta DEBE ser ÚNICAMENTE un objeto JSON válido, sin texto adicional antes o después.

Cuando el usuario pida cambios de estilo (colores, tamaños, bordes, etc.) o de contenido, tu lógica debe ser:
1.  **Analiza el `prompt actual`** para entender su estructura e instrucciones.
2.  **Identifica la instrucción** que controla el elemento que el usuario quiere cambiar (ej. el título, las secciones, las tablas).
3.  **NO REEMPLACES la instrucción completa.** En su lugar, **AÑADE una aclaración** a la instrucción existente para que la IA generadora sepa qué hacer.
4.  **Genera un "diff"** que contenga la línea original a modificar (`search`) y la nueva línea con la instrucción añadida (`replace`).

**Formato de respuesta (SOLO JSON):**
{
    "explicacion": "Una descripción breve y amigable del cambio que realizaste.",
    "diff": [
        {
            "type": "replace_line_content",
            "search": "<contenido original de la línea a buscar>",
            "replace": "<nuevo contenido de la línea modificada>"
        }
    ]
}

**Ejemplo de Lógica:**
-   **Prompt actual tiene la línea:** "Genera un título atractivo"
-   **Usuario pide:** "el título en verde y más grande"
-   **Tu razonamiento:** Debo modificar la instrucción del título para añadirle estilos. No debo borrarla, sino complementarla.
-   **Respuesta JSON que DEBES generar:**
    {
        "explicacion": "¡Claro! He ajustado la instrucción del prompt para que el título se genere en color verde y con una fuente más grande.",
        "diff": [
            {
                "type": "replace_line_content",
                "search": "Genera un título atractivo",
                "replace": "Genera un título atractivo con el siguiente estilo: <h1 style='color: green; font-size: 28px;'>TÍTULO</h1>"
            }
        ]
    }
"""
        
        user_message = f"""
        PROMPT ACTUAL:
        ---
        {current_prompt}
        ---
        
        SOLICITUD DEL USUARIO: "{user_request}"
        
        Por favor, analiza mi solicitud y genera un diff en el formato JSON especificado para modificar el prompt actual.
        """
        
        try:
            response = self.model.generate_content([system_prompt, user_message])
            response_text = response.text.strip()
            
            # Limpiar y parsear la respuesta JSON
            if "```json" in response_text:
                json_start = response_text.find("```json") + 7
                json_end = response_text.rfind("```")
                json_text = response_text[json_start:json_end].strip()
            else:
                json_text = response_text

            result = json.loads(json_text)

            # Validar que la respuesta tiene el formato esperado
            if 'diff' not in result or 'explicacion' not in result:
                raise ValueError("La respuesta de la IA no tiene el formato JSON esperado (debe contener 'diff' y 'explicacion').")

            modified_prompt = current_prompt
            for change in result.get('diff', []):
                if change.get('type') == 'replace_line_content':
                    search_text = change.get('search')
                    replace_text = change.get('replace')
                    if search_text and replace_text and search_text in modified_prompt:
                        modified_prompt = modified_prompt.replace(search_text, replace_text, 1)

            final_result = {
                "explicacion": result['explicacion'],
                "prompt_modificado": modified_prompt
            }

            self.conversation_history.append({'request': user_request, 'suggestion': result})
            
            return final_result
            
        except Exception as e:
            print(f"Error procesando la sugerencia de la IA: {e}")
            return {
                "explicacion": f"Lo siento, ocurrió un error al procesar tu solicitud: {str(e)}",
                "prompt_modificado": current_prompt, # Devolver el prompt original en caso de error
                "error": True
            }

    def get_conversation_history(self):
        """Retorna el historial de la conversación"""
        return self.conversation_history
    
    def clear_history(self):
        """Limpia el historial de conversación"""
        self.conversation_history = []
