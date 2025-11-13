#!/usr/bin/env python3
import sys
sys.path.insert(0, '/run/media/arch/Storage/SENA/Proyecto-Formativo/Acadify/backend')

print("🔍 Ejecutando routes.py línea por línea...\n")

routers = []

try:
    print("1. Import auth_router...")
    from src.api.routes.auth_main import router as auth_router
    print("   ✅")
    
    print("2. Import avatar_router...")
    from src.api.routes.avatar import router as avatar_router
    print("   ✅")
    
    print("3. Import dev_email_router...")
    from src.api.routes.dev_email import router as dev_email_router
    print("   ✅")
    
    print("4. Import evaluaciones_router...")
    from src.api.routes.evaluaciones import router as evaluaciones_router
    print("   ✅")
    
    print("5. Import invitaciones_router...")
    from src.api.routes.invitaciones import router as invitaciones_router
    print(f"   ✅ ({len(invitaciones_router.routes)} routes)")
    
    print("6. Import instituciones_publicas_router...")
    from src.api.routes.instituciones_publicas import router as instituciones_publicas_router
    print(f"   ✅ ({len(instituciones_publicas_router.routes)} routes)")
    
    print("7. Import cursos_router...")
    from src.api.routes.academic.cursos import router as cursos_router
    print("   ✅")
    
    print("8. Import inscripciones_curso_router...")
    from src.api.routes.academic.inscripciones import router as inscripciones_curso_router
    print("   ✅")
    
    print("9. Import tareas_router...")
    from src.api.routes.academic.curso_tareas import router as tareas_router
    print("   ✅")
    
    print("10. Import comentarios_router...")
    from src.api.routes.academic.curso_comentarios import router as comentarios_router
    print("   ✅")
    
    print("11. Import reacciones_router...")
    from src.api.routes.academic.curso_reacciones import router as reacciones_router
    print("   ✅")
    
    print("12. Import archivos_router...")
    from src.api.routes.academic.curso_archivos import router as archivos_router
    print("   ✅")
    
    print("13. Import personas_router...")
    from src.api.routes.academic.personas import router as personas_router
    print("   ✅")
    
    print("14. Import institucion_router...")
    from src.api.routes.academic.institucion import router as institucion_router
    print("   ✅")
    
    print("\n✅ Todos los imports exitosos!")
    
    print("\n📦 Construyendo lista de routers...")
    routers = [
        (auth_router, "/auth", ["Autenticación"]),
        (avatar_router, "/avatar", ["Avatars"]),
        (invitaciones_router, "/invitaciones", ["Invitaciones"]),
        (instituciones_publicas_router, "", ["Instituciones Públicas"]),
        (evaluaciones_router, "/evaluaciones", ["Evaluaciones"]),
        (cursos_router, "/api", ["Cursos"]),
        (inscripciones_curso_router, "/api", ["Inscripciones"]),
        (tareas_router, "/api", ["Tareas"]),
        (comentarios_router, "/api", ["Comentarios"]),
        (reacciones_router, "/api", ["Reacciones"]),
        (archivos_router, "/api", ["Archivos"]),
        (personas_router, "/api", ["Personas y Perfiles"]),
        (institucion_router, "/api/instituciones", ["Instituciones"]),
    ]
    
    # Dev
    from src.core.config import get_settings
    settings = get_settings()
    if settings.is_development():
        routers.append((dev_email_router, "", ["Development-Email"]))
    
    print(f"\n✅ Lista construida: {len(routers)} routers")
    for i, (r, p, t) in enumerate(routers, 1):
        print(f"   {i}. prefix='{p}' tags={t}")
    
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
