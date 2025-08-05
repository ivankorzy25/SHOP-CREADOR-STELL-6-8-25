"""
Módulo de Generación con IA para STEL Shop
Gestiona la creación de descripciones HTML usando Google Gemini
"""

import json
from typing import Dict, Optional
import google.generativeai as genai
from pathlib import Path
import traceback

# Importar el registro de plantillas y funciones necesarias
from .product_templates import TEMPLATE_REGISTRY
from .premium_generator_v2 import (
    extraer_contenido_pdf, 
    validar_caracteristicas_producto
)
from .premium_generator import extraer_info_tecnica
from .compatibility_fixes import (
    ensure_dict,
    ensure_caracteristicas_dict,
    safe_contenido_pdf_access,
    safe_json_parse
)

class AIHandler:
    """Maneja la generación de descripciones con IA"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        self.model = None
        self.current_prompt_version = "base"
        self.module_path = Path(__file__).parent
        self.product_types = self._load_product_types()
        
        if api_key is not None:
            self.initialize_model(api_key)
    
    def initialize_model(self, api_key: str) -> bool:
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
            print(f"[SUCCESS] Modelo de IA inicializado correctamente: gemini-1.5-flash")
            return True
                    
        except Exception as e:
            error_message = str(e)
            print(f"[ERROR] Error al inicializar el modelo: {error_message}")
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

    def _generate_fallback_description(self, product_info: Optional[Dict], error_message: Optional[str]) -> str:
        """Genera una descripción HTML de fallback con estilos y un mensaje de error claro."""
        product_info = product_info or {}
        nombre_producto = product_info.get('nombre', 'Producto Desconocido')
        error_message = error_message or "Error desconocido"
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

    def generate_description(self, product_info: Optional[Dict], config: Optional[Dict] = None, prompt_template: Optional[str] = None) -> str:
        """
        Genera la descripción HTML del producto de forma dinámica basada en la categoría.
        """
        if not self.model:
            return self._generate_fallback_description(product_info, "El modelo de IA no está configurado.")

        if not product_info:
            return self._generate_fallback_description(None, "No se proporcionó información del producto.")

        try:
            # 1. Extraer datos base y del PDF
            info = extraer_info_tecnica(product_info)
            pdf_url = info.get('pdf_url', '')
            contenido_pdf = None
            if pdf_url and str(pdf_url).lower() not in ['nan', 'none', '']:
                if not pdf_url.startswith('http'):
                    pdf_url = f"https://storage.googleapis.com/fichas_tecnicas/{pdf_url}"
                contenido_pdf = extraer_contenido_pdf(pdf_url, print_callback=print)

            # 2. Usar IA para extraer datos estructurados y categoría
            prompt_path = self.module_path / "templates" / "detailed_product_prompt.json"
            with open(prompt_path, 'r', encoding='utf-8') as f:
                prompts = json.load(f)
            
            # Manejar contenido_pdf de forma segura
            pdf_text = ""
            pdf_tables = ""
            if contenido_pdf:
                if isinstance(contenido_pdf, dict):
                    pdf_text = contenido_pdf.get('text', '')[:4000]
                    pdf_tables = contenido_pdf.get('tables_markdown', '')
                elif isinstance(contenido_pdf, str):
                    pdf_text = contenido_pdf[:4000]
            
            prompt_extract = prompts['prompt_extract'].format(
                pdf_text=pdf_text,
                pdf_tables_as_markdown=pdf_tables,
                nombre=info.get('nombre'),
                familia=info.get('familia'),
                modelo=info.get('modelo'),
                marca=info.get('marca')
            )
            response_extract = self.model.generate_content(prompt_extract)
            json_text = response_extract.text
            try:
                # Búsqueda robusta de JSON en la respuesta
                start_index = json_text.find('{')
                end_index = json_text.rfind('}') + 1
                if start_index != -1 and end_index != -1:
                    json_str = json_text[start_index:end_index]
                    extracted_data = json.loads(json_str)
                    info.update(extracted_data)
                else:
                    raise ValueError("No se encontró un objeto JSON válido en la respuesta de extracción.")
            except json.JSONDecodeError as json_err:
                print(f"Error de decodificación JSON. Respuesta de la IA: >>>{json_text}<<<")
                raise ValueError(f"Respuesta de IA no es un JSON válido: {json_err}") from json_err

            # Normalizar valores de consumo según tipo de combustible
            if info.get('combustible', '').lower() in ['gas', 'gnc', 'glp']:
                # Para gas, asegurar que el consumo esté en m³
                consumo = info.get('consumo', info.get('consumo_75_carga', ''))
                if consumo and 'L/h' not in consumo:
                    info['consumo'] = consumo
            else:
                # Para diesel/nafta, normalizar a L/h
                consumo = info.get('consumo', info.get('consumo_75_carga', ''))
                if consumo:
                    info['consumo'] = consumo.replace('Lts/h', 'L/h').replace('litros/hora', 'L/h')
            
            categoria = info.get('categoria_producto', 'default')

            # Detección manual de tipos de producto para anular la IA si es necesario
            nombre_lower = info.get('nombre', '').lower()
            modelo_lower = info.get('modelo', '').lower()

            # Detectar generadores Cummins específicamente
            if 'cummins' in nombre_lower or 'yns' in modelo_lower or 'cs' in modelo_lower:
                categoria = 'generador_cummins'
            
            print(f"[INFO] Categoría de producto identificada: {categoria}")

            # 3. Usar IA para generar contenido de marketing
            prompt_generate = prompts['prompt_generate'].format(
                categoria_producto=categoria,
                product_data_json=json.dumps(info, indent=2)
            )
            response_generate = self.model.generate_content(prompt_generate)
            json_text_marketing = response_generate.text
            # Parse seguro del JSON de marketing
            marketing_content = safe_json_parse(json_text_marketing)
            if not marketing_content:
                raise ValueError("No se encontró un objeto JSON válido en la respuesta de marketing.")
            
            # 4. Seleccionar y renderizar la plantilla HTML correcta
            # Asegurar que contenido_pdf sea manejado correctamente
            texto_pdf = safe_contenido_pdf_access(contenido_pdf)
            caracteristicas = validar_caracteristicas_producto(info, texto_pdf)
            # Asegurar que caracteristicas sea un diccionario
            caracteristicas = ensure_caracteristicas_dict(caracteristicas)
            
            # Cargar el prompt de generación específico para la categoría
            prompt_generate_path = self.module_path / "templates" / f"{categoria}_prompt.json"
            if not prompt_generate_path.exists():
                prompt_generate_path = self.module_path / "templates" / "default_prompt.json"

            with open(prompt_generate_path, 'r', encoding='utf-8') as f:
                specific_prompts = json.load(f)
            
            prompt_generate = specific_prompts['prompt_generate'].format(product_data_json=json.dumps(info, indent=2))
            response_generate = self.model.generate_content(prompt_generate)
            json_text_marketing = response_generate.text
            # Parse seguro del segundo JSON de marketing
            marketing_content = safe_json_parse(json_text_marketing)
            if not marketing_content:
                raise ValueError("No se encontró un objeto JSON válido en la respuesta de marketing específica.")

            template_function = TEMPLATE_REGISTRY.get(categoria, TEMPLATE_REGISTRY['default'])
            
            print(f"[INFO] Usando plantilla y prompt para '{categoria}'.")
            return template_function(info, marketing_content, caracteristicas, config)

        except Exception as e:
            print(f"[ERROR] Error crítico durante la generación: {e}")
            traceback.print_exc()
            return self._generate_fallback_description(product_info, str(e))

    def _generate_html_with_custom_prompt(self, product_info: Optional[Dict], config: Optional[Dict], prompt_template: str) -> str:
        """Genera descripción con un prompt personalizado."""
        full_context = {
            "product_data": product_info or {},
            "contact_config": config or {}
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
        
        assert self.model is not None
        response = self.model.generate_content(system_message)
        html_content = response.text.strip()

        # Limpieza básica de la respuesta
        if "```html" in html_content:
            html_content = html_content.split("```html")[1].split("```")[0]

        return html_content
