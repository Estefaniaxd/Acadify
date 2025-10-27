"""
Modelos para el sistema de evaluaciones y exámenes
Incluye: Exámenes, Preguntas, Respuestas, Intentos, Banco de Preguntas
"""

from sqlalchemy import Column, String, Text, DateTime, Boolean, Integer, Float, ForeignKey, JSON, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
import enum

from ...db.base_class import Base


class TipoExamen(str, enum.Enum):
    """Tipos de exámenes"""
    EVALUACION = "evaluacion"
    PRUEBA = "prueba"
    EXAMEN_FINAL = "examen_final"
    QUIZ = "quiz"
    SIMULACRO = "simulacro"
    DIAGNOSTICO = "diagnostico"


class EstadoExamen(str, enum.Enum):
    """Estados del examen"""
    BORRADOR = "borrador"
    PUBLICADO = "publicado"
    ACTIVO = "activo"
    FINALIZADO = "finalizado"
    ARCHIVADO = "archivado"


class TipoPregunta(str, enum.Enum):
    """Tipos de preguntas"""
    OPCION_MULTIPLE = "opcion_multiple"
    VERDADERO_FALSO = "verdadero_falso"
    ENSAYO = "ensayo"
    RESPUESTA_CORTA = "respuesta_corta"
    COMPLETAR = "completar"
    EMPAREJAMIENTO = "emparejamiento"
    ORDENAMIENTO = "ordenamiento"


class DificultadPregunta(str, enum.Enum):
    """Nivel de dificultad de la pregunta"""
    MUY_FACIL = "muy_facil"
    FACIL = "facil"
    MEDIO = "medio"
    DIFICIL = "dificil"
    MUY_DIFICIL = "muy_dificil"


class EstadoIntento(str, enum.Enum):
    """Estado de un intento de examen"""
    EN_PROGRESO = "en_progreso"
    FINALIZADO = "finalizado"
    TIEMPO_AGOTADO = "tiempo_agotado"
    CANCELADO = "cancelado"
    ABANDONADO = "abandonado"


class TipoEvento(str, enum.Enum):
    """Tipos de eventos anti-trampa"""
    CAMBIO_PESTANA = "cambio_pestana"
    CAMBIO_APLICACION = "cambio_aplicacion"
    CLIC_FUERA_VENTANA = "clic_fuera_ventana"
    TIEMPO_INACTIVO = "tiempo_inactivo"
    PANTALLA_COMPLETA_SALIDA = "pantalla_completa_salida"
    TECLAS_SOSPECHOSAS = "teclas_sospechosas"
    MULTIPLE_SESION_IP = "multiple_sesion_ip"
    PATRON_RESPUESTA_SOSPECHOSO = "patron_respuesta_sospechoso"
    VELOCIDAD_RESPUESTA_ANOMALA = "velocidad_respuesta_anomala"


