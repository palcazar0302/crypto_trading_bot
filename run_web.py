#!/usr/bin/env python3
"""
Script para ejecutar la interfaz web del bot
"""
import sys
import os

# Agregar el directorio actual al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def main():
    """Función principal para ejecutar la interfaz web"""
    print("🌐 Iniciando Interfaz Web del Bot de Trading...")
    print("=" * 50)
    
    try:
        # Verificar dependencias
        import uvicorn
        from web_interface import app
        
        print("✅ Interfaz web cargada correctamente")
        print("🌐 Servidor iniciando en http://localhost:8000")
        print("📊 Abre tu navegador y ve a la URL para acceder al dashboard")
        print("Presiona Ctrl+C para detener el servidor")
        print("=" * 50)
        
        # Ejecutar servidor
        uvicorn.run(
            app, 
            host="0.0.0.0", 
            port=8000, 
            log_level="info",
            reload=False
        )
        
    except KeyboardInterrupt:
        print("\n🛑 Servidor detenido por el usuario")
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()



