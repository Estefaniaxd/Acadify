from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from ...enums.communication.chat_grupo_enums import EstadoChatGrupo


class ChatGrupoBase(BaseModel):
    descripcion: str | None = None
    foto_perfil: str | None = None
    permite_archivos: bool = True
    capacidad_almacenamiento: int = 52428800
    estado_chat: EstadoChatGrupo = EstadoChatGrupo.activo


class ChatGrupoCreate(ChatGrupoBase):
    grupo_id: UUID


class ChatGrupoUpdate(BaseModel):
    descripcion: str | None = None
    foto_perfil: str | None = None
    permite_archivos: bool | None = None
    capacidad_almacenamiento: int | None = None
    estado_chat: EstadoChatGrupo | None = None


class ChatGrupoInDBBase(ChatGrupoBase):
    chat_grupo_id: UUID
    fecha_creacion: datetime

    class Config:
        from_attributes = True


class ChatGrupo(ChatGrupoInDBBase):
    pass
