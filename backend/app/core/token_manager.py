"""
Gestión de JWT para Acadify
Incluye creación, decodificación y verificación de Access y Refresh Tokens
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any

from jose import jwt, JWTError
from fastapi import HTTPException, status

from app.core.config import settings


class TokenManager:
    """Clase para manejo de tokens JWT"""

    @staticmethod
    def create_access_token(
        data: dict,
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """
        Crea un JWT de acceso.
        Args:
            data: Diccionario con payload (ej. {"sub": user_id})
            expires_delta: Duración opcional
        Returns:
            Token JWT como string
        """
        to_encode = data.copy()
        expire = datetime.utcnow() + (expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
        to_encode.update({"exp": expire, "type": "access"})
        return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

    @staticmethod
    def create_refresh_token(
        data: dict,
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """
        Crea un JWT de refresh.
        Args:
            data: Diccionario con payload
            expires_delta: Duración opcional
        Returns:
            Token JWT como string
        """
        to_encode = data.copy()
        expire = datetime.utcnow() + (expires_delta or timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS))
        to_encode.update({"exp": expire, "type": "refresh"})
        return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

    @staticmethod
    def decode_token(token: str, expected_type: Optional[str] = None) -> Dict[str, Any]:
        """
        Decodifica un JWT.
        Args:
            token: JWT
            expected_type: "access" o "refresh" para validar tipo de token
        Returns:
            Payload decodificado
        Raises:
            HTTPException si es inválido o expirado
        """
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            if expected_type and payload.get("type") != expected_type:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Tipo de token inválido")
            return payload
        except JWTError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token inválido o expirado")

    @staticmethod
    def verify_access_token(token: str) -> Dict[str, Any]:
        """Verifica un access token y retorna payload"""
        return TokenManager.decode_token(token, expected_type="access")

    @staticmethod
    def verify_refresh_token(token: str) -> Dict[str, Any]:
        """Verifica un refresh token y retorna payload"""
        return TokenManager.decode_token(token, expected_type="refresh")


# Instancia global
token_manager = TokenManager()
