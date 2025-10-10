#!/usr/bin/env python3
"""
Bot simplificado que funciona sin verificar balance
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
from exchange_manager import ExchangeManager
from technical_analysis import TechnicalAnalysis
from risk_manager import RiskManager
from logger_config import setup_logger

class SimpleTradingBot:
    def __init__(self):
        self.logger = setup_logger('simple_bot')
        self.exchange = ExchangeManager()
        self.ta = TechnicalAnalysis()
        self.risk_manager = RiskManager()
        self.is_running = False
        
    def start(self):
        """Iniciar el bot simplificado"""
        try:
            self.logger.info("🤖 Iniciando bot simplificado de trading...")
            
            # Programar tareas
            schedule.every(5).minutes.do(self._run_trading_cycle)
            
            self.is_running = True
            self.logger.info("✅ Bot simplificado iniciado correctamente")
            
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
                    
                    # Log de señales
                    if signals['buy'] or signals['sell']:
                        self.logger.info(f"🎯 {symbol}: {'COMPRA' if signals['buy'] else 'VENTA'} - Confianza: {signals['confidence']:.2f}")
                    
                except Exception as e:
                    self.logger.error(f"❌ Error analizando {symbol}: {e}")
                    continue
            
            self.logger.info("✅ Ciclo de trading completado")
            
        except Exception as e:
            self.logger.error(f"❌ Error en ciclo de trading: {e}")
    
    def stop(self):
        """Detener el bot"""
        self.logger.info("🛑 Deteniendo bot...")
        self.is_running = False

if __name__ == "__main__":
    bot = SimpleTradingBot()
    try:
        bot.start()
    except KeyboardInterrupt:
        bot.stop()
    except Exception as e:
        print(f"Error fatal: {e}")
        bot.stop()
