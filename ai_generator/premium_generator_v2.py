# -*- coding: utf-8 -*-
"""
Módulo para la generación de descripciones HTML premium de productos.
Versión 2.3 - Con iconos mejorados y visuales adicionales
"""
import re
import requests
import PyPDF2
import io
import fitz  # PyMuPDF
import json
from pathlib import Path
import unicodedata
import pytesseract
from PIL import Image

# Configurar la ruta de Tesseract-OCR
try:
    pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
except Exception:
    pass

# ============================================================================
# ICONOS SVG COMPLETOS MEJORADOS
# ============================================================================
ICONOS_SVG = {
    # Iconos principales de la UI (existentes)
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
    
    # Iconos técnicos existentes
    'voltaje': '<svg width="20" height="20" viewBox="0 0 24 24" fill="#D32F2F"><path d="M11 15h2v2h-2zm0-8h2v6h-2zm1-5C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2z"/></svg>',
    'frecuencia': '<svg width="20" height="20" viewBox="0 0 24 24" fill="#D32F2F"><path d="M16 6l-4 4-4-4v3l4 4 4-4zm0 6l-4 4-4-4v3l4 4 4-4z"/></svg>',
    'consumo': '<svg width="20" height="20" viewBox="0 0 24 24" fill="#D32F2F"><path d="M3 2v2h1v16h5v-8h6v8h5V4h1V2H3zm3 4h3v3H6V6zm6 0h3v3h-3V6zm6 0h3v3h-3V6z"/></svg>',
    'ruido': '<svg width="20" height="20" viewBox="0 0 24 24" fill="#D32F2F"><path d="M3 9v6h4l5 5V4L7 9H3zm13.5 3c0-1.77-1.02-3.29-2.5-4.03v8.05c1.48-.73 2.5-2.25 2.5-4.02z"/></svg>',
    'dimensiones': '<svg width="20" height="20" viewBox="0 0 24 24" fill="#D32F2F"><path d="M21 3H3c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h18c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm0 16H3V5h18v14z"/></svg>',
    'peso': '<svg width="20" height="20" viewBox="0 0 24 24" fill="#D32F2F"><path d="M12 3c-1.27 0-2.4.8-2.82 2H3v2h1.95l2 7c.17.59.71 1 1.32 1H15.73c.61 0 1.15-.41 1.32-1l2-7H21V5h-6.18C14.4 3.8 13.27 3 12 3zm0 2c.55 0 1 .45 1 1s-.45 1-1 1-1-.45-1-1 .45-1 1-1z"/></svg>',
    
    # NUEVOS ICONOS TÉCNICOS MEJORADOS
    'rpm': '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#ff6600" stroke-width="2"><circle cx="12" cy="12" r="9"/><path d="M12 6v6l4 2"/><path d="M6 12h.01M12 6h.01M17.66 17.66h.01M6 18h.01M18 12h.01"/></svg>',
    'tanque': '<svg width="20" height="20" viewBox="0 0 24 24" fill="#2196F3"><path d="M19 9v6c0 1.1-.9 2-2 2H7c-1.1 0-2-.9-2-2V9c0-1.1.9-2 2-2h10c1.1 0 2 .9 2 2zM7 11h10M12 7v4"/></svg>',
    'temperatura': '<svg width="20" height="20" viewBox="0 0 24 24" fill="#F44336"><path d="M15 13V5a3 3 0 0 0-6 0v8a5 5 0 1 0 6 0m-3-9a1 1 0 0 1 1 1v5.3a3 3 0 1 1-2 0V5a1 1 0 0 1 1-1z"/></svg>',
    'presion': '<svg width="20" height="20" viewBox="0 0 24 24" fill="#673AB7"><path d="M12 2C6.5 2 2 6.5 2 12s4.5 10 10 10 10-4.5 10-10S17.5 2 12 2zm0 18c-4.41 0-8-3.59-8-8s3.59-8 8-8 8 3.59 8 8-3.59 8-8 8zm-1-13h2v6h-2zm0 8h2v2h-2z"/></svg>',
    'gauge': '<svg width="20" height="20" viewBox="0 0 24 24" fill="#ff6600"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 18c-1.19 0-2.34-.26-3.33-.72l3.33-3.33 3.33 3.33c-.99.46-2.14.72-3.33.72zm4.24-3.76l-3.54-3.54c.43-.4.71-.96.71-1.58 0-1.21-1.01-2.14-2.22-2.07-.96.06-1.78.89-1.84 1.85-.07 1.21.86 2.22 2.07 2.22.62 0 1.18-.28 1.58-.71l3.54 3.54c-.7.89-1.63 1.58-2.7 1.95l-.54-3.55c-.1-.67-.72-1.13-1.38-1.02-.67.1-1.13.72-1.02 1.38l.39 2.53c-3.61-.41-6.42-3.45-6.42-7.14 0-3.98 3.23-7.21 7.21-7.21s7.21 3.23 7.21 7.21c0 1.87-.71 3.57-1.87 4.85z"/></svg>',
    'battery': '<svg width="20" height="20" viewBox="0 0 24 24" fill="#4CAF50"><path d="M16.67 4H15V2h-6v2H7.33C6.6 4 6 4.6 6 5.33v15.33c0 .74.6 1.34 1.33 1.34h9.33c.74 0 1.34-.6 1.34-1.33V5.33C18 4.6 17.4 4 16.67 4z"/></svg>',
    'gear': '<svg width="20" height="20" viewBox="0 0 24 24" fill="#757575"><path d="M12 15.5A3.5 3.5 0 0 1 8.5 12 3.5 3.5 0 0 1 12 8.5a3.5 3.5 0 0 1 3.5 3.5 3.5 3.5 0 0 1-3.5 3.5m7.43-2.53c.04-.32.07-.64.07-.97s-.03-.66-.07-1l2.11-1.63c.19-.15.24-.42.12-.64l-2-3.46c-.12-.22-.39-.31-.61-.22l-2.49 1c-.52-.39-1.06-.73-1.69-.98l-.37-2.65A.506.506 0 0 0 14 2h-4c-.25 0-.46.18-.5.42l-.37 2.65c-.63.25-1.17.59-1.69.98l-2.49-1c-.22-.09-.49 0-.61.22l-2 3.46c-.13.22-.07.49.12.64L4.57 11c-.04.34-.07.67-.07 1s.03.65.07.97l-2.11 1.66c-.19.15-.25.42-.12.64l2 3.46c.12.22.39.3.61.22l2.49-1.01c.52.4 1.06.74 1.69.99l.37 2.65c.04.24.25.42.5.42h4c.25 0 .46-.18.5-.42l.37-2.65c.63-.26 1.17-.59 1.69-.99l2.49 1.01c.22.08.49 0 .61-.22l2-3.46c.12-.22.07-.49-.12-.64l-2.11-1.66Z"/></svg>',
    'chart': '<svg width="20" height="20" viewBox="0 0 24 24" fill="#009688"><path d="M3 13h2v8H3zm4-8h2v16H7zm4-2h2v18h-2zm4 4h2v14h-2zm4-2h2v16h-2z"/></svg>',
    'clock': '<svg width="20" height="20" viewBox="0 0 24 24" fill="#FF9800"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 18c-4.41 0-8-3.59-8-8s3.59-8 8-8 8 3.59 8 8-3.59 8-8 8zm.5-13H11v6l5.2 3.1.8-1.3-4.5-2.7z"/></svg>',
    'plug': '<svg width="20" height="20" viewBox="0 0 24 24" fill="#795548"><path d="M16 7V3h-2v4h-4V3H8v4h-.5C6 7 5 8 5 9.5v5.5L4 17v4h16v-4l-1-2v-5.5C19 8 18 7 16.5 7H16z"/></svg>',
    
    # Iconos de aplicaciones
    'hospital': '<svg width="20" height="20" viewBox="0 0 24 24" fill="#4caf50"><path d="M19 8h-2V6c0-1.1-.9-2-2-2H9c-1.1 0-2 .9-2 2v2H5c-1.1 0-2 .9-2 2v10h18V10c0-1.1-.9-2-2-2zM9 6h6v2H9V6zm7 10h-3v3h-2v-3H8v-2h3v-3h2v3h3v2z"/></svg>',
    'industria': '<svg width="20" height="20" viewBox="0 0 24 24" fill="#795548"><path d="M9 2v6l3-3 3 3V2H9zM5 11v10h4v-5h6v5h4V11l-7-5-7 5z"/></svg>',
    'construccion': '<svg width="20" height="20" viewBox="0 0 24 24" fill="#ff6600"><path d="M22 11V9L12 2 2 9v2h2v9h5v-6h6v6h5v-9h2z"/></svg>',
    'datacenter': '<svg width="20" height="20" viewBox="0 0 24 24" fill="#2196F3"><path d="M4 3h16a1 1 0 011 1v4a1 1 0 01-1 1H4a1 1 0 01-1-1V4a1 1 0 011-1zm0 8h16a1 1 0 011 1v4a1 1 0 01-1 1H4a1 1 0 01-1-1v-4a1 1 0 011-1zM6 5h.01M6 13h.01M10 5h.01M10 13h.01"/></svg>',
    'campo': '<svg width="20" height="20" viewBox="0 0 24 24" fill="#4caf50"><path d="M12 2c-4.42 0-8 3.58-8 8s3.58 8 8 8 8-3.58 8-8-3.58-8-8-8zm0 14c-3.31 0-6-2.69-6-6s2.69-6 6-6 6 2.69 6 6-2.69 6-6 6z"/><path d="M8 10l2 2 4-4"/></svg>',
    'mineria': '<svg width="20" height="20" viewBox="0 0 24 24" fill="#607D8B"><path d="M23 12l-2.44-2.78.34-3.68-3.61-.82-1.89-3.18L12 3 8.6 1.54 6.71 4.72l-3.61.81.34 3.68L1 12l2.44 2.78-.34 3.69 3.61.82 1.89 3.18L12 21l3.4 1.46 1.89-3.18 3.61-.82-.34-3.68L23 12z"/></svg>',
    
    # Iconos de características especiales
    'insonorizado': '<svg width="20" height="20" viewBox="0 0 24 24" fill="#673AB7"><path d="M3 9v6h4l5 5V4L7 9H3zm13.5 3c0-1.77-1.02-3.29-2.5-4.03v8.05c1.48-.73 2.5-2.25 2.5-4.02zM14 3.23v2.06c2.89.86 5 3.54 5 6.71s-2.11 5.85-5 6.71v2.06c4.01-.91 7-4.49 7-8.77s-2.99-7.86-7-8.77z"/></svg>',
    'automatico': '<svg width="20" height="20" viewBox="0 0 24 24" fill="#FF5722"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm3.5 6L12 10.5 8.5 8 11 5.5 12 6.55l3.5-3.5 1 1z"/></svg>',
    'remoto': '<svg width="20" height="20" viewBox="0 0 24 24" fill="#3F51B5"><path d="M12 2C7.05 2 3 6.05 3 11c0 2.76 1.12 5.26 2.93 7.07L12 24l6.07-6.07C19.88 16.26 21 13.76 21 11c0-4.95-4.05-9-9-9zm0 4c2.76 0 5 2.24 5 5s-2.24 5-5 5-5-2.24-5-5 2.24-5 5-5z"/></svg>',
    'tta': '<svg width="20" height="20" viewBox="0 0 24 24" fill="#9C27B0"><path d="M6.62 10.79c1.44 2.83 3.76 5.14 6.59 6.59l2.2-2.2c.27-.27.67-.36 1.02-.24 1.12.37 2.33.57 3.57.57.55 0 1 .45 1 1V20c0 .55-.45 1-1 1-9.39 0-17-7.61-17-17 0-.55.45-1 1-1h3.5c.55 0 1 .45 1 1 0 1.25.2 2.45.57 3.57.11.35.03.74-.25 1.02l-2.2 2.2z"/></svg>',
    'inverter': '<svg width="20" height="20" viewBox="0 0 24 24" fill="#00BCD4"><path d="M12 2l-5.5 9h11z"/><circle cx="17.5" cy="17.5" r="4.5"/><path d="M3 13.5h8v8H3z"/></svg>',
    
    # Iconos de estado
    'check_circle': '<svg width="20" height="20" viewBox="0 0 24 24" fill="#4caf50"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/></svg>',
    'warning': '<svg width="20" height="20" viewBox="0 0 24 24" fill="#ff9800"><path d="M1 21h22L12 2 1 21zm12-3h-2v-2h2v2zm0-4h-2v-4h2v4z"/></svg>',
    'info': '<svg width="20" height="20" viewBox="0 0 24 24" fill="#2196f3"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-6h2v6zm0-8h-2V7h2v2z"/></svg>',
    'star': '<svg width="20" height="20" viewBox="0 0 24 24" fill="#ffc107"><path d="M12 17.27L18.18 21l-1.64-7.03L22 9.24l-7.19-.61L12 2 9.19 8.63 2 9.24l5.46 4.73L5.82 21z"/></svg>',
    'award': '<svg width="20" height="20" viewBox="0 0 24 24" fill="#ff6600"><path d="M12 1L3 5v6c0 5.55 3.84 10.74 9 12 5.16-1.26 9-6.45 9-12V5l-9-4z"/></svg>',
    
    # Iconos para listas
    'check': '<svg width="20" height="20" viewBox="0 0 24 24" fill="#4caf50"><path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z"/></svg>',
    'dot': '<svg width="20" height="20" viewBox="0 0 24 24" fill="#ff6600"><circle cx="12" cy="12" r="6"/></svg>',
    'arrow_right': '<svg width="20" height="20" viewBox="0 0 24 24" fill="#2196f3"><path d="M10 6L8.59 7.41 13.17 12l-4.58 4.59L10 18l6-6z"/></svg>',
    'autonomia_L': '<svg width="20" height="20" viewBox="0 0 24 24" fill="#4caf50"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-1 14H9V8h4v2h-2v4z"/></svg>',
    'wrench': '<svg width="20" height="20" viewBox="0 0 24 24" fill="#ff6600"><path d="M22.7 19l-9.1-9.1c.9-2.3.4-5-1.5-6.9-2-2-5-2.4-7.4-1.3L9 6 6 9 1.6 4.7C.4 7.1.9 10.1 2.9 12.1c1.9 1.9 4.6 2.4 6.9 1.5l9.1 9.1c.4.4 1 .4 1.4 0l2.3-2.3c.5-.4.5-1.1.1-1.4z"/></svg>',
    'lightning': '<svg width="20" height="20" viewBox="0 0 24 24" fill="#ff6600"><path d="M7 2v11h3v9l7-12h-4l4-8z"/></svg>',
    'location': '<svg width="20" height="20" viewBox="0 0 24 24" fill="#4caf50"><path d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13S15.87 2 12 2zm0 9.5c-1.38 0-2.5-1.12-2.5-2.5s1.12-2.5 2.5-2.5 2.5 1.12 2.5 2.5-1.12 2.5-2.5 2.5z"/></svg>',
    'business': '<svg width="20" height="20" viewBox="0 0 24 24" fill="#4caf50"><path d="M12 7V3H2v18h20V7H12zM6 19H4v-2h2v2zm0-4H4v-2h2v2zm0-4H4V9h2v2zm10 8H8v-2h2v-2H8V9h8v10zm-2-8h-2v2h2v-2z"/></svg>'
}

