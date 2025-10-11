"""
Sistema de notificaciones para el bot de trading
"""
import requests
import logging
from typing import Dict, Optional
from config import Config

class NotificationManager:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.telegram_enabled = bool(Config.TELEGRAM_BOT_TOKEN and Config.TELEGRAM_CHAT_ID)
        
    def send_telegram_message(self, message: str, parse_mode: str = 'HTML') -> bool:
        """Enviar mensaje a Telegram"""
        if not self.telegram_enabled:
            return False
            
        try:
            url = f"https://api.telegram.org/bot{Config.TELEGRAM_BOT_TOKEN}/sendMessage"
            data = {
                'chat_id': Config.TELEGRAM_CHAT_ID,
                'text': message,
                'parse_mode': parse_mode
            }
            
            response = requests.post(url, data=data, timeout=10)
            response.raise_for_status()
            
            self.logger.info("Notificación enviada a Telegram")
            return True
            
        except Exception as e:
            self.logger.error(f"Error al enviar notificación a Telegram: {e}")
            return False
    
    def notify_trade_executed(self, trade_type: str, symbol: str, amount: float, 
                            price: float, pnl: float = None):
        """Notificar ejecución de trade"""
        try:
            emoji = "🟢" if trade_type == "buy" else "🔴"
            pnl_text = f"\n💰 PnL: ${pnl:.2f}" if pnl is not None else ""
            
            message = f"""
{emoji} <b>TRADE EJECUTADO</b>

📊 <b>Símbolo:</b> {symbol}
🔄 <b>Tipo:</b> {trade_type.upper()}
📈 <b>Cantidad:</b> {amount:.6f}
💵 <b>Precio:</b> ${price:.4f}{pnl_text}

⏰ {self._get_timestamp()}
            """.strip()
            
            if Config.ENABLE_NOTIFICATIONS:
                self.send_telegram_message(message)
                
        except Exception as e:
            self.logger.error(f"Error al notificar trade ejecutado: {e}")
    
    def notify_signal_generated(self, symbol: str, signal: Dict):
        """Notificar señal generada"""
        try:
            emoji = "🚀" if signal['buy'] else "📉"
            action = "COMPRA" if signal['buy'] else "VENTA"
            confidence = signal.get('confidence', 0)
            
            indicators_text = ""
            if 'indicators' in signal:
                for indicator, status in signal['indicators'].items():
                    indicators_text += f"\n• {indicator.upper()}: {status}"
            
            message = f"""
{emoji} <b>SEÑAL DE TRADING</b>

📊 <b>Símbolo:</b> {symbol}
🎯 <b>Acción:</b> {action}
🎖️ <b>Confianza:</b> {confidence:.1f}%{indicators_text}

⏰ {self._get_timestamp()}
            """.strip()
            
            if Config.ENABLE_NOTIFICATIONS:
                self.send_telegram_message(message)
                
        except Exception as e:
            self.logger.error(f"Error al notificar señal generada: {e}")
    
    def notify_stop_loss_triggered(self, symbol: str, price: float, pnl: float):
        """Notificar activación de stop loss"""
        try:
            emoji = "🛑"
            pnl_emoji = "💚" if pnl > 0 else "❤️"
            
            message = f"""
{emoji} <b>STOP LOSS ACTIVADO</b>

📊 <b>Símbolo:</b> {symbol}
💵 <b>Precio de salida:</b> ${price:.4f}
{pnl_emoji} <b>PnL:</b> ${pnl:.2f}

⏰ {self._get_timestamp()}
            """.strip()
            
            if Config.ENABLE_NOTIFICATIONS:
                self.send_telegram_message(message)
                
        except Exception as e:
            self.logger.error(f"Error al notificar stop loss: {e}")
    
    def notify_take_profit_triggered(self, symbol: str, price: float, pnl: float):
        """Notificar activación de take profit"""
        try:
            emoji = "🎯"
            
            message = f"""
{emoji} <b>TAKE PROFIT ACTIVADO</b>

📊 <b>Símbolo:</b> {symbol}
💵 <b>Precio de salida:</b> ${price:.4f}
💰 <b>PnL:</b> ${pnl:.2f}

⏰ {self._get_timestamp()}
            """.strip()
            
            if Config.ENABLE_NOTIFICATIONS:
                self.send_telegram_message(message)
                
        except Exception as e:
            self.logger.error(f"Error al notificar take profit: {e}")
    
    def notify_daily_summary(self, metrics: Dict):
        """Notificar resumen diario"""
        try:
            daily_return = metrics.get('daily_return', 0)
            total_return = metrics.get('total_return', 0)
            daily_pnl = metrics.get('daily_pnl', 0)
            total_pnl = metrics.get('total_pnl', 0)
            trades = metrics.get('daily_trades', 0)
            positions = metrics.get('open_positions', 0)
            
            # Emoji basado en rendimiento
            if daily_return > 0:
                emoji = "📈"
            elif daily_return < 0:
                emoji = "📉"
            else:
                emoji = "📊"
            
            message = f"""
{emoji} <b>RESUMEN DIARIO</b>

📊 <b>Rendimiento diario:</b> {daily_return:+.2f}%
📈 <b>Rendimiento total:</b> {total_return:+.2f}%
💰 <b>PnL diario:</b> ${daily_pnl:.2f}
💎 <b>PnL total:</b> ${total_pnl:.2f}
🔄 <b>Trades ejecutados:</b> {trades}
📋 <b>Posiciones abiertas:</b> {positions}

⏰ {self._get_timestamp()}
            """.strip()
            
            if Config.ENABLE_NOTIFICATIONS:
                self.send_telegram_message(message)
                
        except Exception as e:
            self.logger.error(f"Error al notificar resumen diario: {e}")
    
    def notify_error(self, error_message: str, context: str = ""):
        """Notificar error crítico"""
        try:
            message = f"""
🚨 <b>ERROR CRÍTICO</b>

⚠️ <b>Mensaje:</b> {error_message}
🔍 <b>Contexto:</b> {context}

⏰ {self._get_timestamp()}
            """.strip()
            
            if Config.ENABLE_NOTIFICATIONS:
                self.send_telegram_message(message)
                
        except Exception as e:
            self.logger.error(f"Error al notificar error: {e}")
    
    def notify_startup(self):
        """Notificar inicio del bot"""
        try:
            message = f"""
🤖 <b>BOT DE TRADING INICIADO</b>

✅ Sistema operativo
📊 Modo: {'TESTNET' if Config.BINANCE_TESTNET else 'LIVE'}
💰 Capital objetivo: ${Config.INVESTMENT_AMOUNT}
🎯 Rentabilidad objetivo: {Config.TARGET_PROFIT_PERCENTAGE}%

⏰ {self._get_timestamp()}
            """.strip()
            
            if Config.ENABLE_NOTIFICATIONS:
                self.send_telegram_message(message)
                
        except Exception as e:
            self.logger.error(f"Error al notificar inicio: {e}")
    
    def _get_timestamp(self) -> str:
        """Obtener timestamp formateado"""
        from datetime import datetime
        return datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    def test_notifications(self) -> bool:
        """Probar sistema de notificaciones"""
        try:
            message = """
🧪 <b>PRUEBA DE NOTIFICACIONES</b>

✅ Sistema de notificaciones funcionando correctamente

⏰ {timestamp}
            """.strip().format(timestamp=self._get_timestamp())
            
            return self.send_telegram_message(message)
            
        except Exception as e:
            self.logger.error(f"Error al probar notificaciones: {e}")
            return False



