"""
Script para verificar columnas de tareas en BD vs modelo
"""
import asyncio
import asyncpg
from sqlalchemy import inspect
import sys
import os

# Añadir el directorio padre al path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.models.academic.tarea import Tarea

async def check_tareas():
    """Compara columnas de Tarea modelo vs BD"""
    
    # Usar DATABASE_URL directamente
    database_url = "postgresql://postgres:243019@localhost:5432/acadify_db"
    conn = await asyncpg.connect(database_url)
    
    try:
        # Obtener columnas de BD
        bd_columns = await conn.fetch("""
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns 
            WHERE table_name = 'tareas'
            ORDER BY ordinal_position
        """)
        
        print("📦 COLUMNAS EN BASE DE DATOS (tareas):")
        print(f"   Total: {len(bd_columns)} columnas\n")
        bd_col_names = set()
        for col in bd_columns:
            nullable = "NULL" if col['is_nullable'] == 'YES' else "NOT NULL"
            print(f"   - {col['column_name']:35} {col['data_type']:25} {nullable}")
            bd_col_names.add(col['column_name'])
        
        # Obtener columnas del modelo
        mapper = inspect(Tarea)
        model_columns = {col.key for col in mapper.columns}
        
        print(f"\n🔧 COLUMNAS EN MODELO (Tarea):")
        print(f"   Total: {len(model_columns)} columnas\n")
        for col in sorted(model_columns):
            print(f"   - {col}")
        
        # Comparar
        faltan_en_bd = model_columns - bd_col_names
        faltan_en_modelo = bd_col_names - model_columns
        
        print(f"\n📊 ANÁLISIS:")
        print(f"   📦 BD: {len(bd_col_names)} columnas")
        print(f"   🔧 Modelo: {len(model_columns)} columnas")
        
        if faltan_en_bd:
            print(f"\n   ❌ Faltan en BD (están en modelo): {len(faltan_en_bd)}")
            for col in sorted(faltan_en_bd):
                print(f"      - {col}")
        
        if faltan_en_modelo:
            print(f"\n   ⚠️  Faltan en modelo (están en BD): {len(faltan_en_modelo)}")
            for col in sorted(faltan_en_modelo):
                print(f"      - {col}")
        
        if not faltan_en_bd and not faltan_en_modelo:
            print(f"\n   ✅ PERFECTO - Todas las columnas coinciden!")
        
    finally:
        await conn.close()

if __name__ == "__main__":
    asyncio.run(check_tareas())