# === MODELO PRINCIPAL: EXAMEN ===
class Examen(Base):
    __tablename__ = "examenes"

    # Identificación
    examen_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    titulo = Column(String(200), nullable=False)
    descripcion = Column(Text)
    
    # Configuración básica
    tipo_examen = Column(Enum(TipoExamen), nullable=False, default=TipoExamen.EVALUACION)
    estado_examen = Column(Enum(EstadoExamen), nullable=False, default=EstadoExamen.BORRADOR)
    
    # Configuración de tiempo
    tiempo_limite = Column(Integer, nullable=False, default=60)  # Tiempo límite en minutos
    fecha_inicio = Column(DateTime(timezone=True))
    fecha_limite = Column(DateTime(timezone=True))
    
    # Configuración de acceso
    intentos_permitidos = Column(Integer, default=1)  # Número máximo de intentos
    requiere_contraseña = Column(Boolean, default=False)
    contraseña_acceso = Column(String(100))
    
    # Configuración de preguntas
    randomizar_preguntas = Column(Boolean, default=False)
    mostrar_resultados_inmediatos = Column(Boolean, default=True)
    permitir_revision = Column(Boolean, default=True)
    mostrar_respuestas_correctas = Column(Boolean, default=True)
    
    # Sistema anti-trampa
    modo_pantalla_completa = Column(Boolean, default=False)
    bloquear_navegacion = Column(Boolean, default=False)
    detectar_cambio_pestana = Column(Boolean, default=False)
    tiempo_maximo_inactividad = Column(Integer, default=300)  # 5 minutos en segundos
    
    # Calificación
    puntuacion_total = Column(Float, nullable=False, default=100.0)
    puntuacion_minima_aprobacion = Column(Float, default=60.0)
    calificacion_automatica = Column(Boolean, default=True)
    
    # Metadatos
    curso_id = Column(UUID(as_uuid=True))  # FK a cursos (opcional para exámenes generales)
    grupo_id = Column(UUID(as_uuid=True))  # FK a grupos (opcional)
    creado_por = Column(UUID(as_uuid=True), ForeignKey("Usuario.usuario_id"), nullable=False)
    fecha_creacion = Column(DateTime(timezone=True), server_default=func.now())
    fecha_actualizacion = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Configuración avanzada
    configuracion_avanzada = Column(JSON)  # Configuraciones adicionales
    instrucciones = Column(Text)  # Instrucciones específicas para el examen
    
    # Estadísticas
    total_preguntas = Column(Integer, default=0)
    total_intentos = Column(Integer, default=0)
    promedio_calificacion = Column(Float)
    
    # Relaciones
    preguntas = relationship("PreguntaExamen", back_populates="examen", cascade="all, delete-orphan")
    intentos = relationship("IntentoExamen", back_populates="examen", cascade="all, delete-orphan")
    estadisticas = relationship("EstadisticaExamen", back_populates="examen", cascade="all, delete-orphan")


# === MODELO: PREGUNTA DE EXAMEN ===
class PreguntaExamen(Base):
    __tablename__ = "preguntas_examen"

    # Identificación
    pregunta_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    examen_id = Column(String, ForeignKey("examenes.examen_id", ondelete="CASCADE"), nullable=False)
    
    # Contenido de la pregunta
    titulo = Column(Text, nullable=False)
    descripcion = Column(Text)  # Contexto adicional
    tipo_pregunta = Column(Enum(TipoPregunta), nullable=False)
    
    # Configuración
    orden = Column(Integer, nullable=False)  # Orden en el examen
    puntuacion = Column(Float, nullable=False, default=1.0)
    es_obligatoria = Column(Boolean, default=True)
    tiempo_limite_segundos = Column(Integer)  # Tiempo límite específico por pregunta
    
    # Configuración específica por tipo
    opciones_respuesta = Column(JSON)  # Para opción múltiple, emparejamiento, etc.
    respuesta_correcta = Column(JSON)  # Respuesta(s) correcta(s)
    explicacion = Column(Text)  # Explicación de la respuesta
    
    # Configuración de calificación
    puntos_respuesta_parcial = Column(Boolean, default=False)  # Permitir puntuación parcial
    dificultad = Column(Enum(DificultadPregunta), default=DificultadPregunta.MEDIO)
    
    # Recursos multimedia
    imagen_url = Column(String(500))
    audio_url = Column(String(500))
    video_url = Column(String(500))
    archivos_adjuntos = Column(JSON)
    
    # Metadatos
    banco_pregunta_id = Column(String, ForeignKey("banco_preguntas.pregunta_id"), nullable=True)  # Si viene del banco
    tags = Column(JSON)  # Etiquetas para categorización
    fecha_creacion = Column(DateTime(timezone=True), server_default=func.now())
    fecha_actualizacion = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Estadísticas
    veces_utilizada = Column(Integer, default=0)
    promedio_aciertos = Column(Float)
    tiempo_promedio_respuesta = Column(Float)  # En segundos
    
    # Relaciones
    examen = relationship("Examen", back_populates="preguntas")
    banco_pregunta = relationship("BancoPregunta", back_populates="usos_en_examenes")
    respuestas = relationship("RespuestaEstudiante", back_populates="pregunta", cascade="all, delete-orphan")


