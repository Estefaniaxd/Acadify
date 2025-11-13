#!/usr/bin/env python3
"""
Script para aplicar objetos de base de datos al sistema Acadify
Ejecuta en orden: funciones, triggers, vistas

Uso:
    python apply_database_objects.py
"""

import sys
import os
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_path))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session
from src.core.config import settings
from colorama import init, Fore, Style

init(autoreset=True)

def print_success(message: str):
    print(f"{Fore.GREEN}✅ {message}{Style.RESET_ALL}")

def print_error(message: str):
    print(f"{Fore.RED}❌ {message}{Style.RESET_ALL}")

def print_info(message: str):
    print(f"{Fore.CYAN}ℹ️  {message}{Style.RESET_ALL}")

def print_warning(message: str):
    print(f"{Fore.YELLOW}⚠️  {message}{Style.RESET_ALL}")

def print_header(title: str):
    print(f"\n{Fore.MAGENTA}{'='*60}")
    print(f"{title}")
    print(f"{'='*60}{Style.RESET_ALL}\n")

def execute_sql_file(session: Session, file_path: Path) -> tuple[bool, str]:
    """
    Ejecuta un archivo SQL completo
    
    Returns:
        tuple: (success: bool, message: str)
    """
    try:
        print_info(f"Leyendo archivo: {file_path.name}")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            sql_content = f.read()
        
        # Execute the entire file as one big statement
        # PostgreSQL can handle this with $$-delimited functions
        try:
            session.execute(text(sql_content))
            session.commit()
            print_success(f"Archivo {file_path.name} ejecutado correctamente")
            return True, f"Archivo {file_path.name} aplicado correctamente"
        except Exception as e:
            # If that fails, try psql approach
            session.rollback()
            raise e
        
    except Exception as e:
        session.rollback()
        error_msg = f"Error al ejecutar {file_path.name}: {str(e)}"
        print_error(error_msg)
        print_warning("Intentando con psql directamente...")
        
        # Try with psql command line
        import subprocess
        try:
            # Get connection params from settings
            result = subprocess.run(
                [
                    'psql',
                    '-h', settings.POSTGRES_SERVER,
                    '-p', str(settings.POSTGRES_PORT),
                    '-U', settings.POSTGRES_USER,
                    '-d', settings.POSTGRES_DB,
                    '-f', str(file_path),
                    '-v', 'ON_ERROR_STOP=1'
                ],
                env={'PGPASSWORD': settings.POSTGRES_PASSWORD},
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                print_success(f"Archivo {file_path.name} ejecutado con psql")
                return True, f"Archivo {file_path.name} aplicado correctamente con psql"
            else:
                print_error(f"Error psql: {result.stderr}")
                return False, f"Error ejecutando {file_path.name}"
                
        except FileNotFoundError:
            print_error("psql no está instalado o no está en el PATH")
            return False, error_msg

def verify_objects_created(session: Session) -> dict:
    """
    Verifica qué objetos fueron creados
    """
    results = {}
    
    # Check functions
    query = text("""
        SELECT COUNT(*) as count 
        FROM pg_proc p
        JOIN pg_namespace n ON p.pronamespace = n.oid
        WHERE n.nspname = 'public'
        AND p.prokind IN ('f', 'p')
    """)
    results['functions'] = session.execute(query).scalar()
    
    # Check triggers
    query = text("""
        SELECT COUNT(*) as count
        FROM information_schema.triggers
        WHERE trigger_schema = 'public'
    """)
    results['triggers'] = session.execute(query).scalar()
    
    # Check views
    query = text("""
        SELECT COUNT(*) as count
        FROM pg_views
        WHERE schemaname = 'public'
    """)
    results['views'] = session.execute(query).scalar()
    
    return results

def list_created_objects(session: Session):
    """
    Lista todos los objetos creados
    """
    print_header("OBJETOS CREADOS EN LA BASE DE DATOS")
    
    # List functions
    print(f"\n{Fore.CYAN}📦 FUNCIONES:{Style.RESET_ALL}")
    query = text("""
        SELECT 
            p.proname as name,
            pg_get_function_identity_arguments(p.oid) as args,
            CASE p.prokind
                WHEN 'f' THEN 'function'
                WHEN 'p' THEN 'procedure'
                WHEN 'a' THEN 'aggregate'
                WHEN 'w' THEN 'window'
            END as type
        FROM pg_proc p
        JOIN pg_namespace n ON p.pronamespace = n.oid
        WHERE n.nspname = 'public'
        AND p.prokind IN ('f', 'p')
        ORDER BY p.proname
    """)
    
    functions = session.execute(query).fetchall()
    for i, func in enumerate(functions, 1):
        print(f"  {i}. {func.name}({func.args}) - {func.type}")
    
    if not functions:
        print_warning("  No se encontraron funciones")
    
    # List triggers
    print(f"\n{Fore.CYAN}⚡ TRIGGERS:{Style.RESET_ALL}")
    query = text("""
        SELECT 
            trigger_name,
            event_object_table as table_name,
            action_timing || ' ' || string_agg(event_manipulation, ', ') as events
        FROM information_schema.triggers
        WHERE trigger_schema = 'public'
        GROUP BY trigger_name, event_object_table, action_timing
        ORDER BY event_object_table, trigger_name
    """)
    
    triggers = session.execute(query).fetchall()
    for i, trig in enumerate(triggers, 1):
        print(f"  {i}. {trig.trigger_name} on {trig.table_name} ({trig.events})")
    
    if not triggers:
        print_warning("  No se encontraron triggers")
    
    # List views
    print(f"\n{Fore.CYAN}👁️  VISTAS:{Style.RESET_ALL}")
    query = text("""
        SELECT 
            viewname as name,
            pg_size_pretty(pg_total_relation_size(quote_ident(schemaname) || '.' || quote_ident(viewname))) as size
        FROM pg_views
        WHERE schemaname = 'public'
        ORDER BY viewname
    """)
    
    views = session.execute(query).fetchall()
    for i, view in enumerate(views, 1):
        print(f"  {i}. {view.name}")
    
    if not views:
        print_warning("  No se encontraron vistas")

def test_functions(session: Session):
    """
    Prueba las funciones creadas con datos de ejemplo
    """
    print_header("PRUEBAS DE FUNCIONES")
    
    try:
        # Test 1: Get a student ID
        print_info("Buscando un estudiante de prueba...")
        query = text("SELECT estudiante_id FROM \"Estudiante\" LIMIT 1")
        result = session.execute(query).fetchone()
        
        if not result:
            print_warning("No hay estudiantes en la base de datos para probar")
            return
        
        estudiante_id = result[0]
        print_success(f"Usando estudiante: {estudiante_id}")
        
        # Test calcular_promedio_estudiante
        print_info("\nProbando calcular_promedio_estudiante()...")
        query = text("SELECT calcular_promedio_estudiante(:id)")
        promedio = session.execute(query, {"id": estudiante_id}).scalar()
        if promedio is not None:
            print_success(f"Promedio del estudiante: {promedio}")
        else:
            print_info("Estudiante sin calificaciones aún")
        
        # Test contar_entregas_pendientes
        print_info("\nProbando contar_entregas_pendientes()...")
        query = text("SELECT contar_entregas_pendientes(:id)")
        pendientes = session.execute(query, {"id": estudiante_id}).scalar()
        print_success(f"Entregas pendientes: {pendientes}")
        
        # Test get a course ID
        print_info("\nBuscando un curso de prueba...")
        query = text("SELECT curso_id FROM \"Curso\" LIMIT 1")
        result = session.execute(query).fetchone()
        
        if result:
            curso_id = result[0]
            print_success(f"Usando curso: {curso_id}")
            
            # Test calcular_estadisticas_curso
            print_info("\nProbando calcular_estadisticas_curso()...")
            query = text("SELECT * FROM calcular_estadisticas_curso(:id)")
            stats = session.execute(query, {"id": curso_id}).fetchone()
            if stats:
                print_success("Estadísticas del curso obtenidas:")
                print(f"  Total estudiantes: {stats.total_estudiantes}")
                print(f"  Total entregas: {stats.total_entregas}")
                print(f"  Promedio: {stats.promedio_curso}")
        
        print_success("\n✅ Todas las funciones probadas exitosamente")
        
    except Exception as e:
        print_error(f"Error al probar funciones: {str(e)}")

def test_views(session: Session):
    """
    Prueba las vistas creadas
    """
    print_header("PRUEBAS DE VISTAS")
    
    views_to_test = [
        'vista_estudiantes_desempeno',
        'vista_cursos_estadisticas',
        'vista_evaluaciones_resumen',
        'vista_entregas_pendientes',
        'vista_estudiantes_riesgo',
    ]
    
    for view_name in views_to_test:
        try:
            print_info(f"\nProbando {view_name}...")
            query = text(f"SELECT COUNT(*) FROM {view_name}")
            count = session.execute(query).scalar()
            print_success(f"{view_name}: {count} registros")
            
            # Show first row as sample
            if count > 0:
                query = text(f"SELECT * FROM {view_name} LIMIT 1")
                result = session.execute(query).fetchone()
                print(f"  Sample: {dict(result._mapping)}")
                
        except Exception as e:
            print_error(f"Error al probar {view_name}: {str(e)}")

def main():
    """
    Main execution
    """
    print_header("APLICACIÓN DE OBJETOS DE BASE DE DATOS - ACADIFY")
    
    # Database files in order
    database_dir = Path(__file__).resolve().parent
    sql_files = [
        database_dir / "01_funciones.sql",
        database_dir / "02_triggers.sql",
        database_dir / "03_vistas.sql",
    ]
    
    # Check files exist
    print_info("Verificando archivos SQL...")
    for sql_file in sql_files:
        if not sql_file.exists():
            print_error(f"Archivo no encontrado: {sql_file}")
            return 1
        print_success(f"Encontrado: {sql_file.name}")
    
    # Create database connection
    print_info(f"\nConectando a base de datos: {settings.POSTGRES_DB}")
    # Use database_url property
    db_url = settings.database_url if hasattr(settings, 'database_url') else settings.DATABASE_URL
    engine = create_engine(db_url)
    
    try:
        with Session(engine) as session:
            # Get initial state
            print_info("\nEstado inicial de la base de datos:")
            initial_state = verify_objects_created(session)
            print(f"  Funciones: {initial_state['functions']}")
            print(f"  Triggers: {initial_state['triggers']}")
            print(f"  Vistas: {initial_state['views']}")
            
            # Execute each SQL file
            print_header("EJECUTANDO ARCHIVOS SQL")
            all_success = True
            
            for sql_file in sql_files:
                print(f"\n{Fore.CYAN}{'─'*60}{Style.RESET_ALL}")
                success, message = execute_sql_file(session, sql_file)
                if not success:
                    all_success = False
                    print_error(f"Falló: {sql_file.name}")
                    break
            
            if not all_success:
                print_error("\n❌ La aplicación falló. Revisa los errores arriba.")
                return 1
            
            # Get final state
            print_header("VERIFICACIÓN FINAL")
            final_state = verify_objects_created(session)
            
            print(f"\n{Fore.CYAN}Estado final:{Style.RESET_ALL}")
            print(f"  Funciones: {initial_state['functions']} → {final_state['functions']} "
                  f"({Fore.GREEN}+{final_state['functions'] - initial_state['functions']}{Style.RESET_ALL})")
            print(f"  Triggers: {initial_state['triggers']} → {final_state['triggers']} "
                  f"({Fore.GREEN}+{final_state['triggers'] - initial_state['triggers']}{Style.RESET_ALL})")
            print(f"  Vistas: {initial_state['views']} → {final_state['views']} "
                  f"({Fore.GREEN}+{final_state['views'] - initial_state['views']}{Style.RESET_ALL})")
            
            # List all created objects
            list_created_objects(session)
            
            # Test functions
            test_functions(session)
            
            # Test views
            test_views(session)
            
            # Success summary
            print_header("RESUMEN")
            print_success("✅ Todos los objetos de base de datos fueron aplicados correctamente")
            print_success(f"✅ {final_state['functions']} funciones disponibles")
            print_success(f"✅ {final_state['triggers']} triggers activos")
            print_success(f"✅ {final_state['views']} vistas creadas")
            
            print(f"\n{Fore.GREEN}{'='*60}")
            print("🎉 ¡BASE DE DATOS ACTUALIZADA EXITOSAMENTE!")
            print(f"{'='*60}{Style.RESET_ALL}\n")
            
            return 0
            
    except Exception as e:
        print_error(f"\n❌ Error fatal: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
