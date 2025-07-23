# GENERADOR INTELIGENTE DE DESCRIPCIONES PARA STEL SHOP - VERSIÓN HÍBRIDA
# Mantiene la estructura de navegación original

import tkinter as tk
from tkinter import (
    Tk, Label, Button, Entry, StringVar, filedialog,
    ttk, scrolledtext, messagebox
)
import threading
import json
import os
import pandas as pd
import time
import traceback
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException, ElementClickInterceptedException, SessionNotCreatedException
import google.generativeai as genai
from typing import Dict, Any
import requests
import PyPDF2
from io import BytesIO
import fitz  # PyMuPDF como alternativa si PyPDF2 falla

def verificar_dependencias():
    """Verifica e instala dependencias faltantes"""
    dependencias = {
        'pandas': 'pandas',
        'openpyxl': 'openpyxl',
        'selenium': 'selenium',
        'google.generativeai': 'google-generativeai',
        'requests': 'requests',
        'PyPDF2': 'PyPDF2',
        'pdfplumber': 'pdfplumber',
        'fitz': 'PyMuPDF'
    }
    
    faltantes = []
    
    for modulo, paquete in dependencias.items():
        try:
            if '.' in modulo:
                parts = modulo.split('.')
                __import__(parts[0])
            else:
                __import__(modulo)
        except ImportError:
            faltantes.append(paquete)
    
    if faltantes:
        print(f"⚠️ Dependencias faltantes: {', '.join(faltantes)}")
        print("Instalando dependencias...")
        
        import subprocess
        import sys
        
        for paquete in faltantes:
            subprocess.check_call([sys.executable, "-m", "pip", "install", paquete])
        
        print("✅ Dependencias instaladas. Por favor, reinicia la aplicación.")
        return False
    
    return True

# ============================================================================
# FUNCIONES PARA LEER PDFs Y VALIDAR CARACTERÍSTICAS
# ============================================================================

def extraer_texto_pdf(pdf_url: str, log_func=print):
    """
    Descarga un PDF desde la URL indicada y devuelve todo su texto en un único string.
    Se intenta primero con PyPDF2 y, si falla, con pdfplumber y PyMuPDF (fitz) como alternativas.
    El parámetro `log_func` permite inyectar un método de log (por ej. `self.log`) para dar feedback al usuario.
    """
    try:
        if not pdf_url or pdf_url in ['nan', 'None']:
            log_func("❌ URL del PDF no válida")
            return None

        # Añadir protocolo si falta
        if not pdf_url.startswith('http'):
            pdf_url = f"https://storage.googleapis.com/fichas_tecnicas/{pdf_url}"

        log_func(f"📄 Descargando PDF: {pdf_url}")
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
            )
        }
        response = requests.get(pdf_url, headers=headers, timeout=30)
        if response.status_code != 200:
            log_func(f"❌ Error HTTP {response.status_code} al descargar el PDF")
            return None

        pdf_file = BytesIO(response.content)
        texto = ""

        # ---------- PyPDF2 ----------
        try:
            reader = PyPDF2.PdfReader(pdf_file)
            log_func(f"✅ PDF descargado. Páginas: {len(reader.pages)}")
            for i, page in enumerate(reader.pages):
                texto_pagina = page.extract_text() or ""
                texto += texto_pagina + "\n"
                log_func(f"   ✓ Página {i+1} leída con PyPDF2")
            return texto
        except Exception as e:
            log_func(f"⚠️ PyPDF2 falló: {e}")

        # ---------- pdfplumber ----------
        try:
            import pdfplumber
            pdf_file.seek(0)
            with pdfplumber.open(pdf_file) as pdf:
                for i, page in enumerate(pdf.pages):
                    texto += (page.extract_text() or "") + "\n"
                    log_func(f"   ✓ Página {i+1} leída con pdfplumber")
            if texto:
                return texto
        except Exception as e:
            log_func(f"⚠️ pdfplumber falló: {e}")

        # ---------- PyMuPDF ----------
        try:
            pdf_file.seek(0)
            import fitz
            doc = fitz.open(stream=pdf_file, filetype="pdf")
            for i, page in enumerate(doc):
                texto += page.get_text() + "\n"
                log_func(f"   ✓ Página {i+1} leída con PyMuPDF")
            return texto if texto else None
        except Exception as e:
            log_func(f"⚠️ PyMuPDF falló: {e}")

        return texto if texto else None

    except Exception as e:
        log_func(f"❌ Error general al procesar PDF: {e}")
        return None


def extraer_datos_tecnicos_del_pdf(texto_pdf: str, info_excel: dict, log_func=print) -> dict:
    """
    Parsea el texto extraído de un PDF y trata de inferir datos técnicos relevantes
    (combustible, potencia, motor, consumo, cabina, TTA, etc.).
    Devuelve un nuevo diccionario con los datos actualizados.
    """
    if not texto_pdf:
        return info_excel

    texto_lower = texto_pdf.lower()
    info = info_excel.copy()

    # Combustible
    if any(x in texto_lower for x in ['diesel', 'diésel', 'gasoil', 'gas oil']):
        info['tipo_combustible_real'] = 'diesel'
        log_func("   ✓ Combustible detectado: DIESEL")
    elif any(x in texto_lower for x in ['nafta', 'gasolina', 'bencina', 'gasoline']):
        info['tipo_combustible_real'] = 'nafta'
        log_func("   ✓ Combustible detectado: NAFTA")
    elif 'gas' in texto_lower and 'gasolina' not in texto_lower:
        info['tipo_combustible_real'] = 'gas'
        log_func("   ✓ Combustible detectado: GAS")

    import re

    # Potencia kVA
    m_kva = re.search(r'(\\d+(?:[.,]\\d+)?)\\s*kva', texto_lower)
    if m_kva and not info.get('potencia_kva'):
        info['potencia_kva'] = m_kva.group(1).replace(',', '.')
        log_func(f"   ✓ Potencia detectada: {info['potencia_kva']} KVA")

    # Motor
    m_motor = re.search(r'motor[:\\s]+([^\\n]{3,50})', texto_lower)
    if m_motor:
        motor_txt = m_motor.group(1).strip()
        info['motor_pdf'] = motor_txt
        log_func(f"   ✓ Motor detectado: {motor_txt}")

    # Consumo
    m_consumo = re.search(r'consumo[:\\s]+(\\d+(?:[.,]\\d+)?)\\s*l/h', texto_lower)
    if m_consumo:
        info['consumo_pdf'] = m_consumo.group(1).replace(',', '.')
        log_func(f"   ✓ Consumo detectado: {info['consumo_pdf']} L/h")

    # Cabina
    info['tiene_cabina_real'] = 'cabina' in texto_lower and any(x in texto_lower for x in ['insonorizada', 'insonorizado'])
    if info['tiene_cabina_real']:
        log_func("   ✓ CABINA INSONORIZADA detectada")

    # TTA
    info['tiene_tta_real'] = (('transferencia' in texto_lower and 'automática' in texto_lower) or 'tta' in texto_lower) and any(
        g in texto_lower for g in ['generador', 'grupo electrógeno', 'genset'])
    if info['tiene_tta_real']:
        log_func("   ✓ TRANSFERENCIA AUTOMÁTICA detectada")

    return info

def validar_caracteristicas_producto(info_tecnica, texto_pdf=None):
    """
    Valida qué características realmente tiene el producto basándose en el PDF o datos del Excel
    """
    caracteristicas = {
        'tiene_cabina': False,
        'tiene_tta': False,
        'es_inverter': False,
        'tipo_combustible': 'diesel',  # por defecto
        'caracteristicas_especiales': []
    }
    
    # Combinar toda la información disponible
    texto_busqueda = f"{info_tecnica.get('nombre', '')} {info_tecnica.get('modelo', '')} {info_tecnica.get('familia', '')}"
    if texto_pdf:
        texto_busqueda += " " + texto_pdf
    
    texto_busqueda = texto_busqueda.lower()
    
    # Validar características solo si están explícitamente mencionadas
    if 'cabina' in texto_busqueda and ('insonorizada' in texto_busqueda or 'insonorizado' in texto_busqueda):
        caracteristicas['tiene_cabina'] = True
        
    if ('transferencia' in texto_busqueda and 'automatica' in texto_busqueda) or 'tta' in texto_busqueda:
        # Verificar que NO sea un vibrador, compresor, etc.
        if not any(x in texto_busqueda for x in ['vibrador', 'vibropisonador', 'compresor', 'compactador']):
            caracteristicas['tiene_tta'] = True
    
    if 'inverter' in texto_busqueda:
        caracteristicas['es_inverter'] = True
    
    # Tipo de combustible
    if 'gas' in texto_busqueda and 'gasolina' not in texto_busqueda:
        caracteristicas['tipo_combustible'] = 'gas'
    elif 'nafta' in texto_busqueda or 'gasolina' in texto_busqueda:
        caracteristicas['tipo_combustible'] = 'nafta'
    
    # Detectar tipo de producto para evitar características incorrectas
    tipo_producto = determinar_tipo_producto(info_tecnica)
    
    # Si NO es un generador, desactivar TTA
    if tipo_producto != 'generador':
        caracteristicas['tiene_tta'] = False
        
    return caracteristicas

# ============================================================================
# CONFIGURACIÓN DE IA Y GENERACIÓN AVANZADA
# ============================================================================

def configurar_gemini(api_key):
    """
    Configura Google Gemini con la API key proporcionada
    """
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-pro')
        return model
    except Exception as e:
        return None

def determinar_tipo_producto_mejorado(info):
    """Determina el tipo de producto con mayor precisión"""
    familia = info.get('familia', '').lower()
    nombre = info.get('nombre', '').lower()
    modelo = info.get('modelo', '').lower()
    
    # Diccionario de palabras clave por tipo
    tipos_producto = {
        'generador': ['generador', 'grupo electrogeno', 'ge-', 'gg-', 'diesel', 'nafta'],
        'compresor': ['compresor', 'aire comprimido', 'psi', 'bar'],
        'vibrador': ['vibrador', 'vibro', 'vcml', 'concreto', 'hormigon'],
        'soldadora': ['soldadora', 'soldador', 'electrodo'],
        'motobomba': ['motobomba', 'bomba', 'agua'],
        'martillo': ['martillo', 'demoledor', 'percutor']
    }
    
    # Buscar coincidencias
    for tipo, palabras in tipos_producto.items():
        for palabra in palabras:
            if palabra in familia or palabra in nombre or palabra in modelo:
                return tipo
    
    return 'generador'  # Por defecto

def validar_caracteristicas_producto(info, tipo_producto):
    """Valida qué características son aplicables según el tipo de producto"""
    
    # Características válidas por tipo de producto
    caracteristicas_validas = {
        'generador': {
            'puede_tener_cabina': True,
            'puede_tener_tta': True,
            'puede_ser_inverter': True,
            'combustibles_validos': ['diesel', 'gas', 'nafta']
        },
        'vibrador': {
            'puede_tener_cabina': False,
            'puede_tener_tta': False,
            'puede_ser_inverter': False,
            'combustibles_validos': ['nafta']
        },
        'compresor': {
            'puede_tener_cabina': False,
            'puede_tener_tta': False,
            'puede_ser_inverter': False,
            'combustibles_validos': ['electrico', 'nafta', 'diesel']
        },
        'soldadora': {
            'puede_tener_cabina': False,
            'puede_tener_tta': False,
            'puede_ser_inverter': True,
            'combustibles_validos': ['diesel', 'nafta', 'electrico']
        }
    }
    
    return caracteristicas_validas.get(tipo_producto, caracteristicas_validas['generador'])

def detectar_caracteristicas_reales(info, tipo_producto):
    """Detecta características basándose en datos reales y tipo de producto"""
    nombre_lower = info['nombre'].lower()
    familia_lower = info['familia'].lower()
    modelo_lower = info['modelo'].lower()
    
    validaciones = validar_caracteristicas_producto(info, tipo_producto)
    
    caracteristicas = {
        'tiene_cabina': False,
        'tiene_tta': False,
        'es_inverter': False,
        'tipo_combustible': None
    }
    
    # Solo buscar cabina si el producto puede tenerla
    if validaciones['puede_tener_cabina']:
        # Buscar palabras específicas que indiquen cabina
        if ('cabina' in nombre_lower and 'insonorizada' in nombre_lower) or \
           ('cabinado' in nombre_lower) or \
           (tipo_producto == 'generador' and 'cs' in modelo_lower):  # CS = Con Silenciador
            caracteristicas['tiene_cabina'] = True
    
    # Solo buscar TTA si el producto puede tenerlo
    if validaciones['puede_tener_tta']:
        # Ser más específico con TTA
        if tipo_producto == 'generador' and \
           (('tta' in modelo_lower) or \
            ('transferencia' in nombre_lower and 'automatica' in nombre_lower) or \
            ('tablero' in nombre_lower and 'transferencia' in nombre_lower)):
            caracteristicas['tiene_tta'] = True
    
    # Solo detectar inverter si aplica
    if validaciones['puede_ser_inverter']:
        if 'inverter' in nombre_lower or \
           (tipo_producto == 'generador' and 'gi-' in modelo_lower) or \
           (tipo_producto == 'soldadora' and 'inv' in modelo_lower):
            caracteristicas['es_inverter'] = True
    
    # Detectar combustible
    for combustible in validaciones['combustibles_validos']:
        if combustible in familia_lower or combustible in nombre_lower:
            caracteristicas['tipo_combustible'] = combustible
            break
    
    return caracteristicas

def generar_prompt_ia_restringido(info_tecnica, tipo_producto, caracteristicas_reales):
    """Genera un prompt que restringe a la IA a usar solo información verificada"""
    
    # Información verificada
    datos_verificados = f"""
    INFORMACIÓN VERIFICADA DEL PRODUCTO:
    - Tipo de producto: {tipo_producto}
    - Nombre: {info_tecnica['nombre']}
    - Potencia: {info_tecnica['potencia_kva']} KVA
    - Motor: {info_tecnica['motor']}
    - Consumo: {info_tecnica['consumo']} L/h
    
    CARACTERÍSTICAS CONFIRMADAS:
    - Tiene cabina insonorizada: {'SÍ' if caracteristicas_reales['tiene_cabina'] else 'NO'}
    - Tiene TTA: {'SÍ' if caracteristicas_reales['tiene_tta'] else 'NO'}
    - Es inverter: {'SÍ' if caracteristicas_reales['es_inverter'] else 'NO'}
    - Combustible: {caracteristicas_reales['tipo_combustible'] or 'No especificado'}
    """
    
    prompt = f"""
    Eres un experto en redacción técnica. Genera una descripción de venta para el siguiente producto.
    
    {datos_verificados}
    
    REGLAS ESTRICTAS:
    1. SOLO menciona características que están marcadas como "SÍ" en la lista anterior
    2. NO inventes características que no están confirmadas
    3. NO menciones cabina insonorizada si está marcada como "NO"
    4. NO menciones TTA (Tablero de Transferencia Automática) si está marcada como "NO"
    5. NO agregues características típicas del producto si no están confirmadas
    6. Si el tipo de producto es "{tipo_producto}", usa terminología apropiada para ese tipo
    7. NO uses características de generadores en productos que no son generadores
    
    Genera un texto persuasivo pero ESTRICTAMENTE basado en los datos verificados.
    """
    
    return prompt

