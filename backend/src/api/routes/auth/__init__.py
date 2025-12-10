# src/api/routes/auth/__init__.py

"""Módulo de rutas de autenticación reorganizado.

Este módulo contiene todas las rutas relacionadas con autenticación
organizadas por funcionalidad:

- auth_core: Login, registro, logout, perfil básico
- auth_password: Gestión de contraseñas (cambio, recuperación)
- auth_2fa: Autenticación de dos factores (configuración, verificación)
- auth_users: CRUD de usuarios (solo administradores)
- auth_account: Gestión de cuentas (activar, desactivar, desbloquear)
- auth_health: Health check del sistema de autenticación
- auth_verify: Verificación de correo electrónico/número de teléfono
- oauth: Autenticación OAuth2 (Google, Facebook, etc.)
"""

from fastapi import APIRouter

from . import (
    auth_2fa,
    auth_account,
    auth_core,
    auth_health,
    auth_password,
    auth_users,
    auth_verify,
    oauth,  # Nuevo router de OAuth
)

# Crear el router principal de autenticación
auth_router = APIRouter()

# Incluir todos los sub-routers
auth_router.include_router(auth_2fa.router)
auth_router.include_router(auth_account.router)
auth_router.include_router(auth_core.router)
auth_router.include_router(auth_health.router)
auth_router.include_router(auth_password.router)
auth_router.include_router(auth_users.router)
auth_router.include_router(auth_verify.router)
auth_router.include_router(oauth.router)  # Router de OAuth


__all__ = [
    "password_router",
    "twofa_router",
    "users_router",
    "verify_router",
]
