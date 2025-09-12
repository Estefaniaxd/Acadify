from pydantic import BaseModel
from uuid import UUID
from datetime import datetime


class ArchivoChatBase(BaseModel):
    chat_grupo_id: UUID
    usuario_id: UUID | None = None
    nombre_archivo: str
    url_archivo: str
    tipo_archivo: str | None = None


class ArchivoChatCreate(ArchivoChatBase):
    """Schema para crear archivo"""

    pass


class ArchivoChatUpdate(BaseModel):
    """Schema para actualizar archivo"""

    nombre_archivo: str | None = None
    url_archivo: str | None = None
    tipo_archivo: str | None = None


class ArchivoChatInDBBase(ArchivoChatBase):
    archivo_id: UUID
    fecha_envio: datetime

    class Config:
        from_attributes = True


class ArchivoChatRead(ArchivoChatInDBBase):
    """Schema de lectura de archivo"""

    pass
