from src.schemas.auth.auth_schemas import EmailVerificationRequest, EmailVerificationResponse

from fastapi import APIRouter, Depends, HTTPException
# ===============================
# Authentication Endpoints
# ===============================

# Endpoint para verificar email

router = APIRouter()

@router.post("/verify-email", response_model=EmailVerificationResponse)
async def verify_email(
    *,
    db: Session = Depends(get_db),
    redis_client: redis.Redis = Depends(get_redis_client),
    data: EmailVerificationRequest
) -> Any:
    """
    Verificar correo electrónico con código recibido por email.
    """
    auth_service = AuthService(redis_client)
    try:
        result = await auth_service.verify_email(db, data)
        return EmailVerificationResponse(message=result["message"])
    except Exception as e:
        logger.error(f"Error en verificación de email: {e}")
        raise HTTPException(status_code=400, detail="No se pudo verificar el correo")
# src/api/routers/auth.py

from typing import Any, Dict
from fastapi import APIRouter, Depends, HTTPException, status, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from uuid import UUID
import logging

from src.api.deps import get_db, get_redis_client, get_current_user, get_current_active_user
from src.services.auth.auth_service import AuthService
from src.schemas.auth.auth_schemas import (
    LoginRequest, TokenResponse, RefreshTokenRequest, RefreshResponse,
    PasswordResetRequest, PasswordResetResponse, PasswordResetConfirm,
    PasswordChangeRequest, TwoFASetupRequest, TwoFASetupResponse,
    TwoFAVerifyRequest, TwoFAVerifyResponse, TwoFADisableRequest,
    TwoFAStatusResponse, UserCurrentResponse, UserProfileUpdate,
    LoginStepResponse, LogoutResponse, MessageResponse
)
from src.schemas.users.usuario import UsuarioCreate
from src.models.users.usuario import Usuario
from src.utils.security import security_manager
import redis.asyncio as redis


logger = logging.getLogger(__name__)

# Constantes para mensajes de error repetidos
ERROR_INTERNO_SERVIDOR = "Error interno del servidor"
USUARIO_NO_ENCONTRADO = "Usuario no encontrado"


# Router de autenticación
router = APIRouter(prefix="/auth", tags=["Autenticación"])
security = HTTPBearer()

# ===============================
# Authentication Endpoints
# ===============================

@router.post("/register", response_model=UserCurrentResponse, status_code=status.HTTP_201_CREATED)
async def register_user(
    *,
    db: Session = Depends(get_db),
    redis_client: redis.Redis = Depends(get_redis_client),
    user_data: UsuarioCreate
) -> Any:
    """
    Registrar nuevo usuario respetando constraints de base de datos.
    
    - **Administradores**: deben tener `username` y NO `correo_institucional`
    - **Otros roles**: deben tener `correo_institucional` y NO `username`
    """
    auth_service = AuthService(redis_client)
    
    try:
        new_user = await auth_service.register_user(db, user_data)
        return UserCurrentResponse.model_validate(new_user)
    except Exception as e:
        logger.error(f"Error en registro: {e}")
        raise


@router.post("/login", status_code=status.HTTP_200_OK)
async def login(
    *,
    db: Session = Depends(get_db),
    redis_client: redis.Redis = Depends(get_redis_client),
    login_data: LoginRequest
) -> Any:
    """
    Autenticar usuario con soporte para 2FA.
    
    **Flujo básico (sin 2FA):**
    - Envía solo `identifier` y `password`
    - Deja `otp_code` vacío o null
    - Recibe tokens JWT directamente
    
    **Flujo con 2FA activado:**
    1. Primera llamada: solo `identifier` y `password`
    2. Backend responde "otp_required" y envía código por email/SMS
    3. Segunda llamada: mismos datos + `otp_code` recibido
    4. Backend responde con tokens JWT
    
    **Respuestas:**
    - 200: Login exitoso → devuelve tokens
    - 202: Se requiere OTP → revisa tu email y reenvía con el código
    - 401: Credenciales incorrectas
    - 423: Cuenta bloqueada por intentos fallidos
    
    **Importante:** Solo llena `otp_code` si el backend te lo solicita en respuesta previa.
    """
    auth_service = AuthService(redis_client)
    
    try:
        result = await auth_service.authenticate_user(db, login_data)
        
        if result["status"] == "success":
            return result["tokens"]
        elif result["status"] == "otp_required":
            return LoginStepResponse(
                status="otp_required",
                message=result["message"],
                requires_otp=result["requires_otp"],
                otp_method=result["otp_method"]
            )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error en login: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ERROR_INTERNO_SERVIDOR
        )


