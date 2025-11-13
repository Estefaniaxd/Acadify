"""Modelos para el sistema de evaluaciones y exámenes
Incluye: Exámenes, Preguntas, Respuestas, Intentos, Banco de Preguntas.

Versión 2.0: BancoPregunta sincronizado con BD (33 campos)
Principios SOLID aplicados
"""

from datetime import UTC, datetime
import enum
import uuid

from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import DOUBLE_PRECISION, TIMESTAMP, UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from src.db.base_class import Base


class TipoExamen(str, enum.Enum):
    """Tipos de exámenes."""

    EVALUACION = "evaluacion"
    PRUEBA = "prueba"
    EXAMEN_FINAL = "examen_final"
    QUIZ = "quiz"
    SIMULACRO = "simulacro"
    DIAGNOSTICO = "diagnostico"


class EstadoExamen(str, enum.Enum):
    """Estados del examen."""

    BORRADOR = "borrador"
    PUBLICADO = "publicado"
    ACTIVO = "activo"
    FINALIZADO = "finalizado"
    ARCHIVADO = "archivado"


class TipoPregunta(str, enum.Enum):
    """Tipos de preguntas."""

    OPCION_MULTIPLE = "opcion_multiple"
    VERDADERO_FALSO = "verdadero_falso"
    ENSAYO = "ensayo"
    RESPUESTA_CORTA = "respuesta_corta"
    COMPLETAR = "completar"
    EMPAREJAMIENTO = "emparejamiento"
    ORDENAMIENTO = "ordenamiento"


class DificultadPregunta(str, enum.Enum):
    """Nivel de dificultad de la pregunta."""

    MUY_FACIL = "muy_facil"
    FACIL = "facil"
    MEDIO = "medio"
    DIFICIL = "dificil"
    MUY_DIFICIL = "muy_dificil"


class EstadoIntento(str, enum.Enum):
    """Estado de un intento de examen."""

    EN_PROGRESO = "en_progreso"
    FINALIZADO = "finalizado"
    TIEMPO_AGOTADO = "tiempo_agotado"
    CANCELADO = "cancelado"
    ABANDONADO = "abandonado"


class TipoEvento(str, enum.Enum):
    """Tipos de eventos anti-trampa."""

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
    tipo_examen = Column(
        Enum(TipoExamen), nullable=False, default=TipoExamen.EVALUACION
    )
    estado_examen = Column(
        Enum(EstadoExamen), nullable=False, default=EstadoExamen.BORRADOR
    )

    # Configuración de tiempo
    tiempo_limite = Column(
        Integer, nullable=False, default=60
    )  # Tiempo límite en minutos
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
    curso_id = Column(
        UUID(as_uuid=True)
    )  # FK a cursos (opcional para exámenes generales)
    grupo_id = Column(UUID(as_uuid=True))  # FK a grupos (opcional)
    creado_por = Column(
        UUID(as_uuid=True), ForeignKey("Usuario.usuario_id"), nullable=False
    )
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
    preguntas = relationship(
        "PreguntaExamen", back_populates="examen", cascade="all, delete-orphan"
    )
    intentos = relationship(
        "IntentoExamen", back_populates="examen", cascade="all, delete-orphan"
    )
    # NOTA: EstadisticaExamen comentada - FK apunta a evaluaciones.id, no a examenes.examen_id
    # La tabla examenes NO EXISTE, los datos están en evaluaciones
    # estadisticas = relationship(
    #     "EstadisticaExamen", back_populates="examen", cascade="all, delete-orphan"
    # )


# === MODELO: PREGUNTA DE EXAMEN ===
class PreguntaExamen(Base):
    __tablename__ = "preguntas_examen"

    # Identificación
    pregunta_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    examen_id = Column(
        String, ForeignKey("examenes.examen_id", ondelete="CASCADE"), nullable=False
    )

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
    puntos_respuesta_parcial = Column(
        Boolean, default=False
    )  # Permitir puntuación parcial
    dificultad = Column(Enum(DificultadPregunta), default=DificultadPregunta.MEDIO)

    # Recursos multimedia
    imagen_url = Column(String(500))
    audio_url = Column(String(500))
    video_url = Column(String(500))
    archivos_adjuntos = Column(JSON)

    # Metadatos
    banco_pregunta_id = Column(
        String, ForeignKey("banco_preguntas.pregunta_id"), nullable=True
    )  # Si viene del banco
    tags = Column(JSON)  # Etiquetas para categorización
    fecha_creacion = Column(DateTime(timezone=True), server_default=func.now())
    fecha_actualizacion = Column(DateTime(timezone=True), onupdate=func.now())

    # Estadísticas
    veces_utilizada = Column(Integer, default=0)
    promedio_aciertos = Column(Float)
    tiempo_promedio_respuesta = Column(Float)  # En segundos

    # Relaciones
    examen = relationship("Examen", back_populates="preguntas")
    # NOTA: BancoPregunta no tiene relación usos_en_examenes definida
    # banco_pregunta = relationship("BancoPregunta", back_populates="usos_en_examenes")
    # NOTA: RespuestaEstudiante se relaciona con preguntas_evaluacion, no con preguntas_examen
    # respuestas = relationship(
    #     "RespuestaEstudiante", back_populates="pregunta", cascade="all, delete-orphan"
    # )


