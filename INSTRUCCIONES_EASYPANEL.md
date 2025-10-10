# 🚀 Instrucciones para desplegar en Easypanel

## 📋 PASO 1: Subir el proyecto

### Opción A: Usar Git (Recomendado)
1. Crear un repositorio en GitHub/GitLab
2. Subir todos los archivos del bot
3. Clonar en Easypanel

### Opción B: Subir archivos directamente
1. Comprimir la carpeta `crypto_trading_bot`
2. Subir el ZIP a Easypanel

## 📋 PASO 2: Configurar en Easypanel

1. **Crear nuevo proyecto:**
   - Nombre: `crypto-trading-bot`
   - Tipo: `Docker`

2. **Configurar Docker:**
   - Dockerfile: `./Dockerfile`
   - Puerto: `8000`
   - Variables de entorno: (ver abajo)

3. **Variables de entorno necesarias:**
```
BINANCE_API_KEY=x148J6vGnfQ2PIucftnWFJ9u4W6puqYZD60PSvs9nsXFLDFdIQHFKqf84ghFlZG8
BINANCE_SECRET_KEY=DMNxidQ4jTLourkEQKm6aSpqBbMVsm5LHm5x1CKI41VAuaHB40P2hHuqq6mMrW2I
BINANCE_TESTNET=False
TELEGRAM_BOT_TOKEN=8095438045:AAHTfdfRiuS7pEfjf1h02WNAzSCHe18Kbqg
TELEGRAM_CHAT_ID=892473746
INVESTMENT_AMOUNT=113.51
RISK_PERCENTAGE=2
TARGET_PROFIT_PERCENTAGE=30
STOP_LOSS_PERCENTAGE=5
MAX_OPEN_POSITIONS=3
MAX_DAILY_LOSS=5
LOG_LEVEL=INFO
ENABLE_NOTIFICATIONS=True
```

## 📋 PASO 3: Configurar dominio (Opcional)

1. **Dominio personalizado:**
   - Añadir dominio en Easypanel
   - Configurar SSL automático
   - Ejemplo: `bot.tudominio.com`

2. **Acceso directo:**
   - Usar IP del servidor: `http://TU_IP:8000`

## 📋 PASO 4: Monitoreo

1. **Logs en tiempo real:**
   - Easypanel → Proyecto → Logs

2. **Estado del servicio:**
   - Easypanel → Proyecto → Status

3. **Reiniciar servicio:**
   - Easypanel → Proyecto → Restart

## 🔧 Configuración avanzada

### Volúmenes persistentes:
- `crypto_bot_data` → Datos del bot
- `crypto_bot_logs` → Logs del bot

### Health Check:
- Verifica cada 30 segundos que el bot esté funcionando
- Reinicia automáticamente si falla

### Auto-restart:
- Se reinicia automáticamente si se cae
- Funciona 24/7 sin intervención

## 🎯 URLs importantes

- **Dashboard:** `http://TU_IP:8000` o `https://bot.tudominio.com`
- **API Status:** `http://TU_IP:8000/api/status`
- **API Portfolio:** `http://TU_IP:8000/api/portfolio`
- **API Logs:** `http://TU_IP:8000/api/logs`

## 🚨 Notas importantes

1. **Puerto 8000:** Asegúrate de que esté abierto en tu VPS
2. **Variables de entorno:** Mantén las API Keys seguras
3. **Logs:** Revisa regularmente los logs para verificar funcionamiento
4. **Backup:** Los datos se guardan en volúmenes persistentes

## 📞 Soporte

Si tienes problemas:
1. Revisa los logs en Easypanel
2. Verifica las variables de entorno
3. Comprueba que el puerto 8000 esté abierto
4. Reinicia el servicio si es necesario
