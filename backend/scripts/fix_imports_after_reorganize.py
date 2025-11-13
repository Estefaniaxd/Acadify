#!/usr/bin/env python3
"""
Script generado automáticamente para corregir imports después de reorganizar archivos.
"""

import os
import re
from pathlib import Path

def fix_imports_in_file(file_path: Path, replacements: dict):
    """Actualizar imports en un archivo"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        for old_import, new_import in replacements.items():
            # Patrón para diferentes tipos de imports
            patterns = [
                (f"from src.api.routes.{old_import}", f"from src.api.routes.{new_import}"),
                (f"from .{old_import}", f"from .{new_import}"),
                (f"import src.api.routes.{old_import}", f"import src.api.routes.{new_import}"),
            ]
            
            for old_pattern, new_pattern in patterns:
                content = content.replace(old_pattern, new_pattern)
        
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        return False
    except Exception as e:
        print(f"Error en {file_path}: {e}")
        return False

def main():
    backend_path = Path(__file__).parent.parent
    
    # Mapeo de cambios de imports
    replacements = {
        "admin_institucion": "academic.admin_institucion",
        "coordinador_invitacion": "auth.coordinador_invitacion",
        "avatar_service_complete": "users.avatar_service_complete",
        "auth_main": "auth.auth_main",
        "dev_email": "dev.dev_email",
        "avatar": "users.avatar",
        "debug": "dev.debug",
    }
    
    print("🔧 Corrigiendo imports en todo el proyecto...")
    print("="*80)
    
    # Buscar todos los archivos Python
    files_to_check = []
    for root, dirs, files in os.walk(backend_path / "src"):
        # Ignorar carpetas específicas
        dirs[:] = [d for d in dirs if d not in ['__pycache__', '.pytest_cache', 'venv']]
        
        for file in files:
            if file.endswith('.py'):
                files_to_check.append(Path(root) / file)
    
    fixed_count = 0
    for file_path in files_to_check:
        if fix_imports_in_file(file_path, replacements):
            fixed_count += 1
            print(f"✅ Actualizado: {file_path.relative_to(backend_path)}")
    
    print(f"\n📊 Total de archivos actualizados: {fixed_count}")
    print("✅ Corrección de imports completada")

if __name__ == "__main__":
    main()
