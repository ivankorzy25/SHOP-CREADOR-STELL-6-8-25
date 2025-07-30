// editor.js - Lógica del Editor de Descripciones IA

// Estado global del editor
const editorState = {
    apiKey: '',
    isApiValid: false,
    currentVersion: null,
    currentProduct: null,
    autoPreview: true,
    tempPrompt: '',
    isDirty: false,
    previewTimeout: null,
    selectedProduct: null,
    productPdfContent: null
};

// Inicialización
document.addEventListener('DOMContentLoaded', function() {
    initializeEditor();
    loadVersions();
    setupEventListeners();
    updateStats();
    loadSavedApiKey();
    
    // Escuchar mensajes del iframe padre
    window.addEventListener('message', handleParentMessage);
});

// Inicializar el editor
function initializeEditor() {
    const editor = document.getElementById('prompt-editor');
    
    // Cargar el último prompt guardado o el prompt base
    const savedPrompt = localStorage.getItem('editor_last_prompt');
    if (savedPrompt) {
        editor.value = savedPrompt;
        editorState.tempPrompt = savedPrompt;
    }
    
    // Marcar cambios en el editor
    editor.addEventListener('input', function() {
        editorState.isDirty = true;
        editorState.tempPrompt = editor.value;
        localStorage.setItem('editor_last_prompt', editor.value);
        updateStats();
        
        // Auto preview con debounce
        if (editorState.autoPreview && editorState.currentProduct) {
            clearTimeout(editorState.previewTimeout);
            editorState.previewTimeout = setTimeout(() => {
                refreshPreview();
            }, 1000);
        }
    });
}

// Cargar versiones disponibles
async function loadVersions() {
    try {
        const response = await fetch('/api/ai-generator/versions');
        const data = await response.json();
        
        if (data.versions) {
            updateVersionSelectors(data.versions);
            document.getElementById('version-count').textContent = data.versions.length;
        }
    } catch (error) {
        console.error('Error cargando versiones:', error);
        showNotification('Error al cargar versiones', 'error');
    }
}

// Actualizar selectores de versión
function updateVersionSelectors(versions) {
    const mainSelector = document.getElementById('version-selector');
    const version1Select = document.getElementById('version1');
    const version2Select = document.getElementById('version2');
    
    // Limpiar selectores
    mainSelector.innerHTML = '<option value="">Seleccionar versión...</option>';
    version1Select.innerHTML = '<option value="">Versión 1...</option>';
    version2Select.innerHTML = '<option value="">Versión 2...</option>';
    
    // Agregar versiones
    versions.forEach(version => {
        const option1 = new Option(version.name, version.version);
        const option2 = new Option(version.name, version.version);
        const option3 = new Option(version.name, version.version);
        
        mainSelector.add(option1);
        version1Select.add(option2);
        version2Select.add(option3);
        
        // Seleccionar versión base por defecto
        if (version.is_base) {
            mainSelector.value = version.version;
            loadSelectedVersion();
        }
    });
}

// Cargar versión seleccionada
async function loadSelectedVersion() {
    const versionId = document.getElementById('version-selector').value;
    if (!versionId) return;
    
    try {
        const response = await fetch(`/api/ai-generator/version/${versionId}`);
        const data = await response.json();
        
        if (data.version) {
            document.getElementById('prompt-editor').value = data.version.prompt;
            editorState.currentVersion = data.version;
            editorState.isDirty = false;
            updateStats();
            
            if (editorState.autoPreview && editorState.currentProduct) {
                refreshPreview();
            }
        }
    } catch (error) {
        console.error('Error cargando versión:', error);
        showNotification('Error al cargar la versión', 'error');
    }
}

// Configurar event listeners
function setupEventListeners() {
    // Cerrar modales al hacer clic fuera
    window.onclick = function(event) {
        if (event.target.classList.contains('modal')) {
            event.target.style.display = 'none';
        }
    };
    
    // Enter en el chat de IA
    document.getElementById('ai-request').addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            askAI();
        }
    });
}

// Mostrar/ocultar modal
function closeModal(modalId) {
    document.getElementById(modalId).style.display = 'none';
}

