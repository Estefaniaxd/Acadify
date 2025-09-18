from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import redis.asyncio as redis
from src.api.deps import get_db, get_redis_client, get_current_user
from src.services.auth.auth_service import AuthService
from src.schemas.auth.auth_schemas import EmailVerificationRequest, EmailVerificationResponse, AccountDeletionRequest, AccountDeletionResponse, AccountRestorationRequest
from src.models.users.usuario import Usuario
from pydantic import BaseModel

# Schema simple para código de eliminación
class DeletionCodeRequest(BaseModel):
    deletion_code: str

router = APIRouter(
    prefix="/auth",
    tags=["🔐 Autenticación - Verificación Email"],
    responses={
        400: {"description": "Código inválido o expirado"},
        404: {"description": "Usuario no encontrado"},
        500: {"description": "Error interno del servidor"}
    }
)

@router.post("/verify-email", response_model=EmailVerificationResponse)
async def verify_email(
    *,
    db: Session = Depends(get_db),
    redis_client: redis.Redis = Depends(get_redis_client),
    data: EmailVerificationRequest
):
    """
    Verificar correo electrónico con código recibido por email.
    """
    print(f"DEBUG ENDPOINT: Datos recibidos: {data}")
    auth_service = AuthService(redis_client)
    try:
        result = await auth_service.verify_email(db, data)
        return EmailVerificationResponse(message=result["message"])
    except HTTPException:
        # Re-raise HTTPExceptions sin modificar
        raise
    except Exception as e:
        print(f"DEBUG ENDPOINT: Error inesperado: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")

@router.post("/request-email-verification")
async def request_email_verification(
    *,
    db: Session = Depends(get_db),
    redis_client: redis.Redis = Depends(get_redis_client),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Solicitar nuevo código de verificación de email.
    Solo disponible para usuarios autenticados con email no verificado.
    """
    auth_service = AuthService(redis_client)
    try:
        result = await auth_service.request_email_verification(db, current_user.usuario_id)
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")

@router.post("/request-account-deletion")
async def request_account_deletion(
    *,
    db: Session = Depends(get_db),
    redis_client: redis.Redis = Depends(get_redis_client),
    current_user: Usuario = Depends(get_current_user),
    data: AccountDeletionRequest
):
    """
    Paso 1: Solicitar eliminación de cuenta (envía código de confirmación por email).
    Requiere confirmación de contraseña.
    """
    auth_service = AuthService(redis_client)
    try:
        result = await auth_service.request_account_deletion(db, current_user.usuario_id, data.password)
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")

@router.post("/confirm-account-deletion", response_model=AccountDeletionResponse)
async def confirm_account_deletion(
    *,
    db: Session = Depends(get_db),
    redis_client: redis.Redis = Depends(get_redis_client),
    current_user: Usuario = Depends(get_current_user),
    data: DeletionCodeRequest
):
    """
    Paso 2: Confirmar eliminación de cuenta con código recibido por email.
    La cuenta será marcada para eliminación con 30 días de gracia.
    """
    auth_service = AuthService(redis_client)
    try:
        result = await auth_service.confirm_account_deletion(db, current_user.usuario_id, data.deletion_code)
        return AccountDeletionResponse(**result)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")
