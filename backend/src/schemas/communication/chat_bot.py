from pydantic import BaseModel
from uuid import UUID
from datetime import date
from typing import Optional

class ChatBotBase(BaseModel):
    nombre: str
    descripcion: str
    foto_perfil_url: str
    activo: Optional[bool] = None
    fecha_registro: Optional[date] = None    
    
class ChatBotCreate(ChatBotBase):
    """Schema para crear chat bot"""
    pass

class ChatBotUpdate(BaseModel):
    """Schema para actualizar chat bot"""
    nombre: Optional[str] = None
    descripcion: Optional[str] = None
    foto_perfil_url: Optional[str] = None
    activo: Optional[bool] = None
    
class ChatBotInDBBase(ChatBotBase):
    chat_bot_id: UUID

    class Config:
        from_attributes = True
        
class ChatBotRead(ChatBotInDBBase):
    """Schema de lectura de chat bot"""
    pass