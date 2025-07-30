"""
Módulo de Generación con IA para STEL Shop
Gestiona la creación de descripciones HTML usando Google Gemini
"""

import json
from typing import Dict
import google.generativeai as genai
from pathlib import Path

# Importar el generador premium
from ai_generator.premium_generator import generar_descripcion_detallada_html_premium

class AIHandler:
    """Maneja la generación de descripciones con IA"""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key
        self.model = None
        self.current_prompt_version = "base"
        self.module_path = Path(__file__).parent
        
        # Cargar configuración de productos
        self.product_types = self._load_product_types()
        
        if api_key:
            self.initialize_model(api_key)
    
    def initialize_model(self, api_key: str):
        """Inicializa y valida el modelo de Google Gemini"""
        try:
            self.api_key = api_key
            genai.configure(api_key=api_key)
            
            models_to_try = [
                'gemini-1.5-flash',
                'gemini-pro',
            ]
            
            for model_name in models_to_try:
                try:
                    self.model = genai.GenerativeModel(model_name)
                    test_response = self.model.generate_content("Di 'funciona' si puedes leer esto")
                    print(f"✅ Modelo de IA inicializado correctamente: {model_name}")
                    return True
                except Exception as model_error:
                    print(f"⚠️ Modelo {model_name} no disponible: {str(model_error)[:50]}...")
                    continue
            
            raise Exception("No se pudo inicializar ningún modelo disponible")
                    
        except Exception as e:
            error_message = str(e)
            if "API key not valid" in error_message or "API_KEY_INVALID" in error_message:
                print("❌ Error: La API key proporcionada no es válida.")
            else:
                print(f"❌ Error al inicializar el modelo: {error_message}")
            self.model = None
            return False
    
    def _load_product_types(self) -> Dict:
        """Carga la configuración de tipos de productos de forma robusta."""
        template_path = self.module_path / "templates" / "product_templates.json"
        default_types = {}
        if template_path.exists():
            try:
                with open(template_path, 'r', encoding='utf-8') as f:
                    default_types = json.load(f)
            except Exception as e:
                print(f"⚠️ Error al cargar 'product_templates.json': {e}. Se usarán los valores por defecto.")
        return default_types
    
    def detect_product_type(self, product_info: Dict) -> str:
        """Detecta el tipo de producto basándose en la información"""
        search_text = f"{product_info.get('nombre', '')} {product_info.get('familia', '')} {product_info.get('modelo', '')}".lower()
        for product_type, config in self.product_types.items():
            for keyword in config.get('keywords', []):
                if keyword.lower() in search_text:
                    return product_type
        return "generico"

    def _generate_fallback_description(self, product_info: Dict, error_message: str = "No se pudo generar la descripción.") -> str:
        """Genera una descripción HTML de fallback con estilos y un mensaje de error."""
        nombre_producto = product_info.get('nombre', 'Producto')
        return f"""
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Error en la Generación</title>
    <style>
        body {{ font-family: sans-serif; background-color: #f4f4f4; color: #333; margin: 0; padding: 20px; }}
        .error-container {{ background-color: #fff; border-left: 5px solid #d9534f; margin: 20px auto; padding: 20px; max-width: 800px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        .error-container h3 {{ color: #d9534f; margin-top: 0; }}
        .error-container p {{ line-height: 1.6; }}
        .error-container code {{ background-color: #eee; padding: 2px 5px; border-radius: 3px; }}
    </style>
</head>
<body>
    <div class="error-container">
        <h3>Error al generar la vista previa para: {nombre_producto}</h3>
        <p>El sistema no pudo generar la descripción HTML por el siguiente motivo:</p>
        <p><code>{error_message}</code></p>
        <p>Se intentará usar un método alternativo para asegurar un resultado.</p>
    </div>
</body>
</html>
"""

    def generate_description(self, product_info: Dict, config: Dict = None, prompt_template: str = None) -> str:
        """
        Genera la descripción HTML del producto.
        - Si no hay prompt_template, usa el generador premium.
        - Si hay prompt_template, usa el método de prompt personalizado.
        """
        if not self.model:
            return self._generate_fallback_description(product_info, "El modelo de IA no está inicializado.")

        if not prompt_template:
            print("🚀 Usando generador premium por defecto.")
            try:
                return generar_descripcion_detallada_html_premium(
                    row=product_info, 
                    config=config, 
                    modelo_ia=self.model,
                    print_callback=print
                )
            except Exception as e:
                print(f"❌ Error en el generador premium: {e}")
                return self._generate_fallback_description(product_info, str(e))
        
        print("📝 Usando prompt personalizado para generar HTML.")
        return self._generate_html_with_custom_prompt(product_info, config, prompt_template)

    def _generate_html_with_custom_prompt(self, product_info: Dict, config: Dict, prompt_template: str) -> str:
        """
        Genera descripción con un prompt personalizado y usa el generador premium como fallback.
        """
        try:
            full_context = {
                "product_data": product_info,
                "contact_config": config
            }
            
            system_message = f"""
Eres un experto en marketing y desarrollo frontend. Tu tarea es generar un código HTML completo y profesional para la descripción de un producto, basándote en un prompt del usuario y datos del producto.

**REQUERIMIENTOS OBLIGATORIOS:**
1.  **HTML COMPLETO:** La respuesta DEBE ser un documento HTML completo, comenzando con `<!DOCTYPE html>` y terminando con `</html>`.
2.  **ESTRUCTURA PROFESIONAL:** Utiliza una estructura semántica (header, section, etc.) y profesional. Incluye secciones como un "Hero Section", "Tarjetas de Información", "Tabla de Especificaciones", y "Llamadas a la Acción (CTA)".
3.  **CSS INTEGRADO:** Incluye estilos CSS dentro de una etiqueta `<style>` en el `<head>`. El diseño debe ser moderno, atractivo y responsive.
4.  **ICONOS SVG INLINE:** Utiliza iconos SVG directamente en el HTML para mejorar el diseño visual.
5.  **DATOS DEL PRODUCTO:** Rellena la plantilla con los datos proporcionados en el JSON `product_data`.
6.  **DATOS DE CONTACTO:** Utiliza la información de `contact_config` para los botones de contacto y CTA.

**PROMPT DEL USUARIO:**
{prompt_template}

**DATOS DISPONIBLES (JSON):**
{json.dumps(full_context, indent=2, ensure_ascii=False)}

Genera el código HTML final. No incluyas explicaciones, solo el código.
"""
            
            response = self.model.generate_content(system_message)
            html_content = response.text.strip()

            if html_content.startswith("```html"):
                html_content = html_content[7:]
            if html_content.endswith("```"):
                html_content = html_content[:-3]

            is_valid_html = html_content.strip().startswith('<!DOCTYPE html>') and len(html_content) > 500
            
            if not is_valid_html:
                print("⚠️ La respuesta de la IA no es un HTML válido o es muy corta. Usando fallback premium.")
                return generar_descripcion_detallada_html_premium(
                    row=product_info, config=config, modelo_ia=self.model, print_callback=print
                )
            
            return html_content
            
        except Exception as e:
            print(f"❌ Error generando con prompt personalizado: {e}. Usando fallback premium.")
            return generar_descripcion_detallada_html_premium(
                row=product_info, config=config, modelo_ia=self.model, print_callback=print
            )

    def preview_with_example(self, example_product: Dict = None) -> str:
        """Genera una vista previa con un producto de ejemplo usando el generador premium."""
        if not example_product:
            example_product = {
                'Descripción': 'Grupo Electrógeno Cummins 100KVA',
                'Marca': 'Cummins',
                'Modelo': 'C100D5',
                'Familia': 'Grupos Electrógenos',
                'Potencia': '100KVA',
                'URL_PDF': 'https://www.example.com/ficha.pdf'
            }
        
        config = {
            'whatsapp': '541139563099',
            'email': 'info@generadores.ar',
            'telefono_display': '+54 11 3956-3099',
            'website': 'www.generadores.ar'
        }
        
        return generar_descripcion_detallada_html_premium(
            row=example_product, config=config, modelo_ia=self.model, print_callback=print
        )
