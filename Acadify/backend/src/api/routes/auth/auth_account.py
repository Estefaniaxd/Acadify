# src/api/routes/auth/auth_account.py

from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from uuid import UUID
import redis.asyncio as redis
import logging
from datetime import datetime, timedelta

from src.api.deps import get_db, get_current_active_user, get_redis_client, get_current_user
from src.schemas.auth.auth_schemas import (
    MessageResponse, AccountDeletionRequest, AccountDeletionResponse, 
    AccountRestorationRequest
)
from src.models.users.usuario import Usuario
from src.services.auth.auth_service import AuthService
from src.utils.security import security_manager

logger = logging.getLogger(__name__)

# Router de gestión de cuentas (solo administradores)
router = APIRouter(
    prefix="/auth/users", 
    tags=["⚙️ Autenticación - Gestión de Cuentas (Admin)"],
    responses={
        401: {"description": "Token inválido o usuario no autenticado"},
        403: {"description": "Solo administradores pueden acceder"},
        404: {"description": "Usuario no encontrado"},
        500: {"description": "Error interno del servidor"}
    }
)

ERROR_INTERNO_SERVIDOR = "Error interno del servidor"
USUARIO_NO_ENCONTRADO = "Usuario no encontrado"


def _verify_admin_permissions(current_user: Usuario) -> None:
    """Verificar que el usuario actual es administrador"""
    if current_user.rol.value != "administrador":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo administradores pueden realizar esta acción"
        )


@router.post("/{user_id}/activate", response_model=MessageResponse)
async def activate_user_account(
    *,
    db: Session = Depends(get_db),
    user_id: UUID,
    current_user: Usuario = Depends(get_current_active_user)
) -> Any:
    """
    Activar cuenta de usuario (solo administradores).
    
    **Permisos requeridos:** Rol administrador
    
    **Funcionalidad:**
    - Cambia estado de cuenta a "activo"
    - Usuario puede volver a iniciar sesión
    - Restaura acceso completo a la plataforma
    
    **Estados de cuenta válidos para activación:**
    - suspendido: Cuenta suspendida temporalmente
    - inactivo: Cuenta creada pero no activada
    - eliminado: Cuenta marcada como eliminada (soft delete)
    
    **Efectos:**
    - Estado → activo
    - Reinicia contadores de seguridad
    - Usuario recibe acceso inmediato
    
    **Casos de uso:**
    - Reactivar cuentas suspendidas
    - Activar cuentas creadas por admin
    - Restaurar cuentas eliminadas por error
    
    **Respuestas:**
    - 200: Cuenta activada exitosamente
    - 403: Permisos insuficientes
    - 404: Usuario no encontrado
    - 500: Error interno del servidor
    """
    _verify_admin_permissions(current_user)
    
    try:
        from src.crud.user.usuario import usuario_crud
        
        user = usuario_crud.get(db, id=user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=USUARIO_NO_ENCONTRADO
            )
        
        usuario_crud.activate_account(db, user_id=user_id)
        
        return MessageResponse(message="Cuenta activada exitosamente")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error activando cuenta {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ERROR_INTERNO_SERVIDOR
        )


@router.post("/{user_id}/deactivate", response_model=MessageResponse)
async def deactivate_user_account(
    *,
    db: Session = Depends(get_db),
    user_id: UUID,
    current_user: Usuario = Depends(get_current_active_user)
) -> Any:
    """
    Desactivar cuenta de usuario (solo administradores).
    
    **Permisos requeridos:** Rol administrador
    
    **Funcionalidad:**
    - Cambia estado de cuenta a "suspendido"
    - Usuario no puede iniciar sesión
    - Preserva todos los datos
    - Acción reversible
    
    **Restricciones:**
    - Administrador no puede desactivar su propia cuenta
    - Solo se puede desactivar cuentas activas
    
    **Efectos:**
    - Estado → suspendido
    - Sesiones activas siguen funcionando hasta expirar
    - Nuevos logins son rechazados
    - Datos permanecen intactos
    
    **Diferencia con eliminación:**
    - Desactivación: temporal, reversible, fácil reactivación
    - Eliminación: permanente, requiere intervención técnica
    
    **Casos de uso:**
    - Suspensión disciplinaria temporal
    - Inactividad prolongada del usuario
    - Cambios temporales de rol/permisos
    
    **Respuestas:**
    - 200: Cuenta desactivada exitosamente
    - 400: Intento de auto-desactivación
    - 403: Permisos insuficientes
    - 404: Usuario no encontrado
    - 500: Error interno del servidor
    """
    _verify_admin_permissions(current_user)
    
    # Prevenir auto-desactivación
    if user_id == current_user.usuario_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No puede desactivar su propia cuenta"
        )
    
    try:
        from src.crud.user.usuario import usuario_crud
        
        user = usuario_crud.get(db, id=user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=USUARIO_NO_ENCONTRADO
            )
        
        usuario_crud.deactivate_account(db, user_id=user_id)
        
        return MessageResponse(message="Cuenta desactivada exitosamente")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error desactivando cuenta {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ERROR_INTERNO_SERVIDOR
        )