# ============================================================================
# FUNCIONES AUXILIARES MEJORADAS
# ============================================================================
def obtener_icono_para_item(texto_item):
    """Devuelve un icono SVG basado en palabras clave en el texto del item."""
    texto_lower = texto_item.lower()
    
    # Mapeo mejorado de palabras clave a iconos
    keyword_icon_map = {
        # Potencia y energía
        'potencia': 'potencia',
        'kva': 'potencia',
        'kw': 'potencia',
        'energia': 'lightning',
        'electrica': 'plug',
        'electrico': 'plug',
        
        # Motor y mecánica
        'motor': 'motor',
        'cummins': 'motor',
        'perkins': 'motor',
        'rpm': 'rpm',
        'cilindrada': 'motor',
        
        # Combustible
        'combustible': 'diesel',
        'diesel': 'diesel',
        'gas': 'gas',
        'nafta': 'nafta',
        'consumo': 'consumo',
        'tanque': 'tanque',
        
        # Control y automatización
        'automatico': 'automatico',
        'manual': 'gear',
        'control': 'gear',
        'inteligente': 'automatico',
        'remoto': 'remoto',
        'transferencia': 'tta',
        
        # Características especiales
        'insonorizado': 'insonorizado',
        'cabina': 'insonorizado',
        'silencioso': 'ruido',
        'bajo ruido': 'ruido',
        'inverter': 'inverter',
        
        # Aplicaciones
        'hospital': 'hospital',
        'clinica': 'hospital',
        'medico': 'hospital',
        'industria': 'industria',
        'fabrica': 'industria',
        'construccion': 'construccion',
        'obra': 'construccion',
        'data center': 'datacenter',
        'servidor': 'datacenter',
        'campo': 'campo',
        'rural': 'campo',
        'mineria': 'mineria',
        
        # Beneficios
        'garantia': 'shield',
        'calidad': 'quality',
        'certificado': 'award',
        'servicio': 'tools',
        'tecnico': 'tools',
        'financiacion': 'money',
        'ahorro': 'money',
        
        # Estados y condiciones
        'temperatura': 'temperatura',
        'presion': 'presion',
        'tiempo': 'clock',
        'horas': 'clock',
        'autonomia': 'autonomia_L',
        
        # Default para otros casos
        'mantenimiento': 'wrench',
        'instalacion': 'wrench',
        'ubicacion': 'location',
        'empresa': 'business'
    }
    
    # Buscar coincidencias
    for keyword, icon in keyword_icon_map.items():
        if keyword in texto_lower:
            return ICONOS_SVG.get(icon, ICONOS_SVG['check'])
    
    # Default icon
    return ICONOS_SVG['dot']

def generar_badges_caracteristicas(info, caracteristicas):
    """Genera badges visuales para características especiales."""
    badges_html = ""
    
    # Definir badges posibles con sus colores
    badges_config = {
        'tiene_tta': {
            'texto': 'TRANSFERENCIA AUTOMÁTICA',
            'color': '#9C27B0',
            'icono': 'tta'
        },
        'tiene_cabina': {
            'texto': 'CABINA INSONORIZADA',
            'color': '#673AB7',
            'icono': 'insonorizado'
        },
        'es_inverter': {
            'texto': 'TECNOLOGÍA INVERTER',
            'color': '#00BCD4',
            'icono': 'inverter'
        },
        'arranque_automatico': {
            'texto': 'ARRANQUE AUTOMÁTICO',
            'color': '#FF5722',
            'icono': 'automatico'
        },
        'control_remoto': {
            'texto': 'CONTROL REMOTO',
            'color': '#3F51B5',
            'icono': 'remoto'
        }
    }
    
    # Generar HTML para cada característica activa
    for key, config in badges_config.items():
        if caracteristicas.get(key) or (key == 'arranque_automatico' and (info.get('tipo_arranque') or '').lower() == 'automatico'):
            icono = ICONOS_SVG.get(config['icono'], '')
            badges_html += f'''
            <span class="special-feature" style="background: {config['color']}; color: white; padding: 5px 15px; border-radius: 20px; font-size: 12px; font-weight: 600; display: inline-flex; align-items: center; gap: 8px; margin: 5px;">
                <span style="width: 16px; height: 16px;">{icono.replace('width="20"', 'width="16"').replace('height="20"', 'height="16"').replace('fill="#', 'fill="white" fill-opacity="0.9" old-fill="#')}</span>
                {config['texto']}
            </span>
            '''
    
    # Agregar badges basados en especificaciones
    if info.get('nivel_sonoro_dba_7m') and float(str(info.get('nivel_sonoro_dba_7m', '100')).replace('dBA', '').strip()) < 75:
        badges_html += f'''
        <span class="special-feature" style="background: #4CAF50; color: white; padding: 5px 15px; border-radius: 20px; font-size: 12px; font-weight: 600; display: inline-flex; align-items: center; gap: 8px; margin: 5px;">
            <span style="width: 16px; height: 16px;">{ICONOS_SVG['ruido'].replace('width="20"', 'width="16"').replace('height="20"', 'height="16"').replace('fill="#', 'fill="white" fill-opacity="0.9" old-fill="#')}</span>
            BAJO NIVEL SONORO
        </span>
        '''
    
    return badges_html

def calcular_eficiencia_universal(info):
    """
    Calcula eficiencia para CUALQUIER tipo de generador o equipo con motor
    """
    # Extraer valores necesarios
    tipo_combustible = info.get('combustible', '').lower()
    consumo_str = info.get('consumo_75_carga_valor') or info.get('consumo_max_carga_valor') or info.get('consumo', '')
    
    # Extraer valor numérico del consumo
    try:
        import re
        match = re.search(r'([\d.]+)', str(consumo_str))
        if match:
            consumo_valor = float(match.group(1))
        else:
            return {
                'porcentaje': 50,
                'texto': 'Información no disponible',
                'color': '#9E9E9E',
                'nota': ''
            }
    except:
        return {
            'porcentaje': 50,
            'texto': 'Información no disponible',
            'color': '#9E9E9E',
            'nota': ''
        }
    
    # Obtener potencia en KW
    potencia_kw = obtener_potencia_kw(info)
    
    if potencia_kw == 0:
        return {
            'porcentaje': 50,
            'texto': 'Información no disponible',
            'color': '#9E9E9E',
            'nota': ''
        }
    
    # Cálculos específicos por tipo de combustible
    eficiencia_data = {}
    
    if tipo_combustible in ['nafta', 'gasolina', 'gasoline', 'bencina']:
        # Generadores nafteros: ~0.4-0.5 L/h por KW es normal
        consumo_esperado = potencia_kw * 0.45
        ratio = consumo_valor / consumo_esperado if consumo_esperado > 0 else 1
        
        if ratio < 0.8:  # Consume menos del 80% esperado
            eficiencia_data = {
                'porcentaje': 90,
                'texto': 'Excelente Eficiencia',
                'color': '#4CAF50',
                'nota': 'Consumo optimizado para nafta'
            }
        elif ratio < 1.2:  # Entre 80% y 120% esperado
            eficiencia_data = {
                'porcentaje': 60,
                'texto': 'Eficiencia Normal',
                'color': '#FFC107',
                'nota': 'Consumo típico para generadores nafteros'
            }
        else:  # Más del 120% esperado
            eficiencia_data = {
                'porcentaje': 30,
                'texto': 'Consumo Elevado',
                'color': '#FF5722',
                'nota': 'Considerar mantenimiento del motor'
            }
    
    elif tipo_combustible in ['diesel', 'gasoil', 'diésel']:
        # Generadores diesel: ~0.2-0.3 L/h por KW es normal
        consumo_esperado = potencia_kw * 0.25
        ratio = consumo_valor / consumo_esperado if consumo_esperado > 0 else 1
        
        if ratio < 0.9:
            eficiencia_data = {
                'porcentaje': 95,
                'texto': 'Eficiencia Superior',
                'color': '#1B5E20',
                'nota': 'Motor diesel de alta eficiencia'
            }
        elif ratio < 1.1:
            eficiencia_data = {
                'porcentaje': 75,
                'texto': 'Buena Eficiencia',
                'color': '#4CAF50',
                'nota': 'Consumo óptimo para diesel'
            }
        elif ratio < 1.3:
            eficiencia_data = {
                'porcentaje': 55,
                'texto': 'Eficiencia Estándar',
                'color': '#FFC107',
                'nota': 'Consumo dentro del rango esperado'
            }
        else:
            eficiencia_data = {
                'porcentaje': 30,
                'texto': 'Consumo Alto',
                'color': '#FF5722',
                'nota': 'Revisar inyectores y filtros'
            }
    
    elif tipo_combustible in ['gas', 'gnc', 'glp', 'gas natural', 'propano']:
        # Generadores a gas: ~0.3-0.4 m³/h por KW
        consumo_esperado = potencia_kw * 0.35
        ratio = consumo_valor / consumo_esperado if consumo_esperado > 0 else 1
        
        if ratio < 0.85:
            eficiencia_data = {
                'porcentaje': 85,
                'texto': 'Alta Eficiencia',
                'color': '#4CAF50',
                'nota': 'Excelente aprovechamiento del gas'
            }
        elif ratio < 1.15:
            eficiencia_data = {
                'porcentaje': 65,
                'texto': 'Eficiencia Normal',
                'color': '#03A9F4',
                'nota': 'Consumo típico para gas'
            }
        else:
            eficiencia_data = {
                'porcentaje': 35,
                'texto': 'Consumo Elevado',
                'color': '#FF5722',
                'nota': 'Verificar presión de gas'
            }
    
    else:
        # Default para otros tipos o combustibles no especificados
        # Usar lógica genérica basada en potencia
        litros_por_hora_por_kw = consumo_valor / potencia_kw
        
        if litros_por_hora_por_kw < 0.3:
            eficiencia_data = {
                'porcentaje': 80,
                'texto': 'Buena Eficiencia',
                'color': '#4CAF50',
                'nota': 'Consumo eficiente'
            }
        elif litros_por_hora_por_kw < 0.5:
            eficiencia_data = {
                'porcentaje': 60,
                'texto': 'Eficiencia Estándar',
                'color': '#FFC107',
                'nota': 'Consumo moderado'
            }
        else:
            eficiencia_data = {
                'porcentaje': 40,
                'texto': 'Consumo Alto',
                'color': '#FF5722',
                'nota': 'Consumo elevado para la potencia'
            }
    
    return eficiencia_data

def obtener_potencia_kw(info):
    """
    Obtiene la potencia en KW desde diferentes campos posibles
    """
    # Primero buscar KW directamente
    if info.get('potencia_kw'):
        try:
            return float(str(info['potencia_kw']).replace('KW', '').replace(',', '.').strip())
        except:
            pass
    
    # Si no, convertir desde KVA (factor 0.8)
    if info.get('potencia_kva'):
        try:
            kva = float(str(info['potencia_kva']).replace('KVA', '').replace(',', '.').strip())
            return kva * 0.8
        except:
            pass
    
    # Si hay potencia en HP, convertir (1 HP = 0.746 KW)
    if info.get('potencia_hp'):
        try:
            hp = float(str(info['potencia_hp']).replace('HP', '').replace(',', '.').strip())
            return hp * 0.746
        except:
            pass
    
    # Si hay potencia en Watts
    if info.get('potencia_w') or info.get('potencia_max_w'):
        try:
            watts = float(str(info.get('potencia_w', info.get('potencia_max_w', '0'))).replace('W', '').replace(',', '.').strip())
            return watts / 1000
        except:
            pass
    
    return 0

def generar_grafico_consumo_universal(info):
    """
    Genera un gráfico visual de consumo universal para cualquier producto
    """
    # Obtener datos de eficiencia calculados
    eficiencia_data = info.get('eficiencia_data', calcular_eficiencia_universal(info))
    
    # Extraer valores
    porcentaje = eficiencia_data.get('porcentaje', 50)
    texto_eficiencia = eficiencia_data.get('texto', 'Eficiencia Media')
    color_principal = eficiencia_data.get('color', '#FFC107')
    nota = eficiencia_data.get('nota', '')
    
    # Obtener consumo para mostrar
    consumo_str = info.get('consumo') or info.get('consumo_75_carga_valor') or 'N/D'
    
    return f'''
    <div style="margin-top: 10px; background: #f5f5f5; border-radius: 8px; padding: 10px;">
        <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
            <span style="font-size: 11px; color: #666; font-weight: 600;">EFICIENCIA DE CONSUMO</span>
            <span style="font-size: 11px; color: {color_principal}; font-weight: 600;">{texto_eficiencia}</span>
        </div>
        <div style="background: #e0e0e0; height: 8px; border-radius: 4px; overflow: hidden; position: relative;">
            <div style="background: linear-gradient(to right, #4CAF50 0%, #8BC34A 25%, #FFC107 50%, #FF9800 75%, #F44336 100%); height: 100%; width: 100%; opacity: 0.3;"></div>
            <div style="position: absolute; top: 0; left: 0; background: {color_principal}; width: {porcentaje}%; height: 100%; transition: width 1s ease; box-shadow: 0 0 4px rgba(0,0,0,0.2);"></div>
        </div>
        <div style="display: flex; justify-content: space-between; margin-top: 5px;">
            <span style="font-size: 10px; color: #4CAF50;">Eficiente</span>
            <span style="font-size: 10px; color: #666;">{consumo_str}</span>
            <span style="font-size: 10px; color: #F44336;">Alto consumo</span>
        </div>
        {f'<div style="text-align: center; margin-top: 5px;"><span style="font-size: 9px; color: #999;">{nota}</span></div>' if nota else ''}
    </div>
    '''

def generar_grafico_consumo(consumo_str):
    """Genera un pequeño gráfico SVG de consumo - DEPRECADO, usar generar_grafico_consumo_universal"""
    return generar_grafico_consumo_universal({'consumo': consumo_str})

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

