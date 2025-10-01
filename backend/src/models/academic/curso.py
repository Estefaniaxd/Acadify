from ...db.base_class import Base
from sqlalchemy import Column, text, ForeignKey, String, UniqueConstraint, Index, Boolean
from sqlalchemy.dialects.postgresql import UUID, ENUM, DATE, TEXT, TIMESTAMP, INTEGER
from ...enums.academic.curso_enums import ModalidadCurso
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

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
        server_default=text('gen_random_uuid()'),
    )

    institucion_id = Column(
        UUID(as_uuid=True),
        ForeignKey("Institucion.institucion_id", ondelete="CASCADE"), 
        nullable=False
    )

    coordinador_id = Column(
        UUID(as_uuid=True),
        ForeignKey("Coordinador.coordinador_id", ondelete="SET NULL")
    )

    programa_id = Column(
        UUID(as_uuid=True),
        ForeignKey("Programa.programa_id", ondelete="CASCADE"),
        nullable=False  
    )

    # Información básica
    nombre = Column(String(100), nullable=False)
    descripcion = Column(TEXT)
    objetivos = Column(TEXT)
    codigo_curso = Column(String(20))  # Código identificador del curso (ej: MAT101)
    codigo_acceso = Column(String(10), unique=True)  # Código para que estudiantes se unan al curso
    creditos = Column(INTEGER, default=0)
    horas_academicas = Column(INTEGER, default=0)
    
    modalidad = Column(
        ENUM(ModalidadCurso, name="modalidad_curso", create_type=False),
        nullable=False
    )
    fecha_inicio = Column(DATE)
    fecha_fin = Column(DATE)
    
    # Configuración
    activo = Column(Boolean, default=True, nullable=False)
    permite_inscripcion = Column(Boolean, default=True, nullable=False)
    maximo_estudiantes = Column(INTEGER)
    minimo_estudiantes = Column(INTEGER, default=1)
    
    # Configuración de material
    permite_material_estudiantes = Column(Boolean, default=False)
    requiere_aprobacion_material = Column(Boolean, default=True)
    
    # Google Drive Integration
    carpeta_drive_id = Column(String(50))
    carpeta_drive_url = Column(String(500))
    
    # Auditoría
    fecha_creacion = Column(TIMESTAMP(timezone=True), server_default=func.now())
    fecha_actualizacion = Column(TIMESTAMP(timezone=True), onupdate=func.now())

    # Relaciones
    institucion = relationship("Institucion", backref="cursos")
    coordinador = relationship("Coordinador", backref="cursos_coordinados")
    programa = relationship("Programa", backref="cursos")
    curso_docentes = relationship("CursoDocente", back_populates="curso", cascade="all, delete-orphan")
    grupo_cursos = relationship("GrupoCurso", back_populates="curso", cascade="all, delete-orphan")
    material_cursos = relationship("MaterialCurso", backref="curso", cascade="all, delete-orphan")
    comentarios = relationship("Comentario", back_populates="curso", cascade="all, delete-orphan")
    
    @property
    def total_estudiantes(self) -> int:
        """Calcula el total de estudiantes inscritos en el curso"""
        total = 0
        for grupo_curso in self.grupo_cursos:
            total += len(grupo_curso.grupo.estudiante_grupos)
        return total
    
    @property
    def total_docentes(self) -> int:
        """Calcula el total de docentes asignados al curso"""
        return len(self.curso_docentes)
    
    @property
    def total_grupos(self) -> int:
        """Calcula el total de grupos vinculados al curso"""
        return len(self.grupo_cursos)