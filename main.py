"""
STEL Shop Manager - Aplicación Principal
Sistema modular para gestión de productos y descripciones
"""

import sys
import os
import webbrowser
import threading
import time
from pathlib import Path
from datetime import datetime

# Agregar módulos al path
sys.path.append(str(Path(__file__).parent))

from flask import Flask, render_template, jsonify, request, send_file
from flask_cors import CORS
import logging
import pandas as pd
import tkinter as tk
from tkinter import filedialog

# Importar módulos
from products.product_manager import ProductManager
from products.database_handler import DatabaseHandler
from products.product_filters import FilterCriteria
from navigation.selenium_handler import SeleniumHandler
from ai_generator.ai_handler import AIHandler
from ai_generator.prompt_manager import PromptManager
from ai_generator.editor_interface import EditorInterface
from ai_generator.prompt_assistant import PromptAssistant

# Configuración de logging con soporte UTF-8
import io

# Crear handler para archivo con UTF-8
file_handler = logging.FileHandler('logs/stel_shop.log', encoding='utf-8')
file_handler.setLevel(logging.INFO)

# Crear handler para consola con UTF-8
console_handler = logging.StreamHandler(io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8'))
console_handler.setLevel(logging.INFO)

# Configurar formato
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    handlers=[file_handler, console_handler]
)

logger = logging.getLogger(__name__)

# Crear aplicación Flask
app = Flask(__name__, 
    static_folder='static',
    template_folder='templates'
)
CORS(app)

# Instancias globales de los módulos
product_manager = ProductManager()
selenium_handler = SeleniumHandler()
ai_handler = AIHandler()
prompt_manager = PromptManager()
editor_interface = EditorInterface(prompt_manager, ai_handler)

# Estado global de la aplicación
app_state = {
    'db_connected': False,
    'browser_running': False,
    'ai_configured': False,
    'processing': False
}

# ============================================================================
# RUTAS PRINCIPALES
# ============================================================================

@app.route('/')
def index():
    """Página principal con las tres pestañas"""
    return render_template('index.html')

@app.route('/health')
def health():
    """Estado de salud de la aplicación"""
    return jsonify({
        'status': 'ok',
        'modules': {
            'products': app_state['db_connected'],
            'navigation': app_state['browser_running'],
            'ai_generator': app_state['ai_configured']
        }
    })

# ============================================================================
# API DE PRODUCTOS
# ============================================================================

@app.route('/api/products/connect', methods=['POST'])
def connect_database():
    """Conectar a la base de datos MySQL con validación mejorada"""
    try:
        logger.info("🔄 Iniciando conexión a la base de datos...")
        
        # Limpiar estado previo
        app_state['db_connected'] = False
        product_manager.product_cache = pd.DataFrame()
        
        # Intentar conexión
        success = product_manager.test_database_connection()
        
        if success:
            logger.info("✅ Conexión a base de datos establecida")
            
            # Verificar configuración
            db_config = product_manager.db_handler.config
            instance_name = db_config.get("instance_connection_name", "Cloud SQL")
            database_name = db_config.get('database', 'N/A')
            table_name = db_config.get('table', 'N/A')
            
            logger.info(f"📊 Configuración: {database_name}.{table_name} @ {instance_name}")
            
            # Obtener estadísticas y validar datos
            try:
                stats = product_manager.get_statistics()
                total_products = stats.get('total_products', 0)
                
                # Hacer una consulta de prueba para validar datos
                test_df = product_manager.refresh_products(use_filter=False)
                valid_products = len(test_df)
                
                if valid_products > 0:
                    app_state['db_connected'] = True
                    logger.info(f"✅ Conexión validada: {total_products} productos totales, {valid_products} productos válidos")
                    
                    return jsonify({
                        'success': True,
                        'info': f"{database_name}.{table_name} @ {instance_name}",
                        'details': {
                            'database': database_name,
                            'table': table_name,
                            'instance': instance_name,
                            'total_products': total_products,
                            'valid_products': valid_products,
                            'data_quality': f"{(valid_products/total_products*100):.1f}%" if total_products > 0 else "N/A",
                            'connection_time': datetime.now().isoformat()
                        }
                    })
                else:
                    logger.warning("⚠️ Conexión establecida pero no se encontraron productos válidos")
                    return jsonify({
                        'success': False,
                        'error': f'Conexión establecida pero no se encontraron productos válidos. Total en BD: {total_products}'
                    })
                    
            except Exception as stats_error:
                logger.error(f"❌ Error validando datos: {stats_error}")
                return jsonify({
                    'success': False,
                    'error': f'Conexión establecida pero error validando datos: {str(stats_error)}'
                })
        else:
            app_state['db_connected'] = False
            logger.error("❌ Falló la conexión a la base de datos")
            # Mensaje de error más genérico
            connection_type = "Cloud SQL" if product_manager.db_handler.config.get("use_cloud_sql") else "MySQL local"
            error_message = f"No se pudo conectar a la base de datos ({connection_type}). Verifica las credenciales y la configuración."
            return jsonify({
                'success': False,
                'error': error_message
            })
            
    except Exception as e:
        app_state['db_connected'] = False
        logger.error(f"❌ Error crítico conectando DB: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return jsonify({
            'success': False, 
            'error': f'Error crítico de conexión: {str(e)}'
        })

