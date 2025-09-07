from src.db.base_class import Base
from sqlalchemy.dialects.postgresql import UUID, DATE
from sqlalchemy import Column, ForeignKey


class CursoDocente(Base):
    __tablename__ = "CursoDocente"

    curso_id = Column(
        UUID(as_uuid=True),
        ForeignKey("curso.curso_id", ondelete="CASCADE"),
        primary_key=True,
        nullable=False,
    )
    docente_id = Column(
        UUID(as_uuid=True),
        ForeignKey("docente.docente_id", ondelete="CASCADE"),
        primary_key=True,
        nullable=False,
    )
    fecha_asignada = Column(DATE)
