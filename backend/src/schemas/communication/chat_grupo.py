from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import Optional
from src.enums.communication.chat_grupo_enums import EstadoChatGrupo

class ChatGrupoBase(BaseModel):
    grupo_id: UUID
    fecha_creacion: datetime
    descripcion: Optional[str] = None
    foto_perfil: Optional[str] = None
    permite_archivos: bool
    capacidad_almacenamiento: int
    estado_chat: EstadoChatGrupo
    
class ChatGrupoCreate(ChatGrupoBase):
    pass

class ChatGrupoUpdate(BaseModel):
    descripcion: Optional[str] = None
    foto_perfil: Optional[str] = None
    permite_archivos: Optional[bool] = None
    capacidad_almacenamiento: Optional[int] = None
    estado_chat: EstadoChatGrupo = None

class ChatGrupoInDBBase(ChatGrupoBase):
    archivo_id: UUID
    fecha_envio: datetime

    class Config:
        from_attributes = True
        
class ChatGrupo(ChatGrupoInDBBase):
    pass