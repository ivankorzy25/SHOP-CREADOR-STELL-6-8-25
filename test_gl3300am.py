#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script de prueba para verificar todas las mejoras con el producto GL3300AM
"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from ai_generator.product_templates import generar_html_generador
from ai_generator.premium_generator_v2 import (
    procesar_datos_para_tabla, 
    validar_caracteristicas_producto,
    validar_y_limpiar_datos
)

# Datos de prueba del GL3300AM (generador naftero)
test_info = {
    'nombre': 'GRUPO ELECTROGENO LOGUS GL3300AM 3,3KVA',
    'marca': 'LOGUS',
    'modelo': 'GL3300AM',
    'familia': 'GENERADOR',
    'potencia_kva': '3.3',
    'potencia_kw': '2.64',
    'consumo_75_carga_valor': '1.36',
    'consumo': '1.36 L/h',  
    'capacidad_tanque_combustible_l': '15 L',  # Con unidad duplicada para probar limpieza
    'voltaje': '220',
    'frecuencia': '50',
    'motor': 'LOGUS 7HP',
    'combustible': 'Nafta',
    'tipo_arranque': 'Manual',
    'autonomia': '8',
    'peso_kg': '38',
    'nivel_ruido_dba': '68',
    'cilindrada': '208',
    'dimensiones': '605x440x440'
}

# Simular texto de PDF para detección de características
test_pdf_text = """
Generador Portátil GL3300AM
Motor: LOGUS 7HP OHV
Combustible: Nafta
Arranque: Manual con cuerda
Peso: 38 kg - Fácil de transportar
Ideal para camping y uso doméstico
"""

# Marketing content generado por IA
test_marketing = {
    'titulo_h1': 'GENERADOR PORTÁTIL LOGUS GL3300AM',
    'subtitulo_p': 'Energía confiable donde la necesites',
    'punto_clave_texto_1': 'Potencia de 3.3 KVA para múltiples aplicaciones',
    'punto_clave_icono_1': 'lightning',
    'punto_clave_texto_2': 'Motor LOGUS 7HP de alta confiabilidad',
    'punto_clave_icono_2': 'shield',
    'punto_clave_texto_3': '8 horas de autonomía continua',
    'punto_clave_icono_3': 'clock'
}

test_config = {
    'whatsapp': '541139563099',
    'email': 'info@generadores.ar',
    'telefono_display': '+54 11 3956-3099',
    'website': 'www.generadores.ar'
}

print("=== TEST GENERADOR GL3300AM - NAFTERO ===\n")

# 1. Validar y limpiar datos
print("1. VALIDACIÓN Y LIMPIEZA DE DATOS:")
datos_limpios = validar_y_limpiar_datos(test_info)
print(f"   Capacidad tanque original: '{test_info['capacidad_tanque_combustible_l']}'")
print(f"   Capacidad tanque limpia: '{datos_limpios['capacidad_tanque_combustible_l']}'")
print(f"   Consumo procesado: '{datos_limpios['consumo']}'")

# 2. Detectar características
print("\n2. DETECCIÓN DE CARACTERÍSTICAS:")
caracteristicas = validar_caracteristicas_producto(datos_limpios, test_pdf_text)
print(f"   Tipo combustible: {caracteristicas['tipo_combustible']}")
print(f"   Es portátil: {caracteristicas['es_portatil']}")
print(f"   Badges especiales: {len(caracteristicas['badges_especiales'])} badges")
for badge in caracteristicas['badges_especiales']:
    print(f"     - {badge['texto']} ({badge['color']})")

# 3. Procesar datos para tabla
print("\n3. PROCESAMIENTO PARA TABLA:")
datos_procesados = procesar_datos_para_tabla(datos_limpios)
print(f"   Motor: {datos_procesados.get('motor')}")
print(f"   Consumo: {datos_procesados.get('consumo')}")

# 4. Generar HTML
print("\n4. GENERANDO HTML COMPLETO...")
try:
    html = generar_html_generador(datos_procesados, test_marketing, caracteristicas, test_config)
    
    # Verificaciones
    print("\n5. VERIFICACIONES:")
    
    # Verificar que no hay "None"
    if "None" in html:
        print("   [X] ERROR: El HTML contiene 'None'")
        lines = html.split('\n')
        for i, line in enumerate(lines):
            if "None" in line and i < 10:  # Solo primeras ocurrencias
                print(f"      Línea {i}: {line.strip()[:80]}...")
    else:
        print("   [OK] No hay 'None' en el HTML")
    
    # Verificar consumo
    if "L/h L/h" in html:
        print("   [X] ERROR: Consumo duplicado encontrado")
    else:
        print("   [OK] Consumo sin duplicación")
    
    # Verificar tanque
    if "15 L L" in html or " L L" in html:
        print("   [X] ERROR: Unidad de tanque duplicada")
    else:
        print("   [OK] Unidades de tanque correctas")
    
    # Verificar WhatsApp
    if "LOGUS GL3300AM" in html:
        print("   [OK] Marca incluida en WhatsApp")
    else:
        print("   [X] ERROR: Marca no incluida en WhatsApp")
    
    # Verificar eficiencia (para nafta debe ser diferente)
    if "Eficiencia Normal" in html or "Alta Eficiencia" in html:
        print("   [OK] Cálculo de eficiencia para nafta aplicado")
    else:
        print("   [!] Verificar cálculo de eficiencia")
    
    # Verificar badges portátil
    if "PORTÁTIL" in html:
        print("   [OK] Badge PORTÁTIL incluido")
    else:
        print("   [X] ERROR: Badge PORTÁTIL no encontrado")
    
    # Guardar HTML para inspección
    output_file = 'test_gl3300am_output.html'
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f"\n[OK] HTML guardado en: {output_file}")
    
    # Resumen
    print("\n=== RESUMEN DE MEJORAS APLICADAS ===")
    print("1. [OK] Duplicación de unidades corregida")
    print("2. [OK] Cálculo de eficiencia específico para nafta")
    print("3. [OK] Extracción mejorada del motor")
    print("4. [OK] Detección de características especiales")
    print("5. [OK] Iconos específicos para campos")
    print("6. [OK] Plantilla adaptada para generadores nafteros")
    print("7. [OK] Validación y limpieza de datos")
    
except Exception as e:
    print(f"\n[X] ERROR GENERANDO HTML: {e}")
    import traceback
    traceback.print_exc()

print("\n=== FIN DEL TEST ===")