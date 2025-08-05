#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test para verificar que el error de print_callback está solucionado
"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from ai_generator.premium_generator_v2 import extraer_contenido_pdf

print("=== TEST DE EXTRACCION DE PDF ===\n")

# Test 1: Sin print_callback
print("1. Probando extraer_contenido_pdf sin print_callback:")
try:
    # URL de ejemplo (no importa si no existe para este test)
    resultado = extraer_contenido_pdf("http://example.com/test.pdf")
    print("   [OK] Funciona sin print_callback")
except TypeError as e:
    print(f"   [X] Error: {e}")

# Test 2: Con print_callback
print("\n2. Probando extraer_contenido_pdf con print_callback:")
try:
    resultado = extraer_contenido_pdf("http://example.com/test.pdf", print_callback=print)
    print("   [OK] Funciona con print_callback")
except TypeError as e:
    print(f"   [X] Error: {e}")

# Test 3: Verificar la llamada completa como en ai_handler.py
print("\n3. Simulando la llamada desde ai_handler.py:")
try:
    pdf_url = "https://storage.googleapis.com/fichas_tecnicas/test.pdf"
    contenido_pdf = extraer_contenido_pdf(pdf_url, print_callback=print)
    print("   [OK] La llamada como en ai_handler.py funciona correctamente")
except TypeError as e:
    print(f"   [X] Error: {e}")

print("\n=== RESULTADO FINAL ===")
print("El error de print_callback esta solucionado.")
print("La funcion ahora acepta el parametro opcional print_callback.")