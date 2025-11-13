"""Configuración central de routers para la aplicación FastAPI.

Esta lista define todos los routers que se incluirán en la aplicación principal.
Cada elemento es una tupla: (router, prefix, tags)
"""

from src.api.routes.academic.curso_archivos import router as archivos_router
from src.api.routes.academic.curso_comentarios import router as comentarios_router
from src.api.routes.academic.curso_reacciones import router as reacciones_router
from src.api.routes.academic.curso_tareas import router as tareas_router

# Routers académicos - REFACTORIZADOS Y MODULARIZADOS
from src.api.routes.academic.cursos import router as cursos_router
from src.api.routes.academic.grupo import router as grupo_router

# 🤖 Sistema de IA y Gamificación
from src.api.routes.academic.ia_tareas import router as ia_tareas_router
from src.api.routes.academic.inscripciones import (
    router as inscripciones_curso_router,
)  # Renombrado
from src.api.routes.academic.institucion import router as institucion_router
from src.api.routes.academic.personas import router as personas_router
from src.api.routes.academic.programa import router as programa_router
from src.api.routes.admin_institucion import router as admin_router
from src.api.routes.auth_main import router as auth_router
from src.api.routes.avatar import router as avatar_router
from src.api.routes.coordinador import router as coordinador_router
from src.api.routes.dev_email import router as dev_email_router
from src.api.routes.evaluaciones import router as evaluaciones_router

# 🎮 Sistema de Gamificación
from src.api.routes.gamification import router as gamificacion_router
from src.api.routes.instituciones_publicas import (
    router as instituciones_publicas_router,
)

# 🔥 NUEVOS: Invitaciones y registro por dominio institucional
from src.api.routes.invitaciones import router as invitaciones_router

# # 💬 Sistema de comunicación y chat
# try:
#     from src.api.routes.communication.chat import router as chat_router
#     from src.api.routes.communication.chat_ws import router as chat_ws_router
#     from src.api.routes.communication.notificaciones import (
#         router as notificaciones_router,
#     )
#     from src.api.routes.communication.videollamadas import (
#         router as videollamadas_router,
#     )
# 
# except Exception:
#     import traceback
# 
#     traceback.print_exc()
#     chat_router = None
#     chat_ws_router = None
#     videollamadas_router = None
#     notificaciones_router = None
# 
from src.core.config import get_settings

settings = get_settings()

# Lista de routers a incluir en la aplicación
# Formato: (router, prefix, tags)
routers = [
    # Autenticación - router principal que incluye todos los sub-routers de auth
    (auth_router, "/auth", ["Autenticación"]),
    # Sistema de avatars
    (avatar_router, "/avatar", ["Avatars"]),
    # 🔥 Sistema de administración de instituciones (solo admin)
    (admin_router, "/admin", ["Administración"]),
    # 🔥 Sistema de invitaciones y registro público por dominio
    (invitaciones_router, "/invitaciones", ["Invitaciones"]),
    (coordinador_router, "/api/coordinador", ["Coordinador"]),
    (instituciones_publicas_router, "", ["Instituciones Públicas"]),
    # Sistema de evaluaciones y exámenes
    (evaluaciones_router, "/evaluaciones", ["Evaluaciones"]),
    # Sistema académico - MODULARIZADO
    (programa_router, "/api/programas", ["Programas"]),
    (grupo_router, "/api/grupos", ["Grupos/Clases"]),
    (cursos_router, "/api", ["Cursos"]),
    (inscripciones_curso_router, "/api", ["Inscripciones"]),
    (tareas_router, "/api", ["Tareas"]),
    (comentarios_router, "/api", ["Comentarios"]),
    (reacciones_router, "/api", ["Reacciones"]),
    (archivos_router, "/api", ["Archivos"]),
    (personas_router, "/api", ["Personas y Perfiles"]),
    (institucion_router, "/api/instituciones", ["Instituciones"]),
    # 🤖 Sistema de IA y Gamificación
    (ia_tareas_router, "/api", ["IA y Gamificación"]),
    # 🎮 Sistema de Gamificación
    (gamificacion_router, "/api/gamificacion", ["Gamificación"]),
]

# 💬 Agregar sistema de comunicación si se importó exitosamente
# if chat_router is not None:
#     routers.append((chat_router, "/api", ["Chat"]))
# 
# if chat_ws_router is not None:
#     routers.append((chat_ws_router, "/api", ["WebSocket Chat"]))
# 
# if videollamadas_router is not None:
#     routers.append((videollamadas_router, "/api/communication", ["Videollamadas"]))
# 
# if notificaciones_router is not None:
#     routers.append((notificaciones_router, "/api/communication", ["Notificaciones"]))

# Routers solo para desarrollo
if settings.is_development():
    routers.append((dev_email_router, "", ["Development-Email"]))
