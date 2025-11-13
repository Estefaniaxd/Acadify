from sqlalchemy import Column, ForeignKey
from sqlalchemy.dialects.postgresql import UUID

from src.db.base_class import Base


class MaterialClase(Base):
    __tablename__ = "MaterialClase"

    material_clase_id = Column(
        UUID(as_uuid=True),
        ForeignKey("MaterialEducativo.material_id", ondelete="CASCADE"),
        primary_key=True,
    )
    clase_id = Column(
        UUID(as_uuid=True),
        ForeignKey("Clase.clase_id", ondelete="SET NULL"),
        nullable=True,
    )
