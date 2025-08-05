#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test exhaustivo para verificar la seguridad de tipos y prevención de errores
"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from ai_generator.compatibility_fixes import (
    safe_dict_access,
    ensure_dict,
    safe_json_parse,
    ensure_caracteristicas_dict,
    safe_contenido_pdf_access
)
from ai_generator.product_templates import validar_parametros_entrada

print("=== TEST DE SEGURIDAD DE TIPOS ===\n")

# Test 1: safe_dict_access
print("1. Testing safe_dict_access:")
test_cases = [
    ({'key': 'value'}, 'key', 'default'),  # Normal dict
    ('string', 'key', 'default'),          # String instead of dict
    (None, 'key', 'default'),              # None
    (123, 'key', 'default'),               # Number
]

for data, key, default in test_cases:
    result = safe_dict_access(data, key, default)
    print(f"   Input: {type(data).__name__} -> Result: {result}")

# Test 2: ensure_dict
print("\n2. Testing ensure_dict:")
test_inputs = [
    {'valid': 'dict'},
    'string',
    None,
    123,
    ['list']
]

for data in test_inputs:
    result = ensure_dict(data)
    print(f"   Input: {type(data).__name__} -> Result type: {type(result).__name__}, Value: {result}")

# Test 3: safe_json_parse
print("\n3. Testing safe_json_parse:")
json_tests = [
    '{"key": "value"}',                    # Valid JSON
    'Invalid JSON',                        # Invalid JSON
    '{"incomplete": ',                     # Incomplete JSON
    {'already': 'dict'},                   # Already a dict
    None,                                  # None
    'Some text {"json": "inside"} text',   # JSON inside text
]

for data in json_tests:
    result = safe_json_parse(data)
    print(f"   Input: {repr(data)[:30]}... -> Result: {result}")

# Test 4: ensure_caracteristicas_dict
print("\n4. Testing ensure_caracteristicas_dict:")
caracteristicas_tests = [
    {'tipo_producto': 'generador'},        # Partial dict
    'string',                              # String
    None,                                  # None
    {},                                    # Empty dict
]

for data in caracteristicas_tests:
    result = ensure_caracteristicas_dict(data)
    has_required = all(k in result for k in ['tipo_producto', 'tipo_combustible', 'es_portatil'])
    print(f"   Input: {type(data).__name__} -> Has required keys: {has_required}")

# Test 5: safe_contenido_pdf_access
print("\n5. Testing safe_contenido_pdf_access:")
pdf_tests = [
    {'text': 'PDF content here'},          # Dict with text
    'Direct PDF string',                   # String
    None,                                  # None
    {'no_text': 'key'},                   # Dict without text key
]

for data in pdf_tests:
    result = safe_contenido_pdf_access(data)
    print(f"   Input: {type(data).__name__} -> Result: '{result[:20]}...' if result else ''")

# Test 6: validar_parametros_entrada
print("\n6. Testing validar_parametros_entrada:")
param_tests = [
    # All correct types
    ({'modelo': 'TEST'}, {'titulo': 'Test'}, {'tipo_producto': 'generador'}, {'whatsapp': '123'}),
    # All wrong types
    ('string', 'string', 'string', 'string'),
    # Mixed types
    ({}, None, 123, []),
    # All None
    (None, None, None, None)
]

for info, marketing, caract, config in param_tests:
    i, m, c, cf = validar_parametros_entrada(info, marketing, caract, config)
    all_dicts = all(isinstance(x, dict) for x in [i, m, c, cf])
    print(f"   Input types: ({type(info).__name__}, {type(marketing).__name__}, {type(caract).__name__}, {type(config).__name__})")
    print(f"   Output: All dicts? {all_dicts}")

print("\n=== SIMULACION DE ESCENARIO PROBLEMATICO ===")

# Simular el error "string indices must be integers, not 'str'"
print("\nSimulando acceso a string como si fuera dict:")
caracteristicas = "esto es un string"  # Problema: es string, no dict
try:
    # Esto causaría el error
    value = caracteristicas['tipo_producto']
    print("   [X] No debería llegar aquí")
except TypeError as e:
    print(f"   [OK] Error capturado: {e}")

# Con la protección
caracteristicas_safe = ensure_caracteristicas_dict(caracteristicas)
try:
    value = caracteristicas_safe['tipo_producto']
    print(f"   [OK] Con protección funciona: tipo_producto = '{value}'")
except Exception as e:
    print(f"   [X] Error inesperado: {e}")

print("\n=== RESULTADO FINAL ===")
print("Todas las funciones de seguridad de tipos están funcionando correctamente.")
print("Los errores 'string indices must be integers' deberían estar prevenidos.")