# === MODELO: BANCO DE PREGUNTAS ===
class BancoPregunta(Base):
    __tablename__ = "banco_preguntas"

    # Identificación
    pregunta_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    titulo = Column(Text, nullable=False)
    descripcion = Column(Text)
    
    # Clasificación
    tipo_pregunta = Column(Enum(TipoPregunta), nullable=False)
    dificultad = Column(Enum(DificultadPregunta), default=DificultadPregunta.MEDIO)
    materia = Column(String(100))  # Área de conocimiento
    tema = Column(String(200))  # Tema específico
    subtema = Column(String(200))  # Subtema
    
    # Contenido
    opciones_respuesta = Column(JSON)
    respuesta_correcta = Column(JSON)
    explicacion = Column(Text)
    
    # Recursos
    imagen_url = Column(String(500))
    audio_url = Column(String(500))
    video_url = Column(String(500))
    archivos_adjuntos = Column(JSON)
    
    # Metadatos
    creado_por = Column(String, nullable=False)
    institucion_id = Column(UUID(as_uuid=True))  # Para compartir entre instituciones
    es_publica = Column(Boolean, default=False)  # Disponible para otros profesores
    
    # Etiquetas y categorización
    tags = Column(JSON)
    categoria = Column(String(100))
    nivel_educativo = Column(String(50))  # primaria, secundaria, universidad
    
    # Configuración
    puntuacion_sugerida = Column(Float, default=1.0)
    tiempo_estimado_segundos = Column(Integer)
    
    # Estadísticas de uso
    veces_utilizada = Column(Integer, default=0)
    promedio_aciertos = Column(Float)
    calificacion_dificultad = Column(Float)  # Calculada automáticamente
    
    # Fechas
    fecha_creacion = Column(DateTime(timezone=True), server_default=func.now())
    fecha_actualizacion = Column(DateTime(timezone=True), onupdate=func.now())
    ultima_vez_utilizada = Column(DateTime(timezone=True))
    
    # Validación y revisión
    revisado_por = Column(UUID(as_uuid=True), ForeignKey("Usuario.usuario_id"))  # Usuario que revisó la pregunta
    fecha_revision = Column(DateTime(timezone=True))
    estado_revision = Column(String(50), default="pendiente")  # pendiente, aprobado, rechazado
    comentarios_revision = Column(Text)
    
    # Relaciones
    usos_en_examenes = relationship("PreguntaExamen", back_populates="banco_pregunta")


# === MODELO: INTENTO DE EXAMEN ===
class IntentoExamen(Base):
    __tablename__ = "intentos_examen"

    # Identificación
    intento_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    examen_id = Column(String, ForeignKey("examenes.examen_id", ondelete="CASCADE"), nullable=False)
    estudiante_id = Column(UUID(as_uuid=True), ForeignKey("Usuario.usuario_id"), nullable=False)
    
    # Control de intento
    numero_intento = Column(Integer, nullable=False)  # 1, 2, 3, etc.
    estado_intento = Column(Enum(EstadoIntento), nullable=False, default=EstadoIntento.EN_PROGRESO)
    
    # Tiempos
    fecha_inicio = Column(DateTime(timezone=True), server_default=func.now())
    fecha_fin = Column(DateTime(timezone=True))
    tiempo_total_segundos = Column(Integer)  # Tiempo total empleado
    tiempo_limite_vencido = Column(Boolean, default=False)
    
    # Calificación
    puntuacion_obtenida = Column(Float, default=0.0)
    puntuacion_maxima = Column(Float, nullable=False)
    porcentaje = Column(Float)  # Calculado: (obtenida/maxima) * 100
    aprobado = Column(Boolean)
    
    # Progreso
    preguntas_respondidas = Column(Integer, default=0)
    total_preguntas = Column(Integer, nullable=False)
    pregunta_actual = Column(Integer, default=1)
    
    # Sistema anti-trampa
    cambios_pestana_detectados = Column(Integer, default=0)
    tiempo_inactividad_total = Column(Integer, default=0)  # En segundos
    ip_address = Column(String(45))  # IPv4 o IPv6
    user_agent = Column(Text)
    eventos_sospechosos = Column(JSON)  # Log de eventos sospechosos
    
    # Configuración específica del intento
    orden_preguntas = Column(JSON)  # Orden de preguntas para este intento
    configuracion_intento = Column(JSON)  # Configuraciones específicas
    
    # Metadatos de finalización
    finalizado_por = Column(String(50), default="estudiante")  # estudiante, tiempo_agotado, administrador
    comentarios_finalizacion = Column(Text)
    
    # Fechas de revisión (para preguntas de ensayo)
    fecha_revision = Column(DateTime(timezone=True))
    revisado_por = Column(UUID(as_uuid=True), ForeignKey("Usuario.usuario_id"))
    comentarios_profesor = Column(Text)
    
    # Relaciones
    examen = relationship("Examen", back_populates="intentos")
    respuestas = relationship("RespuestaEstudiante", back_populates="intento", cascade="all, delete-orphan")
    eventos_anti_trampa = relationship("EventoAntiTrampa", back_populates="intento", cascade="all, delete-orphan")
    respuestas = relationship("RespuestaEstudiante", back_populates="intento", cascade="all, delete-orphan")


