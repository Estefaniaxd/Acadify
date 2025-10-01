"""
Schemas Pydantic para el sistema de evaluaciones
"""

from pydantic import BaseModel, Field, validator
from typing import List, Dict, Any, Optional, Union
from datetime import datetime
from enum import Enum

from src.models.evaluaciones import (
    TipoExamen, EstadoExamen, TipoPregunta, DificultadPregunta, EstadoIntento
)


# === SCHEMAS BASE ===
class ExamenBase(BaseModel):
    titulo: str = Field(..., min_length=1, max_length=200, description="Título del examen")
    descripcion: Optional[str] = Field(None, description="Descripción detallada del examen")
    tipo_examen: TipoExamen = Field(default=TipoExamen.EVALUACION, description="Tipo de examen")
    duracion_minutos: int = Field(default=60, ge=1, le=1440, description="Duración en minutos (máx 24 horas)")
    fecha_inicio: Optional[datetime] = Field(None, description="Fecha y hora de inicio disponible")
    fecha_fin: Optional[datetime] = Field(None, description="Fecha y hora de fin disponible")
    intentos_permitidos: int = Field(default=1, ge=1, le=10, description="Número máximo de intentos")
    requiere_contraseña: bool = Field(default=False, description="Si requiere contraseña de acceso")
    contraseña_acceso: Optional[str] = Field(None, min_length=4, max_length=100, description="Contraseña de acceso")
    randomizar_preguntas: bool = Field(default=False, description="Aleatorizar orden de preguntas")
    mostrar_resultados_inmediatos: bool = Field(default=True, description="Mostrar resultados al terminar")
    permitir_revision: bool = Field(default=True, description="Permitir revisar respuestas después")
    mostrar_respuestas_correctas: bool = Field(default=True, description="Mostrar respuestas correctas")
    modo_pantalla_completa: bool = Field(default=False, description="Forzar modo pantalla completa")
    bloquear_navegacion: bool = Field(default=False, description="Bloquear navegación del navegador")
    detectar_cambio_pestana: bool = Field(default=False, description="Detectar cambios de pestaña")
    tiempo_maximo_inactividad: int = Field(default=300, ge=60, le=3600, description="Tiempo máx inactividad (seg)")
    puntuacion_total: float = Field(default=100.0, gt=0, description="Puntuación total del examen")
    puntuacion_minima_aprobacion: float = Field(default=60.0, ge=0, description="Puntuación mínima para aprobar")
    calificacion_automatica: bool = Field(default=True, description="Usar calificación automática")
    curso_id: Optional[str] = Field(None, description="ID del curso asociado")
    grupo_id: Optional[str] = Field(None, description="ID del grupo asociado")
    configuracion_avanzada: Optional[Dict[str, Any]] = Field(None, description="Configuraciones adicionales")
    instrucciones: Optional[str] = Field(None, description="Instrucciones específicas")

    @validator('fecha_fin')
    def fecha_fin_posterior_a_inicio(cls, v, values):
        if v and 'fecha_inicio' in values and values['fecha_inicio']:
            if v <= values['fecha_inicio']:
                raise ValueError('La fecha de fin debe ser posterior a la fecha de inicio')
        return v

    @validator('contraseña_acceso')
    def validar_contraseña_si_requerida(cls, v, values):
        if values.get('requiere_contraseña', False) and not v:
            raise ValueError('Debe proporcionar una contraseña si está habilitada')
        return v


class ExamenCreate(ExamenBase):
    creado_por: str = Field(..., description="ID del usuario creador")


