#!/usr/bin/env python3
"""
Script para insertar datos de prueba en la base de datos
"""
import sys
import os

# Agregar el directorio raíz al path de Python
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text
from src.db.session import SessionLocal
from datetime import datetime, date, timedelta
import hashlib

def create_test_user():
    """Crear un usuario de prueba"""
    db = SessionLocal()
    try:
        # Verificar si ya existe
        existing_user = db.execute(text("""
            SELECT usuario_id FROM "Usuario" WHERE email = 'test@acadify.com'
        """)).fetchone()
        
        if existing_user:
            print("Usuario test@acadify.com ya existe")
            return existing_user[0]
        
        # Crear hash de la contraseña
        password_hash = hashlib.sha256("test123".encode()).hexdigest()
        
        # Insertar usuario
        result = db.execute(text("""
            INSERT INTO "Usuario" (
                nombres, apellidos, nombre_completo, email, 
                correo_institucional, username, password_hash, 
                tipo_documento, numero_documento, telefono, 
                fecha_nacimiento, genero, rol, estado, fecha_creacion
            ) VALUES (
                'Usuario', 'Test', 'Usuario Test', 'test@acadify.com',
                'test@acadify.com', 'test_user', :password_hash,
                'cedula', '12345678', '1234567890',
                '1990-01-01', 'masculino', 'estudiante', 'activo', CURRENT_TIMESTAMP
            ) RETURNING usuario_id
        """), {"password_hash": password_hash})
        
        user_id = result.fetchone()[0]
        db.commit()
        print(f"Usuario test@acadify.com creado con ID: {user_id}")
        return user_id
        
    except Exception as e:
        print(f"Error creando usuario: {e}")
        db.rollback()
        return None
    finally:
        db.close()

def create_test_courses():
    """Crear cursos de prueba con fechas realistas"""
    db = SessionLocal()
    try:
        # Fechas para diferentes estados de cursos
        hoy = date.today()
        
        cursos_test = [
            {
                "nombre": "Matemáticas Avanzadas",
                "descripcion": "Curso avanzado de cálculo diferencial e integral",
                "codigo_acceso": "MAT001",
                "modalidad": "Presencial",
                "fecha_inicio": hoy - timedelta(days=30),  # Comenzó hace un mes (activo)
                "fecha_fin": hoy + timedelta(days=60),     # Termina en 2 meses
                "estado": "activo",
                "creditos": 4
            },
            {
                "nombre": "Programación Orientada a Objetos", 
                "descripcion": "Fundamentos de POO con Java y Python",
                "codigo_acceso": "POO002",
                "modalidad": "Virtual",
                "fecha_inicio": hoy + timedelta(days=15),  # Comienza en 15 días (próximo)
                "fecha_fin": hoy + timedelta(days=120),    # Termina en 4 meses
                "estado": "próximo",
                "creditos": 3
            },
            {
                "nombre": "Base de Datos I",
                "descripcion": "Diseño y administración de bases de datos relacionales",
                "codigo_acceso": "BD003",
                "modalidad": "Híbrida",
                "fecha_inicio": hoy - timedelta(days=90),  # Comenzó hace 3 meses
                "fecha_fin": hoy - timedelta(days=10),     # Terminó hace 10 días (completado)
                "estado": "completado", 
                "creditos": 3
            }
        ]
        
        curso_ids = []
        for curso in cursos_test:
            # Verificar si ya existe
            existing = db.execute(text("""
                SELECT curso_id FROM "Curso" WHERE codigo_acceso = :codigo
            """), {"codigo": curso["codigo_acceso"]}).fetchone()
            
            if existing:
                print(f"Curso {curso['codigo_acceso']} ya existe")
                curso_ids.append(existing[0])
                continue
            
            # Insertar curso
            result = db.execute(text("""
                INSERT INTO "Curso" (
                    nombre, descripcion, codigo_acceso, modalidad,
                    fecha_inicio, fecha_fin, estado, creditos,
                    fecha_creacion, horas_academicas
                ) VALUES (
                    :nombre, :descripcion, :codigo_acceso, :modalidad,
                    :fecha_inicio, :fecha_fin, :estado, :creditos,
                    CURRENT_TIMESTAMP, 48
                ) RETURNING curso_id
            """), curso)
            
            curso_id = result.fetchone()[0]
            curso_ids.append(curso_id)
            print(f"Curso {curso['codigo_acceso']} creado con ID: {curso_id}")
        
        db.commit()
        return curso_ids
        
    except Exception as e:
        print(f"Error creando cursos: {e}")
        db.rollback()
        return []
    finally:
        db.close()

