from pydantic import BaseModel, Field, field_validator, ConfigDict, model_validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from src.enums.academic.tareas import EstadoTarea, TipoTarea, PrioridadTarea, EstadoEntrega

# Schemas para Tarea
class TareaBase(BaseModel):
    model_config = ConfigDict(use_enum_values=True)
    
    titulo: str = Field(..., min_length=1, max_length=200)
    descripcion: Optional[str] = None
    instrucciones: Optional[str] = None
    objetivos: Optional[str] = None
    tipo: Optional[str] = Field(None, max_length=13)  # Campo real en BD (VARCHAR(13))
    prioridad: PrioridadTarea = PrioridadTarea.MEDIA
    
    @field_validator('prioridad', mode='before')
    @classmethod
    def normalize_prioridad(cls, v):
        """Normaliza prioridad - acepta enums de SQLAlchemy, strings, etc."""
        # Si ya es un enum, retorna directamente
        if isinstance(v, PrioridadTarea):
            return v
        # Si es string, busca el enum por valor (case-insensitive)
        if isinstance(v, str):
            v_lower = v.lower()
            for enum_member in PrioridadTarea:
                if enum_member.value == v_lower:
                    return enum_member
            # Si no encuentra por valor, intenta por nombre
            try:
                return PrioridadTarea[v.upper()]
            except KeyError:
                pass
        return v
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
    
    @field_validator('prioridad', mode='before')
    @classmethod
    def normalizar_prioridad(cls, v):
        """Normaliza valor de prioridad a enum válido (insensible a mayúsculas)."""
        if v is None:
            return PrioridadTarea.MEDIA
        if isinstance(v, PrioridadTarea):
            return v
        if isinstance(v, str):
            # Intenta con mayúsculas primero
            try:
                return PrioridadTarea[v.upper()]
            except KeyError:
                # Si falla, intenta como valor (minúsculas)
                for enum_member in PrioridadTarea:
                    if enum_member.value == v.lower():
                        return enum_member
        return v
    
    @field_validator('fecha_limite')
    @classmethod
    def validar_fecha_limite(cls, v, info):
        if info.data.get('fecha_inicio_disponible'):
            if v <= info.data['fecha_inicio_disponible']:
                raise ValueError('La fecha límite debe ser posterior a la fecha de inicio disponible')
        return v
    
    @field_validator('tags')
    @classmethod
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


class TareaCreateRequest(BaseModel):
    """
    Schema para crear una tarea vía API (formulario frontend).
    
    Campos requeridos:
    - titulo: Nombre de la tarea
    - fecha_limite: Cuándo vence la tarea
    
    Campos opcionales con defaults sensatos:
    - descripcion: Descripción (default: vacío)
    - puntos_max: Puntuación máxima (default: 100)
    - tipo: Tipo de tarea como "ejercicios", "ensayo", etc (default: "ejercicios")
    - prioridad: Nivel de urgencia (default: "media")
    """
    titulo: str = Field(..., min_length=1, max_length=200, description="Título de la tarea")
    fecha_limite: datetime = Field(..., description="Fecha y hora límite de entrega (ISO 8601)")
    descripcion: Optional[str] = Field(default="", max_length=5000, description="Descripción detallada de la tarea")
    puntos_max: float = Field(default=100, ge=1, le=1000, description="Puntuación máxima de la tarea")
    tipo: Optional[str] = Field(default="ejercicios", max_length=13, description="Tipo de tarea (ejercicios, ensayo, proyecto, etc)")
    prioridad: Optional[PrioridadTarea] = Field(default=PrioridadTarea.MEDIA, description="Nivel de prioridad")


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
    tipo: Optional[str] = Field(None, max_length=13)  # Campo real en BD (VARCHAR(13))
    prioridad: Optional[PrioridadTarea] = None
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
    
    model_config = ConfigDict(from_attributes=True, use_enum_values=True)
    
    @field_validator('estado', mode='before')
    @classmethod
    def normalize_estado_tarea(cls, v):
        """Normaliza estado de tarea - acepta enums de SQLAlchemy, strings, etc."""
        # Si ya es un enum, retorna directamente
        if isinstance(v, EstadoTarea):
            return v
        # Si es string, busca el enum por valor (case-insensitive)
        if isinstance(v, str):
            v_lower = v.lower()
            for enum_member in EstadoTarea:
                if enum_member.value == v_lower:
                    return enum_member
            # Si no encuentra por valor, intenta por nombre
            try:
                return EstadoTarea[v.upper()]
            except KeyError:
                pass
        return v
    
    @field_validator('estado', mode='before')
    @classmethod
    def normalizar_estado_tarea(cls, v):
        """Normaliza estado de tarea a enum válido."""
        if v is None:
            return EstadoTarea.ASIGNADA
        if isinstance(v, EstadoTarea):
            return v
        if isinstance(v, str):
            try:
                return EstadoTarea[v.upper()]
            except KeyError:
                for enum_member in EstadoTarea:
                    if enum_member.value == v.lower():
                        return enum_member
        return v

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
    model_config = ConfigDict(use_enum_values=True)
    
    titulo_entrega: Optional[str] = None
    descripcion_entrega: Optional[str] = None
    comentarios_estudiante: Optional[str] = None
    archivo_url: Optional[str] = None
    archivos_adicionales: Optional[List[Dict[str, Any]]] = None
    contenido_texto: Optional[str] = None
    enlaces_externos: Optional[List[Dict[str, str]]] = None
    google_resources: Optional[List[Dict[str, Any]]] = None  # Recursos Google Workspace
    tiempo_empleado: Optional[int] = None
    dificultad_percibida: Optional[int] = Field(None, ge=1, le=5)
    satisfaccion_estudiante: Optional[int] = Field(None, ge=1, le=5)

