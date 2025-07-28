// navigation.js - Lógica del módulo de navegación

// Estado global del módulo
let moduleState = {
    isConnected: false,
    isProcessing: false,
    isPaused: false,
    browserStatus: null,
    stats: {
        processed: 0,
        failed: 0,
        total: 0
    },
    logs: [],
    errors: []
};

// Temporizadores
let statusTimer = null;
let uptimeTimer = null;

// URL del backend (ajustar según tu configuración)
const API_BASE_URL = 'http://localhost:5001/api/navigation';

// Inicialización
document.addEventListener('DOMContentLoaded', function() {
    updateUI();
    startStatusPolling();
});

// Funciones del Navegador
async function startBrowser() {
    updateButton('start-browser', true, 'Iniciando...');
    
    try {
        const response = await fetch(`${API_BASE_URL}/start-browser`, {
            method: 'POST'
        });
        
        const result = await response.json();
        
        if (result.success) {
            moduleState.isConnected = true;
            addLog('Navegador iniciado correctamente', 'INFO');
            addLog('Por favor, inicia sesión manualmente en Stelorder y luego presiona "Confirmar Login"', 'INFO');
            document.getElementById('confirm-login').disabled = false; // Habilitar directamente
            updateUI();
        } else {
            addLog(`Error: ${result.message}`, 'ERROR');
            console.error(result.message);
        }
    } catch (error) {
        addLog(`Error al iniciar navegador: ${error.message}`, 'ERROR');
        console.error('Error al comunicarse con el servidor');
    } finally {
        updateButton('start-browser', false, '🚀 Iniciar Navegador');
    }
}

async function checkLogin() {
    updateButton('check-login', true, 'Verificando...');
    
    try {
        const response = await fetch(`${API_BASE_URL}/check-login`);
        const result = await response.json();
        
        if (result.logged_in) {
            document.getElementById('login-status').textContent = '✅ Conectado';
            document.getElementById('login-status').style.color = 'var(--success-color)';
            document.getElementById('confirm-login').disabled = false;
            addLog('Login verificado correctamente', 'INFO');
        } else {
            document.getElementById('login-status').textContent = '❌ No conectado';
            document.getElementById('login-status').style.color = 'var(--danger-color)';
            addLog('No se detectó login activo', 'ERROR');
        }
    } catch (error) {
        addLog(`Error al verificar login: ${error.message}`, 'ERROR');
    } finally {
        updateButton('check-login', false, '🔍 Verificar Login');
    }
}

async function confirmLogin() {
    addLog('Login confirmado por el usuario.', 'INFO');
    
    // Obtener productos seleccionados desde el módulo de productos
    const productsFrame = window.parent.document.getElementById('products-frame');
    const productsToProcess = productsFrame.contentWindow.getSelectedProductsForProcessing();
    
    if (!productsToProcess || productsToProcess.length === 0) {
        addLog('No hay productos seleccionados en la pestaña "Productos". Por favor, selecciona los productos que deseas procesar y vuelve a confirmar el login.', 'ERROR');
        console.warn('No hay productos seleccionados para procesar');
        return;
    }
    
    addLog(`Se encontraron ${productsToProcess.length} productos seleccionados. Iniciando proceso...`, 'INFO');
    
    try {
        const response = await fetch(`${API_BASE_URL}/process-products`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ 
                products: productsToProcess,
                settings: { use_ai: true, update_seo: true } // Puedes ajustar esto si es necesario
            })
        });
        
        const result = await response.json();
        
        if (result.success) {
            moduleState.isProcessing = true;
            moduleState.stats.total = productsToProcess.length;
            addLog(`Procesamiento de ${productsToProcess.length} productos iniciado.`, 'INFO');
            document.getElementById('confirm-login').disabled = true;
            updateUI();
        } else {
            addLog(`Error al iniciar procesamiento: ${result.error}`, 'ERROR');
            console.error(`Error al iniciar procesamiento: ${result.error}`);
        }
    } catch (error) {
        addLog(`Error de comunicación al iniciar procesamiento: ${error.message}`, 'ERROR');
        console.error(`Error de comunicación al iniciar procesamiento: ${error.message}`);
    }
}

