#!/usr/bin/env python3
"""
Script para extraer el esquema completo de la base de datos PostgreSQL.

Genera:
1. database_schema.sql - Archivo maestro con TODO el esquema
2. tables/*.sql - Un archivo por cada tabla con su DDL completo
3. database_documentation.md - Documentación en Markdown

Autor: Acadify Team
Fecha: 2025-10-29
"""

import os
from pathlib import Path
from sqlalchemy import text, inspect
from src.db.session import SessionLocal

# Directorios de salida
DOCS_DIR = Path(__file__).parent.parent / "Docs" / "database"
TABLES_DIR = DOCS_DIR / "tables"
MASTER_FILE = DOCS_DIR / "database_schema.sql"
DOCS_FILE = DOCS_DIR / "database_documentation.md"

# Asegurar que existen los directorios
DOCS_DIR.mkdir(parents=True, exist_ok=True)
TABLES_DIR.mkdir(parents=True, exist_ok=True)


def get_all_tables(db):
    """Obtiene lista de todas las tablas ordenadas alfabéticamente."""
    query = text("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public' 
        AND table_type = 'BASE TABLE'
        AND table_name != 'alembic_version'
        ORDER BY table_name;
    """)
    result = db.execute(query)
    return [row[0] for row in result]


def get_table_columns(db, table_name):
    """Obtiene todas las columnas de una tabla con sus tipos y constraints."""
    query = text("""
        SELECT 
            column_name,
            data_type,
            character_maximum_length,
            is_nullable,
            column_default
        FROM information_schema.columns
        WHERE table_schema = 'public' 
        AND table_name = :table_name
        ORDER BY ordinal_position;
    """)
    result = db.execute(query, {"table_name": table_name})
    return result.fetchall()


def get_primary_keys(db, table_name):
    """Obtiene las primary keys de una tabla."""
    query = text("""
        SELECT kcu.column_name
        FROM information_schema.table_constraints tc
        JOIN information_schema.key_column_usage kcu 
            ON tc.constraint_name = kcu.constraint_name
            AND tc.table_schema = kcu.table_schema
        WHERE tc.constraint_type = 'PRIMARY KEY'
        AND tc.table_schema = 'public'
        AND tc.table_name = :table_name
        ORDER BY kcu.ordinal_position;
    """)
    result = db.execute(query, {"table_name": table_name})
    return [row[0] for row in result]


def get_foreign_keys(db, table_name):
    """Obtiene las foreign keys de una tabla."""
    query = text("""
        SELECT
            kcu.column_name,
            ccu.table_name AS foreign_table_name,
            ccu.column_name AS foreign_column_name,
            tc.constraint_name
        FROM information_schema.table_constraints AS tc
        JOIN information_schema.key_column_usage AS kcu
            ON tc.constraint_name = kcu.constraint_name
            AND tc.table_schema = kcu.table_schema
        JOIN information_schema.constraint_column_usage AS ccu
            ON ccu.constraint_name = tc.constraint_name
            AND ccu.table_schema = tc.table_schema
        WHERE tc.constraint_type = 'FOREIGN KEY'
        AND tc.table_schema = 'public'
        AND tc.table_name = :table_name;
    """)
    result = db.execute(query, {"table_name": table_name})
    return result.fetchall()


def get_unique_constraints(db, table_name):
    """Obtiene los constraints UNIQUE de una tabla."""
    query = text("""
        SELECT
            tc.constraint_name,
            string_agg(kcu.column_name, ', ' ORDER BY kcu.ordinal_position) as columns
        FROM information_schema.table_constraints AS tc
        JOIN information_schema.key_column_usage AS kcu
            ON tc.constraint_name = kcu.constraint_name
            AND tc.table_schema = kcu.table_schema
        WHERE tc.constraint_type = 'UNIQUE'
        AND tc.table_schema = 'public'
        AND tc.table_name = :table_name
        GROUP BY tc.constraint_name;
    """)
    result = db.execute(query, {"table_name": table_name})
    return result.fetchall()


def get_check_constraints(db, table_name):
    """Obtiene los CHECK constraints de una tabla."""
    query = text("""
        SELECT
            tc.constraint_name,
            cc.check_clause
        FROM information_schema.table_constraints AS tc
        JOIN information_schema.check_constraints AS cc
            ON tc.constraint_name = cc.constraint_name
        WHERE tc.constraint_type = 'CHECK'
        AND tc.table_schema = 'public'
        AND tc.table_name = :table_name;
    """)
    result = db.execute(query, {"table_name": table_name})
    return result.fetchall()


def get_indexes(db, table_name):
    """Obtiene los índices de una tabla."""
    query = text("""
        SELECT
            indexname,
            indexdef
        FROM pg_indexes
        WHERE schemaname = 'public'
        AND tablename = :table_name
        AND indexname NOT LIKE '%_pkey';
    """)
    result = db.execute(query, {"table_name": table_name})
    return result.fetchall()


def format_column_type(data_type, char_max_length):
    """Formatea el tipo de dato de una columna."""
    if char_max_length and data_type in ('character varying', 'character'):
        return f"{data_type}({char_max_length})"
    return data_type


def generate_table_ddl(db, table_name):
    """Genera el DDL completo de una tabla."""
    lines = []
    lines.append(f"-- =====================================================")
    lines.append(f"-- Tabla: {table_name}")
    lines.append(f"-- =====================================================")
    lines.append("")
    
    # CREATE TABLE
    lines.append(f"CREATE TABLE IF NOT EXISTS {table_name} (")
    
    # Columnas
    columns = get_table_columns(db, table_name)
    primary_keys = get_primary_keys(db, table_name)
    
    column_defs = []
    for col in columns:
        col_name, data_type, char_max_len, is_nullable, col_default = col
        
        # Tipo
        col_type = format_column_type(data_type, char_max_len)
        
        # Definición
        col_def = f"    {col_name} {col_type}"
        
        # NOT NULL
        if is_nullable == 'NO':
            col_def += " NOT NULL"
        
        # DEFAULT
        if col_default:
            col_def += f" DEFAULT {col_default}"
        
        column_defs.append(col_def)
    
    lines.append(",\n".join(column_defs))
    
    # PRIMARY KEY
    if primary_keys:
        lines.append(f",\n    PRIMARY KEY ({', '.join(primary_keys)})")
    
    lines.append(");")
    lines.append("")
    
    # FOREIGN KEYS
    foreign_keys = get_foreign_keys(db, table_name)
    if foreign_keys:
        lines.append(f"-- Foreign Keys de {table_name}")
        for fk in foreign_keys:
            col_name, foreign_table, foreign_col, constraint_name = fk
            lines.append(
                f"ALTER TABLE {table_name} ADD CONSTRAINT {constraint_name} "
                f"FOREIGN KEY ({col_name}) REFERENCES {foreign_table}({foreign_col});"
            )
        lines.append("")
    
    # UNIQUE CONSTRAINTS
    unique_constraints = get_unique_constraints(db, table_name)
    if unique_constraints:
        lines.append(f"-- Unique Constraints de {table_name}")
        for constraint_name, columns in unique_constraints:
            lines.append(
                f"ALTER TABLE {table_name} ADD CONSTRAINT {constraint_name} "
                f"UNIQUE ({columns});"
            )
        lines.append("")
    
    # CHECK CONSTRAINTS
    check_constraints = get_check_constraints(db, table_name)
    if check_constraints:
        lines.append(f"-- Check Constraints de {table_name}")
        for constraint_name, check_clause in check_constraints:
            lines.append(
                f"ALTER TABLE {table_name} ADD CONSTRAINT {constraint_name} "
                f"CHECK ({check_clause});"
            )
        lines.append("")
    
    # INDEXES
    indexes = get_indexes(db, table_name)
    if indexes:
        lines.append(f"-- Índices de {table_name}")
        for idx_name, idx_def in indexes:
            lines.append(f"{idx_def};")
        lines.append("")
    
    return "\n".join(lines)


def generate_markdown_docs(db, tables):
    """Genera documentación en Markdown."""
    lines = []
    lines.append("# 📊 Documentación de Base de Datos - Acadify")
    lines.append("")
    lines.append(f"**Fecha de generación**: 2025-10-29")
    lines.append(f"**Total de tablas**: {len(tables)}")
    lines.append("")
    lines.append("---")
    lines.append("")
    
    # Índice
    lines.append("## 📋 Índice de Tablas")
    lines.append("")
    for i, table in enumerate(tables, 1):
        lines.append(f"{i}. [{table}](#{table.lower()})")
    lines.append("")
    lines.append("---")
    lines.append("")
    
    # Detalles de cada tabla
    for table in tables:
        lines.append(f"## {table}")
        lines.append("")
        
        # Columnas
        columns = get_table_columns(db, table)
        primary_keys = get_primary_keys(db, table)
        
        lines.append("### Columnas")
        lines.append("")
        lines.append("| Columna | Tipo | Nullable | Default | PK |")
        lines.append("|---------|------|----------|---------|-----|")
        
        for col in columns:
            col_name, data_type, char_max_len, is_nullable, col_default = col
            col_type = format_column_type(data_type, char_max_len)
            is_pk = "✅" if col_name in primary_keys else ""
            default = col_default if col_default else "-"
            
            lines.append(f"| {col_name} | {col_type} | {is_nullable} | {default} | {is_pk} |")
        
        lines.append("")
        
        # Foreign Keys
        foreign_keys = get_foreign_keys(db, table)
        if foreign_keys:
            lines.append("### Relaciones (Foreign Keys)")
            lines.append("")
            lines.append("| Columna | Referencia | Tabla Relacionada |")
            lines.append("|---------|-----------|-------------------|")
            
            for fk in foreign_keys:
                col_name, foreign_table, foreign_col, _ = fk
                lines.append(f"| {col_name} | {foreign_table}.{foreign_col} | {foreign_table} |")
            
            lines.append("")
        
        # Índices
        indexes = get_indexes(db, table)
        if indexes:
            lines.append("### Índices")
            lines.append("")
            for idx_name, idx_def in indexes:
                lines.append(f"- `{idx_name}`")
            lines.append("")
        
        lines.append("---")
        lines.append("")
    
    return "\n".join(lines)


def main():
    """Función principal."""
    print("🔍 EXTRAYENDO ESQUEMA DE BASE DE DATOS")
    print("=" * 60)
    
    db = SessionLocal()
    
    try:
        # Obtener todas las tablas
        tables = get_all_tables(db)
        print(f"\n📊 Total de tablas encontradas: {len(tables)}")
        
        # Generar archivo maestro
        print(f"\n📝 Generando archivo maestro: {MASTER_FILE}")
        master_content = []
        master_content.append("-- =====================================================")
        master_content.append("-- ESQUEMA COMPLETO DE BASE DE DATOS - ACADIFY")
        master_content.append("-- =====================================================")
        master_content.append("-- Generado automáticamente")
        master_content.append("-- Fecha: 2025-10-29")
        master_content.append(f"-- Total de tablas: {len(tables)}")
        master_content.append("-- =====================================================")
        master_content.append("")
        master_content.append("-- NOTA: Este archivo contiene el esquema completo.")
        master_content.append("-- Para DDL individual, ver carpeta tables/")
        master_content.append("")
        master_content.append("=" * 60)
        master_content.append("")
        
        # Generar DDL para cada tabla
        for i, table in enumerate(tables, 1):
            print(f"  {i:2d}/{len(tables)} - Procesando {table}...", end="")
            
            # DDL de la tabla
            table_ddl = generate_table_ddl(db, table)
            
            # Agregar al archivo maestro
            master_content.append(table_ddl)
            master_content.append("\n" + "=" * 60 + "\n")
            
            # Guardar archivo individual
            table_file = TABLES_DIR / f"{table}.sql"
            with open(table_file, 'w', encoding='utf-8') as f:
                f.write(table_ddl)
            
            print(" ✅")
        
        # Guardar archivo maestro
        with open(MASTER_FILE, 'w', encoding='utf-8') as f:
            f.write("\n".join(master_content))
        
        print(f"\n✅ Archivo maestro generado: {MASTER_FILE}")
        
        # Generar documentación Markdown
        print(f"\n📝 Generando documentación Markdown...")
        markdown_content = generate_markdown_docs(db, tables)
        with open(DOCS_FILE, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
        
        print(f"✅ Documentación generada: {DOCS_FILE}")
        
        # Resumen
        print("\n" + "=" * 60)
        print("✅ PROCESO COMPLETADO EXITOSAMENTE")
        print("=" * 60)
        print(f"\n📁 Archivos generados:")
        print(f"  1. {MASTER_FILE} - Esquema completo")
        print(f"  2. {DOCS_FILE} - Documentación Markdown")
        print(f"  3. {TABLES_DIR}/*.sql - {len(tables)} archivos individuales")
        print(f"\n📊 Estadísticas:")
        print(f"  - Total de tablas: {len(tables)}")
        print(f"  - Archivos SQL generados: {len(tables) + 1}")
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    main()
