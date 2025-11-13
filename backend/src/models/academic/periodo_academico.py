"""Modelo de Período Académico.

Define la estructura temporal en que se organizan los programas académicos.
Un período puede ser: semestre, trimestre, bimestre, módulo, año, etc.
"""

from datetime import date

from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from src.db.base_class import Base


class PeriodoAcademico(Base):
    """Período académico de una institución.

    Representa el marco temporal en que se organizan los cursos/programas.
    Ejemplos: Semestre 2024-1, Trimestre Q1-2024, Módulo Intensivo Jun-2024.

    Universal para:
    - Universidades: Semestres/trimestres/anuales
    - SENA: Fichas/convocatorias/trimestres
    - Escuelas de idiomas: Módulos/intensivos/mensuales
    - Colegios: Años/períodos/bimestres
    """

    __tablename__ = "periodos_academicos"

    # ==================== Identificación ====================
    id = Column(Integer, primary_key=True, index=True)
    institucion_id = Column(
        UUID(as_uuid=True),
        ForeignKey("Institucion.institucion_id"),
        nullable=False,
        index=True,
    )

    # Información básica
    nombre = Column(String(200), nullable=False)  # "Semestre 2024-1", "Ficha 2893156"
    codigo = Column(String(50), unique=True, index=True)  # "2024-1", "F2893156"
    descripcion = Column(Text, nullable=True)

    # ==================== Tipo y Clasificación ====================
    tipo = Column(String(50), nullable=False)  # TipoPeriodo enum
    estado = Column(
        String(50), nullable=False, default="programado"
    )  # EstadoPeriodo enum

    # Metadata adicional
    anio = Column(Integer, nullable=False, index=True)  # 2024
    numero_periodo = Column(
        Integer, nullable=True
    )  # 1, 2, 3... (período dentro del año)
    nivel_aplica = Column(
        String(100), nullable=True
    )  # A qué nivel/programa aplica (opcional)

    # ==================== Fechas Críticas ====================
    # Período completo
    fecha_inicio = Column(Date, nullable=False, index=True)
    fecha_fin = Column(Date, nullable=False, index=True)

    # Inscripciones
    fecha_inicio_preinscripciones = Column(Date, nullable=True)
    fecha_fin_preinscripciones = Column(Date, nullable=True)
    fecha_inicio_inscripciones = Column(Date, nullable=False)
    fecha_fin_inscripciones = Column(Date, nullable=False)

    # Ajustes
    fecha_inicio_ajustes = Column(Date, nullable=True)  # Agregar/retirar cursos
    fecha_fin_ajustes = Column(Date, nullable=True)

    # Clases
    fecha_inicio_clases = Column(Date, nullable=False)
    fecha_fin_clases = Column(Date, nullable=False)

    # Retiros
    fecha_limite_retiro = Column(Date, nullable=True)  # Último día para retirarse
    fecha_limite_retiro_con_reembolso = Column(Date, nullable=True)

    # Evaluaciones
    fecha_inicio_examenes = Column(Date, nullable=True)
    fecha_fin_examenes = Column(Date, nullable=True)

    # Calificaciones
    fecha_cierre_notas = Column(Date, nullable=True)
    fecha_publicacion_notas = Column(Date, nullable=True)

    # ==================== Configuración ====================
    # Capacidades
    permite_inscripciones = Column(Boolean, default=True, nullable=False)
    permite_ajustes = Column(Boolean, default=True, nullable=False)
    permite_retiros = Column(Boolean, default=True, nullable=False)

    # Visibilidad
    visible_estudiantes = Column(Boolean, default=True, nullable=False)
    visible_profesores = Column(Boolean, default=True, nullable=False)
    visible_publico = Column(Boolean, default=False, nullable=False)

    # Números y límites
    creditos_minimos = Column(Integer, nullable=True)  # Mínimo de créditos a inscribir
    creditos_maximos = Column(Integer, nullable=True)  # Máximo de créditos a inscribir
    cursos_minimos = Column(Integer, nullable=True)
    cursos_maximos = Column(Integer, nullable=True)

    # Costos (opcional, depende institución)
    costo_matricula = Column(Numeric(10, 2), nullable=True)
    costo_por_credito = Column(Numeric(10, 2), nullable=True)
    moneda = Column(String(10), default="COP")  # COP, USD, EUR, etc.

    # ==================== Metadata y Configuración ====================
    # Calendario académico adicional
    dias_festivos = Column(JSON, nullable=True)  # ["2024-01-15", "2024-03-25"]
    vacaciones = Column(
        JSON, nullable=True
    )  # [{"inicio": "...", "fin": "...", "tipo": "..."}]

    # Configuración específica
    configuracion = Column(JSON, nullable=True)  # Config flexible por institución
    notas = Column(Text, nullable=True)

    # ==================== Estado y Control ====================
    activo = Column(Boolean, default=True, nullable=False, index=True)
    es_actual = Column(
        Boolean, default=False, nullable=False, index=True
    )  # Período en curso

    # Auditoría
    creado_por_id = Column(
        UUID(as_uuid=True), ForeignKey("Usuario.usuario_id"), nullable=True
    )
    modificado_por_id = Column(
        UUID(as_uuid=True), ForeignKey("Usuario.usuario_id"), nullable=True
    )
    fecha_creacion = Column(DateTime, nullable=False, server_default=func.now())
    fecha_actualizacion = Column(
        DateTime, nullable=False, server_default=func.now(), onupdate=func.now()
    )

    # ==================== Relaciones ====================
    # NOTA: Institucion no tiene relación periodos_academicos definida
    # institucion = relationship("Institucion", back_populates="periodos_academicos")
    creado_por = relationship("Usuario", foreign_keys=[creado_por_id])
    modificado_por = relationship("Usuario", foreign_keys=[modificado_por_id])

    # Relaciones con otros modelos (se agregarán cuando se creen)
    # grupos = relationship("Grupo", back_populates="periodo_academico")
    # inscripciones = relationship("Inscripcion", back_populates="periodo_academico")
    # evaluaciones = relationship("Evaluacion", back_populates="periodo_academico")

    # ==================== Properties ====================
    @property
    def nombre_completo(self) -> str:
        """Nombre completo del período."""
        return f"{self.nombre} ({self.anio})"

    @property
    def esta_activo(self) -> bool:
        """Verifica si el período está activo."""
        return self.activo and self.estado != "cancelado"

    @property
    def permite_inscribirse_ahora(self) -> bool:
        """Verifica si actualmente se permiten inscripciones."""
        if not self.permite_inscripciones:
            return False

        hoy = date.today()
        return (
            self.fecha_inicio_inscripciones <= hoy <= self.fecha_fin_inscripciones
            and self.estado in ["inscripciones_abiertas", "preinscripciones"]
        )

    @property
    def esta_en_curso(self) -> bool:
        """Verifica si el período está en curso actualmente."""
        hoy = date.today()
        return (
            self.fecha_inicio_clases <= hoy <= self.fecha_fin_clases
            and self.estado == "en_curso"
        )

    @property
    def dias_hasta_inicio(self) -> int | None:
        """Días faltantes hasta el inicio de clases."""
        if not self.fecha_inicio_clases:
            return None
        hoy = date.today()
        if hoy > self.fecha_inicio_clases:
            return 0
        return (self.fecha_inicio_clases - hoy).days

    @property
    def dias_transcurridos(self) -> int | None:
        """Días transcurridos desde inicio de clases."""
        if not self.fecha_inicio_clases:
            return None
        hoy = date.today()
        if hoy < self.fecha_inicio_clases:
            return 0
        return (hoy - self.fecha_inicio_clases).days

    @property
    def duracion_dias(self) -> int | None:
        """Duración total del período en días."""
        if not self.fecha_inicio or not self.fecha_fin:
            return None
        return (self.fecha_fin - self.fecha_inicio).days

    @property
    def porcentaje_avance(self) -> float | None:
        """Porcentaje de avance del período (0-100)."""
        if not self.esta_en_curso:
            return None

        total = (self.fecha_fin_clases - self.fecha_inicio_clases).days
        transcurrido = self.dias_transcurridos

        if total <= 0:
            return 0.0

        return min(100.0, (transcurrido / total) * 100)

    # ==================== Métodos ====================
    def activar(self) -> None:
        """Activa el período."""
        self.activo = True
        self.estado = "programado" if date.today() < self.fecha_inicio else "en_curso"

    def desactivar(self) -> None:
        """Desactiva el período."""
        self.activo = False

    def marcar_como_actual(self) -> None:
        """Marca este período como el actual."""
        self.es_actual = True
        self.activo = True

    def finalizar(self) -> None:
        """Finaliza el período."""
        self.estado = "finalizado"
        self.es_actual = False

    def cancelar(self, motivo: str | None = None) -> None:
        """Cancela el período."""
        self.estado = "cancelado"
        self.activo = False
        self.es_actual = False
        if motivo and self.notas:
            self.notas += f"\n[CANCELACIÓN] {motivo}"
        elif motivo:
            self.notas = f"[CANCELACIÓN] {motivo}"

    def puede_inscribirse_estudiante(self) -> tuple[bool, str]:
        """Verifica si un estudiante puede inscribirse.

        Returns:
            tuple: (puede, mensaje)
        """
        if not self.activo:
            return False, "Período inactivo"

        if self.estado == "cancelado":
            return False, "Período cancelado"

        if self.estado == "finalizado":
            return False, "Período finalizado"

        if not self.permite_inscripciones:
            return False, "Inscripciones no permitidas"

        hoy = date.today()

        # Verificar fechas de inscripción
        if hoy < self.fecha_inicio_inscripciones:
            return False, f"Inscripciones inician el {self.fecha_inicio_inscripciones}"

        if hoy > self.fecha_fin_inscripciones:
            return False, "Período de inscripciones cerrado"

        return True, "Puede inscribirse"

    def __repr__(self) -> str:
        return f"<PeriodoAcademico(id={self.id}, nombre='{self.nombre}', estado='{self.estado}')>"
