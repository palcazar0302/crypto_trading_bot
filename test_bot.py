#!/usr/bin/env python3
"""
Bot de prueba ultra simplificado
"""
import time
import schedule
import logging
from datetime import datetime
import sys
import os

# Agregar el directorio actual al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import Config

# Configurar logging simple
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'logs/test_bot_{datetime.now().strftime("%Y-%m-%d")}.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class TestBot:
    def __init__(self):
        self.logger = logger
        self.is_running = False
        
    def start(self):
        """Iniciar el bot de prueba"""
        try:
            self.logger.info("🤖 Iniciando bot de prueba...")
            
            # Programar tareas
            schedule.every(1).minutes.do(self._test_cycle)
            
            self.is_running = True
            self.logger.info("✅ Bot de prueba iniciado correctamente")
            
            # Loop principal
            while self.is_running:
                schedule.run_pending()
                time.sleep(1)
                
        except KeyboardInterrupt:
            self.logger.info("🛑 Bot detenido por el usuario")
        except Exception as e:
            self.logger.error(f"❌ Error: {e}")
    
    def _test_cycle(self):
        """Ciclo de prueba"""
        try:
            self.logger.info("🔄 Ejecutando ciclo de prueba...")
            
            for symbol in Config.SYMBOLS:
                self.logger.info(f"📊 Analizando {symbol}...")
                time.sleep(0.1)  # Pequeña pausa
            
            self.logger.info("✅ Ciclo de prueba completado")
            
        except Exception as e:
            self.logger.error(f"❌ Error en ciclo de prueba: {e}")
    
    def stop(self):
        """Detener el bot"""
        self.logger.info("🛑 Deteniendo bot...")
        self.is_running = False

if __name__ == "__main__":
    bot = TestBot()
    try:
        bot.start()
    except KeyboardInterrupt:
        bot.stop()
    except Exception as e:
        print(f"Error fatal: {e}")
        bot.stop()