@router.post("/refresh", response_model=RefreshResponse)
async def refresh_access_token(
    *,
    db: Session = Depends(get_db),
    redis_client: redis.Redis = Depends(get_redis_client),
    refresh_data: RefreshTokenRequest
) -> Any:
    """
    Refrescar access token usando refresh token válido.
    """
    auth_service = AuthService(redis_client)
    
    try:
        new_tokens = await auth_service.refresh_token(db, refresh_data.refresh_token)
        return RefreshResponse(
            access_token=new_tokens.access_token,
            expires_in=new_tokens.expires_in
        )
    except Exception as e:
        logger.error(f"Error refrescando token: {e}")
        raise


@router.post("/logout", response_model=LogoutResponse)
async def logout(
    *,
    redis_client: redis.Redis = Depends(get_redis_client),
    credentials: HTTPAuthorizationCredentials = Depends(security),
    refresh_token: str = Header(None, alias="X-Refresh-Token")
) -> Any:
    """
    Cerrar sesión añadiendo tokens a blacklist.
    
    Requiere access token en Authorization header y opcionalmente
    refresh token en header X-Refresh-Token.
    """
    auth_service = AuthService(redis_client)
    
    try:
        access_token = credentials.credentials
        result = await auth_service.logout(access_token, refresh_token or "")
        return LogoutResponse(message=result["message"])
    except Exception as e:
        logger.error(f"Error en logout: {e}")
        # Siempre considerar logout como exitoso
        return LogoutResponse(message="Logout procesado")


# ===============================
# Password Management
# ===============================

@router.post("/forgot-password", response_model=PasswordResetResponse)
async def request_password_reset(
    *,
    db: Session = Depends(get_db),
    redis_client: redis.Redis = Depends(get_redis_client),
    reset_request: PasswordResetRequest
) -> Any:
    """
    Solicitar reset de contraseña. Envía código por email si el usuario existe.
    
    Por seguridad, siempre devuelve el mismo mensaje sin revelar si el email existe.
    """
    auth_service = AuthService(redis_client)
    
    try:
        result = await auth_service.request_password_reset(db, reset_request)
        return PasswordResetResponse(message=result["message"])
    except Exception as e:
        logger.error(f"Error en password reset request: {e}")
        # Siempre devolver mensaje genérico por seguridad
        return PasswordResetResponse()


@router.post("/reset-password", response_model=MessageResponse)
async def confirm_password_reset(
    *,
    db: Session = Depends(get_db),
    redis_client: redis.Redis = Depends(get_redis_client),
    reset_confirm: PasswordResetConfirm
) -> Any:
    """
    Confirmar reset de contraseña con código recibido por email.
    """
    auth_service = AuthService(redis_client)
    
    try:
        result = await auth_service.reset_password(db, reset_confirm)
        return MessageResponse(message=result["message"])
    except Exception as e:
        logger.error(f"Error confirmando password reset: {e}")
        raise


@router.post("/change-password", response_model=MessageResponse)
async def change_password(
    *,
    db: Session = Depends(get_db),
    redis_client: redis.Redis = Depends(get_redis_client),
    change_request: PasswordChangeRequest,
    current_user: Usuario = Depends(get_current_active_user)
) -> Any:
    """
    Cambiar contraseña (usuario autenticado).
    """
    auth_service = AuthService(redis_client)
    
    try:
        result = await auth_service.change_password(db, current_user.usuario_id, change_request)
        return MessageResponse(message=result["message"])
    except Exception as e:
        logger.error(f"Error cambiando contraseña: {e}")
        raise


# ===============================
# Two-Factor Authentication
# ===============================

@router.post("/2fa/setup", response_model=TwoFASetupResponse)
async def setup_2fa(
    *,
    db: Session = Depends(get_db),
    redis_client: redis.Redis = Depends(get_redis_client),
    setup_request: TwoFASetupRequest,
    current_user: Usuario = Depends(get_current_active_user)
) -> Any:
    """
    Iniciar configuración de 2FA.
    
    - **email**: Envía código de verificación al correo
    - **totp**: Genera secret y QR code para app de autenticación
    """
    auth_service = AuthService(redis_client)
    
    try:
        result = await auth_service.setup_2fa(db, current_user.usuario_id, setup_request)
        return result
    except Exception as e:
        logger.error(f"Error configurando 2FA: {e}")
        raise