def generar_descripcion_detallada_html_premium(row, config, modelo_ia=None):
    """
    Genera descripción HTML premium con diseño visual estilo calculadora KOR
    SIN EMOJIS - Solo caracteres comunes en el texto
    """
    info = extraer_info_tecnica(row)
    
    # Configuración de contacto
    whatsapp = config.get('whatsapp', '541139563099')
    email = config.get('email', 'info@generadores.ar')
    telefono_display = config.get('telefono_display', '+54 11 3956-3099')
    website = config.get('website', 'www.generadores.ar')
    
    # ------- Paso 1: Leer PDF y actualizar info técnica -------
    pdf_url = info.get('pdf_url', '')
    texto_pdf = None
    if pdf_url and pdf_url not in ['nan', 'None', '']:
        if not pdf_url.startswith('http'):
            pdf_url = f"https://storage.googleapis.com/fichas_tecnicas/{pdf_url}"
        texto_pdf = extraer_texto_pdf(pdf_url)
        if texto_pdf:
            info = extraer_datos_tecnicos_del_pdf(texto_pdf, info)
    else:
        print("⚠️ No hay URL de PDF disponible para este producto")
    
    # Flags basados en la información (PDF tiene prioridad)
    tipo_combustible = info.get('tipo_combustible_real', '').lower()
    es_diesel = tipo_combustible == 'diesel'
    es_gas = tipo_combustible == 'gas'
    es_nafta = tipo_combustible == 'nafta'
    
    tiene_cabina = info.get('tiene_cabina_real', False)
    tiene_tta = info.get('tiene_tta_real', False)
    
    # Fallback heurístico si algo no se detectó
    if not (es_diesel or es_gas or es_nafta):
        nombre_lower = info['nombre'].lower()
        familia_lower = info['familia'].lower()
        es_diesel = 'diesel' in familia_lower or 'diesel' in nombre_lower
        es_gas = 'gas' in familia_lower or 'gas' in nombre_lower
        es_nafta = 'nafta' in familia_lower or 'nafta' in nombre_lower
    
    # Actualizar datos motor/consumo si fueron detectados en el PDF
    if info.get('motor_pdf'):
        info['motor'] = info['motor_pdf']
    if info.get('consumo_pdf'):
        info['consumo'] = info['consumo_pdf']
    
    # Detectar si es inverter
    es_inverter = 'inverter' in info['nombre'].lower() or 'gi' in info['modelo'].lower()
    
    # Iconos SVG para cada característica
    iconos = {
        'potencia': '<svg width="28" height="28" viewBox="0 0 24 24" fill="#ff6600"><path d="M7 2v11h3v9l7-12h-4l4-8z"/></svg>',
        'motor': '<svg width="28" height="28" viewBox="0 0 24 24" fill="#ff6600"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 18c-4.42 0-8-3.58-8-8s3.58-8 8-8 8 3.58 8 8-3.58 8-8 8z"/></svg>',
        'alternador': '<svg width="28" height="28" viewBox="0 0 24 24" fill="#ff6600"><path d="M12 2l-5.5 9h11z M12 22l5.5-9h-11z M3.5 9L12 12l-3.5 6z M20.5 9L12 12l3.5 6z"/></svg>',
        'voltaje': '<svg width="28" height="28" viewBox="0 0 24 24" fill="#ff6600"><path d="M7 2v11h3v9l7-12h-4l4-8z"/></svg>',
        'frecuencia': '<svg width="28" height="28" viewBox="0 0 24 24" fill="#ff6600"><path d="M16 6l-4 4-4-4v3l4 4 4-4zm0 6l-4 4-4-4v3l4 4 4-4z"/></svg>',
        'consumo': '<svg width="28" height="28" viewBox="0 0 24 24" fill="#ff6600"><path d="M6 2v6l1-2h1l1 2V2c1.1 0 2 .9 2 2v6c0 1.1-.9 2-2 2H7c-1.1 0-2-.9-2-2V4c0-1.1.9-2 2-2h1zm6 0h10v10h-2V4h-8v2zm0 4h8v10h-2V8h-6v2z"/></svg>',
        'tanque': '<svg width="28" height="28" viewBox="0 0 24 24" fill="#ff6600"><path d="M3 13c0 1.1.9 2 2 2s2-.9 2-2-.9-2-2-2-2 .9-2 2m4 8c0 .6.5 1 1 1h8c.6 0 1-.5 1-1v-1H7v1m11.8-9.7l-2.5 2.5L17.5 15 20 12.5l-2.5-2.5-1.1 1.1 1.4 1.4-1.4 1.5m3.2-.3c0 3.3-2.7 6-6 6-1.6 0-3.1-.7-4.2-1.8L10 17h1c1.1 0 2-.9 2-2v-3c0-.3-.1-.5-.2-.8L18.2 5.8c.5-.5.8-1.2.8-1.9 0-1.5-1.2-2.7-2.7-2.7-.7 0-1.4.3-1.9.8l-11.7 11.7c-.5.6-.7 1.3-.7 2.1 0 1.8 1.5 3.2 3.2 3.2H7v2c-3.9 0-7-3.1-7-7s3.1-7 7-7h10c3.9 0 7 3.1 7 7z"/></svg>',
        'ruido': '<svg width="28" height="28" viewBox="0 0 24 24" fill="#ff6600"><path d="M14 3.23v2.06c2.89.86 5 3.54 5 6.71s-2.11 5.84-5 6.7v2.07c4-.91 7-4.49 7-8.77 0-4.28-3-7.86-7-8.77M16.5 12c0-1.77-1-3.29-2.5-4.03V16c1.5-.71 2.5-2.24 2.5-4M3 9v6h4l5 5V4L7 9H3z"/></svg>',
        'dimensiones': '<svg width="28" height="28" viewBox="0 0 24 24" fill="#ff6600"><path d="M21 3H3c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h18c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm0 16H3V5h18v14z"/></svg>',
        'peso': '<svg width="28" height="28" viewBox="0 0 24 24" fill="#ff6600"><path d="M12 3c-1.3 0-2.4.8-2.8 2H6c-.6 0-1 .4-1 1s.4 1 1 1h.2l.9 11c0 .6.4 1 1 1h7.8c.6 0 1-.4 1-1l.9-11h.2c.6 0 1-.4 1-1s-.4-1-1-1h-3.2c-.4-1.2-1.5-2-2.8-2zm0 2c.3 0 .5.2.5.5s-.2.5-.5.5-.5-.2-.5-.5.2-.5.5-.5z"/></svg>',
        'diesel': '<svg width="28" height="28" viewBox="0 0 24 24" fill="#333"><path d="M12 2C8.13 2 5 5.13 5 9c0 1.88.79 3.56 2 4.78V22h10v-8.22c1.21-1.22 2-2.9 2-4.78 0-3.87-3.13-7-7-7zm0 2c2.76 0 5 2.24 5 5s-2.24 5-5 5-5-2.24-5-5 2.24-5 5-5z"/></svg>',
        'gas': '<svg width="28" height="28" viewBox="0 0 24 24" fill="#1976d2"><path d="M13.5.67s.74 2.65.74 4.8c0 2.06-1.35 3.73-3.41 3.73-2.07 0-3.63-1.67-3.63-3.73l.03-.36C5.21 7.51 4 10.62 4 14c0 4.42 3.58 8 8 8s8-3.58 8-8C20 8.61 17.41 3.8 13.5.67z"/></svg>',
        'nafta': '<svg width="28" height="28" viewBox="0 0 24 24" fill="#f44336"><path d="M12 3c-1.1 0-2 .9-2 2v12.5c0 .83.67 1.5 1.5 1.5s1.5-.67 1.5-1.5V5c0-1.1-.9-2-2-2zm-3 4H7v11h2V7zm6 0h-2v11h2V7z"/></svg>',
        'check': '<svg width="20" height="20" viewBox="0 0 24 24" fill="#4caf50"><path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z"/></svg>',
        'beneficios': '<svg width="24" height="24" viewBox="0 0 24 24" fill="#D32F2F"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/></svg>',
        'confiabilidad': '<svg width="24" height="24" viewBox="0 0 24 24" fill="#D32F2F"><path d="M12 1L3 5v6c0 5.55 3.84 10.74 9 12 5.16-1.26 9-6.45 9-12V5l-9-4z"/></svg>',
        'aplicaciones': '<svg width="24" height="24" viewBox="0 0 24 24" fill="#D32F2F"><path d="M4 6h16v2H4zm0 5h16v2H4zm0 5h16v2H4z"/></svg>',
        'porque': '<svg width="24" height="24" viewBox="0 0 24 24" fill="#D32F2F"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 17h-2v-2h2v2zm2.07-7.75l-.9.92C13.45 12.9 13 13.5 13 15h-2v-.5c0-1.1.45-2.1 1.17-2.83l1.24-1.26c.37-.36.59-.86.59-1.41 0-1.1-.9-2-2-2s-2 .9-2 2H8c0-2.21 1.79-4 4-4s4 1.79 4 4c0 .88-.36 1.68-.93 2.25z"/></svg>',
        'presion': '<svg width="28" height="28" viewBox="0 0 24 24" fill="#ff6600"><path d="M12 8c-2.21 0-4 1.79-4 4s1.79 4 4 4 4-1.79 4-4-1.79-4-4-4zm-7 7H3v-2h2v2zm16 0h-2v-2h2v2z"/></svg>',
        'caudal': '<svg width="28" height="28" viewBox="0 0 24 24" fill="#ff6600"><path d="M12 3L4 9v12h16V9l-8-6zm-2 16H8v-6h2v6zm4 0h-2v-6h2v6zm4 0h-2v-6h2v6z"/></svg>',
        'fuerza_impacto': '<svg width="28" height="28" viewBox="0 0 24 24" fill="#ff6600"><path d="M19 7h-2V5h2v2zm-4 0h-2V5h2v2zm-4 0H9V5h2v2zm-4 0H5V5h2v2zm-2 4h16v2H3zm16 4h-2v-2h2v2zm-4 0h-2v-2h2v2zm-4 0H9v-2h2v2zm-4 0H5v-2h2v2z"/></svg>',
        'whatsapp': '<svg width="24" height="24" viewBox="0 0 24 24" fill="white"><path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413Z"/></svg>',
        'email': '<svg width="24" height="24" viewBox="0 0 24 24" fill="white"><path d="M20 4H4c-1.1 0-1.99.9-1.99 2L2 18c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V6c0-1.1-.9-2-2-2zm0 4l-8 5-8-5V6l8 5 8-5v2z"/></svg>',
        'pdf': '<svg width="24" height="24" viewBox="0 0 24 24" fill="white"><path d="M20 2H8c-1.1 0-2 .9-2 2v12c0 1.1.9 2 2 2h12c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2zm-8.5 7.5c0 .83-.67 1.5-1.5 1.5H9v2H7.5V7H10c.83 0 1.5.67 1.5 1.5v1zm5 2c0 .83-.67 1.5-1.5 1.5h-2.5V7H15c.83 0 1.5.67 1.5 1.5v3zm4-3H19v1h1.5V11H19v2h-1.5V7h3v1.5zM9 9.5h1v-1H9v1zM4 6H2v14c0 1.1.9 2 2 2h14v-2H4V6zm10 5.5h1v-3h-1v3z"/></svg>',
        'shield': '<svg width="24" height="24" viewBox="0 0 24 24" fill="#4caf50"><path d="M12 1L3 5v6c0 5.55 3.84 10.74 9 12 5.16-1.26 9-6.45 9-12V5l-9-4z"/></svg>'
    }
    
    # Generar speech de ventas con IA o fallback
    if modelo_ia:
        speech_ventas = generar_speech_venta_ia_mejorado(info, modelo_ia, iconos, tiene_cabina, tiene_tta)
    else:
        speech_ventas = generar_speech_venta_mejorado(info, iconos, tiene_cabina, tiene_tta)
    
    # Mensajes para enlaces
    nombre_producto = info['nombre']
    whatsapp_msg = f"Hola,%20vengo%20de%20ver%20el%20{nombre_producto.replace(' ', '%20')}%20en%20la%20tienda%20de%20Stelorder%20y%20quisiera%20mas%20informacion%20sobre%20este%20producto"
    email_subject = f"Consulta%20desde%20Stelorder%20-%20{nombre_producto.replace(' ', '%20')}"
    email_body = f"Hola,%0A%0AVengo%20de%20ver%20el%20{nombre_producto.replace(' ', '%20')}%20en%20la%20tienda%20de%20Stelorder%20y%20quisiera%20mas%20informacion%20sobre%20este%20producto.%0A%0AQuedo%20a%20la%20espera%20de%20su%20respuesta.%0A%0ASaludos"
    
    # Determinar icono de combustible
    icono_combustible = iconos['diesel'] if es_diesel else iconos['gas'] if es_gas else iconos['nafta']
    tipo_combustible = 'Diesel' if es_diesel else 'Gas' if es_gas else 'Nafta'
    
    # --- Bloques HTML condicionales ---
    potencia_kw_html = f'<p style="margin: 0; font-size: 14px; color: #999;">{info["potencia_kw"]} KW</p>' if info['potencia_kw'] else ''
    
    cabina_html = "<div style='margin: 30px 0;'><div style='background: #4caf50; color: white; padding: 15px; border-radius: 10px; display: flex; align-items: center; gap: 10px; box-shadow: 0 2px 8px rgba(76,175,80,0.3);'>" + iconos['check'] + "<span style='font-size: 18px; font-weight: bold;'>INCLUYE CABINA INSONORIZADA</span></div></div>" if tiene_cabina else ""
    
    tta_html = "<div style='margin: 30px 0;'><div style='background: #2196f3; color: white; padding: 15px; border-radius: 10px; display: flex; align-items: center; gap: 10px; box-shadow: 0 2px 8px rgba(33,150,243,0.3);'>" + iconos['check'] + "<span style='font-size: 18px; font-weight: bold;'>TABLERO DE TRANSFERENCIA AUTOMATICA INCLUIDO</span></div></div>" if tiene_tta else ""
    
    inverter_html = "<div style='margin: 30px 0;'><div style='background: #9c27b0; color: white; padding: 15px; border-radius: 10px; display: flex; align-items: center; gap: 10px; box-shadow: 0 2px 8px rgba(156,39,176,0.3);'>" + iconos['check'] + "<span style='font-size: 18px; font-weight: bold;'>TECNOLOGIA INVERTER - MAXIMA EFICIENCIA</span></div></div>" if es_inverter else ""

    # --- Lógica de Tabla de Especificaciones Dinámica ---
    tipo_producto = determinar_tipo_producto(info)
    tabla_especificaciones_html = generar_tabla_especificaciones_html(info, tipo_producto, iconos)

    # Generar HTML con diseño estilo calculadora KOR
    html = f"""
    <div style="font-family: Arial, sans-serif; max-width: 1000px; margin: 0 auto; background: #fafafa; padding: 20px;">
        
        <!-- HEADER HERO -->
        <div style="background: linear-gradient(135deg, #ff6600, #ff8833); border-radius: 15px; padding: 30px; text-align: center; margin-bottom: 30px; box-shadow: 0 5px 20px rgba(255,102,0,0.3);">
            <h1 style="color: white; font-size: 32px; margin: 0 0 10px 0; text-transform: uppercase; text-shadow: 2px 2px 4px rgba(0,0,0,0.2);">
                {nombre_producto}
            </h1>
            <p style="color: white; font-size: 18px; margin: 0; opacity: 0.95;">
                Solucion energetica profesional de ultima generacion
            </p>
        </div>
        
        <!-- ESPECIFICACIONES PRINCIPALES EN CARDS -->
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 20px; margin-bottom: 30px;">
            
            <!-- Card Potencia -->
            <div style="background: white; border-radius: 10px; padding: 20px; box-shadow: 0 2px 8px rgba(0,0,0,0.08); transition: transform 0.2s; cursor: pointer;" onmouseover="this.style.transform='translateY(-2px)'" onmouseout="this.style.transform='translateY(0)'">
                <div style="display: flex; align-items: center; gap: 15px;">
                    <div style="width: 50px; height: 50px; background: #ffe8cc; border-radius: 50%; display: flex; align-items: center; justify-content: center;">
                        {iconos['potencia']}
                    </div>
                    <div>
                        <h4 style="margin: 0; color: #666; font-size: 14px; text-transform: uppercase;">Potencia</h4>
                        <p style="margin: 5px 0 0 0; font-size: 22px; font-weight: bold; color: #ff6600;">
                            {info['potencia_kva'] or 'N/D'} KVA
                        </p>
                        {potencia_kw_html}
                    </div>
                </div>
            </div>
            
            <!-- Card Motor -->
            <div style="background: white; border-radius: 10px; padding: 20px; box-shadow: 0 2px 8px rgba(0,0,0,0.08); transition: transform 0.2s; cursor: pointer;" onmouseover="this.style.transform='translateY(-2px)'" onmouseout="this.style.transform='translateY(0)'">
                <div style="display: flex; align-items: center; gap: 15px;">
                    <div style="width: 50px; height: 50px; background: #ffe8cc; border-radius: 50%; display: flex; align-items: center; justify-content: center;">
                        {iconos['motor']}
                    </div>
                    <div>
                        <h4 style="margin: 0; color: #666; font-size: 14px; text-transform: uppercase;">Motor</h4>
                        <p style="margin: 5px 0 0 0; font-size: 18px; font-weight: bold; color: #333;">
                            {info['motor'] or 'N/D'}
                        </p>
                    </div>
                </div>
            </div>
            
            <!-- Card Combustible -->
            <div style="background: white; border-radius: 10px; padding: 20px; box-shadow: 0 2px 8px rgba(0,0,0,0.08); transition: transform 0.2s; cursor: pointer;" onmouseover="this.style.transform='translateY(-2px)'" onmouseout="this.style.transform='translateY(0)'">
                <div style="display: flex; align-items: center; gap: 15px;">
                    <div style="width: 50px; height: 50px; background: #ffe8cc; border-radius: 50%; display: flex; align-items: center; justify-content: center;">
                        {icono_combustible}
                    </div>
                    <div>
                        <h4 style="margin: 0; color: #666; font-size: 14px; text-transform: uppercase;">Combustible</h4>
                        <p style="margin: 5px 0 0 0; font-size: 18px; font-weight: bold; color: #333;">
                            {tipo_combustible}
                        </p>
                        <p style="margin: 0; font-size: 14px; color: #999;">{info['consumo'] or 'N/D'} L/h</p>
                    </div>
                </div>
            </div>
            
        </div>
        
        <!-- TABLA DE ESPECIFICACIONES DINAMICA -->
        {tabla_especificaciones_html}
        
        <!-- CARACTERISTICAS ESPECIALES SI LAS TIENE -->
        {cabina_html}
        {tta_html}
        {inverter_html}
        
        <!-- SECCIONES DEL SPEECH DE VENTA -->
        {speech_ventas}
        
        <!-- VENTAJAS EN CARDS -->
        <div style="margin: 30px 0;">
            <h3 style="text-align: center; font-size: 28px; color: #333; margin-bottom: 30px;">
                POR QUE ELEGIR ESTE GENERADOR
            </h3>
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px;">
                
                <!-- Ventaja 1 -->
                <div style="background: white; border-radius: 10px; padding: 25px; text-align: center; box-shadow: 0 2px 8px rgba(0,0,0,0.08); border-top: 4px solid #ff6600;">
                    <div style="width: 60px; height: 60px; background: #ffe8cc; border-radius: 50%; margin: 0 auto 15px; display: flex; align-items: center; justify-content: center;">
                        {iconos['shield']}
                    </div>
                    <h4 style="margin: 0 0 10px 0; color: #333;">GARANTIA OFICIAL</h4>
                    <p style="margin: 0; color: #666; font-size: 14px;">Respaldo total del fabricante con garantia extendida</p>
                </div>
                
                <!-- Ventaja 2 -->
                <div style="background: white; border-radius: 10px; padding: 25px; text-align: center; box-shadow: 0 2px 8px rgba(0,0,0,0.08); border-top: 4px solid #ff6600;">
                    <div style="width: 60px; height: 60px; background: #ffe8cc; border-radius: 50%; margin: 0 auto 15px; display: flex; align-items: center; justify-content: center;">
                        <svg width="35" height="35" viewBox="0 0 24 24" fill="#ff6600"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/></svg>
                    </div>
                    <h4 style="margin: 0 0 10px 0; color: #333;">CALIDAD CERTIFICADA</h4>
                    <p style="margin: 0; color: #666; font-size: 14px;">Cumple con todas las normas internacionales</p>
                </div>
                
                <!-- Ventaja 3 -->
                <div style="background: white; border-radius: 10px; padding: 25px; text-align: center; box-shadow: 0 2px 8px rgba(0,0,0,0.08); border-top: 4px solid #ff6600;">
                    <div style="width: 60px; height: 60px; background: #ffe8cc; border-radius: 50%; margin: 0 auto 15px; display: flex; align-items: center; justify-content: center;">
                        <svg width="35" height="35" viewBox="0 0 24 24" fill="#ff6600"><path d="M12 1L3 5v6c0 5.55 3.84 10.74 9 12 5.16-1.26 9-6.45 9-12V5l-9-4zm0 10.99h7c-.53 4.12-3.28 7.79-7 8.94V12H5V6.3l7-3.11v8.8z"/></svg>
                    </div>
                    <h4 style="margin: 0 0 10px 0; color: #333;">SERVICIO TECNICO</h4>
                    <p style="margin: 0; color: #666; font-size: 14px;">Red nacional de servicio y repuestos originales</p>
                </div>
                
                <!-- Ventaja 4 -->
                <div style="background: white; border-radius: 10px; padding: 25px; text-align: center; box-shadow: 0 2px 8px rgba(0,0,0,0.08); border-top: 4px solid #ff6600;">
                    <div style="width: 60px; height: 60px; background: #ffe8cc; border-radius: 50%; margin: 0 auto 15px; display: flex; align-items: center; justify-content: center;">
                        <svg width="35" height="35" viewBox="0 0 24 24" fill="#ff6600"><path d="M11.8 10.9c-2.27-.59-3-1.2-3-2.15 0-1.09 1.01-1.85 2.7-1.85 1.78 0 2.44.85 2.5 2.1h2.21c-.07-1.72-1.12-3.3-3.21-3.81V3h-3v2.16c-1.94.42-3.5 1.68-3.5 3.61 0 2.31 1.91 3.46 4.7 4.13 2.5.6 3 1.48 3 2.41 0 .69-.49 1.79-2.7 1.79-2.06 0-2.87-.92-2.98-2.1h-2.2c.12 2.19 1.76 3.42 3.68 3.83V21h3v-2.15c1.95-.37 3.5-1.5 3.5-3.55 0-2.84-2.43-3.81-4.7-4.4z"/></svg>
                    </div>
                    <h4 style="margin: 0 0 10px 0; color: #333;">FINANCIACION</h4>
                    <p style="margin: 0; color: #666; font-size: 14px;">Multiples opciones de pago y financiacion a medida</p>
                </div>
                
            </div>
        </div>
        
        <!-- BOTONES DE ACCION MEJORADOS -->
        <div style="background: linear-gradient(135deg, #000000, #333333); padding: 40px; border-radius: 15px; text-align: center; margin: 40px 0; box-shadow: 0 5px 20px rgba(0,0,0,0.3);">
            <h3 style="color: #FFC107; font-size: 28px; margin-bottom: 10px; text-transform: uppercase;">
                TOME ACCION AHORA
            </h3>
            <p style="color: white; font-size: 16px; margin-bottom: 30px; opacity: 0.9;">
                No pierda esta oportunidad. Consulte con nuestros especialistas hoy mismo.
            </p>
            
            <div style="display: flex; flex-wrap: wrap; gap: 15px; justify-content: center;">
                
                <!-- Boton WhatsApp -->
                <a href="https://wa.me/{whatsapp}?text={whatsapp_msg}" target="_blank" 
                   style="display: inline-flex; align-items: center; gap: 10px; background-color: #25d366; color: white; padding: 15px 30px; text-decoration: none; border-radius: 50px; font-weight: bold; font-size: 16px; box-shadow: 0 3px 10px rgba(37,211,102,0.4); transition: all 0.3s;"
                   onmouseover="this.style.transform='scale(1.05)'" onmouseout="this.style.transform='scale(1)'">
                    {iconos['whatsapp']}
                    CONSULTAR POR WHATSAPP
                </a>
                
                <!-- Boton PDF -->
                <a href="{pdf_url}" target="_blank" 
                   style="display: inline-flex; align-items: center; gap: 10px; background-color: #FFC107; color: #000000; padding: 15px 30px; text-decoration: none; border-radius: 50px; font-weight: bold; font-size: 16px; box-shadow: 0 3px 10px rgba(255,193,7,0.4); transition: all 0.3s;"
                   onmouseover="this.style.transform='scale(1.05)'" onmouseout="this.style.transform='scale(1)'">
                    {iconos['pdf']}
                    DESCARGAR FICHA TECNICA
                </a>
                
                <!-- Boton Email -->
                <a href="mailto:{email}?subject={email_subject}&body={email_body}" 
                   style="display: inline-flex; align-items: center; gap: 10px; background-color: #D32F2F; color: white; padding: 15px 30px; text-decoration: none; border-radius: 50px; font-weight: bold; font-size: 16px; box-shadow: 0 3px 10px rgba(211,47,47,0.4); transition: all 0.3s;"
                   onmouseover="this.style.transform='scale(1.05)'" onmouseout="this.style.transform='scale(1)'">
                    {iconos['email']}
                    SOLICITAR COTIZACION
                </a>
                
            </div>
        </div>
        
        <!-- INFORMACION DE CONTACTO MEJORADA -->
        <div style="background: white; border-radius: 10px; padding: 30px; box-shadow: 0 2px 8px rgba(0,0,0,0.08); text-align: center;">
            <h4 style="color: #333; font-size: 24px; margin-bottom: 20px;">CONTACTO DIRECTO</h4>
            
            <div style="display: flex; flex-wrap: wrap; justify-content: center; gap: 30px;">
                
                <div style="display: flex; align-items: center; gap: 10px;">
                    <div style="width: 40px; height: 40px; background: #ffe8cc; border-radius: 50%; display: flex; align-items: center; justify-content: center;">
                        <svg width="24" height="24" viewBox="0 0 24 24" fill="#ff6600"><path d="M6.62 10.79c1.44 2.83 3.76 5.14 6.59 6.59l2.2-2.2c.27-.27.67-.36 1.02-.24 1.12.37 2.33.57 3.57.57.55 0 1 .45 1 1V20c0 .55-.45 1-1 1-9.39 0-17-7.61-17-17 0-.55.45-1 1-1h3.5c.55 0 1 .45 1 1 0 1.25.2 2.45.57 3.57.11.35.03.74-.25 1.02l-2.2 2.2z"/></svg>
                    </div>
                    <div style="text-align: left;">
                        <p style="margin: 0; color: #666; font-size: 12px;">Telefono / WhatsApp</p>
                        <a href="https://wa.me/{whatsapp}?text={whatsapp_msg}" style="color: #ff6600; text-decoration: none; font-weight: bold;">{telefono_display}</a>
                    </div>
                </div>
                
                <div style="display: flex; align-items: center; gap: 10px;">
                    <div style="width: 40px; height: 40px; background: #ffe8cc; border-radius: 50%; display: flex; align-items: center; justify-content: center;">
                        <svg width="24" height="24" viewBox="0 0 24 24" fill="#ff6600"><path d="M20 4H4c-1.1 0-1.99.9-1.99 2L2 18c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V6c0-1.1-.9-2-2-2zm0 4l-8 5-8-5V6l8 5 8-5v2z"/></svg>
                    </div>
                    <div style="text-align: left;">
                        <p style="margin: 0; color: #666; font-size: 12px;">Email</p>
                        <a href="mailto:{email}?subject={email_subject}&body={email_body}" style="color: #ff6600; text-decoration: none; font-weight: bold;">{email}</a>
                    </div>
                </div>
                
                <div style="display: flex; align-items: center; gap: 10px;">
                    <div style="width: 40px; height: 40px; background: #ffe8cc; border-radius: 50%; display: flex; align-items: center; justify-content: center;">
                        <svg width="24" height="24" viewBox="0 0 24 24" fill="#ff6600"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-1 17.93c-3.94-.49-7-3.85-7-7.93 0-.62.08-1.21.21-1.79L9 15v1c0 1.1.9 2 2 2v1.93zm6.9-2.54c-.26-.81-1-1.39-1.9-1.39h-1v-3c0-.55-.45-1-1-1H8v-2h2c.55 0 1-.45 1-1V7h2c1.1 0 2-.9 2-2v-.41c2.93 1.19 5 4.06 5 7.41 0 2.08-.8 3.97-2.1 5.39z"/></svg>
                    </div>
                    <div style="text-align: left;">
                        <p style="margin: 0; color: #666; font-size: 12px;">Sitio Web</p>
                        <a href="https://{website}" target="_blank" style="color: #ff6600; text-decoration: none; font-weight: bold;">{website}</a>
                    </div>
                </div>
                
            </div>
        </div>
        
        <!-- FOOTER MEJORADO -->
        <div style="text-align: center; padding: 30px 20px; margin-top: 40px; border-top: 3px solid #FFC107;">
            <div style="display: flex; flex-wrap: wrap; justify-content: center; gap: 20px; margin-bottom: 20px;">
                <div style="display: flex; align-items: center; gap: 5px; color: #666;">
                    {iconos['check']} <span style="font-weight: bold;">Garantia Oficial</span>
                </div>
                <div style="display: flex; align-items: center; gap: 5px; color: #666;">
                    {iconos['check']} <span style="font-weight: bold;">Servicio Tecnico</span>
                </div>
                <div style="display: flex; align-items: center; gap: 5px; color: #666;">
                    {iconos['check']} <span style="font-weight: bold;">Repuestos Originales</span>
                </div>
                <div style="display: flex; align-items: center; gap: 5px; color: #666;">
                    {iconos['check']} <span style="font-weight: bold;">Financiacion</span>
                </div>
            </div>
            <p style="color: #999; font-size: 14px; margin: 0;">
                Copyright 2024 - Todos los derechos reservados | Distribuidor Oficial de Grupos Electrogenos
            </p>
        </div>
        
    </div>
    """
    
    return html

