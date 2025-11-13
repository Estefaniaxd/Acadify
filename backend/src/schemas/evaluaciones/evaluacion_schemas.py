"""
Schemas Pydantic para el sistema completo de evaluaciones.
Validación de datos para evaluaciones, preguntas, intentos y respuestas.
"""
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, validator, root_validator
from datetime import datetime
from uuid import UUID

from src.models.evaluaciones.evaluacion_expandida import (
    TipoEvaluacion, VisibilidadEvaluacion, ModoEvaluacion,
    TipoCalificacion, EstadoEvaluacion,
    TipoPreguntaExpandido as TipoPregunta,
)
from src.models.evaluaciones.intento_respuesta_gamificacion import (
    EstadoIntento,
    NivelRiesgoIntento as NivelRiesgo,
)

# DificultadPregunta es un string simple, no un enum
# Valores: muy_facil, facil, medio, dificil, muy_dificil


# ==========================================
# SCHEMAS DE EVALUACIÓN
# ==========================================

class EvaluacionBase(BaseModel):
    """Base para evaluaciones"""
    titulo: str = Field(..., min_length=3, max_length=200)
    descripcion: Optional[str] = Field(None, max_length=2000)
    instrucciones: Optional[str] = Field(None, max_length=5000)
    
    tipo_evaluacion: TipoEvaluacion = Field(TipoEvaluacion.EVALUACION)
    visibilidad: VisibilidadEvaluacion = Field(VisibilidadEvaluacion.CURSO)
    modo_evaluacion: ModoEvaluacion = Field(ModoEvaluacion.STANDARD)
    
    categoria: Optional[str] = Field(None, max_length=100)
    etiquetas: Optional[List[str]] = Field(default_factory=list)
    
    # Tiempo
    tiempo_limite_minutos: Optional[int] = Field(None, ge=1, le=1440, description="null = sin límite")
    fecha_apertura: Optional[datetime] = None
    fecha_cierre: Optional[datetime] = None
    permitir_pausar: bool = True
    
    # Configuración de preguntas
    total_preguntas: int = Field(..., ge=1, le=500)
    num_preguntas_mostrar: Optional[int] = Field(None, ge=1, description="null = todas")
    randomizar_preguntas: bool = False
    randomizar_opciones: bool = False
    una_pregunta_por_vez: bool = False
    permitir_navegar_atras: bool = True
    
    # Intentos
    max_intentos: int = Field(1, ge=1, le=100)
    
    # Acceso
    requiere_codigo_acceso: bool = False
    codigo_acceso: Optional[str] = Field(None, max_length=20)
    requiere_contrasena: bool = False
    contrasena: Optional[str] = Field(None, max_length=100)
    
    # Calificación
    tipo_calificacion: TipoCalificacion = Field(TipoCalificacion.AUTOMATICA)
    usar_ia_calificacion: bool = False
    puntuacion_total: float = Field(..., ge=0)
    puntuacion_minima_aprobacion: Optional[float] = Field(None, ge=0)
    permitir_puntuacion_parcial: bool = True
    penalizacion_respuesta_incorrecta: float = Field(0.0, ge=0.0, le=100.0)
    rubrica_ia: Optional[Dict[str, Any]] = None
    generar_feedback_ia: bool = False
    
    # Resultados
    mostrar_resultados_inmediatos: bool = True
    mostrar_respuestas_correctas: bool = True
    mostrar_puntuacion: bool = True
    mostrar_feedback: bool = True
    fecha_publicacion_resultados: Optional[datetime] = None
    
    # Pantalla completa
    requiere_pantalla_completa: bool = False
    
    # Anti-trampa (referencia o configuración rápida)
    configuracion_antitrampa_id: Optional[UUID] = None
    detectar_cambio_pestana: bool = False
    max_cambios_pestana: Optional[int] = Field(5, ge=0, le=100)
    
    # Multimedia
    requerir_camara: bool = False
    grabar_camara_continuo: bool = False
    captura_periodica_webcam: bool = False
    intervalo_captura_minutos: Optional[int] = Field(5, ge=1, le=60)
    verificar_identidad_facial: bool = False
    monitorear_identidad_continuo: bool = False
    requerir_audio: bool = False
    grabar_audio_continuo: bool = False
    
    # Gamificación
    otorga_puntos: bool = False
    puntos_base: int = Field(0, ge=0, le=10000)
    puntos_por_acierto: int = Field(0, ge=0, le=1000)
    multiplicador_puntos: float = Field(1.0, ge=0.1, le=10.0)
    otorga_insignia: bool = False
    insignia_id: Optional[UUID] = None
    incluir_en_ranking: bool = False
    mostrar_ranking_tiempo_real: bool = False
    
    # Innovaciones
    es_adaptativa: bool = False
    es_colaborativa: bool = False
    max_miembros_equipo: Optional[int] = Field(4, ge=2, le=10)
    permitir_peer_review: bool = False
    num_revisiones_requeridas: Optional[int] = Field(2, ge=1, le=10)
    
    @validator('num_preguntas_mostrar')
    def validar_num_preguntas(cls, v, values):
        if v and 'total_preguntas' in values and v > values['total_preguntas']:
            raise ValueError('num_preguntas_mostrar no puede ser mayor que total_preguntas')
        return v
    
    @validator('puntuacion_minima_aprobacion')
    def validar_puntuacion_minima(cls, v, values):
        if v and 'puntuacion_total' in values and v > values['puntuacion_total']:
            raise ValueError('puntuacion_minima_aprobacion no puede ser mayor que puntuacion_total')
        return v
    
    @validator('fecha_cierre')
    def validar_fechas(cls, v, values):
        if v and 'fecha_apertura' in values and values['fecha_apertura']:
            if v <= values['fecha_apertura']:
                raise ValueError('fecha_cierre debe ser posterior a fecha_apertura')
        return v
    
    class Config:
        use_enum_values = True
        schema_extra = {
            "example": {
                "titulo": "Examen Final de Python",
                "descripcion": "Evaluación integral de conceptos avanzados",
                "tipo_evaluacion": "examen_final",
                "visibilidad": "curso",
                "tiempo_limite_minutos": 120,
                "total_preguntas": 50,
                "max_intentos": 1,
                "puntuacion_total": 100,
                "usar_ia_calificacion": True,
                "requerir_camara": True,
                "otorga_puntos": False
            }
        }


