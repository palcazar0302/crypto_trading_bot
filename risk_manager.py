"""
Gestor de riesgo para el bot de trading
"""
import logging
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from config import Config

class RiskManager:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.daily_pnl = 0.0
        self.total_pnl = 0.0
        self.open_positions = {}
        self.daily_trades = 0
        self.max_daily_trades = 10
        
    def calculate_position_size(self, account_balance: float, risk_percentage: float, 
                              entry_price: float, stop_loss_price: float) -> float:
        """Calcular tamaño de posición basado en gestión de riesgo"""
        try:
            # Calcular pérdida máxima por posición
            risk_amount = account_balance * (risk_percentage / 100)
            
            # Calcular diferencia de precio hasta stop loss
            price_diff = abs(entry_price - stop_loss_price)
            
            if price_diff == 0:
                return 0
            
            # Calcular cantidad de moneda
            position_size = risk_amount / price_diff
            
            # Limitar tamaño de posición a un porcentaje máximo del capital
            max_position_value = account_balance * (Config.POSITION_SIZE_PERCENTAGE / 100)
            max_position_size = max_position_value / entry_price
            
            return min(position_size, max_position_size)
            
        except Exception as e:
            self.logger.error(f"Error al calcular tamaño de posición: {e}")
            return 0
    
    def validate_trade(self, symbol: str, side: str, amount: float, price: float) -> Dict:
        """Validar si un trade cumple con las reglas de riesgo"""
        validation = {
            'valid': True,
            'reason': '',
            'adjusted_amount': amount
        }
        
        try:
            # Verificar límite de posiciones abiertas
            if len(self.open_positions) >= Config.MAX_OPEN_POSITIONS:
                validation['valid'] = False
                validation['reason'] = f'Máximo de posiciones abiertas alcanzado ({Config.MAX_OPEN_POSITIONS})'
                return validation
            
            # Verificar si ya existe una posición para este símbolo
            if symbol in self.open_positions:
                validation['valid'] = False
                validation['reason'] = f'Ya existe una posición abierta para {symbol}'
                return validation
            
            # Verificar límite de trades diarios
            if self.daily_trades >= self.max_daily_trades:
                validation['valid'] = False
                validation['reason'] = f'Límite de trades diarios alcanzado ({self.max_daily_trades})'
                return validation
            
            # Verificar pérdida diaria máxima
            if self.daily_pnl <= -Config.MAX_DAILY_LOSS:
                validation['valid'] = False
                validation['reason'] = f'Pérdida diaria máxima alcanzada ({Config.MAX_DAILY_LOSS}%)'
                return validation
            
            # Verificar tamaño mínimo de orden
            min_order_value = 10.0  # $10 USDT mínimo
            order_value = amount * price
            
            if order_value < min_order_value:
                validation['valid'] = False
                validation['reason'] = f'Valor de orden muy pequeño (mínimo ${min_order_value})'
                return validation
            
            return validation
            
        except Exception as e:
            self.logger.error(f"Error al validar trade: {e}")
            validation['valid'] = False
            validation['reason'] = f'Error en validación: {str(e)}'
            return validation
    
    def add_position(self, symbol: str, side: str, amount: float, entry_price: float, 
                    stop_loss: float, take_profit: float, order_id: str):
        """Agregar nueva posición al seguimiento"""
        try:
            position = {
                'symbol': symbol,
                'side': side,
                'amount': amount,
                'entry_price': entry_price,
                'current_price': entry_price,
                'stop_loss': stop_loss,
                'take_profit': take_profit,
                'order_id': order_id,
                'entry_time': datetime.now(),
                'unrealized_pnl': 0.0,
                'status': 'open'
            }
            
            self.open_positions[symbol] = position
            self.daily_trades += 1
            
            self.logger.info(f"Posición agregada: {symbol} - {side} - Cantidad: {amount} - Precio: {entry_price}")
            
        except Exception as e:
            self.logger.error(f"Error al agregar posición: {e}")
    
    def update_position_price(self, symbol: str, current_price: float):
        """Actualizar precio actual de una posición"""
        try:
            if symbol in self.open_positions:
                position = self.open_positions[symbol]
                position['current_price'] = current_price
                
                # Calcular PnL no realizado
                if position['side'] == 'buy':
                    position['unrealized_pnl'] = (current_price - position['entry_price']) * position['amount']
                else:
                    position['unrealized_pnl'] = (position['entry_price'] - current_price) * position['amount']
                
        except Exception as e:
            self.logger.error(f"Error al actualizar precio de posición: {e}")
    
    def check_stop_loss_take_profit(self, symbol: str, current_price: float) -> Dict:
        """Verificar si se debe activar stop loss o take profit"""
        try:
            if symbol not in self.open_positions:
                return {'action': 'none', 'reason': ''}
            
            position = self.open_positions[symbol]
            
            # Verificar stop loss
            if position['side'] == 'buy' and current_price <= position['stop_loss']:
                return {
                    'action': 'sell',
                    'reason': f'Stop loss activado: {current_price} <= {position["stop_loss"]}',
                    'price': position['stop_loss']
                }
            elif position['side'] == 'sell' and current_price >= position['stop_loss']:
                return {
                    'action': 'buy',
                    'reason': f'Stop loss activado: {current_price} >= {position["stop_loss"]}',
                    'price': position['stop_loss']
                }
            
            # Verificar take profit
            if position['side'] == 'buy' and current_price >= position['take_profit']:
                return {
                    'action': 'sell',
                    'reason': f'Take profit activado: {current_price} >= {position["take_profit"]}',
                    'price': position['take_profit']
                }
            elif position['side'] == 'sell' and current_price <= position['take_profit']:
                return {
                    'action': 'buy',
                    'reason': f'Take profit activado: {current_price} <= {position["take_profit"]}',
                    'price': position['take_profit']
                }
            
            return {'action': 'none', 'reason': ''}
            
        except Exception as e:
            self.logger.error(f"Error al verificar stop loss/take profit: {e}")
            return {'action': 'none', 'reason': ''}
    
    def close_position(self, symbol: str, exit_price: float, exit_reason: str = 'manual'):
        """Cerrar posición y calcular PnL"""
        try:
            if symbol not in self.open_positions:
                return {'success': False, 'reason': 'Posición no encontrada'}
            
            position = self.open_positions[symbol]
            
            # Calcular PnL final
            if position['side'] == 'buy':
                pnl = (exit_price - position['entry_price']) * position['amount']
            else:
                pnl = (position['entry_price'] - exit_price) * position['amount']
            
            # Actualizar estadísticas
            self.total_pnl += pnl
            self.daily_pnl += pnl
            
            # Marcar posición como cerrada
            position['status'] = 'closed'
            position['exit_price'] = exit_price
            position['exit_time'] = datetime.now()
            position['exit_reason'] = exit_reason
            position['realized_pnl'] = pnl
            
            # Remover de posiciones abiertas
            del self.open_positions[symbol]
            
            self.logger.info(f"Posición cerrada: {symbol} - PnL: {pnl:.2f} - Razón: {exit_reason}")
            
            return {
                'success': True,
                'pnl': pnl,
                'total_pnl': self.total_pnl,
                'daily_pnl': self.daily_pnl
            }
            
        except Exception as e:
            self.logger.error(f"Error al cerrar posición: {e}")
            return {'success': False, 'reason': str(e)}
    
    def calculate_portfolio_metrics(self, account_balance: float) -> Dict:
        """Calcular métricas del portafolio"""
        try:
            total_unrealized_pnl = sum(pos['unrealized_pnl'] for pos in self.open_positions.values())
            total_value = account_balance + total_unrealized_pnl
            
            return {
                'account_balance': account_balance,
                'total_unrealized_pnl': total_unrealized_pnl,
                'total_value': total_value,
                'daily_pnl': self.daily_pnl,
                'total_pnl': self.total_pnl,
                'daily_return': (self.daily_pnl / account_balance) * 100 if account_balance > 0 else 0,
                'total_return': (self.total_pnl / account_balance) * 100 if account_balance > 0 else 0,
                'open_positions': len(self.open_positions),
                'daily_trades': self.daily_trades
            }
            
        except Exception as e:
            self.logger.error(f"Error al calcular métricas del portafolio: {e}")
            return {}
    
    def reset_daily_metrics(self):
        """Reiniciar métricas diarias"""
        self.daily_pnl = 0.0
        self.daily_trades = 0
        self.logger.info("Métricas diarias reiniciadas")
    
    def get_risk_report(self) -> Dict:
        """Generar reporte de riesgo"""
        try:
            return {
                'timestamp': datetime.now().isoformat(),
                'daily_pnl': self.daily_pnl,
                'total_pnl': self.total_pnl,
                'open_positions': len(self.open_positions),
                'daily_trades': self.daily_trades,
                'max_daily_loss_limit': Config.MAX_DAILY_LOSS,
                'max_positions_limit': Config.MAX_OPEN_POSITIONS,
                'risk_per_trade': Config.RISK_PERCENTAGE,
                'positions_detail': list(self.open_positions.values())
            }
        except Exception as e:
            self.logger.error(f"Error al generar reporte de riesgo: {e}")
            return {}


