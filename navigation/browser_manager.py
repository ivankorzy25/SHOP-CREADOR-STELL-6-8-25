"""
Gestor del Navegador Chrome
Maneja la inicialización y control del navegador
"""

import os
import time
import json
from pathlib import Path
from typing import Optional, Dict, Any
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.wait import WebDriverWait
from selenium.common.exceptions import SessionNotCreatedException, WebDriverException
from webdriver_manager.chrome import ChromeDriverManager

class BrowserManager:
    """Gestiona la instancia del navegador Chrome"""
    
    def __init__(self, profile_name: str = "selenium_stel_profile"):
        self.profile_name = profile_name
        self.driver: Optional[webdriver.Chrome] = None
        self.wait: Optional[WebDriverWait] = None
        self.profile_path = Path("./browser_profiles") / profile_name
        self.is_running = False
        self.start_time = None
        self.config = self._load_config()
        
    def _load_config(self) -> Dict[str, Any]:
        """Carga la configuración del navegador"""
        default_config = {
            "timeout": 60,
            "implicit_wait": 10,
            "page_load_timeout": 30,
            "headless": False,
            "window_size": "1280,720",
            "disable_images": False,
            "user_agent": None
        }
        
        config_file = Path("config/browser_config.json")
        if config_file.exists():
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    user_config = json.load(f)
                    default_config.update(user_config)
            except Exception as e:
                print(f"Error cargando configuración: {e}")
        
        return default_config
    
    def initialize_browser(self) -> Dict[str, Any]:
        """Inicializa el navegador Chrome con perfil persistente"""
        try:
            # Crear directorio de perfil si no existe
            os.makedirs(self.profile_path, exist_ok=True)
            
            # Configurar opciones de Chrome
            options = Options()
            options.add_experimental_option("detach", True)
            options.add_argument(f"user-data-dir={os.path.abspath(self.profile_path)}")
            
            # Configuraciones adicionales
            if self.config["window_size"]:
                options.add_argument(f"--window-size={self.config['window_size']}")
            
            if self.config["disable_images"]:
                prefs = {"profile.managed_default_content_settings.images": 2}
                options.add_experimental_option("prefs", prefs)
            
            if self.config["user_agent"]:
                options.add_argument(f'user-agent={self.config["user_agent"]}')
            
            # Opciones para mejorar estabilidad y limpiar configuraciones
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--disable-blink-features=AutomationControlled")
            options.add_argument("--disable-web-security")
            options.add_argument("--disable-features=VizDisplayCompositor")
            options.add_argument("--disable-extensions")
            options.add_argument("--disable-plugins")
            options.add_argument("--disable-background-timer-throttling")
            options.add_argument("--disable-backgrounding-occluded-windows")
            options.add_argument("--disable-renderer-backgrounding")
            options.add_argument("--disable-background-networking")
            options.add_argument("--no-first-run")
            options.add_argument("--no-default-browser-check")
            options.add_argument("--disable-default-apps")
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)
            
            # Limpiar cache y datos de sesión
            options.add_argument("--aggressive-cache-discard")
            options.add_argument("--disable-background-mode")
            
            # Inicializar driver usando ChromeDriverManager
            print("[INFO] Descargando/verificando ChromeDriver...")
            
            import shutil
            import platform
            
            # Limpiar completamente el cache de WebDriver Manager
            wdm_path = Path.home() / ".wdm"
            if wdm_path.exists():
                try:
                    shutil.rmtree(wdm_path)
                    print("[INFO] Cache de WebDriver Manager limpiado completamente")
                except Exception as e:
                    print(f"[WARN] No se pudo limpiar todo el cache: {e}")
            
            # Configurar WebDriver Manager para Windows 64-bit
            os.environ['WDM_ARCHITECTURE'] = '64'
            
            try:
                # Usar ChromeDriverManager estándar
                chromedriver_path = ChromeDriverManager().install()
                
                print(f"[INFO] ChromeDriver instalado en: {chromedriver_path}")
                
                # Verificar que no sea win32 en un sistema de 64 bits
                if platform.system() == "Windows" and platform.machine().endswith('64') and "win32" in chromedriver_path:
                    print("[WARN] Se detectó ChromeDriver win32 en sistema de 64 bits")
                    
                    # Limpiar y reintentar
                    try:
                        driver_parent = Path(chromedriver_path).parent.parent
                        if driver_parent.exists():
                            shutil.rmtree(driver_parent)
                    except:
                        pass
                    
                    # Descargar manualmente la versión correcta
                    import requests
                    import zipfile
                    
                    try:
                        # Obtener la versión más reciente
                        version_url = "https://googlechromelabs.github.io/chrome-for-testing/LATEST_RELEASE_STABLE"
                        response = requests.get(version_url)
                        driver_version = response.text.strip()
                        
                        # URL para Windows 64-bit
                        download_url = f"https://storage.googleapis.com/chrome-for-testing-public/{driver_version}/win64/chromedriver-win64.zip"
                        
                        print(f"[INFO] Descargando ChromeDriver {driver_version} para Windows 64-bit...")
                        
                        # Crear directorio local para el driver
                        driver_dir = Path("drivers")
                        driver_dir.mkdir(exist_ok=True)
                        
                        # Descargar
                        zip_path = driver_dir / "chromedriver.zip"
                        response = requests.get(download_url)
                        response.raise_for_status()
                        
                        with open(zip_path, 'wb') as f:
                            f.write(response.content)
                        
                        # Extraer
                        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                            zip_ref.extractall(driver_dir)
                        
                        # Buscar chromedriver.exe
                        for item in driver_dir.rglob("chromedriver.exe"):
                            chromedriver_path = str(item)
                            break
                        
                        # Limpiar
                        zip_path.unlink()
                        
                        print(f"[INFO] ChromeDriver descargado correctamente: {chromedriver_path}")
                        
                    except Exception as download_error:
                        print(f"[ERROR] Fallo la descarga manual: {download_error}")
                        raise Exception("No se pudo obtener ChromeDriver compatible")
                
            except Exception as e:
                print(f"[ERROR] Error con ChromeDriver: {e}")
                raise Exception(f"No se pudo configurar ChromeDriver: {e}")
            
            print(f"[OK] ChromeDriver instalado en: {chromedriver_path}")
            
            # Verificar que el archivo existe y es ejecutable
            if not Path(chromedriver_path).exists():
                raise Exception(f"ChromeDriver no se descargó correctamente en: {chromedriver_path}")
            
            service = Service(chromedriver_path)
            self.driver = webdriver.Chrome(service=service, options=options)
            
            # Configurar timeouts
            self.driver.implicitly_wait(self.config["implicit_wait"])
            self.driver.set_page_load_timeout(self.config["page_load_timeout"])
            
            # Crear objeto wait
            self.wait = WebDriverWait(self.driver, self.config["timeout"])
            
            # Marcar como activo
            self.is_running = True
            self.start_time = time.time()
            
            print(f"[OK] Navegador iniciado con perfil limpio: {self.profile_path}")
            
            return {
                "success": True,
                "message": "Navegador iniciado correctamente con perfil limpio",
                "session_id": self.driver.session_id,
                "profile_path": str(self.profile_path)
            }
            
        except SessionNotCreatedException as e:
            print(f"[ERROR] Error: Perfil en uso - {e}")
            return {
                "success": False,
                "error": "profile_in_use",
                "message": "El perfil ya está en uso. Cierra todas las ventanas de Chrome con este perfil."
            }
        except Exception as e:
            print(f"[ERROR] Error inicializando navegador: {e}")
            return {
                "success": False,
                "error": "initialization_failed",
                "message": f"Error al inicializar navegador: {str(e)}"
            }
    
    def close_browser(self) -> bool:
        """Cierra el navegador de forma segura"""
        try:
            if self.driver:
                self.driver.quit()
                self.driver = None
                self.wait = None
                self.is_running = False
                return True
        except Exception as e:
            print(f"Error al cerrar navegador: {e}")
        return False
    
    def is_alive(self) -> bool:
        """Verifica si el navegador sigue activo"""
        if not self.driver or not self.is_running:
            return False
        
        try:
            # Intentar obtener el título de la página actual
            _ = self.driver.title
            return True
        except WebDriverException:
            self.is_running = False
            return False
    
    def navigate_to(self, url: str) -> Dict[str, Any]:
        """Navega a una URL específica"""
        if not self.is_alive():
            return {"success": False, "error": "Browser not running"}
        
        try:
            self.driver.get(url)
            return {"success": True, "current_url": self.driver.current_url}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def refresh_page(self) -> bool:
        """Refresca la página actual"""
        if not self.is_alive():
            return False
        
        try:
            self.driver.refresh()
            return True
        except:
            return False
    
    def get_status(self) -> Dict[str, Any]:
        """Obtiene el estado actual del navegador"""
        status = {
            "is_running": self.is_running,
            "is_alive": self.is_alive(),
            "profile": self.profile_name,
            "uptime": None,
            "current_url": None,
            "page_title": None
        }
        
        if self.is_alive():
            try:
                status["current_url"] = self.driver.current_url
                status["page_title"] = self.driver.title
                if self.start_time:
                    status["uptime"] = time.time() - self.start_time
            except:
                pass
        
        return status
    
    def take_screenshot(self, filename: str = None) -> Optional[str]:
        """Toma una captura de pantalla"""
        if not self.is_alive():
            return None
        
        try:
            if not filename:
                filename = f"screenshot_{int(time.time())}.png"
            
            screenshot_dir = Path("screenshots")
            screenshot_dir.mkdir(exist_ok=True)
            filepath = screenshot_dir / filename
            
            self.driver.save_screenshot(str(filepath))
            return str(filepath)
        except Exception as e:
            print(f"Error tomando screenshot: {e}")
            return None
    
    def execute_script(self, script: str, *args) -> Any:
        """Ejecuta JavaScript en la página"""
        if not self.is_alive():
            return None
        
        try:
            return self.driver.execute_script(script, *args)
        except Exception as e:
            print(f"Error ejecutando script: {e}")
            return None
    
    def cleanup_profile(self) -> bool:
        """Limpia los archivos del perfil para evitar configuraciones viejas"""
        try:
            if self.is_running:
                self.close_browser()
            
            # Esperar un momento para asegurar que Chrome liberó los archivos
            time.sleep(3)
            
            if self.profile_path.exists():
                import shutil
                
                # Archivos y directorios específicos a limpiar
                items_to_clean = [
                    "Default/Cookies",
                    "Default/Cookies-journal", 
                    "Default/Local Storage",
                    "Default/Session Storage",
                    "Default/IndexedDB",
                    "Default/Cache",
                    "Default/Code Cache",
                    "Default/GPUCache",
                    "Default/Service Worker",
                    "Default/Web Data",
                    "Default/Web Data-journal",
                    "Default/History",
                    "Default/History-journal",
                    "Default/Login Data",
                    "Default/Login Data-journal",
                    "Default/Preferences",
                    "Default/Secure Preferences",
                    "Default/Network",
                    "Default/blob_storage",
                    "Default/databases",
                    "Default/File System",
                    "Default/Platform Notifications",
                    "ShaderCache",
                    "GrShaderCache"
                ]
                
                print(f"🧹 Limpiando perfil del navegador: {self.profile_path}")
                
                for item in items_to_clean:
                    item_path = self.profile_path / item
                    try:
                        if item_path.exists():
                            if item_path.is_file():
                                item_path.unlink()
                                print(f"  [OK] Eliminado archivo: {item}")
                            elif item_path.is_dir():
                                shutil.rmtree(item_path)
                                print(f"  [OK] Eliminado directorio: {item}")
                    except Exception as e:
                        print(f"  [WARN] No se pudo eliminar {item}: {e}")
                        continue
                
                print("[OK] Limpieza del perfil completada")
                return True
            else:
                print("[INFO] No existe perfil para limpiar")
                return True
                
        except Exception as e:
            print(f"[ERROR] Error limpiando perfil: {e}")
            return False
