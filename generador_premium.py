"""
GENERADOR PREMIUM DE DESCRIPCIONES HTML
Versión mejorada con gráficos de alta calidad
"""

import streamlit as st
import streamlit.components.v1 as components
import google.generativeai as genai
from PIL import Image
import PyPDF2
import io
import os
from pathlib import Path
import base64

# Configuración de página
st.set_page_config(
    page_title="Generador Premium HTML",
    page_icon="🚀",
    layout="wide"
)

# CSS PERSONALIZADO PARA MEJOR UI
st.markdown("""
<style>
    .main {
        padding-top: 2rem;
    }
    .stButton > button {
        width: 100%;
        background: linear-gradient(135deg, #ff6600 0%, #ff8533 100%);
        color: white;
        font-weight: bold;
        border: none;
        padding: 1rem;
        border-radius: 10px;
        font-size: 1.2rem;
        transition: all 0.3s ease;
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 20px rgba(255, 102, 0, 0.4);
    }
    .success-message {
        padding: 1rem;
        background: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 8px;
        color: #155724;
    }
</style>
""", unsafe_allow_html=True)

# BIBLIOTECA DE ICONOS SVG REALES
ICONOS_SVG = {
    'lightning': '<svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor"><path d="M7 2v11h3v9l7-12h-4l4-8z"/></svg>',
    'shield': '<svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor"><path d="M12 1L3 5v6c0 5.55 3.84 10.74 9 12 5.16-1.26 9-6.45 9-12V5l-9-4z"/></svg>',
    'tools': '<svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor"><path d="M22.7 19l-9.1-9.1c.9-2.3.4-5-1.5-6.9-2-2-5-2.4-7.4-1.3L9 6 6 9 1.6 4.7C.4 7.1.9 10.1 2.9 12.1c1.9 1.9 4.6 2.4 6.9 1.5l9.1 9.1c.4.4 1 .4 1.4 0l2.3-2.3c.5-.4.5-1.1.1-1.4z"/></svg>',
    'quality': '<svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor"><path d="M9 16.2L4.8 12l-1.4 1.4L9 19 21 7l-1.4-1.4L9 16.2z"/></svg>',
    'money': '<svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1.41 16.09V20h-2.67v-1.93c-1.71-.36-3.16-1.46-3.27-3.4h1.96c.1.93.66 1.64 2.08 1.64 1.71 0 2.1-.86 2.1-1.39 0-.73-.39-1.41-2.34-1.87-2.17-.53-3.66-1.42-3.66-3.21 0-1.51 1.22-2.48 2.94-2.81V5.33h2.67v1.71c1.63.39 2.75 1.48 2.85 3.08h-1.96c-.05-.8-.45-1.61-1.78-1.61-1.2 0-1.91.62-1.91 1.39 0 .75.49 1.21 2.34 1.67 1.99.51 3.66 1.28 3.66 3.41 0 1.74-1.36 2.67-3 3.11z"/></svg>',
    'settings': '<svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor"><path d="M19.14,12.94c0.04-0.3,0.06-0.61,0.06-0.94c0-0.32-0.02-0.64-0.07-0.94l2.03-1.58c0.18-0.14,0.23-0.41,0.12-0.61 l-1.92-3.32c-0.12-0.22-0.37-0.29-0.59-0.22l-2.39,0.96c-0.5-0.38-1.03-0.7-1.62-0.94L14.4,2.81c-0.04-0.24-0.24-0.41-0.48-0.41 h-3.84c-0.24,0-0.43,0.17-0.47,0.41L9.25,5.35C8.66,5.59,8.12,5.92,7.63,6.29L5.24,5.33c-0.22-0.08-0.47,0-0.59,0.22L2.74,8.87 C2.62,9.08,2.66,9.34,2.86,9.48l2.03,1.58C4.84,11.36,4.8,11.69,4.8,12s0.02,0.64,0.07,0.94l-2.03,1.58 c-0.18,0.14-0.23,0.41-0.12,0.61l1.92,3.32c0.12,0.22,0.37,0.29,0.59,0.22l2.39-0.96c0.5,0.38,1.03,0.7,1.62,0.94l0.36,2.54 c0.05,0.24,0.24,0.41,0.48,0.41h3.84c0.24,0,0.44-0.17,0.47-0.41l0.36-2.54c0.59-0.24,1.13-0.56,1.62-0.94l2.39,0.96 c0.22,0.08,0.47,0,0.59-0.22l1.92-3.32c0.12-0.22,0.07-0.47-0.12-0.61L19.14,12.94z M12,15.6c-1.98,0-3.6-1.62-3.6-3.6 s1.62-3.6,3.6-3.6s3.6,1.62,3.6,3.6S13.98,15.6,12,15.6z"/></svg>',
    'check': '<svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor"><path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z"/></svg>',
    'fuel': '<svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor"><path d="M19.77 7.23l.01-.01-3.72-3.72L15 4.56l2.11 2.11c-.94.36-1.61 1.26-1.61 2.33 0 1.38 1.12 2.5 2.5 2.5.36 0 .69-.08 1-.21v7.21c0 .55-.45 1-1 1s-1-.45-1-1V14c0-1.1-.9-2-2-2h-1V5c0-1.1-.9-2-2-2H6c-1.1 0-2 .9-2 2v16h10v-7.5h1.5v5c0 1.38 1.12 2.5 2.5 2.5s2.5-1.12 2.5-2.5V9c0-.69-.28-1.32-.73-1.77zM12 10H6V5h6v5zm6 0c.55 0 1-.45 1-1s-.45-1-1-1-1 .45-1 1 .45 1 1 1z"/></svg>',
    'time': '<svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor"><path d="M11.99 2C6.47 2 2 6.48 2 12s4.47 10 9.99 10C17.52 22 22 17.52 22 12S17.52 2 11.99 2zM12 20c-4.42 0-8-3.58-8-8s3.58-8 8-8 8 3.58 8 8-3.58 8-8 8zm.5-13H11v6l5.25 3.15.75-1.23-4.5-2.67z"/></svg>',
    'volume': '<svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor"><path d="M3 9v6h4l5 5V4L7 9H3zm13.5 3c0-1.77-1.02-3.29-2.5-4.03v8.05c1.48-.73 2.5-2.25 2.5-4.02zM14 3.23v2.06c2.89.86 5 3.54 5 6.71s-2.11 5.85-5 6.71v2.06c4.01-.91 7-4.49 7-8.77s-2.99-7.86-7-8.77z"/></svg>',
    'weight': '<svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor"><path d="M17.66 17.66l-1.06 1.06-.71-.71 1.06-1.06-1.94-1.94-1.06 1.06-.71-.71 1.06-1.06-1.94-1.94-1.06 1.06-.71-.71 1.06-1.06L9.7 9.7l-1.06 1.06-.71-.71 1.06-1.06-1.94-1.94-1.06 1.06-.71-.71 1.06-1.06L4 4v14c0 1.1.9 2 2 2h14l-2.34-2.34zM7 17v-5.76L12.76 17H7z"/></svg>',
    'dimensions': '<svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor"><path d="M14 6l-3.75 5 2.85 3.8-1.6 1.2C9.81 13.75 7 10 7 10l-6 8h22L14 6z"/></svg>',
    'start': '<svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor"><path d="M14.59 7.41L18.17 11H6v2h12.17l-3.59 3.59L16 18l6-6-6-6-1.41 1.41zM2 6v12h2V6H2z"/></svg>',
    'efficiency': '<svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor"><path d="M3.5 18.49l6-6.01 4 4L22 6.92l-1.41-1.41-7.09 7.97-4-4L2 16.99z"/></svg>',
    'waves': '<svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor"><path d="M17 16.99c-1.35 0-2.2.42-2.95.8-.65.33-1.18.6-2.05.6-.9 0-1.4-.25-2.05-.6-.75-.38-1.57-.8-2.95-.8s-2.2.42-2.95.8c-.65.33-1.17.6-2.05.6v1.95c1.35 0 2.2-.42 2.95-.8.65-.33 1.17-.6 2.05-.6s1.4.25 2.05.6c.75.38 1.57.8 2.95.8s2.2-.42 2.95-.8c.65-.33 1.18-.6 2.05-.6.9 0 1.4.25 2.05.6.75.38 1.58.8 2.95.8v-1.95c-.9 0-1.4-.25-2.05-.6-.75-.38-1.6-.8-2.95-.8zm0-4.45c-1.35 0-2.2.42-2.95.8-.65.32-1.18.6-2.05.6-.9 0-1.4-.25-2.05-.6-.75-.38-1.57-.8-2.95-.8s-2.2.42-2.95.8c-.65.32-1.17.6-2.05.6v1.95c1.35 0 2.2-.42 2.95-.8.65-.35 1.15-.6 2.05-.6s1.4.25 2.05.6c.75.38 1.57.8 2.95.8s2.2-.42 2.95-.8c.65-.35 1.15-.6 2.05-.6s1.4.25 2.05.6c.75.38 1.58.8 2.95.8v-1.95c-.9 0-1.4-.25-2.05-.6-.75-.38-1.6-.8-2.95-.8zm2.95-8.08c-.75-.38-1.58-.8-2.95-.8s-2.2.42-2.95.8c-.65.32-1.18.6-2.05.6-.9 0-1.4-.25-2.05-.6-.75-.37-1.57-.8-2.95-.8s-2.2.42-2.95.8c-.65.33-1.17.6-2.05.6v1.93c1.35 0 2.2-.43 2.95-.8.65-.33 1.17-.6 2.05-.6s1.4.25 2.05.6c.75.38 1.57.8 2.95.8s2.2-.43 2.95-.8c.65-.32 1.18-.6 2.05-.6.9 0 1.4.25 2.05.6.75.38 1.58.8 2.95.8V5.04c-.9 0-1.4-.25-2.05-.58zM17 8.09c-1.35 0-2.2.43-2.95.8-.65.32-1.18.6-2.05.6-.9 0-1.4-.25-2.05-.6-.75-.38-1.57-.8-2.95-.8s-2.2.43-2.95.8c-.65.32-1.17.6-2.05.6v1.95c1.35 0 2.2-.43 2.95-.8.65-.35 1.15-.6 2.05-.6s1.4.25 2.05.6c.75.38 1.57.8 2.95.8s2.2-.43 2.95-.8c.65-.35 1.15-.6 2.05-.6s1.4.25 2.05.6c.75.38 1.58.8 2.95.8V9.49c-.9 0-1.4-.25-2.05-.6-.75-.38-1.6-.8-2.95-.8z"/></svg>',
    'engine': '<svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor"><path d="M7 4v2h3v2H7l-2 2v3h2v2H5v3h2v2h3v-2h10v2h3v-2h2v-3h-2v-2h2V9l-2-2h-3V5h3V3h-3c-1.1 0-2 .9-2 2v2h-6V5c0-1.1-.9-2-2-2H7zm10 5v6h-6V9h6z"/></svg>'
}

