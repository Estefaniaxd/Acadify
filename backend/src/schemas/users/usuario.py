from pydantic import BaseModel, EmailStr, field_validator
from uuid import UUID
from ...enums.users.usuario_enums import (
    TipoDocumentoUsuario,
    RolUsuario,
    EstadoCuentaUsuario,
)
from datetime import datetime


class UsuarioBase(BaseModel):
    correo_institucional: EmailStr | None = None
    username: str | None = None
    nombres: str
    apellidos: str
    tipo_documento: TipoDocumentoUsuario
    numero_documento: str
    rol: RolUsuario
    password_hash: str
    estado_cuenta: EstadoCuentaUsuario = EstadoCuentaUsuario.activo
    ultimo_acceso: datetime
    perfil_url: str | None = None
    portada_url: str | None = None
    telefono: str | None = None
    descripcion: str | None = None



# Solo los campos que el usuario debe enviar al registrarse
class UsuarioCreate(BaseModel):
    correo_institucional: EmailStr
    username: str
    nombres: str
    apellidos: str
    tipo_documento: str
    numero_documento: str
    rol: RolUsuario
    telefono: str | None = None
    descripcion: str | None = None
    password: str


class UsuarioUpdate(BaseModel):
    correo_institucional: EmailStr | None = None
    username: str | None = None
    nombres: str | None = None
    apellidos: str | None = None
    tipo_documento: TipoDocumentoUsuario | None = None
    numero_documento: str | None = None
    rol: RolUsuario | None = None
    password_hash: str | None = None
    estado_cuenta: EstadoCuentaUsuario | None = None
    ultimo_acceso: datetime | None = None
    perfil_url: str | None = None
    portada_url: str | None = None
    telefono: str | None = None
    descripcion: str | None = None
    # Se eliminan las validaciones que restringían username/correo por rol.
    # Ahora la política es que los usuarios pueden tener ambos campos y las
    # reglas de negocio sobre uso para login deben aplicarse en el servicio.


class UsuarioInDBBase(UsuarioBase):
    usuario_id: UUID

    class Config:
        from_attributes = True


class Usuario(UsuarioInDBBase):
    pass
