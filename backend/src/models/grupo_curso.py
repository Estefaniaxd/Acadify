from src.db.base_class import Base
from sqlalchemy.dialects.postgresql import UUID, DATE
from sqlalchemy import Column, ForeignKey, UniqueConstraint


class GrupoCurso(Base):
    __tablename__ = "GrupoCurso"

    __table_args__ = (UniqueConstraint("curso_id", "grupo_id", name="uq_grupo_curso"),)

    grupo_curso_id = Column(
        UUID(as_uuid=True), primary_key=True, server_default="gen_random_uuid()"
    )
    grupo_id = Column(ForeignKey("grupo.grupo_id", ondelete="CASCADE"), nullable=False)
    curso_id = Column(ForeignKey("curso.curso_id", ondelete="CASCADE"), nullable=False)
    docente_id = Column(
        ForeignKey("docente.docente_id", ondelete="CASCADE"), nullable=False
    )
    fecha_asignacion = Column(DATE)
