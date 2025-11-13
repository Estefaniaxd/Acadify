#!/usr/bin/env python3
"""
Script para ejecutar todos los tests con información detallada
de progreso y guardar un reporte HTML.

Uso:
    python run_all_tests.py [--html]
"""

import subprocess
import re
from pathlib import Path
from datetime import datetime
import argparse

def run_tests_with_details():
    """Ejecuta todos los tests y captura información detallada."""
    cmd = [
        "pytest",
        "tests/gamification/test_puntos_api.py",
        "-v",
        "--tb=no",
        "--color=yes"
    ]
    
    result = subprocess.run(
        cmd,
        cwd=Path(__file__).parent.parent.parent.parent,
        capture_output=True,
        text=True
    )
    
    return result.stdout + result.stderr

def parse_test_results(output):
    """Parsea la salida de pytest y extrae estadísticas."""
    results = {
        'passed': [],
        'failed': [],
        'errors': [],
        'skipped': []
    }
    
    # Buscar líneas de resultados
    for line in output.split('\n'):
        if ' PASSED' in line:
            test_name = re.search(r'test_\w+', line)
            if test_name:
                results['passed'].append(test_name.group())
        elif ' FAILED' in line:
            test_name = re.search(r'test_\w+', line)
            if test_name:
                results['failed'].append(test_name.group())
        elif ' ERROR' in line:
            test_name = re.search(r'test_\w+', line)
            if test_name:
                results['errors'].append(test_name.group())
    
    # Buscar resumen final
    summary_match = re.search(
        r'(\d+) failed,?\s*(\d+) passed,?\s*(?:(\d+) errors?)?',
        output
    )
    
    if summary_match:
        results['summary'] = {
            'failed': int(summary_match.group(1)),
            'passed': int(summary_match.group(2)),
            'errors': int(summary_match.group(3) or 0)
        }
    
    # Buscar tiempo de ejecución
    time_match = re.search(r'in ([\d.]+)s', output)
    if time_match:
        results['execution_time'] = float(time_match.group(1))
    
    return results

def print_console_report(results):
    """Imprime un reporte colorido en la consola."""
    print("\n" + "="*80)
    print("🎯 REPORTE DE TESTS - GAMIFICACIÓN")
    print("="*80 + "\n")
    
    if 'summary' in results:
        total = results['summary']['passed'] + results['summary']['failed'] + results['summary']['errors']
        passed_pct = (results['summary']['passed'] / total * 100) if total > 0 else 0
        
        print(f"📊 RESUMEN:")
        print(f"  Total de tests: {total}")
        print(f"  ✅ Pasando: {results['summary']['passed']} ({passed_pct:.1f}%)")
        print(f"  ❌ Fallando: {results['summary']['failed']}")
        print(f"  ⚠️  Errores: {results['summary']['errors']}")
        
        if 'execution_time' in results:
            print(f"  ⏱️  Tiempo: {results['execution_time']:.2f}s")
        
        # Barra de progreso
        passed = results['summary']['passed']
        failed = results['summary']['failed']
        errors = results['summary']['errors']
        
        bar_width = 50
        passed_width = int(passed / total * bar_width)
        failed_width = int(failed / total * bar_width)
        error_width = int(errors / total * bar_width)
        
        bar = '█' * passed_width + '▓' * failed_width + '░' * error_width
        print(f"\n  [{bar}]")
        print()
    
    # Tests que pasan
    if results['passed']:
        print(f"✅ TESTS PASANDO ({len(results['passed'])}):")
        for test in results['passed'][:10]:
            print(f"  ✓ {test}")
        if len(results['passed']) > 10:
            print(f"  ... y {len(results['passed']) - 10} más")
        print()
    
    # Tests que fallan
    if results['failed']:
        print(f"❌ TESTS FALLANDO ({len(results['failed'])}):")
        for test in results['failed'][:10]:
            print(f"  ✗ {test}")
        if len(results['failed']) > 10:
            print(f"  ... y {len(results['failed']) - 10} más")
        print()
    
    # Siguiente paso
    print("="*80)
    print("💡 PRÓXIMOS PASOS:")
    print("="*80)
    
    if results['failed'] or results['errors']:
        print("1. Ejecutar: python debug_500_errors.py")
        print("   Para ver detalles de cada error")
        print()
        print("2. Ejecutar: python analyze_test_errors.py")
        print("   Para categorizar y analizar patrones de errores")
        print()
        print("3. Ejecutar: python convert_sync_to_async.py --dir src/services")
        print("   Para encontrar y corregir problemas sync/async")
    else:
        print("🎉 ¡Todos los tests están pasando! ¡Excelente trabajo!")
    
    print("\n")