class ExamenUpdate(BaseModel):
    titulo: Optional[str] = Field(None, min_length=1, max_length=200)
    descripcion: Optional[str] = None
    tipo_examen: Optional[TipoExamen] = None
    estado: Optional[EstadoExamen] = None
    duracion_minutos: Optional[int] = Field(None, ge=1, le=1440)
    fecha_inicio: Optional[datetime] = None
    fecha_fin: Optional[datetime] = None
    intentos_permitidos: Optional[int] = Field(None, ge=1, le=10)
    requiere_contraseña: Optional[bool] = None
    contraseña_acceso: Optional[str] = Field(None, min_length=4, max_length=100)
    randomizar_preguntas: Optional[bool] = None
    mostrar_resultados_inmediatos: Optional[bool] = None
    permitir_revision: Optional[bool] = None
    mostrar_respuestas_correctas: Optional[bool] = None
    modo_pantalla_completa: Optional[bool] = None
    bloquear_navegacion: Optional[bool] = None
    detectar_cambio_pestana: Optional[bool] = None
    tiempo_maximo_inactividad: Optional[int] = Field(None, ge=60, le=3600)
    puntuacion_total: Optional[float] = Field(None, gt=0)
    puntuacion_minima_aprobacion: Optional[float] = Field(None, ge=0)
    calificacion_automatica: Optional[bool] = None
    curso_id: Optional[str] = None
    grupo_id: Optional[str] = None
    configuracion_avanzada: Optional[Dict[str, Any]] = None
    instrucciones: Optional[str] = None


class ExamenResponse(ExamenBase):
    examen_id: str
    estado: EstadoExamen
    creado_por: str
    fecha_creacion: datetime
    fecha_actualizacion: Optional[datetime]
    total_preguntas: int
    total_intentos: int
    promedio_calificacion: Optional[float]

    class Config:
        from_attributes = True


# === SCHEMAS DE PREGUNTA ===
class PreguntaExamenBase(BaseModel):
    titulo: str = Field(..., min_length=1, description="Texto de la pregunta")
    descripcion: Optional[str] = Field(None, description="Contexto adicional")
    tipo_pregunta: TipoPregunta = Field(..., description="Tipo de pregunta")
    orden: int = Field(..., ge=1, description="Orden en el examen")
    puntuacion: float = Field(default=1.0, gt=0, description="Puntos que vale la pregunta")
    es_obligatoria: bool = Field(default=True, description="Si es obligatorio responder")
    tiempo_limite_segundos: Optional[int] = Field(None, ge=10, le=3600, description="Tiempo límite específico")
    opciones_respuesta: Optional[Dict[str, Any]] = Field(None, description="Opciones de respuesta")
    respuesta_correcta: Optional[Dict[str, Any]] = Field(None, description="Respuesta(s) correcta(s)")
    explicacion: Optional[str] = Field(None, description="Explicación de la respuesta")
    puntos_respuesta_parcial: bool = Field(default=False, description="Permitir puntuación parcial")
    dificultad: DificultadPregunta = Field(default=DificultadPregunta.MEDIO, description="Nivel de dificultad")
    imagen_url: Optional[str] = Field(None, description="URL de imagen asociada")
    audio_url: Optional[str] = Field(None, description="URL de audio asociado")
    video_url: Optional[str] = Field(None, description="URL de video asociado")
    archivos_adjuntos: Optional[Dict[str, Any]] = Field(None, description="Archivos adjuntos")
    tags: Optional[List[str]] = Field(None, description="Etiquetas de la pregunta")

    @validator('opciones_respuesta')
    def validar_opciones_respuesta(cls, v, values):
        tipo_pregunta = values.get('tipo_pregunta')
        if tipo_pregunta == TipoPregunta.OPCION_MULTIPLE:
            if not v or not isinstance(v, dict) or 'opciones' not in v:
                raise ValueError('Las preguntas de opción múltiple deben tener opciones definidas')
            if len(v['opciones']) < 2:
                raise ValueError('Debe haber al menos 2 opciones')
        elif tipo_pregunta == TipoPregunta.VERDADERO_FALSO:
            if not v:
                v = {'opciones': ['Verdadero', 'Falso']}
        return v

    @validator('respuesta_correcta')
    def validar_respuesta_correcta(cls, v, values):
        tipo_pregunta = values.get('tipo_pregunta')
        if tipo_pregunta in [TipoPregunta.OPCION_MULTIPLE, TipoPregunta.VERDADERO_FALSO]:
            if not v:
                raise ValueError('Debe especificar la respuesta correcta')
        return v


class PreguntaExamenCreate(PreguntaExamenBase):
    examen_id: str = Field(..., description="ID del examen")
    banco_pregunta_id: Optional[str] = Field(None, description="ID de pregunta del banco si aplica")


