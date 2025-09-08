from pydantic import BaseModel, EmailStr, field_validator
from src.enums.users.usuario_enums import RolUsuario


class UsuarioBase(BaseModel):
    correo_institucional: EmailStr | None = None
    username: str | None = None
    rol: RolUsuario


class UsuarioCreate(UsuarioBase):
    password: str


class UsuarioRead(UsuarioBase):
    usuario_id: str

    class Config:
        from_attributes = True


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
