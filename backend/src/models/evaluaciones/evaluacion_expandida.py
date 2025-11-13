"""Sistema de Evaluaciones - Modelos Sincronizados con BD.

Este módulo contiene los modelos principales del sistema de evaluaciones,
100% sincronizados con las tablas reales de la base de datos.

Incluye:
- Evaluacion: Modelo principal de evaluaciones/exámenes (82 campos)
- PreguntaEvaluacion: Preguntas asociadas a evaluaciones (42 campos)

Principios aplicados:
- Single Responsibility: Cada modelo tiene una responsabilidad clara
- Open/Closed: Extensible mediante herencia y composición
- Liskov Substitution: Interfaces consistentes
- Interface Segregation: Propiedades y métodos cohesivos
- Dependency Inversion: Dependencias mediante relaciones ORM

Versión: 2.0 (Sincronizado con BD - 2025-11-04)
"""

from datetime import UTC, datetime
from typing import Any

from sqlalchemy import (
    JSON,
    Boolean,
    CheckConstraint,
    Column,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import DOUBLE_PRECISION, TIMESTAMP
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from src.db.base_class import Base


class Evaluacion(Base):
    """Modelo principal de evaluaciones/exámenes.

    Representa una evaluación completa con:
    - Configuración de tiempo y fechas
    - Sistema de calificación
    - Medidas antitrampa
    - Gamificación e IA
    - Estadísticas

    Estados: borrador, programada, activa, pausada, finalizada, cerrada
    """

    __tablename__ = "evaluaciones"

    # ===== IDENTIFICACIÓN =====
    id = Column(String, primary_key=True, index=True)
    curso_id = Column(
        String,
        ForeignKey("Curso.curso_id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )
    grupo_id = Column(
        String,
        ForeignKey("Grupo.grupo_id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )
    creador_id = Column(
        String, ForeignKey("Usuario.usuario_id"), nullable=False, index=True
    )
    configuracion_antitrampa_id = Column(
        String(36),
        # FIXME: Tabla configuraciones_antitrampa no existe aún
        # ForeignKey("configuraciones_antitrampa.id"),
        nullable=True,
        index=True,
    )
    insignia_id = Column(String(36), nullable=True, index=True)

    # ===== BÁSICO =====
    titulo = Column(String(200), nullable=False, index=True)
    descripcion = Column(Text, nullable=True)
    instrucciones = Column(Text, nullable=True)

    # ===== TIPO Y MODO =====
    tipo_examen = Column(String(50), nullable=False, default="evaluacion", index=True)
    tipo_evaluacion = Column(String(50), nullable=True)
    modo_evaluacion = Column(String(50), nullable=True, default="standard")
    tipo_calificacion = Column(String(50), nullable=True, default="automatica")
    modo_pantalla_completa = Column(Boolean, nullable=True, default=False)

    # ===== ESTADO =====
    estado_examen = Column(String(50), nullable=False, default="borrador", index=True)
    estado = Column(String(50), nullable=True)
    visibilidad = Column(String(50), nullable=True, default="curso")

    # ===== TIEMPO =====
    tiempo_limite_minutos = Column(Integer, nullable=False, default=60)
    fecha_inicio = Column(TIMESTAMP(timezone=True), nullable=True)
    fecha_limite = Column(TIMESTAMP(timezone=True), nullable=True)
    fecha_apertura = Column(TIMESTAMP(timezone=True), nullable=True)
    fecha_cierre = Column(TIMESTAMP(timezone=True), nullable=True)
    fecha_publicacion = Column(TIMESTAMP(timezone=True), nullable=True)
    fecha_publicacion_resultados = Column(TIMESTAMP(timezone=True), nullable=True)
    tiempo_entre_intentos_minutos = Column(Integer, nullable=True, default=0)
    advertencia_tiempo_restante = Column(Boolean, nullable=True, default=True)
    tiempo_maximo_inactividad = Column(Integer, nullable=True)
    tiempo_promedio_minutos = Column(DOUBLE_PRECISION, nullable=True)

    # ===== PREGUNTAS =====
    total_preguntas = Column(Integer, nullable=True, default=0)
    num_preguntas_mostrar = Column(Integer, nullable=True)
    randomizar_preguntas = Column(Boolean, nullable=True, default=False)
    randomizar_opciones = Column(Boolean, nullable=True, default=False)
    una_pregunta_por_vez = Column(Boolean, nullable=True, default=False)

    # ===== CALIFICACIÓN =====
    puntuacion_total = Column(DOUBLE_PRECISION, nullable=False, default=100.0)
    puntuacion_minima_aprobacion = Column(DOUBLE_PRECISION, nullable=True, default=60.0)
    calificacion_automatica = Column(Boolean, nullable=True, default=True)
    usar_ia_calificacion = Column(Boolean, nullable=True, default=False)
    rubrica_ia = Column(JSON, nullable=True)
    promedio_calificacion = Column(DOUBLE_PRECISION, nullable=True)
    distribucion_calificaciones = Column(JSON, nullable=True)

    # ===== GAMIFICACIÓN =====
    otorga_puntos = Column(Boolean, nullable=True, default=False)
    puntos_base = Column(Integer, nullable=True, default=0)
    puntos_por_acierto = Column(Integer, nullable=True, default=0)
    puntos_por_tiempo = Column(Boolean, nullable=True, default=False)
    multiplicador_puntos = Column(DOUBLE_PRECISION, nullable=True, default=1.0)
    otorga_insignia = Column(Boolean, nullable=True, default=False)

    # ===== SEGURIDAD =====
    codigo_acceso = Column(String(20), nullable=True)
    contrasena = Column(String(255), nullable=True)
    contraseña_acceso = Column(String(100), nullable=True)
    requiere_contraseña = Column(Boolean, nullable=True, default=False)
    detectar_cambio_pestana = Column(Boolean, nullable=True, default=False)
    bloquear_navegacion = Column(Boolean, nullable=True, default=False)
    permitir_navegar_atras = Column(Boolean, nullable=True, default=True)
    permitir_pausar = Column(Boolean, nullable=True, default=False)
    permitir_revision = Column(Boolean, nullable=True, default=True)
    requerir_camara = Column(Boolean, nullable=True, default=False)
    grabar_camara_continuo = Column(Boolean, nullable=True, default=False)
    requerir_microfono = Column(Boolean, nullable=True, default=False)
    grabar_audio_continuo = Column(Boolean, nullable=True, default=False)
    permitir_grabacion_pantalla = Column(Boolean, nullable=True, default=False)
    verificar_identidad_facial = Column(Boolean, nullable=True, default=False)

    # ===== INTENTOS =====
    intentos_permitidos = Column(Integer, nullable=True, default=1)
    total_intentos = Column(Integer, nullable=True, default=0)
    max_pausas = Column(Integer, nullable=True)

    # ===== VISUALIZACIÓN =====
    mostrar_resultados_inmediatos = Column(Boolean, nullable=True, default=False)
    mostrar_respuestas_correctas = Column(Boolean, nullable=True, default=False)
    mostrar_progreso = Column(Boolean, nullable=True, default=True)

    # ===== FEEDBACK =====
    generar_feedback_ia = Column(Boolean, nullable=True, default=False)
    feedback_personalizado = Column(Boolean, nullable=True, default=False)

    # ===== IA =====
    es_adaptativa = Column(Boolean, nullable=True, default=False)
    nivel_dificultad_inicial = Column(String(50), nullable=True)
    minutos_advertencia = Column(Integer, nullable=True, default=5)

    # ===== COLABORACIÓN =====
    es_colaborativa = Column(Boolean, nullable=True, default=False)
    max_miembros_equipo = Column(Integer, nullable=True)
    permitir_peer_review = Column(Boolean, nullable=True, default=False)
    num_peer_reviews_requeridos = Column(Integer, nullable=True)

    # ===== ESTADÍSTICAS =====
    total_completados = Column(Integer, nullable=True, default=0)
    tasa_completacion = Column(DOUBLE_PRECISION, nullable=True)
    tasa_aprobacion = Column(DOUBLE_PRECISION, nullable=True)

    # ===== CONFIGURACIÓN =====
    configuracion_avanzada = Column(JSON, nullable=True)

    # ===== AUDITORÍA =====
    fecha_creacion = Column(
        TIMESTAMP(timezone=True), nullable=True, server_default=func.now()
    )
    fecha_modificacion = Column(
        TIMESTAMP(timezone=True),
        nullable=True,
        server_default=func.now(),
        onupdate=func.now(),
    )

    # ===== RELACIONES =====
    curso = relationship("Curso", foreign_keys=[curso_id], backref="evaluaciones")
    grupo = relationship("Grupo", foreign_keys=[grupo_id], backref="evaluaciones")
    creador = relationship(
        "Usuario", foreign_keys=[creador_id], backref="evaluaciones_creadas"
    )
    # NOTA: ConfiguracionAntiTrampa comentada - tabla no existe actualmente en BD
    # configuracion_antitrampa = relationship(
    #     "ConfiguracionAntiTrampa",
    #     foreign_keys=[configuracion_antitrampa_id],
    #     backref="evaluaciones",
    # )
    preguntas = relationship(
        "PreguntaEvaluacion",
        back_populates="evaluacion",
        cascade="all, delete-orphan",
        passive_deletes=True,
        lazy="dynamic",
    )

    # ===== CONSTRAINTS =====
    __table_args__ = (
        CheckConstraint("puntuacion_total >= 0", name="check_puntuacion_positiva"),
        CheckConstraint("tiempo_limite_minutos >= 0", name="check_tiempo_positivo"),
    )

    # ===== PROPIEDADES =====
    @property
    def esta_activa(self) -> bool:
        return self.estado_examen == "activa"

    @property
    def esta_disponible(self) -> bool:
        if self.estado_examen != "activa":
            return False
        ahora = datetime.now(UTC)
        if self.fecha_apertura and ahora < self.fecha_apertura:
            return False
        return not (self.fecha_cierre and ahora > self.fecha_cierre)

    @property
    def requiere_antitrampa(self) -> bool:
        return (
            self.configuracion_antitrampa_id is not None
            or self.detectar_cambio_pestana
            or self.modo_pantalla_completa
            or self.requerir_camara
            or self.verificar_identidad_facial
        )

    # ===== MÉTODOS =====
    def activar(self) -> None:
        if self.estado_examen == "programada":
            self.estado_examen = "activa"
            if not self.fecha_apertura:
                self.fecha_apertura = datetime.now(UTC)

    def finalizar(self) -> None:
        self.estado_examen = "finalizada"
        if not self.fecha_cierre:
            self.fecha_cierre = datetime.now(UTC)

    def calcular_estadisticas(self, intentos: list[Any]) -> None:
        if not intentos:
            return
        self.total_completados = len([i for i in intentos if i.estado == "finalizado"])
        self.total_intentos = len(intentos)
        if self.total_completados > 0:
            calificaciones = [
                i.puntuacion_obtenida for i in intentos if i.puntuacion_obtenida
            ]
            if calificaciones:
                self.promedio_calificacion = sum(calificaciones) / len(calificaciones)
                aprobados = len(
                    [
                        c
                        for c in calificaciones
                        if c >= (self.puntuacion_minima_aprobacion or 60)
                    ]
                )
                self.tasa_aprobacion = (aprobados / len(calificaciones)) * 100
            self.tasa_completacion = (
                self.total_completados / self.total_intentos
            ) * 100

    def __repr__(self) -> str:
        return f"<Evaluacion(id='{self.id}', titulo='{self.titulo}', estado='{self.estado_examen}')>"


class PreguntaEvaluacion(Base):
    """Pregunta asociada a una evaluación.

    Tipos: opcion_multiple, seleccion_multiple, verdadero_falso,
    respuesta_corta, ensayo, completar_blancos, codigo, formula, etc.

    Soporta multimedia, interactividad, IA para evaluación automática,
    y configuración avanzada para diferentes tipos de pregunta.
    """

    __tablename__ = "preguntas_evaluacion"

    # ===== IDENTIFICACIÓN =====
    id = Column(String, primary_key=True, index=True)
    evaluacion_id = Column(
        String,
        ForeignKey("evaluaciones.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    banco_pregunta_id = Column(
        String, ForeignKey("banco_preguntas.pregunta_id"), nullable=True, index=True
    )

    # ===== INFORMACIÓN BÁSICA =====
    titulo = Column(String(200), nullable=True)
    enunciado = Column(Text, nullable=False)
    descripcion = Column(Text, nullable=True)

    # ===== CONFIGURACIÓN =====
    tipo_pregunta = Column(String(50), nullable=False, default="opcion_multiple")
    dificultad = Column(String(20), nullable=True, default="intermedio")
    orden = Column(Integer, nullable=False, default=1)
    es_obligatoria = Column(Boolean, nullable=True, default=True)

    # ===== PUNTUACIÓN =====
    puntuacion = Column(DOUBLE_PRECISION, nullable=False, default=1.0)
    puntos_respuesta_parcial = Column(DOUBLE_PRECISION, nullable=True)

    # ===== RESPUESTAS =====
    opciones_respuesta = Column(JSON, nullable=True)
    respuesta_correcta = Column(JSON, nullable=True)
    respuestas_alternativas = Column(JSON, nullable=True)

    # ===== FEEDBACK =====
    explicacion = Column(Text, nullable=True)
    feedback_correcto = Column(Text, nullable=True)
    feedback_incorrecto = Column(Text, nullable=True)
    solucion_referencia = Column(Text, nullable=True)

    # ===== MULTIMEDIA =====
    imagen_url = Column(String(500), nullable=True)
    video_url = Column(String(500), nullable=True)
    audio_url = Column(String(500), nullable=True)
    archivos_adjuntos = Column(JSON, nullable=True)

    # ===== TIEMPO =====
    tiempo_limite_segundos = Column(Integer, nullable=True)
    tiempo_promedio_respuesta = Column(DOUBLE_PRECISION, nullable=True)

    # ===== MATEMÁTICAS Y FÓRMULAS =====
    formula_latex = Column(Text, nullable=True)
    variables_formula = Column(JSON, nullable=True)
    tolerancia_numerica = Column(DOUBLE_PRECISION, nullable=True)

    # ===== PROGRAMACIÓN =====
    lenguaje_codigo = Column(String(50), nullable=True)
    plantilla_codigo = Column(Text, nullable=True)
    tests_unitarios = Column(JSON, nullable=True)

    # ===== INTERACTIVIDAD =====
    tipo_interaccion = Column(String(50), nullable=True)
    configuracion_interactiva = Column(JSON, nullable=True)

    # ===== IA =====
    criterios_evaluacion_ia = Column(JSON, nullable=True)
    configuracion_ia = Column(JSON, nullable=True)

    # ===== METADATOS =====
    tags = Column(JSON, nullable=True)
    etiquetas = Column(JSON, nullable=True)
    metadata_extra = Column("metadata", JSON, nullable=True)

    # ===== ESTADÍSTICAS =====
    veces_utilizada = Column(Integer, nullable=True, default=0)
    promedio_aciertos = Column(DOUBLE_PRECISION, nullable=True)

    # ===== AUDITORÍA =====
    fecha_creacion = Column(
        TIMESTAMP(timezone=True), nullable=True, server_default=func.now()
    )
    fecha_actualizacion = Column(
        TIMESTAMP(timezone=True),
        nullable=True,
        server_default=func.now(),
        onupdate=func.now(),
    )

    # ===== RELACIONES =====
    evaluacion = relationship("Evaluacion", back_populates="preguntas")
    banco_pregunta = relationship(
        "BancoPregunta",
        foreign_keys=[banco_pregunta_id],
        backref="preguntas_evaluacion",
    )

    # ===== PROPIEDADES =====
    @property
    def permite_respuesta_parcial(self) -> bool:
        return (
            self.puntos_respuesta_parcial is not None
            and self.puntos_respuesta_parcial > 0
        )

    @property
    def tiene_multimedia(self) -> bool:
        return bool(
            self.imagen_url
            or self.video_url
            or self.audio_url
            or self.archivos_adjuntos
        )

    def __repr__(self) -> str:
        return f"<PreguntaEvaluacion(id='{self.id}', tipo='{self.tipo_pregunta}', puntuacion={self.puntuacion})>"
