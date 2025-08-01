"""
Módulo de Generación con IA para STEL Shop
Gestiona la creación de descripciones HTML usando Google Gemini
"""

import json
from typing import Dict
import google.generativeai as genai
from pathlib import Path
import traceback

# Importar el generador premium v2
from ai_generator.premium_generator_v2 import generar_descripcion_detallada_html_premium

class AIHandler:
    """Maneja la generación de descripciones con IA"""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key
        self.model = None
        self.current_prompt_version = "base"
        self.module_path = Path(__file__).parent
        self.product_types = self._load_product_types()
        
        if api_key:
            self.initialize_model(api_key)
    
    def initialize_model(self, api_key: str):
        """Inicializa y valida el modelo de Google Gemini"""
        try:
            self.api_key = api_key
            genai.configure(api_key=api_key)
            
            # Configuración para el modelo, incluyendo un timeout más largo
            generation_config = genai.types.GenerationConfig(
                temperature=0.7,
                max_output_tokens=8192,
            )
            safety_settings = [
                {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
            ]
            
            # Priorizar el modelo más nuevo y rápido
            self.model = genai.GenerativeModel(
                model_name='gemini-1.5-flash',
                generation_config=generation_config,
                safety_settings=safety_settings
            )

            # Prueba rápida para asegurar que el modelo está listo
            self.model.generate_content("Test")
            print(f"✅ Modelo de IA inicializado correctamente: gemini-1.5-flash")
            return True
                    
        except Exception as e:
            error_message = str(e)
            print(f"❌ Error al inicializar el modelo: {error_message}")
            traceback.print_exc()
            self.model = None
            return False
    
    def _load_product_types(self) -> Dict:
        """Carga la configuración de tipos de productos."""
        template_path = self.module_path / "templates" / "product_templates.json"
        if template_path.exists():
            with open(template_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}

    def _generate_fallback_description(self, product_info: Dict, error_message: str) -> str:
        """Genera una descripción HTML de fallback con estilos y un mensaje de error claro."""
        nombre_producto = product_info.get('nombre', 'Producto Desconocido')
        error_limpio = error_message.split('generated_content=')[0].strip() # Limpiar mensajes largos
        return f"""
        <!DOCTYPE html>
        <html lang="es"><head><meta charset="UTF-8"><title>Error de Generación</title></head>
        <body>
            <div style="font-family: sans-serif; background-color: #fff; border-left: 5px solid #e74c3c; margin: 20px; padding: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                <h3 style="color: #e74c3c;">¡Ups! La IA no pudo generar la descripción.</h3>
                <p><strong>Producto:</strong> {nombre_producto}</p>
                <p><strong>Motivo del error:</strong> La IA está tardando demasiado en responder o está sobrecargada. Esto suele ser un problema temporal del servicio.</p>
                <p><strong>Mensaje técnico:</strong><br><code>{error_limpio}</code></p>
                <p>Por favor, <strong>inténtalo de nuevo en unos segundos</strong>. Si el problema persiste, verifica tu conexión a internet o la validez de tu API Key.</p>
            </div>
        </body></html>
        """

    def generate_description(self, product_info: Dict, config: Dict = None, prompt_template: str = None) -> str:
        """
        Genera la descripción HTML del producto con manejo de errores y fallback.
        """
        if not self.model:
            return self._generate_fallback_description(product_info, "El modelo de IA no está configurado. Por favor, valida tu API Key.")

        try:
            # Si no se proporciona un prompt, usa el generador premium por defecto.
            if not prompt_template:
                print("🚀 Usando generador premium por defecto.")
                return generar_descripcion_detallada_html_premium(
                    row=product_info, 
                    config=config, 
                    modelo_ia=self.model,
                    print_callback=print
                )
            
            # Si se proporciona un prompt, úsalo.
            print("📝 Usando prompt personalizado para generar HTML.")
            return self._generate_html_with_custom_prompt(product_info, config, prompt_template)
        
        except Exception as e:
            print(f"❌ Error crítico durante la generación: {e}")
            traceback.print_exc()
            # Si cualquier cosa falla, devolvemos el fallback.
            return self._generate_fallback_description(product_info, str(e))

    def _generate_html_with_custom_prompt(self, product_info: Dict, config: Dict, prompt_template: str) -> str:
        """Genera descripción con un prompt personalizado."""
        full_context = {
            "product_data": product_info,
            "contact_config": config
        }
        
        system_message = f"""
        Eres un experto en marketing y desarrollo frontend. Tu tarea es generar un código HTML completo y profesional para la descripción de un producto.

        PROMPT DEL USUARIO:
        ---
        {prompt_template}
        ---

        DATOS DISPONIBLES (JSON):
        {json.dumps(full_context, indent=2, ensure_ascii=False)}

        Genera únicamente el código HTML final. No incluyas explicaciones ni texto adicional. Comienza con `<!DOCTYPE html>`.
        """
        
        response = self.model.generate_content(system_message)
        html_content = response.text.strip()

        # Limpieza básica de la respuesta
        if "```html" in html_content:
            html_content = html_content.split("```html")[1].split("```")[0]

        return html_content
