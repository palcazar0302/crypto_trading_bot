#!/bin/bash
# Script para iniciar la interfaz web del bot

echo "🌐 Iniciando Interfaz Web del Bot de Trading..."
echo "=============================================="

# Verificar que estamos en el directorio correcto
if [ ! -f "web_interface.py" ]; then
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
    echo "🌐 Iniciando servidor web..."
    echo "📊 Abre tu navegador y ve a: http://localhost:8000"
    echo "⚠️ Presiona Ctrl+C para detener el servidor"
    echo "=============================================="
    python run_web.py
else
    echo "❌ Error en la configuración. Revisa el archivo .env"
    exit 1
fi