@router.post("/2fa/verify", response_model=TwoFAVerifyResponse)
async def verify_2fa_setup(
    *,
    db: Session = Depends(get_db),
    redis_client: redis.Redis = Depends(get_redis_client),
    verify_request: TwoFAVerifyRequest,
    current_user: Usuario = Depends(get_current_active_user)
) -> Any:
    """
    Verificar y completar configuración de 2FA.
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


@router.post("/2fa/disable", response_model=MessageResponse)
async def disable_2fa(
    *,
    db: Session = Depends(get_db),
    redis_client: redis.Redis = Depends(get_redis_client),
    disable_request: TwoFADisableRequest,
    current_user: Usuario = Depends(get_current_active_user)
) -> Any:
    """
    Desactivar 2FA. Requiere contraseña actual para confirmación.
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


@router.get("/2fa/status", response_model=TwoFAStatusResponse)
async def get_2fa_status(
    current_user: Usuario = Depends(get_current_active_user)
) -> Any:
    """
    Obtener estado de 2FA del usuario actual.
    """
    twofa_method = getattr(current_user, 'twofa_method', None)
    
    return TwoFAStatusResponse(
        twofa_enabled=current_user.twofa_enabled,
        twofa_method=twofa_method
    )


# ===============================
# User Profile Management
# ===============================

@router.get("/me", response_model=UserCurrentResponse)
async def get_current_user_info(
    db: Session = Depends(get_db),
    redis_client: redis.Redis = Depends(get_redis_client),
    current_user: Usuario = Depends(get_current_active_user)
) -> Any:
    """
    Obtener información del usuario actual autenticado.
    """
    auth_service = AuthService(redis_client)
    
    try:
        return auth_service.get_current_user_profile(db, current_user.usuario_id)
    except Exception as e:
        logger.error(f"Error obteniendo perfil: {e}")
        raise


@router.put("/me", response_model=UserCurrentResponse)
async def update_current_user_profile(
    *,
    db: Session = Depends(get_db),
    redis_client: redis.Redis = Depends(get_redis_client),
    user_update: UserProfileUpdate,
    current_user: Usuario = Depends(get_current_active_user)
) -> Any:
    """
    Actualizar perfil del usuario actual.
    
    Permite actualizar: nombres, apellidos, teléfono, descripción.
    """
    auth_service = AuthService(redis_client)
    
    try:
        return await auth_service.update_user_profile(db, current_user.usuario_id, user_update)
    except Exception as e:
        logger.error(f"Error actualizando perfil: {e}")
        raise


# ===============================
# Admin User CRUD Endpoints
# ===============================

@router.post("/users", response_model=UserCurrentResponse, status_code=status.HTTP_201_CREATED)
async def create_user_by_admin(
    *,
    db: Session = Depends(get_db),
    redis_client: redis.Redis = Depends(get_redis_client),
    user_data: UsuarioCreate,
    current_user: Usuario = Depends(get_current_active_user)
) -> Any:
    """
    Crear usuario (solo administradores).
    
    Endpoint para que administradores creen usuarios de cualquier rol.
    """
    # Verificar permisos de admin
    if current_user.rol.value != "administrador":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo administradores pueden crear usuarios"
        )
    
    auth_service = AuthService(redis_client)
    
    try:
        new_user = await auth_service.register_user(db, user_data)
        return UserCurrentResponse.model_validate(new_user)
    except Exception as e:
        logger.error(f"Error creando usuario (admin): {e}")
        raise


@router.get("/users", response_model=list[UserCurrentResponse])
async def list_users(
    *,
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    role: str = None,
    search: str = None,
    current_user: Usuario = Depends(get_current_active_user)
) -> Any:
    """
    Listar usuarios con paginación y filtros (solo administradores).
    
    **Filtros disponibles:**
    - role: filtrar por rol específico
    - search: buscar por nombre, email o documento
    """
    # Verificar permisos de admin
    if current_user.rol.value != "administrador":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo administradores pueden listar usuarios"
        )
    
    try:
        from src.crud.user.usuario import usuario_crud
        from src.enums.users.usuario_enums import RolUsuario
        
        if search:
            # Buscar usuarios por texto
            role_filter = None
            if role:
                try:
                    role_filter = RolUsuario(role)
                except ValueError:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Rol inválido"
                    )
            
            users = usuario_crud.search_users(
                db, query=search, role=role_filter, skip=skip, limit=limit
            )
        elif role:
            # Filtrar por rol
            try:
                role_filter = RolUsuario(role)
                users = usuario_crud.get_users_by_role(
                    db, rol=role_filter, skip=skip, limit=limit
                )
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Rol inválido"
                )
        else:
            # Listar todos los usuarios activos
            users = usuario_crud.get_active_users(db, skip=skip, limit=limit)
        
        return [UserCurrentResponse.model_validate(user) for user in users]
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error listando usuarios: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ERROR_INTERNO_SERVIDOR
        )