@router.post("/{user_id}/unlock", response_model=MessageResponse)
async def unlock_user_account(
    *,
    db: Session = Depends(get_db),
    user_id: UUID,
    current_user: Usuario = Depends(get_current_active_user)
) -> Any:
    """
    Desbloquear cuenta de usuario (resetear intentos fallidos - solo administradores).
    
    **Permisos requeridos:** Rol administrador
    
    **Funcionalidad:**
    - Reinicia contador de intentos fallidos de login
    - Elimina lockout temporal por intentos fallidos
    - Permite al usuario intentar login inmediatamente
    
    **Cuándo usar:**
    - Usuario bloqueado por múltiples intentos fallidos
    - Usuario olvidó contraseña y fue bloqueado
    - Necesidad de acceso urgente del usuario
    
    **Efectos:**
    - failed_login_attempts → 0
    - locked_until → null
    - Usuario puede intentar login inmediatamente
    - No afecta estado de cuenta (activo/suspendido)
    
    **Consideraciones de seguridad:**
    - Usar solo cuando el admin confía en la identidad del usuario
    - Considerar si el bloqueo fue por motivo legítimo
    - Usuario debe cambiar contraseña si la olvidó
    
    **Alternativas recomendadas:**
    - Esperar expiración automática del lockout
    - Usuario use recuperación de contraseña
    - Verificar identidad antes de desbloquear
    
    **Respuestas:**
    - 200: Cuenta desbloqueada exitosamente
    - 403: Permisos insuficientes
    - 404: Usuario no encontrado
    - 500: Error interno del servidor
    """
    _verify_admin_permissions(current_user)
    
    try:
        from src.crud.user.usuario import usuario_crud
        
        user = usuario_crud.get(db, id=user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=USUARIO_NO_ENCONTRADO
            )
        
        usuario_crud.reset_failed_login_attempts(db, user_id=user_id)
        
        return MessageResponse(message="Cuenta desbloqueada exitosamente")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error desbloqueando cuenta {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ERROR_INTERNO_SERVIDOR
        )

# ===============================
# Eliminación de Cuenta de Usuario
# ===============================

