"""
Script para crear manualmente la tabla invitation_tokens
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.db.session import SessionLocal
from sqlalchemy import text

def crear_tabla_invitation_tokens():
    db = SessionLocal()
    
    try:
        print("Creando tabla invitation_tokens...")
        
        # Primero, crear el enum si no existe
        db.execute(text("""
            DO $$ BEGIN
                CREATE TYPE estado_invitacion AS ENUM ('pendiente', 'usado', 'expirado');
            EXCEPTION
                WHEN duplicate_object THEN null;
            END $$;
        """))
        
        # Crear la tabla
        db.execute(text("""
            CREATE TABLE IF NOT EXISTS invitation_tokens (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                codigo VARCHAR(6) NOT NULL UNIQUE,
                email_destino VARCHAR(100) NOT NULL,
                institucion_id UUID NOT NULL REFERENCES "Institucion"(institucion_id) ON DELETE CASCADE,
                estado estado_invitacion NOT NULL DEFAULT 'pendiente',
                fecha_creacion TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
                fecha_expiracion TIMESTAMP WITH TIME ZONE NOT NULL,
                coordinador_id UUID REFERENCES "Usuario"(usuario_id) ON DELETE SET NULL,
                usado_en TIMESTAMP WITH TIME ZONE
            );
        """))
        
        # Crear índice en codigo
        db.execute(text("""
            CREATE UNIQUE INDEX IF NOT EXISTS ix_invitation_tokens_codigo 
            ON invitation_tokens(codigo);
        """))
        
        # Crear índice en id
        db.execute(text("""
            CREATE INDEX IF NOT EXISTS ix_invitation_tokens_id 
            ON invitation_tokens(id);
        """))
        
        db.commit()
        print("✓ Tabla invitation_tokens creada exitosamente!")
        
        # Verificar
        result = db.execute(text("SELECT COUNT(*) FROM invitation_tokens;"))
        count = result.scalar()
        print(f"✓ Tabla verificada. Registros actuales: {count}")
        
    except Exception as e:
        db.rollback()
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    crear_tabla_invitation_tokens()
