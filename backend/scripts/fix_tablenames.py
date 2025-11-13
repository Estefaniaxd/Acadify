"""
Script para corregir __tablename__ de PascalCase a snake_case.

Este script identifica todos los modelos con __tablename__ en PascalCase
y los convierte a snake_case para coincidir con las tablas reales en PostgreSQL.
"""

import re
from pathlib import Path
from typing import Dict, List, Tuple

def pascal_to_snake(name: str) -> str:
    """Convierte PascalCase a snake_case."""
    # Insertar guión bajo antes de mayúsculas (excepto la primera)
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    # Insertar guión bajo antes de mayúsculas seguidas de minúsculas
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()

def find_tablename_issues() -> List[Tuple[Path, str, str]]:
    """
    Encuentra todos los archivos con __tablename__ en PascalCase.
    
    Returns:
        Lista de tuplas (archivo, tablename_actual, tablename_correcto)
    """
    issues = []
    base_path = Path(__file__).parent.parent  # backend/
    models_path = base_path / "src" / "models"
    
    for py_file in models_path.rglob("*.py"):
        if "__pycache__" in str(py_file):
            continue
            
        content = py_file.read_text(encoding='utf-8')
        
        # Buscar __tablename__ = "PascalCase"
        matches = re.findall(r'__tablename__\s*=\s*"([A-Z][a-zA-Z]*)"', content)
        
        for tablename in matches:
            snake_case = pascal_to_snake(tablename)
            if tablename != snake_case:
                issues.append((py_file, tablename, snake_case))
    
    return issues

def fix_file(file_path: Path, old_name: str, new_name: str) -> bool:
    """
    Corrige un archivo reemplazando el tablename.
    
    Returns:
        True si se hizo el cambio, False si no se encontró
    """
    content = file_path.read_text(encoding='utf-8')
    old_line = f'__tablename__ = "{old_name}"'
    new_line = f'__tablename__ = "{new_name}"'
    
    if old_line in content:
        new_content = content.replace(old_line, new_line)
        file_path.write_text(new_content, encoding='utf-8')
        return True
    return False

def main():
    print("🔍 Buscando __tablename__ en PascalCase...\n")
    
    issues = find_tablename_issues()
    
    if not issues:
        print("✅ No se encontraron problemas. Todos los __tablename__ están en snake_case.")
        return
    
    print(f"📋 Encontrados {len(issues)} modelos a corregir:\n")
    
    base_path = Path(__file__).parent.parent
    for file_path, old_name, new_name in issues:
        try:
            relative_path = file_path.relative_to(base_path)
        except ValueError:
            relative_path = file_path
        print(f"  {relative_path}")
        print(f"    {old_name} → {new_name}")
    
    print("\n" + "="*70)
    response = input("\n¿Desea aplicar estos cambios? (s/n): ").lower().strip()
    
    if response != 's':
        print("❌ Operación cancelada.")
        return
    
    print("\n🔧 Aplicando cambios...\n")
    
    success_count = 0
    fail_count = 0
    
    base_path = Path(__file__).parent.parent
    for file_path, old_name, new_name in issues:
        try:
            relative_path = file_path.relative_to(base_path)
        except ValueError:
            relative_path = file_path
        if fix_file(file_path, old_name, new_name):
            print(f"  ✅ {relative_path}")
            success_count += 1
        else:
            print(f"  ❌ {relative_path} - No se pudo aplicar el cambio")
            fail_count += 1
    
    print("\n" + "="*70)
    print(f"\n✅ Cambios aplicados: {success_count}")
    if fail_count > 0:
        print(f"❌ Fallos: {fail_count}")
    
    print("\n💡 Recomendaciones:")
    print("  1. Ejecuta: python scripts/verify_models_vs_sql.py")
    print("  2. Verifica que los errores críticos se hayan reducido")
    print("  3. Si todo está bien, haz commit de los cambios")

if __name__ == "__main__":
    main()
