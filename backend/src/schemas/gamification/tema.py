import uuid
from typing import Optional
from pydantic import BaseModel, Field


class TemaBase(BaseModel):
    nombre: str = Field(max_length=100, description="Nombre del tema")
    emoji: str = Field(max_length=8, description="Emoji representativo del tema")


class TemaCreate(TemaBase):
    pass


class TemaUpdate(BaseModel):
    nombre: Optional[str] = Field(None, max_length=100)
    emoji: Optional[str] = Field(None, max_length=8)


class TemaResponse(TemaBase):
    tema_id: uuid.UUID
    
    class Config:
        from_attributes = True


class TemaPredefinidoResponse(TemaResponse):
    es_predefinido: bool = True


class TemaPersonalizadoBase(BaseModel):
    pass


class TemaPersonalizadoCreate(TemaPersonalizadoBase):
    usuario_id: uuid.UUID
    tema_id: uuid.UUID


class TemaPersonalizadoResponse(TemaPersonalizadoBase):
    tema_id: uuid.UUID
    usuario_id: uuid.UUID
    tema: TemaResponse
    
    class Config:
        from_attributes = True


class AsignarTemaPersonalizadoRequest(BaseModel):
    usuario_id: uuid.UUID
    tema_id: uuid.UUID


class TemasUsuarioResponse(BaseModel):
    usuario_id: uuid.UUID
    temas_predefinidos: list[TemaResponse]
    temas_personalizados: list[TemaResponse]
    total_temas: int