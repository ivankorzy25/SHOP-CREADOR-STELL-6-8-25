# -*- coding: utf-8 -*-
"""
Módulo para definir plantillas HTML específicas para cada categoría de producto.
"""
from .premium_generator_v2 import (
    ICONOS_SVG,
    generar_hero_section_inline,
    generar_specs_table_inline,
    generar_benefits_section_inline,
    generar_cta_section_inline,
    generar_contact_footer_inline,
    generar_css_hover_effects
)

def generar_html_generador(info, marketing_content, caracteristicas, config):
    """
    Genera el HTML completo para la categoría 'generador'.
    Esta es la plantilla principal y más detallada.
    """
    # Reutilizar la lógica de `generar_info_cards_inline_mejorado` de premium_generator_v2
    from .premium_generator_v2 import generar_info_cards_inline_mejorado
    
    titulo = marketing_content.get('titulo_h1', info.get('nombre', 'Producto'))
    subtitulo = marketing_content.get('subtitulo_p', 'Solución energética de última generación')

    html_completo = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{titulo} - Vista Previa</title>
    {generar_css_hover_effects()}
</head>
<body style="margin: 0; padding: 0; background: #f5f5f5;">
    <div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Arial, sans-serif; max-width: 1200px; margin: 0 auto; background: #ffffff; color: #333333;">
        
        {generar_hero_section_inline(titulo, subtitulo)}
        
        {generar_info_cards_inline_mejorado(info, caracteristicas)}
        
        {generar_specs_table_inline(info)}
        
        {generar_content_sections_inline(info, marketing_content)}
        
        {generar_benefits_section_inline()}
        
        {generar_cta_section_inline(info, config)}
        
        {generar_contact_footer_inline(config)}
        
    </div>
</body>
</html>"""
    return html_completo

def generar_html_compresor(info, marketing_content, caracteristicas, config):
    """
    Genera el HTML completo para la categoría 'compresor'.
    (Plantilla de ejemplo, se puede expandir)
    """
    titulo = marketing_content.get('titulo_h1', info.get('nombre', 'Compresor'))
    subtitulo = marketing_content.get('subtitulo_p', 'Potencia y eficiencia para tus herramientas')

    # Crear una versión simplificada de las tarjetas de info para compresores
    info_cards = f"""
    <div style="padding: 30px; display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px;">
        <div class="card-hover" style="background: #f8f9fa; border-radius: 12px; padding: 25px; border-left: 4px solid #17a2b8;">
            <p>Capacidad Tanque</p>
            <p style="font-size: 24px; font-weight: 700;">{info.get('capacidad_tanque_litros', 'N/D')} L</p>
        </div>
        <div class="card-hover" style="background: #f8f9fa; border-radius: 12px; padding: 25px; border-left: 4px solid #17a2b8;">
            <p>Presión Máxima</p>
            <p style="font-size: 24px; font-weight: 700;">{info.get('presion_bar', 'N/D')} BAR</p>
        </div>
    </div>
    """

    html_completo = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>{titulo}</title>
    {generar_css_hover_effects()}
</head>
<body>
    <div style="font-family: sans-serif; max-width: 1200px; margin: auto;">
        {generar_hero_section_inline(titulo, subtitulo)}
        {info_cards}
        {generar_specs_table_inline(info)}
        {generar_benefits_section_inline()}
        {generar_cta_section_inline(info, config)}
        {generar_contact_footer_inline(config)}
    </div>
</body>
</html>"""
    return html_completo

def generar_html_default(info, marketing_content, caracteristicas, config):
    """
    Genera una plantilla HTML genérica para categorías no especificadas.
    """
    titulo = marketing_content.get('titulo_h1', info.get('nombre', 'Producto'))
    subtitulo = marketing_content.get('subtitulo_p', 'Descripción del producto')
    
    html_completo = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>{titulo}</title>
    {generar_css_hover_effects()}
