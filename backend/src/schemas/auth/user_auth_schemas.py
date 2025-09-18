from pydantic import BaseModel, EmailStr, Field, field_validator
from src.enums.users.usuario_enums import RolUsuario, TipoDocumentoUsuario


class UserRegisterRequest(BaseModel):
    """Schema para registro de nuevo usuario"""

    correo_institucional: EmailStr | None = Field(
        None, description="Email institucional"
    )
    username: str | None = Field(
        None, description="Nombre de usuario (solo administrador)"
    )
    nombres: str = Field(
        ..., min_length=2, max_length=100, description="Nombres del usuario"
    )
    apellidos: str = Field(
        ..., min_length=2, max_length=100, description="Apellidos del usuario"
    )
    tipo_documento: TipoDocumentoUsuario = Field(..., description="Tipo de documento")
    numero_documento: str = Field(
        ..., min_length=5, max_length=20, description="Número de documento"
    )
    rol: RolUsuario = Field(..., description="Rol del usuario")
    password: str = Field(..., min_length=10, description="Contraseña")
    telefono: str | None = Field(None, max_length=20, description="Teléfono")
    descripcion: str | None = Field(None, description="Descripción del usuario")

    @field_validator("password")
    def validate_password_strength(cls, v):
        """Validar fortaleza de la contraseña"""
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

    @field_validator("username", pre=True, always=True)
    def validate_admin_username(cls, v, values):
        """Validar que solo admin tenga username"""
        rol = values.get("rol")
        if rol == RolUsuario.administrador:
            if not v:
                raise ValueError("El administrador debe tener username")
        else:
            if v:
                raise ValueError("Solo el administrador puede tener username")
        return v

    @field_validator("correo_institucional", pre=True, always=True)
    def validate_non_admin_email(cls, v, values):
        """Validar que roles no admin tengan email institucional"""
        rol = values.get("rol")
        if rol != RolUsuario.administrador:
            if not v:
                raise ValueError(
                    "El correo institucional es obligatorio para roles distintos a administrador"
                )
        else:
            if v:
                raise ValueError("El administrador no debe tener correo institucional")
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "correo_institucional": "estudiante@universidad.edu.co",
                "username": None,
                "nombres": "María José",
                "apellidos": "García López",
                "tipo_documento": "cedula",
                "numero_documento": "12345678",
                "rol": "estudiante",
                "password": "MiContraseña123!",
                "telefono": "+57 300 123 4567",
                "descripcion": "Estudiante de Ingeniería de Sistemas",
            }
        }


class UserProfileUpdate(BaseModel):
    """Schema para actualización de perfil de usuario"""

    nombres: str | None = Field(None, min_length=2, max_length=100)
    apellidos: str | None = Field(None, min_length=2, max_length=100)
    telefono: str | None = Field(None, max_length=20)
    descripcion: str | None = None

    class Config:
        json_schema_extra = {
            "example": {
                "nombres": "María José",
                "apellidos": "García López",
                "telefono": "+57 300 123 4567",
                "descripcion": "Estudiante de Ingeniería de Sistemas - Semestre 8",
            }
        }
