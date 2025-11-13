"""
Script de prueba rápida para verificar imports y configuración del sistema.

Este script NO requiere uvicorn ni bases de datos.
Solo verifica que todos los módulos se importen correctamente.
"""

import sys
from pathlib import Path

# Agregar el directorio backend al PYTHONPATH
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

# Colores
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
RESET = "\033[0m"

def test_import(module_path, name):
    """Intenta importar un módulo y reporta el resultado."""
    try:
        __import__(module_path)
        print(f"{GREEN}✓{RESET} {name:40} OK")
        return True
    except Exception as e:
        print(f"{RED}✗{RESET} {name:40} ERROR: {str(e)[:60]}")
        return False

def main():
    print(f"\n{BLUE}╔══════════════════════════════════════════════════════════╗{RESET}")
    print(f"{BLUE}║     PRUEBA DE IMPORTS - Sistema IA y Gamificación       ║{RESET}")
    print(f"{BLUE}╚══════════════════════════════════════════════════════════╝{RESET}\n")
    
    all_ok = True
    
    print(f"{YELLOW}1. Verificando Schemas...{RESET}")
    all_ok &= test_import("src.schemas.ai_schemas", "ai_schemas")
    
    print(f"\n{YELLOW}2. Verificando Servicios...{RESET}")
    all_ok &= test_import("src.services.gamification.puntos_service", "PuntosService")
    all_ok &= test_import("src.services.academic.tarea_service", "TareaService")
    
    print(f"\n{YELLOW}3. Verificando API Routes...{RESET}")
    all_ok &= test_import("src.api.routes.academic.ia_tareas", "ia_tareas router")
    
    print(f"\n{YELLOW}4. Verificando registro de routers...{RESET}")
    all_ok &= test_import("src.api.routes", "routes __init__")
    
    print(f"\n{YELLOW}5. Verificando FastAPI main...{RESET}")
    all_ok &= test_import("src.main", "FastAPI app")
    
    # Intentar obtener el router y contar rutas
    print(f"\n{YELLOW}6. Verificando rutas del router de IA...{RESET}")
    try:
        from src.api.routes.academic.ia_tareas import router
        num_routes = len(router.routes)
        print(f"{GREEN}✓{RESET} Router de IA tiene {num_routes} rutas registradas")
        
        for i, route in enumerate(router.routes, 1):
            method = ", ".join(route.methods) if hasattr(route, 'methods') else "N/A"
            path = route.path
            print(f"  {i}. {method:8} {path}")
    except Exception as e:
        print(f"{RED}✗{RESET} Error obteniendo rutas: {str(e)[:60]}")
        all_ok = False
    
    # Resumen
    print(f"\n{BLUE}{'=' * 60}{RESET}")
    if all_ok:
        print(f"{GREEN}✓ TODOS LOS IMPORTS FUNCIONAN CORRECTAMENTE{RESET}")
        print(f"\n{YELLOW}Sistema listo para iniciar el servidor.{RESET}")
        print(f"Para iniciar el servidor:")
        print(f"  {BLUE}1. Asegúrate de tener uvicorn instalado: pip install uvicorn{RESET}")
        print(f"  {BLUE}2. Ejecuta: python -m uvicorn src.main:app --reload{RESET}")
        print(f"  {BLUE}3. O ejecuta: uvicorn src.main:app --reload{RESET}")
    else:
        print(f"{RED}✗ ALGUNOS IMPORTS FALLARON{RESET}")
        print(f"{YELLOW}Revisa los errores arriba.{RESET}")
    print(f"{BLUE}{'=' * 60}{RESET}\n")
    
    return all_ok

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print(f"\n{YELLOW}Prueba interrumpida por el usuario{RESET}")
        sys.exit(0)
    except Exception as e:
        print(f"\n{RED}ERROR FATAL: {e}{RESET}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
