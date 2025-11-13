#!/usr/bin/env python3
"""
Script para verificar índices en la BD y generar SQL para crear los faltantes.
"""

import subprocess
import json
from pathlib import Path

def run_sql_query(query: str) -> str:
    """Ejecuta una query SQL y retorna el resultado"""
    cmd = [
        'psql',
        '-d', 'acadify_db',
        '-U', 'admin',
        '-h', 'localhost',
        '-t',  # Solo datos, sin headers
        '-A',  # Sin alineación
        '-c', query
    ]
    
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        env={'PGPASSWORD': 'admin123'}
    )
    
    if result.returncode != 0:
        print(f"Error: {result.stderr}")
        return ""
    
    return result.stdout.strip()

def main():
    print("\n" + "="*80)
    print("📊 ANÁLISIS DE ÍNDICES EN LA BASE DE DATOS")
    print("="*80)
    
    # 1. Contar índices actuales
    print("\n1️⃣  ÍNDICES ACTUALES:")
    query_count = """
        SELECT COUNT(*) 
        FROM pg_indexes 
        WHERE schemaname = 'public';
    """
    total_indexes = run_sql_query(query_count)
    print(f"   Total de índices: {total_indexes}")
    
    # 2. Verificar FK sin índice
    print("\n2️⃣  VERIFICANDO FOREIGN KEYS:")
    fk_query = """
        SELECT
            tc.table_name || '.' || kcu.column_name as fk_column,
            CASE WHEN EXISTS(
                SELECT 1 FROM pg_indexes pi
                WHERE pi.tablename = tc.table_name
                AND (pi.indexdef LIKE '%' || kcu.column_name || '%'
                     OR pi.indexdef LIKE '%' || kcu.column_name || ',%')
            ) THEN 'YES' ELSE 'NO' END as has_index
        FROM information_schema.table_constraints AS tc
        JOIN information_schema.key_column_usage AS kcu
            ON tc.constraint_name = kcu.constraint_name
        WHERE tc.constraint_type = 'FOREIGN KEY'
        AND tc.table_schema = 'public'
        ORDER BY tc.table_name, kcu.column_name;
    """
    
    result = run_sql_query(fk_query)
    if result:
        lines = result.split('\n')
        total_fks = len(lines)
        fks_with_index = len([l for l in lines if '|YES' in l])
        fks_without_index = total_fks - fks_with_index
        
        print(f"   Total ForeignKeys: {total_fks}")
        print(f"   ✅ Con índice: {fks_with_index}")
        print(f"   ❌ Sin índice: {fks_without_index}")
        
        if fks_without_index > 0:
            print("\n   ⚠️  FK sin índice:")
            for line in lines:
                if '|NO' in line:
                    fk_name = line.split('|')[0]
                    print(f"      - {fk_name}")
    
    # 3. Generar script de índices
    print("\n3️⃣  GENERANDO SCRIPT SQL DE ÍNDICES:")
    
    migration_statements = []
    
    # Obtener FK sin índice para crear
    if result:
        for line in lines:
            if '|NO' in line:
                fk_full = line.split('|')[0]
                table, column = fk_full.split('.')
                idx_name = f"idx_{table}_{column}"
                stmt = f'CREATE INDEX IF NOT EXISTS {idx_name} ON "{table}" ("{column}");'
                migration_statements.append(stmt)
    
    # Índices para columnas de búsqueda frecuente
    search_indexes = [
        ("Usuario", "email", "Búsqueda de usuarios por email"),
        ("Usuario", "estado", "Filtrar usuarios por estado"),
        ("Curso", "estado", "Filtrar cursos por estado"),
        ("Curso", "codigo", "Búsqueda de cursos por código"),
        ("Examen", "estado", "Filtrar exámenes por estado"),
        ("Tarea", "estado", "Filtrar tareas por estado"),
        ("Mensaje", "fecha_envio", "Ordenar mensajes por fecha"),
        ("Estudiante", "estado", "Filtrar estudiantes por estado"),
        ("Docente", "estado", "Filtrar docentes por estado"),
    ]
    
    print("\n   📋 Índices para columnas de búsqueda:")
    for table, column, description in search_indexes:
        idx_name = f"idx_{table}_{column}"
        stmt = f'CREATE INDEX IF NOT EXISTS {idx_name} ON "{table}" ("{column}");'
        migration_statements.append(stmt)
        print(f"   - {idx_name}: {description}")
    
    # Índices compuestos para mejorar queries complejas
    composite_indexes = [
        ("Mensaje", ["chat_id", "fecha_envio"], "Mensajes por chat ordenados"),
        ("Examen", ["curso_id", "estado"], "Exámenes activos por curso"),
        ("Tarea", ["curso_id", "estado"], "Tareas activas por curso"),
        ("Tarea", ["curso_id", "fecha_limite"], "Tareas próximas por curso"),
        ("Clase", ["curso_id", "fecha_inicio"], "Clases ordenadas por fecha"),
        ("Material_Educativo", ["curso_id", "tipo"], "Materiales por tipo"),
        ("Chat", ["tipo", "estado"], "Chats activos por tipo"),
    ]
    
    print("\n   📋 Índices compuestos recomendados:")
    for table, columns, description in composite_indexes:
        idx_name = f"idx_{table}_{'_'.join(columns)}"
        cols_str = ', '.join([f'"{col}"' for col in columns])
        stmt = f'CREATE INDEX IF NOT EXISTS {idx_name} ON "{table}" ({cols_str});'
        migration_statements.append(stmt)
        print(f"   - {idx_name}: {description}")
    
    # Guardar script SQL
    migration_path = Path("create_missing_indexes.sql")
    with open(migration_path, 'w', encoding='utf-8') as f:
        f.write("-- Script de creación de índices para mejorar rendimiento\n")
        f.write("-- Generado automáticamente para Acadify\n")
        f.write(f"-- Total de índices: {len(migration_statements)}\n\n")
        f.write("BEGIN;\n\n")
        
        for i, stmt in enumerate(migration_statements, 1):
            f.write(f"-- Índice {i}/{len(migration_statements)}\n")
            f.write(stmt + "\n\n")
        
        f.write("COMMIT;\n\n")
        f.write("-- Verificar índices creados:\n")
        f.write("-- SELECT schemaname, tablename, indexname FROM pg_indexes WHERE schemaname = 'public' ORDER BY tablename;\n")
    
    print(f"\n   ✅ Script guardado en: {migration_path.absolute()}")
    print(f"   📊 Total de índices a crear: {len(migration_statements)}")
    
    # Resumen
    print("\n" + "="*80)
    print("📊 RESUMEN Y RECOMENDACIONES")
    print("="*80)
    print(f"\n✅ Índices a crear: {len(migration_statements)}")
    
    print("\n🚀 IMPACTO ESPERADO:")
    print("   - Reducción de 50-80% en tiempo de queries con JOIN")
    print("   - Mejora significativa en consultas con WHERE/ORDER BY")
    print("   - Reducción de uso de CPU y memoria")
    print("   - Mejor rendimiento en listados paginados")
    
    print("\n📝 APLICAR ÍNDICES:")
    print("   export PGPASSWORD='admin123'")
    print("   psql -d acadify_db -U admin -h localhost < create_missing_indexes.sql")
    
    print("\n🔍 VERIFICAR DESPUÉS:")
    print("   psql -d acadify_db -U admin -h localhost -c \"SELECT COUNT(*) FROM pg_indexes WHERE schemaname='public';\"")
    
    print("\n" + "="*80)

if __name__ == "__main__":
    main()
