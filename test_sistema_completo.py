#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test exhaustivo del sistema completo reescrito
Verifica que TODOS los productos se generen perfectamente
"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from ai_generator.product_templates import generar_html_universal
from ai_generator.data_processor import UniversalDataProcessor
from ai_generator.efficiency_calculator import UniversalEfficiencyCalculator
from ai_generator.feature_detector import UniversalFeatureDetector

# Casos de prueba con diferentes tipos de productos
productos_test = [
    {
        'nombre': 'GENERADOR NAFTERO GL3300AM',
        'marca': 'LOGUS',
        'modelo': 'GL3300AM',
        'familia': 'GENERADOR',
        'categoria_producto': 'generador',
        
        # Datos con problemas originales
        'potencia_kva': '3.3',
        'consumo': '1.36 L/h L/h',  # Duplicación
        'capacidad_tanque_combustible_l': '15 L L',  # Duplicación
        'peso_kg': '41 kg kg',  # Duplicación
        'motor': 'Motor 7HP',
        'combustible': 'Nafta',
        'autonomia_horas': '8',
        'autonomia_horas_unidad': 'horas',  # NO debe aparecer
        'voltaje_v_unidad': 'V',  # NO debe aparecer
        'nivel_ruido_dba': '68',
        'tipo_arranque': 'Manual',
        'voltaje': '220',
        'frecuencia': '50',
        'cilindrada_cc': '210'
    },
    {
        'nombre': 'GENERADOR DIESEL GD12000',
        'marca': 'POWERGEN',
        'modelo': 'GD12000',
        'familia': 'GENERADOR',
        'categoria_producto': 'generador',
        
        'potencia_kva': '12',
        'consumo': '3.2',  # Sin unidad
        'capacidad_tanque': '45',  # Sin unidad
        'motor': 'Cummins 4BT',
        'combustible': 'Diesel',
        'peso_kg': '350',
        'nivel_ruido_dba': '75 dBA dBA',  # Duplicación
        'tipo_arranque': 'Eléctrico',
        'bateria': '12V 45Ah',
        'panel_control': 'Digital',
        'certificaciones': 'ISO 9001, CE'
    },
    {
        'nombre': 'MOTOBOMBA MB550',
        'marca': 'FLOWMAX',
        'modelo': 'MB550',
        'familia': 'BOMBA',
        'categoria_producto': 'bomba',
        
        'potencia_hp': '5.5',
        'caudal': '550 L/min L/min',  # Duplicación
        'motor': 'Motor Motor 5.5HP',  # Redundancia
        'combustible': 'Nafta',
        'diametro_succion': '2"',
        'presion_max_bar': '6 BAR BAR',  # Duplicación
        'peso': '28',  # Sin unidad
        'arranque': 'Manual'
    },
    {
        'nombre': 'COMPRESOR INDUSTRIAL CI300',
        'marca': 'AIRTECH',
        'modelo': 'CI300',
        'familia': 'COMPRESOR',
        'categoria_producto': 'compresor',
        
        'potencia_hp': '3',
        'presion': '8',  # Sin unidad
        'caudal_lts_min': '300 L/min',
        'capacidad_tanque_l': '100 L L',  # Duplicación
        'motor': '3HP',  # Solo potencia
        'voltaje': '380',
        'fases': 'Trifásico',
        'nivel_sonoro_dba': '72',
        'peso_kg': '85'
    }
]

# Marketing content de ejemplo
marketing_test = {
    'titulo_h1': 'Producto de Alta Calidad',
    'subtitulo_p': 'Solución confiable para sus necesidades',
    'punto_clave_texto_1': 'Alta eficiencia y rendimiento',
    'punto_clave_icono_1': 'lightning',
    'punto_clave_texto_2': 'Construcción robusta y duradera',
    'punto_clave_icono_2': 'shield',
    'punto_clave_texto_3': 'Fácil mantenimiento',
    'punto_clave_icono_3': 'tools',
    'app_texto_1': 'Uso industrial',
    'app_icono_1': 'factory',
    'app_texto_2': 'Aplicaciones comerciales',
    'app_icono_2': 'briefcase'
}

