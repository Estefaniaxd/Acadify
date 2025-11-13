#!/usr/bin/env python3
"""
Script de auditoría completa: Base de datos vs Modelos SQLAlchemy
Encuentra todas las inconsistencias y genera reporte detallado
"""

import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_path))

from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import Session
from src.core.config import settings
from colorama import init, Fore, Style
import json

init(autoreset=True)

def print_header(title: str):
    print(f"\n{Fore.MAGENTA}{'='*80}")
    print(f"{title}")
    print(f"{'='*80}{Style.RESET_ALL}\n")

def print_success(msg: str):
    print(f"{Fore.GREEN}✅ {msg}{Style.RESET_ALL}")

def print_error(msg: str):
    print(f"{Fore.RED}❌ {msg}{Style.RESET_ALL}")

def print_warning(msg: str):
    print(f"{Fore.YELLOW}⚠️  {msg}{Style.RESET_ALL}")

def print_info(msg: str):
    print(f"{Fore.CYAN}ℹ️  {msg}{Style.RESET_ALL}")

def get_all_tables(inspector):
    """Obtiene todas las tablas de la base de datos"""
    return sorted(inspector.get_table_names())

def get_table_columns(inspector, table_name):
    """Obtiene todas las columnas de una tabla"""
    columns = inspector.get_columns(table_name)
    return {col['name']: str(col['type']) for col in columns}

def get_table_foreign_keys(inspector, table_name):
    """Obtiene todas las foreign keys de una tabla"""
    return inspector.get_foreign_keys(table_name)

def get_table_primary_keys(inspector, table_name):
    """Obtiene las primary keys de una tabla"""
    return inspector.get_pk_constraint(table_name)

def audit_critical_tables(inspector):
    """Audita las tablas críticas del sistema"""
    
    critical_tables = [
        'Usuario',
        'Estudiante',
        'Curso',
        'Grupo',
        'tareas',
        'entregas_tareas',
        'evaluaciones',
        'intentos_evaluacion',
        'preguntas_evaluacion',
        'respuestas_estudiante',
        'Comentario',
        'estudiantes_grupos',
    ]
    
    print_header("AUDITORÍA DE TABLAS CRÍTICAS")
    
    report = {}
    
    for table_name in critical_tables:
        try:
            print(f"\n{Fore.CYAN}{'─'*80}")
            print(f"📊 Tabla: {table_name}")
            print(f"{'─'*80}{Style.RESET_ALL}")
            
            columns = get_table_columns(inspector, table_name)
            fks = get_table_foreign_keys(inspector, table_name)
            pks = get_table_primary_keys(inspector, table_name)
            
            print(f"\n{Fore.YELLOW}Columnas ({len(columns)}):{Style.RESET_ALL}")
            for col_name, col_type in sorted(columns.items()):
                print(f"  • {col_name:<40} {col_type}")
            
            print(f"\n{Fore.YELLOW}Primary Keys:{Style.RESET_ALL}")
            if pks and pks.get('constrained_columns'):
                for pk in pks['constrained_columns']:
                    print(f"  🔑 {pk}")
            
            print(f"\n{Fore.YELLOW}Foreign Keys ({len(fks)}):{Style.RESET_ALL}")
            for fk in fks:
                print(f"  🔗 {fk['constrained_columns']} → {fk['referred_table']}.{fk['referred_columns']}")
            
            # Guardar en reporte
            report[table_name] = {
                'columns': columns,
                'primary_keys': pks.get('constrained_columns', []) if pks else [],
                'foreign_keys': fks,
                'column_count': len(columns),
                'exists': True
            }
            
            print_success(f"Tabla {table_name} auditada correctamente")
            
        except Exception as e:
            print_error(f"Error al auditar {table_name}: {str(e)}")
            report[table_name] = {
                'exists': False,
                'error': str(e)
            }
    
    return report

def find_column_inconsistencies(report):
    """Encuentra inconsistencias comunes en nombres de columnas"""
    
    print_header("ANÁLISIS DE INCONSISTENCIAS")
    
    inconsistencies = []
    
    # Patrones comunes de inconsistencias
    patterns = [
        ('nombre', 'nombres'),
        ('apellido', 'apellidos'),
        ('correo_electronico', 'correo_institucional'),
        ('email', 'correo_institucional'),
        ('calificacion_obtenida', 'puntuacion_obtenida'),
        ('intento_id', 'id'),
    ]
    
    for table_name, table_data in report.items():
        if not table_data.get('exists'):
            continue
        
        columns = table_data.get('columns', {})
        
        for wrong, correct in patterns:
            if wrong in columns:
                inconsistencies.append({
                    'table': table_name,
                    'found': wrong,
                    'expected': correct,
                    'type': columns[wrong],
                    'severity': 'high'
                })
    
    if inconsistencies:
        print_warning(f"Encontradas {len(inconsistencies)} posibles inconsistencias:")
        for inc in inconsistencies:
            print(f"  • Tabla '{inc['table']}': columna '{inc['found']}' debería ser '{inc['expected']}'")
    else:
        print_success("No se encontraron inconsistencias en patrones comunes")
    
    return inconsistencies

