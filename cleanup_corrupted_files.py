#!/usr/bin/env python3
"""
Script para limpiar archivos corruptos y resetear el estado del bot
"""
import os
import json
import shutil
from datetime import datetime

def backup_file(filepath):
    """Crear backup de un archivo"""
    if os.path.exists(filepath):
        backup_path = f"{filepath}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        try:
            shutil.copy2(filepath, backup_path)
            print(f"✅ Backup creado: {backup_path}")
            return True
        except Exception as e:
            print(f"❌ Error creando backup: {e}")
            return False
    return False

def cleanup_corrupted_files():
    """Limpiar archivos corruptos"""
    data_dir = "data"
    
    print("🧹 Iniciando limpieza de archivos corruptos...")
    print("=" * 60)
    
    # Lista de archivos a limpiar
    files_to_clean = [
        "open_positions.json",
        "bot_status.json",
    ]
    
    for filename in files_to_clean:
        filepath = os.path.join(data_dir, filename)
        
        if not os.path.exists(filepath):
            print(f"⚠️  {filename} no existe, creando nuevo...")
            continue
        
        print(f"\n📄 Procesando: {filename}")
        
        # Intentar leer el archivo
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
            print(f"   ✅ JSON válido")
            
            # Si es open_positions.json, verificar y limpiar posiciones cerradas
            if filename == "open_positions.json":
                if isinstance(data, dict):
                    closed_count = 0
                    positions_to_keep = {}
                    
                    for symbol, pos in data.items():
                        if pos.get('status') == 'closed':
                            closed_count += 1
                            print(f"   🗑️  Removiendo posición cerrada: {symbol}")
                        else:
                            positions_to_keep[symbol] = pos
                    
                    if closed_count > 0:
                        # Crear backup
                        backup_file(filepath)
                        
                        # Guardar solo posiciones abiertas
                        with open(filepath, 'w') as f:
                            json.dump(positions_to_keep, f, indent=2)
                        print(f"   ✅ {closed_count} posiciones cerradas removidas")
                        print(f"   ✅ {len(positions_to_keep)} posiciones abiertas mantenidas")
                    else:
                        print(f"   ℹ️  No hay posiciones cerradas para remover")
            
        except json.JSONDecodeError as e:
            print(f"   ❌ JSON corrupto detectado: {e}")
            
            # Crear backup del archivo corrupto
            backup_file(filepath)
            
            # Crear archivo limpio
            if filename == "open_positions.json":
                clean_data = {}
            elif filename == "bot_status.json":
                clean_data = {
                    "running": False,
                    "last_update": datetime.now().isoformat()
                }
            else:
                clean_data = {}
            
            try:
                with open(filepath, 'w') as f:
                    json.dump(clean_data, f, indent=2)
                print(f"   ✅ Archivo limpio creado")
            except Exception as e2:
                print(f"   ❌ Error creando archivo limpio: {e2}")
    
    # Limpiar archivos .corrupto antiguos
    print(f"\n🗑️  Limpiando archivos .corrupto antiguos...")
    corrupto_count = 0
    for filename in os.listdir(data_dir):
        if ".corrupto" in filename:
            filepath = os.path.join(data_dir, filename)
            try:
                os.remove(filepath)
                corrupto_count += 1
                print(f"   🗑️  Removido: {filename}")
            except Exception as e:
                print(f"   ❌ Error removiendo {filename}: {e}")
    
    if corrupto_count > 0:
        print(f"   ✅ {corrupto_count} archivos corruptos removidos")
    else:
        print(f"   ℹ️  No hay archivos .corrupto para remover")
    
    print("\n" + "=" * 60)
    print("✅ Limpieza completada")
    print("\nAhora puedes reiniciar el bot:")
    print("   docker-compose restart crypto-bot")

if __name__ == "__main__":
    # Verificar que estamos en el directorio correcto
    if not os.path.exists("data"):
        print("❌ Directorio 'data' no encontrado")
        print("   Asegúrate de ejecutar este script desde el directorio del bot")
        exit(1)
    
    cleanup_corrupted_files()

