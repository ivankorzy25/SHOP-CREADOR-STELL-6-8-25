"""
GENERADOR DE DESCRIPCIONES SUPER SIMPLE
Solo ejecuta este archivo y sigue las instrucciones
"""

import streamlit as st
import google.generativeai as genai
from PIL import Image
import PyPDF2
import io
import os
from pathlib import Path

# Configuración de página
st.set_page_config(
    page_title="Generador de Descripciones",
    page_icon="🚀",
    layout="wide"
)

st.title("🚀 Generador de Descripciones de Productos")
st.markdown("### Súper simple: Sube un archivo y obtén tu descripción HTML")

# Configurar API Key
api_key = st.sidebar.text_input(
    "🔑 API Key de Google:", 
    type="password",
    help="Obtén tu API key gratis en: https://aistudio.google.com/apikey"
)

if not api_key:
    st.warning("⚠️ Por favor, ingresa tu API Key de Google en la barra lateral")
    st.stop()

# Configurar Gemini
genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-2.0-flash-exp')

# Subir archivo
st.markdown("---")
uploaded_file = st.file_uploader(
    "📁 Sube tu archivo (PDF, imagen o texto):",
    type=['pdf', 'png', 'jpg', 'jpeg', 'txt'],
    help="Arrastra o selecciona el archivo con la información del producto"
)

# Área de texto manual
texto_manual = st.text_area(
    "✏️ O pega el texto aquí:",
    height=200,
    placeholder="Ejemplo:\nGenerador Logus GL3300AM\nPotencia: 3000W\nMotor: 6.5HP\n..."
)

# Botón para generar
if st.button("🎯 GENERAR DESCRIPCIÓN", type="primary", use_container_width=True):
    
    contenido = ""
    
    # Procesar archivo subido
    if uploaded_file:
        with st.spinner("📖 Leyendo archivo..."):
            
            # PDF
            if uploaded_file.type == "application/pdf":
                pdf_reader = PyPDF2.PdfReader(uploaded_file)
                for page in pdf_reader.pages:
                    contenido += page.extract_text() + "\n"
            
            # Imagen
            elif uploaded_file.type in ["image/png", "image/jpeg", "image/jpg"]:
                image = Image.open(uploaded_file)
                st.image(image, caption="Imagen cargada", use_column_width=True)
                
                # Enviar imagen a Gemini
                response = model.generate_content([
                    "Extrae TODA la información de este producto. Lista cada especificación:",
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
        st.error("❌ Por favor sube un archivo o pega el texto")
        st.stop()
    
    # Generar descripción
    with st.spinner("🤖 Generando descripción HTML..."):
        
        prompt = f"""
        Eres un experto en crear descripciones HTML para productos industriales.
        
        DATOS DEL PRODUCTO:
        {contenido}
        
        GENERA UN HTML COMPLETO con:
        1. Título atractivo del producto
        2. Características principales en cards visuales
        3. Tabla de especificaciones técnicas
        4. Descripción detallada
        5. Aplicaciones del producto
        6. Botones de contacto WhatsApp
        
        USA ESTE FORMATO HTML:
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; }}
                .container {{ max-width: 1200px; margin: 0 auto; }}
                .header {{ background: #f8f9fa; padding: 30px; border-radius: 10px; margin-bottom: 30px; }}
                .cards {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin: 30px 0; }}
                .card {{ background: #fff; border: 1px solid #ddd; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
                .specs-table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
                .specs-table th, .specs-table td {{ padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }}
                .cta-button {{ background: #25d366; color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px; display: inline-block; margin: 10px; }}
            </style>
        </head>
        <body>
            <!-- GENERA TODO EL CONTENIDO HTML AQUÍ -->
        </body>
        </html>
        
        IMPORTANTE: Genera HTML completo y listo para usar.
        """
        
        response = model.generate_content(prompt)
        html_generado = response.text
        
        # Limpiar el HTML
        if "```html" in html_generado:
            html_generado = html_generado.split("```html")[1].split("```")[0]
        elif "```" in html_generado:
            html_generado = html_generado.split("```")[1].split("```")[0]
    
    # Mostrar resultado
    st.success("✅ ¡Descripción generada exitosamente!")
    
    # Vista previa
    st.markdown("### 👁️ Vista Previa:")
    st.components.v1.html(html_generado, height=600, scrolling=True)
    
    # Botón de descarga
    st.download_button(
        label="⬇️ DESCARGAR HTML",
        data=html_generado,
        file_name="descripcion_producto.html",
        mime="text/html",
        use_container_width=True
    )
    
    # Mostrar código HTML
    with st.expander("📄 Ver código HTML"):
        st.code(html_generado, language="html")

# Instrucciones en el sidebar
st.sidebar.markdown("---")
st.sidebar.markdown("### 📖 Instrucciones:")
st.sidebar.markdown("""
1. **Ingresa tu API Key** arriba
2. **Sube un archivo** (PDF/imagen)  
   O **pega el texto** directamente
3. **Click en GENERAR**
4. **Descarga** tu HTML

¡Así de simple! 🎉
""")

# Footer
st.markdown("---")
st.markdown("💡 **Tip:** Puedes subir fotos de catálogos, PDFs con especificaciones o simplemente pegar el texto")