class PreguntaExamenUpdate(BaseModel):
    titulo: Optional[str] = Field(None, min_length=1)
    descripcion: Optional[str] = None
    tipo_pregunta: Optional[TipoPregunta] = None
    orden: Optional[int] = Field(None, ge=1)
    puntuacion: Optional[float] = Field(None, gt=0)
    es_obligatoria: Optional[bool] = None
    tiempo_limite_segundos: Optional[int] = Field(None, ge=10, le=3600)
    opciones_respuesta: Optional[Dict[str, Any]] = None
    respuesta_correcta: Optional[Dict[str, Any]] = None
    explicacion: Optional[str] = None
    puntos_respuesta_parcial: Optional[bool] = None
    dificultad: Optional[DificultadPregunta] = None
    imagen_url: Optional[str] = None
    audio_url: Optional[str] = None
    video_url: Optional[str] = None
    archivos_adjuntos: Optional[Dict[str, Any]] = None
    tags: Optional[List[str]] = None


class PreguntaExamenResponse(PreguntaExamenBase):
    pregunta_id: str
    examen_id: str
    banco_pregunta_id: Optional[str]
    fecha_creacion: datetime
    fecha_actualizacion: Optional[datetime]
    veces_utilizada: int
    promedio_aciertos: Optional[float]
    tiempo_promedio_respuesta: Optional[float]

    class Config:
        from_attributes = True


# === SCHEMAS DE BANCO DE PREGUNTAS ===
class BancoPreguntaBase(BaseModel):
    titulo: str = Field(..., min_length=1, description="Texto de la pregunta")
    descripcion: Optional[str] = Field(None, description="Descripción adicional")
    tipo_pregunta: TipoPregunta = Field(..., description="Tipo de pregunta")
    dificultad: DificultadPregunta = Field(default=DificultadPregunta.MEDIO)
    materia: Optional[str] = Field(None, max_length=100, description="Área de conocimiento")
    tema: Optional[str] = Field(None, max_length=200, description="Tema específico")
    subtema: Optional[str] = Field(None, max_length=200, description="Subtema")
    opciones_respuesta: Optional[Dict[str, Any]] = None
    respuesta_correcta: Optional[Dict[str, Any]] = None
    explicacion: Optional[str] = None
    imagen_url: Optional[str] = None
    audio_url: Optional[str] = None
    video_url: Optional[str] = None
    archivos_adjuntos: Optional[Dict[str, Any]] = None
    es_publica: bool = Field(default=False, description="Disponible para otros profesores")
    tags: Optional[List[str]] = None
    categoria: Optional[str] = Field(None, max_length=100)
    nivel_educativo: Optional[str] = Field(None, max_length=50)
    puntuacion_sugerida: float = Field(default=1.0, gt=0)
    tiempo_estimado_segundos: Optional[int] = Field(None, ge=10, le=3600)


class BancoPreguntaCreate(BancoPreguntaBase):
    creado_por: str = Field(..., description="ID del usuario creador")
    institucion_id: Optional[str] = Field(None, description="ID de la institución")


class BancoPreguntaUpdate(BaseModel):
    titulo: Optional[str] = Field(None, min_length=1)
    descripcion: Optional[str] = None
    tipo_pregunta: Optional[TipoPregunta] = None
    dificultad: Optional[DificultadPregunta] = None
    materia: Optional[str] = Field(None, max_length=100)
    tema: Optional[str] = Field(None, max_length=200)
    subtema: Optional[str] = Field(None, max_length=200)
    opciones_respuesta: Optional[Dict[str, Any]] = None
    respuesta_correcta: Optional[Dict[str, Any]] = None
    explicacion: Optional[str] = None
    imagen_url: Optional[str] = None
    audio_url: Optional[str] = None
    video_url: Optional[str] = None
    archivos_adjuntos: Optional[Dict[str, Any]] = None
    es_publica: Optional[bool] = None
    tags: Optional[List[str]] = None
    categoria: Optional[str] = Field(None, max_length=100)
    nivel_educativo: Optional[str] = Field(None, max_length=50)
    puntuacion_sugerida: Optional[float] = Field(None, gt=0)
    tiempo_estimado_segundos: Optional[int] = Field(None, ge=10, le=3600)


