"""
Script para validar el flujo completo de Instituciones y Cursos

Crea:
1. Una institución con dominio
2. Un coordinador vinculado
3. Un programa académico
4. Cursos vinculados a la institución

Luego valida:
- Búsqueda por dominio
- Estadísticas
- Relaciones completas
"""

import asyncio
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from passlib.context import CryptContext

from src.core.config import settings
from src.models.users.usuario import Usuario
from src.models.users.coordinador import Coordinador
from src.models.academic.institucion import Institucion
from src.models.academic.programa import Programa
from src.models.academic.curso import Curso
from src.schemas.academic.institucion import InstitucionCreate
from src.schemas.academic.programa import ProgramaCreate
from src.services.academic.institucion_service import institucion_service
from datetime import date


# Configuración
SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def crear_coordinador_prueba(db):
    """Crea o recupera coordinador de prueba"""
    print("\n1️⃣  Creando/recuperando coordinador...")
    
    # Buscar existente
    coordinador = db.query(Usuario).filter(
        Usuario.correo_institucional == "coord.demo@techabc.edu"
    ).first()
    
    if coordinador:
        print(f"   ✅ Coordinador existente: {coordinador.nombres} {coordinador.apellidos}")
        
        # Verificar si existe registro en tabla Coordinador
        coordinador_registro = db.query(Coordinador).filter(
            Coordinador.coordinador_id == coordinador.usuario_id
        ).first()
        
        if not coordinador_registro:
            print("      ⚠️  Creando registro en tabla Coordinador...")
            coordinador_registro = Coordinador(
                coordinador_id=coordinador.usuario_id,
                fecha_inicio_carrera=date.today()
            )
            db.add(coordinador_registro)
            db.commit()
            print("      ✅ Registro en tabla Coordinador creado")
        
        return coordinador
    
    # Crear nuevo
    coordinador = Usuario(
        nombres="Carlos",
        apellidos="Martínez",
        correo_institucional="coord.demo@techabc.edu",
        tipo_documento="cc",  # Enum: cc, ti, ce
        numero_documento="1234567890",
        rol="coordinador",
        estado_cuenta="activo",
        password_hash=pwd_context.hash("Demo123!")
    )
    
    db.add(coordinador)
    db.commit()
    db.refresh(coordinador)
    
    # Crear registro en tabla Coordinador
    coordinador_registro = Coordinador(
        coordinador_id=coordinador.usuario_id,
        fecha_inicio_carrera=date.today()
    )
    db.add(coordinador_registro)
    db.commit()
    
    print(f"   ✅ Coordinador creado: {coordinador.nombres} {coordinador.apellidos}")
    return coordinador


def crear_institucion_prueba(db, coordinador):
    """Crea institución de prueba"""
    print("\n2️⃣  Creando institución...")
    
    # Verificar si existe
    institucion_existente = db.query(Institucion).filter(
        Institucion.dominio == "techabc.edu"
    ).first()
    
    if institucion_existente:
        print(f"   ✅ Institución existente: {institucion_existente.nombre}")
        return institucion_existente
    
    # Crear nueva
    institucion_data = InstitucionCreate(
        nombre="Instituto Tecnológico ABC",
        tipo_institucion="instituto",
        usa_programas=True,
        nivel_educativo="tecnica",
        sector="publico",
        direccion="Av. Principal 456, Bogotá",
        ciudad="Bogotá",
        pais="Colombia",
        telefono="3001234567",
        correo_institucional="info@techabc.edu",
        nit="900123456-1"
    )
    
    resultado = institucion_service.crear_institucion(
        db,
        institucion_data,
        coordinador
    )
    
    if resultado["success"]:
        institucion_id = resultado["data"]["institucion_id"]
        institucion = db.query(Institucion).filter(
            Institucion.institucion_id == institucion_id
        ).first()
        
        print(f"   ✅ Institución creada: {institucion.nombre}")
        print(f"      - Dominio: {institucion.dominio}")
        print(f"      - ID: {institucion_id}")
        
        return institucion
    else:
        print(f"   ❌ Error: {resultado.get('message')}")
        return None


