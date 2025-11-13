#!/usr/bin/env python3
"""
Script para aplicar correcciones B904 en batch.

Uso:
    python scripts/fix_b904_batch.py
"""

import re
import subprocess
from pathlib import Path


def get_b904_violations() -> list[tuple[str, int]]:
    """Obtiene todas las violaciones B904 del proyecto."""
    result = subprocess.run(
        ["ruff", "check", "src/", "--select", "B904", "--output-format=concise"],
        capture_output=True,
        text=True,
    )
    
    if result.returncode == 0:
        print("✅ No hay violaciones B904")
        return []
    
    violations = []
    
    # Formato concise: path:line:col: CODE message
    for line in result.stdout.strip().split('\n'):
        if line and not line.startswith('warning:') and 'B904' in line:
            parts = line.split(':')
            if len(parts) >= 3:
                filepath = parts[0]
                line_num = int(parts[1])
                violations.append((filepath, line_num))
    
    return violations


def fix_b904_in_file(filepath: str, line_num: int) -> bool:
    """
    Intenta corregir una violación B904 en un archivo.
    
    Estrategia:
    1. Buscar el raise statement en o cerca de la línea indicada
    2. Determinar si el raise está en un except block
    3. Agregar 'from e' o 'from None' según contexto
    """
    path = Path(filepath)
    if not path.exists():
        return False
    
    lines = path.read_text().splitlines()
    
    # Encontrar el contexto del raise
    target_line = line_num - 1  # 0-indexed
    
    if target_line >= len(lines):
        return False
    
    # Buscar hacia atrás para encontrar el except
    except_var = None
    for i in range(target_line, max(0, target_line - 20), -1):
        line = lines[i].strip()
        
        # Patrón: except SomeError as var:
        match = re.match(r'except\s+(\w+)\s+as\s+(\w+):', line)
        if match:
            except_var = match.group(2)
            break
        
        # Patrón: except SomeError: (sin variable)
        if re.match(r'except\s+\w+:', line):
            except_var = None
            break
    
    # Buscar el raise statement
    raise_line = lines[target_line].rstrip()
    
    # Si no termina con paréntesis o comilla, buscar la línea de cierre
    if not raise_line.endswith((')','",', "',")):
        for i in range(target_line + 1, min(len(lines), target_line + 10)):
            if lines[i].strip().endswith(')'):
                target_line = i
                raise_line = lines[target_line].rstrip()
                break
    
    # Aplicar fix
    if except_var:
        # Hay variable de excepción -> usar from e/from var
        if not raise_line.endswith(f' from {except_var}'):
            lines[target_line] = f"{raise_line} from {except_var}"
    else:
        # No hay variable -> usar from None (exception transformation)
        if not raise_line.endswith(' from None'):
            lines[target_line] = f"{raise_line} from None"
    
    # Escribir de vuelta
    path.write_text('\n'.join(lines) + '\n')
    return True


def main():
    """Ejecuta el proceso de corrección."""
    print("🔍 Buscando violaciones B904...")
    violations = get_b904_violations()
    
    if not violations:
        return
    
    print(f"📋 Encontradas {len(violations)} violaciones B904")
    
    # Agrupar por archivo
    files_dict = {}
    for filepath, line_num in violations:
        if filepath not in files_dict:
            files_dict[filepath] = []
        files_dict[filepath].append(line_num)
    
    print(f"📁 Archivos afectados: {len(files_dict)}")
    
    # Mostrar resumen
    print("\n📊 Resumen por archivo:")
    for filepath, lines in sorted(files_dict.items(), key=lambda x: len(x[1]), reverse=True)[:10]:
        print(f"  {Path(filepath).name}: {len(lines)} errores")
    
    # Preguntar confirmación
    response = input("\n¿Aplicar correcciones automáticas? (y/N): ").strip().lower()
    
    if response != 'y':
        print("❌ Cancelado")
        return
    
    # Aplicar correcciones
    print("\n🔧 Aplicando correcciones...")
    fixed = 0
    failed = 0
    
    for filepath in files_dict:
        # Recargar violaciones para este archivo (pueden haber cambiado)
        result = subprocess.run(
            ["ruff", "check", filepath, "--select", "B904", "--output-format=concise"],
            capture_output=True,
            text=True,
        )
        
        if result.returncode == 0:
            continue
        
        file_violations = []
        for line in result.stdout.strip().split('\n'):
            if line and not line.startswith('warning:') and 'B904' in line:
                parts = line.split(':')
                if len(parts) >= 3:
                    file_violations.append(int(parts[1]))
        
        # Procesar de abajo hacia arriba para no desajustar líneas
        for line_num in sorted(file_violations, reverse=True):
            try:
                if fix_b904_in_file(filepath, line_num):
                    fixed += 1
                else:
                    failed += 1
            except Exception as e:
                print(f"  ❌ Error en {filepath}:{line_num} - {e}")
                failed += 1
    
    print(f"\n✅ Correcciones aplicadas: {fixed}")
    print(f"❌ Errores: {failed}")
    
    # Formatear con black
    print("\n🎨 Formateando con black...")
    subprocess.run(["black", "src/"], capture_output=True)
    
    # Verificación final
    print("\n🔍 Verificación final...")
    result = subprocess.run(
        ["ruff", "check", "src/", "--select", "B904", "--statistics"],
        capture_output=True,
        text=True,
    )
    
    print(result.stdout)
    
    if result.returncode == 0:
        print("\n🎉 ¡Todos los errores B904 corregidos!")
    else:
        print(f"\n⚠️ Quedan {result.stdout.split()[0] if result.stdout else '?'} errores B904")
        print("   Estos requieren revisión manual.")


if __name__ == "__main__":
    main()
