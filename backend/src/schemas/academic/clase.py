from pydantic import BaseModel, Field, validator
from uuid import UUID
from datetime import datetime
from typing import Optional, List
from ...enums.academic.clase_enums import EstadoClase, TipoClase, EstadoCodigoAcceso


class ClaseBase(BaseModel):
    titulo: str = Field(..., min_length=3, max_length=150)
    descripcion: Optional[str] = None
    tipo_clase: TipoClase = TipoClase.teorica
    fecha_inicio: datetime
    fecha_fin: Optional[datetime] = None
    duracion_estimada: Optional[int] = Field(None, ge=15, le=480)  # Entre 15 min y 8 horas
    max_estudiantes: Optional[int] = Field(None, ge=1, le=100)

    @validator('fecha_fin')
    def validar_fecha_fin(cls, v, values):
        if v and 'fecha_inicio' in values and v <= values['fecha_inicio']:
            raise ValueError('La fecha de fin debe ser posterior a la fecha de inicio')
        return v


class ClaseCreate(ClaseBase):
    grupo_id: UUID
    docente_id: UUID
    fecha_vencimiento_codigo: Optional[datetime] = None

    @validator('fecha_vencimiento_codigo')
    def validar_vencimiento(cls, v, values):
        if v and 'fecha_inicio' in values and v <= values['fecha_inicio']:
            raise ValueError('La fecha de vencimiento del código debe ser posterior a la fecha de inicio')
        return v


class ClaseUpdate(BaseModel):
    titulo: Optional[str] = Field(None, min_length=3, max_length=150)
    descripcion: Optional[str] = None
    tipo_clase: Optional[TipoClase] = None
    estado: Optional[EstadoClase] = None
    fecha_inicio: Optional[datetime] = None
    fecha_fin: Optional[datetime] = None
    duracion_estimada: Optional[int] = Field(None, ge=15, le=480)
    max_estudiantes: Optional[int] = Field(None, ge=1, le=100)
    fecha_vencimiento_codigo: Optional[datetime] = None


class CodigoAccesoResponse(BaseModel):
    codigo_acceso: str
    estado_codigo: EstadoCodigoAcceso
    fecha_vencimiento: Optional[datetime]
    fecha_generacion: datetime

    class Config:
        from_attributes = True


class HistorialAccesoBase(BaseModel):
    codigo_usado: str
    ip_acceso: Optional[str] = None
    user_agent: Optional[str] = None


class HistorialAccesoCreate(HistorialAccesoBase):
    clase_id: UUID
    estudiante_id: UUID


class HistorialAcceso(HistorialAccesoBase):
    historial_id: UUID
    clase_id: UUID
    estudiante_id: UUID
    fecha_acceso: datetime

    class Config:
        from_attributes = True


class ClaseInDBBase(ClaseBase):
    clase_id: UUID
    grupo_id: UUID
    docente_id: UUID
    estado: EstadoClase
    codigo_acceso: str
    estado_codigo: EstadoCodigoAcceso
    fecha_vencimiento_codigo: Optional[datetime]
    fecha_creacion: datetime
    fecha_actualizacion: Optional[datetime]

    class Config:
        from_attributes = True


class Clase(ClaseInDBBase):
    pass


class ClaseDetallada(ClaseInDBBase):
    # Información del grupo
    grupo_nombre: Optional[str] = None
    # Información del docente
    docente_nombre: Optional[str] = None
    docente_apellido: Optional[str] = None
    # Estadísticas
    total_estudiantes_unidos: int = 0
    total_material_subido: int = 0

    class Config:
        from_attributes = True


class ClaseConHistorial(ClaseInDBBase):
    historial_accesos: List[HistorialAcceso] = []

    class Config:
        from_attributes = True


class EstudianteUnirse(BaseModel):
    codigo_acceso: str = Field(..., min_length=8, max_length=8)
    ip_acceso: Optional[str] = None
    user_agent: Optional[str] = None


class RespuestaUnirse(BaseModel):
    success: bool
    message: str
    clase: Optional[Clase] = None