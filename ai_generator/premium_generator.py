# -*- coding: utf-8 -*-
"""
Módulo para la generación de descripciones HTML premium de productos.
"""
import re
import requests
import fitz  # PyMuPDF
import json
from pathlib import Path

# ============================================================================
# ICONOS SVG PARA EL DISEÑO PREMIUM
# ============================================================================
ICONOS_SVG = {
    'potencia': '<svg width="28" height="28" viewBox="0 0 24 24" fill="#ff6600"><path d="M7 2v11h3v9l7-12h-4l4-8z"/></svg>',
    'motor': '<svg width="28" height="28" viewBox="0 0 24 24" fill="#ff6600"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 18c-4.42 0-8-3.58-8-8s3.58-8 8-8 8 3.58 8 8-3.58 8-8 8z"/></svg>',
    'gas': '<svg width="28" height="28" viewBox="0 0 24 24" fill="#1976d2"><path d="M13.5.67s.74 2.65.74 4.8c0 2.06-1.35 3.73-3.41 3.73-2.07 0-3.63-1.67-3.63-3.73l.03-.36C5.21 7.51 4 10.62 4 14c0 4.42 3.58 8 8 8s8-3.58 8-8C20 8.61 17.41 3.8 13.5.67z"/></svg>',
    'diesel': '<svg width="28" height="28" viewBox="0 0 24 24" fill="#333"><path d="M12 2C8.13 2 5 5.13 5 9c0 1.88.79 3.56 2 4.78V22h10v-8.22c1.21-1.22 2-2.9 2-4.78 0-3.87-3.13-7-7-7zm0 2c2.76 0 5 2.24 5 5s-2.24 5-5 5-5-2.24-5-5 2.24-5 5-5z"/></svg>',
    'nafta': '<svg width="28" height="28" viewBox="0 0 24 24" fill="#f44336"><path d="M12 3c-1.1 0-2 .9-2 2v12.5c0 .83.67 1.5 1.5 1.5s1.5-.67 1.5-1.5V5c0-1.1-.9-2-2-2zm-3 4H7v11h2V7zm6 0h-2v11h2V7z"/></svg>',
    'check': '<svg width="20" height="20" viewBox="0 0 24 24" fill="white"><path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z"/></svg>',
    'shield': '<svg width="28" height="28" viewBox="0 0 24 24" fill="#ff6600"><path d="M12 1L3 5v6c0 5.55 3.84 10.74 9 12 5.16-1.26 9-6.45 9-12V5l-9-4z"/></svg>',
    'money': '<svg width="28" height="28" viewBox="0 0 24 24" fill="#ff6600"><path d="M11.8 10.9c-2.27-.59-3-1.2-3-2.15 0-1.09 1.01-1.85 2.7-1.85 1.78 0 2.44.85 2.5 2.1h2.21c-.07-1.72-1.12-3.3-3.21-3.81V3h-3v2.16c-1.94.42-3.5 1.68-3.5 3.61 0 2.31 1.91 3.46 4.7 4.13 2.5.6 3 1.48 3 2.41 0 .69-.49 1.79-2.7 1.79-2.06 0-2.87-.92-2.98-2.1h-2.2c.12 2.19 1.76 3.42 3.68 3.83V21h3v-2.15c1.95-.37 3.5-1.5 3.5-3.55 0-2.84-2.43-3.81-4.7-4.4z"/></svg>',
    'tools': '<svg width="28" height="28" viewBox="0 0 24 24" fill="#ff6600"><path d="M22.7 19l-9.1-9.1c.9-2.3.4-5-1.5-6.9-2-2-5-2.4-7.4-1.3L9 6 6 9 1.6 4.7C.4 7.1.9 10.1 2.9 12.1c1.9 1.9 4.6 2.4 6.9 1.5l9.1 9.1c.4.4 1 .4 1.4 0l2.3-2.3c.5-.4.5-1.1.1-1.4z"/></svg>',
    'quality': '<svg width="28" height="28" viewBox="0 0 24 24" fill="#4caf50"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/></svg>',
    'whatsapp': '<svg width="24" height="24" viewBox="0 0 24 24" fill="white"><path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413Z"/></svg>',
    'pdf': '<svg width="24" height="24" viewBox="0 0 24 24" fill="#000"><path d="M20 2H8c-1.1 0-2 .9-2 2v12c0 1.1.9 2 2 2h12c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2zm-8.5 7.5c0 .83-.67 1.5-1.5 1.5H9v2H7.5V7H10c.83 0 1.5.67 1.5 1.5v1zm5 2c0 .83-.67 1.5-1.5 1.5h-2.5V7H15c.83 0 1.5.67 1.5 1.5v3zm4-3H19v1h1.5V11H19v2h-1.5V7h3v1.5zM9 9.5h1v-1H9v1zM4 6H2v14c0 1.1.9 2 2 2h14v-2H4V6zm10 5.5h1v-3h-1v3z"/></svg>',
    'email': '<svg width="24" height="24" viewBox="0 0 24 24" fill="white"><path d="M20 4H4c-1.1 0-1.99.9-1.99 2L2 18c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V6c0-1.1-.9-2-2-2zm0 4l-8 5-8-5V6l8 5 8-5v2z"/></svg>',
    'phone': '<svg width="24" height="24" viewBox="0 0 24 24" fill="#ff6600"><path d="M6.62 10.79c1.44 2.83 3.76 5.14 6.59 6.59l2.2-2.2c.27-.27.67-.36 1.02-.24 1.12.37 2.33.57 3.57.57.55 0 1 .45 1 1V20c0 .55-.45 1-1 1-9.39 0-17-7.61-17-17 0-.55.45-1 1-1h3.5c.55 0 1 .45 1 1 0 1.25.2 2.45.57 3.57.11.35.03.74-.25 1.02l-2.2 2.2z"/></svg>',
    'web': '<svg width="24" height="24" viewBox="0 0 24 24" fill="#ff6600"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-1 17.93c-3.94-.49-7-3.85-7-7.93 0-.62.08-1.21.21-1.79L9 15v1c0 1.1.9 2 2 2v1.93zm6.9-2.54c-.26-.81-1-1.39-1.9-1.39h-1v-3c0-.55-.45-1-1-1H8v-2h2c.55 0 1-.45 1-1V7h2c1.1 0 2-.9 2-2v-.41c2.93 1.19 5 4.06 5 7.41 0 2.08-.8 3.97-2.1 5.39z"/></svg>',
    'frecuencia': '<svg width="20" height="20" viewBox="0 0 24 24" fill="#D32F2F"><path d="M16 6l-4 4-4-4v3l4 4 4-4zm0 6l-4 4-4-4v3l4 4 4-4z"/></svg>',
    'voltaje': '<svg width="20" height="20" viewBox="0 0 24 24" fill="#D32F2F"><path d="M11 15h2v2h-2zm0-8h2v6h-2zm1-5C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2z"/></svg>',
    'cilindrada': '<svg width="20" height="20" viewBox="0 0 24 24" fill="#D32F2F"><path d="M17 3H7c-1.1 0-1.99.9-1.99 2L5 21l7-3 7 3V5c0-1.1-.9-2-2-2z"/></svg>',
    'consumo': '<svg width="20" height="20" viewBox="0 0 24 24" fill="#D32F2F"><path d="M19.77 7.23l.01-.01-3.72-3.72L15 4.56l2.11 2.11c-.94.36-1.61 1.26-1.61 2.33 0 1.38 1.12 2.5 2.5 2.5.36 0 .69-.08 1-.21v7.21c0 .55-.45 1-1 1s-1-.45-1-1V14c0-1.1-.9-2-2-2h-1V5c0-1.1-.9-2-2-2H6c-1.1 0-2 .9-2 2v16h10v-7.5h1.5v5c0 1.38 1.12 2.5 2.5 2.5s2.5-1.12 2.5-2.5V9c0-.69-.28-1.32-.73-1.77z"/></svg>',
    'ruido': '<svg width="20" height="20" viewBox="0 0 24 24" fill="#D32F2F"><path d="M3 9v6h4l5 5V4L7 9H3zm13.5 3c0-1.77-1-3.29-2.5-4.03v8.05c1.5-.73 2.5-2.25 2.5-4.02zM14 3.23v2.06c2.89.86 5 3.54 5 6.71s-2.11 5.85-5 6.71v2.06c4.01-.91 7-4.49 7-8.77s-2.99-7.86-7-8.77z"/></svg>',
    'dimensiones': '<svg width="20" height="20" viewBox="0 0 24 24" fill="#D32F2F"><path d="M21 3H3c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h18c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm0 16H3V5h18v14z"/></svg>',
    'peso': '<svg width="20" height="20" viewBox="0 0 24 24" fill="#D32F2F"><path d="M12 3c-1.27 0-2.4.8-2.82 2H3v2h1.95l2 7c.17.59.71 1 1.32 1H15.73c.61 0 1.15-.41 1.32-1l2-7H21V5h-6.18C14.4 3.8 13.27 3 12 3zm0 2c.55 0 1 .45 1 1s-.45 1-1 1-1-.45-1-1 .45-1 1-1z"/></svg>',
    'specs': '<svg width="30" height="30" viewBox="0 0 24 24" fill="#000"><path d="M9 17H7v-7h2m4 7h-2V7h2m4 10h-2v-4h2m4 4h-2V4h2v13z"/></svg>'
}

