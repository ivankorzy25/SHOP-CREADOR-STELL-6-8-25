# -*- coding: utf-8 -*-
"""
Test directo del generador premium sin necesidad de API
"""

from ai_generator.premium_generator_restored import generar_html_premium_completo

def test_generador_directo():
    """Prueba directa del generador con varios productos"""
    
    productos_test = [
        {
            'nombre': 'Generador Diesel GD12000',
            'marca': 'Gamma',
            'modelo': 'GD12000',
            'motor': 'Motor Diesel 25 HP',  # Sin redundancia
            'motor_valor': '25',
            'motor_unidad': 'HP',  # Campos que deben ser ignorados
            'potencia': '12 KVA',
            'potencia_kva': '12',
            'potencia_kva_valor': '12',  # Campo redundante
            'potencia_kva_unidad': 'KVA',  # Campo redundante
            'combustible': 'Diesel',
            'consumo': '3.5 L/h',
            'consumo_valor': '3.5',  # Campo redundante
            'consumo_unidad': 'L/h',  # Campo redundante
            'capacidad_tanque': '25 L',
            'autonomia': '7.1 horas',
            'voltaje': '380V',
            'frecuencia': '50 Hz',
            'arranque': 'Eléctrico',
            'peso': '180 kg',
            'nivel_ruido': '75 dB @ 7m',
            'dimensiones': '900 x 600 x 750 mm'
        },
        {
            'nombre': 'Motobomba MB550',
            'marca': 'Toyama',
            'modelo': 'MB550',
            'motor': '5.5 HP',  # Solo valor sin "Motor"
            'potencia': '550 L/min',
            'combustible': 'Nafta',
            'consumo': '1.8 L/h',
            'capacidad_tanque': '3.6 L',
            'autonomia': '2 horas',
            'caudal_maximo': '550 L/min',
            'altura_maxima': '28 m',
            'succion': '8 m',
            'entrada_salida': '3" x 3"',
            'peso': '27 kg'
        }
    ]
    
    marketing_base = {
        'titulo_h1': '{marca} {modelo} - Equipo Profesional',
        'subtitulo_p': 'Solución confiable para sus necesidades',
        'seccion_1_titulo': 'Calidad Superior',
        'seccion_1_contenido': 'Fabricado con los más altos estándares de calidad.',
        'seccion_2_titulo': 'Rendimiento Óptimo',
        'seccion_2_contenido': 'Diseñado para ofrecer el máximo rendimiento en cualquier situación.',
        'seccion_3_titulo': 'Servicio Garantizado',
        'seccion_3_contenido': 'Respaldo completo con servicio técnico especializado.'
    }
    
    config = {
        'whatsapp': '541139563099',
        'email': 'info@generadores.ar',
        'telefono': '+541139563099',
        'telefono_display': '+54 11 3956-3099',
        'website': 'www.generadores.ar'
    }
    
    print("=== TEST DIRECTO DEL GENERADOR PREMIUM ===\n")
    
    for i, producto in enumerate(productos_test, 1):
        print(f"\n--- Producto {i}: {producto['nombre']} ---")
        
        # Personalizar marketing
        marketing = marketing_base.copy()
        marketing['titulo_h1'] = f"{producto['marca']} {producto['modelo']} - Equipo Profesional"
        
        # Generar HTML
        try:
            html = generar_html_premium_completo(producto, marketing, config)
            
            # Verificaciones básicas
            verificaciones = {
                'Diseño Premium': 'background: linear-gradient(135deg, #ff6600',
                'CSS Completo': '@keyframes pulse',
                'Cards Hover': '.card-hover:hover',
                'Tabla Amarilla': 'background: #FFC107',
                'Gráfico Eficiencia': 'EFICIENCIA DE CONSUMO',
                'CTA WhatsApp': 'Consultar por WhatsApp',
                'Sin Redundancia HP': 'Motor 25 HP HP' not in html and 'Motor Diesel 25 HP HP' not in html,
                'Sin campos _valor': '_valor' not in html,
                'Sin campos _unidad': '_unidad' not in html
            }
            
            todos_ok = True
            for nombre, condicion in verificaciones.items():
                if isinstance(condicion, bool):
                    ok = condicion
                else:
                    ok = condicion in html
                
                if ok:
                    print(f"  [OK] {nombre}")
                else:
                    print(f"  [ERROR] {nombre}")
                    todos_ok = False
            
            # Guardar HTML
            filename = f"test_output_{producto['modelo'].lower()}_premium.html"
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(html)
            
            if todos_ok:
                print(f"  [EXITO] HTML guardado en: {filename}")
            else:
                print(f"  [PARCIAL] HTML guardado en: {filename} (con errores)")
                
        except Exception as e:
            print(f"  [ERROR] Excepción: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "="*50)
    print("Test completado. Revisa los archivos HTML generados.")
    print("="*50)

if __name__ == "__main__":
    test_generador_directo()