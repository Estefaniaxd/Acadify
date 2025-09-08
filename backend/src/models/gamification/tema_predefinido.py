from src.db.base_class import Base
from sqlalchemy import Column, ForeignKey
from sqlalchemy.dialects.postgresql import UUID


class TemaPredefinido(Base):
    __tablename__ = "TemaPredefinido"

    tema_id = Column(
        UUID(as_uuid=True),
        ForeignKey("Tema.tema_id", ondelete="CASCADE"),
        primary_key=True,
        nullable=False,
        unique=True  
    )