#!/usr/bin/env python3
"""
Script para crear un ecosistema académico completo de prueba
Crea: Instituciones, Cursos, Usuarios (docentes y estudiantes), Inscripciones, Tareas, etc.
"""
import sys
import os
from pathlib import Path
from datetime import datetime, timedelta
import random

# Add backend directory to Python path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from sqlalchemy.orm import Session
from src.db.session import SessionLocal
from src.models.users.usuario import Usuario
from src.models.academic.institucion import Institucion
from src.models.academic.curso import Curso
from src.models.academic.programa import Programa  # Add Programa import
from src.enums.users.usuario_enums import RolUsuario, TipoDocumentoUsuario, EstadoCuentaUsuario
from src.utils.security import SecurityManager

# Initialize security manager
security_manager = SecurityManager()

# Constants
NUM_INSTITUCIONES = 3
NUM_CURSOS_POR_INSTITUCION = 5
NUM_DOCENTES_POR_INSTITUCION = 4
NUM_ESTUDIANTES_POR_INSTITUCION = 20


def create_instituciones(db: Session):
    """Crear instituciones de prueba"""
    print("\n" + "="*70)
    print("📚 CREANDO INSTITUCIONES")
    print("="*70)
    
    instituciones = []
    nombres = [
        "SENA Centro Tecnológico",
        "Instituto Técnico Nacional",
        "Centro de Formación Empresarial"
    ]
    
    for i, nombre in enumerate(nombres, 1):
        # Check if exists
        existing = db.query(Institucion).filter(Institucion.nombre == nombre).first()
        if existing:
            print(f"✓ Institución ya existe: {existing.nombre} (ID: {existing.institucion_id})")
            instituciones.append(existing)
            continue
        
        institucion = Institucion(
            nombre=nombre,
            sigla=f"INST{i}",
            lema="Formación de calidad para el futuro",
            tipo_institucion="centro_de_formacion",  # Valid enum value
            usa_programas=False,  # Set to False to avoid programa_id requirement
            nivel_educativo="superior",  # Valid enum value
            sector="publico",  # Valid enum value
            correo_institucional=f"institucion{i}@acadify.test",
            telefono=f"300100000{i}",
            direccion=f"Calle {i} #10-20",
            ciudad="Bogotá",
            pais="Colombia",
            nit=f"90010000{i}-1",
            dominio=f"inst{i}.acadify.test",
            estado="activa"  # Valid enum value
        )
        
        db.add(institucion)
        db.flush()
        instituciones.append(institucion)
        print(f"✓ Institución creada: {institucion.nombre} (ID: {institucion.institucion_id})")
    
    db.commit()
    print(f"\n✅ Total instituciones: {len(instituciones)}")
    return instituciones


def create_programas(db: Session, instituciones):
    """Crear un programa por cada institución"""
    print("\n" + "="*70)
    print("📚 CREANDO PROGRAMAS")
    print("="*70)
    
    programas_por_institucion = {}
    
    for institucion in instituciones:
        inst_code = institucion.sigla[-3:]
        nombre = f"Programa Técnico {inst_code}"
        
        # Check if exists
        existing = db.query(Programa).filter(
            Programa.institucion_id == institucion.institucion_id,
            Programa.nombre == nombre
        ).first()
        if existing:
            print(f"✓ Programa ya existe: {existing.nombre} (ID: {existing.programa_id})")
            programas_por_institucion[institucion.institucion_id] = existing
            continue
        
        programa = Programa(
            institucion_id=institucion.institucion_id,
            nombre=nombre,
            descripcion=f"Programa técnico para testing - {institucion.nombre}",
            nivel="tecnico",  # Valid enum value
            tipo="presencial"  # Valid enum value
        )
        
        db.add(programa)
        db.flush()
        programas_por_institucion[institucion.institucion_id] = programa
        print(f"✓ Programa creado: {programa.nombre} (ID: {programa.programa_id})")
    
    db.commit()
    print(f"\n✅ Total programas: {len(programas_por_institucion)}")
    return programas_por_institucion


