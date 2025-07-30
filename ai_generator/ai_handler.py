"""
Módulo de Generación con IA para STEL Shop
Gestiona la creación de descripciones HTML usando Google Gemini
"""

import json
from typing import Dict
import google.generativeai as genai
from pathlib import Path
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
            # Guardar la API key
            self.api_key = api_key
            
            # Configurar la API key
            genai.configure(api_key=api_key)
            
            # Intentar con diferentes modelos en orden de preferencia
            models_to_try = [
                'gemini-2.0-flash-exp',  # Gemini 2.0 (más avanzado)
                'gemini-1.5-pro',       # Gemini 1.5 Pro (más potente que Flash)
                'gemini-1.5-flash',     # Gemini 1.5 Flash (fallback)
                'gemini-pro',           # Gemini Pro clásico
                'gemini-1.0-pro'        # Versión 1.0 (último recurso)
            ]
            
            for model_name in models_to_try:
                try:
                    # Crear el modelo
                    self.model = genai.GenerativeModel(model_name)
                    
                    # Hacer una prueba simple para verificar que funciona
                    test_response = self.model.generate_content("Di 'funciona' si puedes leer esto")
                    
                    # Si llegamos aquí, el modelo funciona
                    print(f"✅ Modelo de IA inicializado correctamente: {model_name}")
                    return True
                    
                except Exception as model_error:
                    # Este modelo no funcionó, intentar el siguiente
                    print(f"⚠️ Modelo {model_name} no disponible: {str(model_error)[:50]}...")
                    continue
            
            # Si ningún modelo funcionó
            raise Exception("No se pudo inicializar ningún modelo disponible")
                    
        except Exception as e:
            error_message = str(e)
            
            # Mensajes de error más específicos
            if "DNS resolution failed" in error_message:
                print("❌ Error de red: No se pudo conectar con los servidores de Google. Verifica tu conexión a internet y configuración de DNS.")
            elif "API key not valid" in error_message or "API_KEY_INVALID" in error_message:
                print("❌ Error: La API key proporcionada no es válida.")
            elif "quota" in error_message.lower():
                print("❌ Error: Se excedió la cuota de uso de la API.")
            elif "not found" in error_message.lower():
                print("❌ Error: No se encontró el modelo solicitado.")
            else:
                print(f"❌ Error al inicializar el modelo: {error_message}")
            
            self.model = None
            return False
    
    def _load_product_types(self) -> Dict:
        """Carga la configuración de tipos de productos de forma robusta."""
        template_path = self.module_path / "templates" / "product_templates.json"
        
        # Estructura por defecto para evitar errores si el JSON está mal formado
        default_types = {
            "grupo_electrogeno": {
                "keywords": ["generador", "grupo electrógeno", "kva", "kw", "diesel", "nafta", "gas"],
                "focus": "potencia, autonomía, motor, confiabilidad",
                "applications": "respaldo energético, obras, industria, eventos, comercios",
                "extraction_prompt": "Extrae las siguientes especificaciones técnicas de un PDF de un generador eléctrico: 'potencia_kva', 'potencia_kw', 'voltaje', 'frecuencia', 'motor', 'alternador', 'consumo_lph', 'capacidad_tanque_l', 'nivel_ruido_dba', 'dimensiones_mm', 'peso_kg', 'tiene_cabina', 'tiene_tta', 'es_inverter'.",
                "description_prompt": "Eres un experto en marketing de equipos de energía. Genera una descripción de venta detallada y persuasiva para el siguiente generador eléctrico, destacando su confiabilidad, eficiencia y aplicaciones ideales. Utiliza la siguiente información: Nombre: {nombre}, Marca: {marca}, Modelo: {modelo}, Potencia: {potencia_kva} KVA, Motor: {motor}, Consumo: {consumo_lph} L/h. Menciona si tiene cabina ({tiene_cabina}) o TTA ({tiene_tta})."
            },
            "compresor": {
                "keywords": ["compresor", "psi", "bar", "aire comprimido"],
                "focus": "presión, caudal, capacidad del tanque",
                "applications": "talleres, pintura, herramientas neumáticas, limpieza",
                "extraction_prompt": "Extrae las siguientes especificaciones de un PDF de un compresor: 'potencia_hp', 'presion_bar', 'caudal_lpm', 'capacidad_tanque_l', 'tipo_motor', 'dimensiones_mm', 'peso_kg'.",
                "description_prompt": "Eres un redactor técnico especializado en herramientas industriales. Crea una descripción de producto para el compresor {nombre} ({modelo}), enfocándote en su potencia de {potencia_hp} HP y su presión de {presion_bar} Bar. Destaca su uso en talleres y para herramientas neumáticas."
            },
            "motobomba": {
                "keywords": ["motobomba", "bomba", "caudal", "litros"],
                "focus": "caudal, altura máxima de bombeo, diámetro de succión",
                "applications": "riego, drenaje de inundaciones, construcción, agricultura",
                "extraction_prompt": "Extrae las siguientes especificaciones de un PDF de una motobomba: 'potencia_hp', 'caudal_lph', 'altura_maxima_m', 'diametro_succ_pulg', 'tipo_motor', 'peso_kg'.",
                "description_prompt": "Crea una descripción para la motobomba {nombre}, modelo {modelo}. Resalta su caudal de {caudal_lph} L/h y su motor de {potencia_hp} HP. Menciona sus aplicaciones en riego, agricultura y construcción."
            },
            "generico": {
                "keywords": [],
                "focus": "características principales, calidad, durabilidad",
                "applications": "uso general, profesional, industrial",
                "extraction_prompt": "Extrae las especificaciones técnicas clave del siguiente documento. Busca datos como: 'potencia', 'motor', 'dimensiones', 'peso', 'voltaje', 'capacidad'.",
                "description_prompt": "Genera una descripción de producto profesional y clara para {nombre}, modelo {modelo}. Utiliza la información técnica extraída para describir sus características y beneficios principales."
            }
        }
        
        if template_path.exists():
            try:
                with open(template_path, 'r', encoding='utf-8') as f:
                    custom_types = json.load(f)
                    # Actualizar los valores por defecto con los personalizados
                    for key, value in custom_types.items():
                        if key in default_types:
                            default_types[key].update(value)
                        else:
                            default_types[key] = value
            except Exception as e:
                print(f"⚠️ Error al cargar 'product_templates.json': {e}. Se usarán los valores por defecto.")
        
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
    
    def generate_description(self, product_info: Dict, config: Dict = None, prompt_template: str = None) -> str:
        """
        Genera la descripción HTML del producto usando el prompt proporcionado.
        """
        # Si no se proporciona un prompt, no se puede generar nada.
        if not prompt_template:
            return "<div class='error-preview'><h3>Error</h3><p>No se proporcionó un prompt para la generación.</p></div>"

        return self._generate_with_custom_prompt(product_info, config, prompt_template)
    
    def _generate_with_custom_prompt(self, product_info: Dict, config: Dict, prompt_template: str) -> str:
        """Genera descripción con un prompt personalizado, usando una plantilla HTML como base."""
        try:
            # Plantilla HTML basada en el ejemplo proporcionado
            html_template = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{product_data[nombre]}} - Descripción Premium</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif; background: #f5f5f5; color: #333; line-height: 1.6; }
        .container { max-width: 1200px; margin: 0 auto; padding: 20px; }
        .hero-header { background: linear-gradient(135deg, #ff6600 0%, #ff8844 100%); border-radius: 20px; padding: 40px 30px; text-align: center; color: white; margin-bottom: 40px; box-shadow: 0 10px 30px rgba(255, 102, 0, 0.3); position: relative; overflow: hidden; }
        .hero-header::before { content: ''; position: absolute; top: -50%; right: -50%; width: 200%; height: 200%; background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%); animation: pulse 4s ease-in-out infinite; }
        @keyframes pulse { 0%, 100% { transform: scale(1); opacity: 0.5; } 50% { transform: scale(1.1); opacity: 0.8; } }
        .hero-header h1 { font-size: clamp(28px, 5vw, 42px); font-weight: 800; margin-bottom: 10px; text-transform: uppercase; letter-spacing: 1px; position: relative; z-index: 1; }
        .hero-header p { font-size: clamp(16px, 2.5vw, 20px); opacity: 0.95; position: relative; z-index: 1; }
        .info-cards { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; margin-bottom: 40px; }
        .info-card { background: white; border-radius: 16px; padding: 24px; box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08); transition: all 0.3s ease; display: flex; align-items: center; gap: 20px; position: relative; overflow: hidden; }
        .info-card::after { content: ''; position: absolute; top: 0; left: 0; width: 4px; height: 100%; background: #ff6600; transform: scaleY(0); transition: transform 0.3s ease; }
        .info-card:hover { transform: translateY(-5px); box-shadow: 0 8px 30px rgba(0, 0, 0, 0.12); }
        .info-card:hover::after { transform: scaleY(1); }
        .icon-wrapper { width: 60px; height: 60px; background: linear-gradient(135deg, #ffe8cc 0%, #ffd4a3 100%); border-radius: 16px; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
        .icon-wrapper svg { width: 32px; height: 32px; }
        .info-content h4 { font-size: 12px; text-transform: uppercase; color: #666; font-weight: 600; letter-spacing: 1px; margin-bottom: 4px; }
        .info-content .value { font-size: 24px; font-weight: 700; color: #ff6600; line-height: 1.2; }
        .info-content .sub-value { font-size: 14px; color: #999; margin-top: 2px; }
        .specs-section { background: #FFC107; border: 3px solid #000; border-radius: 20px; padding: 30px; margin-bottom: 40px; box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1); }
        .specs-header { display: flex; align-items: center; justify-content: center; gap: 15px; margin-bottom: 25px; }
        .specs-header h2 { font-size: clamp(20px, 3vw, 28px); color: #000; font-weight: 800; text-transform: uppercase; }
        .specs-table { background: white; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1); }
        .specs-table table { width: 100%; border-collapse: collapse; }
        .specs-table th { background: #000; color: #FFC107; padding: 15px 20px; text-align: left; font-weight: 700; font-size: 14px; text-transform: uppercase; letter-spacing: 1px; }
        .specs-table td { padding: 15px 20px; border-bottom: 1px solid #f0f0f0; }
        .specs-table tr:nth-child(even) { background: #f9f9f9; }
        .specs-table tr:last-child td { border-bottom: none; }
        .spec-label { font-weight: 600; color: #D32F2F; display: flex; align-items: center; gap: 10px; }
        .spec-value { font-weight: 600; color: #333; }
        .feature-badges { display: flex; flex-direction: column; gap: 15px; margin: 40px 0; }
        .feature-badge { background: linear-gradient(135deg, #2196f3 0%, #1976d2 100%); color: white; padding: 20px 25px; border-radius: 12px; display: flex; align-items: center; gap: 15px; box-shadow: 0 5px 20px rgba(33, 150, 243, 0.3); transition: transform 0.3s ease; }
        .feature-badge:hover { transform: translateX(10px); }
        .feature-badge.green { background: linear-gradient(135deg, #4caf50 0%, #388e3c 100%); box-shadow: 0 5px 20px rgba(76, 175, 80, 0.3); }
        .feature-badge svg { width: 24px; height: 24px; flex-shrink: 0; }
        .feature-badge span { font-size: 18px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px; }
        .speech-section { background: white; border-radius: 16px; padding: 30px; margin: 20px 0; box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08); border-left: 5px solid #FFC107; position: relative; overflow: hidden; }
        .speech-section::before { content: ''; position: absolute; top: -50px; right: -50px; width: 100px; height: 100px; background: radial-gradient(circle, rgba(255, 193, 7, 0.1) 0%, transparent 70%); border-radius: 50%; }
        .speech-header { display: flex; align-items: center; gap: 15px; margin-bottom: 20px; }
        .speech-icon { width: 50px; height: 50px; background: linear-gradient(135deg, #ffe8cc 0%, #ffd4a3 100%); border-radius: 12px; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
        .speech-section h3 { color: #D32F2F; font-size: 22px; font-weight: 700; text-transform: uppercase; flex: 1; }
        .speech-section p { font-size: 16px; line-height: 1.8; color: #555; }
        .speech-section ul { list-style: none; padding: 0; }
        .speech-section li { padding: 8px 0; padding-left: 30px; position: relative; color: #555; }
        .speech-section li::before { content: '✓'; position: absolute; left: 0; color: #4caf50; font-weight: bold; font-size: 18px; }
        .benefits-section { margin: 50px 0; }
        .benefits-header { text-align: center; margin-bottom: 40px; }
        .benefits-header h3 { font-size: clamp(24px, 4vw, 32px); color: #333; font-weight: 800; text-transform: uppercase; margin-bottom: 10px; }
        .benefits-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 25px; }
        .benefit-card { background: white; border-radius: 16px; padding: 30px 25px; text-align: center; box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08); border-top: 4px solid #ff6600; transition: all 0.3s ease; position: relative; }
        .benefit-card:hover { transform: translateY(-10px); box-shadow: 0 10px 40px rgba(0, 0, 0, 0.15); }
        .benefit-icon { width: 70px; height: 70px; background: linear-gradient(135deg, #ffe8cc 0%, #ffd4a3 100%); border-radius: 50%; display: flex; align-items: center; justify-content: center; margin: 0 auto 20px; position: relative; }
        .benefit-icon::after { content: ''; position: absolute; width: 100%; height: 100%; background: inherit; border-radius: 50%; opacity: 0.3; animation: ripple 2s ease-out infinite; }
        @keyframes ripple { 0% { transform: scale(1); opacity: 0.3; } 100% { transform: scale(1.3); opacity: 0; } }
        .benefit-icon svg { width: 35px; height: 35px; position: relative; z-index: 1; }
        .benefit-card h4 { font-size: 18px; color: #333; font-weight: 700; margin-bottom: 10px; text-transform: uppercase; }
        .benefit-card p { font-size: 14px; color: #666; line-height: 1.6; }
        .cta-section { background: linear-gradient(135deg, #000 0%, #333 100%); border-radius: 20px; padding: 50px 30px; text-align: center; margin: 50px 0; box-shadow: 0 15px 40px rgba(0, 0, 0, 0.3); position: relative; overflow: hidden; }
        .cta-section::before { content: ''; position: absolute; top: -50%; left: -50%; width: 200%; height: 200%; background: radial-gradient(circle, rgba(255, 193, 7, 0.1) 0%, transparent 70%); animation: rotate 10s linear infinite; }
        @keyframes rotate { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
        .cta-section h3 { color: #FFC107; font-size: clamp(24px, 4vw, 32px); font-weight: 800; text-transform: uppercase; margin-bottom: 15px; position: relative; z-index: 1; }
        .cta-section p { color: rgba(255, 255, 255, 0.9); font-size: 18px; margin-bottom: 35px; position: relative; z-index: 1; }
        .cta-buttons { display: flex; flex-wrap: wrap; gap: 20px; justify-content: center; position: relative; z-index: 1; }
        .cta-button { display: inline-flex; align-items: center; gap: 12px; padding: 18px 35px; border-radius: 50px; text-decoration: none; font-weight: 700; font-size: 16px; text-transform: uppercase; letter-spacing: 0.5px; transition: all 0.3s ease; position: relative; overflow: hidden; }
        .cta-button::before { content: ''; position: absolute; top: 50%; left: 50%; width: 0; height: 0; background: rgba(255, 255, 255, 0.2); border-radius: 50%; transform: translate(-50%, -50%); transition: width 0.6s, height 0.6s; }
        .cta-button:hover::before { width: 300px; height: 300px; }
        .cta-button.whatsapp { background: linear-gradient(135deg, #25d366 0%, #20ba5a 100%); color: white; box-shadow: 0 5px 20px rgba(37, 211, 102, 0.4); }
        .cta-button.whatsapp:hover { transform: translateY(-3px); box-shadow: 0 8px 30px rgba(37, 211, 102, 0.5); }
        .cta-button.pdf { background: linear-gradient(135deg, #FFC107 0%, #ffb300 100%); color: #000; box-shadow: 0 5px 20px rgba(255, 193, 7, 0.4); }
        .cta-button.pdf:hover { transform: translateY(-3px); box-shadow: 0 8px 30px rgba(255, 193, 7, 0.5); }
        .cta-button.email { background: linear-gradient(135deg, #D32F2F 0%, #c62828 100%); color: white; box-shadow: 0 5px 20px rgba(211, 47, 47, 0.4); }
        .cta-button.email:hover { transform: translateY(-3px); box-shadow: 0 8px 30px rgba(211, 47, 47, 0.5); }
        .cta-button svg { width: 24px; height: 24px; position: relative; z-index: 1; }
        .cta-button span { position: relative; z-index: 1; }
        .contact-footer { background: white; border-radius: 16px; padding: 40px 30px; box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08); text-align: center; }
        .contact-footer h4 { font-size: 24px; color: #333; font-weight: 700; margin-bottom: 30px; text-transform: uppercase; }
        .contact-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 30px; max-width: 800px; margin: 0 auto; }
        .contact-item { display: flex; flex-direction: column; align-items: center; gap: 10px; }
        .contact-icon { width: 50px; height: 50px; background: linear-gradient(135deg, #ffe8cc 0%, #ffd4a3 100%); border-radius: 12px; display: flex; align-items: center; justify-content: center; }
        .contact-icon svg { width: 24px; height: 24px; }
        .contact-info { text-align: center; }
        .contact-info .label { font-size: 12px; color: #666; text-transform: uppercase; letter-spacing: 0.5px; }
        .contact-info a { color: #ff6600; text-decoration: none; font-weight: 600; font-size: 16px; transition: color 0.3s ease; }
        .contact-info a:hover { color: #ff8844; }
        @media (max-width: 768px) { .container { padding: 15px; } .hero-header { padding: 30px 20px; } .info-cards { grid-template-columns: 1fr; gap: 15px; } .specs-section { padding: 20px; } .specs-table { overflow-x: auto; } .specs-table table { min-width: 500px; } .cta-buttons { flex-direction: column; align-items: stretch; } .cta-button { justify-content: center; } .benefits-grid { grid-template-columns: 1fr; } .contact-grid { grid-template-columns: 1fr; } }
        @keyframes fadeInUp { from { opacity: 0; transform: translateY(30px); } to { opacity: 1; transform: translateY(0); } }
        .animate-fade-in { animation: fadeInUp 0.6s ease-out; }
    </style>
</head>
<body>
    <div class="container">
        <div class="hero-header animate-fade-in"><h1>{{product_data[modelo]}}</h1><p>{{product_data[nombre]}}</p></div>
        <div class="info-cards">
            <div class="info-card"><div class="icon-wrapper"><svg viewBox="0 0 24 24" fill="#ff6600"><path d="M7 2v11h3v9l7-12h-4l4-8z"/></svg></div><div class="info-content"><h4>POTENCIA</h4><div class="value">{{product_data[potencia_kva]}} KVA</div><div class="sub-value">{{product_data[potencia_kw]}} W</div></div></div>
            <div class="info-card"><div class="icon-wrapper"><svg viewBox="0 0 24 24" fill="#ff6600"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 18c-4.42 0-8-3.58-8-8s3.58-8 8-8 8 3.58 8 8-3.58 8-8 8z"/><circle cx="12" cy="12" r="5" fill="#ff6600"/></svg></div><div class="info-content"><h4>MOTOR</h4><div class="value" style="font-size: 20px;">{{product_data[motor]}}</div><div class="sub-value">{{product_data[cilindrada]}}cc - {{product_data[cilindros]}} Cilindros</div></div></div>
            <div class="info-card"><div class="icon-wrapper"><svg viewBox="0 0 24 24" fill="#1976d2"><path d="M13.5.67s.74 2.65.74 4.8c0 2.06-1.35 3.73-3.41 3.73-2.07 0-3.63-1.67-3.63-3.73l.03-.36C5.21 7.51 4 10.62 4 14c0 4.42 3.58 8 8 8s8-3.58 8-8C20 8.61 17.41 3.8 13.5.67z"/></svg></div><div class="info-content"><h4>COMBUSTIBLE</h4><div class="value" style="font-size: 20px;">{{product_data[combustible]}}</div><div class="sub-value"></div></div></div>
        </div>
        <div class="specs-section"><div class="specs-header"><svg width="30" height="30" viewBox="0 0 24 24" fill="#000"><path d="M9 17H7v-7h2m4 7h-2V7h2m4 10h-2v-4h2m4 4h-2V4h2v13z"/></svg><h2>ESPECIFICACIONES TÉCNICAS COMPLETAS</h2></div><div class="specs-table"><table><thead><tr><th style="width: 40%;">CARACTERÍSTICA</th><th>ESPECIFICACIÓN</th></tr></thead><tbody>
        <tr><td class="spec-label"><svg width="20" height="20" viewBox="0 0 24 24" fill="#D32F2F"><path d="M7 2v11h3v9l7-12h-4l4-8z"/></svg>POTENCIA STANDBY</td><td class="spec-value">{{product_data[potencia_kva]}} KVA / {{product_data[potencia_kw]}} W</td></tr>
        <tr><td class="spec-label"><svg width="20" height="20" viewBox="0 0 24 24" fill="#D32F2F"><path d="M11 15h2v2h-2zm0-8h2v6h-2zm1-5C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2z"/></svg>VOLTAJE</td><td class="spec-value">{{product_data[voltaje]}} V</td></tr>
        <tr><td class="spec-label"><svg width="20" height="20" viewBox="0 0 24 24" fill="#D32F2F"><path d="M16 6l-4 4-4-4v3l4 4 4-4zm0 6l-4 4-4-4v3l4 4 4-4z"/></svg>FRECUENCIA</td><td class="spec-value">{{product_data[frecuencia]}} Hz</td></tr>
        <tr><td class="spec-label"><svg width="20" height="20" viewBox="0 0 24 24" fill="#D32F2F"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 18c-4.42 0-8-3.58-8-8s3.58-8 8-8 8 3.58 8 8-3.58 8-8 8z"/></svg>MOTOR</td><td class="spec-value">{{product_data[motor]}}</td></tr>
        <tr><td class="spec-label"><svg width="20" height="20" viewBox="0 0 24 24" fill="#D32F2F"><path d="M17 3H7c-1.1 0-1.99.9-1.99 2L5 21l7-3 7 3V5c0-1.1-.9-2-2-2z"/></svg>CILINDRADA</td><td class="spec-value">{{product_data[cilindrada]}} cm³</td></tr>
        <tr><td class="spec-label"><svg width="20" height="20" viewBox="0 0 24 24" fill="#D32F2F"><path d="M19.77 7.23l.01-.01-3.72-3.72L15 4.56l2.11 2.11c-.94.36-1.61 1.26-1.61 2.33 0 1.38 1.12 2.5 2.5 2.5.36 0 .69-.08 1-.21v7.21c0 .55-.45 1-1 1s-1-.45-1-1V14c0-1.1-.9-2-2-2h-1V5c0-1.1-.9-2-2-2H6c-1.1 0-2 .9-2 2v16h10v-7.5h1.5v5c0 1.38 1.12 2.5 2.5 2.5s2.5-1.12 2.5-2.5V9c0-.69-.28-1.32-.73-1.77z"/></svg>CONSUMO</td><td class="spec-value">{{product_data[consumo]}} L/h</td></tr>
        <tr><td class="spec-label"><svg width="20" height="20" viewBox="0 0 24 24" fill="#D32F2F"><path d="M3 9v6h4l5 5V4L7 9H3zm13.5 3c0-1.77-1-3.29-2.5-4.03v8.05c1.5-.73 2.5-2.25 2.5-4.02zM14 3.23v2.06c2.89.86 5 3.54 5 6.71s-2.11 5.85-5 6.71v2.06c4.01-.91 7-4.49 7-8.77s-2.99-7.86-7-8.77z"/></svg>NIVEL SONORO</td><td class="spec-value">{{product_data[ruido]}} dBA @ 7 metros</td></tr>
        <tr><td class="spec-label"><svg width="20" height="20" viewBox="0 0 24 24" fill="#D32F2F"><path d="M21 3H3c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h18c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm0 16H3V5h18v14z"/></svg>DIMENSIONES</td><td class="spec-value">{{product_data[largo]}} x {{product_data[ancho]}} x {{product_data[alto]}} mm</td></tr>
        <tr><td class="spec-label"><svg width="20" height="20" viewBox="0 0 24 24" fill="#D32F2F"><path d="M12 3c-1.27 0-2.4.8-2.82 2H3v2h1.95l2 7c.17.59.71 1 1.32 1H15.73c.61 0 1.15-.41 1.32-1l2-7H21V5h-6.18C14.4 3.8 13.27 3 12 3zm0 2c.55 0 1 .45 1 1s-.45 1-1 1-1-.45-1-1 .45-1 1-1zm-3.73 8l-1.43-5h10.32l-1.43 5H8.27z"/></svg>PESO</td><td class="spec-value">{{product_data[peso]}} kg</td></tr>
        </tbody></table></div></div>
        <div class="feature-badges"><div class="feature-badge"><svg viewBox="0 0 24 24" fill="white"><path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z"/></svg><span>TABLERO DE TRANSFERENCIA AUTOMÁTICA INCLUIDO</span></div><div class="feature-badge green"><svg viewBox="0 0 24 24" fill="white"><path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z"/></svg><span>CABINA INSONORIZADA DE ALUMINIO</span></div></div>
        <div class="speech-section"><div class="speech-header"><div class="speech-icon"><svg viewBox="0 0 24 24" fill="#ff6600"><path d="M7 2v11h3v9l7-12h-4l4-8z"/></svg></div><h3>POTENCIA Y RENDIMIENTO SUPERIOR</h3></div><p>Este generador con una potencia de {{product_data[potencia_kva]}} KVA garantiza el desempeño excepcional gracias a su robusto motor {{product_data[motor]}}. Su diseño optimizado integra una entrega de energía confiable y constante, incluso bajo las condiciones más exigentes.</p></div>
        <div class="speech-section"><div class="speech-header"><div class="speech-icon"><svg viewBox="0 0 24 24" fill="#ff6600"><path d="M11.8 10.9c-2.27-.59-3-1.2-3-2.15 0-1.09 1.01-1.85 2.7-1.85 1.78 0 2.44.85 2.5 2.1h2.21c-.07-1.72-1.12-3.3-3.21-3.81V3h-3v2.16c-1.94.42-3.5 1.68-3.5 3.61 0 2.31 1.91 3.46 4.7 4.13 2.5.6 3 1.48 3 2.41 0 .69-.49 1.79-2.7 1.79-2.06 0-2.87-.92-2.98-2.1h-2.2c.12 2.19 1.76 3.42 3.68 3.83V21h3v-2.15c1.95-.37 3.5-1.5 3.5-3.55 0-2.84-2.43-3.81-4.7-4.4z"/></svg></div><h3>ECONOMÍA OPERATIVA GARANTIZADA</h3></div><p>Minimice sus costos operativos con un consumo de combustible tan solo {{product_data[consumo]}} L/h. Su tanque de {{product_data[tanque]}} L proporciona una autonomía considerable, reduciendo la frecuencia de repostaje y maximizando la eficiencia de su operación.</p></div>
        <div class="cta-section"><h3>TOME ACCIÓN AHORA</h3><p>No pierda esta oportunidad. Consulte con nuestros especialistas hoy mismo.</p><div class="cta-buttons"><a href="https://wa.me/{{contact_config[whatsapp]}}?text=Hola,%20vengo%20de%20ver%20el%20{{product_data[modelo]}}%20en%20la%20tienda%20de%20Stelorder%20y%20quisiera%20mas%20informacion%20sobre%20este%20producto" class="cta-button whatsapp"><svg viewBox="0 0 24 24" fill="white"><path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413Z"/></svg><span>CONSULTAR POR WHATSAPP</span></a><a href="{{product_data[pdf_url]}}" class="cta-button pdf"><svg viewBox="0 0 24 24" fill="#000"><path d="M20 2H8c-1.1 0-2 .9-2 2v12c0 1.1.9 2 2 2h12c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2zm-8.5 7.5c0 .83-.67 1.5-1.5 1.5H9v2H7.5V7H10c.83 0 1.5.67 1.5 1.5v1zm5 2c0 .83-.67 1.5-1.5 1.5h-2.5V7H15c.83 0 1.5.67 1.5 1.5v3zm4-3H19v1h1.5V11H19v2h-1.5V7h3v1.5zM9 9.5h1v-1H9v1zM4 6H2v14c0 1.1.9 2 2 2h14v-2H4V6zm10 5.5h1v-3h-1v3z"/></svg><span>DESCARGAR FICHA TÉCNICA</span></a><a href="mailto:{{contact_config[email]}}?subject=Consulta%20desde%20Stelorder%20-%20{{product_data[modelo]}}&body=Hola,%0A%0AVengo%20de%20ver%20el%20{{product_data[modelo]}}%20en%20la%20tienda%20de%20Stelorder%20y%20quisiera%20mas%20informacion%20sobre%20este%20producto.%0A%0AQuedo%20a%20la%20espera%20de%20su%20respuesta.%0A%0ASaludos" class="cta-button email"><svg viewBox="0 0 24 24" fill="white"><path d="M20 4H4c-1.1 0-1.99.9-1.99 2L2 18c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V6c0-1.1-.9-2-2-2zm0 4l-8 5-8-5V6l8 5 8-5v2z"/></svg><span>SOLICITAR COTIZACIÓN</span></a></div></div>
    </div>
</body>
</html>
            """

            system_message = f"""
Eres un experto en redacción de marketing que genera descripciones de productos en formato HTML.
Tu tarea es tomar un prompt del usuario, una plantilla HTML y los datos de un producto para generar una descripción HTML final.

1.  **Analiza el prompt del usuario:** Entiende las instrucciones específicas sobre tono, estilo y contenido.
2.  **Usa la plantilla HTML:** La plantilla ya tiene la estructura y los estilos. No la cambies, solo rellénala.
3.  **Rellena los datos:** Usa los datos del producto para rellenar los placeholders (ej: {{{{product_data[nombre]}}}}).
4.  **Adapta el contenido:** Adapta los textos (párrafos, beneficios, etc.) para que coincidan con el producto y el tono solicitado en el prompt.

**PLANTILLA HTML BASE:**
```html
{html_template}
```
"""
            
            full_context = {
                "product_data": product_info,
                "contact_config": config
            }
            
            user_message = f"""
            **PROMPT DEL USUARIO:**
            {prompt_template}

            **DATOS DEL PRODUCTO (JSON):**
            {json.dumps(full_context, indent=2, ensure_ascii=False)}

            Por favor, genera el código HTML final basándote en la plantilla, el prompt y los datos.
            """

            response = self.model.generate_content([system_message, user_message])
            html_content = response.text.strip()

            # Limpiar si el modelo devuelve el resultado en un bloque de código
            if html_content.startswith("```html"):
                html_content = html_content[7:]
            if html_content.endswith("```"):
                html_content = html_content[:-3]

            # Asegurar que el HTML esté bien formateado
            if not html_content.strip().startswith('<'):
                # Si no es HTML, envolverlo en un div para que sea visible
                html_content = f"<div class='descripcion-generada' style='white-space: pre-wrap; font-family: monospace;'>{html_content}</div>"
            
            return html_content
            
        except Exception as e:
            print(f"Error generando con prompt personalizado: {e}")
            # Fallback a un mensaje de error visible en la vista previa
            return f"<div class='error-preview'><h3>Error al generar la descripción</h3><p>{e}</p></div>"

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
