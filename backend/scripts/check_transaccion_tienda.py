"""
Análisis de TransaccionTienda
"""
import asyncio
import asyncpg
from src.core.config import settings
from sqlalchemy import inspect
from src.models.gamification.transaccion_tienda import TransaccionTienda


async def main():
    print("\n🔍 Análisis: TransaccionTienda")
    print("="*70)
    
    db_url = settings.get_database_url(async_driver=False)
    conn = await asyncpg.connect(db_url)
    
    try:
        # Columnas de BD
        bd_columns = await conn.fetch("""
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns
            WHERE table_name = 'transaccion_tienda'
            ORDER BY ordinal_position
        """)
        
        # Columnas del modelo
        mapper = inspect(TransaccionTienda)
        model_columns = {col.key for col in mapper.columns}
        
        bd_column_names = {col['column_name'] for col in bd_columns}
        
        solo_bd = bd_column_names - model_columns
        solo_modelo = model_columns - bd_column_names
        
        print(f"\n📦 BD: {len(bd_column_names)} columnas")
        print(f"📦 Modelo: {len(model_columns)} columnas\n")
        
        if solo_bd:
            print("❌ Faltan en modelo:")
            for col in sorted(solo_bd):
                info = next(c for c in bd_columns if c['column_name'] == col)
                print(f"   - {col:30} ({info['data_type']})")
        
        if solo_modelo:
            print("\n⚠️  Sobran en modelo:")
            for col in sorted(solo_modelo):
                print(f"   - {col}")
        
        if not solo_bd and not solo_modelo:
            print("✅ ¡PERFECTO!")
        
    finally:
        await conn.close()


if __name__ == "__main__":
    asyncio.run(main())
