#!/usr/bin/env python3
"""
Sistema de seguimiento del portafolio y balance
"""
import json
import os
from datetime import datetime
from typing import Dict
from config import Config

PORTFOLIO_FILE = 'data/portfolio.json'

class PortfolioTracker:
    def __init__(self):
        self.initial_balance = float(Config.INVESTMENT_AMOUNT)
        self.portfolio = self._load_portfolio()
        
    def _load_portfolio(self) -> Dict:
        """Cargar portafolio desde archivo"""
        try:
            if os.path.exists(PORTFOLIO_FILE):
                with open(PORTFOLIO_FILE, 'r') as f:
                    return json.load(f)
            else:
                # Crear portafolio inicial
                return {
                    'cash': self.initial_balance,
                    'positions': {},
                    'total_value': self.initial_balance,
                    'initial_balance': self.initial_balance,
                    'trades_history': [],
                    'last_update': datetime.now().isoformat()
                }
        except Exception as e:
            print(f"Error cargando portafolio: {e}")
            return {
                'cash': self.initial_balance,
                'positions': {},
                'total_value': self.initial_balance,
                'initial_balance': self.initial_balance,
                'trades_history': [],
                'last_update': datetime.now().isoformat()
            }
    
    def _save_portfolio(self):
        """Guardar portafolio en archivo"""
        try:
            os.makedirs('data', exist_ok=True)
            with open(PORTFOLIO_FILE, 'w') as f:
                json.dump(self.portfolio, f, indent=2)
        except Exception as e:
            print(f"Error guardando portafolio: {e}")
    
    def update_position_values(self, prices: Dict[str, float]):
        """Actualizar valores de posiciones con precios actuales"""
        try:
            total_positions_value = 0
            
            for symbol, position in self.portfolio.get('positions', {}).items():
                if symbol in prices:
                    current_price = prices[symbol]
                    position['current_price'] = current_price
                    position['current_value'] = position['amount'] * current_price
                    position['pnl'] = position['current_value'] - position['entry_value']
                    position['pnl_percentage'] = (position['pnl'] / position['entry_value']) * 100
                    total_positions_value += position['current_value']
            
            self.portfolio['total_value'] = self.portfolio['cash'] + total_positions_value
            self.portfolio['last_update'] = datetime.now().isoformat()
            self._save_portfolio()
            
        except Exception as e:
            print(f"Error actualizando valores: {e}")
    
    def add_trade(self, symbol: str, side: str, amount: float, price: float):
        """Registrar un nuevo trade"""
        try:
            trade_value = amount * price
            
            if side == 'buy':
                # Compra: reducir cash, añadir posición
                self.portfolio['cash'] -= trade_value
                
                if symbol not in self.portfolio['positions']:
                    self.portfolio['positions'][symbol] = {
                        'amount': amount,
                        'entry_price': price,
                        'entry_value': trade_value,
                        'current_price': price,
                        'current_value': trade_value,
                        'pnl': 0,
                        'pnl_percentage': 0,
                        'entry_time': datetime.now().isoformat()
                    }
                else:
                    # Promedio ponderado si ya existe posición
                    pos = self.portfolio['positions'][symbol]
                    total_amount = pos['amount'] + amount
                    total_value = pos['entry_value'] + trade_value
                    pos['amount'] = total_amount
                    pos['entry_price'] = total_value / total_amount
                    pos['entry_value'] = total_value
                    pos['current_value'] = total_value
                    
            elif side == 'sell':
                # Venta: añadir cash, reducir/eliminar posición
                self.portfolio['cash'] += trade_value
                
                if symbol in self.portfolio['positions']:
                    pos = self.portfolio['positions'][symbol]
                    if pos['amount'] >= amount:
                        pos['amount'] -= amount
                        if pos['amount'] <= 0:
                            del self.portfolio['positions'][symbol]
                        else:
                            pos['entry_value'] = pos['amount'] * pos['entry_price']
                            pos['current_value'] = pos['amount'] * price
            
            # Registrar trade en historial
            self.portfolio['trades_history'].append({
                'symbol': symbol,
                'side': side,
                'amount': amount,
                'price': price,
                'value': trade_value,
                'timestamp': datetime.now().isoformat()
            })
            
            # Mantener solo los últimos 100 trades
            if len(self.portfolio['trades_history']) > 100:
                self.portfolio['trades_history'] = self.portfolio['trades_history'][-100:]
            
            self._save_portfolio()
            
        except Exception as e:
            print(f"Error registrando trade: {e}")
    
    def get_portfolio_summary(self) -> Dict:
        """Obtener resumen del portafolio"""
        try:
            total_positions_value = sum(
                pos.get('current_value', 0) 
                for pos in self.portfolio.get('positions', {}).values()
            )
            
            total_value = self.portfolio.get('cash', 0) + total_positions_value
            initial_balance = self.portfolio.get('initial_balance', self.initial_balance)
            
            total_pnl = total_value - initial_balance
            total_pnl_percentage = (total_pnl / initial_balance * 100) if initial_balance > 0 else 0
            
            return {
                'cash': round(self.portfolio.get('cash', 0), 2),
                'positions_value': round(total_positions_value, 2),
                'total_value': round(total_value, 2),
                'initial_balance': round(initial_balance, 2),
                'total_pnl': round(total_pnl, 2),
                'total_pnl_percentage': round(total_pnl_percentage, 2),
                'total_trades': len(self.portfolio.get('trades_history', [])),
                'open_positions': len(self.portfolio.get('positions', {})),
                'last_update': self.portfolio.get('last_update', datetime.now().isoformat())
            }
        except Exception as e:
            print(f"Error obteniendo resumen: {e}")
            return {
                'cash': self.initial_balance,
                'positions_value': 0,
                'total_value': self.initial_balance,
                'initial_balance': self.initial_balance,
                'total_pnl': 0,
                'total_pnl_percentage': 0,
                'total_trades': 0,
                'open_positions': 0,
                'last_update': datetime.now().isoformat()
            }

# Instancia global
_portfolio_tracker = None

def get_portfolio_tracker():
    """Obtener instancia del portfolio tracker"""
    global _portfolio_tracker
    if _portfolio_tracker is None:
        _portfolio_tracker = PortfolioTracker()
    return _portfolio_tracker

