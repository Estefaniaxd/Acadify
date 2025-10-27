from src.db.base_class import Base
from sqlalchemy import Column, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, DATE
from sqlalchemy.orm import relationship


class CursoDocente(Base):
    __tablename__ = "CursoDocente"

    curso_id = Column(
        UUID(as_uuid=True),
        ForeignKey("Curso.curso_id", ondelete="CASCADE"),
        primary_key=True,
        nullable=False,
    )
    docente_id = Column(
        UUID(as_uuid=True),
        ForeignKey("Docente.docente_id", ondelete="CASCADE"),
        primary_key=True,
        nullable=False,
    )
    fecha_asignacion = Column(DATE)
    
    curso = relationship("Curso", back_populates="curso_docentes")
    docente = relationship("Docente", back_populates="curso_docentes")
