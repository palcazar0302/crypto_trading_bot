"""
Gestor de riesgo para el bot de trading
"""
import logging
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from config import Config
import traceback

class RiskManager:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.daily_pnl = 0.0
        self.total_pnl = 0.0
        self.open_positions = {}
        self.daily_trades = 0
        self.max_daily_trades = 10
        self.closed_trades = []
        
        # Archivos de persistencia
        self.data_dir = "data"
        self.positions_file = os.path.join(self.data_dir, "open_positions.json")
        self.trades_file = os.path.join(self.data_dir, "trades_history.json")
        self.metrics_file = os.path.join(self.data_dir, "daily_metrics.json")
        
        # Crear directorio si no existe
        os.makedirs(self.data_dir, exist_ok=True)
        
        # Cargar datos al inicializar
        self._load_positions()
        self._load_metrics()
        self._load_trades_history()
        
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
            
            # Verificar tamaño mínimo de orden (ajustado para Binance)
            min_order_value = 5.0  # $5 USDT mínimo (algunos pares permiten desde $5)
            order_value = amount * price
            
            if order_value < min_order_value:
                validation['valid'] = False
                validation['reason'] = f'Valor de orden muy pequeño (mínimo ${min_order_value})'
                return validation
            
            # Advertencia si el valor es muy bajo pero válido
            if order_value < 10.0:
                self.logger.warning(f"⚠️ Orden pequeña: ${order_value:.2f} para {symbol}")
            
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
            
            self.logger.info(f"✅ Posición agregada: {symbol} - {side} - Cantidad: {amount} - Precio: {entry_price}")
            
            # Guardar inmediatamente
            self._save_positions()
            self._save_metrics()
            
        except Exception as e:
            self.logger.error(f"Error al agregar posición: {e}")
            self.logger.error(traceback.format_exc())
    
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
                self.logger.warning(f"⚠️ Intento de cerrar posición inexistente: {symbol}")
                return {'success': False, 'reason': 'Posición no encontrada'}
            
            position = self.open_positions[symbol]
            
            # Calcular PnL final
            if position['side'] == 'buy':
                pnl = (exit_price - position['entry_price']) * position['amount']
            else:
                pnl = (position['entry_price'] - exit_price) * position['amount']
            
            pnl_percentage = (pnl / (position['entry_price'] * position['amount'])) * 100
            
            # Actualizar estadísticas
            self.total_pnl += pnl
            self.daily_pnl += pnl
            
            # Calcular duración
            entry_time = position.get('entry_time', datetime.now())
            exit_time = datetime.now()
            duration_minutes = (exit_time - entry_time).total_seconds() / 60
            
            # Crear registro para historial
            trade_record = {
                'symbol': symbol,
                'side': position['side'],
                'entry_price': position['entry_price'],
                'exit_price': exit_price,
                'amount': position['amount'],
                'pnl': round(pnl, 2),
                'pnl_percentage': round(pnl_percentage, 2),
                'reason': exit_reason,
                'duration_minutes': int(duration_minutes),
                'timestamp': exit_time.isoformat()
            }
            
            # Agregar a lista de trades cerrados
            self.closed_trades.append(trade_record)
            
            # Remover de posiciones abiertas
            del self.open_positions[symbol]
            
            self.logger.info(f"✅ Posición cerrada: {symbol} - PnL: ${pnl:.2f} ({pnl_percentage:.2f}%) - Razón: {exit_reason}")
            
            # Guardar inmediatamente
            self._save_positions()
            self._save_trades_history()
            self._save_metrics()
            
            return {
                'success': True,
                'pnl': pnl,
                'pnl_percentage': pnl_percentage,
                'total_pnl': self.total_pnl,
                'daily_pnl': self.daily_pnl
            }
            
        except Exception as e:
            self.logger.error(f"Error al cerrar posición: {e}")
            self.logger.error(traceback.format_exc())
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
        self.logger.info("🔄 Métricas diarias reiniciadas")
        self._save_metrics()
    
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
    
    def _save_json_safe(self, filepath: str, data: dict, backup: bool = True):
        """Guardar JSON de forma segura con backup"""
        try:
            # Crear backup del archivo actual si existe
            if backup and os.path.exists(filepath):
                backup_file = f"{filepath}.backup"
                try:
                    import shutil
                    shutil.copy2(filepath, backup_file)
                except Exception as e:
                    self.logger.warning(f"No se pudo crear backup: {e}")
            
            # Guardar en archivo temporal primero
            temp_file = f"{filepath}.tmp"
            with open(temp_file, 'w') as f:
                json.dump(data, f, indent=2, default=str)
            
            # Validar que el JSON es válido
            with open(temp_file, 'r') as f:
                json.load(f)
            
            # Si la validación pasa, renombrar el archivo temporal
            if os.path.exists(filepath):
                os.remove(filepath)
            os.rename(temp_file, filepath)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error guardando JSON {filepath}: {e}")
            self.logger.error(traceback.format_exc())
            # Limpiar archivo temporal si existe
            if os.path.exists(temp_file):
                try:
                    os.remove(temp_file)
                except:
                    pass
            return False
    
    def _load_json_safe(self, filepath: str) -> dict:
        """Cargar JSON de forma segura con manejo de errores"""
        try:
            if not os.path.exists(filepath):
                return {}
            
            with open(filepath, 'r') as f:
                data = json.load(f)
            
            return data
            
        except json.JSONDecodeError as e:
            self.logger.error(f"Error cargando JSON corrupto {filepath}: {e}")
            
            # Intentar cargar desde backup
            backup_file = f"{filepath}.backup"
            if os.path.exists(backup_file):
                try:
                    self.logger.info(f"Intentando cargar desde backup: {backup_file}")
                    with open(backup_file, 'r') as f:
                        data = json.load(f)
                    self.logger.info("✅ Backup cargado exitosamente")
                    return data
                except Exception as e2:
                    self.logger.error(f"Backup también está corrupto: {e2}")
            
            # Si todo falla, mover archivo corrupto y empezar limpio
            corrupto_file = f"{filepath}.corrupto_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            try:
                os.rename(filepath, corrupto_file)
                self.logger.warning(f"Archivo corrupto movido a: {corrupto_file}")
            except:
                pass
            
            return {}
            
        except Exception as e:
            self.logger.error(f"Error inesperado cargando {filepath}: {e}")
            return {}
    
    def _save_positions(self):
        """Guardar posiciones abiertas"""
        try:
            # Solo guardar posiciones realmente abiertas
            positions_to_save = {}
            for symbol, pos in self.open_positions.items():
                if pos.get('status') == 'open':
                    # Convertir datetime a string
                    pos_copy = pos.copy()
                    if 'entry_time' in pos_copy and isinstance(pos_copy['entry_time'], datetime):
                        pos_copy['entry_time'] = pos_copy['entry_time'].isoformat()
                    positions_to_save[symbol] = pos_copy
            
            self._save_json_safe(self.positions_file, positions_to_save)
            self.logger.debug(f"💾 Posiciones guardadas: {len(positions_to_save)}")
            
        except Exception as e:
            self.logger.error(f"Error guardando posiciones: {e}")
            self.logger.error(traceback.format_exc())
    
    def _load_positions(self):
        """Cargar posiciones abiertas"""
        try:
            data = self._load_json_safe(self.positions_file)
            
            # Filtrar solo posiciones realmente abiertas
            open_count = 0
            for symbol, pos in data.items():
                if pos.get('status') == 'open' or 'status' not in pos:
                    # Convertir string a datetime
                    if 'entry_time' in pos and isinstance(pos['entry_time'], str):
                        try:
                            pos['entry_time'] = datetime.fromisoformat(pos['entry_time'])
                        except:
                            pos['entry_time'] = datetime.now()
                    
                    self.open_positions[symbol] = pos
                    open_count += 1
                else:
                    self.logger.info(f"⚠️ Posición cerrada encontrada en archivo: {symbol}, se ignorará")
            
            if open_count > 0:
                self.logger.info(f"✅ {open_count} posiciones abiertas cargadas")
            
        except Exception as e:
            self.logger.error(f"Error cargando posiciones: {e}")
            self.logger.error(traceback.format_exc())
            self.open_positions = {}
    
    def _save_trades_history(self):
        """Guardar historial de trades"""
        try:
            # Cargar historial existente
            existing = self._load_json_safe(self.trades_file)
            if not isinstance(existing, list):
                existing = []
            
            # Agregar nuevos trades cerrados
            all_trades = existing + self.closed_trades
            
            # Limpiar duplicados (por timestamp)
            seen = set()
            unique_trades = []
            for trade in all_trades:
                timestamp = trade.get('timestamp', '')
                if timestamp and timestamp not in seen:
                    seen.add(timestamp)
                    unique_trades.append(trade)
            
            # Ordenar por timestamp descendente (más reciente primero)
            unique_trades.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
            
            # Guardar
            self._save_json_safe(self.trades_file, unique_trades)
            self.logger.debug(f"💾 Historial guardado: {len(unique_trades)} trades")
            
            # Limpiar lista temporal
            self.closed_trades = []
            
        except Exception as e:
            self.logger.error(f"Error guardando historial: {e}")
            self.logger.error(traceback.format_exc())
    
    def _load_trades_history(self):
        """Cargar historial de trades (solo para estadísticas)"""
        try:
            trades = self._load_json_safe(self.trades_file)
            if isinstance(trades, list):
                self.logger.info(f"📊 {len(trades)} trades en historial")
        except Exception as e:
            self.logger.error(f"Error cargando historial: {e}")
    
    def _save_metrics(self):
        """Guardar métricas diarias"""
        try:
            metrics = {
                'daily_pnl': self.daily_pnl,
                'total_pnl': self.total_pnl,
                'daily_trades': self.daily_trades,
                'last_reset': datetime.now().isoformat()
            }
            self._save_json_safe(self.metrics_file, metrics)
            
        except Exception as e:
            self.logger.error(f"Error guardando métricas: {e}")
    
    def _load_metrics(self):
        """Cargar métricas diarias"""
        try:
            metrics = self._load_json_safe(self.metrics_file)
            
            if metrics:
                # Verificar si es del mismo día
                last_reset = metrics.get('last_reset', '')
                if last_reset:
                    last_date = datetime.fromisoformat(last_reset).date()
                    today = datetime.now().date()
                    
                    if last_date == today:
                        self.daily_pnl = metrics.get('daily_pnl', 0.0)
                        self.daily_trades = metrics.get('daily_trades', 0)
                        self.logger.info(f"📊 Métricas del día cargadas: PnL={self.daily_pnl:.2f}, Trades={self.daily_trades}")
                    else:
                        self.logger.info("🔄 Nuevo día detectado, métricas reiniciadas")
                
                self.total_pnl = metrics.get('total_pnl', 0.0)
                
        except Exception as e:
            self.logger.error(f"Error cargando métricas: {e}")


