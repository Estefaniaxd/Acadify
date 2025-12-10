# src/api/routes.py
"""Configuración central de routers para la aplicación FastAPI.
Lista de todos los routers que se incluirán en la aplicación principal.
Cada elemento es una tupla: (router, prefix, tags).
"""

# Imports de routers base
from src.api.routes.auth_main import router as auth_router
from src.api.routes.avatar import router as avatar_router
from src.api.routes.dev_email import router as dev_email_router
from src.api.routes.evaluaciones import router as evaluaciones_router
from src.api.routes.instituciones_publicas import (
    router as instituciones_publicas_router,
)

# 🔥 NUEVOS: Invitaciones y registro por dominio
from src.api.routes.invitaciones import router as invitaciones_router


# Routers de comunicación
try:
    from src.api.routes.communication.videollamadas import (
        router as videollamadas_router,
    )
    from src.api.routes.communication.chat_ws import (
        router as chat_ws_router,
    )
    from src.api.routes.communication.notificaciones import (
        router as notificaciones_router,
    )

except Exception:
    import traceback

    traceback.print_exc()
    videollamadas_router = None
    chat_ws_router = None

# Routers académicos
from src.api.routes.classes.clase import router as clase_router
from src.api.routes.academic.curso_archivos import router as archivos_router
from src.api.routes.academic.curso_comentarios import router as comentarios_router
from src.api.routes.academic.curso_reacciones import router as reacciones_router
from src.api.routes.academic.curso_tareas import router as curso_tareas_router
from src.api.routes.academic.ia_tareas import router as ia_tareas_router
from src.api.routes.academic.tareas import router as tareas_router
from src.api.routes.academic.cursos import router as cursos_router
from src.api.routes.academic.inscripciones import router as inscripciones_curso_router
from src.api.routes.academic.institucion import router as institucion_router
from src.api.routes.academic.periodos_academicos import router as periodos_router
from src.api.routes.academic.personas import router as personas_router
from src.core.config import get_settings


settings = get_settings()

# Lista principal de routers
routers = [
    (auth_router, "/auth", ["Autenticación"]),
    (avatar_router, "/avatar", ["Avatars"]),
    (invitaciones_router, "/invitaciones", ["Invitaciones"]),
    (instituciones_publicas_router, "", ["Instituciones Públicas"]),
    (evaluaciones_router, "/evaluaciones", ["Evaluaciones"]),
    (cursos_router, "/api", ["Cursos"]),
    (periodos_router, "/api", ["Períodos Académicos"]),
    (inscripciones_curso_router, "/api", ["Inscripciones"]),
    (curso_tareas_router, "/api/cursos/tareas", ["Tareas Cursos"]),
    (tareas_router, "/api/tareas", ["Tareas"]),
    (comentarios_router, "/api", ["Comentarios"]),
    (reacciones_router, "/api", ["Reacciones"]),
    (archivos_router, "/api", ["Archivos"]),
    (personas_router, "/api", ["Personas y Perfiles"]),
    (institucion_router, "/api/instituciones", ["Instituciones"]),
    (clase_router, "/api/v1", ["Clases"]),
    (ia_tareas_router, "/api/cursos/tareas", ["IA Tareas"]),
    (notificaciones_router, "/api", ["Notificaciones"]),
]

# Rachas router is already included in gamificacion_router
# try:
#     from src.api.routes.gamification.rachas_routes import router as rachas_router
#     # routers.append((rachas_router, "/api/gamification/rachas", ["Rachas"]))
# except Exception:
#     pass

# Agregar videollamadas si se importó exitosamente
if videollamadas_router is not None:
    routers.append((videollamadas_router, "/api/communication", ["Videollamadas"]))

# Agregar WebSocket de chat si se importó exitosamente
if chat_ws_router is not None:
    routers.append((chat_ws_router, "/api/communication", ["Chat WebSocket"]))

# Agregar routers de desarrollo
if settings.is_development():
    routers.append((dev_email_router, "", ["Development-Email"]))
