"""
Schemas Pydantic para Inscripciones

Define los schemas de entrada/salida para la API de inscripciones.
Incluye validaciones de negocio y transformaciones.
"""
from datetime import date, datetime
from typing import Optional, List, Dict, Any
from decimal import Decimal
from uuid import UUID
from pydantic import BaseModel, Field, validator, root_validator

from src.enums.academic import (
    EstadoInscripcion,
    TipoInscripcion,
    MotivoRechazo,
    MotivoRetiro,
    FormaPago
)


# ==================== Base Schemas ====================

class InscripcionBase(BaseModel):
    """Schema base con campos comunes"""
    tipo_inscripcion: TipoInscripcion = Field(default=TipoInscripcion.regular)
    
    # Carga académica
    creditos_inscritos: Optional[int] = Field(None, ge=0)
    horas_semanales: Optional[int] = Field(None, ge=0)
    
    # Convalidaciones
    tiene_convalidacion: bool = False
    creditos_convalidados: Optional[int] = Field(0, ge=0)
    tiene_homologacion: bool = False
    
    # Financiero
    forma_pago: Optional[FormaPago] = None
    tiene_beca: bool = False
    porcentaje_beca: Optional[Decimal] = Field(0, ge=0, le=100)
    tipo_beca: Optional[str] = Field(None, max_length=100)
    tiene_credito: bool = False
    entidad_credito: Optional[str] = Field(None, max_length=200)
    
    # Configuración
    observaciones: Optional[str] = None
    metadata_adicional: Optional[Dict[str, Any]] = None


# ==================== Create Schema ====================

class InscripcionCreate(InscripcionBase):
    """Schema para crear una nueva inscripción"""
    estudiante_id: UUID = Field(..., description="ID del estudiante (UUID)")
    grupo_id: UUID = Field(..., description="ID del grupo/sección (UUID)")
    periodo_academico_id: int = Field(..., gt=0, description="ID del período académico")
    programa_id: UUID = Field(..., description="ID del programa (UUID)")
    
    # Fechas
    fecha_solicitud: datetime = Field(default_factory=datetime.now)
    costo_total: Decimal = Field(default=Decimal("0.00"), ge=0)
    monto_final: Decimal = Field(default=Decimal("0.00"), ge=0)
    
    @validator('creditos_convalidados')
    def validar_creditos_convalidados(cls, v, values):
        """Si tiene convalidación, debe tener créditos"""
        if values.get('tiene_convalidacion') and (v is None or v <= 0):
            raise ValueError('Si tiene convalidación debe especificar créditos convalidados')
        return v
    
    @validator('tipo_beca')
    def validar_tipo_beca(cls, v, values):
        """Si tiene beca, debe especificar tipo"""
        if values.get('tiene_beca') and not v:
            raise ValueError('Si tiene beca debe especificar el tipo')
        return v


# ==================== Update Schema ====================

class InscripcionUpdate(BaseModel):
    """Schema para actualizar una inscripción"""
    tipo_inscripcion: Optional[TipoInscripcion] = None
    creditos_inscritos: Optional[int] = Field(None, ge=0)
    horas_semanales: Optional[int] = Field(None, ge=0)
    
    # Financiero
    costo_total: Optional[Decimal] = Field(None, ge=0)
    monto_final: Optional[Decimal] = Field(None, ge=0)
    tiene_beca: Optional[bool] = None
    porcentaje_beca: Optional[Decimal] = Field(None, ge=0, le=100)
    tipo_beca: Optional[str] = Field(None, max_length=100)
    forma_pago: Optional[FormaPago] = None
    
    # Documentación
    documentos_completos: Optional[bool] = None
    documentos_entregados: Optional[List[str]] = None
    
    # Calificaciones
    calificacion_final: Optional[Decimal] = Field(None, ge=0, le=5)
    porcentaje_asistencia: Optional[Decimal] = Field(None, ge=0, le=100)
    aprobo_curso: Optional[bool] = None
    
    # Configuración
    puede_cancelar: Optional[bool] = None
    puede_retirar: Optional[bool] = None
    requiere_atencion: Optional[bool] = None
    motivo_atencion: Optional[str] = None
    observaciones: Optional[str] = None
    notas_internas: Optional[str] = None


# ==================== Response Schemas ====================

class InscripcionResponse(InscripcionBase):
    """Schema de respuesta completo"""
    id: int
    codigo_inscripcion: str
    estudiante_id: int
    grupo_id: int
    periodo_academico_id: int
    programa_id: Optional[int]
    
    estado: EstadoInscripcion
    
    # Fechas
    fecha_solicitud: datetime
    fecha_inscripcion: Optional[datetime]
    fecha_confirmacion: Optional[datetime]
    fecha_finalizacion: Optional[datetime]
    
    # Financiero
    costo_total: Optional[Decimal]
    monto_final: Optional[Decimal]
    esta_pagado: bool
    fecha_pago: Optional[datetime]
    
    # Documentos
    documentos_completos: bool
    
    # Aprobación
    requiere_aprobacion: bool
    esta_aprobada: bool
    fecha_aprobacion: Optional[datetime]
    
    # Rechazo/Retiro
    fue_rechazada: bool
    motivo_rechazo: Optional[str]
    fue_retirada: bool
    motivo_retiro: Optional[str]
    
    # Lista de espera
    en_lista_espera: bool
    posicion_lista_espera: Optional[int]
    
    # Calificaciones
    calificacion_final: Optional[Decimal]
    aprobo_curso: Optional[bool]
    porcentaje_asistencia: Optional[Decimal]
    
    # Auditoría
    creado_por_id: Optional[int]
    fecha_creacion: datetime
    fecha_actualizacion: datetime
    activo: bool
    
    # Computed properties
    nombre_completo_estudiante: str
    esta_activa: bool
    esta_pendiente: bool
    puede_asistir_clases: bool
    tiene_deuda: bool
    dias_desde_solicitud: Optional[int]
    progreso_documentos: Dict[str, Any]
    info_financiera: Dict[str, Any]
    
    class Config:
        from_attributes = True
        json_encoders = {
            Decimal: float,
            date: lambda v: v.isoformat(),
            datetime: lambda v: v.isoformat()
        }


