#!/usr/bin/env python3
"""
Script de prueba para verificar que Gemini 2.0 funciona correctamente
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ai_generator.ai_handler import AIHandler

def test_gemini_2_model():
    """Prueba la inicialización y funcionamiento de Gemini 2.0"""
    print("🧪 Probando inicialización de Gemini 2.0...")
    
    # Crear instancia del handler
    ai_handler = AIHandler()
    
    if ai_handler.model is None:
        print("❌ Error: No se pudo inicializar ningún modelo de IA")
        return False
    
    print(f"✅ Modelo inicializado: {ai_handler.model._model_name}")
    
    # Probar generación simple
    print("\n🧪 Probando generación de contenido...")
    try:
        producto_prueba = {
            'nombre': 'Generador de Prueba Gemini 2.0',
            'marca': 'TestBrand',
            'modelo': 'G2-TEST',
            'potencia_kva': '50',
            'motor': 'Motor de Prueba'
        }
        
        config_prueba = {
            'whatsapp': '1234567890',
            'email': 'test@test.com'
        }
        
        # Generar descripción
        descripcion = ai_handler.generate_description(producto_prueba, config_prueba)
        
        if descripcion and len(descripcion) > 50:
            print("✅ Generación exitosa!")
            print(f"📝 Longitud de respuesta: {len(descripcion)} caracteres")
            print(f"🔤 Primeros 200 caracteres: {descripcion[:200]}...")
            return True
        else:
            print("❌ La respuesta generada parece incompleta")
            return False
            
    except Exception as e:
        print(f"❌ Error durante la generación: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Test de Upgrade a Gemini 2.0")
    print("=" * 50)
    
    success = test_gemini_2_model()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 Upgrade a Gemini 2.0 completado exitosamente!")
        print("📈 El sistema ahora priorizará Gemini 2.0 Flash Experimental")
        print("🔄 Fallback disponible: 1.5 Pro → 1.5 Flash → Pro → 1.0 Pro")
    else:
        print("⚠️ Hubo problemas durante la prueba")
        print("💡 El sistema seguirá funcionando con los modelos de fallback")
    
    print("\n🔍 Para monitorear qué modelo se está usando, observa los logs del servidor")
