# -*- coding: utf-8 -*-
"""
Test para verificar que el diseño premium se mantiene EXACTAMENTE igual
Solo deben cambiar los datos procesados
"""

from ai_generator.premium_generator_restored import generar_html_premium_completo

def test_premium_design_preserved():
    """Prueba que el diseño premium se mantiene completo"""
    
    # Datos de prueba con campos problemáticos
    info_producto = {
        'nombre': 'Generador Eléctrico Premium',
        'marca': 'Honda',
        'modelo': 'EU22i',
        'motor': 'Motor 4.5 HP HP',  # Redundancia a corregir
        'potencia': '2.2 KVA',
        'potencia_kva': '2.2 KVA',
        'combustible': 'Nafta',
        'consumo': '1.1 L/h @ 75% carga',
        'capacidad_tanque': '3.6 L',
        'autonomia': '3.3 horas @ 75% carga',
        'voltaje': '220V',
        'frecuencia': '50 Hz',
        'arranque': 'Manual',
        'peso': '21 kg',
        'nivel_ruido': '57 dB @ 7m',
        'dimensiones': '509 x 290 x 425 mm'
    }
    
    marketing_content = {
        'titulo_h1': 'Generador Honda EU22i - Potencia Silenciosa',
        'subtitulo_p': 'La solución ideal para energía portátil de alta calidad',
        'seccion_1_titulo': 'Tecnología Inverter Avanzada',
        'seccion_1_contenido': 'Proporciona energía limpia y estable para equipos electrónicos sensibles.',
        'seccion_2_titulo': 'Ultra Silencioso',
        'seccion_2_contenido': 'Con solo 57 dB, es uno de los generadores más silenciosos del mercado.',
        'seccion_3_titulo': 'Portabilidad Superior',
        'seccion_3_contenido': 'Diseño compacto y ligero de solo 21 kg para máxima movilidad.'
    }
    
    config = {
        'whatsapp': '541139563099',
        'email': 'info@generadores.ar',
        'telefono': '+541139563099',
        'telefono_display': '+54 11 3956-3099',
        'website': 'www.generadores.ar'
    }
    
    # Generar HTML
    html_resultado = generar_html_premium_completo(info_producto, marketing_content, config)
    
    # Verificar que se mantienen TODOS los elementos del diseño premium
    elementos_criticos = [
        # CSS completo con animaciones
        '@keyframes pulse',
        '@keyframes float',
        '@keyframes shine',
        '@keyframes spin',
        '.card-hover',
        '.card-hover:hover',
        '.benefit-card',
        '.btn-hover',
        '.shine-effect',
        '.pulse-animation',
        '.float-animation',
        
        # Header con gradiente
        'background: linear-gradient(135deg, #ff6600 0%, #ff8533 100%)',
        
        # Cards principales con diseño completo
        'ESPECIFICACIONES PRINCIPALES',
        'Potencia Nominal',
        'border-left: 4px solid #ff6600',
        'box-shadow: 0 2px 8px rgba(0,0,0,0.08)',
        
        # Gráfico de eficiencia VISIBLE
        'EFICIENCIA DE CONSUMO',
        'background: linear-gradient(to right, #4CAF50 0%, #8BC34A 25%, #FFC107 50%, #FF9800 75%, #F44336 100%)',
        'Consumo optimizado para',
        
        # Tabla amarilla premium
        'background: #FFC107',
        'ESPECIFICACIONES TÉCNICAS COMPLETAS',
        'border-radius: 16px',
        
        # Ventajas competitivas con cards
        '¿Por Qué Elegirnos?',
        'Calidad Garantizada',
        'Servicio Técnico',
        'Garantía Extendida',
        'Mejor Precio',
        
        # CTA con gradiente y botones
        '¿Listo para Potenciar tu Negocio?',
        'Consultar por WhatsApp',
        'Llamar Ahora',
        
        # Footer completo
        'Información de Contacto',
        'Teléfono',
        'WhatsApp',
        'Email'
    ]
    
    # Verificar cada elemento
    print("=== VERIFICACIÓN DEL DISEÑO PREMIUM ===\n")
    todos_presentes = True
    
    for elemento in elementos_criticos:
        if elemento in html_resultado:
            print(f"[OK] {elemento[:50]}...")
        else:
            print(f"[FALTA] {elemento}")
            todos_presentes = False
    
    # Verificar correcciones de datos
    print("\n=== VERIFICACIÓN DE CORRECCIONES DE DATOS ===\n")
    
    # El motor no debe mostrar "Motor 4.5 HP HP"
    if "Motor 4.5 HP HP" in html_resultado:
        print("[ERROR] Motor muestra redundancia 'HP HP'")
        todos_presentes = False
    else:
        print("[OK] Motor corregido (sin redundancia)")
    
    # Guardar resultado para inspección visual
    with open('test_output_premium_design.html', 'w', encoding='utf-8') as f:
        f.write(html_resultado)
    
    print(f"\n{'='*50}")
    if todos_presentes:
        print("[EXITO] El diseño premium se mantiene COMPLETO con datos corregidos")
    else:
        print("[ERROR] Faltan elementos del diseño premium")
    print(f"{'='*50}")
    
    print("\nHTML generado guardado en: test_output_premium_design.html")
    
    return todos_presentes

if __name__ == "__main__":
    test_premium_design_preserved()