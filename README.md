# 🤖 Bot de Trading de Criptomonedas

Un bot de trading automático avanzado para criptomonedas que utiliza análisis técnico, gestión de riesgo y estrategias de trading automatizadas para lograr una rentabilidad objetivo del 30%.

## ✨ Características Principales

- **Trading Automático**: Ejecuta compras y ventas basadas en análisis técnico
- **Análisis Técnico Avanzado**: RSI, MACD, Bandas de Bollinger, EMA, Estocástico
- **Gestión de Riesgo**: Stop-loss, take-profit, límites de pérdida diaria
- **Múltiples Indicadores**: Sistema de señales combinadas con alta precisión
- **Backtesting**: Validación de estrategias con datos históricos
- **Interfaz Web**: Dashboard en tiempo real para monitoreo y control
- **Notificaciones**: Alertas por Telegram para trades y eventos importantes
- **Logging Completo**: Registro detallado de todas las operaciones

## 🚀 Instalación

### Requisitos Previos

- Python 3.8 o superior
- Cuenta en Binance (con API keys)
- Telegram Bot (opcional, para notificaciones)

### Pasos de Instalación

1. **Clonar el repositorio**
```bash
git clone <tu-repositorio>
cd crypto_trading_bot
```

2. **Instalar dependencias**
```bash
pip install -r requirements.txt
```

3. **Configurar variables de entorno**
```bash
cp config.env.example .env
```

Edita el archivo `.env` con tus credenciales:
```env
# Configuración de Binance
BINANCE_API_KEY=tu_api_key_aqui
BINANCE_SECRET_KEY=tu_secret_key_aqui
BINANCE_TESTNET=True  # Cambiar a False para trading real

# Configuración del bot
INVESTMENT_AMOUNT=1000
TARGET_PROFIT_PERCENTAGE=30
STOP_LOSS_PERCENTAGE=5
RISK_PERCENTAGE=2
MAX_OPEN_POSITIONS=3

# Notificaciones Telegram (opcional)
TELEGRAM_BOT_TOKEN=tu_bot_token_aqui
TELEGRAM_CHAT_ID=tu_chat_id_aqui
```

## 📊 Configuración de Binance

