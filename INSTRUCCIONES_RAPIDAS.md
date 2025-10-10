# 🚀 Instrucciones Rápidas - Bot de Trading

## ⚡ Inicio Rápido (5 minutos)

### 1. Instalación
```bash
# Instalar dependencias
pip install -r requirements.txt

# Configurar automáticamente
python setup.py
```

### 2. Configurar Credenciales
Edita el archivo `.env` que se creó automáticamente:
```env
BINANCE_API_KEY=tu_api_key_aqui
BINANCE_SECRET_KEY=tu_secret_key_aqui
BINANCE_TESTNET=True  # ¡IMPORTANTE! Mantener en True para pruebas
```

### 3. Ejecutar el Bot
```bash
# Opción 1: Bot en consola
python run_bot.py

# Opción 2: Interfaz web
python run_web.py
# Luego ve a http://localhost:8000
```

## 🔑 Obtener API Keys de Binance

1. Ve a [binance.com](https://binance.com) → Perfil → API Management
2. Crea nueva API key
3. **IMPORTANTE**: Activa solo "Enable Spot & Margin Trading"
4. Configura restricciones de IP (recomendado)
5. Copia API Key y Secret Key al archivo `.env`

## 📱 Configurar Telegram (Opcional)

1. Busca [@BotFather](https://t.me/botfather) en Telegram
2. Crea un nuevo bot: `/newbot`
3. Copia el token al archivo `.env`
4. Obtén tu Chat ID: [@userinfobot](https://t.me/userinfobot)
5. Copia el Chat ID al archivo `.env`

## ⚠️ Seguridad - PASOS OBLIGATORIOS

1. **Siempre comenzar con TESTNET=True**
2. **No usar dinero real hasta probar completamente**
3. **Configurar límites de IP en Binance**
4. **No compartir nunca tus API keys**
5. **Usar autenticación de 2 factores en Binance**

## 🎯 Configuración Recomendada para Principiantes

```env
# Configuración conservadora
INVESTMENT_AMOUNT=100          # Solo $100 para empezar
TARGET_PROFIT_PERCENTAGE=15    # 15% objetivo (más realista)
STOP_LOSS_PERCENTAGE=3         # Stop loss más ajustado
RISK_PERCENTAGE=1              # Solo 1% de riesgo por trade
MAX_OPEN_POSITIONS=2           # Máximo 2 posiciones
```

## 📊 Monitoreo

### Interfaz Web
- Ve a `http://localhost:8000`
- Dashboard en tiempo real
- Control del bot
- Métricas de rendimiento
- Logs en vivo

### Logs
- Archivos en carpeta `logs/`
- `crypto_bot_YYYY-MM-DD.log`: Log general
- `trades_YYYY-MM-DD.log`: Solo trades

## 🔧 Comandos Útiles

```bash
# Backtesting
python backtesting.py

# Solo probar conexión
python -c "from exchange_manager import ExchangeManager; e = ExchangeManager(); print(e.get_usdt_balance())"

# Verificar configuración
python -c "from config import Config; Config.validate_config(); print('Config OK')"
```

## 🚨 Solución de Problemas Comunes

### Error: "API key no válida"
- Verifica que las API keys estén correctas
- Asegúrate de que tienen permisos de trading
- Verifica restricciones de IP

### Error: "No hay suficiente balance"
- Deposita USDT en tu cuenta de Binance
- Verifica que estás en el mercado spot
- Comprueba que no hay órdenes pendientes

### Bot no ejecuta trades
- Verifica que `BINANCE_TESTNET=False` (para trading real)
- Revisa los logs para errores
- Asegúrate de que hay suficiente volatilidad en el mercado

### Notificaciones no llegan
- Verifica el token de Telegram
- Comprueba el Chat ID
- Asegúrate de haber enviado `/start` al bot

## 📈 Expectativas Realistas

- **Rentabilidad objetivo**: 15-30% anual
- **Trades por día**: 2-5 en promedio
- **Win rate esperado**: 60-70%
- **Riesgo máximo**: 5% pérdida diaria

## 🆘 Emergencias

### Detener el bot inmediatamente
```bash
# Si está en consola: Ctrl+C
# Si está en web: Botón "Detener Bot"
```

### Cerrar todas las posiciones
El bot tiene protección automática, pero si necesitas cerrar manualmente:
1. Ve a Binance.com
2. Spot Trading → Órdenes Abiertas
3. Cancela todas las órdenes
4. Vende todas las posiciones

## 📞 Soporte

1. **Revisa los logs** en la carpeta `logs/`
2. **Verifica la configuración** en `.env`
3. **Consulta la documentación** de Binance API
4. **Prueba primero en TESTNET**

---

**⚠️ RECORDATORIO IMPORTANTE**: Este bot es para fines educativos. El trading de criptomonedas conlleva riesgos significativos. Nunca inviertas más de lo que puedes permitirte perder. Los resultados pasados no garantizan resultados futuros.

**🎯 OBJETIVO**: Aprender sobre trading algorítmico y automatización, no hacerse rico rápidamente.



