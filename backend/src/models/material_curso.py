from src.db.base_class import Base
from sqlalchemy import Column, ForeignKey
from sqlalchemy.dialects.postgresql import UUID


class MaterialCurso(Base):
    __tablename__ = "MaterialCurso"

    material_curso_id = Column(
        UUID(as_uuid=True),
        ForeignKey("MaterialEducativo.material_id", ondelete="CASCADE"),
        primary_key=True,
        nullable=False,
    )
    curso_id = Column(
        UUID(as_uuid=True),
        ForeignKey("Curso.curso_id", ondelete="SET NULL"),
        primary_key=True,
        nullable=True,
    )