class BancoPreguntaResponse(BancoPreguntaBase):
    pregunta_id: str
    creado_por: str
    institucion_id: Optional[str]
    fecha_creacion: datetime
    fecha_actualizacion: Optional[datetime]
    veces_utilizada: int
    promedio_aciertos: Optional[float]
    calificacion_dificultad: Optional[float]
    ultima_vez_utilizada: Optional[datetime]
    revisado_por: Optional[str]
    fecha_revision: Optional[datetime]
    estado_revision: str
    comentarios_revision: Optional[str]

    class Config:
        from_attributes = True


# === SCHEMAS DE INTENTO ===
class IntentoExamenBase(BaseModel):
    examen_id: str = Field(..., description="ID del examen")
    estudiante_id: str = Field(..., description="ID del estudiante")


class IntentoExamenCreate(IntentoExamenBase):
    pass


class IntentoExamenUpdate(BaseModel):
    estado: Optional[EstadoIntento] = None
    pregunta_actual: Optional[int] = Field(None, ge=1)
    eventos_sospechosos: Optional[Dict[str, Any]] = None
    cambios_pestana_detectados: Optional[int] = None
    tiempo_inactividad_total: Optional[int] = None


class IntentoExamenResponse(IntentoExamenBase):
    intento_id: str
    numero_intento: int
    estado: EstadoIntento
    fecha_inicio: datetime
    fecha_fin: Optional[datetime]
    tiempo_total_segundos: Optional[int]
    tiempo_limite_vencido: bool
    puntuacion_obtenida: float
    puntuacion_maxima: float
    porcentaje: Optional[float]
    aprobado: Optional[bool]
    preguntas_respondidas: int
    total_preguntas: int
    pregunta_actual: int
    cambios_pestana_detectados: int
    tiempo_inactividad_total: int
    ip_address: Optional[str]
    user_agent: Optional[str]
    eventos_sospechosos: Optional[Dict[str, Any]]
    orden_preguntas: Optional[List[str]]
    finalizado_por: str
    fecha_revision: Optional[datetime]
    revisado_por: Optional[str]
    comentarios_profesor: Optional[str]

    class Config:
        from_attributes = True


# === SCHEMAS DE RESPUESTA ===
class RespuestaEstudianteBase(BaseModel):
    intento_id: str = Field(..., description="ID del intento")
    pregunta_id: str = Field(..., description="ID de la pregunta")
    respuesta_estudiante: Optional[Dict[str, Any]] = Field(None, description="Respuesta del estudiante")
    texto_respuesta: Optional[str] = Field(None, description="Respuesta en texto libre")


class RespuestaEstudianteCreate(RespuestaEstudianteBase):
    tiempo_empleado_segundos: Optional[int] = Field(None, ge=0)


class RespuestaEstudianteUpdate(BaseModel):
    respuesta_estudiante: Optional[Dict[str, Any]] = None
    texto_respuesta: Optional[str] = None
    tiempo_empleado_segundos: Optional[int] = Field(None, ge=0)


class RespuestaEstudianteResponse(RespuestaEstudianteBase):
    respuesta_id: str
    puntuacion_obtenida: float
    puntuacion_maxima: float
    es_correcta: Optional[bool]
    calificada_automaticamente: bool
    fecha_respuesta: datetime
    tiempo_empleado_segundos: Optional[int]
    fecha_ultima_modificacion: Optional[datetime]
    numero_modificaciones: int
    feedback_automatico: Optional[str]
    feedback_profesor: Optional[str]
    mostrar_respuesta_correcta: bool

    class Config:
        from_attributes = True


# === SCHEMAS DE CONFIGURACIÓN ===
class ConfiguracionEvaluacionesResponse(BaseModel):
    config_id: str
    tiempo_gracia_segundos: int
    maximo_intentos_globales: int
    tiempo_minimo_entre_intentos: int
    max_cambios_pestana_permitidos: int
    tiempo_max_inactividad_global: int
    habilitar_deteccion_copia_texto: bool
    habilitar_deteccion_pantalla_completa: bool
    algoritmo_calificacion_ensayos: str
    umbral_similitud_plagio: float
    habilitar_feedback_automatico: bool
    notificar_intento_finalizado: bool
    notificar_resultado_disponible: bool
    notificar_tiempo_restante: bool
    tiempo_notificacion_previa_minutos: int
    guardar_progreso_cada_segundos: int
    habilitar_recuperacion_sesion: bool
    tiempo_expiracion_backup_horas: int
    institucion_id: Optional[str]
    aplicar_globalmente: bool

    class Config:
        from_attributes = True