def extraer_contenido_pdf(pdf_url, print_callback=print):
    """
    Extrae texto y tablas de un PDF desde una URL, usando OCR como fallback.
    Devuelve un diccionario con 'text' y 'tables'.
    """
    try:
        response = requests.get(pdf_url, timeout=10)
        response.raise_for_status()
        pdf_bytes = response.content
        
        pdf_document = fitz.open(stream=pdf_bytes, filetype="pdf")  # type: ignore
        texto_completo = ""
        tablas_markdown = []
        texto_ocr = ""

        for page_num in range(pdf_document.page_count):
            page = pdf_document[page_num]
            
            # 1. Extracción de texto nativo
            texto_pagina = page.get_text("text")
            texto_completo += texto_pagina
            
            # 2. Extracción de tablas
            tabla_finder = page.find_tables()
            if tabla_finder.tables:
                print_callback(f"  -> Encontradas {len(tabla_finder.tables)} tablas en la página {page_num + 1}")
                for i, tabla in enumerate(tabla_finder.tables):
                    header = " | ".join(str(h) for h in tabla.header.names)
                    alignment = " | ".join(["---"] * len(tabla.header.names))
                    rows = "\n".join([" | ".join(str(cell) for cell in row) for row in tabla.extract()])
                    markdown_table = f"Tabla {i+1}:\n{header}\n{alignment}\n{rows}\n"
                    tablas_markdown.append(markdown_table)

            # 3. Lógica de OCR como fallback
            # Si la página tiene muy poco texto nativo, es probable que sea una imagen.
            if len(texto_pagina.strip()) < 100:
                print_callback(f"  -> ⚠️ Página {page_num + 1} con poco texto. Aplicando OCR...")
                try:
                    pix = page.get_pixmap(dpi=300)  # Renderizar a alta resolución
                    img_bytes = pix.tobytes("png")
                    imagen = Image.open(io.BytesIO(img_bytes))
                    # Usar español como idioma para el OCR
                    texto_ocr_pagina = pytesseract.image_to_string(imagen, lang='spa')
                    if texto_ocr_pagina:
                        print_callback(f"  -> ✅ OCR extrajo {len(texto_ocr_pagina)} caracteres de la página {page_num + 1}.")
                        texto_ocr += texto_ocr_pagina + "\n"
                except Exception as ocr_error:
                    print_callback(f"  -> ❌ Error durante el OCR en la página {page_num + 1}: {ocr_error}")

        pdf_document.close()
        
        # Combinar texto nativo con texto de OCR
        texto_final_combinado = texto_completo + "\n\n--- OCR TEXT ---\n" + texto_ocr
        
        contenido_extraido = {
            "text": texto_final_combinado,
            "tables_markdown": "\n".join(tablas_markdown)
        }

        if texto_final_combinado.strip() or tablas_markdown:
            print_callback(f"✅ Contenido extraído correctamente de {pdf_url} (con OCR si fue necesario).")
            return contenido_extraido
        else:
            print_callback(f"⚠️ El PDF en {pdf_url} parece estar completamente vacío.")
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
        'motor': [
            r'Motor[:\s]+([A-Za-z0-9\s\-\.]+?)(?:\n|$)',
            r'Marca del motor[:\s]+([A-Za-z0-9\s\-\.]+?)(?:\n|$)',
            r'Motor marca[:\s]+([A-Za-z0-9\s\-\.]+?)(?:\n|$)',
            r'ENGINE[:\s]+([A-Za-z0-9\s\-\.]+?)(?:\n|$)',
            r'Motor\s*:\s*([A-Za-z0-9\s\-\.]+?)(?:\n|$)',
            r'Tipo de motor[:\s]+([A-Za-z0-9\s\-\.]+?)(?:\n|$)'
        ],
        'alternador': r'Alternador\s*[:\s]*([A-Za-z0-9\.\-\s]+)',
        'cilindrada': r'Cilindrada\s*\(cc\)\s*[:\s]*(\d+)'
    }
    
    for campo, patron in patrones.items():
        # Si es una lista de patrones, probar cada uno
        if isinstance(patron, list):
            for p in patron:
                match = re.search(p, texto_pdf, re.IGNORECASE | re.MULTILINE)
                if match:
                    valor_extraido = match.group(1).strip()
                    # Siempre se da prioridad al dato del PDF
                    info_actualizada[campo] = valor_extraido
                    print_callback(f"  -> Dato extraído de PDF: {campo} = {valor_extraido}")
                    break  # Salir al encontrar el primer match
        else:
            match = re.search(patron, texto_pdf, re.IGNORECASE | re.DOTALL)
            if match:
                valor_extraido = match.group(1).strip()
                # Siempre se da prioridad al dato del PDF
                info_actualizada[campo] = valor_extraido
                print_callback(f"  -> Dato extraído de PDF: {campo} = {valor_extraido}")
            
    return info_actualizada

def detectar_caracteristicas_universal(info, texto_pdf=''):
    """
    Detecta características especiales para CUALQUIER producto universalmente
    """
    caracteristicas = {
        'tiene_tta': False,
        'tiene_cabina': False,
        'es_inverter': False,
        'es_portatil': False,
        'arranque_automatico': False,
        'es_trifasico': False,
        'es_monofasico': False,
        'tiene_control_remoto': False,
        'es_industrial': False,
        'tipo_combustible': '',
        'badges_especiales': [],
        'caracteristicas_adicionales': []
    }
    
    # Combinar TODA la información disponible para búsqueda
    texto_busqueda = ' '.join(str(v) for v in info.values() if v).lower()
    if texto_pdf:
        texto_busqueda += ' ' + texto_pdf.lower()
    
    # Detectar tipo de combustible universalmente
    if any(fuel in texto_busqueda for fuel in ['nafta', 'gasolina', 'gasoline', 'bencina']):
        caracteristicas['tipo_combustible'] = 'nafta'
    elif any(fuel in texto_busqueda for fuel in ['diesel', 'gasoil', 'diésel']):
        caracteristicas['tipo_combustible'] = 'diesel'
    elif any(fuel in texto_busqueda for fuel in ['gas natural', 'gnc', 'glp', 'propano']):
        caracteristicas['tipo_combustible'] = 'gas'
    else:
        # Intentar obtener del campo directo
        caracteristicas['tipo_combustible'] = info.get('combustible', 'diesel').lower()
    
    # Detección de características técnicas principales
    if any(keyword in texto_busqueda for keyword in ['tta', 'transferencia automática', 'transferencia automatica', 'ats', 'automatic transfer']):
        caracteristicas['tiene_tta'] = True
        caracteristicas['badges_especiales'].append({
            'texto': 'TRANSFERENCIA AUTOMÁTICA',
            'color': '#9C27B0',
            'icono': 'tta'
        })
    
    if any(keyword in texto_busqueda for keyword in ['cabinado', 'insonorizado', 'soundproof', 'silent', 'cabina acustica', 'cabina acústica']):
        caracteristicas['tiene_cabina'] = True
        caracteristicas['badges_especiales'].append({
            'texto': 'INSONORIZADO',
            'color': '#2196F3',
            'icono': 'insonorizado'
        })
    
    if 'inverter' in texto_busqueda:
        caracteristicas['es_inverter'] = True
        caracteristicas['badges_especiales'].append({
            'texto': 'TECNOLOGÍA INVERTER',
            'color': '#00BCD4',
            'icono': 'inverter'
        })
    
    # Detección de portabilidad basada en múltiples factores
    peso_str = str(info.get('peso_kg', '999')).replace('kg', '').strip()
    try:
        peso = float(peso_str)
        if peso < 100 or any(word in texto_busqueda for word in ['portátil', 'portatil', 'portable', 'movil', 'móvil']):
            caracteristicas['es_portatil'] = True
            caracteristicas['badges_especiales'].append({
                'texto': 'PORTÁTIL',
                'color': '#FF9800',
                'icono': 'portable'
            })
    except:
        # Si no hay peso, buscar por palabras clave
        if any(word in texto_busqueda for word in ['portátil', 'portatil', 'portable']):
            caracteristicas['es_portatil'] = True
            caracteristicas['badges_especiales'].append({
                'texto': 'PORTÁTIL',
                'color': '#FF9800',
                'icono': 'portable'
            })
    
    # Detección de arranque
    if any(keyword in texto_busqueda for keyword in ['arranque automático', 'arranque automatico', 'autostart', 'automatic start', 'arranque eléctrico']):
        caracteristicas['arranque_automatico'] = True
        caracteristicas['badges_especiales'].append({
            'texto': 'ARRANQUE AUTOMÁTICO',
            'color': '#FF5722',
            'icono': 'automatico'
        })
    elif any(keyword in texto_busqueda for keyword in ['arranque remoto', 'control remoto', 'remote control', 'remote start']):
        caracteristicas['tiene_control_remoto'] = True
        caracteristicas['badges_especiales'].append({
            'texto': 'CONTROL REMOTO',
            'color': '#3F51B5',
            'icono': 'remoto'
        })
    
    # Detección de sistema eléctrico
    if any(keyword in texto_busqueda for keyword in ['trifásico', 'trifasico', '3 fases', 'three phase', '380v', '400v']):
        caracteristicas['es_trifasico'] = True
        caracteristicas['badges_especiales'].append({
            'texto': 'TRIFÁSICO',
            'color': '#673AB7',
            'icono': 'trifasico'
        })
    elif any(keyword in texto_busqueda for keyword in ['monofásico', 'monofasico', '1 fase', 'single phase', '220v', '230v']):
        caracteristicas['es_monofasico'] = True
    
    # Detección de uso industrial
    if any(keyword in texto_busqueda for keyword in ['industrial', 'heavy duty', 'trabajo pesado', 'uso intensivo', 'continuo']):
        caracteristicas['es_industrial'] = True
        caracteristicas['badges_especiales'].append({
            'texto': 'USO INDUSTRIAL',
            'color': '#795548',
            'icono': 'industria'
        })
    
    # Características adicionales por categoría de producto
    categoria = info.get('familia', '').lower()
    
    # Para compresores
    if 'compresor' in categoria:
        if any(word in texto_busqueda for word in ['libre de aceite', 'oil free', 'sin aceite']):
            caracteristicas['badges_especiales'].append({
                'texto': 'LIBRE DE ACEITE',
                'color': '#4CAF50',
                'icono': 'eco'
            })
    
    # Para hidrolavadoras
    if 'hidrolavadora' in categoria:
        if any(word in texto_busqueda for word in ['agua caliente', 'hot water', 'termica']):
            caracteristicas['badges_especiales'].append({
                'texto': 'AGUA CALIENTE',
                'color': '#F44336',
                'icono': 'temperatura'
            })
    
    # Para motobombas
    if 'motobomba' in categoria or 'bomba' in categoria:
        if any(word in texto_busqueda for word in ['autocebante', 'self priming']):
            caracteristicas['badges_especiales'].append({
                'texto': 'AUTOCEBANTE',
                'color': '#03A9F4',
                'icono': 'water'
            })
    
    # Certificaciones y normativas
    if any(cert in texto_busqueda for cert in ['ce', 'iso', 'certificado', 'homologado', 'norma']):
        caracteristicas['caracteristicas_adicionales'].append('Certificaciones de calidad')
    
    # Garantías especiales
    if any(word in texto_busqueda for word in ['garantía extendida', 'garantia extendida', '2 años', '3 años', '5 años']):
        caracteristicas['caracteristicas_adicionales'].append('Garantía extendida')
    
    # Limitar badges a los 4 más importantes
    if len(caracteristicas['badges_especiales']) > 4:
        caracteristicas['badges_especiales'] = caracteristicas['badges_especiales'][:4]
    
    return caracteristicas

# Mantener compatibilidad con función anterior
def validar_caracteristicas_producto(info, texto_pdf):
    """Compatibilidad con código existente"""
    return detectar_caracteristicas_universal(info, texto_pdf)
    
    # Detectar arranque automático
    if any(keyword in texto_busqueda for keyword in ['automático', 'automatic', 'auto start', 'arranque automatico']):
        caracteristicas['arranque_automatico'] = True
        caracteristicas['badges_especiales'].append({
            'texto': 'ARRANQUE AUTOMÁTICO',
            'color': '#FF5722',
            'icono': 'automatico'
        })
    
    # Detectar portabilidad
    if any(keyword in texto_busqueda for keyword in ['portátil', 'portable', 'portatil']) or (
        info.get('peso_kg') and float(str(info.get('peso_kg', '100')).replace('kg', '').strip()) < 50
    ):
        caracteristicas['es_portatil'] = True

    # Determine fuel type
    if info.get('combustible'):
        fuel = info.get('combustible').lower()
        if 'gas' in fuel:
            caracteristicas['tipo_combustible'] = 'gas'
        elif 'nafta' in fuel:
            caracteristicas['tipo_combustible'] = 'nafta'
    elif any(keyword in texto_busqueda for keyword in ['gas', 'glp', 'gnc']):
        caracteristicas['tipo_combustible'] = 'gas'
    elif 'nafta' in texto_busqueda or 'gasolina' in texto_busqueda:
        caracteristicas['tipo_combustible'] = 'nafta'
    
    # Badge especial para generadores nafteros
    if caracteristicas['tipo_combustible'] == 'nafta' and caracteristicas['es_portatil']:
        caracteristicas['badges_especiales'].append({
            'texto': 'PORTÁTIL',
            'color': '#FF9800',
            'icono': 'portable'
        })
        
    return caracteristicas

def procesar_campo_con_unidad(info, campo_base):
    """
    Combina campos separados de valor y unidad en un solo campo formateado
    """
    valor = info.get(f'{campo_base}_valor', '')
    unidad = info.get(f'{campo_base}_unidad', '')
    
    if valor and valor != 'N/D':
        return f"{valor} {unidad}" if unidad else str(valor)
    return None

