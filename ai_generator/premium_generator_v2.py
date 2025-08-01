# -*- coding: utf-8 -*-
"""
Módulo para la generación de descripciones HTML premium de productos.
Versión 2.2 - Con estilos inline exactos
"""
import re
import requests
import PyPDF2
import io
import fitz  # PyMuPDF
import json
from pathlib import Path
import unicodedata

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
        '✓': '',
        '✔': '',
        '✗': '',
        '✘': '',
        '★': '',
        '☆': '',
        '♦': '',
        '♥': '',
        '♠': '',
        '♣': '',
        '►': '',
        '◄': '',
        '▲': '',
        '▼': '',
        '→': '',
        '←': '',
        '↑': '',
        '↓': '',
        '↔': '',
        '⇒': '',
        '⇐': '',
        '⇑': '',
        '⇓': '',
        '⇔': '',
        '✅': '',
        '❌': '',
        '⚠️': '',
        '⚡': '',
        '🔧': '',
        '📍': '',
        '🏢': '',
        '💡': '',
        '🔨': '',
        '🌟': ''
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
    
    # Iconos de combustibles
    'gas': '<svg width="28" height="28" viewBox="0 0 24 24" fill="#1976d2"><path d="M13.5.67s.74 2.65.74 4.8c0 2.06-1.35 3.73-3.41 3.73-2.07 0-3.63-1.67-3.63-3.73l.03-.36C5.21 7.51 4 10.62 4 14c0 4.42 3.58 8 8 8s8-3.58 8-8C20 8.61 17.41 3.8 13.5.67z"/></svg>',
    'diesel': '<svg width="28" height="28" viewBox="0 0 24 24" fill="#333"><path d="M12 2C8.13 2 5 5.13 5 9c0 1.88.79 3.56 2 4.78V22h10v-8.22c1.21-1.22 2-2.9 2-4.78 0-3.87-3.13-7-7-7zm0 2c2.76 0 5 2.24 5 5s-2.24 5-5 5-5-2.24-5-5 2.24-5 5-5z"/></svg>',
    'nafta': '<svg width="28" height="28" viewBox="0 0 24 24" fill="#f44336"><path d="M12 3c-1.1 0-2 .9-2 2v12.5c0 .83.67 1.5 1.5 1.5s1.5-.67 1.5-1.5V5c0-1.1-.9-2-2-2zm-3 4H7v11h2V7zm6 0h-2v11h2V7z"/></svg>',
    
    # Iconos de beneficios
    'quality': '<svg width="28" height="28" viewBox="0 0 24 24" fill="#4caf50"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/></svg>',
    'money': '<svg width="28" height="28" viewBox="0 0 24 24" fill="#ff6600"><path d="M11.8 10.9c-2.27-.59-3-1.2-3-2.15 0-1.09 1.01-1.85 2.7-1.85 1.78 0 2.44.85 2.5 2.1h2.21c-.07-1.72-1.12-3.3-3.21-3.81V3h-3v2.16c-1.94.42-3.5 1.68-3.5 3.61 0 2.31 1.91 3.46 4.7 4.13 2.5.6 3 1.48 3 2.41 0 .69-.49 1.79-2.7 1.79-2.06 0-2.87-.92-2.98-2.1h-2.2c.12 2.19 1.76 3.42 3.68 3.83V21h3v-2.15c1.95-.37 3.5-1.5 3.5-3.55 0-2.84-2.43-3.81-4.7-4.4z"/></svg>',
    
    # Iconos de contacto
    'whatsapp': '<svg width="24" height="24" viewBox="0 0 24 24" fill="white"><path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413Z"/></svg>',
    'pdf': '<svg width="24" height="24" viewBox="0 0 24 24" fill="#000"><path d="M20 2H8c-1.1 0-2 .9-2 2v12c0 1.1.9 2 2 2h12c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2zm-8.5 7.5c0 .83-.67 1.5-1.5 1.5H9v2H7.5V7H10c.83 0 1.5.67 1.5 1.5v1zm5 2c0 .83-.67 1.5-1.5 1.5h-2.5V7H15c.83 0 1.5.67 1.5 1.5v3zm4-3H19v1h1.5V11H19v2h-1.5V7h3v1.5zM9 9.5h1v-1H9v1zM4 6H2v14c0 1.1.9 2 2 2h14v-2H4V6zm10 5.5h1v-3h-1v3z"/></svg>',
    'email': '<svg width="24" height="24" viewBox="0 0 24 24" fill="white"><path d="M20 4H4c-1.1 0-1.99.9-1.99 2L2 18c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V6c0-1.1-.9-2-2-2zm0 4l-8 5-8-5V6l8 5 8-5v2z"/></svg>',
    'phone': '<svg width="24" height="24" viewBox="0 0 24 24" fill="#ff6600"><path d="M6.62 10.79c1.44 2.83 3.76 5.14 6.59 6.59l2.2-2.2c.27-.27.67-.36 1.02-.24 1.12.37 2.33.57 3.57.57.55 0 1 .45 1 1V20c0 .55-.45 1-1 1-9.39 0-17-7.61-17-17 0-.55.45-1 1-1h3.5c.55 0 1 .45 1 1 0 1.25.2 2.45.57 3.57.11.35.03.74-.25 1.02l-2.2 2.2z"/></svg>',
    'web': '<svg width="24" height="24" viewBox="0 0 24 24" fill="#ff6600"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-1 17.93c-3.94-.49-7-3.85-7-7.93 0-.62.08-1.21.21-1.79L9 15v1c0 1.1.9 2 2 2v1.93zm6.9-2.54c-.26-.81-1-1.39-1.9-1.39h-1v-3c0-.55-.45-1-1-1H8v-2h2c.55 0 1-.45 1-1V7h2c1.1 0 2-.9 2-2v-.41c2.93 1.19 5 4.06 5 7.41 0 2.08-.8 3.97-2.1 5.39z"/></svg>',
    
    # Iconos de especificaciones técnicas
    'voltaje': '<svg width="20" height="20" viewBox="0 0 24 24" fill="#D32F2F"><path d="M11 15h2v2h-2zm0-8h2v6h-2zm1-5C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2z"/></svg>',
    'frecuencia': '<svg width="20" height="20" viewBox="0 0 24 24" fill="#D32F2F"><path d="M16 6l-4 4-4-4v3l4 4 4-4zm0 6l-4 4-4-4v3l4 4 4-4z"/></svg>',
    'cilindrada': '<svg width="20" height="20" viewBox="0 0 24 24" fill="#D32F2F"><path d="M17 3H7c-1.1 0-1.99.9-1.99 2L5 21l7-3 7 3V5c0-1.1-.9-2-2-2z"/></svg>',
    'consumo': '<svg width="20" height="20" viewBox="0 0 24 24" fill="#D32F2F"><path d="M19.77 7.23l.01-.01-3.72-3.72L15 4.56l2.11 2.11c-.94.36-1.61 1.26-1.61 2.33 0 1.38 1.12 2.5 2.5 2.5.36 0 .69-.08 1-.21v7.21c0 .55-.45 1-1 1s-1-.45-1-1V14c0-1.1-.9-2-2-2h-1V5c0-1.1-.9-2-2-2H6c-1.1 0-2 .9-2 2v16h10v-7.5h1.5v5c0 1.38 1.12 2.5 2.5 2.5s2.5-1.12 2.5-2.5V9c0-.69-.28-1.32-.73-1.77z"/></svg>',
    'ruido': '<svg width="20" height="20" viewBox="0 0 24 24" fill="#D32F2F"><path d="M3 9v6h4l5 5V4L7 9H3zm13.5 3c0-1.77-1-3.29-2.5-4.03v8.05c1.5-.73 2.5-2.25 2.5-4.02zM14 3.23v2.06c2.89.86 5 3.54 5 6.71s-2.11 5.85-5 6.71v2.06c4.01-.91 7-4.49 7-8.77s-2.99-7.86-7-8.77z"/></svg>',
    'dimensiones': '<svg width="20" height="20" viewBox="0 0 24 24" fill="#D32F2F"><path d="M21 3H3c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h18c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm0 16H3V5h18v14z"/></svg>',
    'peso': '<svg width="20" height="20" viewBox="0 0 24 24" fill="#D32F2F"><path d="M12 3c-1.27 0-2.4.8-2.82 2H3v2h1.95l2 7c.17.59.71 1 1.32 1H15.73c.61 0 1.15-.41 1.32-1l2-7H21V5h-6.18C14.4 3.8 13.27 3 12 3zm0 2c.55 0 1 .45 1 1s-.45 1-1 1-1-.45-1-1 .45-1 1-1z"/></svg>',
    
    # Iconos para listas (basados en la última imagen)
    'check': '<svg width="20" height="20" viewBox="0 0 24 24" fill="#4caf50"><path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z"/></svg>',
    'dot': '<svg width="20" height="20" viewBox="0 0 24 24" fill="#ff6600"><circle cx="12" cy="12" r="6"/></svg>',
    'autonomia_L': '<svg width="20" height="20" viewBox="0 0 24 24" fill="#4caf50"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-1 14H9V8h4v2h-2v4z"/></svg>',
    'wrench': '<svg width="20" height="20" viewBox="0 0 24 24" fill="#ff6600"><path d="M22.7 19l-9.1-9.1c.9-2.3.4-5-1.5-6.9-2-2-5-2.4-7.4-1.3L9 6 6 9 1.6 4.7C.4 7.1.9 10.1 2.9 12.1c1.9 1.9 4.6 2.4 6.9 1.5l9.1 9.1c.4.4 1 .4 1.4 0l2.3-2.3c.5-.4.5-1.1.1-1.4z"/></svg>',
    'lightning': '<svg width="20" height="20" viewBox="0 0 24 24" fill="#ff6600"><path d="M7 2v11h3v9l7-12h-4l4-8z"/></svg>',
    'location': '<svg width="20" height="20" viewBox="0 0 24 24" fill="#4caf50"><path d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13S15.87 2 12 2zm0 9.5c-1.38 0-2.5-1.12-2.5-2.5s1.12-2.5 2.5-2.5 2.5 1.12 2.5 2.5-1.12 2.5-2.5 2.5z"/></svg>',
    'business': '<svg width="20" height="20" viewBox="0 0 24 24" fill="#4caf50"><path d="M12 7V3H2v18h20V7H12zM6 19H4v-2h2v2zm0-4H4v-2h2v2zm0-4H4V9h2v2zm10 8H8v-2h2v-2H8V9h8v10zm-2-8h-2v2h2v-2z"/></svg>'
}

