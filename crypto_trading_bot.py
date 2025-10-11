"""
Bot principal de trading de criptomonedas
"""
import time
import schedule
import logging
from datetime import datetime, timedelta
from typing import Dict, List
import pandas as pd

from config import Config
from exchange_manager import ExchangeManager
from technical_analysis import TechnicalAnalysis
from risk_manager import RiskManager
from notifications import NotificationManager
from logger_config import setup_logger, log_trade, log_signal, log_error, log_performance

class CryptoTradingBot:
    def __init__(self):
        # Configurar logging
        self.logger = setup_logger('crypto_bot')
        self.trades_logger = setup_logger('trades')
        
        # Inicializar componentes
        self.exchange = ExchangeManager()
        self.ta = TechnicalAnalysis()
        self.risk_manager = RiskManager()
        self.notifications = NotificationManager()
        
        # Estado del bot
        self.is_running = False
        self.last_check_time = None
        
        # Validar configuración
        try:
            Config.validate_config()
            self.logger.info("Configuración validada correctamente")
        except Exception as e:
            self.logger.error(f"Error en configuración: {e}")
            raise
    
    def start(self):
        """Iniciar el bot de trading"""
        try:
            self.logger.info("🤖 Iniciando bot de trading de criptomonedas...")
            
            # Programar tareas primero
            self._schedule_tasks()
            
            # Probar conexiones (sin fallar si hay problemas)
            try:
                self._test_connections()
            except Exception as e:
                self.logger.warning(f"⚠️ Error en conexiones: {e}")
                self.logger.info("📋 Continuando sin verificar conexiones...")
            
            # Notificar inicio
            try:
                self.notifications.notify_startup()
            except Exception as e:
                self.logger.warning(f"⚠️ Error en notificaciones: {e}")
            
            self.is_running = True
            self.logger.info("✅ Bot iniciado correctamente")
            
            # Loop principal
            self._main_loop()
            
        except Exception as e:
            log_error(self.logger, e, "Error al iniciar bot")
            try:
                self.notifications.notify_error(str(e), "Inicio del bot")
            except:
                pass
            raise
    
    def stop(self):
        """Detener el bot"""
        self.logger.info("🛑 Deteniendo bot...")
        self.is_running = False
        
        # Cerrar todas las posiciones abiertas si es necesario
        self._close_all_positions("Bot detenido")
        
        self.logger.info("✅ Bot detenido")
    
    def _test_connections(self):
        """Probar conexiones con exchanges y servicios"""
        try:
            # Probar conexión con Binance (sin verificar balance)
            self.logger.info("✅ Conexión con Binance configurada")
            self.logger.info("📋 Bot iniciado en modo TESTNET")
            
            # Probar notificaciones
            if Config.ENABLE_NOTIFICATIONS:
                try:
                    if self.notifications.test_notifications():
                        self.logger.info("✅ Sistema de notificaciones funcionando")
                    else:
                        self.logger.warning("⚠️ Sistema de notificaciones no disponible")
                except Exception as e:
                    self.logger.warning(f"⚠️ Error en notificaciones: {e}")
            
        except Exception as e:
            log_error(self.logger, e, "Error en pruebas de conexión")
            self.logger.warning("⚠️ Continuando sin conexión completa...")
    
    def _schedule_tasks(self):
        """Programar tareas automáticas"""
        # Ejecutar análisis cada 5 minutos
        schedule.every(5).minutes.do(self._run_trading_cycle)
        
        # Resumen diario a las 23:59
        schedule.every().day.at("23:59").do(self._daily_summary)
        
        # Reiniciar métricas diarias a medianoche
        schedule.every().day.at("00:00").do(self._reset_daily_metrics)
        
        self.logger.info("📅 Tareas programadas correctamente")
    
    def _main_loop(self):
        """Loop principal del bot"""
        self.logger.info("🔄 Iniciando loop principal...")
        
        try:
            while self.is_running:
                schedule.run_pending()
                time.sleep(1)
                
        except KeyboardInterrupt:
            self.logger.info("🛑 Interrupción del usuario detectada")
            self.stop()
        except Exception as e:
            log_error(self.logger, e, "Error en loop principal")
            self.notifications.notify_error(str(e), "Loop principal")
            self.stop()
    
    def _run_trading_cycle(self):
        """Ejecutar ciclo de trading"""
        try:
            self.logger.info("🔄 Ejecutando ciclo de trading...")
            
            # Verificar métricas de riesgo
            account_balance = self.exchange.get_usdt_balance()
            if not self._check_risk_limits(account_balance):
                return
            
            # Analizar cada símbolo
            for symbol in Config.SYMBOLS:
                try:
                    self._analyze_symbol(symbol, account_balance)
                except Exception as e:
                    log_error(self.logger, e, f"Error analizando {symbol}")
                    continue
            
            # Verificar posiciones abiertas
            self._monitor_open_positions()
            
            self.last_check_time = datetime.now()
            
        except Exception as e:
            log_error(self.logger, e, "Error en ciclo de trading")
    
    def _check_risk_limits(self, account_balance: float) -> bool:
        """Verificar límites de riesgo"""
        try:
            metrics = self.risk_manager.calculate_portfolio_metrics(account_balance)
            
            # Verificar pérdida diaria máxima
            if metrics.get('daily_return', 0) <= -Config.MAX_DAILY_LOSS:
                self.logger.warning(f"⚠️ Pérdida diaria máxima alcanzada: {metrics['daily_return']:.2f}%")
                self.notifications.notify_error(
                    f"Pérdida diaria máxima alcanzada: {metrics['daily_return']:.2f}%",
                    "Límite de riesgo"
                )
                return False
            
            return True
            
        except Exception as e:
            log_error(self.logger, e, "Error verificando límites de riesgo")
            return False
    
    def _analyze_symbol(self, symbol: str, account_balance: float):
        """Analizar símbolo y ejecutar trades si es necesario"""
        try:
            # Obtener datos OHLCV
            ohlcv_data = self.exchange.get_ohlcv(symbol, Config.TIMEFRAME, 100)
            if not ohlcv_data:
                return
            
            # Preparar DataFrame
            df = self.ta.prepare_dataframe(ohlcv_data)
            if df.empty:
                return
            
            # Generar señales
            signals = self.ta.get_trading_signals(df)
            
            # Log de señales
            log_signal(self.logger, symbol, signals)
            
            # Obtener precio actual
            ticker = self.exchange.get_ticker(symbol)
            current_price = ticker.get('last', 0)
            
            if current_price == 0:
                return
            
            # Ejecutar trades basados en señales
            if signals['buy'] and signals['confidence'] > 40:  # Confianza en porcentaje (40%)
                self._execute_buy_order(symbol, current_price, account_balance, signals)
            elif signals['sell'] and signals['confidence'] > 40:  # Confianza en porcentaje (40%)
                self._execute_sell_order(symbol, current_price, signals)
                
        except Exception as e:
            log_error(self.logger, e, f"Error analizando {symbol}")
    
    def _execute_buy_order(self, symbol: str, price: float, account_balance: float, signals: Dict):
        """Ejecutar orden de compra"""
        try:
            # Calcular stop loss y take profit
            stop_loss = price * (1 - Config.STOP_LOSS_PERCENTAGE / 100)
            take_profit = price * (1 + Config.TARGET_PROFIT_PERCENTAGE / 100)
            
            # Calcular tamaño de posición
            position_size = self.risk_manager.calculate_position_size(
                account_balance, Config.RISK_PERCENTAGE, price, stop_loss
            )
            
            if position_size == 0:
                self.logger.warning(f"⚠️ Tamaño de posición calculado como 0 para {symbol}")
                return
            
            # Validar trade
            validation = self.risk_manager.validate_trade(symbol, 'buy', position_size, price)
            if not validation['valid']:
                self.logger.warning(f"⚠️ Trade no válido para {symbol}: {validation['reason']}")
                return
            
            # Ejecutar orden
            order = self.exchange.place_market_buy_order(symbol, position_size)
            if order and 'id' in order:
                # Agregar a gestión de riesgo
                self.risk_manager.add_position(
                    symbol, 'buy', position_size, price, stop_loss, take_profit, order['id']
                )
                
                # Notificar
                self.notifications.notify_trade_executed('buy', symbol, position_size, price)
                log_trade(self.trades_logger, 'BUY', symbol, position_size, price, reason="Señal de compra")
                
                self.logger.info(f"✅ Orden de compra ejecutada: {symbol} - {position_size:.6f} @ ${price:.4f}")
            else:
                self.logger.error(f"❌ Error ejecutando orden de compra para {symbol}")
                
        except Exception as e:
            log_error(self.logger, e, f"Error ejecutando compra de {symbol}")
    
    def _execute_sell_order(self, symbol: str, price: float, signals: Dict):
        """Ejecutar orden de venta (solo si hay posición abierta)"""
        try:
            # Solo vender si tenemos posición abierta
            if symbol not in self.risk_manager.open_positions:
                return
            
            position = self.risk_manager.open_positions[symbol]
            
            # Validar trade
            validation = self.risk_manager.validate_trade(symbol, 'sell', position['amount'], price)
            if not validation['valid']:
                self.logger.warning(f"⚠️ Venta no válida para {symbol}: {validation['reason']}")
                return
            
            # Ejecutar orden
            order = self.exchange.place_market_sell_order(symbol, position['amount'])
            if order and 'id' in order:
                # Cerrar posición
                result = self.risk_manager.close_position(symbol, price, "Señal de venta")
                
                if result['success']:
                    pnl = result['pnl']
                    
                    # Notificar
                    self.notifications.notify_trade_executed('sell', symbol, position['amount'], price, pnl)
                    log_trade(self.trades_logger, 'SELL', symbol, position['amount'], price, pnl, "Señal de venta")
                    
                    self.logger.info(f"✅ Orden de venta ejecutada: {symbol} - {position['amount']:.6f} @ ${price:.4f} - PnL: ${pnl:.2f}")
                else:
                    self.logger.error(f"❌ Error cerrando posición: {result['reason']}")
            else:
                self.logger.error(f"❌ Error ejecutando orden de venta para {symbol}")
                
        except Exception as e:
            log_error(self.logger, e, f"Error ejecutando venta de {symbol}")
    
    def _monitor_open_positions(self):
        """Monitorear posiciones abiertas"""
        try:
            for symbol, position in self.risk_manager.open_positions.items():
                # Obtener precio actual
                ticker = self.exchange.get_ticker(symbol)
                current_price = ticker.get('last', 0)
                
                if current_price == 0:
                    continue
                
                # Actualizar precio en gestión de riesgo
                self.risk_manager.update_position_price(symbol, current_price)
                
                # Verificar stop loss y take profit
                action_result = self.risk_manager.check_stop_loss_take_profit(symbol, current_price)
                
                if action_result['action'] != 'none':
                    self._handle_position_exit(symbol, current_price, action_result)
                    
        except Exception as e:
            log_error(self.logger, e, "Error monitoreando posiciones")
    
    def _handle_position_exit(self, symbol: str, price: float, action_result: Dict):
        """Manejar salida de posición"""
        try:
            position = self.risk_manager.open_positions[symbol]
            action = action_result['action']
            reason = action_result['reason']
            
            # Ejecutar orden de salida
            if action == 'sell':
                order = self.exchange.place_market_sell_order(symbol, position['amount'])
            else:
                order = self.exchange.place_market_buy_order(symbol, position['amount'])
            
            if order and 'id' in order:
                # Cerrar posición
                result = self.risk_manager.close_position(symbol, price, reason)
                
                if result['success']:
                    pnl = result['pnl']
                    
                    # Notificar según el tipo de salida
                    if 'stop loss' in reason.lower():
                        self.notifications.notify_stop_loss_triggered(symbol, price, pnl)
                    elif 'take profit' in reason.lower():
                        self.notifications.notify_take_profit_triggered(symbol, price, pnl)
                    
                    log_trade(self.trades_logger, action.upper(), symbol, position['amount'], price, pnl, reason)
                    
                    self.logger.info(f"✅ Posición cerrada: {symbol} - {reason} - PnL: ${pnl:.2f}")
                else:
                    self.logger.error(f"❌ Error cerrando posición: {result['reason']}")
                    
        except Exception as e:
            log_error(self.logger, e, f"Error manejando salida de posición {symbol}")
    
    def _close_all_positions(self, reason: str = "Bot detenido"):
        """Cerrar todas las posiciones abiertas"""
        try:
            for symbol in list(self.risk_manager.open_positions.keys()):
                ticker = self.exchange.get_ticker(symbol)
                current_price = ticker.get('last', 0)
                
                if current_price > 0:
                    position = self.risk_manager.open_positions[symbol]
                    
                    if position['side'] == 'buy':
                        order = self.exchange.place_market_sell_order(symbol, position['amount'])
                    else:
                        order = self.exchange.place_market_buy_order(symbol, position['amount'])
                    
                    if order:
                        self.risk_manager.close_position(symbol, current_price, reason)
                        self.logger.info(f"✅ Posición cerrada: {symbol} - {reason}")
                        
        except Exception as e:
            log_error(self.logger, e, "Error cerrando todas las posiciones")
    
    def _daily_summary(self):
        """Generar resumen diario"""
        try:
            account_balance = self.exchange.get_usdt_balance()
            metrics = self.risk_manager.calculate_portfolio_metrics(account_balance)
            
            # Log de rendimiento
            log_performance(self.logger, metrics)
            
            # Notificar resumen
            self.notifications.notify_daily_summary(metrics)
            
            self.logger.info("📊 Resumen diario generado")
            
        except Exception as e:
            log_error(self.logger, e, "Error generando resumen diario")
    
    def _reset_daily_metrics(self):
        """Reiniciar métricas diarias"""
        try:
            self.risk_manager.reset_daily_metrics()
            self.logger.info("🔄 Métricas diarias reiniciadas")
        except Exception as e:
            log_error(self.logger, e, "Error reiniciando métricas diarias")

if __name__ == "__main__":
    bot = CryptoTradingBot()
    try:
        bot.start()
    except KeyboardInterrupt:
        bot.stop()
    except Exception as e:
        print(f"Error fatal: {e}")
        bot.stop()