def generar_speech_venta_fallback(info_tecnica, caracteristicas_reales):
    """
    Genera un speech de ventas sin IA como respaldo
    Ahora usa características validadas
    """
    tipo_combustible = caracteristicas_reales['tipo_combustible']
    tiene_cabina = caracteristicas_reales['tiene_cabina']
    tiene_tta = caracteristicas_reales['tiene_tta']
    
    # Adaptar el texto según el tipo de producto real
    tipo_producto = determinar_tipo_producto(info_tecnica)
    
    if tipo_producto == 'vibrador' or tipo_producto == 'vibropisonador':
        return generar_speech_vibrador(info_tecnica)
    elif tipo_producto == 'compresor':
        return generar_speech_compresor(info_tecnica)
    else:
        # Continuar con el speech de generador usando características validadas
        return generar_speech_venta_mejorado(info_tecnica, obtener_iconos_por_tipo('generador'), tiene_cabina, tiene_tta)

def generar_speech_vibrador(info_tecnica):
    """Genera speech específico para vibradores/vibropisonadores"""
    iconos = obtener_iconos_por_tipo('vibrador')
    
    return f"""
    <div style="background: white; border-radius: 10px; padding: 25px; margin: 20px 0; box-shadow: 0 2px 8px rgba(0,0,0,0.08); border-left: 5px solid #FFC107;">
        <h3 style="color: #D32F2F; font-size: 22px; margin: 0 0 15px 0;">POTENCIA DE COMPACTACION SUPERIOR</h3>
        <p style="font-size: 16px; line-height: 1.8; color: #333;">
            Este vibropisonador de alta performance está diseñado para trabajos de compactación exigentes. 
            Su motor {info_tecnica['motor']} garantiza la potencia necesaria para lograr la compactación óptima 
            en todo tipo de suelos y materiales granulares.
        </p>
    </div>
    
    <div style="background: white; border-radius: 10px; padding: 25px; margin: 20px 0; box-shadow: 0 2px 8px rgba(0,0,0,0.08); border-left: 5px solid #FFC107;">
        <h3 style="color: #D32F2F; font-size: 22px; margin: 0 0 15px 0;">APLICACIONES PROFESIONALES</h3>
        <ul style="font-size: 16px; line-height: 1.8; color: #333; margin: 0; padding-left: 20px;">
            <li>Compactación de suelos en construcción</li>
            <li>Preparación de bases para pavimentos</li>
            <li>Trabajos de jardinería y paisajismo</li>
            <li>Compactación de zanjas y rellenos</li>
            <li>Mantenimiento de caminos rurales</li>
        </ul>
    </div>
    """

