from ...db.base_class import Base
from sqlalchemy import Column, text, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID, DATE
from sqlalchemy.orm import relationship


class GrupoCurso(Base):
    __tablename__ = "GrupoCurso"

    __table_args__ = (UniqueConstraint("curso_id", "grupo_id", name="uq_grupo_curso"),)

    grupo_curso_id = Column(
    UUID(as_uuid=True), primary_key=True, server_default=text('gen_random_uuid()')
    )
    grupo_id = Column(ForeignKey("Grupo.grupo_id", ondelete="CASCADE"), nullable=False)
    curso_id = Column(ForeignKey("Curso.curso_id", ondelete="CASCADE"), nullable=False)
    docente_id = Column(
        ForeignKey("Docente.docente_id", ondelete="CASCADE"), nullable=False
    )
    fecha_asignacion = Column(DATE)

    grupo = relationship("Grupo", back_populates="grupo_cursos")

    curso = relationship("Curso", back_populates="grupo_cursos")
