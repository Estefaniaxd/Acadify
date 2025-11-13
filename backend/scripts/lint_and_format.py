#!/usr/bin/env python3
"""
Script de formateo y linting para el proyecto Acadify Backend.

Este script ejecuta Ruff para formatear y verificar el código.
"""

import subprocess
import sys
from pathlib import Path


def run_command(cmd: list[str], description: str) -> bool:
    """Ejecuta un comando y muestra el resultado."""
    print(f"\n{'='*80}")
    print(f"🔧 {description}")
    print(f"{'='*80}")
    
    result = subprocess.run(cmd, capture_output=False)
    
    if result.returncode == 0:
        print(f"✅ {description} - Completado")
        return True
    else:
        print(f"❌ {description} - Falló")
        return False


def main():
    """Función principal."""
    print("\n🚀 Iniciando formateo y linting del proyecto Acadify Backend\n")
    
    # Verificar que estamos en el directorio correcto
    if not Path("pyproject.toml").exists():
        print("❌ Error: pyproject.toml no encontrado. Ejecuta desde el directorio backend/")
        sys.exit(1)
    
    success = True
    
    # 1. Formatear código con Ruff
    success &= run_command(
        ["python", "-m", "ruff", "format", "src/", "scripts/"],
        "Formateando código con Ruff"
    )
    
    # 2. Organizar imports
    success &= run_command(
        ["python", "-m", "ruff", "check", "--select", "I", "--fix", "src/", "scripts/"],
        "Organizando imports"
    )
    
    # 3. Aplicar fixes automáticos seguros
    success &= run_command(
        ["python", "-m", "ruff", "check", "--fix", "--unsafe-fixes", "src/", "scripts/"],
        "Aplicando fixes automáticos"
    )
    
    # 4. Verificación final (sin modificar archivos)
    success &= run_command(
        ["python", "-m", "ruff", "check", "src/", "scripts/"],
        "Verificación final de linting"
    )
    
    print("\n" + "="*80)
    if success:
        print("🎉 ¡Formateo y linting completados exitosamente!")
    else:
        print("⚠️  Algunas verificaciones fallaron. Revisa los mensajes arriba.")
    print("="*80 + "\n")
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
