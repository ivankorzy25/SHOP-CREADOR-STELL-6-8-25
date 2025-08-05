# -*- coding: utf-8 -*-
"""
Generador Premium Restaurado - Mantiene TODO el diseño visual premium
con las correcciones de datos aplicadas

IMPORTANTE: Este archivo mantiene EXACTAMENTE el mismo diseño visual premium
Solo aplica correcciones en el procesamiento de datos
"""
from .data_processor import UniversalDataProcessor
from .efficiency_calculator import UniversalEfficiencyCalculator
from .feature_detector import UniversalFeatureDetector
from .premium_generator_v2 import ICONOS_SVG, extraer_info_motor_limpia

def generar_html_premium_completo(info, marketing_content, config):
    """
    Genera HTML manteniendo TODO el diseño premium original
    con datos correctamente procesados
    """
    # 1. Procesar datos con el sistema universal
    datos_limpios = UniversalDataProcessor.clean_all_data(info)
    caracteristicas = UniversalFeatureDetector.detect_all(datos_limpios)
    eficiencia = UniversalEfficiencyCalculator.calculate(datos_limpios)
    
    # 2. Generar cada componente premium
    css_completo = generar_css_premium_completo()
    header_html = generar_header_premium(datos_limpios, marketing_content)
    badges_html = generar_badges_especiales(caracteristicas)
    cards_principales = generar_cards_principales_premium(datos_limpios, eficiencia)
    cards_adicionales = generar_cards_adicionales_premium(datos_limpios)
    tabla_html = generar_tabla_amarilla_premium(datos_limpios)
    puntos_clave = generar_puntos_clave_premium(marketing_content)
    ventajas_html = generar_ventajas_competitivas_premium()
    cta_html = generar_cta_premium(datos_limpios, config)
    footer_html = generar_footer_premium(config)
    
    # 3. Ensamblar HTML completo
    return f'''<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{datos_limpios.get('nombre', 'Generador Premium')} - Vista Previa</title>
    
    {css_completo}
</head>
<body>
    <div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Arial, sans-serif; max-width: 1200px; margin: 0 auto; background: #ffffff; color: #333333;">
        
        {header_html}
        {badges_html}
        {cards_principales}
        {cards_adicionales}
        {tabla_html}
        {puntos_clave}
        {ventajas_html}
        {cta_html}
        {footer_html}
        
    </div>
</body>
</html>'''

