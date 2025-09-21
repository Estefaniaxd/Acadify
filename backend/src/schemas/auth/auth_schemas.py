
from pydantic import BaseModel, EmailStr, Field, field_validator, ConfigDict
from typing import Optional, Literal
from datetime import datetime
from uuid import UUID, uuid4

# ===============================
# Email Verification Schemas
# ===============================
class EmailVerificationRequest(BaseModel):
    usuario_id: str = Field(..., description="ID del usuario a verificar")
    verification_code: str = Field(..., description="Código de verificación enviado por email")
    
    @field_validator('usuario_id')
    @classmethod
    def validate_uuid(cls, v):
        try:
            UUID(str(v))
            return str(v)
        except ValueError:
            raise ValueError('usuario_id debe ser un UUID válido')

class EmailVerificationResponse(BaseModel):
    message: str = Field(default="Correo verificado exitosamente", description="Mensaje de confirmación")

# Constante global para ejemplos
EXAMPLE_EMAIL = "usuario@universidad.edu.co"
# src/schemas/auth/auth_schemas.py

# ===============================
# Authentication Schemas
# ===============================

class LoginRequest(BaseModel):
    """Schema para solicitud de login unificado"""
    identifier: str = Field(..., description="Email institucional o username")
    password: str = Field(..., min_length=1, description="Contraseña del usuario")
    otp_code: Optional[str] = Field(None, min_length=6, max_length=6, description="Código OTP para 2FA (solo si se requiere)")
    
    @field_validator('otp_code')
    @classmethod
    def validate_otp_format(cls, v):
        if v and not v.isdigit():
            raise ValueError('El código OTP debe contener solo números')
        return v
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "identifier": "estebanAdmin",
                "password": "Juanito243019@"
            }
        }
    )


class TokenResponse(BaseModel):
    """Schema para respuesta de tokens JWT"""
    access_token: str = Field(..., description="JWT access token")
    refresh_token: str = Field(..., description="JWT refresh token")
    token_type: str = Field(default="Bearer", description="Tipo de token")
    expires_in: int = Field(..., description="Tiempo de expiración access token en segundos")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
                "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
                "token_type": "Bearer",
                "expires_in": 900
            }
        }
    )


class RefreshTokenRequest(BaseModel):
    """Schema para solicitud de refresh token"""
    refresh_token: str = Field(..., description="Refresh token JWT")


class RefreshResponse(BaseModel):
    """Schema para respuesta de refresh token"""

    access_token: str = Field(..., description="Nuevo JWT access token")
    token_type: str = Field(default="Bearer", description="Tipo de token")
    expires_in: int = Field(..., description="Tiempo de expiración en segundos")


class LogoutResponse(BaseModel):
    """Schema para respuesta de logout"""
    message: str = Field(default="Logout exitoso", description="Mensaje de confirmación")


# ===============================
# Password Reset Schemas
# ===============================

class PasswordResetRequest(BaseModel):
    """Schema para solicitar reset de contraseña"""

    correo_institucional: EmailStr = Field(..., description="Email del usuario")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "correo_institucional": EXAMPLE_EMAIL
            }
        }
    )


class PasswordResetResponse(BaseModel):
    """Schema para respuesta de solicitud reset"""
    message: str = Field(
        default="Si el email existe, se envió un código de recuperación",
        description="Mensaje genérico por seguridad"
    )


class PasswordResetConfirm(BaseModel):
    """Schema para confirmar reset de contraseña"""
    correo_institucional: EmailStr = Field(..., description="Email del usuario")
    reset_code: str = Field(..., min_length=6, max_length=8, description="Código de reset recibido por email")
    new_password: str = Field(..., min_length=10, description="Nueva contraseña")
    
    @field_validator('new_password')
    @classmethod
    def validate_password_strength(cls, v):
        if len(v) < 10:
            raise ValueError("La contraseña debe tener al menos 10 caracteres")

        has_upper = any(c.isupper() for c in v)
        has_lower = any(c.islower() for c in v)
        has_digit = any(c.isdigit() for c in v)
        has_special = any(c in '!@#$%^&*(),.?":{}|<>' for c in v)

        if not all([has_upper, has_lower, has_digit, has_special]):
            raise ValueError(
                "La contraseña debe contener al menos: "
                "1 mayúscula, 1 minúscula, 1 número y 1 carácter especial"
            )

        return v
    
    @field_validator('reset_code')
    @classmethod
    def validate_reset_code_format(cls, v):
        if not v.isalnum():
            raise ValueError('El código debe contener solo números y letras')
        return v
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "correo_institucional": EXAMPLE_EMAIL,
                "reset_code": "ABC123",
                "new_password": "NuevaContraseña123!"
            }
        }
    )


