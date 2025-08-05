# -*- coding: utf-8 -*-
"""
Módulo de correcciones de compatibilidad para prevenir errores de tipos
"""

def safe_dict_access(data, key, default=None):
    """
    Acceso seguro a diccionarios que podrían ser strings u otros tipos
    """
    if isinstance(data, dict):
        return data.get(key, default)
    return default

def ensure_dict(data, default=None):
    """
    Asegura que el dato sea un diccionario
    """
    if isinstance(data, dict):
        return data
    if default is None:
        return {}
    return default

def safe_json_parse(json_str):
    """
    Parse seguro de JSON que maneja diferentes tipos de entrada
    """
    import json
    
    if isinstance(json_str, dict):
        return json_str
    
    if not isinstance(json_str, str):
        return {}
    
    try:
        # Intentar encontrar JSON en el string
        start = json_str.find('{')
        end = json_str.rfind('}') + 1
        
        if start != -1 and end > start:
            return json.loads(json_str[start:end])
    except:
        pass
    
    return {}

def ensure_caracteristicas_dict(caracteristicas):
    """
    Asegura que caracteristicas sea un diccionario válido
    """
    if isinstance(caracteristicas, str):
        # Si es un string, crear un diccionario básico
        return {
            'tipo_producto': 'equipo',
            'tipo_combustible': 'combustible',
            'es_portatil': False,
            'caracteristicas_principales': [],
            'badges_especiales': []
        }
    
    if not isinstance(caracteristicas, dict):
        return {
            'tipo_producto': 'equipo',
            'tipo_combustible': 'combustible',
            'es_portatil': False,
            'caracteristicas_principales': [],
            'badges_especiales': []
        }
    
    # Asegurar que tenga las claves mínimas
    defaults = {
        'tipo_producto': 'equipo',
        'tipo_combustible': 'combustible',
        'es_portatil': False,
        'caracteristicas_principales': [],
        'badges_especiales': []
    }
    
    for key, value in defaults.items():
        if key not in caracteristicas:
            caracteristicas[key] = value
    
    return caracteristicas

def safe_contenido_pdf_access(contenido_pdf):
    """
    Maneja el acceso seguro a contenido_pdf que puede ser string o dict
    """
    if isinstance(contenido_pdf, dict):
        return contenido_pdf.get('text', '')
    elif isinstance(contenido_pdf, str):
        return contenido_pdf
    else:
        return ''