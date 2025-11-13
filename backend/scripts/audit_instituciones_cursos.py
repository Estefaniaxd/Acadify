"""
Script de auditoría para Instituciones y Cursos
Verifica integridad, relaciones y funcionalidades faltantes
"""

import sys
import os
from pathlib import Path

# Agregar el directorio raíz al path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from sqlalchemy import create_engine, inspect, text, func
from sqlalchemy.orm import sessionmaker
from src.core.config import settings
from src.models.academic.institucion import Institucion
from src.models.academic.curso import Curso
from src.models.academic.programa import Programa
from src.models.users.institucion_coordinador import InstitucionCoordinador
from src.models.users.coordinador import Coordinador
from src.models.academic.curso_docente import CursoDocente
from src.models.academic.grupo_curso import GrupoCurso
from colorama import Fore, Style, init

init(autoreset=True)

# Conexión a la base de datos
engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def print_header(title: str):
    """Imprime un encabezado formateado"""
    print(f"\n{Fore.CYAN}{'=' * 80}")
    print(f"{Fore.CYAN}{title:^80}")
    print(f"{Fore.CYAN}{'=' * 80}{Style.RESET_ALL}\n")


def print_section(title: str):
    """Imprime una sección"""
    print(f"\n{Fore.YELLOW}{'─' * 80}")
    print(f"{Fore.YELLOW}{title}")
    print(f"{Fore.YELLOW}{'─' * 80}{Style.RESET_ALL}")


def check_table_structure():
    """Verifica estructura de tablas"""
    print_section("📋 ESTRUCTURA DE TABLAS")
    
    inspector = inspect(engine)
    
    tables_to_check = {
        "Institucion": [
            "institucion_id", "nombre", "dominio", "correo_institucional",
            "estado", "fecha_creacion", "fecha_activacion"
        ],
        "Curso": [
            "curso_id", "institucion_id", "nombre", "codigo_curso",
            "codigo_acceso", "activo", "permite_inscripcion"
        ],
        "Programa": [
            "programa_id", "institucion_id", "nombre", "nivel", "tipo"
        ],
        "InstitucionCoordinador": [
            "institucion_id", "coordinador_id", "fecha_asignacion", "estado"
        ]
    }
    
    for table_name, expected_columns in tables_to_check.items():
        print(f"\n{Fore.GREEN}✓ Tabla: {table_name}{Style.RESET_ALL}")
        
        if not inspector.has_table(table_name):
            print(f"  {Fore.RED}✗ Tabla NO existe{Style.RESET_ALL}")
            continue
            
        columns = [col['name'] for col in inspector.get_columns(table_name)]
        
        for col in expected_columns:
            if col in columns:
                print(f"  {Fore.GREEN}✓{Style.RESET_ALL} {col}")
            else:
                print(f"  {Fore.RED}✗{Style.RESET_ALL} {col} (FALTA)")
        
        # Verificar índices
        indexes = inspector.get_indexes(table_name)
        if indexes:
            print(f"  {Fore.CYAN}Índices: {len(indexes)}{Style.RESET_ALL}")
        
        # Verificar foreign keys
        fks = inspector.get_foreign_keys(table_name)
        if fks:
            print(f"  {Fore.CYAN}Foreign Keys: {len(fks)}{Style.RESET_ALL}")


def check_data_integrity():
    """Verifica integridad de datos"""
    print_section("🔍 INTEGRIDAD DE DATOS")
    
    db = SessionLocal()
    try:
        # 1. Instituciones sin dominio
        instituciones_sin_dominio = db.query(Institucion).filter(
            Institucion.dominio.is_(None)
        ).count()
        
        if instituciones_sin_dominio > 0:
            print(f"{Fore.YELLOW}⚠ {instituciones_sin_dominio} instituciones sin dominio{Style.RESET_ALL}")
        else:
            print(f"{Fore.GREEN}✓ Todas las instituciones tienen dominio{Style.RESET_ALL}")
        
        # 2. Cursos sin código de acceso
        cursos_sin_codigo = db.query(Curso).filter(
            Curso.codigo_acceso.is_(None)
        ).count()
        
        if cursos_sin_codigo > 0:
            print(f"{Fore.YELLOW}⚠ {cursos_sin_codigo} cursos sin código de acceso{Style.RESET_ALL}")
        else:
            print(f"{Fore.GREEN}✓ Todos los cursos tienen código de acceso{Style.RESET_ALL}")
        
        # 3. Cursos sin institución (huérfanos)
        cursos_huerfanos = db.query(Curso).outerjoin(
            Institucion, Curso.institucion_id == Institucion.institucion_id
        ).filter(Institucion.institucion_id.is_(None)).count()
        
        if cursos_huerfanos > 0:
            print(f"{Fore.RED}✗ {cursos_huerfanos} cursos huérfanos (sin institución){Style.RESET_ALL}")
        else:
            print(f"{Fore.GREEN}✓ Todos los cursos tienen institución válida{Style.RESET_ALL}")
        
        # 4. Programas sin cursos
        programas_sin_cursos = db.query(Programa).outerjoin(
            Curso, Programa.programa_id == Curso.programa_id
        ).group_by(Programa.programa_id).having(func.count(Curso.curso_id) == 0).count()
        
        if programas_sin_cursos > 0:
            print(f"{Fore.YELLOW}⚠ {programas_sin_cursos} programas sin cursos asignados{Style.RESET_ALL}")
        else:
            print(f"{Fore.GREEN}✓ Todos los programas tienen cursos{Style.RESET_ALL}")
        
        # 5. Instituciones sin coordinadores
        instituciones_sin_coord = db.query(Institucion).outerjoin(
            InstitucionCoordinador,
            Institucion.institucion_id == InstitucionCoordinador.institucion_id
        ).group_by(Institucion.institucion_id).having(
            func.count(InstitucionCoordinador.coordinador_id) == 0
        ).count()
        
        if instituciones_sin_coord > 0:
            print(f"{Fore.YELLOW}⚠ {instituciones_sin_coord} instituciones sin coordinadores{Style.RESET_ALL}")
        
    finally:
        db.close()