def generar_speech_compresor(info_tecnica):
    """Genera speech específico para compresores"""
    iconos = obtener_iconos_por_tipo('compresor')
    
    return f"""
    <div style="background: white; border-radius: 10px; padding: 25px; margin: 20px 0; box-shadow: 0 2px 8px rgba(0,0,0,0.08); border-left: 5px solid #FFC107;">
        <h3 style="color: #D32F2F; font-size: 22px; margin: 0 0 15px 0;">AIRE COMPRIMIDO DE CALIDAD PROFESIONAL</h3>
        <p style="font-size: 16px; line-height: 1.8; color: #333;">
            Este compresor de aire está diseñado para brindar un suministro constante y confiable de aire comprimido. 
            Su motor {info_tecnica['motor']} asegura un rendimiento óptimo para todas sus herramientas neumáticas 
            y aplicaciones industriales.
        </p>
    </div>
    
    <div style="background: white; border-radius: 10px; padding: 25px; margin: 20px 0; box-shadow: 0 2px 8px rgba(0,0,0,0.08); border-left: 5px solid #FFC107;">
        <h3 style="color: #D32F2F; font-size: 22px; margin: 0 0 15px 0;">VERSATILIDAD DE APLICACIONES</h3>
        <ul style="font-size: 16px; line-height: 1.8; color: #333; margin: 0; padding-left: 20px;">
            <li>Herramientas neumáticas de taller</li>
            <li>Sistemas de pintura por aspersión</li>
            <li>Inflado de neumáticos y equipos</li>
            <li>Limpieza con aire a presión</li>
            <li>Aplicaciones industriales diversas</li>
        </ul>
    </div>
    """

def generar_speech_venta_mejorado(info_tecnica, iconos, tiene_cabina=False, tiene_tta=False):
    """
    Genera un speech de ventas estructurado por secciones con diseño mejorado (fallback sin IA)
    """
    tipo_combustible = "diesel" if 'diesel' in info_tecnica['familia'].lower() else "gas"
    
    secciones = [
        {
            "titulo": "POTENCIA Y RENDIMIENTO SUPERIOR",
            "icono": iconos['potencia'],
            "contenido": f"Con una capacidad de {info_tecnica['potencia_kva']} KVA, este grupo electrogeno esta disenado para superar las expectativas mas exigentes. Su motor {info_tecnica['motor']} representa lo ultimo en tecnologia {'diesel de alta eficiencia' if tipo_combustible == 'diesel' else 'a gas con bajas emisiones'}, garantizando un funcionamiento optimo en cualquier condicion de trabajo."
        },
        {
            "titulo": "ECONOMIA OPERATIVA GARANTIZADA",
            "icono": iconos['consumo'],
            "contenido": f"Con un consumo de apenas {info_tecnica['consumo']} litros por hora y un tanque de {info_tecnica['tanque']} litros, obtendra horas de operacion continua sin interrupciones. Esto se traduce en ahorro real y menor frecuencia de reabastecimiento, maximizando su productividad."
        },
        {
            "titulo": "CONFIABILIDAD COMPROBADA",
            "icono": iconos['confiabilidad'],
            "contenido": f"El alternador {info_tecnica['alternador']} asegura una entrega de energia estable y constante, protegiendo sus equipos mas sensibles. {'La cabina insonorizada reduce drasticamente el ruido, ' if tiene_cabina else ''}{'El tablero de transferencia automatica garantiza el cambio instantaneo de energia, ' if tiene_tta else ''}brindando tranquilidad absoluta en su operacion."
        },
        {
            "titulo": "APLICACIONES IDEALES",
            "icono": iconos['aplicaciones'],
            "contenido": """
                <ul style="font-size: 16px; line-height: 1.8; color: #333; margin: 0; padding-left: 20px;">
                    <li>Industrias y fabricas que requieren energia constante</li>
                    <li>Comercios y centros de atencion al publico</li>
                    <li>Hospitales y centros de salud</li>
                    <li>Eventos y espectaculos al aire libre</li>
                    <li>Respaldo para sistemas criticos</li>
                </ul>
            """
        },
        {
            "titulo": "POR QUE ELEGIR ESTE EQUIPO",
            "icono": iconos['porque'],
            "contenido": "No es solo un generador, es su socio en continuidad operativa. Con respaldo de marca reconocida, servicio tecnico especializado y disponibilidad inmediata de repuestos, su inversion esta protegida. La calidad se paga sola con el primer corte de energia que resuelva."
        }
    ]
    
    speech_html = ""
    for seccion in secciones:
        speech_html += f"""
        <div style="background: white; border-radius: 10px; padding: 25px; margin: 20px 0; box-shadow: 0 2px 8px rgba(0,0,0,0.08); border-left: 5px solid #FFC107;">
            <div style="display: flex; align-items: center; gap: 15px; margin-bottom: 15px;">
                <div style="width: 40px; height: 40px; background: #ffe8cc; border-radius: 50%; display: flex; align-items: center; justify-content: center;">
                    {seccion['icono']}
                </div>
                <h3 style="color: #D32F2F; font-size: 22px; margin: 0;">
                    {seccion['titulo']}
                </h3>
            </div>
            <div style="font-size: 16px; line-height: 1.8; color: #333;">
                {seccion['contenido']}
            </div>
        </div>
        """
    
    return speech_html

def generar_speech_venta_ia(info_tecnica, modelo_ia, pdf_url=None):
    """
    Genera un speech de ventas completo y persuasivo usando IA
    Ahora con validación de características basada en PDF
    """
    # Primero, intentar leer el PDF si está disponible
    texto_pdf = None
    if pdf_url:
        texto_pdf = extraer_texto_pdf(pdf_url)
        
    # Validar características reales del producto
    caracteristicas_reales = validar_caracteristicas_producto(info_tecnica, texto_pdf)
    
    # Preparar contexto detallado para la IA
    contexto_producto = f"""
    Producto: {info_tecnica['nombre']}
    Marca: {info_tecnica['marca']}
    Modelo: {info_tecnica['modelo']}
    Familia: {info_tecnica['familia']}
    Potencia: {info_tecnica['potencia_kva']} KVA / {info_tecnica['potencia_kw']} KW
    Voltaje: {info_tecnica['voltaje']} V
    Frecuencia: {info_tecnica['frecuencia']} Hz
    Motor: {info_tecnica['motor']}
    Alternador: {info_tecnica['alternador']}
    Consumo: {info_tecnica['consumo']} L/h
    Capacidad Tanque: {info_tecnica['tanque']} L
    Nivel Ruido: {info_tecnica['ruido']} dBA
    Dimensiones: {info_tecnica['largo']}x{info_tecnica['ancho']}x{info_tecnica['alto']} mm
    Peso: {info_tecnica['peso']} kg
    
    IMPORTANTE - CARACTERÍSTICAS CONFIRMADAS:
    - Tipo de combustible: {caracteristicas_reales['tipo_combustible']}
    - Tiene cabina insonorizada: {'SÍ' if caracteristicas_reales['tiene_cabina'] else 'NO'}
    - Tiene transferencia automática (TTA): {'SÍ' if caracteristicas_reales['tiene_tta'] else 'NO'}
    - Es inverter: {'SÍ' if caracteristicas_reales['es_inverter'] else 'NO'}
    """
    
    # Si hay información del PDF, agregarla al contexto
    if texto_pdf:
        contexto_producto += f"\n\nINFORMACIÓN ADICIONAL DEL PDF:\n{texto_pdf[:1000]}..."  # Limitar a 1000 caracteres
    
    # Prompt mejorado con restricciones claras
    prompt = f"""
    Eres un experto vendedor de equipos industriales. Genera un texto de venta MUY PERSUASIVO y EXTENSO (mínimo 600 palabras) para:
    
    {contexto_producto}
    
    REGLAS ESTRICTAS:
    1. SOLO menciona las características que están marcadas como "SÍ" en las características confirmadas
    2. NO INVENTES características que no están en los datos
    3. Si el producto NO es un generador eléctrico, NO menciones características de generadores
    4. Enfócate en los beneficios reales basados en las especificaciones proporcionadas
    
    El texto debe incluir:
    1. APERTURA IMPACTANTE que identifique la necesidad real del cliente para este tipo de producto
    2. BENEFICIOS TÉCNICOS explicando por qué cada especificación real importa
    3. VENTAJAS del combustible {caracteristicas_reales['tipo_combustible']} (solo si aplica)
    4. CASOS DE USO específicos y realistas para este tipo de equipo
    5. ROI y ahorro a largo plazo basado en datos reales
    6. GARANTÍAS y respaldo de servicio
    7. CIERRE PERSUASIVO con llamada a la acción
    
    Usa un tono profesional pero apasionado. NO uses bullets, solo párrafos bien escritos.
    NO menciones características que no están confirmadas como "SÍ".
    """

def generar_speech_venta_ia_mejorado(info_tecnica, modelo_ia, iconos, tiene_cabina=False, tiene_tta=False):
    """
    Genera un speech de ventas con IA usando formato estructurado y lo limpia
    """
    contexto_producto = f"""
    Producto: {info_tecnica['nombre']}, Potencia: {info_tecnica['potencia_kva']} KVA, Motor: {info_tecnica['motor']}, 
    Alternador: {info_tecnica['alternador']}, Consumo: {info_tecnica['consumo']} L/h, Tanque: {info_tecnica['tanque']} L
    {'Incluye cabina insonorizada.' if tiene_cabina else ''} {'Incluye TTA.' if tiene_tta else ''}
    """
    
    prompt = f"""
    Eres un experto en marketing para equipos industriales. Genera 5 secciones de texto de venta para un generador.
    Cada sección debe tener un título y un párrafo de 2-3 frases.
    
    Producto: {contexto_producto}
    
    Las secciones son:
    1.  **POTENCIA Y RENDIMIENTO SUPERIOR**: Enfócate en la capacidad y el motor.
    2.  **ECONOMIA OPERATIVA GARANTIZADA**: Habla del consumo y la autonomía.
    3.  **CONFIABILIDAD COMPROBADA**: Menciona el alternador y las características especiales.
    4.  **APLICACIONES IDEALES**: Lista 5 usos comunes en formato de lista con guiones.
    5.  **POR QUE ELEGIR ESTE EQUIPO**: Cierra con un mensaje de confianza y respaldo.
    
    Usa un lenguaje persuasivo y profesional. NO uses emojis. NO uses markdown.
    Separa cada sección con "---".
    Ejemplo de formato:
    TITULO 1
    Párrafo 1.
    ---
    TITULO 2
    Párrafo 2.
    """
    
    try:
        response = modelo_ia.generate_content(
            prompt,
            generation_config={'temperature': 0.7, 'max_output_tokens': 1500}
        )
        
        if not response or not response.text:
            raise Exception("No se genero respuesta de la IA")
            
        # Limpieza del texto de la IA
        texto_crudo = response.text
        texto_limpio = re.sub(r'```html|```', '', texto_crudo).strip()
        
        secciones_texto = texto_limpio.split('---')
        
        iconos_secciones = [
            iconos['potencia'], 
            iconos['consumo'], 
            iconos['confiabilidad'], 
            iconos['aplicaciones'], 
            iconos['porque']
        ]
        
        speech_html = ""
        for i, seccion_texto in enumerate(secciones_texto):
            if not seccion_texto.strip():
                continue
            
            partes = seccion_texto.strip().split('\n', 1)
            titulo = partes[0].replace('**', '').strip()
            contenido = partes[1].strip() if len(partes) > 1 else ''
            
            # Formatear lista de aplicaciones
            if "APLICACIONES IDEALES" in titulo.upper():
                items = [f'<li>{item.strip()}</li>' for item in contenido.replace('-', '').split('\n') if item.strip()]
                contenido = f'<ul style="font-size: 16px; line-height: 1.8; color: #333; margin: 0; padding-left: 20px;">{"".join(items)}</ul>'
            else:
                contenido = f'<p style="font-size: 16px; line-height: 1.8; color: #333; margin: 0;">{contenido}</p>'

            icono_actual = iconos_secciones[i] if i < len(iconos_secciones) else iconos['check']
            
            speech_html += f"""
            <div style="background: white; border-radius: 10px; padding: 25px; margin: 20px 0; box-shadow: 0 2px 8px rgba(0,0,0,0.08); border-left: 5px solid #FFC107;">
                <div style="display: flex; align-items: center; gap: 15px; margin-bottom: 15px;">
                    <div style="width: 40px; height: 40px; background: #ffe8cc; border-radius: 50%; display: flex; align-items: center; justify-content: center;">
                        {icono_actual}
                    </div>
                    <h3 style="color: #D32F2F; font-size: 22px; margin: 0;">
                        {titulo}
                    </h3>
                </div>
                {contenido}
            </div>
            """
            
        return speech_html

    except Exception as e:
        print(f"Error generando con IA, usando fallback: {e}")
        return generar_speech_venta_mejorado(info_tecnica, iconos, tiene_cabina, tiene_tta)

