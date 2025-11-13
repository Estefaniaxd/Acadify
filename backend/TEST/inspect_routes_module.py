#!/usr/bin/env python
import sys

print("Importando módulo routes...")
import src.api.routes as routes_module

print(f"\n1. Atributos del módulo routes:")
for attr in dir(routes_module):
    if not attr.startswith('_'):
        value = getattr(routes_module, attr)
        print(f"   - {attr}: {type(value)}")

print(f"\n2. Variable 'routers' definida: {'routers' in dir(routes_module)}")

if hasattr(routes_module, 'routers'):
    routers_list = getattr(routes_module, 'routers')
    print(f"   Tipo: {type(routers_list)}")
    print(f"   Longitud: {len(routers_list)}")
    
    print(f"\n3. Elementos en routers:")
    for i, item in enumerate(routers_list, 1):
        if isinstance(item, tuple) and len(item) >= 3:
            router, prefix, tags = item[0], item[1], item[2]
            print(f"   {i}. {tags[0] if tags else 'Sin tag':30} prefix={prefix}")

print(f"\n4. Verificando imports de routers:")
print(f"   personas_router existe: {hasattr(routes_module, 'personas_router')}")
print(f"   institucion_router existe: {hasattr(routes_module, 'institucion_router')}")