def check_relationships():
    """Verifica relaciones entre tablas"""
    print_section("🔗 RELACIONES ENTRE TABLAS")
    
    db = SessionLocal()
    try:
        # Estadísticas de relaciones
        total_instituciones = db.query(Institucion).count()
        total_cursos = db.query(Curso).count()
        total_programas = db.query(Programa).count()
        total_coord = db.query(InstitucionCoordinador).count()
        
        print(f"{Fore.CYAN}Total Instituciones:{Style.RESET_ALL} {total_instituciones}")
        print(f"{Fore.CYAN}Total Cursos:{Style.RESET_ALL} {total_cursos}")
        print(f"{Fore.CYAN}Total Programas:{Style.RESET_ALL} {total_programas}")
        print(f"{Fore.CYAN}Total Relaciones Institución-Coordinador:{Style.RESET_ALL} {total_coord}")
        
        if total_instituciones > 0:
            print(f"\n{Fore.GREEN}Promedio cursos por institución:{Style.RESET_ALL} {total_cursos / total_instituciones:.2f}")
            print(f"{Fore.GREEN}Promedio programas por institución:{Style.RESET_ALL} {total_programas / total_instituciones:.2f}")
        
        # Verificar cursos activos vs inactivos
        cursos_activos = db.query(Curso).filter(Curso.activo == True).count()
        cursos_inactivos = db.query(Curso).filter(Curso.activo == False).count()
        
        print(f"\n{Fore.GREEN}Cursos Activos:{Style.RESET_ALL} {cursos_activos}")
        print(f"{Fore.YELLOW}Cursos Inactivos:{Style.RESET_ALL} {cursos_inactivos}")
        
        # Cursos con inscripción abierta
        cursos_inscripcion = db.query(Curso).filter(
            Curso.activo == True,
            Curso.permite_inscripcion == True
        ).count()
        
        print(f"{Fore.GREEN}Cursos con inscripción abierta:{Style.RESET_ALL} {cursos_inscripcion}")
        
    finally:
        db.close()