class EvaluacionCreate(EvaluacionBase):
    """Schema para crear evaluación"""
    curso_id: Optional[UUID] = None
    institucion_id: Optional[UUID] = None


class EvaluacionUpdate(BaseModel):
    """Schema para actualizar evaluación - todos campos opcionales"""
    titulo: Optional[str] = Field(None, min_length=3, max_length=200)
    descripcion: Optional[str] = None
    instrucciones: Optional[str] = None
    estado_evaluacion: Optional[EstadoEvaluacion] = None
    
    tiempo_limite_minutos: Optional[int] = None
    fecha_apertura: Optional[datetime] = None
    fecha_cierre: Optional[datetime] = None
    
    max_intentos: Optional[int] = None
    
    tipo_calificacion: Optional[TipoCalificacion] = None
    usar_ia_calificacion: Optional[bool] = None
    puntuacion_total: Optional[float] = None
    puntuacion_minima_aprobacion: Optional[float] = None
    
    mostrar_resultados_inmediatos: Optional[bool] = None
    
    requerir_camara: Optional[bool] = None
    grabar_camara_continuo: Optional[bool] = None
    verificar_identidad_facial: Optional[bool] = None
    
    otorga_puntos: Optional[bool] = None
    puntos_base: Optional[int] = None
    puntos_por_acierto: Optional[int] = None
    
    class Config:
        use_enum_values = True


class EvaluacionResponse(EvaluacionBase):
    """Schema de respuesta de evaluación"""
    id: UUID
    estado_evaluacion: EstadoEvaluacion
    
    curso_id: Optional[UUID]
    institucion_id: Optional[UUID]
    creado_por_id: UUID
    
    # Estadísticas
    total_intentos: int
    total_completados: int
    tasa_aprobacion: float
    tasa_completacion: float
    calificacion_promedio: Optional[float]
    calificacion_mediana: Optional[float]
    tiempo_promedio_minutos: Optional[float]
    
    fecha_creacion: datetime
    fecha_modificacion: datetime
    
    class Config:
        from_attributes = True
        use_enum_values = True