def create_docentes(db: Session, instituciones):
    """Crear docentes de prueba para cada institución"""
    print("\n" + "="*70)
    print("👨‍🏫 CREANDO DOCENTES")
    print("="*70)
    
    docentes_por_institucion = {}
    
    for institucion in instituciones:
        docentes = []
        inst_code = institucion.sigla[-3:]  # Use sigla instead of codigo
        
        for i in range(1, NUM_DOCENTES_POR_INSTITUCION + 1):
            email = f"docente{inst_code}_{i}@acadify.test"
            
            # Check if exists
            existing = db.query(Usuario).filter(Usuario.correo_institucional == email).first()
            if existing:
                print(f"✓ Docente ya existe: {existing.correo_institucional}")
                docentes.append(existing)
                continue
            
            docente = Usuario(
                nombres=f"Docente{i}",
                apellidos=f"Inst{inst_code}",
                correo_institucional=email,
                username=None,
                password_hash=security_manager.get_password_hash("docente123"),
                tipo_documento=TipoDocumentoUsuario.cc,
                numero_documento=f"100{inst_code}{i:04d}",
                rol=RolUsuario.docente,
                estado_cuenta=EstadoCuentaUsuario.activo
            )
            
            db.add(docente)
            db.flush()
            docentes.append(docente)
            print(f"✓ Docente creado: {docente.correo_institucional} (ID: {docente.usuario_id})")
        
        docentes_por_institucion[institucion.institucion_id] = docentes
    
    db.commit()
    total = sum(len(d) for d in docentes_por_institucion.values())
    print(f"\n✅ Total docentes: {total}")
    return docentes_por_institucion


def create_estudiantes(db: Session, instituciones):
    """Crear estudiantes de prueba para cada institución"""
    print("\n" + "="*70)
    print("👨‍🎓 CREANDO ESTUDIANTES")
    print("="*70)
    
    estudiantes_por_institucion = {}
    
    for institucion in instituciones:
        estudiantes = []
        inst_code = institucion.sigla[-3:]  # Use sigla instead of codigo
        
        for i in range(1, NUM_ESTUDIANTES_POR_INSTITUCION + 1):
            email = f"estudiante{inst_code}_{i}@acadify.test"
            
            # Check if exists
            existing = db.query(Usuario).filter(Usuario.correo_institucional == email).first()
            if existing:
                print(f"✓ Estudiante ya existe: {existing.correo_institucional}")
                estudiantes.append(existing)
                continue
            
            estudiante = Usuario(
                nombres=f"Estudiante{i}",
                apellidos=f"Inst{inst_code}",
                correo_institucional=email,
                username=None,
                password_hash=security_manager.get_password_hash("estudiante123"),
                tipo_documento=TipoDocumentoUsuario.cc,
                numero_documento=f"200{inst_code}{i:04d}",
                rol=RolUsuario.estudiante,
                estado_cuenta=EstadoCuentaUsuario.activo
            )
            
            db.add(estudiante)
            if i % 10 == 0:
                db.flush()
                print(f"✓ Creados {i} estudiantes para {institucion.nombre}...")
            
            estudiantes.append(estudiante)
        
        estudiantes_por_institucion[institucion.institucion_id] = estudiantes
        print(f"✓ Completados {len(estudiantes)} estudiantes para {institucion.nombre}")
    
    db.commit()
    total = sum(len(e) for e in estudiantes_por_institucion.values())
    print(f"\n✅ Total estudiantes: {total}")
    return estudiantes_por_institucion


