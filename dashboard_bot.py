#!/usr/bin/env python3
"""
Bot que se integra perfectamente con el dashboard
"""
import time
import schedule
import logging
from datetime import datetime
import sys
import os
import threading

# Agregar el directorio actual al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import Config
from exchange_manager import ExchangeManager
from technical_analysis import TechnicalAnalysis
from risk_manager import RiskManager
from logger_config import setup_logger
from indicators_store import save_indicators
from bot_status import save_status

class DashboardBot:
    def __init__(self):
        self.logger = setup_logger('crypto_bot')  # Usar el mismo logger que el dashboard
        self.exchange = ExchangeManager()
        self.ta = TechnicalAnalysis()
        self.risk_manager = RiskManager()
        self.is_running = False
        self.last_activity = datetime.now()
        self.last_analysis = {}  # Almacenar análisis de indicadores
        
    def start(self):
        """Iniciar el bot"""
        try:
            self.logger.info("🤖 Iniciando bot de trading de criptomonedas...")
            
            # Programar tareas
            schedule.every(2).minutes.do(self._run_trading_cycle)
            
            self.is_running = True
            save_status(True, datetime.now())  # Guardar estado inicial
            self.logger.info("✅ Bot iniciado correctamente")
            
            # Loop principal
            while self.is_running:
                schedule.run_pending()
                time.sleep(1)
                
        except KeyboardInterrupt:
            self.logger.info("🛑 Bot detenido por el usuario")
        except Exception as e:
            self.logger.error(f"❌ Error: {e}")
    
    def _run_trading_cycle(self):
        """Ejecutar ciclo de trading"""
        try:
            self.logger.info("🔄 Ejecutando ciclo de trading...")
            
            for symbol in Config.SYMBOLS:
                try:
                    self.logger.info(f"📊 Analizando {symbol}...")
                    
                    # Obtener datos OHLCV
                    ohlcv_data = self.exchange.get_ohlcv(symbol, Config.TIMEFRAME, 100)
                    if not ohlcv_data:
                        self.logger.warning(f"⚠️ No se pudieron obtener datos para {symbol}")
                        continue
                    
                    # Preparar DataFrame
                    df = self.ta.prepare_dataframe(ohlcv_data)
                    if df.empty:
                        continue
                    
                    # Generar señales
                    signals = self.ta.get_trading_signals(df)
                    
                    # Guardar análisis de indicadores
                    self.last_analysis[symbol] = {
                        'indicators': signals.get('indicators', {}),
                        'buy': signals.get('buy', False),
                        'sell': signals.get('sell', False),
                        'confidence': signals.get('confidence', 0.0),
                        'timestamp': datetime.now().isoformat()
                    }
                    
                    # Log de señales
                    if signals['buy'] or signals['sell']:
                        self.logger.info(f"🎯 {symbol}: {'COMPRA' if signals['buy'] else 'VENTA'} - Confianza: {signals['confidence']:.2f}")
                    else:
                        self.logger.info(f"📊 {symbol}: Sin señales - Confianza: {signals['confidence']:.2f}")
                    
                    self.last_activity = datetime.now()
                    
                except Exception as e:
                    self.logger.error(f"❌ Error analizando {symbol}: {e}")
                    continue
            
            # Guardar indicadores en archivo compartido
            save_indicators(self.last_analysis)
            
            # Actualizar estado del bot
            save_status(True, self.last_activity)
            
            self.logger.info("✅ Ciclo de trading completado")
            
        except Exception as e:
            self.logger.error(f"❌ Error en ciclo de trading: {e}")
    
    def stop(self):
        """Detener el bot"""
        self.logger.info("🛑 Deteniendo bot...")
        self.is_running = False
        save_status(False, datetime.now())  # Guardar estado de detenido

# Instancia global del bot
_bot_instance = None

def get_bot_instance():
    """Obtener instancia del bot"""
    global _bot_instance
    if _bot_instance is None:
        _bot_instance = DashboardBot()
    return _bot_instance

if __name__ == "__main__":
    bot = get_bot_instance()
    try:
        bot.start()
    except KeyboardInterrupt:
        bot.stop()
    except Exception as e:
        print(f"Error fatal: {e}")
        bot.stop()
