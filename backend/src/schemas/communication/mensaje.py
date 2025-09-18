from pydantic import BaseModel, field_validator
from uuid import UUID
from datetime import datetime
from ...enums.communication.mensaje_enums import TipoMensaje


class MensajeBase(BaseModel):
    tipo: TipoMensaje
    contenido: str


class MensajeCreate(MensajeBase):
    chat_grupo_id: UUID
    emisor_id: UUID | None = None


class MensajeUpdate(BaseModel):
    tipo: TipoMensaje | None = None
    contenido: str | None = None

    @field_validator("contenido")
    def contenido_no_vacio(cls, v):
        if not v or not v.strip():
            raise ValueError("El contenido no puede estar vacío")
        return v


class MensajeInDBBase(MensajeBase):
    mensaje_id: UUID
    chat_grupo_id: UUID
    emisor_id: UUID | None = None
    fecha_hora: datetime

    class Config:
        from_attributes = True


class Mensaje(MensajeInDBBase):
    pass
