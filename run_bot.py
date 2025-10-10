#!/usr/bin/env python3
"""
Script principal para ejecutar el bot de trading
"""
import sys
import os
import logging
from pathlib import Path

# Agregar el directorio actual al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def check_setup():
    """Verificar que el setup esté completo"""
    # Verificar archivo .env
    if not Path('.env').exists():
        print("❌ Archivo .env no encontrado")
        print("Ejecuta: python setup.py")
        return False
    
    # Verificar dependencias críticas
    try:
        import ccxt
        import pandas
        import numpy
        import talib
        from dotenv import load_dotenv
        print("✅ Dependencias principales verificadas")
        return True
    except ImportError as e:
        print(f"❌ Dependencia faltante: {e}")
        print("Ejecuta: pip install -r requirements.txt")
        return False

def main():
    """Función principal"""
    print("🤖 Iniciando Bot de Trading de Criptomonedas...")
    print("=" * 50)
    
    # Verificar setup
    if not check_setup():
        sys.exit(1)
    
    try:
        # Importar y ejecutar el bot
        from crypto_trading_bot import CryptoTradingBot
        
        print("✅ Bot cargado correctamente")
        print("⚠️ IMPORTANTE: Asegúrate de configurar BINANCE_TESTNET=True para pruebas")
        print("🔄 Iniciando bot...")
        print("Presiona Ctrl+C para detener el bot")
        print("=" * 50)
        
        # Crear y ejecutar bot
        bot = CryptoTradingBot()
        bot.start()
        
    except KeyboardInterrupt:
        print("\n🛑 Bot detenido por el usuario")
        if 'bot' in locals():
            bot.stop()
    except Exception as e:
        print(f"❌ Error fatal: {e}")
        logging.error(f"Error fatal en run_bot: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()