st.title("🚀 Generador Premium de Descripciones HTML")
st.markdown("### Genera descripciones profesionales con diseño de alta calidad")

# Configurar API Key
api_key = st.sidebar.text_input(
    "🔑 API Key de Google:", 
    type="password",
    help="Obtén tu API key gratis en: https://aistudio.google.com/apikey"
)

# Opciones de personalización
st.sidebar.markdown("---")
st.sidebar.markdown("### ⚙️ Personalización")
whatsapp = st.sidebar.text_input("WhatsApp:", value="541139563099")
telefono = st.sidebar.text_input("Teléfono:", value="+54 11 3956-3099")
email = st.sidebar.text_input("Email:", value="info@generadores.ar")
empresa = st.sidebar.text_input("Empresa:", value="Tu Empresa")

if not api_key:
    st.warning("⚠️ Por favor, ingresa tu API Key de Google en la barra lateral")
    st.stop()

# Configurar Gemini
genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-2.0-flash-exp')

# Función para generar HTML Premium
def generar_html_premium(contenido, config):
    # Convertir diccionario de iconos a string para el prompt
    iconos_str = str(ICONOS_SVG)
    
    prompt = f"""
    Eres un experto en crear páginas HTML premium para productos industriales.
    
    INFORMACIÓN DEL PRODUCTO:
    {contenido}
    
    CONFIGURACIÓN:
    - WhatsApp: {config['whatsapp']}
    - Teléfono: {config['telefono']}
    - Email: {config['email']}
    - Empresa: {config['empresa']}
    
    GENERA UN HTML COMPLETO Y PROFESIONAL que incluya:
    
    1. **Header Hero Impactante** con gradientes y diseño moderno
    2. **Cards de Características Principales** con iconos SVG y efectos hover
    3. **Gráfico Visual de Eficiencia** (si aplica para el producto)
    4. **Tabla de Especificaciones Completa** con diseño premium
    5. **Sección de Beneficios** con cards visuales
    6. **Call to Action Potente** con botones de WhatsApp
    7. **Footer Profesional** con información de contacto
    
    IMPORTANTE: USA ESTOS ICONOS SVG REALES (NO PLACEHOLDERS):
    
    Para icono de rayo/potencia: <svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor"><path d="M7 2v11h3v9l7-12h-4l4-8z"/></svg>
    Para icono de escudo/protección: <svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor"><path d="M12 1L3 5v6c0 5.55 3.84 10.74 9 12 5.16-1.26 9-6.45 9-12V5l-9-4z"/></svg>
    Para icono de herramientas: <svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor"><path d="M22.7 19l-9.1-9.1c.9-2.3.4-5-1.5-6.9-2-2-5-2.4-7.4-1.3L9 6 6 9 1.6 4.7C.4 7.1.9 10.1 2.9 12.1c1.9 1.9 4.6 2.4 6.9 1.5l9.1 9.1c.4.4 1 .4 1.4 0l2.3-2.3c.5-.4.5-1.1.1-1.4z"/></svg>
    Para icono de check/calidad: <svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor"><path d="M9 16.2L4.8 12l-1.4 1.4L9 19 21 7l-1.4-1.4L9 16.2z"/></svg>
    Para icono de combustible: <svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor"><path d="M19.77 7.23l.01-.01-3.72-3.72L15 4.56l2.11 2.11c-.94.36-1.61 1.26-1.61 2.33 0 1.38 1.12 2.5 2.5 2.5.36 0 .69-.08 1-.21v7.21c0 .55-.45 1-1 1s-1-.45-1-1V14c0-1.1-.9-2-2-2h-1V5c0-1.1-.9-2-2-2H6c-1.1 0-2 .9-2 2v16h10v-7.5h1.5v5c0 1.38 1.12 2.5 2.5 2.5s2.5-1.12 2.5-2.5V9c0-.69-.28-1.32-.73-1.77zM12 10H6V5h6v5zm6 0c.55 0 1-.45 1-1s-.45-1-1-1-1 .45-1 1 .45 1 1 1z"/></svg>
    Para icono de tiempo: <svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor"><path d="M11.99 2C6.47 2 2 6.48 2 12s4.47 10 9.99 10C17.52 22 22 17.52 22 12S17.52 2 11.99 2zM12 20c-4.42 0-8-3.58-8-8s3.58-8 8-8 8 3.58 8 8-3.58 8-8 8zm.5-13H11v6l5.25 3.15.75-1.23-4.5-2.67z"/></svg>
    Para icono de motor: <svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor"><path d="M7 4v2h3v2H7l-2 2v3h2v2H5v3h2v2h3v-2h10v2h3v-2h2v-3h-2v-2h2V9l-2-2h-3V5h3V3h-3c-1.1 0-2 .9-2 2v2h-6V5c0-1.1-.9-2-2-2H7zm10 5v6h-6V9h6z"/></svg>
    
    USA ESTA ESTRUCTURA HTML:
    
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>[TÍTULO DEL PRODUCTO]</title>
        <style>
            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }}
            
            body {{
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Arial, sans-serif;
                line-height: 1.6;
                color: #333;
                background: #f5f5f5;
            }}
            
            .container {{
                max-width: 1200px;
                margin: 0 auto;
                background: white;
                box-shadow: 0 0 20px rgba(0,0,0,0.1);
            }}
            
            /* Header Hero */
            .hero {{
                background: linear-gradient(135deg, #ff6600 0%, #ff8533 100%);
                color: white;
                padding: 60px 30px;
                text-align: center;
                position: relative;
                overflow: hidden;
            }}
            
            .hero::before {{
                content: '';
                position: absolute;
                top: -50%;
                right: -50%;
                width: 200%;
                height: 200%;
                background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%);
                animation: pulse 3s ease-in-out infinite;
            }}
            
            @keyframes pulse {{
                0%, 100% {{ transform: scale(1); opacity: 0.5; }}
                50% {{ transform: scale(1.1); opacity: 0.3; }}
            }}
            
            .hero h1 {{
                font-size: 2.5rem;
                font-weight: 800;
                margin-bottom: 20px;
                position: relative;
                z-index: 1;
                text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
            }}
            
            .hero p {{
                font-size: 1.3rem;
                opacity: 0.95;
                position: relative;
                z-index: 1;
            }}
            
            /* Feature Cards */
            .features {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
                gap: 25px;
                padding: 40px 30px;
            }}
            
            .feature-card {{
                background: #f8f9fa;
                border-radius: 12px;
                padding: 30px;
                border-left: 4px solid #ff6600;
                box-shadow: 0 2px 10px rgba(0,0,0,0.08);
                transition: all 0.3s ease;
                position: relative;
                overflow: hidden;
            }}
            
            .feature-card:hover {{
                transform: translateY(-5px);
                box-shadow: 0 8px 25px rgba(0,0,0,0.15);
            }}
            
            .feature-card::after {{
                content: '';
                position: absolute;
                top: -50px;
                right: -50px;
                width: 100px;
                height: 100px;
                background: rgba(255,102,0,0.1);
                border-radius: 50%;
                transition: all 0.3s ease;
            }}
            
            .feature-card:hover::after {{
                transform: scale(1.5);
            }}
            
            .feature-icon {{
                width: 50px;
                height: 50px;
                background: #fff3e0;
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                margin-bottom: 20px;
                transition: all 0.3s ease;
            }}
            
            .feature-card:hover .feature-icon {{
                background: #ff6600;
                transform: rotate(15deg) scale(1.1);
            }}
            
            .feature-card:hover .feature-icon svg {{
                fill: white;
            }}
            
            .feature-icon svg {{
                width: 28px;
                height: 28px;
                fill: #ff6600;
                transition: all 0.3s ease;
            }}
            
            .feature-title {{
                font-size: 0.9rem;
                color: #666;
                text-transform: uppercase;
                letter-spacing: 0.5px;
                margin-bottom: 5px;
            }}
            
            .feature-value {{
                font-size: 1.8rem;
                font-weight: 700;
                color: #ff6600;
            }}
            
            /* Efficiency Graph */
            .efficiency-graph {{
                background: #f5f5f5;
                border-radius: 12px;
                padding: 20px;
                margin: 20px 30px;
            }}
            
            .efficiency-bar {{
                background: linear-gradient(to right, #4CAF50 0%, #8BC34A 25%, #FFC107 50%, #FF9800 75%, #F44336 100%);
                height: 10px;
                border-radius: 5px;
                position: relative;
                margin: 15px 0;
            }}
            
            .efficiency-indicator {{
                position: absolute;
                top: -8px;
                width: 26px;
                height: 26px;
                background: #FFC107;
                border: 3px solid white;
                border-radius: 50%;
                box-shadow: 0 2px 5px rgba(0,0,0,0.2);
                transition: all 0.3s ease;
            }}
            
            /* Specs Table */
            .specs-section {{
                padding: 40px 30px;
                margin: 40px 0;
            }}
            
            .specs-table {{
                background: white;
                border-radius: 12px;
                overflow: hidden;
                box-shadow: 0 2px 10px rgba(0,0,0,0.05);
            }}
            
            .specs-table table {{
                width: 100%;
                border-collapse: collapse;
            }}
            
            .specs-table th {{
                background: #333;
                color: white;
                padding: 15px 20px;
                text-align: left;
                font-weight: 600;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }}
            
            .specs-table td {{
                padding: 15px 20px;
                border-bottom: 1px solid #eee;
            }}
            
            .specs-table tr:hover {{
                background: #fff3e0;
            }}
            
            .spec-category {{
                background: #f5f5f5;
                font-weight: 600;
                color: #666;
                text-transform: uppercase;
                font-size: 0.85rem;
                letter-spacing: 1px;
            }}
            
            /* Benefits Section */
            .benefits {{
                background: #f0f0f0;
                padding: 60px 30px;
            }}
            
            .benefits h2 {{
                text-align: center;
                font-size: 2rem;
                margin-bottom: 40px;
                color: #333;
            }}
            
            .benefits-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                gap: 25px;
                max-width: 1000px;
                margin: 0 auto;
            }}
            
            .benefit-card {{
                background: white;
                border-radius: 12px;
                padding: 30px;
                text-align: center;
                box-shadow: 0 3px 10px rgba(0,0,0,0.08);
                transition: all 0.3s ease;
                position: relative;
                overflow: hidden;
            }}
            
            .benefit-card:hover {{
                transform: translateY(-8px);
                box-shadow: 0 10px 30px rgba(0,0,0,0.15);
            }}
            
            .benefit-icon {{
                width: 60px;
                height: 60px;
                margin: 0 auto 20px;
                background: #fff3e0;
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                transition: all 0.3s ease;
            }}
            
            .benefit-card:hover .benefit-icon {{
                background: #ff6600;
                transform: scale(1.1);
            }}
            
            .benefit-card:hover .benefit-icon svg {{
                fill: white;
            }}
            
            .benefit-icon svg {{
                width: 30px;
                height: 30px;
                fill: #ff6600;
                transition: all 0.3s ease;
            }}
            
            /* CTA Section */
            .cta {{
                background: linear-gradient(135deg, #ff6600 0%, #ff8533 100%);
                padding: 60px 30px;
                text-align: center;
                color: white;
                position: relative;
                overflow: hidden;
            }}
            
            .cta h2 {{
                font-size: 2.2rem;
                margin-bottom: 20px;
                position: relative;
                z-index: 1;
            }}
            
            .cta p {{
                font-size: 1.2rem;
                margin-bottom: 30px;
                opacity: 0.95;
                position: relative;
                z-index: 1;
            }}
            
            .cta-buttons {{
                display: flex;
                gap: 20px;
                justify-content: center;
                flex-wrap: wrap;
                position: relative;
                z-index: 1;
            }}
            
            .btn {{
                padding: 18px 40px;
                border-radius: 30px;
                text-decoration: none;
                font-weight: 700;
                font-size: 1.1rem;
                display: inline-flex;
                align-items: center;
                gap: 10px;
                transition: all 0.3s ease;
                box-shadow: 0 4px 15px rgba(0,0,0,0.2);
            }}
            
            .btn-primary {{
                background: white;
                color: #ff6600;
            }}
            
            .btn-primary:hover {{
                transform: translateY(-3px) scale(1.05);
                box-shadow: 0 8px 25px rgba(0,0,0,0.3);
            }}
            
            .btn-secondary {{
                background: rgba(255,255,255,0.2);
                color: white;
                border: 2px solid white;
            }}
            
            .btn-secondary:hover {{
                background: white;
                color: #ff6600;
            }}
            
            /* Footer */
            footer {{
                background: #333;
                color: white;
                padding: 40px 30px;
                text-align: center;
            }}
            
            .contact-info {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 30px;
                margin-bottom: 30px;
                max-width: 800px;
                margin-left: auto;
                margin-right: auto;
            }}
            
            .contact-item p {{
                margin: 5px 0;
            }}
            
            .contact-item a {{
                color: white;
                text-decoration: none;
                transition: all 0.3s ease;
            }}
            
            .contact-item a:hover {{
                color: #ff6600;
                transform: translateY(-2px);
                display: inline-block;
            }}
            
            /* Responsive */
            @media (max-width: 768px) {{
                .hero h1 {{
                    font-size: 2rem;
                }}
                
                .features {{
                    grid-template-columns: 1fr;
                }}
                
                .cta h2 {{
                    font-size: 1.8rem;
                }}
            }}
        </style>
    </head>
    <body>
        <div class="container">
            [GENERA TODO EL CONTENIDO HTML AQUÍ]
        </div>
    </body>
    </html>
    
    IMPORTANTE:
    1. Reemplaza [TÍTULO DEL PRODUCTO] con el título real
    2. Reemplaza [GENERA TODO EL CONTENIDO HTML AQUÍ] con todo el contenido generado
    3. USA los iconos SVG REALES proporcionados arriba, NO uses placeholders
    4. Incluye TODOS los datos del producto
    5. Asegúrate de que el diseño sea visualmente impactante
    6. Los botones de WhatsApp deben tener el número correcto con el formato: https://wa.me/{config['whatsapp']}
    7. Si el producto tiene información de consumo/eficiencia, incluye el gráfico visual
    
    Genera el HTML completo, listo para usar, con la máxima calidad visual y profesional.
    """
    
    response = model.generate_content(prompt)
    html = response.text
    
    # Limpiar el HTML
    if "```html" in html:
        html = html.split("```html")[1].split("```")[0]
    elif "```" in html:
        html = html.split("```")[1].split("```")[0]
    
    return html

