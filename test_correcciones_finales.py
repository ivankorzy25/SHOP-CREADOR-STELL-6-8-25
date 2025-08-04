#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script de prueba para verificar TODAS las correcciones implementadas
"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from ai_generator.product_templates import generar_html_generador, aplicar_mejoras_universales
from ai_generator.premium_generator_v2 import (
    validar_y_limpiar_datos_universal,
    detectar_caracteristicas_universal,
    calcular_eficiencia_universal,
    generar_specs_table_inline,
    extraer_info_motor_limpia
)

# Producto de prueba con todos los problemas identificados
producto_test = {
    'nombre': 'GENERADOR NAFTERO GL2200 PORTÁTIL',
    'marca': 'LOGUS',
    'modelo': 'GL2200',
    'familia': 'GENERADOR',
    'potencia_kva': '2.2',
    'potencia_kw': '1.76',
    
    # Campos con unidades duplicadas
    'consumo': '0.9 L/h L/h',
    'capacidad_tanque_combustible_l': '15 L L',
    'peso_kg': '38 kg kg',
    'presion_bar': '8 BAR BAR',
    
    # Motor con formato redundante
    'motor': 'Motor 6.5 HP',
    'potencia_motor_valor': '6.5',
    'potencia_motor_unidad': 'HP',
    
    # Campos de unidades que NO deben aparecer en tabla
    'autonomia_horas_unidad': 'horas',
    'frecuencia_hz_unidad': 'Hz',
    'voltaje_v_unidad': 'V',
    'consumo_unidad': 'L/h',
    'potencia_kva_unidad': 'KVA',
    
    # Datos para detección de características
    'combustible': 'Nafta',
    'tipo_arranque': 'Manual',
    'voltaje': '220',
    'frecuencia': '50',
    
    # Campos adicionales
    'autonomia_horas': '8',
    'nivel_ruido_dba': '68',
    'cilindrada_cc': '163',
    'capacidad_aceite_l': '0.6',
    
    # Campo que podría mostrar eficiencia_data como texto
    'eficiencia_data': {
        'porcentaje': 60,
        'texto': 'Eficiencia Normal',
        'color': '#FFC107'
    }
}

# Marketing content
test_marketing = {
    'titulo_h1': 'GENERADOR PORTÁTIL GL2200',
    'subtitulo_p': 'Energía confiable donde la necesites',
    'punto_clave_texto_1': 'Potencia de 2.2 KVA',
    'punto_clave_icono_1': 'lightning',
    'punto_clave_texto_2': 'Motor 4 tiempos 6.5HP',
    'punto_clave_icono_2': 'motor',
    'punto_clave_texto_3': '8 horas de autonomía',
    'punto_clave_icono_3': 'clock'
}

test_config = {
    'whatsapp': '541139563099',
    'email': 'info@generadores.ar',
    'telefono_display': '+54 11 3956-3099',
    'website': 'www.generadores.ar'
}

print("=== TEST DE CORRECCIONES FINALES ===\n")

# 1. Validar y limpiar datos
print("1. VALIDACIÓN Y LIMPIEZA DE DATOS:")
datos_limpios = validar_y_limpiar_datos_universal(producto_test)

# Verificar limpieza de duplicaciones
verificaciones_limpieza = {
    'consumo': ('0.9 L/h L/h', datos_limpios.get('consumo')),
    'capacidad_tanque_combustible_l': ('15 L L', datos_limpios.get('capacidad_tanque_combustible_l')),
    'peso_kg': ('38 kg kg', datos_limpios.get('peso_kg')),
    'presion_bar': ('8 BAR BAR', datos_limpios.get('presion_bar'))
}

for campo, (original, limpio) in verificaciones_limpieza.items():
    if original != limpio and ' L L' not in limpio and ' L/h L/h' not in limpio:
        print(f"   [OK] {campo}: '{original}' -> '{limpio}'")
    else:
        print(f"   [X] {campo}: NO se limpió correctamente")

# 2. Verificar extracción del motor
print("\n2. EXTRACCIÓN DEL MOTOR:")
motor_procesado = extraer_info_motor_limpia(datos_limpios)
print(f"   Motor original: '{producto_test['motor']}'")
print(f"   Motor procesado: '{motor_procesado}'")
if motor_procesado == "Motor 6.5 HP" and "Motor Motor" not in motor_procesado:
    print("   [OK] Motor sin redundancia")
else:
    print("   [X] Motor con problemas")