class PasswordChangeRequest(BaseModel):
    """Schema para cambio de contraseña (usuario logueado)"""

    current_password: str = Field(..., description="Contraseña actual")
    new_password: str = Field(..., min_length=10, description="Nueva contraseña")
    
    @field_validator('new_password')
    @classmethod
    def validate_password_strength(cls, v):
        # Reutilizar la misma validación
        return PasswordResetConfirm.validate_password_strength(v)


# ===============================
# Two-Factor Authentication Schemas
# ===============================

class TwoFASetupRequest(BaseModel):
    """Schema para solicitar configuración 2FA"""
    method: Literal["email", "totp"] = Field(..., description="Método de 2FA")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "method": "email"
            }
        }
    )


class TwoFASetupResponse(BaseModel):
    """Schema para respuesta de configuración 2FA"""
    method: str = Field(..., description="Método configurado")
    message: str = Field(..., description="Instrucciones para el usuario")
    # Solo para TOTP
    secret: Optional[str] = Field(None, description="Secret para configurar en app 2FA")
    qr_code_url: Optional[str] = Field(None, description="URL para generar código QR")
    backup_codes: Optional[list[str]] = Field(None, description="Códigos de respaldo")
    
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "method": "email",
                    "message": "Se envió un código de verificación al correo para activar 2FA"
                },
                {
                    "method": "totp",
                    "message": "Escanea el código QR con tu app de autenticación y confirma con un código",
                    "secret": "JBSWY3DPEHPK3PXP",
                    "qr_code_url": f"otpauth://totp/Acadify:{EXAMPLE_EMAIL}?secret=JBSWY3DPEHPK3PXP&issuer=Acadify",
                    "backup_codes": ["12345678", "87654321", "11223344"]
                }
            ]
        }
    )


class TwoFAVerifyRequest(BaseModel):
    """Schema para verificar código 2FA en setup"""
    verification_code: str = Field(..., min_length=6, max_length=6, description="Código de verificación")
    
    @field_validator('verification_code')
    @classmethod
    def validate_code_format(cls, v):
        if not v.isdigit():
            raise ValueError('El código debe contener solo números')
        return v
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "verification_code": "123456"
            }
        }
    )


class TwoFAVerifyResponse(BaseModel):
    """Schema para respuesta de verificación 2FA"""
    success: bool = Field(..., description="Si la verificación fue exitosa")
    message: str = Field(..., description="Mensaje de resultado")
    twofa_enabled: bool = Field(..., description="Estado de 2FA tras verificación")


class TwoFADisableRequest(BaseModel):
    """Schema para desactivar 2FA"""
    current_password: str = Field(..., description="Contraseña actual para confirmación")


class TwoFAStatusResponse(BaseModel):
    """Schema para estado de 2FA del usuario"""
    twofa_enabled: bool = Field(..., description="Si 2FA está activado")
    twofa_method: Optional[str] = Field(None, description="Método de 2FA configurado")


# ===============================
# User Profile Schemas
# ===============================

class UserCurrentResponse(BaseModel):
    """Schema para respuesta de usuario actual (/auth/me)"""

    usuario_id: UUID
    correo_institucional: EmailStr | None = None
    username: str | None = None
    nombres: str
    apellidos: str
    tipo_documento: str
    numero_documento: str
    rol: str
    estado_cuenta: str
    email_verified: bool
    twofa_enabled: bool
    twofa_method: Optional[str] = None
    telefono: Optional[str] = None
    descripcion: Optional[str] = None
    fecha_creacion: datetime
    ultimo_acceso: Optional[datetime] = None
    
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "usuario_id": "123e4567-e89b-12d3-a456-426614174000",
                "correo_institucional": EXAMPLE_EMAIL,
                "username": None,
                "nombres": "Juan Carlos",
                "apellidos": "Pérez González",
                "tipo_documento": "cc",
                "numero_documento": "12345678",
                "rol": "estudiante",
                "estado_cuenta": "activo",
                "email_verified": True,
                "twofa_enabled": False,
                "twofa_method": None,
                "telefono": "+57 300 123 4567",
                "descripcion": "Estudiante de Ingeniería",
                "fecha_creacion": "2024-01-15T10:30:00Z",
                "ultimo_acceso": "2024-01-20T14:45:00Z",
            }
        }
    )


