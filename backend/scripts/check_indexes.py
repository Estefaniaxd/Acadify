#!/usr/bin/env python3
"""
Script para verificar índices en la BD y crear los que falten para mejorar rendimiento.
"""

import asyncio
import asyncpg
from pathlib import Path
import json

class IndexAnalyzer:
    def __init__(self):
        self.db_url = "postgresql://admin:admin123@localhost/acadify_db"
        
    async def check_indexes(self):
        """Verifica índices actuales en la BD"""
        conn = await asyncpg.connect(self.db_url)
        
        print("\n" + "="*80)
        print("📊 ANÁLISIS DE ÍNDICES EN LA BASE DE DATOS")
        print("="*80)
        
        # 1. Índices actuales
        print("\n1️⃣  ÍNDICES ACTUALES:")
        query = """
            SELECT 
                schemaname,
                tablename,
                indexname,
                indexdef
            FROM pg_indexes
            WHERE schemaname = 'public'
            ORDER BY tablename, indexname;
        """
        indexes = await conn.fetch(query)
        print(f"   Total de índices: {len(indexes)}")
        
        # Agrupar por tabla
        tables_with_indexes = {}
        for idx in indexes:
            table = idx['tablename']
            if table not in tables_with_indexes:
                tables_with_indexes[table] = []
            tables_with_indexes[table].append(idx['indexname'])
        
        print(f"   Tablas con índices: {len(tables_with_indexes)}")
        
        # 2. Foreign Keys sin índice
        print("\n2️⃣  VERIFICANDO FOREIGN KEYS:")
        fk_query = """
            SELECT
                tc.table_name,
                kcu.column_name,
                ccu.table_name AS foreign_table_name,
                ccu.column_name AS foreign_column_name,
                EXISTS(
                    SELECT 1 FROM pg_indexes pi
                    WHERE pi.tablename = tc.table_name
                    AND pi.indexdef LIKE '%' || kcu.column_name || '%'
                ) as has_index
            FROM information_schema.table_constraints AS tc
            JOIN information_schema.key_column_usage AS kcu
                ON tc.constraint_name = kcu.constraint_name
                AND tc.table_schema = kcu.table_schema
            JOIN information_schema.constraint_column_usage AS ccu
                ON ccu.constraint_name = tc.constraint_name
                AND ccu.table_schema = tc.table_schema
            WHERE tc.constraint_type = 'FOREIGN KEY'
            AND tc.table_schema = 'public'
            ORDER BY tc.table_name, kcu.column_name;
        """
        foreign_keys = await conn.fetch(fk_query)
        
        fks_without_index = [fk for fk in foreign_keys if not fk['has_index']]
        fks_with_index = [fk for fk in foreign_keys if fk['has_index']]
        
        print(f"   Total ForeignKeys: {len(foreign_keys)}")
        print(f"   ✅ Con índice: {len(fks_with_index)}")
        print(f"   ❌ Sin índice: {len(fks_without_index)}")
        
        if fks_without_index:
            print("\n   ⚠️  FK sin índice:")
            for fk in fks_without_index[:10]:  # Mostrar solo primeras 10
                print(f"      - {fk['table_name']}.{fk['column_name']} -> {fk['foreign_table_name']}")
            if len(fks_without_index) > 10:
                print(f"      ... y {len(fks_without_index) - 10} más")
        
        # 3. Columnas frecuentemente consultadas sin índice
        print("\n3️⃣  COLUMNAS QUE NECESITAN ÍNDICES:")
        
        # Columnas comunes que se usan en WHERE/JOIN
        common_search_columns = [
            ('Usuario', 'email'),
            ('Usuario', 'estado'),
            ('Curso', 'estado'),
            ('Curso', 'codigo'),
            ('Examen', 'estado'),
            ('Tarea', 'estado'),
            ('Mensaje', 'fecha_envio'),
            ('Estudiante', 'estado'),
            ('Docente', 'estado'),
        ]
        
        needed_indexes = []
        for table, column in common_search_columns:
            check_query = f"""
                SELECT EXISTS(
                    SELECT 1 FROM pg_indexes pi
                    WHERE pi.tablename = '{table}'
                    AND pi.indexdef LIKE '%{column}%'
                ) as has_index;
            """
            try:
                result = await conn.fetchval(check_query)
                if not result:
                    needed_indexes.append((table, column))
                    print(f"   ❌ {table}.{column} - Sin índice")
            except:
                pass
        
        # 4. Generar script de creación de índices
        print("\n4️⃣  GENERANDO SCRIPT DE MIGRACIÓN:")
        
        migration_statements = []
        
        # Índices para FK sin índice
        for fk in fks_without_index:
            idx_name = f"idx_{fk['table_name']}_{fk['column_name']}"
            stmt = f"CREATE INDEX IF NOT EXISTS {idx_name} ON \"{fk['table_name']}\" (\"{fk['column_name']}\");"
            migration_statements.append(stmt)
        
        # Índices para columnas de búsqueda
        for table, column in needed_indexes:
            idx_name = f"idx_{table}_{column}"
            stmt = f"CREATE INDEX IF NOT EXISTS {idx_name} ON \"{table}\" (\"{column}\");"
            migration_statements.append(stmt)
        
        # Índices compuestos útiles
        composite_indexes = [
            ("Mensaje", ["chat_id", "fecha_envio"], "Para consultas de mensajes por chat ordenados por fecha"),
            ("Examen", ["curso_id", "estado"], "Para listar exámenes activos por curso"),
            ("Tarea", ["curso_id", "estado"], "Para listar tareas activas por curso"),
            ("Estudiante", ["usuario_id", "estado"], "Para consultas de estudiantes activos"),
        ]
        
        print("\n   📋 Índices compuestos recomendados:")
        for table, columns, description in composite_indexes:
            idx_name = f"idx_{table}_{'_'.join(columns)}"
            cols_str = ', '.join([f'"{col}"' for col in columns])
            stmt = f"CREATE INDEX IF NOT EXISTS {idx_name} ON \"{table}\" ({cols_str});"
            migration_statements.append(stmt)
            print(f"   - {idx_name}: {description}")
        
        # Guardar script de migración
        migration_path = Path("create_missing_indexes.sql")
        with open(migration_path, 'w') as f:
            f.write("-- Script de creación de índices para mejorar rendimiento\n")
            f.write("-- Generado automáticamente\n\n")
            f.write("BEGIN;\n\n")
            for stmt in migration_statements:
                f.write(stmt + "\n")
            f.write("\nCOMMIT;\n")
        
        print(f"\n   ✅ Script guardado en: {migration_path}")
        print(f"   📊 Total de índices a crear: {len(migration_statements)}")
        
        # 5. Resumen y recomendaciones
        print("\n" + "="*80)
        print("📊 RESUMEN")
        print("="*80)
        print(f"✅ Índices actuales: {len(indexes)}")
        print(f"❌ FK sin índice: {len(fks_without_index)}")
        print(f"📋 Índices a crear: {len(migration_statements)}")
        
        print("\n🚀 IMPACTO ESPERADO:")
        print("   - Reducción de 50-70% en tiempo de queries con JOIN")
        print("   - Mejora en consultas con WHERE en columnas indexadas")
        print("   - Reducción de uso de CPU en queries complejas")
        
        print("\n📝 SIGUIENTES PASOS:")
        print("   1. Revisar: cat create_missing_indexes.sql")
        print("   2. Aplicar: psql -d acadify_db -U admin < create_missing_indexes.sql")
        print("   3. Verificar: SELECT * FROM pg_stat_user_indexes;")
        
        await conn.close()

async def main():
    analyzer = IndexAnalyzer()
    await analyzer.check_indexes()

if __name__ == "__main__":
    asyncio.run(main())
