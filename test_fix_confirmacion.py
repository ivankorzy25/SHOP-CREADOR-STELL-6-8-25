#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test de confirmación que el error está solucionado
"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from ai_generator.premium_generator import extraer_info_tecnica

# Simular datos de producto como vienen de la BD
producto_test = {
    'Descripción': 'GENERADOR NAFTERO GL3300AM',
    'Marca': 'LOGUS',
    'Modelo': 'GL3300AM',
    'Familia': 'GENERADOR',
    'Potencia': '3.3 KVA',
    'Tensión': '220V',
    'Motor': 'Motor 7HP',
    'Peso_(kg)': '41',
    'URL_PDF': 'gl3300am.pdf'
}

print("=== TEST DE SOLUCION DEL ERROR ===")
print("\nProbando funcion extraer_info_tecnica:")

try:
    # Llamar a la función con un solo argumento (como espera ai_handler.py)
    resultado = extraer_info_tecnica(producto_test)
    
    print("[OK] La funcion acepta un solo argumento correctamente")
    print("\nDatos extraidos:")
    for key, value in resultado.items():
        print(f"  {key}: {value}")
    
    print("\n=== RESULTADO: ERROR SOLUCIONADO ===")
    print("La funcion extraer_info_tecnica ahora se importa desde premium_generator.py")
    print("y acepta correctamente un solo argumento (el diccionario del producto)")
    
except TypeError as e:
    print(f"[X] ERROR: {e}")
    print("La funcion todavia espera mas argumentos")
except Exception as e:
    print(f"[X] ERROR INESPERADO: {e}")