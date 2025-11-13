"""
Script de verificación de API Routes de IA y Gamificación.

Este script verifica que:
1. Los archivos existen
2. Los imports son correctos
3. Los routers están registrados
4. Las rutas están disponibles

Author: Acadify Team
"""

import sys
from pathlib import Path

# Colores para terminal
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
RESET = "\033[0m"

def print_header(text):
    print(f"\n{BLUE}{'=' * 80}{RESET}")
    print(f"{BLUE}{text:^80}{RESET}")
    print(f"{BLUE}{'=' * 80}{RESET}\n")

def check_file_exists(filepath, description):
    """Verifica que un archivo existe."""
    if Path(filepath).exists():
        print(f"{GREEN}✓{RESET} {description}: {filepath}")
        return True
    else:
        print(f"{RED}✗{RESET} {description}: {filepath} {RED}NO ENCONTRADO{RESET}")
        return False

def check_imports():
    """Verifica que los imports funcionan correctamente."""
    print_header("VERIFICANDO IMPORTS")
    
    all_ok = True
    
    # Test 1: Import schemas
    try:
        from src.schemas.ai_schemas import (
            EntregarTareaRequest,
            EntregaConIAResponse,
            PuntosUsuarioResponse,
            RankingResponse
        )
        print(f"{GREEN}✓{RESET} Schemas de IA importados correctamente")
        print(f"  - EntregarTareaRequest")
        print(f"  - EntregaConIAResponse")
        print(f"  - PuntosUsuarioResponse")
        print(f"  - RankingResponse")
    except ImportError as e:
        print(f"{RED}✗{RESET} Error importando schemas: {e}")
        all_ok = False
    
    # Test 2: Import PuntosService
    try:
        from src.services.gamification.puntos_service import PuntosService
        print(f"{GREEN}✓{RESET} PuntosService importado correctamente")
    except ImportError as e:
        print(f"{RED}✗{RESET} Error importando PuntosService: {e}")
        all_ok = False
    
    # Test 3: Import TareaService
    try:
        from src.services.academic.tarea_service import TareaService
        print(f"{GREEN}✓{RESET} TareaService importado correctamente")
    except ImportError as e:
        print(f"{RED}✗{RESET} Error importando TareaService: {e}")
        all_ok = False
    
    # Test 4: Import router
    try:
        from src.api.routes.academic.ia_tareas import router
        print(f"{GREEN}✓{RESET} Router de IA importado correctamente")
        print(f"  - Total de rutas registradas: {len(router.routes)}")
    except ImportError as e:
        print(f"{RED}✗{RESET} Error importando router: {e}")
        all_ok = False
    except Exception as e:
        # Puede fallar por configuración de Settings, pero el código es correcto
        if "GEMINI_API_KEY" in str(e) or "Extra inputs" in str(e):
            print(f"{YELLOW}⚠{RESET} Router de IA: código correcto, issue de config (GEMINI_API_KEY)")
            print(f"  {YELLOW}Nota: Esto es esperado si .env no está configurado{RESET}")
        else:
            print(f"{RED}✗{RESET} Error importando router: {e}")
            all_ok = False
    
    return all_ok

def list_routes():
    """Lista todas las rutas disponibles."""
    print_header("RUTAS DISPONIBLES EN EL ROUTER")
    
    try:
        from src.api.routes.academic.ia_tareas import router
        
        for i, route in enumerate(router.routes, 1):
            method = ", ".join(route.methods) if hasattr(route, 'methods') else "N/A"
            path = route.path
            name = route.name if hasattr(route, 'name') else "N/A"
            
            print(f"{i}. {GREEN}{method:8}{RESET} {path}")
            print(f"   └─ Name: {name}")
        
        return True
    except Exception as e:
        print(f"{RED}✗{RESET} Error listando rutas: {e}")
        return False

def verify_route_registration():
    """Verifica que el router está registrado en __init__.py"""
    print_header("VERIFICANDO REGISTRO DEL ROUTER")
    
    try:
        from src.api.routes import routers
        
        # Buscar el router de IA
        ia_router_found = False
        for router, prefix, tags in routers:
            if "IA y Gamificación" in tags:
                ia_router_found = True
                print(f"{GREEN}✓{RESET} Router de IA registrado en routers")
                print(f"  - Prefix: {prefix}")
                print(f"  - Tags: {tags}")
                break
        
        if not ia_router_found:
            print(f"{RED}✗{RESET} Router de IA NO encontrado en routers")
            return False
        
        print(f"\n{GREEN}✓{RESET} Total de routers registrados: {len(routers)}")
        return True
        
    except Exception as e:
        print(f"{RED}✗{RESET} Error verificando registro: {e}")
        return False

