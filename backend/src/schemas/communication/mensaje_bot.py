from pydantic import BaseModel
from uuid import UUID
from datetime import datetime


class MensajeBotBase(BaseModel):
    usuario_id: UUID | None = None
    chat_grupo_id: UUID
    referencia_material_id: UUID | None = None
    contenido: str
    respuesta: str
    contexto: str
    fecha_hora: datetime
