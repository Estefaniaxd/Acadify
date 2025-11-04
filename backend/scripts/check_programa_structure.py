#!/usr/bin/env python3
"""Verificar estructura de la tabla Programa"""

import asyncio
import asyncpg
from src.core.config import settings

async def main():
    conn = await asyncpg.connect(settings.get_database_url(async_driver=False))
    
    cols = await conn.fetch("""
        SELECT column_name, data_type, udt_name, is_nullable, column_default
        FROM information_schema.columns
        WHERE table_name = 'Programa'
        ORDER BY ordinal_position
    """)
    
    print(f'📋 Tabla Programa ({len(cols)} columnas):\n')
    
    for i, col in enumerate(cols, 1):
        nullable = 'NULL' if col['is_nullable'] == 'YES' else 'NOT NULL'
        default = f" DEFAULT {col['column_default']}" if col['column_default'] else ''
        tipo = col['udt_name'] if col['data_type'] == 'USER-DEFINED' else col['data_type']
        print(f"{i:2}. {col['column_name']:40} {tipo:25} {nullable:10}{default}")
    
    await conn.close()

if __name__ == "__main__":
    asyncio.run(main())