// Insertar variable
function insertVariable() {
    document.getElementById('variables-modal').style.display = 'block';
}

function insertVar(variable) {
    const editor = document.getElementById('prompt-editor');
    const start = editor.selectionStart;
    const end = editor.selectionEnd;
    const text = editor.value;
    
    editor.value = text.substring(0, start) + variable + text.substring(end);
    editor.selectionStart = editor.selectionEnd = start + variable.length;
    editor.focus();
    
    closeModal('variables-modal');
    editorState.isDirty = true;
    updateStats();
}

// Formatear prompt
function formatPrompt() {
    const editor = document.getElementById('prompt-editor');
    let prompt = editor.value;
    
    // Formateo básico
    prompt = prompt
        .replace(/\n{3,}/g, '\n\n') // Máximo 2 saltos de línea
        .replace(/[ \t]+$/gm, '') // Eliminar espacios al final de líneas
        .trim();
    
    editor.value = prompt;
    editorState.isDirty = true;
    updateStats();
}

// Deshacer/Rehacer (básico)
function undoEdit() {
    // Por ahora usar el nativo del navegador
    document.getElementById('prompt-editor').focus();
    document.execCommand('undo');
}

function redoEdit() {
    document.getElementById('prompt-editor').focus();
    document.execCommand('redo');
}

// Cargar producto de muestra
async function loadSampleProduct() {
    const productType = document.getElementById('product-type').value;
    if (!productType) return;
    
    console.log('DEBUG: Cargando producto de muestra tipo:', productType);
    
    // Productos de muestra
    const samples = {
        grupo_electrogeno: {
            nombre: 'Grupo Electrógeno Honda EU70is',
            marca: 'Honda',
            modelo: 'EU70is',
            familia: 'Grupos Electrógenos',
            potencia_kva: '7',
            potencia_kw: '5.5',
            motor: 'Honda GX390',
            combustible: 'Nafta',
            caracteristicas: 'Inverter, Ultra silencioso, 7000W máxima'
        },
        compresor: {
            nombre: 'Compresor Wayne 100L',
            marca: 'Wayne',
            modelo: 'W-100',
            familia: 'Compresores',
            potencia_hp: '3',
            presion_bar: '10',
            tanque: '100',
            caracteristicas: 'Cabezal de aluminio, Monofásico, 300L/min'
        },
        motobomba: {
            nombre: 'Motobomba Honda WB30',
            marca: 'Honda',
            modelo: 'WB30',
            familia: 'Motobombas',
            caudal_lph: '60000',
            motor: 'Honda GX160',
            combustible: 'Nafta',
            caracteristicas: 'Alta presión, Arranque manual, 3 pulgadas'
        }
    };
    
    const product = samples[productType];
    if (product) {
        console.log('DEBUG: Producto de muestra cargado:', product);
        editorState.currentProduct = product;
        editorState.selectedProduct = product;
        console.log('DEBUG: Estado después de cargar producto de muestra:', editorState);
        displayProductInfo(product);
        
        if (editorState.autoPreview) {
            refreshPreview();
        }
    }
}

// Mostrar información del producto
function displayProductInfo(product) {
    const infoDiv = document.getElementById('product-info');
    
    if (!product) {
    infoDiv.innerHTML = `
        <div class="empty-state">
            <p>No hay producto seleccionado.</p>
            <small>Selecciona un tipo de producto de muestra:</small>
            <div style="margin-top: 10px;">
                <select id="product-type" style="width: 100%; margin-bottom: 10px;">
                    <option value="">-- Seleccionar --</option>
                    <option value="grupo_electrogeno">Grupo Electrógeno</option>
                    <option value="compresor">Compresor</option>
                    <option value="motobomba">Motobomba</option>
                </select>
                <button onclick="loadSampleProduct()" class="btn btn-primary btn-block">Cargar Producto</button>
            </div>
        </div>`;
        return;
    }

    infoDiv.innerHTML = `
        <div class="product-card">
            <h4>${product.modelo || 'Sin modelo'}</h4>
            <p><strong>Marca:</strong> ${product.marca || 'N/A'}</p>
            <p><strong>Familia:</strong> ${product.familia || 'N/A'}</p>
            ${product.urlPdf ? `<p><strong>PDF:</strong> <a href="${product.urlPdf}" target="_blank">Ver ficha técnica</a></p>` : ''}
        </div>
    `;
}

