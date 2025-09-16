from pydantic import BaseModel
from uuid import UUID
from datetime import datetime


class FAQBotBase(BaseModel):
    pregunta: str
    respuesta: str
    categoria: str
    ultima_actualizacion: datetime | None = None


class FAQBotCreate(FAQBotBase):
    pass


class FAQBotUpdate(BaseModel):
    pregunta: str | None = None
    respuesta: str | None = None
    categoria: str | None = None
    ultima_actualizacion: datetime | None = None


class FAQBotInDBBase(FAQBotBase):
    faq_id: UUID

    class Config:
        from_attributes = True


class FAQBotRead(FAQBotInDBBase):
    pass
