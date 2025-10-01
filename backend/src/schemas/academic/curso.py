from pydantic import BaseModel, Field, validator
from uuid import UUID
from datetime import date, datetime
from typing import Optional
from ...enums.academic.curso_enums import ModalidadCurso


class CursoBase(BaseModel):
    nombre: str = Field(..., min_length=3, max_length=100)
    descripcion: Optional[str] = None
    objetivos: Optional[str] = None
    codigo_curso: Optional[str] = Field(None, max_length=20)
    creditos: int = Field(0, ge=0, le=20)
    horas_academicas: int = Field(0, ge=0, le=200)
    modalidad: ModalidadCurso
    fecha_inicio: Optional[date] = None
    fecha_fin: Optional[date] = None
    maximo_estudiantes: Optional[int] = Field(None, ge=1, le=500)
    minimo_estudiantes: int = Field(1, ge=1, le=100)
    permite_inscripcion: bool = True
    permite_material_estudiantes: bool = False
    requiere_aprobacion_material: bool = True

    @validator('fecha_fin')
    def validar_fecha_fin(cls, v, values):
        if v and 'fecha_inicio' in values and values['fecha_inicio'] and v <= values['fecha_inicio']:
            raise ValueError('La fecha de fin debe ser posterior a la fecha de inicio')
        return v


class CursoCreate(CursoBase):
    institucion_id: UUID
<<<<<<< HEAD
    coordinador_id: Optional[UUID] = None
    programa_id: UUID
=======
    coordinador_id: UUID | None = None
    programa_id: UUID | None = None
>>>>>>> cf42a38e98e83ad9207c8f65d1c1d4100a739333


class CursoUpdate(BaseModel):
    nombre: Optional[str] = Field(None, min_length=3, max_length=100)
    descripcion: Optional[str] = None
    objetivos: Optional[str] = None
    codigo_curso: Optional[str] = Field(None, max_length=20)
    creditos: Optional[int] = Field(None, ge=0, le=20)
    horas_academicas: Optional[int] = Field(None, ge=0, le=200)
    modalidad: Optional[ModalidadCurso] = None
    fecha_inicio: Optional[date] = None
    fecha_fin: Optional[date] = None
    maximo_estudiantes: Optional[int] = Field(None, ge=1, le=500)
    minimo_estudiantes: Optional[int] = Field(None, ge=1, le=100)
    activo: Optional[bool] = None
    permite_inscripcion: Optional[bool] = None
    permite_material_estudiantes: Optional[bool] = None
    requiere_aprobacion_material: Optional[bool] = None


class CursoInDBBase(CursoBase):
    curso_id: UUID
    institucion_id: UUID
<<<<<<< HEAD
    coordinador_id: Optional[UUID] = None
    programa_id: UUID
    activo: bool
    carpeta_drive_id: Optional[str] = None
    carpeta_drive_url: Optional[str] = None
    fecha_creacion: datetime
    fecha_actualizacion: Optional[datetime]
=======
    coordinador_id: UUID | None = None
    programa_id: UUID | None = None
>>>>>>> cf42a38e98e83ad9207c8f65d1c1d4100a739333

    class Config:
        from_attributes = True


class Curso(CursoInDBBase):
    pass


class CursoDetallado(CursoInDBBase):
    # Información de relaciones
    institucion_nombre: Optional[str] = None
    coordinador_nombre: Optional[str] = None
    coordinador_apellido: Optional[str] = None
    programa_nombre: Optional[str] = None
    
    # Estadísticas
    total_estudiantes: int = 0
    total_docentes: int = 0
    total_grupos: int = 0
    total_material: int = 0
    total_clases: int = 0

    class Config:
        from_attributes = True


class EstadisticasCurso(BaseModel):
    curso_id: UUID
    total_estudiantes_inscritos: int
    total_docentes_asignados: int
    total_grupos_vinculados: int
    total_material_subido: int
    total_clases_programadas: int
    promedio_asistencia: float
    ultima_actividad: Optional[datetime]

    class Config:
        from_attributes = True


class ConfiguracionDriveCurso(BaseModel):
    crear_carpeta_drive: bool = False
    nombre_carpeta: Optional[str] = None
    permisos_lectura_estudiantes: bool = True
    permisos_escritura_docentes: bool = True