def validar_y_limpiar_datos_universal(info):
    """
    Valida y limpia los datos para TODOS los productos universalmente
    """
    datos_limpios = info.copy()
    
    # Lista ampliada de campos que pueden tener unidades duplicadas
    campos_con_unidad = [
        'capacidad_tanque_combustible_l', 
        'consumo_75_carga_valor',
        'consumo_max_carga_valor',
        'consumo',
        'capacidad_aceite_l',
        'autonomia_horas',
        'peso_kg',
        'capacidad_tanque_litros',
        'presion_bar',
        'caudal_lts_min',
        'caudal_lph',
        'ancho_labranza_cm',
        'capacidad_tanque_l',
        'cilindrada_cc',
        'diametro_max_rama_cm',
        'potencia_hp',
        'frecuencia_hz',
        'fuerza_impacto_kg',
        'profundidad_corte_mm',
        'potencia_max_w'
    ]
    
    # Patrón regex para detectar duplicación de unidades
    import re
    for campo in campos_con_unidad:
        if campo in datos_limpios and isinstance(datos_limpios[campo], str):
            valor = str(datos_limpios[campo])
            # Remover duplicaciones como "15 L L" → "15 L"
            # Patrón: número + unidad + misma unidad
            valor = re.sub(r'(\d+\.?\d*)\s*([A-Za-z/]+)\s*\2+', r'\1 \2', valor)
            # Limpiar espacios múltiples
            valor = re.sub(r'\s+', ' ', valor)
            datos_limpios[campo] = valor.strip()
    
    # Normalizar y extraer información del motor si está como N/D
    if datos_limpios.get('motor') in ['N/D', 'n/d', None, '']:
        # Intentar extraer de otros campos
        motor_alt = extraer_info_motor_alternativa(datos_limpios)
        if motor_alt and motor_alt != 'N/D':
            datos_limpios['motor'] = motor_alt
    
    # Validar y calcular consumo específico para TODOS los tipos de combustible
    combustible = datos_limpios.get('combustible', '').lower()
    consumo_campo = datos_limpios.get('consumo_75_carga_valor') or datos_limpios.get('consumo')
    
    if consumo_campo and combustible:
        try:
            consumo_num = float(str(consumo_campo).replace('L/h', '').replace('m³/h', '').replace(',', '.').strip())
            potencia_num = float(str(datos_limpios.get('potencia_kva', '1')).replace('KVA', '').strip())
            
            # Calcular consumo específico según tipo de combustible
            consumo_por_kw = consumo_num / (potencia_num * 0.8)  # Convertir a KW
            
            # Agregar notas según eficiencia detectada
            if combustible in ['nafta', 'gasolina', 'gasoline']:
                if consumo_por_kw > 0.6:
                    datos_limpios['nota_consumo'] = "Consumo en condiciones de carga máxima"
                elif consumo_por_kw < 0.3:
                    datos_limpios['nota_consumo'] = "Excelente eficiencia de combustible"
            elif combustible in ['diesel', 'gasoil']:
                if consumo_por_kw > 0.35:
                    datos_limpios['nota_consumo'] = "Consumo en condiciones exigentes"
                elif consumo_por_kw < 0.2:
                    datos_limpios['nota_consumo'] = "Alta eficiencia para diesel"
            elif combustible in ['gas', 'gnc', 'glp']:
                if consumo_por_kw > 0.45:
                    datos_limpios['nota_consumo'] = "Consumo elevado de gas"
                elif consumo_por_kw < 0.25:
                    datos_limpios['nota_consumo'] = "Óptimo consumo de gas"
        except:
            pass
    
    # Limpiar valores "N/D" o vacíos en TODOS los campos
    for key, value in list(datos_limpios.items()):
        if isinstance(value, str):
            value_lower = value.lower().strip()
            if value_lower in ['n/d', 'n/a', 'none', 'null', 'undefined', '']:
                datos_limpios[key] = None
    
    # Normalizar campos booleanos
    for campo_bool in ['tiene_tta', 'tiene_cabina', 'es_inverter', 'es_trifasico']:
        if campo_bool in datos_limpios:
            datos_limpios[campo_bool] = bool(datos_limpios[campo_bool])
    
    return datos_limpios

def extraer_info_motor_alternativa(info):
    """
    Intenta extraer información del motor de campos alternativos
    """
    # Buscar en descripción o nombre
    nombre = str(info.get('nombre', '')).upper()
    
    # Patrones comunes de motores
    patrones_motor = [
        r'MOTOR\s+([A-Z]+\s*\d+HP)',
        r'([A-Z]+\s+\d+HP)',
        r'MOTOR\s+([A-Z]+)',
        r'(\d+HP)',
        r'(\d+\s*CC)'
    ]
    
    for patron in patrones_motor:
        match = re.search(patron, nombre)
        if match:
            return match.group(1)
    
    # Si hay cilindrada, usar eso
    if info.get('cilindrada'):
        return f"Motor {info['cilindrada']}"
    
    # Si hay potencia HP
    if info.get('potencia_hp'):
        return f"Motor {info['potencia_hp']} HP"
    
    return 'N/D'

# Mantener compatibilidad con función anterior
def validar_y_limpiar_datos(info):
    """Compatibilidad con código existente"""
    return validar_y_limpiar_datos_universal(info)

def procesar_datos_para_tabla(info):
    """
    Procesa y combina campos antes de generar la tabla
    """
    # Primero validar y limpiar
    datos_procesados = validar_y_limpiar_datos(info)
    
    # Combinar campos de potencia motor
    if 'potencia_motor_valor' in info and 'potencia_motor_unidad' in info:
        datos_procesados['motor'] = f"{info.get('potencia_motor_valor', '')} {info.get('potencia_motor_unidad', '')}"
    
    # PROCESAR CONSUMO - COMBINAR VALOR Y UNIDAD
    consumo_valor = datos_procesados.get('consumo_75_carga_valor', 
                                         datos_procesados.get('consumo_max_carga_valor', 
                                         datos_procesados.get('consumo', '')))
    
    if consumo_valor and str(consumo_valor) not in ['N/D', '', 'None']:
        consumo_str = str(consumo_valor).strip()
        
        # Si ya tiene "L/h", no agregarlo de nuevo
        if 'L/h' in consumo_str or 'l/h' in consumo_str.lower():
            datos_procesados['consumo'] = consumo_str
        # Si es solo un número (puede tener punto decimal)
        elif consumo_str.replace('.','').replace(',','').isdigit():
            datos_procesados['consumo'] = f"{consumo_str} L/h"
        else:
            # Si tiene otro formato, dejarlo como está
            datos_procesados['consumo'] = consumo_str
            
    # Normalizar campos específicos
    campos_a_normalizar = {
        'cilindrada_cc': ('cilindrada', 'cc'),
        'capacidad_aceite_l': ('capacidad_aceite', 'L'),
        'autonomia_horas': ('autonomia', 'horas'),
        'capacidad_tanque_combustible_l': ('capacidad_tanque', 'L'),
        'dimensiones_mm': ('dimensiones', ''),
        'peso_kg': ('peso', 'kg'),
        'frecuencia': ('frecuencia', 'Hz'),
        'voltaje': ('voltaje', 'V')
    }
    
    for campo_original, (nombre_display, unidad_default) in campos_a_normalizar.items():
        if campo_original in datos_procesados:
            valor = datos_procesados[campo_original]
            if valor and valor != 'N/D':
                # Si es un número solo, agregar unidad
                if str(valor).replace('.','').isdigit() and unidad_default:
                    datos_procesados[campo_original] = f"{valor} {unidad_default}"
    
    return datos_procesados

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

    # Asegurarse de que el título nunca sea None antes de llamar a upper()
    titulo_limpio = (titulo or '')
    return titulo_limpio.upper()

def generar_subtitulo_producto(info, caracteristicas):
    """Genera el subtítulo del producto."""
    subtitulo_ia = info.get('marketing_content', {}).get('subtitulo_p', '')
    if subtitulo_ia:
        return subtitulo_ia
    return "Solución energética de última generación para su proyecto"

def generar_hero_section_inline(titulo, subtitulo):
    """Genera la sección hero con badges de características."""
    return f'''
        <!-- HEADER HERO SECTION -->
        <div style="background: linear-gradient(135deg, #ff6600 0%, #ff8833 100%); padding: 40px 30px; text-align: center; border-radius: 0 0 20px 20px; box-shadow: 0 4px 20px rgba(0,0,0,0.1); position: relative; overflow: hidden;">
            <!-- Patrón de fondo decorativo -->
            <div style="position: absolute; top: 0; left: 0; right: 0; bottom: 0; opacity: 0.1;">
                <svg width="100%" height="100%" xmlns="http://www.w3.org/2000/svg">
                    <pattern id="grid" width="40" height="40" patternUnits="userSpaceOnUse">
                        <path d="M 40 0 L 0 0 0 40" fill="none" stroke="white" stroke-width="1"/>
                    </pattern>
                    <rect width="100%" height="100%" fill="url(#grid)" />
                </svg>
            </div>
            
            <h1 style="color: white; font-size: 36px; margin: 0 0 15px 0; font-weight: 700; text-transform: uppercase; letter-spacing: 1px; position: relative; z-index: 1;">
                {titulo}
            </h1>
            <p style="color: white; font-size: 18px; margin: 0; opacity: 0.95; font-weight: 300; position: relative; z-index: 1;">
                {subtitulo}
            </p>
        </div>
    '''

def generar_info_cards_inline_mejorado(info, caracteristicas):
    """Versión mejorada con gráfico de consumo visible."""
    tipo_combustible = caracteristicas.get('tipo_combustible', 'diesel')
    
    # Mapeo mejorado de iconos por tipo de combustible
    iconos_combustible = {
        'diesel': '<svg width="24" height="24" viewBox="0 0 24 24" fill="#333"><path d="M12 2C8.13 2 5 5.13 5 9c0 1.88.79 3.56 2 4.78V22h10v-8.22c1.21-1.22 2-2.9 2-4.78 0-3.87-3.13-7-7-7zm0 2c2.76 0 5 2.24 5 5s-2.24 5-5 5-5-2.24-5-5 2.24-5 5-5z"/></svg>',
        'gas': '<svg width="24" height="24" viewBox="0 0 24 24" fill="#1976d2"><path d="M13.5.67s.74 2.65.74 4.8c0 2.06-1.35 3.73-3.41 3.73-2.07 0-3.63-1.67-3.63-3.73l.03-.36C5.21 7.51 4 10.62 4 14c0 4.42 3.58 8 8 8s8-3.58 8-8C20 8.61 17.41 3.8 13.5.67z"/></svg>',
        'nafta': '<svg width="24" height="24" viewBox="0 0 24 24" fill="#f44336"><path d="M12 3c-1.1 0-2 .9-2 2v12.5c0 .83.67 1.5 1.5 1.5s1.5-.67 1.5-1.5V5c0-1.1-.9-2-2-2zm-3 4H7v11h2V7zm6 0h-2v11h2V7z"/></svg>',
        'gnc': '<svg width="24" height="24" viewBox="0 0 24 24" fill="#4caf50"><path d="M17.66 8L12 2.35 6.34 8C4.78 9.56 4 11.64 4 13.64s.78 4.11 2.34 5.67 3.61 2.35 5.66 2.35 4.1-.79 5.66-2.35S20 15.64 20 13.64s-.78-4.08-2.34-5.64z"/></svg>'
    }
    
    icono_combustible = iconos_combustible.get(tipo_combustible.lower(), iconos_combustible['diesel'])

    # Lógica de potencia mejorada
    potencia_valor = info.get('potencia_standby_valor') or info.get('potencia_max_valor') or info.get('potencia_valor')
    potencia_unidad = info.get('potencia_standby_unidad') or info.get('potencia_max_unidad') or info.get('potencia_unidad', 'W')
    
    if potencia_valor and potencia_unidad:
        potencia_str = f"{potencia_valor} {potencia_unidad.upper()}"
    elif info.get('potencia_kva'):
        potencia_str = f"{info.get('potencia_kva')}"
    else:
        potencia_str = "N/D"

    # Limpiar duplicados
    parts = potencia_str.split()
    if len(parts) > 1 and parts[-1].lower() == parts[-2].lower():
        potencia_str = " ".join(parts[:-1])

    potencia_kw = str(info.get('potencia_kw', '') or '').strip()
    motor = str(info.get('motor') or info.get('potencia_motor_valor', '') or '').strip()
    if motor and info.get('potencia_motor_unidad'):
        motor += f" {info['potencia_motor_unidad']}"
    
    # Obtener consumo correctamente - usar el campo ya procesado
    consumo_str = info.get('consumo', 'N/D')
    
    # Si por alguna razón todavía no está procesado, intentar procesarlo aquí
    if consumo_str == 'N/D' or not consumo_str:
        consumo_valor = info.get('consumo_valor') or info.get('consumo_75_carga_valor') or info.get('consumo_max_carga_valor')
        if consumo_valor and str(consumo_valor) != 'N/D':
            consumo_str_temp = str(consumo_valor).strip()
            # Verificar si ya tiene unidad
            if 'L/h' not in consumo_str_temp and 'l/h' not in consumo_str_temp.lower():
                consumo_str = f"{consumo_str_temp} L/h"
            else:
                consumo_str = consumo_str_temp
        else:
            consumo_str = "N/D"

    # Generar badges de características
    badges_html = generar_badges_caracteristicas(info, caracteristicas)

    # Función para generar el gráfico de consumo
    # Usar función universal para gráfico de consumo
    grafico_consumo = generar_grafico_consumo_universal(info)

    return f'''
        <!-- BADGES DE CARACTERÍSTICAS ESPECIALES -->
        {f'<div style="text-align: center; padding: 20px 30px 0 30px;">{badges_html}</div>' if badges_html else ''}
        
        <!-- ESPECIFICACIONES PRINCIPALES -->
        <div style="padding: 30px; display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 20px;">
            
            <!-- Card Potencia con animación -->
            <div class="card-hover" style="background: #f8f9fa; border-radius: 12px; padding: 25px; border-left: 4px solid #ff6600; box-shadow: 0 2px 8px rgba(0,0,0,0.08); position: relative; overflow: hidden;">
                <div style="position: absolute; top: -20px; right: -20px; width: 80px; height: 80px; background: rgba(255,102,0,0.1); border-radius: 50%;"></div>
                <div style="display: flex; align-items: center; gap: 15px; position: relative;">
                    <div style="width: 48px; height: 48px; background: #fff3e0; border-radius: 50%; display: flex; align-items: center; justify-content: center; transition: all 0.3s ease;" class="icon-wrapper">
                        <svg width="24" height="24" viewBox="0 0 24 24" fill="#ff6600"><path d="M7 2v11h3v9l7-12h-4l4-8z"/></svg>
                    </div>
                    <div>
                        <p style="margin: 0; color: #666; font-size: 12px; text-transform: uppercase; letter-spacing: 0.5px;">Potencia Máxima</p>
                        <p style="margin: 5px 0 0 0; font-size: 24px; font-weight: 700; color: #ff6600;">
                            {potencia_str}
                        </p>
                        {f'<p style="margin: 0; font-size: 14px; color: #999;">{potencia_kw} KW</p>' if potencia_kw else ''}
                    </div>
                </div>
            </div>
            
            <!-- Card Motor mejorada -->
            <div class="card-hover" style="background: #f8f9fa; border-radius: 12px; padding: 25px; border-left: 4px solid #2196F3; box-shadow: 0 2px 8px rgba(0,0,0,0.08); position: relative; overflow: hidden;">
                <div style="position: absolute; top: -20px; right: -20px; width: 80px; height: 80px; background: rgba(33,150,243,0.1); border-radius: 50%;"></div>
                <div style="display: flex; align-items: center; gap: 15px; position: relative;">
                    <div style="width: 48px; height: 48px; background: #e3f2fd; border-radius: 50%; display: flex; align-items: center; justify-content: center; transition: all 0.3s ease;" class="icon-wrapper">
                        <svg width="24" height="24" viewBox="0 0 24 24" fill="#2196F3"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 18c-4.42 0-8-3.58-8-8s3.58-8 8-8 8 3.58 8 8-3.58 8-8 8z"/></svg>
                    </div>
                    <div>
                        <p style="margin: 0; color: #666; font-size: 12px; text-transform: uppercase; letter-spacing: 0.5px;">Motor</p>
                        <p style="margin: 5px 0 0 0; font-size: 18px; font-weight: 600; color: #333;">
                            {motor if motor else 'N/D'}
                        </p>
                        {f'<p style="margin: 0; font-size: 12px; color: #999;"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#999" stroke-width="2" style="display: inline-block; vertical-align: middle; margin-right: 4px;"><circle cx="12" cy="12" r="9"/><path d="M12 6v6l4 2"/></svg>{info.get("rpm", "3000")} RPM</p>' if info.get('rpm') else ''}
                    </div>
                </div>
            </div>
            
            <!-- Card Combustible/Consumo mejorada con gráfico VISIBLE -->
            <div class="card-hover" style="background: #f8f9fa; border-radius: 12px; padding: 25px; border-left: 4px solid #4CAF50; box-shadow: 0 2px 8px rgba(0,0,0,0.08); position: relative; overflow: hidden;">
                <div style="position: absolute; top: -20px; right: -20px; width: 80px; height: 80px; background: rgba(76,175,80,0.1); border-radius: 50%;"></div>
                <div style="display: flex; align-items: center; gap: 15px; position: relative;">
                    <div style="width: 48px; height: 48px; background: #e8f5e9; border-radius: 50%; display: flex; align-items: center; justify-content: center; transition: all 0.3s ease;" class="icon-wrapper">
                        {icono_combustible}
                    </div>
                    <div style="flex: 1;">
                        <p style="margin: 0; color: #666; font-size: 12px; text-transform: uppercase; letter-spacing: 0.5px;">Tipo de Combustible</p>
                        <p style="margin: 5px 0 0 0; font-size: 18px; font-weight: 600; color: #333; text-transform: capitalize;">
                            {tipo_combustible.upper()}
                        </p>
                        {f'<p style="margin: 5px 0 0 0; font-size: 14px; color: #666;">Consumo: <strong>{consumo_str}</strong></p>' if consumo_str != "N/D" else ''}
                        {grafico_consumo if consumo_str != "N/D" else ''}
                    </div>
                </div>
            </div>
            
        </div>
        
        <!-- CARACTERÍSTICAS ADICIONALES EN CARDS -->
        <div style="padding: 0 30px 30px 30px; display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px;">
            {generar_mini_cards_adicionales(info)}
        </div>
    '''

