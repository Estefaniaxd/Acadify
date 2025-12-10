import sys
import os
from pathlib import Path

# Add backend directory to path
backend_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(backend_dir))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from src.core.config import get_settings
from src.models.academic.tarea import EntregaTarea

def fix_submissions():
    settings = get_settings()
    engine = create_engine(settings.get_database_url())
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()

    try:
        print("🔍 Listando TODAS las entregas encontradas:")
        entregas = db.query(EntregaTarea).all()
        
        if not entregas:
            print("❌ No se encontraron entregas en la base de datos.")
        
        for entrega in entregas:
            print(f"📄 Entrega {entrega.entrega_id} | Estudiante: {entrega.estudiante_id} | Tarea: {entrega.tarea_id} | Estado: {entrega.estado}")
            
            # Si el estado es None o vacío, forzar entregada
            if not entrega.estado or entrega.estado == 'borrador':
                print(f"   ⚠️ Corrigiendo estado de '{entrega.estado}' a 'entregada'")
                entrega.estado = 'entregada'
                count += 1
        
        if count > 0:
            db.commit()
            print(f"✅ Se corrigieron {count} entregas.")
        else:
            print("ℹ️ No se requirieron correcciones.")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    fix_submissions()
