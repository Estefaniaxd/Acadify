# src/api/routes/auth/__init__.py

"""
Módulo de rutas de autenticación reorganizado.

Este módulo contiene todas las rutas relacionadas con autenticación
organizadas por funcionalidad:

- auth_core: Login, registro, logout, perfil básico
- auth_password: Gestión de contraseñas (cambio, recuperación)
- auth_2fa: Autenticación de dos factores (configuración, verificación)
- auth_users: CRUD de usuarios (solo administradores)
- auth_account: Gestión de cuentas (activar, desactivar, desbloquear)
- auth_health: Health check del sistema de autenticación
"""

from .auth_core import router as core_router
from .auth_password import router as password_router
from .auth_2fa import router as twofa_router
from .auth_users import router as users_router
from .auth_account import router as account_router
from .auth_health import router as health_router

__all__ = [
    "core_router",
    "password_router", 
    "twofa_router",
    "users_router",
    "account_router",
    "health_router"
]