def generar_mini_cards_adicionales(info):
    """Genera mini cards para características adicionales."""
    mini_cards = []
    
    # Autonomía
    if info.get('autonomia_potencia_nominal_valor'):
        mini_cards.append(f'''
        <div style="background: #fff3e0; border-radius: 8px; padding: 15px; text-align: center; border: 1px solid #ffcc80;">
            <div style="width: 32px; height: 32px; margin: 0 auto 8px;">{ICONOS_SVG['clock']}</div>
            <p style="margin: 0; font-size: 12px; color: #666;">Autonomía</p>
            <p style="margin: 5px 0 0 0; font-size: 16px; font-weight: 600; color: #ff6600;">{info['autonomia_potencia_nominal_valor']} horas</p>
        </div>
        ''')
    
    # Tanque
    if info.get('capacidad_tanque_combustible_l'):
        mini_cards.append(f'''
        <div style="background: #e3f2fd; border-radius: 8px; padding: 15px; text-align: center; border: 1px solid #90caf9;">
            <div style="width: 32px; height: 32px; margin: 0 auto 8px;">{ICONOS_SVG['tanque']}</div>
            <p style="margin: 0; font-size: 12px; color: #666;">Tanque</p>
            <p style="margin: 5px 0 0 0; font-size: 16px; font-weight: 600; color: #2196F3;">{info['capacidad_tanque_combustible_l']}</p>
        </div>
        ''')
    
    # Nivel sonoro
    if info.get('nivel_sonoro_dba_7m'):
        nivel_sonoro = str(info['nivel_sonoro_dba_7m']).replace('dBA', '').strip()
        mini_cards.append(f'''
        <div style="background: #f3e5f5; border-radius: 8px; padding: 15px; text-align: center; border: 1px solid #ce93d8;">
            <div style="width: 32px; height: 32px; margin: 0 auto 8px;">{ICONOS_SVG['ruido']}</div>
            <p style="margin: 0; font-size: 12px; color: #666;">Nivel Sonoro</p>
            <p style="margin: 5px 0 0 0; font-size: 16px; font-weight: 600; color: #9c27b0;">{nivel_sonoro} dBA</p>
        </div>
        ''')
    
    # Temperatura
    if info.get('temperatura_operacion'):
        mini_cards.append(f'''
        <div style="background: #ffebee; border-radius: 8px; padding: 15px; text-align: center; border: 1px solid #ef9a9a;">
            <div style="width: 32px; height: 32px; margin: 0 auto 8px;">{ICONOS_SVG['temperatura']}</div>
            <p style="margin: 0; font-size: 12px; color: #666;">Temperatura Op.</p>
            <p style="margin: 5px 0 0 0; font-size: 16px; font-weight: 600; color: #f44336;">{info['temperatura_operacion']}°C</p>
        </div>
        ''')
    
    return ''.join(mini_cards)

def obtener_icono_para_campo_universal(nombre_campo, valor_campo=''):
    """
    Retorna el icono apropiado para CUALQUIER campo de forma universal
    """
    # Normalizar nombre del campo
    campo_norm = nombre_campo.lower().replace('_', ' ')
    
    # Para combustible, elegir icono según el valor
    if 'combustible' in campo_norm or 'fuel' in campo_norm:
        valor_norm = str(valor_campo).lower()
        if any(fuel in valor_norm for fuel in ['nafta', 'gasolina', 'gasoline']):
            return ICONOS_SVG.get('nafta', ICONOS_SVG['gas'])
        elif any(fuel in valor_norm for fuel in ['diesel', 'gasoil']):
            return ICONOS_SVG.get('diesel', ICONOS_SVG['gas'])
        elif any(fuel in valor_norm for fuel in ['gas', 'gnc', 'glp']):
            return ICONOS_SVG.get('gas', ICONOS_SVG['gas'])
        else:
            return ICONOS_SVG['gas']
    
    # Diccionario completo de mapeo de iconos
    iconos_campos = {
        # Potencia y energía
        'potencia': ICONOS_SVG['potencia'],
        'power': ICONOS_SVG['potencia'],
        'kva': ICONOS_SVG['potencia'],
        'kw': ICONOS_SVG['potencia'],
        'watts': ICONOS_SVG['potencia'],
        'hp': ICONOS_SVG['motor'],
        
        # Motor y mecánica
        'motor': ICONOS_SVG['motor'],
        'engine': ICONOS_SVG['motor'],
        'cilindrada': ICONOS_SVG.get('cilindros', ICONOS_SVG['motor']),
        'cilindros': ICONOS_SVG.get('cilindros', ICONOS_SVG['motor']),
        'rpm': ICONOS_SVG.get('rpm', ICONOS_SVG['gear']),
        'revoluciones': ICONOS_SVG.get('rpm', ICONOS_SVG['gear']),
        
        # Combustible y consumo
        'consumo': ICONOS_SVG['consumo'],
        'consumption': ICONOS_SVG['consumo'],
        'tanque': ICONOS_SVG.get('tanque', ICONOS_SVG['gas']),
        'tank': ICONOS_SVG.get('tanque', ICONOS_SVG['gas']),
        'capacidad tanque': ICONOS_SVG.get('tanque', ICONOS_SVG['gas']),
        'autonomia': ICONOS_SVG['clock'],
        'autonomía': ICONOS_SVG['clock'],
        
        # Control y arranque
        'arranque': ICONOS_SVG.get('arranque', ICONOS_SVG['gear']),
        'starting': ICONOS_SVG.get('arranque', ICONOS_SVG['gear']),
        'controlador': ICONOS_SVG['gear'],
        'controller': ICONOS_SVG['gear'],
        'panel': ICONOS_SVG['gear'],
        'bateria': ICONOS_SVG.get('battery', ICONOS_SVG['potencia']),
        'battery': ICONOS_SVG.get('battery', ICONOS_SVG['potencia']),
        
        # Sistema eléctrico
        'voltaje': ICONOS_SVG['voltaje'],
        'voltage': ICONOS_SVG['voltaje'],
        'tension': ICONOS_SVG['voltaje'],
        'frecuencia': ICONOS_SVG['frecuencia'],
        'frequency': ICONOS_SVG['frecuencia'],
        'fases': ICONOS_SVG.get('fases', ICONOS_SVG['voltaje']),
        'phases': ICONOS_SVG.get('fases', ICONOS_SVG['voltaje']),
        'alternador': ICONOS_SVG['potencia'],
        
        # Dimensiones y peso
        'dimensiones': ICONOS_SVG['dimensiones'],
        'dimensions': ICONOS_SVG['dimensiones'],
        'tamaño': ICONOS_SVG['dimensiones'],
        'peso': ICONOS_SVG['peso'],
        'weight': ICONOS_SVG['peso'],
        'largo': ICONOS_SVG['dimensiones'],
        'ancho': ICONOS_SVG['dimensiones'],
        'alto': ICONOS_SVG['dimensiones'],
        
        # Ambiente y condiciones
        'temperatura': ICONOS_SVG['temperatura'],
        'temperature': ICONOS_SVG['temperatura'],
        'ruido': ICONOS_SVG['ruido'],
        'noise': ICONOS_SVG['ruido'],
        'sonoro': ICONOS_SVG['ruido'],
        'nivel sonoro': ICONOS_SVG['ruido'],
        'dba': ICONOS_SVG['ruido'],
        
        # Presión y flujo
        'presion': ICONOS_SVG.get('presion', ICONOS_SVG['gauge']),
        'presión': ICONOS_SVG.get('presion', ICONOS_SVG['gauge']),
        'pressure': ICONOS_SVG.get('gauge', ICONOS_SVG['gauge']),
        'caudal': ICONOS_SVG.get('water', ICONOS_SVG['gauge']),
        'flujo': ICONOS_SVG.get('water', ICONOS_SVG['gauge']),
        'bar': ICONOS_SVG.get('gauge', ICONOS_SVG['gauge']),
        
        # Otros
        'aceite': ICONOS_SVG.get('aceite', ICONOS_SVG['tanque']),
        'oil': ICONOS_SVG.get('aceite', ICONOS_SVG['tanque']),
        'certificacion': ICONOS_SVG.get('award', ICONOS_SVG['shield']),
        'certificaciones': ICONOS_SVG.get('award', ICONOS_SVG['shield']),
        'garantia': ICONOS_SVG['shield'],
        'garantía': ICONOS_SVG['shield'],
        'warranty': ICONOS_SVG['shield'],
        'modelo': ICONOS_SVG.get('info', ICONOS_SVG['gear']),
        'model': ICONOS_SVG.get('info', ICONOS_SVG['gear']),
        'serie': ICONOS_SVG.get('info', ICONOS_SVG['gear']),
        'factor potencia': ICONOS_SVG.get('chart', ICONOS_SVG['potencia']),
        'marca': ICONOS_SVG.get('award', ICONOS_SVG['info']),
        
        # Campos específicos por producto
        'labranza': ICONOS_SVG.get('campo', ICONOS_SVG['tools']),
        'profundidad': ICONOS_SVG['dimensiones'],
        'diametro': ICONOS_SVG['dimensiones'],
        'diámetro': ICONOS_SVG['dimensiones'],
        'marchas': ICONOS_SVG['gear'],
        'eje': ICONOS_SVG['gear'],
        'corte': ICONOS_SVG['tools'],
        'alcance': ICONOS_SVG.get('location', ICONOS_SVG['arrow_right'])
    }
    
    # Buscar coincidencia más específica primero
    for key, icon in iconos_campos.items():
        if key in campo_norm:
            return icon
    
    # Si no hay coincidencia, usar icono por defecto
    return ICONOS_SVG.get('dot', '<svg width="20" height="20" viewBox="0 0 24 24" fill="#666"><circle cx="12" cy="12" r="3"/></svg>')