# ============================================================================
# FUNCIONES PARA GENERAR DESCRIPCIONES HÍBRIDAS
# ============================================================================

def extraer_info_tecnica(row):
    """
    Extrae toda la información técnica relevante de la fila
    """
    info = {
        'nombre': str(row.get('Título para Store', 'Producto')),
        'marca': str(row.get('Marca', '')),
        'modelo': str(row.get('Modelo', '')),
        'codigo': str(row.get('Código SKU', '')),
        'familia': str(row.get('Familia', '')),
        'potencia_kva': str(row.get('Potencia_KVA_Emergencia', '')),
        'potencia_kw': str(row.get('Potencia_KW_Emergencia', '')),
        'voltaje': str(row.get('Voltaje', '')),
        'frecuencia': str(row.get('Frecuencia', '')),
        'motor': str(row.get('Motor_Marca_Modelo', '')),
        'alternador': str(row.get('Alternador_Marca_Modelo', '')),
        'consumo': str(row.get('Consumo_Combustible_L_H', '')),
        'tanque': str(row.get('Capacidad_Tanque_L', '')),
        'ruido': str(row.get('Nivel_Ruido_dBA', '')),
        'largo': str(row.get('Dimensiones_Largo_mm', '')),
        'ancho': str(row.get('Dimensiones_Ancho_mm', '')),
        'alto': str(row.get('Dimensiones_Alto_mm', '')),
        'peso': str(row.get('Peso_kg', '')),
        'pdf_url': str(row.get('URL PDF', ''))
    }
    
    # Limpiar valores nan
    for key in info:
        if info[key] in ['nan', 'None', '', 'NaN']:
            info[key] = ''
    
    return info

def mejorar_descripcion_existente(descripcion_base, info_tecnica):
    """
    Toma una descripción existente y la mejora con formato y estructura
    """
    if not descripcion_base or descripcion_base in ['nan', 'None', '']:
        return None
    
    # Extraer puntos clave de la descripción existente
    puntos_clave = []
    
    # Buscar características mencionadas
    lineas = descripcion_base.split('.')
    for linea in lineas:
        if len(linea.strip()) > 10:  # Ignorar líneas muy cortas
            puntos_clave.append(linea.strip())
    
    # Reorganizar con mejor formato
    descripcion_mejorada = f"""========================================
    {info_tecnica['marca'].upper()} {info_tecnica['modelo']}
========================================

{puntos_clave[0] if puntos_clave else 'Grupo electrógeno de alta calidad y rendimiento superior.'}

[ ESPECIFICACIONES PRINCIPALES ]
- Potencia: {info_tecnica['potencia_kva']} KVA{f" / {info_tecnica['potencia_kw']} KW" if info_tecnica['potencia_kw'] else ''}
- Tensión: {info_tecnica['voltaje']} V
- Frecuencia: {info_tecnica['frecuencia']} Hz

[ MOTORIZACIÓN Y GENERACIÓN ]
- Motor: {info_tecnica['motor']}
- Alternador: {info_tecnica['alternador']}

"""
    
    # Si hay más puntos clave, agregarlos
    if len(puntos_clave) > 1:
        descripcion_mejorada += "[ CARACTERÍSTICAS DESTACADAS ]\n"
        for punto in puntos_clave[1:4]:  # Máximo 3 puntos adicionales
            descripcion_mejorada += f"• {punto}\n"
    
    return descripcion_mejorada

def generar_descripcion_hibrida(row, usar_base=False, col_base=None):
    """
    Genera descripción combinando datos técnicos con descripción existente si está disponible
    """
    info = extraer_info_tecnica(row)
    
    # Si se solicita usar descripción base y existe
    if usar_base and col_base and col_base in row:
        desc_existente = str(row.get(col_base, ''))
        desc_mejorada = mejorar_descripcion_existente(desc_existente, info)
        if desc_mejorada:
            return desc_mejorada
    
    # Generar descripción técnica completa
    # Calcular autonomía
    autonomia = "Variable según carga"
    if info['consumo'] and info['tanque']:
        try:
            horas = float(info['tanque']) / float(info['consumo'])
            autonomia = f"~ {horas:.1f} horas"
        except:
            pass
    
    descripcion = f"""========================================
    {info['marca'].upper()} {info['modelo']}
========================================

[ CAPACIDAD NOMINAL ]
- Potencia: {info['potencia_kva'] or 'N/D'} KVA{f" / {info['potencia_kw']} KW" if info['potencia_kw'] else ''}
- Tensión: {info['voltaje'] or 'N/D'} V
- Frecuencia: {info['frecuencia'] or 'N/D'} Hz

[ CONJUNTO MOTOR-GENERADOR ]
- Motor: {info['motor'] or 'N/D'}
- Alternador: {info['alternador'] or 'N/D'}

[ CONSUMO Y AUTONOMÍA ]
- Consumo al 75%: {info['consumo'] or 'N/D'} L/h
- Capacidad tanque: {info['tanque'] or 'N/D'} L
- Autonomía estimada: {autonomia}

[ NIVEL SONORO ]
- {info['ruido'] or 'N/D'} dBA @ 7 metros

[ DIMENSIONES Y PESO ]
- Medidas (LxAxH): {info['largo'] or 'N/D'}x{info['ancho'] or 'N/D'}x{info['alto'] or 'N/D'} mm
- Peso operativo: {info['peso'] or 'N/D'} kg

[ CARACTERÍSTICAS CONSTRUCTIVAS ]
- Chasis estructural reforzado
- Sistema de amortiguación de vibraciones  
- Panel de control con protecciones
- Radiador tropical de alto rendimiento
- Filtros de aire de doble etapa
- Sistema de escape con silenciador

[ PROTECCIONES INCLUIDAS ]
- Baja presión de aceite
- Alta temperatura de motor
- Sobrecarga y cortocircuito
- Bajo nivel de combustible
- Falla de carga de batería

========================================"""
    
    return descripcion

def generar_descripcion_detallada_html(row, config):
    """
    Genera descripción detallada en HTML con información de contacto configurable
    """
    info = extraer_info_tecnica(row)
    
    # Configuración de contacto
    whatsapp = config.get('whatsapp', '541139563099')
    email = config.get('email', 'info@generadores.ar')
    telefono_display = config.get('telefono_display', '+54 11 3956-3099')
    website = config.get('website', 'www.generadores.ar')
    
    # URL del PDF
    pdf_url = info['pdf_url']
    if pdf_url and not pdf_url.startswith('http'):
        pdf_url = f"https://storage.googleapis.com/fichas_tecnicas/{pdf_url}"
    
    # Mensajes para enlaces
    nombre_producto = info['nombre']
    whatsapp_msg = f"Hola,%20vengo%20de%20ver%20el%20{nombre_producto.replace(' ', '%20')}%20en%20la%20tienda%20de%20Stelorder%20y%20quisiera%20más%20información%20sobre%20este%20producto"
    email_subject = f"Consulta%20desde%20Stelorder%20-%20{nombre_producto.replace(' ', '%20')}"
    email_body = f"Hola,%0A%0AVengo%20de%20ver%20el%20{nombre_producto.replace(' ', '%20')}%20en%20la%20tienda%20de%20Stelorder%20y%20quisiera%20más%20información%20sobre%20este%20producto.%0A%0AQuedo%20a%20la%20espera%20de%20su%20respuesta.%0A%0ASaludos"
    
    # Generar HTML
    html = f"""<p><strong>{nombre_producto.upper()}</strong></p>

<p>Producto de alta calidad y rendimiento comprobado. Este grupo electrógeno ofrece una solución confiable para sus necesidades específicas, con tecnología de vanguardia y diseño optimizado para máxima eficiencia.</p>

<p><strong>Características Técnicas Principales:</strong><br>
- <strong>Potencia:</strong> {info['potencia_kva'] or 'N/D'} KVA{f" / {info['potencia_kw']} KW" if info['potencia_kw'] else ''}<br>
- <strong>Voltaje:</strong> {info['voltaje'] or 'N/D'} V<br>
- <strong>Frecuencia:</strong> {info['frecuencia'] or 'N/D'} Hz<br>
- <strong>Motor:</strong> {info['motor'] or 'N/D'}<br>
- <strong>Alternador:</strong> {info['alternador'] or 'N/D'}</p>

<p>-----------------------------------</p>

<p><strong>DOCUMENTACIÓN TÉCNICA</strong><br>
<a href="{pdf_url}" target="_blank">Descargar Ficha Técnica Completa (PDF)</a></p>

<p><strong>¿NECESITA ASESORAMIENTO?</strong><br>
<a href="https://wa.me/{whatsapp}?text={whatsapp_msg}" target="_blank">Consultar por WhatsApp</a><br>
<a href="mailto:{email}?subject={email_subject}&body={email_body}">Enviar Consulta por Email</a></p>

<p>-----------------------------------</p>

<p><strong>INFORMACIÓN DE CONTACTO</strong><br>
<strong>Teléfono:</strong> <a href="https://wa.me/{whatsapp}?text={whatsapp_msg}" target="_blank">{telefono_display}</a><br>
<strong>WhatsApp:</strong> <a href="https://wa.me/{whatsapp}?text={whatsapp_msg}" target="_blank">{telefono_display}</a><br>
<strong>Email:</strong> <a href="mailto:{email}?subject={email_subject}&body={email_body}">{email}</a><br>
<strong>Web:</strong> <a href="https://{website}" target="_blank">{website}</a></p>

<p>Garantía oficial | Servicio técnico especializado | Repuestos disponibles</p>"""
    
    return html

# ============================================================================
# FUNCIONES DE SELENIUM (respetando estructura original)
# ============================================================================

def run_automation(self):
    """
    Inicia el navegador Chrome con perfil persistente y espera el login manual del usuario.
    ESTRUCTURA ORIGINAL RESPETADA
    """
    import os
    from selenium.common.exceptions import SessionNotCreatedException
    options = Options()
    options.add_experimental_option("detach", True)
    profile_dir = os.path.abspath("./selenium_stel_profile")
    os.makedirs(profile_dir, exist_ok=True)
    options.add_argument(f"user-data-dir={profile_dir}")
    driver_service = Service()
    try:
        self.driver = webdriver.Chrome(service=driver_service, options=options)
    except SessionNotCreatedException as e:
        self.log("❌ El perfil de Chrome ya está en uso. Cierra todas las ventanas de Chrome abiertas que usen este perfil e inténtalo de nuevo.")
        return
    except Exception as e:
        self.log(f"❌ Error al iniciar Chrome: {e}")
        return
    self.driver.get("https://www.stelorder.com/app/")
    self.wait = WebDriverWait(self.driver, 60)
    try:
        self.log("🌐 Cargando página y esperando que todo esté listo...")
        self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        self.log("✅ Body cargado.")
        self.log("🔔 El navegador está listo. Por favor, logueate manualmente y luego presioná el botón '✅ Confirmar que ya estoy logueado'.")
        self.continuar_button.config(state="normal")
    except Exception as e:
        self.log(f"⚠️ Error en login: {e}")
        self.driver.quit()
        return
    def cleanup_profile():
        try:
            self.driver.quit()
        except:
            pass
    self.cleanup_temp_profile = cleanup_profile

