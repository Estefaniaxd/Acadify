from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import Optional

class FAQBotBase(BaseModel):
    pregunta: str
    respuesta: str
    categoria: str
    ultima_actualizacion: Optional[datetime] = None
    
class FAQBotCreate(FAQBotBase):
    pass

class FAQBotUpdate(BaseModel):
    pregunta: Optional[str] = None
    respuesta: Optional[str] = None
    categoria: Optional[str] = None
    ultima_actualizacion: Optional[datetime] = None
    
class FAQBotInDBBase(FAQBotBase):
    faq_id: UUID

    class Config:
        from_attributes = True
        
class FAQBot(FAQBotInDBBase):
    pass
    