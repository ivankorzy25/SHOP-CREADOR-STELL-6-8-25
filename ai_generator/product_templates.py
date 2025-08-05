# -*- coding: utf-8 -*-
"""
Módulo para definir plantillas HTML específicas para cada categoría de producto.
Versión 4.0 - Usa el generador premium restaurado que mantiene el diseño completo
"""
from .premium_generator_restored import generar_html_premium_completo
from .premium_generator_v2 import (
    ICONOS_SVG,
    procesar_producto_universal,
    generar_specs_table_inline,
    generar_mini_cards_adicionales,
    generar_badge_eficiencia,
    generar_cta_whatsapp,
    extraer_info_motor_limpia
)

def validar_parametros_entrada(info, marketing_content, caracteristicas, config):
    """Valida y asegura que todos los parámetros sean del tipo correcto"""
    # Asegurar que todos sean diccionarios
    if not isinstance(info, dict):
        info = {}
    if not isinstance(marketing_content, dict):
        marketing_content = {}
    if not isinstance(caracteristicas, dict):
        caracteristicas = {
            'tipo_producto': 'equipo',
            'tipo_combustible': 'combustible',
            'es_portatil': False,
            'caracteristicas_principales': [],
            'badges_especiales': []
        }
    if not isinstance(config, dict):
        config = {}
    
    return info, marketing_content, caracteristicas, config

def generar_html_universal(info, marketing_content, config):
    """
    Genera HTML para CUALQUIER producto usando el generador premium restaurado
    
    Args:
        info: Datos del producto
        marketing_content: Contenido de marketing de AI
        config: Configuración (whatsapp, email, etc)
    
    Returns:
        HTML completo del producto con diseño premium
    """
    # Usar el generador premium completo que mantiene todo el diseño
    return generar_html_premium_completo(info, marketing_content, config)

def generar_hero_section(titulo, subtitulo, caracteristicas):
    """Genera la sección hero con título y subtítulo"""
    # Color según tipo de producto
    tipo_producto = caracteristicas.get('tipo_producto', 'equipo')
    colores = {
        'generador': '#ff6600',
        'bomba': '#2196F3',
        'compresor': '#4CAF50',
        'motocultor': '#795548',
        'chipeadora': '#009688',
        'fumigadora': '#9C27B0',
        'soldadora': '#F44336',
        'default': '#ff6600'
    }
    color_principal = colores.get(tipo_producto, colores['default'])
    
    return f'''
    <div style="background: linear-gradient(135deg, {color_principal} 0%, {color_principal}dd 100%); 
                color: white; padding: 40px 20px; text-align: center;">
        <h1 style="margin: 0 0 10px 0; font-size: 32px; font-weight: bold;">
            {titulo}
        </h1>
        {f'<p style="margin: 0; font-size: 18px; opacity: 0.9;">{subtitulo}</p>' if subtitulo else ''}
    </div>
    '''

def generar_puntos_clave(marketing_content, caracteristicas):
    """Genera los puntos clave del producto"""
    html = '''
    <div style="background: white; padding: 30px 20px; margin: 20px auto; max-width: 1200px; 
                border-radius: 10px; box-shadow: 0 2px 5px rgba(0,0,0,0.1);">
        <div style="display: flex; flex-wrap: wrap; justify-content: space-around; gap: 20px;">
    '''
    
    # Obtener puntos clave del marketing
    for i in range(1, 4):
        texto = marketing_content.get(f'punto_clave_texto_{i}', '')
        icono = marketing_content.get(f'punto_clave_icono_{i}', 'info')
        
        if texto:
            icono_svg = ICONOS_SVG.get(icono, ICONOS_SVG['info'])
            html += f'''
            <div style="flex: 1; min-width: 250px; text-align: center;">
                <div style="margin-bottom: 10px;">{icono_svg}</div>
                <p style="margin: 0; color: #333; font-size: 16px;">{texto}</p>
            </div>
            '''
    
    html += '''
        </div>
    </div>
    '''
    
    return html

def generar_aplicaciones(marketing_content):
    """Genera la sección de aplicaciones"""
    aplicaciones = []
    
    # Recolectar aplicaciones del marketing
    for i in range(1, 6):
        texto = marketing_content.get(f'app_texto_{i}', '')
        icono = marketing_content.get(f'app_icono_{i}', 'check-circle')
        if texto:
            aplicaciones.append((texto, icono))
    
    if not aplicaciones:
        return ''
    
    html = '''
    <div style="background: #f8f9fa; padding: 40px 20px; margin: 20px 0;">
        <div style="max-width: 1200px; margin: 0 auto;">
            <h2 style="text-align: center; color: #333; margin-bottom: 30px;">
                Aplicaciones Principales
            </h2>
            <div style="display: flex; flex-wrap: wrap; gap: 20px; justify-content: center;">
    '''
    
    for texto, icono in aplicaciones:
        icono_svg = ICONOS_SVG.get(icono, ICONOS_SVG['check-circle'])
        html += f'''
        <div style="flex: 1; min-width: 200px; max-width: 300px; background: white; 
                    padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
            <div style="display: flex; align-items: center; gap: 10px;">
                <div style="color: #ff6600;">{icono_svg}</div>
                <p style="margin: 0; color: #333;">{texto}</p>
            </div>
        </div>
        '''
    
    html += '''
            </div>
        </div>
    </div>
    '''
    
    return html

def generar_footer(config):
    """Genera el footer con información de contacto"""
    return f'''
    <footer style="background: #333; color: white; padding: 30px 20px; text-align: center;">
        <div style="max-width: 800px; margin: 0 auto;">
            <p style="margin: 10px 0;">
                <strong>Teléfono:</strong> {config.get('telefono_display', '')}
            </p>
            <p style="margin: 10px 0;">
                <strong>Email:</strong> {config.get('email', '')}
            </p>
            <p style="margin: 10px 0;">
                <strong>WhatsApp:</strong> {config.get('whatsapp', '')}
            </p>
            {f'<p style="margin: 10px 0;"><strong>Web:</strong> {config.get("website", "")}</p>' if config.get('website') else ''}
        </div>
    </footer>
    '''