# === SCHEMAS DE ESTADÍSTICAS ===
class EstadisticaExamenResponse(BaseModel):
    estadistica_id: str
    examen_id: str
    total_estudiantes_asignados: int
    total_intentos_realizados: int
    total_intentos_finalizados: int
    total_aprobados: int
    total_reprobados: int
    puntuacion_promedio: float
    puntuacion_mediana: float
    puntuacion_maxima_obtenida: float
    puntuacion_minima_obtenida: float
    desviacion_estandar: float
    tiempo_promedio_minutos: float
    tiempo_maximo_empleado: int
    tiempo_minimo_empleado: int
    estadisticas_preguntas: Optional[Dict[str, Any]]
    preguntas_mas_dificiles: Optional[List[str]]
    preguntas_mas_faciles: Optional[List[str]]
    patrones_abandono: Optional[Dict[str, Any]]
    tiempo_por_pregunta: Optional[Dict[str, Any]]
    fecha_calculo: datetime

    class Config:
        from_attributes = True


# === SCHEMAS COMBINADOS Y ESPECIALES ===
class ExamenCompleto(ExamenResponse):
    """Examen con todas sus preguntas incluidas"""
    preguntas: List[PreguntaExamenResponse] = []


class ExamenParaEstudiante(BaseModel):
    """Examen sin información sensible para estudiantes"""
    examen_id: str
    titulo: str
    descripcion: Optional[str]
    tipo_examen: TipoExamen
    duracion_minutos: int
    fecha_inicio: Optional[datetime]
    fecha_fin: Optional[datetime]
    intentos_permitidos: int
    requiere_contraseña: bool
    mostrar_resultados_inmediatos: bool
    permitir_revision: bool
    mostrar_respuestas_correctas: bool
    modo_pantalla_completa: bool
    bloquear_navegacion: bool
    detectar_cambio_pestana: bool
    tiempo_maximo_inactividad: int
    puntuacion_total: float
    puntuacion_minima_aprobacion: float
    instrucciones: Optional[str]
    total_preguntas: int
    # Información específica del estudiante
    intentos_realizados: int = 0
    mejor_calificacion: Optional[float] = None
    puede_tomar_examen: bool = True
    mensaje_acceso: Optional[str] = None


class PreguntaParaEstudiante(BaseModel):
    """Pregunta sin respuesta correcta para estudiantes"""
    pregunta_id: str
    titulo: str
    descripcion: Optional[str]
    tipo_pregunta: TipoPregunta
    orden: int
    puntuacion: float
    es_obligatoria: bool
    tiempo_limite_segundos: Optional[int]
    opciones_respuesta: Optional[Dict[str, Any]]
    imagen_url: Optional[str]
    audio_url: Optional[str]
    video_url: Optional[str]
    archivos_adjuntos: Optional[Dict[str, Any]]


class ResultadoExamen(BaseModel):
    """Resultado completo de un intento de examen"""
    intento: IntentoExamenResponse
    respuestas: List[RespuestaEstudianteResponse]
    estadisticas_intento: Dict[str, Any]
    puede_revisar: bool = True
    mostrar_respuestas_correctas: bool = True


class FiltrosBancoPreguntas(BaseModel):
    """Filtros para búsqueda en banco de preguntas"""
    tipo_pregunta: Optional[TipoPregunta] = None
    dificultad: Optional[DificultadPregunta] = None
    materia: Optional[str] = None
    tema: Optional[str] = None
    categoria: Optional[str] = None
    nivel_educativo: Optional[str] = None
    tags: Optional[List[str]] = None
    es_publica: Optional[bool] = None
    creado_por: Optional[str] = None
    texto_busqueda: Optional[str] = None
    limite: int = Field(default=50, ge=1, le=200)
    offset: int = Field(default=0, ge=0)