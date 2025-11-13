"""
Schemas Pydantic para Período Académico

Define los schemas de entrada/salida para la API de períodos académicos.
"""
from datetime import date, datetime
from typing import Optional, List, Dict, Any
from decimal import Decimal
from pydantic import BaseModel, Field, validator, root_validator

from src.enums.academic import TipoPeriodo, EstadoPeriodo


# ==================== Base Schemas ====================

class PeriodoAcademicoBase(BaseModel):
    """Schema base con campos comunes"""
    nombre: str = Field(..., min_length=1, max_length=200, description="Nombre del período")
    codigo: str = Field(..., min_length=1, max_length=50, description="Código único del período")
    descripcion: Optional[str] = Field(None, description="Descripción detallada")
    
    tipo: TipoPeriodo = Field(..., description="Tipo de período")
    anio: int = Field(..., ge=2000, le=2100, description="Año del período")
    numero_periodo: Optional[int] = Field(None, ge=1, le=12, description="Número del período en el año")
    nivel_aplica: Optional[str] = Field(None, max_length=100, description="Nivel al que aplica")
    
    # Fechas principales
    fecha_inicio: date = Field(..., description="Fecha de inicio del período")
    fecha_fin: date = Field(..., description="Fecha de fin del período")
    
    # Fechas de inscripciones
    fecha_inicio_preinscripciones: Optional[date] = None
    fecha_fin_preinscripciones: Optional[date] = None
    fecha_inicio_inscripciones: date = Field(..., description="Inicio de inscripciones")
    fecha_fin_inscripciones: date = Field(..., description="Fin de inscripciones")
    
    # Fechas de ajustes
    fecha_inicio_ajustes: Optional[date] = None
    fecha_fin_ajustes: Optional[date] = None
    
    # Fechas de clases
    fecha_inicio_clases: date = Field(..., description="Inicio de clases")
    fecha_fin_clases: date = Field(..., description="Fin de clases")
    
    # Fechas de retiros
    fecha_limite_retiro: Optional[date] = None
    fecha_limite_retiro_con_reembolso: Optional[date] = None
    
    # Fechas de evaluaciones
    fecha_inicio_examenes: Optional[date] = None
    fecha_fin_examenes: Optional[date] = None
    
    # Fechas de calificaciones
    fecha_cierre_notas: Optional[date] = None
    fecha_publicacion_notas: Optional[date] = None
    
    # Configuración
    permite_inscripciones: bool = True
    permite_ajustes: bool = True
    permite_retiros: bool = True
    
    visible_estudiantes: bool = True
    visible_profesores: bool = True
    visible_publico: bool = False
    
    # Límites
    creditos_minimos: Optional[int] = Field(None, ge=0)
    creditos_maximos: Optional[int] = Field(None, ge=0)
    cursos_minimos: Optional[int] = Field(None, ge=0)
    cursos_maximos: Optional[int] = Field(None, ge=0)
    
    # Costos
    costo_matricula: Optional[Decimal] = Field(None, ge=0)
    costo_por_credito: Optional[Decimal] = Field(None, ge=0)
    moneda: str = Field(default="COP", max_length=10)
    
    # Metadata
    dias_festivos: Optional[List[str]] = Field(None, description="Lista de fechas festivas")
    vacaciones: Optional[List[Dict[str, Any]]] = Field(None, description="Períodos de vacaciones")
    configuracion: Optional[Dict[str, Any]] = Field(None, description="Configuración adicional")
    notas: Optional[str] = None
    
    @validator('fecha_fin')
    def validar_fecha_fin(cls, v, values):
        """Valida que fecha_fin sea posterior a fecha_inicio"""
        if 'fecha_inicio' in values and v <= values['fecha_inicio']:
            raise ValueError('fecha_fin debe ser posterior a fecha_inicio')
        return v
    
    @validator('fecha_fin_inscripciones')
    def validar_fecha_fin_inscripciones(cls, v, values):
        """Valida fechas de inscripciones"""
        if 'fecha_inicio_inscripciones' in values and v < values['fecha_inicio_inscripciones']:
            raise ValueError('fecha_fin_inscripciones debe ser posterior o igual a fecha_inicio_inscripciones')
        return v
    
    @validator('fecha_fin_clases')
    def validar_fecha_fin_clases(cls, v, values):
        """Valida fechas de clases"""
        if 'fecha_inicio_clases' in values and v <= values['fecha_inicio_clases']:
            raise ValueError('fecha_fin_clases debe ser posterior a fecha_inicio_clases')
        return v
    
    @validator('creditos_maximos')
    def validar_creditos_maximos(cls, v, values):
        """Valida que creditos_maximos >= creditos_minimos"""
        if v is not None and 'creditos_minimos' in values:
            minimo = values['creditos_minimos']
            if minimo is not None and v < minimo:
                raise ValueError('creditos_maximos debe ser mayor o igual a creditos_minimos')
        return v
    
    @validator('cursos_maximos')
    def validar_cursos_maximos(cls, v, values):
        """Valida que cursos_maximos >= cursos_minimos"""
        if v is not None and 'cursos_minimos' in values:
            minimo = values['cursos_minimos']
            if minimo is not None and v < minimo:
                raise ValueError('cursos_maximos debe ser mayor o igual a cursos_minimos')
        return v


# ==================== Create Schema ====================

class PeriodoAcademicoCreate(PeriodoAcademicoBase):
    """Schema para crear un nuevo período académico"""
    institucion_id: int = Field(..., gt=0, description="ID de la institución")
    estado: EstadoPeriodo = Field(default=EstadoPeriodo.programado, description="Estado inicial")
    activo: bool = Field(default=True)
    es_actual: bool = Field(default=False)