def crear_programa_prueba(db, institucion):
    """Crea programa académico de prueba"""
    print("\n3️⃣  Creando programa académico...")
    
    # Verificar existente
    programa_existente = db.query(Programa).filter(
        Programa.nombre == "Desarrollo de Software",
        Programa.institucion_id == institucion.institucion_id
    ).first()
    
    if programa_existente:
        print(f"   ✅ Programa existente: {programa_existente.nombre}")
        return programa_existente
    
    # Crear nuevo
    programa = Programa(
        institucion_id=institucion.institucion_id,
        nombre="Desarrollo de Software",
        descripcion="Programa técnico en desarrollo de aplicaciones web y móviles",
        nivel="tecnico",
        tipo="presencial"
    )
    
    db.add(programa)
    db.commit()
    db.refresh(programa)
    
    print(f"   ✅ Programa creado: {programa.nombre}")
    print(f"      - Nivel: {programa.nivel}")
    print(f"      - Tipo: {programa.tipo}")
    
    return programa


def crear_cursos_prueba(db, institucion, programa, coordinador):
    """Crea cursos de prueba"""
    print("\n4️⃣  Creando cursos...")
    
    cursos_data = [
        {
            "nombre": "Fundamentos de Programación",
            "descripcion": "Introducción a la lógica de programación y algoritmos",
            "codigo_curso": "DS101",
            "codigo_acceso": "PROG2024"
        },
        {
            "nombre": "Bases de Datos",
            "descripcion": "Diseño e implementación de bases de datos relacionales",
            "codigo_curso": "DS201",
            "codigo_acceso": "BD2024"
        },
        {
            "nombre": "Desarrollo Web",
            "descripcion": "Creación de aplicaciones web con HTML, CSS y JavaScript",
            "codigo_curso": "DS301",
            "codigo_acceso": "WEB2024"
        }
    ]
    
    cursos_creados = []
    
    for curso_data in cursos_data:
        # Verificar existente
        curso_existente = db.query(Curso).filter(
            Curso.codigo_acceso == curso_data["codigo_acceso"]
        ).first()
        
        if curso_existente:
            print(f"   ✅ Curso existente: {curso_existente.nombre}")
            cursos_creados.append(curso_existente)
            continue
        
        # Crear nuevo
        curso = Curso(
            institucion_id=institucion.institucion_id,
            programa_id=programa.programa_id,
            coordinador_id=coordinador.usuario_id,
            nombre=curso_data["nombre"],
            descripcion=curso_data["descripcion"],
            codigo_curso=curso_data["codigo_curso"],
            codigo_acceso=curso_data["codigo_acceso"],
            modalidad="semestral",  # ModalidadCurso enum
            activo=True,
            permite_inscripcion=True
        )
        
        db.add(curso)
        db.commit()
        db.refresh(curso)
        
        print(f"   ✅ Curso creado: {curso.nombre}")
        print(f"      - Código: {curso.codigo_curso}")
        print(f"      - Acceso: {curso.codigo_acceso}")
        
        cursos_creados.append(curso)
    
    return cursos_creados


def validar_busqueda_dominio(db):
    """Valida búsqueda por dominio"""
    print("\n5️⃣  Validando búsqueda por dominio...")
    
    try:
        institucion = institucion_service.buscar_por_dominio(db, "techabc.edu")
        
        if institucion:
            print(f"   ✅ Institución encontrada: {institucion.nombre}")
            print(f"      - Dominio: {institucion.dominio}")
            print(f"      - Tipo: {institucion.tipo_institucion}")
            return True
        else:
            print("   ❌ No se encontró institución con ese dominio")
            return False
    except Exception as e:
        db.rollback()
        print(f"   ❌ Error: {str(e)}")
        return False


