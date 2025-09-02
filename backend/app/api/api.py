# backend/app/api/api.py
"""
Router principal de la API
Agrupa todas las rutas de los diferentes módulos
"""
from fastapi import APIRouter

from app.api.endpoints import (
    auth, users, institutions, programs, 
    courses, groups, classes, assignments, 
    chat, gamification
)

api_router = APIRouter()

# Incluir rutas de autenticación
api_router.include_router(
    auth.router, 
    prefix="/auth", 
    tags=["Autenticación"]
)

# Incluir rutas de usuarios
api_router.include_router(
    users.router, 
    prefix="/users", 
    tags=["Usuarios"]
)

# Incluir rutas de instituciones
api_router.include_router(
    institutions.router, 
    prefix="/institutions", 
    tags=["Instituciones"]
)

# Incluir rutas de programas
api_router.include_router(
    programs.router, 
    prefix="/programs", 
    tags=["Programas"]
)

# Incluir rutas de cursos
api_router.include_router(
    courses.router, 
    prefix="/courses", 
    tags=["Cursos"]
)

# Incluir rutas de grupos
api_router.include_router(
    groups.router, 
    prefix="/groups", 
    tags=["Grupos"]
)

# Incluir rutas de clases
api_router.include_router(
    classes.router, 
    prefix="/classes", 
    tags=["Clases"]
)

# Incluir rutas de tareas
api_router.include_router(
    assignments.router, 
    prefix="/assignments", 
    tags=["Tareas"]
)

# Incluir rutas de chat
api_router.include_router(
    chat.router, 
    prefix="/chat", 
    tags=["Chat"]
)

# Incluir rutas de gamificación
api_router.include_router(
    gamification.router, 
    prefix="/gamification", 
    tags=["Gamificación"]
)