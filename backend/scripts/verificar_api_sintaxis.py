"""
Verificación simple de sintaxis de API Routes.

Este script verifica:
1. Que los archivos existen
2. Que no tienen errores de sintaxis
3. Lista de rutas esperadas

No requiere configuración de .env ni bases de datos.
"""

import sys
import ast
from pathlib import Path

# Colores
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
RESET = "\033[0m"

def check_syntax(filepath):
    """Verifica la sintaxis de un archivo Python."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        ast.parse(content)
        return True, None
    except SyntaxError as e:
        return False, str(e)

def main():
    print(f"\n{BLUE}╔══════════════════════════════════════════════════════════════╗{RESET}")
    print(f"{BLUE}║     VERIFICACIÓN DE SINTAXIS - API ROUTES IA                 ║{RESET}")
    print(f"{BLUE}╚══════════════════════════════════════════════════════════════╝{RESET}\n")
    
    files_to_check = [
        ("Router de IA", "src/api/routes/academic/ia_tareas.py"),
        ("Schemas de IA", "src/schemas/ai_schemas.py"),
        ("PuntosService", "src/services/gamification/puntos_service.py"),
        ("TareaService", "src/services/academic/tarea_service.py"),
        ("Routes Init", "src/api/routes/__init__.py"),
    ]
    
    all_ok = True
    
    print(f"{YELLOW}Verificando archivos y sintaxis...{RESET}\n")
    
    for name, filepath in files_to_check:
        if not Path(filepath).exists():
            print(f"{RED}✗{RESET} {name:20} - Archivo no encontrado: {filepath}")
            all_ok = False
            continue
        
        syntax_ok, error = check_syntax(filepath)
        if syntax_ok:
            # Contar líneas
            with open(filepath, 'r') as f:
                lines = len(f.readlines())
            print(f"{GREEN}✓{RESET} {name:20} - Sintaxis OK ({lines} líneas)")
        else:
            print(f"{RED}✗{RESET} {name:20} - Error de sintaxis:")
            print(f"    {error}")
            all_ok = False
    
    # Verificar contenido del router
    print(f"\n{YELLOW}Verificando contenido del router...{RESET}\n")
    
    router_file = "src/api/routes/academic/ia_tareas.py"
    if Path(router_file).exists():
        with open(router_file, 'r') as f:
            content = f.read()
        
        # Buscar decoradores de rutas
        expected_routes = [
            ("POST", "/cursos/{curso_id}/tareas/{tarea_id}/entregas", "entregar_tarea_con_ia"),
            ("GET", "/entregas/{entrega_id}/retroalimentacion", "obtener_retroalimentacion_ia"),
            ("GET", "/usuarios/{usuario_id}/puntos", "obtener_puntos_usuario"),
            ("GET", "/usuarios/ranking", "obtener_ranking_puntos"),
            ("GET", "/usuarios/mi-ranking", "obtener_mi_posicion_ranking"),
            ("GET", "/cursos/{curso_id}/tareas/{tarea_id}/estadisticas-ia", "obtener_estadisticas_ia_tarea"),
            ("GET", "/ia/health", "health_check_ia"),
        ]
        
        for method, path, func_name in expected_routes:
            if f"@router.{method.lower()}(" in content and f"def {func_name}(" in content:
                print(f"{GREEN}✓{RESET} {method:6} {path:50} → {func_name}")
            else:
                print(f"{RED}✗{RESET} {method:6} {path:50} → {func_name} NO ENCONTRADO")
                all_ok = False
    
    # Verificar registro en __init__.py
    print(f"\n{YELLOW}Verificando registro del router...{RESET}\n")
    
    init_file = "src/api/routes/__init__.py"
    if Path(init_file).exists():
        with open(init_file, 'r') as f:
            content = f.read()
        
        if "from src.api.routes.academic.ia_tareas import router as ia_tareas_router" in content:
            print(f"{GREEN}✓{RESET} Import del router de IA encontrado")
        else:
            print(f"{RED}✗{RESET} Import del router de IA NO encontrado")
            all_ok = False
        
        if 'ia_tareas_router, "/api", ["IA y Gamificación"]' in content:
            print(f"{GREEN}✓{RESET} Router de IA registrado en lista de routers")
        else:
            print(f"{RED}✗{RESET} Router de IA NO registrado en lista")
            all_ok = False
    
    # Resumen
    print(f"\n{BLUE}{'=' * 70}{RESET}")
    if all_ok:
        print(f"{GREEN}✓ TODAS LAS VERIFICACIONES PASARON{RESET}")
        print(f"\n{YELLOW}API Routes lista para usar. Próximos pasos:{RESET}")
        print(f"  1. Configurar .env con GEMINI_API_KEY")
        print(f"  2. Iniciar servidor: {BLUE}python -m uvicorn src.main:app --reload{RESET}")
        print(f"  3. Ver docs: {BLUE}http://localhost:8000/docs{RESET}")
    else:
        print(f"{RED}✗ ALGUNAS VERIFICACIONES FALLARON{RESET}")
    print(f"{BLUE}{'=' * 70}{RESET}\n")
    
    return all_ok

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