# ==========================================
# SCHEMAS DE PREGUNTA
# ==========================================

class PreguntaBase(BaseModel):
    """Base para preguntas"""
    titulo: str = Field(..., min_length=3, max_length=500)
    enunciado: str = Field(..., min_length=5, max_length=5000)
    tipo_pregunta: TipoPregunta
    dificultad: str = Field("medio")
    
    opciones_respuesta: Optional[Dict[str, Any]] = None
    respuesta_correcta: Optional[Any] = None
    respuestas_alternativas: Optional[List[Any]] = None
    
    explicacion: Optional[str] = Field(None, max_length=2000)
    puntuacion: float = Field(..., ge=0, le=100)
    puntos_respuesta_parcial: float = Field(0.0, ge=0.0, le=1.0)
    
    es_obligatoria: bool = True
    tiempo_limite_segundos: Optional[int] = Field(None, ge=10, le=3600)
    
    # Media
    imagen_url: Optional[str] = None
    audio_url: Optional[str] = None
    video_url: Optional[str] = None
    archivos_adjuntos: Optional[List[str]] = None
    
    # Para código
    lenguaje_codigo: Optional[str] = None
    plantilla_codigo: Optional[str] = None
    tests_unitarios: Optional[List[Dict[str, Any]]] = None
    
    # Para LaTeX
    formula_latex: Optional[str] = None
    
    # Para interactivos
    configuracion_interactiva: Optional[Dict[str, Any]] = None
    
    etiquetas: Optional[List[str]] = None
    
    class Config:
        use_enum_values = True
        schema_extra = {
            "example": {
                "titulo": "¿Qué es una función lambda?",
                "enunciado": "Explica el concepto de función lambda en Python y proporciona un ejemplo",
                "tipo_pregunta": "ensayo",
                "dificultad": "media",
                "puntuacion": 10.0,
                "explicacion": "Las funciones lambda son funciones anónimas de una sola línea"
            }
        }


class PreguntaCreate(PreguntaBase):
    """Schema para crear pregunta"""
    evaluacion_id: UUID
    banco_pregunta_id: Optional[UUID] = None
    orden: Optional[int] = None


class PreguntaUpdate(BaseModel):
    """Schema para actualizar pregunta"""
    titulo: Optional[str] = None
    enunciado: Optional[str] = None
    opciones_respuesta: Optional[Dict[str, Any]] = None
    respuesta_correcta: Optional[Any] = None
    explicacion: Optional[str] = None
    puntuacion: Optional[float] = None
    dificultad: Optional[str] = None
    orden: Optional[int] = None
    
    class Config:
        use_enum_values = True


class PreguntaResponse(PreguntaBase):
    """Schema de respuesta de pregunta"""
    id: UUID
    evaluacion_id: UUID
    orden: int
    
    # Estadísticas (solo para profesores)
    veces_utilizada: int
    promedio_aciertos: Optional[float]
    tiempo_promedio_respuesta: Optional[float]
    
    fecha_creacion: datetime
    fecha_modificacion: datetime
    
    class Config:
        from_attributes = True
        use_enum_values = True


class PreguntaEstudianteResponse(BaseModel):
    """Schema de pregunta para estudiantes (sin respuesta correcta)"""
    id: UUID
    titulo: str
    enunciado: str
    tipo_pregunta: TipoPregunta
    opciones_respuesta: Optional[Dict[str, Any]]
    puntuacion: float
    es_obligatoria: bool
    tiempo_limite_segundos: Optional[int]
    orden: int
    
    imagen_url: Optional[str]
    audio_url: Optional[str]
    video_url: Optional[str]
    
    lenguaje_codigo: Optional[str]
    plantilla_codigo: Optional[str]
    formula_latex: Optional[str]
    configuracion_interactiva: Optional[Dict[str, Any]]
    
    class Config:
        from_attributes = True
        use_enum_values = True


# ==========================================
# SCHEMAS DE INTENTO
# ==========================================

