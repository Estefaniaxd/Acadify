from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from src.enums.communication.mensaje_enums import TipoMensaje


class MensajeBase(BaseModel):
    chat_grupo_id: UUID
    emisor_id: UUID | None = None
    fecha_hora: datetime | None = None
    tipo: TipoMensaje
    contenido: str


class MensajeCreate(MensajeBase):
    pass


class MensajeUpdate(BaseModel):
    fecha_hora: datetime | None = None
    contenido: str | None = None


class MensajeInDBBase(MensajeBase):
    mensaje_id: UUID

    class Config:
        from_attributes = True
