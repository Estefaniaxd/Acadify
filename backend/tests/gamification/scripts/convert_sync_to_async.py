#!/usr/bin/env python3
"""
Script para encontrar y corregir automáticamente llamadas síncronas
que deben ser async en servicios y endpoints.

Uso:
    python convert_sync_to_async.py [--dry-run] [--file path/to/file.py]
"""

import re
from pathlib import Path
import argparse

def find_sync_calls(file_path):
    """Encuentra llamadas síncronas que deben ser async."""
    with open(file_path) as f:
        content = f.read()
        lines = content.split('\n')
    
    issues = []
    
    for i, line in enumerate(lines, 1):
        # Buscar db.query()
        if 'db.query(' in line and 'async' not in lines[max(0, i-5):i]:
            issues.append({
                'line': i,
                'type': 'sync_query',
                'code': line.strip(),
                'file': file_path
            })
        
        # Buscar user_crud.get_by_id sin await
        if re.search(r'(\w+_crud|crud)\.\w+\([^)]*\)(?!\s*\))', line):
            if 'await' not in line:
                issues.append({
                    'line': i,
                    'type': 'crud_without_await',
                    'code': line.strip(),
                    'file': file_path
                })
        
        # Buscar Session en lugar de AsyncSession
        if re.search(r'def \w+.*\(.*db:\s*Session', line):
            issues.append({
                'line': i,
                'type': 'sync_session_type',
                'code': line.strip(),
                'file': file_path
            })
    
    return issues

def suggest_fix(issue):
    """Sugiere una corrección para el problema."""
    if issue['type'] == 'sync_query':
        # Convertir db.query() a select()
        model_match = re.search(r'db\.query\((\w+)\)', issue['code'])
        if model_match:
            model = model_match.group(1)
            return f"stmt = select({model}); result = await db.execute(stmt); return result.scalars().all()"
    
    elif issue['type'] == 'crud_without_await':
        return f"await {issue['code']}"
    
    elif issue['type'] == 'sync_session_type':
        return issue['code'].replace('Session', 'AsyncSession')
    
    return "Manual review required"

def scan_directory(directory, pattern='*.py'):
    """Escanea un directorio en busca de problemas."""
    all_issues = []
    
    for file_path in Path(directory).rglob(pattern):
        # Ignorar __pycache__, venv, etc
        if any(skip in str(file_path) for skip in ['__pycache__', 'venv', '.venv', 'alembic']):
            continue
        
        issues = find_sync_calls(file_path)
        if issues:
            all_issues.extend(issues)
    
    return all_issues

def print_report(issues):
    """Imprime un reporte de los problemas encontrados."""
    if not issues:
        print("✅ ¡No se encontraron problemas de sync/async!")
        return
    
    print("\n" + "="*80)
    print("REPORTE DE PROBLEMAS SYNC/ASYNC")
    print("="*80 + "\n")
    
    # Agrupar por archivo
    by_file = {}
    for issue in issues:
        file_str = str(issue['file'])
        if file_str not in by_file:
            by_file[file_str] = []
        by_file[file_str].append(issue)
    
    print(f"📊 Total de problemas: {len(issues)} en {len(by_file)} archivos\n")
    
    for file_path, file_issues in sorted(by_file.items()):
        print(f"📄 {file_path}")
        print("-" * 80)
        
        for issue in file_issues:
            icon = "🔴" if issue['type'] == 'sync_query' else "🟡"
            print(f"  {icon} Línea {issue['line']}: {issue['type']}")
            print(f"     Código: {issue['code']}")
            print(f"     Sugerencia: {suggest_fix(issue)}")
            print()
    
    print("\n" + "="*80)
    print("RESUMEN POR TIPO")
    print("="*80)
    
    by_type = {}
    for issue in issues:
        t = issue['type']
        by_type[t] = by_type.get(t, 0) + 1
    
    for issue_type, count in sorted(by_type.items()):
        print(f"  • {issue_type}: {count}")
    
    print("\n")

def auto_fix_file(file_path, dry_run=True):
    """Intenta corregir automáticamente un archivo."""
    with open(file_path) as f:
        content = f.read()
    
    original = content
    fixes_applied = 0
    
    # Fix 1: Importar select si no existe
    if 'db.query(' in content and 'from sqlalchemy import select' not in content:
        # Agregar import después del último import de sqlalchemy
        import_pattern = r'(from sqlalchemy[^\n]+\n)'
        matches = list(re.finditer(import_pattern, content))
        if matches:
            last_import = matches[-1]
            insert_pos = last_import.end()
            content = content[:insert_pos] + "from sqlalchemy import select\n" + content[insert_pos:]
            fixes_applied += 1
    
    # Fix 2: Reemplazar Session con AsyncSession en type hints
    content = re.sub(
        r'\bdb:\s*Session\b',
        'db: AsyncSession',
        content
    )
    if content != original:
        fixes_applied += 1
    
    # Fix 3: Agregar await antes de CRUD calls (conservador)
    # Solo si la línea no tiene await y es claramente un CRUD call
    lines = content.split('\n')
    new_lines = []
    
    for line in lines:
        if re.search(r'^\s*\w+\s*=\s*\w+_crud\.\w+\(', line) and 'await' not in line:
            # Agregar await
            indent = len(line) - len(line.lstrip())
            new_line = ' ' * indent + 'await ' + line.lstrip()
            new_lines.append(new_line)
            if not dry_run:
                fixes_applied += 1
        else:
            new_lines.append(line)
    
    content = '\n'.join(new_lines)
    
    if dry_run:
        print(f"🔍 [DRY RUN] Se aplicarían {fixes_applied} correcciones a {file_path}")
        return False
    else:
        if fixes_applied > 0:
            with open(file_path, 'w') as f:
                f.write(content)
            print(f"✅ Se aplicaron {fixes_applied} correcciones a {file_path}")
            return True
        return False

def main():
    parser = argparse.ArgumentParser(description='Encuentra y corrige problemas sync/async')
    parser.add_argument('--dry-run', action='store_true', help='Solo muestra los cambios sin aplicarlos')
    parser.add_argument('--file', type=str, help='Archivo específico a analizar')
    parser.add_argument('--fix', action='store_true', help='Intenta corregir automáticamente')
    parser.add_argument('--dir', type=str, default='src/services', help='Directorio a escanear')
    
    args = parser.parse_args()
    
    if args.file:
        print(f"🔍 Analizando {args.file}...")
        issues = find_sync_calls(Path(args.file))
    else:
        print(f"🔍 Escaneando directorio {args.dir}...")
        issues = scan_directory(args.dir)
    
    print_report(issues)
    
    if args.fix and issues:
        print("\n" + "="*80)
        print("APLICANDO CORRECCIONES AUTOMÁTICAS")
        print("="*80 + "\n")
        
        files_to_fix = set(issue['file'] for issue in issues)
        
        for file_path in files_to_fix:
            auto_fix_file(file_path, dry_run=args.dry_run)

if __name__ == "__main__":
    main()
