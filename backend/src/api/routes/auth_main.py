# src/api/routes/auth_main.py

"""
Router principal de autenticación que combina todos los sub-routers organizados.

Esta es la nueva estructura organizada que reemplaza el archivo auth.py monolítico.
"""

from fastapi import APIRouter

# Importar todos los sub-routers
from src.api.routes.auth import (
    core_router,
    password_router,
    twofa_router,
    users_router,
    account_router,
    health_router,
    verify_router
)

# Router principal que combina todos los sub-routers
router = APIRouter()

# Incluir todos los sub-routers
router.include_router(core_router)          # /auth/register, /auth/login, /auth/logout, /auth/me
router.include_router(password_router)      # /auth/forgot-password, /auth/reset-password, /auth/change-password
router.include_router(twofa_router)         # /auth/2fa/setup, /auth/2fa/verify, /auth/2fa/disable, /auth/2fa/status
router.include_router(users_router)        # /auth/users (CRUD - solo admins)
router.include_router(account_router)      # /auth/users/{id}/activate, /auth/users/{id}/deactivate, /auth/users/{id}/unlock
router.include_router(health_router)       # /auth/health
router.include_router(verify_router)       # /auth/verify-email