#!/usr/bin/env python3
"""
Script para analizar errores en tests de gamificación.
Ejecuta los tests y extrae información detallada de los errores 500.

Uso:
    python analyze_test_errors.py [test_file]
    
Ejemplo:
    python analyze_test_errors.py test_puntos_api.py
"""

import subprocess
import re
import json
from pathlib import Path
from collections import defaultdict

def run_tests_and_capture(test_file=None):
    """Ejecuta los tests y captura la salida."""
    cmd = ["pytest", "-xvs", "--tb=short"]
    
    if test_file:
        cmd.append(f"tests/gamification/{test_file}")
    else:
        cmd.append("tests/gamification/")
    
    result = subprocess.run(
        cmd,
        cwd=Path(__file__).parent.parent.parent.parent,
        capture_output=True,
        text=True
    )
    
    return result.stdout + result.stderr

def extract_500_errors(output):
    """Extrae todos los errores 500 con sus detalles."""
    errors = []
    
    # Patrón para encontrar respuestas 500 con detail
    pattern = r'RESPONSE BODY: \{"detail":"([^"]+)"\}'
    matches = re.finditer(pattern, output)
    
    for match in matches:
        detail = match.group(1)
        # Decodificar \n
        detail = detail.replace('\\n', '\n')
        errors.append(detail)
    
    # Si no hay RESPONSE BODY, buscar en los assertion errors
    if not errors:
        pattern = r'assert 500 == (200|404)'
        matches = re.finditer(pattern, output)
        for match in matches:
            errors.append(f"Expected {match.group(1)} but got 500")
    
    return errors

def categorize_errors(errors):
    """Categoriza los errores por tipo."""
    categories = defaultdict(list)
    
    for error in errors:
        if 'AttributeError' in error and 'has no attribute' in error:
            # Error de campo inexistente
            match = re.search(r"'(\w+)' has no attribute '(\w+)'", error)
            if match:
                model, field = match.groups()
                categories['missing_fields'].append({
                    'model': model,
                    'field': field,
                    'full_error': error
                })
        elif 'no such table' in error:
            # Tabla faltante
            match = re.search(r'no such table: (\w+)', error)
            if match:
                table = match.group(1)
                categories['missing_tables'].append({
                    'table': table,
                    'full_error': error
                })
        elif 'query' in error.lower() or 'asyncsession' in error.lower():
            # Problema de async/sync
            categories['sync_issues'].append(error)
        elif 'invalid keyword argument' in error:
            # Campo inválido en modelo
            match = re.search(r"'(\w+)' is an invalid keyword argument for (\w+)", error)
            if match:
                field, model = match.groups()
                categories['invalid_fields'].append({
                    'model': model,
                    'field': field,
                    'full_error': error
                })
        else:
            categories['other'].append(error)
    
    return categories

def print_report(categories):
    """Imprime un reporte formateado de los errores."""
    print("\n" + "="*80)
    print("REPORTE DE ANÁLISIS DE ERRORES EN TESTS DE GAMIFICACIÓN")
    print("="*80 + "\n")
    
    total_errors = sum(len(v) for v in categories.values())
    print(f"📊 Total de errores únicos encontrados: {total_errors}\n")
    
    # Missing fields
    if categories['missing_fields']:
        print("🔴 CAMPOS FALTANTES EN MODELOS:")
        print("-" * 80)
        for error in categories['missing_fields']:
            print(f"  • Modelo: {error['model']}")
            print(f"    Campo faltante: {error['field']}")
            print(f"    Solución: Verificar nombre correcto del campo en el modelo")
            print()
    
    # Missing tables
    if categories['missing_tables']:
        print("🔴 TABLAS FALTANTES EN BASE DE DATOS:")
        print("-" * 80)
        for error in categories['missing_tables']:
            print(f"  • Tabla: {error['table']}")
            print(f"    Solución: Agregar '{error['table']}' a tables_to_create en conftest.py")
            print()
    
    # Invalid fields
    if categories['invalid_fields']:
        print("🔴 CAMPOS INVÁLIDOS (nombres incorrectos):")
        print("-" * 80)
        field_count = defaultdict(list)
        for error in categories['invalid_fields']:
            field_count[error['field']].append(error['model'])
        
        for field, models in field_count.items():
            print(f"  • Campo incorrecto: '{field}'")
            print(f"    Usado en: {', '.join(set(models))}")
            print(f"    Solución: Buscar y reemplazar en fixtures/tests")
            print()
    
    # Sync issues
    if categories['sync_issues']:
        print("🔴 PROBLEMAS ASYNC/SYNC:")
        print("-" * 80)
        print(f"  • Total: {len(categories['sync_issues'])} errores")
        print(f"    Solución: Convertir db.query() a async select()")
        print()
    
    # Other
    if categories['other']:
        print("🔴 OTROS ERRORES:")
        print("-" * 80)
        for i, error in enumerate(categories['other'][:3], 1):
            print(f"  {i}. {error[:200]}...")
            print()
    
    # Sugerencias
    print("\n" + "="*80)
    print("💡 SUGERENCIAS DE CORRECCIÓN:")
    print("="*80)
    print("1. Ejecutar fix_model_fields.py para corregir campos automáticamente")
    print("2. Ejecutar add_missing_tables.py para agregar tablas faltantes")
    print("3. Ejecutar convert_sync_to_async.py para convertir llamadas síncronas")
    print("\n")

def main():
    import sys
    
    test_file = sys.argv[1] if len(sys.argv) > 1 else None
    
    print("🔍 Ejecutando tests y analizando errores...")
    output = run_tests_and_capture(test_file)
    
    print("📝 Extrayendo errores 500...")
    errors = extract_500_errors(output)
    
    if not errors:
        print("✅ ¡No se encontraron errores 500! Todos los tests están pasando.")
        return
    
    print("🔬 Categorizando errores...")
    categories = categorize_errors(errors)
    
    print_report(categories)
    
    # Guardar reporte JSON
    report_file = Path(__file__).parent / "error_report.json"
    with open(report_file, 'w') as f:
        json.dump({k: v for k, v in categories.items()}, f, indent=2)
    
    print(f"💾 Reporte detallado guardado en: {report_file}")

if __name__ == "__main__":
    main()
