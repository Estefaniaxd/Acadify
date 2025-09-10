# src/schemas/users/usuario.py


from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional
from uuid import UUID
from src.enums.users.usuario_enums import RolUsuario

# -----------------------------
# Base para los usuarios
# -----------------------------
class UsuarioBase(BaseModel):
    correo_institucional: Optional[EmailStr] = None
    username: Optional[str] = None
    rol: RolUsuario

# -----------------------------
# Esquema para creación de usuario
# -----------------------------
class UsuarioCreate(UsuarioBase):
    nombres: str
    apellidos: str
    tipo_documento: str
    numero_documento: str
    telefono: str | None = None
    descripcion: str | None = None
    password: str

# -----------------------------
# Esquema para lectura de usuario
# -----------------------------
class UsuarioRead(UsuarioBase):
    usuario_id: UUID

    model_config = {
        "from_attributes": True  # Permite leer atributos de SQLAlchemy
    }

# -----------------------------
# Esquema para actualización de usuario
# -----------------------------
class UsuarioUpdate(BaseModel):
    correo_institucional: Optional[EmailStr] = None
    username: Optional[str] = None
    nombres: Optional[str] = None
    apellidos: Optional[str] = None
    telefono: Optional[str] = None
    descripcion: Optional[str] = None
    rol: Optional[RolUsuario] = None

    @field_validator("username", mode="before")
    def validar_admin(cls, v, info):
        rol = info.data.get("rol")
        if rol == RolUsuario.administrador:
            if not v:
                raise ValueError("El administrador debe tener username")
        else:
            if v:
                raise ValueError("Solo el administrador puede tener username")
        return v

    @field_validator("correo_institucional", mode="before")
    def validar_no_admin(cls, v, info):
        rol = info.data.get("rol")
        if rol != RolUsuario.administrador:
            if not v:
                raise ValueError(
                    "El correo institucional es obligatorio para roles distintos a administrador"
                )
        else:
            if v:
                raise ValueError("El administrador no debe tener correo institucional")
        return v
