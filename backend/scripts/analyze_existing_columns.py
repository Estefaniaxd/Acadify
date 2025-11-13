#!/usr/bin/env python3
"""Analiza las columnas existentes en las tablas de evaluaciones"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import create_engine, text
from src.core.config import settings

engine = create_engine(settings.database_url)

print("=" * 100)
print("ANÁLISIS COMPLETO DE COLUMNAS EXISTENTES - SISTEMA DE EVALUACIONES")
print("=" * 100)
print()

tables_to_analyze = {
    'examenes': 'Tabla principal de evaluaciones',
    'preguntas_examen': 'Tabla de preguntas',
    'intentos_examen': 'Tabla de intentos',
    'respuestas_estudiante': 'Tabla de respuestas',
    'banco_preguntas': 'Banco de preguntas',
    'configuracion_evaluaciones': 'Configuración global',
    'estadisticas_examen': 'Estadísticas',
}

with engine.connect() as conn:
    for table_name, description in tables_to_analyze.items():
        print(f"\n{'='*100}")
        print(f"📊 {table_name.upper()} - {description}")
        print('='*100)
        
        # Verificar si la tabla existe
        table_exists = conn.execute(text(f"""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = '{table_name}'
            )
        """)).scalar()
        
        if not table_exists:
            print(f"❌ Tabla '{table_name}' no existe")
            continue
        
        # Obtener columnas
        result = conn.execute(text(f"""
            SELECT 
                column_name, 
                data_type, 
                is_nullable,
                column_default
            FROM information_schema.columns 
            WHERE table_name = '{table_name}'
            ORDER BY ordinal_position
        """))
        
        columns = list(result)
        print(f"\n✅ Total de columnas: {len(columns)}\n")
        
        for col in columns:
            nullable = "NULL" if col[2] == 'YES' else "NOT NULL"
            default = f" DEFAULT {col[3]}" if col[3] else ""
            print(f"  • {col[0]:<35} {col[1]:<25} {nullable:<10}{default}")

print("\n" + "=" * 100)
print("✅ Análisis completado")
print("=" * 100)

engine.dispose()
