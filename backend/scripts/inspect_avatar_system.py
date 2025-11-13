#!/usr/bin/env python3
"""
Script para inspeccionar el sistema de avatares en la base de datos.
Analiza tablas, campos, relaciones y genera reporte completo.
"""

import sys
from pathlib import Path

# Agregar el directorio raíz al path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from sqlalchemy import inspect, text
from src.db.session import engine


def get_avatar_tables():
    """Obtiene todas las tablas relacionadas con avatares."""
    inspector = inspect(engine)
    all_tables = inspector.get_table_names()
    
    # Filtrar tablas relacionadas con avatares
    avatar_tables = [
        table for table in all_tables 
        if 'avatar' in table.lower()
    ]
    
    return sorted(avatar_tables)


def analyze_table(table_name: str):
    """Analiza una tabla específica y retorna información completa."""
    inspector = inspect(engine)
    
    # Obtener columnas
    columns = inspector.get_columns(table_name)
    
    # Obtener foreign keys
    foreign_keys = inspector.get_foreign_keys(table_name)
    
    # Obtener índices
    indexes = inspector.get_indexes(table_name)
    
    # Obtener primary keys
    pk_constraint = inspector.get_pk_constraint(table_name)
    
    # Obtener unique constraints
    unique_constraints = inspector.get_unique_constraints(table_name)
    
    # Contar registros
    with engine.connect() as conn:
        result = conn.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
        row_count = result.scalar()
    
    return {
        'table_name': table_name,
        'columns': columns,
        'foreign_keys': foreign_keys,
        'indexes': indexes,
        'primary_key': pk_constraint,
        'unique_constraints': unique_constraints,
        'row_count': row_count
    }


def print_table_analysis(analysis: dict):
    """Imprime el análisis de una tabla de forma legible."""
    print(f"\n{'='*80}")
    print(f"TABLA: {analysis['table_name']}")
    print(f"{'='*80}")
    print(f"Registros: {analysis['row_count']}")
    
    # Columnas
    print(f"\n📋 COLUMNAS ({len(analysis['columns'])} campos):")
    print(f"{'─'*80}")
    for col in analysis['columns']:
        nullable = "NULL" if col['nullable'] else "NOT NULL"
        default = f" DEFAULT {col['default']}" if col['default'] else ""
        print(f"  • {col['name']:30} {str(col['type']):20} {nullable:10}{default}")
    
    # Primary Key
    if analysis['primary_key'] and analysis['primary_key'].get('constrained_columns'):
        pk_cols = ', '.join(analysis['primary_key']['constrained_columns'])
        print(f"\n🔑 PRIMARY KEY: {pk_cols}")
    
    # Foreign Keys
    if analysis['foreign_keys']:
        print(f"\n🔗 FOREIGN KEYS ({len(analysis['foreign_keys'])}):")
        for fk in analysis['foreign_keys']:
            local_cols = ', '.join(fk['constrained_columns'])
            ref_table = fk['referred_table']
            ref_cols = ', '.join(fk['referred_columns'])
            on_delete = fk.get('ondelete', 'NO ACTION')
            print(f"  • {local_cols} → {ref_table}({ref_cols}) ON DELETE {on_delete}")
    
    # Unique Constraints
    if analysis['unique_constraints']:
        print(f"\n✨ UNIQUE CONSTRAINTS ({len(analysis['unique_constraints'])}):")
        for uc in analysis['unique_constraints']:
            cols = ', '.join(uc['column_names'])
            name = uc.get('name', 'unnamed')
            print(f"  • {name}: {cols}")
    
    # Indexes
    if analysis['indexes']:
        print(f"\n📇 INDEXES ({len(analysis['indexes'])}):")
        for idx in analysis['indexes']:
            cols = ', '.join(idx['column_names'])
            unique = "UNIQUE" if idx['unique'] else ""
            print(f"  • {idx['name']:40} ({cols}) {unique}")


