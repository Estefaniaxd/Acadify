from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import Optional


class ArchivoChatBase(BaseModel):
    chat_grupo_id: UUID
    usuario_id: Optional[UUID] = None
    nombre_archivo: str
    url_archivo: str
    tipo_archivo: Optional[str] = None


class ArchivoChatCreate(ArchivoChatBase):
    """Schema para crear archivo"""
    pass


class ArchivoChatUpdate(BaseModel):
    """Schema para actualizar archivo"""
    nombre_archivo: Optional[str] = None
    url_archivo: Optional[str] = None
    tipo_archivo: Optional[str] = None


class ArchivoChatInDBBase(ArchivoChatBase):
    archivo_id: UUID
    fecha_envio: datetime

    class Config:
        from_attributes = True


class ArchivoChatRead(ArchivoChatInDBBase):
    """Schema de lectura de archivo"""
    pass
