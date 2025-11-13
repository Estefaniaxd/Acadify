#!/usr/bin/env python3
"""
Script de corrección rápida automática para problemas comunes
encontrados en los tests de gamificación.

Uso:
    python quick_fix.py [--dry-run] [--all]
"""

import re
from pathlib import Path
import argparse
import shutil
from datetime import datetime

# Mapeo de campos incorrectos a correctos
FIELD_MAPPINGS = {
    'Usuario': {
        'email': 'correo_institucional',
        'nombre': 'nombres',
        'apellido': 'apellidos',
        'hashed_password': 'password_hash',
        'id': 'usuario_id'
    },
    'UsuarioPuntos': {
        'nivel': None,  # Este campo no existe, debe removerse
        'puntos_nivel_actual': None  # Este campo no existe
    },
    'HistorialPuntos': {
        'puntos': 'cambio',
        'descripcion': 'motivo'
    },
    'UsuarioInsignia': {
        'fecha_obtencion': 'fecha_otorgada'
    }
}

# Tablas que deben estar en tables_to_create
REQUIRED_TABLES = [
    'Usuario',
    'UsuarioPuntos',
    'HistorialPuntos',
    'Insignia',
    'UsuarioInsignia',  # Comúnmente olvidada
    'EtiquetaPerfil',
    'UsuarioEtiqueta',
    'TiendaItem',
    'TransaccionTienda',
    'InventarioUsuario',
    'RachaUsuario',
    'HistorialRacha',
    'RecompensaRacha'
]

def backup_file(file_path):
    """Crea un backup del archivo."""
    backup_dir = Path(__file__).parent / 'backups'
    backup_dir.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_path = backup_dir / f"{file_path.name}.{timestamp}.bak"
    
    shutil.copy2(file_path, backup_path)
    return backup_path

def fix_field_mappings(content, model_name):
    """Corrige mapeos de campos para un modelo específico."""
    if model_name not in FIELD_MAPPINGS:
        return content, 0
    
    mappings = FIELD_MAPPINGS[model_name]
    fixes = 0
    
    for old_field, new_field in mappings.items():
        if new_field is None:
            # Campo debe removerse
            # Patrón: field_name=value,
            pattern = rf'\b{old_field}\s*=\s*[^,\n]+,?\s*'
            old_content = content
            content = re.sub(pattern, '', content)
            if content != old_content:
                fixes += 1
        else:
            # Reemplazar nombre de campo
            # En kwargs: old_field=
            pattern = rf'\b{old_field}\s*='
            old_content = content
            content = re.sub(pattern, f'{new_field}=', content)
            if content != old_content:
                fixes += 1
            
            # En acceso: .old_field
            pattern = rf'\.{old_field}\b'
            old_content = content
            content = re.sub(pattern, f'.{new_field}', content)
            if content != old_content:
                fixes += 1
    
    return content, fixes

def fix_test_file(file_path, dry_run=True):
    """Corrige problemas en archivo de tests."""
    with open(file_path) as f:
        content = f.read()
    
    original_content = content
    total_fixes = 0
    fixes_detail = []
    
    # Fix 1: Corregir campos de Usuario
    content, fixes = fix_field_mappings(content, 'Usuario')
    if fixes > 0:
        total_fixes += fixes
        fixes_detail.append(f"Usuario fields: {fixes}")
    
    # Fix 2: Corregir campos de UsuarioPuntos
    content, fixes = fix_field_mappings(content, 'UsuarioPuntos')
    if fixes > 0:
        total_fixes += fixes
        fixes_detail.append(f"UsuarioPuntos fields: {fixes}")
    
    # Fix 3: Corregir campos de HistorialPuntos
    content, fixes = fix_field_mappings(content, 'HistorialPuntos')
    if fixes > 0:
        total_fixes += fixes
        fixes_detail.append(f"HistorialPuntos fields: {fixes}")
    
    # Fix 4: Agregar await a llamadas async faltantes
    pattern = r'^(\s+)(\w+\s*=\s*)(\w+_service\.\w+\([^)]*\))$'
    def add_await(match):
        indent, assignment, call = match.groups()
        if 'await' not in assignment:
            return f"{indent}{assignment}await {call}"
        return match.group(0)
    
    old_content = content
    content = re.sub(pattern, add_await, content, flags=re.MULTILINE)
    if content != old_content:
        total_fixes += 1
        fixes_detail.append("Added await to service calls")
    
    if content != original_content:
        if dry_run:
            print(f"  [DRY RUN] Would fix {total_fixes} issues: {', '.join(fixes_detail)}")
            return False
        else:
            backup_path = backup_file(file_path)
            with open(file_path, 'w') as f:
                f.write(content)
            print(f"  ✅ Fixed {total_fixes} issues: {', '.join(fixes_detail)}")
            print(f"     Backup: {backup_path}")
            return True
    else:
        print(f"  ℹ️  No issues found")
        return False

