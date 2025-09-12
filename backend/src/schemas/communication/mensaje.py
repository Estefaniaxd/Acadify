from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from src.enums.communication.mensaje_enums import TipoMensaje
from typing import Optional

class MensajeBase(BaseModel):
    chat_grupo_id: UUID
    emisor_id: Optional[UUID] = None
    fecha_hora: Optional[datetime] = None
    tipo: TipoMensaje
    contenido: str
    
class MensajeCreate(MensajeBase):
    pass

class MensajeUpdate(BaseModel):
    fecha_hora: Optional[datetime] = None
    contenido: Optional[str] = None
    
class MensajeInDBBase(MensajeBase):
    mensaje_id: UUID
    
    class Config:
        from_attributes = True
    