from pydantic import BaseModel
from uuid import UUID
from datetime import datetime


class ArchivoChatBase(BaseModel):
    nombre_archivo: str
    url_archivo: str
    tipo_archivo: str | None = None


class ArchivoChatCreate(ArchivoChatBase):
    chat_grupo_id: UUID
    usuario_id: UUID | None = None


class ArchivoChatUpdate(BaseModel):
    nombre_archivo: str | None = None
    url_archivo: str | None = None
    tipo_archivo: str | None = None


class ArchivoChatInDBBase(ArchivoChatBase):
    archivo_id: UUID
    chat_grupo_id: UUID
    usuario_id: UUID | None = None
    fecha_envio: datetime

    class Config:
        from_attributes = True


class ArchivoChat(ArchivoChatInDBBase):
    pass