// Usar producto real
async function useRealProduct() {
    // Comunicar con el módulo de productos para seleccionar un producto
    window.parent.postMessage({
        type: 'request-product-selection',
        from: 'editor'
    }, window.location.origin);
}

// Manejar mensajes del iframe padre
async function handleParentMessage(event) {
    // No hay comprobación de origen para permitir la comunicación entre iframes de diferentes orígenes (file:// y http://)
    const data = event.data;
    
    if (data.type === 'product-selected-for-ai' || data.type === 'product-selected-for-editor') {
        console.log('DEBUG: Producto recibido desde módulo productos:', data.product);
        editorState.currentProduct = data.product;
        editorState.selectedProduct = data.product;
        console.log('DEBUG: Estado actualizado. currentProduct:', editorState.currentProduct);
        displayProductInfo(data.product);
        
        if (editorState.autoPreview) {
            refreshPreview();
        }
        
        showNotification('Producto cargado: ' + data.product.nombre, 'success');

        // Si hay PDF, extraer contenido
        if (data.product.urlPdf) {
            document.getElementById('pdf-status').innerHTML = '<div class="loading">Extrayendo información del PDF...</div>';
            try {
                const response = await fetch(`/api/ai-generator/extract-pdf`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ pdf_url: data.product.urlPdf })
                });
                
                const result = await response.json();
                if (result.success) {
                    editorState.productPdfContent = result.content;
                    document.getElementById('pdf-status').innerHTML = '<div class="success">✅ PDF procesado correctamente</div>';
                } else {
                    document.getElementById('pdf-status').innerHTML = '<div class="error">❌ Error al procesar PDF</div>';
                }
            } catch (error) {
                console.error('Error extrayendo PDF:', error);
                document.getElementById('pdf-status').innerHTML = '<div class="error">❌ Error al procesar PDF</div>';
            }
        }
    }
}

// Refrescar vista previa
async function refreshPreview() {
    console.log('DEBUG: refreshPreview() - Estado actual:', {
        isApiValid: editorState.isApiValid,
        currentProduct: editorState.currentProduct,
        selectedProduct: editorState.selectedProduct
    });
    
    if (!editorState.isApiValid) {
        showNotification('Por favor valida tu API key primero', 'error');
        return;
    }

    if (!editorState.currentProduct) {
        // Mostrar mensaje en el área de vista previa
        const container = document.getElementById('preview-container');
        container.innerHTML = `
            <div class="preview-placeholder" style="background: #fff3e0; border: 2px solid #ff6600; padding: 20px;">
                <i class="fas fa-exclamation-triangle" style="color: #ff6600; font-size: 2em;"></i>
                <h3 style="color: #ff6600;">⚠️ No hay producto seleccionado</h3>
                <p>Para generar la vista previa necesitas:</p>
                <ol style="text-align: left; max-width: 400px; margin: 0 auto;">
                    <li>Hacer clic en el botón <strong>"Seleccionar Producto"</strong> arriba</li>
                    <li>O cargar un producto de muestra desde el selector</li>
                    <li>Luego hacer clic en <strong>"Actualizar"</strong> o esperar a que se genere automáticamente</li>
                </ol>
            </div>
        `;
        showNotification('⚠️ Selecciona un producto primero para generar la vista previa', 'warning', 7000);
        return;
    }
    
    const prompt = document.getElementById('prompt-editor').value;
    if (!prompt) {
        showNotification('El prompt está vacío', 'warning');
        return;
    }
    
    const usePremium = document.getElementById('use-premium-generator').checked;
    const loadingMessage = usePremium 
        ? "Usando generador HTML premium..." 
        : "Generando con prompt personalizado...";

    // Mostrar indicador de carga en el preview
    const container = document.getElementById('preview-container');
    container.innerHTML = `
        <div class="preview-placeholder">
            <div class="loading-spinner"></div>
            <p>${loadingMessage}</p>
        </div>
    `;
    
    try {
        const payload = {
            product: editorState.currentProduct,
            prompt: prompt,
            api_key: editorState.apiKey,
            pdf_content: editorState.productPdfContent,
            use_premium_generator: usePremium
        };
        
        console.log("Enviando al backend para generar vista previa:", payload);

        const response = await fetch('/api/ai-generator/test-prompt', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(payload)
        });
        
        const data = await response.json();
        
        if (data.success) {
            displayPreview(data.html);
            // Si fue llamado desde el asistente, notificar
            if (document.querySelector('.chat-message:last-child')?.textContent.includes('Generando nueva vista previa')) {
                addChatMessage('✨ Vista previa actualizada con los cambios solicitados.', 'ai');
            }
        } else {
            container.innerHTML = `
                <div class="preview-placeholder">
                    <i class="fas fa-exclamation-triangle" style="color: #dc3545;"></i>
                    <p>Error al generar preview</p>
                    <small>${data.error}</small>
                </div>
            `;
            showNotification('Error al generar preview: ' + data.error, 'error');
        }
    } catch (error) {
        console.error('Error:', error);
        container.innerHTML = `
            <div class="preview-placeholder">
                <i class="fas fa-exclamation-triangle" style="color: #dc3545;"></i>
                <p>Error de conexión</p>
                <small>${error.message}</small>
            </div>
        `;
        showNotification('Error al conectar con el servidor', 'error');
    }
}