def generar_specs_table_inline(info):
    """Genera la tabla de especificaciones con iconos específicos mejorados."""
    
    # Procesar y combinar campos antes de generar la tabla
    info = procesar_datos_para_tabla(info)

    # Mapeo extendido con iconos específicos para cada tipo de campo
    spec_map = {
        # Información básica
        'modelo': ('Modelo', '<svg width="20" height="20" viewBox="0 0 24 24" fill="#ff6600"><path d="M9 2v6h6V2H9zm7 0v6h6V6c0-2.2-1.8-4-4-4h-2zm0 8H8v6h8v-6zm2 0v6h4c2.2 0 4-1.8 4-4v-2h-6zm-10 0H2v2c0 2.2 1.8 4 4 4h2v-6zm0-2V2H6C3.8 2 2 3.8 2 6v2h6z"/></svg>'),
        'serie': ('Serie', '<svg width="20" height="20" viewBox="0 0 24 24" fill="#ff6600"><path d="M3 9v6h4l5 5V4L7 9H3zm13.5 3c0-1.77-1.02-3.29-2.5-4.03v8.05c1.48-.73 2.5-2.25 2.5-4.02z"/></svg>'),
        
        # Potencia y energía
        'potencia_kva': ('Potencia Stand By', '<svg width="20" height="20" viewBox="0 0 24 24" fill="#ff6600"><path d="M7 2v11h3v9l7-12h-4l4-8z"/></svg>'),
        'potencia_prime': ('Potencia Prime', '<svg width="20" height="20" viewBox="0 0 24 24" fill="#ff9800"><path d="M11 2v11h3v9l7-12h-4l3-8z"/></svg>'),
        'potencia_kw': ('Potencia en KW', '<svg width="20" height="20" viewBox="0 0 24 24" fill="#ff5722"><path d="M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm-7 14l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/></svg>'),
        
        # Sistema eléctrico
        'voltaje': ('Voltaje', '<svg width="20" height="20" viewBox="0 0 24 24" fill="#f44336"><path d="M8 7v4h8V7l4 5-4 5v-4H8v4l-4-5 4-5z"/></svg>'),
        'frecuencia': ('Frecuencia', '<svg width="20" height="20" viewBox="0 0 24 24" fill="#e91e63"><path d="M16 6l-4 4-4-4v3l4 4 4-4zm0 6l-4 4-4-4v3l4 4 4-4z"/></svg>'),
        'fases': ('Fases', '<svg width="20" height="20" viewBox="0 0 24 24" fill="#9c27b0"><path d="M11 15h2v2h-2zm0-8h2v6h-2zm1-5C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2z"/></svg>'),
        
        # Motor
        'motor': ('Motor', '<svg width="20" height="20" viewBox="0 0 24 24" fill="#2196f3"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 18c-4.42 0-8-3.58-8-8s3.58-8 8-8 8 3.58 8 8-3.58 8-8 8z"/></svg>'),
        'marca_motor': ('Marca Motor', '<svg width="20" height="20" viewBox="0 0 24 24" fill="#3f51b5"><path d="M21 3H3c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h18c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm0 16H3V5h18v14z"/></svg>'),
        'modelo_motor': ('Modelo Motor', '<svg width="20" height="20" viewBox="0 0 24 24" fill="#00bcd4"><path d="M15 9H9v6h6V9zm-2 4h-2v-2h2v2zm8-2V9l-2-2h-2V5c0-1.1-.9-2-2-2H9c-1.1 0-2 .9-2 2v2H5L3 9v2c-1.1 0-2 .9-2 2v6h2c0 1.1.9 2 2 2s2-.9 2-2h10c0 1.1.9 2 2 2s2-.9 2-2h2v-6c0-1.1-.9-2-2-2z"/></svg>'),
        'rpm': ('RPM', '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#ff6600" stroke-width="2"><circle cx="12" cy="12" r="9"/><path d="M12 6v6l4 2"/></svg>'),
        'cilindrada': ('Cilindrada', '<svg width="20" height="20" viewBox="0 0 24 24" fill="#795548"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 18c-1.19 0-2.34-.26-3.33-.72l3.33-3.33 3.33 3.33c-.99.46-2.14.72-3.33.72z"/></svg>'),
        
        # Combustible y consumo
        'combustible': ('Combustible', '<svg width="20" height="20" viewBox="0 0 24 24" fill="#4caf50"><path d="M19.77 7.23l.01-.01-3.72-3.72L15 4.56l2.11 2.11c-.94.36-1.61 1.26-1.61 2.33 0 1.38 1.12 2.5 2.5 2.5.36 0 .69-.08 1-.21v7.21c0 .55-.45 1-1 1s-1-.45-1-1V14c0-1.1-.9-2-2-2h-1V5c0-1.1-.9-2-2-2H6c-1.1 0-2 .9-2 2v16h10v-7.5h1.5v7.21c0 1.38 1.12 2.5 2.5 2.5s2.5-1.12 2.5-2.5V9c0-.69-.28-1.32-.73-1.77z"/></svg>'),
        'consumo': ('Consumo', '<svg width="20" height="20" viewBox="0 0 24 24" fill="#ff9800"><path d="M3 2v2h1v16h5v-8h6v8h5V4h1V2H3zm3 4h3v3H6V6zm6 0h3v3h-3V6zm6 0h3v3h-3V6z"/></svg>'),
        'capacidad_tanque_litros': ('Capacidad Tanque', '<svg width="20" height="20" viewBox="0 0 24 24" fill="#2196f3"><path d="M19 9v6c0 1.1-.9 2-2 2H7c-1.1 0-2-.9-2-2V9c0-1.1.9-2 2-2h10c1.1 0 2 .9 2 2zM7 11h10M12 7v4"/></svg>'),
        'autonomia': ('Autonomía', '<svg width="20" height="20" viewBox="0 0 24 24" fill="#009688"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 18c-4.41 0-8-3.59-8-8s3.59-8 8-8 8 3.59 8 8-3.59 8-8 8zm.5-13H11v6l5.2 3.1.8-1.3-4.5-2.7z"/></svg>'),
        
        # Control y operación
        'arranque': ('Tipo de Arranque', '<svg width="20" height="20" viewBox="0 0 24 24" fill="#607d8b"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm3.5 6L12 10.5 8.5 8 11 5.5 12 6.55l3.5-3.5 1 1z"/></svg>'),
        'controlador': ('Controlador', '<svg width="20" height="20" viewBox="0 0 24 24" fill="#9e9e9e"><path d="M22 9V7h-2V5c0-1.1-.9-2-2-2H4c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2v-2h2v-2h-2v-2h2v-2h-2V9h2zm-4 10H4V5h14v14z"/></svg>'),
        'panel_control': ('Panel de Control', '<svg width="20" height="20" viewBox="0 0 24 24" fill="#455a64"><path d="M13 3h-2v10h2V3zm4.83 2.17l-1.42 1.42C17.99 7.86 19 9.81 19 12c0 3.87-3.13 7-7 7s-7-3.13-7-7c0-2.19 1.01-4.14 2.58-5.42L6.17 5.17C4.23 6.82 3 9.26 3 12c0 4.97 4.03 9 9 9s9-4.03 9-9c0-2.74-1.23-5.18-3.17-6.83z"/></svg>'),
        'alternador': ('Alternador', '<svg width="20" height="20" viewBox="0 0 24 24" fill="#3f51b5"><path d="M7 2v11h3v9l7-12h-4l4-8z"/></svg>'),
        'bateria': ('Batería', '<svg width="20" height="20" viewBox="0 0 24 24" fill="#4caf50"><path d="M16.67 4H15V2h-6v2H7.33C6.6 4 6 4.6 6 5.33v15.33c0 .74.6 1.34 1.33 1.34h9.33c.74 0 1.34-.6 1.34-1.33V5.33C18 4.6 17.4 4 16.67 4z"/></svg>'),
        
        # Características físicas
        'dimensiones_mm': ('Dimensiones (LxAxH)', '<svg width="20" height="20" viewBox="0 0 24 24" fill="#ff5722"><path d="M21 3H3c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h18c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm0 16H3V5h18v14z"/></svg>'),
        'peso_kg': ('Peso', '<svg width="20" height="20" viewBox="0 0 24 24" fill="#795548"><path d="M12 3c-1.27 0-2.4.8-2.82 2H3v2h1.95l2 7c.17.59.71 1 1.32 1H15.73c.61 0 1.15-.41 1.32-1l2-7H21V5h-6.18C14.4 3.8 13.27 3 12 3zm0 2c.55 0 1 .45 1 1s-.45 1-1 1-1-.45-1-1 .45-1 1-1z"/></svg>'),
        'peso': ('Peso', '<svg width="20" height="20" viewBox="0 0 24 24" fill="#795548"><path d="M12 3c-1.27 0-2.4.8-2.82 2H3v2h1.95l2 7c.17.59.71 1 1.32 1H15.73c.61 0 1.15-.41 1.32-1l2-7H21V5h-6.18C14.4 3.8 13.27 3 12 3zm0 2c.55 0 1 .45 1 1s-.45 1-1 1-1-.45-1-1 .45-1 1-1z"/></svg>'),
        
        # Condiciones ambientales
        'nivel_sonoro_dba_7m': ('Nivel Sonoro', '<svg width="20" height="20" viewBox="0 0 24 24" fill="#673ab7"><path d="M3 9v6h4l5 5V4L7 9H3zm13.5 3c0-1.77-1.02-3.29-2.5-4.03v8.05c1.48-.73 2.5-2.25 2.5-4.02z"/></svg>'),
        'nivel_ruido': ('Nivel de Ruido', '<svg width="20" height="20" viewBox="0 0 24 24" fill="#673ab7"><path d="M3 9v6h4l5 5V4L7 9H3zm13.5 3c0-1.77-1.02-3.29-2.5-4.03v8.05c1.48-.73 2.5-2.25 2.5-4.02z"/></svg>'),
        'temperatura_operacion': ('Temperatura Op.', '<svg width="20" height="20" viewBox="0 0 24 24" fill="#f44336"><path d="M15 13V5a3 3 0 0 0-6 0v8a5 5 0 1 0 6 0m-3-9a1 1 0 0 1 1 1v5.3a3 3 0 1 1-2 0V5a1 1 0 0 1 1-1z"/></svg>'),
        
        # Certificaciones y garantías
        'certificaciones': ('Certificaciones', '<svg width="20" height="20" viewBox="0 0 24 24" fill="#ffc107"><path d="M12 1L3 5v6c0 5.55 3.84 10.74 9 12 5.16-1.26 9-6.45 9-12V5l-9-4z"/></svg>'),
        'garantia': ('Garantía', '<svg width="20" height="20" viewBox="0 0 24 24" fill="#4caf50"><path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z"/></svg>'),
        
        # Otros campos específicos
        'capacidad_aceite': ('Capacidad de Aceite', '<svg width="20" height="20" viewBox="0 0 24 24" fill="#ffeb3b"><path d="M10 2v6h4V2h-4zm0 8v12h4V10h-4z"/></svg>'),
        'cilindrada': ('Cilindrada', '<svg width="20" height="20" viewBox="0 0 24 24" fill="#666"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 18c-4.42 0-8-3.58-8-8s3.58-8 8-8 8 3.58 8 8-3.58 8-8 8z"/><circle cx="12" cy="12" r="3"/></svg>'),
        'autonomia': ('Autonomía', '<svg width="20" height="20" viewBox="0 0 24 24" fill="#666"><path d="M12 2C6.5 2 2 6.5 2 12s4.5 10 10 10 10-4.5 10-10S17.5 2 12 2zm4.2 14.2L11 13V7h1.5v5.2l4.5 2.7-.8 1.3z"/></svg>'),
        'capacidad_tanque': ('Capacidad Tanque', '<svg width="20" height="20" viewBox="0 0 24 24" fill="#666"><path d="M19 9v6c0 1.1-.9 2-2 2H7c-1.1 0-2-.9-2-2V9c0-1.1.9-2 2-2h10c1.1 0 2 .9 2 2zM7 11h10M12 7v4"/></svg>'),
        'tipo_arranque': ('Tipo de Arranque', '<svg width="20" height="20" viewBox="0 0 24 24" fill="#666"><path d="M12 2v10l4-4-4-4zm0 20V12l-4 4 4 4z"/></svg>'),
        'cilindros': ('Cilindros', '<svg width="20" height="20" viewBox="0 0 24 24" fill="#666"><path d="M7 4h10v16H7V4zm2 2v12h6V6H9z"/></svg>'),
        'factor_potencia': ('Factor de Potencia', '<svg width="20" height="20" viewBox="0 0 24 24" fill="#666"><path d="M11 2v9.4l-3.5-3.5-1.4 1.4 5.9 5.9 5.9-5.9-1.4-1.4L13 11.4V2h-2z"/></svg>'),
        'potencia_motor_hp': ('Potencia Motor', '<svg width="20" height="20" viewBox="0 0 24 24" fill="#666"><path d="M12 16c2.2 0 4-1.8 4-4s-1.8-4-4-4-4 1.8-4 4 1.8 4 4 4zm0-6c1.1 0 2 .9 2 2s-.9 2-2 2-2-.9-2-2 .9-2 2-2z"/></svg>')
    }

    rows_html = ""
    row_count = 0
    
    # Lista actualizada de claves a excluir
    exclude_keys = [
        'nombre', 'marca', 'familia', 'pdf_url', 'marketing_content',
        'categoria_producto', 'caracteristicas_especiales',
        'potencia_standby_valor', 'potencia_standby_unidad',
        'potencia_prime_valor', 'potencia_prime_unidad',
        'consumo_75_carga_valor', 'consumo_75_carga_unidad',
        'consumo_max_carga_valor', 'consumo_max_carga_unidad',
        # AGREGAR ESTOS:
        'potencia_motor_valor',
        'potencia_motor_unidad',
        'voltaje_unidad',
        'frecuencia_hz',
        'voltaje_valor',
        'potencia_valor',
        'potencia_unidad',
        'nivel_ruido_dba',
        'nivel_ruido_valor', 
        'nivel_ruido_unidad',
    ]

    # Agrupar especificaciones por categoría para mejor organización
    categorias = {
        'Especificaciones Eléctricas': ['modelo', 'serie', 'potencia_kva', 'potencia_prime', 'potencia_kw', 'voltaje', 'frecuencia', 'fases'],
        'Motor y Mecánica': ['motor', 'marca_motor', 'modelo_motor', 'rpm', 'cilindrada', 'cilindrada_cc'],
        'Combustible y Autonomía': ['combustible', 'consumo', 'capacidad_tanque_litros', 'autonomia', 'autonomia_horas', 'capacidad_tanque_combustible_l', 'capacidad_tanque'],
        'Control y Operación': ['arranque', 'controlador', 'panel_control', 'alternador', 'bateria', 'tipo_arranque'],
        'Características Físicas': ['dimensiones_mm', 'peso_kg', 'peso', 'dimensiones'],
        'Condiciones Ambientales': ['nivel_sonoro_dba_7m', 'nivel_ruido', 'temperatura_operacion'],
        'Otros': ['capacidad_aceite_l', 'capacidad_aceite']
    }

    # Procesar datos por categoría
    for categoria, campos in categorias.items():
        categoria_tiene_datos = False
        
        # Verificar si hay datos en esta categoría
        for key in campos:
            if key in info and info[key] not in [None, '', 'N/D']:
                categoria_tiene_datos = True
                break
        
        if not categoria_tiene_datos and categoria == 'Otros':
             for key, value in info.items():
                if key not in exclude_keys and value not in [None, '', 'N/D']:
                    if not any(key in cat_campos for cat_campos in categorias.values()):
                        categoria_tiene_datos = True
                        break

        if categoria_tiene_datos:
            if row_count > 0:
                # Agregar separador de categoría
                rows_html += f'''
                    <tr style="background: #f5f5f5; border-top: 2px solid #ddd;">
                        <td colspan="2" style="padding: 10px 20px; font-weight: 600; color: #666; font-size: 12px; text-transform: uppercase; letter-spacing: 1px;">
                            {categoria}
                        </td>
                    </tr>'''
            
            # Agregar filas de la categoría
            for key, value in sorted(info.items()):
                if key in exclude_keys or value in [None, '', 'N/D']:
                    continue

                is_in_category = key in campos
                if not is_in_category and categoria == 'Otros':
                    if not any(key in cat_campos for cat_campos in categorias.values()):
                        is_in_category = True

                if is_in_category:
                    # Usar función universal para obtener iconos
                    icon = obtener_icono_para_campo_universal(key, value)
                    
                    # Intentar obtener label del spec_map primero
                    if key in spec_map:
                        label = spec_map[key][0]
                    else:
                        # Mapeo de nombres específicos mejorado
                        nombre_mapping = {
                            'cilindrada_cc': 'Cilindrada',
                            'capacidad_aceite_l': 'Capacidad de Aceite',
                            'autonomia_horas': 'Autonomía',
                            'capacidad_tanque_combustible_l': 'Capacidad del Tanque',
                            'dimensiones_mm': 'Dimensiones',
                            'peso_kg': 'Peso',
                            'potencia_kva': 'Potencia',
                            'frecuencia_hz': 'Frecuencia',
                            'tipo_arranque': 'Tipo de Arranque',
                            'nivel_ruido_dba': 'Nivel de Ruido',
                            'presion_bar': 'Presión',
                            'caudal_lts_min': 'Caudal',
                            'ancho_labranza_cm': 'Ancho de Labranza',
                            'diametro_max_rama_cm': 'Diámetro Máximo',
                            'potencia_motor_hp': 'Potencia Motor',
                            'potencia_hp': 'Potencia',
                            'potencia_max_w': 'Potencia Máxima',
                            'frecuencia_hz': 'Frecuencia',
                            'fuerza_impacto_kg': 'Fuerza de Impacto',
                            'profundidad_corte_mm': 'Profundidad de Corte'
                        }
                        label = nombre_mapping.get(key, key.replace('_', ' ').title())
                    
                    display_name = label
                    
                    value_display = str(value)

                    bg_color = '#f8f9fa' if row_count % 2 == 0 else 'white'
                    
                    rows_html += f'''
                        <tr class="spec-row" style="background: {bg_color}; border-bottom: 1px solid #eee; transition: all 0.2s ease;">
                            <td style="padding: 15px 20px; display: flex; align-items: center; gap: 10px;">
                                <div style="width: 20px; height: 20px; opacity: 0.7; transition: all 0.3s ease;">{icon}</div>
                                <span style="color: #666; font-weight: 500;">{display_name}</span>
                            </td>
                            <td style="padding: 15px 20px; font-weight: 600; color: #333;">{value_display}</td>
                        </tr>'''
                    row_count += 1
    
    # El consumo ya se procesa en procesar_datos_para_tabla y se incluye en la tabla principal
    
    return f'''
        <!-- TABLA DE ESPECIFICACIONES TÉCNICAS MEJORADA -->
        <div style="background: #FFC107; margin: 30px; padding: 30px; border-radius: 16px; box-shadow: 0 4px 20px rgba(0,0,0,0.1); position: relative;">
            <!-- Decoración de esquina -->
            <div style="position: absolute; top: -10px; right: -10px; width: 60px; height: 60px; background: #ff6600; border-radius: 50%; opacity: 0.2;"></div>
            
            <h2 style="color: #333; font-size: 28px; margin: 0 0 25px 0; text-align: center; font-weight: 700; position: relative;">
                <svg width="36" height="36" viewBox="0 0 24 24" fill="#333"><path d="M9 17H7v-7h2m4 7h-2V7h2m4 10h-2v-4h2m4 4h-2V4h2v13z"/></svg>
                <br>
                ESPECIFICACIONES TÉCNICAS COMPLETAS
            </h2>
            
            <div style="background: white; border-radius: 12px; overflow: hidden; box-shadow: 0 2px 10px rgba(0,0,0,0.05);">
                <table style="width: 100%; border-collapse: collapse;">
                    <tr style="background: #333; color: white;">
                        <td style="padding: 15px 20px; font-weight: 600; font-size: 14px; text-transform: uppercase; letter-spacing: 0.5px;">Característica</td>
                        <td style="padding: 15px 20px; font-weight: 600; font-size: 14px; text-transform: uppercase; letter-spacing: 0.5px;">Especificación</td>
                    </tr>
                    {rows_html}
                </table>
            </div>
        </div>
    '''

