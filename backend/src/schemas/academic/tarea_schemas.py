from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from ..enums.academic.tareas import EstadoTarea, TipoTarea, PrioridadTarea, EstadoEntrega

# Schemas para Tarea
class TareaBase(BaseModel):
    titulo: str = Field(..., min_length=1, max_length=200)
    descripcion: Optional[str] = None
    instrucciones: Optional[str] = None
    objetivos: Optional[str] = None
    tipo_tarea: TipoTarea = TipoTarea.ENSAYO
    prioridad: PrioridadTarea = PrioridadTarea.MEDIA
    categoria: Optional[str] = None
    tags: Optional[str] = None
    fecha_limite: datetime
    fecha_inicio_disponible: Optional[datetime] = None
    tiempo_estimado: Optional[int] = None
    permite_entrega_tardia: bool = False
    penalizacion_tardia: float = Field(default=0.0, ge=0.0, le=100.0)
    intentos_maximos: int = Field(default=1, ge=1)
    formato_entrega: Optional[str] = None
    tamano_maximo_mb: float = Field(default=10.0, gt=0)
    puntuacion_maxima: float = Field(default=100.0, gt=0)
    peso_evaluacion: float = Field(default=1.0, gt=0)
    es_grupal: bool = False
    es_publica: bool = True
    requiere_aprobacion: bool = False
    recursos_necesarios: Optional[str] = None
    criterios_evaluacion: Optional[str] = None

class TareaCreate(TareaBase):
    grupo_id: str
    docente_id: str
    rubrica_id: Optional[str] = None
    configuracion_json: Optional[Dict[str, Any]] = None

class TareaUpdate(BaseModel):
    titulo: Optional[str] = Field(None, min_length=1, max_length=200)
    descripcion: Optional[str] = None
    instrucciones: Optional[str] = None
    objetivos: Optional[str] = None
    tipo_tarea: Optional[TipoTarea] = None
    prioridad: Optional[PrioridadTarea] = None
    categoria: Optional[str] = None
    tags: Optional[str] = None
    fecha_limite: Optional[datetime] = None
    fecha_inicio_disponible: Optional[datetime] = None
    tiempo_estimado: Optional[int] = None
    permite_entrega_tardia: Optional[bool] = None
    penalizacion_tardia: Optional[float] = Field(None, ge=0.0, le=100.0)
    intentos_maximos: Optional[int] = Field(None, ge=1)
    formato_entrega: Optional[str] = None
    tamano_maximo_mb: Optional[float] = Field(None, gt=0)
    puntuacion_maxima: Optional[float] = Field(None, gt=0)
    peso_evaluacion: Optional[float] = Field(None, gt=0)
    estado: Optional[EstadoTarea] = None
    es_grupal: Optional[bool] = None
    es_publica: Optional[bool] = None
    requiere_aprobacion: Optional[bool] = None
    recursos_necesarios: Optional[str] = None
    criterios_evaluacion: Optional[str] = None
    rubrica_id: Optional[str] = None
    configuracion_json: Optional[Dict[str, Any]] = None
    activa: Optional[bool] = None

class TareaResponse(TareaBase):
    tarea_id: str
    grupo_id: str
    docente_id: str
    estado: EstadoTarea
    rubrica_id: Optional[str] = None
    fecha_asignacion: datetime
    fecha_creacion: datetime
    fecha_actualizacion: Optional[datetime] = None
    creado_por: Optional[str] = None
    actualizado_por: Optional[str] = None
    activa: bool
    
    # Propiedades calculadas
    total_entregas: Optional[int] = 0
    entregas_pendientes: Optional[int] = 0
    promedio_calificaciones: Optional[float] = 0.0
    esta_vencida: Optional[bool] = False
    
    class Config:
        from_attributes = True

class TareaDetallada(TareaResponse):
    # Información adicional del docente
    docente_nombre: Optional[str] = None
    docente_apellido: Optional[str] = None
    
    # Información del grupo
    grupo_nombre: Optional[str] = None
    
    # Información de la rúbrica
    rubrica_nombre: Optional[str] = None
    
    # Estadísticas detalladas
    estudiantes_asignados: Optional[int] = 0
    entregas_calificadas: Optional[int] = 0
    porcentaje_completitud: Optional[float] = 0.0

# Schemas para EntregaTarea
class EntregaTareaBase(BaseModel):
    titulo_entrega: Optional[str] = None
    descripcion_entrega: Optional[str] = None
    comentarios_estudiante: Optional[str] = None
    archivo_url: Optional[str] = None
    archivos_adicionales: Optional[List[Dict[str, Any]]] = None
    contenido_texto: Optional[str] = None
    enlaces_externos: Optional[List[Dict[str, str]]] = None
    tiempo_empleado: Optional[int] = None
    dificultad_percibida: Optional[int] = Field(None, ge=1, le=5)
    satisfaccion_estudiante: Optional[int] = Field(None, ge=1, le=5)

class EntregaTareaCreate(EntregaTareaBase):
    tarea_id: str
    estudiante_id: str

class EntregaTareaUpdate(EntregaTareaBase):
    estado: Optional[EstadoEntrega] = None
    es_final: Optional[bool] = None

class CalificarEntrega(BaseModel):
    calificacion: float = Field(..., ge=0)
    calificacion_letras: Optional[str] = None
    comentarios_docente: Optional[str] = None
    rubrica_calificacion: Optional[Dict[str, Any]] = None
    requiere_revision: bool = False

