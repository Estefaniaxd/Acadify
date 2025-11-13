"""
Script para verificar columnas de examenes/evaluaciones en BD vs modelo
"""
import asyncio
import asyncpg
from sqlalchemy import inspect
import sys
import os

# Añadir el directorio padre al path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.models.evaluaciones.evaluacion_expandida import Evaluacion

async def check_evaluaciones():
    """Compara columnas de Evaluacion modelo vs BD"""
    
    # Usar DATABASE_URL directamente
    database_url = "postgresql://postgres:243019@localhost:5432/acadify_db"
    conn = await asyncpg.connect(database_url)
    
    try:
        # Primero verificar qué tabla existe
        tables = await conn.fetch("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name LIKE '%evaluac%' OR table_name LIKE '%examen%'
            ORDER BY table_name
        """)
        
        print("📋 TABLAS RELACIONADAS CON EVALUACIONES:")
        for t in tables:
            print(f"   - {t['table_name']}")
        
        # Buscar la tabla correcta
        table_name = "evaluaciones"  # Cambiado a evaluaciones
        
        # Obtener columnas de BD
        bd_columns = await conn.fetch(f"""
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns 
            WHERE table_name = '{table_name}'
            ORDER BY ordinal_position
        """)
        
        print(f"\n📦 COLUMNAS EN BASE DE DATOS ({table_name}):")
        print(f"   Total: {len(bd_columns)} columnas\n")
        bd_col_names = set()
        for col in bd_columns:
            nullable = "NULL" if col['is_nullable'] == 'YES' else "NOT NULL"
            print(f"   - {col['column_name']:40} {col['data_type']:25} {nullable}")
            bd_col_names.add(col['column_name'])
        
        # Obtener columnas del modelo
        mapper = inspect(Evaluacion)
        model_columns = {col.key for col in mapper.columns}
        
        print(f"\n🔧 COLUMNAS EN MODELO (Evaluacion):")
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
    asyncio.run(check_evaluaciones())
