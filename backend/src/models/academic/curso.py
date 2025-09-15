from src.db.base_class import Base
from sqlalchemy import Column, text, ForeignKey, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID, ENUM, DATE, TEXT
from src.enums.academic.curso_enums import ModalidadCurso
from sqlalchemy.orm import relationship

class Curso(Base):
    __tablename__ = "Curso"
    __table_args__ = (
        UniqueConstraint("institucion_id", "nombre", name="uq_curso_nombre"),  
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

    nombre = Column(String(50), nullable=False)
    descripcion = Column(TEXT)
    modalidad = Column(
        ENUM(ModalidadCurso, name="modalidad_curso", create_type=False),
        nullable=False
    )
    fecha_inicio = Column(DATE)
    fecha_fin = Column(DATE)

    curso_docentes = relationship("CursoDocente", back_populates="curso")
    grupo_cursos = relationship("GrupoCurso", back_populates="curso")