# Configuración
config_test = {
    'whatsapp': '541139563099',
    'email': 'info@test.com',
    'telefono_display': '+54 11 3956-3099',
    'website': 'www.test.com'
}

print("=== TEST EXHAUSTIVO DEL SISTEMA COMPLETO ===\n")

# Probar cada producto
for idx, producto in enumerate(productos_test, 1):
    print(f"\n{'='*60}")
    print(f"PRODUCTO {idx}: {producto['nombre']}")
    print('='*60)
    
    # 1. Probar limpieza de datos
    print("\n1. LIMPIEZA DE DATOS:")
    datos_limpios = UniversalDataProcessor.clean_all_data(producto)
    
    # Verificar campos críticos
    verificaciones = {
        'consumo': 'L/h L/h' not in str(datos_limpios.get('consumo', '')),
        'capacidad_tanque': ' L L' not in str(datos_limpios.get('capacidad_tanque_combustible_l', '')),
        'peso': 'kg kg' not in str(datos_limpios.get('peso_kg', '')),
        'presion': 'BAR BAR' not in str(datos_limpios.get('presion_max_bar', '')),
        'nivel_ruido': 'dBA dBA' not in str(datos_limpios.get('nivel_ruido_dba', '')),
        'caudal': 'L/min L/min' not in str(datos_limpios.get('caudal', ''))
    }
    
    for campo, ok in verificaciones.items():
        print(f"   {'[OK]' if ok else '[X]'} {campo} sin duplicación")
    
    # Verificar que campos de unidad NO estén presentes
    campos_unidad = ['autonomia_horas_unidad', 'voltaje_v_unidad', 'consumo_unidad']
    campos_unidad_presentes = [c for c in campos_unidad if c in datos_limpios]
    if campos_unidad_presentes:
        print(f"   [X] Campos de unidad presentes: {campos_unidad_presentes}")
    else:
        print("   [OK] No hay campos de unidad")
    
    # 2. Probar detección de características
    print("\n2. DETECCIÓN DE CARACTERÍSTICAS:")
    caracteristicas = UniversalFeatureDetector.detect_all(datos_limpios)
    print(f"   Tipo producto: {caracteristicas['tipo_producto']}")
    print(f"   Tipo combustible: {caracteristicas['tipo_combustible']}")
    print(f"   Es portátil: {caracteristicas['es_portatil']}")
    print(f"   Badges detectados: {len(caracteristicas['badges_especiales'])}")
    for badge in caracteristicas['badges_especiales']:
        print(f"     - {badge['texto']}")
    
    # 3. Probar cálculo de eficiencia
    print("\n3. CÁLCULO DE EFICIENCIA:")
    eficiencia = UniversalEfficiencyCalculator.calculate(datos_limpios)
    print(f"   Porcentaje: {eficiencia['porcentaje']}%")
    print(f"   Texto: {eficiencia['texto']}")
    print(f"   Color: {eficiencia['color']}")
    if eficiencia.get('consumo_por_kw', 0) > 0:
        print(f"   Consumo por KW: {eficiencia['consumo_por_kw']} L/h")
    
    # 4. Generar HTML
    print("\n4. GENERACIÓN DE HTML:")
    try:
        html = generar_html_universal(producto, marketing_test, config_test)
        
        # Verificaciones en el HTML
        verificaciones_html = {
            'Sin L/h L/h': 'L/h L/h' not in html,
            'Sin L L': ' L L' not in html,
            'Sin kg kg': 'kg kg' not in html,
            'Sin BAR BAR': 'BAR BAR' not in html,
            'Sin dBA dBA': 'dBA dBA' not in html,
            'Sin Motor Motor': 'Motor Motor' not in html,
            'Sin campos _unidad': not any(f'{campo}' in html for campo in campos_unidad),
            'Tabla presente': '<table' in html,
            'WhatsApp presente': 'wa.me' in html,
            'Badges presentes': all(badge['texto'] in html for badge in caracteristicas['badges_especiales'][:2])
        }
        
        for verificacion, resultado in verificaciones_html.items():
            print(f"   {'[OK]' if resultado else '[X]'} {verificacion}")
        
        # Guardar HTML
        filename = f'test_output_{producto["modelo"].lower()}.html'
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(html)
        print(f"   HTML guardado en: {filename}")
        
    except Exception as e:
        print(f"   [X] ERROR: {e}")
        import traceback
        traceback.print_exc()

