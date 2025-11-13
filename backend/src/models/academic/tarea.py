from datetime import UTC
from enum import Enum
import uuid

from sqlalchemy import (
    JSON,
    NUMERIC,
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from src.db.base_class import Base


class EstadoTarea(str, Enum):
    ASIGNADA = "asignada"
    EN_PROGRESO = "en_progreso"
    ENTREGADA = "entregada"
    CALIFICADA = "calificada"
    VENCIDA = "vencida"
    CANCELADA = "cancelada"


class TipoTarea(str, Enum):
    ENSAYO = "ensayo"
    PROYECTO = "proyecto"
    EJERCICIOS = "ejercicios"
    INVESTIGACION = "investigacion"
    PRESENTACION = "presentacion"
    LABORATORIO = "laboratorio"
    LECTURA = "lectura"
    EXAMEN = "examen"
    OTRO = "otro"


class PrioridadTarea(str, Enum):
    BAJA = "baja"
    MEDIA = "media"
    ALTA = "alta"
    URGENTE = "urgente"


class Tarea(Base):
    """Modelo de Tarea Académica.

    Representa una tarea asignada a un grupo de estudiantes con funcionalidades completas:
    - Gestión de entregas y calificaciones
    - Integración con IA para retroalimentación
    - Sistema de rúbricas
    - Control de fechas y entregas tardías
    - Gamificación con puntos
    """

    __tablename__ = "tareas"

    # ============================================
    # IDENTIFICACIÓN Y RELACIONES
    # ============================================
    tarea_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    grupo_id = Column(
        String, ForeignKey("Grupo.grupo_id", ondelete="CASCADE"), nullable=False
    )
    docente_id = Column(
        String, ForeignKey("Usuario.usuario_id", ondelete="CASCADE"), nullable=False
    )
    clase_id = Column(
        String, ForeignKey("Clase.clase_id", ondelete="SET NULL"), nullable=True
    )

    # ============================================
    # INFORMACIÓN BÁSICA
    # ============================================
    titulo = Column(String(200), nullable=False)
    descripcion = Column(Text)
    instrucciones = Column(Text)
    objetivos = Column(Text)
    archivo_adjunto = Column(
        String(500), nullable=True
    )  # Archivo adjunto de la tarea (enunciado PDF, etc.)

    # ============================================
    # CLASIFICACIÓN
    # ============================================
    tipo = Column(String(13), nullable=True)  # Tipo de tarea (VARCHAR en BD)
    prioridad = Column(
        SQLEnum(PrioridadTarea), nullable=False, default=PrioridadTarea.MEDIA
    )
    tags = Column(String(500), nullable=True)

    # ============================================
    # FECHAS Y TIEMPO
    # ============================================
    fecha_asignacion = Column(DateTime(timezone=True), server_default=func.now())
    fecha_limite = Column(DateTime(timezone=True), nullable=False)
    fecha_inicio_disponible = Column(DateTime(timezone=True), nullable=True)
    tiempo_estimado = Column(Integer, nullable=True)

    # ============================================
    # CONFIGURACIÓN DE ENTREGA
    # ============================================
    permite_entrega_tardia = Column(Boolean, default=False)
    permite_entregas_tardias = Column(Boolean, default=False)  # Campo duplicado en BD
    penalizacion_tardia = Column(Float, default=0.0)
    intentos_maximos = Column(Integer, default=1)
    formato_entrega = Column(String(200), nullable=True)
    tamano_maximo_mb = Column(Float, default=10.0)
    restricciones_archivo = Column(
        JSONB, nullable=True
    )  # Restricciones detalladas de archivos

    # ============================================
    # CALIFICACIÓN Y PUNTUACIÓN
    # ============================================
    puntuacion_maxima = Column(Float, nullable=False, default=100.0)
    peso_evaluacion = Column(Float, default=1.0)
    peso_calificacion = Column(
        NUMERIC(5, 2), nullable=True
    )  # Peso en calificación final
    rubrica_id = Column(String, ForeignKey("rubricas.rubrica_id"), nullable=True)
    rubrica = Column(JSONB, nullable=True)  # Rúbrica en formato JSON
    criterios_evaluacion = Column(Text, nullable=True)

    # ============================================
    # GAMIFICACIÓN
    # ============================================
    puntos_base = Column(Integer, nullable=True)  # Puntos base por completar
    puntos_bonificacion = Column(Integer, nullable=True)  # Puntos extra por excelencia

    # ============================================
    # INTELIGENCIA ARTIFICIAL
    # ============================================
    habilitar_retroalimentacion_ia = Column(Boolean, default=False)
    prompt_ia_personalizado = Column(
        Text, nullable=True
    )  # Prompt personalizado para IA

    # ============================================
    # ESTADO Y CONFIGURACIÓN
    # ============================================
    estado = Column(
        String(11), nullable=False, default="asignada"
    )  # Campo VARCHAR en BD
    es_grupal = Column(Boolean, default=False)
    es_publica = Column(Boolean, default=True)
    requiere_aprobacion = Column(Boolean, default=False)
    activa = Column(Boolean, default=True)

    # ============================================
    # RECURSOS Y CONFIGURACIÓN
    # ============================================
    configuracion_json = Column(JSON, nullable=True)
    recursos_necesarios = Column(Text, nullable=True)

    # ============================================
    # AUDITORÍA Y METADATOS
    # ============================================
    fecha_creacion = Column(DateTime(timezone=True), server_default=func.now())
    fecha_actualizacion = Column(DateTime(timezone=True), onupdate=func.now())
    fecha_modificacion = Column(
        DateTime(timezone=True), nullable=True
    )  # Última modificación manual
    creado_por = Column(String, ForeignKey("Usuario.usuario_id"), nullable=True)
    actualizado_por = Column(String, ForeignKey("Usuario.usuario_id"), nullable=True)

    # Relaciones
    grupo = relationship("Grupo", back_populates="tareas")
    docente = relationship("Usuario", foreign_keys=[docente_id])
    entregas = relationship(
        "EntregaTarea", back_populates="tarea", cascade="all, delete-orphan"
    )
    rubrica_obj = relationship("Rubrica", back_populates="tareas", uselist=False)

    # Propiedades calculadas
    @property
    def total_entregas(self) -> int:
        """Número total de entregas recibidas."""
        return len([e for e in self.entregas if e.estado != "borrador"])

    @property
    def entregas_pendientes(self) -> int:
        """Número de entregas pendientes de calificación."""
        return len([e for e in self.entregas if e.estado == "entregada"])

    @property
    def promedio_calificaciones(self) -> float:
        """Promedio de las calificaciones otorgadas."""
        calificadas = [e for e in self.entregas if e.calificacion is not None]
        if not calificadas:
            return 0.0
        return sum(e.calificacion for e in calificadas) / len(calificadas)

    @property
    def esta_vencida(self) -> bool:
        """Indica si la fecha límite ya pasó."""
        from datetime import datetime

        return datetime.now(UTC) > self.fecha_limite if self.fecha_limite else False

    def to_dict(self):
        """Convertir a diccionario para API."""
        return {
            "tarea_id": self.tarea_id,
            "grupo_id": self.grupo_id,
            "docente_id": self.docente_id,
            "titulo": self.titulo,
            "descripcion": self.descripcion,
            "tipo": self.tipo,  # Campo real en BD
            "prioridad": self.prioridad.value if self.prioridad else None,
            "estado": self.estado,  # Campo VARCHAR en BD
            "fecha_limite": (
                self.fecha_limite.isoformat() if self.fecha_limite else None
            ),
            "puntuacion_maxima": self.puntuacion_maxima,
            "es_grupal": self.es_grupal,
            "total_entregas": self.total_entregas,
            "entregas_pendientes": self.entregas_pendientes,
            "esta_vencida": self.esta_vencida,
            "fecha_creacion": (
                self.fecha_creacion.isoformat() if self.fecha_creacion else None
            ),
        }


class EntregaTarea(Base):
    """Modelo de Entrega de Tarea con principios SOLID.

    Responsabilidades:
    - Gestionar información de entrega del estudiante
    - Tracking de intentos y fechas
    - Integración con IA para análisis y retroalimentación
    - Gestión de calificaciones (manual y preliminar IA)
    - Gamificación con puntos otorgados
    - Comentarios públicos y privados para docentes
    """

    __tablename__ = "entregas_tareas"

    # ============================================
    # IDENTIFICACIÓN Y RELACIONES
    # ============================================
    entrega_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    tarea_id = Column(
        String, ForeignKey("tareas.tarea_id", ondelete="CASCADE"), nullable=False
    )
    estudiante_id = Column(
        String, ForeignKey("Usuario.usuario_id", ondelete="CASCADE"), nullable=False
    )

    # ============================================
    # INFORMACIÓN DE ENTREGA
    # ============================================
    titulo_entrega = Column(String(200))
    descripcion_entrega = Column(Text)
    comentarios_estudiante = Column(Text)  # Comentarios del estudiante al entregar

    # ============================================
    # ARCHIVOS Y CONTENIDO
    # ============================================
    archivo_url = Column(String(500))  # URL del archivo principal
    archivo_metadata = Column(
        JSONB, nullable=True
    )  # Metadatos del archivo (tamaño, tipo, hash)
    archivos_adicionales = Column(JSON)  # Lista de archivos adicionales
    contenido_texto = Column(Text)  # Para entregas de texto plano
    enlaces_externos = Column(JSON)  # Enlaces a recursos externos (GitHub, etc.)

    # ============================================
    # FECHAS Y CONTROL DE INTENTOS
    # ============================================
    fecha_entrega = Column(DateTime(timezone=True))
    fecha_limite_original = Column(
        DateTime(timezone=True)
    )  # Para tracking de entregas tardías
    numero_intento = Column(Integer, default=1)
    intentos = Column(Integer, nullable=True)  # Total de intentos realizados
    es_entrega_tardia = Column(Boolean, default=False)
    es_tardia = Column(Boolean, default=False)  # Campo duplicado en BD (legacy)

    # ============================================
    # CALIFICACIÓN MANUAL (DOCENTE)
    # ============================================
    calificacion = Column(Float)  # Nota numérica final
    calificacion_letras = Column(String(5))  # A, B, C, D, F
    comentarios_docente = Column(Text)  # Retroalimentación del docente
    retroalimentacion_docente = Column(
        Text, nullable=True
    )  # Retroalimentación detallada
    rubrica_calificacion = Column(JSON)  # Calificación detallada por rúbrica
    comentarios_privados = Column(Text, nullable=True)  # Notas privadas para docentes

    # ============================================
    # CALIFICACIÓN PRELIMINAR IA
    # ============================================
    calificacion_preliminar_ia = Column(
        NUMERIC(5, 2), nullable=True
    )  # Calificación sugerida por IA
    retroalimentacion_ia = Column(JSONB, nullable=True)  # Análisis completo de IA

    # ============================================
    # GAMIFICACIÓN
    # ============================================
    puntos_otorgados = Column(
        Integer, nullable=True
    )  # Puntos de gamificación otorgados

    # ============================================
    # ESTADO Y CONFIGURACIÓN
    # ============================================
    estado = Column(
        String(50), default="borrador"
    )  # borrador, entregada, calificada, devuelta
    es_final = Column(Boolean, default=False)  # Si es la entrega final
    requiere_revision = Column(Boolean, default=False)  # Si necesita revisión adicional

    # ============================================
    # METADATOS DE EVALUACIÓN (ESTUDIANTE)
    # ============================================
    tiempo_empleado = Column(Integer)  # Tiempo empleado en minutos (self-reported)
    dificultad_percibida = Column(Integer)  # 1-5, qué tan difícil percibió la tarea
    satisfaccion_estudiante = Column(
        Integer
    )  # 1-5, qué tan satisfecho está con su entrega

    # ============================================
    # AUDITORÍA Y METADATOS
    # ============================================
    fecha_creacion = Column(DateTime(timezone=True), server_default=func.now())
    fecha_actualizacion = Column(DateTime(timezone=True), onupdate=func.now())
    calificado_por = Column(String, ForeignKey("Usuario.usuario_id"), nullable=True)
    fecha_calificacion = Column(DateTime(timezone=True))

    # ============================================
    # RELACIONES
    # ============================================
    tarea = relationship("src.models.academic.tarea.Tarea", back_populates="entregas")
    estudiante = relationship("Usuario", foreign_keys=[estudiante_id])
    calificador = relationship("Usuario", foreign_keys=[calificado_por])

    # ============================================
    # PROPIEDADES CALCULADAS (Single Responsibility)
    # ============================================

    @property
    def dias_desde_entrega(self) -> int:
        """Días transcurridos desde la entrega."""
        if not self.fecha_entrega:
            return 0
        from datetime import datetime

        return (datetime.now(UTC) - self.fecha_entrega).days

    @property
    def porcentaje_calificacion(self) -> float:
        """Calificación como porcentaje."""
        if not self.calificacion or not self.tarea:
            return 0.0
        return (self.calificacion / self.tarea.puntuacion_maxima) * 100

    @property
    def tiene_retroalimentacion_ia(self) -> bool:
        """Indica si tiene retroalimentación de IA disponible."""
        return (
            self.retroalimentacion_ia is not None and len(self.retroalimentacion_ia) > 0
        )

    @property
    def tiene_calificacion_preliminar(self) -> bool:
        """Indica si tiene calificación preliminar de IA."""
        return self.calificacion_preliminar_ia is not None

    @property
    def diferencia_calificacion_ia(self) -> float:
        """Diferencia entre calificación final y preliminar IA."""
        if not self.calificacion or not self.calificacion_preliminar_ia:
            return 0.0
        return float(self.calificacion - self.calificacion_preliminar_ia)

    @property
    def esta_calificada(self) -> bool:
        """Indica si la entrega ya fue calificada."""
        return self.calificacion is not None and self.estado == "calificada"

    @property
    def pendiente_revision(self) -> bool:
        """Indica si está pendiente de revisión."""
        return self.estado == "entregada" or self.requiere_revision

    @property
    def intentos_restantes(self) -> int:
        """Intentos restantes si la tarea permite múltiples intentos."""
        if not self.tarea or not self.tarea.intentos_maximos:
            return 0
        return max(
            0, self.tarea.intentos_maximos - (self.intentos or self.numero_intento)
        )

    @property
    def puede_reintentar(self) -> bool:
        """Indica si el estudiante puede hacer otro intento."""
        return self.intentos_restantes > 0 and not self.es_final

    @property
    def tiene_archivos(self) -> bool:
        """Indica si tiene archivos adjuntos."""
        return bool(
            self.archivo_url
            or (self.archivos_adicionales and len(self.archivos_adicionales) > 0)
        )

    # ============================================
    # PROPIEDADES DE COMPATIBILIDAD CON LEGACY
    # Para transición desde EntregarTarea (src.models.classes)
    # ============================================

    @property
    def archivo(self) -> str | None:
        """Alias de compatibilidad: archivo -> archivo_url."""
        return self.archivo_url

    @archivo.setter
    def archivo(self, value: str) -> None:
        """Setter de compatibilidad: archivo -> archivo_url."""
        self.archivo_url = value

    @property
    def fecha_envio(self):
        """Alias de compatibilidad: fecha_envio -> fecha_entrega."""
        return self.fecha_entrega

    @fecha_envio.setter
    def fecha_envio(self, value) -> None:
        """Setter de compatibilidad: fecha_envio -> fecha_entrega."""
        self.fecha_entrega = value

    # ============================================
    # MÉTODOS DE NEGOCIO (Open/Closed Principle)
    # ============================================

    def aplicar_calificacion_ia(
        self, calificacion_ia: float, retroalimentacion: dict
    ) -> None:
        """Aplicar calificación preliminar de IA.

        Args:
            calificacion_ia: Calificación sugerida por IA (0-100)
            retroalimentacion: Objeto JSON con análisis completo
        """
        self.calificacion_preliminar_ia = calificacion_ia
        self.retroalimentacion_ia = retroalimentacion

    def calificar_manualmente(
        self,
        calificacion: float,
        comentarios: str | None = None,
        rubrica: dict | None = None,
        calificado_por: str | None = None,
    ) -> None:
        """Calificar la entrega manualmente (docente).

        Args:
            calificacion: Nota final (0-100)
            comentarios: Retroalimentación del docente
            rubrica: Calificación detallada por rúbrica
            calificado_por: ID del docente que califica
        """
        from datetime import datetime

        self.calificacion = calificacion
        self.comentarios_docente = comentarios
        self.rubrica_calificacion = rubrica
        self.calificado_por = calificado_por
        self.fecha_calificacion = datetime.now(UTC)
        self.estado = "calificada"
        self.requiere_revision = False

    def marcar_para_revision(self, comentario_privado: str | None = None) -> None:
        """Marcar entrega para revisión adicional."""
        self.requiere_revision = True
        if comentario_privado:
            self.comentarios_privados = comentario_privado

    def otorgar_puntos(self, puntos: int) -> None:
        """Otorgar puntos de gamificación.

        Args:
            puntos: Cantidad de puntos a otorgar
        """
        self.puntos_otorgados = puntos

    def finalizar_entrega(self) -> None:
        """Marcar entrega como final (no se permiten más intentos)."""
        self.es_final = True

    def to_dict(self):
        """Convertir a diccionario para API (Interface Segregation)."""
        return {
            "entrega_id": self.entrega_id,
            "tarea_id": self.tarea_id,
            "estudiante_id": self.estudiante_id,
            "titulo_entrega": self.titulo_entrega,
            "estado": self.estado,
            "fecha_entrega": (
                self.fecha_entrega.isoformat() if self.fecha_entrega else None
            ),
            "calificacion": self.calificacion,
            "calificacion_preliminar_ia": (
                float(self.calificacion_preliminar_ia)
                if self.calificacion_preliminar_ia
                else None
            ),
            "es_entrega_tardia": self.es_entrega_tardia,
            "numero_intento": self.numero_intento,
            "intentos_restantes": self.intentos_restantes,
            "tiene_retroalimentacion_ia": self.tiene_retroalimentacion_ia,
            "esta_calificada": self.esta_calificada,
            "pendiente_revision": self.pendiente_revision,
            "puede_reintentar": self.puede_reintentar,
            "puntos_otorgados": self.puntos_otorgados,
            "fecha_creacion": (
                self.fecha_creacion.isoformat() if self.fecha_creacion else None
            ),
            "porcentaje_calificacion": self.porcentaje_calificacion,
        }


class Rubrica(Base):
    __tablename__ = "rubricas"

    # Clave primaria
    rubrica_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))

    # Información básica
    nombre = Column(String(200), nullable=False)
    descripcion = Column(Text)

    # Criterios de evaluación (JSON)
    criterios = Column(
        JSON, nullable=False
    )  # Lista de criterios con niveles y puntuaciones

    # Configuración
    puntuacion_total = Column(Float, nullable=False, default=100.0)
    es_publica = Column(Boolean, default=True)  # Si puede ser usada por otros docentes
    es_plantilla = Column(Boolean, default=False)  # Si es una plantilla predefinida

    # Metadatos
    activa = Column(Boolean, default=True)
    fecha_creacion = Column(DateTime(timezone=True), server_default=func.now())
    fecha_actualizacion = Column(DateTime(timezone=True), onupdate=func.now())
    creado_por = Column(String, ForeignKey("Usuario.usuario_id"), nullable=False)

    # Relaciones
    tareas = relationship(
        "src.models.academic.tarea.Tarea", back_populates="rubrica_obj"
    )
    creador = relationship("Usuario", foreign_keys=[creado_por])

    def to_dict(self):
        """Convertir a diccionario para API."""
        return {
            "rubrica_id": self.rubrica_id,
            "nombre": self.nombre,
            "descripcion": self.descripcion,
            "criterios": self.criterios,
            "puntuacion_total": self.puntuacion_total,
            "es_publica": self.es_publica,
            "fecha_creacion": (
                self.fecha_creacion.isoformat() if self.fecha_creacion else None
            ),
        }
