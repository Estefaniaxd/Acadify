"""
Script para eliminar el CheckConstraint incorrecto de la tabla Usuario.

El constraint actual requiere que administradores tengan solo username
y no-administradores tengan solo correo_institucional, pero esto es incorrecto.

TODOS los usuarios deben tener ambos campos para recuperación de contraseña.
La diferencia está en cómo inician sesión, no en qué campos tienen.
"""

from sqlalchemy import text
from src.db.session import SessionLocal

def fix_constraint():
    db = SessionLocal()
    
    try:
        print("🔧 Eliminando constraint incorrecto chk_login...")
        
        # Eliminar el constraint que está mal
        db.execute(text("""
            ALTER TABLE "Usuario" 
            DROP CONSTRAINT IF EXISTS chk_login;
        """))
        
        db.commit()
        print("✅ Constraint eliminado exitosamente!")
        print("")
        print("ℹ️  Ahora TODOS los usuarios pueden tener username Y correo_institucional.")
        print("ℹ️  La diferencia está en el login:")
        print("   - Administradores: login con username")
        print("   - Coordinador/Docente/Estudiante: login con correo_institucional")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    fix_constraint()
