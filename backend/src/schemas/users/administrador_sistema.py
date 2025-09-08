import uuid
from pydantic import BaseModel


class AdministradorSistemaBase(BaseModel):
    administrador_id: uuid.UUID


class AdministradorSistemaCreate(AdministradorSistemaBase):
    pass


class AdministradorSistemaRead(AdministradorSistemaBase):
    class Config:
        from_attributes = True
