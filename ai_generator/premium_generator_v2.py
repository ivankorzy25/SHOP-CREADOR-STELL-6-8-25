# -*- coding: utf-8 -*-
"""
Módulo para la generación de descripciones HTML premium de productos.
Versión 3.0 - Completamente reescrito con arquitectura modular
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

# Importar los nuevos módulos
from .data_processor import UniversalDataProcessor
from .efficiency_calculator import UniversalEfficiencyCalculator
from .feature_detector import UniversalFeatureDetector

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
    
    # Nuevos iconos
    'autonomia': '<svg width="20" height="20" viewBox="0 0 24 24" fill="#D32F2F"><path d="M12 2C6.5 2 2 6.5 2 12s4.5 10 10 10 10-4.5 10-10S17.5 2 12 2zm0 18c-4.41 0-8-3.59-8-8s3.59-8 8-8 8 3.59 8 8-3.59 8-8 8zm.5-13H11v6l5.25 3.15.75-1.23-4.5-2.67z"/></svg>',
    'capacidad': '<svg width="20" height="20" viewBox="0 0 24 24" fill="#D32F2F"><path d="M3 2v2h1v16h5v-8h6v8h5V4h1V2H3zm3 4h3v3H6V6zm6 0h3v3h-3V6zm6 0h3v3h-3V6z"/></svg>',
    'arranque': '<svg width="20" height="20" viewBox="0 0 24 24" fill="#D32F2F"><path d="M12 2l-5.5 9h11z"/><circle cx="17.5" cy="17.5" r="4.5"/><path d="M3 13.5h8v8H3z"/></svg>',
    'cilindrada': '<svg width="20" height="20" viewBox="0 0 24 24" fill="#D32F2F"><path d="M19 3h-1V1h-2v2H8V1H6v2H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm0 16H5V8h14v11z"/></svg>',
    'rpm': '<svg width="20" height="20" viewBox="0 0 24 24" fill="#D32F2F"><path d="M4.01 6.03l7.51 3.22-5.84 1.25z"/><path d="M11.53 10.23l-8.66 4.49c-.37.2-.6.59-.57 1 .03.42.29.78.67.96l11.16 5.13c.38.17.82.13 1.15-.11.33-.23.52-.61.5-1.01l-.39-11.63c-.02-.41-.26-.77-.62-.96-.35-.19-.78-.17-1.12.05z"/><path d="M18.89 11.62c-.03-.41-.29-.78-.67-.95L7.06 5.54c-.38-.18-.82-.13-1.15.1-.33.24-.52.62-.5 1.02l.39 11.62c.02.42.26.77.61.96.16.09.33.13.5.13.21 0 .42-.07.62-.19l8.66-4.49c.37-.19.61-.58.58-1z"/></svg>',
    'clock': '<svg width="20" height="20" viewBox="0 0 24 24" fill="#D32F2F"><path d="M12 2C6.5 2 2 6.5 2 12s4.5 10 10 10 10-4.5 10-10S17.5 2 12 2zm0 18c-4.41 0-8-3.59-8-8s3.59-8 8-8 8 3.59 8 8-3.59 8-8 8zm.5-13H11v6l5.25 3.15.75-1.23-4.5-2.67z"/></svg>',
    'fuel': '<svg width="20" height="20" viewBox="0 0 24 24" fill="#D32F2F"><path d="M19.77 7.23l.01-.01-3.72-3.72L15 4.56l2.11 2.11c-.94.36-1.61 1.26-1.61 2.33 0 1.38 1.12 2.5 2.5 2.5.36 0 .69-.08 1-.21v7.21c0 .55-.45 1-1 1s-1-.45-1-1V14c0-1.1-.9-2-2-2h-1V5c0-1.1-.9-2-2-2H6c-1.1 0-2 .9-2 2v16h10v-7.5h1.5v5c0 1.38 1.12 2.5 2.5 2.5s2.5-1.12 2.5-2.5V9c0-.69-.28-1.32-.73-1.77zM12 10H6V5h6v5zm6 0c.55 0 1-.45 1-1s-.45-1-1-1-1 .45-1 1 .45 1 1 1z"/></svg>',
    'lightning': '<svg width="20" height="20" viewBox="0 0 24 24" fill="#D32F2F"><path d="M7 2v11h3v9l7-12h-4l4-8z"/></svg>',
    'settings': '<svg width="20" height="20" viewBox="0 0 24 24" fill="#D32F2F"><path d="M12 15.5c-1.93 0-3.5-1.57-3.5-3.5s1.57-3.5 3.5-3.5 3.5 1.57 3.5 3.5-1.57 3.5-3.5 3.5zm7.43-2.53c.04-.32.07-.64.07-.97s-.03-.66-.07-.98l2.11-1.65c.19-.15.24-.42.12-.64l-2-3.46c-.12-.22-.39-.3-.61-.22l-2.49 1c-.52-.4-1.08-.73-1.69-.98l-.38-2.65C14.46 2.18 14.25 2 14 2h-4c-.25 0-.46.18-.49.42l-.38 2.65c-.61.25-1.17.59-1.69.98l-2.49-1c-.23-.09-.49 0-.61.22l-2 3.46c-.13.22-.07.49.12.64l2.11 1.65c-.04.32-.07.65-.07.98s.03.66.07.98l-2.11 1.65c-.19.15-.24.42-.12.64l2 3.46c.12.22.39.3.61.22l2.49-1c.52.4 1.08.73 1.69.98l.38 2.65c.03.24.24.42.49.42h4c.25 0 .46-.18.49-.42l.38-2.65c.61-.25 1.17-.59 1.69-.98l2.49 1c.23.09.49 0 .61-.22l2-3.46c.12-.22.07-.49-.12-.64l-2.11-1.65z"/></svg>',
    'battery': '<svg width="20" height="20" viewBox="0 0 24 24" fill="#D32F2F"><path d="M15.67 4H14V2h-4v2H8.33C7.6 4 7 4.6 7 5.33v15.33c0 .74.6 1.34 1.33 1.34h7.33c.74 0 1.34-.6 1.34-1.33V5.33C17 4.6 16.4 4 15.67 4z"/></svg>',
    'bolt': '<svg width="20" height="20" viewBox="0 0 24 24" fill="#D32F2F"><path d="M11 21h-1l1-7H7.5c-.58 0-.57-.32-.38-.66.19-.34.05-.08.07-.12C8.48 10.94 10.42 7.54 13 3h1l-1 7h3.5c.49 0 .56.33.47.51l-.07.15C12.96 17.55 11 21 11 21z"/></svg>',
    'power': '<svg width="20" height="20" viewBox="0 0 24 24" fill="#D32F2F"><path d="M16.01 7L16 3h-2v4h-4V3H8v4l-.01 4c0 .38.04.74.14 1.08l.57 1.92h6.6l.57-1.92c.1-.34.14-.7.14-1.08L16.01 7zM12 21c2.21 0 4-1.79 4-4v-1H8v1c0 2.21 1.79 4 4 4z"/></svg>',
    'cpu': '<svg width="20" height="20" viewBox="0 0 24 24" fill="#D32F2F"><path d="M9 2v2H7c-1.1 0-2 .9-2 2v2H3v2h2v2H3v2h2v2c0 1.1.9 2 2 2h2v2h2v-2h2v2h2v-2h2c1.1 0 2-.9 2-2v-2h2v-2h-2v-2h2V8h-2V6c0-1.1-.9-2-2-2h-2V2h-2v2h-2V2H9zm8 14H7V8h10v8z"/></svg>',
    'monitor': '<svg width="20" height="20" viewBox="0 0 24 24" fill="#D32F2F"><path d="M21 2H3c-1.1 0-2 .9-2 2v12c0 1.1.9 2 2 2h7l-2 3v1h8v-1l-2-3h7c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2zm0 12H3V4h18v10z"/></svg>',
    'ruler': '<svg width="20" height="20" viewBox="0 0 24 24" fill="#D32F2F"><path d="M7 2h10c1.1 0 2 .9 2 2v16c0 1.1-.9 2-2 2H7c-1.1 0-2-.9-2-2V4c0-1.1.9-2 2-2zm0 2v4h2V4H7zm0 6v2h2v-2H7zm0 4v4h2v-4H7zm4-10v2h2V4h-2zm0 4v2h2V8h-2zm0 4v2h2v-2h-2zm0 4v2h2v-2h-2zm4-12v8h2V4h-2zm0 10v2h2v-2h-2zm0 4v4h2v-4h-2z"/></svg>',
    'weight': '<svg width="20" height="20" viewBox="0 0 24 24" fill="#D32F2F"><path d="M12 3c-1.27 0-2.4.8-2.82 2H3v2h1.95l2 7c.17.59.71 1 1.32 1H15.73c.61 0 1.15-.41 1.32-1l2-7H21V5h-6.18C14.4 3.8 13.27 3 12 3zm0 2c.55 0 1 .45 1 1s-.45 1-1 1-1-.45-1-1 .45-1 1-1z"/></svg>',
    'volume': '<svg width="20" height="20" viewBox="0 0 24 24" fill="#D32F2F"><path d="M3 9v6h4l5 5V4L7 9H3zm13.5 3c0-1.77-1.02-3.29-2.5-4.03v8.05c1.48-.73 2.5-2.25 2.5-4.02z"/></svg>',
    'thermometer': '<svg width="20" height="20" viewBox="0 0 24 24" fill="#D32F2F"><path d="M15 13V5c0-1.66-1.34-3-3-3S9 3.34 9 5v8c-1.21.91-2 2.37-2 4 0 2.76 2.24 5 5 5s5-2.24 5-5c0-1.63-.79-3.09-2-4zm-4-8c0-.55.45-1 1-1s1 .45 1 1h-1v1h1v2h-1v1h1v2h-2V5z"/></svg>',
    'zap': '<svg width="20" height="20" viewBox="0 0 24 24" fill="#D32F2F"><path d="M7 2v11h3v9l7-12h-4l4-8z"/></svg>',
    'activity': '<svg width="20" height="20" viewBox="0 0 24 24" fill="#D32F2F"><path d="M22 12h-4l-3 9L9 3l-3 9H2"/></svg>',
    'award': '<svg width="20" height="20" viewBox="0 0 24 24" fill="#D32F2F"><circle cx="12" cy="8" r="7"/><path d="M8.21 13.89L7 23l5-3 5 3-1.21-9.11"/></svg>',
    'gauge': '<svg width="20" height="20" viewBox="0 0 24 24" fill="#D32F2F"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/></svg>',
    'droplet': '<svg width="20" height="20" viewBox="0 0 24 24" fill="#D32F2F"><path d="M12 2.69l5.66 5.66c1.56 1.56 1.56 4.1 0 5.66s-4.1 1.56-5.66 0-1.56-4.1 0-5.66L12 2.69z"/></svg>',
    'circle': '<svg width="20" height="20" viewBox="0 0 24 24" fill="#D32F2F"><circle cx="12" cy="12" r="10"/></svg>',
    'disc': '<svg width="20" height="20" viewBox="0 0 24 24" fill="#D32F2F"><circle cx="12" cy="12" r="3"/><circle cx="12" cy="12" r="10" fill="none" stroke="#D32F2F" stroke-width="2"/></svg>',
    'percent': '<svg width="20" height="20" viewBox="0 0 24 24" fill="#D32F2F"><line x1="19" y1="5" x2="5" y2="19"/><circle cx="6.5" cy="6.5" r="2.5"/><circle cx="17.5" cy="17.5" r="2.5"/></svg>',
    'move': '<svg width="20" height="20" viewBox="0 0 24 24" fill="#D32F2F"><polyline points="5 9 2 12 5 15"/><polyline points="9 5 12 2 15 5"/><polyline points="15 19 12 22 9 19"/><polyline points="19 9 22 12 19 15"/><line x1="2" y1="12" x2="22" y2="12"/><line x1="12" y1="2" x2="12" y2="22"/></svg>',
    'volume-x': '<svg width="20" height="20" viewBox="0 0 24 24" fill="#D32F2F"><polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"/><line x1="23" y1="9" x2="17" y2="15"/><line x1="17" y1="9" x2="23" y2="15"/></svg>',
    'hand': '<svg width="20" height="20" viewBox="0 0 24 24" fill="#D32F2F"><path d="M18 11V8.5c0-.83-.67-1.5-1.5-1.5s-1.5.67-1.5 1.5V11h-1V1.5c0-.83-.67-1.5-1.5-1.5S11 .67 11 1.5V11h-1V2.5c0-.83-.67-1.5-1.5-1.5S7 1.67 7 2.5V11H6V5.5C6 4.67 5.33 4 4.5 4S3 4.67 3 5.5V15c0 4.42 3.58 8 8 8h1c4.42 0 8-3.58 8-8v-3.5c0-.83-.67-1.5-1.5-1.5s-1.5.67-1.5 1.5V11h-1z"/></svg>',
    'factory': '<svg width="20" height="20" viewBox="0 0 24 24" fill="#D32F2F"><path d="M2 20h20v2H2v-2zm2-8v5h2v-5h3v5h2v-5h3v5h2v-5h3l1 5h2l-1.33-6.67C21.67 9.6 21.4 9 20.67 9H14V7h-4v2H3c-.55 0-1 .45-1 1v2h2z"/></svg>',
    'briefcase': '<svg width="20" height="20" viewBox="0 0 24 24" fill="#D32F2F"><path d="M10 2v2H5.01c-1.1 0-2 .9-2 2L3 19c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V6c0-1.1-.9-2-2-2H14V2h-4zm4 4V4h-4v2h4z"/></svg>',
    'trending-up': '<svg width="20" height="20" viewBox="0 0 24 24" fill="#D32F2F"><polyline points="23 6 13.5 15.5 8.5 10.5 1 18"/><polyline points="17 6 23 6 23 12"/></svg>',
    'battery-charging': '<svg width="20" height="20" viewBox="0 0 24 24" fill="#D32F2F"><path d="M5 18H3l4-8v6h2l-4 8v-6zM21 10h-7V4.41c0-.89-.36-1.42-1.02-1.42H8.02C7.36 3 7 3.53 7 4.41V10H0v11.59c0 .89.36 1.41 1.02 1.41h13.96c.67 0 1.02-.53 1.02-1.41V10z"/></svg>',
    'engine': '<svg width="20" height="20" viewBox="0 0 24 24" fill="#D32F2F"><path d="M7 4v2h3v2H7l-2 2v3h2v2H5v3h2v2h3v-2h10v2h3v-2h2v-3h-2v-2h2V9l-2-2h-3V5h3V3h-3c-1.1 0-2 .9-2 2v2h-6V5c0-1.1-.9-2-2-2H7zm10 5v6h-6V9h6z"/></svg>',
    'tachometer': '<svg width="20" height="20" viewBox="0 0 24 24" fill="#D32F2F"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 18c-4.41 0-8-3.59-8-8s3.59-8 8-8 8 3.59 8 8-3.59 8-8 8zm-5.5-2.5l7.51-3.49c.85-.4.85-1.61 0-2.01l-7.51-3.49c-.85-.4-1.84.2-1.84 1.11v6.77c0 .91.99 1.51 1.84 1.11z"/></svg>',
    'database': '<svg width="20" height="20" viewBox="0 0 24 24" fill="#D32F2F"><ellipse cx="12" cy="5" rx="9" ry="3"/><path d="M21 12c0 1.66-4 3-9 3s-9-1.34-9-3"/><path d="M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5"/></svg>',
    'wind': '<svg width="20" height="20" viewBox="0 0 24 24" fill="#D32F2F"><path d="M9.59 4.59C10.36 3.82 11.41 3.41 12.5 3.41c2.21 0 4 1.79 4 4s-1.79 4-4 4H2"/><path d="M2 15h16.17c1.39 0 2.66-.57 3.57-1.48.91-.91 1.48-2.18 1.48-3.57 0-2.78-2.26-5.04-5.04-5.04-1.39 0-2.66.57-3.57 1.48"/></svg>',
    'tractor': '<svg width="20" height="20" viewBox="0 0 24 24" fill="#D32F2F"><circle cx="7" cy="17" r="3"/><circle cx="17" cy="17" r="3"/><path d="M7 14h10v-4L13 7H9v7z"/></svg>',
    'tree': '<svg width="20" height="20" viewBox="0 0 24 24" fill="#D32F2F"><path d="M15 21v-4.24c-.5.17-1.02.24-1.55.24h-.1c-.51 0-1.02-.07-1.51-.21l-.84 3.13c-.1.35.08.72.42.87.34.14.72-.01.89-.32l.61-1.14c.24-.44.89-.44 1.13 0l.61 1.14c.13.24.38.39.64.39.08 0 .17-.02.25-.06.34-.15.52-.52.42-.87l-.87-3.13zm-7.65-1.67c.23-.45.89-.45 1.12 0l.59 1.11c.13.24.38.39.65.39.09 0 .17-.02.26-.06.34-.15.51-.52.41-.87l-.82-3.02c-.09-.34-.41-.58-.77-.58s-.68.24-.77.58l-.82 3.02c-.1.35.07.72.41.87s.72-.01.89-.32l.59-1.12zm11.78-5.37c.34-.15.51-.52.41-.87l-.91-3.36c-.09-.34-.41-.58-.77-.58s-.68.24-.77.58l-.91 3.36c-.1.35.07.72.41.87.09.04.17.06.26.06.26 0 .51-.15.64-.39l.66-1.23c.11-.22.33-.35.57-.35s.46.13.57.35l.66 1.23c.13.24.38.39.64.39.09 0 .18-.02.27-.06zM11 10.5c0-.55.45-1 1-1s1 .45 1 1-.45 1-1 1-1-.45-1-1zm0-4c0-.55.45-1 1-1s1 .45 1 1-.45 1-1 1-1-.45-1-1zm4 2c0-.55.45-1 1-1s1 .45 1 1-.45 1-1 1-1-.45-1-1zm-8 0c0-.55.45-1 1-1s1 .45 1 1-.45 1-1 1-1-.45-1-1z"/></svg>',
    'spray': '<svg width="20" height="20" viewBox="0 0 24 24" fill="#D32F2F"><path d="M18 1.5V5h-1V1.5c0-.28.22-.5.5-.5s.5.22.5.5zM11 8c0-1.1.9-2 2-2h6c1.1 0 2 .9 2 2v5c0 1.1-.9 2-2 2h-1v4c0 1.1-.9 2-2 2h-4c-1.1 0-2-.9-2-2V8zm9.5-4.5c0-.28-.22-.5-.5-.5s-.5.22-.5.5V5h1V3.5zm1 0c0-.28-.22-.5-.5-.5s-.5.22-.5.5V5h1V3.5z"/></svg>',
    'hammer': '<svg width="20" height="20" viewBox="0 0 24 24" fill="#D32F2F"><path d="M2 19.63L13.43 8.2l-.71-.71c-1.17-1.17-1.17-3.07 0-4.24l2.83 2.83c1.17-1.17 3.07-1.17 4.24 0l-.71.71L8.37 18.22c-.78.78-2.05.78-2.83 0l-3.54-3.54c-.78-.79-.78-2.05 0-2.83z"/></svg>',
    'tool': '<svg width="20" height="20" viewBox="0 0 24 24" fill="#D32F2F"><path d="M22.7 19l-9.1-9.1c.9-2.3.4-5-1.5-6.9-2-2-5-2.4-7.4-1.3L9 6 6 9 1.6 4.7C.4 7.1.9 10.1 2.9 12.1c1.9 1.9 4.6 2.4 6.9 1.5l9.1 9.1c.4.4 1 .4 1.4 0l2.3-2.3c.5-.4.5-1.1.1-1.4z"/></svg>',
    'info': '<svg width="20" height="20" viewBox="0 0 24 24" fill="#D32F2F"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-6h2v6zm0-8h-2V7h2v2z"/></svg>',
    'star': '<svg width="20" height="20" viewBox="0 0 24 24" fill="#D32F2F"><path d="M12 17.27L18.18 21l-1.64-7.03L22 9.24l-7.19-.61L12 2 9.19 8.63 2 9.24l5.46 4.73L5.82 21z"/></svg>',
    'check-circle': '<svg width="20" height="20" viewBox="0 0 24 24" fill="#D32F2F"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/></svg>',
    'info-circle': '<svg width="20" height="20" viewBox="0 0 24 24" fill="#D32F2F"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-6h2v6zm0-8h-2V7h2v2z"/></svg>',
    'zap-off': '<svg width="20" height="20" viewBox="0 0 24 24" fill="#D32F2F"><polyline points="12.41 6.75 13 2 10.57 4.92"/><polyline points="18.57 12.91 21 10 15.66 10"/><polyline points="8 8 3 3"/><line x1="1" y1="1" x2="23" y2="23"/><path d="M9 12H4l7 12v-6h5l1.86-3.15"/></svg>'
}

# ============================================================================
# FUNCIONES PRINCIPALES DE GENERACIÓN
# ============================================================================

def procesar_producto_universal(info: dict) -> tuple:
    """
    Procesa cualquier producto usando los módulos universales
    
    Returns:
        tuple: (datos_limpios, caracteristicas, eficiencia)
    """
    # 1. Limpiar datos con UniversalDataProcessor
    datos_limpios = UniversalDataProcessor.clean_all_data(info)
    
    # 2. Detectar características con UniversalFeatureDetector
    caracteristicas = UniversalFeatureDetector.detect_all(datos_limpios)
    
    # 3. Calcular eficiencia con UniversalEfficiencyCalculator
    eficiencia = UniversalEfficiencyCalculator.calculate(datos_limpios)
    
    # Agregar eficiencia a datos limpios
    datos_limpios['eficiencia_data'] = eficiencia
    
    return datos_limpios, caracteristicas, eficiencia

def obtener_icono_svg(campo: str) -> str:
    """Obtiene el icono SVG apropiado para un campo"""
    # Usar el detector de características para obtener el icono
    icono_nombre = UniversalFeatureDetector.get_icon_for_field(campo)
    
    # Buscar en el diccionario de SVG
    if icono_nombre in ICONOS_SVG:
        return ICONOS_SVG[icono_nombre]
    
    # Default
    return ICONOS_SVG.get('info', '')

def extraer_info_motor_limpia(info: dict) -> str:
    """Extrae información del motor sin redundancia"""
    motor = str(info.get('motor', '')).strip()
    
    # Si no hay información, retornar vacío
    if not motor or motor in ['N/D', 'None', '']:
        return ''
    
    # Si ya está bien formateado, retornarlo
    if any(marca in motor.upper() for marca in ['HONDA', 'YAMAHA', 'CUMMINS', 'PERKINS', 'KOHLER']):
        return motor
    
    # Si dice "Motor X HP", está bien
    if motor.lower().startswith('motor ') and 'hp' in motor.lower():
        return motor
    
    # Si es solo potencia, formatear
    match = re.match(r'^(\d+\.?\d*)\s*HP$', motor, re.IGNORECASE)
    if match:
        return f"Motor {match.group(1)} HP"
    
    return motor

def generar_specs_table_inline(info: dict) -> str:
    """Genera tabla de especificaciones con estilos inline"""
    # Usar el procesador para obtener datos limpios
    datos_limpios = UniversalDataProcessor.clean_all_data(info)
    
    # Campos a mostrar en orden
    campos_ordenados = [
        'modelo', 'potencia', 'motor', 'combustible', 'consumo',
        'capacidad_tanque', 'autonomia', 'arranque', 'voltaje',
        'frecuencia', 'peso', 'dimensiones', 'nivel_ruido'
    ]
    
    # HTML de la tabla
    table_html = '''
    <table style="width: 100%; border-collapse: collapse; margin: 20px 0; background: white; box-shadow: 0 2px 4px rgba(0,0,0,0.1); border-radius: 8px; overflow: hidden;">
        <tbody>
    '''
    
    # Generar filas
    row_count = 0
    for campo in campos_ordenados:
        # Buscar el campo en los datos limpios
        valor = None
        campo_real = None
        
        # Buscar coincidencia exacta o parcial
        for key, value in datos_limpios.items():
            if campo in key or key in campo:
                valor = value
                campo_real = key
                break
        
        if valor and str(valor).strip() not in ['', 'N/D', 'None']:
            # Obtener nombre display
            nombre_display = UniversalDataProcessor.get_display_name(campo_real or campo)
            
            # Obtener icono
            icono_svg = obtener_icono_svg(campo)
            
            # Color de fondo alternado
            bg_color = '#f8f9fa' if row_count % 2 == 0 else '#ffffff'
            
            table_html += f'''
            <tr style="background-color: {bg_color}; border-bottom: 1px solid #e0e0e0;">
                <td style="padding: 12px 15px; font-weight: 500; color: #333; border-right: 1px solid #e0e0e0; width: 40%; vertical-align: middle;">
                    <div style="display: flex; align-items: center; gap: 10px;">
                        {icono_svg}
                        <span>{nombre_display}</span>
                    </div>
                </td>
                <td style="padding: 12px 15px; color: #666; vertical-align: middle;">
                    {valor}
                </td>
            </tr>
            '''
            row_count += 1
    
    table_html += '''
        </tbody>
    </table>
    '''
    
    return table_html if row_count > 0 else '<p>No hay especificaciones disponibles</p>'

def generar_mini_cards_adicionales(caracteristicas: dict) -> str:
    """Genera mini cards con características especiales"""
    html = ''
    
    # Generar cards para badges especiales
    badges = caracteristicas.get('badges_especiales', [])
    
    if badges:
        html += '''
        <div style="display: flex; flex-wrap: wrap; gap: 15px; margin: 20px 0;">
        '''
        
        for badge in badges[:4]:  # Máximo 4 badges
            icono = ICONOS_SVG.get(badge.get('icono', 'info'), ICONOS_SVG['info'])
            color = badge.get('color', '#ff6600')
            texto = badge.get('texto', '')
            
            html += f'''
            <div style="flex: 1; min-width: 200px; background: white; border-radius: 8px; 
                        padding: 15px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); 
                        border-left: 4px solid {color};">
                <div style="display: flex; align-items: center; gap: 10px;">
                    <div style="color: {color};">{icono}</div>
                    <span style="font-weight: 600; color: #333; font-size: 14px;">
                        {texto}
                    </span>
                </div>
            </div>
            '''
        
        html += '</div>'
    
    return html

def generar_badge_eficiencia(eficiencia_data: dict) -> str:
    """Genera badge de eficiencia visual"""
    porcentaje = eficiencia_data.get('porcentaje', 60)
    color = eficiencia_data.get('color', '#FFC107')
    texto = eficiencia_data.get('texto', 'Eficiencia Normal')
    
    # Determinar icono según porcentaje
    if porcentaje >= 80:
        icono = ICONOS_SVG.get('star', '')
    elif porcentaje >= 60:
        icono = ICONOS_SVG.get('check-circle', '')
    else:
        icono = ICONOS_SVG.get('info-circle', '')
    
    return f'''
    <div style="display: inline-flex; align-items: center; gap: 8px; 
                background: {color}22; padding: 8px 16px; border-radius: 20px;
                border: 2px solid {color};">
        <div style="color: {color};">{icono}</div>
        <span style="font-weight: 600; color: {color};">
            {texto} ({porcentaje}%)
        </span>
    </div>
    '''

def generar_cta_whatsapp(info: dict, config: dict) -> str:
    """Genera CTA de WhatsApp con información del producto"""
    marca = info.get('marca', '')
    modelo = info.get('modelo', '')
    whatsapp = config.get('whatsapp', '')
    
    # Construir mensaje
    producto_ref = f"{marca} {modelo}".strip() if marca and modelo else "este producto"
    mensaje = f"Hola! Me interesa obtener más información sobre el {producto_ref}. ¿Podrían ayudarme?"
    
    # URL de WhatsApp
    whatsapp_url = f"https://wa.me/{whatsapp}?text={mensaje}"
    
    return f'''
    <div style="text-align: center; margin: 30px 0;">
        <a href="{whatsapp_url}" target="_blank" style="display: inline-flex; align-items: center; 
           gap: 10px; background: #25D366; color: white; padding: 15px 30px; 
           border-radius: 30px; text-decoration: none; font-weight: 600; 
           font-size: 16px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); 
           transition: all 0.3s ease;"
           onmouseover="this.style.transform='translateY(-2px)'; this.style.boxShadow='0 6px 12px rgba(0,0,0,0.15)';"
           onmouseout="this.style.transform='translateY(0)'; this.style.boxShadow='0 4px 6px rgba(0,0,0,0.1)';">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="white">
                <path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.693.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413Z"/>
            </svg>
            Consultar por WhatsApp
        </a>
    </div>
    '''

# ============================================================================
# FUNCIONES DE EXTRACCIÓN DE PDF (sin cambios)
# ============================================================================

def extraer_texto_pdf_online(url):
    """Extrae texto de un PDF online"""
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        # Intentar con PyMuPDF primero
        try:
            pdf_document = fitz.open(stream=response.content, filetype="pdf")
            texto_completo = ""
            
            for pagina_num in range(len(pdf_document)):
                pagina = pdf_document[pagina_num]
                texto_completo += pagina.get_text()
            
            pdf_document.close()
            
            if texto_completo.strip():
                return texto_completo
                
        except Exception:
            pass
        
        # Si falla, intentar con PyPDF2
        pdf_file = io.BytesIO(response.content)
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        
        texto_completo = ""
        for pagina in pdf_reader.pages:
            texto_completo += pagina.extract_text()
        
        return texto_completo
        
    except Exception as e:
        print(f"Error extrayendo PDF: {str(e)}")
        return ""

def extraer_info_de_pdf(texto_pdf, campos_buscar):
    """Extrae información específica del texto del PDF"""
    info_extraida = {}
    texto_lower = texto_pdf.lower()
    
    # Patrones mejorados de búsqueda
    patrones = {
        'motor': [
            r'motor[:\s]+([^\n]+)',
            r'engine[:\s]+([^\n]+)',
            r'marca motor[:\s]+([^\n]+)',
            r'motor.*?(\d+\.?\d*\s*hp)',
            r'motor.*?(\d+\.?\d*\s*cv)'
        ],
        'cilindrada': [
            r'cilindrada[:\s]+(\d+\.?\d*)\s*(cc|cm3|cm³)',
            r'displacement[:\s]+(\d+\.?\d*)\s*(cc|cm3|cm³)',
            r'(\d+\.?\d*)\s*(cc|cm3|cm³)'
        ],
        'consumo': [
            r'consumo[:\s]+(\d+\.?\d*)\s*l/h',
            r'consumo.*?(\d+\.?\d*)\s*litros/hora',
            r'fuel consumption[:\s]+(\d+\.?\d*)\s*l/h',
            r'consumo\s+(?:a\s+)?75%[:\s]+(\d+\.?\d*)\s*l/h'
        ],
        'capacidad_tanque': [
            r'capacidad (?:del )?tanque[:\s]+(\d+\.?\d*)\s*(?:l|litros)',
            r'tanque (?:de )?combustible[:\s]+(\d+\.?\d*)\s*(?:l|litros)',
            r'fuel tank[:\s]+(\d+\.?\d*)\s*(?:l|liters)',
            r'depósito[:\s]+(\d+\.?\d*)\s*(?:l|litros)'
        ],
        'autonomia': [
            r'autonomía[:\s]+(\d+\.?\d*)\s*(?:h|horas)',
            r'runtime[:\s]+(\d+\.?\d*)\s*(?:h|hours)',
            r'tiempo de funcionamiento[:\s]+(\d+\.?\d*)\s*(?:h|horas)'
        ],
        'nivel_ruido': [
            r'nivel (?:de )?ruido[:\s]+(\d+\.?\d*)\s*db',
            r'nivel sonoro[:\s]+(\d+\.?\d*)\s*db',
            r'noise level[:\s]+(\d+\.?\d*)\s*db',
            r'(\d+\.?\d*)\s*db\s*(?:@|a)\s*7\s*m'
        ]
    }
    
    # Buscar cada campo
    for campo, patrones_campo in patrones.items():
        if campo in campos_buscar:
            for patron in patrones_campo:
                match = re.search(patron, texto_lower, re.IGNORECASE)
                if match:
                    info_extraida[campo] = match.group(1).strip()
                    break
    
    return info_extraida

# ============================================================================
# FUNCIONES EXPORTADAS PARA COMPATIBILIDAD
# ============================================================================

# Mantener funciones existentes para compatibilidad
def validar_y_limpiar_datos_universal(info):
    """Función de compatibilidad"""
    return UniversalDataProcessor.clean_all_data(info)

def calcular_eficiencia_universal(info):
    """Función de compatibilidad"""
    return UniversalEfficiencyCalculator.calculate(info)

def detectar_caracteristicas_universal(info):
    """Función de compatibilidad"""
    return UniversalFeatureDetector.detect_all(info)

def obtener_icono_para_campo_universal(campo):
    """Función de compatibilidad"""
    return UniversalFeatureDetector.get_icon_for_field(campo)

def aplicar_mejoras_universales(info, caracteristicas=None):
    """Función de compatibilidad"""
    # Procesar con los nuevos módulos
    datos_limpios, nuevas_caracteristicas, eficiencia = procesar_producto_universal(info)
    
    # Si se pasaron características, combinarlas
    if caracteristicas:
        nuevas_caracteristicas.update(caracteristicas)
    
    return datos_limpios, nuevas_caracteristicas

# ============================================================================
# FUNCIONES ADICIONALES PARA COMPATIBILIDAD
# ============================================================================

def extraer_contenido_pdf(url, print_callback=None):
    """Extrae contenido de un PDF - alias para compatibilidad"""
    # El print_callback se ignora por ahora, solo está para compatibilidad
    texto = extraer_texto_pdf_online(url)
    
    # Siempre devolver un diccionario para consistencia
    if texto:
        return {
            'text': texto,
            'tables_markdown': ''  # Por ahora no extraemos tablas separadamente
        }
    return None

def validar_caracteristicas_producto(info, texto_pdf=''):
    """Valida características del producto - función de compatibilidad"""
    return UniversalFeatureDetector.detect_all(info)

def extraer_info_tecnica(texto_pdf, campos_buscar):
    """Extrae información técnica del PDF - alias para compatibilidad"""
    return extraer_info_de_pdf(texto_pdf, campos_buscar)

def procesar_datos_para_tabla(info):
    """Procesa datos para la tabla - función de compatibilidad"""
    return UniversalDataProcessor.clean_all_data(info)

def generar_hero_section_inline(titulo, subtitulo):
    """Genera hero section - función de compatibilidad"""
    return f'''
    <div style="background: linear-gradient(135deg, #ff6600 0%, #ff6600dd 100%); 
                color: white; padding: 40px 20px; text-align: center;">
        <h1 style="margin: 0 0 10px 0; font-size: 32px; font-weight: bold;">
            {titulo}
        </h1>
        <p style="margin: 0; font-size: 18px; opacity: 0.9;">{subtitulo}</p>
    </div>
    '''

def generar_info_cards_inline_mejorado(info, caracteristicas):
    """Genera cards de información - función de compatibilidad"""
    return generar_mini_cards_adicionales(caracteristicas)

def generar_benefits_section_inline(marketing_content):
    """Genera sección de beneficios - función de compatibilidad"""
    return ''  # Ya incluido en otras secciones

def generar_cta_section_inline(marketing_content, config):
    """Genera sección CTA - función de compatibilidad"""
    return generar_cta_whatsapp(marketing_content, config)

def generar_contact_footer_inline(config):
    """Genera footer de contacto - función de compatibilidad"""
    return f'''
    <footer style="background: #333; color: white; padding: 30px 20px; text-align: center;">
        <p>Teléfono: {config.get('telefono_display', '')}</p>
        <p>Email: {config.get('email', '')}</p>
        <p>WhatsApp: {config.get('whatsapp', '')}</p>
    </footer>
    '''

def generar_css_hover_effects():
    """Genera CSS para efectos hover - función de compatibilidad"""
    return ''  # Los estilos ya están inline

def extraer_datos_tecnicos_del_pdf(texto_pdf, info_actual):
    """Extrae datos técnicos del PDF usando regex - función de compatibilidad"""
    if not texto_pdf:
        return {}
    
    # Campos a buscar
    campos_buscar = ['motor', 'cilindrada', 'consumo', 'capacidad_tanque', 'autonomia', 'nivel_ruido']
    
    # Usar la función existente
    datos_extraidos = extraer_info_de_pdf(texto_pdf, campos_buscar)
    
    # Combinar con info actual
    resultado = info_actual.copy() if info_actual else {}
    resultado.update(datos_extraidos)
    
    return resultado

def generar_titulo_producto(info):
    """Genera título del producto - función de compatibilidad"""
    marca = info.get('marca', '')
    modelo = info.get('modelo', '')
    nombre = info.get('nombre', 'Producto')
    
    if marca and modelo:
        return f"{marca} {modelo}"
    return nombre

def generar_subtitulo_producto(info):
    """Genera subtítulo del producto - función de compatibilidad"""
    return info.get('descripcion_corta', 'Solución confiable para sus necesidades')

def generar_badges_caracteristicas(caracteristicas):
    """Genera badges de características - función de compatibilidad"""
    badges = caracteristicas.get('badges_especiales', [])
    html = ''
    
    for badge in badges[:3]:
        color = badge.get('color', '#ff6600')
        texto = badge.get('texto', '')
        html += f'<span style="background: {color}; color: white; padding: 5px 10px; border-radius: 15px; margin: 0 5px;">{texto}</span>'
    
    return html

def generar_content_sections_inline(info, marketing_content):
    """Genera secciones de contenido - función de compatibilidad"""
    return ''  # Ya incluido en otras funciones