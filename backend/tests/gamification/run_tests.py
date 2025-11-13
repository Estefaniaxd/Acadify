#!/usr/bin/env python3
"""
Test Runner para Sistema de Gamificación.

Ejecuta todos los tests con opciones configurables.

Uso:
    python run_tests.py                    # Todos los tests
    python run_tests.py --fast             # Sin tests lentos
    python run_tests.py --coverage         # Con reporte de cobertura
    python run_tests.py --verbose          # Modo detallado
    python run_tests.py --module puntos    # Solo módulo específico

Author: GitHub Copilot & Team
Date: 2 de noviembre de 2025
"""

import sys
import subprocess
from pathlib import Path


def run_tests(args: list[str]) -> int:
    """Ejecuta pytest con argumentos."""
    test_dir = Path(__file__).parent
    
    cmd = ["pytest", str(test_dir)]
    
    # Opciones por defecto
    cmd.extend([
        "-v",  # Verbose
        "--tb=short",  # Traceback corto
        "--strict-markers",  # Markers estrictos
        "--disable-warnings",  # Deshabilitar warnings
    ])
    
    # Argumentos personalizados
    if "--fast" in args:
        cmd.append("-m not slow")
        args.remove("--fast")
    
    if "--coverage" in args:
        cmd.extend([
            "--cov=src/api/routes/gamification",
            "--cov=src/services/gamification",
            "--cov-report=html",
            "--cov-report=term-missing",
        ])
        args.remove("--coverage")
    
    if "--verbose" in args:
        cmd.append("-vv")
        args.remove("--verbose")
    
    # Módulo específico
    if "--module" in args:
        idx = args.index("--module")
        module = args[idx + 1]
        cmd.append(f"test_{module}_api.py")
        args.pop(idx)
        args.pop(idx)
    
    # Agregar args restantes
    cmd.extend(args)
    
    print(f"🧪 Ejecutando: {' '.join(cmd)}")
    print("=" * 80)
    
    return subprocess.call(cmd)


def main():
    """Punto de entrada."""
    args = sys.argv[1:]
    
    if "--help" in args or "-h" in args:
        print(__doc__)
        return 0
    
    return run_tests(args)


if __name__ == "__main__":
    sys.exit(main())
