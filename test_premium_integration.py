#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test de integración del generador premium restaurado
"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from ai_generator.product_templates import generar_html_universal
from ai_generator.data_processor import UniversalDataProcessor

print("=== TEST DE INTEGRACIÓN DEL GENERADOR PREMIUM ===\n")

# Datos de prueba del GL3300AM
info_test = {
    'nombre': 'Generador Eléctrico LÜSQTOFF GL3300AM',
    'marca': 'LÜSQTOFF',
    'modelo': 'GL3300AM',
    'familia': 'GENERADORES_NAFTA',
    'potencia': '3000W',
    'motor': 'Lüsqtoff LC168FB-2 7HP',
    'consumo': '1.36 L/h',
    'tanque': '15L',
    'autonomia': '11 horas',
    'arranque': 'Manual + Eléctrico',
    'descripcion': 'Generador monofásico de 3KVA con motor de 7HP'
}

marketing_content_test = {
    'titulo_h1': 'Generador Eléctrico LÜSQTOFF GL3300AM - 3000W con Arranque Dual',
    'subtitulo_p': 'Potencia confiable para tu hogar y trabajo con tecnología alemana',
    'descripcion_marketing': 'El generador GL3300AM combina potencia, eficiencia y confiabilidad.',
    'punto_clave_icono_1': 'power',
    'punto_clave_texto_1': '3000W de potencia máxima',
    'punto_clave_icono_2': 'fuel',
    'punto_clave_texto_2': '11 horas de autonomía',
    'punto_clave_icono_3': 'shield',
    'punto_clave_texto_3': 'Protección contra sobrecargas',
    'caracteristica_titulo_1': 'Motor Potente',
    'caracteristica_descripcion_1': 'Motor Lüsqtoff 7HP de alta eficiencia',
    'caracteristica_titulo_2': 'Arranque Dual',
    'caracteristica_descripcion_2': 'Sistema manual y eléctrico para mayor comodidad',
    'caracteristica_titulo_3': 'Panel Digital',
    'caracteristica_descripcion_3': 'Indicadores LED para monitoreo en tiempo real',
    'app_icono_1': 'home',
    'app_texto_1': 'Respaldo energético para el hogar',
    'app_icono_2': 'tool',
    'app_texto_2': 'Herramientas eléctricas en obra',
    'app_icono_3': 'camping',
    'app_texto_3': 'Camping y actividades al aire libre',
    'ventaja_titulo_1': 'Tecnología Alemana',
    'ventaja_descripcion_1': 'Diseño y calidad alemana garantizada',
    'ventaja_titulo_2': 'Bajo Consumo',
    'ventaja_descripcion_2': 'Solo 1.36 L/h para máxima eficiencia',
    'ventaja_titulo_3': 'Fácil Mantenimiento',
    'ventaja_descripcion_3': 'Acceso simple a todos los componentes',
}

config_test = {
    'whatsapp': '541139563099',
    'email': 'info@generadores.ar',
    'telefono_display': '+54 11 3956-3099',
    'website': 'www.generadores.ar'
}

print("1. Procesando datos con UniversalDataProcessor...")
datos_limpios = UniversalDataProcessor.clean_all_data(info_test)
print(f"   Campos limpios: {list(datos_limpios.keys())}")

print("\n2. Generando HTML con el generador premium restaurado...")
try:
    html_resultado = generar_html_universal(info_test, marketing_content_test, config_test)
    
    # Verificar que contiene elementos clave del diseño premium
    verificaciones = [
        ('CSS con animaciones', '@keyframes fadeInUp' in html_resultado),
        ('Tabla amarilla premium', 'background: linear-gradient(135deg, #FFD700' in html_resultado),
        ('Gráfico de eficiencia', 'Eficiencia Energética' in html_resultado),
        ('Badges especiales', 'badge-especial' in html_resultado),
        ('Sección de ventajas', 'ventajas-grid' in html_resultado),
        ('CTA WhatsApp animado', 'cta-whatsapp' in html_resultado),
        ('Footer premium', 'footer-premium' in html_resultado),
        ('Cards con hover', ':hover' in html_resultado),
        ('Decoraciones visuales', 'decoracion-' in html_resultado)
    ]
    
    print("\n3. Verificando elementos del diseño premium:")
    todos_presentes = True
    for nombre, presente in verificaciones:
        estado = "[OK]" if presente else "[X]"
        print(f"   {estado} {nombre}")
        if not presente:
            todos_presentes = False
    
    # Guardar resultado para inspección
    output_file = Path('test_output_premium.html')
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_resultado)
    
    print(f"\n4. HTML guardado en: {output_file}")
    print(f"   Tamaño: {len(html_resultado):,} caracteres")
    
    if todos_presentes:
        print("\n[EXITO] El generador premium está correctamente integrado")
    else:
        print("\n[ADVERTENCIA] Algunos elementos premium no se encontraron")
        
except Exception as e:
    print(f"\n[ERROR] {e}")
    import traceback
    traceback.print_exc()

print("\n=== TEST COMPLETADO ===")