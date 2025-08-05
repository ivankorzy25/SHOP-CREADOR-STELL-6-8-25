# -*- coding: utf-8 -*-
"""
Calculador universal de eficiencia para TODOS los productos
"""
import re
from typing import Dict, Any, Optional, Tuple

class UniversalEfficiencyCalculator:
    """Calculador universal de eficiencia adaptativo según tipo de combustible"""
    
    # Configuración de eficiencia por tipo de combustible
    EFFICIENCY_CONFIG = {
        'nafta': {
            'excelente': {
                'min': 0.0,
                'max': 0.35,
                'color': '#4CAF50',
                'texto': 'Eficiencia Excelente'
            },
            'muy_buena': {
                'min': 0.35,
                'max': 0.45,
                'color': '#8BC34A',
                'texto': 'Muy Buena Eficiencia'
            },
            'buena': {
                'min': 0.45,
                'max': 0.6,
                'color': '#FFC107',
                'texto': 'Buena Eficiencia'
            },
            'normal': {
                'min': 0.6,
                'max': 0.8,
                'color': '#FF9800',
                'texto': 'Eficiencia Normal'
            },
            'baja': {
                'min': 0.8,
                'max': float('inf'),
                'color': '#F44336',
                'texto': 'Eficiencia Baja'
            }
        },
        'diesel': {
            'excelente': {
                'min': 0.0,
                'max': 0.25,
                'color': '#4CAF50',
                'texto': 'Eficiencia Excelente'
            },
            'muy_buena': {
                'min': 0.25,
                'max': 0.35,
                'color': '#8BC34A',
                'texto': 'Muy Buena Eficiencia'
            },
            'buena': {
                'min': 0.35,
                'max': 0.45,
                'color': '#FFC107',
                'texto': 'Buena Eficiencia'
            },
            'normal': {
                'min': 0.45,
                'max': 0.6,
                'color': '#FF9800',
                'texto': 'Eficiencia Normal'
            },
            'baja': {
                'min': 0.6,
                'max': float('inf'),
                'color': '#F44336',
                'texto': 'Eficiencia Baja'
            }
        },
        'gas': {
            'excelente': {
                'min': 0.0,
                'max': 0.3,
                'color': '#4CAF50',
                'texto': 'Eficiencia Excelente'
            },
            'muy_buena': {
                'min': 0.3,
                'max': 0.4,
                'color': '#8BC34A',
                'texto': 'Muy Buena Eficiencia'
            },
            'buena': {
                'min': 0.4,
                'max': 0.5,
                'color': '#FFC107',
                'texto': 'Buena Eficiencia'
            },
            'normal': {
                'min': 0.5,
                'max': 0.65,
                'color': '#FF9800',
                'texto': 'Eficiencia Normal'
            },
            'baja': {
                'min': 0.65,
                'max': float('inf'),
                'color': '#F44336',
                'texto': 'Eficiencia Baja'
            }
        }
    }
    
    @classmethod
    def calculate(cls, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calcula la eficiencia universal para cualquier producto
        
        Args:
            data: Diccionario con los datos del producto
            
        Returns:
            Dict con porcentaje, texto, color y consumo_por_kw
        """
        # Detectar tipo de combustible
        fuel_type = cls._detect_fuel_type(data)
        
        # Extraer potencia
        power_kw = cls._extract_power_kw(data)
        
        # Extraer consumo
        consumption_lh = cls._extract_consumption_lh(data)
        
        # Si no hay datos suficientes, retornar valores por defecto
        if not power_kw or not consumption_lh:
            return cls._get_default_efficiency(fuel_type)
        
        # Calcular consumo por KW
        consumption_per_kw = consumption_lh / power_kw
        
        # Determinar nivel de eficiencia
        efficiency_level = cls._determine_efficiency_level(fuel_type, consumption_per_kw)
        
        # Calcular porcentaje (inverso del consumo normalizado)
        percentage = cls._calculate_percentage(fuel_type, consumption_per_kw)
        
        return {
            'porcentaje': percentage,
            'texto': efficiency_level['texto'],
            'color': efficiency_level['color'],
            'consumo_por_kw': round(consumption_per_kw, 2),
            'tipo_combustible': fuel_type,
            'potencia_kw': power_kw,
            'consumo_lh': consumption_lh
        }
    
    @classmethod
    def _detect_fuel_type(cls, data: Dict[str, Any]) -> str:
        """Detecta el tipo de combustible del producto"""
        # Buscar en campo combustible
        combustible = str(data.get('combustible', '')).lower()
        
        # También buscar en nombre y modelo
        nombre = str(data.get('nombre', '')).lower()
        modelo = str(data.get('modelo', '')).lower()
        
        # Búsqueda combinada
        texto_completo = f"{combustible} {nombre} {modelo}"
        
        # Patrones de detección
        if any(term in texto_completo for term in ['nafta', 'gasolina', 'bencina', 'petrol']):
            return 'nafta'
        elif any(term in texto_completo for term in ['diesel', 'gasoil', 'diésel']):
            return 'diesel'
        elif any(term in texto_completo for term in ['gas', 'glp', 'gnc', 'propano', 'butano']):
            return 'gas'
        
        # Si no se detecta, usar nafta como default para generadores pequeños
        if 'generador' in texto_completo:
            # Si la potencia es menor a 10KVA, probablemente es nafta
            potencia = cls._extract_power_kw(data)
            if potencia and potencia < 8:  # ~10KVA
                return 'nafta'
                
        return 'nafta'  # Default
    
    @classmethod
    def _extract_power_kw(cls, data: Dict[str, Any]) -> Optional[float]:
        """Extrae la potencia en KW"""
        # Campos posibles de potencia
        power_fields = [
            'potencia_kw', 'potencia_kw_valor', 'potencia_kw_value',
            'potencia', 'potencia_valor', 'potencia_value'
        ]
        
        # Buscar primero en campos KW
        for field in power_fields:
            if field in data:
                value = cls._parse_number(str(data[field]))
                if value and 'kw' in field:
                    return value
        
        # Si no hay KW, buscar KVA y convertir
        kva_fields = [
            'potencia_kva', 'potencia_kva_valor', 'potencia_kva_value',
            'potencia_nominal_kva', 'potencia_prime_kva'
        ]
        
        for field in kva_fields:
            if field in data:
                kva = cls._parse_number(str(data[field]))
                if kva:
                    # Factor de potencia típico 0.8
                    return kva * 0.8
        
        # Buscar en campo potencia genérico
        if 'potencia' in data:
            potencia_str = str(data['potencia'])
            
            # Buscar KW
            match = re.search(r'(\d+\.?\d*)\s*kw', potencia_str, re.IGNORECASE)
            if match:
                return cls._parse_number(match.group(1))
            
            # Buscar KVA
            match = re.search(r'(\d+\.?\d*)\s*kva', potencia_str, re.IGNORECASE)
            if match:
                return cls._parse_number(match.group(1)) * 0.8
            
            # Si es solo número, asumir KVA
            value = cls._parse_number(potencia_str)
            if value:
                return value * 0.8
        
        return None
    
    @classmethod
    def _extract_consumption_lh(cls, data: Dict[str, Any]) -> Optional[float]:
        """Extrae el consumo en L/h"""
        # Campos posibles de consumo
        consumption_fields = [
            'consumo', 'consumo_valor', 'consumo_value',
            'consumo_75_carga', 'consumo_75_carga_valor',
            'consumo_max_carga', 'consumo_max_carga_valor',
            'consumo_nominal', 'consumo_nominal_valor'
        ]
        
        # Buscar en campos de consumo
        for field in consumption_fields:
            if field in data:
                value_str = str(data[field])
                
                # Buscar patrón L/h
                match = re.search(r'(\d+\.?\d*)\s*l/h', value_str, re.IGNORECASE)
                if match:
                    return cls._parse_number(match.group(1))
                
                # Si es solo número, asumir L/h
                value = cls._parse_number(value_str)
                if value:
                    return value
        
        return None
    
    @classmethod
    def _parse_number(cls, value: str) -> Optional[float]:
        """Parsea un número de un string"""
        try:
            # Limpiar el string
            clean = re.sub(r'[^\d.,]', '', value)
            clean = clean.replace(',', '.')
            
            # Si hay múltiples puntos, mantener solo el último
            if clean.count('.') > 1:
                parts = clean.split('.')
                clean = '.'.join(parts[:-1]).replace('.', '') + '.' + parts[-1]
            
            return float(clean)
        except:
            return None
    
    @classmethod
    def _determine_efficiency_level(cls, fuel_type: str, consumption_per_kw: float) -> Dict[str, Any]:
        """Determina el nivel de eficiencia según el tipo de combustible"""
        config = cls.EFFICIENCY_CONFIG.get(fuel_type, cls.EFFICIENCY_CONFIG['nafta'])
        
        for level_name, level_config in config.items():
            if level_config['min'] <= consumption_per_kw < level_config['max']:
                return level_config
        
        # Default: eficiencia baja
        return config['baja']
    
    @classmethod
    def _calculate_percentage(cls, fuel_type: str, consumption_per_kw: float) -> int:
        """Calcula el porcentaje de eficiencia"""
        # Obtener rangos del tipo de combustible
        config = cls.EFFICIENCY_CONFIG.get(fuel_type, cls.EFFICIENCY_CONFIG['nafta'])
        
        # Definir rangos para el cálculo
        min_consumption = config['excelente']['max']  # Mejor consumo posible
        max_consumption = config['normal']['max']     # Peor consumo aceptable
        
        # Calcular porcentaje inverso (menor consumo = mayor eficiencia)
        if consumption_per_kw <= min_consumption:
            return 95  # Excelente
        elif consumption_per_kw >= max_consumption:
            return 30  # Bajo
        else:
            # Interpolación lineal inversa
            range_consumption = max_consumption - min_consumption
            position = (consumption_per_kw - min_consumption) / range_consumption
            # Invertir: menor consumo = mayor porcentaje
            percentage = 95 - (position * 65)  # De 95% a 30%
            return max(30, min(95, int(percentage)))
    
    @classmethod
    def _get_default_efficiency(cls, fuel_type: str) -> Dict[str, Any]:
        """Retorna valores por defecto cuando no hay datos suficientes"""
        return {
            'porcentaje': 60,
            'texto': 'Eficiencia Normal',
            'color': '#FFC107',
            'consumo_por_kw': 0,
            'tipo_combustible': fuel_type,
            'potencia_kw': 0,
            'consumo_lh': 0
        }
    
    @classmethod
    def get_efficiency_badge(cls, efficiency_data: Dict[str, Any]) -> Dict[str, Any]:
        """Genera un badge de eficiencia para mostrar"""
        percentage = efficiency_data.get('porcentaje', 60)
        color = efficiency_data.get('color', '#FFC107')
        
        # Determinar ícono según porcentaje
        if percentage >= 80:
            icon = 'star'
        elif percentage >= 60:
            icon = 'check-circle'
        else:
            icon = 'info-circle'
        
        return {
            'texto': f"Eficiencia: {percentage}%",
            'color': color,
            'icono': icon
        }
    
    @classmethod
    def format_consumption_info(cls, efficiency_data: Dict[str, Any]) -> str:
        """Formatea información de consumo para mostrar"""
        consumption_per_kw = efficiency_data.get('consumo_por_kw', 0)
        fuel_type = efficiency_data.get('tipo_combustible', 'combustible')
        
        if consumption_per_kw > 0:
            return f"{consumption_per_kw:.2f} L/h por KW"
        else:
            return "Consumo no especificado"