# ============================================================================
# FUNCIONES AUXILIARES (Extracción y Validación de Datos)
# ============================================================================
def obtener_icono_para_item(texto_item):
    """Devuelve un icono SVG basado en palabras clave en el texto del item."""
    texto_item = texto_item.lower()
    # Mapeo de palabras clave a iconos
    mapa_iconos = {
        'wrench': ['obra', 'construccion', 'mantenimiento', 'reparacion', 'robusta', 'duradera'],
        'location': ['fincas', 'zonas rurales', 'agricultura', 'ganaderia'],
        'lightning': ['eventos', 'aire libre', 'camping'],
        'business': ['hogar', 'pequenos negocios', 'industrial', 'emergencias'],
        'dot': ['seguridad', 'protegidos', 'potencia', 'equipos', 'alimenta', 'avr'],
        'autonomia_L': ['autonomia', 'horas', 'tanque', 'consumo']
    }
    
    for icono, keywords in mapa_iconos.items():
        if any(keyword in texto_item for keyword in keywords):
            return ICONOS_SVG[icono]
            
    # Si no coincide nada, se devuelve el icono de punto naranja como fallback
    return ICONOS_SVG['dot']

def extraer_info_tecnica(row):
    """Extrae y normaliza la información técnica de una fila de datos de la BD."""
    # Mapeo de columnas SQL a claves del diccionario 'info'
    info = {
        'nombre': row.get('Descripción', 'Producto sin nombre'),
        'marca': row.get('Marca', 'N/D'),
        'modelo': row.get('Modelo', 'N/D'),
        'familia': row.get('Familia', ''),
        'potencia_kva': row.get('Potencia', 'N/D'),
        'potencia_kw': '', # Se buscará en el PDF
        'voltaje': row.get('Tensión', 'N/D'),
        'frecuencia': '50', # Valor por defecto, se puede buscar en PDF
        'motor': row.get('Motor', 'N/D'),
        'alternador': 'N/D', # Se buscará en el PDF
        'cilindrada': '', # Se buscará en el PDF
        'consumo': 'N/D', # Se buscará en el PDF
        'tanque': 'N/D', # Se buscará en el PDF
        'ruido': 'N/D', # Se buscará en el PDF
        'largo': '', 'ancho': '', 'alto': '', # Se buscará en el PDF
        'peso': row.get('Peso_(kg)', 'N/D'),
        'pdf_url': row.get('URL_PDF', '')
    }
    
    # Extraer dimensiones si vienen juntas
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
        
        # Usar PyMuPDF que es más robusto
        pdf_document = fitz.open(stream=response.content, filetype="pdf")
        texto_completo = ""
        for page_num in range(pdf_document.page_count):
            page = pdf_document[page_num]
            texto_completo += page.get_text()
        pdf_document.close()
        
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
    
    # Patrones de regex mejorados para ser más flexibles
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
            # Siempre se da prioridad al dato del PDF
            info_actualizada[campo] = valor_extraido
            print_callback(f"  -> Dato extraído de PDF: {campo} = {valor_extraido}")
            
    return info_actualizada