# ============================================================================
# FUNCIONES AUXILIARES
# ============================================================================

def extraer_info_tecnica(row):
    """Extrae y normaliza la información técnica de una fila de datos de la BD."""
    info = {
        'nombre': row.get('Descripción', 'Producto sin nombre'),
        'marca': row.get('Marca', 'N/D'),
        'modelo': row.get('Modelo', 'N/D'),
        'familia': row.get('Familia', ''),
        'potencia_kva': row.get('Potencia', 'N/D'),
        'potencia_kw': '',
        'voltaje': row.get('Tensión', 'N/D'),
        'frecuencia': '50',
        'motor': row.get('Motor', 'N/D'),
        'alternador': 'N/D',
        'cilindrada': '',
        'consumo': 'N/D',
        'tanque': 'N/D',
        'ruido': 'N/D',
        'largo': '', 'ancho': '', 'alto': '',
        'peso': row.get('Peso_(kg)', 'N/D'),
        'pdf_url': row.get('URL_PDF', '')
    }
    
    if row.get('Dimensiones'):
        dims = str(row.get('Dimensiones')).split('x')
        if len(dims) == 3:
            info['largo'] = dims[0].strip()
            info['ancho'] = dims[1].strip()
            info['alto'] = dims[2].strip()
            
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
            print_callback(f"✅ Texto extraído correctamente de {pdf_url}")
            return texto_completo
        else:
            print_callback(f"⚠️ El PDF en {pdf_url} parece estar vacío o ser una imagen.")
            return None

    except requests.exceptions.RequestException as e:
        print_callback(f"❌ Error al descargar el PDF desde {pdf_url}: {e}")
        return None
    except Exception as e:
        print_callback(f"❌ Error al procesar el PDF desde {pdf_url}: {e}")
        return None

