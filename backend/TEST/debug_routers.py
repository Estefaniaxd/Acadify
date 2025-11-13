#!/usr/bin/env python
import sys
import traceback

try:
    print("1. Leyendo archivo routes.py directamente...")
    with open('src/api/routes.py', 'r', encoding='utf-8') as f:
        content = f.read()
        print(f"   Tamaño: {len(content)} bytes")
        print(f"   Contiene 'personas_router': {'personas_router' in content}")
        print(f"   Contiene 'institucion_router': {'institucion_router' in content}")
        
        # Buscar las líneas específicas
        lines = content.split('\n')
        for i, line in enumerate(lines, 1):
            if 'personas_router' in line and '/api' in line:
                print(f"   Línea {i}: {line.strip()}")
            if 'institucion_router' in line and '/api' in line:
                print(f"   Línea {i}: {line.strip()}")
    
    print("\n2. Importando archivos_router...")
    from src.api.routes.academic.curso_archivos import router as archivos_router
    print(f"   ✅ OK - {len(archivos_router.routes)} rutas")
    
    print("\n3. Importando personas_router...")
    from src.api.routes.academic.personas import router as personas_router
    print(f"   ✅ OK - {len(personas_router.routes)} rutas")
    
    print("\n4. Importando institucion_router...")
    from src.api.routes.academic.institucion import router as institucion_router
    print(f"   ✅ OK - {len(institucion_router.routes)} rutas")
    
    print("\n5. Importando todo routes.py...")
    from src.api.routes import routers
    print(f"   Total routers: {len(routers)}")
    
    print("\n6. Listando todos los routers:")
    for i, (router, prefix, tags) in enumerate(routers, 1):
        route_count = len(getattr(router, 'routes', []))
        print(f"   {i}. {prefix:30} {str(tags):40} ({route_count} rutas)")
    
    print("\n7. Verificando si personas_router está en la lista...")
    personas_in_list = any(r is personas_router for r, _, _ in routers)
    print(f"   personas_router en routers: {personas_in_list}")
    
    institucion_in_list = any(r is institucion_router for r, _, _ in routers)
    print(f"   institucion_router en routers: {institucion_in_list}")
    
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    traceback.print_exc()
