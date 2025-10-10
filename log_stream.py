#!/usr/bin/env python3
"""
Sistema de streaming de logs en tiempo real para el dashboard
"""
import time
import threading
from datetime import datetime
import os

class LogStreamer:
    def __init__(self, log_file_path):
        self.log_file_path = log_file_path
        self.last_position = 0
        self.new_logs = []
        self.lock = threading.Lock()
        
    def get_new_logs(self):
        """Obtener nuevos logs desde la última lectura"""
        try:
            with open(self.log_file_path, 'r', encoding='utf-8') as f:
                f.seek(self.last_position)
                new_content = f.read()
                self.last_position = f.tell()
                
                if new_content:
                    lines = new_content.strip().split('\n')
                    with self.lock:
                        self.new_logs.extend(lines)
                        
        except FileNotFoundError:
            return []
        except Exception as e:
            print(f"Error reading logs: {e}")
            return []
            
        return self.new_logs.copy()
    
    def get_recent_logs(self, num_lines=10):
        """Obtener las últimas N líneas del log"""
        try:
            with open(self.log_file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                return [line.strip() for line in lines[-num_lines:] if line.strip()]
        except FileNotFoundError:
            return ["Archivo de log no encontrado"]
        except Exception as e:
            return [f"Error leyendo logs: {e}"]

# Instancia global del streamer
log_streamer = None

def get_log_streamer():
    """Obtener instancia del log streamer"""
    global log_streamer
    if log_streamer is None:
        log_file = f"logs/crypto_bot_{datetime.now().strftime('%Y-%m-%d')}.log"
        log_streamer = LogStreamer(log_file)
    return log_streamer

if __name__ == "__main__":
    streamer = get_log_streamer()
    while True:
        logs = streamer.get_new_logs()
        if logs:
            for log in logs:
                print(log)
        time.sleep(1)
