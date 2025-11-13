"""Check audit column names in tienda_item table"""
import asyncio
import asyncpg
from src.core.config import settings

async def check():
    conn = await asyncpg.connect(settings.get_database_url(async_driver=False))
    result = await conn.fetch("""
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name='tienda_item' 
        AND column_name IN ('creado_en', 'actualizado_en', 'fecha_creacion', 'fecha_actualizacion', 'created_at', 'updated_at') 
        ORDER BY column_name
    """)
    print("Columnas de auditoría encontradas en la BD:")
    for r in result:
        print(f"  - {r['column_name']}")
    await conn.close()

if __name__ == "__main__":
    asyncio.run(check())