// Mostrar vista previa
function displayPreview(html) {
    const container = document.getElementById('preview-container');
    container.innerHTML = html;
}

// Toggle auto preview
function toggleAutoPreview() {
    editorState.autoPreview = !editorState.autoPreview;
    const btn = document.getElementById('auto-preview-btn');
    
    if (editorState.autoPreview) {
        btn.classList.add('btn-active');
        showNotification('Vista previa automática activada', 'info');
    } else {
        btn.classList.remove('btn-active');
        showNotification('Vista previa automática desactivada', 'info');
    }
}

// Asistente IA
async function askAI() {
    const request = document.getElementById('ai-request').value.trim();
    if (!request) return;

    // Validar que tenemos API key y producto
    if (!editorState.isApiValid) {
        showNotification('Por favor valida tu API key primero', 'error');
        return;
    }

    if (!editorState.currentProduct) {
        addChatMessage('ℹ️ Para generar una vista previa, necesitas seleccionar un producto. Te sugiero cargar un producto de muestra desde la sección "Producto de Trabajo" en el centro de la pantalla.', 'ai');
        hideLoading();
        return;
    }

    const editor = document.getElementById('prompt-editor');
    const currentPrompt = editor.value;
    const productType = editorState.currentProduct ? (editorState.currentProduct.familia || 'general') : 'general';

    addChatMessage(request, 'user');
    document.getElementById('ai-request').value = '';
    showLoading();

    try {
        const response = await fetch('/api/ai-generator/ai-assistant', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                prompt: currentPrompt,
                request: request,
                product_type: productType,
                api_key: editorState.apiKey
            })
        });

        const data = await response.json();

        if (data.error) {
            addChatMessage(data.explicacion || 'Lo siento, ocurrió un error.', 'ai');
            hideLoading();
            return;
        }

        // Mostrar la explicación de la IA
        if (data.explicacion) {
            addChatMessage(data.explicacion, 'ai');
        }

        // Aplicar los cambios del diff
        if (data.diff && data.diff.length > 0) {
            let lines = currentPrompt.split('\n');
            let changesApplied = 0;

            data.diff.forEach(change => {
                if (change.type === 'replace_line' && change.line_number > 0 && change.line_number <= lines.length) {
                    lines[change.line_number - 1] = change.new_content;
                    changesApplied++;
                }
            });

            if (changesApplied > 0) {
                const newPrompt = lines.join('\n');
                editor.value = newPrompt;
                editorState.isDirty = true;
                editorState.tempPrompt = newPrompt;
                localStorage.setItem('editor_last_prompt', newPrompt);
                updateStats();

                // Disparar un evento de input para que cualquier listener reaccione
                editor.dispatchEvent(new Event('input', { bubbles: true }));

                addChatMessage(`✅ He aplicado ${changesApplied} cambio${changesApplied > 1 ? 's' : ''} al prompt. Generando nueva vista previa...`, 'ai');
                
                // Regenerar automáticamente la vista previa
                hideLoading();
                refreshPreview();
            } else {
                addChatMessage('⚠️ No pude aplicar los cambios sugeridos. El texto buscado no coincide exactamente con el prompt actual. Puedes aplicar los cambios manualmente.', 'ai');
                
                // Mostrar los cambios sugeridos en el chat para aplicación manual
                data.diff.forEach((change, index) => {
                    addChatMessage(`🔄 Cambio ${index + 1}:\nBuscar: "${change.search}"\nReemplazar con: "${change.replace}"`, 'ai');
                });
                
                hideLoading();
            }
        } else {
            addChatMessage('ℹ️ No hay cambios específicos para aplicar en esta sugerencia.', 'ai');
            hideLoading();
        }

    } catch (error) {
        console.error('Error:', error);
        addChatMessage('Error al conectar con el asistente IA: ' + error.message, 'ai');
        hideLoading();
    }
}