</head>
<body>
    <div style="font-family: sans-serif; max-width: 1200px; margin: auto;">
        {generar_hero_section_inline(titulo, subtitulo)}
        {generar_specs_table_inline(info)}
        {generar_benefits_section_inline()}
        {generar_cta_section_inline(info, config)}
        {generar_contact_footer_inline(config)}
    </div>
</body>
</html>"""
    return html_completo

def generar_html_hidrolavadora(info, marketing_content, caracteristicas, config):
    """
    Genera el HTML completo para la categoría 'hidrolavadora'.
    """
    titulo = marketing_content.get('titulo_h1', info.get('nombre', 'Hidrolavadora'))
    subtitulo = marketing_content.get('subtitulo_p', 'Limpieza a alta presión para resultados profesionales')

    # Info Cards específicas para hidrolavadoras
    info_cards = f"""
    <div style="padding: 30px; display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px;">
        <div class="card-hover" style="background: #f8f9fa; border-radius: 12px; padding: 25px; border-left: 4px solid #007bff;">
            <p>Presión Máxima</p>
            <p style="font-size: 24px; font-weight: 700;">{info.get('presion_bar', 'N/D')} BAR</p>
        </div>
        <div class="card-hover" style="background: #f8f9fa; border-radius: 12px; padding: 25px; border-left: 4px solid #17a2b8;">
            <p>Caudal</p>
            <p style="font-size: 24px; font-weight: 700;">{info.get('caudal_lts_min', 'N/D')} L/min</p>
        </div>
        <div class="card-hover" style="background: #f8f9fa; border-radius: 12px; padding: 25px; border-left: 4px solid #ff6600;">
            <p>Motor</p>
            <p style="font-size: 24px; font-weight: 700;">{info.get('motor', 'N/D')}</p>
        </div>
    </div>
    """

    html_completo = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>{titulo}</title>
    {generar_css_hover_effects()}
</head>
<body>
    <div style="font-family: sans-serif; max-width: 1200px; margin: auto;">
        {generar_hero_section_inline(titulo, subtitulo)}
        {info_cards}
        {generar_specs_table_inline(info)}
        {generar_content_sections_inline(info, marketing_content)}
        {generar_benefits_section_inline()}
        {generar_cta_section_inline(info, config)}
        {generar_contact_footer_inline(config)}
    </div>
</body>
</html>"""
    return html_completo

def generar_html_motobomba(info, marketing_content, caracteristicas, config):
    """
    Genera el HTML completo para la categoría 'motobomba'.
    """
    titulo = marketing_content.get('titulo_h1', info.get('nombre', 'Motobomba'))
    subtitulo = marketing_content.get('subtitulo_p', 'Soluciones de bombeo para cada necesidad')

    info_cards = f"""
    <div style="padding: 30px; display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px;">
        <div class="card-hover" style="background: #f8f9fa; border-radius: 12px; padding: 25px; border-left: 4px solid #17a2b8;">
            <p>Caudal Máximo</p>
            <p style="font-size: 24px; font-weight: 700;">{info.get('caudal_lph', 'N/D')} L/h</p>
        </div>
        <div class="card-hover" style="background: #f8f9fa; border-radius: 12px; padding: 25px; border-left: 4px solid #ff6600;">
            <p>Motor</p>
            <p style="font-size: 24px; font-weight: 700;">{info.get('motor', 'N/D')}</p>
        </div>
    </div>
    """

    html_completo = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>{titulo}</title>
    {generar_css_hover_effects()}
</head>
<body>
    <div style="font-family: sans-serif; max-width: 1200px; margin: auto;">
        {generar_hero_section_inline(titulo, subtitulo)}
        {info_cards}
        {generar_specs_table_inline(info)}
        {generar_content_sections_inline(info, marketing_content)}
        {generar_benefits_section_inline()}
        {generar_cta_section_inline(info, config)}
        {generar_contact_footer_inline(config)}
    </div>