def create_cursos(db: Session, instituciones, docentes_por_institucion, programas_por_institucion):
    """Crear cursos de prueba para cada institución"""
    print("\n" + "="*70)
    print("📖 CREANDO CURSOS")
    print("="*70)
    
    cursos_por_institucion = {}
    
    temas = [
        "Programación Python",
        "Base de Datos SQL",
        "Desarrollo Web",
        "Arquitectura de Software",
        "Gestión de Proyectos"
    ]
    
    for institucion in instituciones:
        cursos = []
        inst_code = institucion.sigla[-3:]  # Use sigla instead of codigo
        docentes = docentes_por_institucion[institucion.institucion_id]
        programa = programas_por_institucion[institucion.institucion_id]  # Get programa for this institution
        
        for i, tema in enumerate(temas, 1):
            codigo = f"CUR{inst_code}{i:02d}"
            
            # Check if exists
            existing = db.query(Curso).filter(Curso.codigo_curso == codigo).first()
            if existing:
                print(f"✓ Curso ya existe: {existing.nombre} ({existing.codigo_curso})")
                cursos.append(existing)
                continue
            
            # Asignar docente rotativo (pero los cursos no tienen docente_id directo)
            docente = docentes[(i - 1) % len(docentes)]
            
            curso = Curso(
                codigo_curso=codigo,
                nombre=f"{tema} - {institucion.nombre[:20]}",
                descripcion=f"Curso de {tema.lower()} para load testing",
                institucion_id=institucion.institucion_id,
                programa_id=programa.programa_id,  # Add programa_id (required by DB)
                fecha_inicio=datetime.now() - timedelta(days=30),
                fecha_fin=datetime.now() + timedelta(days=60),
                creditos=3,
                maximo_estudiantes=30,  # Use maximo_estudiantes instead of cupo_maximo
                modalidad="semestral",  # Valid enum value
                activo=True  # Use activo instead of estado
            )
            
            db.add(curso)
            db.flush()
            cursos.append(curso)
            print(f"✓ Curso creado: {curso.nombre} ({curso.codigo_curso})")
        
        cursos_por_institucion[institucion.institucion_id] = cursos
    
    db.commit()
    total = sum(len(c) for c in cursos_por_institucion.values())
    print(f"\n✅ Total cursos: {total}")
    return cursos_por_institucion


def create_inscripciones(db: Session, cursos_por_institucion, estudiantes_por_institucion):
    """Crear inscripciones de estudiantes a cursos"""
    print("\n" + "="*70)
    print("✍️  CREANDO INSCRIPCIONES")
    print("="*70)
    
    total_inscripciones = 0
    
    for institucion_id, cursos in cursos_por_institucion.items():
        estudiantes = estudiantes_por_institucion[institucion_id]
        
        for curso in cursos:
            # Inscribir entre 10 y 20 estudiantes por curso
            num_inscritos = random.randint(10, min(20, len(estudiantes)))
            estudiantes_seleccionados = random.sample(estudiantes, num_inscritos)
            
            for estudiante in estudiantes_seleccionados:
                # Check if already enrolled
                existing = db.query(Inscripcion).filter(
                    Inscripcion.curso_id == curso.curso_id,
                    Inscripcion.usuario_id == estudiante.usuario_id
                ).first()
                
                if existing:
                    continue
                
                inscripcion = Inscripcion(
                    curso_id=curso.curso_id,
                    usuario_id=estudiante.usuario_id,
                    fecha_inscripcion=datetime.now() - timedelta(days=random.randint(1, 25)),
                    estado="activo",
                    nota_final=None
                )
                
                db.add(inscripcion)
                total_inscripciones += 1
            
            print(f"✓ {num_inscritos} estudiantes inscritos en {curso.codigo}")
    
    db.commit()
    print(f"\n✅ Total inscripciones: {total_inscripciones}")
    return total_inscripciones


