# -*- coding: utf-8 -*-
"""
Test con producto real para verificar el diseño premium completo
"""

import requests
import json
import time

def test_producto_real():
    """Prueba el generador con un producto real de la BD"""
    
    base_url = "http://localhost:5002"
    
    print("=== TEST CON PRODUCTO REAL ===\n")
    
    try:
        # 1. Verificar que la aplicación esté corriendo
        health = requests.get(f"{base_url}/health")
        if health.status_code != 200:
            print("[ERROR] La aplicación no está respondiendo")
            return
        
        print("[OK] Aplicación en línea")
        
        # 2. Validar API key (usar la que ya está configurada)
        api_response = requests.post(f"{base_url}/api/ai-generator/validate-api-key", 
                                   json={})
        
        if not api_response.json().get('success'):
            print("[ERROR] API key no válida")
            return
            
        print("[OK] API key validada")
        
        # 3. Producto de prueba con campos problemáticos
        producto_test = {
            'nombre': 'Generador Eléctrico Honda EU22i',
            'marca': 'Honda',
            'modelo': 'EU22i',
            'familia': 'Generadores Inverter',
            'motor': 'Motor 4.5 HP',  # Sin redundancia HP HP
            'potencia': '2.2 KVA',
            'potencia_kva': '2.2',
            'potencia_kw': '1.8',
            'combustible': 'Nafta',
            'consumo': '1.1 L/h',
            'consumo_75_carga': '1.1 L/h @ 75%',
            'capacidad_tanque': '3.6 L',
            'autonomia': '3.3 horas',
            'voltaje': '220V',
            'frecuencia': '50 Hz',
            'tipo_arranque': 'Manual',
            'peso': '21 kg',
            'nivel_ruido': '57 dB',
            'dimensiones': '509 x 290 x 425 mm',
            'pdf_url': ''  # Sin PDF para esta prueba
        }
        
        # 4. Generar descripción con el generador premium
        print("\nGenerando descripción premium...")
        
        start_time = time.time()
        
        response = requests.post(f"{base_url}/api/ai-generator/test-prompt",
                               json={
                                   'product': producto_test,
                                   'use_premium_generator': True,
                                   'save_locally': True,
                                   'save_path': 'test_output'
                               })
        
        end_time = time.time()
        
        if response.status_code != 200:
            print(f"[ERROR] Error HTTP: {response.status_code}")
            print(response.text)
            return
            
        result = response.json()
        
        if not result.get('success'):
            print(f"[ERROR] {result.get('error')}")
            return
            
        print(f"[OK] Descripción generada en {end_time - start_time:.2f} segundos")
        
        # 5. Verificar el HTML generado
        html_content = result.get('html', '')
        
        elementos_verificar = [
            ('CSS Animaciones', '@keyframes pulse'),
            ('Header Gradiente', 'linear-gradient(135deg, #ff6600'),
            ('Cards Principales', 'ESPECIFICACIONES PRINCIPALES'),
            ('Gráfico Eficiencia', 'EFICIENCIA DE CONSUMO'),
            ('Tabla Amarilla', 'background: #FFC107'),
            ('Ventajas', '¿Por Qué Elegirnos?'),
            ('CTA Premium', '¿Listo para Potenciar tu Negocio?'),
            ('WhatsApp Button', 'Consultar por WhatsApp'),
            ('Footer Contacto', 'Información de Contacto')
        ]
        
        print("\n=== VERIFICACIÓN DE ELEMENTOS ===")
        todos_ok = True
        
        for nombre, elemento in elementos_verificar:
            if elemento in html_content:
                print(f"[OK] {nombre}")
            else:
                print(f"[FALTA] {nombre}")
                todos_ok = False
        
        # 6. Verificar correcciones de datos
        print("\n=== VERIFICACIÓN DE DATOS ===")
        
        # No debe haber redundancia HP HP
        if "Motor 4.5 HP HP" in html_content:
            print("[ERROR] Redundancia HP HP encontrada")
            todos_ok = False
        else:
            print("[OK] Sin redundancia en motor")
            
        # Verificar formato de consumo
        if "1.1 L/h" in html_content:
            print("[OK] Formato de consumo correcto")
        else:
            print("[ERROR] Formato de consumo incorrecto")
            todos_ok = False
        
        # 7. Guardar para inspección
        if result.get('save_message'):
            print(f"\n{result['save_message']}")
        
        # También guardar una copia local
        with open('test_producto_real_output.html', 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print("\nHTML guardado en: test_producto_real_output.html")
        
        print(f"\n{'='*50}")
        if todos_ok:
            print("[EXITO] Diseño premium completo con datos corregidos")
        else:
            print("[ERROR] Faltan elementos o hay errores en los datos")
        print(f"{'='*50}")
        
    except requests.exceptions.ConnectionError:
        print("[ERROR] No se puede conectar con la aplicación. Asegúrate de que esté corriendo en http://localhost:5002")
    except Exception as e:
        print(f"[ERROR] Error inesperado: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_producto_real()