class EntregaTareaCreate(EntregaTareaBase):
    tarea_id: str
    estudiante_id: str

class EntregaTareaUpdate(EntregaTareaBase):
    estado: Optional[EstadoEntrega] = None
    es_final: Optional[bool] = None
    
    @field_validator('estado', mode='before')
    @classmethod
    def normalize_estado_update(cls, v):
        """Normaliza estado de entrega - acepta enums de SQLAlchemy, strings, etc."""
        if v is None:
            return v
        # Si ya es un enum, retorna directamente
        if isinstance(v, EstadoEntrega):
            return v
        # Si es string, busca el enum por valor (case-insensitive)
        if isinstance(v, str):
            v_lower = v.lower()
            for enum_member in EstadoEntrega:
                if enum_member.value == v_lower:
                    return enum_member
            # Si no encuentra por valor, intenta por nombre
            try:
                return EstadoEntrega[v.upper()]
            except KeyError:
                pass
        return v

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
    estudiante_nombre: Optional[str] = None
    estudiante_apellido: Optional[str] = None
    estudiante_email: Optional[str] = None
    fecha_entrega: Optional[datetime] = None
    fecha_limite_original: Optional[datetime] = None
    numero_intento: Optional[int] = 1
    es_entrega_tardia: Optional[bool] = False
    calificacion: Optional[float] = None
    calificacion_letras: Optional[str] = None
    comentarios_docente: Optional[str] = None
    rubrica_calificacion: Optional[Dict[str, Any]] = None
    estado: EstadoEntrega
    es_final: Optional[bool] = False
    requiere_revision: Optional[bool] = False
    fecha_creacion: datetime
    fecha_actualizacion: Optional[datetime] = None
    calificado_por: Optional[str] = None
    fecha_calificacion: Optional[datetime] = None
    
    # Field validators
    @field_validator('calificado_por', mode='before')
    @classmethod
    def convert_calificado_por_to_str(cls, v):
        """Convert UUID to string if needed."""
        if v is None:
            return None
        return str(v)
    
    # Propiedades calculadas
    dias_desde_entrega: Optional[int] = 0
    porcentaje_calificacion: Optional[float] = 0.0

    @field_validator('archivos_adicionales', mode='before')
    @classmethod
    def normalize_archivos_adicionales(cls, v):
        """Extrae la lista de archivos si viene envuelta en un dict."""
        if isinstance(v, dict) and "archivos" in v:
            return v["archivos"]
        return v

    @field_validator('entrega_id', 'tarea_id', 'estudiante_id', mode='before')
    @classmethod
    def normalize_uuids(cls, v):
        """Convierte UUIDs a string."""
        if v is None:
            return None
        return str(v)
    
    model_config = ConfigDict(from_attributes=True, use_enum_values=True)
    
    @field_validator('estado', mode='before')
    @classmethod
    def normalize_estado_entrega(cls, v):
        """Normaliza estado de entrega - acepta enums de SQLAlchemy, strings, etc."""
        if v is None:
            return EstadoEntrega.BORRADOR
        # Si ya es un enum, retorna directamente
        if isinstance(v, EstadoEntrega):
            return v
        # Si es string, busca el enum por valor (case-insensitive)
        if isinstance(v, str):
            v_lower = v.lower()
            for enum_member in EstadoEntrega:
                if enum_member.value == v_lower:
                    return enum_member
            # Si no encuentra por valor, intenta por nombre
            try:
                return EstadoEntrega[v.upper()]
            except KeyError:
                pass
        # Si no se puede mapear, retornar BORRADOR por defecto para evitar crash
        return EstadoEntrega.BORRADOR

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
    
    model_config = ConfigDict(from_attributes=True)

class RubricaDetallada(RubricaResponse):
    # Información del creador
    creador_nombre: Optional[str] = None
    creador_apellido: Optional[str] = None
    
    # Estadísticas de uso
    veces_utilizada: Optional[int] = 0
    tareas_asociadas: Optional[int] = 0

# Schemas para filtros y búsquedas
class FiltrosTarea(BaseModel):
    model_config = ConfigDict(use_enum_values=True)
    
    grupo_id: Optional[str] = None
    docente_id: Optional[str] = None
    tipo: Optional[str] = Field(None, max_length=13)  # Campo real en BD (VARCHAR(13))
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