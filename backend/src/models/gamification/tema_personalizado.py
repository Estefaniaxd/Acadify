from src.db.base_class import Base
from sqlalchemy import Column, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship


class TemaPersonalizado(Base):
    __tablename__ = "TemaPersonalizado"

    __table_args__ = (
        UniqueConstraint("usuario_id", "tema_id", name="uq_nombre_predefinido"),
    )

    tema_id = Column(
        UUID(as_uuid=True),
        ForeignKey("Tema.tema_id", ondelete="CASCADE"),
        primary_key=True,
    )
    usuario_id = Column(
        UUID(as_uuid=True),
        ForeignKey("Usuario.usuario_id", ondelete="CASCADE"),
    )
    
    
