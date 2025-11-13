"""Debug de imports en routes.py"""

print("=== DEBUGEANDO IMPORTS ===\n")

try:
    from src.api.routes.auth_main import router as auth_router
    print("✓ auth_router cargado")
except Exception as e:
    print(f"✗ auth_router ERROR: {e}")

try:
    from src.api.routes.avatar import router as avatar_router
    print("✓ avatar_router cargado")
except Exception as e:
    print(f"✗ avatar_router ERROR: {e}")

try:
    from src.api.routes.dev_email import router as dev_email_router
    print("✓ dev_email_router cargado")
except Exception as e:
    print(f"✗ dev_email_router ERROR: {e}")

try:
    from src.api.routes.evaluaciones import router as evaluaciones_router
    print("✓ evaluaciones_router cargado")
except Exception as e:
    print(f"✗ evaluaciones_router ERROR: {e}")

try:
    from src.api.routes.invitaciones import router as invitaciones_router
    print(f"✓ invitaciones_router cargado: {invitaciones_router}")
    print(f"  - Prefix: {invitaciones_router.prefix}")
    print(f"  - Routes: {len(invitaciones_router.routes)}")
except Exception as e:
    print(f"✗ invitaciones_router ERROR: {e}")
    import traceback
    traceback.print_exc()

print("\n=== FIN DEBUG ===")