# ============================================================================
# FUNCIONES ESPECÍFICAS POR CATEGORÍA (usando el sistema universal)
# ============================================================================

def generar_html_generador(info, marketing_content, caracteristicas, config):
    """Genera HTML para generadores"""
    info, marketing_content, caracteristicas, config = validar_parametros_entrada(info, marketing_content, caracteristicas, config)
    return generar_html_universal(info, marketing_content, config)

def generar_html_bomba(info, marketing_content, caracteristicas, config):
    """Genera HTML para bombas"""
    info, marketing_content, caracteristicas, config = validar_parametros_entrada(info, marketing_content, caracteristicas, config)
    return generar_html_universal(info, marketing_content, config)

def generar_html_compresor(info, marketing_content, caracteristicas, config):
    """Genera HTML para compresores"""
    info, marketing_content, caracteristicas, config = validar_parametros_entrada(info, marketing_content, caracteristicas, config)
    return generar_html_universal(info, marketing_content, config)

def generar_html_motor(info, marketing_content, caracteristicas, config):
    """Genera HTML para motores"""
    return generar_html_universal(info, marketing_content, config)

def generar_html_motocultor(info, marketing_content, caracteristicas, config):
    """Genera HTML para motocultores"""
    return generar_html_universal(info, marketing_content, config)

def generar_html_chipeadora(info, marketing_content, caracteristicas, config):
    """Genera HTML para chipeadoras"""
    return generar_html_universal(info, marketing_content, config)

def generar_html_fumigadora(info, marketing_content, caracteristicas, config):
    """Genera HTML para fumigadoras"""
    return generar_html_universal(info, marketing_content, config)

def generar_html_cortadora(info, marketing_content, caracteristicas, config):
    """Genera HTML para cortadoras"""
    return generar_html_universal(info, marketing_content, config)

def generar_html_soldadora(info, marketing_content, caracteristicas, config):
    """Genera HTML para soldadoras"""
    return generar_html_universal(info, marketing_content, config)

def generar_html_herramientas_construccion(info, marketing_content, caracteristicas, config):
    """Genera HTML para herramientas de construcción"""
    return generar_html_universal(info, marketing_content, config)

def generar_html_hidrolavadora(info, marketing_content, caracteristicas, config):
    """Genera HTML para hidrolavadoras"""
    return generar_html_universal(info, marketing_content, config)

def generar_html_vibrador(info, marketing_content, caracteristicas, config):
    """Genera HTML para vibradores de concreto"""
    return generar_html_universal(info, marketing_content, config)

def generar_html_electrico(info, marketing_content, caracteristicas, config):
    """Genera HTML para equipos eléctricos"""
    return generar_html_universal(info, marketing_content, config)

def generar_html_default(info, marketing_content, caracteristicas, config):
    """Genera HTML por defecto para cualquier producto"""
    info, marketing_content, caracteristicas, config = validar_parametros_entrada(info, marketing_content, caracteristicas, config)
    return generar_html_universal(info, marketing_content, config)

# ============================================================================
# FUNCIÓN PRINCIPAL DE DESPACHO
# ============================================================================

def obtener_generador_html(categoria):
    """
    Retorna la función generadora de HTML según la categoría del producto.
    TODAS usan el sistema universal ahora.
    """
    generadores = {
        'generador': generar_html_generador,
        'bomba': generar_html_bomba,
        'compresor': generar_html_compresor,
        'motor': generar_html_motor,
        'motocultor': generar_html_motocultor,
        'chipeadora': generar_html_chipeadora,
        'fumigadora': generar_html_fumigadora,
        'cortadora': generar_html_cortadora,
        'soldadora': generar_html_soldadora,
        'herramientas_construccion': generar_html_herramientas_construccion,
        'hidrolavadora': generar_html_hidrolavadora,
        'vibrador': generar_html_vibrador,
        'electrico': generar_html_electrico,
    }
    
    return generadores.get(categoria, generar_html_default)

# ============================================================================
# FUNCIONES DE COMPATIBILIDAD
# ============================================================================

def enriquecer_marketing_generador_naftero(info, marketing_content, caracteristicas):
    """Función de compatibilidad - ya no es necesaria"""
    return marketing_content

def aplicar_mejoras_universales(info, caracteristicas=None, texto_pdf=''):
    """Función de compatibilidad"""
    from .premium_generator_v2 import procesar_producto_universal
    datos_limpios, nuevas_caracteristicas, eficiencia = procesar_producto_universal(info)
    
    if caracteristicas:
        nuevas_caracteristicas.update(caracteristicas)
        
    return datos_limpios, nuevas_caracteristicas

# ============================================================================
# REGISTRO DE PLANTILLAS PARA COMPATIBILIDAD
# ============================================================================

TEMPLATE_REGISTRY = {
    'generador': generar_html_generador,
    'bomba': generar_html_bomba,
    'compresor': generar_html_compresor,
    'motor': generar_html_motor,
    'motocultor': generar_html_motocultor,
    'chipeadora': generar_html_chipeadora,
    'fumigadora': generar_html_fumigadora,
    'cortadora': generar_html_cortadora,
    'soldadora': generar_html_soldadora,
    'herramientas_construccion': generar_html_herramientas_construccion,
    'hidrolavadora': generar_html_hidrolavadora,
    'vibrador': generar_html_vibrador,
    'electrico': generar_html_electrico,
    'default': generar_html_default
}