</body>
</html>"""
    return html_completo

def generar_html_motocultivador(info, marketing_content, caracteristicas, config):
    """Genera HTML para motocultivadores."""
    titulo = marketing_content.get('titulo_h1', info.get('nombre', 'Motocultivador'))
    subtitulo = marketing_content.get('subtitulo_p', 'Potencia y eficiencia para preparar la tierra')

    info_cards = f"""
    <div style="padding: 30px; display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px;">
        <div class="card-hover" style="background: #f8f9fa; border-radius: 12px; padding: 25px; border-left: 4px solid #8bc34a;">
            <p>Ancho de Labranza</p>
            <p style="font-size: 24px; font-weight: 700;">{info.get('ancho_labranza_cm', 'N/D')} cm</p>
        </div>
        <div class="card-hover" style="background: #f8f9fa; border-radius: 12px; padding: 25px; border-left: 4px solid #ff6600;">
            <p>Motor</p>
            <p style="font-size: 24px; font-weight: 700;">{info.get('potencia_motor_hp', 'N/D')} HP</p>
        </div>
        <div class="card-hover" style="background: #f8f9fa; border-radius: 12px; padding: 25px; border-left: 4px solid #607d8b;">
            <p>Marchas</p>
            <p style="font-size: 20px; font-weight: 700;">{info.get('marchas_adelante_atras', 'N/D')}</p>
        </div>
    </div>
    """

    return generar_html_con_estructura_base(titulo, subtitulo, info_cards, info, marketing_content, config)

def generar_html_atomizador(info, marketing_content, caracteristicas, config):
    """Genera HTML para atomizadores/fumigadores."""
    titulo = marketing_content.get('titulo_h1', info.get('nombre', 'Atomizador'))
    subtitulo = marketing_content.get('subtitulo_p', 'Fumigación eficiente y profesional')

    info_cards = f"""
    <div style="padding: 30px; display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px;">
        <div class="card-hover" style="background: #f8f9fa; border-radius: 12px; padding: 25px; border-left: 4px solid #4caf50;">
            <p>Capacidad Tanque</p>
            <p style="font-size: 24px; font-weight: 700;">{info.get('capacidad_tanque_l', 'N/D')} L</p>
        </div>
        <div class="card-hover" style="background: #f8f9fa; border-radius: 12px; padding: 25px; border-left: 4px solid #ff6600;">
            <p>Motor</p>
            <p style="font-size: 20px; font-weight: 700;">{info.get('cilindrada_cc', 'N/D')} cc</p>
        </div>
        <div class="card-hover" style="background: #f8f9fa; border-radius: 12px; padding: 25px; border-left: 4px solid #2196f3;">
            <p>Alcance</p>
            <p style="font-size: 20px; font-weight: 700;">{info.get('alcance_pulverizacion', 'Amplio')}</p>
        </div>
    </div>
    """

    return generar_html_con_estructura_base(titulo, subtitulo, info_cards, info, marketing_content, config)

def generar_html_chipeadora(info, marketing_content, caracteristicas, config):
    """Genera HTML para chipeadoras."""
    titulo = marketing_content.get('titulo_h1', info.get('nombre', 'Chipeadora'))
    subtitulo = marketing_content.get('subtitulo_p', 'Tritura ramas y residuos eficientemente')

    info_cards = f"""
    <div style="padding: 30px; display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px;">
        <div class="card-hover" style="background: #f8f9fa; border-radius: 12px; padding: 25px; border-left: 4px solid #795548;">
            <p>Diámetro Máximo</p>
            <p style="font-size: 24px; font-weight: 700;">{info.get('diametro_max_rama_cm', 'N/D')} cm</p>
        </div>
        <div class="card-hover" style="background: #f8f9fa; border-radius: 12px; padding: 25px; border-left: 4px solid #ff6600;">
            <p>Motor</p>
            <p style="font-size: 24px; font-weight: 700;">{info.get('potencia_motor_hp', 'N/D')} HP</p>
        </div>
    </div>
    """

    return generar_html_con_estructura_base(titulo, subtitulo, info_cards, info, marketing_content, config)

def generar_html_motor_estacionario(info, marketing_content, caracteristicas, config):
    """Genera HTML para motores estacionarios."""
    titulo = marketing_content.get('titulo_h1', info.get('nombre', 'Motor Estacionario'))
    subtitulo = marketing_content.get('subtitulo_p', 'Potencia versátil para sus proyectos')

    info_cards = f"""
    <div style="padding: 30px; display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px;">
        <div class="card-hover" style="background: #f8f9fa; border-radius: 12px; padding: 25px; border-left: 4px solid #ff6600;">
            <p>Potencia</p>
            <p style="font-size: 24px; font-weight: 700;">{info.get('potencia_hp', 'N/D')} HP</p>
        </div>
        <div class="card-hover" style="background: #f8f9fa; border-radius: 12px; padding: 25px; border-left: 4px solid #17a2b8;">
            <p>Tipo de Arranque</p>
            <p style="font-size: 20px; font-weight: 700;">{info.get('tipo_arranque', 'Manual')}</p>
        </div>
        <div class="card-hover" style="background: #f8f9fa; border-radius: 12px; padding: 25px; border-left: 4px solid #28a745;">
            <p>Eje de Salida</p>
            <p style="font-size: 20px; font-weight: 700;">{info.get('eje_salida', 'Horizontal')}</p>
        </div>
    </div>
    """

    return generar_html_con_estructura_base(titulo, subtitulo, info_cards, info, marketing_content, config)

def generar_html_equipo_construccion(info, marketing_content, caracteristicas, config):
    """Genera HTML para equipos de construcción."""
    titulo = marketing_content.get('titulo_h1', info.get('nombre', 'Equipo de Construcción'))
    subtitulo = marketing_content.get('subtitulo_p', 'Herramienta profesional para obras')

    # Determinar tipo de equipo para mostrar specs relevantes
    tipo_equipo = info.get('tipo_equipo_construccion', '').lower()
    
    info_cards = ""
    if 'vibr' in tipo_equipo:
        info_cards = f"""
        <div style="padding: 30px; display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px;">
            <div class="card-hover" style="background: #f8f9fa; border-radius: 12px; padding: 25px; border-left: 4px solid #ff6600;">
                <p>Frecuencia</p>
                <p style="font-size: 24px; font-weight: 700;">{info.get('frecuencia_hz', 'N/D')} Hz</p>
            </div>
            <div class="card-hover" style="background: #f8f9fa; border-radius: 12px; padding: 25px; border-left: 4px solid #17a2b8;">
                <p>Fuerza de Impacto</p>
                <p style="font-size: 20px; font-weight: 700;">{info.get('fuerza_impacto_kg', 'N/D')} Kg</p>
            </div>
        </div>
        """
    elif 'cortadora' in tipo_equipo:
        info_cards = f"""
        <div style="padding: 30px; display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px;">
            <div class="card-hover" style="background: #f8f9fa; border-radius: 12px; padding: 25px; border-left: 4px solid #ff6600;">
                <p>Profundidad de Corte</p>
                <p style="font-size: 24px; font-weight: 700;">{info.get('profundidad_corte_mm', 'N/D')} mm</p>
            </div>
            <div class="card-hover" style="background: #f8f9fa; border-radius: 12px; padding: 25px; border-left: 4px solid #17a2b8;">
                <p>Diámetro de Disco</p>
                <p style="font-size: 20px; font-weight: 700;">{info.get('diametro_disco', 'N/D')}"</p>
            </div>
        </div>
        """

    return generar_html_con_estructura_base(titulo, subtitulo, info_cards, info, marketing_content, config)

def generar_html_generador_inverter(info, marketing_content, caracteristicas, config):
    """Genera HTML para generadores inverter."""
    titulo = marketing_content.get('titulo_h1', info.get('nombre', 'Generador Inverter'))
    subtitulo = marketing_content.get('subtitulo_p', 'Tecnología silenciosa y eficiente')

    info_cards = f"""
    <div style="padding: 30px; display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px;">
        <div class="card-hover" style="background: #f8f9fa; border-radius: 12px; padding: 25px; border-left: 4px solid #4caf50;">
            <p>Tecnología</p>
            <p style="font-size: 24px; font-weight: 700;">INVERTER</p>
        </div>
        <div class="card-hover" style="background: #f8f9fa; border-radius: 12px; padding: 25px; border-left: 4px solid #ff6600;">
            <p>Potencia Máxima</p>
            <p style="font-size: 24px; font-weight: 700;">{info.get('potencia_max_w', 'N/D')} W</p>
        </div>
        <div class="card-hover" style="background: #f8f9fa; border-radius: 12px; padding: 25px; border-left: 4px solid #2196f3;">
            <p>Nivel de Ruido</p>
            <p style="font-size: 20px; font-weight: 700;">Ultra Silencioso</p>
        </div>
    </div>
    """

    return generar_html_con_estructura_base(titulo, subtitulo, info_cards, info, marketing_content, config)

def generar_html_con_estructura_base(titulo, subtitulo, info_cards, info, marketing_content, config):
    """Función helper para generar HTML con estructura común."""
    html_completo = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>{titulo}</title>
    {generar_css_hover_effects()}
</head>
<body>
    <div style="font-family: sans-serif; max-width: 1200px; margin: auto;">
        {generar_hero_section_inline(titulo, subtitulo)}
        {info_cards}
        {generar_specs_table_inline(info)}
        {generar_content_sections_inline(info, marketing_content)}
        {generar_benefits_section_inline()}
        {generar_cta_section_inline(info, config)}
        {generar_contact_footer_inline(config)}
    </div>
</body>
</html>"""
    return html_completo