def generate_html_report(results, output_file='test_report.html'):
    """Genera un reporte HTML interactivo."""
    html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Reporte de Tests - Gamificación</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            margin: 0;
            padding: 20px;
            background: #f5f5f5;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #333;
            border-bottom: 3px solid #4CAF50;
            padding-bottom: 10px;
        }}
        .stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }}
        .stat-card {{
            padding: 20px;
            border-radius: 8px;
            text-align: center;
        }}
        .stat-card.passed {{
            background: #4CAF50;
            color: white;
        }}
        .stat-card.failed {{
            background: #f44336;
            color: white;
        }}
        .stat-card.error {{
            background: #ff9800;
            color: white;
        }}
        .stat-number {{
            font-size: 48px;
            font-weight: bold;
            margin: 10px 0;
        }}
        .stat-label {{
            font-size: 14px;
            opacity: 0.9;
        }}
        .progress-bar {{
            height: 30px;
            background: #eee;
            border-radius: 15px;
            overflow: hidden;
            margin: 20px 0;
        }}
        .progress-fill {{
            height: 100%;
            display: flex;
        }}
        .progress-passed {{
            background: #4CAF50;
        }}
        .progress-failed {{
            background: #f44336;
        }}
        .progress-error {{
            background: #ff9800;
        }}
        .test-list {{
            margin: 20px 0;
        }}
        .test-item {{
            padding: 10px;
            margin: 5px 0;
            border-radius: 4px;
            font-family: monospace;
        }}
        .test-item.passed {{
            background: #e8f5e9;
            border-left: 4px solid #4CAF50;
        }}
        .test-item.failed {{
            background: #ffebee;
            border-left: 4px solid #f44336;
        }}
        .timestamp {{
            color: #666;
            font-size: 14px;
            text-align: center;
            margin-top: 30px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>📊 Reporte de Tests - Sistema de Gamificación</h1>
        <p class="timestamp">Generado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
"""
    
    if 'summary' in results:
        total = results['summary']['passed'] + results['summary']['failed'] + results['summary']['errors']
        passed_pct = (results['summary']['passed'] / total * 100) if total > 0 else 0
        failed_pct = (results['summary']['failed'] / total * 100) if total > 0 else 0
        error_pct = (results['summary']['errors'] / total * 100) if total > 0 else 0
        
        html += f"""
        <div class="stats">
            <div class="stat-card passed">
                <div class="stat-label">PASANDO</div>
                <div class="stat-number">{results['summary']['passed']}</div>
                <div class="stat-label">{passed_pct:.1f}%</div>
            </div>
            <div class="stat-card failed">
                <div class="stat-label">FALLANDO</div>
                <div class="stat-number">{results['summary']['failed']}</div>
                <div class="stat-label">{failed_pct:.1f}%</div>
            </div>
            <div class="stat-card error">
                <div class="stat-label">ERRORES</div>
                <div class="stat-number">{results['summary']['errors']}</div>
                <div class="stat-label">{error_pct:.1f}%</div>
            </div>
        </div>
        
        <div class="progress-bar">
            <div class="progress-fill">
                <div class="progress-passed" style="width: {passed_pct}%"></div>
                <div class="progress-failed" style="width: {failed_pct}%"></div>
                <div class="progress-error" style="width: {error_pct}%"></div>
            </div>
        </div>
"""
    
    # Tests que pasan
    if results['passed']:
        html += f"""
        <h2>✅ Tests Pasando ({len(results['passed'])})</h2>
        <div class="test-list">
"""
        for test in results['passed']:
            html += f'            <div class="test-item passed">✓ {test}</div>\n'
        html += "        </div>\n"
    
    # Tests que fallan
    if results['failed']:
        html += f"""
        <h2>❌ Tests Fallando ({len(results['failed'])})</h2>
        <div class="test-list">
"""
        for test in results['failed']:
            html += f'            <div class="test-item failed">✗ {test}</div>\n'
        html += "        </div>\n"
    
    html += """
    </div>
</body>
</html>
"""
    
    output_path = Path(__file__).parent / output_file
    with open(output_path, 'w') as f:
        f.write(html)
    
    print(f"📄 Reporte HTML generado: {output_path}")

def main():
    parser = argparse.ArgumentParser(description='Ejecuta todos los tests y genera reporte')
    parser.add_argument('--html', action='store_true', help='Genera reporte HTML')
    args = parser.parse_args()
    
    print("🚀 Ejecutando tests de gamificación...")
    print("   (Esto puede tardar un momento...)\n")
    
    output = run_tests_with_details()
    results = parse_test_results(output)
    
    print_console_report(results)
    
    if args.html:
        generate_html_report(results)

if __name__ == "__main__":
    main()
