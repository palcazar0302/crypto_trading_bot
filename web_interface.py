"""
Interfaz web para control y monitoreo del bot de trading
"""
import asyncio
import json
from datetime import datetime
from typing import Dict, List
import logging

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from config import Config
from crypto_trading_bot import CryptoTradingBot
from backtesting import BacktestingEngine
from exchange_manager import ExchangeManager
from risk_manager import RiskManager

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Inicializar FastAPI
app = FastAPI(title="Crypto Trading Bot", version="1.0.0")

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Variables globales
bot_instance = None
bot_status = {"running": False, "last_update": None}
connected_clients = []

# Importar el bot funcional
try:
    from dashboard_bot import get_bot_instance
    dashboard_bot = get_bot_instance()
except:
    dashboard_bot = None

# Importar el log streamer
try:
    from log_stream import get_log_streamer
    log_streamer = get_log_streamer()
except:
    log_streamer = None

# Importar el performance tracker
try:
    from performance_tracker import performance_tracker
except:
    performance_tracker = None

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
    
    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
    
    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)
    
    async def broadcast(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except:
                self.active_connections.remove(connection)

manager = ConnectionManager()

@app.on_event("startup")
async def startup_event():
    """Inicializar componentes en el startup"""
    global bot_instance
    try:
        # Inicializar componentes
        bot_instance = CryptoTradingBot()
        logger.info("✅ Componentes inicializados")
    except Exception as e:
        logger.error(f"❌ Error inicializando componentes: {e}")

@app.get("/", response_class=HTMLResponse)
async def get_dashboard():
    """Servir el dashboard principal"""
    return """
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Crypto Trading Bot</title>
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body { 
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                color: #333;
            }
            .container { 
                max-width: 1200px; 
                margin: 0 auto; 
                padding: 20px; 
            }
            .header { 
                text-align: center; 
                color: white; 
                margin-bottom: 30px; 
            }
            .header h1 { 
                font-size: 2.5em; 
                margin-bottom: 10px; 
                text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
            }
            .status { 
                background: white; 
                padding: 20px; 
                border-radius: 15px; 
                box-shadow: 0 8px 32px rgba(0,0,0,0.1);
                margin-bottom: 20px;
            }
            .status-indicator { 
                display: inline-block; 
                width: 12px; 
                height: 12px; 
                border-radius: 50%; 
                margin-right: 10px; 
            }
            .status-running { background: #4CAF50; }
            .status-stopped { background: #f44336; }
            .grid { 
                display: grid; 
                grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); 
                gap: 20px; 
                margin-bottom: 20px;
            }
            .card { 
                background: white; 
                padding: 20px; 
                border-radius: 15px; 
                box-shadow: 0 8px 32px rgba(0,0,0,0.1);
                transition: transform 0.3s ease;
            }
            .card:hover { transform: translateY(-5px); }
            .card h3 { 
                color: #667eea; 
                margin-bottom: 15px; 
                font-size: 1.3em;
            }
            .metric { 
                display: flex; 
                justify-content: space-between; 
                margin-bottom: 10px; 
                padding: 8px 0;
                border-bottom: 1px solid #f0f0f0;
            }
            .metric:last-child { border-bottom: none; }
            .metric-value { 
                font-weight: bold; 
                color: #333; 
            }
            .metric-positive { color: #4CAF50; }
            .metric-negative { color: #f44336; }
            .controls { 
                display: flex; 
                gap: 10px; 
                flex-wrap: wrap;
            }
            .btn { 
                padding: 12px 24px; 
                border: none; 
                border-radius: 8px; 
                cursor: pointer; 
                font-size: 14px; 
                font-weight: bold; 
                transition: all 0.3s ease;
                text-transform: uppercase;
                letter-spacing: 1px;
            }
            .btn-primary { 
                background: #667eea; 
                color: white; 
            }
            .btn-primary:hover { 
                background: #5a6fd8; 
                transform: translateY(-2px);
            }
            .btn-success { 
                background: #4CAF50; 
                color: white; 
            }
            .btn-success:hover { 
                background: #45a049; 
                transform: translateY(-2px);
            }
            .btn-danger { 
                background: #f44336; 
                color: white; 
            }
            .btn-danger:hover { 
                background: #da190b; 
                transform: translateY(-2px);
            }
            .btn-warning { 
                background: #ff9800; 
                color: white; 
            }
            .btn-warning:hover { 
                background: #e68900; 
                transform: translateY(-2px);
            }
            .positions { 
                max-height: 400px; 
                overflow-y: auto; 
            }
            .position { 
                background: #f8f9fa; 
                padding: 15px; 
                border-radius: 8px; 
                margin-bottom: 10px; 
                border-left: 4px solid #667eea;
            }
            .position-header { 
                display: flex; 
                justify-content: space-between; 
                align-items: center; 
                margin-bottom: 10px;
            }
            .position-symbol { 
                font-weight: bold; 
                color: #667eea; 
                font-size: 1.1em;
            }
            .position-side { 
                padding: 4px 8px; 
                border-radius: 4px; 
                font-size: 0.8em; 
                font-weight: bold;
            }
            .side-buy { 
                background: #e8f5e8; 
                color: #4CAF50; 
            }
            .side-sell { 
                background: #ffeaea; 
                color: #f44336; 
            }
            .logs { 
                background: #1e1e1e; 
                color: #00ff00; 
                padding: 15px; 
                border-radius: 8px; 
                font-family: 'Courier New', monospace; 
                font-size: 12px; 
                max-height: 300px; 
                overflow-y: auto;
            }
            .loading { 
                text-align: center; 
                padding: 20px; 
                color: #666; 
            }
            
            .indicators-section {
                max-height: 600px;
                overflow-y: auto;
            }
            
            .indicators-table {
                width: 100%;
                border-collapse: collapse;
                font-size: 13px;
            }
            
            .indicators-table th {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 12px 8px;
                text-align: center;
                font-weight: 600;
                position: sticky;
                top: 0;
                z-index: 10;
            }
            
            .indicators-table td {
                padding: 10px 8px;
                text-align: center;
                border-bottom: 1px solid #eee;
            }
            
            .indicators-table tr:hover {
                background: #f8f9fa;
            }
            
            .symbol-cell {
                font-weight: bold;
                color: #667eea;
                text-align: left !important;
            }
            
            .indicator-bullish {
                background: #e8f5e9;
                color: #2e7d32;
                padding: 4px 8px;
                border-radius: 4px;
                font-weight: 600;
                display: inline-block;
            }
            
            .indicator-bearish {
                background: #ffebee;
                color: #c62828;
                padding: 4px 8px;
                border-radius: 4px;
                font-weight: 600;
                display: inline-block;
            }
            
            .indicator-neutral {
                background: #f5f5f5;
                color: #666;
                padding: 4px 8px;
                border-radius: 4px;
                font-weight: 600;
                display: inline-block;
            }
            
            .confidence-high {
                color: #2e7d32;
                font-weight: bold;
            }
            
            .confidence-medium {
                color: #f57c00;
                font-weight: bold;
            }
            
            .confidence-low {
                color: #c62828;
                font-weight: bold;
            }
            
            .signal-buy {
                background: #4caf50;
                color: white;
                padding: 6px 12px;
                border-radius: 6px;
                font-weight: bold;
                display: inline-block;
            }
            
            .signal-sell {
                background: #f44336;
                color: white;
                padding: 6px 12px;
                border-radius: 6px;
                font-weight: bold;
                display: inline-block;
            }
            
            .signal-none {
                background: #9e9e9e;
                color: white;
                padding: 6px 12px;
                border-radius: 6px;
                font-weight: bold;
                display: inline-block;
            }
            
            .metric {
                display: flex;
                justify-content: space-between;
                margin: 8px 0;
                padding: 4px 0;
                border-bottom: 1px solid #eee;
            }
            
            .metric:last-child {
                border-bottom: none;
            }
            
            .metric-label {
                font-weight: 500;
                color: #333;
            }
            
            .metric-value {
                font-weight: bold;
                color: #2e7d32;
            }
            
            .metric-value.negative {
                color: #d32f2f;
            }
            
            .position {
                background: #f8f9fa;
                border: 1px solid #e9ecef;
                border-radius: 8px;
                padding: 12px;
                margin: 8px 0;
                display: flex;
                justify-content: space-between;
                align-items: center;
            }
            
            .position-info {
                flex: 1;
            }
            
            .position-symbol {
                font-weight: bold;
                font-size: 16px;
                color: #333;
            }
            
            .position-details {
                font-size: 12px;
                color: #666;
                margin-top: 4px;
            }
            
            .position-pnl {
                text-align: right;
                font-weight: bold;
                font-size: 16px;
            }
            
            .position-pnl.positive {
                color: #2e7d32;
            }
            
            .position-pnl.negative {
                color: #d32f2f;
            }
            
            .position-type {
                display: inline-block;
                padding: 2px 8px;
                border-radius: 12px;
                font-size: 10px;
                font-weight: bold;
                text-transform: uppercase;
            }
            
            .position-type.buy {
                background: #e8f5e8;
                color: #2e7d32;
            }
            
            .position-type.sell {
                background: #ffebee;
                color: #d32f2f;
            }
            @media (max-width: 768px) {
                .grid { grid-template-columns: 1fr; }
                .controls { justify-content: center; }
                .header h1 { font-size: 2em; }
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🤖 Crypto Trading Bot</h1>
                <p>Dashboard de Control y Monitoreo</p>
            </div>
            
            <div class="status">
                <h3>
                    <span id="status-indicator" class="status-indicator status-stopped"></span>
                    Estado del Bot: <span id="bot-status">Detenido</span>
                </h3>
                <p id="last-update">Última actualización: Nunca</p>
            </div>
            
            <div class="controls">
                <button class="btn btn-success" onclick="startBot()">▶️ Iniciar Bot</button>
                <button class="btn btn-danger" onclick="stopBot()">⏹️ Detener Bot</button>
                <button class="btn btn-warning" onclick="runBacktest()">📊 Backtesting</button>
                <button class="btn btn-primary" onclick="refreshData()">🔄 Actualizar</button>
            </div>
            
            <div class="grid">
                <div class="card">
                    <h3>📊 Métricas del Portafolio</h3>
                    <div id="portfolio-metrics">
                        <div class="loading">Cargando métricas...</div>
                    </div>
                </div>
                
                <div class="card">
                    <h3>💰 Balance de Cuenta</h3>
                    <div id="account-balance">
                        <div class="loading">Cargando balance...</div>
                    </div>
                </div>
                
                <div class="card">
                    <h3>📈 Rendimiento</h3>
                    <div id="performance-metrics">
                        <div class="metric">
                            <span class="metric-label">Rendimiento Total:</span>
                            <span class="metric-value" id="total-return">0.0%</span>
                        </div>
                        <div class="metric">
                            <span class="metric-label">Rendimiento Diario:</span>
                            <span class="metric-value" id="daily-return">0.0%</span>
                        </div>
                        <div class="metric">
                            <span class="metric-label">Rendimiento Semanal:</span>
                            <span class="metric-value" id="weekly-return">0.0%</span>
                        </div>
                        <div class="metric">
                            <span class="metric-label">Volatilidad:</span>
                            <span class="metric-value" id="volatility">0.0%</span>
                        </div>
                        <div class="metric">
                            <span class="metric-label">Máximo Drawdown:</span>
                            <span class="metric-value" id="max-drawdown">0.0%</span>
                        </div>
                        <div class="metric">
                            <span class="metric-label">Total Trades:</span>
                            <span class="metric-value" id="total-trades">0</span>
                        </div>
                    </div>
                </div>
                
                <div class="card">
                    <h3>🔄 Posiciones Abiertas</h3>
                    <div class="positions" id="open-positions">
                        <div id="positions-list">
                            <div class="loading">Cargando posiciones...</div>
                        </div>
                    </div>
                </div>
                
                <div class="card">
                    <h3>📊 Análisis de Indicadores</h3>
                    <div class="indicators-section">
                        <div id="indicators-table">
                            <div class="loading">Cargando análisis de indicadores...</div>
                        </div>
                    </div>
                </div>
                
                <div class="card">
                    <h3>📋 Logs en Tiempo Real</h3>
                    <div class="logs" id="logs">
                        <div>Conectando al sistema de logs...</div>
                    </div>
                </div>
                
                <div class="card">
                    <h3>⚙️ Configuración</h3>
                    <div id="config-info">
                        <div class="metric">
                            <span>Capital objetivo:</span>
                            <span class="metric-value">$""" + str(Config.INVESTMENT_AMOUNT) + """</span>
                        </div>
                        <div class="metric">
                            <span>Rentabilidad objetivo:</span>
                            <span class="metric-value">""" + str(Config.TARGET_PROFIT_PERCENTAGE) + """%</span>
                        </div>
                        <div class="metric">
                            <span>Stop Loss:</span>
                            <span class="metric-value">""" + str(Config.STOP_LOSS_PERCENTAGE) + """%</span>
                        </div>
                        <div class="metric">
                            <span>Riesgo por trade:</span>
                            <span class="metric-value">""" + str(Config.RISK_PERCENTAGE) + """%</span>
                        </div>
                        <div class="metric">
                            <span>Máx. posiciones:</span>
                            <span class="metric-value">""" + str(Config.MAX_OPEN_POSITIONS) + """</span>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
        <script>
            let ws = null;
            
            function connectWebSocket() {
                const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
                ws = new WebSocket(`${protocol}//${window.location.host}/ws`);
                
                ws.onopen = function(event) {
                    console.log('WebSocket conectado');
                };
                
                ws.onmessage = function(event) {
                    const data = JSON.parse(event.data);
                    updateDashboard(data);
                };
                
                ws.onclose = function(event) {
                    console.log('WebSocket desconectado');
                    setTimeout(connectWebSocket, 5000); // Reconectar en 5 segundos
                };
                
                ws.onerror = function(error) {
                    console.error('Error WebSocket:', error);
                };
            }
            
            function updateDashboard(data) {
                if (data.status) {
                    updateBotStatus(data.status);
                }
                if (data.portfolio) {
                    updatePortfolioMetrics(data.portfolio);
                }
                if (data.balance) {
                    updateAccountBalance(data.balance);
                }
                if (data.positions) {
                    updateOpenPositions(data.positions);
                }
                if (data.log) {
                    addLogEntry(data.log);
                }
            }
            
            function updateBotStatus(status) {
                const indicator = document.getElementById('status-indicator');
                const statusText = document.getElementById('bot-status');
                const lastUpdate = document.getElementById('last-update');
                
                if (status.running) {
                    indicator.className = 'status-indicator status-running';
                    statusText.textContent = 'Ejecutándose';
                } else {
                    indicator.className = 'status-indicator status-stopped';
                    statusText.textContent = 'Detenido';
                }
                
                lastUpdate.textContent = `Última actualización: ${new Date().toLocaleTimeString()}`;
            }
            
            function updatePortfolioMetrics(portfolio) {
                const container = document.getElementById('portfolio-metrics');
                container.innerHTML = `
                    <div class="metric">
                        <span>Valor total:</span>
                        <span class="metric-value">$${portfolio.total_value?.toFixed(2) || '0.00'}</span>
                    </div>
                    <div class="metric">
                        <span>PnL no realizado:</span>
                        <span class="metric-value ${portfolio.total_unrealized_pnl >= 0 ? 'metric-positive' : 'metric-negative'}">$${portfolio.total_unrealized_pnl?.toFixed(2) || '0.00'}</span>
                    </div>
                    <div class="metric">
                        <span>PnL diario:</span>
                        <span class="metric-value ${portfolio.daily_pnl >= 0 ? 'metric-positive' : 'metric-negative'}">$${portfolio.daily_pnl?.toFixed(2) || '0.00'}</span>
                    </div>
                    <div class="metric">
                        <span>PnL total:</span>
                        <span class="metric-value ${portfolio.total_pnl >= 0 ? 'metric-positive' : 'metric-negative'}">$${portfolio.total_pnl?.toFixed(2) || '0.00'}</span>
                    </div>
                `;
            }
            
            function updateAccountBalance(balance) {
                const container = document.getElementById('account-balance');
                container.innerHTML = `
                    <div class="metric">
                        <span>USDC disponible:</span>
                        <span class="metric-value">$${balance.USDC?.toFixed(2) || '0.00'}</span>
                    </div>
                    <div class="metric">
                        <span>Balance total:</span>
                        <span class="metric-value">$${balance.total?.toFixed(2) || '0.00'}</span>
                    </div>
                `;
            }
            
            function loadPortfolioData() {
                fetch('/api/portfolio')
                    .then(response => response.json())
                    .then(data => {
                        updatePortfolioFromTracker(data);
                    })
                    .catch(error => {
                        console.error('Error cargando portafolio:', error);
                    });
            }
            
            function updatePortfolioFromTracker(portfolio) {
                // Actualizar Métricas del Portafolio
                const metricsContainer = document.getElementById('portfolio-metrics');
                const pnlClass = portfolio.total_pnl >= 0 ? 'metric-positive' : 'metric-negative';
                
                metricsContainer.innerHTML = `
                    <div class="metric">
                        <span>Valor total:</span>
                        <span class="metric-value">$${portfolio.total_value?.toFixed(2) || '0.00'}</span>
                    </div>
                    <div class="metric">
                        <span>Valor posiciones:</span>
                        <span class="metric-value">$${portfolio.positions_value?.toFixed(2) || '0.00'}</span>
                    </div>
                    <div class="metric">
                        <span>Efectivo disponible:</span>
                        <span class="metric-value">$${portfolio.cash?.toFixed(2) || '0.00'}</span>
                    </div>
                    <div class="metric">
                        <span>PnL Total:</span>
                        <span class="metric-value ${pnlClass}">$${portfolio.total_pnl?.toFixed(2) || '0.00'} (${portfolio.total_pnl_percentage?.toFixed(2) || '0.00'}%)</span>
                    </div>
                    <div class="metric">
                        <span>Posiciones abiertas:</span>
                        <span class="metric-value">${portfolio.open_positions || 0}</span>
                    </div>
                    <div class="metric">
                        <span>Total de trades:</span>
                        <span class="metric-value">${portfolio.total_trades || 0}</span>
                    </div>
                `;
                
                // Actualizar Balance de Cuenta
                const balanceContainer = document.getElementById('account-balance');
                balanceContainer.innerHTML = `
                    <div class="metric">
                        <span>Balance inicial:</span>
                        <span class="metric-value">$${portfolio.initial_balance?.toFixed(2) || '0.00'} USDC</span>
                    </div>
                    <div class="metric">
                        <span>USDC disponible:</span>
                        <span class="metric-value">$${portfolio.cash?.toFixed(2) || '0.00'} USDC</span>
                    </div>
                    <div class="metric">
                        <span>Balance total actual:</span>
                        <span class="metric-value ${pnlClass}">$${portfolio.total_value?.toFixed(2) || '0.00'} USDC</span>
                    </div>
                    <div class="metric">
                        <span>Ganancia/Pérdida:</span>
                        <span class="metric-value ${pnlClass}">$${portfolio.total_pnl?.toFixed(2) || '0.00'} (${portfolio.total_pnl_percentage?.toFixed(2) || '0.00'}%)</span>
                    </div>
                `;
            }
            
            function updateOpenPositions(positions) {
                const container = document.getElementById('positions-list');
                
                if (!positions || positions.length === 0) {
                    container.innerHTML = '<div class="loading">No hay posiciones abiertas</div>';
                    return;
                }
                
                const positionsHTML = positions.map(position => {
                    const pnlClass = position.unrealized_pnl >= 0 ? 'positive' : 'negative';
                    const typeClass = position.side.toLowerCase();
                    const pnlSign = position.unrealized_pnl >= 0 ? '+' : '';
                    
                    return `
                        <div class="position">
                            <div class="position-info">
                                <div class="position-symbol">
                                    ${position.symbol}
                                    <span class="position-type ${typeClass}">${position.side.toUpperCase()}</span>
                                </div>
                                <div class="position-details">
                                    Cantidad: ${position.amount?.toFixed(6) || '0.000000'} | 
                                    Precio: $${position.entry_price?.toFixed(4) || '0.0000'} → $${position.current_price?.toFixed(4) || '0.0000'} | 
                                    Abierto: ${position.duration || 'N/A'}
                                </div>
                            </div>
                            <div class="position-pnl ${pnlClass}">
                                ${pnlSign}${position.unrealized_pnl?.toFixed(2) || '0.00'}%
                            </div>
                        </div>
                    `;
                }).join('');
                
                container.innerHTML = positionsHTML;
            }
            
            function addLogEntry(logEntry) {
                const logsContainer = document.getElementById('logs');
                logsContainer.innerHTML += `<div>${logEntry}</div>`;
                logsContainer.scrollTop = logsContainer.scrollHeight;
                
                // Mantener solo los últimos 50 logs
                const logs = logsContainer.children;
                if (logs.length > 50) {
                    logsContainer.removeChild(logs[0]);
                }
            }
            
            // Función para cargar logs desde el servidor
            function loadLogsFromServer() {
                fetch('/api/logs')
                    .then(response => response.json())
                    .then(data => {
                        const logsContainer = document.getElementById('logs');
                        if (data.logs && data.logs.length > 0) {
                            logsContainer.innerHTML = data.logs.map(log => 
                                `<div>${log}</div>`
                            ).join('');
                            logsContainer.scrollTop = logsContainer.scrollHeight;
                        }
                    })
                    .catch(error => {
                        console.error('Error cargando logs:', error);
                    });
            }

            function loadIndicators() {
                fetch('/api/indicators')
                    .then(response => response.json())
                    .then(data => {
                        updateIndicatorsTable(data.indicators);
                    })
                    .catch(error => {
                        console.error('Error cargando indicadores:', error);
                    });
            }

            function getIndicatorClass(indicator) {
                const bullishValues = ['alcista', 'sobrecompra', 'sobreventa', 'rebote_esperado', 'cruce_alcista'];
                const bearishValues = ['bajista', 'cruce_bajista'];
                
                if (bullishValues.includes(indicator)) {
                    return 'indicator-bullish';
                } else if (bearishValues.includes(indicator)) {
                    return 'indicator-bearish';
                } else {
                    return 'indicator-neutral';
                }
            }

            function getIndicatorIcon(indicator) {
                const bullishValues = ['alcista', 'sobrecompra', 'sobreventa', 'rebote_esperado', 'cruce_alcista'];
                const bearishValues = ['bajista', 'cruce_bajista'];
                
                if (bullishValues.includes(indicator)) {
                    return '✅';
                } else if (bearishValues.includes(indicator)) {
                    return '❌';
                } else {
                    return '⚪';
                }
            }

            function getIndicatorText(indicator) {
                const textMap = {
                    'alcista': 'Alcista',
                    'bajista': 'Bajista',
                    'neutral': 'Neutral',
                    'sobrecompra': 'Sobrecompra',
                    'sobreventa': 'Sobreventa',
                    'rebote_esperado': 'Rebote',
                    'cruce_alcista': 'Cruce ↗',
                    'cruce_bajista': 'Cruce ↘',
                    'normal': 'Normal'
                };
                return textMap[indicator] || indicator;
            }

            function updateIndicatorsTable(indicators) {
                const container = document.getElementById('indicators-table');
                
                if (!indicators || Object.keys(indicators).length === 0) {
                    container.innerHTML = '<div class="loading">No hay datos de indicadores disponibles</div>';
                    return;
                }

                let tableHTML = `
                    <table class="indicators-table">
                        <thead>
                            <tr>
                                <th>Símbolo</th>
                                <th>RSI</th>
                                <th>EMA</th>
                                <th>MACD</th>
                                <th>Bollinger</th>
                                <th>Stochastic</th>
                                <th>Señal</th>
                                <th>Confianza</th>
                            </tr>
                        </thead>
                        <tbody>
                `;

                Object.keys(indicators).sort().forEach(symbol => {
                    const data = indicators[symbol];
                    const ind = data.indicators || {};
                    
                    const rsiClass = getIndicatorClass(ind.rsi || 'neutral');
                    const emaClass = getIndicatorClass(ind.ema || 'neutral');
                    const macdClass = getIndicatorClass(ind.macd || 'neutral');
                    const bbClass = getIndicatorClass(ind.bb || 'neutral');
                    const stochClass = getIndicatorClass(ind.stoch || 'neutral');
                    
                    const rsiIcon = getIndicatorIcon(ind.rsi || 'neutral');
                    const emaIcon = getIndicatorIcon(ind.ema || 'neutral');
                    const macdIcon = getIndicatorIcon(ind.macd || 'neutral');
                    const bbIcon = getIndicatorIcon(ind.bb || 'neutral');
                    const stochIcon = getIndicatorIcon(ind.stoch || 'neutral');
                    
                    let signalClass = 'signal-none';
                    let signalText = 'Sin señal';
                    
                    if (data.buy) {
                        signalClass = 'signal-buy';
                        signalText = 'COMPRA';
                    } else if (data.sell) {
                        signalClass = 'signal-sell';
                        signalText = 'VENTA';
                    }
                    
                    const confidence = data.confidence.toFixed(0);
                    let confidenceClass = 'confidence-low';
                    if (confidence >= 80) confidenceClass = 'confidence-high';
                    else if (confidence >= 60) confidenceClass = 'confidence-medium';
                    
                    tableHTML += `
                        <tr>
                            <td class="symbol-cell">${symbol}</td>
                            <td><span class="${rsiClass}">${rsiIcon} ${getIndicatorText(ind.rsi || 'neutral')}</span></td>
                            <td><span class="${emaClass}">${emaIcon} ${getIndicatorText(ind.ema || 'neutral')}</span></td>
                            <td><span class="${macdClass}">${macdIcon} ${getIndicatorText(ind.macd || 'neutral')}</span></td>
                            <td><span class="${bbClass}">${bbIcon} ${getIndicatorText(ind.bb || 'neutral')}</span></td>
                            <td><span class="${stochClass}">${stochIcon} ${getIndicatorText(ind.stoch || 'neutral')}</span></td>
                            <td><span class="${signalClass}">${signalText}</span></td>
                            <td><span class="${confidenceClass}">${confidence}%</span></td>
                        </tr>
                    `;
                });

                tableHTML += `
                        </tbody>
                    </table>
                `;

                container.innerHTML = tableHTML;
            }
            
            // Función para cargar métricas de rendimiento
            function loadPerformanceMetrics() {
                fetch('/api/performance')
                    .then(response => response.json())
                    .then(data => {
                        if (data.metrics) {
                            updatePerformanceDisplay(data.metrics);
                        }
                    })
                    .catch(error => {
                        console.error('Error cargando rendimiento:', error);
                    });
            }
            
            // Función para actualizar la visualización de rendimiento
            function updatePerformanceDisplay(metrics) {
                const elements = {
                    'total-return': metrics.total_return + '%',
                    'daily-return': metrics.daily_return + '%',
                    'weekly-return': metrics.weekly_return + '%',
                    'volatility': metrics.volatility + '%',
                    'max-drawdown': metrics.max_drawdown + '%',
                    'total-trades': metrics.total_trades
                };
                
                Object.entries(elements).forEach(([id, value]) => {
                    const element = document.getElementById(id);
                    if (element) {
                        element.textContent = value;
                        
                        // Colorear según si es positivo o negativo
                        if (typeof value === 'string' && value.includes('%')) {
                            const numValue = parseFloat(value);
                            element.className = 'metric-value' + (numValue < 0 ? ' negative' : '');
                        }
                    }
                });
            }
            
            // Función para actualizar posiciones abiertas
            function updatePositions(positions) {
                const positionsContainer = document.getElementById('positions-list');
                
                if (!positions || positions.length === 0) {
                    positionsContainer.innerHTML = '<div class="loading">No hay posiciones abiertas</div>';
                    return;
                }
                
                const positionsHTML = positions.map(position => {
                    const pnlClass = position.pnl >= 0 ? 'positive' : 'negative';
                    const typeClass = position.type.toLowerCase();
                    const pnlSign = position.pnl >= 0 ? '+' : '';
                    
                    return `
                        <div class="position">
                            <div class="position-info">
                                <div class="position-symbol">
                                    ${position.symbol}
                                    <span class="position-type ${typeClass}">${position.type}</span>
                                </div>
                                <div class="position-details">
                                    Cantidad: ${position.quantity} | 
                                    Precio: $${position.entry_price} → $${position.current_price} | 
                                    Abierto: ${position.duration}
                                </div>
                            </div>
                            <div class="position-pnl ${pnlClass}">
                                ${pnlSign}${position.pnl.toFixed(2)}%
                            </div>
                        </div>
                    `;
                }).join('');
                
                positionsContainer.innerHTML = positionsHTML;
            }
            
            async function startBot() {
                try {
                    const response = await fetch('/api/bot/start', { method: 'POST' });
                    const result = await response.json();
                    if (result.success) {
                        addLogEntry('Bot iniciado exitosamente');
                    } else {
                        addLogEntry(`Error iniciando bot: ${result.error}`);
                    }
                } catch (error) {
                    addLogEntry(`Error: ${error.message}`);
                }
            }
            
            async function stopBot() {
                try {
                    const response = await fetch('/api/bot/stop', { method: 'POST' });
                    const result = await response.json();
                    if (result.success) {
                        addLogEntry('Bot detenido');
                    } else {
                        addLogEntry(`Error deteniendo bot: ${result.error}`);
                    }
                } catch (error) {
                    addLogEntry(`Error: ${error.message}`);
                }
            }
            
            async function runBacktest() {
                try {
                    addLogEntry('Iniciando backtesting...');
                    const response = await fetch('/api/backtest/run', { method: 'POST' });
                    const result = await response.json();
                    if (result.success) {
                        addLogEntry('Backtesting completado');
                        alert('Backtesting completado. Revisa los logs para detalles.');
                    } else {
                        addLogEntry(`Error en backtesting: ${result.error}`);
                    }
                } catch (error) {
                    addLogEntry(`Error: ${error.message}`);
                }
            }
            
            async function refreshData() {
                try {
                    const response = await fetch('/api/status');
                    const data = await response.json();
                    updateDashboard(data);
                    addLogEntry('Datos actualizados');
                } catch (error) {
                    addLogEntry(`Error actualizando datos: ${error.message}`);
                }
            }
            
            // Inicializar
            connectWebSocket();
            refreshData();
            loadLogsFromServer(); // Cargar logs iniciales
            loadPerformanceMetrics(); // Cargar métricas de rendimiento
            loadPortfolioData(); // Cargar datos del portafolio
            
            // Actualizar datos cada 30 segundos
            setInterval(refreshData, 30000);
            // Actualizar logs cada 3 segundos
            setInterval(loadLogsFromServer, 3000);
            // Actualizar indicadores cada 30 segundos
            setInterval(loadIndicators, 30000);
            // Actualizar rendimiento cada 60 segundos
            setInterval(loadPerformanceMetrics, 60000);
            // Actualizar portafolio cada 30 segundos
            setInterval(loadPortfolioData, 30000);
            
            // Cargar indicadores inicialmente
            loadIndicators();
        </script>
    </body>
    </html>
    """

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket para actualizaciones en tiempo real"""
    await manager.connect(websocket)
    try:
        while True:
            # Mantener conexión activa
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)

@app.get("/api/status")
async def get_status():
    """Obtener estado actual del bot"""
    try:
        # Leer estado desde archivo compartido
        from bot_status import load_status
        status_data = load_status()
        
        return {
            "status": {
                "running": status_data.get("running", False),
                "last_update": status_data.get("last_update", datetime.now().isoformat())
            },
            "portfolio": {},
            "balance": {},
            "positions": []
        }
        
    except Exception as e:
        logger.error(f"Error obteniendo estado: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/logs")
async def get_logs():
    """Obtener logs recientes del bot"""
    try:
        if log_streamer:
            logs = log_streamer.get_recent_logs(20)
            return {"logs": logs}
        else:
            return {"logs": ["Sistema de logs no disponible"]}
    except Exception as e:
        logger.error(f"Error obteniendo logs: {e}")
        return {"logs": [f"Error: {e}"]}

@app.get("/api/portfolio")
async def get_portfolio():
    """Obtener balance y resumen del portafolio"""
    try:
        from portfolio_tracker import get_portfolio_tracker
        from exchange_manager import ExchangeManager
        
        # Intentar obtener balance real de Binance
        try:
            exchange = ExchangeManager()
            real_balance = exchange.get_usdc_balance()
            
            # Si hay balance real, usarlo
            if real_balance > 0:
                tracker = get_portfolio_tracker()
                summary = tracker.get_portfolio_summary()
                # Actualizar con balance real
                summary['cash'] = real_balance
                summary['total_value'] = real_balance + summary.get('positions_value', 0)
                initial = summary.get('initial_balance', 100)
                summary['total_pnl'] = summary['total_value'] - initial
                summary['total_pnl_percentage'] = (summary['total_pnl'] / initial * 100) if initial > 0 else 0
                return summary
        except Exception as e:
            logger.warning(f"No se pudo obtener balance real: {e}")
        
        # Fallback a balance simulado
        tracker = get_portfolio_tracker()
        return tracker.get_portfolio_summary()
    except Exception as e:
        logger.error(f"Error obteniendo portafolio: {e}")
        from config import Config
        initial_balance = float(Config.INVESTMENT_AMOUNT)
        return {
            'cash': initial_balance,
            'positions_value': 0,
            'total_value': initial_balance,
            'initial_balance': initial_balance,
            'total_pnl': 0,
            'total_pnl_percentage': 0,
            'total_trades': 0,
            'open_positions': 0,
            'last_update': datetime.now().isoformat()
        }

@app.get("/api/indicators")
async def get_indicators():
    """Obtener indicadores técnicos de todas las criptomonedas"""
    try:
        from indicators_store import get_indicators_with_timestamp
        return get_indicators_with_timestamp()
    except Exception as e:
        logger.error(f"Error obteniendo indicadores: {e}")
        return {
            "indicators": {},
            "timestamp": datetime.now().isoformat()
        }

@app.get("/api/performance")
async def get_performance():
    """Obtener métricas de rendimiento"""
    try:
        if performance_tracker:
            metrics = performance_tracker.get_performance_metrics()
            chart_data = performance_tracker.get_performance_chart_data()
            return {
                "metrics": metrics,
                "chart_data": chart_data
            }
        else:
            return {
                "metrics": {
                    "total_return": 0.0,
                    "daily_return": 0.0,
                    "weekly_return": 0.0,
                    "monthly_return": 0.0,
                    "volatility": 0.0,
                    "max_drawdown": 0.0,
                    "current_value": 1000.0,
                    "total_trades": 0,
                    "winning_trades": 0,
                    "losing_trades": 0
                },
                "chart_data": {"dates": [], "values": []}
            }
    except Exception as e:
        logger.error(f"Error obteniendo rendimiento: {e}")
        return {"error": str(e)}

@app.get("/api/trades/history")
async def get_trades_history():
    """Obtener historial de trades"""
    try:
        import os
        trades_file = "data/trades_history.json"
        
        if not os.path.exists(trades_file):
            return []
        
        with open(trades_file, 'r') as f:
            trades = json.load(f)
        
        # Asegurarse de que sea una lista
        if not isinstance(trades, list):
            return []
        
        return trades
        
    except Exception as e:
        logger.error(f"Error obteniendo historial de trades: {e}")
        return []

@app.post("/api/bot/start")
async def start_bot():
    """Iniciar el bot de trading"""
    try:
        global bot_status
        
        if bot_status["running"]:
            return {"success": False, "error": "Bot ya está ejecutándose"}
        
        if not bot_instance:
            return {"success": False, "error": "Bot no inicializado"}
        
        # Iniciar bot en hilo separado
        import threading
        bot_thread = threading.Thread(target=bot_instance.start, daemon=True)
        bot_thread.start()
        
        bot_status["running"] = True
        bot_status["last_update"] = datetime.now().isoformat()
        
        await manager.broadcast(json.dumps({
            "status": bot_status,
            "log": "Bot iniciado exitosamente"
        }))
        
        return {"success": True, "message": "Bot iniciado"}
        
    except Exception as e:
        logger.error(f"Error iniciando bot: {e}")
        return {"success": False, "error": str(e)}

@app.post("/api/bot/stop")
async def stop_bot():
    """Detener el bot de trading"""
    try:
        global bot_status
        
        if not bot_status["running"]:
            return {"success": False, "error": "Bot no está ejecutándose"}
        
        if bot_instance:
            bot_instance.stop()
        
        bot_status["running"] = False
        bot_status["last_update"] = datetime.now().isoformat()
        
        await manager.broadcast(json.dumps({
            "status": bot_status,
            "log": "Bot detenido"
        }))
        
        return {"success": True, "message": "Bot detenido"}
        
    except Exception as e:
        logger.error(f"Error deteniendo bot: {e}")
        return {"success": False, "error": str(e)}

@app.post("/api/backtest/run")
async def run_backtest():
    """Ejecutar backtesting"""
    try:
        engine = BacktestingEngine(initial_capital=Config.INVESTMENT_AMOUNT)
        
        # Ejecutar backtesting en múltiples símbolos
        symbols = ['BTC/USDT', 'ETH/USDT', 'BNB/USDT']
        result = engine.run_multi_symbol_backtest(symbols, '2023-01-01', '2023-12-31')
        
        # Enviar resultados por WebSocket
        await manager.broadcast(json.dumps({
            "log": f"Backtesting completado: {result.get('summary', 'Sin resumen')}"
        }))
        
        return {"success": True, "result": result}
        
    except Exception as e:
        logger.error(f"Error en backtesting: {e}")
        return {"success": False, "error": str(e)}

@app.get("/api/config")
async def get_config():
    """Obtener configuración actual"""
    try:
        return {
            "investment_amount": Config.INVESTMENT_AMOUNT,
            "target_profit_percentage": Config.TARGET_PROFIT_PERCENTAGE,
            "stop_loss_percentage": Config.STOP_LOSS_PERCENTAGE,
            "risk_percentage": Config.RISK_PERCENTAGE,
            "max_open_positions": Config.MAX_OPEN_POSITIONS,
            "symbols": Config.SYMBOLS,
            "testnet": Config.BINANCE_TESTNET
        }
    except Exception as e:
        logger.error(f"Error obteniendo configuración: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")



