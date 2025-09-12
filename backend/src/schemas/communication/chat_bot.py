from pydantic import BaseModel
from uuid import UUID
from datetime import date


class ChatBotBase(BaseModel):
    nombre: str
    descripcion: str
    foto_perfil_url: str
    activo: bool | None = None
    fecha_registro: date | None = None


class ChatBotCreate(ChatBotBase):
    """Schema para crear chat bot"""

    pass


class ChatBotUpdate(BaseModel):
    """Schema para actualizar chat bot"""

    nombre: str | None = None
    descripcion: str | None = None
    foto_perfil_url: str | None = None
    activo: bool | None = None


class ChatBotInDBBase(ChatBotBase):
    chat_bot_id: UUID

    class Config:
        from_attributes = True


class ChatBotRead(ChatBotInDBBase):
    """Schema de lectura de chat bot"""

    pass