@router.get("/users/{user_id}", response_model=UserCurrentResponse)
async def get_user_by_id(
    *,
    db: Session = Depends(get_db),
    user_id: UUID,
    current_user: Usuario = Depends(get_current_active_user)
) -> Any:
    """
    Obtener usuario por ID (solo administradores).
    """
    # Verificar permisos de admin
    if current_user.rol.value != "administrador":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo administradores pueden ver otros usuarios"
        )
    
    try:
        from src.crud.user.usuario import usuario_crud
        
        user = usuario_crud.get(db, id=user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=USUARIO_NO_ENCONTRADO
            )
        
        return UserCurrentResponse.model_validate(user)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error obteniendo usuario {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ERROR_INTERNO_SERVIDOR
        )


@router.put("/users/{user_id}", response_model=UserCurrentResponse)
async def update_user_by_admin(
    *,
    db: Session = Depends(get_db),
    user_id: UUID,
    user_update: UserProfileUpdate,
    current_user: Usuario = Depends(get_current_active_user)
) -> Any:
    """
    Actualizar usuario por ID (solo administradores).
    """
    # Verificar permisos de admin
    if current_user.rol.value != "administrador":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo administradores pueden editar otros usuarios"
        )
    
    try:
        from src.crud.user.usuario import usuario_crud
        
        user = usuario_crud.get(db, id=user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=USUARIO_NO_ENCONTRADO
            )
        
        # Actualizar usuario
        update_dict = user_update.model_dump(exclude_unset=True)
        updated_user = usuario_crud.update(db, db_obj=user, obj_in=update_dict)
        
        return UserCurrentResponse.model_validate(updated_user)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error actualizando usuario {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ERROR_INTERNO_SERVIDOR
        )


@router.delete("/users/{user_id}", response_model=MessageResponse)
async def delete_user_by_admin(
    *,
    db: Session = Depends(get_db),
    user_id: UUID,
    current_user: Usuario = Depends(get_current_active_user)
) -> Any:
    """
    Eliminar usuario por ID (soft delete - solo administradores).
    
    Realiza un soft delete marcando el estado como "eliminado".
    """
    # Verificar permisos de admin
    if current_user.rol.value != "administrador":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo administradores pueden eliminar usuarios"
        )
    
    # Prevenir auto-eliminación
    if user_id == current_user.usuario_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No puede eliminar su propia cuenta"
        )
    
    try:
        from src.crud.user.usuario import usuario_crud
        
        user = usuario_crud.get(db, id=user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=USUARIO_NO_ENCONTRADO
            )
        
        # Soft delete
        usuario_crud.delete_account(db, user_id=user_id)
        
        return MessageResponse(message="Usuario eliminado exitosamente")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error eliminando usuario {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ERROR_INTERNO_SERVIDOR
        )


# ===============================
# Account Management Endpoints
# ===============================

@router.post("/users/{user_id}/activate", response_model=MessageResponse)
async def activate_user_account(
    *,
    db: Session = Depends(get_db),
    user_id: UUID,
    current_user: Usuario = Depends(get_current_active_user)
) -> Any:
    """
    Activar cuenta de usuario (solo administradores).
    """
    # Verificar permisos de admin
    if current_user.rol.value != "administrador":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo administradores pueden activar cuentas"
        )
    
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


@router.post("/users/{user_id}/deactivate", response_model=MessageResponse)
async def deactivate_user_account(
    *,
    db: Session = Depends(get_db),
    user_id: UUID,
    current_user: Usuario = Depends(get_current_active_user)
) -> Any:
    """
    Desactivar cuenta de usuario (solo administradores).
    """
    # Verificar permisos de admin
    if current_user.rol.value != "administrador":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo administradores pueden desactivar cuentas"
        )
    
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


@router.post("/users/{user_id}/unlock", response_model=MessageResponse)
async def unlock_user_account(
    *,
    db: Session = Depends(get_db),
    user_id: UUID,
    current_user: Usuario = Depends(get_current_active_user)
) -> Any:
    """
    Desbloquear cuenta de usuario (resetear intentos fallidos - solo administradores).
    """
    # Verificar permisos de admin
    if current_user.rol.value != "administrador":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo administradores pueden desbloquear cuentas"
        )
    
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
# Health Check
# ===============================

@router.get("/health")
async def auth_health_check(
    redis_client: redis.Redis = Depends(get_redis_client)
) -> Dict[str, Any]:
    """
    Health check del sistema de autenticación.
    """
    try:
        # Test Redis connection
        await redis_client.ping()
        redis_status = "healthy"
    except Exception as e:
        logger.error(f"Redis connection failed: {e}")
        redis_status = "unhealthy"
    
    return {
        "status": "healthy" if redis_status == "healthy" else "degraded",
        "components": {
            "redis": redis_status,
            "auth_service": "healthy"
        }
    }
