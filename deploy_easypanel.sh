#!/bin/bash

echo "🚀 PREPARANDO DESPLIEGUE EN EASYPANEL"
echo "======================================"

# Crear archivo ZIP para subir
echo "📦 Creando archivo ZIP..."
zip -r crypto_trading_bot.zip . -x "venv/*" "*.pyc" "__pycache__/*" ".git/*" "*.log" "data/*"

echo "✅ Archivo crypto_trading_bot.zip creado"
echo ""
echo "📋 SIGUIENTE PASO:"
echo "1. Ve a tu panel de Easypanel"
echo "2. Crea un nuevo proyecto Docker"
echo "3. Sube el archivo crypto_trading_bot.zip"
echo "4. Configura las variables de entorno (ver config_easypanel.env)"
echo "5. Establece el puerto 8000"
echo ""
echo "🔗 URLs importantes:"
echo "- Dashboard: http://TU_IP:8000"
echo "- API Status: http://TU_IP:8000/api/status"
echo "- API Portfolio: http://TU_IP:8000/api/portfolio"
echo ""
echo "📖 Para más detalles, consulta INSTRUCCIONES_EASYPANEL.md"