def create_groups_and_enrollments(user_id, curso_ids):
    """Crear grupos e inscribir al usuario"""
    db = SessionLocal()
    try:
        for i, curso_id in enumerate(curso_ids):
            # Crear grupo para el curso
            result = db.execute(text("""
                INSERT INTO "Grupo" (nombre, descripcion, estado, fecha_creacion)
                VALUES (:nombre, :descripcion, 'activo', CURRENT_TIMESTAMP)
                RETURNING grupo_id
            """), {
                "nombre": f"Grupo A - Curso {curso_id}",
                "descripcion": f"Grupo principal para el curso {curso_id}"
            })
            
            grupo_id = result.fetchone()[0]
            
            # Vincular grupo con curso
            db.execute(text("""
                INSERT INTO "GrupoCurso" (grupo_id, curso_id, fecha_asignacion)
                VALUES (:grupo_id, :curso_id, CURRENT_DATE)
            """), {"grupo_id": grupo_id, "curso_id": curso_id})
            
            # Solo inscribir al usuario en los primeros 2 cursos
            if i < 2:
                # Inscribir usuario en el grupo
                db.execute(text("""
                    INSERT INTO "EstudianteGrupo" (grupo_id, estudiante_id, fecha_vinculacion)
                    VALUES (:grupo_id, :estudiante_id, CURRENT_DATE)
                """), {"grupo_id": grupo_id, "estudiante_id": user_id})
                
                print(f"Usuario {user_id} inscrito en grupo {grupo_id} del curso {curso_id}")
            
            # Inscribir algunos estudiantes ficticios para tener conteos reales
            for j in range(3):  # 3 estudiantes adicionales por grupo
                try:
                    db.execute(text("""
                        INSERT INTO "EstudianteGrupo" (grupo_id, estudiante_id, fecha_vinculacion)
                        VALUES (:grupo_id, :estudiante_id, CURRENT_DATE)
                    """), {"grupo_id": grupo_id, "estudiante_id": user_id + j + 1})
                except:
                    # Si el estudiante no existe, crear uno ficticio
                    db.execute(text("""
                        INSERT INTO "Usuario" (
                            nombres, apellidos, nombre_completo, email,
                            correo_institucional, username, password_hash,
                            tipo_documento, numero_documento, telefono,
                            fecha_nacimiento, genero, rol, estado, fecha_creacion
                        ) VALUES (
                            :nombres, :apellidos, :nombre_completo, :email,
                            :email, :username, 'dummy_hash',
                            'cedula', :documento, '0000000000',
                            '1995-01-01', 'otro', 'estudiante', 'activo', CURRENT_TIMESTAMP
                        )
                    """), {
                        "nombres": f"Estudiante{j+1}",
                        "apellidos": f"Test{j+1}",
                        "nombre_completo": f"Estudiante{j+1} Test{j+1}",
                        "email": f"estudiante{j+1}_{curso_id}@test.com",
                        "username": f"estudiante{j+1}_{curso_id}",
                        "documento": f"1234567{j+1}"
                    })
                    
                    # Obtener el ID del usuario recién creado
                    user_result = db.execute(text("""
                        SELECT usuario_id FROM "Usuario" WHERE email = :email
                    """), {"email": f"estudiante{j+1}_{curso_id}@test.com"})
                    
                    new_user_id = user_result.fetchone()[0]
                    
                    # Inscribir al nuevo usuario
                    db.execute(text("""
                        INSERT INTO "EstudianteGrupo" (grupo_id, estudiante_id, fecha_vinculacion)
                        VALUES (:grupo_id, :estudiante_id, CURRENT_DATE)
                    """), {"grupo_id": grupo_id, "estudiante_id": new_user_id})
        
        db.commit()
        print("Grupos e inscripciones creados exitosamente")
        
    except Exception as e:
        print(f"Error creando grupos e inscripciones: {e}")
        db.rollback()
    finally:
        db.close()

def main():
    print("🔄 Insertando datos de prueba...")
    
    # Crear usuario de prueba
    user_id = create_test_user()
    if not user_id:
        print("❌ Error creando usuario de prueba")
        return
    
    # Crear cursos de prueba
    curso_ids = create_test_courses()
    if not curso_ids:
        print("❌ Error creando cursos de prueba")
        return
    
    # Crear grupos e inscripciones
    create_groups_and_enrollments(user_id, curso_ids)
    
    print("✅ Datos de prueba insertados exitosamente")
    print("\nCredenciales de prueba:")
    print("Email: test@acadify.com")
    print("Password: test123")
    print("\nCódigos de cursos:")
    print("MAT001 - Matemáticas Avanzadas (activo)")
    print("POO002 - Programación Orientada a Objetos (próximo)")
    print("BD003 - Base de Datos I (completado)")

if __name__ == "__main__":
    main()