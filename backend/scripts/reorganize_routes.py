#!/usr/bin/env python3
"""
Script para reorganizar archivos de routes que están fuera de sus módulos.
"""

import os
import shutil
from pathlib import Path
from typing import Dict, List

class RouteOrganizer:
    def __init__(self, backend_path: str):
        self.backend_path = Path(backend_path)
        self.routes_path = self.backend_path / "src" / "api" / "routes"
        
        # Mapeo de archivos a sus módulos correctos
        self.file_mapping = {
            'admin_institucion.py': 'academic',
            'coordinador_invitacion.py': 'auth',
            'avatar_service_complete.py': 'users',  # o crear módulo avatar
            'auth_main.py': 'auth',
            'dev_email.py': 'dev',  # crear módulo dev para herramientas de desarrollo
            'avatar.py': 'users',
            'debug.py': 'dev',
        }
        
        self.moves = []
        
    def create_modules(self):
        """Crear módulos faltantes si no existen"""
        modules_needed = set(self.file_mapping.values())
        
        for module in modules_needed:
            module_path = self.routes_path / module
            if not module_path.exists():
                print(f"📁 Creando módulo: {module}")
                module_path.mkdir(parents=True, exist_ok=True)
                
                # Crear __init__.py si no existe
                init_file = module_path / "__init__.py"
                if not init_file.exists():
                    init_file.touch()
    
    def move_files(self, dry_run=True):
        """Mover archivos a sus módulos correctos"""
        print("\n" + "="*80)
        print(f"{'🔍 SIMULACIÓN' if dry_run else '📦 MOVIENDO'} DE ARCHIVOS")
        print("="*80 + "\n")
        
        for filename, target_module in self.file_mapping.items():
            source = self.routes_path / filename
            target_dir = self.routes_path / target_module
            target = target_dir / filename
            
            if not source.exists():
                print(f"⚠️  Archivo no encontrado: {filename}")
                continue
            
            if target.exists():
                print(f"⚠️  Ya existe: {target_module}/{filename}")
                continue
            
            self.moves.append({
                'source': source,
                'target': target,
                'filename': filename,
                'module': target_module
            })
            
            if dry_run:
                print(f"   {filename} → {target_module}/")
            else:
                shutil.move(str(source), str(target))
                print(f"✅ {filename} → {target_module}/")
        
        return self.moves
    
    def generate_import_fix_script(self, moves: List[Dict]):
        """Generar script para corregir imports"""
        script_content = '''#!/usr/bin/env python3
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
'''
        
        # Agregar reemplazos basados en los movimientos
        for move in moves:
            filename_without_ext = move['filename'].replace('.py', '')
            old_import = filename_without_ext
            new_import = f"{move['module']}.{filename_without_ext}"
            script_content += f'        "{old_import}": "{new_import}",\n'
        
        script_content += '''    }
    
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
    
    print(f"\\n📊 Total de archivos actualizados: {fixed_count}")
    print("✅ Corrección de imports completada")

if __name__ == "__main__":
    main()
'''
        
        # Guardar script
        script_path = self.backend_path / "scripts" / "fix_imports_after_reorganize.py"
        with open(script_path, 'w') as f:
            f.write(script_content)
        
        # Hacer ejecutable
        os.chmod(script_path, 0o755)
        
        print(f"\n📝 Script de corrección de imports generado: {script_path}")
        return script_path

def main():
    print("\n" + "="*80)
    print("🔄 REORGANIZACIÓN DE ARCHIVOS EN API/ROUTES")
    print("="*80)
    
    backend_path = "/run/media/arch/Storage/SENA/Proyecto-Formativo/Acadify/backend"
    organizer = RouteOrganizer(backend_path)
    
    # Crear módulos necesarios
    organizer.create_modules()
    
    # Simulación primero
    print("\n1️⃣  PASO 1: SIMULACIÓN")
    moves = organizer.move_files(dry_run=True)
    
    if not moves:
        print("\n✅ No hay archivos para mover")
        return
    
    # Generar script de corrección de imports
    print("\n2️⃣  PASO 2: GENERANDO SCRIPT DE CORRECCIÓN DE IMPORTS")
    script_path = organizer.generate_import_fix_script(moves)
    
    # Confirmar antes de mover
    print("\n3️⃣  PASO 3: CONFIRMACIÓN")
    print(f"\n📋 Se moverán {len(moves)} archivos.")
    print("💡 Después de mover, ejecuta:")
    print(f"   python {script_path}")
    print("   para actualizar todos los imports automáticamente.")
    
    response = input("\n¿Proceder con el movimiento? (si/no): ").lower()
    
    if response in ['si', 's', 'yes', 'y']:
        print("\n4️⃣  PASO 4: MOVIENDO ARCHIVOS")
        organizer.move_files(dry_run=False)
        print("\n✅ Archivos movidos exitosamente")
        print(f"\n⚠️  IMPORTANTE: Ahora ejecuta:")
        print(f"   python {script_path}")
    else:
        print("\n❌ Operación cancelada")

if __name__ == "__main__":
    main()