class IniciarIntentoRequest(BaseModel):
    """Request para iniciar un intento"""
    evaluacion_id: UUID
    codigo_acceso: Optional[str] = None
    contrasena: Optional[str] = None
    equipo_ids: Optional[List[UUID]] = None  # Para colaborativas
    ip_address: Optional[str] = None  # Detectado automáticamente
    user_agent: Optional[str] = None  # Detectado automáticamente
    
    class Config:
        schema_extra = {
            "example": {
                "evaluacion_id": "123e4567-e89b-12d3-a456-426614174000",
                "codigo_acceso": "EXAM2024"
            }
        }


class IntentoResponse(BaseModel):
    """Schema de respuesta de intento"""
    id: UUID
    evaluacion_id: UUID
    estudiante_id: UUID
    numero_intento: int
    estado_intento: EstadoIntento
    
    fecha_inicio: datetime
    fecha_fin: Optional[datetime]
    tiempo_total_segundos: Optional[int]
    tiempo_activo_segundos: Optional[int]
    tiempo_pausado_segundos: Optional[int]
    
    progreso_actual: int
    total_preguntas: int
    preguntas_respondidas: int
    pregunta_actual_orden: Optional[int]
    
    # Calificación
    puntuacion_obtenida: Optional[float]
    puntuacion_maxima: float
    porcentaje: Optional[float]
    aprobado: Optional[bool]
    requiere_revision_manual: bool
    
    # Anti-trampa
    nivel_riesgo: NivelRiesgo
    puntuacion_riesgo: float
    total_eventos_antitrampa: int
    detecciones_ia: int
    detecciones_plagio: int
    
    # Multimedia
    total_capturas_webcam: int
    capturas_con_anomalias: int
    verificacion_identidad_exitosa: Optional[bool]
    
    # Gamificación
    puntos_ganados: int
    multiplicador_aplicado: float
    insignias_ganadas: List[str]
    posicion_ranking: Optional[int]
    
    # Adaptativa
    dificultad_actual: Optional[str]
    
    orden_preguntas: List[int]
    
    class Config:
        from_attributes = True
        use_enum_values = True


class IntentoDetalladoResponse(IntentoResponse):
    """Respuesta detallada con preguntas y respuestas"""
    preguntas: List[PreguntaEstudianteResponse]
    respuestas: List[Dict[str, Any]]
    feedback_ia: Optional[str]
    recomendaciones_ia: Optional[List[str]]
    
    class Config:
        from_attributes = True


# ==========================================
# SCHEMAS DE RESPUESTA
# ==========================================

class ResponderPreguntaRequest(BaseModel):
    """Request para responder una pregunta"""
    intento_id: UUID
    pregunta_id: UUID
    respuesta: Any = Field(..., description="Puede ser string, int, list, dict según el tipo")
    tiempo_respuesta_segundos: int = Field(..., ge=0)
    
    # Para preguntas de código
    codigo_ejecutado: Optional[str] = None
    resultado_ejecucion: Optional[Dict[str, Any]] = None
    
    # Para multimedia
    audio_url: Optional[str] = None
    video_url: Optional[str] = None
    archivo_url: Optional[str] = None
    
    class Config:
        schema_extra = {
            "example": {
                "intento_id": "123e4567-e89b-12d3-a456-426614174000",
                "pregunta_id": "223e4567-e89b-12d3-a456-426614174000",
                "respuesta": "B",
                "tiempo_respuesta_segundos": 45
            }
        }


class RespuestaResponse(BaseModel):
    """Schema de respuesta guardada"""
    id: UUID
    intento_id: UUID
    pregunta_id: UUID
    respuesta_estudiante: Any
    tiempo_respuesta_segundos: int
    
    es_correcta: Optional[bool]
    puntuacion_obtenida: Optional[float]
    puntuacion_maxima: float
    
    feedback: Optional[str]
    feedback_ia: Optional[str]
    explicacion: Optional[str]
    
    # Análisis
    fue_detectada_ia: bool
    probabilidad_ia: Optional[float]
    fue_detectado_plagio: bool
    similitud_plagio: Optional[float]
    
    requiere_revision_manual: bool
    revisado_por_id: Optional[UUID]
    fecha_revision: Optional[datetime]
    
    fecha_respuesta: datetime
    
    class Config:
        from_attributes = True


# ==========================================
# SCHEMAS DE ACCIONES
# ==========================================

class PausarIntentoRequest(BaseModel):
    """Request para pausar intento"""
    intento_id: UUID
    motivo: Optional[str] = None