def generar_css_premium_completo():
    """Genera TODO el CSS premium con animaciones"""
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
            transform: translateY(-2px);
            text-decoration: none;
        }
        
        /* Animaciones */
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
        
        @keyframes shine {
            0% { left: -100%; }
            100% { left: 100%; }
        }
        
        @keyframes spin {
            from { transform: rotate(0deg); }
            to { transform: rotate(360deg); }
        }
        
        .pulse-animation {
            animation: pulse 2s ease-in-out infinite;
        }
        
        .float-animation {
            animation: float 3s ease-in-out infinite;
        }
        
        .loading-spinner {
            animation: spin 1s linear infinite;
        }
        
        .shine-effect {
            position: relative;
            overflow: hidden;
        }
        .shine-effect:after {
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, transparent, rgba(255,255,255,0.4), transparent);
            animation: shine 3s infinite;
        }
    </style>
    '''

def generar_header_premium(info, marketing_content):
    """Genera header con gradiente y diseño premium"""
    titulo = marketing_content.get('titulo_h1', info.get('nombre', 'Producto Premium'))
    subtitulo = marketing_content.get('subtitulo_p', 'Solución profesional de alta calidad')
    
    # Extraer modelo y marca limpios
    marca = info.get('marca', '')
    modelo = info.get('modelo', '')
    
    return f'''
    <!-- HEADER HERO SECTION -->
    <div style="background: linear-gradient(135deg, #ff6600 0%, #ff8533 100%); color: white; padding: 50px 30px; text-align: center; position: relative; overflow: hidden;">
        <!-- Decoración de fondo -->
        <div style="position: absolute; top: -50px; right: -50px; width: 200px; height: 200px; background: rgba(255,255,255,0.1); border-radius: 50%;"></div>
        <div style="position: absolute; bottom: -30px; left: -30px; width: 150px; height: 150px; background: rgba(255,255,255,0.05); border-radius: 50%;"></div>
        
        <h1 style="margin: 0 0 15px 0; font-size: 42px; font-weight: 800; text-shadow: 2px 2px 4px rgba(0,0,0,0.2); position: relative;">
            {titulo}
        </h1>
        <p style="margin: 0 0 10px 0; font-size: 20px; opacity: 0.95; font-weight: 300;">
            {subtitulo}
        </p>
        <div style="display: flex; gap: 15px; justify-content: center; margin-top: 20px;">
            <span style="background: rgba(255,255,255,0.2); padding: 8px 20px; border-radius: 25px; font-size: 14px; backdrop-filter: blur(10px);">
                <strong>{marca}</strong> {modelo}
            </span>
        </div>
    </div>
    '''

def generar_badges_especiales(caracteristicas):
    """Genera badges de características especiales"""
    badges = caracteristicas.get('badges_especiales', [])
    
    if not badges:
        return ''
    
    html = '''
    <!-- BADGES DE CARACTERÍSTICAS ESPECIALES -->
    <div style="padding: 20px 30px 0 30px; display: flex; gap: 10px; flex-wrap: wrap; justify-content: center;">
    '''
    
    for badge in badges[:4]:  # Máximo 4 badges
        color = badge.get('color', '#ff6600')
        texto = badge.get('texto', '')
        icono = badge.get('icono', 'star')
        
        html += f'''
        <div class="pulse-animation" style="background: {color}; color: white; padding: 8px 16px; 
                    border-radius: 20px; font-size: 12px; font-weight: 600; 
                    display: inline-flex; align-items: center; gap: 8px;
                    box-shadow: 0 2px 8px rgba(0,0,0,0.15);">
            {ICONOS_SVG.get(icono, '')}
            {texto}
        </div>
        '''
    
    html += '</div>'
    return html

def generar_cards_principales_premium(info, eficiencia):
    """Genera las cards principales con gráfico de eficiencia VISIBLE"""
    # Card de Potencia
    potencia = info.get('potencia_kva', info.get('potencia', 'N/D'))
    
    # Card de Motor
    motor = extraer_info_motor_limpia(info)
    
    # Card de Combustible con gráfico
    combustible = info.get('combustible', 'N/D')
    consumo = info.get('consumo', 'N/D')
    
    # Card de Autonomía
    autonomia = info.get('autonomia', info.get('autonomia_horas', 'N/D'))
    capacidad = info.get('capacidad_tanque', 'N/D')
    
    return f'''
    <!-- ESPECIFICACIONES PRINCIPALES -->
    <div style="padding: 30px; display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 20px;">
        
        <!-- Card Potencia -->
        <div class="card-hover" style="background: #f8f9fa; border-radius: 12px; padding: 25px; 
                    border-left: 4px solid #ff6600; box-shadow: 0 2px 8px rgba(0,0,0,0.08); 
                    position: relative; overflow: hidden;">
            <div style="position: absolute; top: -20px; right: -20px; width: 80px; height: 80px; 
                        background: rgba(255,102,0,0.1); border-radius: 50%;"></div>
            <div style="display: flex; align-items: center; gap: 15px; position: relative;">
                <div style="width: 48px; height: 48px; background: #fff3e0; border-radius: 50%; 
                            display: flex; align-items: center; justify-content: center; 
                            transition: all 0.3s ease;" class="icon-wrapper">
                    {ICONOS_SVG['potencia']}
                </div>
                <div style="flex: 1;">
                    <p style="margin: 0; color: #666; font-size: 12px; text-transform: uppercase; letter-spacing: 0.5px;">
                        Potencia Nominal
                    </p>
                    <p style="margin: 5px 0 0 0; font-size: 28px; font-weight: 700; color: #ff6600;">
                        {potencia}
                    </p>
                </div>
            </div>
        </div>
        
        <!-- Card Motor -->
        <div class="card-hover" style="background: #f8f9fa; border-radius: 12px; padding: 25px; 
                    border-left: 4px solid #2196F3; box-shadow: 0 2px 8px rgba(0,0,0,0.08); 
                    position: relative; overflow: hidden;">
            <div style="position: absolute; top: -20px; right: -20px; width: 80px; height: 80px; 
                        background: rgba(33,150,243,0.1); border-radius: 50%;"></div>
            <div style="display: flex; align-items: center; gap: 15px; position: relative;">
                <div style="width: 48px; height: 48px; background: #e3f2fd; border-radius: 50%; 
                            display: flex; align-items: center; justify-content: center; 
                            transition: all 0.3s ease;" class="icon-wrapper">
                    {ICONOS_SVG['motor']}
                </div>
                <div style="flex: 1;">
                    <p style="margin: 0; color: #666; font-size: 12px; text-transform: uppercase; letter-spacing: 0.5px;">
                        Motor
                    </p>
                    <p style="margin: 5px 0 0 0; font-size: 18px; font-weight: 600; color: #333;">
                        {motor}
                    </p>
                </div>
            </div>
        </div>
        
        <!-- Card Combustible con Gráfico de Eficiencia -->
        <div class="card-hover" style="background: #f8f9fa; border-radius: 12px; padding: 25px; 
                    border-left: 4px solid #4CAF50; box-shadow: 0 2px 8px rgba(0,0,0,0.08); 
                    position: relative; overflow: hidden;">
            <div style="position: absolute; top: -20px; right: -20px; width: 80px; height: 80px; 
                        background: rgba(76,175,80,0.1); border-radius: 50%;"></div>
            <div style="display: flex; align-items: center; gap: 15px; position: relative;">
                <div style="width: 48px; height: 48px; background: #e8f5e9; border-radius: 50%; 
                            display: flex; align-items: center; justify-content: center; 
                            transition: all 0.3s ease;" class="icon-wrapper">
                    {get_fuel_icon(combustible)}
                </div>
                <div style="flex: 1;">
                    <p style="margin: 0; color: #666; font-size: 12px; text-transform: uppercase; letter-spacing: 0.5px;">
                        Tipo de Combustible
                    </p>
                    <p style="margin: 5px 0 0 0; font-size: 18px; font-weight: 600; color: #333; text-transform: capitalize;">
                        {combustible}
                    </p>
                    <p style="margin: 5px 0 0 0; font-size: 14px; color: #666;">
                        Consumo: <strong>{consumo}</strong>
                    </p>
                    
                    <!-- GRÁFICO DE EFICIENCIA VISUAL -->
                    <div style="margin-top: 10px; background: #f5f5f5; border-radius: 8px; padding: 10px;">
                        <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
                            <span style="font-size: 11px; color: #666; font-weight: 600;">EFICIENCIA DE CONSUMO</span>
                            <span style="font-size: 11px; color: {eficiencia.get('color', '#FFC107')}; font-weight: 600;">
                                {eficiencia.get('texto', 'Eficiencia Normal')}
                            </span>
                        </div>
                        <div style="background: #e0e0e0; height: 8px; border-radius: 4px; overflow: hidden; position: relative;">
                            <div style="background: linear-gradient(to right, #4CAF50 0%, #8BC34A 25%, #FFC107 50%, #FF9800 75%, #F44336 100%); 
                                        height: 100%; width: 100%; opacity: 0.3;"></div>
                            <div style="position: absolute; top: 0; left: 0; background: {eficiencia.get('color', '#FFC107')}; 
                                        width: {eficiencia.get('porcentaje', 60)}%; height: 100%; 
                                        transition: width 1s ease; box-shadow: 0 0 4px rgba(0,0,0,0.2);"></div>
                        </div>
                        <div style="display: flex; justify-content: space-between; margin-top: 5px;">
                            <span style="font-size: 10px; color: #4CAF50;">Eficiente</span>
                            <span style="font-size: 10px; color: #666;">{consumo}</span>
                            <span style="font-size: 10px; color: #F44336;">Alto consumo</span>
                        </div>
                        <div style="text-align: center; margin-top: 5px;">
                            <span style="font-size: 9px; color: #999;">
                                Consumo optimizado para {combustible}
                            </span>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- Card Autonomía -->
        <div class="card-hover" style="background: #f8f9fa; border-radius: 12px; padding: 25px; 
                    border-left: 4px solid #9C27B0; box-shadow: 0 2px 8px rgba(0,0,0,0.08); 
                    position: relative; overflow: hidden;">
            <div style="position: absolute; top: -20px; right: -20px; width: 80px; height: 80px; 
                        background: rgba(156,39,176,0.1); border-radius: 50%;"></div>
            <div style="display: flex; align-items: center; gap: 15px; position: relative;">
                <div style="width: 48px; height: 48px; background: #f3e5f5; border-radius: 50%; 
                            display: flex; align-items: center; justify-content: center; 
                            transition: all 0.3s ease;" class="icon-wrapper">
                    {ICONOS_SVG.get('clock', ICONOS_SVG['autonomia'])}
                </div>
                <div style="flex: 1;">
                    <p style="margin: 0; color: #666; font-size: 12px; text-transform: uppercase; letter-spacing: 0.5px;">
                        Autonomía
                    </p>
                    <p style="margin: 5px 0 0 0; font-size: 24px; font-weight: 700; color: #9C27B0;">
                        {autonomia}
                    </p>
                    <p style="margin: 5px 0 0 0; font-size: 14px; color: #666;">
                        Tanque: <strong>{capacidad}</strong>
                    </p>
                </div>
            </div>
        </div>
        
    </div>
    '''

def generar_cards_adicionales_premium(info):
    """Genera cards adicionales con información secundaria"""
    # Extraer datos adicionales
    voltaje = info.get('voltaje', '')
    frecuencia = info.get('frecuencia', '')
    arranque = info.get('tipo_arranque', info.get('arranque', ''))
    nivel_ruido = info.get('nivel_ruido', info.get('nivel_ruido_dba', ''))
    
    cards_html = '''
    <!-- CARACTERÍSTICAS ADICIONALES EN CARDS -->
    <div style="padding: 0 30px 30px 30px; display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px;">
    '''
    
    # Card Voltaje
    if voltaje:
        cards_html += f'''
        <div style="background: #e3f2fd; border-radius: 8px; padding: 15px; text-align: center; border: 1px solid #90caf9;">
            <div style="width: 32px; height: 32px; margin: 0 auto 8px;">
                {ICONOS_SVG.get('voltaje', ICONOS_SVG['zap'])}
            </div>
            <p style="margin: 0; font-size: 12px; color: #666;">Voltaje</p>
            <p style="margin: 5px 0 0 0; font-size: 16px; font-weight: 600; color: #2196F3;">{voltaje}</p>
        </div>
        '''
    
    # Card Frecuencia
    if frecuencia:
        cards_html += f'''
        <div style="background: #f3e5f5; border-radius: 8px; padding: 15px; text-align: center; border: 1px solid #ce93d8;">
            <div style="width: 32px; height: 32px; margin: 0 auto 8px;">
                {ICONOS_SVG.get('frecuencia', ICONOS_SVG['activity'])}
            </div>
            <p style="margin: 0; font-size: 12px; color: #666;">Frecuencia</p>
            <p style="margin: 5px 0 0 0; font-size: 16px; font-weight: 600; color: #9C27B0;">{frecuencia}</p>
        </div>
        '''
    
    # Card Arranque
    if arranque:
        cards_html += f'''
        <div style="background: #e8f5e9; border-radius: 8px; padding: 15px; text-align: center; border: 1px solid #a5d6a7;">
            <div style="width: 32px; height: 32px; margin: 0 auto 8px;">
                {ICONOS_SVG.get('arranque', ICONOS_SVG['power'])}
            </div>
            <p style="margin: 0; font-size: 12px; color: #666;">Arranque</p>
            <p style="margin: 5px 0 0 0; font-size: 16px; font-weight: 600; color: #4CAF50;">{arranque}</p>
        </div>
        '''
    
    # Card Nivel de Ruido
    if nivel_ruido:
        cards_html += f'''
        <div style="background: #fff3e0; border-radius: 8px; padding: 15px; text-align: center; border: 1px solid #ffcc80;">
            <div style="width: 32px; height: 32px; margin: 0 auto 8px;">
                {ICONOS_SVG.get('ruido', ICONOS_SVG['volume'])}
            </div>
            <p style="margin: 0; font-size: 12px; color: #666;">Nivel Sonoro</p>
            <p style="margin: 5px 0 0 0; font-size: 16px; font-weight: 600; color: #FF9800;">{nivel_ruido}</p>
        </div>
        '''
    
    cards_html += '</div>'
    return cards_html

def generar_tabla_amarilla_premium(info):
    """Genera la tabla amarilla con diseño premium y datos limpios"""
    return f'''
    <!-- TABLA DE ESPECIFICACIONES TÉCNICAS MEJORADA -->
    <div style="background: #FFC107; margin: 30px; padding: 30px; border-radius: 16px; 
                box-shadow: 0 4px 20px rgba(0,0,0,0.1); position: relative;">
        <!-- Decoración de esquina -->
        <div style="position: absolute; top: -10px; right: -10px; width: 60px; height: 60px; 
                    background: #ff6600; border-radius: 50%; opacity: 0.2;"></div>
        
        <h2 style="color: #333; font-size: 28px; margin: 0 0 25px 0; text-align: center; 
                   font-weight: 700; position: relative;">
            {ICONOS_SVG.get('specs', '')}
            <br>
            ESPECIFICACIONES TÉCNICAS COMPLETAS
        </h2>
        
        <div style="background: white; border-radius: 12px; overflow: hidden; 
                    box-shadow: 0 2px 10px rgba(0,0,0,0.05);">
            <table style="width: 100%; border-collapse: collapse;">
                <tr style="background: #333; color: white;">
                    <td style="padding: 15px 20px; font-weight: 600; font-size: 14px; 
                               text-transform: uppercase; letter-spacing: 0.5px;">Característica</td>
                    <td style="padding: 15px 20px; font-weight: 600; font-size: 14px; 
                               text-transform: uppercase; letter-spacing: 0.5px;">Especificación</td>
                </tr>
                {generar_filas_tabla_premium(info)}
            </table>
        </div>
    </div>
    '''

def generar_filas_tabla_premium(info):
    """Genera las filas de la tabla con agrupación por categorías"""
    filas_html = ''
    
    # Definir grupos de campos
    grupos = {
        'Información General': ['modelo', 'marca', 'familia', 'serie'],
        'Potencia y Electricidad': ['potencia', 'potencia_kva', 'potencia_kw', 'voltaje', 'frecuencia', 'fases'],
        'Motor y Mecánica': ['motor', 'cilindrada', 'cilindros', 'rpm'],
        'Combustible y Autonomía': ['combustible', 'consumo', 'capacidad_tanque', 'autonomia'],
        'Control y Operación': ['tipo_arranque', 'arranque', 'bateria', 'panel_control', 'controlador'],
        'Características Físicas': ['dimensiones', 'peso', 'nivel_ruido'],
        'Otros': []  # Para campos no categorizados
    }
    
    # Procesar cada grupo
    campos_procesados = set()
    row_count = 0
    
    for grupo_nombre, campos_grupo in grupos.items():
        campos_en_grupo = []
        
        # Buscar campos del grupo en info
        for campo in campos_grupo:
            for key, value in info.items():
                if campo in key and key not in campos_procesados and value and str(value).strip():
                    campos_en_grupo.append((key, value))
                    campos_procesados.add(key)
        
        # Si hay campos en el grupo, agregar header y filas
        if campos_en_grupo:
            filas_html += f'''
            <tr style="background: #f5f5f5; border-top: 2px solid #ddd;">
                <td colspan="2" style="padding: 10px 20px; font-weight: 600; color: #666; 
                                       font-size: 12px; text-transform: uppercase; letter-spacing: 1px;">
                    {grupo_nombre}
                </td>
            </tr>
            '''
            
            for campo_key, valor in campos_en_grupo:
                bg_color = '#f8f9fa' if row_count % 2 == 0 else 'white'
                nombre_display = UniversalDataProcessor.get_display_name(campo_key)
                icono = obtener_icono_tabla(campo_key)
                
                filas_html += f'''
                <tr class="spec-row" style="background: {bg_color}; border-bottom: 1px solid #eee; transition: all 0.2s ease;">
                    <td style="padding: 15px 20px; display: flex; align-items: center; gap: 10px;">
                        <div style="width: 20px; height: 20px; opacity: 0.7; transition: all 0.3s ease;">
                            {icono}
                        </div>
                        <span style="color: #666; font-weight: 500;">{nombre_display}</span>
                    </td>
                    <td style="padding: 15px 20px; font-weight: 600; color: #333;">{valor}</td>
                </tr>
                '''
                row_count += 1
    
    # Agregar campos no categorizados
    campos_otros = []
    for key, value in info.items():
        if key not in campos_procesados and value and str(value).strip() and not UniversalDataProcessor._should_exclude_field(key):
            campos_otros.append((key, value))
    
    if campos_otros:
        filas_html += f'''
        <tr style="background: #f5f5f5; border-top: 2px solid #ddd;">
            <td colspan="2" style="padding: 10px 20px; font-weight: 600; color: #666; 
                                   font-size: 12px; text-transform: uppercase; letter-spacing: 1px;">
                Otros
            </td>
        </tr>
        '''
        
        for campo_key, valor in campos_otros:
            bg_color = '#f8f9fa' if row_count % 2 == 0 else 'white'
            nombre_display = UniversalDataProcessor.get_display_name(campo_key)
            icono = obtener_icono_tabla(campo_key)
            
            filas_html += f'''
            <tr class="spec-row" style="background: {bg_color}; border-bottom: 1px solid #eee; transition: all 0.2s ease;">
                <td style="padding: 15px 20px; display: flex; align-items: center; gap: 10px;">
                    <div style="width: 20px; height: 20px; opacity: 0.7; transition: all 0.3s ease;">
                        {icono}
                    </div>
                    <span style="color: #666; font-weight: 500;">{nombre_display}</span>
                </td>
                <td style="padding: 15px 20px; font-weight: 600; color: #333;">{valor}</td>
            </tr>
            '''
            row_count += 1
    
    return filas_html

def generar_puntos_clave_premium(marketing_content):
    """Genera los puntos clave del marketing"""
    puntos_html = '''
    <!-- SECCIONES DE CONTENIDO -->
    <div style="padding: 0 30px 30px 30px;">
    '''
    
    # Buscar puntos clave en el marketing content
    for i in range(1, 6):
        titulo = marketing_content.get(f'seccion_{i}_titulo', '')
        contenido = marketing_content.get(f'seccion_{i}_contenido', '')
        
        if titulo and contenido:
            color = ['#ff6600', '#2196F3', '#4CAF50', '#9C27B0', '#FF9800'][i-1]
            puntos_html += f'''
            <div class="content-section" style="background: #f8f9fa; border-radius: 12px; 
                        padding: 25px; margin-bottom: 20px; border-left: 5px solid {color}; 
                        box-shadow: 0 2px 8px rgba(0,0,0,0.08); position: relative; overflow: hidden;">
                <div style="position: absolute; top: -30px; right: -30px; width: 100px; height: 100px; 
                            background: {color}22; border-radius: 50%; opacity: 0.5;"></div>
                <h3 style="margin: 0 0 15px 0; color: #333; font-size: 22px; position: relative;">
                    {titulo}
                </h3>
                <p style="margin: 0; color: #666; line-height: 1.6; position: relative;">
                    {contenido}
                </p>
            </div>
            '''
    
    puntos_html += '</div>'
    return puntos_html

def generar_ventajas_competitivas_premium():
    """Genera sección de ventajas competitivas"""
    return '''
    <!-- VENTAJAS COMPETITIVAS MEJORADAS -->
    <div style="background: #f0f0f0; padding: 50px 30px; margin-top: 40px;">
        <h2 style="text-align: center; color: #333; font-size: 32px; margin: 0 0 40px 0; font-weight: 700;">
            ¿Por Qué Elegirnos?
        </h2>
        
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 25px; max-width: 1000px; margin: 0 auto;">
            
            <div class="benefit-card" style="background: white; border-radius: 12px; padding: 30px; 
                        text-align: center; box-shadow: 0 3px 10px rgba(0,0,0,0.08); position: relative; overflow: hidden;">
                <div style="position: absolute; top: 0; right: 0; width: 80px; height: 80px; 
                            background: linear-gradient(135deg, #ff6600 0%, #ff8533 100%); 
                            border-radius: 0 0 0 100%; opacity: 0.1;"></div>
                <div class="icon-circle" style="width: 60px; height: 60px; background: #fff3e0; 
                            border-radius: 50%; display: flex; align-items: center; 
                            justify-content: center; margin: 0 auto 20px;">
                    {ICONOS_SVG['quality']}
                </div>
                <h3 style="margin: 0 0 10px 0; color: #333; font-size: 20px;">Calidad Garantizada</h3>
                <p style="margin: 0; color: #666; line-height: 1.5;">
                    Productos certificados con los más altos estándares de calidad internacional
                </p>
            </div>
            
            <div class="benefit-card" style="background: white; border-radius: 12px; padding: 30px; 
                        text-align: center; box-shadow: 0 3px 10px rgba(0,0,0,0.08); position: relative; overflow: hidden;">
                <div style="position: absolute; top: 0; right: 0; width: 80px; height: 80px; 
                            background: linear-gradient(135deg, #2196F3 0%, #42a5f5 100%); 
                            border-radius: 0 0 0 100%; opacity: 0.1;"></div>
                <div class="icon-circle" style="width: 60px; height: 60px; background: #e3f2fd; 
                            border-radius: 50%; display: flex; align-items: center; 
                            justify-content: center; margin: 0 auto 20px;">
                    {ICONOS_SVG['tools']}
                </div>
                <h3 style="margin: 0 0 10px 0; color: #333; font-size: 20px;">Servicio Técnico</h3>
                <p style="margin: 0; color: #666; line-height: 1.5;">
                    Soporte técnico especializado y mantenimiento preventivo disponible 24/7
                </p>
            </div>
            
            <div class="benefit-card" style="background: white; border-radius: 12px; padding: 30px; 
                        text-align: center; box-shadow: 0 3px 10px rgba(0,0,0,0.08); position: relative; overflow: hidden;">
                <div style="position: absolute; top: 0; right: 0; width: 80px; height: 80px; 
                            background: linear-gradient(135deg, #4CAF50 0%, #66bb6a 100%); 
                            border-radius: 0 0 0 100%; opacity: 0.1;"></div>
                <div class="icon-circle" style="width: 60px; height: 60px; background: #e8f5e9; 
                            border-radius: 50%; display: flex; align-items: center; 
                            justify-content: center; margin: 0 auto 20px;">
                    {ICONOS_SVG['shield']}
                </div>
                <h3 style="margin: 0 0 10px 0; color: #333; font-size: 20px;">Garantía Extendida</h3>
                <p style="margin: 0; color: #666; line-height: 1.5;">
                    Respaldo total con garantía extendida y repuestos originales disponibles
                </p>
            </div>
            
            <div class="benefit-card" style="background: white; border-radius: 12px; padding: 30px; 
                        text-align: center; box-shadow: 0 3px 10px rgba(0,0,0,0.08); position: relative; overflow: hidden;">
                <div style="position: absolute; top: 0; right: 0; width: 80px; height: 80px; 
                            background: linear-gradient(135deg, #9C27B0 0%, #ab47bc 100%); 
                            border-radius: 0 0 0 100%; opacity: 0.1;"></div>
                <div class="icon-circle" style="width: 60px; height: 60px; background: #f3e5f5; 
                            border-radius: 50%; display: flex; align-items: center; 
                            justify-content: center; margin: 0 auto 20px;">
                    {ICONOS_SVG['money']}
                </div>
                <h3 style="margin: 0 0 10px 0; color: #333; font-size: 20px;">Mejor Precio</h3>
                <p style="margin: 0; color: #666; line-height: 1.5;">
                    Relación calidad-precio inmejorable con financiación a medida
                </p>
            </div>
            
        </div>
    </div>
    '''

def generar_cta_premium(info, config):
    """Genera Call to Action mejorado"""
    marca = info.get('marca', '')
    modelo = info.get('modelo', '')
    whatsapp = config.get('whatsapp', '')
    
    producto_ref = f"{marca} {modelo}".strip() if marca and modelo else "este producto"
    mensaje = f"Hola! Me interesa el {producto_ref}. ¿Podrían enviarme más información?"
    whatsapp_url = f"https://wa.me/{whatsapp}?text={mensaje}"
    
    return f'''
    <!-- CALL TO ACTION MEJORADO -->
    <div style="background: linear-gradient(135deg, #ff6600 0%, #ff8533 100%); 
                padding: 60px 30px; text-align: center; position: relative; overflow: hidden;">
        <div style="position: absolute; top: -50px; left: -50px; width: 150px; height: 150px; 
                    background: rgba(255,255,255,0.1); border-radius: 50%;"></div>
        <div style="position: absolute; bottom: -30px; right: -30px; width: 100px; height: 100px; 
                    background: rgba(255,255,255,0.05); border-radius: 50%;"></div>
        
        <h2 style="color: white; font-size: 36px; margin: 0 0 20px 0; font-weight: 700; position: relative;">
            ¿Listo para Potenciar tu Negocio?
        </h2>
        <p style="color: white; font-size: 18px; margin: 0 0 30px 0; opacity: 0.95; 
                  max-width: 600px; margin-left: auto; margin-right: auto; position: relative;">
            Contáctanos ahora y recibe asesoramiento personalizado de nuestros expertos
        </p>
        
        <div style="display: flex; gap: 20px; justify-content: center; flex-wrap: wrap; position: relative;">
            <a href="{whatsapp_url}" target="_blank" 
               class="btn-hover shine-effect" 
               style="background: white; color: #ff6600; padding: 18px 40px; 
                      border-radius: 30px; text-decoration: none; font-weight: 700; 
                      font-size: 18px; display: inline-flex; align-items: center; 
                      gap: 10px; box-shadow: 0 4px 15px rgba(0,0,0,0.2);">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="#25D366">
                    <path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.693.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413Z"/>
                </svg>
                Consultar por WhatsApp
            </a>
            
            <a href="tel:{config.get('telefono', '')}" 
               class="btn-hover" 
               style="background: rgba(255,255,255,0.2); color: white; 
                      padding: 18px 40px; border-radius: 30px; 
                      text-decoration: none; font-weight: 700; 
                      font-size: 18px; border: 2px solid white; 
                      display: inline-flex; align-items: center; gap: 10px;">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="white">
                    <path d="M6.62 10.79c1.44 2.83 3.76 5.14 6.59 6.59l2.2-2.2c.27-.27.67-.36 1.02-.24 1.12.37 2.33.57 3.57.57.55 0 1 .45 1 1V20c0 .55-.45 1-1 1-9.39 0-17-7.61-17-17 0-.55.45-1 1-1h3.5c.55 0 1 .45 1 1 0 1.25.2 2.45.57 3.57.11.35.03.74-.25 1.02l-2.2 2.2z"/>
                </svg>
                Llamar Ahora
            </a>
        </div>
    </div>
    '''

def generar_footer_premium(config):
    """Genera footer con información de contacto"""
    return f'''
    <!-- FOOTER CONTACTO MEJORADO -->
    <footer style="background: #333; color: white; padding: 40px 30px; text-align: center;">
        <div style="max-width: 800px; margin: 0 auto;">
            <h3 style="margin: 0 0 25px 0; font-size: 24px; font-weight: 300;">
                Información de Contacto
            </h3>
            
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); 
                        gap: 30px; margin-bottom: 30px;">
                
                <div>
                    <p style="margin: 0 0 5px 0; opacity: 0.7; font-size: 14px;">Teléfono</p>
                    <p style="margin: 0; font-size: 18px; font-weight: 500;">
                        <a href="tel:{config.get('telefono', '')}" class="contact-link" 
                           style="color: white; text-decoration: none;">
                            {config.get('telefono_display', '')}
                        </a>
                    </p>
                </div>
                
                <div>
                    <p style="margin: 0 0 5px 0; opacity: 0.7; font-size: 14px;">WhatsApp</p>
                    <p style="margin: 0; font-size: 18px; font-weight: 500;">
                        <a href="https://wa.me/{config.get('whatsapp', '')}" class="contact-link" 
                           style="color: white; text-decoration: none;">
                            {config.get('whatsapp', '')}
                        </a>
                    </p>
                </div>
                
                <div>
                    <p style="margin: 0 0 5px 0; opacity: 0.7; font-size: 14px;">Email</p>
                    <p style="margin: 0; font-size: 18px; font-weight: 500;">
                        <a href="mailto:{config.get('email', '')}" class="contact-link" 
                           style="color: white; text-decoration: none;">
                            {config.get('email', '')}
                        </a>
                    </p>
                </div>
                
            </div>
            
            <div style="border-top: 1px solid #555; padding-top: 20px; margin-top: 20px;">
                <p style="margin: 0; opacity: 0.7; font-size: 14px;">
                    © 2024 - Todos los derechos reservados
                </p>
            </div>
        </div>
    </footer>
    '''

# Funciones auxiliares

def get_fuel_icon(combustible):
    """Obtiene el icono apropiado para el tipo de combustible"""
    combustible_lower = str(combustible).lower()
    
    if 'diesel' in combustible_lower or 'gasoil' in combustible_lower:
        return ICONOS_SVG.get('diesel', ICONOS_SVG['fuel'])
    elif 'nafta' in combustible_lower or 'gasolina' in combustible_lower:
        return ICONOS_SVG.get('nafta', ICONOS_SVG['fuel'])
    elif 'gas' in combustible_lower:
        return ICONOS_SVG.get('gas', ICONOS_SVG['fuel'])
    else:
        return ICONOS_SVG.get('fuel', '')

def obtener_icono_tabla(campo):
    """Obtiene el icono apropiado para mostrar en la tabla"""
    # Usar el UniversalFeatureDetector para obtener el nombre del icono
    icono_nombre = UniversalFeatureDetector.get_icon_for_field(campo)
    
    # Buscar el SVG correspondiente
    return ICONOS_SVG.get(icono_nombre, ICONOS_SVG.get('info', ''))