def extraer_datos_tecnicos_del_pdf(texto_pdf, info_actual, print_callback=print):
    """Intenta extraer y actualizar datos técnicos desde el texto de un PDF con regex mejoradas."""
    info_actualizada = info_actual.copy()
    
    patrones = {
        'potencia_kva': r'(\d{1,4}[\.,]?\d{1,2})\s*kVA',
        'potencia_kw': r'(\d{1,4}[\.,]?\d{1,2})\s*kW',
        'voltaje': r'(\d{3}(?:/\d{3})?)\s*V',
        'consumo': r'Consumo(?: de combustible)?\s*\(?L/h\)?\s*[:\s]*([\d\.]+)',
        'tanque': r'(?:Capacidad del tanque|Tanque de combustible)\s*\(?L\)?\s*[:\s]*(\d+)',
        'peso': r'Peso\s*\(?kg\)?\s*[:\s]*(\d+)',
        'ruido': r'Nivel de ruido\s*\(?dBA?@\d+m\)?\s*[:\s]*(\d+)',
        'motor': r'Motor\s*[:\s]*([A-Za-z0-9\.\-\s]+)',
        'alternador': r'Alternador\s*[:\s]*([A-Za-z0-9\.\-\s]+)',
        'cilindrada': r'Cilindrada\s*\(cc\)\s*[:\s]*(\d+)'
    }
    
    for campo, patron in patrones.items():
        match = re.search(patron, texto_pdf, re.IGNORECASE | re.DOTALL)
        if match:
            valor_extraido = match.group(1).strip()
            info_actualizada[campo] = valor_extraido
            print_callback(f"  -> Dato extraído de PDF: {campo} = {valor_extraido}")
            
    return info_actualizada