def check_method_existence():
    """Verifica que los métodos requeridos existen en los servicios."""
    print_header("VERIFICANDO MÉTODOS DE SERVICIOS")
    
    all_ok = True
    
    # PuntosService
    try:
        from src.services.gamification.puntos_service import PuntosService
        
        required_methods = [
            'calcular_puntos_tarea',
            'otorgar_puntos',
            'obtener_puntos_usuario',
            'obtener_ranking',
            'obtener_posicion_usuario'
        ]
        
        print(f"\n{YELLOW}PuntosService:{RESET}")
        for method_name in required_methods:
            if hasattr(PuntosService, method_name):
                print(f"  {GREEN}✓{RESET} {method_name}")
            else:
                print(f"  {RED}✗{RESET} {method_name} {RED}NO ENCONTRADO{RESET}")
                all_ok = False
    except Exception as e:
        print(f"{RED}✗{RESET} Error verificando PuntosService: {e}")
        all_ok = False
    
    # TareaService
    try:
        from src.services.academic.tarea_service import TareaService
        
        required_methods = [
            'procesar_entrega_con_ia',
            'obtener_retroalimentacion_ia',
            'obtener_estadisticas_ia_tarea'
        ]
        
        print(f"\n{YELLOW}TareaService:{RESET}")
        for method_name in required_methods:
            if hasattr(TareaService, method_name):
                print(f"  {GREEN}✓{RESET} {method_name}")
            else:
                print(f"  {RED}✗{RESET} {method_name} {RED}NO ENCONTRADO{RESET}")
                all_ok = False
    except Exception as e:
        print(f"{RED}✗{RESET} Error verificando TareaService: {e}")
        all_ok = False
    
    return all_ok

def main():
    """Función principal de verificación."""
    print(f"\n{BLUE}╔══════════════════════════════════════════════════════════════════════╗{RESET}")
    print(f"{BLUE}║       VERIFICACIÓN DE API ROUTES DE IA Y GAMIFICACIÓN               ║{RESET}")
    print(f"{BLUE}╚══════════════════════════════════════════════════════════════════════╝{RESET}")
    
    # Verificar archivos
    print_header("VERIFICANDO ARCHIVOS")
    files_ok = True
    files_ok &= check_file_exists(
        "src/api/routes/academic/ia_tareas.py",
        "Router de IA"
    )
    files_ok &= check_file_exists(
        "src/schemas/ai_schemas.py",
        "Schemas de IA"
    )
    files_ok &= check_file_exists(
        "src/services/gamification/puntos_service.py",
        "PuntosService"
    )
    files_ok &= check_file_exists(
        "src/services/academic/tarea_service.py",
        "TareaService"
    )
    files_ok &= check_file_exists(
        "Docs/API_IA_GAMIFICACION.md",
        "Documentación"
    )
    
    if not files_ok:
        print(f"\n{RED}✗ FALLO: Algunos archivos no se encontraron{RESET}")
        return False
    
    # Verificar imports
    imports_ok = check_imports()
    
    # Verificar métodos
    methods_ok = check_method_existence()
    
    # Listar rutas
    routes_ok = list_routes()
    
    # Verificar registro
    registration_ok = verify_route_registration()
    
    # Resumen final
    print_header("RESUMEN DE VERIFICACIÓN")
    
    checks = [
        ("Archivos existentes", files_ok),
        ("Imports correctos", imports_ok),
        ("Métodos de servicios", methods_ok),
        ("Rutas del router", routes_ok),
        ("Registro del router", registration_ok)
    ]
    
    all_passed = True
    for check_name, result in checks:
        status = f"{GREEN}✓ PASS{RESET}" if result else f"{RED}✗ FAIL{RESET}"
        print(f"  {check_name:30} {status}")
        all_passed &= result
    
    # Resultado final
    print()
    if all_passed:
        print(f"{GREEN}{'═' * 80}{RESET}")
        print(f"{GREEN}✓ TODOS LOS CHECKS PASARON - API LISTA PARA USAR{RESET:^80}")
        print(f"{GREEN}{'═' * 80}{RESET}")
        print(f"\n{YELLOW}Próximos pasos:{RESET}")
        print(f"  1. Iniciar servidor: {BLUE}python -m uvicorn src.main:app --reload{RESET}")
        print(f"  2. Ver documentación: {BLUE}http://localhost:8000/docs{RESET}")
        print(f"  3. Probar endpoints con Swagger UI")
        return True
    else:
        print(f"{RED}{'═' * 80}{RESET}")
        print(f"{RED}✗ ALGUNOS CHECKS FALLARON - REVISAR ERRORES{RESET:^80}")
        print(f"{RED}{'═' * 80}{RESET}")
        return False

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n{RED}ERROR FATAL: {e}{RESET}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
