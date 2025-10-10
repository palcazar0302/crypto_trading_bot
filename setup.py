"""
Script de configuración inicial para el bot de trading
"""
import os
import sys
from pathlib import Path

def create_directories():
    """Crear directorios necesarios"""
    directories = ['logs', 'data', 'backups']
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"✅ Directorio '{directory}' creado")

def check_dependencies():
    """Verificar dependencias instaladas"""
    required_packages = [
        'ccxt', 'pandas', 'numpy', 'talib', 'dotenv',
        'schedule', 'requests', 'fastapi', 'uvicorn', 'matplotlib'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"✅ {package} instalado")
        except ImportError:
            missing_packages.append(package)
            print(f"❌ {package} no instalado")
    
    if missing_packages:
        print(f"\n⚠️ Paquetes faltantes: {', '.join(missing_packages)}")
        print("Ejecuta: pip install -r requirements.txt")
        return False
    
    return True

def setup_environment():
    """Configurar archivo de entorno"""
    env_file = Path('.env')
    example_file = Path('config.env.example')
    
    if env_file.exists():
        print("✅ Archivo .env ya existe")
        return True
    
    if not example_file.exists():
        print("❌ Archivo config.env.example no encontrado")
        return False
    
    # Copiar archivo de ejemplo
    with open(example_file, 'r') as src, open(env_file, 'w') as dst:
        dst.write(src.read())
    
    print("✅ Archivo .env creado desde config.env.example")
    print("⚠️ IMPORTANTE: Edita el archivo .env con tus credenciales reales")
    return True

def validate_config():
    """Validar configuración básica"""
    try:
        from config import Config
        Config.validate_config()
        print("✅ Configuración validada correctamente")
        return True
    except Exception as e:
        print(f"❌ Error en configuración: {e}")
        print("Asegúrate de configurar las variables de entorno en .env")
        return False

def main():
    """Función principal de configuración"""
    print("🚀 Configurando Bot de Trading de Criptomonedas...\n")
    
    # Crear directorios
    print("📁 Creando directorios...")
    create_directories()
    print()
    
    # Verificar dependencias
    print("📦 Verificando dependencias...")
    deps_ok = check_dependencies()
    print()
    
    if not deps_ok:
        print("❌ Instala las dependencias antes de continuar")
        return False
    
    # Configurar entorno
    print("⚙️ Configurando entorno...")
    env_ok = setup_environment()
    print()
    
    if not env_ok:
        print("❌ Error configurando entorno")
        return False
    
    # Validar configuración
    print("🔍 Validando configuración...")
    config_ok = validate_config()
    print()
    
    if config_ok:
        print("🎉 ¡Configuración completada exitosamente!")
        print("\n📋 Próximos pasos:")
        print("1. Edita el archivo .env con tus credenciales de Binance")
        print("2. Configura las notificaciones de Telegram (opcional)")
        print("3. Ejecuta 'python crypto_trading_bot.py' para iniciar el bot")
        print("4. O ejecuta 'python web_interface.py' para la interfaz web")
        print("\n⚠️ RECUERDA: Comienza siempre con BINANCE_TESTNET=True")
        return True
    else:
        print("❌ Configuración incompleta")
        print("Configura las variables de entorno en .env antes de continuar")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)



