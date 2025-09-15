# src/api/routes/auth/auth_account.py

from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID
import logging

from src.api.deps import get_db, get_current_active_user
from src.schemas.auth.auth_schemas import MessageResponse
from src.models.users.usuario import Usuario

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