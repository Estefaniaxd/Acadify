#!/usr/bin/env python3
import sys
sys.path.insert(0, '/run/media/arch/Storage/SENA/Proyecto-Formativo/Acadify/backend')

print("🔍 Test: Importación limpia de routes\n")

# Eliminar módulo del cache si existe
if 'src.api.routes' in sys.modules:
    print("⚠️  Módulo src.api.routes encontrado en cache - eliminando...")
    del sys.modules['src.api.routes']

if 'src.api' in sys.modules:
    print("⚠️  Módulo src.api encontrado en cache - eliminando...")
    del sys.modules['src.api']

print("✅ Cache limpiado\n")

# Ahora importar
print("Importando src.api.routes...")
from src.api import routes

print(f"\n📦 Total routers: {len(routes.routers)}")
for i, (r, p, t) in enumerate(routes.routers, 1):
    print(f"   {i}. prefix='{p}' tags={t}")