// Agregar mensaje al chat
function addChatMessage(message, sender, isHtml = false) {
    const messagesDiv = document.getElementById('chat-messages');
    const messageDiv = document.createElement('div');
    messageDiv.className = `chat-message ${sender}`;
    
    // Agregar timestamp
    const timestamp = new Date().toLocaleTimeString('es-AR', { hour: '2-digit', minute: '2-digit' });
    const timeSpan = document.createElement('span');
    timeSpan.style.cssText = 'font-size: 0.8em; opacity: 0.7; display: block; margin-bottom: 4px;';
    timeSpan.textContent = timestamp;
    
    messageDiv.appendChild(timeSpan);
    
    const contentDiv = document.createElement('div');
    if (isHtml) {
        contentDiv.innerHTML = message;
    } else {
        contentDiv.textContent = message;
    }
    
    messageDiv.appendChild(contentDiv);
    messagesDiv.appendChild(messageDiv);
    messagesDiv.scrollTop = messagesDiv.scrollHeight;
}


// Comparar versiones
async function compareVersions() {
    const version1Id = document.getElementById('version1').value;
    const version2Id = document.getElementById('version2').value;
    
    if (!version1Id || !version2Id) {
        showNotification('Selecciona dos versiones para comparar', 'warning');
        return;
    }
    
    if (version1Id === version2Id) {
        showNotification('Selecciona versiones diferentes', 'warning');
        return;
    }
    
    if (!editorState.currentProduct) {
        showNotification('Selecciona un producto primero', 'warning');
        return;
    }
    
    showLoading();
    
    try {
        const response = await fetch('/api/ai-generator/compare-versions', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                version1: version1Id,
                version2: version2Id,
                product: editorState.currentProduct
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            showComparisonModal(data.comparison);
        } else {
            showNotification('Error al comparar versiones', 'error');
        }
    } catch (error) {
        console.error('Error:', error);
        showNotification('Error al conectar con el servidor', 'error');
    } finally {
        hideLoading();
    }
}

// Mostrar modal de comparación
function showComparisonModal(comparison) {
    document.getElementById('version1-title').textContent = comparison.version1.info.name;
    document.getElementById('version2-title').textContent = comparison.version2.info.name;
    
    document.getElementById('version1-content').innerHTML = comparison.version1.html;
    document.getElementById('version2-content').innerHTML = comparison.version2.html;
    
    document.getElementById('comparison-modal').style.display = 'block';
}

// Acciones rápidas
function testWithProduct() {
    refreshPreview();
}

function saveAsVersion() {
    if (!editorState.isDirty && editorState.currentVersion) {
        showNotification('No hay cambios para guardar', 'info');
        return;
    }
    
    document.getElementById('save-version-modal').style.display = 'block';
}

