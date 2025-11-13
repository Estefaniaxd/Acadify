#!/usr/bin/env python3
"""
Script final para corregir TODOS los imports de una vez
Aplicando principio DRY: una sola fuente de verdad
"""
from pathlib import Path
import re


def fix_all_imports():
    """Corrige todos los imports basándose en la estructura real de modelos"""
    
    base_path = Path(__file__).parent.parent
    
    # Buscar todos los archivos
    test_files = list(base_path.glob("TEST/test_*.py"))
    service_files = list(base_path.glob("src/services/evaluaciones/*.py"))
    
    all_files = test_files + service_files
    
    print(f"🔍 Procesando {len(all_files)} archivos...")
    
    replacements = {
        # Imports de modelos - usar módulo correcto
        r'from src\.models\.evaluaciones\.evaluacion import': 'from src.models.evaluaciones.evaluacion_expandida import',
        r'from src\.models\.evaluaciones\.intento_evaluacion import': 'from src.models.evaluaciones.intento_respuesta_gamificacion import',
        r'from src\.models\.evaluaciones\.pregunta_evaluacion import': 'from src.models.evaluaciones.evaluacion_expandida import',
        r'from src\.models\.evaluaciones\.respuesta_estudiante import': 'from src.models.evaluaciones.intento_respuesta_gamificacion import',
        
        # Imports de enums incorrectos
        r'from src\.enums\.evaluaciones import': 'from src.models.evaluaciones import',
        
        # EstadoIntento está en intento_respuesta_gamificacion, no en evaluacion_expandida
        r'from src\.models\.evaluaciones\.evaluacion_expandida import (.*?)EstadoIntento': lambda m: m.group(0).replace('evaluacion_expandida', 'intento_respuesta_gamificacion').replace('EstadoIntento', 'EstadoIntento'),
    }
    
    fixes_applied = 0
    
    for file_path in all_files:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Aplicar reemplazos
        for pattern, replacement in replacements.items():
            if callable(replacement):
                content = re.sub(pattern, replacement, content)
            else:
                content = re.sub(pattern, replacement, content)
        
        # Correcciones específicas para imports multi-línea
        # Si importa EstadoIntento desde evaluacion_expandida, moverlo
        lines = content.split('\n')
        new_lines = []
        skip_next = False
        
        for i, line in enumerate(lines):
            if skip_next:
                skip_next = False
                continue
                
            # Detectar import de evaluacion_expandida con EstadoIntento
            if 'from src.models.evaluaciones.evaluacion_expandida import' in line and 'EstadoIntento' in line:
                # Separar EstadoIntento del resto
                imports = line.split('import')[1].strip()
                import_list = [x.strip() for x in imports.split(',')]
                
                # Separar los que van a evaluacion_expandida de los que van a intento_respuesta
                eval_imports = [x for x in import_list if x != 'EstadoIntento']
                intento_imports = [x for x in import_list if x == 'EstadoIntento']
                
                if eval_imports:
                    new_lines.append(f"from src.models.evaluaciones.evaluacion_expandida import {', '.join(eval_imports)}")
                if intento_imports:
                    new_lines.append(f"from src.models.evaluaciones.intento_respuesta_gamificacion import {', '.join(intento_imports)}")
            else:
                new_lines.append(line)
        
        content = '\n'.join(new_lines)
        
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            fixes_applied += 1
            print(f"  ✅ {file_path.name}")
    
    print(f"\n📊 Total de archivos corregidos: {fixes_applied}")


def main():
    print("="*80)
    print("🔧 CORRECCIÓN FINAL DE TODOS LOS IMPORTS")
    print("="*80 + "\n")
    
    fix_all_imports()
    
    print("\n" + "="*80)
    print("✨ Correcciones completadas")
    print("="*80 + "\n")


if __name__ == "__main__":
    main()
