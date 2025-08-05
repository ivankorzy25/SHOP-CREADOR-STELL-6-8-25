# -*- coding: utf-8 -*-
"""
Módulo para la generación de descripciones HTML premium de productos.
Versión 2.1 - Adaptado a la nueva plantilla, con extracción de datos por IA y más íconos.
"""
import re
import requests
import PyPDF2
import io
import fitz  # PyMuPDF
import json
from pathlib import Path
import unicodedata
from .premium_generator_v2 import (
    generar_titulo_producto,
    generar_subtitulo_producto,
    generar_hero_section_inline,
    generar_info_cards_inline_mejorado,
    generar_specs_table_inline,
    generar_badges_caracteristicas,
    generar_content_sections_inline,
    generar_benefits_section_inline,
    generar_cta_section_inline,
    generar_contact_footer_inline,
    generar_css_hover_effects
)

# ============================================================================
# FUNCIONES DE LIMPIEZA DE TEXTO
# ============================================================================
def eliminar_tildes_y_especiales(texto):
    """Elimina tildes y caracteres especiales del texto."""
    if not texto:
        return texto
    
    # Convertir a string si no lo es
    texto = str(texto)
    
    # Normalizar y remover tildes
    texto_sin_tildes = ''.join(
        c for c in unicodedata.normalize('NFD', texto)
        if unicodedata.category(c) != 'Mn'
    )
    
    # Reemplazar caracteres especiales comunes
    reemplazos = {
        'ñ': 'n',
        'Ñ': 'N',
        '°': ' grados',
        '€': 'EUR',
        '£': 'GBP',
        '¥': 'JPY',
        '¢': 'centavos',
        '©': '(c)',
        '®': '(r)',
        '™': '(tm)',
        '¿': '',
        '¡': '',
        '«': '"',
        '»': '"',
        '—': '-',
        '–': '-',
        ''': "'",
        ''': "'",
        '"': '"',
        '"': '"',
        '…': '...',
        '•': '',
        '·': '',
        '§': 'seccion',
        '¶': 'parrafo',
    }
    
    for char_especial, reemplazo in reemplazos.items():
        texto_sin_tildes = texto_sin_tildes.replace(char_especial, reemplazo)
    
    # Remover cualquier otro carácter no ASCII que quede
    texto_limpio = ''.join(char if ord(char) < 128 else ' ' for char in texto_sin_tildes)
    
    # Limpiar espacios múltiples
    texto_limpio = ' '.join(texto_limpio.split())
    
    return texto_limpio

# ============================================================================
# ICONOS SVG COMPLETOS (SET ORIGINAL + NUEVOS ICONOS PARA LISTAS)
# ============================================================================
ICONOS_SVG = {
    # Iconos principales de la UI
    'potencia': '<svg width="28" height="28" viewBox="0 0 24 24" fill="#ff6600"><path d="M7 2v11h3v9l7-12h-4l4-8z"/></svg>',
    'motor': '<svg width="28" height="28" viewBox="0 0 24 24" fill="#ff6600"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 18c-4.42 0-8-3.58-8-8s3.58-8 8-8 8 3.58 8 8-3.58 8-8 8z"/></svg>',
    'shield': '<svg width="28" height="28" viewBox="0 0 24 24" fill="#ff6600"><path d="M12 1L3 5v6c0 5.55 3.84 10.74 9 12 5.16-1.26 9-6.45 9-12V5l-9-4z"/></svg>',
    'tools': '<svg width="28" height="28" viewBox="0 0 24 24" fill="#ff6600"><path d="M22.7 19l-9.1-9.1c.9-2.3.4-5-1.5-6.9-2-2-5-2.4-7.4-1.3L9 6 6 9 1.6 4.7C.4 7.1.9 10.1 2.9 12.1c1.9 1.9 4.6 2.4 6.9 1.5l9.1 9.1c.4.4 1 .4 1.4 0l2.3-2.3c.5-.4.5-1.1.1-1.4z"/></svg>',
    'specs': '<svg width="30" height="30" viewBox="0 0 24 24" fill="#000"><path d="M9 17H7v-7h2m4 7h-2V7h2m4 10h-2v-4h2m4 4h-2V4h2v13z"/></svg>',
}

# ============================================================================
# FUNCIONES AUXILIARES (Extracción y Validación de Datos)
# ============================================================================
def extraer_info_tecnica(row):
    """Extrae y normaliza la información técnica de una fila de datos de la BD."""
    info = {
        'nombre': row.get('Descripción', 'Producto sin nombre'),
        'marca': row.get('Marca', 'N/D'),
        'modelo': row.get('Modelo', 'N/D'),
        'familia': row.get('Familia', ''),
        'potencia_kva': row.get('Potencia', 'N/D'),
        'voltaje': row.get('Tensión', 'N/D'),
        'motor': row.get('Motor', 'N/D'),
        'peso': row.get('Peso_(kg)', 'N/D'),
        'pdf_url': row.get('URL_PDF', '')
    }
    return info

def extraer_texto_pdf(pdf_url, print_callback=print):
    """Extrae texto de un PDF desde una URL."""
    try:
        response = requests.get(pdf_url, timeout=10)
        response.raise_for_status()
        
        with fitz.open(stream=response.content, filetype="pdf") as doc:
            texto_completo = ""
            for page in doc:
                texto_completo += page.get_text()
        
        if texto_completo.strip():
            print_callback(f"[OK] Texto extraído correctamente de {pdf_url}")
            return texto_completo
        else:
            print_callback(f"[WARN] El PDF en {pdf_url} parece estar vacío o ser una imagen.")
            return None

    except requests.exceptions.RequestException as e:
        print_callback(f"[ERROR] Error al descargar el PDF desde {pdf_url}: {e}")
        return None
    except Exception as e:
        print_callback(f"[ERROR] Error al procesar el PDF desde {pdf_url}: {e}")
        return None