# 3. Detectar características
print("\n3. DETECCIÓN DE CARACTERÍSTICAS:")
caracteristicas = detectar_caracteristicas_universal(datos_limpios)
print(f"   Tipo combustible: {caracteristicas['tipo_combustible']}")
print(f"   Es portátil: {caracteristicas['es_portatil']}")
print(f"   Badges detectados: {len(caracteristicas['badges_especiales'])}")
for badge in caracteristicas['badges_especiales']:
    print(f"     - {badge['texto']}")

# Verificar si detectó portátil (peso < 60kg para nafta)
peso_num = float(datos_limpios.get('peso_kg', '999').replace('kg', '').strip())
if peso_num < 60 and caracteristicas['tipo_combustible'] == 'nafta':
    if caracteristicas['es_portatil']:
        print("   [OK] Detectó correctamente que es portátil")
    else:
        print("   [X] NO detectó que es portátil")

# 4. Calcular eficiencia
print("\n4. CÁLCULO DE EFICIENCIA:")
eficiencia = calcular_eficiencia_universal(datos_limpios)
print(f"   Porcentaje: {eficiencia['porcentaje']}%")
print(f"   Texto: {eficiencia['texto']}")
print(f"   Color: {eficiencia['color']}")

# 5. Generar HTML
print("\n5. GENERANDO HTML...")
try:
    # Aplicar mejoras universales
    info_procesada, caracteristicas = aplicar_mejoras_universales(datos_limpios, caracteristicas)
    
    # Generar HTML
    html = generar_html_generador(info_procesada, test_marketing, caracteristicas, test_config)
    
    # Verificaciones en el HTML
    print("\n6. VERIFICACIONES DEL HTML:")
    
    # Verificar que NO aparecen campos de unidades
    campos_unidades = [
        'autonomia_horas_unidad', 'frecuencia_hz_unidad', 
        'voltaje_v_unidad', 'consumo_unidad', 'potencia_kva_unidad'
    ]
    
    campos_encontrados = []
    for campo in campos_unidades:
        if campo in html:
            campos_encontrados.append(campo)
    
    if campos_encontrados:
        print(f"   [X] Campos de unidades encontrados en HTML: {campos_encontrados}")
    else:
        print("   [OK] No hay campos de unidades en el HTML")
    
    # Verificar que eficiencia_data no aparece como texto
    if "'eficiencia_data'" in html or "eficiencia_data" in html:
        print("   [X] eficiencia_data aparece como texto en el HTML")
    else:
        print("   [OK] eficiencia_data no aparece como texto")
    
    # Verificar duplicaciones
    verificaciones_html = {
        'Sin duplicación L L': ' L L' not in html,
        'Sin duplicación L/h L/h': 'L/h L/h' not in html,
        'Sin duplicación BAR BAR': 'BAR BAR' not in html,
        'Sin duplicación kg kg': 'kg kg' not in html,
        'Motor sin redundancia': 'Motor Motor' not in html,
        'Badge PORTÁTIL presente': 'PORTÁTIL' in html,
        'Marca en WhatsApp': 'LOGUS%20GL2200' in html
    }
    
    for verificacion, resultado in verificaciones_html.items():
        print(f"   {'[OK]' if resultado else '[X]'} {verificacion}")
    
    # Guardar HTML
    with open('test_correcciones_output.html', 'w', encoding='utf-8') as f:
        f.write(html)
    print("\n   HTML guardado en: test_correcciones_output.html")
    
    # Verificar tabla de especificaciones
    print("\n7. VERIFICACIÓN DE TABLA DE ESPECIFICACIONES:")
    # Extraer solo la parte de la tabla
    if '<table' in html:
        tabla_start = html.find('<table')
        tabla_end = html.find('</table>') + 8
        tabla_html = html[tabla_start:tabla_end]
        
        # Contar filas con campos de unidades
        filas_unidad = 0
        for campo in campos_unidades:
            if campo.replace('_', ' ').title() in tabla_html:
                filas_unidad += 1
                print(f"   [X] Campo de unidad en tabla: {campo}")
        
        if filas_unidad == 0:
            print("   [OK] La tabla no contiene campos de unidades")
    
except Exception as e:
    print(f"\n[X] ERROR: {e}")
    import traceback
    traceback.print_exc()

print("\n=== RESUMEN FINAL ===")
print("Las correcciones implementadas deben resolver:")
print("- Campos de unidades NO aparecen en la tabla")
print("- Motor muestra información sin redundancia")
print("- Detección automática de características (PORTÁTIL)")
print("- eficiencia_data se usa correctamente, no como texto")
print("- Valores limpios sin duplicación de unidades")
print("- Iconos específicos para cada campo")

print("\n=== FIN DEL TEST ===")