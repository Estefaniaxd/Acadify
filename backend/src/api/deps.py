# src/api/deps.py

from typing import Generator, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from uuid import UUID
import redis.asyncio as redis
import logging

from src.db.base_session import SessionLocal
from src.models.users.usuario import Usuario
from src.crud.user.usuario import usuario_crud
from src.utils.security import security_manager, get_token_blacklist
from src.enums.users.usuario_enums import EstadoCuentaUsuario, RolUsuario
from src.core.config import get_settings

logger = logging.getLogger(__name__)
security = HTTPBearer()
settings = get_settings()

# ===============================
# Database Dependencies
# ===============================

def get_db() -> Generator:
    """Dependency to get database session"""
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


# ===============================
# Redis Dependencies  
# ===============================

async def get_redis_client() -> redis.Redis:
    """Dependency to get Redis client"""
    try:
        # Create async Redis client using the connection string
        client = redis.from_url(
            f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/{settings.REDIS_DB}",
            decode_responses=True
        )
        # Test connection
        await client.ping()
        return client
    except Exception as e:
        logger.error(f"Error creating Redis client: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error de conexión a Redis"
        )


# ===============================
# Authentication Dependencies
# ===============================

# ===============================
# Token Validation Helpers
# ===============================

def _validate_token_format(token: str) -> None:
    """Validate basic JWT token format"""
    if not token or len(token.strip()) == 0:
        logger.warning("Empty or missing token")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token requerido",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Check if token has basic JWT structure (3 parts separated by dots)
    token_parts = token.split('.')
    if len(token_parts) != 3:
        logger.warning(f"Token inválido: Not enough segments. Token parts: {len(token_parts)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido: formato incorrecto",
            headers={"WWW-Authenticate": "Bearer"},
        )


def _validate_token_payload(payload: dict) -> None:
    """Validate token payload structure"""
    if payload.get("type") != "access":
        logger.warning(f"Invalid token type: {payload.get('type')}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token tipo inválido",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user_id_str = payload.get("sub")
    if not user_id_str:
        logger.warning("Token missing 'sub' claim")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido - sin usuario",
            headers={"WWW-Authenticate": "Bearer"},
        )


def _extract_user_id(payload: dict) -> UUID:
    """Extract and validate user ID from token payload"""
    user_id_str = payload.get("sub")
    try:
        return UUID(user_id_str)
    except ValueError as e:
        logger.warning(f"Invalid UUID in token sub claim: {user_id_str}, error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="ID de usuario inválido",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_user_from_token(
    db: Session = Depends(get_db),
    redis_client: redis.Redis = Depends(get_redis_client),
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> Usuario:
    """
    Extract and validate current user from JWT token.
    
    Validates token, checks blacklist, and retrieves user from database.
    """
    token = credentials.credentials
    
    # Log token info for debugging (safely)
    logger.debug(f"Validating token with length: {len(token) if token else 0}")
    logger.debug(f"Token starts with: {token[:10] if token and len(token) >= 10 else 'N/A'}...")
    
    # Basic token format validation
    _validate_token_format(token)
    
    try:
        # Decode and validate token
        payload = security_manager.decode_token(token)
        logger.debug(f"Token decoded successfully for user: {payload.get('sub', 'unknown')}")
        
        # Validate payload structure
        _validate_token_payload(payload)
        
        # Check token blacklist
        token_blacklist = get_token_blacklist(redis_client)
        if await token_blacklist.is_blacklisted(token):
            logger.warning("Token found in blacklist")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token revocado",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Extract user ID from token
        user_id = _extract_user_id(payload)
        
        # Get user from database
        user = usuario_crud.get(db, id=user_id)
        if not user:
            logger.warning(f"User not found in database: {user_id}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Usuario no encontrado",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        logger.debug(f"User authenticated successfully: {user.username or user.correo_institucional}")
        return user
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Token inválido: {str(e)}")
        # Provide more specific error message if possible
        error_detail = "Token inválido o expirado"
        if "signature" in str(e).lower():
            error_detail = "Token con firma inválida"
        elif "expired" in str(e).lower():
            error_detail = "Token expirado"
        elif "not enough segments" in str(e).lower():
            error_detail = "Token malformado"
        
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=error_detail,
            headers={"WWW-Authenticate": "Bearer"},
        )


def get_current_user(
    current_user: Usuario = Depends(get_current_user_from_token)
) -> Usuario:
    """
    Dependency to get current authenticated user.
    """
    return current_user


def get_current_active_user(
    current_user: Usuario = Depends(get_current_user)
) -> Usuario:
    """
    Dependency to get current active user.
    
    Ensures user account is in active state.
    """
    if current_user.estado_cuenta != EstadoCuentaUsuario.activo:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cuenta inactiva"
        )
    
    return current_user


def get_current_admin_user(
    current_user: Usuario = Depends(get_current_active_user)
) -> Usuario:
    """
    Dependency to ensure current user is an administrator.
    """
    if current_user.rol != RolUsuario.administrador:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Se requieren permisos de administrador"
        )
    
    return current_user


# ===============================
# Role-based Dependencies
# ===============================

