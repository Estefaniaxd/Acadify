from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime
from src.enums.gamification.insignia_enums import TipoInsignia


class InsigniaBase(BaseModel):
    nombre: str = Field(max_length=100, description="Nombre de la insignia")
    descripcion: str | None = Field(None, description="Descripción de la insignia")
    imagen_url: str | None = Field(None, description="URL de la imagen de la insignia")
    es_unica: bool = Field(description="Si la insignia se puede obtener solo una vez")


class InsigniaCreate(InsigniaBase):
    tipo: TipoInsignia = Field(
        default=TipoInsignia.manual, description="Tipo de insignia"
    )


class InsigniaUpdate(BaseModel):
    nombre: str | None = Field(None, max_length=100)
    descripcion: str | None = None
    imagen_url: str | None = None
    es_unica: bool | None = None
    tipo: TipoInsignia | None = None


class InsigniaResponse(InsigniaBase):
    insignia_id: UUID
    tipo: TipoInsignia

    class Config:
        from_attributes = True


class UsuarioInsigniaBase(BaseModel):
    pass


class UsuarioInsigniaCreate(UsuarioInsigniaBase):
    usuario_id: UUID
    insignia_id: UUID
    otorgada_por: UUID | None = Field(
        None, description="ID del usuario que otorgó la insignia"
    )


class UsuarioInsigniaResponse(UsuarioInsigniaBase):
    usuario_id: UUID
    insignia_id: UUID
    otorgada_por: UUID | None = None
    fecha_otorgada: datetime

    # Datos de la insignia incluidos
    insignia: InsigniaResponse

    class Config:
        from_attributes = True


class OtorgarInsigniaRequest(BaseModel):
    usuario_id: UUID
    insignia_id: UUID
    otorgada_por: UUID | None = Field(
        None, description="ID del usuario que otorga la insignia"
    )


class UsuarioInsigniasResponse(BaseModel):
    usuario_id: UUID
    total_insignias: int
    insignias: list[UsuarioInsigniaResponse]


class InsigniaConEstadisticasResponse(InsigniaResponse):
    total_usuarios_con_insignia: int
    porcentaje_usuarios: float