def create_tareas(db: Session, cursos_por_institucion):
    """Crear tareas para cada curso"""
    print("\n" + "="*70)
    print("📝 CREANDO TAREAS")
    print("="*70)
    
    total_tareas = 0
    tipos = ["practica", "evaluacion", "proyecto"]
    
    for institucion_id, cursos in cursos_por_institucion.items():
        for curso in cursos:
            for i in range(1, NUM_TAREAS_POR_CURSO + 1):
                # Check if exists (by title and course)
                titulo = f"Tarea {i}: {curso.nombre[:30]}"
                existing = db.query(db.execute(
                    "SELECT 1 FROM \"Tarea\" WHERE curso_id = :curso_id AND titulo = :titulo",
                    {"curso_id": str(curso.curso_id), "titulo": titulo}
                ).fetchone())
                
                # Skip if exists - esto es mejor con un modelo, pero lo hacemos simple
                try:
                    from src.models.academic.tarea import Tarea
                    existing = db.query(Tarea).filter(
                        Tarea.curso_id == curso.curso_id,
                        Tarea.titulo == titulo
                    ).first()
                    
                    if existing:
                        continue
                    
                    tarea = Tarea(
                        curso_id=curso.curso_id,
                        titulo=titulo,
                        descripcion=f"Descripción de la tarea {i} para {curso.nombre}",
                        tipo=random.choice(tipos),
                        fecha_inicio=datetime.now() - timedelta(days=random.randint(5, 20)),
                        fecha_fin=datetime.now() + timedelta(days=random.randint(5, 30)),
                        calificacion_maxima=100,
                        porcentaje_nota=random.choice([10, 15, 20, 25, 30]),
                        estado="activo"
                    )
                    
                    db.add(tarea)
                    total_tareas += 1
                except ImportError:
                    # Si no existe el modelo, lo saltamos
                    print(f"⚠️  Modelo Tarea no encontrado, saltando creación de tareas")
                    return 0
            
            print(f"✓ {NUM_TAREAS_POR_CURSO} tareas creadas para {curso.codigo}")
    
    db.commit()
    print(f"\n✅ Total tareas: {total_tareas}")
    return total_tareas


def create_comentarios(db: Session, cursos_por_institucion, estudiantes_por_institucion):
    """Crear comentarios en cursos"""
    print("\n" + "="*70)
    print("💬 CREANDO COMENTARIOS")
    print("="*70)
    
    total_comentarios = 0
    
    try:
        from src.models.communication.comentario import Comentario
        
        for institucion_id, cursos in cursos_por_institucion.items():
            estudiantes = estudiantes_por_institucion[institucion_id]
            
            for curso in cursos:
                # 3-5 comentarios por curso
                num_comentarios = random.randint(3, 5)
                
                for i in range(num_comentarios):
                    estudiante = random.choice(estudiantes)
                    
                    comentario = Comentario(
                        curso_id=curso.curso_id,
                        usuario_id=estudiante.usuario_id,
                        contenido=f"Este es un comentario de prueba #{i+1} para el curso {curso.codigo}. Contenido generado automáticamente para load testing.",
                        fecha_creacion=datetime.now() - timedelta(days=random.randint(1, 20)),
                        estado="activo"
                    )
                    
                    db.add(comentario)
                    total_comentarios += 1
                
                print(f"✓ {num_comentarios} comentarios creados para {curso.codigo}")
        
        db.commit()
        print(f"\n✅ Total comentarios: {total_comentarios}")
        return total_comentarios
        
    except ImportError:
        print(f"⚠️  Modelo Comentario no encontrado, saltando creación de comentarios")
        return 0