def validar_caracteristicas_producto(info, texto_pdf):
    """Detecta características especiales del producto."""
    caracteristicas = {
        'tiene_tta': False,
        'tiene_cabina': False,
        'es_inverter': False,
        'tipo_combustible': 'diesel' # Por defecto
    }
    
    texto_busqueda = f"{info.get('nombre', '')} {info.get('familia', '')}".lower()
    if texto_pdf:
        texto_busqueda += " " + texto_pdf.lower()

    special_features = info.get('caracteristicas_especiales', [])
    if any('tta' in feature.lower() for feature in special_features):
        caracteristicas['tiene_tta'] = True
    if any('cabinado' in feature.lower() or 'insonorizado' in feature.lower() for feature in special_features):
        caracteristicas['tiene_cabina'] = True
    if any('inverter' in feature.lower() for feature in special_features):
        caracteristicas['es_inverter'] = True

    if not caracteristicas['tiene_tta'] and any(keyword in texto_busqueda for keyword in ['tta', 'transferencia automatica', 'ats']):
        caracteristicas['tiene_tta'] = True
    if not caracteristicas['tiene_cabina'] and any(keyword in texto_busqueda for keyword in ['cabinado', 'insonorizado', 'soundproof', 'silent']):
        caracteristicas['tiene_cabina'] = True
    if not caracteristicas['es_inverter'] and 'inverter' in texto_busqueda:
        caracteristicas['es_inverter'] = True

    if info.get('combustible'):
        fuel = info.get('combustible').lower()
        if 'gas' in fuel:
            caracteristicas['tipo_combustible'] = 'gas'
        elif 'nafta' in fuel:
            caracteristicas['tipo_combustible'] = 'nafta'
    elif any(keyword in texto_busqueda for keyword in ['gas', 'glp', 'gnc']):
        caracteristicas['tipo_combustible'] = 'gas'
    elif 'nafta' in texto_busqueda:
        caracteristicas['tipo_combustible'] = 'nafta'
        
    return caracteristicas

def generar_descripcion_detallada_html_premium(row, config, modelo_ia=None, print_callback=print):
    """
    Función principal que orquesta la generación de la descripción HTML premium.
    """
    info_inicial = extraer_info_tecnica(row)
    info = info_inicial.copy()
    
    pdf_url = info_inicial.get('pdf_url', '')
    texto_pdf = None
    if pdf_url and str(pdf_url).lower() not in ['nan', 'none', '']:
        if not pdf_url.startswith('http'):
            pdf_url = f"https://storage.googleapis.com/fichas_tecnicas/{pdf_url}"
        texto_pdf = extraer_texto_pdf(pdf_url, print_callback)

    marketing_content = {}
    if texto_pdf and modelo_ia:
        print("🤖 Iniciando extracción y generación de contenido con IA...")
        try:
            prompt_path = Path(__file__).parent / 'templates' / 'detailed_product_prompt.json'
            with open(prompt_path, 'r', encoding='utf-8') as f:
                prompts = json.load(f)

            prompt_extract = prompts['prompt_extract'].format(
                pdf_text=texto_pdf[:4000],
                nombre=info.get('nombre'),
                familia=info.get('familia'),
                modelo=info.get('modelo'),
                marca=info.get('marca')
            )
            response_extract = modelo_ia.generate_content(prompt_extract)
            
            json_text = response_extract.text.strip().replace('```json', '').replace('```', '').strip()
            extracted_data = json.loads(json_text)
            info.update(extracted_data)
            print("[OK] Datos extraídos con IA.")

            prompt_generate = prompts['prompt_generate'].format(product_data_json=json.dumps(info, indent=2))
            response_generate = modelo_ia.generate_content(prompt_generate)
            json_text_marketing = response_generate.text.strip().replace('```json', '').replace('```', '').strip()
            marketing_content = json.loads(json_text_marketing)
            print("[OK] Contenido de marketing generado por IA.")

        except Exception as e:
            print(f"[WARN] Error en el proceso con IA, se usarán datos básicos y contenido por defecto: {e}")
            
    caracteristicas = validar_caracteristicas_producto(info, texto_pdf)
    
    if marketing_content:
        info['marketing_content'] = marketing_content
    
    titulo = generar_titulo_producto(info, caracteristicas)
    subtitulo = generar_subtitulo_producto(info, caracteristicas)
    
    html_completo = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{eliminar_tildes_y_especiales(titulo)} - Vista Previa</title>
    {generar_css_hover_effects()}
</head>
<body style="margin: 0; padding: 0; background: #f5f5f5;">
    <div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Arial, sans-serif; max-width: 1200px; margin: 0 auto; background: #ffffff; color: #333333;">
        
        {generar_hero_section_inline(titulo, subtitulo)}
        
        {generar_info_cards_inline_mejorado(info, caracteristicas)}
        
        {generar_specs_table_inline(info)}
        
        {generar_badges_caracteristicas(info, caracteristicas)}
        
        {generar_content_sections_inline(info, marketing_content)}
        
        {generar_benefits_section_inline()}
        
        {generar_cta_section_inline(info, config)}
        
        {generar_contact_footer_inline(config)}
        
    </div>
</body>
</html>"""
    
    return html_completo
