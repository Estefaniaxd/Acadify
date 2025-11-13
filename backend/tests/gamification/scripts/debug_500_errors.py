#!/usr/bin/env python3
"""
Script para depurar errores 500 en tests ejecutándolos uno por uno
y capturando las respuestas de error detalladas.

Uso:
    python debug_500_errors.py
"""

import subprocess
import re
from pathlib import Path
from collections import defaultdict

def get_all_test_names():
    """Extrae todos los nombres de tests del archivo."""
    test_file = Path(__file__).parent.parent / "test_puntos_api.py"
    
    with open(test_file) as f:
        content = f.read()
    
    # Buscar todos los métodos async def test_
    pattern = r'async def (test_\w+)'
    tests = re.findall(pattern, content)
    
    return tests

def run_single_test(test_name):
    """Ejecuta un test individual y captura el output."""
    cmd = [
        "pytest",
        f"tests/gamification/test_puntos_api.py::{test_name}",
        "-xvs",
        "--tb=short",
        "--log-cli-level=ERROR"
    ]
    
    result = subprocess.run(
        cmd,
        cwd=Path(__file__).parent.parent.parent.parent,
        capture_output=True,
        text=True,
        timeout=30
    )
    
    return {
        'stdout': result.stdout,
        'stderr': result.stderr,
        'returncode': result.returncode
    }

def extract_error_detail(output):
    """Extrae el detalle del error de la respuesta."""
    # Buscar RESPONSE BODY
    match = re.search(r'RESPONSE BODY: (\{[^}]+\})', output)
    if match:
        body = match.group(1)
        # Extraer detail
        detail_match = re.search(r'"detail":"([^"]+)"', body)
        if detail_match:
            return detail_match.group(1).replace('\\n', '\n')
    
    # Buscar en el traceback
    match = re.search(r'detail["\s:]+([^\n]+)', output)
    if match:
        return match.group(1)
    
    # Buscar assertion error
    if 'assert 500 ==' in output:
        match = re.search(r'assert 500 == (\d+)', output)
        if match:
            return f"Expected {match.group(1)} but got 500"
    
    return None

def categorize_by_class(test_name):
    """Categoriza el test por su clase."""
    if 'TestPuntosMe' in test_name:
        return 'TestPuntosMe'
    elif 'TestPuntosRanking' in test_name:
        return 'TestPuntosRanking'
    elif 'TestOtorgarPuntos' in test_name:
        return 'TestOtorgarPuntos'
    elif 'TestHistorialPuntos' in test_name:
        return 'TestHistorialPuntos'
    elif 'TestNivelInfo' in test_name:
        return 'TestNivelInfo'
    elif 'TestPuntosIntegracion' in test_name:
        return 'TestPuntosIntegracion'
    elif 'TestPuntosPerformance' in test_name:
        return 'TestPuntosPerformance'
    return 'Other'

def main():
    print("🔍 Descubriendo tests...")
    tests = get_all_test_names()
    print(f"✅ Encontrados {len(tests)} tests\n")
    
    results = {
        'passed': [],
        'failed': [],
        'error': []
    }
    
    errors_by_type = defaultdict(list)
    
    for i, test in enumerate(tests, 1):
        print(f"[{i}/{len(tests)}] Ejecutando {test}...", end=" ")
        
        try:
            result = run_single_test(test)
            
            if result['returncode'] == 0:
                print("✅ PASSED")
                results['passed'].append(test)
            else:
                output = result['stdout'] + result['stderr']
                
                if 'FAILED' in output:
                    print("❌ FAILED")
                    results['failed'].append(test)
                    
                    # Extraer error
                    error = extract_error_detail(output)
                    if error:
                        category = categorize_by_class(test)
                        errors_by_type[category].append({
                            'test': test,
                            'error': error
                        })
                else:
                    print("⚠️  ERROR")
                    results['error'].append(test)
        
        except subprocess.TimeoutExpired:
            print("⏱️  TIMEOUT")
            results['error'].append(test)
        except Exception as e:
            print(f"💥 EXCEPTION: {e}")
            results['error'].append(test)
    
    # Imprimir resumen
    print("\n" + "="*80)
    print("RESUMEN DE EJECUCIÓN")
    print("="*80)
    print(f"✅ PASSED: {len(results['passed'])}")
    print(f"❌ FAILED: {len(results['failed'])}")
    print(f"⚠️  ERROR: {len(results['error'])}")
    print()
    
    if errors_by_type:
        print("="*80)
        print("ERRORES POR CATEGORÍA")
        print("="*80)
        
        for category, errors in sorted(errors_by_type.items()):
            print(f"\n📁 {category} ({len(errors)} errores)")
            print("-" * 80)
            
            # Agrupar por error similar
            error_groups = defaultdict(list)
            for item in errors:
                # Extraer parte clave del error
                error_key = item['error'][:100]
                error_groups[error_key].append(item['test'])
            
            for error_key, tests in error_groups.items():
                print(f"\n  Error: {error_key}...")
                print(f"  Tests afectados: {len(tests)}")
                for test in tests[:3]:
                    print(f"    • {test}")
                if len(tests) > 3:
                    print(f"    ... y {len(tests) - 3} más")
    
    # Tests que pasaron
    if results['passed']:
        print("\n" + "="*80)
        print("✅ TESTS QUE PASAN CORRECTAMENTE")
        print("="*80)
        for test in results['passed']:
            print(f"  ✓ {test}")
    
    print("\n")

if __name__ == "__main__":
    main()