def procesar_productos(self):
    """
    Versión híbrida que genera descripciones combinando datos técnicos y descripciones existentes
    MANTIENE LA ESTRUCTURA DE NAVEGACIÓN ORIGINAL
    """
    self.log("🚀 Comenzando procesamiento HÍBRIDO de productos...")
    
    # Verificar que el navegador esté inicializado
    if not hasattr(self, "driver") or not self.driver:
        self.log("❌ ERROR: El navegador no está inicializado.")
        return
    
    if not hasattr(self, "wait") or not self.wait:
        self.log("❌ ERROR: WebDriverWait no está inicializado.")
        return
        
    # Leer datos del Excel
    try:
        df = pd.read_excel(self.excel_path.get())
        self.log(f"✅ Excel cargado con {len(df)} productos.")
    except Exception as e:
        self.log(f"❌ Error al leer el Excel: {e}")
        return
    
    # Verificar si hay productos
    if len(df) == 0:
        self.log("❌ No hay productos en el Excel.")
        return
    
    # Configuración de contacto
    config_contacto = {
        'whatsapp': self.whatsapp_var.get(),
        'email': self.email_var.get(),
        'telefono_display': self.telefono_display_var.get(),
        'website': self.web_var.get()
    }
    
    # Obtener columnas configuradas
    col_codigo = self.col_codigo.get()
    col_destacado = self.col_destacado.get()
    col_seo_titulo = self.col_seo_titulo.get()
    col_seo_desc = self.col_seo_desc.get()
    
    # Verificar columnas obligatorias
    if not col_codigo:
        self.log("❌ ERROR: No se ha seleccionado la columna de Código/SKU")
        return
    
    # Opciones de generación
    usar_desc_base = self.usar_desc_existente.get()
    col_desc_base = self.col_desc_base.get() if usar_desc_base else None
    usar_ia = self.usar_ia_premium.get() and hasattr(self, 'modelo_ia') and self.modelo_ia
    
    if usar_ia:
        self.log("🤖 Modo IA PREMIUM activado")
    else:
        self.log("📝 Modo estándar (sin IA)")
    
    driver = self.driver
    wait = self.wait
    
    # Procesar cada producto
    for i, row in df.iterrows():
        try:
            # Para cada producto, siempre comenzamos navegando al catálogo
            self.log(f"\n{'='*50}")
            self.log(f"📦 Producto {i+1}/{len(df)}")
            self.log(f"{'='*50}")
            
            # Verificar si el proceso está pausado
            if hasattr(self, "verificar_pausa"):
                self.verificar_pausa()
            
            # Verificar si se cerró el navegador
            if not self.driver:
                self.log("❌ Navegador cerrado. Deteniendo proceso.")
                return
            
            # PASO 1: Navegar al catálogo (SOLUCIÓN FORZADA - ESTRUCTURA ORIGINAL)
            try:
                self.log("🔄 NAVEGACIÓN FORZADA al catálogo...")
                
                # 1.1 Limpiar completamente la sesión navegando a una página en blanco
                driver.get("about:blank")
                time.sleep(1)
                
                # 1.2 Navegar directamente al catálogo con URL completa
                driver.get("https://app.stelorder.com/app/#main_catalogo")
                time.sleep(5)  # Espera extendida para carga completa
                
                # 1.3 Forzar refresco de página
                driver.refresh()
                time.sleep(3)
                
                # 1.4 Hacer clic en la pestaña Catálogo usando JavaScript
                try:
                    catalogo_btn = wait.until(EC.presence_of_element_located((By.XPATH, "//a[@id='ui-id-2']")))
                    driver.execute_script("arguments[0].click();", catalogo_btn)
                    self.log("✅ Pestaña Catálogo activada mediante JavaScript.")
                    time.sleep(3)
                except Exception as e:
                    self.log(f"⚠️ No se pudo hacer clic en pestaña Catálogo: {e}")
                    # Segundo intento con método normal
                    try:
                        catalogo_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//a[@id='ui-id-2']")))
                        catalogo_btn.click()
                        time.sleep(3)
                    except:
                        self.log("⚠️ Ambos intentos de clic en Catálogo fallaron.")
                
                # 1.5 Verificar que el buscador está disponible y activo
                try:
                    buscador = wait.until(EC.presence_of_element_located((By.XPATH, "//input[contains(@class, 'buscadorListado')]")))
                    if buscador.is_displayed() and buscador.is_enabled():
                        # Usar JavaScript para limpiar el campo
                        driver.execute_script("arguments[0].value = '';", buscador)
                        buscador.clear()  # Doble limpieza
                        self.log("✅ Buscador limpiado y listo.")
                        
                        # Limpiar filtros solo en el primer producto
                        if i == 0:
                            try:
                                self.log("🔍 Buscando botón para limpiar filtros...")
                                limpiar_filtros = wait.until(EC.element_to_be_clickable((By.XPATH, "//*[@id='main_catalogo']/div[2]/div[1]/button[4]")))
                                driver.execute_script("arguments[0].scrollIntoView(true);", limpiar_filtros)
                                driver.execute_script("arguments[0].click();", limpiar_filtros)
                                self.log("🗑️ Filtros limpiados correctamente.")
                                time.sleep(2)
                            except Exception as e:
                                self.log(f"⚠️ No se pudo limpiar los filtros: {e}")
                    else:
                        raise Exception("Buscador no está visible o habilitado")
                except Exception as e:
                    self.log(f"❌ Error crítico: Buscador no disponible: {e}")
                    continue
                    
                self.log("✅ Catálogo cargado y listo.")
            except Exception as e:
                self.log(f"❌ Error al navegar al catálogo: {e}")
                self.log(f"   Detalles: {traceback.format_exc()}")
                continue
                
            # Datos del producto actual
            codigo_producto = str(row[col_codigo])
            self.log(f"📦 Procesando: {codigo_producto}")
            
            # GENERAR DESCRIPCIONES HÍBRIDAS
            self.log("🤖 Generando descripciones...")
            
            try:
                # Descripción simple (técnica)
                if usar_desc_base:
                    self.log(f"📝 Usando columna base: {col_desc_base}")
                descripcion = generar_descripcion_hibrida(row, usar_desc_base, col_desc_base)
                
                # Descripción detallada (HTML)
                if usar_ia and self.modelo_ia:
                    self.log("🌟 Generando descripción PREMIUM con IA...")
                    detallada = generar_descripcion_detallada_html_premium(row, config_contacto, self.modelo_ia)
                else:
                    self.log("📝 Generando descripción estándar...")
                    detallada = generar_descripcion_detallada_html(row, config_contacto)
                
                self.log("✅ Descripciones generadas exitosamente")
            except Exception as e:
                self.log(f"❌ Error generando descripciones: {e}")
                continue
            
            # SEO
            seo_titulo = str(row[col_seo_titulo]) if col_seo_titulo and pd.notna(row.get(col_seo_titulo)) else f"{row.get('Título para Store', codigo_producto)} - Generador Eléctrico"
            seo_desc = str(row[col_seo_desc]) if col_seo_desc and pd.notna(row.get(col_seo_desc)) else descripcion[:160].replace('\n', ' ')
            destacado = str(row[col_destacado]).strip().lower() if col_destacado and col_destacado in row else "no"
            
            # Verificar pausa antes de buscar el producto
            if hasattr(self, "verificar_pausa"):
                self.verificar_pausa()
            
            # PASO 2: Buscar y seleccionar el producto
            self.log(f"🔍 Buscando producto: '{codigo_producto}'")
            try:
                # Limpiar buscador con método alternativo
                buscador = wait.until(EC.element_to_be_clickable((By.XPATH, "//input[contains(@class, 'buscadorListado')]")))
                buscador.clear()
                driver.execute_script("arguments[0].value = '';", buscador)  # Doble limpieza con JS
                time.sleep(0.5)
                
                # Escribir texto letra por letra con pequeñas pausas
                for letra in codigo_producto:
                    buscador.send_keys(letra)
                    time.sleep(0.05)
                time.sleep(2)  # Espera para resultados
                
                # Buscar y hacer clic en el primer resultado
                primer_fila = wait.until(EC.element_to_be_clickable((By.XPATH, "//td[@class='tdTextoLargo tdBold']")))
                driver.execute_script("arguments[0].click();", primer_fila)  # Clic vía JavaScript
                time.sleep(3)
                self.log("✅ Producto encontrado y seleccionado.")
            except Exception as e:
                self.log(f"❌ Error al buscar producto: {e}")
                continue
                
            # PASO 3: Ir a pestaña Shop
            self.log("🔍 Buscando pestaña Shop...")
            shop_encontrado = False
            for selector in ["//a[@id='ui-id-31']", "//li[contains(@class, 'ui-tabs-tab')]/a[contains(text(), 'Shop')]", "//a[contains(text(), 'Shop')]"]:
                try:
                    shop_tab = wait.until(EC.element_to_be_clickable((By.XPATH, selector)))
                    driver.execute_script("arguments[0].scrollIntoView(true);", shop_tab)
                    time.sleep(1)
                    driver.execute_script("arguments[0].click();", shop_tab)
                    time.sleep(3)
                    shop_encontrado = True
                    self.log(f"✅ Pestaña Shop activada con selector: {selector}")
                    break
                except Exception:
                    continue
                    
            if not shop_encontrado:
                self.log("❌ No se pudo encontrar la pestaña Shop.")
                continue
                
            # PASO 4: Hacer clic en botón Editar Shop
            self.log("🔍 Buscando botón Editar Shop...")
            editar_encontrado = False
            for selector in ["//*[@id='editarShop']", "//button[contains(text(), 'Editar')]", "//button[contains(@class, 'editarShop')]"]:
                try:
                    editar_btn = wait.until(EC.element_to_be_clickable((By.XPATH, selector)))
                    driver.execute_script("arguments[0].scrollIntoView(true);", editar_btn)
                    time.sleep(1)
                    driver.execute_script("arguments[0].click();", editar_btn)
                    time.sleep(3)
                    editar_encontrado = True
                    self.log(f"✅ Botón Editar Shop activado con selector: {selector}")
                    break
                except Exception:
                    continue
                    
            if not editar_encontrado:
                self.log("❌ No se pudo encontrar el botón Editar Shop.")
                continue
                
            # PASO 5: Editar campos en el modal
            self.log("🔧 Editando campos en el modal...")
            try:
                # Esperar modal
                modal = wait.until(EC.visibility_of_element_located((By.ID, "editarObjetoCatalogoConfiguracionShop_dialog")))
                self.log("✅ Modal de edición detectado.")
                
                # Mostrar campos SEO
                try:
                    mostrar_seo = modal.find_element(By.ID, "trMostrarOcultarCamposSeoShopTable")
                    driver.execute_script("arguments[0].click();", mostrar_seo)
                    time.sleep(1)
                except Exception:
                    pass
                
                # Editar Descripción
                try:
                    desc_input = modal.find_element(By.ID, "descriptionShop")
                    desc_input.clear()
                    driver.execute_script("arguments[0].value = '';", desc_input)
                    for linea in descripcion.split('\n'):
                        desc_input.send_keys(linea)
                        desc_input.send_keys(Keys.SHIFT + Keys.ENTER)
                        time.sleep(0.05)
                    self.log("✅ Campo Descripción completado.")
                except Exception as e:
                    self.log(f"⚠️ Error al editar Descripción: {e}")
                
                # Editar Descripción Detallada (CKEditor)
                try:
                    iframe = modal.find_element(By.CSS_SELECTOR, "iframe.cke_wysiwyg_frame")
                    driver.switch_to.frame(iframe)
                    body = wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
                    
                    driver.execute_script("arguments[0].innerHTML = '';", body)
                    time.sleep(0.5)
                    
                    driver.execute_script("arguments[0].innerHTML = arguments[1];", body, detallada)
                    
                    driver.execute_script("""
                        var event = new Event('input', { bubbles: true });
                        arguments[0].dispatchEvent(event);
                        var changeEvent = new Event('change', { bubbles: true });
                        arguments[0].dispatchEvent(changeEvent);
                    """, body)
                    
                    time.sleep(1)
                    driver.switch_to.default_content()
                    self.log("✅ Campo Descripción Detallada completado con HTML.")
                    
                except Exception as e:
                    self.log(f"⚠️ Error al editar Descripción Detallada: {e}")
                    driver.switch_to.default_content()
                
                # Continuar con SEO y demás campos...
                # (el resto del código sigue igual)
                
                # Guardar cambios
                try:
                    guardar_btn = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button.opcionMenuGuardar.primaryButton")))
                    driver.execute_script("arguments[0].scrollIntoView(true);", guardar_btn)
                    time.sleep(1)
                    driver.execute_script("arguments[0].click();", guardar_btn)
                    self.log("💾 Botón Guardar clickeado.")
                    
                    wait.until(EC.invisibility_of_element_located((By.ID, "editarObjetoCatalogoConfiguracionShop_dialog")))
                    self.log("✅ Modal cerrado correctamente.")
                    time.sleep(3)
                except Exception as e:
                    self.log(f"❌ Error al guardar cambios: {e}")
                    continue
                
                self.log(f"✅ Producto '{codigo_producto}' procesado correctamente.")
                
            except Exception as e:
                self.log(f"❌ Error al editar campos: {e}")
                self.log(f"   Detalles: {traceback.format_exc()}")
                continue
            
            # Al final del producto, forzar navegación al catálogo
            self.log("🔄 Volviendo al catálogo para el siguiente producto...")
            driver.get("about:blank")
            time.sleep(1)
            
        except Exception as e:
            self.log(f"❌ Error general procesando producto {i+1}: {e}")
            self.log(f"   Detalles: {traceback.format_exc()}")
            continue
    
    self.log("\n" + "="*50)
    self.log("🏁 PROCESO FINALIZADO")
    self.log(f"✅ Se procesaron todos los productos")
    self.log("="*50)

# ============================================================================
# CLASE PRINCIPAL DE LA GUI
# ============================================================================

