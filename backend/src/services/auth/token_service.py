import jwt
import uuid
from datetime import timedelta
from src.services.auth.datetime_utils import utcnow_aware
from typing import Optional, Dict, Any
from jose import JWTError
from src.core.config import settings
from src.services.auth.redis_service import RedisService


class TokenService:
    """Servicio centralizado para operaciones con tokens JWT"""
    
    def __init__(self, redis_service: RedisService):
        self.redis_service = redis_service
        self.algorithm = settings.JWT_ALGORITHM
        self.secret_key = settings.JWT_SECRET
    
    def create_access_token(
        self, 
        user_id: str, 
        roles: list[str], 
        expires_delta: Optional[timedelta] = None
    ) -> tuple[str, str]:
        """
        Crear access token JWT
        
        Returns:
            tuple: (token, jti) - token y su identificador único
        """
        if expires_delta:
            expire = utcnow_aware() + expires_delta
        else:
            expire = utcnow_aware() + timedelta(
                minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
            )
        
        # Generar JTI único para este token
        jti = str(uuid.uuid4())
        
        payload = {
            "sub": str(user_id),  # Subject: usuario
            "exp": expire,        # Expiration time
            "iat": utcnow_aware(),  # Issued at
            "jti": jti,          # JWT ID para revocación
            "roles": roles,      # Roles del usuario
            "type": "access"     # Tipo de token
        }
        
        token = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
        return token, jti
    
    def create_refresh_token(
        self, 
        user_id: str, 
        expires_delta: Optional[timedelta] = None
    ) -> tuple[str, str]:
        """
        Crear refresh token JWT
        
        Returns:
            tuple: (token, jti) - token y su identificador único
        """
        if expires_delta:
            expire = utcnow_aware() + expires_delta
        else:
            expire = utcnow_aware() + timedelta(
                days=settings.REFRESH_TOKEN_EXPIRE_DAYS
            )
        
        jti = str(uuid.uuid4())
        
        payload = {
            "sub": str(user_id),
            "exp": expire,
            "iat": utcnow_aware(),
            "jti": jti,
            "type": "refresh"
        }
        
        token = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
        return token, jti
    
    def decode_token(self, token: str) -> Dict[str, Any]:
        """
        Decodificar y validar token JWT
        
        Raises:
            JWTError: Si el token es inválido, expiró o está revocado
        """
        try:
            payload = jwt.decode(
                token, 
                self.secret_key, 
                algorithms=[self.algorithm]
            )
            
            # Verificar si el token está revocado
            jti = payload.get("jti")
            if jti and self.is_token_revoked(jti):
                raise JWTError("Token revocado")
            
            return payload
            
        except jwt.ExpiredSignatureError:
            raise JWTError("Token expirado")
        except jwt.InvalidTokenError:
            raise JWTError("Token inválido")
    
    def is_token_revoked(self, jti: str) -> bool:
        """Verificar si un token está en la blacklist de Redis"""
        return self.redis_service.is_token_blacklisted(jti)
    
    def revoke_token(self, jti: str, ttl_seconds: int) -> None:
        """Agregar token a la blacklist de Redis"""
        self.redis_service.blacklist_token(jti, ttl_seconds)
    
    def revoke_all_user_tokens(self, user_id: str) -> None:
        """Revocar todos los refresh tokens de un usuario"""
        self.redis_service.revoke_all_user_refresh_tokens(str(user_id))
    
    def store_refresh_token(self, user_id: str, jti: str, ttl_seconds: int) -> None:
        """Almacenar refresh token activo en Redis"""
        self.redis_service.store_active_refresh_token(str(user_id), jti, ttl_seconds)
    
    def get_token_ttl(self, token_type: str) -> int:
        """Obtener TTL en segundos según el tipo de token"""
        if token_type == "access":
            return settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        elif token_type == "refresh":
            return settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60
        else:
            return 3600