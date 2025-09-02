from pydantic import BaseModel, EmailStr
from typing import Optional
from app.schemas.user import UserResponse

class Token(BaseModel):
    """Respuesta de token de acceso y refresh"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    """Datos extraídos del token (payload)"""
    user_id: Optional[str] = None

class LoginRequest(BaseModel):
    """Solicitud de login con email y contraseña"""
    email: EmailStr
    password: str

class LoginResponse(BaseModel):
    """Respuesta de login exitosa"""
    user: UserResponse
    token: Token

class RefreshTokenRequest(BaseModel):
    """Solicitud para refrescar el token de acceso"""
    refresh_token: str