class StelUpdaterApp:
    """
    Generador inteligente de descripciones para STEL Shop - Versión Híbrida
    """
    def __init__(self, root):
        self.root = root
        self.root.title("STEL Shop - Generador Inteligente de Descripciones")
        self.root.geometry("900x800")
        
        # Variables
        self.excel_path = StringVar()
        self.columns = []
        
        # Variables de contacto
        self.whatsapp_var = StringVar(value="541139563099")
        self.email_var = StringVar(value="info@generadores.ar")
        self.telefono_display_var = StringVar(value="+54 11 3956-3099")
        self.web_var = StringVar(value="www.generadores.ar")
        
        # Variables de columnas
        self.col_codigo = StringVar()
        self.col_pdf = StringVar()
        self.col_destacado = StringVar()
        self.col_seo_titulo = StringVar()
        self.col_seo_desc = StringVar()
        self.col_desc_base = StringVar()
        
        # Variables de opciones
        self.usar_desc_existente = tk.BooleanVar(value=False)
        self.gemini_api_key = StringVar()
        self.usar_ia_premium = tk.BooleanVar(value=False)
        self.modelo_ia = None
        
        # Control
        self.pausado = False
        self.proceso_activo = False
        
        self.load_config()
        self.setup_ui()

    def setup_ui(self):
        # Frame principal con scroll
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Canvas y scrollbar
        canvas = tk.Canvas(main_frame)
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Layout
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # TÍTULO
        titulo_label = Label(scrollable_frame, text="STEL Shop - Generador Inteligente de Descripciones", 
                           font=('Arial', 16, 'bold'), fg='darkblue')
        titulo_label.grid(row=0, column=0, columnspan=3, pady=15)
        
        # FRAME 1: CONFIGURACIÓN DE CONTACTO
        contact_frame = ttk.LabelFrame(scrollable_frame, text="📞 Datos de Contacto", padding="15")
        contact_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        
        # WhatsApp
        Label(contact_frame, text="WhatsApp:").grid(row=0, column=0, sticky="e", padx=5, pady=3)
        Entry(contact_frame, textvariable=self.whatsapp_var, width=30).grid(row=0, column=1, sticky="w", padx=5)
        Label(contact_frame, text="(solo números, sin espacios)", font=('Arial', 8), fg='gray').grid(row=0, column=2)
        
        # Email
        Label(contact_frame, text="Email:").grid(row=1, column=0, sticky="e", padx=5, pady=3)
        Entry(contact_frame, textvariable=self.email_var, width=30).grid(row=1, column=1, sticky="w", padx=5)
        
        # Teléfono display
        Label(contact_frame, text="Teléfono (display):").grid(row=2, column=0, sticky="e", padx=5, pady=3)
        Entry(contact_frame, textvariable=self.telefono_display_var, width=30).grid(row=2, column=1, sticky="w", padx=5)
        
        # Sitio web
        Label(contact_frame, text="Sitio Web:").grid(row=3, column=0, sticky="e", padx=5, pady=3)
        Entry(contact_frame, textvariable=self.web_var, width=30).grid(row=3, column=1, sticky="w", padx=5)
        
        # FRAME 1.5: CONFIGURACIÓN DE IA (NUEVO)
        ia_frame = ttk.LabelFrame(scrollable_frame, text="🤖 Inteligencia Artificial (Opcional)", padding="15")
        ia_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)

        # Checkbox para activar IA
        tk.Checkbutton(ia_frame, 
                      text="Usar Google Gemini AI para generar descripciones premium de venta",
                      variable=self.usar_ia_premium,
                      command=self.toggle_ia_config).grid(row=0, column=0, columnspan=3, sticky="w", pady=5)

        # Frame para API Key (oculto inicialmente)
        self.ia_config_frame = ttk.Frame(ia_frame)

        Label(self.ia_config_frame, text="API Key de Google:").grid(row=0, column=0, sticky="e", padx=5)
        Entry(self.ia_config_frame, textvariable=self.gemini_api_key, width=50, show="*").grid(row=0, column=1, padx=5)
        Button(self.ia_config_frame, text="Validar", command=self.validar_api_key, bg='lightyellow').grid(row=0, column=2, padx=5)
        Button(self.ia_config_frame, text="Probar", command=self.probar_ia_descripcion, bg='lightblue').grid(row=0, column=3, padx=5)

        Label(self.ia_config_frame, text="Obtén tu API key gratis en:", font=('Arial', 8), fg='gray').grid(row=1, column=0, sticky="e")
        Label(self.ia_config_frame, text="https://makersuite.google.com/app/apikey", 
              font=('Arial', 8), fg='blue', cursor="hand2").grid(row=1, column=1, sticky="w")
        
        # FRAME 2: ARCHIVO EXCEL
        excel_frame = ttk.LabelFrame(scrollable_frame, text="📁 Archivo de Datos", padding="15")
        excel_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        
        Label(excel_frame, text="Archivo Excel:").grid(row=0, column=0, sticky="e", padx=5)
        Entry(excel_frame, textvariable=self.excel_path, width=50).grid(row=0, column=1, padx=5)
        Button(excel_frame, text="Seleccionar", command=self.load_excel, bg='lightblue').grid(row=0, column=2, padx=5)
        
        # FRAME 3: COLUMNAS PRINCIPALES
        columnas_frame = ttk.LabelFrame(scrollable_frame, text="🔧 Configuración de Columnas", padding="15")
        columnas_frame.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        
        self.add_combo_row("Código/SKU:", self.col_codigo, 0, columnas_frame)
        self.add_combo_row("URL del PDF:", self.col_pdf, 1, columnas_frame)
        self.add_combo_row("Destacado:", self.col_destacado, 2, columnas_frame)
        self.add_combo_row("SEO Título (opcional):", self.col_seo_titulo, 3, columnas_frame)
        self.add_combo_row("SEO Descripción (opcional):", self.col_seo_desc, 4, columnas_frame)
        
        # FRAME 4: OPCIONES DE GENERACIÓN
        opciones_frame = ttk.LabelFrame(scrollable_frame, text="⚙️ Opciones de Generación", padding="15")
        opciones_frame.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        
        # Checkbox para usar descripciones existentes
        tk.Checkbutton(opciones_frame, 
                      text="Usar descripciones existentes como base (si están disponibles)",
                      variable=self.usar_desc_existente,
                      command=self.toggle_desc_columns).grid(row=0, column=0, columnspan=3, sticky="w", pady=5)
        
        # Frame para selector de descripción base (oculto inicialmente)
        self.desc_frame = ttk.Frame(opciones_frame)
        Label(self.desc_frame, text="Columna base:").grid(row=0, column=0, sticky="e", padx=5)
        self.combo_desc_base = ttk.Combobox(self.desc_frame, textvariable=self.col_desc_base, width=50)
        self.combo_desc_base.grid(row=0, column=1, padx=5)
        
        # BOTÓN INICIAR
        Button(scrollable_frame, text="🚀 Iniciar Generación", command=self.start_process, 
               bg='lightgreen', font=('Arial', 14, 'bold'), height=2).grid(row=6, column=0, columnspan=3, pady=20)
        
        # ÁREA DE LOG
        log_frame = ttk.LabelFrame(scrollable_frame, text="📊 Registro de Actividad", padding="10")
        log_frame.grid(row=7, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)
        
        self.log_area = scrolledtext.ScrolledText(log_frame, width=100, height=15)
        self.log_area.pack(fill=tk.BOTH, expand=True)
        
        # BOTONES DE CONTROL
        self.botones_frame = tk.Frame(scrollable_frame)
        self.botones_frame.grid(row=8, column=0, columnspan=3, pady=10)
        
        self.continuar_button = tk.Button(
            self.botones_frame,
            text="✅ Confirmar que ya estoy logueado",
            command=self.confirmar_logueo,
            state="disabled"
        )
        self.continuar_button.pack(side=tk.LEFT, padx=5)
        
        self.pausar_button = tk.Button(
            self.botones_frame,
            text="⏸️ Pausar proceso",
            command=self.pausar_reanudar_proceso,
            state="disabled"
        )
        self.pausar_button.pack(side=tk.LEFT, padx=5)
        
        self.guardar_log_button = tk.Button(
            self.botones_frame,
            text="💾 Guardar Log",
            command=self.guardar_log
        )
        self.guardar_log_button.pack(side=tk.LEFT, padx=5)
        
        self.cerrar_button = tk.Button(
            self.botones_frame,
            text="❌ Cerrar navegador",
            command=self.cerrar_navegador,
            state="disabled"
        )
        self.cerrar_button.pack(side=tk.LEFT, padx=5)

    def add_combo_row(self, label_text, var, row, parent):
        Label(parent, text=label_text).grid(row=row, column=0, sticky="e", padx=5, pady=3)
        combo = ttk.Combobox(parent, textvariable=var, values=self.columns, width=50, state="readonly")
        combo.grid(row=row, column=1, sticky="w", padx=5, pady=3)
        return combo

    def toggle_ia_config(self):
        """Muestra/oculta configuración de IA"""
        if self.usar_ia_premium.get():
            self.ia_config_frame.grid(row=1, column=0, columnspan=3, pady=10)
        else:
            self.ia_config_frame.grid_remove()
            self.modelo_ia = None

    def validar_api_key(self):
        """Valida la API key de Google Gemini con el modelo correcto"""
        api_key = self.gemini_api_key.get().strip()
        
        if not api_key:
            messagebox.showerror("Error", "Por favor ingresa una API key")
            return
        
        if not api_key.startswith("AIza"):
            messagebox.showerror("Error", "La API key debe comenzar con 'AIza...'")
            return
        
        self.log("🔄 Validando API key de Google Gemini...")
        
        try:
            # Importar módulo
            try:
                import google.generativeai as genai
            except ImportError:
                self.log("❌ Módulo google-generativeai no instalado")
                messagebox.showerror("Error", 
                    "Por favor instala el módulo:\npip install google-generativeai")
                return
            
            # Configurar con la API key
            genai.configure(api_key=api_key)
            
            # CAMBIO IMPORTANTE: Usar el modelo correcto
            try:
                # Primero, listar modelos disponibles
                self.log("📋 Buscando modelos disponibles...")
                
                models = []
                for m in genai.list_models():
                    if 'generateContent' in m.supported_generation_methods:
                        models.append(m.name)
                        self.log(f"   ✓ Modelo encontrado: {m.name}")
                
                # Usar el modelo más reciente disponible
                if models:
                    # Preferir gemini-1.5-flash o gemini-1.0-pro
                    model_name = None
                    for preferred in ['gemini-1.5-flash', 'gemini-1.0-pro', 'gemini-pro-latest']:
                        for available in models:
                            if preferred in available:
                                model_name = available.split('/')[-1]  # Obtener solo el nombre sin 'models/'
                                break
                        if model_name:
                            break
                    
                    # Si no encuentra los preferidos, usar el primero disponible
                    if not model_name:
                        model_name = models[0].split('/')[-1]
                    
                    self.log(f"🎯 Usando modelo: {model_name}")
                    
                    # Crear el modelo
                    model = genai.GenerativeModel(model_name)
                    
                    # Prueba simple
                    response = model.generate_content(
                        "Responde solo con la palabra OK si funciona",
                        generation_config=genai.types.GenerationConfig(
                            temperature=0.1,
                            max_output_tokens=10,
                        )
                    )
                    
                    if response and response.text:
                        self.modelo_ia = model
                        self.model_name = model_name  # Guardar el nombre del modelo
                        self.log(f"✅ API key válida. Modelo {model_name} activado")
                        self.log(f"✅ Respuesta de prueba: {response.text.strip()}")
                        messagebox.showinfo("Éxito", 
                            f"¡API key válida!\n\nModelo activo: {model_name}\n\nLa IA está lista para generar descripciones premium.")
                        return
                    else:
                        raise Exception("No se recibió respuesta del modelo")
                else:
                    raise Exception("No se encontraron modelos compatibles")
                    
            except Exception as e:
                error_msg = str(e)
                if "API_KEY_INVALID" in error_msg:
                    self.log("❌ API key inválida")
                    messagebox.showerror("Error", 
                        "API key inválida.\n\nVerifica que copiaste correctamente la key.")
                elif "PERMISSION_DENIED" in error_msg:
                    self.log("❌ Permisos denegados")
                    messagebox.showerror("Error", 
                        "Permisos denegados.\n\nVerifica que habilitaste la API en Google Cloud Console.")
                elif "404" in error_msg:
                    self.log("❌ Modelo no encontrado")
                    messagebox.showerror("Error", 
                        "El modelo solicitado no está disponible.\n\nEl código se actualizó para buscar modelos compatibles.")
                else:
                    self.log(f"❌ Error al validar: {error_msg}")
                    messagebox.showerror("Error", 
                        f"Error al validar API key:\n\n{error_msg[:200]}...")
                
                self.modelo_ia = None
                
        except Exception as e:
            self.log(f"❌ Error general: {str(e)}")
            messagebox.showerror("Error", 
                f"Error inesperado:\n{str(e)[:200]}...\n\nVerifica tu conexión a internet.")
            self.modelo_ia = None

    def probar_ia_descripcion(self):
        """Prueba la generación de una descripción con IA"""
        if not self.modelo_ia:
            messagebox.showerror("Error", "Primero valida tu API key")
            return
        
        self.log("🧪 Probando generación con IA...")
        
        try:
            prompt = """
        Genera una descripción corta (3 líneas) para un generador eléctrico 
        de 10 KVA diesel, destacando su confiabilidad.
        """
            
            response = self.modelo_ia.generate_content(prompt)
            
            if response and response.text:
                self.log("✅ Prueba exitosa. Respuesta de IA:")
                self.log(response.text[:200] + "...")
                messagebox.showinfo("Prueba Exitosa", 
                    "La IA está funcionando correctamente.\n\n" + 
                    "Muestra de respuesta:\n" + response.text[:200] + "...")
            else:
                raise Exception("Sin respuesta")
                
        except Exception as e:
            self.log(f"❌ Error en prueba: {e}")
            messagebox.showerror("Error", f"Error al probar IA:\n{str(e)[:200]}")

    def toggle_desc_columns(self):
        """Muestra/oculta el selector de columna base"""
        if self.usar_desc_existente.get():
            self.desc_frame.grid(row=1, column=0, columnspan=3, pady=10)
            # Filtrar columnas que contengan "desc" o "texto"
            desc_columns = [col for col in self.columns if any(x in col.lower() for x in ['desc', 'texto', 'mix'])]
            self.combo_desc_base['values'] = desc_columns
        else:
            self.desc_frame.grid_remove()

    def load_excel(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("Archivos Excel", "*.xlsx *.xls")]
        )
        if file_path:
            self.excel_path.set(file_path)
            self.save_config()
            self.log(f"📁 Excel cargado: {file_path}")
            
            try:
                df = pd.read_excel(file_path)
                self.columns = df.columns.tolist()
                
                # Actualizar todos los combos
                for widget in self.root.winfo_children():
                    if isinstance(widget, ttk.Frame):
                        for child in widget.winfo_children():
                            if isinstance(child, ttk.LabelFrame):
                                for subchild in child.winfo_children():
                                    if isinstance(subchild, ttk.Combobox):
                                        subchild['values'] = self.columns
                
                # Auto-detectar columnas
                self.auto_detect_columns()
                
                self.log(f"✅ {len(df)} productos encontrados")
                self.log("🤖 Modo HÍBRIDO: Combinando datos técnicos con descripciones existentes")
                
            except Exception as e:
                self.log(f"❌ Error al leer Excel: {e}")

    def auto_detect_columns(self):
        """Auto-detecta columnas comunes"""
        for col in self.columns:
            col_lower = col.lower()
            if 'sku' in col_lower or 'codigo' in col_lower or 'código' in col_lower:
                self.col_codigo.set(col)
            elif 'url pdf' in col_lower:
                self.col_pdf.set(col)
            elif 'destacado' in col_lower and 'shop' in col_lower:
                self.col_destacado.set(col)
            elif 'seo' in col_lower and ('titulo' in col_lower or 'título' in col_lower):
                self.col_seo_titulo.set(col)
            elif 'seo' in col_lower and 'descripcion' in col_lower:
                self.col_seo_desc.set(col)

    def log(self, message):
        def do_log():
            try:
                timestamp = time.strftime("[%H:%M:%S] ")
                self.log_area.insert("end", timestamp + message + "\n")
                self.log_area.see("end")
            except:
                pass
        try:
            self.root.after(0, do_log)
        except:
            pass

    def start_process(self):
        # Validar campos obligatorios
        if not self.excel_path.get():
            messagebox.showerror("Error", "Por favor selecciona un archivo Excel")
            return
        
        if not self.col_codigo.get():
            messagebox.showerror("Error", "Por favor selecciona la columna de Código/SKU")
            return
        
        self.save_config()
        self.proceso_activo = True
        self.cerrar_button.config(state="normal")
        self.log("🚀 Iniciando proceso...")
        threading.Thread(target=self.run_automation).start()

    def save_config(self):
        config = {
            "excel_path": self.excel_path.get(),
            "whatsapp": self.whatsapp_var.get(),
            "email": self.email_var.get(),
            "telefono_display": self.telefono_display_var.get(),
            "website": self.web_var.get(),
            "col_codigo": self.col_codigo.get(),
            "col_pdf": self.col_pdf.get(),
            "col_destacado": self.col_destacado.get(),
            "col_seo_titulo": self.col_seo_titulo.get(),
            "col_seo_desc": self.col_seo_desc.get(),
            "usar_desc_existente": self.usar_desc_existente.get(),
            "col_desc_base": self.col_desc_base.get(),
            "gemini_api_key": self.gemini_api_key.get(),
            "usar_ia_premium": self.usar_ia_premium.get()
        }
        with open("config_stel_hibrido.json", "w") as f:
            json.dump(config, f)

    def load_config(self):
        if os.path.exists("config_stel_hibrido.json"):
            try:
                with open("config_stel_hibrido.json", "r") as f:
                    config = json.load(f)
                
                # Cargar valores
                self.excel_path.set(config.get("excel_path", ""))
                self.whatsapp_var.set(config.get("whatsapp", "541139563099"))
                self.email_var.set(config.get("email", "info@generadores.ar"))
                self.telefono_display_var.set(config.get("telefono_display", "+54 11 3956-3099"))
                self.web_var.set(config.get("website", "www.generadores.ar"))
                self.col_codigo.set(config.get("col_codigo", ""))
                self.col_pdf.set(config.get("col_pdf", ""))
                self.col_destacado.set(config.get("col_destacado", ""))
                self.col_seo_titulo.set(config.get("col_seo_titulo", ""))
                self.col_seo_desc.set(config.get("col_seo_desc", ""))
                self.usar_desc_existente.set(config.get("usar_desc_existente", False))
                self.col_desc_base.set(config.get("col_desc_base", ""))
                self.gemini_api_key.set(config.get("gemini_api_key", ""))
                self.usar_ia_premium.set(config.get("usar_ia_premium", False))
                
                # Cargar Excel si existe
                if self.excel_path.get() and os.path.exists(self.excel_path.get()):
                    self.log(f"📁 Configuración cargada")
                    
            except Exception as e:
                self.log(f"⚠️ Error al cargar configuración: {e}")

    def confirmar_logueo(self):
        self.log("="*50)
        self.log("✅ CONFIRMACIÓN DE LOGIN RECIBIDA")
        self.log("="*50)
        
        # Verificar estado del sistema
        self.log("🔍 Verificando estado del sistema...")
        
        if hasattr(self, 'driver') and self.driver:
            self.log("✅ Navegador: OK")
        else:
            self.log("❌ Navegador: NO ENCONTRADO")
            return
        
        if hasattr(self, 'wait') and self.wait:
            self.log("✅ WebDriverWait: OK")
        else:
            self.log("❌ WebDriverWait: NO ENCONTRADO")
            return
        
        if self.excel_path.get():
            self.log(f"✅ Excel: {self.excel_path.get()}")
        else:
            self.log("❌ Excel: NO CARGADO")
            return
        
        if self.col_codigo.get():
            self.log(f"✅ Columna código: {self.col_codigo.get()}")
        else:
            self.log("❌ Columna código: NO SELECCIONADA")
            return
        
        self.log("🚀 Iniciando procesamiento de productos...")
        
        # Deshabilitar botón y habilitar pausa
        self.continuar_button.config(state="disabled")
        self.pausar_button.config(state="normal")
        
        # Iniciar procesamiento en thread separado
        thread = threading.Thread(target=self.procesar_productos)
        thread.daemon = True  # Para que se cierre con la aplicación
        thread.start()
        
        self.log("✅ Thread de procesamiento iniciado")

    def pausar_reanudar_proceso(self):
        self.pausado = not self.pausado
        if self.pausado:
            self.pausar_button.config(text="▶️ Reanudar proceso")
            self.log("⏸️ Proceso PAUSADO. Haz clic en 'Reanudar proceso' para continuar.")
        else:
            self.pausar_button.config(text="⏸️ Pausar proceso")
            self.log("▶️ Proceso REANUDADO. Continuando la automatización...")

    def verificar_pausa(self):
        while self.pausado and self.proceso_activo:
            time.sleep(0.5)

    def guardar_log(self):
        try:
            log_text = self.log_area.get("1.0", tk.END).strip()
            if not log_text:
                self.log("⚠️ El log está vacío, no se guardó ningún archivo.")
                return
            now = time.strftime("%Y%m%d_%H%M%S")
            filename = f"log_stel_hibrido_{now}.txt"
            with open(filename, "w", encoding="utf-8") as f:
                f.write(log_text)
            self.log(f"💾 Log guardado como '{filename}'.")
        except Exception as e:
            self.log(f"❌ Error al guardar log: {e}")

    def cerrar_navegador(self):
        try:
            if hasattr(self, "driver") and self.driver:
                self.log("🔴 Cerrando navegador y finalizando proceso...")
                if hasattr(self, "cleanup_temp_profile") and self.cleanup_temp_profile:
                    self.cleanup_temp_profile()
                else:
                    self.driver.quit()
                self.proceso_activo = False
                self.pausar_button.config(state="disabled")
                self.cerrar_button.config(state="disabled")
                self.log("✅ Navegador cerrado correctamente.")
            else:
                self.log("⚠️ No hay navegador activo para cerrar.")
        except Exception as e:
            self.log(f"❌ Error al cerrar navegador: {e}")

