# -*- coding: utf-8 -*-
"""
Detector universal de características para TODOS los productos
"""
import re
from typing import Dict, Any, List, Optional

class UniversalFeatureDetector:
    """Detector universal de características especiales para cualquier producto"""
    
    # Mapeo de iconos por categoría y campo
    ICON_MAPPING = {
        # Iconos por campo específico
        'fields': {
            # Potencia
            'potencia': 'lightning',
            'potencia_kva': 'lightning',
            'potencia_kw': 'lightning',
            'potencia_hp': 'lightning',
            'potencia_max_w': 'lightning',
            
            # Motor
            'motor': 'settings',
            'marca_motor': 'settings',
            'modelo_motor': 'settings',
            'cilindrada': 'engine',
            'cilindros': 'engine',
            'rpm': 'tachometer',
            
            # Combustible
            'combustible': 'fuel',
            'consumo': 'fuel',
            'capacidad_tanque': 'fuel',
            'autonomia': 'clock',
            
            # Arranque
            'tipo_arranque': 'power',
            'arranque': 'power',
            'bateria': 'battery',
            'alternador': 'bolt',
            'controlador': 'cpu',
            'panel_control': 'monitor',
            
            # Físicas
            'dimensiones': 'ruler',
            'peso': 'weight',
            'largo': 'ruler',
            'ancho': 'ruler',
            'alto': 'ruler',
            
            # Ambiente
            'nivel_ruido': 'volume',
            'nivel_sonoro': 'volume',
            'temperatura_operacion': 'thermometer',
            'temperatura_trabajo': 'thermometer',
            
            # Eléctrico
            'voltaje': 'bolt',
            'frecuencia': 'activity',
            'fases': 'zap',
            'factor_potencia': 'percent',
            
            # Certificaciones
            'certificaciones': 'award',
            'garantia': 'shield',
            
            # Específicos por tipo
            'presion': 'gauge',
            'caudal': 'droplet',
            'diametro_succion': 'circle',
            'profundidad_corte': 'ruler',
            'diametro_disco': 'disc',
            'capacidad_aceite': 'droplet'
        },
        
        # Iconos por categoría de producto
        'categories': {
            'generador': 'power',
            'bomba': 'droplet',
            'compresor': 'wind',
            'motocultor': 'tractor',
            'chipeadora': 'tree',
            'fumigadora': 'spray',
            'construccion': 'hammer',
            'herramienta': 'tool'
        },
        
        # Iconos por característica especial
        'features': {
            'portatil': 'move',
            'insonorizado': 'volume-x',
            'avr': 'cpu',
            'monofasico': 'zap',
            'trifasico': 'zap-off',
            'arranque_electrico': 'power',
            'arranque_manual': 'hand',
            'inverter': 'cpu',
            'industrial': 'factory',
            'profesional': 'briefcase',
            'alta_presion': 'trending-up',
            'bajo_consumo': 'battery-charging',
            'silencioso': 'volume-x'
        }
    }
    
    # Palabras clave para detectar características
    FEATURE_KEYWORDS = {
        'portatil': ['portátil', 'portable', 'móvil', 'transportable'],
        'insonorizado': ['insonorizado', 'silencioso', 'cabinado', 'silent'],
        'avr': ['avr', 'regulador automático', 'automatic voltage'],
        'inverter': ['inverter', 'inversor'],
        'industrial': ['industrial', 'profesional', 'heavy duty'],
        'alta_eficiencia': ['alta eficiencia', 'bajo consumo', 'económico'],
        'arranque_electrico': ['arranque eléctrico', 'electric start', 'e-start'],
        'panel_digital': ['panel digital', 'display digital', 'lcd', 'led'],
        'proteccion_ip': ['ip23', 'ip54', 'ip55', 'protección ip'],
        'motor_marca': ['honda', 'yamaha', 'cummins', 'perkins', 'kohler'],
        'certificado': ['certificado', 'iso', 'ce', 'certificación']
    }
    
    @classmethod
    def detect_all(cls, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Detecta todas las características del producto
        
        Returns:
            Dict con tipo_producto, tipo_combustible, es_portatil, 
            caracteristicas_principales, badges_especiales
        """
        # Detectar tipo de producto
        product_type = cls._detect_product_type(data)
        
        # Detectar tipo de combustible
        fuel_type = cls._detect_fuel_type(data)
        
        # Detectar si es portátil
        is_portable = cls._detect_portable(data, product_type, fuel_type)
        
        # Detectar características principales
        main_features = cls._detect_main_features(data)
        
        # Generar badges especiales
        special_badges = cls._generate_special_badges(data, product_type, fuel_type, is_portable)
        
        # Detectar categorías de iconos
        icon_categories = cls._detect_icon_categories(data, product_type)
        
        return {
            'tipo_producto': product_type,
            'tipo_combustible': fuel_type,
            'es_portatil': is_portable,
            'caracteristicas_principales': main_features,
            'badges_especiales': special_badges,
            'categorias_iconos': icon_categories,
            'tiene_caracteristicas_premium': len(special_badges) > 2
        }
    
    @classmethod
    def _detect_product_type(cls, data: Dict[str, Any]) -> str:
        """Detecta el tipo de producto"""
        # Buscar en múltiples campos
        nombre = str(data.get('nombre', '')).lower()
        familia = str(data.get('familia', '')).lower()
        categoria = str(data.get('categoria_producto', '')).lower()
        modelo = str(data.get('modelo', '')).lower()
        
        texto_completo = f"{nombre} {familia} {categoria} {modelo}"
        
        # Mapeo de tipos
        type_patterns = {
            'generador': ['generador', 'generator', 'grupo electrógeno'],
            'bomba': ['bomba', 'motobomba', 'pump'],
            'compresor': ['compresor', 'compressor'],
            'motocultor': ['motocultor', 'motocultivador', 'tiller'],
            'chipeadora': ['chipeadora', 'chipper', 'trituradora'],
            'fumigadora': ['fumigadora', 'pulverizadora', 'sprayer'],
            'soldadora': ['soldadora', 'welder', 'soldador'],
            'cortadora': ['cortadora', 'cortador', 'cutter'],
            'vibrador': ['vibrador', 'vibrator', 'vibradora'],
            'hidrolavadora': ['hidrolavadora', 'hidrolimpiadora', 'pressure washer']
        }
        
        for product_type, keywords in type_patterns.items():
            if any(keyword in texto_completo for keyword in keywords):
                return product_type
        
        return 'equipo'  # Default
    
    @classmethod
    def _detect_fuel_type(cls, data: Dict[str, Any]) -> str:
        """Detecta el tipo de combustible"""
        combustible = str(data.get('combustible', '')).lower()
        nombre = str(data.get('nombre', '')).lower()
        modelo = str(data.get('modelo', '')).lower()
        
        texto_completo = f"{combustible} {nombre} {modelo}"
        
        if any(term in texto_completo for term in ['nafta', 'gasolina', 'bencina']):
            return 'nafta'
        elif any(term in texto_completo for term in ['diesel', 'gasoil', 'diésel']):
            return 'diesel'
        elif any(term in texto_completo for term in ['gas', 'glp', 'gnc']):
            return 'gas'
        elif any(term in texto_completo for term in ['eléctric', 'electric']):
            return 'electrico'
        
        # Default según producto
        if 'generador' in texto_completo:
            # Generadores pequeños suelen ser nafta
            power = cls._extract_numeric_value(data.get('potencia_kva', ''))
            if power and power < 10:
                return 'nafta'
        
        return 'combustible'
    
    @classmethod
    def _detect_portable(cls, data: Dict[str, Any], product_type: str, fuel_type: str) -> bool:
        """Detecta si el producto es portátil"""
        # Buscar en nombre y modelo
        nombre = str(data.get('nombre', '')).lower()
        modelo = str(data.get('modelo', '')).lower()
        
        # Si dice explícitamente portátil
        if any(word in f"{nombre} {modelo}" for word in ['portátil', 'portable']):
            return True
        
        # Por peso según tipo
        peso_str = str(data.get('peso_kg', data.get('peso', '')))
        peso = cls._extract_numeric_value(peso_str)
        
        if peso:
            # Umbrales por tipo de producto
            if product_type == 'generador':
                if fuel_type == 'nafta':
                    return peso < 60  # Generadores nafta < 60kg son portátiles
                elif fuel_type == 'diesel':
                    return peso < 100  # Diesel más pesados
            elif product_type == 'bomba':
                return peso < 30
            elif product_type == 'compresor':
                return peso < 40
        
        # Por características del arranque
        arranque = str(data.get('tipo_arranque', data.get('arranque', ''))).lower()
        if 'manual' in arranque and product_type == 'generador':
            # Arranque manual suele indicar portátil
            return True
        
        return False
    
    @classmethod
    def _detect_main_features(cls, data: Dict[str, Any]) -> List[str]:
        """Detecta las características principales del producto"""
        features = []
        
        # Buscar en todos los campos relevantes
        search_text = ' '.join([
            str(data.get('nombre', '')),
            str(data.get('descripcion', '')),
            str(data.get('caracteristicas', '')),
            str(data.get('especificaciones', ''))
        ]).lower()
        
        # Detectar por palabras clave
        for feature, keywords in cls.FEATURE_KEYWORDS.items():
            if any(keyword in search_text for keyword in keywords):
                features.append(feature)
        
        # Características específicas por datos
        # AVR
        if data.get('avr') or data.get('regulador_tension'):
            features.append('avr')
        
        # Arranque eléctrico
        arranque = str(data.get('tipo_arranque', '')).lower()
        if 'eléctrico' in arranque or 'electric' in arranque:
            features.append('arranque_electrico')
        
        # Panel digital
        if data.get('panel_control') or data.get('controlador'):
            features.append('panel_control')
        
        # Insonorizado por nivel de ruido
        ruido_str = str(data.get('nivel_ruido_dba', data.get('nivel_ruido', '')))
        ruido = cls._extract_numeric_value(ruido_str)
        if ruido and ruido < 70:
            features.append('silencioso')
        
        return list(set(features))  # Eliminar duplicados
    
    @classmethod
    def _generate_special_badges(cls, data: Dict[str, Any], product_type: str, 
                                fuel_type: str, is_portable: bool) -> List[Dict[str, Any]]:
        """Genera badges especiales para mostrar"""
        badges = []
        
        # Badge de portátil
        if is_portable:
            badges.append({
                'texto': 'PORTÁTIL',
                'color': '#2196F3',
                'icono': 'move'
            })
        
        # Badge por tipo de combustible especial
        if fuel_type == 'diesel':
            badges.append({
                'texto': 'DIESEL',
                'color': '#795548',
                'icono': 'fuel'
            })
        elif fuel_type == 'gas':
            badges.append({
                'texto': 'GAS',
                'color': '#009688',
                'icono': 'fuel'
            })
        
        # Badge por características detectadas
        features = cls._detect_main_features(data)
        
        if 'inverter' in features:
            badges.append({
                'texto': 'INVERTER',
                'color': '#9C27B0',
                'icono': 'cpu'
            })
        
        if 'insonorizado' in features:
            badges.append({
                'texto': 'INSONORIZADO',
                'color': '#607D8B',
                'icono': 'volume-x'
            })
        
        if 'avr' in features:
            badges.append({
                'texto': 'AVR',
                'color': '#FF5722',
                'icono': 'shield'
            })
        
        if 'arranque_electrico' in features:
            badges.append({
                'texto': 'ARRANQUE ELÉCTRICO',
                'color': '#4CAF50',
                'icono': 'power'
            })
        
        # Badge por certificaciones
        if data.get('certificaciones'):
            badges.append({
                'texto': 'CERTIFICADO',
                'color': '#FFC107',
                'icono': 'award'
            })
        
        # Badge por garantía extendida
        garantia_str = str(data.get('garantia', ''))
        garantia_num = cls._extract_numeric_value(garantia_str)
        if garantia_num and garantia_num >= 2:
            badges.append({
                'texto': f'{int(garantia_num)} AÑOS GARANTÍA',
                'color': '#4CAF50',
                'icono': 'shield'
            })
        
        # Badge por motor de marca
        motor = str(data.get('motor', data.get('marca_motor', ''))).lower()
        for marca in ['honda', 'yamaha', 'cummins', 'perkins', 'kohler', 'briggs']:
            if marca in motor:
                badges.append({
                    'texto': f'MOTOR {marca.upper()}',
                    'color': '#3F51B5',
                    'icono': 'settings'
                })
                break
        
        # Limitar a los más importantes (máximo 4)
        return badges[:4]
    
    @classmethod
    def _detect_icon_categories(cls, data: Dict[str, Any], product_type: str) -> List[str]:
        """Detecta las categorías de iconos aplicables"""
        categories = [product_type]
        
        # Agregar categorías por características
        features = cls._detect_main_features(data)
        
        if 'industrial' in features or 'profesional' in features:
            categories.append('industrial')
        
        if 'portatil' in features:
            categories.append('portatil')
        
        return categories
    
    @classmethod
    def get_icon_for_field(cls, field_name: str, value: Any = None) -> str:
        """Obtiene el icono apropiado para un campo"""
        # Buscar en mapeo de campos
        field_lower = field_name.lower()
        
        # Coincidencia exacta
        if field_lower in cls.ICON_MAPPING['fields']:
            return cls.ICON_MAPPING['fields'][field_lower]
        
        # Coincidencia parcial
        for field, icon in cls.ICON_MAPPING['fields'].items():
            if field in field_lower or field_lower in field:
                return icon
        
        # Por palabras clave en el nombre del campo
        if any(word in field_lower for word in ['potencia', 'power', 'kva', 'kw']):
            return 'lightning'
        elif any(word in field_lower for word in ['motor', 'engine']):
            return 'settings'
        elif any(word in field_lower for word in ['combustible', 'fuel', 'consumo']):
            return 'fuel'
        elif any(word in field_lower for word in ['tanque', 'tank', 'capacidad']):
            return 'database'
        elif any(word in field_lower for word in ['peso', 'weight']):
            return 'weight'
        elif any(word in field_lower for word in ['dimensi', 'size', 'largo', 'ancho', 'alto']):
            return 'ruler'
        elif any(word in field_lower for word in ['ruido', 'noise', 'sonoro']):
            return 'volume'
        elif any(word in field_lower for word in ['temperatura', 'temp']):
            return 'thermometer'
        elif any(word in field_lower for word in ['presion', 'pressure']):
            return 'gauge'
        elif any(word in field_lower for word in ['caudal', 'flow']):
            return 'droplet'
        elif any(word in field_lower for word in ['voltaje', 'voltage', 'volt']):
            return 'zap'
        elif any(word in field_lower for word in ['frecuencia', 'frequency', 'hz']):
            return 'activity'
        elif any(word in field_lower for word in ['certificac', 'certif']):
            return 'award'
        elif any(word in field_lower for word in ['garantia', 'warranty']):
            return 'shield'
        
        # Default
        return 'info'
    
    @classmethod
    def _extract_numeric_value(cls, text: str) -> Optional[float]:
        """Extrae valor numérico de un texto"""
        if not text:
            return None
            
        try:
            # Buscar primer número en el texto
            match = re.search(r'(\d+\.?\d*)', str(text))
            if match:
                return float(match.group(1))
        except:
            pass
        
        return None