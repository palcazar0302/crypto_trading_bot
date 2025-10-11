"""
Módulo de análisis técnico para el bot de trading
"""
import pandas as pd
import numpy as np
import talib
import logging
from typing import Dict, List, Tuple, Optional
from config import Config

class TechnicalAnalysis:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def prepare_dataframe(self, ohlcv_data: List) -> pd.DataFrame:
        """Convertir datos OHLCV a DataFrame de pandas"""
        try:
            df = pd.DataFrame(ohlcv_data, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            df.set_index('timestamp', inplace=True)
            return df
        except Exception as e:
            self.logger.error(f"Error al preparar DataFrame: {e}")
            return pd.DataFrame()
    
    def calculate_rsi(self, prices: pd.Series, period: int = 14) -> pd.Series:
        """Calcular RSI (Relative Strength Index)"""
        try:
            return talib.RSI(prices.values, timeperiod=period)
        except Exception as e:
            self.logger.error(f"Error al calcular RSI: {e}")
            return pd.Series()
    
    def calculate_ema(self, prices: pd.Series, period: int) -> pd.Series:
        """Calcular EMA (Exponential Moving Average)"""
        try:
            return talib.EMA(prices.values, timeperiod=period)
        except Exception as e:
            self.logger.error(f"Error al calcular EMA: {e}")
            return pd.Series()
    
    def calculate_macd(self, prices: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9) -> Tuple:
        """Calcular MACD (Moving Average Convergence Divergence)"""
        try:
            macd, macd_signal, macd_hist = talib.MACD(prices.values, fastperiod=fast, slowperiod=slow, signalperiod=signal)
            return macd, macd_signal, macd_hist
        except Exception as e:
            self.logger.error(f"Error al calcular MACD: {e}")
            return pd.Series(), pd.Series(), pd.Series()
    
    def calculate_bollinger_bands(self, prices: pd.Series, period: int = 20, std_dev: float = 2) -> Tuple:
        """Calcular Bandas de Bollinger"""
        try:
            upper, middle, lower = talib.BBANDS(prices.values, timeperiod=period, nbdevup=std_dev, nbdevdn=std_dev)
            return upper, middle, lower
        except Exception as e:
            self.logger.error(f"Error al calcular Bandas de Bollinger: {e}")
            return pd.Series(), pd.Series(), pd.Series()
    
    def calculate_stochastic(self, high: pd.Series, low: pd.Series, close: pd.Series, 
                           k_period: int = 14, d_period: int = 3) -> Tuple:
        """Calcular Oscilador Estocástico"""
        try:
            slowk, slowd = talib.STOCH(high.values, low.values, close.values, 
                                     fastk_period=k_period, slowk_period=d_period, slowd_period=d_period)
            return slowk, slowd
        except Exception as e:
            self.logger.error(f"Error al calcular Estocástico: {e}")
            return pd.Series(), pd.Series()
    
    def calculate_atr(self, high: pd.Series, low: pd.Series, close: pd.Series, period: int = 14) -> pd.Series:
        """Calcular ATR (Average True Range)"""
        try:
            return talib.ATR(high.values, low.values, close.values, timeperiod=period)
        except Exception as e:
            self.logger.error(f"Error al calcular ATR: {e}")
            return pd.Series()
    
    def get_trading_signals(self, df: pd.DataFrame) -> Dict:
        """Generar señales de trading basadas en múltiples indicadores"""
        try:
            signals = {
                'buy': False,
                'sell': False,
                'confidence': 0.0,
                'indicators': {}
            }
            
            if len(df) < 50:  # Necesitamos suficientes datos
                return signals
            
            close_prices = df['close']
            high_prices = df['high']
            low_prices = df['low']
            
            # Calcular indicadores
            rsi = self.calculate_rsi(close_prices, Config.RSI_PERIOD)
            ema_short = self.calculate_ema(close_prices, Config.EMA_SHORT)
            ema_long = self.calculate_ema(close_prices, Config.EMA_LONG)
            macd, macd_signal, macd_hist = self.calculate_macd(close_prices, Config.EMA_SHORT, Config.EMA_LONG, Config.MACD_SIGNAL)
            bb_upper, bb_middle, bb_lower = self.calculate_bollinger_bands(close_prices, Config.BOLLINGER_PERIOD, Config.BOLLINGER_STD)
            stoch_k, stoch_d = self.calculate_stochastic(high_prices, low_prices, close_prices)
            
            # Obtener valores más recientes
            current_price = close_prices.iloc[-1]
            current_rsi = rsi[-1]
            current_ema_short = ema_short[-1]
            current_ema_long = ema_long[-1]
            current_macd = macd[-1]
            current_macd_signal = macd_signal[-1]
            current_bb_upper = bb_upper[-1]
            current_bb_lower = bb_lower[-1]
            current_stoch_k = stoch_k[-1]
            current_stoch_d = stoch_d[-1]
            
            # Estrategia de trading combinada
            buy_signals = 0
            sell_signals = 0
            
            # 1. RSI - Sobreventa/Sobrecompra
            if current_rsi < Config.RSI_OVERSOLD:
                buy_signals += 1
                signals['indicators']['rsi'] = 'sobreventa'
            elif current_rsi > Config.RSI_OVERBOUGHT:
                sell_signals += 1
                signals['indicators']['rsi'] = 'sobrecompra'
            else:
                signals['indicators']['rsi'] = 'neutral'
            
            # 2. EMA - Tendencia
            if current_ema_short > current_ema_long:
                buy_signals += 1
                signals['indicators']['ema'] = 'alcista'
            else:
                sell_signals += 1
                signals['indicators']['ema'] = 'bajista'
            
            # 3. MACD - Momentum
            if current_macd > current_macd_signal:
                buy_signals += 1
                signals['indicators']['macd'] = 'alcista'
            else:
                sell_signals += 1
                signals['indicators']['macd'] = 'bajista'
            
            # 4. Bandas de Bollinger - Volatilidad
            if current_price < current_bb_lower:
                buy_signals += 1
                signals['indicators']['bb'] = 'rebote_esperado'
            elif current_price > current_bb_upper:
                sell_signals += 1
                signals['indicators']['bb'] = 'sobrecompra'
            else:
                signals['indicators']['bb'] = 'normal'
            
            # 5. Estocástico - Momentum
            if current_stoch_k < 20 and current_stoch_k > current_stoch_d:
                buy_signals += 1
                signals['indicators']['stoch'] = 'sobreventa'
            elif current_stoch_k > 80 and current_stoch_k < current_stoch_d:
                sell_signals += 1
                signals['indicators']['stoch'] = 'sobrecompra'
            else:
                signals['indicators']['stoch'] = 'neutral'
            
            # Determinar señal final
            total_signals = buy_signals + sell_signals
            if total_signals > 0:
                # Calcular confianza como porcentaje de señales a favor
                confidence = (max(buy_signals, sell_signals) / total_signals) * 100
                
                if buy_signals > sell_signals and buy_signals >= 2:  # Mínimo 2 señales de compra
                    signals['buy'] = True
                    signals['confidence'] = min(confidence, 100)  # Máximo 100%
                elif sell_signals > buy_signals and sell_signals >= 2:  # Mínimo 2 señales de venta
                    signals['sell'] = True
                    signals['confidence'] = min(confidence, 100)  # Máximo 100%
            
            return signals
            
        except Exception as e:
            self.logger.error(f"Error al generar señales de trading: {e}")
            return {'buy': False, 'sell': False, 'confidence': 0.0, 'indicators': {}}
    
    def calculate_support_resistance(self, df: pd.DataFrame, window: int = 20) -> Dict:
        """Calcular niveles de soporte y resistencia"""
        try:
            high_prices = df['high']
            low_prices = df['low']
            
            # Calcular máximos y mínimos locales
            resistance = high_prices.rolling(window=window).max()
            support = low_prices.rolling(window=window).min()
            
            current_price = df['close'].iloc[-1]
            current_resistance = resistance.iloc[-1]
            current_support = support.iloc[-1]
            
            return {
                'support': current_support,
                'resistance': current_resistance,
                'distance_to_support': ((current_price - current_support) / current_support) * 100,
                'distance_to_resistance': ((current_resistance - current_price) / current_price) * 100
            }
            
        except Exception as e:
            self.logger.error(f"Error al calcular soporte y resistencia: {e}")
            return {}
    
    def get_volatility(self, df: pd.DataFrame, period: int = 20) -> float:
        """Calcular volatilidad del precio"""
        try:
            returns = df['close'].pct_change()
            volatility = returns.rolling(window=period).std() * np.sqrt(24)  # Volatilidad anualizada
            return volatility.iloc[-1] * 100
        except Exception as e:
            self.logger.error(f"Error al calcular volatilidad: {e}")
            return 0.0



