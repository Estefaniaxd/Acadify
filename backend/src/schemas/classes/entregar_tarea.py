from pydantic import BaseModel
from uuid import UUID
from datetime import datetime

class EntregarTareaBase(BaseModel):
    tarea_id: UUID
    estudiante_id: UUID
    archivo: str | None = None

class EntregarTareaCreate(EntregarTareaBase):
    pass

class EntregarTareaUpdate(BaseModel):
    archivo: str | None = None

class EntregarTareaInDBBase(EntregarTareaBase):
    entrega_id: UUID
    fecha_entrega: datetime

    class Config:
        from_attributes = True

class EntregarTarea(EntregarTareaInDBBase):
    pass
