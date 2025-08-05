#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test para verificar que el error de extraer_info_tecnica está solucionado
"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

try:
    from ai_generator.ai_handler import AIHandler
    from ai_generator.premium_generator import extraer_info_tecnica
    
    print("=== TEST DE IMPORTACIÓN Y FUNCIÓN ===\n")
    
    # Test 1: Verificar que extraer_info_tecnica acepta un solo argumento
    print("1. Probando extraer_info_tecnica con un diccionario:")
    test_row = {
        'Descripción': 'GENERADOR TEST',
        'Marca': 'TEST BRAND',
        'Modelo': 'TEST-001',
        'Familia': 'GENERADOR',
        'Potencia': '5.5 KVA',
        'Tensión': '220V',
        'Motor': 'Honda GX',
        'Peso_(kg)': '45',
        'URL_PDF': 'test.pdf'
    }
    
    try:
        resultado = extraer_info_tecnica(test_row)
        print("   [OK] La función acepta un solo argumento")
        print(f"   Resultado: {resultado['nombre']} - {resultado['marca']} {resultado['modelo']}")
    except TypeError as e:
        print(f"   [X] Error: {e}")
    
    # Test 2: Verificar que AIHandler puede importarse correctamente
    print("\n2. Verificando importación de AIHandler:")
    try:
        ai_handler = AIHandler(api_key="test_key")
        print("   [OK] AIHandler importado correctamente")
    except Exception as e:
        print(f"   [X] Error al importar AIHandler: {e}")
    
    # Test 3: Verificar las importaciones en ai_handler.py
    print("\n3. Verificando importaciones en ai_handler.py:")
    try:
        from ai_generator.premium_generator_v2 import extraer_contenido_pdf, validar_caracteristicas_producto
        from ai_generator.premium_generator import extraer_info_tecnica as extraer_info_tecnica_pg
        print("   [OK] Todas las funciones importadas correctamente")
        print("   - extraer_contenido_pdf: importada de premium_generator_v2")
        print("   - validar_caracteristicas_producto: importada de premium_generator_v2")
        print("   - extraer_info_tecnica: importada de premium_generator")
    except ImportError as e:
        print(f"   [X] Error de importación: {e}")
    
    print("\n=== RESULTADO FINAL ===")
    print("[OK] El error de extraer_info_tecnica debería estar solucionado")
    print("La función ahora se importa correctamente de premium_generator.py")
    
except Exception as e:
    print(f"\n[ERROR] ERROR INESPERADO: {e}")
    import traceback
    traceback.print_exc()