from datetime import timedelta
from typing import Any
import uuid

from jose import JWTError
import jwt

from src.core.config import settings
from src.services.auth.datetime_utils import utcnow_aware
from src.services.auth.redis_service import RedisService


class TokenService:
    """Servicio centralizado para operaciones con tokens JWT."""

    def __init__(self, redis_service: RedisService) -> None:
        self.redis_service = redis_service
        self.algorithm = settings.ALGORITHM
        self.secret_key = settings.SECRET_KEY

    def create_access_token(
        self, user_id: str, roles: list[str], expires_delta: timedelta | None = None
    ) -> tuple[str, str]:
        """Crear access token JWT.

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
            "exp": int(expire.timestamp()),  # Expiration time
            "iat": int(utcnow_aware().timestamp()),  # Issued at
            "jti": jti,  # JWT ID para revocación
            "roles": roles,  # Roles del usuario
            "type": "access",  # Tipo de token
        }

        token = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
        return token, jti

    def create_refresh_token(
        self, user_id: str, expires_delta: timedelta | None = None
    ) -> tuple[str, str]:
        """Crear refresh token JWT.

        Returns:
            tuple: (token, jti) - token y su identificador único
        """
        if expires_delta:
            expire = utcnow_aware() + expires_delta
        else:
            expire = utcnow_aware() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)

        jti = str(uuid.uuid4())

        payload = {
            "sub": str(user_id),
            "exp": expire,
            "iat": utcnow_aware(),
            "jti": jti,
            "type": "refresh",
        }

        token = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
        return token, jti

    async def decode_token(self, token: str) -> dict[str, Any]:
        """Decodificar y validar token JWT de acceso.

        Raises:
            JWTError: Si el token es inválido, expiró o está revocado
        """
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            # Verificar si el token está revocado
            jti = payload.get("jti")
            if jti and await self.is_token_revoked(jti):
                msg = "El token ha sido revocado"
                raise JWTError(msg)
            if payload.get("type") != "access":
                msg = "El token no es de tipo acceso"
                raise JWTError(msg)
            return payload
        except jwt.ExpiredSignatureError:
            msg = "El token ha expirado"
            raise JWTError(msg) from None
        except jwt.InvalidTokenError:
            msg = "El token es inválido"
            raise JWTError(msg) from None

    async def decode_refresh_token(self, token: str) -> str:
        """Decodificar y validar token JWT de refresco.

        Returns:
            str: user_id (sub)

        Raises:
            JWTError: Si el token es inválido, expiró o está revocado
        """
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            jti = payload.get("jti")
            if jti and await self.is_token_revoked(jti):
                msg = "El token de refresco ha sido revocado"
                raise JWTError(msg)
            if payload.get("type") != "refresh":
                msg = "El token no es de tipo refresco"
                raise JWTError(msg)
            return payload.get("sub")
        except jwt.ExpiredSignatureError:
            msg = "El token de refresco ha expirado"
            raise JWTError(msg) from None
        except jwt.InvalidTokenError:
            msg = "El token de refresco es inválido"
            raise JWTError(msg) from None

    async def is_token_revoked(self, jti: str) -> bool:
        """Verificar si un token está en la blacklist de Redis."""
        return await self.redis_service.is_token_blacklisted(jti)

    def revoke_token(self, jti: str, ttl_seconds: int) -> None:
        """Agregar token a la blacklist de Redis."""
        self.redis_service.blacklist_token(jti, ttl_seconds)

    def revoke_all_user_tokens(self, user_id: str) -> None:
        """Revocar todos los refresh tokens de un usuario."""
        self.redis_service.revoke_all_user_refresh_tokens(str(user_id))

    def store_refresh_token(self, user_id: str, jti: str, ttl_seconds: int) -> None:
        """Almacenar refresh token activo en Redis."""
        self.redis_service.store_active_refresh_token(str(user_id), jti, ttl_seconds)

    def get_token_ttl(self, token_type: str) -> int:
        """Obtener TTL en segundos según el tipo de token."""
        if token_type == "access":
            return settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        if token_type == "refresh":
            return settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60
        return 3600
