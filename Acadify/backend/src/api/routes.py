# src/api/routes.py

"""
Configuración central de routers para la aplicación FastAPI.

Esta lista define todos los routers que se incluirán en la aplicación principal.
Cada elemento es una tupla: (router, prefix, tags)
"""

from src.api.routes.auth_main import router as auth_router
from src.api.routes.avatar import router as avatar_router
from src.api.routes.dev_email import router as dev_email_router
from src.api.routes.evaluaciones import router as evaluaciones_router

# Routers académicos
from src.api.routes.academic.curso import router as curso_router
# from src.api.routes.academic.grupo import router as grupo_router
# from src.api.routes.academic.material_educativo import router as material_router
# from src.api.routes.academic.institucion import router as institucion_router

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
    
    # Sistema académico (router registrado directamente en main.py)
    # (curso_router, "/academic", ["Cursos"]),
    # (grupo_router, "/academic/grupos", ["Grupos"]),
    # (material_router, "/academic/material", ["Material Educativo"]),
    # (institucion_router, "/instituciones", ["Instituciones"]),
]

# Routers solo para desarrollo
if settings.is_development():
    routers.append((dev_email_router, "", ["Development-Email"]))