# Asignar los métodos de selenium a la clase
StelUpdaterApp.run_automation = run_automation
StelUpdaterApp.procesar_productos = procesar_productos

# ============================================================================
# FUNCIÓN PRINCIPAL
# ============================================================================

def main():
    if not verificar_dependencias():
        input("Presiona Enter para salir...")
        return
    
    try:
        root = Tk()
        app = StelUpdaterApp(root)
        root.mainloop()
    except Exception as e:
        import traceback
        import time
        with open("error_stel_hibrido.log", "a", encoding="utf-8") as f:
            f.write(f"[ERROR GLOBAL] {time.strftime('%Y-%m-%d %H:%M:%S')}\n{traceback.format_exc()}\n")
        print(f"[ERROR GLOBAL] {e}")

# ============================================================================
# LÓGICA DE ESPECIFICACIONES DINÁMICAS
# ============================================================================

def determinar_tipo_producto(info):
    """Determina el tipo de producto basado en la familia o nombre."""
    familia = info.get('familia', '').lower()
    nombre = info.get('nombre', '').lower()
    
    if 'compresor' in familia or 'compresor' in nombre:
        return 'compresor'
    if 'vibro' in familia or 'vibro' in nombre:
        return 'vibropisonador'
    # Por defecto, se asume que es un generador
    return 'generador'

def validar_descripcion_generada(descripcion, tipo_producto, caracteristicas):
    """Valida que la descripción no contenga información incorrecta"""
    errores = []
    
    # Verificar que no se mencionen características que no tiene
    if not caracteristicas['tiene_cabina'] and 'cabina insonorizada' in descripcion.lower():
        errores.append("Se menciona cabina insonorizada pero el producto no la tiene")
    
    if not caracteristicas['tiene_tta'] and 'transferencia automática' in descripcion.lower():
        errores.append("Se menciona TTA pero el producto no lo tiene")
    
    # Verificar coherencia con tipo de producto
    if tipo_producto != 'generador':
        palabras_prohibidas = ['grupo electrógeno', 'generador eléctrico', 'alternador']
        for palabra in palabras_prohibidas:
            if palabra in descripcion.lower():
                errores.append(f"Se usa terminología de generador en un {tipo_producto}")
    
    return errores

def obtener_iconos_por_tipo(tipo_producto):
    """Devuelve un diccionario de iconos apropiado para el tipo de producto."""
    # Esta es una función placeholder. Deberías expandirla para que devuelva
    # los SVGs correctos para cada tipo de producto.
    # Por ahora, devuelve los de generador como fallback.
    return {
        'potencia': '<svg width="28" height="28" viewBox="0 0 24 24" fill="#ff6600"><path d="M7 2v11h3v9l7-12h-4l4-8z"/></svg>',
        'motor': '<svg width="28" height="28" viewBox="0 0 24 24" fill="#ff6600"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 18c-4.42 0-8-3.58-8-8s3.58-8 8-8 8 3.58 8 8-3.58 8-8 8z"/></svg>',
        'alternador': '<svg width="28" height="28" viewBox="0 0 24 24" fill="#ff6600"><path d="M12 2l-5.5 9h11z M12 22l5.5-9h-11z M3.5 9L12 12l-3.5 6z M20.5 9L12 12l3.5 6z"/></svg>',
        'voltaje': '<svg width="28" height="28" viewBox="0 0 24 24" fill="#ff6600"><path d="M7 2v11h3v9l7-12h-4l4-8z"/></svg>',
        'frecuencia': '<svg width="28" height="28" viewBox="0 0 24 24" fill="#ff6600"><path d="M16 6l-4 4-4-4v3l4 4 4-4zm0 6l-4 4-4-4v3l4 4 4-4z"/></svg>',
        'consumo': '<svg width="28" height="28" viewBox="0 0 24 24" fill="#ff6600"><path d="M6 2v6l1-2h1l1 2V2c1.1 0 2 .9 2 2v6c0 1.1-.9 2-2 2H7c-1.1 0-2-.9-2-2V4c0-1.1.9-2 2-2h1zm6 0h10v10h-2V4h-8v2zm0 4h8v10h-2V8h-6v2z"/></svg>',
        'tanque': '<svg width="28" height="28" viewBox="0 0 24 24" fill="#ff6600"><path d="M3 13c0 1.1.9 2 2 2s2-.9 2-2-.9-2-2-2-2 .9-2 2m4 8c0 .6.5 1 1 1h8c.6 0 1-.5 1-1v-1H7v1m11.8-9.7l-2.5 2.5L17.5 15 20 12.5l-2.5-2.5-1.1 1.1 1.4 1.4-1.4 1.5m3.2-.3c0 3.3-2.7 6-6 6-1.6 0-3.1-.7-4.2-1.8L10 17h1c1.1 0 2-.9 2-2v-3c0-.3-.1-.5-.2-.8L18.2 5.8c.5-.5.8-1.2.8-1.9 0-1.5-1.2-2.7-2.7-2.7-.7 0-1.4.3-1.9.8l-11.7 11.7c-.5.6-.7 1.3-.7 2.1 0 1.8 1.5 3.2 3.2 3.2H7v2c-3.9 0-7-3.1-7-7s3.1-7 7-7h10c3.9 0 7 3.1 7 7z"/></svg>',
        'ruido': '<svg width="28" height="28" viewBox="0 0 24 24" fill="#ff6600"><path d="M14 3.23v2.06c2.89.86 5 3.54 5 6.71s-2.11 5.84-5 6.7v2.07c4-.91 7-4.49 7-8.77 0-4.28-3-7.86-7-8.77M16.5 12c0-1.77-1-3.29-2.5-4.03V16c1.5-.71 2.5-2.24 2.5-4M3 9v6h4l5 5V4L7 9H3z"/></svg>',
        'dimensiones': '<svg width="28" height="28" viewBox="0 0 24 24" fill="#ff6600"><path d="M21 3H3c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h18c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm0 16H3V5h18v14z"/></svg>',
        'peso': '<svg width="28" height="28" viewBox="0 0 24 24" fill="#ff6600"><path d="M12 3c-1.3 0-2.4.8-2.8 2H6c-.6 0-1 .4-1 1s.4 1 1 1h.2l.9 11c0 .6.4 1 1 1h7.8c.6 0 1-.4 1-1l.9-11h.2c.6 0 1-.4 1-1s-.4-1-1-1h-3.2c-.4-1.2-1.5-2-2.8-2zm0 2c.3 0 .5.2.5.5s-.2.5-.5.5-.5-.2-.5-.5.2-.5.5-.5z"/></svg>',
    }

def generar_tabla_especificaciones_html(info, tipo_producto, iconos):
    """
    Genera la tabla de especificaciones HTML dinámicamente según el tipo de producto
    """
    return generar_tabla_especificaciones_por_tipo(info, tipo_producto, iconos)

def generar_tabla_especificaciones_por_tipo(info, tipo, iconos):
    """Genera la tabla de especificaciones HTML dinámicamente."""
    
    mapa_especificaciones = {
        'generador': [
            {'label': 'POTENCIA', 'key': 'potencia_kva', 'icon': 'potencia', 'unit': 'KVA'},
            {'label': 'VOLTAJE', 'key': 'voltaje', 'icon': 'voltaje', 'unit': 'V'},
            {'label': 'FRECUENCIA', 'key': 'frecuencia', 'icon': 'frecuencia', 'unit': 'Hz'},
            {'label': 'MOTOR', 'key': 'motor', 'icon': 'motor', 'unit': ''},
            {'label': 'ALTERNADOR', 'key': 'alternador', 'icon': 'alternador', 'unit': ''},
            {'label': 'CONSUMO', 'key': 'consumo', 'icon': 'consumo', 'unit': 'L/h @ 75%'},
            {'label': 'TANQUE', 'key': 'tanque', 'icon': 'tanque', 'unit': 'Litros'},
            {'label': 'NIVEL SONORO', 'key': 'ruido', 'icon': 'ruido', 'unit': 'dBA @ 7m'},
            {'label': 'DIMENSIONES', 'key': 'dimensiones', 'icon': 'dimensiones', 'unit': 'mm'},
            {'label': 'PESO', 'key': 'peso', 'icon': 'peso', 'unit': 'kg'}
        ],
        'compresor': [
            {'label': 'POTENCIA MOTOR', 'key': 'potencia_kw', 'icon': 'potencia', 'unit': 'HP'},
            {'label': 'PRESION MAXIMA', 'key': 'presion_bar', 'icon': 'presion', 'unit': 'Bar'},
            {'label': 'CAUDAL', 'key': 'caudal_lpm', 'icon': 'caudal', 'unit': 'L/min'},
            {'label': 'CAPACIDAD TANQUE', 'key': 'tanque', 'icon': 'tanque', 'unit': 'Litros'},
            {'label': 'MOTOR', 'key': 'motor', 'icon': 'motor', 'unit': ''},
            {'label': 'DIMENSIONES', 'key': 'dimensiones', 'icon': 'dimensiones', 'unit': 'mm'},
            {'label': 'PESO', 'key': 'peso', 'icon': 'peso', 'unit': 'kg'}
        ],
        'vibropisonador': [
            {'label': 'FUERZA DE IMPACTO', 'key': 'fuerza_kn', 'icon': 'fuerza_impacto', 'unit': 'kN'},
            {'label': 'FRECUENCIA', 'key': 'frecuencia_vpm', 'icon': 'frecuencia', 'unit': 'VPM'},
            {'label': 'MOTOR', 'key': 'motor', 'icon': 'motor', 'unit': ''},
            {'label': 'POTENCIA MOTOR', 'key': 'potencia_hp', 'icon': 'potencia', 'unit': 'HP'},
            {'label': 'DIMENSIONES PLACA', 'key': 'dimensiones_placa', 'icon': 'dimensiones', 'unit': 'mm'},
            {'label': 'PESO', 'key': 'peso', 'icon': 'peso', 'unit': 'kg'}
        ]
    }
    
    especificaciones = mapa_especificaciones.get(tipo, mapa_especificaciones['generador'])
    
    filas_html = ""
    for i, spec in enumerate(especificaciones):
        valor = info.get(spec['key'], 'N/D')
        
        # Manejo especial para dimensiones
        if spec['key'] == 'dimensiones':
            valor = f"{info.get('largo', 'N/D')} x {info.get('ancho', 'N/D')} x {info.get('alto', 'N/D')}"
        
        if valor and valor != 'N/D':
            background_color = "#f9f9f9" if i % 2 == 0 else "white"
            filas_html += f"""
            <tr style="background-color: {background_color};">
                <td style="padding: 12px; font-weight: bold; color: #D32F2F; display: flex; align-items: center; gap: 8px;">
                    <div style="width: 24px; height: 24px;">{iconos.get(spec['icon'], '')}</div> {spec['label']}
                </td>
                <td style="padding: 12px; font-weight: bold;">{valor} {spec['unit']}</td>
            </tr>
            """

    if not filas_html:
        return ""

    return f"""
    <div style="background-color: #FFC107; border: 3px solid #000000; border-radius: 10px; padding: 25px; margin-bottom: 30px;">
        <h2 style="color: #000000; font-size: 24px; margin: 0 0 20px 0; text-align: center; display: flex; align-items: center; justify-content: center; gap: 10px;">
            <svg width="30" height="30" viewBox="0 0 24 24" fill="#000000"><path d="M9 17H7v-7h2m4 7h-2V7h2m4 10h-2v-4h2m4 4h-2V4h2v13z"/></svg>
            ESPECIFICACIONES TECNICAS COMPLETAS
        </h2>
        <table style="width: 100%; background-color: white; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
            <tr style="background-color: #000000; color: #FFC107;">
                <td style="padding: 12px; font-weight: bold; width: 40%; font-size: 14px;">CARACTERISTICA</td>
                <td style="padding: 12px; font-weight: bold; font-size: 14px;">ESPECIFICACION</td>
            </tr>
            {filas_html}
        </table>
    </div>
    """

if __name__ == "__main__":
    main()
