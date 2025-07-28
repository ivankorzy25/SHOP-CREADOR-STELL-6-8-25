// generator.js - Lógica del módulo de generación con IA

// Estado global del módulo
let moduleState = {
    apiKey: '',
    isApiValid: false,
    currentPrompt: '',
    currentVersion: 'base',
    versions: [],
    productTypes: {}
};

// URL del backend (ajustar según tu configuración)
const API_BASE_URL = 'http://localhost:5001/api/ai-generator';

// Inicialización
document.addEventListener('DOMContentLoaded', function() {
    loadSavedApiKey();
    loadPromptVersions();
    loadProductTypes();
    loadCurrentPrompt();
});

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
        const response = await fetch(`${API_BASE_URL}/validate-api-key`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ api_key: apiKey })
        });
        
        const result = await response.json();
        
        if (result.success) {
            moduleState.apiKey = apiKey;
            moduleState.isApiValid = true;
            localStorage.setItem('gemini_api_key', apiKey);
            showStatus(statusDiv, '✅ API key válida y activa', 'success');
        } else {
            showStatus(statusDiv, '❌ ' + result.error, 'error');
        }
    } catch (error) {
        showStatus(statusDiv, '❌ Error al validar: ' + error.message, 'error');
    }
}

// Funciones de Prompts
async function loadPromptVersions() {
    try {
        const response = await fetch(`${API_BASE_URL}/prompt-versions`);
        const versions = await response.json();
        
        moduleState.versions = versions;
        updateVersionSelector(versions);
    } catch (error) {
        console.error('Error cargando versiones:', error);
    }
}

function updateVersionSelector(versions) {
    const selector = document.getElementById('version-selector');
    selector.innerHTML = '';
    
    versions.forEach(version => {
        const option = document.createElement('option');
        option.value = version.version;
        option.textContent = version.name;
        if (version.is_base) {
            option.textContent += ' (BASE)';
        }
        selector.appendChild(option);
    });
}

async function loadPromptVersion() {
    const versionId = document.getElementById('version-selector').value;
    
    try {
        const response = await fetch(`${API_BASE_URL}/prompt-version/${versionId}`);
        const version = await response.json();
        
        document.getElementById('prompt-editor').value = version.prompt;
        document.getElementById('current-version-name').textContent = version.name;
        document.getElementById('current-version-date').textContent = 
            new Date(version.created_at).toLocaleString();
        
        moduleState.currentPrompt = version.prompt;
        moduleState.currentVersion = version.version;
    } catch (error) {
        console.error('Error cargando versión:', error);
    }
}

