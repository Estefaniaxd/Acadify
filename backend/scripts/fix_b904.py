#!/usr/bin/env python3
"""
Script para corregir automáticamente errores B904 (raise without from).
Agrega 'from e' o 'from None' según el contexto.
"""

import re
from pathlib import Path
from typing import List, Tuple


def fix_b904_in_file(filepath: str) -> Tuple[bool, int]:
    """
    Corrige errores B904 en un archivo.
    
    B904: Within an except clause, raise exceptions with 
          `raise ... from err` or `raise ... from None`
    """
    path = Path(filepath)
    if not path.exists():
        print(f"❌ Archivo no encontrado: {filepath}")
        return False, 0
    
    content = path.read_text(encoding='utf-8')
    original_content = content
    lines = content.split('\n')
    
    modified = False
    count = 0
    i = 0
    
    while i < len(lines):
        line = lines[i]
        
        # Detectar contexto de except con variable
        # except SomeError as e:
        except_match = re.match(r'(\s*)except\s+(\w+(?:\s*\|\s*\w+)*)\s+as\s+(\w+):', line)
        
        if except_match:
            indent = except_match.group(1)
            exception_var = except_match.group(3)  # e.g., 'e'
            
            # Buscar el raise dentro del except block
            j = i + 1
            except_indent_len = len(indent)
            
            while j < len(lines):
                next_line = lines[j]
                
                # Si la línea no está indentada más que el except, salimos
                if next_line.strip() and not next_line.startswith(indent + '    '):
                    break
                
                # Buscar raise HTTPException o cualquier raise
                raise_match = re.match(
                    rf'{indent}    (\s*)raise\s+([\w\.]+)\s*\(',
                    next_line
                )
                
                if raise_match:
                    # Verificar si ya tiene 'from'
                    # Buscar el cierre del paréntesis
                    paren_count = 1
                    full_raise = next_line
                    k = j + 1
                    
                    # Contar paréntesis para encontrar el final del raise
                    for char in next_line[next_line.index('(') + 1:]:
                        if char == '(':
                            paren_count += 1
                        elif char == ')':
                            paren_count -= 1
                    
                    # Si no está balanceado, seguir leyendo líneas
                    while paren_count > 0 and k < len(lines):
                        full_raise += '\n' + lines[k]
                        for char in lines[k]:
                            if char == '(':
                                paren_count += 1
                            elif char == ')':
                                paren_count -= 1
                                if paren_count == 0:
                                    break
                        k += 1
                    
                    # Verificar si ya tiene 'from'
                    if ' from ' not in full_raise:
                        # Encontrar la última línea del raise
                        last_raise_line_idx = k - 1 if k > j else j
                        
                        # Agregar 'from e' al final
                        if lines[last_raise_line_idx].rstrip().endswith(')'):
                            lines[last_raise_line_idx] = (
                                lines[last_raise_line_idx].rstrip() + f' from {exception_var}'
                            )
                            modified = True
                            count += 1
                    
                    break  # Solo el primer raise en el except block
                
                j += 1
        
        i += 1
    
    if modified:
        new_content = '\n'.join(lines)
        path.write_text(new_content, encoding='utf-8')
        return True, count
    
    return False, 0


# Archivos críticos a corregir
CRITICAL_FILES = [
    "src/services/auth/auth_service.py",
    "src/services/auth/token_service.py",
    "src/api/deps.py",
    "src/api/dependencies.py",
]


def main():
    print("🔧 Corrigiendo errores B904 (raise without from)...\n")
    
    total_files = 0
    total_fixes = 0
    
    for filepath in CRITICAL_FILES:
        modified, count = fix_b904_in_file(filepath)
        if modified:
            total_files += 1
            total_fixes += count
            print(f"✅ {filepath}: {count} correcciones")
        else:
            print(f"⏭️  {filepath}: Sin cambios")
    
    print(f"\n{'='*60}")
    print(f"📊 RESUMEN:")
    print(f"   Archivos modificados: {total_files}")
    print(f"   Total de correcciones: {total_fixes}")
    print(f"{'='*60}")
    
    if total_fixes > 0:
        print("\n✨ Ejecuta 'black src/' para formatear")


if __name__ == "__main__":
    main()
