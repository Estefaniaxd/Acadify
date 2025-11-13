"""Sistema de Intentos de Evaluación - Sincronizado con BD.

Este módulo contiene los modelos para:
- IntentoEvaluacion: Intentos de evaluación con tracking completo (68 campos)
- RespuestaEstudiante: Respuestas individuales con calificación (47 campos)
- EventoAntiTrampa: Eventos de seguridad (11 campos)
- Gamificación: Puntos, insignias, rankings

Principios SOLID aplicados.
Versión: 2.0 (Sincronizado con BD - 2025-11-04)
"""

from datetime import UTC, datetime
import uuid

from sqlalchemy import (
    JSON,
    Boolean,
    CheckConstraint,
    Column,
    DateTime,
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


class IntentoEvaluacion(Base):
    """Intento de evaluación realizado por un estudiante.

    Gestiona:
    - Progreso y estado del intento
    - Tiempos y límites
    - Calificación y feedback
    - Sistema antitrampa
    - Gamificación y ranking
    - Evaluaciones adaptativas
    - Trabajo colaborativo

    Estados: iniciado, en_progreso, pausado, finalizado,
             tiempo_agotado, cancelado, en_revision, calificado
    """

    __tablename__ = "intentos_evaluacion"

    # ===== IDENTIFICACIÓN =====
    id = Column(String, primary_key=True, index=True)
    evaluacion_id = Column(
        String,
        ForeignKey("evaluaciones.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    estudiante_id = Column(
        String, ForeignKey("Usuario.usuario_id"), nullable=False, index=True
    )

    # ===== CONTROL DE INTENTO =====
    numero_intento = Column(Integer, nullable=False, index=True)
    estado_intento = Column(String(50), nullable=False, default="iniciado", index=True)

    # ===== TIEMPOS =====
    fecha_inicio = Column(TIMESTAMP(timezone=True), nullable=True)
    fecha_fin = Column(TIMESTAMP(timezone=True), nullable=True)
    tiempo_total_segundos = Column(Integer, nullable=True, default=0)
    tiempo_activo_segundos = Column(Integer, nullable=True, default=0)
    tiempo_pausado_segundos = Column(Integer, nullable=True, default=0)
    tiempo_limite_vencido = Column(Boolean, nullable=True, default=False)
    tiempo_inactividad_total = Column(Integer, nullable=True, default=0)

    # ===== PROGRESO =====
    total_preguntas = Column(Integer, nullable=False)
    preguntas_respondidas = Column(Integer, nullable=True, default=0)
    pregunta_actual_orden = Column(Integer, nullable=True, default=1)
    progreso_actual = Column(DOUBLE_PRECISION, nullable=True, default=0.0)
    orden_preguntas = Column(JSON, nullable=True)

    # ===== CALIFICACIÓN =====
    puntuacion_obtenida = Column(DOUBLE_PRECISION, nullable=True, default=0.0)
    puntuacion_maxima = Column(DOUBLE_PRECISION, nullable=False)
    porcentaje = Column(DOUBLE_PRECISION, nullable=True)
    aprobado = Column(Boolean, nullable=True)

    # ===== PAUSAS =====
    numero_pausas = Column(Integer, nullable=True, default=0)

    # ===== REVISIÓN MANUAL =====
    requiere_revision_manual = Column(Boolean, nullable=True, default=False)
    fecha_revision = Column(TIMESTAMP(timezone=True), nullable=True)
    revisado_por = Column(String, nullable=True)
    comentarios_profesor = Column(Text, nullable=True)

    # ===== FINALIZACIÓN =====
    finalizado_por = Column(String(50), nullable=True)
    comentarios_finalizacion = Column(Text, nullable=True)

    # ===== CALIFICACIÓN CON IA =====
    calificado_por_ia = Column(Boolean, nullable=True, default=False)
    feedback_ia = Column(Text, nullable=True)
    feedback_manual = Column(Text, nullable=True)
    confianza_calificacion_ia = Column(DOUBLE_PRECISION, nullable=True)
    recomendaciones_ia = Column(JSON, nullable=True)

    # ===== SEGURIDAD - CONTEXTO =====
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)

    # ===== SEGURIDAD - ANTITRAMPA =====
    nivel_riesgo = Column(String(50), nullable=True, default="ninguno")
    puntuacion_riesgo = Column(DOUBLE_PRECISION, nullable=True, default=0.0)
    cambios_pestana_detectados = Column(Integer, nullable=True, default=0)
    total_eventos_antitrampa = Column(Integer, nullable=True, default=0)
    eventos_sospechosos = Column(JSON, nullable=True)
    eventos_detallados = Column(JSON, nullable=True)
    bloqueado_automaticamente = Column(Boolean, nullable=True, default=False)
    razon_bloqueo = Column(Text, nullable=True)

    # ===== SEGURIDAD - DETECCIÓN IA/PLAGIO =====
    detecciones_ia = Column(Integer, nullable=True, default=0)
    detecciones_plagio = Column(Integer, nullable=True, default=0)

    # ===== MULTIMEDIA - GRABACIÓN =====
    sesion_grabacion_id = Column(String(100), nullable=True)
    total_capturas_webcam = Column(Integer, nullable=True, default=0)
    capturas_con_anomalias = Column(Integer, nullable=True, default=0)
    capturas_urls = Column(JSON, nullable=True)
    verificacion_identidad_exitosa = Column(Boolean, nullable=True, default=False)
    url_grabacion_video = Column(String(500), nullable=True)
    url_grabacion_audio = Column(String(500), nullable=True)

    # ===== GAMIFICACIÓN =====
    puntos_ganados = Column(Integer, nullable=True, default=0)
    multiplicador_aplicado = Column(DOUBLE_PRECISION, nullable=True, default=1.0)
    bonus_tiempo = Column(Integer, nullable=True, default=0)
    bonus_precision = Column(Integer, nullable=True, default=0)
    insignias_ganadas = Column(JSON, nullable=True)
    logros_desbloqueados = Column(JSON, nullable=True)

    # ===== RANKING =====
    posicion_ranking = Column(Integer, nullable=True)

    # ===== ADAPTABILIDAD =====
    dificultad_inicial = Column(String(50), nullable=True)
    dificultad_actual = Column(String(50), nullable=True)
    ajustes_dificultad = Column(JSON, nullable=True)
    nivel_habilidad_estimado = Column(DOUBLE_PRECISION, nullable=True)

    # ===== COLABORACIÓN =====
    equipo_id = Column(String(36), nullable=True)
    equipo_ids = Column(JSON, nullable=True)
    es_lider_equipo = Column(Boolean, nullable=True, default=False)
    contribucion_equipo = Column(JSON, nullable=True)

    # ===== CONFIGURACIÓN =====
    configuracion_intento = Column(JSON, nullable=True)

    # ===== RELACIONES =====
    evaluacion = relationship(
        "Evaluacion", foreign_keys=[evaluacion_id], backref="intentos"
    )
    estudiante = relationship(
        "Usuario", foreign_keys=[estudiante_id], backref="intentos_evaluacion"
    )
    eventos_audio = relationship(
        "EventoAudio", 
        back_populates="intento",
        cascade="all, delete-orphan",
        lazy="dynamic"
    )

    # ===== CONSTRAINTS =====
    __table_args__ = (
        CheckConstraint(
            "puntuacion_obtenida >= 0", name="check_puntuacion_intento_positiva"
        ),
        CheckConstraint(
            "tiempo_total_segundos >= 0", name="check_tiempo_intento_positivo"
        ),
        CheckConstraint("numero_intento > 0", name="check_numero_intento_positivo"),
    )

    # ===== PROPIEDADES =====
    @property
    def esta_activo(self) -> bool:
        return self.estado_intento in ["iniciado", "en_progreso"]

    @property
    def esta_finalizado(self) -> bool:
        return self.estado_intento in ["finalizado", "tiempo_agotado", "calificado"]

    @property
    def requiere_revision(self) -> bool:
        return self.requiere_revision_manual and not self.revisado_por

    @property
    def porcentaje_progreso(self) -> float:
        if self.total_preguntas == 0:
            return 0.0
        return (self.preguntas_respondidas / self.total_preguntas) * 100

    @property
    def tiene_riesgo_alto(self) -> bool:
        return (
            self.nivel_riesgo in ["alto", "critico"]
            or (self.puntuacion_riesgo or 0) > 70
        )

    # ===== MÉTODOS DE NEGOCIO =====
    def iniciar(self) -> None:
        """Inicia el intento."""
        self.estado_intento = "en_progreso"
        if not self.fecha_inicio:
            self.fecha_inicio = datetime.now(UTC)

    def finalizar(
        self, finalizado_por: str = "estudiante", comentario: str | None = None
    ) -> None:
        """Finaliza el intento."""
        self.estado_intento = "finalizado"
        self.fecha_fin = datetime.now(UTC)
        self.finalizado_por = finalizado_por
        if comentario:
            self.comentarios_finalizacion = comentario

    def pausar(self) -> None:
        """Pausa el intento."""
        if self.esta_activo:
            self.estado_intento = "pausado"
            self.numero_pausas = (self.numero_pausas or 0) + 1

    def reanudar(self) -> None:
        """Reanuda el intento."""
        if self.estado_intento == "pausado":
            self.estado_intento = "en_progreso"

    def calcular_puntuacion_final(self) -> None:
        """Calcula puntuación y porcentaje."""
        if self.puntuacion_maxima and self.puntuacion_maxima > 0:
            self.porcentaje = (self.puntuacion_obtenida / self.puntuacion_maxima) * 100
            # Determinar si aprobó (por defecto 60%)
            self.aprobado = self.porcentaje >= 60.0

    def registrar_evento_antitrampa(
        self, tipo: str, severidad: str, datos: dict
    ) -> None:
        """Registra un evento antitrampa."""
        self.total_eventos_antitrampa = (self.total_eventos_antitrampa or 0) + 1
        if not self.eventos_detallados:
            self.eventos_detallados = []
        self.eventos_detallados.append(
            {
                "tipo": tipo,
                "severidad": severidad,
                "datos": datos,
                "timestamp": datetime.now(UTC).isoformat(),
            }
        )

        # Actualizar nivel de riesgo
        if severidad in ["alta", "critica"]:
            self.puntuacion_riesgo = min((self.puntuacion_riesgo or 0) + 10, 100)
            if self.puntuacion_riesgo > 70:
                self.nivel_riesgo = "critico"
            elif self.puntuacion_riesgo > 50:
                self.nivel_riesgo = "alto"

    def __repr__(self) -> str:
        return f"<IntentoEvaluacion(id='{self.id}', intento={self.numero_intento}, estado='{self.estado_intento}')>"


# ==========================================
# MODELO: RESPUESTA DEL ESTUDIANTE
# ==========================================


class RespuestaEstudiante(Base):
    """Respuesta de un estudiante a una pregunta de evaluación.

    Gestiona:
    - Respuestas en múltiples formatos (texto, código, multimedia)
    - Calificación automática y manual
    - Feedback personalizado
    - Detección de IA y plagio
    - Historial de modificaciones
    - Análisis de similitud
    - Ejecución de código
    """

    __tablename__ = "respuestas_estudiante"

    # ===== IDENTIFICACIÓN =====
    id = Column(String, primary_key=True, index=True)
    intento_id = Column(
        String,
        ForeignKey("intentos_evaluacion.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    pregunta_id = Column(
        String, ForeignKey("preguntas_evaluacion.id"), nullable=False, index=True
    )

    # ===== RESPUESTA =====
    respuesta_estudiante = Column(JSON, nullable=True)
    texto_respuesta = Column(Text, nullable=True)

    # ===== CALIFICACIÓN =====
    puntuacion_obtenida = Column(DOUBLE_PRECISION, nullable=True, default=0.0)
    puntuacion_maxima = Column(DOUBLE_PRECISION, nullable=False)
    es_correcta = Column(Boolean, nullable=True)
    calificada_automaticamente = Column(Boolean, nullable=True, default=False)

    # ===== TIEMPOS =====
    fecha_respuesta = Column(TIMESTAMP(timezone=True), nullable=True)
    tiempo_respuesta_segundos = Column(Integer, nullable=True)
    fecha_ultima_modificacion = Column(TIMESTAMP(timezone=True), nullable=True)

    # ===== HISTORIAL =====
    historial_respuestas = Column(JSON, nullable=True)
    numero_modificaciones = Column(Integer, nullable=True, default=0)

    # ===== FEEDBACK =====
    feedback_automatico = Column(Text, nullable=True)
    feedback_profesor = Column(Text, nullable=True)
    feedback = Column(Text, nullable=True)
    feedback_ia = Column(Text, nullable=True)
    feedback_manual = Column(Text, nullable=True)
    explicacion = Column(Text, nullable=True)
    sugerencias_mejora = Column(Text, nullable=True)

    # ===== ANÁLISIS DE RESPUESTA =====
    mostrar_respuesta_correcta = Column(Boolean, nullable=True, default=False)
    palabras_clave_encontradas = Column(JSON, nullable=True)
    similitud_respuesta_correcta = Column(DOUBLE_PRECISION, nullable=True)

    # ===== VERSIÓN =====
    version_pregunta = Column(String(50), nullable=True)
    metadata_respuesta = Column(JSON, nullable=True)

    # ===== DETECCIÓN DE IA =====
    fue_detectada_ia = Column(Boolean, nullable=True, default=False)
    probabilidad_ia = Column(DOUBLE_PRECISION, nullable=True)
    indicadores_ia = Column(JSON, nullable=True)
    modelo_ia_usado = Column(String(100), nullable=True)

    # ===== DETECCIÓN DE PLAGIO =====
    fue_detectado_plagio = Column(Boolean, nullable=True, default=False)
    similitud_plagio = Column(DOUBLE_PRECISION, nullable=True)
    fuentes_plagio = Column(JSON, nullable=True)
    tipo_plagio = Column(String(50), nullable=True)

    # ===== REVISIÓN MANUAL =====
    requiere_revision_manual = Column(Boolean, nullable=True, default=False)
    revisado_por_id = Column(String(36), nullable=True)
    fecha_revision = Column(TIMESTAMP(timezone=True), nullable=True)
    notas_revision = Column(Text, nullable=True)

    # ===== CÓDIGO =====
    codigo_ejecutado = Column(Text, nullable=True)
    resultado_ejecucion = Column(JSON, nullable=True)
    tests_pasados = Column(Integer, nullable=True, default=0)
    tests_fallados = Column(Integer, nullable=True, default=0)
    cobertura_codigo = Column(DOUBLE_PRECISION, nullable=True)

    # ===== MULTIMEDIA =====
    audio_url = Column(String(500), nullable=True)
    video_url = Column(String(500), nullable=True)
    archivo_url = Column(String(500), nullable=True)
    dibujo_url = Column(String(500), nullable=True)

    # ===== RELACIONES =====
    intento = relationship(
        "IntentoEvaluacion", foreign_keys=[intento_id], backref="respuestas"
    )
    pregunta = relationship(
        "PreguntaEvaluacion",
        foreign_keys=[pregunta_id],
        backref="respuestas_estudiante",
    )

    # ===== CONSTRAINTS =====
    __table_args__ = (
        CheckConstraint(
            "puntuacion_obtenida >= 0", name="check_puntuacion_respuesta_positiva"
        ),
        CheckConstraint(
            "tiempo_respuesta_segundos >= 0", name="check_tiempo_respuesta_positivo"
        ),
    )

    # ===== PROPIEDADES =====
    @property
    def porcentaje_acierto(self) -> float:
        """Calcula el porcentaje de acierto."""
        if self.puntuacion_maxima == 0:
            return 0.0
        return (self.puntuacion_obtenida / self.puntuacion_maxima) * 100

    @property
    def necesita_revision(self) -> bool:
        """Determina si necesita revisión manual."""
        return (
            self.requiere_revision_manual
            and not self.revisado_por_id
            and not self.calificada_automaticamente
        )

    @property
    def tiene_sospecha_trampa(self) -> bool:
        """Detecta posible trampa (IA o plagio)."""
        return (
            self.fue_detectada_ia
            or self.fue_detectado_plagio
            or (self.probabilidad_ia or 0) > 0.7
            or (self.similitud_plagio or 0) > 0.8
        )

    @property
    def tiene_multimedia(self) -> bool:
        """Verifica si tiene contenido multimedia."""
        return bool(
            self.audio_url or self.video_url or self.archivo_url or self.dibujo_url
        )

    @property
    def todos_tests_pasados(self) -> bool:
        """Verifica si pasó todos los tests de código."""
        if not self.codigo_ejecutado:
            return False
        total = (self.tests_pasados or 0) + (self.tests_fallados or 0)
        return total > 0 and self.tests_fallados == 0

    # ===== MÉTODOS DE NEGOCIO =====
    def calificar_automaticamente(self, es_correcta: bool, puntuacion: float) -> None:
        """Califica la respuesta automáticamente."""
        self.es_correcta = es_correcta
        self.puntuacion_obtenida = min(puntuacion, self.puntuacion_maxima)
        self.calificada_automaticamente = True

    def agregar_feedback_ia(self, feedback: str, modelo: str | None = None) -> None:
        """Agrega feedback generado por IA."""
        self.feedback_ia = feedback
        if modelo:
            self.modelo_ia_usado = modelo

    def marcar_sospecha_ia(self, probabilidad: float, indicadores: dict) -> None:
        """Marca como sospecha de uso de IA."""
        self.fue_detectada_ia = probabilidad > 0.5
        self.probabilidad_ia = probabilidad
        self.indicadores_ia = indicadores
        if self.fue_detectada_ia:
            self.requiere_revision_manual = True

    def marcar_sospecha_plagio(
        self, similitud: float, fuentes: list[dict], tipo: str
    ) -> None:
        """Marca como sospecha de plagio."""
        self.fue_detectado_plagio = similitud > 0.7
        self.similitud_plagio = similitud
        self.fuentes_plagio = fuentes
        self.tipo_plagio = tipo
        if self.fue_detectado_plagio:
            self.requiere_revision_manual = True

    def registrar_modificacion(self, nueva_respuesta: str) -> None:
        """Registra una modificación de la respuesta."""
        if not self.historial_respuestas:
            self.historial_respuestas = []

        self.historial_respuestas.append(
            {
                "respuesta_anterior": self.texto_respuesta,
                "fecha": datetime.now(UTC).isoformat(),
            }
        )

        self.texto_respuesta = nueva_respuesta
        self.numero_modificaciones = (self.numero_modificaciones or 0) + 1
        self.fecha_ultima_modificacion = datetime.now(UTC)

    def __repr__(self) -> str:
        return f"<RespuestaEstudiante(id='{self.id}', correcta={self.es_correcta}, puntos={self.puntuacion_obtenida})>"


# ==========================================
# MODELO: EVENTO ANTI-TRAMPA DETALLADO
# ==========================================


class EventoAntiTrampa(Base):
    """Registro detallado de eventos anti-trampa."""

    __tablename__ = "eventos_antitrampa"

    # ===== IDENTIFICACIÓN =====
    evento_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    intento_id = Column(
        UUID(as_uuid=True), ForeignKey("intentos_evaluacion.id", ondelete="CASCADE")
    )

    # ===== EVENTO =====
    tipo_evento = Column(String(100), nullable=False)  # Tipo específico
    categoria = Column(
        String(50)
    )  # navegacion, dispositivo, comportamiento, multimedia

    severidad = Column(String(20))  # info, advertencia, alta, critica
    peso = Column(Integer, default=1)  # Peso del evento para puntuación

    # ===== DETALLES =====
    descripcion = Column(Text)
    datos_evento = Column(JSON)  # Datos completos del evento

    timestamp = Column(DateTime(timezone=True), server_default=func.now())

    # ===== CONTEXTO =====
    pregunta_id = Column(UUID(as_uuid=True))  # Pregunta activa cuando ocurrió
    tiempo_transcurrido = Column(Integer)  # Segundos desde inicio del intento

    ip_address = Column(String(45))
    user_agent = Column(Text)

    # ===== ANÁLISIS =====
    es_sospechoso = Column(Boolean, default=False)
    requiere_revision = Column(Boolean, default=False)

    # ===== ACCIÓN TOMADA =====
    accion_tomada = Column(String(50))  # ninguna, alerta, pausar, terminar
    notificacion_enviada = Column(Boolean, default=False)

    # ===== RELACIONES =====
    # NOTA: IntentoEvaluacion no tiene relación eventos_detalle definida
    # intento = relationship("IntentoEvaluacion", back_populates="eventos_detalle")

    def __repr__(self) -> str:
        return f"<EventoAntiTrampa {self.tipo_evento} - {self.severidad}>"


# ==========================================
# MODELO: REGISTRO DE PUNTOS POR EVALUACIÓN
# ==========================================


class RegistroPuntosEvaluacion(Base):
    """Registro de puntos ganados en evaluaciones (para gamificación)."""

    __tablename__ = "registros_puntos_evaluacion"

    # ===== IDENTIFICACIÓN =====
    registro_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    usuario_id = Column(
        UUID(as_uuid=True), ForeignKey("Usuario.usuario_id"), nullable=False
    )  # Tabla Usuario con mayúscula
    evaluacion_id = Column(UUID(as_uuid=True), ForeignKey("evaluaciones.id"))
    intento_id = Column(UUID(as_uuid=True), ForeignKey("intentos_evaluacion.id"))

    # ===== PUNTOS =====
    puntos_base = Column(Integer, nullable=False)
    puntos_bonus = Column(Integer, default=0)
    multiplicador = Column(Float, default=1.0)
    puntos_totales = Column(Integer, nullable=False)

    # ===== DESGLOSE =====
    puntos_por_completar = Column(Integer, default=0)
    puntos_por_aciertos = Column(Integer, default=0)
    puntos_por_velocidad = Column(Integer, default=0)
    puntos_por_racha = Column(Integer, default=0)
    puntos_por_ranking = Column(Integer, default=0)

    # ===== METADATOS =====
    fecha_otorgamiento = Column(DateTime(timezone=True), server_default=func.now())
    descripcion = Column(Text)

    # ===== RELACIONES =====
    usuario = relationship("Usuario")
    evaluacion = relationship("Evaluacion")
    intento = relationship("IntentoEvaluacion")

    def __repr__(self) -> str:
        return f"<RegistroPuntosEvaluacion {self.puntos_totales} pts>"


# ==========================================
# MODELO: INSIGNIA GANADA POR EVALUACIÓN
# ==========================================


class InsigniaEvaluacion(Base):
    """Insignia ganada al completar evaluación."""

    __tablename__ = "insignias_evaluacion"

    # ===== IDENTIFICACIÓN =====
    insignia_evaluacion_id = Column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )

    usuario_id = Column(
        UUID(as_uuid=True), ForeignKey("Usuario.usuario_id"), nullable=False
    )  # Tabla Usuario con mayúscula
    evaluacion_id = Column(UUID(as_uuid=True), ForeignKey("evaluaciones.id"))
    insignia_id = Column(UUID(as_uuid=True))  # FK a sistema de insignias

    # ===== DATOS =====
    nombre_insignia = Column(String(200))
    descripcion = Column(Text)
    imagen_url = Column(String(500))

    fecha_obtencion = Column(DateTime(timezone=True), server_default=func.now())

    # ===== CRITERIOS CUMPLIDOS =====
    criterios_cumplidos = Column(JSON)  # Detalles de cómo se ganó

    # ===== RELACIONES =====
    usuario = relationship("Usuario")
    evaluacion = relationship("Evaluacion")

    def __repr__(self) -> str:
        return f"<InsigniaEvaluacion {self.nombre_insignia}>"


# ==========================================
# MODELO: RANKING DE EVALUACIÓN
# ==========================================


class RankingEvaluacion(Base):
    """Ranking de estudiantes en una evaluación competitiva."""

    __tablename__ = "ranking_evaluacion"

    # ===== IDENTIFICACIÓN =====
    ranking_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    evaluacion_id = Column(UUID(as_uuid=True), ForeignKey("evaluaciones.id"))
    usuario_id = Column(
        UUID(as_uuid=True), ForeignKey("Usuario.usuario_id")
    )  # Tabla Usuario con mayúscula
    intento_id = Column(UUID(as_uuid=True), ForeignKey("intentos_evaluacion.id"))

    # ===== POSICIÓN =====
    posicion = Column(Integer, nullable=False)
    posicion_anterior = Column(Integer)

    # ===== MÉTRICAS =====
    puntuacion = Column(Float, nullable=False)
    tiempo_total = Column(Integer, nullable=False)  # En segundos

    # Criterios de desempate
    respuestas_correctas_seguidas = Column(Integer, default=0)
    tiempo_primera_respuesta = Column(Integer)

    # ===== METADATOS =====
    fecha_actualizacion = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # ===== RELACIONES =====
    evaluacion = relationship("Evaluacion")
    usuario = relationship("Usuario")
    intento = relationship("IntentoEvaluacion")

    def __repr__(self) -> str:
        return f"<RankingEvaluacion Posición {self.posicion}>"
