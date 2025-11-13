# src/api/routes/auth/auth_password.py

import logging
from typing import Any

from fastapi import APIRouter, Depends
import redis.asyncio as redis
from sqlalchemy.orm import Session

from src.api.deps import get_current_active_user, get_db, get_redis_client
from src.models.users.usuario import Usuario
from src.schemas.auth.auth_schemas import (
    MessageResponse,
    PasswordChangeRequest,
    PasswordResetConfirm,
    PasswordResetRequest,
    PasswordResetResponse,
    UserCurrentResponse,
    UserProfileUpdate,
)
from src.services.auth.auth_service import AuthService


logger = logging.getLogger(__name__)

# Router de gestión de contraseñas
router = APIRouter(
    tags=["🔑 Autenticación - Contraseñas"],
    responses={
        401: {"description": "Token inválido o usuario no autenticado"},
        403: {"description": "Permisos insuficientes"},
        500: {"description": "Error interno del servidor"},
    },
)

ERROR_INTERNO_SERVIDOR = "Error interno del servidor"


@router.post("/forgot-password", response_model=PasswordResetResponse)
async def request_password_reset(
    *,
    db: Session = Depends(get_db),
    redis_client: redis.Redis = Depends(get_redis_client),
    reset_request: PasswordResetRequest,
) -> Any:
    """Solicitar reset de contraseña. Envía código por email si el usuario existe.

    **Proceso:**
    - Verifica si el email existe en el sistema
    - Genera código de recuperación de 6 dígitos
    - Envía código por email (válido 15 minutos)
    - Respuesta siempre igual por seguridad

    **Seguridad:**
    - No revela si el email existe o no
    - Códigos tienen expiración corta (15 min)
    - Rate limiting aplicado (máximo 3 intentos por hora)

    **Respuestas:**
    - 200: Mensaje enviado (no revela si email existe)
    - 500: Error interno del servidor
    """
    auth_service = AuthService(redis_client)

    try:
        result = await auth_service.request_password_reset(db, reset_request)
        return PasswordResetResponse(message=result["message"])
    except Exception as e:
        logger.exception(f"Error en password reset request: {e}")
        # Siempre devolver mensaje genérico por seguridad
        return PasswordResetResponse()


@router.post("/reset-password", response_model=MessageResponse)
async def confirm_password_reset(
    *,
    db: Session = Depends(get_db),
    redis_client: redis.Redis = Depends(get_redis_client),
    reset_confirm: PasswordResetConfirm,
) -> Any:
    """Confirmar reset de contraseña con código recibido por email.

    **Datos requeridos:**
    - Email institucional
    - Código de recuperación (6 dígitos)
    - Nueva contraseña

    **Validaciones:**
    - Usuario debe existir
    - Código debe ser válido y no expirado
    - Nueva contraseña debe cumplir políticas de seguridad

    **Proceso:**
    - Valida código de recuperación
    - Actualiza contraseña con hash seguro
    - Invalida código usado
    - Envía confirmación por email

    **Respuestas:**
    - 200: Contraseña actualizada exitosamente
    - 400: Código inválido o expirado
    - 404: Usuario no encontrado
    - 500: Error interno del servidor
    """
    auth_service = AuthService(redis_client)

    try:
        result = await auth_service.reset_password(db, reset_confirm)
        return MessageResponse(message=result["message"])
    except Exception as e:
        logger.exception(f"Error confirmando password reset: {e}")
        raise


@router.post("/change-password", response_model=MessageResponse)
async def change_password(
    *,
    db: Session = Depends(get_db),
    redis_client: redis.Redis = Depends(get_redis_client),
    change_request: PasswordChangeRequest,
    current_user: Usuario = Depends(get_current_active_user),
) -> Any:
    """Cambiar contraseña (usuario autenticado).

    **Datos requeridos:**
    - Contraseña actual (para verificación)
    - Nueva contraseña

    **Validaciones:**
    - Usuario debe estar autenticado
    - Contraseña actual debe ser correcta
    - Nueva contraseña debe cumplir políticas de seguridad
    - Nueva contraseña debe ser diferente a la actual

    **Proceso:**
    - Verifica contraseña actual
    - Valida nueva contraseña
    - Actualiza hash en base de datos
    - No invalida sesiones activas

    **Respuestas:**
    - 200: Contraseña cambiada exitosamente
    - 400: Contraseña actual incorrecta o nueva contraseña inválida
    - 401: Usuario no autenticado
    - 500: Error interno del servidor
    """
    auth_service = AuthService(redis_client)

    try:
        result = await auth_service.change_password(
            db, current_user.usuario_id, change_request
        )
        return MessageResponse(message=result["message"])
    except Exception as e:
        logger.exception(f"Error cambiando contraseña: {e}")
        raise


@router.put("/me", response_model=UserCurrentResponse)
async def update_current_user_profile(
    *,
    db: Session = Depends(get_db),
    redis_client: redis.Redis = Depends(get_redis_client),
    user_update: UserProfileUpdate,
    current_user: Usuario = Depends(get_current_active_user),
) -> Any:
    """Actualizar perfil del usuario actual.

    **Campos actualizables:**
    - nombres: Nombres completos
    - apellidos: Apellidos completos
    - telefono: Número de teléfono
    - descripcion: Descripción personal o biografía

    **Campos NO actualizables:**
    - correo_institucional
    - username
    - numero_documento
    - rol
    - estado_cuenta

    **Validaciones:**
    - Usuario debe estar autenticado
    - Solo se actualizan campos proporcionados
    - Validación de formato en campos requeridos

    **Respuestas:**
    - 200: Perfil actualizado exitosamente
    - 400: Datos inválidos
    - 401: Usuario no autenticado
    - 403: Cuenta inactiva
    - 500: Error interno del servidor
    """
    auth_service = AuthService(redis_client)

    try:
        return auth_service.update_user_profile(
            db, current_user.usuario_id, user_update
        )
    except Exception as e:
        logger.exception(f"Error actualizando perfil: {e}")
        raise
