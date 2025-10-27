from uuid import UUID
from pydantic import BaseModel


class AdministradorSistemaBase(BaseModel):
    pass

class AdministradorSistemaCreate(AdministradorSistemaBase):
    pass


class AdministradorSistemaUpdate(BaseModel):
    pass


class AdministradorSistemaInDBBase(AdministradorSistemaBase):
    administrador_id: UUID

    class Config:
        from_attributes = True


class AdministradorSistema(AdministradorSistemaInDBBase):
    pass