@app.route('/api/products/products', methods=['POST'])
def get_products():
    """Obtener productos con filtros"""
    try:
        if not app_state['db_connected']:
            return jsonify({'success': False, 'error': 'No hay conexión a la base de datos. Conecta primero.'})

        data = request.get_json() or {}
        filters = data.get('filters', {})
        logger.info(f"API /products: Filtros recibidos del frontend: {filters}")

        clean_filters = {k: v for k, v in filters.items() if v is not None and v != ''}
        
        criteria = FilterCriteria(**clean_filters)
        logger.info(f"API /products: FilterCriteria creado: {criteria.__dict__}")
        df = product_manager.apply_filter(criteria)
        
        logger.info(f"API /products: Productos devueltos después de filtro/refresh: {len(df)} registros")
        
        products = df.to_dict('records')
        
        return jsonify({
            'success': True,
            'products': products,
            'total_count': len(products),
            'filters_applied': clean_filters
        })
        
    except Exception as e:
        logger.error(f"Error obteniendo productos: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return jsonify({'success': False, 'error': f'Error interno: {str(e)}'})

@app.route('/api/products/filter-options')
def get_filter_options():
    """Obtener opciones para filtros"""
    try:
        options = product_manager.get_filter_options()
        return jsonify(options)
    except Exception as e:
        return jsonify({
            'familias': [],
            'marcas': [],
            'saved_filters': [],
            'preset_filters': []
        })

@app.route('/api/products/search', methods=['POST'])
def search_products():
    """Búsqueda rápida de productos"""
    try:
        data = request.get_json() or {}
        query = data.get('query', '')
        df = product_manager.search_products(query)
        
        return jsonify({
            'success': True,
            'products': df.to_dict('records')
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/products/statistics')
def get_statistics():
    """Obtener estadísticas"""
    try:
        stats = product_manager.get_statistics()
        return jsonify(stats)
    except Exception as e:
        return jsonify({})

@app.route('/api/products/export-selection', methods=['POST'])
def export_selection():
    """Exportar productos seleccionados"""
    try:
        data = request.get_json() or {}
        format_type = data.get('format', 'excel')
        filepath = product_manager.export_selected_products(format_type)
        
        if filepath:
            filename = os.path.basename(filepath)
            return jsonify({
                'success': True,
                'filename': filename
            })
        else:
            return jsonify({
                'success': False,
                'error': 'No se pudo exportar'
            })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/products/download-export/<filename>')
def download_export(filename):
    """Descargar archivo exportado"""
    filepath = Path('exports') / filename
    if filepath.exists():
        return send_file(filepath, as_attachment=True)
    else:
        return "Archivo no encontrado", 404

@app.route('/api/debug/filter-test', methods=['POST'])
def debug_filter():
    """Debug de filtros"""
    try:
        data = request.get_json() or {}
        filters = data.get('filters', {})
        criteria = FilterCriteria(**filters)
        filter_dict = product_manager.filters.apply_filter(criteria)
        
        return jsonify({
            'original_filters': filters,
            'criteria_dict': criteria.__dict__,
            'sql_filter_dict': filter_dict
        })
    except Exception as e:
        return jsonify({'error': str(e)})

# ============================================================================
# API DE NAVEGACIÓN
# ============================================================================

@app.route('/api/navigation/start-browser', methods=['POST'])
def start_browser():
    """Iniciar navegador Chrome"""
    try:
        # Configurar callbacks
        selenium_handler.set_callback('on_log', lambda log: logger.info(log['message']))
        selenium_handler.set_callback('on_product_complete', handle_product_complete)
        selenium_handler.set_callback('on_error', handle_navigation_error)
        
        result = selenium_handler.initialize_browser()
        
        if result['success']:
            app_state['browser_running'] = True
            
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})


@app.route('/api/navigation/close-browser', methods=['POST'])
def close_browser():
    """Cerrar navegador"""
    try:
        selenium_handler.close_browser()
        app_state['browser_running'] = False
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/navigation/process-products', methods=['POST'])
def process_products():
    """Procesar lista de productos y subirlos a Stel Order."""
    try:
        data = request.get_json() or {}
        products = data.get('products', [])
        settings = data.get('settings', {})
        
        if not products:
            return jsonify({'success': False, 'error': 'No hay productos para procesar.'})
        
        def generate_descriptions_for_upload(product):
            product_info = product.get('row_data', {})
            descripcion_detallada = ai_handler.generate_description(
                product_info=product_info,
                config=get_contact_config()
            )
            descripcion_corta = generate_short_description(product_info)
            return {
                'descripcion': descripcion_corta,
                'descripcion_detallada': descripcion_detallada,
                'seo_titulo': f"{product_info.get('nombre', 'Producto')} - Generador Eléctrico",
                'seo_descripcion': descripcion_corta[:160]
            }

        selenium_handler.process_products(products, generate_descriptions_for_upload)
        app_state['processing'] = True
        return jsonify({'success': True})
        
    except Exception as e:
        logger.error(f"Error procesando productos para Stel Order: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/navigation/status')
def get_navigation_status():
    """Obtener estado del navegador"""
    try:
        status = selenium_handler.get_status()
        return jsonify(status)
    except Exception as e:
        return jsonify({
            'browser_status': None,
            'is_processing': False,
            'stats': {}
        })

@app.route('/api/navigation/pause', methods=['POST'])
def pause_navigation():
    """Pausar procesamiento"""
    selenium_handler.pause_processing()
    return jsonify({'success': True})

@app.route('/api/navigation/resume', methods=['POST'])
def resume_navigation():
    """Reanudar procesamiento"""
    selenium_handler.resume_processing()
    return jsonify({'success': True})

@app.route('/api/navigation/stop', methods=['POST'])
def stop_navigation():
    """Detener procesamiento"""
    selenium_handler.stop_processing()
    app_state['processing'] = False
    return jsonify({'success': True})

# ============================================================================
# API DE GENERADOR IA
# ============================================================================

@app.route('/api/ai-generator/validate-api-key', methods=['POST'])
def validate_api_key():
    """Validar API key de Google Gemini"""
    try:
        data = request.get_json() or {}
        api_key = data.get('api_key')
        
        # Si no se proporciona una clave, se usa la que está por defecto en el handler
        if not api_key:
            api_key = ai_handler.api_key

        if ai_handler.initialize_model(api_key):
            app_state['ai_configured'] = True
            return jsonify({'success': True})
        else:
            app_state['ai_configured'] = False
            return jsonify({
                'success': False,
                'error': 'API key inválida o error de configuración.'
            })
    except Exception as e:
        app_state['ai_configured'] = False
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/ai-generator/versions')
def get_versions():
    """Obtener versiones para el editor"""
    try:
        versions = prompt_manager.get_all_versions()
        return jsonify({'versions': versions})
    except Exception as e:
        return jsonify({'versions': []})

@app.route('/api/ai-generator/version/<version_id>')
def get_version(version_id):
    """Obtener una versión específica"""
    try:
        if version_id == 'base':
            version = prompt_manager.get_base_prompt()
        else:
            version = prompt_manager.get_version(version_id)
        return jsonify({'version': version})
    except Exception as e:
        return jsonify({'version': None})

@app.route('/api/ai-generator/save-version', methods=['POST'])
def save_version():
    """Guardar nueva versión de prompt (alias para el editor)"""
    try:
        data = request.get_json() or {}
        version = prompt_manager.save_new_version(
            data['prompt'],
            data['name'],
            data['description']
        )
        return jsonify({'success': True, 'version': version})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/ai-generator/update-base', methods=['POST'])
def update_base():
    """Actualizar el prompt base"""
    try:
        data = request.get_json() or {}
        prompt_text = data.get('prompt')
        description = data.get('description', 'Prompt base actualizado desde el editor')
        
        updated = prompt_manager.update_base_prompt(prompt_text, description)
        return jsonify({'success': True, 'version': updated})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

# ============================================================================
# API DE EDITOR DE DESCRIPCIONES IA
# ============================================================================

@app.route('/api/ai-generator/extract-pdf', methods=['POST'])
def extract_pdf_content():
    """Extrae contenido de un PDF para usar en la generación"""
    try:
        data = request.get_json() or {}
        pdf_url = data.get('pdf_url')
        
        if not pdf_url:
            return jsonify({'success': False, 'error': 'No se proporcionó URL del PDF'})
        
        # Importar la nueva función de extracción estructurada
        from ai_generator.premium_generator_v2 import extraer_contenido_pdf
        
        # Extraer contenido (texto y tablas)
        contenido_pdf = extraer_contenido_pdf(pdf_url)
        
        if contenido_pdf:
            texto_pdf = contenido_pdf.get('text', '')
            tablas_md = contenido_pdf.get('tables_markdown', '')

            # Extraer datos técnicos con regex como fallback para la UI
            from ai_generator.premium_generator_v2 import extraer_datos_tecnicos_del_pdf
            info_actual = {}
            datos_tecnicos = extraer_datos_tecnicos_del_pdf(texto_pdf, info_actual)
            
            return jsonify({
                'success': True,
                'content': texto_pdf[:5000],  # Limitar para no sobrecargar
                'tables': tablas_md, # Devolver tablas para posible uso futuro en UI
                'technical_data': datos_tecnicos,
                'full_length': len(texto_pdf)
            })
        else:
            return jsonify({
                'success': False,
                'error': 'No se pudo extraer contenido del PDF'
            })
            
    except Exception as e:
        logger.error(f"Error extrayendo PDF: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/ai-generator/test-prompt', methods=['POST'])
def test_prompt_with_product():
    """Prueba un prompt y opcionalmente guarda el resultado localmente."""
    try:
        data = request.get_json() or {}
        product_data = data.get('product')
        temp_prompt = data.get('prompt')
        api_key = data.get('api_key')
        pdf_content = data.get('pdf_content')
        use_premium = data.get('use_premium_generator', False)
        save_locally = data.get('save_locally', False)
        save_path = data.get('save_path', '')

        logger.info("=== DEBUG: test_prompt_with_product ===")
        logger.info(f"Producto: {product_data.get('nombre') if product_data else 'N/A'}")
        logger.info(f"Guardar localmente: {save_locally}, Ruta: {save_path}")
        logger.info("=====================================")

        if not ai_handler.model:
            if api_key:
                ai_handler.initialize_model(api_key)
            elif not ai_handler.initialize_model(ai_handler.api_key):
                return jsonify({'success': False, 'error': 'No hay modelo de IA configurado.'})

        if pdf_content and product_data:
            product_data['pdf_content'] = pdf_content

        html_result = None
        try:
            if use_premium or not temp_prompt:
                logger.info("Ejecutando generador PREMIUM...")
                html_result = ai_handler.generate_description(
                    product_info=product_data,
                    prompt_template=None,
                    config=get_contact_config()
                )
            else:
                logger.info("Ejecutando con prompt PERSONALIZADO...")
                html_result = ai_handler.generate_description(
                    product_info=product_data,
                    prompt_template=temp_prompt,
                    config=get_contact_config()
                )
        except Exception as e:
            logger.error(f"Error generando preview: {e}")
            return jsonify({'success': False, 'error': str(e)})

        if not html_result:
            return jsonify({'success': False, 'error': 'No se pudo generar contenido con IA.'})

        save_message = ''
        if save_locally and save_path and product_data:
            try:
                save_message = save_html_locally(html_result, product_data, save_path)
                logger.info(f"Guardado local: {save_message}")
            except Exception as e:
                logger.error(f"Error guardando localmente: {e}")
                save_message = f'Error al guardar: {e}'

        return jsonify({
            'success': True,
            'html': html_result,
            'processed': True,
            'save_message': save_message
        })
        
    except Exception as e:
        logger.error(f"Error crítico en test-prompt: {e}")
        return jsonify({'success': False, 'error': f'Error crítico del sistema: {str(e)}'})

@app.route('/api/ai-generator/ai-assistant', methods=['POST'])
def ai_prompt_assistant():
    """IA que ayuda a mejorar prompts"""
    try:
        data = request.get_json() or {}
        api_key = data.get('api_key')
        
        # Inicializar modelo si es necesario
        if not ai_handler.model:
            if api_key and ai_handler.initialize_model(api_key):
                app_state['ai_configured'] = True
            else:
                return jsonify({
                    'success': False,
                    'error': 'Modelo de IA no inicializado. Valida tu API key.'
                })

        assistant = PromptAssistant(ai_handler.model)
        suggestion = assistant.suggest_improvements(
            current_prompt=data.get('prompt'),
            user_request=data.get('request'),
            product_type=data.get('product_type')
        )
        
        # El asistente ahora devuelve todo lo que necesitamos
        suggestion['success'] = not suggestion.get('error', False)
        
        logger.info(f"[DEBUG] Respuesta del asistente IA enviada al frontend: {suggestion}")
        
        return jsonify(suggestion)
        
    except Exception as e:
        logger.error(f"Error en el endpoint del asistente IA: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return jsonify({
            'success': False, 
            'error': str(e),
            'explicacion': 'Ocurrió un error inesperado en el servidor.'
        })

@app.route('/api/ai-generator/compare-versions', methods=['POST'])
def compare_prompt_versions():
    """Compara dos versiones de prompts con un producto de ejemplo"""
    try:
        data = request.get_json() or {}
        version1_id = data.get('version1')
        version2_id = data.get('version2')
        product_data = data.get('product')
        
        # Obtener las versiones
        version1 = prompt_manager.get_version(version1_id)
        version2 = prompt_manager.get_version(version2_id)
        
        # Usar el handler principal que ya tiene Gemini 2.0 configurado
        temp_handler = ai_handler
        
        html1 = temp_handler.generate_description(
            product_info=product_data,
            prompt_template=version1['prompt'],
            config=get_contact_config()
        )
        
        html2 = temp_handler.generate_description(
            product_info=product_data,
            prompt_template=version2['prompt'],
            config=get_contact_config()
        )
        
        return jsonify({
            'success': True,
            'comparison': {
                'version1': {'info': version1, 'html': html1},
                'version2': {'info': version2, 'html': html2}
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/ai-generator/process-batch-locally', methods=['POST'])
def process_batch_locally():
    """Genera y guarda localmente los HTML para un lote de productos."""
    try:
        data = request.get_json() or {}
        products = data.get('products', [])
        save_path = data.get('save_path', '')

        if not products:
            return jsonify({'success': False, 'error': 'No hay productos para procesar.'})
        if not save_path:
            return jsonify({'success': False, 'error': 'No se proporcionó una ruta de guardado.'})

        def processing_thread():
            count = 0
            for product in products:
                try:
                    product_info = product.get('row_data', {})
                    html_content = ai_handler.generate_description(
                        product_info=product_info,
                        config=get_contact_config()
                    )
                    if html_content:
                        save_html_locally(html_content, product_info, save_path)
                        count += 1
                except Exception as e:
                    logger.error(f"Error generando/guardando para {product.get('nombre')}: {e}")
            logger.info(f"Proceso de guardado local finalizado. Se guardaron {count} archivos.")

        threading.Thread(target=processing_thread, daemon=True).start()
        
        return jsonify({'success': True, 'message': f'Iniciando la generación de {len(products)} archivos. El proceso se ejecutará en segundo plano.'})

    except Exception as e:
        logger.error(f"Error en el endpoint de procesamiento por lotes: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/save/select-folder', methods=['GET'])
def select_folder():
    """Abre un diálogo para seleccionar una carpeta y devuelve la ruta."""
    try:
        root = tk.Tk()
        root.withdraw()  # Ocultar la ventana principal de Tkinter
        root.attributes('-topmost', True)  # Poner el diálogo al frente
        folder_path = filedialog.askdirectory(title="Seleccione una carpeta para guardar los archivos HTML")
        root.destroy()
        
        if folder_path:
            return jsonify({'success': True, 'path': folder_path})
        else:
            return jsonify({'success': False, 'error': 'No se seleccionó ninguna carpeta.'})
    except Exception as e:
        logger.error(f"Error al abrir el diálogo de selección de carpeta: {e}")
        return jsonify({'success': False, 'error': f'Error del sistema: {str(e)}'})

# ============================================================================
# FUNCIONES AUXILIARES
# ============================================================================

def handle_product_complete(result):
    """Callback cuando se completa un producto"""
    logger.info(f"Producto {result['sku']} procesado: {result['success']}")

def handle_navigation_error(error_data):
    """Callback para errores de navegación"""
    logger.error(f"Error en navegación: {error_data}")

def save_html_locally(html_content, product_info, base_path):
    """Guarda el contenido HTML en una carpeta local basada en la familia del producto."""
    try:
        # Obtener datos para el nombre del archivo y la carpeta
        family = product_info.get('familia', 'SIN_FAMILIA')
        model = product_info.get('modelo', 'sin_modelo')
        
        # Limpiar nombres para que sean válidos en sistemas de archivos
        safe_family_name = "".join([c for c in family if c.isalnum() or c in (' ', '-')]).rstrip()
        safe_model_name = "".join([c for c in model if c.isalnum() or c in (' ', '-')]).rstrip().replace(' ', '_')

        # Crear nombre de archivo
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_name = f"{safe_model_name}_{timestamp}.html"
        
        # Crear ruta completa usando la familia como nombre de la subcarpeta
        target_folder = Path(base_path) / safe_family_name
        target_folder.mkdir(parents=True, exist_ok=True)
        file_path = target_folder / file_name
        
        # Guardar archivo
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
            
        return f"Archivo guardado en: {file_path}"
    except Exception as e:
        raise IOError(f"No se pudo guardar el archivo en {base_path}: {e}")

def get_contact_config():
    """Obtener configuración de contacto"""
    return {
        'whatsapp': '541139563099',
        'email': 'info@generadores.ar',
        'telefono_display': '+54 11 3956-3099',
        'website': 'www.generadores.ar'
    }

def generate_fallback_preview(product_data):
    """Genera una vista previa básica cuando la IA no está disponible"""
    if not product_data:
        return '<div class="fallback-preview"><h3>Vista Previa No Disponible</h3><p>No se pudo generar la vista previa.</p></div>'
    
    # Extraer información básica del producto
    nombre = product_data.get('nombre', 'Producto')
    marca = product_data.get('marca', '')
    modelo = product_data.get('modelo', '')
    familia = product_data.get('familia', '')
    
    # Generar HTML básico
    html_content = f"""
    <div style="max-width: 800px; margin: 0 auto; padding: 20px; font-family: Arial, sans-serif; background: #f9f9f9; border-radius: 10px;">
        <div style="background: white; padding: 25px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
            <h2 style="color: #ff6600; margin-bottom: 15px; border-bottom: 2px solid #ff6600; padding-bottom: 10px;">
                {marca} {modelo}
            </h2>
            
            <div style="background: #fff3e0; padding: 15px; border-left: 4px solid #ff6600; margin: 20px 0;">
                <h3 style="color: #e65100; margin-top: 0;">📋 Información del Producto</h3>
                <ul style="margin: 0; padding-left: 20px;">
                    <li><strong>Producto:</strong> {nombre}</li>
                    <li><strong>Marca:</strong> {marca}</li>
                    <li><strong>Modelo:</strong> {modelo}</li>
                    <li><strong>Familia:</strong> {familia}</li>
                </ul>
            </div>
            
            <div style="background: #e3f2fd; padding: 15px; border-left: 4px solid #2196f3; margin: 20px 0;">
                <h3 style="color: #1976d2; margin-top: 0;">⚠️ Vista Previa Básica</h3>
                <p style="margin: 0;">Esta es una vista previa básica generada sin IA. Para obtener una descripción completa y optimizada, asegúrate de que el modelo de IA esté disponible.</p>
            </div>
            
            <div style="text-align: center; margin-top: 30px; padding: 20px; background: #f5f5f5; border-radius: 5px;">
                <p style="margin: 0; color: #666; font-size: 14px;">
                    <strong>📞 Contactanos para más información:</strong><br>
                    WhatsApp: +54 11 3956-3099 | Email: info@generadores.ar
                </p>
            </div>
        </div>
    </div>
    """
    
    return html_content

def generate_short_description(product_data):
    """Generar descripción corta sin HTML"""
    info = {
        'nombre': str(product_data.get('Descripción', 'Producto')),
        'marca': str(product_data.get('Marca', '')),
        'modelo': str(product_data.get('Modelo', '')),
        'potencia': str(product_data.get('Potencia', '')),
        'familia': str(product_data.get('Familia', ''))
    }
    
    # Calcular autonomía si es posible
    autonomia = "Variable según carga"
    consumo = product_data.get('Consumo_Combustible_L_H')
    tanque = product_data.get('Capacidad_Tanque_L')
    
    if consumo and tanque:
        try:
            horas = float(tanque) / float(consumo)
            autonomia = f"~ {horas:.1f} horas"
        except:
            pass
    
    descripcion = f"""========================================
{info['marca'].upper()} {info['modelo']}
========================================

[ INFORMACIÓN GENERAL ]
- Producto: {info['nombre']}
- Familia: {info['familia']}
- Potencia: {info['potencia']}

[ CARACTERÍSTICAS PRINCIPALES ]
- Motor de alta calidad
- Construcción robusta
- Mantenimiento simplificado
- Garantía oficial

[ AUTONOMÍA ]
- Autonomía estimada: {autonomia}

========================================"""
    
    return descripcion

# ============================================================================
# INICIALIZACIÓN
# ============================================================================

def create_directories():
    """Crear directorios necesarios"""
    directories = [
        'logs',
        'exports',
        'screenshots',
        'selections',
        'config',
        'browser_profiles',
        'modules/ai_generator/versions',
        'modules/ai_generator/templates'
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)

def open_browser():
    """Abrir navegador automáticamente"""
    time.sleep(2)
    webbrowser.open('http://localhost:5002')

def initialize_ai_model():
    """Inicializar el modelo de IA en segundo plano"""
    logger.info("🤖 Intentando inicializar el modelo de IA con la clave por defecto...")
    if ai_handler.api_key:
        if ai_handler.initialize_model(ai_handler.api_key):
            app_state['ai_configured'] = True
            logger.info("✅ Modelo de IA configurado correctamente al inicio.")
        else:
            app_state['ai_configured'] = False
            logger.warning("⚠️ No se pudo configurar el modelo de IA al inicio. Se requerirá una clave válida en la UI.")
    else:
        logger.info("No se encontró API key por defecto. Se configurará desde la UI.")

if __name__ == '__main__':
    # Crear directorios
    create_directories()
    
    # Mensaje de inicio
    print("""
    ╔══════════════════════════════════════════════╗
    ║       STEL SHOP MANAGER - v1.0.0             ║
    ║   Sistema Modular de Gestión de Productos    ║
    ╚══════════════════════════════════════════════╝
    
    Iniciando servidor...
    """)
    
    # Abrir navegador en thread separado
    threading.Thread(target=open_browser, daemon=True).start()
    
    # Inicializar IA en thread separado
    threading.Thread(target=initialize_ai_model, daemon=True).start()
    
    # Iniciar aplicación
    app.run(debug=False, host='0.0.0.0', port=5002)