async function closeBrowser() {
    // Crear modal de confirmación personalizado
    const modal = document.createElement('div');
    modal.className = 'modal';
    modal.style.display = 'block';
    modal.innerHTML = `
        <div class="modal-content">
            <h3>Confirmar cierre</h3>
            <p>¿Estás seguro de cerrar el navegador?</p>
            <div class="modal-buttons">
                <button onclick="this.closest('.modal').remove()" class="btn btn-secondary">Cancelar</button>
                <button onclick="confirmCloseBrowser(this)" class="btn btn-danger">Cerrar navegador</button>
            </div>
        </div>
    `;
    document.body.appendChild(modal);
}

async function confirmCloseBrowser(button) {
    button.closest('.modal').remove();
    
    try {
        const response = await fetch(`${API_BASE_URL}/close-browser`, {
            method: 'POST'
        });
        
        const result = await response.json();
        
        if (result.success) {
            moduleState.isConnected = false;
            addLog('Navegador cerrado correctamente', 'INFO');
            updateUI();
        }
    } catch (error) {
        addLog(`Error al cerrar navegador: ${error.message}`, 'ERROR');
    }
}

// Funciones de Control
async function refreshPage() {
    try {
        const response = await fetch(`${API_BASE_URL}/refresh-page`, {
            method: 'POST'
        });
        
        if (response.ok) {
            addLog('Página refrescada', 'INFO');
        }
    } catch (error) {
        addLog(`Error al refrescar: ${error.message}`, 'ERROR');
    }
}

async function takeScreenshot() {
    try {
        const response = await fetch(`${API_BASE_URL}/screenshot`);
        const result = await response.json();
        
        if (result.success) {
            // Mostrar screenshot en modal
            document.getElementById('screenshot-image').src = result.image_url;
            document.getElementById('screenshot-modal').style.display = 'block';
            addLog('Screenshot capturado', 'INFO');
        }
    } catch (error) {
        addLog(`Error al tomar screenshot: ${error.message}`, 'ERROR');
    }
}

async function navigateToCatalog() {
    try {
        const response = await fetch(`${API_BASE_URL}/navigate-catalog`, {
            method: 'POST'
        });
        
        const result = await response.json();
        
        if (result.success) {
            addLog('Navegado al catálogo', 'INFO');
        } else {
            addLog(`Error navegando: ${result.error}`, 'ERROR');
        }
    } catch (error) {
        addLog(`Error: ${error.message}`, 'ERROR');
    }
}

// Funciones de Procesamiento
function togglePause() {
    if (moduleState.isPaused) {
        resumeProcessing();
    } else {
        pauseProcessing();
    }
}

async function pauseProcessing() {
    try {
        const response = await fetch(`${API_BASE_URL}/pause`, {
            method: 'POST'
        });
        
        if (response.ok) {
            moduleState.isPaused = true;
            document.getElementById('pause-btn').innerHTML = '▶️ Reanudar';
            addLog('Procesamiento pausado', 'INFO');
        }
    } catch (error) {
        addLog(`Error al pausar: ${error.message}`, 'ERROR');
    }
}

async function resumeProcessing() {
    try {
        const response = await fetch(`${API_BASE_URL}/resume`, {
            method: 'POST'
        });
        
        if (response.ok) {
            moduleState.isPaused = false;
            document.getElementById('pause-btn').innerHTML = '⏸️ Pausar';
            addLog('Procesamiento reanudado', 'INFO');
        }
    } catch (error) {
        addLog(`Error al reanudar: ${error.message}`, 'ERROR');
    }
}

async function stopProcessing() {
    // Crear modal de confirmación personalizado
    const modal = document.createElement('div');
    modal.className = 'modal';
    modal.style.display = 'block';
    modal.innerHTML = `
        <div class="modal-content">
            <h3>Confirmar detención</h3>
            <p>¿Estás seguro de detener el procesamiento?</p>
            <div class="modal-buttons">
                <button onclick="this.closest('.modal').remove()" class="btn btn-secondary">Cancelar</button>
                <button onclick="confirmStopProcessing(this)" class="btn btn-danger">Detener proceso</button>
            </div>
        </div>
    `;
    document.body.appendChild(modal);
}

