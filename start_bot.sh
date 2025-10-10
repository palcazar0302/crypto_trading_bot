#!/bin/bash
# Script para iniciar el bot de trading

echo "🤖 Iniciando Bot de Trading de Criptomonedas..."
echo "=============================================="

# Verificar que estamos en el directorio correcto
if [ ! -f "crypto_trading_bot.py" ]; then
    echo "❌ Error: Ejecuta este script desde el directorio del bot"
    exit 1
fi

# Activar entorno virtual
echo "🔄 Activando entorno virtual..."
source venv/bin/activate

# Verificar configuración
echo "🔍 Verificando configuración..."
python test_config.py

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Configuración verificada correctamente"
    echo "🚀 Iniciando bot..."
    echo "⚠️ Presiona Ctrl+C para detener el bot"
    echo "=============================================="
    python run_bot.py
else
    echo "❌ Error en la configuración. Revisa el archivo .env"
    exit 1
fi
