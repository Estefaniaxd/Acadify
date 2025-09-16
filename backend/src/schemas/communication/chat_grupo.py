from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from src.enums.communication.chat_grupo_enums import EstadoChatGrupo


class ChatGrupoBase(BaseModel):
    grupo_id: UUID
    fecha_creacion: datetime
    descripcion: str | None = None
    foto_perfil: str | None = None
    permite_archivos: bool
    capacidad_almacenamiento: int
    estado_chat: EstadoChatGrupo | None = None


class ChatGrupoCreate(ChatGrupoBase):
    pass


class ChatGrupoUpdate(BaseModel):
    descripcion: str | None = None
    foto_perfil: str | None = None
    permite_archivos: bool | None = None
    capacidad_almacenamiento: int | None = None
    estado_chat: EstadoChatGrupo = None


class ChatGrupoInDBBase(ChatGrupoBase):
    chat_grupo_id: UUID
    fecha_creacion: datetime

    class Config:
        from_attributes = True


class ChatGrupoRead(ChatGrupoInDBBase):
    pass