# Test de integración con el procesador universal
print(f"\n\n{'='*60}")
print("TEST DE INTEGRACIÓN")
print('='*60)

# Producto con TODOS los problemas conocidos
producto_problematico = {
    'nombre': 'PRODUCTO TEST COMPLETO',
    'marca': 'TEST',
    'modelo': 'TC-001',
    'potencia_kva': '5.5 KVA KVA',  # Duplicación en valor
    'consumo': '2.5 L/h L/h',  # Duplicación
    'consumo_unidad': 'L/h',  # Campo unidad
    'capacidad_tanque_combustible_l': '25 L L',  # Duplicación
    'capacidad_tanque_unidad': 'L',  # Campo unidad
    'peso_kg': '120 kg kg',  # Duplicación
    'peso_unidad': 'kg',  # Campo unidad
    'motor': 'Motor Motor 10HP',  # Redundancia
    'motor_unidad': 'HP',  # Campo unidad
    'autonomia_horas': '10 horas horas',  # Duplicación
    'autonomia_horas_unidad': 'horas',  # Campo unidad
    'nivel_ruido_dba': '70 dBA dBA',  # Duplicación
    'eficiencia_data': {  # Datos complejos
        'porcentaje': 85,
        'texto': 'Alta Eficiencia'
    }
}

print("\nProcesando producto con TODOS los problemas...")
datos_limpios = UniversalDataProcessor.clean_all_data(producto_problematico)

# Verificar limpieza completa
print("\nVERIFICACIONES:")
problemas_resueltos = {
    'Potencia sin duplicación KVA': 'KVA KVA' not in str(datos_limpios.get('potencia_kva', '')),
    'Consumo sin duplicación L/h': 'L/h L/h' not in str(datos_limpios.get('consumo', '')),
    'Tanque sin duplicación L': ' L L' not in str(datos_limpios.get('capacidad_tanque_combustible_l', '')),
    'Peso sin duplicación kg': 'kg kg' not in str(datos_limpios.get('peso_kg', '')),
    'Motor sin redundancia': 'Motor Motor' not in str(datos_limpios.get('motor', '')),
    'Autonomía sin duplicación': 'horas horas' not in str(datos_limpios.get('autonomia_horas', '')),
    'Ruido sin duplicación': 'dBA dBA' not in str(datos_limpios.get('nivel_ruido_dba', '')),
    'Sin campo consumo_unidad': 'consumo_unidad' not in datos_limpios,
    'Sin campo capacidad_tanque_unidad': 'capacidad_tanque_unidad' not in datos_limpios,
    'Sin campo peso_unidad': 'peso_unidad' not in datos_limpios,
    'Sin campo motor_unidad': 'motor_unidad' not in datos_limpios,
    'Sin campo autonomia_horas_unidad': 'autonomia_horas_unidad' not in datos_limpios,
    'eficiencia_data excluido': 'eficiencia_data' not in datos_limpios
}

todos_ok = True
for verificacion, resultado in problemas_resueltos.items():
    print(f"{'[OK]' if resultado else '[X]'} {verificacion}")
    if not resultado:
        todos_ok = False

print(f"\n{'='*60}")
if todos_ok:
    print("[OK] TODOS LOS TESTS PASARON - EL SISTEMA FUNCIONA CORRECTAMENTE")
else:
    print("[ERROR] ALGUNOS TESTS FALLARON - REVISAR IMPLEMENTACIÓN")
print('='*60)

print("\n=== FIN DEL TEST EXHAUSTIVO ===")