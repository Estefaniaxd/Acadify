#!/usr/bin/env python3
"""
Script para migrar imports de modelos legacy a modelos activos

Reemplaza:
- from src.models.academic.tarea import Tarea → from src.models.academic.tarea import Tarea
- from src.models.academic.tarea import EntregaTarea → from src.models.academic.tarea import EntregaTarea
"""

import os
import re
from pathlib import Path

# Directorio raíz del backend
BACKEND_DIR = Path(__file__).parent.parent

# Patrones a reemplazar
REPLACEMENTS = [
    (
        r'from\s+src\.models\.classes\.tarea\s+import\s+Tarea',
        'from src.models.academic.tarea import Tarea'
    ),
    (
        r'from\s+\.\.\.models\.classes\.tarea\s+import\s+Tarea',
        'from ...models.academic.tarea import Tarea'
    ),
    (
        r'from\s+src\.models\.classes\.entregar_tarea\s+import\s+EntregarTarea',
        'from src.models.academic.tarea import EntregaTarea'
    ),
    (
        r'from\s+\.\.\.models\.classes\.entregar_tarea\s+import\s+EntregarTarea',
        'from ...models.academic.tarea import EntregaTarea'
    ),
]

def migrate_imports():
    """Migra imports de modelos legacy a activos"""
    
    files_modified = []
    
    # Buscar archivos Python
    for py_file in BACKEND_DIR.rglob('*.py'):
        # Saltar archivos en directorios especiales
        if any(x in str(py_file) for x in ['__pycache__', '.venv', 'venv', 'migrations']):
            continue
        
        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            modified = False
            
            # Aplicar reemplazos
            for pattern, replacement in REPLACEMENTS:
                new_content = re.sub(pattern, replacement, content)
                if new_content != content:
                    content = new_content
                    modified = True
            
            # Guardar si hubo cambios
            if modified:
                with open(py_file, 'w', encoding='utf-8') as f:
                    f.write(content)
                files_modified.append(py_file)
                print(f"✅ Actualizado: {py_file.relative_to(BACKEND_DIR)}")
        
        except Exception as e:
            print(f"❌ Error procesando {py_file}: {e}")
    
    return files_modified

def main():
    print("=" * 80)
    print("🔄 MIGRACIÓN DE IMPORTS - MODELOS LEGACY → ACTIVOS")
    print("=" * 80)
    print()
    
    files_modified = migrate_imports()
    
    print()
    print("=" * 80)
    print(f"✅ Migración completada: {len(files_modified)} archivos modificados")
    print("=" * 80)
    
    if files_modified:
        print("\nArchivos actualizados:")
        for f in files_modified:
            print(f"  - {f.relative_to(BACKEND_DIR)}")
    
    print("\n⚠️  PRÓXIMOS PASOS:")
    print("1. Revisar cambios con: git diff")
    print("2. Ejecutar tests: pytest")
    print("3. Si todo OK, eliminar:")
    print("   - src/models/classes/tarea.py")
    print("   - src/models/classes/entregar_tarea.py")
    print("   - src/crud/classes/tarea.py")

if __name__ == "__main__":
    main()
