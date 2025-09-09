from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import Optional


class MensajeBotBase(BaseModel):
    usuario_id: Optional[UUID] = None
    chat_grupo_id: UUID
    referencia_material_id: Optional[UUID] = None
    contenido: str
    respuesta: str
    contexto: str 
    fecha_hora: datetime