# Mapeo de categorías a funciones de plantilla
TEMPLATE_REGISTRY = {
    'generador_cummins': generar_html_generador,
    'generador': generar_html_generador,
    'compresor': generar_html_compresor,
    'hidrolavadora': generar_html_hidrolavadora,
    'motobomba': generar_html_motobomba,
    'motocultivador': generar_html_motocultivador,
    'atomizador': generar_html_atomizador,
    'chipeadora': generar_html_chipeadora,
    'cortadora_troncos': generar_html_default,
    'zanjadora': generar_html_default,
    'vibrador_concreto': generar_html_default,
    'implemento_agricola': generar_html_default,
    'motor_estacionario': generar_html_motor_estacionario,
    'equipo_construccion': generar_html_equipo_construccion,
    'generador_inverter': generar_html_generador_inverter,
    'transferencia_automatica': generar_html_default,
    'generador_gas_residencial': generar_html_generador,
    'generador_gas_industrial': generar_html_generador,
    'otro': generar_html_default,
    'default': generar_html_default
}

def generar_content_sections_inline(info, marketing_content):
    """Genera las secciones de contenido dinámicamente desde el JSON plano de la IA."""
    html = ""
    
    # 1. Puntos Clave (Highlights) con iconos dinámicos
    puntos_clave = []
    for i in range(1, 4):
        texto = marketing_content.get(f'punto_clave_texto_{i}')
        icono = marketing_content.get(f'punto_clave_icono_{i}')
        if texto and icono:
            puntos_clave.append({'texto': texto, 'icono': icono})

    if puntos_clave:
        items_html = ""
        for punto in puntos_clave:
            icono_svg = ICONOS_SVG.get(punto.get('icono', 'check'), ICONOS_SVG['check'])
            items_html += f'''
                <li style="padding: 8px 0; display: flex; align-items: start; gap: 10px;">
                    <div style="min-width: 20px; margin-top: 3px;">{icono_svg.replace('width="28"', 'width="20"').replace('height="28"', 'height="20"')}
                    <span>{punto.get('texto', '')}</span>
                </li>'''
        
        html += f'''
        <div class="content-section" style="margin: 30px; padding: 30px; background: #fff3e0; border-radius: 12px; box-shadow: 0 2px 10px rgba(0,0,0,0.05); border-left: 4px solid #ff6600;">
            <h3 style="color: #D32F2F; font-size: 24px; margin: 0 0 15px 0; font-weight: 700;">PUNTOS CLAVE</h3>
            <ul style="list-style: none; padding: 0; margin: 0; font-size: 16px; line-height: 1.8; color: #555;">
                {items_html}
            </ul>
        </div>'''

    # 2. Descripción Detallada (Párrafos dinámicos)
    secciones_descripcion = []
    if marketing_content.get('desc_titulo_1') and marketing_content.get('desc_parrafo_1'):
        secciones_descripcion.append({
            'titulo': marketing_content['desc_titulo_1'],
            'parrafo': marketing_content['desc_parrafo_1']
        })
    if marketing_content.get('desc_titulo_2') and marketing_content.get('desc_parrafo_2'):
        secciones_descripcion.append({
            'titulo': marketing_content['desc_titulo_2'],
            'parrafo': marketing_content['desc_parrafo_2']
        })

    if not secciones_descripcion:
        secciones_descripcion.append({
            'titulo': 'POTENCIA Y RENDIMIENTO SUPERIOR',
            'parrafo': f"Este equipo con {info.get('potencia_kva', 'alta')} KVA de potencia maxima esta disenado para brindar energia confiable y constante."
        })

    for section in secciones_descripcion:
        html += f'''
        <div class="content-section" style="margin: 30px; padding: 30px; background: white; border-radius: 12px; box-shadow: 0 2px 10px rgba(0,0,0,0.05); border-left: 4px solid #FFC107;">
            <h3 style="color: #D32F2F; font-size: 24px; margin: 0 0 15px 0; font-weight: 700;">
                {section.get('titulo', 'CARACTERISTICAS').upper()}
            </h3>
            <div style="font-size: 16px; line-height: 1.8; color: #555;">
                {section.get('parrafo', '')}
            </div>
        </div>'''

    # 3. Aplicaciones Ideales
    aplicaciones = []
    if marketing_content.get('app_texto_1') and marketing_content.get('app_icono_1'):
        aplicaciones.append({
            'texto': marketing_content['app_texto_1'],
            'icono': marketing_content['app_icono_1']
        })
    if marketing_content.get('app_texto_2') and marketing_content.get('app_icono_2'):
        aplicaciones.append({
            'texto': marketing_content['app_texto_2'],
            'icono': marketing_content['app_icono_2']
        })

    if aplicaciones:
        apps_html = ""
        for app in aplicaciones:
            icono_svg = ICONOS_SVG.get(app.get('icono', 'dot'), ICONOS_SVG['dot'])
            apps_html += f'''
                <li style="padding: 8px 0; display: flex; align-items: start; gap: 10px;">
                    <div style="min-width: 20px; margin-top: 3px;">{icono_svg}</div>
                    <span>{app.get('texto', '')}</span>
                </li>'''
        
        html += f'''
        <div class="content-section" style="margin: 30px; padding: 30px; background: white; border-radius: 12px; box-shadow: 0 2px 10px rgba(0,0,0,0.05); border-left: 4px solid #4caf50;">
            <h3 style="color: #D32F2F; font-size: 24px; margin: 0 0 15px 0; font-weight: 700;">APLICACIONES IDEALES</h3>
            <ul style="list-style: none; padding: 0; margin: 0; font-size: 16px; line-height: 1.8; color: #555;">
                {apps_html}
            </ul>
        </div>'''
        
    return html
