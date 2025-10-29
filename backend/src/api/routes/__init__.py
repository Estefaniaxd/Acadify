"""
Configuración central de routers para la aplicación FastAPI.

Esta lista define todos los routers que se incluirán en la aplicación principal.
Cada elemento es una tupla: (router, prefix, tags)
"""

from src.api.routes.auth_main import router as auth_router
from src.api.routes.avatar import router as avatar_router
from src.api.routes.dev_email import router as dev_email_router
from src.api.routes.evaluaciones import router as evaluaciones_router

# Routers académicos - REFACTORIZADOS Y MODULARIZADOS
from src.api.routes.academic.cursos import router as cursos_router
from src.api.routes.academic.inscripciones import router as inscripciones_router
from src.api.routes.academic.curso_tareas import router as tareas_router
from src.api.routes.academic.curso_comentarios import router as comentarios_router
from src.api.routes.academic.curso_reacciones import router as reacciones_router
from src.api.routes.academic.curso_archivos import router as archivos_router

from src.core.config import get_settings

settings = get_settings()

# Lista de routers a incluir en la aplicación
# Formato: (router, prefix, tags)
routers = [
    # Autenticación - router principal que incluye todos los sub-routers de auth
    (auth_router, "/auth", ["Autenticación"]),
    
    # Sistema de avatars
    (avatar_router, "/avatar", ["Avatars"]),
    
    # Sistema de evaluaciones y exámenes
    (evaluaciones_router, "/evaluaciones", ["Evaluaciones"]),
    
    # Sistema académico - MODULARIZADO
    (cursos_router, "/api", ["Cursos"]),
    (inscripciones_router, "/api", ["Inscripciones"]),
    (tareas_router, "/api", ["Tareas"]),
    (comentarios_router, "/api", ["Comentarios"]),
    (reacciones_router, "/api", ["Reacciones"]),
    (archivos_router, "/api", ["Archivos"]),
]

# Routers solo para desarrollo
if settings.is_development():
    routers.append((dev_email_router, "", ["Development-Email"]))