@router.delete("/delete-account", response_model=AccountDeletionResponse)
async def delete_account(
    *,
    db: Session = Depends(get_db),
    redis_client: redis.Redis = Depends(get_redis_client),
    current_user: Usuario = Depends(get_current_user),
    data: AccountDeletionRequest,
    request: Request
):
    """
    Marcar cuenta para eliminación con período de gracia de 30 días.
    
    Requiere:
    - Contraseña actual correcta
    - Texto de confirmación exacto
    - Usuario autenticado
    
    Durante el período de gracia:
    - La cuenta se mantiene activa pero marcada para eliminación
    - Se puede restaurar usando el token enviado por email
    - Después de 30 días se elimina permanentemente
    """
    auth_service = AuthService(redis_client)
    
    # Verificar contraseña actual
    if not security_manager.verify_password(data.current_password, current_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Contraseña incorrecta"
        )
    
    # Calcular fecha de eliminación (30 días)
    grace_period_days = 30
    deletion_date = datetime.now() + timedelta(days=grace_period_days)
    
    # Generar token de restauración
    restoration_token = f"rest_{security_manager.generate_otp_code(32)}"
    
    # Guardar en Redis con TTL de 30 días
    restore_key = f"restore_account:{current_user.usuario_id}"
    await redis_client.setex(restore_key, grace_period_days * 24 * 3600, restoration_token)
    
    # Marcar usuario para eliminación (agregar campo o estado)
    # Por ahora, guardamos la info en Redis
    deletion_info = {
        "user_id": str(current_user.usuario_id),
        "deletion_date": deletion_date.isoformat(),
        "restoration_token": restoration_token,
        "reason": data.reason or "",
        "ip_address": request.client.host,
        "user_agent": request.headers.get("user-agent", ""),
        "requested_at": datetime.now().isoformat()
    }
    
    deletion_key = f"pending_deletion:{current_user.usuario_id}"
    await redis_client.setex(deletion_key, grace_period_days * 24 * 3600, str(deletion_info))
    
    # Enviar email de notificación
    try:
        await auth_service.email_service.send_template_email(
            to_email=current_user.correo_institucional,
            subject="Eliminación de cuenta programada - Acadify",
            template_name="account_deletion_notification.html",
            context={
                "nombre": f"{current_user.nombres} {current_user.apellidos}",
                "dias_restantes": grace_period_days,
                "fecha_eliminacion_final": deletion_date.strftime("%d/%m/%Y a las %H:%M"),
                "fecha_solicitud": datetime.now().strftime("%d/%m/%Y a las %H:%M"),
                "ip_address": request.client.host,
                "dispositivo": request.headers.get("user-agent", "Dispositivo desconocido")[:100],
                "email_cuenta": current_user.correo_institucional,
                "usuario_id": str(current_user.usuario_id),
                "enlace_restaurar": f"https://acadify.com/restore-account?token={restoration_token}",
                "enlace_soporte": "https://acadify.com/soporte"
            }
        )
    except Exception as e:
        # Log error pero no fallar la operación
        print(f"Error enviando email de eliminación: {e}")
    
    return AccountDeletionResponse(
        message=f"Tu cuenta será eliminada permanentemente el {deletion_date.strftime('%d/%m/%Y')}. Revisa tu email para instrucciones de restauración.",
        grace_period_days=grace_period_days,
        deletion_date=deletion_date,
        restoration_token=restoration_token
    )

@router.post("/restore-account", response_model=MessageResponse)
async def restore_account(
    *,
    db: Session = Depends(get_db),
    redis_client: redis.Redis = Depends(get_redis_client),
    data: AccountRestorationRequest
):
    """
    Restaurar cuenta que estaba marcada para eliminación.
    
    Requiere:
    - Token de restauración válido (recibido por email)
    - Contraseña actual correcta
    
    Solo funciona durante el período de gracia (30 días).
    """
    # Buscar el token en todas las claves de restauración
    keys = await redis_client.keys("restore_account:*")
    user_id = None
    
    for key in keys:
        stored_token = await redis_client.get(key)
        if stored_token:
            # El stored_token puede ser bytes o string
            if isinstance(stored_token, bytes):
                stored_token_str = stored_token.decode()
            else:
                stored_token_str = str(stored_token)
            
            if stored_token_str == data.restoration_token:
                user_id = key.decode().split(":")[-1] if isinstance(key, bytes) else key.split(":")[-1]
                break
    
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Token de restauración inválido o expirado"
        )
    
    # Obtener usuario
    from src.crud.user.usuario import usuario_crud
    user = usuario_crud.get(db, id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    
    # Verificar contraseña
    if not security_manager.verify_password(data.current_password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Contraseña incorrecta"
        )
    
    # Limpiar datos de eliminación
    restore_key = f"restore_account:{user_id}"
    deletion_key = f"pending_deletion:{user_id}"
    
    await redis_client.delete(restore_key)
    await redis_client.delete(deletion_key)
    
    # Enviar email de confirmación de restauración
    auth_service = AuthService(redis_client)
    try:
        await auth_service.email_service.send_template_email(
            to_email=user.correo_institucional,
            subject="Cuenta restaurada exitosamente - Acadify",
            template_name="password_changed_notification.html",  # Reutilizamos plantilla
            context={
                "nombre": f"{user.nombres} {user.apellidos}",
                "fecha_hora": datetime.now().strftime("%d/%m/%Y a las %H:%M"),
                "ip_address": "Sistema",
                "dispositivo": "Restauración de cuenta",
                "metodo": "Restauración por token",
                "enlace_soporte": "https://acadify.com/soporte",
                "enlace_configuracion": "https://acadify.com/configuracion"
            }
        )
    except Exception as e:
        print(f"Error enviando email de restauración: {e}")
    
    return MessageResponse(
        message="Tu cuenta ha sido restaurada exitosamente. Ya puedes continuar usándola normalmente."
    )