def validar_caracteristicas_producto(info, texto_pdf):
    """Detecta características especiales del producto."""
    caracteristicas = {
        'tiene_tta': False,
        'tiene_cabina': False,
        'es_inverter': False,
        'tipo_combustible': 'diesel' # Por defecto
    }
    
    # Combinar toda la información de texto disponible
    texto_busqueda = f"{info.get('nombre', '')} {info.get('familia', '')}".lower()
    if texto_pdf:
        texto_busqueda += " " + texto_pdf.lower()

    # Check from 'caracteristicas_especiales' if available from AI extraction
    special_features = info.get('caracteristicas_especiales', [])
    if any('tta' in feature.lower() for feature in special_features):
        caracteristicas['tiene_tta'] = True
    if any('cabinado' in feature.lower() or 'insonorizado' in feature.lower() for feature in special_features):
        caracteristicas['tiene_cabina'] = True
    if any('inverter' in feature.lower() for feature in special_features):
        caracteristicas['es_inverter'] = True

    # Fallback to text search if not in special features
    if not caracteristicas['tiene_tta'] and any(keyword in texto_busqueda for keyword in ['tta', 'transferencia automatica', 'ats']):
        caracteristicas['tiene_tta'] = True
    if not caracteristicas['tiene_cabina'] and any(keyword in texto_busqueda for keyword in ['cabinado', 'insonorizado', 'soundproof', 'silent']):
        caracteristicas['tiene_cabina'] = True
    if not caracteristicas['es_inverter'] and 'inverter' in texto_busqueda:
        caracteristicas['es_inverter'] = True

    # Determine fuel type
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

# ============================================================================
# FUNCIONES DE GENERACIÓN DE HTML CON ESTILOS INLINE
# ============================================================================

def generar_titulo_producto(info, caracteristicas):
    """Genera el título del producto."""
    valores_no_deseados = ['N/D', 'n/d', 'N/A', 'n/a', 'None', 'null', '']
    
    # Primero intentar usar el título generado por IA
    titulo = info.get('marketing_content', {}).get('titulo_h1', '')
    
    if not titulo:
        # Construir título inteligente evitando N/D
        marca = info.get('marca', '').strip()
        modelo = info.get('modelo', '').strip()
        potencia = info.get('potencia_kva', '').strip()
        
        if marca and marca not in valores_no_deseados:
            titulo = marca
        else:
            titulo = "GRUPO ELECTROGENO"
            
        if modelo and modelo not in valores_no_deseados:
            titulo += f" {modelo}"
        elif potencia and potencia not in valores_no_deseados:
            titulo += f" {potencia}"
            
        # Si el título es muy genérico, usar el nombre completo del producto
        if titulo == "GRUPO ELECTROGENO" or len(titulo.split()) < 2:
            nombre_producto = info.get('nombre', '')
            if nombre_producto and nombre_producto not in valores_no_deseados:
                titulo = nombre_producto

    return eliminar_tildes_y_especiales(titulo).upper()

def generar_subtitulo_producto(info, caracteristicas):
    """Genera el subtítulo del producto."""
    subtitulo_ia = info.get('marketing_content', {}).get('subtitulo_p', '')
    if subtitulo_ia:
        return eliminar_tildes_y_especiales(subtitulo_ia)
    return "Solucion energetica de ultima generacion para su proyecto"

def generar_hero_section_inline(titulo, subtitulo):
    """Genera el header hero con estilos inline."""
    return f'''
        <!-- HEADER HERO SECTION -->
        <div style="background: linear-gradient(135deg, #ff6600 0%, #ff8833 100%); padding: 40px 30px; text-align: center; border-radius: 0 0 20px 20px; box-shadow: 0 4px 20px rgba(0,0,0,0.1);">
            <h1 style="color: white; font-size: 36px; margin: 0 0 15px 0; font-weight: 700; text-transform: uppercase; letter-spacing: 1px;">
                {titulo}
            </h1>
            <p style="color: white; font-size: 18px; margin: 0; opacity: 0.95; font-weight: 300;">
                {subtitulo}
            </p>
        </div>
    '''