def print_summary(instituciones, docentes_por_institucion, estudiantes_por_institucion, 
                 cursos_por_institucion):
    """Imprimir resumen de datos creados"""
    print("\n" + "="*70)
    print("📊 RESUMEN DE DATOS CREADOS")
    print("="*70)
    
    total_docentes = sum(len(d) for d in docentes_por_institucion.values())
    total_estudiantes = sum(len(e) for e in estudiantes_por_institucion.values())
    total_cursos = sum(len(c) for c in cursos_por_institucion.values())
    
    print(f"\n🏢 Instituciones:     {len(instituciones)}")
    print(f"👨‍🏫 Docentes:          {total_docentes}")
    print(f"👨‍🎓 Estudiantes:       {total_estudiantes}")
    print(f"📖 Cursos:            {total_cursos}")
    
    print("\n" + "="*70)
    print("🎯 ESTADÍSTICAS POR INSTITUCIÓN")
    print("="*70)
    
    for institucion in instituciones:
        inst_id = institucion.institucion_id
        print(f"\n📚 {institucion.nombre}")
        print(f"   Docentes:      {len(docentes_por_institucion[inst_id])}")
        print(f"   Estudiantes:   {len(estudiantes_por_institucion[inst_id])}")
        print(f"   Cursos:        {len(cursos_por_institucion[inst_id])}")
        
        for curso in cursos_por_institucion[inst_id]:
            print(f"      - {curso.codigo_curso}: {curso.nombre[:40]}")
    
    print("\n" + "="*70)
    print("🧪 CREDENCIALES DE PRUEBA")
    print("="*70)
    
    print("\n📋 Usuarios principales:")
    print("   Admin:      admin_sena / admin123")
    print("   Docente:    docente@senasofia.edu.co / docente123")
    print("   Estudiante: estudiante@senasofia.edu.co / estudiante123")
    
    print("\n📋 Usuarios de prueba:")
    inst_code = instituciones[0].sigla[-3:]  # Use sigla instead of codigo
    print(f"   Docente1:   docente{inst_code}_1@acadify.test / docente123")
    print(f"   Estudiante1: estudiante{inst_code}_1@acadify.test / estudiante123")
    
    print("\n💡 Comandos útiles:")
    print("   # Test login docente")
    print(f'   curl -X POST http://localhost:8000/auth/login -H "Content-Type: application/json" \\')
    print(f'     -d \'{{"identifier":"docente{inst_code}_1@acadify.test","password":"docente123"}}\'')
    
    print("\n   # Ver cursos de la primera institución")
    print(f'   curl http://localhost:8000/api/cursos?institucion_id={instituciones[0].institucion_id}')
    
    print("\n   # Ejecutar load test")
    print('   cd backend && ./venv/bin/locust -f locustfile.py --host=http://localhost:8000 \\')
    print('     --headless -u 50 -r 5 -t 60s --html=locust_report_v3.html')


def main():
    """Main function"""
    print("\n" + "="*70)
    print("🚀 CREANDO ECOSISTEMA ACADÉMICO COMPLETO")
    print("="*70)
    print(f"\nConfiguración:")
    print(f"  - Instituciones:              {NUM_INSTITUCIONES}")
    print(f"  - Cursos por institución:     {NUM_CURSOS_POR_INSTITUCION}")
    print(f"  - Docentes por institución:   {NUM_DOCENTES_POR_INSTITUCION}")
    print(f"  - Estudiantes por institución: {NUM_ESTUDIANTES_POR_INSTITUCION}")
    
    print(f"\n📊 Total estimado:")
    print(f"  - Usuarios:       {NUM_INSTITUCIONES * (NUM_DOCENTES_POR_INSTITUCION + NUM_ESTUDIANTES_POR_INSTITUCION)}")
    print(f"  - Cursos:         {NUM_INSTITUCIONES * NUM_CURSOS_POR_INSTITUCION}")
    
    input("\n⏸️  Presiona ENTER para continuar o Ctrl+C para cancelar...")
    
    db = SessionLocal()
    try:
        # Paso 1: Crear instituciones
        instituciones = create_instituciones(db)
        
        # Paso 2: Crear programas (requerido por Curso)
        programas_por_institucion = create_programas(db, instituciones)
        
        # Paso 3: Crear docentes
        docentes_por_institucion = create_docentes(db, instituciones)
        
        # Paso 4: Crear estudiantes
        estudiantes_por_institucion = create_estudiantes(db, instituciones)
        
        # Paso 5: Crear cursos
        cursos_por_institucion = create_cursos(db, instituciones, docentes_por_institucion, programas_por_institucion)
        
        # Resumen final
        print_summary(
            instituciones, 
            docentes_por_institucion, 
            estudiantes_por_institucion,
            cursos_por_institucion
        )
        
        print("\n" + "="*70)
        print("✅ ECOSISTEMA ACADÉMICO CREADO EXITOSAMENTE")
        print("="*70)
        print("\n🎉 Ahora puedes ejecutar el load test con datos reales!")
        
    except Exception as e:
        print(f"\n❌ Error creando ecosistema: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    main()
