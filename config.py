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
SYMBOLS = [
    # Top 10 criptomonedas principales (siempre disponibles)
    'BTC/USDC',
    'ETH/USDC',
    'BNB/USDC',
    'XRP/USDC',    # Ripple
    'ADA/USDC',
    'SOL/USDC',
    'DOGE/USDC',   # Dogecoin
    'TRX/USDC',    # TRON
    'LINK/USDC',   # Chainlink
    'MATIC/USDC',
    
    # Criptomonedas estables y líquidas
    'DOT/USDC',
    'LTC/USDC',    # Litecoin
    'AVAX/USDC',
    'UNI/USDC',    # Uniswap
    'ATOM/USDC',   # Cosmos
    'NEAR/USDC',   # Near Protocol
    'ALGO/USDC',   # Algorand
    'VET/USDC',    # VeChain
    'ICP/USDC',    # Internet Computer
    'FIL/USDC',    # Filecoin
    
    # Memecoins populares (alta volatilidad)
    'SHIB/USDC',   # Shiba Inu
    'PEPE/USDC',   # Pepe
    'FLOKI/USDC',  # Floki
    'BONK/USDC',   # Bonk
    'WIF/USDC',    # Dogwifhat
    
    # Layer 1 y Layer 2
    'ARB/USDC',    # Arbitrum
    'OP/USDC',     # Optimism
    'SUI/USDC',    # Sui
    'APT/USDC',    # Aptos
    
    # DeFi principales
    'AAVE/USDC',   # Aave
    'COMP/USDC',   # Compound
    'CRV/USDC',    # Curve
    'MKR/USDC',    # Maker
    
    # Gaming y Metaverse
    'SAND/USDC',   # The Sandbox
    'AXS/USDC',    # Axie Infinity
    'MANA/USDC',   # Decentraland
    'GALA/USDC',   # Gala
    
    # AI y Tecnología
    'FET/USDC',    # Fetch.ai
    'AGIX/USDC',   # SingularityNET
    'OCEAN/USDC'   # Ocean Protocol
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