def fix_conftest_tables(conftest_path, dry_run=True):
    """Verifica y corrige la lista de tablas en conftest."""
    with open(conftest_path) as f:
        content = f.read()
    
    # Buscar tables_to_create
    match = re.search(
        r'tables_to_create\s*=\s*\[(.*?)\]',
        content,
        re.DOTALL
    )
    
    if not match:
        print("  ⚠️  No se encontró tables_to_create")
        return False
    
    current_tables_str = match.group(1)
    current_tables = [
        t.strip().strip('"').strip("'")
        for t in re.findall(r'["\'](\w+)["\']', current_tables_str)
    ]
    
    missing_tables = [t for t in REQUIRED_TABLES if t not in current_tables]
    
    if missing_tables:
        if dry_run:
            print(f"  [DRY RUN] Would add missing tables: {', '.join(missing_tables)}")
            return False
        else:
            # Agregar tablas faltantes
            new_tables = current_tables + missing_tables
            new_tables_str = ',\n        '.join(f"'{t}'" for t in new_tables)
            
            new_content = content.replace(
                match.group(0),
                f"tables_to_create = [\n        {new_tables_str}\n    ]"
            )
            
            backup_path = backup_file(conftest_path)
            with open(conftest_path, 'w') as f:
                f.write(new_content)
            
            print(f"  ✅ Added {len(missing_tables)} missing tables")
            print(f"     Tables: {', '.join(missing_tables)}")
            print(f"     Backup: {backup_path}")
            return True
    else:
        print("  ℹ️  All required tables present")
        return False

def main():
    parser = argparse.ArgumentParser(description='Quick fix para tests de gamificación')
    parser.add_argument('--dry-run', action='store_true', help='Mostrar cambios sin aplicar')
    parser.add_argument('--all', action='store_true', help='Corregir todos los archivos')
    parser.add_argument('--file', type=str, help='Archivo específico a corregir')
    
    args = parser.parse_args()
    
    print("""
╔════════════════════════════════════════════════════════════════════════════╗
║                    🔧 QUICK FIX - TESTS DE GAMIFICACIÓN                    ║
╚════════════════════════════════════════════════════════════════════════════╝
""")
    
    if args.dry_run:
        print("⚠️  Modo DRY RUN - No se aplicarán cambios\n")
    
    base_path = Path(__file__).parent.parent
    
    # Corregir conftest.py
    print("📄 Verificando conftest.py...")
    conftest_path = base_path / 'conftest.py'
    if conftest_path.exists():
        fix_conftest_tables(conftest_path, dry_run=args.dry_run)
    print()
    
    # Corregir archivos de tests
    if args.file:
        files_to_fix = [base_path / args.file]
    elif args.all:
        files_to_fix = list(base_path.glob('test_*.py'))
    else:
        files_to_fix = [base_path / 'test_puntos_api.py']
    
    print(f"📄 Verificando {len(files_to_fix)} archivo(s) de tests...\n")
    
    for file_path in files_to_fix:
        if not file_path.exists():
            print(f"  ⚠️  Archivo no encontrado: {file_path}")
            continue
        
        print(f"  {file_path.name}:")
        fix_test_file(file_path, dry_run=args.dry_run)
        print()
    
    print("="*80)
    if args.dry_run:
        print("💡 Para aplicar los cambios, ejecuta sin --dry-run:")
        print(f"   python {Path(__file__).name} --all")
    else:
        print("✅ Correcciones aplicadas!")
        print("   Los archivos originales están respaldados en backups/")
        print("\n   Siguiente paso: ejecutar tests")
        print("   pytest tests/gamification/test_puntos_api.py -v")
    print()

if __name__ == "__main__":
    main()
