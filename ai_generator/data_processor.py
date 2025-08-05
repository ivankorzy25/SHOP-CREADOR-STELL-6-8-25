# -*- coding: utf-8 -*-
"""
Procesador universal de datos para TODOS los productos
"""
import re
from typing import Dict, Any, List, Tuple

class UniversalDataProcessor:
    """Procesador universal para TODOS los productos"""
    
    # Mapeo de campos a nombres display
    FIELD_DISPLAY_NAMES = {
        # Básicos
        'modelo': 'Modelo',
        'serie': 'Serie',
        'potencia': 'Potencia',
        'potencia_kva': 'Potencia',
        'potencia_stand_by': 'Potencia Stand By',
        'potencia_prime': 'Potencia Prime',
        'potencia_kw': 'Potencia (KW)',
        'potencia_hp': 'Potencia',
        'potencia_max_w': 'Potencia Máxima',
        'voltaje': 'Voltaje',
        'frecuencia': 'Frecuencia',
        'fases': 'Fases',
        
        # Motor
        'motor': 'Motor',
        'marca_motor': 'Marca Motor',
        'modelo_motor': 'Modelo Motor',
        'cilindrada': 'Cilindrada',
        'cilindrada_cc': 'Cilindrada',
        'cilindros': 'Cilindros',
        'rpm': 'RPM',
        
        # Combustible
        'combustible': 'Combustible',
        'consumo': 'Consumo',
        'consumo_75_carga': 'Consumo al 75%',
        'consumo_max_carga': 'Consumo Máximo',
        'capacidad_tanque': 'Capacidad del Tanque',
        'capacidad_tanque_combustible_l': 'Capacidad del Tanque',
        'capacidad_tanque_litros': 'Capacidad del Tanque',
        'autonomia': 'Autonomía',
        'autonomia_horas': 'Autonomía',
        'autonomia_potencia_nominal': 'Autonomía',
        
        # Arranque
        'tipo_arranque': 'Tipo de Arranque',
        'arranque': 'Tipo de Arranque',
        'bateria': 'Batería',
        'alternador': 'Alternador',
        'controlador': 'Controlador',
        'panel_control': 'Panel de Control',
        
        # Físicas
        'dimensiones': 'Dimensiones (LxAxH)',
        'dimensiones_mm': 'Dimensiones',
        'largo': 'Largo',
        'ancho': 'Ancho',
        'alto': 'Alto',
        'peso': 'Peso',
        'peso_kg': 'Peso',
        
        # Ambiente
        'nivel_ruido': 'Nivel Sonoro',
        'nivel_ruido_dba': 'Nivel Sonoro',
        'nivel_sonoro_dba': 'Nivel Sonoro',
        'nivel_sonoro_dba_7m': 'Nivel Sonoro a 7m',
        'temperatura_operacion': 'Temperatura Operación',
        'temperatura_trabajo': 'Temperatura de Trabajo',
        'temperatura_max': 'Temperatura Máxima',
        
        # Otros
        'capacidad_aceite': 'Capacidad de Aceite',
        'capacidad_aceite_l': 'Capacidad de Aceite',
        'factor_potencia': 'Factor de Potencia',
        'regulacion_tension': 'Regulación de Tensión',
        'certificaciones': 'Certificaciones',
        'garantia': 'Garantía',
        
        # Específicos por categoría
        'presion': 'Presión',
        'presion_bar': 'Presión',
        'presion_max_bar': 'Presión Máxima',
        'caudal': 'Caudal',
        'caudal_lts_min': 'Caudal',
        'caudal_lph': 'Caudal',
        'ancho_labranza_cm': 'Ancho de Labranza',
        'diametro_max_rama_cm': 'Diámetro Máximo',
        'marchas_adelante_atras': 'Marchas',
        'alcance_pulverizacion': 'Alcance',
        'diametro_succion': 'Diámetro Succión',
        'eje_salida': 'Eje de Salida',
        'frecuencia_hz': 'Frecuencia',
        'fuerza_impacto_kg': 'Fuerza de Impacto',
        'profundidad_corte_mm': 'Profundidad de Corte',
        'diametro_disco': 'Diámetro de Disco',
        'capacidad_tanque_l': 'Capacidad Tanque',
        'tipo_equipo_construccion': 'Tipo de Equipo'
    }
    
    # Campos que NUNCA deben aparecer en la tabla
    EXCLUDED_FIELDS = {
        'nombre', 'marca', 'familia', 'pdf_url', 'marketing_content',
        'categoria_producto', 'caracteristicas_especiales', 'eficiencia_data',
        'nota_consumo', 'tipo_combustible', 'customized_for_gasoline',
        'caracteristicas_adicionales', 'badges_especiales'
    }
    
    # Patrones de exclusión
    EXCLUSION_PATTERNS = [
        r'.*_unidad$', r'.*_unit$', r'.*_valor$', r'.*_value$',
        r'.*unidad.*', r'.*unit.*', r'.*_url$', r'.*_id$'
    ]
    
    @classmethod
    def clean_all_data(cls, info: Dict[str, Any]) -> Dict[str, Any]:
        """Limpia TODOS los datos del producto"""
        cleaned = {}
        
        for key, value in info.items():
            # Saltar campos excluidos
            if cls._should_exclude_field(key):
                continue
                
            # Limpiar el valor
            clean_key, clean_value = cls._clean_field(key, value)
            if clean_value and str(clean_value).strip() not in ['N/D', 'None', 'null', '']:
                cleaned[clean_key] = clean_value
        
        # Procesar campos especiales
        cleaned = cls._process_special_fields(cleaned)
        
        return cleaned
    
    @classmethod
    def _should_exclude_field(cls, field_name: str) -> bool:
        """Determina si un campo debe ser excluido"""
        # Excluir por nombre exacto
        if field_name in cls.EXCLUDED_FIELDS:
            return True
            
        # Excluir por patrones
        for pattern in cls.EXCLUSION_PATTERNS:
            if re.match(pattern, field_name, re.IGNORECASE):
                return True
                
        return False
    
    @classmethod
    def _clean_field(cls, key: str, value: Any) -> Tuple[str, str]:
        """Limpia un campo individual"""
        # Normalizar la clave
        clean_key = key.lower().strip()
        
        # Limpiar el valor
        if value is None or str(value).strip() in ['', 'N/D', 'n/d', 'None', 'null']:
            return clean_key, ''
            
        clean_value = str(value).strip()
        
        # Limpiar duplicaciones de unidades PRIMERO
        clean_value = cls._clean_unit_duplications(clean_value)
        
        # Casos especiales por tipo de campo
        if 'motor' in clean_key:
            clean_value = cls._clean_motor_field(clean_value)
        elif 'consumo' in clean_key:
            clean_value = cls._format_consumption(clean_value)
        elif 'capacidad' in clean_key and 'tanque' in clean_key:
            clean_value = cls._format_tank_capacity(clean_value)
        elif 'autonomia' in clean_key:
            clean_value = cls._format_autonomy(clean_value)
        elif 'peso' in clean_key:
            clean_value = cls._format_weight(clean_value)
        elif 'dimensiones' in clean_key:
            clean_value = cls._format_dimensions(clean_value)
        elif 'nivel' in clean_key and ('ruido' in clean_key or 'sonoro' in clean_key):
            clean_value = cls._format_noise_level(clean_value)
        elif 'presion' in clean_key:
            clean_value = cls._format_pressure(clean_value)
        elif 'caudal' in clean_key:
            clean_value = cls._format_flow(clean_value)
        elif 'temperatura' in clean_key:
            clean_value = cls._format_temperature(clean_value)
        elif 'cilindrada' in clean_key:
            clean_value = cls._format_displacement(clean_value)
        elif 'capacidad_aceite' in clean_key:
            clean_value = cls._format_oil_capacity(clean_value)
            
        return clean_key, clean_value
    
    @classmethod
    def _clean_unit_duplications(cls, value: str) -> str:
        """Elimina duplicaciones de unidades"""
        # Patrones comunes de duplicación
        patterns = [
            # Litros
            (r'(\d+\.?\d*)\s*L\s+L', r'\1 L'),
            (r'(\d+\.?\d*)\s*l\s+l', r'\1 L'),
            (r'(\d+\.?\d*)\s*litro[s]?\s+litro[s]?', r'\1 litros'),
            # Potencia
            (r'(\d+\.?\d*)\s*KVA\s+KVA', r'\1 KVA'),
            (r'(\d+\.?\d*)\s*kva\s+kva', r'\1 KVA'),
            (r'(\d+\.?\d*)\s*KW\s+KW', r'\1 KW'),
            (r'(\d+\.?\d*)\s*kw\s+kw', r'\1 KW'),
            (r'(\d+\.?\d*)\s*W\s+W', r'\1 W'),
            (r'(\d+\.?\d*)\s*HP\s+HP', r'\1 HP'),
            (r'(\d+\.?\d*)\s*hp\s+hp', r'\1 HP'),
            # Frecuencia y voltaje
            (r'(\d+\.?\d*)\s*Hz\s+Hz', r'\1 Hz'),
            (r'(\d+\.?\d*)\s*hz\s+hz', r'\1 Hz'),
            (r'(\d+\.?\d*)\s*V\s+V', r'\1 V'),
            (r'(\d+\.?\d*)\s*v\s+v', r'\1 V'),
            # Peso y dimensiones
            (r'(\d+\.?\d*)\s*kg\s+kg', r'\1 kg'),
            (r'(\d+\.?\d*)\s*Kg\s+Kg', r'\1 kg'),
            (r'(\d+\.?\d*)\s*mm\s+mm', r'\1 mm'),
            (r'(\d+\.?\d*)\s*cm\s+cm', r'\1 cm'),
            # Otros
            (r'(\d+\.?\d*)\s*cc\s+cc', r'\1 cc'),
            (r'(\d+\.?\d*)\s*CC\s+CC', r'\1 cc'),
            (r'(\d+\.?\d*)\s*dB[A]?\s+dB[A]?', r'\1 dBA'),
            (r'(\d+\.?\d*)\s*h\s+h', r'\1 h'),
            (r'(\d+\.?\d*)\s*hora[s]?\s+hora[s]?', r'\1 horas'),
            (r'(\d+\.?\d*)\s*L/h\s+L/h', r'\1 L/h'),
            (r'(\d+\.?\d*)\s*l/h\s+l/h', r'\1 L/h'),
            (r'(\d+\.?\d*)\s*L/min\s+L/min', r'\1 L/min'),
            (r'(\d+\.?\d*)\s*l/min\s+l/min', r'\1 L/min'),
            (r'(\d+\.?\d*)\s*BAR\s+BAR', r'\1 BAR'),
            (r'(\d+\.?\d*)\s*bar\s+bar', r'\1 BAR'),
        ]
        
        for pattern, replacement in patterns:
            value = re.sub(pattern, replacement, value, flags=re.IGNORECASE)
            
        return value.strip()
    
    @classmethod
    def _clean_motor_field(cls, value: str) -> str:
        """Limpia el campo motor"""
        # Primero eliminar redundancias como "Motor Motor"
        value = re.sub(r'motor\s+motor\s+', 'Motor ', value, flags=re.IGNORECASE)
        
        # Si ya está limpio (marca/modelo), dejarlo
        if any(marca in value.upper() for marca in ['CUMMINS', 'HONDA', 'YAMAHA', 'PERKINS', 
                                                     'KOHLER', 'BRIGGS', 'LOGUS', 'HYUNDAI']):
            # Solo quitar "Motor" si está al principio
            value = re.sub(r'^motor\s+', '', value, flags=re.IGNORECASE)
            return value
            
        # Si dice "Motor X HP" y no tiene redundancia, mantenerlo
        if value.lower().startswith('motor ') and 'motor motor' not in value.lower():
            return value
            
        # Si es solo potencia (ej: "6.5 HP"), agregar "Motor"
        match = re.match(r'^(\d+\.?\d*)\s*HP$', value, re.IGNORECASE)
        if match:
            return f"Motor {match.group(1)} HP"
            
        return value
    
    @classmethod
    def _format_consumption(cls, value: str) -> str:
        """Formatea el consumo"""
        match = re.search(r'(\d+\.?\d*)', value)
        if match:
            num = match.group(1)
            if 'l/h' not in value.lower():
                return f"{num} L/h"
        return value
    
    @classmethod
    def _format_tank_capacity(cls, value: str) -> str:
        """Formatea capacidad del tanque"""
        match = re.search(r'(\d+\.?\d*)', value)
        if match:
            num = match.group(1)
            if 'l' not in value.lower() and 'litro' not in value.lower():
                return f"{num} L"
        return value
    
    @classmethod
    def _format_autonomy(cls, value: str) -> str:
        """Formatea autonomía"""
        match = re.search(r'(\d+\.?\d*)', value)
        if match:
            num = match.group(1)
            if 'h' not in value.lower() and 'hora' not in value.lower():
                return f"{num} horas"
        return value
    
    @classmethod
    def _format_weight(cls, value: str) -> str:
        """Formatea peso"""
        match = re.search(r'(\d+\.?\d*)', value)
        if match:
            num = match.group(1)
            if 'kg' not in value.lower():
                return f"{num} kg"
        return value
    
    @classmethod
    def _format_dimensions(cls, value: str) -> str:
        """Formatea dimensiones"""
        # Si tiene formato XXXxYYYxZZZ, agregar mm si no tiene
        if any(sep in value for sep in ['x', 'X', '*']) and 'mm' not in value.lower():
            return f"{value} mm"
        return value
    
    @classmethod
    def _format_noise_level(cls, value: str) -> str:
        """Formatea nivel de ruido"""
        match = re.search(r'(\d+\.?\d*)', value)
        if match:
            num = match.group(1)
            if 'db' not in value.lower():
                return f"{num} dBA"
        return value
    
    @classmethod
    def _format_pressure(cls, value: str) -> str:
        """Formatea presión"""
        match = re.search(r'(\d+\.?\d*)', value)
        if match:
            num = match.group(1)
            if 'bar' not in value.lower():
                return f"{num} BAR"
        return value
    
    @classmethod
    def _format_flow(cls, value: str) -> str:
        """Formatea caudal"""
        match = re.search(r'(\d+\.?\d*)', value)
        if match:
            num = match.group(1)
            # Determinar unidad según el valor
            if float(num) > 1000:
                if 'l/h' not in value.lower():
                    return f"{num} L/h"
            else:
                if 'l/min' not in value.lower():
                    return f"{num} L/min"
        return value
    
    @classmethod
    def _format_temperature(cls, value: str) -> str:
        """Formatea temperatura"""
        match = re.search(r'(\d+\.?\d*)', value)
        if match:
            num = match.group(1)
            if '°' not in value and 'c' not in value.lower():
                return f"{num}°C"
        return value
    
    @classmethod
    def _format_displacement(cls, value: str) -> str:
        """Formatea cilindrada"""
        match = re.search(r'(\d+\.?\d*)', value)
        if match:
            num = match.group(1)
            if 'cc' not in value.lower():
                return f"{num} cc"
        return value
    
    @classmethod
    def _format_oil_capacity(cls, value: str) -> str:
        """Formatea capacidad de aceite"""
        match = re.search(r'(\d+\.?\d*)', value)
        if match:
            num = match.group(1)
            if 'l' not in value.lower():
                return f"{num} L"
        return value
    
    @classmethod
    def _process_special_fields(cls, data: Dict[str, Any]) -> Dict[str, Any]:
        """Procesa campos especiales que requieren lógica adicional"""
        
        # Consolidar campos de potencia
        potencia_fields = ['potencia_kva', 'potencia_max_valor', 'potencia_standby_valor', 'potencia']
        for field in potencia_fields:
            if field in data and 'potencia' not in data:
                data['potencia'] = data[field]
                break
                
        # Consolidar campos de consumo
        consumo_fields = ['consumo_75_carga_valor', 'consumo_max_carga_valor', 'consumo_valor', 'consumo']
        for field in consumo_fields:
            if field in data and 'consumo' not in data:
                data['consumo'] = data[field]
                break
                
        # Consolidar campos de tanque
        tanque_fields = ['capacidad_tanque_combustible_l', 'capacidad_tanque_litros', 'capacidad_tanque']
        for field in tanque_fields:
            if field in data:
                data['capacidad_tanque'] = data[field]
                # Remover duplicados
                if field != 'capacidad_tanque':
                    data.pop(field, None)
                break
                
        # Consolidar campos de autonomía
        autonomia_fields = ['autonomia_potencia_nominal_valor', 'autonomia_horas', 'autonomia']
        for field in autonomia_fields:
            if field in data:
                data['autonomia'] = data[field]
                # Remover duplicados
                if field != 'autonomia':
                    data.pop(field, None)
                break
                
        # Consolidar campos de nivel sonoro
        ruido_fields = ['nivel_sonoro_dba_7m', 'nivel_ruido_dba', 'nivel_sonoro_dba', 'nivel_ruido']
        for field in ruido_fields:
            if field in data:
                data['nivel_ruido'] = data[field]
                # Remover duplicados
                if field != 'nivel_ruido':
                    data.pop(field, None)
                break
                
        return data
    
    @classmethod
    def get_display_name(cls, field_key: str) -> str:
        """Obtiene el nombre display para un campo"""
        # Buscar en el mapeo
        if field_key in cls.FIELD_DISPLAY_NAMES:
            return cls.FIELD_DISPLAY_NAMES[field_key]
            
        # Buscar coincidencia parcial
        for key, display_name in cls.FIELD_DISPLAY_NAMES.items():
            if key in field_key:
                return display_name
                
        # Default: formatear el campo
        return field_key.replace('_', ' ').title()