# ==================== Simple Response ====================

class InscripcionSimple(BaseModel):
    """Schema simple para listados"""
    id: int
    codigo_inscripcion: str
    estudiante_id: int
    grupo_id: int
    estado: EstadoInscripcion
    tipo_inscripcion: TipoInscripcion
    
    fecha_solicitud: datetime
    esta_pagado: bool
    esta_aprobada: bool
    esta_activa: bool
    esta_pendiente: bool
    
    nombre_completo_estudiante: str
    
    class Config:
        from_attributes = True


# ==================== List Response ====================

class InscripcionListResponse(BaseModel):
    """Schema para respuesta de listados con paginación"""
    items: List[InscripcionSimple]
    total: int
    page: int
    page_size: int
    total_pages: int


# ==================== Action Schemas ====================

class InscripcionAprobar(BaseModel):
    """Schema para aprobar una inscripción"""
    comentarios: Optional[str] = Field(None, description="Comentarios de aprobación")


class InscripcionRechazar(BaseModel):
    """Schema para rechazar una inscripción"""
    motivo: MotivoRechazo = Field(..., description="Motivo del rechazo")
    descripcion: str = Field(..., min_length=10, description="Descripción detallada")


class InscripcionRetirar(BaseModel):
    """Schema para retirar una inscripción"""
    motivo: MotivoRetiro = Field(..., description="Motivo del retiro")
    descripcion: str = Field(..., min_length=10, description="Descripción detallada")
    es_voluntario: bool = Field(default=True, description="Es retiro voluntario")


class InscripcionRegistrarPago(BaseModel):
    """Schema para registrar un pago"""
    monto: Decimal = Field(..., gt=0, description="Monto pagado")
    referencia: Optional[str] = Field(None, max_length=100, description="Referencia del pago")
    forma_pago: FormaPago = Field(..., description="Forma de pago")
    
    @validator('monto')
    def validar_monto_positivo(cls, v):
        if v <= 0:
            raise ValueError('El monto debe ser mayor a cero')
        return v


class InscripcionActualizarDocumentos(BaseModel):
    """Schema para actualizar documentos"""
    documentos_entregados: List[str] = Field(..., min_items=1, description="Lista de documentos entregados")
    documentos_completos: bool = Field(..., description="Indica si ya están todos los documentos")


class InscripcionActualizarCalificacion(BaseModel):
    """Schema para actualizar calificación"""
    calificacion_final: Decimal = Field(..., ge=0, le=5, description="Calificación final (0-5)")
    calificacion_literal: Optional[str] = Field(None, max_length=10, description="Calificación literal (A, B, C)")
    aprobo_curso: bool = Field(..., description="Indica si aprobó el curso")
    porcentaje_asistencia: Optional[Decimal] = Field(None, ge=0, le=100, description="Porcentaje de asistencia")


class InscripcionListaEspera(BaseModel):
    """Schema para agregar a lista de espera"""
    posicion: int = Field(..., gt=0, description="Posición en la lista de espera")


# ==================== Filter Schemas ====================

class InscripcionFiltros(BaseModel):
    """Schema para filtros de búsqueda"""
    estudiante_id: Optional[int] = Field(None, gt=0)
    grupo_id: Optional[int] = Field(None, gt=0)
    periodo_academico_id: Optional[int] = Field(None, gt=0)
    programa_id: Optional[int] = Field(None, gt=0)
    
    estado: Optional[EstadoInscripcion] = None
    tipo_inscripcion: Optional[TipoInscripcion] = None
    
    esta_pagado: Optional[bool] = None
    esta_aprobada: Optional[bool] = None
    activo: Optional[bool] = None
    
    fecha_desde: Optional[date] = None
    fecha_hasta: Optional[date] = None


# ==================== Statistics Schema ====================

class InscripcionEstadisticas(BaseModel):
    """Schema para estadísticas de inscripciones"""
    total_inscripciones: int
    por_estado: Dict[str, int]
    por_tipo: Dict[str, int]
    
    total_pagadas: int
    total_pendientes_pago: int
    monto_total_recaudado: Decimal
    
    total_aprobadas: int
    total_rechazadas: int
    total_retiradas: int
    total_lista_espera: int
    
    promedio_calificacion: Optional[Decimal]
    porcentaje_aprobacion: Optional[Decimal]
    
    class Config:
        json_encoders = {
            Decimal: float
        }


# ==================== Bulk Operations ====================

class InscripcionBulkCreate(BaseModel):
    """Schema para creación masiva de inscripciones"""
    inscripciones: List[InscripcionCreate] = Field(..., min_items=1, max_items=100)
    
    @validator('inscripciones')
    def validar_inscripciones_unicas(cls, v):
        """Valida que no haya inscripciones duplicadas"""
        pares = [(insc.estudiante_id, insc.grupo_id) for insc in v]
        if len(pares) != len(set(pares)):
            raise ValueError('Hay inscripciones duplicadas en el lote')
        return v


class InscripcionBulkResponse(BaseModel):
    """Schema de respuesta para operaciones masivas"""
    exitosas: int
    fallidas: int
    detalles: List[Dict[str, Any]]
    inscripciones_creadas: List[InscripcionSimple]
