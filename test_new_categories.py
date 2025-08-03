"""
Script de prueba para las nuevas categorías
"""
from ai_generator import AIHandler
from ai_generator.prompt_manager import PromptManager

# Datos de prueba para cada categoría
test_products = {
    'motor_estacionario': {
        'nombre': 'Motor Estacionario Logus 188F',
        'marca': 'Logus',
        'modelo': '188F',
        'potencia_hp': '13',
        'tipo_arranque': 'Manual',
        'eje_salida': 'Horizontal',
        'familia': 'Motores Estacionarios'
    },
    'equipo_construccion': {
        'nombre': 'Vibroapisonador RM80H',
        'marca': 'Logus',
        'modelo': 'RM80H',
        'tipo_equipo_construccion': 'vibroapisonador',
        'motor': 'Honda 5.5HP',
        'frecuencia_hz': '48',
        'fuerza_impacto_kg': '1100',
        'familia': 'Construcción'
    },
    'generador_inverter': {
        'nombre': 'Generador Inverter GI3700 SILENT',
        'marca': 'Logus',
        'modelo': 'GI3700',
        'potencia_max_w': '3500',
        'motor': '4.5 HP',
        'tipo_arranque': 'Eléctrico',
        'familia': 'Generadores Inverter'
    }
}

# Probar cada categoría
ai_handler = AIHandler()
for categoria, producto in test_products.items():
    print(f"\n{'='*50}")
    print(f"Probando categoría: {categoria}")
    print(f"{'='*50}")
    
    # Simular que el producto tiene esta categoría
    producto['categoria_producto'] = categoria
    
    try:
        html = ai_handler.generate_description(
            product_info=producto,
            config={'whatsapp': '541139563099', 'email': 'info@generadores.ar'}
        )
        
        # Guardar resultado
        with open(f'test_output_{categoria}.html', 'w', encoding='utf-8') as f:
            f.write(html)
            
        print(f"✅ HTML generado correctamente para {categoria}")
        print(f"   Guardado en: test_output_{categoria}.html")
        
    except Exception as e:
        print(f"❌ Error generando {categoria}: {e}")
