"""Arreglar el constraint chk_login"""
import sys
sys.path.insert(0, '/run/media/arch/Storage/SENA/Proyecto-Formativo/Acadify/backend')

from src.db.session import SessionLocal
from sqlalchemy import text

db = SessionLocal()

try:
    # 1. Eliminar el constraint viejo
    print("1. Eliminando constraint viejo...")
    db.execute(text('ALTER TABLE "Usuario" DROP CONSTRAINT IF EXISTS chk_login'))
    db.commit()
    print("✓ Constraint viejo eliminado")
    
    # 2. Crear el constraint correcto
    print("\n2. Creando constraint correcto...")
    constraint_sql = """
    ALTER TABLE "Usuario" ADD CONSTRAINT chk_login CHECK (
        (rol = 'administrador' AND username IS NOT NULL AND correo_institucional IS NULL) 
        OR 
        (rol <> 'administrador' AND correo_institucional IS NOT NULL AND username IS NULL)
    )
    """
    db.execute(text(constraint_sql))
    db.commit()
    print("✓ Constraint correcto creado")
    
    # 3. Verificar
    print("\n3. Verificando constraint...")
    result = db.execute(text("SELECT conname, pg_get_constraintdef(oid) FROM pg_constraint WHERE conname = 'chk_login'"))
    for r in result:
        print(f"Constraint: {r[0]}")
        print(f"Definition: {r[1]}")
    
    print("\n✅ ¡Constraint actualizado exitosamente!")
    
except Exception as e:
    db.rollback()
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
finally:
    db.close()
