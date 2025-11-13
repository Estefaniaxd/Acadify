#!/usr/bin/env python3
"""
Script para ejecutar un test específico con debugging mejorado.
Agrega automáticamente prints de debug en endpoints.

Uso:
    python run_single_test_debug.py <test_name>
    
Ejemplo:
    python run_single_test_debug.py test_obtener_puntos_exitoso
    python run_single_test_debug.py TestPuntosRanking::test_ranking_paginacion
"""

import subprocess
import sys
from pathlib import Path

def run_test(test_name):
    """Ejecuta un test específico con debugging completo."""
    
    # Determinar el path completo del test
    if '::' in test_name:
        # Ya tiene formato completo
        test_path = f"tests/gamification/test_puntos_api.py::{test_name}"
    else:
        # Solo el nombre del test
        test_path = f"tests/gamification/test_puntos_api.py::*::{test_name}"
    
    print(f"""
╔════════════════════════════════════════════════════════════════════════════╗
║                     🐛 DEBUG MODE - TEST INDIVIDUAL                        ║
╚════════════════════════════════════════════════════════════════════════════╝

Test: {test_name}
Path: {test_path}

Ejecutando con máxima verbosidad...
""")
    
    # Comando con máxima información de debug
    cmd = [
        "pytest",
        test_path,
        "-xvs",                    # Stop en primer error, verboso, sin captura
        "--tb=short",              # Traceback corto
        "--log-cli-level=DEBUG",   # Logs de DEBUG
        "-p", "no:warnings",       # Sin warnings
        "--capture=no"             # No capturar output
    ]
    
    result = subprocess.run(
        cmd,
        cwd=Path(__file__).parent.parent.parent.parent,
    )
    
    return result.returncode

def show_tips():
    """Muestra tips útiles después de ejecutar el test."""
    print("""
╔════════════════════════════════════════════════════════════════════════════╗
║                            💡 TIPS DE DEBUG                                ║
╚════════════════════════════════════════════════════════════════════════════╝

Si el test falló:

1. Busca "RESPONSE BODY" en el output para ver el error 500
2. Busca "FAILED" para ver el assertion que falló
3. Revisa los logs de "auth-debug" y el servicio

Para más debug:
  • Agrega print() en el endpoint
  • Usa pytest --pdb para abrir debugger
  • Revisa conftest.py si es un problema de fixtures

Para ejecutar con debugger interactivo:
  pytest {test_path} -xvs --pdb

Para ejecutar solo setup (sin el test):
  pytest {test_path} -xvs --setup-only
""")

def main():
    if len(sys.argv) < 2:
        print("""
Uso: python run_single_test_debug.py <test_name>

Ejemplos:
  python run_single_test_debug.py test_obtener_puntos_exitoso
  python run_single_test_debug.py TestPuntosRanking::test_ranking_paginacion
  
Para ver todos los tests disponibles:
  pytest tests/gamification/test_puntos_api.py --collect-only
""")
        sys.exit(1)
    
    test_name = sys.argv[1]
    
    returncode = run_test(test_name)
    
    if returncode != 0:
        show_tips()
        print(f"\n❌ Test falló con código: {returncode}\n")
    else:
        print(f"\n✅ ¡Test pasó correctamente!\n")
    
    sys.exit(returncode)

if __name__ == "__main__":
    main()
