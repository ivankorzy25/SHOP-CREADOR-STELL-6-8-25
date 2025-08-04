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

def generar_info_cards_inline(info, caracteristicas):
    """Genera las tarjetas de información con iconos mejorados y gráfico de consumo."""
    tipo_combustible = caracteristicas.get('tipo_combustible', 'diesel')
    icono_combustible = ICONOS_SVG.get(tipo_combustible, ICONOS_SVG['diesel'])

    # Lógica de potencia mejorada
    potencia_valor = info.get('potencia_standby_valor') or info.get('potencia_valor')
    potencia_unidad = info.get('potencia_standby_unidad') or info.get('potencia_unidad')
    
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
    motor = str(info.get('motor') or info.get('modelo_motor', '') or '').strip()
    consumo_valor = info.get('consumo_75_carga_valor', info.get('consumo_max_carga_valor', 'N/D'))
    consumo_str = f"{consumo_valor} L/h" if consumo_valor != 'N/D' else 'N/D'

    # Generar badges de características
    badges_html = generar_badges_caracteristicas(info, caracteristicas)

    return f'''
        <!-- BADGES DE CARACTERÍSTICAS ESPECIALES -->
        {f'<div style="text-align: center; padding: 20px 30px 0 30px;">{badges_html}</div>' if badges_html else ''}
        
        <!-- ESPECIFICACIONES PRINCIPALES -->
        <div style="padding: 30px; display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px;">
            
            <!-- Card Potencia con animación -->
            <div class="card-hover" style="background: #f8f9fa; border-radius: 12px; padding: 25px; border-left: 4px solid #ff6600; box-shadow: 0 2px 8px rgba(0,0,0,0.08); position: relative; overflow: hidden;">
                <div style="position: absolute; top: -20px; right: -20px; width: 80px; height: 80px; background: rgba(255,102,0,0.1); border-radius: 50%;"></div>
                <div style="display: flex; align-items: center; gap: 15px; position: relative;">
                    <div style="width: 48px; height: 48px; background: #fff3e0; border-radius: 50%; display: flex; align-items: center; justify-content: center; transition: all 0.3s ease;" class="icon-wrapper">
                        {ICONOS_SVG['potencia'].replace('width="28"', 'width="24"').replace('height="28"', 'height="24"')}
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
                        {ICONOS_SVG['motor'].replace('width="28"', 'width="24"').replace('height="28"', 'height="24"').replace('fill="#ff6600"', 'fill="#2196F3"')}
                    </div>
                    <div>
                        <p style="margin: 0; color: #666; font-size: 12px; text-transform: uppercase; letter-spacing: 0.5px;">Motor</p>
                        <p style="margin: 5px 0 0 0; font-size: 18px; font-weight: 600; color: #333;">
                            {motor if motor else 'N/D'}
                        </p>
                        {f'<p style="margin: 0; font-size: 12px; color: #999;"><span style="width: 14px; height: 14px; display: inline-block; vertical-align: middle;">{ICONOS_SVG["rpm"]}</span> {info.get("rpm", "1500")} RPM</p>' if info.get('rpm') else ''}
                    </div>
                </div>
            </div>
            
            <!-- Card Combustible/Consumo mejorada con gráfico -->
            <div class="card-hover" style="background: #f8f9fa; border-radius: 12px; padding: 25px; border-left: 4px solid #4CAF50; box-shadow: 0 2px 8px rgba(0,0,0,0.08); position: relative; overflow: hidden;">
                <div style="position: absolute; top: -20px; right: -20px; width: 80px; height: 80px; background: rgba(76,175,80,0.1); border-radius: 50%;"></div>
                <div style="display: flex; align-items: center; gap: 15px; position: relative;">
                    <div style="width: 48px; height: 48px; background: #e8f5e9; border-radius: 50%; display: flex; align-items: center; justify-content: center; transition: all 0.3s ease;" class="icon-wrapper">
                        {icono_combustible.replace('width="28"', 'width="24"').replace('height="28"', 'height="24"')}
                    </div>
                    <div style="flex: 1;">
                        <p style="margin: 0; color: #666; font-size: 12px; text-transform: uppercase; letter-spacing: 0.5px;">Tipo de Combustible</p>
                        <p style="margin: 5px 0 0 0; font-size: 18px; font-weight: 600; color: #333; text-transform: capitalize;">
                            {tipo_combustible.upper()}
                        </p>
                        {f'<p style="margin: 0; font-size: 14px; color: #999;">Consumo: {consumo_str}</p>' if consumo_str != "N/D" else ''}
                        {generar_grafico_consumo(consumo_str) if consumo_str != "N/D" else ''}
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
            <p style="margin: 5px 0 0 0; font-size: 16px; font-weight: 600; color: #2196F3;">{info['capacidad_tanque_combustible_l']} L</p>
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

def generar_specs_table_inline(info):
    """Genera la tabla de especificaciones con iconos mejorados."""
    # Mapeo de claves a etiquetas y unidades
    mapeo_especificaciones = {
        'potencia_standby_valor': ('Potencia Standby', 'kW'),
        'potencia_valor': ('Potencia Máxima', 'kW'),
        'voltaje': ('Voltaje', 'V'),
        'corriente': ('Corriente', 'A'),
        'frecuencia': ('Frecuencia', 'Hz'),
        'fase': ('Número de Fases', ''),
        'tipo_combustible': ('Tipo de Combustible', ''),
        'capacidad_tanque_combustible_l': ('Capacidad del Tanque', 'L'),
        'autonomia_potencia_nominal_valor': ('Autonomía a Potencia Nominal', 'horas'),
        'consumo_75_carga_valor': ('Consumo a 75% Carga', 'L/h'),
        'consumo_max_carga_valor': ('Consumo a Máxima Carga', 'L/h'),
        'nivel_sonoro_dba_7m': ('Nivel Sonoro a 7m', 'dBA'),
        'temperatura_operacion': ('Temperatura de Operación', '°C'),
        'rpm': ('Revoluciones por Minuto', 'RPM'),
        'peso': ('Peso', 'kg'),
        'dimensiones': ('Dimensiones (LxAnxAl)', 'mm'),
        'certificaciones': ('Certificaciones', ''),
        'garantia': ('Garantía', 'años'),
        'marca_motor': ('Marca del Motor', ''),
        'modelo_motor': ('Modelo del Motor', ''),
        'tipo_arranque': ('Tipo de Arranque', ''),
        'proteccion_ip': ('Protección IP', ''),
        'material_carroceria': ('Material de Carrocería', ''),
        'color': ('Color', ''),
        'accesorios_incluidos': ('Accesorios Incluidos', ''),
        'manual_usuario': ('Manual de Usuario', ''),
        'certificado_conformidad': ('Certificado de Conformidad', ''),
        'fecha_certificacion': ('Fecha de Certificación', ''),
        'observaciones': ('Observaciones', ''),
    }

    # Filtrar y agrupar especificaciones
    especificaciones_filtradas = {k: info[k] for k in mapeo_especificaciones.keys() & info.keys()}
    grupo_especificaciones = {
        'Potencia y Consumo': ['potencia_standby_valor', 'potencia_valor', 'consumo_75_carga_valor', 'consumo_max_carga_valor'],
        'Eléctricas': ['voltaje', 'corriente', 'frecuencia', 'fase'],
        'Motor': ['marca_motor', 'modelo_motor', 'tipo_arranque', 'rpm'],
        'Dimensiones y Peso': ['peso', 'dimensiones'],
        'Tanque y Autonomía': ['capacidad_tanque_combustible_l', 'autonomia_potencia_nominal_valor'],
        'Nivel Sonoro y Temperatura': ['nivel_sonoro_dba_7m', 'temperatura_operacion'],
        'Clasificación y Certificación': ['certificaciones', 'garantia'],
        'Observaciones': ['observaciones'],
    }

    # Generar filas de la tabla
    filas_tabla = []
    for grupo, claves in grupo_especificaciones.items():
        filas_tabla.append(f'<tr style="background: #f2f2f2; font-weight: 500;">')
        filas_tabla.append(f'  <td colspan="2" style="padding: 10px; border: 1px solid #ddd; text-align: left;">{grupo}</td>')
        filas_tabla.append(f'</tr>')
        for clave in claves:
            if clave in especificaciones_filtradas:
                valor = especificaciones_filtradas[clave]
                etiqueta, unidad = mapeo_especificaciones[clave]
                filas_tabla.append(f'''
                    <tr class="spec-row" style="transition: background 0.3s, transform 0.3s;">
                        <td style="padding: 10px; border: 1px solid #ddd;">
                            <div style="display: flex; align-items: center; gap: 10px;">
                                <span style="width: 24px; height: 24px; display: inline-block; vertical-align: middle;">
                                    {ICONOS_SVG.get(clave, ICONOS_SVG['default']).replace('width="28"', 'width="24"').replace('height="28"', 'height="24"')}
                                </span>
                                <strong style="font-size: 14px; color: #333;">{etiqueta}</strong>
                            </div>
                        </td>
                        <td style="padding: 10px; border: 1px solid #ddd; font-size: 14px; color: #666;">
                            {valor} {unidad}
                        </td>
                    </tr>
                ''')

    # Unir filas y generar tabla completa
    tabla_html = f'''
    <div style="overflow-x:auto;">
        <table style="width: 100%; border-collapse: collapse; margin: 20px 0;">
            <thead>
                <tr style="background: #ff6600; color: white; text-align: left;">
                    <th style="padding: 12px; border: 1px solid #ddd;">Especificación</th>
                    <th style="padding: 12px; border: 1px solid #ddd;">Detalle</th>
                </tr>
            </thead>
            <tbody>
                {''.join(filas_tabla)}
            </tbody>
        </table>
    </div>
    '''

    return tabla_html

def generar_content_sections_inline(info, marketing_content):
    """Genera las secciones de contenido con iconos mejorados."""
    secciones_html = []
    
    for seccion in marketing_content.get('secciones', []):
        titulo = seccion.get('titulo', '')
        contenido = seccion.get('contenido', '')
        icono = seccion.get('icono', ICONOS_SVG['default'])
        
        secciones_html.append(f'''
        <div class="content-section" style="background: #fff; border-radius: 12px; padding: 30px; margin: 0 0 20px 0; border-left: 4px solid #ff6600; box-shadow: 0 4px 10px rgba(0,0,0,0.1); transition: transform 0.3s, box-shadow 0.3s;">
            <div style="display: flex; align-items: center; gap: 15px; margin-bottom: 15px;">
                <div style="width: 48px; height: 48px; background: #f8f9fa; border-radius: 50%; display: flex; align-items: center; justify-content: center;">
                    {icono.replace('width="28"', 'width="24"').replace('height="28"', 'height="24"')}
                </div>
                <h3 style="margin: 0; font-size: 18px; font-weight: 600; color: #333;">
                    {titulo}
                </h3>
            </div>
            <div style="font-size: 16px; color: #666; line-height: 1.5;">
                {contenido}
            </div>
        </div>
        ''')
    
    return ''.join(secciones_html)

def generar_benefits_section_inline():
    """Genera la sección de beneficios con iconos mejorados y efectos visuales."""
    beneficios = [
        {'icono': ICONOS_SVG['beneficio1'], 'texto': 'Ahorro de combustible'},
        {'icono': ICONOS_SVG['beneficio2'], 'texto': 'Bajo nivel de ruido'},
        {'icono': ICONOS_SVG['beneficio3'], 'texto': 'Fácil mantenimiento'},
        {'icono': ICONOS_SVG['beneficio4'], 'texto': 'Alta durabilidad'},
    ]
    
    beneficios_html = []
    
    for beneficio in beneficios:
        beneficios_html.append(f'''
        <div class="benefit-card" style="background: #f9f9f9; border-radius: 10px; padding: 20px; text-align: center; border: 1px solid #ddd; transition: transform 0.3s, box-shadow 0.3s;">
            <div style="width: 60px; height: 60px; margin: 0 auto 10px; display: flex; align-items: center; justify-content: center; border-radius: 50%; background: #e3f2fd;">
                {beneficio['icono'].replace('width="28"', 'width="24"').replace('height="28"', 'height="24"')}
            </div>
            <p style="margin: 0; font-size: 16px; font-weight: 500; color: #333;">
                {beneficio['texto']}
            </p>
        </div>
        ''')
    
    return f'''
    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px;">
        {''.join(beneficios_html)}
    </div>
    '''

def generar_cta_section_inline(info, config):
    """Genera la sección de call to action con botones mejorados."""
    return f'''
    <div style="text-align: center; padding: 40px 20px; background: #ff6600; border-radius: 12px; margin: 20px 0; box-shadow: 0 4px 20px rgba(0,0,0,0.1);">
        <h2 style="color: white; font-size: 28px; margin: 0 0 15px 0; font-weight: 700;">
            ¿Listo para llevar tu proyecto al siguiente nivel?
        </h2>
        <p style="color: #fff3e0; font-size: 18px; margin: 0 0 25px 0;">
            Contáctanos y obtén una asesoría personalizada.
        </p>
        <a href="mailto:{config['email_contacto']}" style="display: inline-block; background: #fff; color: #ff6600; padding: 15px 30px; border-radius: 25px; font-size: 16px; font-weight: 600; text-transform: uppercase; letter-spacing: 1px; transition: background 0.3s, transform 0.3s;">
            Contáctanos
        </a>
    </div>
    '''

def generar_contact_footer_inline(config):
    """Genera el footer de contacto con iconos mejorados."""
    return f'''
    <div style="background: #f8f9fa; padding: 30px 20px; border-top: 1px solid #ddd;">
        <div style="max-width: 800px; margin: 0 auto; display: flex; flex-direction: column; gap: 20px;">
            <div style="display: flex; justify-content: space-between; flex-wrap: wrap;">
                <div style="flex: 1; min-width: 250px;">
                    <h4 style="margin: 0 0 10px 0; font-size: 18px; font-weight: 600;">Contáctanos</h4>
                    <p style="margin: 0; font-size: 14px; color: #666;">
                        Email: <a href="mailto:{config['email_contacto']}" style="color: #ff6600; text-decoration: none;">{config['email_contacto']}</a><br>
                        Teléfono: <a href="tel:{config['telefono_contacto']}" style="color: #ff6600; text-decoration: none;">{config['telefono_contacto']}</a>
                    </p>
                </div>
                <div style="flex: 1; min-width: 250px;">
                    <h4 style="margin: 0 0 10px 0; font-size: 18px; font-weight: 600;">Síguenos</h4>
                    <div style="display: flex; gap: 10px;">
                        <a href="{config['redes_sociales']['facebook']}" style="color: #3b5998; font-size: 18px; text-decoration: none;" target="_blank">
                            {ICONOS_SVG['facebook']}
                        </a>
                        <a href="{config['redes_sociales']['twitter']}" style="color: #1da1f2; font-size: 18px; text-decoration: none;" target="_blank">
                            {ICONOS_SVG['twitter']}
                        </a>
                        <a href="{config['redes_sociales']['linkedin']}" style="color: #0077b5; font-size: 18px; text-decoration: none;" target="_blank">
                            {ICONOS_SVG['linkedin']}
                        </a>
                    </div>
                </div>
            </div>
            <div style="border-top: 1px solid #ddd; padding-top: 10px; text-align: center;">
                <p style="margin: 0; font-size: 14px; color: #666;">
                    &copy; {config['ano']} {config['nombre_empresa']}. Todos los derechos reservados.
                </p>
            </div>
        </div>
    </div>
    '''

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