def validar_caracteristicas_producto(info, texto_pdf):
    """Detecta características especiales del producto."""
    caracteristicas = {
        'tiene_tta': False,
        'tiene_cabina': False,
        'es_inverter': False,
        'tipo_combustible': 'diesel'
    }
    
    texto_busqueda = f"{info.get('nombre', '')} {info.get('familia', '')}".lower()
    if texto_pdf:
        texto_busqueda += " " + texto_pdf.lower()

    if any(keyword in texto_busqueda for keyword in ['tta', 'transferencia automatica', 'ats']):
        caracteristicas['tiene_tta'] = True

    if any(keyword in texto_busqueda for keyword in ['cabinado', 'insonorizado', 'soundproof', 'silent']):
        caracteristicas['tiene_cabina'] = True

    if 'inverter' in texto_busqueda:
        caracteristicas['es_inverter'] = True

    if any(keyword in texto_busqueda for keyword in ['gas', 'glp', 'gnc']):
        caracteristicas['tipo_combustible'] = 'gas'
    elif 'nafta' in texto_busqueda:
        caracteristicas['tipo_combustible'] = 'nafta'
        
    return caracteristicas

# ============================================================================
# NUEVA VERSIÓN MEJORADA DE GENERACIÓN DE DESCRIPCIONES PREMIUM
# ============================================================================