# === MODELO: RESPUESTA DEL ESTUDIANTE ===
class RespuestaEstudiante(Base):
    __tablename__ = "respuestas_estudiante"

    # Identificación
    respuesta_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    intento_id = Column(String, ForeignKey("intentos_examen.intento_id", ondelete="CASCADE"), nullable=False)
    pregunta_id = Column(String, ForeignKey("preguntas_examen.pregunta_id", ondelete="CASCADE"), nullable=False)
    
    # Contenido de la respuesta
    respuesta_estudiante = Column(JSON)  # Respuesta del estudiante (formato depende del tipo)
    texto_respuesta = Column(Text)  # Para respuestas de texto libre o ensayos
    
    # Calificación
    puntuacion_obtenida = Column(Float, default=0.0)
    puntuacion_maxima = Column(Float, nullable=False)
    es_correcta = Column(Boolean)
    calificada_automaticamente = Column(Boolean, default=False)
    
    # Tiempos
    fecha_respuesta = Column(DateTime(timezone=True), server_default=func.now())
    tiempo_empleado_segundos = Column(Integer)  # Tiempo que tomó responder
    fecha_ultima_modificacion = Column(DateTime(timezone=True))
    
    # Seguimiento de cambios
    historial_respuestas = Column(JSON)  # Para guardar cambios durante el intento
    numero_modificaciones = Column(Integer, default=0)
    
    # Retroalimentación
    feedback_automatico = Column(Text)  # Feedback automático basado en la respuesta
    feedback_profesor = Column(Text)  # Comentarios del profesor
    mostrar_respuesta_correcta = Column(Boolean, default=False)
    
    # Análisis de la respuesta
    palabras_clave_encontradas = Column(JSON)  # Para análisis de ensayos
    similitud_respuesta_correcta = Column(Float)  # Porcentaje de similitud
    
    # Metadatos
    version_pregunta = Column(String(50))  # Para control de versiones de preguntas
    metadata_respuesta = Column(JSON)  # Información adicional específica del tipo
    
    # Relaciones
    intento = relationship("IntentoExamen", back_populates="respuestas")
    pregunta = relationship("PreguntaExamen", back_populates="respuestas")


# === MODELO: CONFIGURACIÓN DEL SISTEMA DE EVALUACIONES ===
class ConfiguracionEvaluaciones(Base):
    __tablename__ = "configuracion_evaluaciones"

    config_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Configuración general
    tiempo_gracia_segundos = Column(Integer, default=300)  # 5 minutos de gracia
    maximo_intentos_globales = Column(Integer, default=5)
    tiempo_minimo_entre_intentos = Column(Integer, default=3600)  # 1 hora
    
    # Configuración anti-trampa
    max_cambios_pestana_permitidos = Column(Integer, default=5)
    tiempo_max_inactividad_global = Column(Integer, default=1800)  # 30 minutos
    habilitar_deteccion_copia_texto = Column(Boolean, default=True)
    habilitar_deteccion_pantalla_completa = Column(Boolean, default=True)
    
    # Configuración de calificación automática
    algoritmo_calificacion_ensayos = Column(String(100), default="keyword_matching")
    umbral_similitud_plagio = Column(Float, default=0.8)  # 80% similitud
    habilitar_feedback_automatico = Column(Boolean, default=True)
    
    # Configuración de notificaciones
    notificar_intento_finalizado = Column(Boolean, default=True)
    notificar_resultado_disponible = Column(Boolean, default=True)
    notificar_tiempo_restante = Column(Boolean, default=True)
    tiempo_notificacion_previa_minutos = Column(Integer, default=10)
    
    # Configuración de backup y recuperación
    guardar_progreso_cada_segundos = Column(Integer, default=30)
    habilitar_recuperacion_sesion = Column(Boolean, default=True)
    tiempo_expiracion_backup_horas = Column(Integer, default=72)
    
    # Configuración específica de institución
    institucion_id = Column(UUID(as_uuid=True))
    aplicar_globalmente = Column(Boolean, default=True)
    
    # Metadatos
    creado_por = Column(UUID(as_uuid=True), ForeignKey("Usuario.usuario_id"), nullable=False)
    fecha_creacion = Column(DateTime(timezone=True), server_default=func.now())
    fecha_actualizacion = Column(DateTime(timezone=True), onupdate=func.now())


