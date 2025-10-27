#!/usr/bin/env python3
"""
Script para crear datos de muestra para cursos y grupos
"""
import sys
import os

# Agregar el directorio padre al path para importar módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.db.session import SessionLocal
from src.models.users.usuario import Usuario
from src.models.users.docente import Docente
from src.models.users.coordinador import Coordinador
from src.models.users.estudiante import Estudiante
from src.models.academic.curso import Curso
from src.models.academic.grupo import Grupo
from src.models.academic.institucion import Institucion
from src.models.academic.programa import Programa
from src.enums.academic.curso_enums import ModalidadCurso
from src.enums.academic.institucion_enums import TipoInstitucion, NivelEducativoInstitucion, SectorInstitucion
from src.enums.academic.programa_enums import NivelPrograma, TipoPrograma
from src.enums.academic.grupo_enums import JornadaGrupo
from datetime import date, datetime
from sqlalchemy import text
import uuid

def create_sample_data():
    db = SessionLocal()
    
    try:
        print("=== CREANDO DATOS DE MUESTRA ===\n")
        
        # 1. Verificar si existe institución
        print("1. Verificando instituciones...")
        institucion = db.query(Institucion).first()
        
        if not institucion:
            print("   No hay instituciones. Creando una...")
            institucion = Institucion(
                nombre="Universidad Ejemplo",
                sigla="UE",
                tipo_institucion=TipoInstitucion.universidad,
                usa_programas=True,
                nivel_educativo=NivelEducativoInstitucion.superior,
                sector=SectorInstitucion.publico,
                pais="Colombia",
                correo_institucional="info@universidad-ejemplo.edu.co",
                telefono="123-456-7890",
                estado="activa"
            )
            db.add(institucion)
            db.commit()
            db.refresh(institucion)
            print(f"   ✓ Institución creada: {institucion.nombre}")
        else:
            print(f"   ✓ Institución encontrada: {institucion.nombre}")
        
        # 2. Verificar si existe programa
        print("\n2. Verificando programas...")
        programa = db.query(Programa).first()
        
        if not programa:
            print("   No hay programas. Creando uno...")
            programa = Programa(
                institucion_id=institucion.institucion_id,
                nombre="Ingeniería de Sistemas",
                descripcion="Programa de ingeniería de sistemas",
                nivel=NivelPrograma.profesional,
                tipo=TipoPrograma.presencial
            )
            db.add(programa)
            db.commit()
            db.refresh(programa)
            print(f"   ✓ Programa creado: {programa.nombre}")
        else:
            print(f"   ✓ Programa encontrado: {programa.nombre}")
        
        # 3. Obtener coordinador
        print("\n3. Obteniendo coordinador...")
        coordinador_usuario = db.query(Usuario).filter(Usuario.rol == 'coordinador').first()
        
        if not coordinador_usuario:
            print("   ❌ No hay coordinadores registrados")
            return
            
        coordinador = db.query(Coordinador).filter(Coordinador.coordinador_id == coordinador_usuario.usuario_id).first()
        if not coordinador:
            print("   Creando datos adicionales para el coordinador...")
            coordinador = Coordinador(
                coordinador_id=coordinador_usuario.usuario_id,
                horario_atencion="Lunes a Viernes 8:00-17:00",
                fecha_inicio_carrera=date(2020, 1, 1)
            )
            db.add(coordinador)
            db.commit()
            db.refresh(coordinador)
            
        print(f"   ✓ Coordinador: {coordinador_usuario.nombres} {coordinador_usuario.apellidos}")
        
        # 4. Crear cursos de muestra
        print("\n4. Creando cursos de muestra...")
        
        cursos_data = [
            {
                "nombre": "Matemáticas Avanzadas",
                "codigo_curso": "MAT301",
                "descripcion": "Curso de cálculo diferencial e integral para estudiantes de ingeniería",
                "modalidad": ModalidadCurso.semestral,
                "creditos": 4,
                "horas_academicas": 64,
                "fecha_inicio": date(2024, 1, 15),
                "fecha_fin": date(2024, 6, 15),
                "maximo_estudiantes": 30
            },
            {
                "nombre": "Historia Universal",
                "codigo_curso": "HIS201",
                "descripcion": "Historia desde la antigüedad hasta la era moderna",
                "modalidad": ModalidadCurso.semestral,
                "creditos": 3,
                "horas_academicas": 48,
                "fecha_inicio": date(2024, 1, 15),
                "fecha_fin": date(2024, 6, 15),
                "maximo_estudiantes": 40
            },
            {
                "nombre": "Programación Orientada a Objetos",
                "codigo_curso": "POO301",
                "descripcion": "Fundamentos de programación orientada a objetos usando Java",
                "modalidad": ModalidadCurso.semestral,
                "creditos": 4,
                "horas_academicas": 64,
                "fecha_inicio": date(2024, 1, 15),
                "fecha_fin": date(2024, 6, 15),
                "maximo_estudiantes": 25
            }
        ]
        
        cursos_creados = []
        
        for curso_data in cursos_data:
            # Verificar si el curso ya existe
            curso_existente = db.query(Curso).filter(
                Curso.codigo_curso == curso_data["codigo_curso"],
                Curso.institucion_id == institucion.institucion_id
            ).first()
            
            if curso_existente:
                print(f"   - Curso {curso_data['codigo_curso']} ya existe")
                cursos_creados.append(curso_existente)
                continue
            
            curso = Curso(
                institucion_id=institucion.institucion_id,
                coordinador_id=coordinador.coordinador_id,
                programa_id=programa.programa_id,
                **curso_data
            )
            
            db.add(curso)
            db.commit()
            db.refresh(curso)
            cursos_creados.append(curso)
            
            print(f"   ✓ Curso creado: {curso.nombre} ({curso.codigo_curso})")
        
        # 5. Crear grupos para los cursos
        print("\n5. Creando grupos de muestra...")
        
        grupos_data = [
            {"nombre": "Grupo A - MAT301", "curso_codigo": "MAT301", "descripcion": "Grupo matutino"},
            {"nombre": "Grupo B - MAT301", "curso_codigo": "MAT301", "descripcion": "Grupo vespertino"},
            {"nombre": "Grupo A - HIS201", "curso_codigo": "HIS201", "descripcion": "Grupo virtual principal"},
            {"nombre": "Grupo A - POO301", "curso_codigo": "POO301", "descripcion": "Grupo de programación"}
        ]
        
        for grupo_data in grupos_data:
            # Encontrar el curso correspondiente
            curso = next((c for c in cursos_creados if c.codigo_curso == grupo_data["curso_codigo"]), None)
            
            if not curso:
                continue
            
            # Verificar si el grupo ya existe
            grupo_existente = db.query(Grupo).filter(Grupo.nombre == grupo_data["nombre"]).first()
            
            if grupo_existente:
                print(f"   - Grupo {grupo_data['nombre']} ya existe")
                continue
            
            grupo = Grupo(
                programa_id=programa.programa_id,
                nombre=grupo_data["nombre"],
                jornada=JornadaGrupo.manana
            )
            
            db.add(grupo)
            db.commit()
            db.refresh(grupo)
            
            print(f"   ✓ Grupo creado: {grupo.nombre}")
        
        print("\n=== DATOS DE MUESTRA CREADOS EXITOSAMENTE ===")
        print(f"✓ {len(cursos_creados)} cursos")
        print(f"✓ {len(grupos_data)} grupos")
        
        # Mostrar resumen
        print("\n=== RESUMEN FINAL ===")
        total_cursos = db.query(Curso).count()
        total_grupos = db.query(Grupo).count()
        total_usuarios = db.query(Usuario).count()
        
        print(f"Total en BD: {total_cursos} cursos, {total_grupos} grupos, {total_usuarios} usuarios")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_sample_data()