# === MODELO: BANCO DE PREGUNTAS ===
class BancoPregunta(Base):
    """Banco centralizado de preguntas reutilizables.

    Permite a los profesores:
    - Crear y compartir preguntas entre evaluaciones
    - Categorizar por materia, tema, dificultad
    - Incluir multimedia y recursos
    - Mantener estadísticas de uso
    - Sistema de revisión por pares

    Principios SOLID: Single Responsibility (gestión de preguntas),
    Open/Closed (extensible para nuevos tipos).
    """

    __tablename__ = "banco_preguntas"

    # ===== IDENTIFICACIÓN =====
    pregunta_id = Column(String, primary_key=True, index=True)

    # ===== INFORMACIÓN BÁSICA =====
    titulo = Column(Text, nullable=False)
    descripcion = Column(Text, nullable=True)

    # ===== CLASIFICACIÓN =====
    tipo_pregunta = Column(String(50), nullable=False, index=True)
    dificultad = Column(String(50), nullable=True, index=True)
    materia = Column(String(100), nullable=True, index=True)
    tema = Column(String(200), nullable=True, index=True)
    subtema = Column(String(200), nullable=True)
    categoria = Column(String(100), nullable=True, index=True)
    nivel_educativo = Column(String(50), nullable=True)

    # ===== CONTENIDO DE LA PREGUNTA =====
    opciones_respuesta = Column(JSON, nullable=True)
    respuesta_correcta = Column(JSON, nullable=True)
    explicacion = Column(Text, nullable=True)

    # ===== MULTIMEDIA =====
    imagen_url = Column(String(500), nullable=True)
    audio_url = Column(String(500), nullable=True)
    video_url = Column(String(500), nullable=True)
    archivos_adjuntos = Column(JSON, nullable=True)

    # ===== METADATOS Y PERMISOS =====
    creado_por = Column(String, nullable=False, index=True)
    institucion_id = Column(String, nullable=True, index=True)
    es_publica = Column(Boolean, nullable=True, default=False)
    tags = Column(JSON, nullable=True)

    # ===== CONFIGURACIÓN =====
    puntuacion_sugerida = Column(DOUBLE_PRECISION, nullable=True, default=1.0)
    tiempo_estimado_segundos = Column(Integer, nullable=True)

    # ===== ESTADÍSTICAS DE USO =====
    veces_utilizada = Column(Integer, nullable=True, default=0)
    promedio_aciertos = Column(DOUBLE_PRECISION, nullable=True)
    calificacion_dificultad = Column(DOUBLE_PRECISION, nullable=True)
    ultima_vez_utilizada = Column(TIMESTAMP(timezone=True), nullable=True)

    # ===== REVISIÓN Y VALIDACIÓN =====
    revisado_por = Column(String, nullable=True)
    fecha_revision = Column(TIMESTAMP(timezone=True), nullable=True)
    estado_revision = Column(String(50), nullable=True, default="pendiente")
    comentarios_revision = Column(Text, nullable=True)

    # ===== AUDITORÍA =====
    fecha_creacion = Column(TIMESTAMP(timezone=True), nullable=True)
    fecha_actualizacion = Column(TIMESTAMP(timezone=True), nullable=True)

    # ===== PROPIEDADES =====
    @property
    def esta_aprobada(self) -> bool:
        """Verifica si la pregunta fue aprobada."""
        return self.estado_revision == "aprobado"

    @property
    def necesita_revision(self) -> bool:
        """Determina si necesita revisión."""
        return self.estado_revision in ["pendiente", None]

    @property
    def es_dificil(self) -> bool:
        """Determina si es una pregunta difícil basado en estadísticas."""
        return (
            self.promedio_aciertos is not None
            and self.promedio_aciertos < 0.5
            and self.veces_utilizada > 5
        )

    @property
    def es_popular(self) -> bool:
        """Determina si es una pregunta popular."""
        return (self.veces_utilizada or 0) > 10

    @property
    def tiene_multimedia(self) -> bool:
        """Verifica si tiene recursos multimedia."""
        return bool(
            self.imagen_url
            or self.audio_url
            or self.video_url
            or self.archivos_adjuntos
        )

    # ===== MÉTODOS DE NEGOCIO =====
    def registrar_uso(self) -> None:
        """Registra un uso de la pregunta."""
        self.veces_utilizada = (self.veces_utilizada or 0) + 1
        self.ultima_vez_utilizada = datetime.now(UTC)

    def actualizar_estadisticas(self, aciertos: int, total: int) -> None:
        """Actualiza estadísticas de acierto."""
        if total > 0:
            tasa_nueva = aciertos / total
            if self.promedio_aciertos is None:
                self.promedio_aciertos = tasa_nueva
            else:
                # Promedio ponderado
                peso_anterior = min(self.veces_utilizada or 0, 10)
                self.promedio_aciertos = (
                    self.promedio_aciertos * peso_anterior + tasa_nueva
                ) / (peso_anterior + 1)

    def aprobar(self, revisor_id: str, comentarios: str | None = None) -> None:
        """Aprueba la pregunta."""
        self.estado_revision = "aprobado"
        self.revisado_por = revisor_id
        self.fecha_revision = datetime.now(UTC)
        if comentarios:
            self.comentarios_revision = comentarios

    def rechazar(self, revisor_id: str, motivo: str) -> None:
        """Rechaza la pregunta."""
        self.estado_revision = "rechazado"
        self.revisado_por = revisor_id
        self.fecha_revision = datetime.now(UTC)
        self.comentarios_revision = motivo

    def hacer_publica(self) -> None:
        """Hace pública la pregunta (solo si está aprobada)."""
        if self.esta_aprobada:
            self.es_publica = True

    def __repr__(self) -> str:
        return f"<BancoPregunta(id='{self.pregunta_id}', tipo='{self.tipo_pregunta}', dificultad='{self.dificultad}')>"


