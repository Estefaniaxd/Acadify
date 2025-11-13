import asyncio
import asyncpg
from src.core.config import settings

async def check():
    conn = await asyncpg.connect(settings.get_database_url(async_driver=False))
    cols = await conn.fetch("""
        SELECT column_name, data_type 
        FROM information_schema.columns 
        WHERE table_name='usuario_etiqueta' 
        ORDER BY ordinal_position
    """)
    print('\nColumnas en BD usuario_etiqueta:')
    for r in cols:
        print(f'  {r["column_name"]:30} ({r["data_type"]})')
    await conn.close()

asyncio.run(check())
