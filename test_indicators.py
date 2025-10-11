#!/usr/bin/env python3
"""
Script de diagnóstico para verificar que los indicadores funcionan correctamente
"""

import sys
import os
import json
from datetime import datetime

# Añadir el directorio actual al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_indicators_store():
    """Probar que indicators_store funciona"""
    try:
        from indicators_store import get_indicators_with_timestamp, save_indicators
        print("✅ indicators_store importado correctamente")
        
        # Crear datos de prueba
        test_data = {
            "BTC/USDC": {
                "indicators": {
                    "rsi": "sobreventa",
                    "ema": "bajista", 
                    "macd": "bajista",
                    "bb": "rebote_esperado",
                    "stoch": "neutral"
                },
                "buy": False,
                "sell": False,
                "confidence": 45.0,
                "timestamp": datetime.now().isoformat()
            }
        }
        
        # Guardar datos de prueba
        save_indicators(test_data)
        print("✅ Datos de prueba guardados")
        
        # Leer datos
        result = get_indicators_with_timestamp()
        print("✅ Datos leídos correctamente")
        print(f"📊 Indicadores encontrados: {len(result.get('indicators', {}))}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en indicators_store: {e}")
        return False

def test_web_interface():
    """Probar que la interfaz web puede obtener indicadores"""
    try:
        from web_interface import app
        print("✅ web_interface importado correctamente")
        
        # Verificar que el endpoint existe
        routes = [route.path for route in app.routes]
        if "/api/indicators" in routes:
            print("✅ Endpoint /api/indicators encontrado")
        else:
            print("❌ Endpoint /api/indicators NO encontrado")
            return False
            
        return True
        
    except Exception as e:
        print(f"❌ Error en web_interface: {e}")
        return False

def test_config():
    """Probar que la configuración es válida"""
    try:
        from config import Config
        print("✅ Config importado correctamente")
        print(f"📈 Símbolos configurados: {len(Config.SYMBOLS)}")
        print(f"🎯 Primeros 5 símbolos: {Config.SYMBOLS[:5]}")
        return True
        
    except Exception as e:
        print(f"❌ Error en config: {e}")
        return False

def main():
    """Función principal de diagnóstico"""
    print("🔍 DIAGNÓSTICO DEL SISTEMA DE INDICADORES")
    print("=" * 50)
    
    tests = [
        ("Configuración", test_config),
        ("Indicators Store", test_indicators_store),
        ("Web Interface", test_web_interface)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n🧪 Probando {test_name}...")
        result = test_func()
        results.append((test_name, result))
    
    print("\n📋 RESUMEN DE RESULTADOS:")
    print("=" * 30)
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name}: {status}")
    
    all_passed = all(result for _, result in results)
    if all_passed:
        print("\n🎉 ¡TODOS LOS TESTS PASARON!")
        print("El sistema de indicadores debería funcionar correctamente.")
    else:
        print("\n⚠️ ALGUNOS TESTS FALLARON")
        print("Hay problemas que necesitan ser solucionados.")
    
    return all_passed

if __name__ == "__main__":
    main()
