"""
Script para limpiar tablas de videollamadas parcialmente creadas
"""
import sys
import os
from pathlib import Path

# Añadir el directorio backend al path
backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))

from sqlalchemy import create_engine, text
from src.core.config import settings

def cleanup_videollamadas_tables():
    """Limpia tablas y objetos relacionados con videollamadas"""
    engine = create_engine(settings.database_url)
    
    with engine.connect() as conn:
        # Usar transacción para rollback si algo falla
        trans = conn.begin()
        try:
            # Eliminar tablas si existen (en orden inverso por foreign keys)
            tables_to_drop = [
                'videollamada_grabaciones',
                'videollamada_participantes',
                'videollamadas'
            ]
            
            for table in tables_to_drop:
                print(f"🗑️  Intentando eliminar tabla {table}...")
                conn.execute(text(f"DROP TABLE IF EXISTS {table} CASCADE"))
                print(f"✅ Tabla {table} eliminada (o no existía)")
            
            # Eliminar índices si existen (por si quedaron huérfanos)
            indices_to_drop = [
                'idx_videollamadas_sala_chat',
                'idx_videollamadas_iniciador',
                'idx_videollamadas_estado',
                'idx_videollamadas_fecha_inicio',
                'idx_videollamadas_deleted_at',
                'idx_participantes_videollamada',
                'idx_participantes_usuario',
                'idx_participantes_fecha_union',
                'idx_grabaciones_videollamada',
                'idx_grabaciones_estado',
                'idx_grabaciones_deleted_at'
            ]
            
            for index in indices_to_drop:
                try:
                    print(f"🗑️  Intentando eliminar índice {index}...")
                    conn.execute(text(f"DROP INDEX IF EXISTS {index} CASCADE"))
                    print(f"✅ Índice {index} eliminado (o no existía)")
                except Exception as e:
                    print(f"⚠️  No se pudo eliminar índice {index}: {e}")
            
            # Commit de la transacción
            trans.commit()
            print("\n✅ Limpieza completada exitosamente!")
            
        except Exception as e:
            trans.rollback()
            print(f"\n❌ Error durante la limpieza: {e}")
            raise

if __name__ == "__main__":
    print("🧹 Iniciando limpieza de tablas videollamadas...\n")
    cleanup_videollamadas_tables()
    print("\n✨ Listo para aplicar migración limpia!")
