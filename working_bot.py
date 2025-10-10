#!/usr/bin/env python3
"""
Bot que funciona y se integra con el dashboard web
"""
import time
import schedule
import logging
from datetime import datetime
import sys
import os
import threading
import json

# Agregar el directorio actual al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import Config
from exchange_manager import ExchangeManager
from technical_analysis import TechnicalAnalysis
from risk_manager import RiskManager
from logger_config import setup_logger

class WorkingTradingBot:
    def __init__(self):
        self.logger = setup_logger('working_bot')
        self.exchange = ExchangeManager()
        self.ta = TechnicalAnalysis()
        self.risk_manager = RiskManager()
        self.is_running = False
        self.last_activity = datetime.now()
        
    def start(self):
        """Iniciar el bot"""
        try:
            self.logger.info("🤖 Iniciando bot de trading funcional...")
            
            # Programar tareas
            schedule.every(2).minutes.do(self._run_trading_cycle)
            
            self.is_running = True
            self.logger.info("✅ Bot de trading iniciado correctamente")
            
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
                    else:
                        self.logger.info(f"📊 {symbol}: Sin señales - Confianza: {signals['confidence']:.2f}")
                    
                    self.last_activity = datetime.now()
                    
                except Exception as e:
                    self.logger.error(f"❌ Error analizando {symbol}: {e}")
                    continue
            
            self.logger.info("✅ Ciclo de trading completado")
            
        except Exception as e:
            self.logger.error(f"❌ Error en ciclo de trading: {e}")
    
    def get_status(self):
        """Obtener estado del bot para el dashboard"""
        try:
            account_balance = 0.0  # En testnet puede ser 0
            portfolio_metrics = self.risk_manager.calculate_portfolio_metrics(account_balance)
            
            return {
                "status": {
                    "running": self.is_running,
                    "last_update": self.last_activity.isoformat()
                },
                "portfolio": portfolio_metrics,
                "balance": {"USDT": {"free": account_balance}},
                "positions": list(self.risk_manager.open_positions.values())
            }
        except Exception as e:
            self.logger.error(f"Error obteniendo estado: {e}")
            return {}
    
    def stop(self):
        """Detener el bot"""
        self.logger.info("🛑 Deteniendo bot...")
        self.is_running = False

# Instancia global del bot
working_bot_instance = None

def get_bot_instance():
    """Obtener instancia del bot"""
    global working_bot_instance
    if working_bot_instance is None:
        working_bot_instance = WorkingTradingBot()
    return working_bot_instance

if __name__ == "__main__":
    bot = WorkingTradingBot()
    try:
        bot.start()
    except KeyboardInterrupt:
        bot.stop()
    except Exception as e:
        print(f"Error fatal: {e}")
        bot.stop()