# === MODELO: ESTADÍSTICAS DE EXAMEN ===
class EstadisticaExamen(Base):
    __tablename__ = "estadisticas_examen"

    estadistica_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    examen_id = Column(String, ForeignKey("examenes.examen_id", ondelete="CASCADE"), nullable=False)
    
    # Estadísticas generales
    total_estudiantes_asignados = Column(Integer, default=0)
    total_intentos_realizados = Column(Integer, default=0)
    total_intentos_finalizados = Column(Integer, default=0)
    total_aprobados = Column(Integer, default=0)
    total_reprobados = Column(Integer, default=0)
    
    # Estadísticas de puntuación
    puntuacion_promedio = Column(Float, default=0.0)
    puntuacion_mediana = Column(Float, default=0.0)
    puntuacion_maxima_obtenida = Column(Float, default=0.0)
    puntuacion_minima_obtenida = Column(Float, default=0.0)
    desviacion_estandar = Column(Float, default=0.0)
    
    # Estadísticas de tiempo
    tiempo_promedio_minutos = Column(Float, default=0.0)
    tiempo_maximo_empleado = Column(Integer, default=0)
    tiempo_minimo_empleado = Column(Integer, default=0)
    
    # Estadísticas por pregunta
    estadisticas_preguntas = Column(JSON)  # Estadísticas detalladas por pregunta
    preguntas_mas_dificiles = Column(JSON)  # IDs de preguntas con menor acierto
    preguntas_mas_faciles = Column(JSON)  # IDs de preguntas con mayor acierto
    
    # Patrones de comportamiento
    patrones_abandono = Column(JSON)  # En qué preguntas abandonan más
    tiempo_por_pregunta = Column(JSON)  # Tiempo promedio por pregunta
    
    # Fechas de cálculo
    fecha_calculo = Column(DateTime(timezone=True), server_default=func.now())
    fecha_ultima_actualizacion = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Configuración de cálculo
    incluir_intentos_incompletos = Column(Boolean, default=False)
    periodo_calculo = Column(String(50), default="completo")  # completo, ultimo_mes, etc.
    
    # Relaciones
    examen = relationship("Examen", back_populates="estadisticas")


# === MODELO: EVENTOS ANTI-TRAMPA ===
class EventoAntiTrampa(Base):
    __tablename__ = "eventos_anti_trampa"

    evento_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    intento_id = Column(String, ForeignKey("intentos_examen.intento_id", ondelete="CASCADE"), nullable=False)
    
    # Tipo y datos del evento
    tipo_evento = Column(Enum(TipoEvento), nullable=False)
    descripcion = Column(Text)
    datos_evento = Column(JSON)  # Datos específicos del evento
    
    # Contexto técnico
    ip_address = Column(String(45))
    user_agent = Column(Text)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    
    # Análisis automático
    es_sospechoso = Column(Boolean, default=False)
    nivel_riesgo = Column(String(20), default="bajo")  # bajo, medio, alto, crítico
    requiere_revision = Column(Boolean, default=False)
    
    # Relaciones
    intento = relationship("IntentoExamen", back_populates="eventos_anti_trampa")