def validar_estadisticas(db, institucion, coordinador):
    """Valida estadísticas de institución"""
    print("\n6️⃣  Validando estadísticas...")
    
    try:
        resultado = institucion_service.obtener_estadisticas_institucion(
            db,
            institucion.institucion_id,
            coordinador
        )
        
        if resultado["success"]:
            stats = resultado["data"]
            print("   ✅ Estadísticas obtenidas:")
            print(f"      - Institución: {stats['nombre']}")
            print(f"      - Cursos totales: {stats['total_cursos']}")
            print(f"      - Cursos activos: {stats['cursos_activos']}")
            print(f"      - Docentes: {stats['total_docentes']}")
            print(f"      - Estudiantes: {stats['total_estudiantes']}")
            print(f"      - Programas: {stats['total_programas']}")
            print(f"      - Coordinadores: {stats['total_coordinadores']}")
            return True
        else:
            print(f"   ❌ Error: {resultado.get('message')}")
            return False
    except Exception as e:
        db.rollback()
        print(f"   ❌ Error: {str(e)}")
        return False


def validar_relaciones(db):
    """Valida relaciones completas"""
    print("\n7️⃣  Validando relaciones completas...")
    
    try:
        query = text("""
            SELECT
                i.nombre as institucion,
                p.nombre as programa,
                c.nombre as curso,
                c.codigo_acceso
            FROM "Institucion" i
            JOIN "Programa" p ON i.institucion_id = p.institucion_id
            JOIN "Curso" c ON p.programa_id = c.programa_id
            WHERE i.dominio = 'techabc.edu'
            ORDER BY c.nombre
        """)
        
        resultados = db.execute(query).fetchall()
        
        if len(resultados) > 0:
            print(f"   ✅ Encontradas {len(resultados)} relaciones completas:")
            for row in resultados:
                print(f"      - {row[0]} > {row[1]} > {row[2]} ({row[3]})")
            return True
        else:
            print("   ⚠️  No se encontraron relaciones completas")
            return False
    except Exception as e:
        db.rollback()
        print(f"   ❌ Error: {str(e)}")
        return False


def main():
    """Función principal"""
    print("="*70)
    print("VALIDACIÓN COMPLETA: INSTITUCIONES Y CURSOS")
    print("="*70)
    
    db = SessionLocal()
    
    try:
        # 1. Crear coordinador
        coordinador = crear_coordinador_prueba(db)
        
        # 2. Crear institución
        institucion = crear_institucion_prueba(db, coordinador)
        if not institucion:
            print("\n❌ No se pudo crear la institución. Abortando.")
            return
        
        # 3. Crear programa
        programa = crear_programa_prueba(db, institucion)
        
        # 4. Crear cursos
        cursos = crear_cursos_prueba(db, institucion, programa, coordinador)
        
        # 5. Validar búsqueda por dominio
        validar_busqueda_dominio(db)
        
        # 6. Validar estadísticas
        validar_estadisticas(db, institucion, coordinador)
        
        # 7. Validar relaciones
        validar_relaciones(db)
        
        print("\n" + "="*70)
        print("✅ VALIDACIÓN COMPLETA EXITOSA")
        print("="*70)
        print("\n📊 Resumen:")
        print(f"   - Institución: {institucion.nombre}")
        print(f"   - Dominio: {institucion.dominio}")
        print(f"   - Coordinador: {coordinador.nombres} {coordinador.apellidos}")
        print(f"   - Programas: 1")
        print(f"   - Cursos: {len(cursos)}")
        print("\n💡 Puedes usar estos códigos de acceso:")
        for curso in cursos:
            print(f"   - {curso.nombre}: {curso.codigo_acceso}")
        
    except Exception as e:
        print(f"\n❌ Error durante validación: {str(e)}")
        db.rollback()
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    main()
