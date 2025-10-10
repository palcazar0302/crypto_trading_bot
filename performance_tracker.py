#!/usr/bin/env python3
"""
Sistema de seguimiento de rendimiento del bot
"""
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import pandas as pd
import numpy as np

class PerformanceTracker:
    def __init__(self, data_file: str = "data/performance.json"):
        self.data_file = data_file
        self.ensure_data_directory()
        self.performance_data = self.load_performance_data()
    
    def ensure_data_directory(self):
        """Asegurar que el directorio de datos existe"""
        os.makedirs(os.path.dirname(self.data_file), exist_ok=True)
    
    def load_performance_data(self) -> Dict:
        """Cargar datos de rendimiento existentes"""
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Error cargando datos de rendimiento: {e}")
        
        return {
            "daily_returns": {},
            "trades": [],
            "portfolio_values": {},
            "start_date": datetime.now().isoformat(),
            "initial_balance": 1000.0
        }
    
    def save_performance_data(self):
        """Guardar datos de rendimiento"""
        try:
            with open(self.data_file, 'w') as f:
                json.dump(self.performance_data, f, indent=2)
        except Exception as e:
            print(f"Error guardando datos de rendimiento: {e}")
    
    def record_trade(self, symbol: str, action: str, amount: float, price: float, timestamp: datetime = None):
        """Registrar una operación"""
        if timestamp is None:
            timestamp = datetime.now()
        
        trade = {
            "timestamp": timestamp.isoformat(),
            "symbol": symbol,
            "action": action,  # "buy" o "sell"
            "amount": amount,
            "price": price,
            "value": amount * price
        }
        
        self.performance_data["trades"].append(trade)
        self.save_performance_data()
    
    def update_portfolio_value(self, value: float, timestamp: datetime = None):
        """Actualizar valor del portafolio"""
        if timestamp is None:
            timestamp = datetime.now()
        
        date_str = timestamp.strftime("%Y-%m-%d")
        self.performance_data["portfolio_values"][date_str] = value
        self.save_performance_data()
    
    def calculate_daily_returns(self) -> Dict[str, float]:
        """Calcular rendimientos diarios"""
        portfolio_values = self.performance_data["portfolio_values"]
        daily_returns = {}
        
        dates = sorted(portfolio_values.keys())
        for i in range(1, len(dates)):
            prev_value = portfolio_values[dates[i-1]]
            curr_value = portfolio_values[dates[i]]
            
            if prev_value > 0:
                daily_return = (curr_value - prev_value) / prev_value * 100
                daily_returns[dates[i]] = round(daily_return, 2)
        
        return daily_returns
    
    def get_performance_metrics(self) -> Dict:
        """Obtener métricas de rendimiento"""
        portfolio_values = self.performance_data["portfolio_values"]
        
        if not portfolio_values:
            return self._get_empty_metrics()
        
        dates = sorted(portfolio_values.keys())
        values = [portfolio_values[date] for date in dates]
        
        if len(values) < 2:
            return self._get_empty_metrics()
        
        # Cálculos básicos
        initial_value = values[0]
        current_value = values[-1]
        total_return = ((current_value - initial_value) / initial_value) * 100
        
        # Rendimiento diario
        daily_returns = self.calculate_daily_returns()
        daily_returns_list = list(daily_returns.values())
        
        # Métricas de riesgo
        if daily_returns_list:
            avg_daily_return = np.mean(daily_returns_list)
            volatility = np.std(daily_returns_list)
            
            # Máximo drawdown
            peak = values[0]
            max_drawdown = 0
            for value in values:
                if value > peak:
                    peak = value
                drawdown = (peak - value) / peak * 100
                if drawdown > max_drawdown:
                    max_drawdown = drawdown
        else:
            avg_daily_return = 0
            volatility = 0
            max_drawdown = 0
        
        # Rendimientos por período
        today = datetime.now().strftime("%Y-%m-%d")
        week_ago = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
        month_ago = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
        
        weekly_return = self._calculate_period_return(values, dates, week_ago, today)
        monthly_return = self._calculate_period_return(values, dates, month_ago, today)
        
        return {
            "total_return": round(total_return, 2),
            "daily_return": round(avg_daily_return, 2),
            "weekly_return": round(weekly_return, 2),
            "monthly_return": round(monthly_return, 2),
            "volatility": round(volatility, 2),
            "max_drawdown": round(max_drawdown, 2),
            "current_value": round(current_value, 2),
            "total_trades": len(self.performance_data["trades"]),
            "winning_trades": self._count_winning_trades(),
            "losing_trades": self._count_losing_trades()
        }
    
    def _get_empty_metrics(self) -> Dict:
        """Métricas vacías para cuando no hay datos"""
        return {
            "total_return": 0.0,
            "daily_return": 0.0,
            "weekly_return": 0.0,
            "monthly_return": 0.0,
            "volatility": 0.0,
            "max_drawdown": 0.0,
            "current_value": 1000.0,
            "total_trades": 0,
            "winning_trades": 0,
            "losing_trades": 0
        }
    
    def _calculate_period_return(self, values: List[float], dates: List[str], start_date: str, end_date: str) -> float:
        """Calcular rendimiento para un período específico"""
        try:
            start_idx = next((i for i, date in enumerate(dates) if date >= start_date), 0)
            end_idx = next((i for i, date in enumerate(dates) if date >= end_date), len(values)-1)
            
            if start_idx < len(values) and end_idx < len(values):
                start_value = values[start_idx]
                end_value = values[end_idx]
                if start_value > 0:
                    return ((end_value - start_value) / start_value) * 100
        except:
            pass
        return 0.0
    
    def _count_winning_trades(self) -> int:
        """Contar trades ganadores"""
        trades = self.performance_data["trades"]
        # Simplificado: contar trades con ganancia positiva
        # En una implementación real, necesitarías trackear el PnL de cada trade
        return len([t for t in trades if t.get("pnl", 0) > 0])
    
    def _count_losing_trades(self) -> int:
        """Contar trades perdedores"""
        trades = self.performance_data["trades"]
        return len([t for t in trades if t.get("pnl", 0) < 0])
    
    def get_performance_chart_data(self) -> Dict:
        """Obtener datos para gráfico de rendimiento"""
        portfolio_values = self.performance_data["portfolio_values"]
        
        if not portfolio_values:
            return {"dates": [], "values": []}
        
        dates = sorted(portfolio_values.keys())
        values = [portfolio_values[date] for date in dates]
        
        return {
            "dates": dates,
            "values": values
        }

# Instancia global
performance_tracker = PerformanceTracker()
