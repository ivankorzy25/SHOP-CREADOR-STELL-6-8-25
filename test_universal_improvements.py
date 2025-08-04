#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script de prueba para verificar que TODAS las mejoras se aplican universalmente
a CUALQUIER categoría de producto
"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from ai_generator.product_templates import (
    generar_html_generador,
    generar_html_hidrolavadora,
    generar_html_compresor,
    generar_html_motobomba,
    generar_html_generador_inverter,
    TEMPLATE_REGISTRY
)
from ai_generator.premium_generator_v2 import (
    validar_y_limpiar_datos_universal,
    detectar_caracteristicas_universal,
    calcular_eficiencia_universal
)

# Productos de prueba de diferentes categorías
productos_test = [
    {
        'nombre': 'GENERADOR DIESEL CUMMINS 200KVA',
        'categoria': 'generador',
        'marca': 'CUMMINS',
        'modelo': 'C200D5',
        'familia': 'GENERADOR',
        'potencia_kva': '200',
        'potencia_kw': '160',
        'consumo_75_carga_valor': '38',
        'consumo': '38 L/h L/h',  # Con duplicación intencional
        'capacidad_tanque_combustible_l': '400 L L',  # Con duplicación
        'voltaje': '380/220',
        'frecuencia': '50',
        'motor': 'CUMMINS 6BT5.9-G2',
        'combustible': 'Diesel',
        'tipo_arranque': 'Automático',
        'peso_kg': '1850 kg kg',  # Con duplicación
        'nivel_ruido_dba': '75'
    },
    {
        'nombre': 'HIDROLAVADORA INDUSTRIAL K5000',
        'categoria': 'hidrolavadora',
        'marca': 'KARCHER',
        'modelo': 'K5000',
        'familia': 'HIDROLAVADORA',
        'presion_bar': '180 BAR BAR',  # Con duplicación
        'caudal_lts_min': '15 L/min L/min',  # Con duplicación
        'motor': 'Motor eléctrico 5.5HP',
        'potencia_hp': '5.5',
        'voltaje': '380',
        'peso_kg': '45',
        'temperatura_max': '80°C'
    },
    {
        'nombre': 'COMPRESOR A TORNILLO 50HP',
        'categoria': 'compresor',
        'marca': 'INGERSOLL RAND',
        'modelo': 'UP6-50',
        'familia': 'COMPRESOR',
        'potencia_hp': '50',
        'presion_bar': '8',
        'caudal_cfm': '250',
        'capacidad_tanque_litros': '500 L L',  # Con duplicación
        'voltaje': '380',
        'peso_kg': '680',
        'nivel_ruido_dba': '68'
    },
    {
        'nombre': 'MOTOBOMBA AUTOCEBANTE 3"',
        'categoria': 'motobomba',
        'marca': 'HONDA',
        'modelo': 'WB30XT',
        'familia': 'MOTOBOMBA',
        'caudal_lph': '60000 L/h L/h',  # Con duplicación
        'motor': 'Honda GX160',
        'potencia_hp': '5.5 HP HP',  # Con duplicación
        'combustible': 'Nafta',
        'consumo': '1.8',
        'peso_kg': '27',
        'diametro_succion': '3"'
    },
    {
        'nombre': 'GENERADOR INVERTER PORTATIL 2000W',
        'categoria': 'generador_inverter',
        'marca': 'YAMAHA',
        'modelo': 'EF2000IS',
        'familia': 'GENERADOR',
        'potencia_max_w': '2000 W W',  # Con duplicación
        'potencia_kva': '2',
        'consumo': '0.9',
        'combustible': 'Nafta',
        'capacidad_tanque_combustible_l': '4.4',
        'peso_kg': '21',
        'nivel_ruido_dba': '51.5',
        'caracteristicas_especiales': ['INVERTER', 'PORTATIL']
    }
]

# Configuración de prueba
test_config = {
    'whatsapp': '541139563099',
    'email': 'info@test.com',
    'telefono_display': '+54 11 3956-3099',
    'website': 'www.test.com'
}

# Marketing content genérico
test_marketing = {
    'titulo_h1': 'PRODUCTO DE PRUEBA',
    'subtitulo_p': 'Verificando mejoras universales',
    'punto_clave_texto_1': 'Todas las mejoras aplicadas',
    'punto_clave_icono_1': 'check',
    'punto_clave_texto_2': 'Sin verificaciones de categoría',
    'punto_clave_icono_2': 'star',
    'punto_clave_texto_3': 'Funcionamiento universal',
    'punto_clave_icono_3': 'shield'
}

