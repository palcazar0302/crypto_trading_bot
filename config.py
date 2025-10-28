"""
Configuración del bot de trading de criptomonedas
"""
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

class Config:
    # Configuración de Binance
    BINANCE_API_KEY = os.getenv('BINANCE_API_KEY')
    BINANCE_SECRET_KEY = os.getenv('BINANCE_SECRET_KEY')
    BINANCE_TESTNET = os.getenv('BINANCE_TESTNET', 'True').lower() == 'true'
    
    # Configuración de Telegram
    TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
    TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
    
    # Configuración del bot
    INVESTMENT_AMOUNT = float(os.getenv('INVESTMENT_AMOUNT', 1000))
    RISK_PERCENTAGE = float(os.getenv('RISK_PERCENTAGE', 2))
    TARGET_PROFIT_PERCENTAGE = float(os.getenv('TARGET_PROFIT_PERCENTAGE', 30))
    STOP_LOSS_PERCENTAGE = float(os.getenv('STOP_LOSS_PERCENTAGE', 5))
    MAX_OPEN_POSITIONS = int(os.getenv('MAX_OPEN_POSITIONS', 3))
    
    # Configuración de monitoreo
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    ENABLE_NOTIFICATIONS = os.getenv('ENABLE_NOTIFICATIONS', 'True').lower() == 'true'
    
    # Configuración de trading
    TIMEFRAME = '1h'
    # Solo 10 símbolos principales con mayor liquidez
    # Reducido para optimizar rendimiento con capital limitado
    SYMBOLS = [
        'BTC/USDC',    # Bitcoin - Máxima liquidez
        'ETH/USDC',    # Ethereum - Máxima liquidez
        'BNB/USDC',    # Binance Coin - Exchange nativo
        'SOL/USDC',    # Solana - Alta volatilidad y liquidez
        'XRP/USDC',    # Ripple - Muy líquido
        'ADA/USDC',    # Cardano - Estable y líquido
        'DOGE/USDC',   # Dogecoin - Popular y volátil
        'MATIC/USDC',  # Polygon - Buen volumen
        'DOT/USDC',    # Polkadot - Líquido
        'AVAX/USDC',   # Avalanche - Buena volatilidad
    ]
    
    # Indicadores técnicos
    RSI_PERIOD = 14
    RSI_OVERSOLD = 30
    RSI_OVERBOUGHT = 70
    EMA_SHORT = 12
    EMA_LONG = 26
    MACD_SIGNAL = 9
    BOLLINGER_PERIOD = 20
    BOLLINGER_STD = 2
    
    # Gestión de riesgo
    MAX_DAILY_LOSS = 5.0  # Porcentaje máximo de pérdida diaria
    POSITION_SIZE_PERCENTAGE = 20  # Porcentaje del capital por posición
    
    @classmethod
    def validate_config(cls):
        """Validar que la configuración sea correcta"""
        required_vars = [
            'BINANCE_API_KEY',
            'BINANCE_SECRET_KEY'
        ]
        
        missing_vars = []
        for var in required_vars:
            if not getattr(cls, var):
                missing_vars.append(var)
        
        if missing_vars:
            raise ValueError(f"Variables de entorno faltantes: {', '.join(missing_vars)}")
        
        return True



