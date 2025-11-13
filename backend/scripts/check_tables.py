#!/usr/bin/env python3
"""Quick script to check evaluation tables"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import create_engine, text
from src.core.config import settings

engine = create_engine(settings.database_url)

print("=" * 80)
print("TABLAS DEL SISTEMA DE EVALUACIONES EN LA BASE DE DATOS")
print("=" * 80)
print()

with engine.connect() as conn:
    # Buscar tablas relacionadas con evaluaciones
    result = conn.execute(text("""
        SELECT tablename 
        FROM pg_tables 
        WHERE schemaname='public' 
        AND (
            tablename LIKE '%eval%' OR 
            tablename LIKE '%examen%' OR 
            tablename LIKE '%pregunta%' OR 
            tablename LIKE '%intento%' OR
            tablename LIKE '%respuesta%' OR
            tablename LIKE '%configuracion%' OR
            tablename LIKE '%estadistica%'
        )
        ORDER BY tablename
    """))
    
    tables = [row[0] for row in result]
    
    if not tables:
        print("❌ No se encontraron tablas del sistema de evaluaciones")
    else:
        print(f"✅ Se encontraron {len(tables)} tablas:\n")
        for table in tables:
            print(f"  - {table}")
            
            # Contar registros
            count_result = conn.execute(text(f"SELECT COUNT(*) FROM {table}"))
            count = count_result.scalar()
            print(f"    └─ Registros: {count}")
            
            # Si es una tabla principal, mostrar algunas columnas
            if table in ['evaluaciones', 'examenes', 'preguntas_evaluacion', 'preguntas_examen']:
                cols_result = conn.execute(text(f"""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name = '{table}' 
                    ORDER BY ordinal_position 
                    LIMIT 10
                """))
                cols = [col[0] for col in cols_result]
                print(f"    └─ Primeras columnas: {', '.join(cols)}")
            print()

engine.dispose()
print("=" * 80)
