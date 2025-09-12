from uuid import UUID
from pydantic import BaseModel, Field


class TemaBase(BaseModel):
    nombre: str = Field(max_length=100, description="Nombre del tema")
    emoji: str = Field(max_length=8, description="Emoji representativo del tema")


class TemaCreate(TemaBase):
    pass


class TemaUpdate(BaseModel):
    nombre: str | None = Field(None, max_length=100)
    emoji: str | None = Field(None, max_length=8)


class TemaResponse(TemaBase):
    tema_id: UUID

    class Config:
        from_attributes = True


class TemaPredefinidoResponse(TemaResponse):
    es_predefinido: bool = True


class TemaPersonalizadoBase(BaseModel):
    pass


class TemaPersonalizadoCreate(TemaPersonalizadoBase):
    usuario_id: UUID
    tema_id: UUID


class TemaPersonalizadoResponse(TemaPersonalizadoBase):
    tema_id: UUID
    usuario_id: UUID
    tema: TemaResponse

    class Config:
        from_attributes = True


class AsignarTemaPersonalizadoRequest(BaseModel):
    usuario_id: UUID
    tema_id: UUID


class TemasUsuarioResponse(BaseModel):
    usuario_id: UUID
    temas_predefinidos: list[TemaResponse]
    temas_personalizados: list[TemaResponse]
    total_temas: int
