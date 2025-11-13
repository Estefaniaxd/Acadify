#!/usr/bin/env python3
"""
SyntaxFixer - Corrector Automático de Sintaxis Post-Validación
==============================================================

Corrige problemas de sintaxis después de eliminar campos:
- Comas faltantes
- Indentación incorrecta
- Paréntesis desbalanceados

Principio: Separation of Concerns
- FieldValidator elimina campos
- SyntaxFixer repara sintaxis

Author: GitHub Copilot
Date: 1 nov 2025
"""

import re
from pathlib import Path
from typing import List, Tuple


class SyntaxFixer:
    """Corrector de sintaxis para tests"""
    
    def __init__(self, test_dir: Path):
        self.test_dir = test_dir
        self.fixes_applied = 0
        
    def fix_missing_commas(self, content: str) -> str:
        """Corrige comas faltantes después de eliminar campos"""
        
        # Pattern: línea que termina sin coma antes de otra asignación
        # ejemplo:
        #   codigo_acceso="ABC"
        #   max_intentos=3,
        # debe ser:
        #   codigo_acceso="ABC",
        #   max_intentos=3,
        
        lines = content.split('\n')
        fixed_lines = []
        
        for i, line in enumerate(lines):
            # Detectar si es una asignación de parámetro (dentro de constructor)
            if '=' in line and not line.strip().startswith('#'):
                # Si la línea NO termina con coma, paréntesis o corchete
                stripped = line.rstrip()
                
                if stripped and not stripped.endswith((',', '(', ')', '[', ']', '{', '}')):
                    # Verificar si la siguiente línea es otra asignación o cierre
                    if i + 1 < len(lines):
                        next_line = lines[i + 1].strip()
                        
                        # Si la siguiente línea es una asignación, agregar coma
                        if next_line and ('=' in next_line or next_line.startswith(')')):
                            # Solo agregar coma si estamos dentro de un constructor
                            indent_level = len(line) - len(line.lstrip())
                            if indent_level > 0:  # Está indentado = dentro de algo
                                line = line.rstrip() + ','
                                self.fixes_applied += 1
                                
            fixed_lines.append(line)
            
        return '\n'.join(fixed_lines)
        
    def fix_double_commas(self, content: str) -> str:
        """Elimina comas dobles"""
        original = content
        content = re.sub(r',,+', ',', content)
        
        if content != original:
            changes = original.count(',,') - content.count(',,')
            self.fixes_applied += changes
            
        return content
        
    def fix_comma_before_close_paren(self, content: str) -> str:
        """Elimina comas antes de paréntesis de cierre"""
        original = content
        content = re.sub(r',(\s*)\)', r'\1)', content)
        
        if content != original:
            self.fixes_applied += 1
            
        return content
        
    def fix_indentation(self, content: str) -> str:
        """Corrige indentación básica"""
        lines = content.split('\n')
        fixed_lines = []
        
        for i, line in enumerate(lines):
            # Si la línea anterior termina en coma y esta está mal indentada
            if i > 0 and lines[i-1].rstrip().endswith(','):
                if line.strip() and not line.startswith(' '):
                    # Copiar indentación de línea anterior
                    prev_indent = len(lines[i-1]) - len(lines[i-1].lstrip())
                    line = ' ' * prev_indent + line.lstrip()
                    self.fixes_applied += 1
                    
            fixed_lines.append(line)
            
        return '\n'.join(fixed_lines)
        
    def fix_file(self, file_path: Path) -> bool:
        """Corrige un archivo completo"""
        content = file_path.read_text()
        original = content
        
        # Aplicar correcciones en orden
        content = self.fix_double_commas(content)
        content = self.fix_comma_before_close_paren(content)
        content = self.fix_missing_commas(content)
        content = self.fix_indentation(content)
        
        if content != original:
            file_path.write_text(content)
            return True
            
        return False
        
    def fix_all(self) -> List[Tuple[Path, bool]]:
        """Corrige todos los archivos de test"""
        results = []
        
        test_files = list(self.test_dir.glob("test_*.py"))
        
        for test_file in test_files:
            fixed = self.fix_file(test_file)
            results.append((test_file, fixed))
            
        return results


def main():
    """Función principal"""
    import os
    
    backend_dir = Path(os.getcwd())
    test_dir = backend_dir / "TEST"
    
    print("🔧 SyntaxFixer - Reparando sintaxis...")
    print("=" * 70)
    
    fixer = SyntaxFixer(test_dir)
    results = fixer.fix_all()
    
    print(f"\n✅ {fixer.fixes_applied} correcciones de sintaxis aplicadas")
    
    # Verificar sintaxis
    print("\n🔍 Verificando sintaxis final...")
    all_valid = True
    
    for file_path, was_fixed in results:
        if was_fixed:
            print(f"   📝 {file_path.name}")
            
        try:
            compile(file_path.read_text(), file_path.name, 'exec')
        except SyntaxError as e:
            print(f"   ❌ {file_path.name}: {e}")
            all_valid = False
            
    if all_valid:
        print("\n   ✅ ¡Sintaxis válida en todos los archivos!")
        print("\n" + "=" * 70)
        print("🎯 Ejecuta los tests:")
        print("venv/bin/python -m pytest TEST/ -v --tb=short")
    else:
        print("\n   ⚠️  Algunos archivos requieren corrección manual")


if __name__ == "__main__":
    main()
