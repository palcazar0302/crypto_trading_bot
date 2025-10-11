"""
Sistema de backtesting para validar estrategias de trading
"""
import pandas as pd
import numpy as np
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
import matplotlib.pyplot as plt
import seaborn as sns

from config import Config
from technical_analysis import TechnicalAnalysis
from risk_manager import RiskManager

class BacktestingEngine:
    def __init__(self, initial_capital: float = 10000):
        self.initial_capital = initial_capital
        self.logger = logging.getLogger(__name__)
        self.ta = TechnicalAnalysis()
        
    def run_backtest(self, symbol: str, start_date: str, end_date: str, 
                    timeframe: str = '1h') -> Dict:
        """Ejecutar backtesting completo"""
        try:
            self.logger.info(f"🔄 Iniciando backtesting para {symbol}")
            
            # Simular datos históricos (en producción usar datos reales)
            data = self._generate_historical_data(symbol, start_date, end_date, timeframe)
            
            if data.empty:
                raise Exception("No se pudieron obtener datos históricos")
            
            # Ejecutar simulación
            results = self._simulate_trading(data, symbol)
            
            # Calcular métricas
            metrics = self._calculate_metrics(results)
            
            # Generar reporte
            report = self._generate_report(results, metrics, symbol)
            
            self.logger.info(f"✅ Backtesting completado para {symbol}")
            return report
            
        except Exception as e:
            self.logger.error(f"Error en backtesting: {e}")
            return {}
    
    def _generate_historical_data(self, symbol: str, start_date: str, end_date: str, 
                                timeframe: str) -> pd.DataFrame:
        """Generar datos históricos simulados (en producción usar API real)"""
        try:
            # Crear rango de fechas
            start = pd.to_datetime(start_date)
            end = pd.to_datetime(end_date)
            
            # Crear timestamps basados en timeframe
            if timeframe == '1h':
                freq = 'H'
            elif timeframe == '4h':
                freq = '4H'
            elif timeframe == '1d':
                freq = 'D'
            else:
                freq = 'H'
            
            timestamps = pd.date_range(start=start, end=end, freq=freq)
            
            # Generar datos OHLCV simulados (precio base para BTC)
            base_price = 45000 if 'BTC' in symbol else 3000 if 'ETH' in symbol else 500
            
            # Simular volatilidad y tendencia
            np.random.seed(42)  # Para reproducibilidad
            returns = np.random.normal(0, 0.02, len(timestamps))  # 2% volatilidad diaria
            prices = [base_price]
            
            for ret in returns[1:]:
                new_price = prices[-1] * (1 + ret)
                prices.append(new_price)
            
            # Crear datos OHLCV
            data = []
            for i, (timestamp, price) in enumerate(zip(timestamps, prices)):
                # Simular OHLC basado en precio de cierre
                volatility = np.random.uniform(0.005, 0.02)
                high = price * (1 + volatility)
                low = price * (1 - volatility)
                open_price = prices[i-1] if i > 0 else price
                
                volume = np.random.uniform(1000, 10000)
                
                data.append({
                    'timestamp': timestamp,
                    'open': open_price,
                    'high': high,
                    'low': low,
                    'close': price,
                    'volume': volume
                })
            
            df = pd.DataFrame(data)
            df.set_index('timestamp', inplace=True)
            
            return df
            
        except Exception as e:
            self.logger.error(f"Error generando datos históricos: {e}")
            return pd.DataFrame()
    
    def _simulate_trading(self, data: pd.DataFrame, symbol: str) -> List[Dict]:
        """Simular trading con datos históricos"""
        try:
            trades = []
            position = None
            capital = self.initial_capital
            
            for i in range(50, len(data)):  # Empezar después de calcular indicadores
                current_data = data.iloc[:i+1]
                current_price = data.iloc[i]['close']
                
                # Generar señales
                signals = self.ta.get_trading_signals(current_data)
                
                # Si no hay posición y señal de compra
                if position is None and signals['buy'] and signals['confidence'] > 40:  # Confianza en porcentaje
                    # Calcular tamaño de posición
                    stop_loss = current_price * (1 - Config.STOP_LOSS_PERCENTAGE / 100)
                    position_size = self._calculate_position_size(capital, current_price, stop_loss)
                    
                    if position_size > 0:
                        position = {
                            'entry_price': current_price,
                            'amount': position_size,
                            'entry_time': data.index[i],
                            'stop_loss': stop_loss,
                            'take_profit': current_price * (1 + Config.TARGET_PROFIT_PERCENTAGE / 100)
                        }
                        
                        capital -= position_size * current_price  # Restar del capital disponible
                        
                        trades.append({
                            'type': 'BUY',
                            'price': current_price,
                            'amount': position_size,
                            'timestamp': data.index[i],
                            'capital': capital,
                            'signal_confidence': signals['confidence']
                        })
                
                # Si hay posición
                elif position is not None:
                    # Verificar stop loss
                    if current_price <= position['stop_loss']:
                        pnl = (current_price - position['entry_price']) * position['amount']
                        capital += position['amount'] * current_price
                        
                        trades.append({
                            'type': 'SELL',
                            'price': current_price,
                            'amount': position['amount'],
                            'timestamp': data.index[i],
                            'capital': capital,
                            'pnl': pnl,
                            'exit_reason': 'stop_loss'
                        })
                        
                        position = None
                    
                    # Verificar take profit
                    elif current_price >= position['take_profit']:
                        pnl = (current_price - position['entry_price']) * position['amount']
                        capital += position['amount'] * current_price
                        
                        trades.append({
                            'type': 'SELL',
                            'price': current_price,
                            'amount': position['amount'],
                            'timestamp': data.index[i],
                            'capital': capital,
                            'pnl': pnl,
                            'exit_reason': 'take_profit'
                        })
                        
                        position = None
                    
                    # Verificar señal de venta
                    elif signals['sell'] and signals['confidence'] > 40:  # Confianza en porcentaje
                        pnl = (current_price - position['entry_price']) * position['amount']
                        capital += position['amount'] * current_price
                        
                        trades.append({
                            'type': 'SELL',
                            'price': current_price,
                            'amount': position['amount'],
                            'timestamp': data.index[i],
                            'capital': capital,
                            'pnl': pnl,
                            'exit_reason': 'signal'
                        })
                        
                        position = None
            
            # Cerrar posición final si queda abierta
            if position is not None:
                final_price = data.iloc[-1]['close']
                pnl = (final_price - position['entry_price']) * position['amount']
                capital += position['amount'] * final_price
                
                trades.append({
                    'type': 'SELL',
                    'price': final_price,
                    'amount': position['amount'],
                    'timestamp': data.index[-1],
                    'capital': capital,
                    'pnl': pnl,
                    'exit_reason': 'end_of_data'
                })
            
            return trades
            
        except Exception as e:
            self.logger.error(f"Error en simulación de trading: {e}")
            return []
    
    def _calculate_position_size(self, capital: float, entry_price: float, stop_loss: float) -> float:
        """Calcular tamaño de posición"""
        try:
            risk_amount = capital * (Config.RISK_PERCENTAGE / 100)
            price_diff = abs(entry_price - stop_loss)
            
            if price_diff == 0:
                return 0
            
            position_size = risk_amount / price_diff
            
            # Limitar a porcentaje máximo del capital
            max_position_value = capital * (Config.POSITION_SIZE_PERCENTAGE / 100)
            max_position_size = max_position_value / entry_price
            
            return min(position_size, max_position_size)
            
        except Exception as e:
            self.logger.error(f"Error calculando tamaño de posición: {e}")
            return 0
    
    def _calculate_metrics(self, trades: List[Dict]) -> Dict:
        """Calcular métricas de rendimiento"""
        try:
            if not trades:
                return {}
            
            # Calcular métricas básicas
            total_trades = len([t for t in trades if t['type'] == 'SELL'])
            winning_trades = len([t for t in trades if t['type'] == 'SELL' and t.get('pnl', 0) > 0])
            losing_trades = total_trades - winning_trades
            
            total_pnl = sum(t.get('pnl', 0) for t in trades if t['type'] == 'SELL')
            final_capital = trades[-1]['capital'] if trades else self.initial_capital
            
            # Calcular retornos
            total_return = ((final_capital - self.initial_capital) / self.initial_capital) * 100
            
            # Calcular métricas de riesgo
            pnl_values = [t.get('pnl', 0) for t in trades if t['type'] == 'SELL']
            
            if pnl_values:
                win_rate = (winning_trades / total_trades) * 100 if total_trades > 0 else 0
                avg_win = np.mean([pnl for pnl in pnl_values if pnl > 0]) if winning_trades > 0 else 0
                avg_loss = np.mean([pnl for pnl in pnl_values if pnl < 0]) if losing_trades > 0 else 0
                profit_factor = abs(avg_win * winning_trades / (avg_loss * losing_trades)) if avg_loss != 0 else 0
                sharpe_ratio = np.mean(pnl_values) / np.std(pnl_values) if np.std(pnl_values) > 0 else 0
                max_drawdown = self._calculate_max_drawdown(trades)
            else:
                win_rate = avg_win = avg_loss = profit_factor = sharpe_ratio = max_drawdown = 0
            
            return {
                'total_trades': total_trades,
                'winning_trades': winning_trades,
                'losing_trades': losing_trades,
                'win_rate': win_rate,
                'total_pnl': total_pnl,
                'total_return': total_return,
                'final_capital': final_capital,
                'avg_win': avg_win,
                'avg_loss': avg_loss,
                'profit_factor': profit_factor,
                'sharpe_ratio': sharpe_ratio,
                'max_drawdown': max_drawdown
            }
            
        except Exception as e:
            self.logger.error(f"Error calculando métricas: {e}")
            return {}
    
    def _calculate_max_drawdown(self, trades: List[Dict]) -> float:
        """Calcular máxima pérdida consecutiva"""
        try:
            if not trades:
                return 0
            
            capital_values = [t['capital'] for t in trades]
            peak = capital_values[0]
            max_dd = 0
            
            for capital in capital_values:
                if capital > peak:
                    peak = capital
                dd = (peak - capital) / peak * 100
                if dd > max_dd:
                    max_dd = dd
            
            return max_dd
            
        except Exception as e:
            self.logger.error(f"Error calculando max drawdown: {e}")
            return 0
    
    def _generate_report(self, trades: List[Dict], metrics: Dict, symbol: str) -> Dict:
        """Generar reporte completo de backtesting"""
        try:
            report = {
                'symbol': symbol,
                'period': f"{trades[0]['timestamp']} - {trades[-1]['timestamp']}" if trades else "N/A",
                'initial_capital': self.initial_capital,
                'metrics': metrics,
                'trades': trades,
                'summary': self._generate_summary(metrics)
            }
            
            return report
            
        except Exception as e:
            self.logger.error(f"Error generando reporte: {e}")
            return {}
    
    def _generate_summary(self, metrics: Dict) -> str:
        """Generar resumen textual"""
        try:
            if not metrics:
                return "No se pudieron calcular métricas"
            
            summary = f"""
📊 RESUMEN DE BACKTESTING

💰 Capital inicial: ${self.initial_capital:,.2f}
💎 Capital final: ${metrics.get('final_capital', 0):,.2f}
📈 Retorno total: {metrics.get('total_return', 0):.2f}%
💵 PnL total: ${metrics.get('total_pnl', 0):,.2f}

📊 ESTADÍSTICAS DE TRADING
🔄 Total de trades: {metrics.get('total_trades', 0)}
✅ Trades ganadores: {metrics.get('winning_trades', 0)}
❌ Trades perdedores: {metrics.get('losing_trades', 0)}
🎯 Tasa de acierto: {metrics.get('win_rate', 0):.1f}%

📈 RENDIMIENTO
💚 Ganancia promedio: ${metrics.get('avg_win', 0):,.2f}
❤️ Pérdida promedio: ${metrics.get('avg_loss', 0):,.2f}
⚖️ Factor de beneficio: {metrics.get('profit_factor', 0):.2f}
📊 Ratio de Sharpe: {metrics.get('sharpe_ratio', 0):.2f}
📉 Máxima pérdida: {metrics.get('max_drawdown', 0):.2f}%
            """.strip()
            
            return summary
            
        except Exception as e:
            self.logger.error(f"Error generando resumen: {e}")
            return "Error generando resumen"
    
    def run_multi_symbol_backtest(self, symbols: List[str], start_date: str, 
                                end_date: str) -> Dict:
        """Ejecutar backtesting en múltiples símbolos"""
        try:
            results = {}
            total_metrics = {
                'total_trades': 0,
                'winning_trades': 0,
                'losing_trades': 0,
                'total_pnl': 0,
                'total_return': 0
            }
            
            for symbol in symbols:
                self.logger.info(f"🔄 Backtesting {symbol}...")
                result = self.run_backtest(symbol, start_date, end_date)
                results[symbol] = result
                
                if result and 'metrics' in result:
                    metrics = result['metrics']
                    total_metrics['total_trades'] += metrics.get('total_trades', 0)
                    total_metrics['winning_trades'] += metrics.get('winning_trades', 0)
                    total_metrics['losing_trades'] += metrics.get('losing_trades', 0)
                    total_metrics['total_pnl'] += metrics.get('total_pnl', 0)
            
            # Calcular métricas combinadas
            if total_metrics['total_trades'] > 0:
                total_metrics['win_rate'] = (total_metrics['winning_trades'] / total_metrics['total_trades']) * 100
                total_metrics['total_return'] = (total_metrics['total_pnl'] / self.initial_capital) * 100
            
            return {
                'symbols': results,
                'combined_metrics': total_metrics,
                'summary': f"Backtesting completado en {len(symbols)} símbolos"
            }
            
        except Exception as e:
            self.logger.error(f"Error en backtesting multi-símbolo: {e}")
            return {}

if __name__ == "__main__":
    # Ejemplo de uso
    engine = BacktestingEngine(initial_capital=10000)
    
    # Backtesting individual
    result = engine.run_backtest('BTC/USDT', '2023-01-01', '2023-12-31')
    print(result.get('summary', 'Sin resumen disponible'))
    
    # Backtesting múltiple
    symbols = ['BTC/USDT', 'ETH/USDT', 'BNB/USDT']
    multi_result = engine.run_multi_symbol_backtest(symbols, '2023-01-01', '2023-12-31')
    print(f"\nBacktesting múltiple: {multi_result.get('summary', 'Sin resumen')}")



