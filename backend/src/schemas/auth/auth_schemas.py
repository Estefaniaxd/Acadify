
from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional
import uuid
from datetime import datetime

# Constante para ejemplo de correo institucional
EXAMPLE_CORREO = "usuario@universidad.edu.co"


class LoginRequest(BaseModel):
    """Schema para solicitud de login"""
    correo_institucional: EmailStr = Field(..., description="Email institucional del usuario")
    password: str = Field(..., min_length=8, description="Contraseña del usuario")
    otp_code: Optional[str] = Field(None, description="Código TOTP para 2FA (si está habilitado)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "correo_institucional": EXAMPLE_CORREO,
                "password": "MiContraseña123!",
                "otp_code": "123456"
            }
        }


class TokenResponse(BaseModel):
    """Schema para respuesta de tokens"""
    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(default="Bearer", description="Tipo de token")
    expires_in: int = Field(..., description="Tiempo de expiración en segundos")
    
    class Config:
        json_schema_extra = {
            "example": {
                "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
                "token_type": "Bearer",
                "expires_in": 600
            }
        }


class RefreshResponse(BaseModel):
    """Schema para respuesta de refresh token"""
    access_token: str = Field(..., description="Nuevo JWT access token")
    token_type: str = Field(default="Bearer", description="Tipo de token")
    expires_in: int = Field(..., description="Tiempo de expiración en segundos")


class PasswordResetRequest(BaseModel):
    """Schema para solicitar reset de contraseña"""
    correo_institucional: EmailStr = Field(..., description="Email del usuario")
    
    class Config:
        json_schema_extra = {
            "example": {
                "correo_institucional": EXAMPLE_CORREO
            }
        }


class PasswordResetConfirm(BaseModel):
    """Schema para confirmar reset de contraseña"""
    token: str = Field(..., description="Token de reset recibido por email")
    new_password: str = Field(..., min_length=10, description="Nueva contraseña")
    
    @validator('new_password')
    def validate_password_strength(cls, v):
        """Validar fortaleza de la contraseña"""
        if len(v) < 10:
            raise ValueError('La contraseña debe tener al menos 10 caracteres')
        
        has_upper = any(c.isupper() for c in v)
        has_lower = any(c.islower() for c in v)
        has_digit = any(c.isdigit() for c in v)
        has_special = any(c in "!@#$%^&*(),.?\":{}|<>" for c in v)
        
        if not all([has_upper, has_lower, has_digit, has_special]):
            raise ValueError(
                'La contraseña debe contener al menos: '
                '1 mayúscula, 1 minúscula, 1 número y 1 carácter especial'
            )
        
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "token": "abc123def456",
                "new_password": "NuevaContraseña123!"
            }
        }


class TwoFASetupResponse(BaseModel):
    """Schema para respuesta de configuración 2FA"""
    secret: str = Field(..., description="Secret para configurar en la app 2FA")
    qr_code_url: str = Field(..., description="URL para generar código QR")
    backup_codes: list[str] = Field(..., description="Códigos de respaldo")
    
    class Config:
        json_schema_extra = {
            "example": {
                "secret": "JBSWY3DPEHPK3PXP",
                "qr_code_url": "otpauth://totp/Acadify:usuario@universidad.edu.co?secret=JBSWY3DPEHPK3PXP&issuer=Acadify",
                "backup_codes": ["12345678", "87654321", "11223344"]
            }
        }


class TwoFAVerifyRequest(BaseModel):
    """Schema para verificar código 2FA"""
    otp_code: str = Field(..., min_length=6, max_length=6, description="Código TOTP de 6 dígitos")
    
    @validator('otp_code')
    def validate_otp_format(cls, v):
        if not v.isdigit():
            raise ValueError('El código debe contener solo números')
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "otp_code": "123456"
            }
        }


class OAuthStateResponse(BaseModel):
    """Schema para respuesta de estado OAuth"""
    authorization_url: str = Field(..., description="URL para autorización OAuth")
    state: str = Field(..., description="Estado para validación CSRF")
    
    class Config:
        json_schema_extra = {
            "example": {
                "authorization_url": "https://accounts.google.com/oauth/authorize?...",
                "state": "abc123def456"
            }
        }


class PasswordChangeRequest(BaseModel):
    """Schema para cambio de contraseña (usuario logueado)"""
    current_password: str = Field(..., description="Contraseña actual")
    new_password: str = Field(..., min_length=10, description="Nueva contraseña")
    
    @validator('new_password')
    def validate_password_strength(cls, v):
        """Reutilizar validación de PasswordResetConfirm"""
        return PasswordResetConfirm.validate_password_strength(v)


class UserCurrentResponse(BaseModel):
    """Schema para respuesta de usuario actual (/auth/me)"""
    usuario_id: uuid.UUID
    correo_institucional: Optional[EmailStr] = None
    username: Optional[str] = None
    nombres: str
    apellidos: str
    rol: str
    email_verified: bool
    twofa_enabled: bool
    fecha_creacion: datetime
    ultimo_acceso: Optional[datetime] = None
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "usuario_id": "123e4567-e89b-12d3-a456-426614174000",
                "correo_institucional": EXAMPLE_CORREO,
                "username": None,
                "nombres": "Juan Carlos",
                "apellidos": "Pérez González",
                "rol": "estudiante",
                "email_verified": True,
                "twofa_enabled": False,
                "fecha_creacion": "2024-01-15T10:30:00Z",
                "ultimo_acceso": "2024-01-20T14:45:00Z"
            }
        }


class LoginAttemptResponse(BaseModel):
    """Schema para respuesta de intento de login bloqueado"""
    locked: bool = Field(..., description="Si la cuenta está bloqueada")
    attempts_remaining: int = Field(..., description="Intentos restantes antes del bloqueo")
    lockout_ends_at: Optional[datetime] = Field(None, description="Cuando termina el bloqueo")
    message: str = Field(..., description="Mensaje descriptivo")
    
    class Config:
        json_schema_extra = {
            "example": {
                "locked": True,
                "attempts_remaining": 0,
                "lockout_ends_at": "2024-01-20T15:00:00Z",
                "message": "Cuenta bloqueada por múltiples intentos fallidos. Inténtelo nuevamente en 14 minutos."
            }
        }