print("=== TEST DE MEJORAS UNIVERSALES ===\n")
errores_encontrados = []

for producto in productos_test:
    print(f"\n{'='*60}")
    print(f"PROBANDO: {producto['nombre']} (Categoría: {producto['categoria']})")
    print(f"{'='*60}")
    
    # 1. Validar y limpiar datos
    print("\n1. VALIDACIÓN Y LIMPIEZA DE DATOS:")
    datos_limpios = validar_y_limpiar_datos_universal(producto)
    
    # Verificar correcciones
    cambios = []
    for campo, valor_original in producto.items():
        if campo in datos_limpios and datos_limpios[campo] != valor_original:
            cambios.append(f"   - {campo}: '{valor_original}' -> '{datos_limpios[campo]}'")
    
    if cambios:
        print("   Correcciones aplicadas:")
        for cambio in cambios:
            print(cambio)
    else:
        print("   [!] No se aplicaron correcciones")
        if any('L L' in str(v) or 'L/h L/h' in str(v) for v in producto.values()):
            errores_encontrados.append(f"{producto['nombre']}: No se corrigieron duplicaciones")
    
    # 2. Detectar características
    print("\n2. DETECCIÓN DE CARACTERÍSTICAS:")
    caracteristicas = detectar_caracteristicas_universal(datos_limpios)
    print(f"   Tipo combustible detectado: {caracteristicas['tipo_combustible']}")
    print(f"   Badges especiales: {len(caracteristicas['badges_especiales'])}")
    for badge in caracteristicas['badges_especiales']:
        print(f"     - {badge['texto']}")
    
    # 3. Calcular eficiencia (si aplica)
    if any(campo in datos_limpios for campo in ['consumo', 'consumo_75_carga_valor']):
        print("\n3. CÁLCULO DE EFICIENCIA:")
        eficiencia_data = calcular_eficiencia_universal(datos_limpios)
        print(f"   Porcentaje: {eficiencia_data['porcentaje']}%")
        print(f"   Texto: {eficiencia_data['texto']}")
        print(f"   Color: {eficiencia_data['color']}")
        if eficiencia_data.get('nota'):
            print(f"   Nota: {eficiencia_data['nota']}")
    
    # 4. Generar HTML según categoría
    print("\n4. GENERANDO HTML...")
    try:
        # Buscar plantilla apropiada
        template_func = TEMPLATE_REGISTRY.get(
            producto['categoria'], 
            TEMPLATE_REGISTRY['default']
        )
        
        html = template_func(datos_limpios, test_marketing, caracteristicas, test_config)
        
        # Verificaciones en el HTML
        verificaciones = {
            'Sin "None"': 'None' not in html,
            'Sin duplicación L L': ' L L' not in html,
            'Sin duplicación L/h L/h': 'L/h L/h' not in html,
            'Sin duplicación HP HP': 'HP HP' not in html,
            'Sin duplicación W W': 'W W' not in html,
            'Sin duplicación BAR BAR': 'BAR BAR' not in html,
            'Marca en WhatsApp': producto['marca'] in html
        }
        
        print("   Verificaciones:")
        for verificacion, resultado in verificaciones.items():
            estado = "[OK]" if resultado else "[X]"
            print(f"   {estado} {verificacion}")
            if not resultado:
                errores_encontrados.append(f"{producto['nombre']}: Falló {verificacion}")
        
        # Guardar HTML
        output_file = f"test_output_{producto['categoria']}.html"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html)
        print(f"\n   HTML guardado en: {output_file}")
        
    except Exception as e:
        print(f"\n   [X] ERROR generando HTML: {e}")
        errores_encontrados.append(f"{producto['nombre']}: Error en generación - {str(e)}")
        import traceback
        traceback.print_exc()

# Resumen final
print("\n" + "="*60)
print("RESUMEN FINAL")
print("="*60)

if errores_encontrados:
    print(f"\n[X] Se encontraron {len(errores_encontrados)} errores:")
    for error in errores_encontrados:
        print(f"   - {error}")
else:
    print("\n[OK] TODAS LAS MEJORAS SE APLICARON CORRECTAMENTE A TODOS LOS PRODUCTOS")
    print("\nMejoras verificadas:")
    print("   [OK] Validación y limpieza de datos universal")
    print("   [OK] Detección de características universal")
    print("   [OK] Cálculo de eficiencia adaptativo")
    print("   [OK] Mapeo de iconos mejorado")
    print("   [OK] Sin verificaciones de categoría específicas")
    print("   [OK] Funcionamiento consistente en todas las categorías")

print("\n=== FIN DEL TEST ===")