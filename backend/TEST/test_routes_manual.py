"""Test directo del archivo routes.py"""

print("=== CARGANDO routes.py ===\n")

# Simular exactamente lo que hace routes.py
from src.api.routes.auth_main import router as auth_router
from src.api.routes.avatar import router as avatar_router
from src.api.routes.dev_email import router as dev_email_router
from src.api.routes.evaluaciones import router as evaluaciones_router
from src.api.routes.invitaciones import router as invitaciones_router

print(f"invitaciones_router importado: {invitaciones_router}")
print(f"Tipo: {type(invitaciones_router)}")
print(f"Prefix: {invitaciones_router.prefix}")

# Crear lista como en routes.py
routers = [
    (auth_router, "/auth", ["Autenticación"]),
    (avatar_router, "/avatar", ["Avatars"]),
    (invitaciones_router, "/invitaciones", ["Invitaciones"]),
    (evaluaciones_router, "/evaluaciones", ["Evaluaciones"]),
    ]

print(f"\nTotal en lista: {len(routers)}")
for i, (r, p, t) in enumerate(routers, 1):
    print(f"{i}. {p} - {t}")