def generar_descripcion_detallada_html_premium(row, config, modelo_ia=None):
    """
    Genera descripción HTML premium con diseño visual mejorado y responsivo
    Versión 2.1 - Corregido el error de KeyError y mejorada la extracción de datos.
    """
    info_inicial = extraer_info_tecnica(row)
    
    pdf_url = info_inicial.get('pdf_url', '')
    texto_pdf = None
    if pdf_url and pdf_url not in ['nan', 'None', '']:
        if not pdf_url.startswith('http'):
            pdf_url = f"https://storage.googleapis.com/fichas_tecnicas/{pdf_url}"
        texto_pdf = extraer_texto_pdf(pdf_url, print)

    info = info_inicial
    if texto_pdf:
        print("🤖 Iniciando extracción de datos con IA...")
        if modelo_ia:
            try:
                prompt_template_path = Path(__file__).parent / "templates" / "detailed_product_prompt.json"
                with open(prompt_template_path, 'r', encoding='utf-8') as f:
                    prompt_templates = json.load(f)

                prompt_template = prompt_templates['prompt_extract']
                
                prompt_extraccion = prompt_template.replace('{pdf_text}', texto_pdf[:4000])
                prompt_extraccion = prompt_extraccion.replace('{familia}', info_inicial['familia'])
                prompt_extraccion = prompt_extraccion.replace('{nombre}', info_inicial['nombre'])
                prompt_extraccion = prompt_extraccion.replace('{modelo}', info_inicial['modelo'])
                prompt_extraccion = prompt_extraccion.replace('{marca}', info_inicial['marca'])

                response = modelo_ia.generate_content(prompt_extraccion)
                
                # Limpiar y parsear la respuesta JSON de la IA
                cleaned_response = response.text.strip().replace('```json', '').replace('```', '').strip()
                extracted_data = json.loads(cleaned_response)
                
                # Actualizar 'info' con los datos extraídos por la IA
                info.update(extracted_data.get('especificaciones', {}))
                print("✅ Datos extraídos con IA correctamente.")

            except Exception as e:
                print(f"⚠️ Error en extracción con IA, usando Regex como fallback: {e}")
                info = extraer_datos_tecnicos_del_pdf(texto_pdf, info_inicial, print)
        else:
            info = extraer_datos_tecnicos_del_pdf(texto_pdf, info_inicial, print)

    caracteristicas = validar_caracteristicas_producto(info, texto_pdf)
    
    html_hero = generar_hero_section(info)
    html_cards = generar_info_cards_section(info, caracteristicas)
    html_specs = generar_specs_table_section(info)
    html_badges = generar_feature_badges_section(caracteristicas)
    html_speech = generar_speech_sections(info, caracteristicas, modelo_ia, texto_pdf)
    html_benefits = generar_benefits_section()
    html_cta = generar_cta_section(info, config)
    html_contact = generar_contact_section(config)
    
    css_styles = generar_css_mejorado()
    
    html = f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{info['nombre']} - Descripción Premium</title>
        {css_styles}
    </head>
    <body>
        <div class="container">
            {html_hero}
            {html_cards}
            {html_specs}
            {html_badges}
            {html_speech}
            {html_benefits}
            {html_cta}
            {html_contact}
        </div>
    </body>
    </html>
    """
    
    return html

def generar_hero_section(info):
    """Genera la sección hero con gradiente"""
    nombre_producto = info['nombre']
    subtitulo = "Solución energética profesional de última generación"
    
    if 'compresor' in info.get('familia', '').lower():
        subtitulo = "Compresión de aire profesional de alta eficiencia"
    elif 'vibro' in info.get('familia', '').lower():
        subtitulo = "Compactación profesional de máxima potencia"
    
    return f'''
    <div class="hero-header animate-fade-in">
        <h1>{nombre_producto}</h1>
        <p>{subtitulo}</p>
    </div>
    '''

def generar_info_cards_section(info, caracteristicas):
    """Genera las cards de información principal"""
    tipo_combustible = caracteristicas['tipo_combustible']
    icono_combustible = ICONOS_SVG.get(tipo_combustible, ICONOS_SVG['diesel'])
    
    motor_display = info.get('motor', 'N/D')
    motor_subtext = ""
    if info.get('cilindrada'):
        motor_subtext = f"{info['cilindrada']}cc"
    
    return f'''
    <div class="info-cards">
        <div class="info-card">
            <div class="icon-wrapper">
                {ICONOS_SVG['potencia']}
            </div>
            <div class="info-content">
                <h4>POTENCIA</h4>
                <div class="value">{info.get('potencia_kva', 'N/D')} KVA</div>
                {f'<div class="sub-value">{info.get("potencia_kw", "")} KW</div>' if info.get('potencia_kw') else ''}
            </div>
        </div>
        <div class="info-card">
            <div class="icon-wrapper">
                {ICONOS_SVG['motor']}
            </div>
            <div class="info-content">
                <h4>MOTOR</h4>
                <div class="value" style="font-size: 20px;">{motor_display}</div>
                {f'<div class="sub-value">{motor_subtext}</div>' if motor_subtext else ''}
            </div>
        </div>
        <div class="info-card">
            <div class="icon-wrapper">
                {icono_combustible}
            </div>
            <div class="info-content">
                <h4>COMBUSTIBLE</h4>
                <div class="value" style="font-size: 20px;">{tipo_combustible.upper()}</div>
                <div class="sub-value">{info.get('consumo', 'N/D')} L/h</div>
            </div>
        </div>
    </div>
    '''

def generar_specs_table_section(info):
    """Genera la tabla de especificaciones técnicas"""
    specs = []
    
    if info.get('potencia_kva'):
        specs.append(('POTENCIA STANDBY', f"{info['potencia_kva']} KVA{f' / {info.get('potencia_kw', '')} KW' if info.get('potencia_kw') else ''}", 'potencia'))
    if info.get('voltaje'):
        specs.append(('VOLTAJE', f"{info['voltaje']} V", 'voltaje'))
    if info.get('frecuencia'):
        specs.append(('FRECUENCIA', f"{info['frecuencia']} Hz", 'frecuencia'))
    if info.get('motor'):
        specs.append(('MOTOR', info['motor'], 'motor'))
    if info.get('alternador'):
        specs.append(('ALTERNADOR', info['alternador'], 'motor'))
    if info.get('cilindrada'):
        specs.append(('CILINDRADA', f"{info['cilindrada']} cm³", 'cilindrada'))
    if info.get('consumo'):
        specs.append(('CONSUMO', f"{info['consumo']} L/h @ 75% carga", 'consumo'))
    if info.get('tanque'):
        specs.append(('CAPACIDAD TANQUE', f"{info['tanque']} L", 'consumo'))
    if info.get('ruido'):
        specs.append(('NIVEL SONORO', f"{info['ruido']} dBA @ 7 metros", 'ruido'))
    
    if all(info.get(x) for x in ['largo', 'ancho', 'alto']):
        dims = f"{info['largo']} x {info['ancho']} x {info['alto']} mm"
        specs.append(('DIMENSIONES', dims, 'dimensiones'))
    
    if info.get('peso'):
        specs.append(('PESO', f"{info['peso']} kg", 'peso'))
    
    rows_html = ""
    for i, (label, value, icon_key) in enumerate(specs):
        icono = ICONOS_SVG.get(icon_key, '')
        rows_html += f'''
        <tr>
            <td class="spec-label">
                {icono}
                {label}
            </td>
            <td class="spec-value">{value}</td>
        </tr>
        '''
    
    if not rows_html:
        return ""
    
    return f'''
    <div class="specs-section">
        <div class="specs-header">
            {ICONOS_SVG['specs']}
            <h2>ESPECIFICACIONES TÉCNICAS COMPLETAS</h2>
        </div>
        <div class="specs-table">
            <table>
                <thead>
                    <tr>
                        <th style="width: 40%;">CARACTERÍSTICA</th>
                        <th>ESPECIFICACIÓN</th>
                    </tr>
                </thead>
                <tbody>
                    {rows_html}
                </tbody>
            </table>
        </div>
    </div>
    '''

def generar_feature_badges_section(caracteristicas):
    """Genera los badges de características especiales"""
    badges_html = ""
    
    if caracteristicas.get('tiene_tta'):
        badges_html += f'''
        <div class="feature-badge">
            {ICONOS_SVG['check']}
            <span>TABLERO DE TRANSFERENCIA AUTOMÁTICA INCLUIDO</span>
        </div>
        '''
    
    if caracteristicas.get('tiene_cabina'):
        badges_html += f'''
        <div class="feature-badge green">
            {ICONOS_SVG['check']}
            <span>CABINA INSONORIZADA DE ALUMINIO</span>
        </div>
        '''
    
    if caracteristicas.get('es_inverter'):
        badges_html += f'''
        <div class="feature-badge purple">
            {ICONOS_SVG['check']}
            <span>TECNOLOGÍA INVERTER - MÁXIMA EFICIENCIA</span>
        </div>
        '''
    
    return f'<div class="feature-badges">{badges_html}</div>' if badges_html else ''

def generar_speech_sections(info, caracteristicas, modelo_ia, texto_pdf):
    """Genera las secciones de speech de ventas usando IA si está disponible."""
    default_content = {
        'potencia': f"Con una capacidad de {info.get('potencia_kva', 'N/D')} KVA, este equipo está diseñado para superar las expectativas más exigentes. Su motor {info.get('motor', 'N/D')} garantiza un funcionamiento óptimo en cualquier condición de trabajo.",
        'money': f"Con un consumo de {info.get('consumo', 'N/D')} litros por hora y un tanque de {info.get('tanque', 'N/D')} litros, obtendrá horas de operación continua sin interrupciones. Esto se traduce en ahorro real y menor frecuencia de reabastecimiento.",
        'shield': f"{'El alternador ' + info.get('alternador', '') + ' asegura una entrega de energía estable y constante. ' if info.get('alternador') else ''}{'La cabina insonorizada reduce drásticamente el ruido. ' if caracteristicas.get('tiene_cabina') else ''}Construido para durar con los más altos estándares de calidad."
    }

    if modelo_ia and texto_pdf:
        try:
            prompt = f"""
            Basado en el siguiente texto de un PDF de un producto, genera 3 párrafos de venta cortos y persuasivos.
            El texto debe ser profesional y enfocado en beneficios.

            Texto del PDF:
            ---
            {texto_pdf[:2000]}
            ---

            Información clave del producto:
            - Nombre: {info['nombre']}
            - Potencia: {info['potencia_kva']} KVA
            - Motor: {info['motor']}

            Genera 3 párrafos separados por '|||' para los siguientes temas:
            1.  **Potencia y Rendimiento Superior**: Destaca la capacidad y el motor.
            2.  **Economía Operativa**: Habla del consumo y la autonomía.
            3.  **Confiabilidad y Construcción**: Menciona la calidad, el alternador y la cabina si aplica.
            
            IMPORTANTE: Responde solo con los 3 párrafos separados por '|||'. No agregues títulos ni numeración.
            """
            
            response = modelo_ia.generate_content(prompt)
            if response and response.text:
                partes = response.text.split('|||')
                if len(partes) == 3:
                    default_content['potencia'] = partes[0].strip()
                    default_content['money'] = partes[1].strip()
                    default_content['shield'] = partes[2].strip()
                    print("✅ Contenido de speech generado por IA.")
        except Exception as e:
            print(f"⚠️ Error generando speech con IA, se usará contenido por defecto: {e}")

    sections = [
        {'icon': 'potencia', 'title': 'POTENCIA Y RENDIMIENTO SUPERIOR', 'content': default_content['potencia']},
        {'icon': 'money', 'title': 'ECONOMÍA OPERATIVA GARANTIZADA', 'content': default_content['money']},
        {'icon': 'shield', 'title': 'CONFIABILIDAD COMPROBADA', 'content': default_content['shield']},
        {
            'icon': 'tools', 'title': 'APLICACIONES IDEALES',
            'content': '''
            <ul>
                <li>Industrias y fábricas que requieren energía constante</li>
                <li>Comercios y centros de atención al público</li>
                <li>Hospitales y centros de salud</li>
                <li>Eventos y espectáculos al aire libre</li>
                <li>Respaldo para sistemas críticos</li>
            </ul>
            '''
        },
        {
            'icon': 'tools', 'title': 'POR QUÉ ELEGIR ESTE EQUIPO',
            'content': "No es solo un generador, es su socio en continuidad operativa. Con respaldo de marca reconocida, servicio técnico especializado y disponibilidad inmediata de repuestos, su inversión está protegida."
        }
    ]
    
    html = ""
    for section in sections:
        html += f'''
        <div class="speech-section">
            <div class="speech-header">
                <div class="speech-icon">
                    {ICONOS_SVG.get(section['icon'], '')}
                </div>
                <h3>{section['title']}</h3>
            </div>
            {'<p>' + section['content'] + '</p>' if '<ul>' not in section['content'] else section['content']}
        </div>
        '''
    
    return html

def generar_benefits_section():
    """Genera la sección de beneficios"""
    benefits = [
        {'icon': 'shield', 'title': 'GARANTÍA OFICIAL', 'desc': 'Respaldo total del fabricante con garantía extendida'},
        {'icon': 'quality', 'title': 'CALIDAD CERTIFICADA', 'desc': 'Cumple con todas las normas internacionales'},
        {'icon': 'tools', 'title': 'SERVICIO TÉCNICO', 'desc': 'Red nacional de servicio y repuestos originales'},
        {'icon': 'money', 'title': 'FINANCIACIÓN', 'desc': 'Múltiples opciones de pago y financiación a medida'}
    ]
    
    cards_html = ""
    for benefit in benefits:
        cards_html += f'''
        <div class="benefit-card">
            <div class="benefit-icon">
                {ICONOS_SVG.get(benefit['icon'], '')}
            </div>
            <h4>{benefit['title']}</h4>
            <p>{benefit['desc']}</p>
        </div>
        '''
    
    return f'''
    <div class="benefits-section">
        <div class="benefits-header">
            <h3>POR QUÉ ELEGIR ESTE GENERADOR</h3>
        </div>
        <div class="benefits-grid">
            {cards_html}
        </div>
    </div>
    '''

def generar_cta_section(info, config):
    """Genera la sección de Call-to-Action"""
    nombre_producto = info['nombre']
    whatsapp = config.get('whatsapp', '541139563099')
    email = config.get('email', 'info@generadores.ar')
    pdf_url = info.get('pdf_url', '#')
    
    if pdf_url and not pdf_url.startswith('http'):
        pdf_url = f"https://storage.googleapis.com/fichas_tecnicas/{pdf_url}"
    
    whatsapp_msg = f"Hola,%20vengo%20de%20ver%20el%20{nombre_producto.replace(' ', '%20')}%20en%20la%20tienda%20de%20Stelorder%20y%20quisiera%20mas%20informacion"
    email_subject = f"Consulta%20desde%20Stelorder%20-%20{nombre_producto.replace(' ', '%20')}"
    email_body = f"Hola,%0A%0AVengo%20de%20ver%20el%20{nombre_producto.replace(' ', '%20')}%20en%20la%20tienda%20de%20Stelorder.%0A%0AQuedo%20a%20la%20espera%20de%20su%20respuesta.%0A%0ASaludos"
    
    return f'''
    <div class="cta-section">
        <h3>TOME ACCIÓN AHORA</h3>
        <p>No pierda esta oportunidad. Consulte con nuestros especialistas hoy mismo.</p>
        
        <div class="cta-buttons">
            <a href="https://wa.me/{whatsapp}?text={whatsapp_msg}" target="_blank" class="cta-button whatsapp">
                {ICONOS_SVG['whatsapp']}
                <span>CONSULTAR POR WHATSAPP</span>
            </a>
            <a href="{pdf_url}" target="_blank" class="cta-button pdf">
                {ICONOS_SVG['pdf']}
                <span>DESCARGAR FICHA TÉCNICA</span>
            </a>
            <a href="mailto:{email}?subject={email_subject}&body={email_body}" class="cta-button email">
                {ICONOS_SVG['email']}
                <span>SOLICITAR COTIZACIÓN</span>
            </a>
        </div>
    </div>
    '''

def generar_contact_section(config):
    """Genera la sección de contacto"""
    return f'''
    <div class="contact-footer">
        <h4>CONTACTO DIRECTO</h4>
        <div class="contact-grid">
            <div class="contact-item">
                <div class="contact-icon">{ICONOS_SVG['phone']}</div>
                <div class="contact-info">
                    <div class="label">Teléfono / WhatsApp</div>
                    <a href="https://wa.me/{config.get('whatsapp', '')}">{config.get('telefono_display', '')}</a>
                </div>
            </div>
            <div class="contact-item">
                <div class="contact-icon">{ICONOS_SVG['email']}</div>
                <div class="contact-info">
                    <div class="label">Email</div>
                    <a href="mailto:{config.get('email', '')}">{config.get('email', '')}</a>
                </div>
            </div>
            <div class="contact-item">
                <div class="contact-icon">{ICONOS_SVG['web']}</div>
                <div class="contact-info">
                    <div class="label">Sitio Web</div>
                    <a href="https://{config.get('website', '')}" target="_blank">{config.get('website', '')}</a>
                </div>
            </div>
        </div>
    </div>
    '''

def generar_css_mejorado():
    """Genera los estilos CSS mejorados y responsivos"""
    return '''
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
        .feature-badge.purple { background: linear-gradient(135deg, #9c27b0 0%, #7b1fa2 100%); box-shadow: 0 5px 20px rgba(156, 39, 176, 0.3); }
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
        @media (max-width: 768px) {
            .container { padding: 15px; }
            .hero-header { padding: 30px 20px; }
            .info-cards { grid-template-columns: 1fr; gap: 15px; }
            .specs-section { padding: 20px; }
            .specs-table { overflow-x: auto; }
            .specs-table table { min-width: 500px; }
            .cta-buttons { flex-direction: column; align-items: stretch; }
            .cta-button { justify-content: center; }
            .benefits-grid { grid-template-columns: 1fr; }
            .contact-grid { grid-template-columns: 1fr; }
        }
        @keyframes fadeInUp { from { opacity: 0; transform: translateY(30px); } to { opacity: 1; transform: translateY(0); } }
        .animate-fade-in { animation: fadeInUp 0.6s ease-out; }
    </style>
    '''
