# src/api/routes.py

"""
Configuración central de routers para la aplicación FastAPI.

Esta lista define todos los routers que se incluirán en la aplicación principal.
Cada elemento es una tupla: (router, prefix, tags)
"""

from src.api.routes.auth_main import router as auth_router

# Lista de routers a incluir en la aplicación
# Formato: (router, prefix, tags)
routers = [
    # Autenticación - router principal que incluye todos los sub-routers de auth
    (auth_router, "/auth", ["Autenticación"]),
]