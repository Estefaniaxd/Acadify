from pydantic import BaseModel, field_validator
from uuid import UUID
from datetime import datetime
from ...enums.communication.mensaje_bots_enum import ContextoMensaje


class MensajeBotBase(BaseModel):
    contenido: str
    respuesta: str
    contexto: ContextoMensaje


class MensajeBotCreate(MensajeBotBase):
    usuario_id: UUID | None = None
    chat_grupo_id: UUID
    referencia_material_id: UUID | None = None


class MensajeBotUpdate(BaseModel):
    contenido: str | None = None
    respuesta: str | None = None
    contexto: ContextoMensaje | None = None

    @field_validator("contenido")
    def contenido_no_vacio(cls, value):
        if not value or not value.strip():
            raise ValueError("El contenido no puede estar vacío")
        return value


class MensajeBotInDBBase(MensajeBotBase):
    mensaje_bot_id: UUID
    usuario_id: UUID | None = None
    chat_grupo_id: UUID
    referencia_material_id: UUID | None = None
    fecha_hora: datetime

    class Config:
        from_attributes: True


class MensajeBot(MensajeBotInDBBase):
    pass