# ==================== Update Schema ====================

class PeriodoAcademicoUpdate(BaseModel):
    """
    Schema para actualizar un período académico.
    Todos los campos son opcionales para permitir actualizaciones parciales.
    
    Principio SOLID: Open/Closed - Schema abierto para extensión,
    pero cerrado para modificación de reglas de negocio (validaciones en Service).
    """
    # Identificación
    nombre: Optional[str] = Field(None, min_length=1, max_length=200)
    codigo: Optional[str] = Field(None, min_length=1, max_length=50, description="Código único del período")
    descripcion: Optional[str] = None
    
    tipo: Optional[TipoPeriodo] = None
    estado: Optional[EstadoPeriodo] = None
    numero_periodo: Optional[int] = Field(None, ge=1, le=12)
    nivel_aplica: Optional[str] = Field(None, max_length=100)
    
    # Fechas
    fecha_inicio: Optional[date] = None
    fecha_fin: Optional[date] = None
    fecha_inicio_preinscripciones: Optional[date] = None
    fecha_fin_preinscripciones: Optional[date] = None
    fecha_inicio_inscripciones: Optional[date] = None
    fecha_fin_inscripciones: Optional[date] = None
    fecha_inicio_ajustes: Optional[date] = None
    fecha_fin_ajustes: Optional[date] = None
    fecha_inicio_clases: Optional[date] = None
    fecha_fin_clases: Optional[date] = None
    fecha_limite_retiro: Optional[date] = None
    fecha_limite_retiro_con_reembolso: Optional[date] = None
    fecha_inicio_examenes: Optional[date] = None
    fecha_fin_examenes: Optional[date] = None
    fecha_cierre_notas: Optional[date] = None
    fecha_publicacion_notas: Optional[date] = None
    
    # Configuración
    permite_inscripciones: Optional[bool] = None
    permite_ajustes: Optional[bool] = None
    permite_retiros: Optional[bool] = None
    visible_estudiantes: Optional[bool] = None
    visible_profesores: Optional[bool] = None
    visible_publico: Optional[bool] = None
    
    # Límites
    creditos_minimos: Optional[int] = Field(None, ge=0)
    creditos_maximos: Optional[int] = Field(None, ge=0)
    cursos_minimos: Optional[int] = Field(None, ge=0)
    cursos_maximos: Optional[int] = Field(None, ge=0)
    
    # Costos
    costo_matricula: Optional[Decimal] = Field(None, ge=0)
    costo_por_credito: Optional[Decimal] = Field(None, ge=0)
    moneda: Optional[str] = Field(None, max_length=10)
    
    # Metadata
    dias_festivos: Optional[List[str]] = None
    vacaciones: Optional[List[Dict[str, Any]]] = None
    configuracion: Optional[Dict[str, Any]] = None
    notas: Optional[str] = None
    
    # Estado
    activo: Optional[bool] = None
    es_actual: Optional[bool] = None


# ==================== Response Schema ====================

class PeriodoAcademicoResponse(PeriodoAcademicoBase):
    """Schema de respuesta completo"""
    id: int
    institucion_id: int
    estado: EstadoPeriodo
    activo: bool
    es_actual: bool
    
    creado_por_id: Optional[int] = None
    modificado_por_id: Optional[int] = None
    fecha_creacion: datetime
    fecha_actualizacion: datetime
    
    # Computed fields
    nombre_completo: str
    esta_activo: bool
    permite_inscribirse_ahora: bool
    esta_en_curso: bool
    dias_hasta_inicio: Optional[int]
    dias_transcurridos: Optional[int]
    duracion_dias: Optional[int]
    porcentaje_avance: Optional[float]
    
    class Config:
        from_attributes = True
        json_encoders = {
            Decimal: float,
            date: lambda v: v.isoformat(),
            datetime: lambda v: v.isoformat()
        }


# ==================== Simple Response (para listados) ====================

class PeriodoAcademicoSimple(BaseModel):
    """Schema simple para listados"""
    id: int
    nombre: str
    codigo: str
    tipo: TipoPeriodo
    estado: EstadoPeriodo
    anio: int
    numero_periodo: Optional[int]
    
    fecha_inicio: date
    fecha_fin: date
    fecha_inicio_inscripciones: date
    fecha_fin_inscripciones: date
    
    activo: bool
    es_actual: bool
    permite_inscribirse_ahora: bool
    
    class Config:
        from_attributes = True


# ==================== List Response ====================

class PeriodoAcademicoListResponse(BaseModel):
    """Schema para respuesta de listados con paginación"""
    items: List[PeriodoAcademicoSimple]
    total: int
    page: int
    page_size: int
    total_pages: int
    
    class Config:
        from_attributes = True


# ==================== Estado Change Schemas ====================

class PeriodoAcademicoActivar(BaseModel):
    """Schema para activar un período"""
    motivo: Optional[str] = Field(None, description="Motivo de la activación")


class PeriodoAcademicoDesactivar(BaseModel):
    """Schema para desactivar un período"""
    motivo: Optional[str] = Field(None, description="Motivo de la desactivación")


class PeriodoAcademicoCancelar(BaseModel):
    """Schema para cancelar un período"""
    motivo: str = Field(..., min_length=10, description="Motivo de la cancelación (requerido)")


class PeriodoAcademicoFinalizar(BaseModel):
    """Schema para finalizar un período"""
    notas_finales: Optional[str] = Field(None, description="Notas finales del período")
