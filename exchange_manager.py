"""
Gestor de conexión con el exchange de criptomonedas
"""
import ccxt
import logging
import time
from typing import Dict, List, Optional, Tuple
from config import Config

class ExchangeManager:
    def __init__(self):
        self.exchange = None
        self.logger = logging.getLogger(__name__)
        self._initialize_exchange()
    
    def _initialize_exchange(self):
        """Inicializar la conexión con Binance"""
        try:
            self.exchange = ccxt.binance({
                'apiKey': Config.BINANCE_API_KEY,
                'secret': Config.BINANCE_SECRET_KEY,
                'sandbox': Config.BINANCE_TESTNET,
                'enableRateLimit': True,
                'options': {
                    'defaultType': 'spot',  # trading spot
                }
            })
            
            # Cargar mercados sin fallar si hay error de autenticación
            try:
                self.exchange.load_markets()
                self.logger.info("Mercados cargados correctamente")
            except Exception as load_error:
                self.logger.warning(f"No se pudieron cargar mercados: {load_error}")
                # Continuar sin cargar mercados, se cargarán cuando sea necesario
            
            self.logger.info("Conexión con Binance establecida correctamente")
            
        except Exception as e:
            self.logger.error(f"Error al conectar con Binance: {e}")
            raise
    
    def get_account_balance(self) -> Dict:
        """Obtener balance de la cuenta"""
        try:
            balance = self.exchange.fetch_balance()
            return balance
        except Exception as e:
            self.logger.error(f"Error al obtener balance: {e}")
            return {}
    
    def get_usdt_balance(self) -> float:
        """Obtener balance en USDT"""
        balance = self.get_account_balance()
        return balance.get('USDT', {}).get('free', 0.0)
    
    def get_usdc_balance(self) -> float:
        """Obtener balance en USDC"""
        balance = self.get_account_balance()
        return balance.get('USDC', {}).get('free', 0.0)
    
    def get_ticker(self, symbol: str) -> Dict:
        """Obtener precio actual de un símbolo"""
        try:
            ticker = self.exchange.fetch_ticker(symbol)
            return ticker
        except Exception as e:
            self.logger.error(f"Error al obtener ticker para {symbol}: {e}")
            return {}
    
    def get_ohlcv(self, symbol: str, timeframe: str = '1h', limit: int = 100) -> List:
        """Obtener datos OHLCV para análisis técnico"""
        try:
            ohlcv = self.exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
            return ohlcv
        except Exception as e:
            self.logger.error(f"Error al obtener OHLCV para {symbol}: {e}")
            return []
    
    def place_market_buy_order(self, symbol: str, amount: float) -> Dict:
        """Colocar orden de compra a mercado"""
        try:
            order = self.exchange.create_market_buy_order(symbol, amount)
            self.logger.info(f"Orden de compra ejecutada: {symbol} - Cantidad: {amount}")
            return order
        except Exception as e:
            self.logger.error(f"Error al colocar orden de compra: {e}")
            return {}
    
    def place_market_sell_order(self, symbol: str, amount: float) -> Dict:
        """Colocar orden de venta a mercado"""
        try:
            order = self.exchange.create_market_sell_order(symbol, amount)
            self.logger.info(f"Orden de venta ejecutada: {symbol} - Cantidad: {amount}")
            return order
        except Exception as e:
            self.logger.error(f"Error al colocar orden de venta: {e}")
            return {}
    
    def place_limit_buy_order(self, symbol: str, amount: float, price: float) -> Dict:
        """Colocar orden de compra limitada"""
        try:
            order = self.exchange.create_limit_buy_order(symbol, amount, price)
            self.logger.info(f"Orden de compra limitada: {symbol} - Cantidad: {amount} - Precio: {price}")
            return order
        except Exception as e:
            self.logger.error(f"Error al colocar orden de compra limitada: {e}")
            return {}
    
    def place_limit_sell_order(self, symbol: str, amount: float, price: float) -> Dict:
        """Colocar orden de venta limitada"""
        try:
            order = self.exchange.create_limit_sell_order(symbol, amount, price)
            self.logger.info(f"Orden de venta limitada: {symbol} - Cantidad: {amount} - Precio: {price}")
            return order
        except Exception as e:
            self.logger.error(f"Error al colocar orden de venta limitada: {e}")
            return {}
    
    def get_open_orders(self, symbol: Optional[str] = None) -> List:
        """Obtener órdenes abiertas"""
        try:
            orders = self.exchange.fetch_open_orders(symbol)
            return orders
        except Exception as e:
            self.logger.error(f"Error al obtener órdenes abiertas: {e}")
            return []
    
    def cancel_order(self, order_id: str, symbol: str) -> bool:
        """Cancelar una orden"""
        try:
            self.exchange.cancel_order(order_id, symbol)
            self.logger.info(f"Orden cancelada: {order_id}")
            return True
        except Exception as e:
            self.logger.error(f"Error al cancelar orden {order_id}: {e}")
            return False
    
    def get_order_status(self, order_id: str, symbol: str) -> Dict:
        """Obtener estado de una orden"""
        try:
            order = self.exchange.fetch_order(order_id, symbol)
            return order
        except Exception as e:
            self.logger.error(f"Error al obtener estado de orden {order_id}: {e}")
            return {}
    
    def get_trading_fees(self, symbol: str) -> Dict:
        """Obtener comisiones de trading"""
        try:
            fees = self.exchange.fetch_trading_fees(symbol)
            return fees
        except Exception as e:
            self.logger.error(f"Error al obtener comisiones: {e}")
            return {}
    
    def calculate_order_amount(self, symbol: str, usdt_amount: float) -> float:
        """Calcular cantidad de moneda basada en cantidad USDT"""
        try:
            ticker = self.get_ticker(symbol)
            current_price = ticker.get('last', 0)
            if current_price > 0:
                return usdt_amount / current_price
            return 0
        except Exception as e:
            self.logger.error(f"Error al calcular cantidad de orden: {e}")
            return 0



