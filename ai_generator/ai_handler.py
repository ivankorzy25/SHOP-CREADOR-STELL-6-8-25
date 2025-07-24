"""
Módulo de Generación con IA para STEL Shop
Gestiona la creación de descripciones HTML usando Google Gemini
"""

import json
from typing import Dict
import google.generativeai as genai
from pathlib import Path
from ai_generator.premium_generator import generar_descripcion_detallada_html_premium

class AIHandler:
    """Maneja la generación de descripciones con IA"""
    
    def __init__(self, api_key: str = "AIzaSyBYjaWimtWtTk3m_4SjFgLQRWPkiu0suiw"):
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
            genai.configure(api_key=api_key)
            
            # Prueba de validación: listar modelos para confirmar que la clave es válida
            # y la conexión funciona. Esto es más fiable que solo configurar.
            models = [m for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
            if not models:
                raise Exception("No se encontraron modelos compatibles para generar contenido.")

            # Intentar con el modelo más reciente
            self.model = genai.GenerativeModel('gemini-1.5-flash')
            
            print("✅ Modelo de IA inicializado y validado correctamente.")
            return True
        except Exception as e:
            error_message = str(e)
            if "API key not valid" in error_message:
                print("❌ Error de autenticación: La API key proporcionada no es válida.")
            else:
                print(f"❌ Error inicializando o validando el modelo: {error_message}")
            self.model = None
            return False
    
    def _load_product_types(self) -> Dict:
        """Carga la configuración de tipos de productos"""
        template_path = self.module_path / "templates" / "product_templates.json"
        
        default_types = {
            "grupo_electrogeno": {
                "keywords": ["generador", "grupo electrógeno", "kva", "kw"],
                "focus": "potencia, autonomía, motor",
                "applications": "respaldo energético, obras, industria"
            },
            "compresor": {
                "keywords": ["compresor", "psi", "bar", "aire comprimido"],
                "focus": "presión, caudal, tanque",
                "applications": "talleres, pintura, herramientas neumáticas"
            },
            "motobomba": {
                "keywords": ["motobomba", "bomba", "caudal", "litros"],
                "focus": "caudal, altura máxima, succión",
                "applications": "riego, drenaje, construcción"
            },
            "motocultivador": {
                "keywords": ["motocultivador", "cultivador", "labranza"],
                "focus": "potencia, ancho de trabajo, profundidad",
                "applications": "agricultura, huertos, preparación de suelo"
            }
        }
        
        if template_path.exists():
            try:
                with open(template_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                pass
        
        return default_types
    
    def detect_product_type(self, product_info: Dict) -> str:
        """Detecta el tipo de producto basándose en la información"""
        # Combinar toda la información relevante
        search_text = f"{product_info.get('nombre', '')} {product_info.get('familia', '')} {product_info.get('modelo', '')}".lower()
        
        # Buscar coincidencias
        for product_type, config in self.product_types.items():
            for keyword in config['keywords']:
                if keyword.lower() in search_text:
                    return product_type
        
        return "generico"
    
    def generate_description(self, product_info: Dict, config: Dict = None) -> str:
        """
        Genera la descripción HTML del producto utilizando el nuevo método premium.
        """
        # Llama directamente a la función de generación premium
        return generar_descripcion_detallada_html_premium(
            row=product_info,
            config=config,
            modelo_ia=self.model
        )

    def preview_with_example(self, example_product: Dict = None) -> str:
        """Genera una vista previa con un producto de ejemplo"""
        if not example_product:
            example_product = {
                'nombre': 'Grupo Electrógeno Cummins 100KVA',
                'marca': 'Cummins',
                'modelo': 'C100D5',
                'codigo': 'GE-CUM-100',
                'familia': 'Grupos Electrógenos',
                'potencia_kva': '100',
                'potencia_kw': '80',
                'voltaje': '380/220',
                'frecuencia': '50',
                'motor': 'Cummins 6BT5.9-G2',
                'alternador': 'Stamford UCI274C',
                'consumo': '22.3',
                'tanque': '220',
                'ruido': '75',
                'largo': '3200',
                'ancho': '1100',
                'alto': '1460',
                'peso': '1720',
                'pdf_url': 'cummins_c100d5.pdf'
            }
        
        config = {
            'whatsapp': '541139563099',
            'email': 'info@generadores.ar',
            'telefono_display': '+54 11 3956-3099',
            'website': 'www.generadores.ar'
        }
        
        return self.generate_description(example_product, config)