async function savePromptVersion() {
    const name = document.getElementById('version-name').value.trim();
    const description = document.getElementById('version-description').value.trim();
    const promptText = document.getElementById('prompt-editor').value;
    
    if (!name || !description) {
        console.warn('Por favor completa el nombre y descripción de la versión');
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE_URL}/save-prompt-version`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                prompt: promptText,
                name: name,
                description: description
            })
        });
        
        const result = await response.json();
        
        if (result.success) {
            console.log('✅ Versión guardada exitosamente');
            document.getElementById('version-name').value = '';
            document.getElementById('version-description').value = '';
            loadPromptVersions();
        } else {
            console.error('Error al guardar: ' + result.error);
        }
    } catch (error) {
        console.error('Error al guardar versión: ' + error.message);
    }
}

async function updateBasePrompt() {
    // Crear modal para descripción
    const modal = document.createElement('div');
    modal.className = 'modal';
    modal.style.display = 'block';
    modal.innerHTML = `
        <div class="modal-content">
            <h3>Actualizar Prompt Base</h3>
            <p>¿Estás seguro de actualizar el prompt base? Se creará un respaldo automático.</p>
            <label>Describe los cambios realizados:</label>
            <textarea id="update-description" rows="3" style="width: 100%; margin: 10px 0;"></textarea>
            <div class="modal-buttons">
                <button onclick="this.closest('.modal').remove()" class="btn btn-secondary">Cancelar</button>
                <button onclick="confirmUpdateBasePrompt(this)" class="btn btn-primary">Actualizar</button>
            </div>
        </div>
    `;
    document.body.appendChild(modal);
}

async function confirmUpdateBasePrompt(button) {
    const modal = button.closest('.modal');
    const description = modal.querySelector('#update-description').value.trim();
    
    if (!description) {
        console.warn('Por favor describe los cambios realizados');
        return;
    }
    
    modal.remove();
    
    const promptText = document.getElementById('prompt-editor').value;
    
    try {
        const response = await fetch(`${API_BASE_URL}/update-base-prompt`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                prompt: promptText,
                description: description
            })
        });
        
        const result = await response.json();
        
        if (result.success) {
            console.log('✅ Prompt base actualizado exitosamente');
            loadPromptVersions();
        } else {
            console.error('Error al actualizar: ' + result.error);
        }
    } catch (error) {
        console.error('Error al actualizar prompt base: ' + error.message);
    }
}

// Funciones de Preview
async function generatePreview() {
    if (!moduleState.isApiValid) {
        console.warn('Por favor valida tu API key primero');
        showStatus(document.getElementById('preview-container'), 'Por favor valida tu API key primero', 'error');
        return;
    }
    
    const productType = document.getElementById('example-product').value;
    const promptText = document.getElementById('prompt-editor').value;
    
    // Mostrar loading
    const previewContainer = document.getElementById('preview-container');
    previewContainer.innerHTML = '<div class="loading">Generando preview con IA...</div>';
    
    try {
        const response = await fetch(`${API_BASE_URL}/generate-preview`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                api_key: moduleState.apiKey,
                prompt: promptText,
                product_type: productType
            })
        });
        
        const result = await response.json();
        
        if (result.success) {
            // Mostrar el HTML generado
            previewContainer.innerHTML = result.html;
        } else {
            previewContainer.innerHTML = `<div class="error">Error: ${result.error}</div>`;
        }
    } catch (error) {
        previewContainer.innerHTML = `<div class="error">Error al generar preview: ${error.message}</div>`;
    }
}

// Funciones de Tipos de Producto
async function loadProductTypes() {
    try {
        const response = await fetch(`${API_BASE_URL}/product-types`);
        const types = await response.json();
        
        moduleState.productTypes = types;
        displayProductTypes(types);
    } catch (error) {
        console.error('Error cargando tipos de producto:', error);
    }
}

function displayProductTypes(types) {
    const container = document.getElementById('product-types-list');
    container.innerHTML = '';
    
    Object.entries(types).forEach(([key, config]) => {
        const card = document.createElement('div');
        card.className = 'product-type-card';
        card.innerHTML = `
            <h4>${key.replace('_', ' ').toUpperCase()}</h4>
            <div class="keywords">
                <strong>Palabras clave:</strong> ${config.keywords.join(', ')}
            </div>
            <div class="focus">
                <strong>Enfoque:</strong> ${config.focus}
            </div>
            <div class="applications">
                <strong>Aplicaciones:</strong> ${config.applications}
            </div>
            <div class="actions">
                <button onclick="editProductType('${key}')" class="btn btn-small">Editar</button>
                <button onclick="deleteProductType('${key}')" class="btn btn-small btn-danger">Eliminar</button>
            </div>
        `;
        container.appendChild(card);
    });
}

// Funciones de Modal
function showVersionHistory() {
    const modal = document.getElementById('version-history-modal');
    const versionList = document.getElementById('version-list');
    
    versionList.innerHTML = '';
    
    moduleState.versions.forEach(version => {
        const item = document.createElement('div');
        item.className = 'version-item';
        item.innerHTML = `
            <h4>${version.name} ${version.is_base ? '(BASE)' : ''}</h4>
            <div class="date">${new Date(version.created_at).toLocaleString()}</div>
            <div class="description">${version.description}</div>
            <div class="actions">
                <button onclick="loadVersion('${version.version}')" class="btn btn-small btn-primary">Cargar</button>
                ${!version.is_base ? `<button onclick="deleteVersion('${version.version}')" class="btn btn-small btn-danger">Eliminar</button>` : ''}
                <button onclick="compareVersions('${version.version}')" class="btn btn-small">Comparar</button>
            </div>
        `;
        versionList.appendChild(item);
    });
    
    modal.style.display = 'block';
}

function closeModal(modalId) {
    document.getElementById(modalId).style.display = 'none';
}

function insertVariable() {
    document.getElementById('variables-modal').style.display = 'block';
}

function copyVariable(variable) {
    const editor = document.getElementById('prompt-editor');
    const cursorPos = editor.selectionStart;
    const textBefore = editor.value.substring(0, cursorPos);
    const textAfter = editor.value.substring(cursorPos);
    
    editor.value = textBefore + variable + textAfter;
    editor.focus();
    editor.setSelectionRange(cursorPos + variable.length, cursorPos + variable.length);
    
    closeModal('variables-modal');
}

// Funciones auxiliares
function showStatus(element, message, type) {
    element.className = 'status-indicator ' + type;
    element.textContent = message;
    element.style.display = 'block';
}

function formatPrompt() {
    const editor = document.getElementById('prompt-editor');
    let text = editor.value;
    
    // Formateo básico
    text = text.replace(/\n{3,}/g, '\n\n'); // Máximo 2 saltos de línea
    text = text.trim();
    
    editor.value = text;
}

function showPromptHelp() {
    // Mostrar ayuda en un elemento de la interfaz en lugar de un popup
    const helpModal = document.createElement('div');
    helpModal.className = 'modal';
    helpModal.style.display = 'block';
    helpModal.innerHTML = `
        <div class="modal-content">
            <span class="close" onclick="this.parentElement.parentElement.remove()">&times;</span>
            <h3>Consejos para escribir buenos prompts</h3>
            <ol>
                <li>Sé específico y claro en las instrucciones</li>
                <li>Usa las variables disponibles ({nombre}, {marca}, etc.)</li>
                <li>Define el tono y estilo deseado</li>
                <li>Especifica restricciones (sin emojis, longitud, etc.)</li>
                <li>Incluye ejemplos si es necesario</li>
                <li>Prueba y ajusta iterativamente</li>
            </ol>
            <p><strong>Recuerda:</strong> Un buen prompt produce resultados consistentes y de calidad.</p>
        </div>
    `;
    document.body.appendChild(helpModal);
}

// Event listeners para cerrar modales
window.onclick = function(event) {
    if (event.target.className === 'modal') {
        event.target.style.display = 'none';
    }
}

// Función para cargar el prompt actual
async function loadCurrentPrompt() {
    const baseVersion = moduleState.versions.find(v => v.is_base);
    if (baseVersion) {
        document.getElementById('version-selector').value = 'base';
        loadPromptVersion();
    }
}