async function confirmSaveVersion() {
    const name = document.getElementById('version-name').value.trim();
    const description = document.getElementById('version-description').value.trim();
    
    if (!name) {
        showNotification('Ingresa un nombre para la versión', 'warning');
        return;
    }
    
    const prompt = document.getElementById('prompt-editor').value;
    
    showLoading();
    
    try {
        const response = await fetch('/api/ai-generator/save-version', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                prompt: prompt,
                name: name,
                description: description
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            showNotification('Versión guardada exitosamente', 'success');
            closeModal('save-version-modal');
            document.getElementById('version-name').value = '';
            document.getElementById('version-description').value = '';
            editorState.isDirty = false;
            loadVersions(); // Recargar versiones
        } else {
            showNotification('Error al guardar: ' + data.error, 'error');
        }
    } catch (error) {
        console.error('Error:', error);
        showNotification('Error al conectar con el servidor', 'error');
    } finally {
        hideLoading();
    }
}

async function updateBasePrompt() {
    if (!confirm('¿Estás seguro de actualizar el prompt base? Esta acción no se puede deshacer.')) {
        return;
    }
    
    const prompt = document.getElementById('prompt-editor').value;
    
    showLoading();
    
    try {
        const response = await fetch('/api/ai-generator/update-base', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                prompt: prompt
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            showNotification('Prompt base actualizado exitosamente', 'success');
            editorState.isDirty = false;
            loadVersions();
        } else {
            showNotification('Error al actualizar: ' + data.error, 'error');
        }
    } catch (error) {
        console.error('Error:', error);
        showNotification('Error al conectar con el servidor', 'error');
    } finally {
        hideLoading();
    }
}

async function convertToStelorder() {
    const html = document.getElementById('preview-container').innerHTML;
    
    if (!html || html.includes('La vista previa aparecera aqui')) {
        showNotification('Genera una vista previa primero', 'warning');
        return;
    }
    
    showLoading();
    
    try {
        const response = await fetch('/api/ai-generator/convert-html-for-stelorder', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                html: html
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            // Mostrar HTML convertido
            const modal = document.createElement('div');
            modal.className = 'modal';
            modal.style.display = 'block';
            modal.innerHTML = `
                <div class="modal-content modal-large">
                    <div class="modal-header">
                        <h3>HTML Convertido para Stelorder</h3>
                        <span class="close" onclick="this.closest('.modal').remove()">&times;</span>
                    </div>
                    <div class="modal-body">
                        <div class="form-group">
                            <label>HTML con estilos inline:</label>
                            <textarea rows="10" readonly style="font-family: monospace;">${data.converted_html}</textarea>
                        </div>
                        <div class="modal-actions">
                            <button onclick="copyToClipboard(\`${encodeURIComponent(data.converted_html)}\`)" class="btn btn-primary">
                                <i class="fas fa-copy"></i> Copiar al portapapeles
                            </button>
                            <button onclick="this.closest('.modal').remove()" class="btn btn-secondary">Cerrar</button>
                        </div>
                    </div>
                </div>
            `;
            document.body.appendChild(modal);
        } else {
            showNotification('Error al convertir HTML', 'error');
        }
    } catch (error) {
        console.error('Error:', error);
        showNotification('Error al conectar con el servidor', 'error');
    } finally {
        hideLoading();
    }
}

// Funciones de API Key
function loadSavedApiKey() {
    const savedKey = localStorage.getItem('gemini_api_key');
    if (savedKey) {
        document.getElementById('api-key').value = savedKey;
        validateApiKey();
    }
}