def generar_content_sections_inline(info, marketing_content):
    """Genera las secciones de contenido con iconos mejorados."""
    sections_html = ""
    
    # Sección de puntos clave
    if marketing_content.get('puntos_clave_li'):
        items_html = ""
        for item in marketing_content['puntos_clave_li']:
            icono = obtener_icono_para_item(item)
            items_html += f'''
                <li style="padding: 8px 0; display: flex; align-items: start; gap: 10px;">
                    <div style="min-width: 20px; margin-top: 3px;">{icono}</div>
                    <span>{item}</span>
                </li>
            '''
        
        sections_html += f'''
        <div class="content-section" style="margin: 30px; padding: 30px; background: #fff3e0; border-radius: 12px; box-shadow: 0 2px 10px rgba(0,0,0,0.05); border-left: 4px solid #ff6600;">
            <h3 style="color: #D32F2F; font-size: 24px; margin: 0 0 15px 0; font-weight: 700;">PUNTOS CLAVE</h3>
            <ul style="list-style: none; padding: 0; margin: 0; font-size: 16px; line-height: 1.8; color: #555;">
                {items_html}
            </ul>
        </div>
        '''
    
    # Sección de descripción detallada
    if marketing_content.get('descripcion_detallada_p'):
        descripcion_html = "".join(f"<p>{p}</p>" for p in marketing_content['descripcion_detallada_p'])
        sections_html += f'''
        <div class="content-section" style="margin: 30px; padding: 30px; background: white; border-radius: 12px; box-shadow: 0 2px 10px rgba(0,0,0,0.05); border-left: 4px solid #FFC107;">
            <h3 style="color: #D32F2F; font-size: 24px; margin: 0 0 15px 0; font-weight: 700;">
                CARACTERÍSTICAS PRINCIPALES
            </h3>
            <div style="font-size: 16px; line-height: 1.8; color: #555;">
                {descripcion_html}
            </div>
        </div>
        '''
    
    # Sección de aplicaciones y usos
    if marketing_content.get('aplicaciones_y_usos_p'):
        aplicaciones_html = "".join(f"<p>{p}</p>" for p in marketing_content['aplicaciones_y_usos_p'])
        sections_html += f'''
        <div class="content-section" style="margin: 30px; padding: 30px; background: white; border-radius: 12px; box-shadow: 0 2px 10px rgba(0,0,0,0.05); border-left: 4px solid #FFC107;">
            <h3 style="color: #D32F2F; font-size: 24px; margin: 0 0 15px 0; font-weight: 700;">
                APLICACIONES Y USOS
            </h3>
            <div style="font-size: 16px; line-height: 1.8; color: #555;">
                {aplicaciones_html}
            </div>
        </div>
        '''
    
    # Sección de aplicaciones ideales con iconos específicos
    if marketing_content.get('aplicaciones_ideales_li'):
        items_html = ""
        for item in marketing_content['aplicaciones_ideales_li']:
            icono = obtener_icono_para_item(item)
            items_html += f'''
                <li style="padding: 8px 0; display: flex; align-items: start; gap: 10px;">
                    <div style="min-width: 20px; margin-top: 3px;">{icono}</div>
                    <span>{item}</span>
                </li>
            '''
        
        sections_html += f'''
        <div class="content-section" style="margin: 30px; padding: 30px; background: white; border-radius: 12px; box-shadow: 0 2px 10px rgba(0,0,0,0.05); border-left: 4px solid #4caf50;">
            <h3 style="color: #D32F2F; font-size: 24px; margin: 0 0 15px 0; font-weight: 700;">APLICACIONES IDEALES</h3>
            <ul style="list-style: none; padding: 0; margin: 0; font-size: 16px; line-height: 1.8; color: #555;">
                {items_html}
            </ul>
        </div>
        '''
    
    return sections_html

def generar_benefits_section_inline():
    """Genera la sección de beneficios con iconos mejorados y efectos visuales."""
    return f'''
        <!-- VENTAJAS COMPETITIVAS MEJORADAS -->
        <div style="background: #f8f9fa; padding: 40px 30px; margin-top: 40px; position: relative; overflow: hidden;">
            <!-- Patrón decorativo de fondo -->
            <div style="position: absolute; top: 0; left: 0; right: 0; bottom: 0; opacity: 0.03;">
                <svg width="100%" height="100%" xmlns="http://www.w3.org/2000/svg">
                    <pattern id="dots" x="0" y="0" width="50" height="50" patternUnits="userSpaceOnUse">
                        <circle cx="25" cy="25" r="3" fill="#ff6600"/>
                    </pattern>
                    <rect x="0" y="0" width="100%" height="100%" fill="url(#dots)"/>
                </svg>
            </div>
            
            <h2 style="text-align: center; font-size: 32px; color: #333; margin-bottom: 40px; font-weight: 700; position: relative;">
                POR QUÉ ELEGIR ESTE EQUIPO
            </h2>
            
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 25px; position: relative;">
                <!-- Garantía Oficial -->
                <div class="benefit-card" style="background: white; border-radius: 12px; padding: 30px; text-align: center; box-shadow: 0 2px 10px rgba(0,0,0,0.05); border-top: 3px solid #ff6600; position: relative; overflow: hidden;">
                    <div class="icon-circle" style="width: 70px; height: 70px; background: #fff3e0; border-radius: 50%; margin: 0 auto 20px; display: flex; align-items: center; justify-content: center; position: relative; z-index: 1;">
                        {ICONOS_SVG['shield'].replace('width="28"', 'width="40"').replace('height="28"', 'height="40"')}
                    </div>
                    <h4 style="margin: 0 0 10px 0; color: #333; font-size: 18px; font-weight: 700;">GARANTÍA OFICIAL</h4>
                    <p style="margin: 0; color: #666; font-size: 14px; line-height: 1.6;">Respaldo total del fabricante con servicio post-venta garantizado</p>
                    <div style="position: absolute; bottom: 0; left: 0; right: 0; height: 3px; background: linear-gradient(to right, #ff6600, #ff8833);"></div>
                </div>
                
                <!-- Calidad Certificada -->
                <div class="benefit-card" style="background: white; border-radius: 12px; padding: 30px; text-align: center; box-shadow: 0 2px 10px rgba(0,0,0,0.05); border-top: 3px solid #4caf50; position: relative; overflow: hidden;">
                    <div class="icon-circle" style="width: 70px; height: 70px; background: #e8f5e9; border-radius: 50%; margin: 0 auto 20px; display: flex; align-items: center; justify-content: center; position: relative; z-index: 1;">
                        {ICONOS_SVG['quality'].replace('width="28"', 'width="40"').replace('height="28"', 'height="40"').replace('fill="#4caf50"', 'fill="#4caf50"')}
                    </div>
                    <h4 style="margin: 0 0 10px 0; color: #333; font-size: 18px; font-weight: 700;">CALIDAD CERTIFICADA</h4>
                    <p style="margin: 0; color: #666; font-size: 14px; line-height: 1.6;">Productos que cumplen con las más altas normas internacionales</p>
                    <div style="position: absolute; bottom: 0; left: 0; right: 0; height: 3px; background: linear-gradient(to right, #4caf50, #66bb6a);"></div>
                </div>
                
                <!-- Servicio Técnico -->
                <div class="benefit-card" style="background: white; border-radius: 12px; padding: 30px; text-align: center; box-shadow: 0 2px 10px rgba(0,0,0,0.05); border-top: 3px solid #2196f3; position: relative; overflow: hidden;">
                    <div class="icon-circle" style="width: 70px; height: 70px; background: #e3f2fd; border-radius: 50%; margin: 0 auto 20px; display: flex; align-items: center; justify-content: center; position: relative; z-index: 1;">
                        {ICONOS_SVG['tools'].replace('width="28"', 'width="40"').replace('height="28"', 'height="40"').replace('fill="#ff6600"', 'fill="#2196f3"')}
                    </div>
                    <h4 style="margin: 0 0 10px 0; color: #333; font-size: 18px; font-weight: 700;">SERVICIO TÉCNICO</h4>
                    <p style="margin: 0; color: #666; font-size: 14px; line-height: 1.6;">Red nacional de servicio técnico especializado y repuestos originales</p>
                    <div style="position: absolute; bottom: 0; left: 0; right: 0; height: 3px; background: linear-gradient(to right, #2196f3, #42a5f5);"></div>
                </div>
                
                <!-- Financiación -->
                <div class="benefit-card" style="background: white; border-radius: 12px; padding: 30px; text-align: center; box-shadow: 0 2px 10px rgba(0,0,0,0.05); border-top: 3px solid #ffc107; position: relative; overflow: hidden;">
                    <div class="icon-circle" style="width: 70px; height: 70px; background: #fff8e1; border-radius: 50%; margin: 0 auto 20px; display: flex; align-items: center; justify-content: center; position: relative; z-index: 1;">
                        {ICONOS_SVG['money'].replace('width="28"', 'width="40"').replace('height="28"', 'height="40"').replace('fill="#ff6600"', 'fill="#ffc107"')}
                    </div>
                    <h4 style="margin: 0 0 10px 0; color: #333; font-size: 18px; font-weight: 700;">FINANCIACIÓN</h4>
                    <p style="margin: 0; color: #666; font-size: 14px; line-height: 1.6;">Múltiples opciones de pago y planes de financiación a su medida</p>
                    <div style="position: absolute; bottom: 0; left: 0; right: 0; height: 3px; background: linear-gradient(to right, #ffc107, #ffca28);"></div>
                </div>
            </div>
            
            <!-- Beneficios adicionales con iconos -->
            <div style="margin-top: 40px; padding: 20px; background: white; border-radius: 12px; box-shadow: 0 2px 10px rgba(0,0,0,0.05);">
                <h3 style="text-align: center; color: #333; margin-bottom: 20px; font-size: 20px;">Beneficios Adicionales</h3>
                <div style="display: flex; flex-wrap: wrap; justify-content: center; gap: 20px;">
                    <div style="display: flex; align-items: center; gap: 8px; padding: 10px 20px; background: #f5f5f5; border-radius: 20px;">
                        {ICONOS_SVG['clock']}
                        <span style="font-size: 14px; color: #666;">Entrega Rápida</span>
                    </div>
                    <div style="display: flex; align-items: center; gap: 8px; padding: 10px 20px; background: #f5f5f5; border-radius: 20px;">
                        {ICONOS_SVG['location']}
                        <span style="font-size: 14px; color: #666;">Cobertura Nacional</span>
                    </div>
                    <div style="display: flex; align-items: center; gap: 8px; padding: 10px 20px; background: #f5f5f5; border-radius: 20px;">
                        {ICONOS_SVG['award']}
                        <span style="font-size: 14px; color: #666;">Marca Líder</span>
                    </div>
                    <div style="display: flex; align-items: center; gap: 8px; padding: 10px 20px; background: #f5f5f5; border-radius: 20px;">
                        {ICONOS_SVG['check_circle']}
                        <span style="font-size: 14px; color: #666;">Stock Permanente</span>
                    </div>
                </div>
            </div>
        </div>
    '''