async function confirmStopProcessing(button) {
    button.closest('.modal').remove();
    
    try {
        const response = await fetch(`${API_BASE_URL}/stop`, {
            method: 'POST'
        });
        
        if (response.ok) {
            moduleState.isProcessing = false;
            addLog('Procesamiento detenido', 'INFO');
            updateUI();
        }
    } catch (error) {
        addLog(`Error al detener: ${error.message}`, 'ERROR');
    }
}

// Funciones de Estado y Actualización
async function updateStatus() {
    if (!moduleState.isConnected) return;
    
    try {
        const response = await fetch(`${API_BASE_URL}/status`);
        const status = await response.json();
        
        moduleState.browserStatus = status.browser_status;
        moduleState.isProcessing = status.is_processing;
        moduleState.isPaused = status.is_paused;
        
        // Actualizar UI
        if (status.browser_status) {
            document.getElementById('browser-state').textContent = 
                status.browser_status.is_alive ? '🟢 Activo' : '🔴 Inactivo';
            
            document.getElementById('current-url').textContent = 
                status.browser_status.current_url || '-';
            
            if (status.browser_status.uptime) {
                const minutes = Math.floor(status.browser_status.uptime / 60);
                const seconds = Math.floor(status.browser_status.uptime % 60);
                document.getElementById('uptime').textContent = 
                    `${minutes}:${seconds.toString().padStart(2, '0')}`;
            }
        }
        
        // Actualizar estado de procesamiento
        document.getElementById('processing-status').textContent = 
            status.is_processing ? (status.is_paused ? '⏸️ Pausado' : '▶️ Procesando') : '⏹️ Inactivo';
        
        document.getElementById('current-task').textContent = 
            status.current_task || '-';
        
        // Actualizar estadísticas
        if (status.stats) {
            moduleState.stats = status.stats;
            updateStats();
        }
        
    } catch (error) {
        console.error('Error actualizando estado:', error);
    }
}

function updateStats() {
    const stats = moduleState.stats;
    
    document.getElementById('products-success').textContent = stats.products_processed || 0;
    document.getElementById('products-failed').textContent = stats.products_failed || 0;
    
    const total = (stats.products_processed || 0) + (stats.products_failed || 0);
    const remaining = stats.total - total;
    document.getElementById('products-remaining').textContent = remaining > 0 ? remaining : 0;
    
    // Actualizar barra de progreso
    if (stats.total > 0) {
        const progress = (total / stats.total) * 100;
        document.getElementById('progress-fill').style.width = `${progress}%`;
        document.getElementById('progress-text').textContent = `${total}/${stats.total}`;
    }
    
    // Mostrar errores si hay
    if (stats.errors && stats.errors.length > 0) {
        showErrors(stats.errors);
    }
}

function updateUI() {
    // Habilitar/deshabilitar botones según estado
    const connected = moduleState.isConnected;
    
    document.getElementById('start-browser').disabled = connected;
    document.getElementById('check-login').style.display = 'none'; // Ocultar botón de verificar
    document.getElementById('close-browser').disabled = !connected;
    
    // El botón de confirmar se maneja por separado
    if (!connected) {
        document.getElementById('confirm-login').disabled = true;
    }
    
    document.querySelectorAll('.browser-actions button').forEach(btn => {
        btn.disabled = !connected;
    });
    
    document.getElementById('pause-btn').disabled = !moduleState.isProcessing;
    document.getElementById('stop-btn').disabled = !moduleState.isProcessing;
}

// Funciones de Log
function addLog(message, level = 'INFO') {
    const timestamp = new Date().toLocaleTimeString();
    const logEntry = { timestamp, message, level };
    
    moduleState.logs.push(logEntry);
    
    // Mantener solo los últimos 500 logs
    if (moduleState.logs.length > 500) {
        moduleState.logs.shift();
    }
    
    // Agregar al DOM
    const logContainer = document.getElementById('log-container');
    const logElement = document.createElement('div');
    logElement.className = `log-entry ${level}`;
    logElement.innerHTML = `<span class="log-timestamp">[${timestamp}]</span> ${message}`;
    
    logContainer.appendChild(logElement);
    logContainer.scrollTop = logContainer.scrollHeight;
}

