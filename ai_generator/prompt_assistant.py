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
        """Sugiere mejoras al prompt basándose en la solicitud del usuario"""
        
        system_prompt = """Eres un asistente que modifica prompts para agregar estilos CSS cuando el usuario lo solicita.

IMPORTANTE: Tu respuesta DEBE ser ÚNICAMENTE un objeto JSON válido, sin texto adicional antes o después.

Cuando el usuario pida cambios de estilo (colores, tamaños, etc.), debes:
1. Identificar la línea o sección del prompt que se debe modificar.
2. Generar un "diff" que reemplace la línea completa.

Formato de respuesta (SOLO JSON):
{
    "explicacion": "Descripción breve del cambio",
    "diff": [
        {
            "type": "replace_line",
            "line_number": <número de línea a reemplazar (empezando en 1)>,
            "new_content": "<nuevo contenido de la línea>"
        }
    ]
}

Ejemplo:
- Si el prompt tiene en la línea 5 "Genera un título atractivo" y el usuario pide "título en verde", la respuesta sería:
{
    "explicacion": "He modificado la línea 5 para que el título sea verde.",
    "diff": [
        {
            "type": "replace_line",
            "line_number": 5,
            "new_content": "Genera un título atractivo con el siguiente estilo: <h1 style='color: green;'>TÍTULO</h1>"
        }
    ]
}
"""
        
        user_message = f"""
        Prompt actual:
        {current_prompt}
        
        Tipo de producto: {product_type or 'No especificado'}
        
        Solicitud del usuario: {user_request}
        
        Por favor, sugiere mejoras al prompt basándote en la solicitud.
        """
        
        try:
            response = self.model.generate_content(
                [system_prompt, user_message]
            )
            
            # Parsear la respuesta
            response_text = response.text.strip()
            
            # Intentar extraer JSON
            result = None
            
            # Buscar JSON en diferentes formatos
            if "```json" in response_text:
                json_start = response_text.find("```json") + 7
                json_end = response_text.find("```", json_start)
                json_text = response_text[json_start:json_end].strip()
                try:
                    result = json.loads(json_text)
                except json.JSONDecodeError:
                    pass
            else:
                # Intentar parsear directamente
                try:
                    result = json.loads(response_text)
                except json.JSONDecodeError:
                    # Intentar extraer JSON si está mezclado con texto
                    if "{" in response_text and "}" in response_text:
                        try:
                            start = response_text.find("{")
                            end = response_text.rfind("}") + 1
                            json_text = response_text[start:end]
                            result = json.loads(json_text)
                        except json.JSONDecodeError:
                            pass
            
            # Si no se pudo parsear como JSON, crear una respuesta por defecto
            if not result or not isinstance(result, dict) or 'diff' not in result:
                result = {
                    "explicacion": "No pude generar un diff automático. Por favor, aplica los cambios manualmente.",
                    "diff": []
                }

            # Agregar a historial
            self.conversation_history.append({
                'request': user_request,
                'suggestion': result
            })
            
            return result
            
        except Exception as e:
            return {
                "explicacion": f"Lo siento, he encontrado un error al procesar tu solicitud: {str(e)}",
                "diff": [],
                "error": True
            }
    
    def get_conversation_history(self):
        """Retorna el historial de la conversación"""
        return self.conversation_history
    
    def clear_history(self):
        """Limpia el historial de conversación"""
        self.conversation_history = []