def check_missing_features():
    """Verifica funcionalidades faltantes basadas en el modelo"""
    print_section("🔧 FUNCIONALIDADES SUGERIDAS")
    
    features = [
        {
            "nombre": "Búsqueda de instituciones por dominio",
            "metodo": "get_by_dominio(dominio: str)",
            "ubicacion": "crud_institucion.py",
            "prioridad": "ALTA"
        },
        {
            "nombre": "Activación/desactivación de instituciones",
            "metodo": "cambiar_estado(institucion_id, estado)",
            "ubicacion": "crud_institucion.py",
            "prioridad": "ALTA"
        },
        {
            "nombre": "Listar instituciones activas",
            "metodo": "get_instituciones_activas()",
            "ubicacion": "crud_institucion.py",
            "prioridad": "MEDIA"
        },
        {
            "nombre": "Estadísticas de institución",
            "metodo": "get_estadisticas_institucion(institucion_id)",
            "ubicacion": "crud_institucion.py",
            "prioridad": "MEDIA"
        },
        {
            "nombre": "Validar código de acceso único",
            "metodo": "generar_codigo_acceso_unico()",
            "ubicacion": "crud_curso.py",
            "prioridad": "ALTA"
        },
        {
            "nombre": "Buscar curso por código de acceso",
            "metodo": "get_by_codigo_acceso(codigo: str)",
            "ubicacion": "crud_curso.py",
            "prioridad": "ALTA"
        },
        {
            "nombre": "Verificar disponibilidad de inscripción",
            "metodo": "verificar_disponibilidad(curso_id, estudiante_id)",
            "ubicacion": "crud_curso.py",
            "prioridad": "ALTA"
        },
        {
            "nombre": "Listar cursos por fecha",
            "metodo": "get_cursos_por_periodo(fecha_inicio, fecha_fin)",
            "ubicacion": "crud_curso.py",
            "prioridad": "BAJA"
        },
        {
            "nombre": "Endpoint: Agregar coordinador a institución",
            "metodo": "POST /instituciones/{id}/coordinadores",
            "ubicacion": "routes/institucion.py",
            "prioridad": "ALTA"
        },
        {
            "nombre": "Endpoint: Listar coordinadores de institución",
            "metodo": "GET /instituciones/{id}/coordinadores",
            "ubicacion": "routes/institucion.py",
            "prioridad": "MEDIA"
        },
        {
            "nombre": "Endpoint: Estadísticas de institución",
            "metodo": "GET /instituciones/{id}/estadisticas",
            "ubicacion": "routes/institucion.py",
            "prioridad": "MEDIA"
        },
        {
            "nombre": "Endpoint: Inscribirse con código",
            "metodo": "POST /cursos/inscribir-con-codigo",
            "ubicacion": "routes/cursos.py",
            "prioridad": "ALTA"
        },
        {
            "nombre": "Endpoint: Listar personas del curso",
            "metodo": "GET /cursos/{id}/personas",
            "ubicacion": "routes/cursos.py",
            "prioridad": "ALTA"
        },
    ]
    
    # Agrupar por prioridad
    prioridades = {"ALTA": [], "MEDIA": [], "BAJA": []}
    for feature in features:
        prioridades[feature["prioridad"]].append(feature)
    
    for prioridad, items in prioridades.items():
        color = Fore.RED if prioridad == "ALTA" else Fore.YELLOW if prioridad == "MEDIA" else Fore.BLUE
        print(f"\n{color}{'⚠' if prioridad == 'ALTA' else '○'} Prioridad {prioridad}:{Style.RESET_ALL}")
        
        for item in items:
            print(f"  • {item['nombre']}")
            print(f"    {Fore.CYAN}└─{Style.RESET_ALL} {item['metodo']}")
            print(f"    {Fore.CYAN}└─{Style.RESET_ALL} Ubicación: {item['ubicacion']}")


def test_queries():
    """Prueba consultas comunes"""
    print_section("🧪 PRUEBAS DE CONSULTAS")
    
    db = SessionLocal()
    try:
        # Test 1: Obtener instituciones con sus cursos
        print(f"\n{Fore.CYAN}Test 1: Instituciones con cursos{Style.RESET_ALL}")
        instituciones = db.query(Institucion).limit(3).all()
        
        for inst in instituciones:
            cursos_count = len(inst.cursos) if hasattr(inst, 'cursos') else 0
            print(f"  • {inst.nombre}: {cursos_count} cursos")
        
        # Test 2: Cursos con coordinadores
        print(f"\n{Fore.CYAN}Test 2: Cursos con coordinadores{Style.RESET_ALL}")
        cursos = db.query(Curso).limit(3).all()
        
        for curso in cursos:
            coord_name = curso.coordinador.usuario.nombre_completo if curso.coordinador else "Sin coordinador"
            print(f"  • {curso.nombre}: {coord_name}")
        
        # Test 3: Programas con cursos
        print(f"\n{Fore.CYAN}Test 3: Programas con cursos{Style.RESET_ALL}")
        programas = db.query(Programa).limit(3).all()
        
        for programa in programas:
            cursos_count = len(programa.cursos) if hasattr(programa, 'cursos') else 0
            print(f"  • {programa.nombre}: {cursos_count} cursos")
        
        print(f"\n{Fore.GREEN}✓ Todas las consultas ejecutadas correctamente{Style.RESET_ALL}")
        
    except Exception as e:
        print(f"\n{Fore.RED}✗ Error en consultas: {str(e)}{Style.RESET_ALL}")
    finally:
        db.close()


def main():
    """Función principal"""
    print_header("AUDITORÍA DE INSTITUCIONES Y CURSOS")
    
    try:
        check_table_structure()
        check_data_integrity()
        check_relationships()
        check_missing_features()
        test_queries()
        
        print_header("AUDITORÍA COMPLETADA")
        print(f"\n{Fore.GREEN}✓ Auditoría finalizada exitosamente{Style.RESET_ALL}\n")
        
    except Exception as e:
        print(f"\n{Fore.RED}✗ Error durante la auditoría: {str(e)}{Style.RESET_ALL}\n")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