function filterLogs() {
    const filter = document.getElementById('log-filter').value;
    const entries = document.querySelectorAll('.log-entry');
    
    entries.forEach(entry => {
        if (filter === 'all' || entry.classList.contains(filter)) {
            entry.style.display = 'block';
        } else {
            entry.style.display = 'none';
        }
    });
}

function clearLogs() {
    document.getElementById('log-container').innerHTML = '';
    moduleState.logs = [];
    addLog('Logs limpiados', 'INFO');
}

function downloadLogs() {
    const logText = moduleState.logs.map(log => 
        `[${log.timestamp}] [${log.level}] ${log.message}`
    ).join('\n');
    
    const blob = new Blob([logText], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `navigation_logs_${new Date().toISOString().slice(0,10)}.txt`;
    a.click();
    URL.revokeObjectURL(url);
}

// Funciones de Errores
function showErrors(errors) {
    const errorsSection = document.getElementById('errors-section');
    const errorsList = document.getElementById('errors-list');
    
    errorsList.innerHTML = '';
    
    errors.forEach(error => {
        const errorItem = document.createElement('div');
        errorItem.className = 'error-item';
        errorItem.innerHTML = `
            <div class="error-sku">${error.sku}</div>
            <div class="error-message">${error.error}</div>
        `;
        errorsList.appendChild(errorItem);
    });
    
    errorsSection.style.display = errors.length > 0 ? 'block' : 'none';
}

// Funciones de Exportación
async function exportStats() {
    try {
        const response = await fetch(`${API_BASE_URL}/export-stats`);
        const result = await response.json();
        
        if (result.success) {
            addLog(`Estadísticas exportadas: ${result.filename}`, 'INFO');
            
            // Descargar archivo
            window.open(`${API_BASE_URL}/download-stats/${result.filename}`, '_blank');
        }
    } catch (error) {
        addLog(`Error al exportar: ${error.message}`, 'ERROR');
    }
}

// Utilidades
function updateButton(buttonId, disabled, text) {
    const button = document.getElementById(buttonId);
    button.disabled = disabled;
    if (text) button.innerHTML = text;
}

function closeModal(modalId) {
    document.getElementById(modalId).style.display = 'none';
}

function downloadScreenshot() {
    const img = document.getElementById('screenshot-image');
    const a = document.createElement('a');
    a.href = img.src;
    a.download = `screenshot_${new Date().getTime()}.png`;
    a.click();
}

// Polling de estado
function startStatusPolling() {
    statusTimer = setInterval(updateStatus, 2000);
}

function stopStatusPolling() {
    if (statusTimer) {
        clearInterval(statusTimer);
        statusTimer = null;
    }
}

// Event Listeners
window.addEventListener('products:process-request', async (event) => {
    // Evento desde el módulo de productos
    const { products, settings } = event.detail;
    
    if (!moduleState.isConnected || !products || products.length === 0) {
        addLog('El navegador no está conectado o no hay productos para procesar', 'ERROR');
        console.warn('El navegador no está conectado o no hay productos para procesar');
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE_URL}/process-products`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ products, settings })
        });
        
        const result = await response.json();
        
        if (result.success) {
            moduleState.isProcessing = true;
            moduleState.stats.total = products.length;
            addLog(`Iniciando procesamiento de ${products.length} productos`, 'INFO');
            updateUI();
        }
    } catch (error) {
        addLog(`Error iniciando procesamiento: ${error.message}`, 'ERROR');
    }
});

// Cleanup al cerrar
window.addEventListener('beforeunload', function() {
    stopStatusPolling();
});

// Cerrar modales al hacer clic fuera
window.onclick = function(event) {
    if (event.target.className === 'modal') {
        event.target.style.display = 'none';
    }
}