def generar_info_cards_inline(info, caracteristicas):
    """Genera las tarjetas de información con estilos inline."""
    tipo_combustible = caracteristicas.get('tipo_combustible', 'diesel')
    icono_combustible = ICONOS_SVG.get(tipo_combustible, ICONOS_SVG['diesel'])
    
    # Obtener valores limpios
    potencia_kva = info.get('potencia_kva', '').strip()
    potencia_kw = info.get('potencia_kw', '').strip()
    motor = info.get('modelo_motor', info.get('motor', '')).strip()
    consumo = info.get('consumo_combustible_75', info.get('consumo', '')).strip()
    
    return f'''
        <!-- ESPECIFICACIONES PRINCIPALES -->
        <div style="padding: 30px; display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px;">
            
            <!-- Card Potencia -->
            <div class="card-hover" style="background: #f8f9fa; border-radius: 12px; padding: 25px; border-left: 4px solid #ff6600; box-shadow: 0 2px 8px rgba(0,0,0,0.08);">
                <div style="display: flex; align-items: center; gap: 15px;">
                    <div style="width: 48px; height: 48px; background: #fff3e0; border-radius: 50%; display: flex; align-items: center; justify-content: center;">
                        <svg width="24" height="24" viewBox="0 0 24 24" fill="#ff6600"><path d="M7 2v11h3v9l7-12h-4l4-8z"/></svg>
                    </div>
                    <div>
                        <p style="margin: 0; color: #666; font-size: 12px; text-transform: uppercase; letter-spacing: 0.5px;">Potencia Maxima</p>
                        <p style="margin: 5px 0 0 0; font-size: 24px; font-weight: 700; color: #ff6600;">
                            {potencia_kva if potencia_kva else 'N/D'} KVA
                        </p>
                        {f'<p style="margin: 0; font-size: 14px; color: #999;">{potencia_kw} KW</p>' if potencia_kw else ''}
                    </div>
                </div>
            </div>
            
            <!-- Card Motor -->
            <div class="card-hover" style="background: #f8f9fa; border-radius: 12px; padding: 25px; border-left: 4px solid #ff6600; box-shadow: 0 2px 8px rgba(0,0,0,0.08);">
                <div style="display: flex; align-items: center; gap: 15px;">
                    <div style="width: 48px; height: 48px; background: #fff3e0; border-radius: 50%; display: flex; align-items: center; justify-content: center;">
                        <svg width="24" height="24" viewBox="0 0 24 24" fill="#ff6600"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 18c-4.42 0-8-3.58-8-8s3.58-8 8-8 8 3.58 8 8-3.58 8-8 8z"/></svg>
                    </div>
                    <div>
                        <p style="margin: 0; color: #666; font-size: 12px; text-transform: uppercase; letter-spacing: 0.5px;">Motor</p>
                        <p style="margin: 5px 0 0 0; font-size: 18px; font-weight: 600; color: #333;">
                            {motor if motor else 'N/D'}
                        </p>
                    </div>
                </div>
            </div>
            
            <!-- Card Combustible/Consumo -->
            <div class="card-hover" style="background: #f8f9fa; border-radius: 12px; padding: 25px; border-left: 4px solid #ff6600; box-shadow: 0 2px 8px rgba(0,0,0,0.08);">
                <div style="display: flex; align-items: center; gap: 15px;">
                    <div style="width: 48px; height: 48px; background: #fff3e0; border-radius: 50%; display: flex; align-items: center; justify-content: center;">
                        {icono_combustible.replace('width="28"', 'width="24"').replace('height="28"', 'height="24"')}
                    </div>
                    <div>
                        <p style="margin: 0; color: #666; font-size: 12px; text-transform: uppercase; letter-spacing: 0.5px;">Tipo de Combustible</p>
                        <p style="margin: 5px 0 0 0; font-size: 18px; font-weight: 600; color: #333; text-transform: capitalize;">
                            {tipo_combustible.upper()}
                        </p>
                        {f'<p style="margin: 0; font-size: 14px; color: #999;">Consumo: {consumo}</p>' if consumo else ''}
                    </div>
                </div>
            </div>
            
        </div>
    '''

def generar_specs_table_inline(info):
    """Genera la tabla de especificaciones con estilos inline."""
    # Mapeo de especificaciones a mostrar
    specs_display = [
        ('modelo', 'Modelo', ICONOS_SVG.get('motor', '')),
        ('potencia_kva', 'Potencia Stand By', ICONOS_SVG.get('potencia', '')),
        ('potencia_prime', 'Potencia Prime', ICONOS_SVG.get('potencia', '')),
        ('voltaje', 'Voltaje', ICONOS_SVG.get('voltaje', '')),
        ('frecuencia', 'Frecuencia', ICONOS_SVG.get('frecuencia', '')),
        ('motor', 'Motor', ICONOS_SVG.get('motor', '')),
        ('alternador', 'Alternador', '<svg width="20" height="20" viewBox="0 0 24 24" fill="#ff6600"><path d="M12 2l-5.5 9h11z M12 22l5.5-9h-11z M3.5 9L12 12l-3.5 6z M20.5 9L12 12l3.5 6z"/></svg>'),
        ('consumo', 'Consumo al 100%', ICONOS_SVG.get('consumo', '')),
        ('dimensiones_mm', 'Dimensiones (LxAxH)', ICONOS_SVG.get('dimensiones', '')),
        ('peso_kg', 'Peso', ICONOS_SVG.get('peso', ''))
    ]
    
    # Generar filas
    rows_html = ""
    row_count = 0
    for key, label, icon in specs_display:
        value = info.get(key, '')
        if value and str(value).strip():
            bg_color = '#f8f9fa' if row_count % 2 == 0 else 'white'
            rows_html += f'''
                    <tr class="spec-row" style="background: {bg_color}; border-bottom: 1px solid #eee;">
                        <td style="padding: 15px 20px; display: flex; align-items: center; gap: 10px;">
                            <div style="width: 20px; height: 20px; opacity: 0.6;">{icon.replace('fill="#D32F2F"', 'fill="#ff6600"')}</div>
                            <span style="color: #666; font-weight: 500;">{label}</span>
                        </td>
                        <td style="padding: 15px 20px; font-weight: 600; color: #333;">{value}</td>
                    </tr>'''
            row_count += 1
    
    return f'''
        <!-- TABLA DE ESPECIFICACIONES TECNICAS -->
        <div style="background: #FFC107; margin: 30px; padding: 30px; border-radius: 16px; box-shadow: 0 4px 20px rgba(0,0,0,0.1);">
            <h2 style="color: #333; font-size: 28px; margin: 0 0 25px 0; text-align: center; font-weight: 700;">
                ESPECIFICACIONES TECNICAS COMPLETAS
            </h2>
            
            <div style="background: white; border-radius: 12px; overflow: hidden; box-shadow: 0 2px 10px rgba(0,0,0,0.05);">
                <table style="width: 100%; border-collapse: collapse;">
                    <tr style="background: #333; color: white;">
                        <td style="padding: 15px 20px; font-weight: 600; font-size: 14px; text-transform: uppercase; letter-spacing: 0.5px;">Caracteristica</td>
                        <td style="padding: 15px 20px; font-weight: 600; font-size: 14px; text-transform: uppercase; letter-spacing: 0.5px;">Especificacion</td>
                    </tr>
                    {rows_html}
                </table>
            </div>
        </div>
    '''

