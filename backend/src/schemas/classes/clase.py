from pydantic import BaseModel
from uuid import UUID, uuid4
from datetime import datetime, timedelta


class ClaseBase(BaseModel):
    grupo_curso_id: UUID
    plataforma_id: UUID | None = None
    titulo: str
    descripcion: str | None = None
    hora_inicio: datetime
    duracion: timedelta
    link_videollamada: str
    
clase = ClaseBase(
    grupo_curso_id=uuid4(),
    plataforma_id=uuid4(),
    titulo="Clase 1",
    descripcion="Descripción de la clase",
    hora_inicio=datetime(2025, 2, 2, 14, 24, 23),
    duracion=timedelta(minutes=60),
    link_videollamada="https://meet.google.com/abc-def-ghi"
)

clase_json_str = clase.model_dump_json()
print(clase_json_str)


class ClaseCreate(ClaseBase):
    pass


class ClaseUpdate(BaseModel):
    titulo: str | None = None
    descripcion: str | None = None
    hora_inicio: datetime | None = None
    duracion: timedelta | None = None
    link_videollamada: str | None = None
    plataforma_id: UUID | None = None


class ClaseInDBBase(ClaseBase):
    clase_id: UUID

    class Config:
        from_attributes = True


class Clase(ClaseInDBBase):
    pass