# === MODELO: INTENTO DE EXAMEN ===
class IntentoExamen(Base):
    __tablename__ = "intentos_examen"

    # Identificación
    intento_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    examen_id = Column(
        String, ForeignKey("examenes.examen_id", ondelete="CASCADE"), nullable=False
    )
    estudiante_id = Column(
        UUID(as_uuid=True), ForeignKey("Usuario.usuario_id"), nullable=False
    )

    # Control de intento
    numero_intento = Column(Integer, nullable=False)  # 1, 2, 3, etc.
    estado_intento = Column(
        Enum(EstadoIntento), nullable=False, default=EstadoIntento.EN_PROGRESO
    )

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
    finalizado_por = Column(
        String(50), default="estudiante"
    )  # estudiante, tiempo_agotado, administrador
    comentarios_finalizacion = Column(Text)

    # Fechas de revisión (para preguntas de ensayo)
    fecha_revision = Column(DateTime(timezone=True))
    revisado_por = Column(UUID(as_uuid=True), ForeignKey("Usuario.usuario_id"))
    comentarios_profesor = Column(Text)

    # Relaciones
    examen = relationship("Examen", back_populates="intentos")
    # NOTA: RespuestaEstudiante se relaciona con intentos_evaluacion, no con intentos_examen
    # respuestas = relationship(
    #     "RespuestaEstudiante", back_populates="intento", cascade="all, delete-orphan"
    # )
    # NOTA: Múltiples clases EventoAntiTrampa - requiere ruta completa o comentar
    # eventos_anti_trampa = relationship(
    #     "EventoAntiTrampa", back_populates="intento", cascade="all, delete-orphan"
    # )


