#!/usr/bin/env python3
"""
Script maestro para ejecutar todos los scripts de diagnóstico
y corrección en secuencia.

Uso:
    python run_diagnostics.py
"""

import subprocess
import sys
from pathlib import Path

def run_script(script_name, description, args=None):
    """Ejecuta un script y muestra su salida."""
    print("\n" + "="*80)
    print(f"🔧 {description}")
    print("="*80 + "\n")
    
    script_path = Path(__file__).parent / script_name
    
    if not script_path.exists():
        print(f"❌ Script no encontrado: {script_path}")
        return False
    
    cmd = [sys.executable, str(script_path)]
    if args:
        cmd.extend(args)
    
    try:
        result = subprocess.run(
            cmd,
            cwd=Path(__file__).parent.parent.parent.parent,
            check=False
        )
        return result.returncode == 0
    except Exception as e:
        print(f"❌ Error ejecutando script: {e}")
        return False

def main():
    print("""
╔════════════════════════════════════════════════════════════════════════════╗
║                  🚀 DIAGNÓSTICO COMPLETO DE TESTS                          ║
║                     Sistema de Gamificación                                 ║
╚════════════════════════════════════════════════════════════════════════════╝
""")
    
    scripts = [
        {
            'name': 'run_all_tests.py',
            'description': 'Paso 1: Ejecutando todos los tests',
            'args': []
        },
        {
            'name': 'analyze_test_errors.py',
            'description': 'Paso 2: Analizando errores encontrados',
            'args': ['test_puntos_api.py']
        },
        {
            'name': 'convert_sync_to_async.py',
            'description': 'Paso 3: Buscando problemas sync/async',
            'args': ['--dir', 'src/services/gamification']
        },
        {
            'name': 'debug_500_errors.py',
            'description': 'Paso 4: Debug detallado de errores 500',
            'args': []
        }
    ]
    
    results = {}
    
    for script in scripts:
        success = run_script(
            script['name'],
            script['description'],
            script.get('args')
        )
        results[script['name']] = success
        
        if not success:
            print(f"\n⚠️  El script {script['name']} completó con advertencias")
    
    # Resumen final
    print("\n" + "="*80)
    print("📊 RESUMEN DEL DIAGNÓSTICO")
    print("="*80 + "\n")
    
    for script_name, success in results.items():
        status = "✅" if success else "⚠️"
        print(f"{status} {script_name}")
    
    print("\n" + "="*80)
    print("💡 SIGUIENTE PASO")
    print("="*80)
    print("""
Los scripts han generado información detallada sobre los problemas encontrados.

Revisa los siguientes archivos:
  • error_report.json - Categorización de errores
  • test_report.html - Reporte visual (si se generó con --html)

Para aplicar correcciones automáticas:
  1. Revisa las sugerencias en los reportes
  2. Ejecuta: python convert_sync_to_async.py --fix --dry-run
  3. Si se ve bien: python convert_sync_to_async.py --fix
  4. Vuelve a ejecutar: python run_all_tests.py

Para correcciones manuales:
  • Usa los reportes como guía
  • Enfócate en los errores más comunes primero
  • Ejecuta tests individuales para verificar: pytest -xvs test_file.py::test_name
""")
    
    print("\n")

if __name__ == "__main__":
    main()
