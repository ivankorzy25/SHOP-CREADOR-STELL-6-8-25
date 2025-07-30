"""
Interfaz para el editor de descripciones con IA
"""

from typing import Dict, List, Optional
import json
from datetime import datetime
from pathlib import Path

class EditorInterface:
    """Maneja la interfaz del editor de descripciones"""
    
    def __init__(self, prompt_manager, ai_handler):
        self.prompt_manager = prompt_manager
        self.ai_handler = ai_handler
        self.temp_prompts = {}  # Cache temporal de prompts no guardados
        
    def create_temp_prompt(self, session_id: str, prompt_text: str) -> str:
        """Crea un prompt temporal para pruebas"""
        temp_id = f"temp_{session_id}_{datetime.now().timestamp()}"
        self.temp_prompts[temp_id] = {
            'id': temp_id,
            'prompt': prompt_text,
            'created_at': datetime.now().isoformat(),
            'is_temp': True
        }
        return temp_id
    
    def get_temp_prompt(self, temp_id: str) -> Optional[Dict]:
        """Obtiene un prompt temporal"""
        return self.temp_prompts.get(temp_id)
    
    def save_temp_as_version(self, temp_id: str, name: str, description: str) -> Dict:
        """Convierte un prompt temporal en una versión guardada"""
        temp_prompt = self.temp_prompts.get(temp_id)
        if not temp_prompt:
            raise ValueError("Prompt temporal no encontrado")
        
        # Guardar como nueva versión
        version = self.prompt_manager.save_new_version(
            prompt_text=temp_prompt['prompt'],
            name=name,
            description=description
        )
        
        # Limpiar temporal
        del self.temp_prompts[temp_id]
        
        return version
    
    def get_product_sample(self, product_type: str = None) -> Dict:
        """Obtiene un producto de muestra para testing"""
        samples = {
            'grupo_electrogeno': {
                'nombre': 'Grupo Electrógeno Honda EU70is',
                'marca': 'Honda',
                'modelo': 'EU70is',
                'familia': 'Grupos Electrógenos',
                'potencia_kva': '7',
                'potencia_kw': '5.5',
                'motor': 'Honda GX390',
                'combustible': 'Nafta',
                'caracteristicas': 'Inverter, Ultra silencioso'
            },
            'compresor': {
                'nombre': 'Compresor Wayne 100L',
                'marca': 'Wayne',
                'modelo': 'W-100',
                'familia': 'Compresores',
                'potencia_hp': '3',
                'presion_bar': '10',
                'tanque': '100',
                'caracteristicas': 'Cabezal de aluminio, Monofásico'
            },
            'motobomba': {
                'nombre': 'Motobomba Honda WB30',
                'marca': 'Honda',
                'modelo': 'WB30',
                'familia': 'Motobombas',
                'caudal_lph': '60000',
                'motor': 'Honda GX160',
                'combustible': 'Nafta',
                'caracteristicas': 'Alta presión, Arranque manual'
            }
        }
        
        if product_type and product_type in samples:
            return samples[product_type]
        
        # Retornar uno aleatorio
        import random
        return random.choice(list(samples.values()))
    
    def clean_old_temps(self, hours: int = 24):
        """Limpia prompts temporales antiguos"""
        cutoff = datetime.now().timestamp() - (hours * 3600)
        to_delete = []
        
        for temp_id, temp_data in self.temp_prompts.items():
            created = datetime.fromisoformat(temp_data['created_at']).timestamp()
            if created < cutoff:
                to_delete.append(temp_id)
        
        for temp_id in to_delete:
            del self.temp_prompts[temp_id]
