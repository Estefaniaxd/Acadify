# src/api/routes/auth/auth_core.py

import logging
from typing import Any

from fastapi import APIRouter, Depends, Header, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
import redis.asyncio as redis
from sqlalchemy.orm import Session

from src.api.deps import get_current_active_user, get_db, get_redis_client
from src.models.users.usuario import Usuario
from src.schemas.auth.auth_schemas import (
    LoginRequest,
    LoginStepResponse,
    LogoutResponse,
    RefreshResponse,
    RefreshTokenRequest,
    UserCurrentResponse,
)
from src.schemas.users.usuario import UsuarioCreate
from src.services.auth.auth_service import AuthService


logger = logging.getLogger(__name__)

# Router de autenticación básica
router = APIRouter(
    tags=["🔐 Autenticación - Core"],
    responses={
        401: {"description": "Token inválido o credenciales incorrectas"},
        403: {"description": "Permisos insuficientes o cuenta inactiva"},
        500: {"description": "Error interno del servidor"},
    },
)
security = HTTPBearer(
    bearerFormat="JWT",
    description="Token JWT obtenido del endpoint /auth/login. Formato: Bearer <your_jwt_token>",
)

ERROR_INTERNO_SERVIDOR = "Error interno del servidor"


@router.post(
    "/register", response_model=UserCurrentResponse, status_code=status.HTTP_201_CREATED
)
async def register_user(
    *,
    db: Session = Depends(get_db),
    redis_client: redis.Redis = Depends(get_redis_client),
    user_data: UsuarioCreate,
) -> Any:
    """Registrar nuevo usuario respetando constraints de base de datos.

    **Reglas de registro:**
    - **Todos los usuarios**: deben tener tanto `username` como `correo_institucional`

    **Validaciones:**
    - Contraseña debe cumplir políticas de seguridad
    - Email institucional debe ser único
    - Username debe ser único
    - Número de documento debe ser único

    **Respuestas:**
    - 201: Usuario creado exitosamente
    - 400: Datos inválidos o duplicados
    - 500: Error interno del servidor
    """
    auth_service = AuthService(redis_client)

    try:
        new_user = await auth_service.register_user(db, user_data)
        return UserCurrentResponse.model_validate(new_user)
    except Exception as e:
        logger.exception(f"Error en registro: {e}")
        raise


@router.post("/login", status_code=status.HTTP_200_OK)
async def login(
    *,
    db: Session = Depends(get_db),
    redis_client: redis.Redis = Depends(get_redis_client),
    login_data: LoginRequest,
) -> Any:
    """Autenticar usuario con soporte para 2FA.

    **Ejemplo de uso:**
    ```json
    {
        "identifier": "estebanAdmin",
        "password": "tu_contraseña_aqui"
    }
    ```

    **Respuesta exitosa:**
    ```json
    {
        "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
        "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
        "expires_in": 3600
    }
    ```

    **Usar el token:** Una vez obtenido el `access_token`, úsalo en el header Authorization:
    ```
    Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
    ```

    **Flujo básico (sin 2FA):**
    - Envía solo `identifier` y `password`
    - Deja `otp_code` vacío o null
    - Recibe tokens JWT directamente

    **Flujo con 2FA activado:**
    1. Primera llamada: solo `identifier` y `password`
    2. Backend responde "otp_required" y envía código por email/SMS
    3. Segunda llamada: mismos datos + `otp_code` recibido
    4. Backend responde con tokens JWT

    **Identificadores válidos:**
    - **Administradores**: pueden usar `username`
    - **Otros roles**: deben usar `correo_institucional`
    - Búsqueda es case-insensitive para emails

    **Respuestas:**
    - 200: Login exitoso → devuelve tokens JWT
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
        if result["status"] == "otp_required":
            return LoginStepResponse(
                status="otp_required",
                message=result["message"],
                requires_otp=result["requires_otp"],
                otp_method=result["otp_method"],
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error en login: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ERROR_INTERNO_SERVIDOR,
        ) from e


@router.post("/refresh", response_model=RefreshResponse)
async def refresh_access_token(
    *,
    db: Session = Depends(get_db),
    redis_client: redis.Redis = Depends(get_redis_client),
    refresh_data: RefreshTokenRequest,
) -> Any:
    """Refrescar access token usando refresh token válido.

    **Uso:**
    - Cuando el access token está próximo a expirar
    - El refresh token debe estar activo y no en blacklist
    - Devuelve nuevo access token (refresh token se mantiene)

    **Respuestas:**
    - 200: Token refrescado exitosamente
    - 401: Refresh token inválido o expirado
    - 500: Error interno del servidor
    """
    auth_service = AuthService(redis_client)

    try:
        new_tokens = await auth_service.refresh_token(db, refresh_data.refresh_token)
        return RefreshResponse(
            access_token=new_tokens.access_token, expires_in=new_tokens.expires_in
        )
    except Exception as e:
        logger.exception(f"Error refrescando token: {e}")
        raise


@router.post("/logout", response_model=LogoutResponse)
async def logout(
    *,
    redis_client: redis.Redis = Depends(get_redis_client),
    credentials: HTTPAuthorizationCredentials = Depends(security),
    refresh_token: str = Header(None, alias="X-Refresh-Token"),
) -> Any:
    """Cerrar sesión añadiendo tokens a blacklist.

    **Tokens requeridos:**
    - Access token en Authorization header (Bearer <token>)
    - Refresh token en header X-Refresh-Token (opcional)

    **Proceso:**
    - Ambos tokens se añaden a blacklist
    - Tokens quedan inutilizables hasta su expiración natural
    - Logout se considera exitoso incluso con errores

    **Respuestas:**
    - 200: Logout procesado exitosamente
    """
    auth_service = AuthService(redis_client)

    try:
        access_token = credentials.credentials
        result = await auth_service.logout(access_token, refresh_token or "")
        return LogoutResponse(message=result["message"])
    except Exception as e:
        logger.exception(f"Error en logout: {e}")
        # Siempre considerar logout como exitoso
        return LogoutResponse(message="Logout procesado")


@router.get("/me", response_model=UserCurrentResponse)
async def get_current_user_info(
    db: Session = Depends(get_db),
    redis_client: redis.Redis = Depends(get_redis_client),
    current_user: Usuario = Depends(get_current_active_user),
) -> Any:
    """Obtener información del usuario actual autenticado.

    **Información incluida:**
    - Datos personales (nombres, apellidos, documento)
    - Información de contacto (email, teléfono)
    - Estado de cuenta y configuraciones
    - Configuración de 2FA
    - Fechas de creación y último acceso

    **Autenticación requerida:** Token JWT válido

    **Respuestas:**
    - 200: Información del usuario
    - 401: Token inválido o usuario no autenticado
    - 403: Cuenta inactiva
    """
    auth_service = AuthService(redis_client)

    try:
        return auth_service.get_current_user_profile(db, current_user.usuario_id)
    except Exception as e:
        logger.exception(f"Error obteniendo perfil: {e}")
        raise
