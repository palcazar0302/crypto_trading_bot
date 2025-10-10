#!/usr/bin/env python3
"""
Script de inicio optimizado para Easypanel
Ejecuta tanto el bot como el dashboard web
"""
import os
import sys
import time
import signal
import subprocess
import threading
from datetime import datetime

def signal_handler(sig, frame):
    """Manejar señales de cierre"""
    print(f"\n[{datetime.now()}] 🛑 Recibida señal de cierre, deteniendo servicios...")
    sys.exit(0)

def start_web_interface():
    """Iniciar la interfaz web"""
    print(f"[{datetime.now()}] 🌐 Iniciando interfaz web...")
    try:
        os.system("python run_web.py")
    except Exception as e:
        print(f"[{datetime.now()}] ❌ Error en interfaz web: {e}")

def start_trading_bot():
    """Iniciar el bot de trading"""
    print(f"[{datetime.now()}] 🤖 Iniciando bot de trading...")
    try:
        os.system("python dashboard_bot.py")
    except Exception as e:
        print(f"[{datetime.now()}] ❌ Error en bot de trading: {e}")

def main():
    """Función principal"""
    print(f"""
╔══════════════════════════════════════════════════════════════════╗
║  🚀 CRYPTO TRADING BOT - EASYPANEL                              ║
╚══════════════════════════════════════════════════════════════════╝

[{datetime.now()}] ✅ Iniciando servicios...
[{datetime.now()}] 📊 Modo: Easypanel
[{datetime.now()}] 🌐 Puerto: 8000
[{datetime.now()}] 💰 Balance: {os.getenv('INVESTMENT_AMOUNT', 'N/A')} USDC
[{datetime.now()}] 🔗 Binance: {'TESTNET' if os.getenv('BINANCE_TESTNET', 'False') == 'True' else 'REAL'}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
""")

    # Configurar manejo de señales
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # Crear directorios necesarios
    os.makedirs('data', exist_ok=True)
    os.makedirs('logs', exist_ok=True)

    # Iniciar bot de trading en hilo separado
    bot_thread = threading.Thread(target=start_trading_bot, daemon=True)
    bot_thread.start()

    # Esperar un poco para que el bot se inicie
    time.sleep(5)

    # Iniciar interfaz web (hilo principal)
    try:
        start_web_interface()
    except KeyboardInterrupt:
        print(f"\n[{datetime.now()}] 🛑 Deteniendo servicios...")
    except Exception as e:
        print(f"[{datetime.now()}] ❌ Error crítico: {e}")
    finally:
        print(f"[{datetime.now()}] ✅ Servicios detenidos correctamente")

if __name__ == "__main__":
    main()
