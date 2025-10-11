"""
Configuración de logging para el bot de trading
"""
import logging
import os
from datetime import datetime
from config import Config

def setup_logger(name: str = 'crypto_bot', level: str = None) -> logging.Logger:
    """Configurar sistema de logging"""
    
    # Crear directorio de logs si no existe
    log_dir = 'logs'
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # Configurar nivel de logging
    log_level = level or Config.LOG_LEVEL
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)
    
    # Crear logger
    logger = logging.getLogger(name)
    logger.setLevel(numeric_level)
    
    # Evitar duplicación de handlers
    if logger.handlers:
        return logger
    
    # Crear formateador
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Handler para archivo principal
    today = datetime.now().strftime('%Y-%m-%d')
    main_log_file = os.path.join(log_dir, f'crypto_bot_{today}.log')
    file_handler = logging.FileHandler(main_log_file, encoding='utf-8')
    file_handler.setLevel(numeric_level)
    file_handler.setFormatter(formatter)
    
    # Handler para archivo de trades
    trades_log_file = os.path.join(log_dir, f'trades_{today}.log')
    trades_handler = logging.FileHandler(trades_log_file, encoding='utf-8')
    trades_handler.setLevel(logging.INFO)
    trades_handler.setFormatter(formatter)
    
    # Handler para consola
    console_handler = logging.StreamHandler()
    console_handler.setLevel(numeric_level)
    console_handler.setFormatter(formatter)
    
    # Agregar handlers al logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

def get_trades_logger() -> logging.Logger:
    """Obtener logger específico para trades"""
    logger = logging.getLogger('trades')
    
    if not logger.handlers:
        log_dir = 'logs'
        today = datetime.now().strftime('%Y-%m-%d')
        trades_log_file = os.path.join(log_dir, f'trades_{today}.log')
        
        handler = logging.FileHandler(trades_log_file, encoding='utf-8')
        handler.setLevel(logging.INFO)
        
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        handler.setFormatter(formatter)
        
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    
    return logger

def log_trade(logger: logging.Logger, trade_type: str, symbol: str, amount: float, 
              price: float, pnl: float = None, reason: str = ''):
    """Log específico para trades"""
    trade_data = {
        'type': trade_type,
        'symbol': symbol,
        'amount': amount,
        'price': price,
        'pnl': pnl,
        'reason': reason,
        'timestamp': datetime.now().isoformat()
    }
    
    logger.info(f"TRADE: {trade_data}")

def log_signal(logger: logging.Logger, symbol: str, signal: dict):
    """Log específico para señales de trading"""
    if signal.get('buy', False):
        logger.info(f"🎯 {symbol}: COMPRA - Confianza: {signal.get('confidence', 0)}")
    elif signal.get('sell', False):
        logger.info(f"🎯 {symbol}: VENTA - Confianza: {signal.get('confidence', 0)}")
    else:
        logger.info(f"📊 {symbol}: Sin señales - Confianza: {signal.get('confidence', 0)}")

def log_error(logger: logging.Logger, error: Exception, context: str = ''):
    """Log específico para errores"""
    logger.error(f"ERROR {context}: {str(error)}", exc_info=True)

def log_performance(logger: logging.Logger, metrics: dict):
    """Log específico para métricas de rendimiento"""
    logger.info(f"PERFORMANCE: {metrics}")