# === MODELO: CONFIGURACIÓN DEL SISTEMA DE EVALUACIONES ===
class ConfiguracionEvaluaciones(Base):
    """Configuración global del sistema de evaluaciones.

    Define límites, restricciones y comportamientos por defecto para:
    - Intentos y tiempos
    - Sistema antitrampa
    - Calificación automática
    - Notificaciones
    - Backup y recuperación

    Puede aplicarse globalmente o por institución.
    Principios SOLID: Single Responsibility (configuración centralizada)
    """

    __tablename__ = "configuracion_evaluaciones"

    # ===== IDENTIFICACIÓN =====
    config_id = Column(String, primary_key=True, index=True)

    # ===== CONFIGURACIÓN GENERAL =====
    tiempo_gracia_segundos = Column(Integer, nullable=True, default=300)
    maximo_intentos_globales = Column(Integer, nullable=True, default=5)
    tiempo_minimo_entre_intentos = Column(Integer, nullable=True, default=3600)

    # ===== CONFIGURACIÓN ANTI-TRAMPA =====
    max_cambios_pestana_permitidos = Column(Integer, nullable=True, default=5)
    tiempo_max_inactividad_global = Column(Integer, nullable=True, default=1800)
    habilitar_deteccion_copia_texto = Column(Boolean, nullable=True, default=True)
    habilitar_deteccion_pantalla_completa = Column(Boolean, nullable=True, default=True)

    # ===== CALIFICACIÓN AUTOMÁTICA =====
    algoritmo_calificacion_ensayos = Column(
        String(100), nullable=True, default="keyword_matching"
    )
    umbral_similitud_plagio = Column(DOUBLE_PRECISION, nullable=True, default=0.8)
    habilitar_feedback_automatico = Column(Boolean, nullable=True, default=True)

    # ===== NOTIFICACIONES =====
    notificar_intento_finalizado = Column(Boolean, nullable=True, default=True)
    notificar_resultado_disponible = Column(Boolean, nullable=True, default=True)
    notificar_tiempo_restante = Column(Boolean, nullable=True, default=True)
    tiempo_notificacion_previa_minutos = Column(Integer, nullable=True, default=10)

    # ===== BACKUP Y RECUPERACIÓN =====
    guardar_progreso_cada_segundos = Column(Integer, nullable=True, default=30)
    habilitar_recuperacion_sesion = Column(Boolean, nullable=True, default=True)
    tiempo_expiracion_backup_horas = Column(Integer, nullable=True, default=72)

    # ===== ALCANCE =====
    institucion_id = Column(String, nullable=True, index=True)
    aplicar_globalmente = Column(Boolean, nullable=True, default=True)

    # ===== AUDITORÍA =====
    creado_por = Column(String, nullable=False)
    fecha_creacion = Column(TIMESTAMP(timezone=True), nullable=True)
    fecha_actualizacion = Column(TIMESTAMP(timezone=True), nullable=True)

    # ===== PROPIEDADES =====
    @property
    def es_estricta(self) -> bool:
        """Determina si la configuración es estricta."""
        return (
            (self.max_cambios_pestana_permitidos or 0) <= 3
            and (self.maximo_intentos_globales or 0) <= 2
            and self.habilitar_deteccion_copia_texto
            and self.habilitar_deteccion_pantalla_completa
        )

    @property
    def es_flexible(self) -> bool:
        """Determina si la configuración es flexible."""
        return (self.max_cambios_pestana_permitidos or 0) >= 10 and (
            self.maximo_intentos_globales or 0
        ) >= 5

    @property
    def tiene_notificaciones_activas(self) -> bool:
        """Verifica si tiene notificaciones activas."""
        return (
            self.notificar_intento_finalizado
            or self.notificar_resultado_disponible
            or self.notificar_tiempo_restante
        )

    @property
    def tiempo_gracia_minutos(self) -> int:
        """Convierte tiempo de gracia a minutos."""
        return (self.tiempo_gracia_segundos or 0) // 60

    # ===== MÉTODOS DE NEGOCIO =====
    def aplicar_perfil_estricto(self) -> None:
        """Aplica perfil estricto de configuración."""
        self.tiempo_gracia_segundos = 120  # 2 minutos
        self.maximo_intentos_globales = 2
        self.max_cambios_pestana_permitidos = 2
        self.tiempo_max_inactividad_global = 600  # 10 minutos
        self.habilitar_deteccion_copia_texto = True
        self.habilitar_deteccion_pantalla_completa = True
        self.umbral_similitud_plagio = 0.7  # Más sensible

    def aplicar_perfil_flexible(self) -> None:
        """Aplica perfil flexible de configuración."""
        self.tiempo_gracia_segundos = 600  # 10 minutos
        self.maximo_intentos_globales = 10
        self.max_cambios_pestana_permitidos = 20
        self.tiempo_max_inactividad_global = 3600  # 1 hora
        self.habilitar_deteccion_copia_texto = False
        self.habilitar_deteccion_pantalla_completa = False
        self.umbral_similitud_plagio = 0.9  # Menos sensible

    def aplicar_perfil_balanceado(self) -> None:
        """Aplica perfil balanceado (por defecto)."""
        self.tiempo_gracia_segundos = 300  # 5 minutos
        self.maximo_intentos_globales = 5
        self.max_cambios_pestana_permitidos = 5
        self.tiempo_max_inactividad_global = 1800  # 30 minutos
        self.habilitar_deteccion_copia_texto = True
        self.habilitar_deteccion_pantalla_completa = True
        self.umbral_similitud_plagio = 0.8

    def __repr__(self) -> str:
        alcance = (
            "Global"
            if self.aplicar_globalmente
            else f"Institución {self.institucion_id}"
        )
        return (
            f"<ConfiguracionEvaluaciones(id='{self.config_id}', alcance='{alcance}')>"
        )