async function validateApiKey() {
    const apiKey = document.getElementById('api-key').value.trim();
    const statusDiv = document.getElementById('api-status');
    
    if (!apiKey) {
        showStatus(statusDiv, 'Por favor ingresa una API key', 'error');
        return;
    }
    
    showStatus(statusDiv, 'Validando API key...', 'info');
    
    try {
        const response = await fetch(`/api/ai-generator/validate-api-key`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ api_key: apiKey })
        });
        
        const result = await response.json();
        
        if (result.success) {
            editorState.apiKey = apiKey;
            editorState.isApiValid = true;
            localStorage.setItem('gemini_api_key', apiKey);
            showStatus(statusDiv, '✅ API key válida y activa', 'success');
        } else {
            editorState.isApiValid = false;
            showStatus(statusDiv, '❌ ' + (result.error || 'API key inválida'), 'error');
        }
    } catch (error) {
        editorState.isApiValid = false;
        showStatus(statusDiv, '❌ Error de conexión: ' + error.message, 'error');
    }
}

function showStatus(element, message, type) {
    if(element) {
        element.className = 'status-indicator ' + type;
        element.textContent = message;
        element.style.display = 'block';
    }
}


// Utilidades
function copyToClipboard(encodedText) {
    const text = decodeURIComponent(encodedText);
    navigator.clipboard.writeText(text).then(() => {
        showNotification('Copiado al portapapeles', 'success');
    }).catch(() => {
        showNotification('Error al copiar', 'error');
    });
}

function showVersionHistory() {
    // Por implementar: mostrar historial completo de versiones
    showNotification('Función en desarrollo', 'info');
}

function saveCurrentWork() {
    // Guardar trabajo actual en localStorage
    const work = {
        prompt: document.getElementById('prompt-editor').value,
        product: editorState.currentProduct,
        timestamp: new Date().toISOString()
    };
    
    localStorage.setItem('editor_current_work', JSON.stringify(work));
    showNotification('Trabajo guardado localmente', 'success');
}

function showHelp() {
    const helpContent = `
        <h4>Guía del Editor de Descripciones IA</h4>
        <ul>
            <li><strong>Variables:</strong> Usa {nombre}, {marca}, {modelo}, etc. para insertar datos del producto</li>
            <li><strong>Vista previa:</strong> Activa el modo Auto para ver cambios en tiempo real</li>
            <li><strong>Asistente IA:</strong> Pide ayuda para mejorar tu prompt</li>
            <li><strong>Versiones:</strong> Guarda diferentes versiones y compáralas</li>
            <li><strong>Convertir:</strong> Convierte el HTML para compatibilidad con Stelorder</li>
        </ul>
    `;
    
    showNotification(helpContent, 'info', 10000);
}

// Actualizar estadísticas
function updateStats() {
    const prompt = document.getElementById('prompt-editor').value;
    
    // Contar caracteres
    document.getElementById('char-count').textContent = prompt.length;
    
    // Contar variables
    const varMatches = prompt.match(/{[^}]+}/g) || [];
    document.getElementById('var-count').textContent = varMatches.length;
}

// Mostrar/ocultar loading
function showLoading() {
    document.getElementById('loading-overlay').style.display = 'flex';
}

function hideLoading() {
    document.getElementById('loading-overlay').style.display = 'none';
}

// Notificaciones
function showNotification(message, type = 'info', duration = 5000) {
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 15px 20px;
        border-radius: 5px;
        color: white;
        font-weight: 500;
        z-index: 3000;
        animation: slideIn 0.3s ease;
        max-width: 400px;
    `;
    
    const colors = {
        success: '#28a745',
        error: '#dc3545',
        warning: '#ffc107',
        info: '#17a2b8'
    };
    
    notification.style.backgroundColor = colors[type] || colors.info;
    
    if (message.includes('<')) {
        notification.innerHTML = message;
    } else {
        notification.textContent = message;
    }
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => notification.remove(), 300);
    }, duration);
}

// Animaciones CSS
const style = document.createElement('style');
style.textContent = `
@keyframes slideIn {
    from {
        transform: translateX(100%);
        opacity: 0;
    }
    to {
        transform: translateX(0);
        opacity: 1;
    }
}

@keyframes slideOut {
    from {
        transform: translateX(0);
        opacity: 1;
    }
    to {
        transform: translateX(100%);
        opacity: 0;
    }
}

.notification {
    box-shadow: 0 4px 12px rgba(0,0,0,0.15);
}
`;
document.head.appendChild(style);
