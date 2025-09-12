import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
from src.enums.gamification.insignia_enums import TipoInsignia


class InsigniaBase(BaseModel):
    nombre: str = Field(max_length=100, description="Nombre de la insignia")
    descripcion: Optional[str] = Field(None, description="Descripción de la insignia")
    imagen_url: Optional[str] = Field(None, description="URL de la imagen de la insignia")
    es_unica: bool = Field(description="Si la insignia se puede obtener solo una vez")


class InsigniaCreate(InsigniaBase):
    tipo: TipoInsignia = Field(default=TipoInsignia.manual, description="Tipo de insignia")


class InsigniaUpdate(BaseModel):
    nombre: Optional[str] = Field(None, max_length=100)
    descripcion: Optional[str] = None
    imagen_url: Optional[str] = None
    es_unica: Optional[bool] = None
    tipo: Optional[TipoInsignia] = None


class InsigniaResponse(InsigniaBase):
    insignia_id: uuid.UUID
    tipo: TipoInsignia
    
    class Config:
        from_attributes = True


class UsuarioInsigniaBase(BaseModel):
    pass


class UsuarioInsigniaCreate(UsuarioInsigniaBase):
    usuario_id: uuid.UUID
    insignia_id: uuid.UUID
    otorgada_por: Optional[uuid.UUID] = Field(None, description="ID del usuario que otorgó la insignia")


class UsuarioInsigniaResponse(UsuarioInsigniaBase):
    usuario_id: uuid.UUID
    insignia_id: uuid.UUID
    otorgada_por: Optional[uuid.UUID]
    fecha_otorgada: datetime
    
    # Datos de la insignia incluidos
    insignia: InsigniaResponse
    
    class Config:
        from_attributes = True


class OtorgarInsigniaRequest(BaseModel):
    usuario_id: uuid.UUID
    insignia_id: uuid.UUID
    otorgada_por: Optional[uuid.UUID] = Field(None, description="ID del usuario que otorga la insignia")


class UsuarioInsigniasResponse(BaseModel):
    usuario_id: uuid.UUID
    total_insignias: int
    insignias: list[UsuarioInsigniaResponse]


class InsigniaConEstadisticasResponse(InsigniaResponse):
    total_usuarios_con_insignia: int
    porcentaje_usuarios: float