# UI Principal
col1, col2 = st.columns([2, 1])

with col1:
    # Subir archivo
    uploaded_file = st.file_uploader(
        "📁 Sube tu archivo (PDF, imagen o texto):",
        type=['pdf', 'png', 'jpg', 'jpeg', 'txt'],
        help="Arrastra o selecciona el archivo con la información del producto"
    )

with col2:
    # Vista previa del archivo
    if uploaded_file:
        if uploaded_file.type in ["image/png", "image/jpeg", "image/jpg"]:
            image = Image.open(uploaded_file)
            st.image(image, caption="Vista previa", use_column_width=True)

# Área de texto manual
texto_manual = st.text_area(
    "✏️ O pega/escribe el texto aquí:",
    height=200,
    placeholder="""Ejemplo:
Generador Logus GL3300AM
Potencia: 3000W
Motor: 6.5HP Nafta
Tanque: 15L
Autonomía: 11 horas
Peso: 49kg"""
)

# Botón para generar
if st.button("🎯 GENERAR DESCRIPCIÓN PREMIUM", type="primary", use_container_width=True):
    
    contenido = ""
    
    # Procesar archivo subido
    if uploaded_file:
        with st.spinner("📖 Procesando archivo..."):
            
            # PDF
            if uploaded_file.type == "application/pdf":
                pdf_reader = PyPDF2.PdfReader(uploaded_file)
                for page in pdf_reader.pages:
                    contenido += page.extract_text() + "\n"
            
            # Imagen
            elif uploaded_file.type in ["image/png", "image/jpeg", "image/jpg"]:
                image = Image.open(uploaded_file)
                
                # Enviar imagen a Gemini
                response = model.generate_content([
                    "Extrae TODA la información técnica de este producto. Lista cada especificación con detalle:",
                    image
                ])
                contenido = response.text
            
            # Texto
            else:
                contenido = str(uploaded_file.read(), "utf-8")
    
    # Si no hay archivo, usar texto manual
    elif texto_manual:
        contenido = texto_manual
    
    else:
        st.error("❌ Por favor sube un archivo o ingresa el texto")
        st.stop()
    
    # Generar HTML Premium
    with st.spinner("🎨 Generando descripción premium..."):
        config = {
            'whatsapp': whatsapp,
            'telefono': telefono,
            'email': email,
            'empresa': empresa
        }
        
        html_generado = generar_html_premium(contenido, config)
    
    # Mostrar resultado
    st.markdown('<div class="success-message">✅ ¡Descripción premium generada exitosamente!</div>', 
                unsafe_allow_html=True)
    
    # Tabs para diferentes vistas
    tab1, tab2, tab3 = st.tabs(["👁️ Vista Previa", "📄 Código HTML", "📊 Análisis"])
    
    with tab1:
        components.html(html_generado, height=800, scrolling=True)
    
    with tab2:
        st.code(html_generado, language="html")
        
        # Botón de copiar
        st.button("📋 Copiar código", key="copy_code")
    
    with tab3:
        # Análisis del HTML generado
        st.metric("Tamaño del archivo", f"{len(html_generado) / 1024:.1f} KB")
        st.metric("Elementos interactivos", html_generado.count("hover"))
        st.metric("Iconos SVG incluidos", html_generado.count("<svg"))
    
    # Botón de descarga mejorado
    st.download_button(
        label="⬇️ DESCARGAR HTML PREMIUM",
        data=html_generado,
        file_name=f"descripcion_premium_{uploaded_file.name if uploaded_file else 'producto'}.html",
        mime="text/html",
        use_container_width=True
    )

# Instrucciones en el sidebar
st.sidebar.markdown("---")
st.sidebar.markdown("### 📖 Guía Rápida:")
st.sidebar.markdown("""
1. **Configura tu API Key** ☝️
2. **Personaliza los datos** de contacto
3. **Sube un archivo** o pega el texto
4. **Click en GENERAR** 
5. **Descarga** tu HTML premium

### 🎨 Características Premium:
- ✨ Diseño moderno y profesional
- 🎯 Iconos SVG de alta calidad
- 📊 Gráficos de eficiencia
- 🎨 Efectos hover avanzados
- 📱 100% responsive
- ⚡ Optimizado para conversión
""")

# Footer
st.markdown("---")
st.markdown("💡 **Tip Pro:** Para mejores resultados, incluye toda la información técnica disponible del producto")
