"""Script temporal para limpiar enums parcialmente creados"""
from src.db.session import SessionLocal
from sqlalchemy import text

db = SessionLocal()

try:
    print("\n🧹 Limpiando enums parciales...")
    
    db.execute(text('DROP TYPE IF EXISTS categoria_etiqueta_enum CASCADE'))
    db.execute(text('DROP TYPE IF EXISTS rareza_enum CASCADE'))
    db.execute(text('DROP TYPE IF EXISTS categoria_item_enum CASCADE'))
    db.execute(text('DROP TYPE IF EXISTS tipo_item_enum CASCADE'))
    db.execute(text('DROP TYPE IF EXISTS tipo_racha_enum CASCADE'))
    
    db.commit()
    print("✅ Enums limpiados exitosamente\n")
    
except Exception as e:
    print(f"❌ Error: {e}")
    db.rollback()
    
finally:
    db.close()