def generar_feature_badge_inline(caracteristicas):
    """Genera el badge de característica especial con estilos inline."""
    if caracteristicas.get('tiene_tta'):
        return f'''
        <!-- CARACTERISTICA ESPECIAL -->
        <div class="special-feature" style="margin: 30px; background: linear-gradient(135deg, #2196f3, #42a5f5); color: white; padding: 20px 30px; border-radius: 12px; display: flex; align-items: center; gap: 15px; box-shadow: 0 4px 15px rgba(33,150,243,0.3); transition: all 0.3s ease;">
            <div style="width: 32px; height: 32px;">
                <svg width="32" height="32" viewBox="0 0 24 24" fill="white"><path d="M19 3h-4.18C14.4 1.84 13.3 1 12 1c-1.3 0-2.4.84-2.82 2H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm-7 0c.55 0 1 .45 1 1s-.45 1-1 1-1-.45-1-1 .45-1 1-1zm2 14H7v-2h7v2zm3-4H7v-2h10v2zm0-4H7V7h10v2z"/></svg>
            </div>
            <span style="font-size: 20px; font-weight: 600;">TABLERO AUTOMATICO INCLUIDO</span>
        </div>
        '''
    return ''

def generar_content_sections_inline(info, marketing_content):
    """Genera las secciones de contenido con estilos inline."""
    # Usar contenido de marketing si está disponible
    sections = []
    
    if marketing_content:
        if marketing_content.get('puntos_clave_li'):
            sections.append({
                'title': 'POTENCIA Y RENDIMIENTO SUPERIOR',
                'content': eliminar_tildes_y_especiales('. '.join(marketing_content['puntos_clave_li'][:2]))
            })
        if marketing_content.get('descripcion_detallada_p'):
            sections.append({
                'title': 'EFICIENCIA Y ECONOMIA OPERATIVA',
                'content': eliminar_tildes_y_especiales(marketing_content['descripcion_detallada_p'][0])
            })
    
    # Contenido por defecto si no hay marketing content
    if not sections:
        sections = [
            {
                'title': 'POTENCIA Y RENDIMIENTO SUPERIOR',
                'content': f"Este equipo con {info.get('potencia_kva', 'alta')} KVA de potencia maxima esta disenado para brindar energia confiable y constante. Su motor {info.get('motor', 'de alta calidad')} garantiza un rendimiento optimo en las condiciones mas exigentes, ofreciendo la tranquilidad que su proyecto necesita."
            },
            {
                'title': 'EFICIENCIA Y ECONOMIA OPERATIVA',
                'content': f"Con un consumo optimizado, este generador ofrece una excelente economia operativa. El sistema de alimentacion garantiza combustion limpia y menores emisiones, ideal para aplicaciones que requieren sostenibilidad ambiental."
            },
            {
                'title': 'CONFIABILIDAD GARANTIZADA',
                'content': "Equipado con alternador de alta calidad y excitacion automatica AVR, este generador asegura un suministro electrico estable y sin fluctuaciones. El panel de control digital y las protecciones de motor integradas garantizan la seguridad de sus equipos conectados."
            }
        ]
    
    # Agregar aplicaciones si están disponibles
    if marketing_content.get('aplicaciones_ideales_li'):
        apps_html = '<ul style="list-style: none; padding: 0; margin: 10px 0;">'
        for app in marketing_content['aplicaciones_ideales_li']:
            apps_html += f'''
                    <li style="padding: 8px 0; display: flex; align-items: start; gap: 10px;">
                        <svg width="20" height="20" viewBox="0 0 24 24" fill="#ff6600" style="min-width: 20px; margin-top: 2px;"><path d="M7 2v11h3v9l7-12h-4l4-8z"/></svg>
                        <span>{eliminar_tildes_y_especiales(app)}</span>
                    </li>'''
        apps_html += '</ul>'
        
        sections.append({
            'title': 'APLICACIONES VERSATILES',
            'content': apps_html
        })
    
    # Generar HTML
    html = ""
    for section in sections:
        html += f'''
        <!-- SECCIONES DE CONTENIDO -->
        <div class="content-section" style="margin: 30px; padding: 30px; background: white; border-radius: 12px; box-shadow: 0 2px 10px rgba(0,0,0,0.05); border-left: 4px solid #FFC107;">
            <h3 style="color: #D32F2F; font-size: 24px; margin: 0 0 15px 0; font-weight: 700;">
                {section['title']}
            </h3>
            <div style="font-size: 16px; line-height: 1.8; color: #555;">
                {section['content']}
            </div>
        </div>'''
    
    return html

