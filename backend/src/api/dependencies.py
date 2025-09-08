from datetime import datetime, timedelta
from typing import Optional, List
from fastapi import Depends, HTTPException, status, Cookie, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError
from sqlalchemy.orm import Session

from src.db.session import get_db
from src.models.users.usuario import Usuario
from src.services.auth.token_service import TokenService
from src.services.auth.redis_service import RedisService
from src.services.auth.password_service import PasswordService
from src.crud.auth.user_crud import UserCRUD
from src.enums.users.usuario_enums import RolUsuario

# Instancias de servicios (idealmente inyectados por DI container)
redis_service = RedisService()
token_service = TokenService(redis_service)
password_service = PasswordService()
user_crud = UserCRUD(password_service)

security = HTTPBearer(auto_error=False)


async def get_redis_service() -> RedisService:
    """Dependency para obtener RedisService"""
    if not redis_service.redis:
        await redis_service.connect()
    return redis_service



def get_token_service() -> TokenService:
    """Dependency para obtener TokenService"""
    return token_service


def get_password_service() -> PasswordService:
    """Dependency para obtener PasswordService"""
    return password_service


def get_user_crud() -> UserCRUD:
    """Dependency para obtener UserCRUD"""
    return user_crud


def get_current_user(
    db: Session = Depends(get_db),
    token_service: TokenService = Depends(get_token_service),
    user_crud: UserCRUD = Depends(get_user_crud),
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    access_token: Optional[str] = Cookie(None)  # También soportar cookies
) -> Usuario:
    """
    Dependency para obtener usuario actual desde JWT token
    
    Soporta Authorization header y cookies
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    # Obtener token desde header Authorization o cookie
    token = None
    if credentials:
        token = credentials.credentials
    elif access_token:
        token = access_token
    
    if not token:
        raise credentials_exception
    
    try:
        # Decodificar y validar token
        payload = token_service.decode_token(token)
        user_id: str = payload.get("sub")
        token_type: str = payload.get("type")
        
        if user_id is None or token_type != "access":
            raise credentials_exception
        
        # Obtener usuario desde DB
        user = user_crud.get_by_id(db, user_id)
        if user is None:
            raise credentials_exception
        
        # Verificar que la cuenta esté activa
        if user.estado_cuenta != "activo":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account is not active"
            )
        
        return user
        
    except JWTError:
        raise credentials_exception


def require_roles(*required_roles: RolUsuario):
    """
    Dependency factory para requerir roles específicos
    
    Usage:
        @app.get("/admin-only", dependencies=[Depends(require_roles(RolUsuario.administrador))])
    """
    def check_roles(current_user: Usuario = Depends(get_current_user)):
        if current_user.rol not in required_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions"
            )
        return current_user
    
    return check_roles


def require_admin():
    """Dependency para requerir rol de administrador"""
    return require_roles(RolUsuario.administrador)


def require_admin_or_coordinator():
    """Dependency para requerir rol admin o coordinador"""
    return require_roles(RolUsuario.administrador, RolUsuario.coordinador)


def require_verified_email():
    """Dependency para requerir email verificado"""
    def check_verified(current_user: Usuario = Depends(get_current_user)):
        if not current_user.email_verified:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Email verification required"
            )
        return current_user
    
    return check_verified


async def rate_limit(
    identifier: str = None,
    endpoint: str = "general",
    max_requests: int = 60,
    window_seconds: int = 3600,
    redis_service: RedisService = Depends(get_redis_service)
):
    """
    Dependency para rate limiting
    
    Args:
        identifier: Identificador único (IP, user_id, etc.)
        endpoint: Nombre del endpoint
        max_requests: Máximo número de requests
        window_seconds: Ventana de tiempo en segundos
    """
    if not identifier:
        # Si no se proporciona identificador, usar un placeholder
        identifier = "anonymous"
    
    is_allowed, _, reset_time = await redis_service.check_rate_limit(
        identifier, endpoint, max_requests, window_seconds
    )
    
    if not is_allowed:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Rate limit exceeded. Try again in {reset_time} seconds.",
            headers={
                "Retry-After": str(reset_time),
                "X-RateLimit-Limit": str(max_requests),
                "X-RateLimit-Remaining": "0",
                "X-RateLimit-Reset": str(reset_time)
            }
        )


# Rate limiting específico para login
async def login_rate_limit(
    redis_service: RedisService = Depends(get_redis_service)
):
    """Rate limit específico para endpoint de login"""
    return await rate_limit(
        identifier="login_global",  # Se puede personalizar por IP
        endpoint="login",
        max_requests=10,  # 10 intentos de login
        window_seconds=300,  # en 5 minutos
        redis_service=redis_service
    )


def get_client_ip(x_forwarded_for: Optional[str] = Header(None)) -> str:
    """Obtener IP del cliente considerando proxies"""
    if x_forwarded_for:
        # Tomar la primera IP de la lista
        return x_forwarded_for.split(",")[0].strip()
    return "unknown"


# Validación CSRF para cookies
def validate_csrf_token(
    csrf_token: Optional[str] = Header(None, alias="X-CSRF-Token"),
    csrf_cookie: Optional[str] = Cookie(None, alias="csrf_token")
):
    """
    Validar token CSRF para requests que usan cookies
    
    Implementa double-submit cookie pattern
    """
    if not csrf_token or not csrf_cookie:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="CSRF token missing"
        )
    
    if csrf_token != csrf_cookie:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="CSRF token mismatch"
        )
    
    return csrf_token