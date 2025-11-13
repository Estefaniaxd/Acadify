"""
Script para limpiar usuarios y hacer que cumplan con el constraint correcto.

Estrategia:
- Administradores: mantener username, eliminar correo_institucional
- Otros (coordinador, docente, estudiante): mantener correo_institucional, eliminar username
"""
import sys
from pathlib import Path

# Configurar PYTHONPATH
backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))

from sqlalchemy import create_engine, text
from src.core.config import settings

def clean_usuarios():
    """Limpia los campos de Usuario para que cumplan el constraint."""
    engine = create_engine(settings.SQLALCHEMY_DATABASE_URL)
    
    with engine.connect() as conn:
        print("🔧 Limpiando usuarios...")
        
        # 1. Para administradores: mantener username, eliminar correo_institucional
        result1 = conn.execute(text("""
            UPDATE "Usuario"
            SET correo_institucional = NULL
            WHERE rol = 'administrador' AND correo_institucional IS NOT NULL
        """))
        conn.commit()
        print(f"✅ Limpiados {result1.rowcount} administradores (correo → NULL)")
        
        # 2. Para NO administradores: mantener correo_institucional, eliminar username
        result2 = conn.execute(text("""
            UPDATE "Usuario"
            SET username = NULL
            WHERE rol <> 'administrador' AND username IS NOT NULL
        """))
        conn.commit()
        print(f"✅ Limpiados {result2.rowcount} no-administradores (username → NULL)")
        
        # 3. Verificar que ahora todos cumplen el constraint
        result_check = conn.execute(text("""
            SELECT COUNT(*) as violaciones
            FROM "Usuario"
            WHERE NOT (
                (rol = 'administrador' AND username IS NOT NULL AND correo_institucional IS NULL) 
                OR 
                (rol <> 'administrador' AND correo_institucional IS NOT NULL AND username IS NULL)
            )
        """))
        violaciones = result_check.fetchone()[0]
        
        if violaciones == 0:
            print(f"\n✅ ¡PERFECTO! Todos los usuarios ahora cumplen el constraint.")
        else:
            print(f"\n⚠️  Aún hay {violaciones} usuarios violando el constraint.")
            
            # Mostrar cuáles siguen violando
            result_details = conn.execute(text("""
                SELECT usuario_id, rol, username, correo_institucional
                FROM "Usuario"
                WHERE NOT (
                    (rol = 'administrador' AND username IS NOT NULL AND correo_institucional IS NULL) 
                    OR 
                    (rol <> 'administrador' AND correo_institucional IS NOT NULL AND username IS NULL)
                )
                LIMIT 10
            """))
            print("\nPrimeros 10 usuarios que aún violan:")
            for row in result_details:
                print(f"  Rol: {row[1]}, username: {row[2]}, correo: {row[3]}")

if __name__ == "__main__":
    try:
        clean_usuarios()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