class UserProfileUpdate(BaseModel):
    """Schema para actualización de perfil de usuario"""
    nombres: Optional[str] = Field(None, min_length=2, max_length=100)
    apellidos: Optional[str] = Field(None, min_length=2, max_length=100)
    telefono: Optional[str] = Field(None, max_length=20)
    descripcion: Optional[str] = None
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "nombres": "María José",
                "apellidos": "García López",
                "telefono": "+57 300 123 4567",
                "descripcion": "Estudiante de Ingeniería de Sistemas - Semestre 8"
            }
        }
    )


# ===============================
# Login Response Schemas (intermedios)
# ===============================

class LoginStepResponse(BaseModel):
    """Schema para respuestas intermedias de login (2FA requerido)"""
    status: Literal["otp_required", "success"] = Field(..., description="Estado del login")
    message: str = Field(..., description="Mensaje descriptivo")
    requires_otp: bool = Field(default=False, description="Si requiere código OTP")
    otp_method: Optional[str] = Field(None, description="Método de OTP utilizado")


class LoginAttemptResponse(BaseModel):
    """Schema para respuesta de intento de login bloqueado"""

    locked: bool = Field(..., description="Si la cuenta está bloqueada")
    attempts_remaining: int = Field(..., description="Intentos restantes antes del bloqueo")
    lockout_ends_at: Optional[datetime] = Field(None, description="Cuándo termina el bloqueo")
    message: str = Field(..., description="Mensaje descriptivo")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "locked": True,
                "attempts_remaining": 0,
                "lockout_ends_at": "2024-01-20T15:00:00Z",
                "message": "Cuenta bloqueada por múltiples intentos fallidos. Inténtelo nuevamente en 14 minutos.",
            }
        }
    )


# ===============================
# Generic Response Schemas
# ===============================

class MessageResponse(BaseModel):
    """Schema genérico para respuestas con mensaje"""
    message: str = Field(..., description="Mensaje de respuesta")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "message": "Operación completada exitosamente"
            }
        }
    )

# ===============================
# Account Deletion Schemas
# ===============================

class AccountDeletionRequest(BaseModel):
    """Schema para solicitar eliminación de cuenta (paso 1 - solo contraseña)"""
    password: str = Field(..., min_length=1, description="Contraseña actual para confirmar identidad")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "password": "MiContraseña123!"
            }
        }
    )

class AccountDeletionFinalRequest(BaseModel):
    """Schema para eliminación final de cuenta con confirmación completa"""
    current_password: str = Field(..., min_length=1, description="Contraseña actual para confirmar eliminación")
    confirmation_text: str = Field(..., description="Texto de confirmación: 'ELIMINAR MI CUENTA'")
    reason: Optional[str] = Field(None, max_length=500, description="Motivo opcional para eliminar la cuenta")
    
    @field_validator('confirmation_text')
    @classmethod
    def validate_confirmation(cls, v):
        if v.upper().strip() != "ELIMINAR MI CUENTA":
            raise ValueError('Debe escribir exactamente "ELIMINAR MI CUENTA" para confirmar')
        return v
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "current_password": "MiContraseña123!",
                "confirmation_text": "ELIMINAR MI CUENTA",
                "reason": "Ya no necesito la plataforma"
            }
        }
    )

class AccountDeletionResponse(BaseModel):
    """Schema para respuesta de eliminación de cuenta"""
    message: str = Field(..., description="Mensaje de confirmación")
    grace_period_days: int = Field(..., description="Días del período de gracia")
    deletion_date: datetime = Field(..., description="Fecha límite para eliminación permanente")
    restoration_token: str = Field(..., description="Token para restaurar la cuenta")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "message": "Cuenta marcada para eliminación. Tienes 30 días para restaurarla.",
                "grace_period_days": 30,
                "deletion_date": "2025-10-17T14:30:00Z",
                "restoration_token": "rest_abc123def456"
            }
        }
    )

class AccountRestorationRequest(BaseModel):
    """Schema para restaurar cuenta eliminada"""
    restoration_token: str = Field(..., description="Token de restauración recibido por email")
    current_password: str = Field(..., min_length=1, description="Contraseña actual para confirmar restauración")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "restoration_token": "rest_abc123def456",
                "current_password": "MiContraseña123!"
            }
        }
    )


class ErrorResponse(BaseModel):
    """Schema para respuestas de error"""
    detail: str = Field(..., description="Descripción del error")
    error_code: Optional[str] = Field(None, description="Código de error interno")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "detail": "Credenciales incorrectas",
                "error_code": "AUTH_INVALID_CREDENTIALS"
            }
        }
    )