def compare_with_model(table_name: str, analysis: dict):
    """Compara la tabla de BD con el modelo de SQLAlchemy."""
    from src.models.avatar import AvatarAsset, UserAvatar
    
    # Mapear tabla a modelo
    model_map = {
        'avatar_asset': AvatarAsset,
        'user_avatar': UserAvatar
    }
    
    if table_name not in model_map:
        print(f"\n⚠️  No hay modelo para la tabla '{table_name}'")
        return
    
    model = model_map[table_name]
    mapper = inspect(model)
    
    # Obtener campos del modelo
    model_columns = {col.name: col for col in mapper.columns}
    
    # Obtener campos de la BD
    db_columns = {col['name']: col for col in analysis['columns']}
    
    # Comparar
    print(f"\n🔍 COMPARACIÓN MODELO vs BASE DE DATOS:")
    print(f"{'─'*80}")
    
    # Campos en BD pero no en modelo
    missing_in_model = set(db_columns.keys()) - set(model_columns.keys())
    if missing_in_model:
        print(f"\n❌ CAMPOS EN BD PERO NO EN MODELO ({len(missing_in_model)}):")
        for field in sorted(missing_in_model):
            col = db_columns[field]
            print(f"  • {field:30} {str(col['type']):20}")
    
    # Campos en modelo pero no en BD
    missing_in_db = set(model_columns.keys()) - set(db_columns.keys())
    if missing_in_db:
        print(f"\n❌ CAMPOS EN MODELO PERO NO EN BD ({len(missing_in_db)}):")
        for field in sorted(missing_in_db):
            col = model_columns[field]
            print(f"  • {field:30} {str(col.type):20}")
    
    # Campos sincronizados
    synchronized = set(model_columns.keys()) & set(db_columns.keys())
    if not missing_in_model and not missing_in_db:
        print(f"\n✅ TODOS LOS CAMPOS SINCRONIZADOS ({len(synchronized)} campos)")
    else:
        print(f"\n✅ CAMPOS SINCRONIZADOS: {len(synchronized)}/{len(db_columns)}")
    
    return {
        'missing_in_model': list(missing_in_model),
        'missing_in_db': list(missing_in_db),
        'synchronized': list(synchronized),
        'sync_percentage': (len(synchronized) / len(db_columns) * 100) if db_columns else 0
    }


def generate_final_report(tables_data: list):
    """Genera reporte final consolidado."""
    print(f"\n{'='*80}")
    print("📊 REPORTE FINAL - SISTEMA DE AVATARES")
    print(f"{'='*80}")
    
    total_tables = len(tables_data)
    total_columns = sum(len(t['analysis']['columns']) for t in tables_data)
    total_records = sum(t['analysis']['row_count'] for t in tables_data)
    
    print(f"\n📈 ESTADÍSTICAS GENERALES:")
    print(f"  • Total de tablas: {total_tables}")
    print(f"  • Total de campos: {total_columns}")
    print(f"  • Total de registros: {total_records}")
    
    print(f"\n🗂️  DETALLE POR TABLA:")
    for table_data in tables_data:
        table_name = table_data['table_name']
        analysis = table_data['analysis']
        comparison = table_data.get('comparison')
        
        status = "✅"
        if comparison:
            if comparison['missing_in_model'] or comparison['missing_in_db']:
                status = "⚠️"
        
        print(f"  {status} {table_name:30} {len(analysis['columns']):3} campos  "
              f"{analysis['row_count']:6} registros", end="")
        
        if comparison:
            print(f"  [{comparison['sync_percentage']:.0f}% sync]")
        else:
            print()
    
    # Resumen de sincronización
    tables_with_comparison = [t for t in tables_data if t.get('comparison')]
    if tables_with_comparison:
        print(f"\n🔄 SINCRONIZACIÓN:")
        perfect_sync = sum(1 for t in tables_with_comparison 
                          if not t['comparison']['missing_in_model'] 
                          and not t['comparison']['missing_in_db'])
        
        print(f"  • Tablas perfectamente sincronizadas: {perfect_sync}/{len(tables_with_comparison)}")
        
        if perfect_sync < len(tables_with_comparison):
            print(f"  ⚠️  Se requiere sincronización en {len(tables_with_comparison) - perfect_sync} tabla(s)")
    
    print()


def main():
    """Función principal."""
    print("🔍 INSPECCIÓN DEL SISTEMA DE AVATARES")
    print("="*80)
    
    try:
        # Obtener tablas de avatares
        avatar_tables = get_avatar_tables()
        
        if not avatar_tables:
            print("❌ No se encontraron tablas de avatares en la base de datos")
            return False
        
        print(f"\n✅ Tablas encontradas: {', '.join(avatar_tables)}")
        
        # Analizar cada tabla
        tables_data = []
        for table_name in avatar_tables:
            print(f"\n🔎 Analizando tabla: {table_name}...")
            analysis = analyze_table(table_name)
            print_table_analysis(analysis)
            
            # Comparar con modelo si existe
            comparison = compare_with_model(table_name, analysis)
            
            tables_data.append({
                'table_name': table_name,
                'analysis': analysis,
                'comparison': comparison
            })
        
        # Generar reporte final
        generate_final_report(tables_data)
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error durante la inspección: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