def get_current_coordinador(
    current_user: Usuario = Depends(get_current_active_user)
) -> Usuario:
    """
    Dependency to ensure current user is a coordinator.
    """
    if current_user.rol != RolUsuario.coordinador:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Se requieren permisos de coordinador"
        )
    
    return current_user


def get_current_docente(
    current_user: Usuario = Depends(get_current_active_user)
) -> Usuario:
    """
    Dependency to ensure current user is a teacher.
    """
    if current_user.rol != RolUsuario.docente:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Se requieren permisos de docente"
        )
    
    return current_user


def get_current_estudiante(
    current_user: Usuario = Depends(get_current_active_user)
) -> Usuario:
    """
    Dependency to ensure current user is a student.
    """
    if current_user.rol != RolUsuario.estudiante:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Se requieren permisos de estudiante"
        )
    
    return current_user


def get_current_docente_or_coordinador(
    current_user: Usuario = Depends(get_current_active_user)
) -> Usuario:
    """
    Dependency to ensure current user is either a teacher or coordinator.
    """
    allowed_roles = [RolUsuario.docente, RolUsuario.coordinador]
    
    if current_user.rol not in allowed_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Se requieren permisos de docente o coordinador"
        )
    
    return current_user


def get_current_admin_or_coordinador(
    current_user: Usuario = Depends(get_current_active_user)
) -> Usuario:
    """
    Dependency to ensure current user is either an admin or coordinator.
    """
    allowed_roles = [RolUsuario.administrador, RolUsuario.coordinador]
    
    if current_user.rol not in allowed_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Se requieren permisos de administrador o coordinador"
        )
    
    return current_user


# ===============================
# Optional Authentication
# ===============================

async def get_current_user_optional(
    db: Session = Depends(get_db),
    redis_client: redis.Redis = Depends(get_redis_client),
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(
        HTTPBearer(auto_error=False)
    )
) -> Optional[Usuario]:
    """
    Dependency to optionally get current user.
    
    Returns user if valid token is provided, None otherwise.
    Useful for endpoints that work both authenticated and unauthenticated.
    """
    if not credentials:
        return None
    
    try:
        return await get_current_user_from_token(db, redis_client, credentials)
    except HTTPException:
        return None
    except Exception:
        return None


# ===============================
# Custom Permission Dependencies
# ===============================

class RequireRoles:
    """
    Custom dependency class to check for specific roles.
    
    Usage:
        @router.get("/admin-only")
        def admin_endpoint(user: Usuario = Depends(RequireRoles([RolUsuario.administrador]))):
            pass
    """
    
    def __init__(self, allowed_roles: list[RolUsuario]):
        self.allowed_roles = allowed_roles
    
    def __call__(self, current_user: Usuario = Depends(get_current_active_user)) -> Usuario:
        if current_user.rol not in self.allowed_roles:
            roles_str = ", ".join([role.value for role in self.allowed_roles])
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Se requiere uno de los siguientes roles: {roles_str}"
            )
        return current_user


class RequireVerifiedEmail:
    """
    Custom dependency to ensure user has verified email.
    """
    
    def __call__(self, current_user: Usuario = Depends(get_current_active_user)) -> Usuario:
        if not current_user.email_verified:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Se requiere email verificado"
            )
        return current_user


class RequireTwoFA:
    """
    Custom dependency to ensure user has 2FA enabled.
    """
    
    def __call__(self, current_user: Usuario = Depends(get_current_active_user)) -> Usuario:
        if not current_user.twofa_enabled:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Se requiere autenticación de dos factores habilitada"
            )
        return current_user


# ===============================
# Rate Limiting Dependencies
# ===============================

class RateLimitChecker:
    """
    Simple rate limiting dependency using Redis.
    """
    
    def __init__(self, max_requests: int, window_seconds: int):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
    
    async def __call__(
        self, 
        request,
        redis_client: redis.Redis = Depends(get_redis_client),
        current_user: Optional[Usuario] = Depends(get_current_user_optional)
    ):
        # Use user ID if authenticated, otherwise IP address
        if current_user:
            identifier = f"rate_limit_user:{current_user.usuario_id}"
        else:
            client_ip = request.client.host
            identifier = f"rate_limit_ip:{client_ip}"
        
        # Check current count
        current_count = await redis_client.get(identifier)
        
        if current_count is None:
            # First request in window
            await redis_client.setex(identifier, self.window_seconds, 1)
        else:
            current_count = int(current_count)
            if current_count >= self.max_requests:
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="Too many requests"
                )
            else:
                await redis_client.incr(identifier)


# ===============================
# Commonly Used Rate Limiters
# ===============================

# Login rate limiting: 10 attempts per 15 minutes
login_rate_limit = RateLimitChecker(max_requests=10, window_seconds=900)

# Password reset rate limiting: 3 requests per hour
password_reset_rate_limit = RateLimitChecker(max_requests=3, window_seconds=3600)

# General API rate limiting: 1000 requests per hour for authenticated users
api_rate_limit = RateLimitChecker(max_requests=1000, window_seconds=3600)

# Email sending rate limiting: 10 emails per hour
email_rate_limit = RateLimitChecker(max_requests=10, window_seconds=3600)