def generate_sql_corrections(report, inconsistencies):
    """Genera correcciones SQL basadas en las inconsistencias encontradas"""
    
    print_header("CORRECCIONES RECOMENDADAS PARA SQL")
    
    corrections = []
    
    # Para archivos SQL (funciones, vistas, triggers)
    sql_files = ['01_funciones.sql', '02_triggers.sql', '03_vistas.sql']
    
    print(f"{Fore.CYAN}Reemplazos necesarios en archivos SQL:{Style.RESET_ALL}\n")
    
    # Basado en el reporte, generar reemplazos
    replacements = []
    
    # Usuario: nombres/apellidos
    if 'Usuario' in report:
        cols = report['Usuario']['columns']
        if 'nombres' in cols and 'apellidos' in cols:
            replacements.append({
                'pattern': "u.nombre || ' ' || u.apellido",
                'replacement': "u.nombres || ' ' || u.apellidos",
                'reason': 'Usuario usa nombres/apellidos (plural)'
            })
            replacements.append({
                'pattern': 'u.correo_electronico',
                'replacement': 'u.correo_institucional',
                'reason': 'Usuario usa correo_institucional'
            })
    
    # intentos_evaluacion: puntuacion_obtenida
    if 'intentos_evaluacion' in report:
        cols = report['intentos_evaluacion']['columns']
        if 'puntuacion_obtenida' in cols:
            replacements.append({
                'pattern': 'calificacion_obtenida',
                'replacement': 'puntuacion_obtenida',
                'reason': 'intentos_evaluacion usa puntuacion_obtenida'
            })
        if 'id' in cols:
            replacements.append({
                'pattern': 'ie.intento_id',
                'replacement': 'ie.id',
                'reason': 'intentos_evaluacion usa id como PK'
            })
    
    for i, repl in enumerate(replacements, 1):
        print(f"{i}. {Fore.YELLOW}{repl['pattern']}{Style.RESET_ALL}")
        print(f"   → {Fore.GREEN}{repl['replacement']}{Style.RESET_ALL}")
        print(f"   Razón: {repl['reason']}\n")
    
    # Generar comando sed
    print(f"{Fore.CYAN}Comandos para aplicar correcciones:{Style.RESET_ALL}\n")
    
    for sql_file in sql_files:
        print(f"# Corregir {sql_file}")
        for repl in replacements:
            # Escapar caracteres especiales para sed
            pattern_escaped = repl['pattern'].replace('/', '\\/')
            replacement_escaped = repl['replacement'].replace('/', '\\/')
            print(f"sed -i 's/{pattern_escaped}/{replacement_escaped}/g' {sql_file}")
        print()
    
    return replacements

def check_model_table_alignment():
    """Verifica que los modelos SQLAlchemy coincidan con las tablas"""
    
    print_header("VERIFICACIÓN MODELOS vs BASE DE DATOS")
    
    try:
        from src.models import Base
        from sqlalchemy import MetaData
        
        # Obtener metadata de los modelos
        metadata = Base.metadata
        
        print(f"{Fore.CYAN}Modelos registrados en SQLAlchemy:{Style.RESET_ALL}\n")
        
        for table_name, table in sorted(metadata.tables.items()):
            print(f"📄 {table_name}")
            print(f"   Columnas: {len(table.columns)}")
            print(f"   PKs: {[c.name for c in table.primary_key.columns]}")
            print(f"   FKs: {len(table.foreign_keys)}")
            print()
        
        print_success(f"Total de modelos registrados: {len(metadata.tables)}")
        
    except Exception as e:
        print_error(f"Error al verificar modelos: {str(e)}")

def save_report(report, filename='database_audit_report.json'):
    """Guarda el reporte en un archivo JSON"""
    
    report_path = Path(__file__).parent / filename
    
    try:
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, default=str)
        
        print_success(f"Reporte guardado en: {report_path}")
        
    except Exception as e:
        print_error(f"Error al guardar reporte: {str(e)}")

def main():
    """Main execution"""
    
    print_header("🔍 AUDITORÍA COMPLETA: BASE DE DATOS vs MODELOS")
    
    # Conectar a la base de datos
    print_info(f"Conectando a base de datos: {settings.POSTGRES_DB}")
    db_url = settings.database_url if hasattr(settings, 'database_url') else settings.DATABASE_URL
    engine = create_engine(db_url)
    inspector = inspect(engine)
    
    # 1. Auditar tablas críticas
    report = audit_critical_tables(inspector)
    
    # 2. Encontrar inconsistencias
    inconsistencies = find_column_inconsistencies(report)
    
    # 3. Generar correcciones SQL
    replacements = generate_sql_corrections(report, inconsistencies)
    
    # 4. Verificar alineación de modelos
    check_model_table_alignment()
    
    # 5. Guardar reporte
    save_report({
        'tables': report,
        'inconsistencies': inconsistencies,
        'recommended_replacements': replacements
    })
    
    # Resumen final
    print_header("📊 RESUMEN FINAL")
    
    total_tables = len([t for t in report.values() if t.get('exists')])
    total_columns = sum(t.get('column_count', 0) for t in report.values() if t.get('exists'))
    
    print(f"✅ Tablas auditadas: {total_tables}")
    print(f"✅ Total de columnas: {total_columns}")
    print(f"⚠️  Inconsistencias encontradas: {len(inconsistencies)}")
    print(f"🔧 Correcciones recomendadas: {len(replacements)}")
    
    if inconsistencies:
        print(f"\n{Fore.YELLOW}⚠️  Se encontraron inconsistencias que deben corregirse.{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}   Revisa las correcciones recomendadas arriba.{Style.RESET_ALL}")
        return 1
    else:
        print(f"\n{Fore.GREEN}🎉 ¡Base de datos y modelos están alineados!{Style.RESET_ALL}")
        return 0

if __name__ == "__main__":
    sys.exit(main())