def generar_benefits_section_inline():
    """Genera la sección de beneficios con estilos inline."""
    return '''
        <!-- VENTAJAS COMPETITIVAS -->
        <div style="background: #f8f9fa; padding: 40px 30px; margin-top: 40px;">
            <h2 style="text-align: center; font-size: 32px; color: #333; margin-bottom: 40px; font-weight: 700;">
                POR QUE ELEGIR ESTE EQUIPO
            </h2>
            
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 25px;">
                <div class="benefit-card" style="background: white; border-radius: 12px; padding: 30px; text-align: center; box-shadow: 0 2px 10px rgba(0,0,0,0.05); border-top: 3px solid #ff6600;">
                    <div class="icon-circle" style="width: 70px; height: 70px; background: #fff3e0; border-radius: 50%; margin: 0 auto 20px; display: flex; align-items: center; justify-content: center;">
                        <svg width="40" height="40" viewBox="0 0 24 24" fill="#ff6600"><path d="M12 1L3 5v6c0 5.55 3.84 10.74 9 12 5.16-1.26 9-6.45 9-12V5l-9-4z"/></svg>
                    </div>
                    <h4 style="margin: 0 0 10px 0; color: #333; font-size: 18px; font-weight: 700;">GARANTIA OFICIAL</h4>
                    <p style="margin: 0; color: #666; font-size: 14px; line-height: 1.6;">Respaldo total del fabricante con servicio post-venta garantizado</p>
                </div>
                
                <div class="benefit-card" style="background: white; border-radius: 12px; padding: 30px; text-align: center; box-shadow: 0 2px 10px rgba(0,0,0,0.05); border-top: 3px solid #ff6600;">
                    <div class="icon-circle" style="width: 70px; height: 70px; background: #fff3e0; border-radius: 50%; margin: 0 auto 20px; display: flex; align-items: center; justify-content: center;">
                        <svg width="40" height="40" viewBox="0 0 24 24" fill="#ff6600"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/></svg>
                    </div>
                    <h4 style="margin: 0 0 10px 0; color: #333; font-size: 18px; font-weight: 700;">CALIDAD CERTIFICADA</h4>
                    <p style="margin: 0; color: #666; font-size: 14px; line-height: 1.6;">Productos que cumplen con las mas altas normas internacionales</p>
                </div>
                
                <div class="benefit-card" style="background: white; border-radius: 12px; padding: 30px; text-align: center; box-shadow: 0 2px 10px rgba(0,0,0,0.05); border-top: 3px solid #ff6600;">
                    <div class="icon-circle" style="width: 70px; height: 70px; background: #fff3e0; border-radius: 50%; margin: 0 auto 20px; display: flex; align-items: center; justify-content: center;">
                        <svg width="40" height="40" viewBox="0 0 24 24" fill="#ff6600"><path d="M22.7 19l-9.1-9.1c.9-2.3.4-5-1.5-6.9-2-2-5-2.4-7.4-1.3L9 6 6 9 1.6 4.7C.4 7.1.9 10.1 2.9 12.1c1.9 1.9 4.6 2.4 6.9 1.5l9.1 9.1c.4.4 1 .4 1.4 0l2.3-2.3c.5-.4.5-1.1.1-1.4z"/></svg>
                    </div>
                    <h4 style="margin: 0 0 10px 0; color: #333; font-size: 18px; font-weight: 700;">SERVICIO TECNICO</h4>
                    <p style="margin: 0; color: #666; font-size: 14px; line-height: 1.6;">Red nacional de servicio tecnico especializado y repuestos originales</p>
                </div>
                
                <div class="benefit-card" style="background: white; border-radius: 12px; padding: 30px; text-align: center; box-shadow: 0 2px 10px rgba(0,0,0,0.05); border-top: 3px solid #ff6600;">
                    <div class="icon-circle" style="width: 70px; height: 70px; background: #fff3e0; border-radius: 50%; margin: 0 auto 20px; display: flex; align-items: center; justify-content: center;">
                        <svg width="40" height="40" viewBox="0 0 24 24" fill="#ff6600"><path d="M11.8 10.9c-2.27-.59-3-1.2-3-2.15 0-1.09 1.01-1.85 2.7-1.85 1.78 0 2.44.85 2.5 2.1h2.21c-.07-1.72-1.12-3.3-3.21-3.81V3h-3v2.16c-1.94.42-3.5 1.68-3.5 3.61 0 2.31 1.91 3.46 4.7 4.13 2.5.6 3 1.48 3 2.41 0 .69-.49 1.79-2.7 1.79-2.06 0-2.87-.92-2.98-2.1h-2.2c.12 2.19 1.76 3.42 3.68 3.83V21h3v-2.15c1.95-.37 3.5-1.5 3.5-3.55 0-2.84-2.43-3.81-4.7-4.4z"/></svg>
                    </div>
                    <h4 style="margin: 0 0 10px 0; color: #333; font-size: 18px; font-weight: 700;">FINANCIACION</h4>
                    <p style="margin: 0; color: #666; font-size: 14px; line-height: 1.6;">Multiples opciones de pago y planes de financiacion a su medida</p>
                </div>
            </div>
        </div>
    '''

def generar_cta_section_inline(info, config):
    """Genera la sección CTA con estilos inline."""
    # Construir descripción detallada del producto
    marca = eliminar_tildes_y_especiales(info.get('marca', ''))
    modelo = eliminar_tildes_y_especiales(info.get('modelo', ''))
    potencia_kva = info.get('potencia_kva', '')
    nombre_producto = eliminar_tildes_y_especiales(info.get('nombre', 'este producto'))
    
    # Crear una descripción más específica del producto
    descripcion_producto = ""
    if marca and marca not in ['N/D', 'n/d', 'N/A', 'n/a', 'None', 'null', '']:
        descripcion_producto = f"Grupo Electrogeno {marca}"
        if modelo and modelo not in ['N/D', 'n/d', 'N/A', 'n/a', 'None', 'null', '']:
            descripcion_producto += f" {modelo}"
        if potencia_kva and str(potencia_kva) not in ['N/D', 'n/d', 'N/A', 'n/a', 'None', 'null', '']:
            descripcion_producto += f" de {potencia_kva} KVA"
    else:
        descripcion_producto = nombre_producto
    
    whatsapp = config.get('whatsapp', '541139563099')
    email = config.get('email', 'info@generadores.ar')
    pdf_url = info.get('pdf_url', '#')
    
    if pdf_url and not pdf_url.startswith('http'):
        pdf_url = f"https://storage.googleapis.com/fichas_tecnicas/{pdf_url}"
    
    # Mensaje de WhatsApp más elaborado y específico
    whatsapp_msg = f"Hola,%20estoy%20interesado%20en%20el%20{descripcion_producto.replace(' ', '%20')}.%20Vi%20este%20producto%20en%20su%20tienda%20online%20y%20me%20gustaria%20recibir%20mas%20informacion%20sobre%20precio,%20disponibilidad%20y%20condiciones%20de%20entrega.%20Muchas%20gracias."
    
    # Cuerpo del email más detallado
    email_body = f"""Hola,%0A%0AEstoy%20interesado%20en%20el%20{descripcion_producto.replace(' ', '%20')}%20que%20vi%20en%20su%20tienda%20online.%0A%0ACaracteristicas%20del%20producto%20consultado:%0A-%20Marca:%20{marca.replace(' ', '%20')}%0A-%20Modelo:%20{modelo.replace(' ', '%20')}%0A-%20Potencia:%20{str(potencia_kva).replace(' ', '%20')}%20KVA%0A%0AMe%20gustaria%20recibir%20informacion%20sobre:%0A-%20Precio%20y%20disponibilidad%0A-%20Condiciones%20de%20pago%20y%20financiacion%0A-%20Plazo%20de%20entrega%0A-%20Garantia%20y%20servicio%20tecnico%0A%0AMis%20datos%20de%20contacto%20son:%0ANombre:%20%0ATelefono:%20%0AEmpresa:%20%0ALocalidad:%20%0A%0AQuedo%20a%20la%20espera%20de%20su%20respuesta.%0A%0ASaludos%20cordiales"""
    
    return f'''
        <!-- CALL TO ACTION -->
        <div style="background: linear-gradient(135deg, #1a1a1a 0%, #333333 100%); padding: 50px 30px; text-align: center;">
            <h2 style="color: #FFC107; font-size: 32px; margin-bottom: 15px; font-weight: 700; text-transform: uppercase;">
                CONSULTE AHORA MISMO
            </h2>
            <p style="color: white; font-size: 18px; margin-bottom: 35px; opacity: 0.9;">
                Nuestros especialistas estan listos para asesorarlo
            </p>
            
            <div style="display: flex; flex-wrap: wrap; gap: 20px; justify-content: center;">
                
                <!-- Boton WhatsApp -->
                <a href="https://wa.me/{whatsapp}?text={whatsapp_msg}" target="_blank" 
                   class="btn-hover" style="display: inline-flex; align-items: center; gap: 12px; background: #25d366; color: white; padding: 18px 35px; text-decoration: none; border-radius: 30px; font-weight: 600; font-size: 16px; box-shadow: 0 4px 15px rgba(37,211,102,0.3);">
                    {ICONOS_SVG['whatsapp']}
                    CONSULTAR POR WHATSAPP
                </a>
                
                <!-- Boton PDF -->
                <a href="{pdf_url}" target="_blank" 
                   class="btn-hover" style="display: inline-flex; align-items: center; gap: 12px; background: #FFC107; color: #333; padding: 18px 35px; text-decoration: none; border-radius: 30px; font-weight: 600; font-size: 16px; box-shadow: 0 4px 15px rgba(255,193,7,0.3);">
                    {ICONOS_SVG['pdf'].replace('fill="#000"', 'fill="#333"')}
                    DESCARGAR FICHA TECNICA
                </a>
                
                <!-- Boton Email -->
                <a href="mailto:{email}?subject=Consulta%20sobre%20{descripcion_producto.replace(' ', '%20')}&body={email_body}" 
                   class="btn-hover" style="display: inline-flex; align-items: center; gap: 12px; background: #D32F2F; color: white; padding: 18px 35px; text-decoration: none; border-radius: 30px; font-weight: 600; font-size: 16px; box-shadow: 0 4px 15px rgba(211,47,47,0.3);">
                    {ICONOS_SVG['email']}
                    SOLICITAR COTIZACION
                </a>
                
            </div>
        </div>
    '''