class ReanudarIntentoRequest(BaseModel):
    """Request para reanudar intento"""
    intento_id: UUID


class FinalizarIntentoRequest(BaseModel):
    """Request para finalizar intento"""
    intento_id: UUID
    forzar: bool = Field(False, description="Forzar finalización aunque falten preguntas")


class CalificarManualmenteRequest(BaseModel):
    """Request para calificación manual"""
    respuesta_id: UUID
    puntuacion: float = Field(..., ge=0)
    feedback: Optional[str] = None


# ==========================================
# SCHEMAS DE ESTADÍSTICAS
# ==========================================

class EstadisticasEvaluacionResponse(BaseModel):
    """Estadísticas completas de una evaluación"""
    evaluacion_id: UUID
    total_intentos: int
    total_completados: int
    total_en_progreso: int
    total_abandonados: int
    
    tasa_aprobacion: float
    tasa_completacion: float
    
    calificacion_promedio: float
    calificacion_mediana: float
    calificacion_minima: float
    calificacion_maxima: float
    desviacion_estandar: float
    
    tiempo_promedio_minutos: float
    tiempo_minimo_minutos: float
    tiempo_maximo_minutos: float
    
    distribucion_calificaciones: Dict[str, int]  # {"0-20": 5, "20-40": 10, ...}
    
    preguntas_mas_dificiles: List[Dict[str, Any]]
    preguntas_mas_faciles: List[Dict[str, Any]]
    
    # Anti-trampa
    total_eventos_sospechosos: int
    intentos_con_riesgo_alto: int
    detecciones_ia_total: int
    detecciones_plagio_total: int
    
    # Insights IA
    insights_ia: Optional[List[str]]
    recomendaciones_mejora: Optional[List[str]]


class EstadisticasEstudianteResponse(BaseModel):
    """Estadísticas de un estudiante en una evaluación"""
    estudiante_id: UUID
    evaluacion_id: UUID
    
    total_intentos: int
    mejor_intento: Optional[IntentoResponse]
    ultimo_intento: Optional[IntentoResponse]
    
    promedio_calificacion: float
    tendencia: str  # "mejorando", "empeorando", "estable"
    
    tiempo_promedio_minutos: float
    velocidad_respuesta: str  # "rápida", "normal", "lenta"
    
    fortalezas: List[str]  # Temas donde va bien
    debilidades: List[str]  # Temas a mejorar
    
    recomendaciones_ia: List[str]


# ==========================================
# SCHEMAS DE FILTROS
# ==========================================

class EvaluacionFiltros(BaseModel):
    """Filtros para listar evaluaciones"""
    tipo_evaluacion: Optional[TipoEvaluacion] = None
    estado_evaluacion: Optional[EstadoEvaluacion] = None
    visibilidad: Optional[VisibilidadEvaluacion] = None
    curso_id: Optional[UUID] = None
    institucion_id: Optional[UUID] = None
    creado_por_id: Optional[UUID] = None
    busqueda: Optional[str] = None
    categoria: Optional[str] = None
    etiquetas: Optional[List[str]] = None
    otorga_puntos: Optional[bool] = None
    
    skip: int = Field(0, ge=0)
    limit: int = Field(20, ge=1, le=100)
    orden: str = Field("fecha_creacion", pattern="^(fecha_creacion|titulo|total_intentos|calificacion_promedio)$")
    descendente: bool = True
    
    class Config:
        use_enum_values = True


# ==========================================
# SCHEMAS DE MONITOREO EN TIEMPO REAL
# ==========================================

class MonitoreoEnVivoResponse(BaseModel):
    """Estado en tiempo real de estudiantes tomando evaluación"""
    evaluacion_id: UUID
    total_estudiantes_activos: int
    
    estudiantes: List[Dict[str, Any]]  # Lista con info de cada estudiante
    # {
    #   "estudiante_id": UUID,
    #   "nombre": str,
    #   "progreso": int (0-100),
    #   "tiempo_transcurrido": int (minutos),
    #   "nivel_riesgo": str,
    #   "ultima_actividad": datetime,
    #   "eventos_sospechosos": int,
    #   "captura_actual_url": Optional[str]
    # }
    
    alertas_activas: List[Dict[str, Any]]
    timestamp: datetime
