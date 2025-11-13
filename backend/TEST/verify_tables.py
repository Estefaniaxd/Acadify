#!/usr/bin/env python3
"""Script para verificar que las tablas periodos_academicos e inscripciones existen."""

from sqlalchemy import text
from src.db.session import engine

def main():
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT table_name, 
                   (SELECT COUNT(*) FROM information_schema.columns 
                    WHERE table_schema = 'public' AND table_name = t.table_name) as column_count
            FROM information_schema.tables t
            WHERE table_schema = 'public' 
            AND table_name IN ('periodos_academicos', 'inscripciones')
            ORDER BY table_name
        """))
        
        tables = list(result)
        
        if tables:
            print("✅ Tablas creadas exitosamente:\n")
            for table_name, col_count in tables:
                print(f"  📋 {table_name}: {col_count} columnas")
        else:
            print("❌ No se encontraron las tablas")

if __name__ == "__main__":
    main()