class EntregaTareaResponse(EntregaTareaBase):
    entrega_id: str
    tarea_id: str
    estudiante_id: str
    fecha_entrega: Optional[datetime] = None
    fecha_limite_original: Optional[datetime] = None
    numero_intento: int
    es_entrega_tardia: bool
    calificacion: Optional[float] = None
    calificacion_letras: Optional[str] = None
    comentarios_docente: Optional[str] = None
    rubrica_calificacion: Optional[Dict[str, Any]] = None
    estado: EstadoEntrega
    es_final: bool
    requiere_revision: bool
    fecha_creacion: datetime
    fecha_actualizacion: Optional[datetime] = None
    calificado_por: Optional[str] = None
    fecha_calificacion: Optional[datetime] = None
    
    # Propiedades calculadas
    dias_desde_entrega: Optional[int] = 0
    porcentaje_calificacion: Optional[float] = 0.0
    
    class Config:
        from_attributes = True

class EntregaTareaDetallada(EntregaTareaResponse):
    # Información del estudiante
    estudiante_nombre: Optional[str] = None
    estudiante_apellido: Optional[str] = None
    estudiante_email: Optional[str] = None
    
    # Información de la tarea
    tarea_titulo: Optional[str] = None
    tarea_puntuacion_maxima: Optional[float] = None
    
    # Información del calificador
    calificador_nombre: Optional[str] = None
    calificador_apellido: Optional[str] = None

# Schemas para Rubrica
class RubricaBase(BaseModel):
    nombre: str = Field(..., min_length=1, max_length=200)
    descripcion: Optional[str] = None
    criterios: Dict[str, Any] = Field(..., min_items=1)
    puntuacion_total: float = Field(default=100.0, gt=0)
    es_publica: bool = True
    es_plantilla: bool = False

class RubricaCreate(RubricaBase):
    creado_por: str

class RubricaUpdate(BaseModel):
    nombre: Optional[str] = Field(None, min_length=1, max_length=200)
    descripcion: Optional[str] = None
    criterios: Optional[Dict[str, Any]] = None
    puntuacion_total: Optional[float] = Field(None, gt=0)
    es_publica: Optional[bool] = None
    es_plantilla: Optional[bool] = None
    activa: Optional[bool] = None

class RubricaResponse(RubricaBase):
    rubrica_id: str
    creado_por: str
    activa: bool
    fecha_creacion: datetime
    fecha_actualizacion: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class RubricaDetallada(RubricaResponse):
    # Información del creador
    creador_nombre: Optional[str] = None
    creador_apellido: Optional[str] = None
    
    # Estadísticas de uso
    veces_utilizada: Optional[int] = 0
    tareas_asociadas: Optional[int] = 0

# Schemas para filtros y búsquedas
class FiltrosTarea(BaseModel):
    grupo_id: Optional[str] = None
    docente_id: Optional[str] = None
    tipo_tarea: Optional[TipoTarea] = None
    estado: Optional[EstadoTarea] = None
    prioridad: Optional[PrioridadTarea] = None
    es_grupal: Optional[bool] = None
    solo_activas: bool = True
    fecha_desde: Optional[datetime] = None
    fecha_hasta: Optional[datetime] = None
    busqueda: Optional[str] = None
    ordenar_por: str = "fecha_limite"
    orden_desc: bool = False
    pagina: int = Field(default=1, ge=1)
    tamaño_pagina: int = Field(default=20, ge=1, le=100)

class FiltrosEntrega(BaseModel):
    tarea_id: Optional[str] = None
    estudiante_id: Optional[str] = None
    estado: Optional[EstadoEntrega] = None
    solo_calificadas: Optional[bool] = None
    solo_pendientes: Optional[bool] = None
    fecha_desde: Optional[datetime] = None
    fecha_hasta: Optional[datetime] = None
    ordenar_por: str = "fecha_entrega"
    orden_desc: bool = True
    pagina: int = Field(default=1, ge=1)
    tamaño_pagina: int = Field(default=20, ge=1, le=100)

# Schemas para estadísticas
class EstadisticasTarea(BaseModel):
    total_tareas: int
    tareas_activas: int
    tareas_vencidas: int
    tareas_completadas: int
    promedio_entregas_por_tarea: float
    promedio_calificaciones: float
    tiempo_promedio_calificacion: Optional[float] = None

class EstadisticasEntrega(BaseModel):
    total_entregas: int
    entregas_calificadas: int
    entregas_pendientes: int
    entregas_tardias: int
    promedio_calificacion: float
    tiempo_promedio_entrega: Optional[float] = None

# Validadores personalizados
@validator('fecha_limite')
def validar_fecha_limite(cls, v, values):
    if 'fecha_inicio_disponible' in values and values['fecha_inicio_disponible']:
        if v <= values['fecha_inicio_disponible']:
            raise ValueError('La fecha límite debe ser posterior a la fecha de inicio disponible')
    return v

@validator('tags')
def validar_tags(cls, v):
    if v:
        # Validar formato de tags separados por comas
        tags = [tag.strip() for tag in v.split(',')]
        if len(tags) > 10:
            raise ValueError('Máximo 10 tags permitidos')
        for tag in tags:
            if len(tag) > 50:
                raise ValueError('Cada tag debe tener máximo 50 caracteres')
    return v