1. Ve a [Binance](https://www.binance.com) y crea una cuenta
2. Activa la autenticación de dos factores (2FA)
3. Ve a "API Management" en tu perfil
4. Crea una nueva API key con permisos de trading
5. **IMPORTANTE**: Comienza con TESTNET habilitado para pruebas

## 🔧 Configuración de Telegram (Opcional)

1. Crea un bot con [@BotFather](https://t.me/botfather)
2. Obtén el token del bot
3. Obtén tu chat ID enviando un mensaje a [@userinfobot](https://t.me/userinfobot)

## 🎯 Estrategia de Trading

### Indicadores Técnicos Utilizados

- **RSI (Relative Strength Index)**: Identifica condiciones de sobreventa/sobrecompra
- **MACD**: Detecta cambios de momentum
- **Bandas de Bollinger**: Identifica niveles de soporte y resistencia dinámicos
- **EMA (Exponential Moving Average)**: Determina tendencias
- **Estocástico**: Confirma señales de momentum

### Sistema de Señales

El bot utiliza un sistema de señales combinadas que requiere **mínimo 3 indicadores** en la misma dirección para ejecutar un trade:

- **Señal de Compra**: RSI < 30, EMA corta > EMA larga, MACD alcista, precio cerca banda inferior
- **Señal de Venta**: RSI > 70, EMA corta < EMA larga, MACD bajista, precio cerca banda superior

### Gestión de Riesgo

- **Stop Loss**: 5% por defecto (configurable)
- **Take Profit**: 30% por defecto (configurable)
- **Riesgo por Trade**: 2% del capital
- **Máxima Pérdida Diaria**: 5% del capital
- **Posiciones Máximas**: 3 simultáneas

## 🖥️ Uso del Bot

### Iniciar el Bot Principal

```bash
python crypto_trading_bot.py
```

### Iniciar Interfaz Web

```bash
python web_interface.py
```

Luego ve a `http://localhost:8000` en tu navegador.

### Ejecutar Backtesting

```bash
python backtesting.py
```

## 📱 Interfaz Web

La interfaz web proporciona:

- **Dashboard en Tiempo Real**: Estado del bot, métricas del portafolio
- **Control del Bot**: Iniciar/detener el bot
- **Monitoreo de Posiciones**: Posiciones abiertas y su rendimiento
- **Logs en Vivo**: Registro de operaciones en tiempo real
- **Métricas de Rendimiento**: PnL, retornos, estadísticas de trading

## 📈 Backtesting

El sistema de backtesting te permite:

- Probar estrategias con datos históricos
- Calcular métricas de rendimiento
- Optimizar parámetros
- Validar la estrategia antes del trading real

### Ejemplo de Uso

```python
from backtesting import BacktestingEngine

engine = BacktestingEngine(initial_capital=10000)
result = engine.run_backtest('BTC/USDT', '2023-01-01', '2023-12-31')
print(result['summary'])
```

## 📊 Métricas de Rendimiento

El bot calcula automáticamente:

- **Tasa de Acierto**: Porcentaje de trades ganadores
- **Factor de Beneficio**: Ratio ganancias/pérdidas
- **Ratio de Sharpe**: Rendimiento ajustado por riesgo
- **Máximo Drawdown**: Mayor pérdida consecutiva
- **Retorno Total**: Rentabilidad acumulada

## ⚠️ Advertencias Importantes

1. **Comienza con TESTNET**: Siempre prueba primero en el entorno de pruebas
2. **Capital Limitado**: No inviertas más de lo que puedes permitirte perder
3. **Monitoreo Constante**: Aunque es automático, supervisa regularmente
4. **Mercados Volátiles**: Las criptomonedas son altamente volátiles
5. **Riesgo de Pérdidas**: El trading conlleva riesgo de pérdidas significativas

## 🔒 Seguridad

- **API Keys**: Nunca compartas tus API keys
- **Permisos Limitados**: Usa solo permisos necesarios en Binance
- **IP Restrictions**: Configura restricciones de IP en Binance
- **Backups**: Respalda regularmente tu configuración

## 📝 Logs y Monitoreo

Los logs se guardan en la carpeta `logs/`:
- `crypto_bot_YYYY-MM-DD.log`: Log general del bot
- `trades_YYYY-MM-DD.log`: Log específico de trades

## 🛠️ Personalización

### Modificar Estrategia

Edita `technical_analysis.py` para ajustar:
- Parámetros de indicadores
- Lógica de señales
- Umbrales de confianza

### Ajustar Gestión de Riesgo

Modifica `risk_manager.py` para cambiar:
- Tamaños de posición
- Límites de riesgo
- Reglas de stop-loss/take-profit

### Configurar Símbolos

Edita `Config.SYMBOLS` en `config.py` para agregar/quitar criptomonedas.

## 📞 Soporte

Para problemas o preguntas:
1. Revisa los logs en la carpeta `logs/`
2. Verifica la configuración en `.env`
3. Consulta la documentación de la API de Binance
4. Asegúrate de tener suficientes permisos en tu API key

## 📄 Licencia

Este proyecto es para fines educativos. Úsalo bajo tu propia responsabilidad.

## ⚡ Rendimiento Esperado

**OBJETIVO**: 30% de rentabilidad anual
**RIESGO**: Máximo 5% de pérdida diaria
**FRECUENCIA**: 2-5 trades por día en promedio
**WIN RATE**: 60-70% esperado

---

**⚠️ DISCLAIMER**: Este software es solo para fines educativos. El trading de criptomonedas conlleva riesgos significativos. Nunca inviertas más de lo que puedes permitirte perder. Los resultados pasados no garantizan resultados futuros.



