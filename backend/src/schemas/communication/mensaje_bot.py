from pydantic import BaseModel, field_validator
from uuid import UUID
from datetime import datetime


class MensajeBotBase(BaseModel):
    usuario_id: UUID | None = None
    chat_grupo_id: UUID
    referencia_material_id: UUID | None = None
    contenido: str
    respuesta: str
    contexto: str
    fecha_hora: datetime


class MensajeBotCreate(MensajeBotBase):
    pass


class MensajeBotUpdate(BaseModel):
    referencia_material_id: UUID | None = None
    contenido: str | None = None
    respuesta: str | None = None
    contexto: str | None = None
    fecha_hora: datetime | None = None

    @field_validator("contenido")
    def contenido_no_vacio(cls, v):
        if not v or not v.strip():
            raise ValueError("El contenido no puede estar vacío")
        return v


class MensajeBotInDBBase(MensajeBotBase):
    mensaje_bot_id: UUID

    class Config:
        from_attributes: True


class MensajeBotRead(MensajeBotInDBBase):
    pass
