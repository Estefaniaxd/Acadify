#!/usr/bin/env python3
import sys
sys.path.insert(0, '/run/media/arch/Storage/SENA/Proyecto-Formativo/Acadify/backend')

print("🔍 DEBUG: Importación de routers paso a paso\n")

print("1. Importando auth...")
from src.api.routes.auth_main import router as auth_router
print(f"   ✅ Auth: {len(auth_router.routes)} routes")

print("\n2. Importando avatar...")
from src.api.routes.avatar import router as avatar_router
print(f"   ✅ Avatar: {len(avatar_router.routes)} routes")

print("\n3. Importando invitaciones...")
try:
    from src.api.routes.invitaciones import router as invitaciones_router
    print(f"   ✅ Invitaciones: {len(invitaciones_router.routes)} routes")
except Exception as e:
    print(f"   ❌ Error: {e}")
    import traceback
    traceback.print_exc()

print("\n4. Importando instituciones_publicas...")
try:
    from src.api.routes.instituciones_publicas import router as instituciones_publicas_router
    print(f"   ✅ Instituciones Públicas: {len(instituciones_publicas_router.routes)} routes")
except Exception as e:
    print(f"   ❌ Error: {e}")
    import traceback
    traceback.print_exc()

print("\n5. Importando módulo routes completo...")
from src.api import routes
print(f"   📦 Total routers en módulo: {len(routes.routers)}")

print("\n6. Detalle de routers en el módulo:")
for i, (r, p, t) in enumerate(routes.routers, 1):
    print(f"   {i}. prefix='{p}' tags={t} - {len(r.routes)} routes")