# === MODELO: ESTADÍSTICAS DE EXAMEN ===
class EstadisticaExamen(Base):
    """Estadísticas agregadas de una evaluación.

    Calcula y almacena métricas sobre:
    - Participación y finalización
    - Distribución de puntuaciones
    - Tiempos de realización
    - Análisis por pregunta
    - Patrones de comportamiento

    Se recalcula periódicamente para mantener datos actualizados.
    Principios SOLID: Single Responsibility (métricas y análisis)
    """

    __tablename__ = "estadisticas_examen"

    # ===== IDENTIFICACIÓN =====
    estadistica_id = Column(String, primary_key=True, index=True)
    examen_id = Column(String, nullable=False, index=True)

    # ===== ESTADÍSTICAS GENERALES =====
    total_estudiantes_asignados = Column(Integer, nullable=True, default=0)
    total_intentos_realizados = Column(Integer, nullable=True, default=0)
    total_intentos_finalizados = Column(Integer, nullable=True, default=0)
    total_aprobados = Column(Integer, nullable=True, default=0)
    total_reprobados = Column(Integer, nullable=True, default=0)

    # ===== ESTADÍSTICAS DE PUNTUACIÓN =====
    puntuacion_promedio = Column(DOUBLE_PRECISION, nullable=True, default=0.0)
    puntuacion_mediana = Column(DOUBLE_PRECISION, nullable=True, default=0.0)
    puntuacion_maxima_obtenida = Column(DOUBLE_PRECISION, nullable=True, default=0.0)
    puntuacion_minima_obtenida = Column(DOUBLE_PRECISION, nullable=True, default=0.0)
    desviacion_estandar = Column(DOUBLE_PRECISION, nullable=True, default=0.0)

    # ===== ESTADÍSTICAS DE TIEMPO =====
    tiempo_promedio_minutos = Column(DOUBLE_PRECISION, nullable=True, default=0.0)
    tiempo_maximo_empleado = Column(Integer, nullable=True, default=0)
    tiempo_minimo_empleado = Column(Integer, nullable=True, default=0)

    # ===== ANÁLISIS POR PREGUNTA =====
    estadisticas_preguntas = Column(JSON, nullable=True)
    preguntas_mas_dificiles = Column(JSON, nullable=True)
    preguntas_mas_faciles = Column(JSON, nullable=True)
    tiempo_por_pregunta = Column(JSON, nullable=True)

    # ===== PATRONES =====
    patrones_abandono = Column(JSON, nullable=True)

    # ===== CONFIGURACIÓN =====
    incluir_intentos_incompletos = Column(Boolean, nullable=True, default=False)
    periodo_calculo = Column(String(50), nullable=True)

    # ===== AUDITORÍA =====
    fecha_calculo = Column(TIMESTAMP(timezone=True), nullable=True)
    fecha_ultima_actualizacion = Column(TIMESTAMP(timezone=True), nullable=True)

    # ===== PROPIEDADES =====
    @property
    def tasa_finalizacion(self) -> float:
        """Calcula tasa de finalización."""
        if self.total_intentos_realizados == 0:
            return 0.0
        return (self.total_intentos_finalizados / self.total_intentos_realizados) * 100

    @property
    def tasa_aprobacion(self) -> float:
        """Calcula tasa de aprobación."""
        if self.total_intentos_finalizados == 0:
            return 0.0
        return (self.total_aprobados / self.total_intentos_finalizados) * 100

    @property
    def tasa_participacion(self) -> float:
        """Calcula tasa de participación."""
        if self.total_estudiantes_asignados == 0:
            return 0.0
        return (self.total_intentos_realizados / self.total_estudiantes_asignados) * 100

    @property
    def es_dificil(self) -> bool:
        """Determina si el examen es difícil basado en estadísticas."""
        return (
            (self.tasa_aprobacion < 50.0)
            and (self.puntuacion_promedio or 0) < 60.0
            and (self.total_intentos_finalizados or 0) >= 5
        )

    @property
    def es_facil(self) -> bool:
        """Determina si el examen es fácil basado en estadísticas."""
        return (
            (self.tasa_aprobacion > 90.0)
            and (self.puntuacion_promedio or 0) > 85.0
            and (self.total_intentos_finalizados or 0) >= 5
        )

    @property
    def tiene_alta_dispersion(self) -> bool:
        """Verifica si hay alta dispersión en resultados."""
        return (self.desviacion_estandar or 0) > 20.0

    # ===== MÉTODOS DE NEGOCIO =====
    def recalcular_desde_intentos(self, intentos: list) -> None:
        """Recalcula estadísticas desde lista de intentos."""
        if not intentos:
            return

        finalizados = [
            i
            for i in intentos
            if hasattr(i, "estado_intento") and i.estado_intento == "finalizado"
        ]

        self.total_intentos_realizados = len(intentos)
        self.total_intentos_finalizados = len(finalizados)

        if finalizados:
            puntuaciones = [
                i.puntuacion_obtenida
                for i in finalizados
                if hasattr(i, "puntuacion_obtenida") and i.puntuacion_obtenida
            ]
            if puntuaciones:
                self.puntuacion_promedio = sum(puntuaciones) / len(puntuaciones)
                self.puntuacion_maxima_obtenida = max(puntuaciones)
                self.puntuacion_minima_obtenida = min(puntuaciones)

                # Calcular mediana
                puntuaciones_sorted = sorted(puntuaciones)
                n = len(puntuaciones_sorted)
                if n % 2 == 0:
                    self.puntuacion_mediana = (
                        puntuaciones_sorted[n // 2 - 1] + puntuaciones_sorted[n // 2]
                    ) / 2
                else:
                    self.puntuacion_mediana = puntuaciones_sorted[n // 2]

                # Calcular desviación estándar
                if len(puntuaciones) > 1:
                    media = self.puntuacion_promedio
                    varianza = sum((p - media) ** 2 for p in puntuaciones) / len(
                        puntuaciones
                    )
                    self.desviacion_estandar = varianza**0.5

            # Contar aprobados/reprobados
            self.total_aprobados = sum(
                1 for i in finalizados if hasattr(i, "aprobado") and i.aprobado
            )
            self.total_reprobados = len(finalizados) - self.total_aprobados

            # Estadísticas de tiempo
            tiempos = [
                i.tiempo_total_segundos
                for i in finalizados
                if hasattr(i, "tiempo_total_segundos") and i.tiempo_total_segundos
            ]
            if tiempos:
                self.tiempo_promedio_minutos = (sum(tiempos) / len(tiempos)) / 60
                self.tiempo_maximo_empleado = max(tiempos)
                self.tiempo_minimo_empleado = min(tiempos)

        self.fecha_ultima_actualizacion = datetime.now(UTC)

    def identificar_preguntas_problematicas(self, umbral_acierto: float = 0.3) -> list:
        """Identifica preguntas con bajo índice de acierto."""
        if not self.estadisticas_preguntas:
            return []

        problematicas = []
        for pregunta_id, stats in self.estadisticas_preguntas.items():
            if stats.get("tasa_acierto", 1.0) < umbral_acierto:
                problematicas.append(
                    {
                        "pregunta_id": pregunta_id,
                        "tasa_acierto": stats.get("tasa_acierto"),
                        "intentos": stats.get("total_intentos"),
                    }
                )

        return sorted(problematicas, key=lambda x: x["tasa_acierto"])

    def __repr__(self) -> str:
        return f"<EstadisticaExamen(id='{self.estadistica_id}', promedio={self.puntuacion_promedio:.1f}, tasa_aprobacion={self.tasa_aprobacion:.1f}%)>"


# === MODELO: EVENTOS ANTI-TRAMPA ===
class EventoAntiTrampa(Base):
    __tablename__ = "eventos_anti_trampa"

    evento_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    intento_id = Column(
        String,
        ForeignKey("intentos_examen.intento_id", ondelete="CASCADE"),
        nullable=False,
    )

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
    # NOTA: FK apunta a intentos_evaluacion, no a intentos_examen
    # intento = relationship("IntentoExamen", back_populates="eventos_anti_trampa")
