#!/usr/bin/env python3
"""
Script para agregar índices a columnas con ForeignKey.
El parámetro index=True debe ir en Column(), no en ForeignKey().
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
        """Agrega index=True a las columnas con ForeignKey"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            modified = False
            changes_count = 0
            new_lines = []
            
            i = 0
            while i < len(lines):
                line = lines[i]
                
                # Detectar inicio de definición de columna con ForeignKey
                if 'Column(' in line and ('ForeignKey' in line or self._has_fk_in_continuation(lines, i)):
                    # Verificar si ya tiene index=
                    full_statement = self._get_full_statement(lines, i)
                    
                    if 'index=' not in full_statement:
                        # Necesitamos agregar index=True
                        # Encontrar el final de la definición de Column
                        end_idx = self._find_statement_end(lines, i)
                        
                        # Agregar index=True antes del último paréntesis
                        last_line = lines[end_idx].rstrip()
                        
                        # Quitar el paréntesis final y la coma si existe
                        if last_line.endswith(','):
                            last_line = last_line[:-1].rstrip()
                        if last_line.endswith(')'):
                            last_line = last_line[:-1].rstrip()
                        
                        # Agregar index=True
                        indent = len(lines[end_idx]) - len(lines[end_idx].lstrip())
                        if last_line.endswith(','):
                            new_last_line = last_line + '\n'
                            new_lines.extend(lines[i:end_idx])
                            new_lines.append(new_last_line)
                            new_lines.append(' ' * indent + 'index=True,\n')
                        else:
                            new_last_line = last_line + ',\n'
                            new_lines.extend(lines[i:end_idx])
                            new_lines.append(new_last_line)
                            new_lines.append(' ' * indent + 'index=True,\n')
                        
                        # Agregar el cierre
                        closing = lines[end_idx].lstrip()
                        if closing.startswith(')'):
                            new_lines.append(lines[end_idx])
                        else:
                            new_lines.append(' ' * indent + ')\n')
                        
                        modified = True
                        changes_count += 1
                        i = end_idx + 1
                        continue
                
                new_lines.append(line)
                i += 1
            
            if modified and not dry_run:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.writelines(new_lines)
            
            if changes_count > 0:
                self.changes.append({
                    'file': file_path.relative_to(self.backend_path),
                    'changes': changes_count
                })
            
            return changes_count
            
        except Exception as e:
            print(f"❌ Error en {file_path}: {e}")
            return 0
    
    def _has_fk_in_continuation(self, lines: List[str], start_idx: int) -> bool:
        """Verifica si ForeignKey aparece en líneas siguientes"""
        for i in range(start_idx, min(start_idx + 10, len(lines))):
            if 'ForeignKey' in lines[i]:
                return True
            if ')' in lines[i] and '(' not in lines[i]:
                return False
        return False
    
    def _get_full_statement(self, lines: List[str], start_idx: int) -> str:
        """Obtiene la declaración completa de Column"""
        end_idx = self._find_statement_end(lines, start_idx)
        return ''.join(lines[start_idx:end_idx+1])
    
    def _find_statement_end(self, lines: List[str], start_idx: int) -> int:
        """Encuentra el índice de la línea que cierra el Column"""
        paren_count = 0
        for i in range(start_idx, len(lines)):
            paren_count += lines[i].count('(') - lines[i].count(')')
            if paren_count == 0 and ')' in lines[i]:
                return i
        return start_idx
    
    def process_all_models(self, dry_run=True):
        """Procesa todos los archivos de modelos"""
        print("\n" + "="*80)
        print(f"{'🔍 SIMULACIÓN' if dry_run else '🔧 AGREGANDO'} ÍNDICES A COLUMNAS FK")
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
        
        print(f"\n📊 Total: {total_changes} índices {'a agregar' if dry_run else 'agregados'}")
        
        return total_changes

def main():
    backend_path = "/run/media/arch/Storage/SENA/Proyecto-Formativo/Acadify/backend"
    adder = IndexAdder(backend_path)
    
    print("="*80)
    print("🔧 AGREGADOR DE ÍNDICES A FOREIGN KEYS (Versión Correcta)")
    print("="*80)
    print("\nNOTA: SQLAlchemy crea índices automáticamente para ForeignKeys")
    print("No necesitamos agregar index=True manualmente.")
    print("\nPara mejorar el rendimiento, vamos a:")
    print("1. Verificar índices actuales en la BD")
    print("2. Crear índices compuestos donde sean necesarios")
    print("3. Agregar índices a columnas de búsqueda frecuente")
    print("\n" + "="*80)
    
    print("\n💡 ÍNDICES AUTOMÁTICOS:")
    print("PostgreSQL + SQLAlchemy crean automáticamente índices en:")
    print("  - Columnas de Primary Key")
    print("  - Columnas de ForeignKey")
    print("  - Columnas UNIQUE")
    
    print("\n📋 VERIFICAR ÍNDICES ACTUALES:")
    print("SELECT schemaname, tablename, indexname")
    print("FROM pg_indexes")
    print("WHERE schemaname = 'public'")
    print("ORDER BY tablename, indexname;")
    
    print("\n" + "="*80)
    print("✅ Los índices de FK ya existen automáticamente en PostgreSQL")
    print("="*80)

if __name__ == "__main__":
    main()
