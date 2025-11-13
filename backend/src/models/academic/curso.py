from sqlalchemy import (
    DECIMAL,
    Boolean,
    Column,
    ForeignKey,
    Index,
    String,
    UniqueConstraint,
    text,
)
from sqlalchemy.dialects.postgresql import (
    DATE,
    ENUM,
    INTEGER,
    JSON,
    TEXT,
    TIMESTAMP,
    UUID,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from src.db.base_class import Base
from src.enums.academic.curso_enums import (
    CategoriaCurso,
    EstadoCurso,
    IdiomaCurso,
    ModalidadCurso,
    NivelDificultad,
    TipoCurso,
)


class Curso(Base):
    __tablename__ = "Curso"
    __table_args__ = (
        UniqueConstraint("institucion_id", "nombre", name="uq_curso_nombre"),
        Index("idx_curso_institucion", "institucion_id"),
        Index("idx_curso_programa", "programa_id"),
        Index("idx_curso_coordinador", "coordinador_id"),
        Index("idx_curso_fechas", "fecha_inicio", "fecha_fin"),
    )

    curso_id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )

    institucion_id = Column(
        UUID(as_uuid=True),
        ForeignKey("Institucion.institucion_id", ondelete="CASCADE"),
        nullable=False,
    )

    coordinador_id = Column(
        UUID(as_uuid=True),
        ForeignKey("Coordinador.coordinador_id", ondelete="SET NULL"),
    )

    programa_id = Column(
        UUID(as_uuid=True),
        ForeignKey("Programa.programa_id", ondelete="CASCADE"),
        nullable=True,
    )

    # Información básica
    nombre = Column(String(100), nullable=False)
    descripcion = Column(TEXT)
    objetivos = Column(TEXT)
    codigo_curso = Column(String(20))  # Código identificador del curso (ej: MAT101)
    codigo_acceso = Column(
        String(10), unique=True
    )  # Código para que estudiantes se unan al curso
    creditos = Column(INTEGER, default=0)
    horas_academicas = Column(INTEGER, default=0)

    # Desglose de horas
    horas_teoricas = Column(INTEGER)
    horas_practicas = Column(INTEGER)
    horas_laboratorio = Column(INTEGER)
    horas_autonomas = Column(INTEGER)

    modalidad = Column(
        ENUM(ModalidadCurso, name="modalidad_curso", create_type=False), nullable=False
    )

    # Clasificación y características
    nivel_dificultad = Column(
        ENUM(NivelDificultad, name="nivel_dificultad", create_type=False), nullable=True
    )
    tipo_curso = Column(
        ENUM(TipoCurso, name="tipo_curso", create_type=False), nullable=True
    )
    categoria_curso = Column(
        ENUM(CategoriaCurso, name="categoria_curso", create_type=False), nullable=True
    )
    estado = Column(
        ENUM(EstadoCurso, name="estado_curso", create_type=False),
        nullable=False,
        default="borrador",
    )
    idioma = Column(ENUM(IdiomaCurso, name="idioma", create_type=False), nullable=True)

    # Fechas
    fecha_inicio = Column(DATE)
    fecha_fin = Column(DATE)
    fecha_limite_inscripcion = Column(DATE)
    fecha_inicio_retiro = Column(DATE)
    fecha_limite_retiro = Column(DATE)

    # Configuración de estudiantes
    activo = Column(Boolean, default=True, nullable=False)
    permite_inscripcion = Column(Boolean, default=True, nullable=False)
    maximo_estudiantes = Column(INTEGER)
    minimo_estudiantes = Column(INTEGER, default=1)
    cupos_disponibles = Column(INTEGER)
    permite_lista_espera = Column(Boolean, default=False)
    maximo_lista_espera = Column(INTEGER)

    # Requisitos académicos
    prerequisitos_ids = Column(JSON)  # Lista de curso_ids requeridos
    correquisitos_ids = Column(
        JSON
    )  # Lista de curso_ids que deben cursarse simultáneamente
    requiere_nivelacion = Column(Boolean, default=False)
    creditos_minimos_requeridos = Column(INTEGER)
    promedio_minimo_requerido = Column(DECIMAL(3, 2))

    # Costos
    tiene_costo = Column(Boolean, default=False)
    costo_matricula = Column(DECIMAL(10, 2))
    costo_mensual = Column(DECIMAL(10, 2))
    costo_total = Column(DECIMAL(10, 2))
    permite_becas = Column(Boolean, default=False)
    porcentaje_descuento = Column(DECIMAL(5, 2))

    # Criterios de aprobación
    calificacion_minima_aprobacion = Column(DECIMAL(3, 2))
    porcentaje_asistencia_minimo = Column(DECIMAL(5, 2))
    permite_recuperacion = Column(Boolean, default=True)
    permite_habilitacion = Column(Boolean, default=True)
    numero_maximo_faltas = Column(INTEGER)

    # Funcionalidades y permisos
    permite_foros = Column(Boolean, default=True)
    permite_comentarios = Column(Boolean, default=True)
    permite_calificacion_entre_pares = Column(Boolean, default=False)
    genera_certificado = Column(Boolean, default=False)
    requiere_trabajo_final = Column(Boolean, default=False)
    tipo_trabajo_final = Column(String(100))

    # Recursos académicos
    syllabus_url = Column(String(500))
    bibliografia = Column(TEXT)
    recursos_adicionales = Column(JSON)
    tags = Column(JSON)
    imagen_url = Column(String(500))

    # Configuración de material
    permite_material_estudiantes = Column(Boolean, default=False)
    requiere_aprobacion_material = Column(Boolean, default=True)

    # Auditoría
    fecha_creacion = Column(TIMESTAMP, server_default=func.now(), nullable=False)
    fecha_actualizacion = Column(
        TIMESTAMP, server_default=func.now(), onupdate=func.now(), nullable=False
    )
    # Relaciones
    institucion = relationship("Institucion", backref="cursos")
    coordinador = relationship("Coordinador", backref="cursos_coordinados")
    programa = relationship("Programa", back_populates="cursos")
    curso_docentes = relationship(
        "CursoDocente", back_populates="curso", cascade="all, delete-orphan"
    )
    grupo_cursos = relationship(
        "GrupoCurso", back_populates="curso", cascade="all, delete-orphan"
    )
    material_cursos = relationship(
        "MaterialCurso", backref="curso", cascade="all, delete-orphan"
    )
    comentarios = relationship(
        "Comentario", back_populates="curso", cascade="all, delete-orphan"
    )

    @property
    def total_estudiantes(self) -> int:
        """Calcula el total de estudiantes inscritos en el curso."""
        total = 0
        for grupo_curso in self.grupo_cursos:
            total += len(grupo_curso.grupo.estudiante_grupos)
        return total

    @property
    def total_docentes(self) -> int:
        """Calcula el total de docentes asignados al curso."""
        return len(self.curso_docentes)

    @property
    def total_grupos(self) -> int:
        """Calcula el total de grupos vinculados al curso."""
        return len(self.grupo_cursos)
        relationship("CursoDocente", back_populates="curso")
        relationship("GrupoCurso", back_populates="curso")
        return None
