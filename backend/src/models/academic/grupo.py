from sqlalchemy import (
    DATE,
    DECIMAL,
    TIME,
    Boolean,
    Column,
    ForeignKey,
    Integer,
    String,
    text,
)
from sqlalchemy.dialects.postgresql import ENUM, JSON, TEXT, TIMESTAMP, UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from src.db.base_class import Base
from src.enums.academic.grupo_enums import (
    EstadoGrupo,
    FormatoEvaluacion,
    JornadaGrupo,
    ModalidadAsistencia,
    TipoGrupo,
)


class Grupo(Base):
    __tablename__ = "Grupo"

    grupo_id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )

    programa_id = Column(
        UUID(as_uuid=True),
        ForeignKey("Programa.programa_id", ondelete="CASCADE"),
        nullable=True,
    )

    docente_tutor_id = Column(
        UUID(as_uuid=True),
        ForeignKey("Docente.docente_id", ondelete="SET NULL"),
        nullable=True,
        unique=True,
    )

    nombre = Column(String(50), nullable=False)
    jornada = Column(
        ENUM(JornadaGrupo, name="jornada_grupo", create_type=False),
        nullable=False,
        default=JornadaGrupo.manana,
        server_default=text("'manana'"),
    )

    # Identificación y organización
    periodo_academico_id = Column(Integer, nullable=True)
    codigo_grupo = Column(String(20), nullable=True)
    nivel_academico = Column(Integer, nullable=True)
    seccion = Column(String(10), nullable=True)
    descripcion = Column(TEXT, nullable=True)

    # Estado y tipo
    estado = Column(
        ENUM(EstadoGrupo, name="estado_grupo", create_type=False),
        nullable=False,
        default="programado",
    )
    tipo_grupo = Column(
        ENUM(TipoGrupo, name="tipo_grupo", create_type=False), nullable=True
    )
    modalidad_asistencia = Column(
        ENUM(ModalidadAsistencia, name="modalidad_asistencia", create_type=False),
        nullable=True,
    )
    formato_evaluacion = Column(
        ENUM(FormatoEvaluacion, name="formato_evaluacion", create_type=False),
        nullable=True,
    )

    # Horarios y ubicación
    hora_inicio = Column(TIME, nullable=True)
    hora_fin = Column(TIME, nullable=True)
    dias_semana = Column(
        JSON, nullable=True
    )  # Lista de días (ej: ["lunes", "miércoles"])
    salon = Column(String(50), nullable=True)
    edificio = Column(String(50), nullable=True)
    ubicacion_virtual = Column(String(500), nullable=True)

    # Capacidad y cupos
    capacidad_maxima = Column(Integer, nullable=True)
    capacidad_minima = Column(Integer, nullable=True)
    cupos_disponibles = Column(Integer, nullable=True)
    permite_lista_espera = Column(Boolean, default=False)
    maximo_lista_espera = Column(Integer, nullable=True)

    # Fechas
    fecha_inicio = Column(DATE, nullable=True)
    fecha_fin = Column(DATE, nullable=True)
    fecha_inicio_inscripciones = Column(DATE, nullable=True)
    fecha_fin_inscripciones = Column(DATE, nullable=True)

    # Académico
    creditos = Column(Integer, nullable=True)
    horas_semanales = Column(Integer, nullable=True)
    porcentaje_asistencia_minimo = Column(DECIMAL(5, 2), nullable=True)
    calificacion_minima_aprobacion = Column(DECIMAL(3, 2), nullable=True)
    permite_recuperacion = Column(Boolean, default=True)
    numero_maximo_faltas = Column(Integer, nullable=True)

    # Costos
    tiene_costo_adicional = Column(Boolean, default=False)
    costo_adicional = Column(DECIMAL(10, 2), nullable=True)

    # Configuración y permisos
    activo = Column(Boolean, default=True, nullable=False)
    permite_inscripcion = Column(Boolean, default=True)
    requiere_aprobacion_inscripcion = Column(Boolean, default=False)
    es_visible = Column(Boolean, default=True)
    permite_autoregistro = Column(Boolean, default=False)
    codigo_acceso = Column(String(20), nullable=True)
    permite_chat = Column(Boolean, default=True)
    permite_foro = Column(Boolean, default=True)
    permite_comentarios = Column(Boolean, default=True)
    permite_material_estudiantes = Column(Boolean, default=False)

    # Contenido
    objetivos = Column(TEXT, nullable=True)
    notas_internas = Column(TEXT, nullable=True)
    recursos_adicionales = Column(JSON, nullable=True)
    tags = Column(JSON, nullable=True)
    imagen_url = Column(String(500), nullable=True)

    # Auditoría
    fecha_creacion = Column(TIMESTAMP, server_default=func.now(), nullable=False)
    fecha_actualizacion = Column(
        TIMESTAMP, server_default=func.now(), onupdate=func.now(), nullable=False
    )
    creado_por_id = Column(
        UUID(as_uuid=True),
        ForeignKey("Usuario.usuario_id", ondelete="SET NULL"),
        nullable=True,
    )
    modificado_por_id = Column(
        UUID(as_uuid=True),
        ForeignKey("Usuario.usuario_id", ondelete="SET NULL"),
        nullable=True,
    )

    # Relaciones
    estudiante_grupos = relationship("EstudianteGrupo", back_populates="grupo")
    grupo_cursos = relationship("GrupoCurso", back_populates="grupo")
    chat_grupos = relationship("ChatGrupo", backref="grupo")
    tareas = relationship("src.models.academic.tarea.Tarea", back_populates="grupo")