def generar_cta_section_inline(info, config):
    """Genera la sección de call to action con botones mejorados."""
    nombre_producto = info.get('nombre', 'este producto')
    marca = info.get('marca', '')
    modelo = info.get('modelo', '')
    potencia = info.get('potencia_kva', '')
    
    # Construir referencia del producto correctamente
    producto_ref = modelo if modelo else nombre_producto
    if marca and marca not in ['N/D', 'None', '']:
        producto_ref = f"{marca} {producto_ref}"
    
    # Agregar potencia si existe
    potencia_text = f" de {potencia}" if potencia and potencia not in ['N/D', 'None', ''] else ""
    
    mensaje_whatsapp = f"Hola, estoy interesado en el {producto_ref}{potencia_text}. Vi este producto en su tienda online y me gustaría recibir más información sobre precio, disponibilidad y condiciones de entrega. Muchas gracias."
    mensaje_whatsapp_encoded = mensaje_whatsapp.replace(' ', '%20')
    
    pdf_button_html = ''
    if info.get('pdf_url'):
        pdf_button_html = f'''<a href="{info.get('pdf_url', '#')}" target="_blank" 
                   class="btn-hover" style="display: inline-flex; align-items: center; gap: 12px; background: #FFC107; color: #333; padding: 18px 35px; text-decoration: none; border-radius: 30px; font-weight: 600; font-size: 16px; box-shadow: 0 4px 15px rgba(255,193,7,0.3); position: relative;">
                    <svg width="24" height="24" viewBox="0 0 24 24" fill="#333"><path d="M20 2H8c-1.1 0-2 .9-2 2v12c0 1.1.9 2 2 2h12c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2zm-8.5 7.5c0 .83-.67 1.5-1.5 1.5H9v2H7.5V7H10c.83 0 1.5.67 1.5 1.5v1zm5 2c0 .83-.67 1.5-1.5 1.5h-2.5V7H15c.83 0 1.5.67 1.5 1.5v3zm4-3H19v1h1.5V11H19v2h-1.5V7h3v1.5zM9 9.5h1v-1H9v1zM4 6H2v14c0 1.1.9 2 2 2h14v-2H4V6zm10 5.5h1v-3h-1v3z"/></svg>
                    DESCARGAR FICHA TÉCNICA
                </a>'''

    return f'''
        <!-- CALL TO ACTION MEJORADO -->
        <div style="background: linear-gradient(135deg, #1a1a1a 0%, #333333 100%); padding: 50px 30px; text-align: center; position: relative; overflow: hidden;">
            <!-- Elementos decorativos -->
            <div style="position: absolute; top: -50px; left: -50px; width: 150px; height: 150px; background: rgba(255,102,0,0.1); border-radius: 50%;"></div>
            <div style="position: absolute; bottom: -50px; right: -50px; width: 150px; height: 150px; background: rgba(255,193,7,0.1); border-radius: 50%;"></div>
            
            <h2 style="color: #FFC107; font-size: 32px; margin-bottom: 15px; font-weight: 700; text-transform: uppercase; position: relative; z-index: 1;">
                CONSULTE AHORA MISMO
            </h2>
            <p style="color: white; font-size: 18px; margin-bottom: 35px; opacity: 0.9; position: relative, z-index: 1;">
                Nuestros especialistas están listos para asesorarlo
            </p>
            
            <div style="display: flex; flex-wrap: wrap; gap: 20px; justify-content: center; position: relative; z-index: 1;">
                
                <!-- Botón WhatsApp -->
                <a href="https://wa.me/{config.get('whatsapp', '541139563099')}?text={mensaje_whatsapp_encoded}" target="_blank" 
                   class="btn-hover" style="display: inline-flex; align-items: center; gap: 12px; background: #25d366; color: white; padding: 18px 35px; text-decoration: none; border-radius: 30px; font-weight: 600; font-size: 16px; box-shadow: 0 4px 15px rgba(37,211,102,0.3); position: relative;">
                    <svg width="24" height="24" viewBox="0 0 24 24" fill="white"><path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413Z"/></svg>
                    CONSULTAR POR WHATSAPP
                </a>
                
                <!-- Botón PDF -->
                {pdf_button_html}
                
                <!-- Botón Email -->
                <a href="mailto:{config.get('email', 'info@generadores.ar')}?subject=Consulta%20sobre%20{marca}%20{modelo}%20de%20{potencia}&body={mensaje_whatsapp_encoded.replace('%20', '%20')}" 
                   class="btn-hover" style="display: inline-flex; align-items: center; gap: 12px; background: #D32F2F; color: white; padding: 18px 35px; text-decoration: none; border-radius: 30px; font-weight: 600; font-size: 16px; box-shadow: 0 4px 15px rgba(211,47,47,0.3); position: relative;">
                    <svg width="24" height="24" viewBox="0 0 24 24" fill="white"><path d="M20 4H4c-1.1 0-1.99.9-1.99 2L2 18c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V6c0-1.1-.9-2-2-2zm0 4l-8 5-8-5V6l8 5 8-5v2z"/></svg>
                    SOLICITAR COTIZACIÓN
                </a>
                
            </div>
            
            <!-- Indicadores de confianza -->
            <div style="margin-top: 40px; display: flex; justify-content: center; gap: 30px; flex-wrap: wrap;">
                <div style="text-align: center; color: white;">
                    <div style="font-size: 36px; font-weight: 700; color: #FFC107;">+500</div>
                    <div style="font-size: 14px; opacity: 0.8;">Clientes Satisfechos</div>
                </div>
                <div style="text-align: center; color: white;">
                    <div style="font-size: 36px; font-weight: 700; color: #FFC107;">24/7</div>
                    <div style="font-size: 14px; opacity: 0.8;">Soporte Técnico</div>
                </div>
                <div style="text-align: center; color: white;">
                    <div style="font-size: 36px; font-weight: 700; color: #FFC107;">100%</div>
                    <div style="font-size: 14px; opacity: 0.8;">Garantía Original</div>
                </div>
            </div>
        </div>
    '''

def generar_contact_footer_inline(config):
    """Genera el footer de contacto con iconos mejorados."""
    return f'''
        <!-- FOOTER CONTACTO MEJORADO -->
        <div style="background: white; padding: 40px 30px; text-align: center; border-top: 3px solid #FFC107;">
            <div style="display: flex; flex-wrap: wrap; justify-content: center; gap: 40px; margin-bottom: 30px;">
                
                <div>
                    <p style="margin: 0; color: #666; font-size: 14px; display: flex; align-items: center; justify-content: center; gap: 5px;">
                        {ICONOS_SVG['phone'] if 'phone' in ICONOS_SVG else '<svg width="16" height="16" viewBox="0 0 24 24" fill="#666"><path d="M6.62 10.79c1.44 2.83 3.76 5.14 6.59 6.59l2.2-2.2c.27-.27.67-.36 1.02-.24 1.12.37 2.33.57 3.57.57.55 0 1 .45 1 1V20c0 .55-.45 1-1 1-9.39 0-17-7.61-17-17 0-.55.45-1 1-1h3.5c.55 0 1 .45 1 1 0 1.25.2 2.45.57 3.57.11.35.03.74-.25 1.02l-2.2 2.2z"/></svg>'}
                        Teléfono / WhatsApp
                    </p>
                    <a href="https://wa.me/{config.get('whatsapp', '541139563099')}" class="contact-link" style="color: #ff6600; text-decoration: none; font-weight: 600; font-size: 18px;">{config.get('telefono', '+54 11 3956-3099')}</a>
                </div>
                
                <div>
                    <p style="margin: 0; color: #666; font-size: 14px; display: flex; align-items: center; justify-content: center; gap: 5px;">
                        {ICONOS_SVG['email'] if 'email' in ICONOS_SVG else '<svg width="16" height="16" viewBox="0 0 24 24" fill="#666"><path d="M20 4H4c-1.1 0-1.99.9-1.99 2L2 18c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V6c0-1.1-.9-2-2-2zm0 4l-8 5-8-5V6l8 5 8-5v2z"/></svg>'}
                        Email
                    </p>
                    <a href="mailto:{config.get('email', 'info@generadores.ar')}" class="contact-link" style="color: #ff6600; text-decoration: none; font-weight: 600; font-size: 18px;">{config.get('email', 'info@generadores.ar')}</a>
                </div>
                
                <div>
                    <p style="margin: 0; color: #666; font-size: 14px; display: flex; align-items: center; justify-content: center; gap: 5px;">
                        {ICONOS_SVG['web'] if 'web' in ICONOS_SVG else '<svg width="16" height="16" viewBox="0 0 24 24" fill="#666"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-1 17.93c-3.94-.49-7-3.85-7-7.93 0-.62.08-1.21.21-1.79L9 15v1c0 1.1.9 2 2 2v1.93zm6.9-2.54c-.26-.81-1-1.39-1.9-1.39h-1v-3c0-.55-.45-1-1-1H8v-2h2c.55 0 1-.45 1-1V7h2c1.1 0 2-.9 2-2v-.41c2.93 1.19 5 4.06 5 7.41 0 2.08-.8 3.97-2.1 5.39z"/></svg>'}
                        Sitio Web
                    </p>
                    <a href="{config.get('website', 'https://www.generadores.ar')}" target="_blank" class="contact-link" style="color: #ff6600; text-decoration: none; font-weight: 600; font-size: 18px;">{config.get('website', 'www.generadores.ar').replace('https://', '').replace('http://', '')}</a>
                </div>
                
            </div>
            
            <div style="display: flex; flex-wrap: wrap; justify-content: center; gap: 30px; margin-bottom: 20px; padding-top: 20px; border-top: 1px solid #eee;">
                <div style="display: flex; align-items: center; gap: 8px; color: #666; transition: all 0.3s ease; cursor: pointer;" onmouseover="this.style.color='#ff6600'" onmouseout="this.style.color='#666'">
                    {ICONOS_SVG['shield']} <span>Garantía Oficial</span>
                </div>
                <div style="display: flex; align-items: center; gap: 8px; color: #666; transition: all 0.3s ease; cursor: pointer;" onmouseover="this.style.color='#ff6600'" onmouseout="this.style.color='#666'">
                    {ICONOS_SVG['tools']} <span>Servicio Técnico Nacional</span>
                </div>
                <div style="display: flex; align-items: center; gap: 8px; color: #666; transition: all 0.3s ease; cursor: pointer;" onmouseover="this.style.color='#ff6600'" onmouseout="this.style.color='#666'">
                    {ICONOS_SVG['star']} <span>Repuestos Originales</span>
                </div>
                <div style="display: flex; align-items: center; gap: 8px; color: #666; transition: all 0.3s ease; cursor: pointer;" onmouseover="this.style.color='#ff6600'" onmouseout="this.style.color='#666'">
                    {ICONOS_SVG['money']} <span>Financiación Disponible</span>
                </div>
            </div>
            
            <p style="color: #999; font-size: 13px; margin: 0;">
                Distribuidor Oficial | Todos los derechos reservados
            </p>
        </div>
    '''

def validar_y_limpiar_datos(info):
    """Limpia y valida los datos antes de generar el HTML"""
    
    # Eliminar campos duplicados o internos
    campos_a_eliminar = [
        'potencia_valor', 'potencia_unidad',
        'nivel_ruido_dba', 'nivel_ruido_valor', 'nivel_ruido_unidad'
    ]
    
    for campo in campos_a_eliminar:
        info.pop(campo, None)
    
    # Normalizar campos específicos
    if 'nivel_sonoro' not in info and 'nivel_ruido_dba' in info:
        info['nivel_sonoro'] = info.pop('nivel_ruido_dba')
    
    return info

def generar_css_hover_effects():
    """Genera los estilos CSS mejorados con nuevas animaciones."""
    return '''
    <style>
        /* Estilos para efectos hover mejorados */
        .card-hover {
            transition: all 0.3s ease;
            cursor: pointer;
        }
        .card-hover:hover {
            transform: translateY(-5px);
            box-shadow: 0 8px 25px rgba(0,0,0,0.15) !important;
        }
        .card-hover:hover .icon-wrapper {
            transform: rotate(15deg) scale(1.1);
            background: #ff6600 !important;
        }
        .card-hover:hover .icon-wrapper svg {
            fill: white !important;
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
        
        .icon-wrapper {
            transition: all 0.3s ease;
        }
        
        .btn-hover {
            transition: all 0.3s ease !important;
            position: relative;
            overflow: hidden;
        }
        .btn-hover:before {
            content: '';
            position: absolute;
            top: 50%;
            left: 50%;
            width: 0;
            height: 0;
            border-radius: 50%;
            background: rgba(255,255,255,0.2);
            transform: translate(-50%, -50%);
            transition: width 0.6s, height 0.6s;
        }
        .btn-hover:hover {
            transform: translateY(-3px) scale(1.05) !important;
            box-shadow: 0 8px 25px rgba(0,0,0,0.25) !important;
        }
        .btn-hover:hover:before {
            width: 300px;
            height: 300px;
        }
        
        .spec-row {
            transition: all 0.2s ease;
        }
        .spec-row:hover {
            background: #fff3e0 !important;
            transform: translateX(5px);
        }
        .spec-row:hover td:first-child div {
            transform: scale(1.2);
            opacity: 1 !important;
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
        
        @keyframes float {
            0% { transform: translateY(0px); }
            50% { transform: translateY(-10px); }
            100% { transform: translateY(0px); }
        }
        
        .special-feature {
            animation: pulse 2s infinite;
        }
        .special-feature:hover {
            animation: float 2s infinite;
        }
        
        /* Animación para iconos */
        @keyframes spin {
            from { transform: rotate(0deg); }
            to { transform: rotate(360deg); }
        }
        
        .icon-wrapper:hover svg {
            animation: spin 1s ease-in-out;
        }
        
        /* Efecto de brillo en badges */
        .special-feature:after {
            content: '';
            position: absolute;
            top: -50%;
            left: -50%;
            width: 200%;
            height: 200%;
            background: linear-gradient(45deg, transparent 30%, rgba(255,255,255,0.3) 50%, transparent 70%);
            transform: rotate(45deg);
            transition: all 0.6s;
            opacity: 0;
        }
        .special-feature:hover:after {
            animation: shine 0.6s ease-in-out;
        }
        
        @keyframes shine {
            0% { transform: translateX(-100%) translateY(-100%) rotate(45deg); opacity: 0; }
            50% { opacity: 1; }
            100% { transform: translateX(100%) translateY(100%) rotate(45deg); opacity: 0; }
        }
    </style>
    '''
