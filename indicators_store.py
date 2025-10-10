#!/usr/bin/env python3
"""
Almacenamiento compartido de indicadores entre el bot y el dashboard
"""
import json
import os
from datetime import datetime
from typing import Dict

INDICATORS_FILE = 'data/indicators.json'

def save_indicators(indicators: Dict):
    """Guardar indicadores en archivo JSON"""
    try:
        os.makedirs('data', exist_ok=True)
        
        data = {
            'indicators': indicators,
            'timestamp': datetime.now().isoformat()
        }
        
        with open(INDICATORS_FILE, 'w') as f:
            json.dump(data, f, indent=2)
            
    except Exception as e:
        print(f"Error guardando indicadores: {e}")

def load_indicators() -> Dict:
    """Cargar indicadores desde archivo JSON"""
    try:
        if not os.path.exists(INDICATORS_FILE):
            return {}
        
        with open(INDICATORS_FILE, 'r') as f:
            data = json.load(f)
            return data.get('indicators', {})
            
    except Exception as e:
        print(f"Error cargando indicadores: {e}")
        return {}

def get_indicators_with_timestamp() -> Dict:
    """Obtener indicadores con timestamp"""
    try:
        if not os.path.exists(INDICATORS_FILE):
            return {
                'indicators': {},
                'timestamp': datetime.now().isoformat()
            }
        
        with open(INDICATORS_FILE, 'r') as f:
            return json.load(f)
            
    except Exception as e:
        print(f"Error cargando indicadores: {e}")
        return {
            'indicators': {},
            'timestamp': datetime.now().isoformat()
        }

