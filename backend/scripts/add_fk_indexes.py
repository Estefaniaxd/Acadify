#!/usr/bin/env python3
"""
Script para agregar índices automáticamente a todos los ForeignKey en los modelos.
"""

import re
from pathlib import Path
from typing import List, Tuple

class IndexAdder:
    def __init__(self, backend_path: str):
        self.backend_path = Path(backend_path)
        self.models_path = self.backend_path / "src" / "models"
        self.changes = []
        
    def add_indexes_to_file(self, file_path: Path, dry_run=True) -> int:
        """Agrega index=True a todos los ForeignKey en un archivo"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            changes_count = 0
            
            # Patrón para encontrar ForeignKey sin index=True
            # Busca ForeignKey(...) que no tenga index=True dentro de los paréntesis
            fk_pattern = r'ForeignKey\([^)]*\)'
            
            def add_index(match):
                nonlocal changes_count
                fk_call = match.group(0)
                
                # Si ya tiene index=True o index=False, no modificar
                if 'index=' in fk_call:
                    return fk_call
                
                # Agregar index=True antes del paréntesis de cierre
                if fk_call.endswith(')'):
                    new_fk = fk_call[:-1] + ', index=True)'
                    changes_count += 1
                    return new_fk
                return fk_call
            
            content = re.sub(fk_pattern, add_index, content)
            
            if content != original_content and not dry_run:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
            
            if changes_count > 0:
                self.changes.append({
                    'file': file_path.relative_to(self.backend_path),
                    'changes': changes_count
                })
            
            return changes_count
            
        except Exception as e:
            print(f"❌ Error en {file_path}: {e}")
            return 0
    
    def process_all_models(self, dry_run=True):
        """Procesa todos los archivos de modelos"""
        print("\n" + "="*80)
        print(f"{'🔍 SIMULACIÓN' if dry_run else '🔧 AGREGANDO'} DE ÍNDICES A FOREIGN KEYS")
        print("="*80 + "\n")
        
        model_files = list(self.models_path.rglob("*.py"))
        total_changes = 0
        
        for file in model_files:
            if file.name == "__init__.py":
                continue
            
            changes = self.add_indexes_to_file(file, dry_run=dry_run)
            if changes > 0:
                total_changes += changes
                status = "📋" if dry_run else "✅"
                print(f"{status} {file.relative_to(self.backend_path)}: {changes} índices")
        
        print(f"\n📊 Total de índices {'a agregar' if dry_run else 'agregados'}: {total_changes}")
        
        return total_changes
    
    def generate_migration(self):
        """Genera una migración de Alembic para agregar los índices"""
        if not self.changes:
            return
        
        migration_content = '''"""Add indexes to all foreign keys

Revision ID: add_fk_indexes
Revises: a9a32870107a
Create Date: 2025-10-28 20:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'add_fk_indexes'
down_revision = 'a9a32870107a'
branch_labels = None
depends_on = None

def upgrade():
    """Add indexes to foreign key columns for better query performance"""
    
    # Nota: Los índices se crearán automáticamente en nuevas instalaciones
    # porque agregamos index=True a los modelos.
    # 
    # Para bases de datos existentes, SQLAlchemy detectará los cambios
    # cuando se ejecute: alembic revision --autogenerate -m "add fk indexes"
    pass

def downgrade():
    """Remove indexes from foreign key columns"""
    pass
'''
        
        migration_path = self.backend_path / "alembic" / "versions" / "add_fk_indexes.py"
        with open(migration_path, 'w') as f:
            f.write(migration_content)
        
        print(f"\n📝 Migración creada: {migration_path}")
        print("💡 Para aplicar los índices a la BD, ejecuta:")
        print("   alembic revision --autogenerate -m 'add foreign key indexes'")
        print("   alembic upgrade head")

def main():
    print("\n" + "="*80)
    print("🔧 AGREGADOR AUTOMÁTICO DE ÍNDICES A FOREIGN KEYS")
    print("="*80)
    
    backend_path = "/run/media/arch/Storage/SENA/Proyecto-Formativo/Acadify/backend"
    adder = IndexAdder(backend_path)
    
    # Simulación primero
    print("\n1️⃣  PASO 1: SIMULACIÓN")
    total = adder.process_all_models(dry_run=True)
    
    if total == 0:
        print("\n✅ No hay ForeignKeys sin índices")
        return
    
    print(f"\n📋 Se agregarán índices a {total} ForeignKeys")
    response = input("\n¿Proceder? (si/no): ").lower()
    
    if response in ['si', 's', 'yes', 'y']:
        print("\n2️⃣  PASO 2: AGREGANDO ÍNDICES")
        adder.changes = []  # Reset
        adder.process_all_models(dry_run=False)
        
        print("\n3️⃣  PASO 3: GENERANDO MIGRACIÓN")
        adder.generate_migration()
        
        print("\n✅ Índices agregados exitosamente")
        print("\n⚠️  SIGUIENTE PASO:")
        print("   1. Revisar los cambios con git diff")
        print("   2. Generar migración: alembic revision --autogenerate -m 'add fk indexes'")
        print("   3. Aplicar: alembic upgrade head")
    else:
        print("\n❌ Operación cancelada")

if __name__ == "__main__":
    main()
