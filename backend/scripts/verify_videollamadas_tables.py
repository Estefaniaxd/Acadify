"""
Script para verificar que las tablas de videollamadas se crearon correctamente
"""
import sys
import os
from pathlib import Path

# Añadir el directorio backend al path
backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))

from sqlalchemy import create_engine, text, inspect
from src.core.config import settings

def verify_videollamadas_tables():
    """Verifica que las tablas de videollamadas existen"""
    engine = create_engine(settings.database_url)
    inspector = inspect(engine)
    
    print("🔍 Verificando tablas de videollamadas...\n")
    
    expected_tables = [
        'videollamadas',
        'videollamada_participantes',
        'videollamada_grabaciones'
    ]
    
    all_tables = inspector.get_table_names()
    
    for table_name in expected_tables:
        if table_name in all_tables:
            print(f"✅ Tabla '{table_name}' encontrada")
            
            # Obtener columnas
            columns = inspector.get_columns(table_name)
            print(f"   📋 Columnas ({len(columns)}):")
            for col in columns:
                col_type = str(col['type'])
                nullable = "NULL" if col['nullable'] else "NOT NULL"
                print(f"      - {col['name']}: {col_type} ({nullable})")
            
            # Obtener índices
            indexes = inspector.get_indexes(table_name)
            if indexes:
                print(f"   🔗 Índices ({len(indexes)}):")
                for idx in indexes:
                    print(f"      - {idx['name']}: {idx['column_names']}")
            
            # Obtener foreign keys
            fks = inspector.get_foreign_keys(table_name)
            if fks:
                print(f"   🔑 Foreign Keys ({len(fks)}):")
                for fk in fks:
                    print(f"      - {fk['name']}: {fk['constrained_columns']} -> {fk['referred_table']}.{fk['referred_columns']}")
            
            print()
        else:
            print(f"❌ Tabla '{table_name}' NO encontrada")
    
    # Verificar el estado de Alembic
    with engine.connect() as conn:
        result = conn.execute(text("SELECT version_num FROM alembic_version"))
        current_version = result.scalar()
        print(f"📌 Versión actual de Alembic: {current_version}")
    
    print("\n✅ Verificación completada!")

if __name__ == "__main__":
    verify_videollamadas_tables()
