"""
Script para agregar código de acceso a los cursos
"""
from src.db.session import SessionLocal
from sqlalchemy import text
import random
import string

def generate_course_code():
    """Genera un código de curso único de 6 caracteres alfanuméricos"""
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

def add_codigo_acceso_column():
    db = SessionLocal()
    try:
        # Agregar la columna codigo_acceso
        print("Agregando columna codigo_acceso a la tabla Curso...")
        db.execute(text('ALTER TABLE "Curso" ADD COLUMN codigo_acceso VARCHAR(10)'))
        
        # Crear un índice único para el código de acceso
        print("Creando índice único para codigo_acceso...")
        db.execute(text('CREATE UNIQUE INDEX idx_curso_codigo_acceso ON "Curso"(codigo_acceso)'))
        
        # Generar códigos únicos para los cursos existentes
        print("Generando códigos para cursos existentes...")
        cursos = db.execute(text('SELECT curso_id, nombre FROM "Curso"')).fetchall()
        
        for curso in cursos:
            # Generar código único
            while True:
                codigo = generate_course_code()
                # Verificar que no exista
                existing = db.execute(text('SELECT 1 FROM "Curso" WHERE codigo_acceso = :codigo'), 
                                    {"codigo": codigo}).fetchone()
                if not existing:
                    break
            
            # Actualizar el curso con el código
            db.execute(text('UPDATE "Curso" SET codigo_acceso = :codigo WHERE curso_id = :curso_id'),
                      {"codigo": codigo, "curso_id": curso[0]})
            print(f"- {curso[1]}: {codigo}")
        
        db.commit()
        print("✅ Migración completada exitosamente!")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error en migración: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    add_codigo_acceso_column()