def generar_contact_footer_inline(config):
    """Genera el footer de contacto con estilos inline."""
    return f'''
        <!-- FOOTER CONTACTO -->
        <div style="background: white; padding: 40px 30px; text-align: center; border-top: 3px solid #FFC107;">
            <div style="display: flex; flex-wrap: wrap; justify-content: center; gap: 40px; margin-bottom: 30px;">
                
                <div>
                    <p style="margin: 0; color: #666; font-size: 14px;">Telefono / WhatsApp</p>
                    <a href="https://wa.me/{config.get('whatsapp', '541139563099')}" class="contact-link" style="color: #ff6600; text-decoration: none; font-weight: 600; font-size: 18px;">{config.get('telefono_display', '+54 11 3956-3099')}</a>
                </div>
                
                <div>
                    <p style="margin: 0; color: #666; font-size: 14px;">Email</p>
                    <a href="mailto:{config.get('email', 'info@generadores.ar')}" class="contact-link" style="color: #ff6600; text-decoration: none; font-weight: 600; font-size: 18px;">{config.get('email', 'info@generadores.ar')}</a>
                </div>
                
                <div>
                    <p style="margin: 0; color: #666; font-size: 14px;">Sitio Web</p>
                    <a href="https://{config.get('website', 'www.generadores.ar')}" target="_blank" class="contact-link" style="color: #ff6600; text-decoration: none; font-weight: 600; font-size: 18px;">{config.get('website', 'www.generadores.ar')}</a>
                </div>
                
            </div>
            
            <div style="display: flex; flex-wrap: wrap; justify-content: center; gap: 30px; margin-bottom: 20px; padding-top: 20px; border-top: 1px solid #eee;">
                <div style="display: flex; align-items: center; gap: 8px; color: #666; transition: all 0.3s ease; cursor: pointer;" onmouseover="this.style.color='#ff6600'" onmouseout="this.style.color='#666'">
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="#ff6600"><path d="M12 1L3 5v6c0 5.55 3.84 10.74 9 12 5.16-1.26 9-6.45 9-12V5l-9-4z"/></svg> <span>Garantia Oficial</span>
                </div>
                <div style="display: flex; align-items: center; gap: 8px; color: #666; transition: all 0.3s ease; cursor: pointer;" onmouseover="this.style.color='#ff6600'" onmouseout="this.style.color='#666'">
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="#ff6600"><path d="M22.7 19l-9.1-9.1c.9-2.3.4-5-1.5-6.9-2-2-5-2.4-7.4-1.3L9 6 6 9 1.6 4.7C.4 7.1.9 10.1 2.9 12.1c1.9 1.9 4.6 2.4 6.9 1.5l9.1 9.1c.4.4 1 .4 1.4 0l2.3-2.3c.5-.4.5-1.1.1-1.4z"/></svg> <span>Servicio Tecnico Nacional</span>
                </div>
                <div style="display: flex; align-items: center; gap: 8px; color: #666; transition: all 0.3s ease; cursor: pointer;" onmouseover="this.style.color='#ff6600'" onmouseout="this.style.color='#666'">
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="#ff6600"><path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/></svg> <span>Repuestos Originales</span>
                </div>
                <div style="display: flex; align-items: center; gap: 8px; color: #666; transition: all 0.3s ease; cursor: pointer;" onmouseover="this.style.color='#ff6600'" onmouseout="this.style.color='#666'">
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="#ff6600"><path d="M11.8 10.9c-2.27-.59-3-1.2-3-2.15 0-1.09 1.01-1.85 2.7-1.85 1.78 0 2.44.85 2.5 2.1h2.21c-.07-1.72-1.12-3.3-3.21-3.81V3h-3v2.16c-1.94.42-3.5 1.68-3.5 3.61 0 2.31 1.91 3.46 4.7 4.13 2.5.6 3 1.48 3 2.41 0 .69-.49 1.79-2.7 1.79-2.06 0-2.87-.92-2.98-2.1h-2.2c.12 2.19 1.76 3.42 3.68 3.83V21h3v-2.15c1.95-.37 3.5-1.5 3.5-3.55 0-2.84-2.43-3.81-4.7-4.4z"/></svg> <span>Financiacion Disponible</span>
                </div>
            </div>
            
            <p style="color: #999; font-size: 13px; margin: 0;">
                Distribuidor Oficial | Todos los derechos reservados
            </p>
        </div>
    '''

