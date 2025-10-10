#!/usr/bin/env python3
"""
Almacenamiento compartido del estado del bot
"""
import json
import os
from datetime import datetime
from typing import Dict

STATUS_FILE = 'data/bot_status.json'

def save_status(is_running: bool, last_activity: datetime = None):
    """Guardar estado del bot"""
    try:
        os.makedirs('data', exist_ok=True)
        
        data = {
            'running': is_running,
            'last_update': (last_activity or datetime.now()).isoformat()
        }
        
        with open(STATUS_FILE, 'w') as f:
            json.dump(data, f, indent=2)
            
    except Exception as e:
        print(f"Error guardando estado: {e}")

def load_status() -> Dict:
    """Cargar estado del bot"""
    try:
        if not os.path.exists(STATUS_FILE):
            return {
                'running': False,
                'last_update': datetime.now().isoformat()
            }
        
        with open(STATUS_FILE, 'r') as f:
            return json.load(f)
            
    except Exception as e:
        print(f"Error cargando estado: {e}")
        return {
            'running': False,
            'last_update': datetime.now().isoformat()
        }

