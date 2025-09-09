from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from src.enums.communication.mensaje_enums import TipoMensaje
from typing import Optional

class MensajeBase(BaseModel):
    chat_grupo_id: UUID
    emisor_id: Optional[UUID] = None
    fecha_hora: datetime
    tipo: TipoMensaje
    contenido: str
    