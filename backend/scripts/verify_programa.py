#!/usr/bin/env python3
"""Verificar sincronización de Programa"""

import asyncio
import asyncpg
import re
from src.core.config import settings

async def main():
    conn = await asyncpg.connect(settings.get_database_url(async_driver=False))
    
    # BD
    db_cols = await conn.fetch("""
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name = 'Programa' 
        ORDER BY ordinal_position
    """)
    db_names = {row['column_name'] for row in db_cols}
    
    # Modelo
    with open('src/models/academic/programa.py', 'r') as f:
        content = f.read()
    
    model_cols = set()
    in_class = False
    for line in content.split('\n'):
        if 'class Programa(Base)' in line:
            in_class = True
        elif in_class and re.match(r'^class \w+', line):
            break
        elif in_class:
            match = re.match(r'^\s+(\w+)\s*=\s*Column\(', line)
            if match:
                model_cols.add(match.group(1))
    
    missing = model_cols - db_names
    extra = db_names - model_cols
    
    print(f'📋 Programa: BD={len(db_names)} | Modelo={len(model_cols)}')
    if not missing and not extra:
        print('✅ Perfectamente sincronizado')
        print(f'\n🎉 ¡Excelente! Todos los {len(db_names)} campos coinciden')
    else:
        if missing:
            print(f'❌ Faltan en BD ({len(missing)}): {sorted(missing)}')
        if extra:
            print(f'⚠️  Extra en BD ({len(extra)}): {sorted(extra)}')
    
    await conn.close()

if __name__ == "__main__":
    asyncio.run(main())
