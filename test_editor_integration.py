"""
Test de integración para el Editor de Descripciones IA
"""

import sys
import os
from pathlib import Path

# Agregar el directorio padre al path
sys.path.append(str(Path(__file__).parent))

from ai_generator.prompt_manager import PromptManager
from ai_generator.editor_interface import EditorInterface
from ai_generator.prompt_assistant import PromptAssistant

def test_editor_endpoints():
    """Verifica que los nuevos endpoints funcionen"""
    print("=== Test de Integración del Editor de Descripciones IA ===\n")
    
    # Test 1: Verificar PromptManager
    print("1. Probando PromptManager...")
    try:
        pm = PromptManager()
        versions = pm.get_all_versions()
        print(f"   ✓ PromptManager funciona. Versiones encontradas: {len(versions)}")
    except Exception as e:
        print(f"   ✗ Error en PromptManager: {e}")
    
    # Test 2: Verificar EditorInterface
    print("\n2. Probando EditorInterface...")
    try:
        from ai_generator.ai_handler import AIHandler
        ai = AIHandler()
        editor = EditorInterface(pm, ai)
        sample = editor.get_product_sample('grupo_electrogeno')
        print(f"   ✓ EditorInterface funciona. Producto muestra: {sample['nombre']}")
    except Exception as e:
        print(f"   ✗ Error en EditorInterface: {e}")
    
    # Test 3: Verificar PromptAssistant
    print("\n3. Probando PromptAssistant...")
    try:
        # Simulamos un modelo para la prueba
        class MockModel:
            def generate_content(self, messages):
                class Response:
                    text = '''```json
                    {
                        "prompt_mejorado": "Prompt de prueba mejorado",
                        "cambios_realizados": ["Cambio de prueba"],
                        "explicacion": "Explicación de prueba"
                    }
                    ```'''
                return Response()
        
        assistant = PromptAssistant(MockModel())
        result = assistant.suggest_improvements(
            current_prompt="Test prompt",
            user_request="Mejora este prompt",
            product_type="generador"
        )
        print(f"   ✓ PromptAssistant funciona. Respuesta: {result.get('explicacion', 'OK')}")
    except Exception as e:
        print(f"   ✗ Error en PromptAssistant: {e}")
    
    # Test 4: Verificar archivos estáticos
    print("\n4. Verificando archivos estáticos...")
    static_files = [
        'static/modules/ai_generator/editor.html',
        'static/modules/ai_generator/editor.css',
        'static/modules/ai_generator/editor.js'
    ]
    
    for file_path in static_files:
        if Path(file_path).exists():
            print(f"   ✓ {file_path} existe")
        else:
            print(f"   ✗ {file_path} NO encontrado")
    
    # Test 5: Verificar rutas API en main.py
    print("\n5. Verificando rutas API...")
    api_routes = [
        '/api/ai-generator/test-prompt',
        '/api/ai-generator/ai-assistant',
        '/api/ai-generator/compare-versions',
        '/api/ai-generator/convert-html-for-stelorder'
    ]
    
    try:
        with open('main.py', 'r', encoding='utf-8') as f:
            main_content = f.read()
            for route in api_routes:
                if route in main_content:
                    print(f"   ✓ Ruta {route} encontrada")
                else:
                    print(f"   ✗ Ruta {route} NO encontrada")
    except Exception as e:
        print(f"   ✗ Error verificando rutas: {e}")
    
    print("\n=== Test completado ===")
    print("\nPara ejecutar el servidor, usa:")
    print("  python main.py")
    print("\nLuego abre http://localhost:5002 y ve a la pestaña 'Editor Descripciones'")

if __name__ == '__main__':
    test_editor_endpoints()
