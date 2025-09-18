# src/api/routes/auth/auth_2fa.py

from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import logging

from src.api.deps import get_db, get_redis_client, get_current_active_user
from src.services.auth.auth_service import AuthService
from src.schemas.auth.auth_schemas import (
    TwoFASetupRequest, TwoFASetupResponse, TwoFAVerifyRequest, 
    TwoFAVerifyResponse, TwoFADisableRequest, TwoFAStatusResponse,
    MessageResponse
)
from src.models.users.usuario import Usuario
import redis.asyncio as redis

logger = logging.getLogger(__name__)

# Router de autenticación de dos factores
router = APIRouter(
    prefix="/auth/2fa", 
    tags=["🛡️ Autenticación - 2FA"],
    responses={
        401: {"description": "Token inválido o usuario no autenticado"},
        403: {"description": "Permisos insuficientes o 2FA requerido"},
        500: {"description": "Error interno del servidor"}
    }
)

ERROR_INTERNO_SERVIDOR = "Error interno del servidor"


@router.post("/setup", response_model=TwoFASetupResponse)
async def setup_2fa(
    *,
    db: Session = Depends(get_db),
    redis_client: redis.Redis = Depends(get_redis_client),
    setup_request: TwoFASetupRequest,
    current_user: Usuario = Depends(get_current_active_user)
) -> Any:
    """
    Iniciar configuración de 2FA.
    
    **Métodos disponibles:**
    - **email**: Códigos OTP enviados por correo electrónico
    - **totp**: App de autenticación (Google Authenticator, Authy, etc.)
    
    **Flujo por email:**
    1. Selecciona método "email"
    2. Se envía código de verificación al correo institucional
    3. Confirma con código recibido en /2fa/verify
    
    **Flujo por TOTP:**
    1. Selecciona método "totp"
    2. Recibe secret y QR code
    3. Escanea QR en tu app de autenticación
    4. Confirma con código de la app en /2fa/verify
    
    **Requisitos:**
    - Usuario autenticado
    - Para email: debe tener correo_institucional
    - 2FA no debe estar ya activado
    
    **Respuestas:**
    - 200: Configuración iniciada
    - 400: Método no soportado o 2FA ya activado
    - 401: Usuario no autenticado
    - 403: Sin correo institucional (para método email)
    - 500: Error interno del servidor
    """
    auth_service = AuthService(redis_client)
    
    try:
        result = await auth_service.setup_2fa(db, current_user.usuario_id, setup_request)
        return result
    except Exception as e:
        logger.error(f"Error configurando 2FA: {e}")
        raise


@router.post("/verify", response_model=TwoFAVerifyResponse)
async def verify_2fa_setup(
    *,
    db: Session = Depends(get_db),
    redis_client: redis.Redis = Depends(get_redis_client),
    verify_request: TwoFAVerifyRequest,
    current_user: Usuario = Depends(get_current_active_user)
) -> Any:
    """
    Verificar y completar configuración de 2FA.
    
    **Proceso:**
    - Valida código de verificación según método configurado
    - Activa 2FA permanentemente en la cuenta
    - Guarda configuración en base de datos
    - Invalida configuración temporal
    
    **Para método email:**
    - Verifica código de 6 dígitos enviado por correo
    - Código válido por 10 minutos
    
    **Para método TOTP:**
    - Verifica código de 6 dígitos de la app
    - Código válido por 30 segundos (window estándar TOTP)
    - Guarda secret para verificaciones futuras
    
    **Respuestas:**
    - 200: 2FA activado exitosamente
    - 400: Código incorrecto o configuración expirada
    - 401: Usuario no autenticado
    - 500: Error interno del servidor
    """
    auth_service = AuthService(redis_client)
    
    try:
        result = await auth_service.verify_2fa_setup(db, current_user.usuario_id, verify_request)
        return TwoFAVerifyResponse(
            success=result["success"],
            message=result["message"],
            twofa_enabled=result["twofa_enabled"]
        )
    except Exception as e:
        logger.error(f"Error verificando 2FA setup: {e}")
        raise


@router.post("/disable", response_model=MessageResponse)
async def disable_2fa(
    *,
    db: Session = Depends(get_db),
    redis_client: redis.Redis = Depends(get_redis_client),
    disable_request: TwoFADisableRequest,
    current_user: Usuario = Depends(get_current_active_user)
) -> Any:
    """
    Desactivar 2FA. Requiere contraseña actual para confirmación.
    
    **Proceso de seguridad:**
    - Verifica contraseña actual del usuario
    - Desactiva 2FA en la cuenta
    - Elimina secrets y configuraciones
    - No afecta sesiones activas
    
    **Datos requeridos:**
    - Contraseña actual para confirmación
    
    **Consideraciones:**
    - Acción irreversible (debe reconfigurar desde cero)
    - Recomendado solo en casos necesarios
    - Reduce nivel de seguridad de la cuenta
    
    **Respuestas:**
    - 200: 2FA desactivado exitosamente
    - 400: Contraseña incorrecta
    - 401: Usuario no autenticado
    - 403: 2FA no estaba activado
    - 500: Error interno del servidor
    """
    auth_service = AuthService(redis_client)
    
    try:
        result = await auth_service.disable_2fa(
            db, current_user.usuario_id, disable_request.current_password
        )
        return MessageResponse(message=result["message"])
    except Exception as e:
        logger.error(f"Error desactivando 2FA: {e}")
        raise


@router.get("/status", response_model=TwoFAStatusResponse)
async def get_2fa_status(
    current_user: Usuario = Depends(get_current_active_user)
) -> Any:
    """
    Obtener estado de 2FA del usuario actual.
    
    **Información devuelta:**
    - twofa_enabled: Si 2FA está activado
    - twofa_method: Método configurado (email/totp) o null
    
    **Casos de uso:**
    - Verificar si usuario tiene 2FA activado
    - Mostrar método configurado en UI
    - Decidir flujo de autenticación
    
    **Estados posibles:**
    - 2FA desactivado: twofa_enabled=false, twofa_method=null
    - 2FA por email: twofa_enabled=true, twofa_method="email"  
    - 2FA por TOTP: twofa_enabled=true, twofa_method="totp"
    
    **Respuestas:**
    - 200: Estado de 2FA obtenido
    - 401: Usuario no autenticado
    - 500: Error interno del servidor
    """
    twofa_method = getattr(current_user, 'twofa_method', None)
    
    return TwoFAStatusResponse(
        twofa_enabled=current_user.twofa_enabled,
        twofa_method=twofa_method
    )