def generar_css_hover_effects():
    """Genera los estilos CSS para efectos hover como en el modelo exacto."""
    return '''
    <style>
        /* Estilos para efectos hover */
        .card-hover {
            transition: all 0.3s ease;
            cursor: pointer;
        }
        .card-hover:hover {
            transform: translateY(-5px);
            box-shadow: 0 8px 25px rgba(0,0,0,0.15) !important;
        }
        
        .benefit-card {
            transition: all 0.3s ease;
        }
        .benefit-card:hover {
            transform: translateY(-8px);
            box-shadow: 0 10px 30px rgba(0,0,0,0.15) !important;
        }
        .benefit-card:hover .icon-circle {
            transform: scale(1.1);
            background: #ff6600 !important;
        }
        .benefit-card:hover .icon-circle svg {
            fill: white !important;
        }
        
        .icon-circle {
            transition: all 0.3s ease;
        }
        
        .btn-hover {
            transition: all 0.3s ease !important;
            position: relative;
            overflow: hidden;
        }
        .btn-hover:hover {
            transform: translateY(-3px) scale(1.05) !important;
            box-shadow: 0 8px 25px rgba(0,0,0,0.25) !important;
        }
        
        .spec-row {
            transition: all 0.2s ease;
        }
        .spec-row:hover {
            background: #fff3e0 !important;
            transform: translateX(5px);
        }
        
        .content-section {
            transition: all 0.3s ease;
        }
        .content-section:hover {
            transform: translateX(10px);
            box-shadow: 0 5px 20px rgba(0,0,0,0.1) !important;
            border-left-width: 8px !important;
        }
        
        .contact-link {
            transition: all 0.3s ease;
            display: inline-block;
        }
        .contact-link:hover {
            transform: scale(1.05);
            color: #ff8833 !important;
        }
        
        @keyframes pulse {
            0% { transform: scale(1); }
            50% { transform: scale(1.05); }
            100% { transform: scale(1); }
        }
        
        .special-feature {
            animation: pulse 2s infinite;
        }
        .special-feature:hover {
            animation: none;
            transform: scale(1.05);
        }
    </style>
    '''

def generar_descripcion_detallada_html_premium(row, config, modelo_ia=None, print_callback=print):
    """
    Función principal que orquesta la generación de la descripción HTML premium.
    """
    # 1. Extraer y procesar datos del producto
    info_inicial = extraer_info_tecnica(row)
    info = info_inicial.copy() # Usar datos base como fallback
    
    pdf_url = info_inicial.get('pdf_url', '')
    texto_pdf = None
    if pdf_url and str(pdf_url).lower() not in ['nan', 'none', '']:
        if not pdf_url.startswith('http'):
            pdf_url = f"https://storage.googleapis.com/fichas_tecnicas/{pdf_url}"
        texto_pdf = extraer_texto_pdf(pdf_url, print_callback)

    marketing_content = {}
    # 2. Enriquecer datos con IA si es posible
    if texto_pdf and modelo_ia:
        print("🤖 Iniciando extracción y generación de contenido con IA...")
        try:
            # Cargar prompts
            prompt_path = Path(__file__).parent / 'templates' / 'detailed_product_prompt.json'
            with open(prompt_path, 'r', encoding='utf-8') as f:
                prompts = json.load(f)

            # Fase 1: Extracción de datos
            prompt_extract = prompts['prompt_extract'].format(
                pdf_text=texto_pdf[:4000], # Limitar para no exceder tokens
                nombre=info.get('nombre'),
                familia=info.get('familia'),
                modelo=info.get('modelo'),
                marca=info.get('marca')
            )
            response_extract = modelo_ia.generate_content(prompt_extract)
            
            # Limpiar y parsear la respuesta JSON de la IA
            json_text = response_extract.text.strip().replace('```json', '').replace('```', '').strip()
            extracted_data = json.loads(json_text)
            info.update(extracted_data)
            print("✅ Datos extraídos con IA.")

            # Fase 2: Generación de contenido de marketing
            prompt_generate = prompts['prompt_generate'].format(product_data_json=json.dumps(info, indent=2))
            response_generate = modelo_ia.generate_content(prompt_generate)
            json_text_marketing = response_generate.text.strip().replace('```json', '').replace('```', '').strip()
            marketing_content = json.loads(json_text_marketing)
            print("✅ Contenido de marketing generado por IA.")

        except Exception as e:
            print(f"⚠️ Error en el proceso con IA, se usarán datos básicos y contenido por defecto: {e}")
            
    caracteristicas = validar_caracteristicas_producto(info, texto_pdf)
    
    # Integrar el contenido de marketing en info para que esté disponible en todas las funciones
    if marketing_content:
        info['marketing_content'] = marketing_content
    
    # 3. Generar cada sección del HTML
    titulo = generar_titulo_producto(info, caracteristicas)
    subtitulo = generar_subtitulo_producto(info, caracteristicas)
    
    # 4. Ensamblar el HTML final con estilo inline exacto
    nombre_producto = eliminar_tildes_y_especiales(info.get('nombre', 'este producto'))
    
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
        
        {generar_info_cards_inline(info, caracteristicas)}
        
        {generar_specs_table_inline(info)}
        
        {generar_feature_badge_inline(caracteristicas)}
        
        {generar_content_sections_inline(info, marketing_content)}
        
        {generar_benefits_section_inline()}
        
        {generar_cta_section_inline(info, config)}
        
        {generar_contact_footer_inline(config)}
        
    </div>
</body>
</html>"""
    
    return html_completo
