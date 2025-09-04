import uuid
from sqlalchemy import Column, String, SmallInteger, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from src.db.base_class import Base


class ValorCalificacion(Base):
    __tablename__ = "ValorCalificacion"

    valor_id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    escala_id = Column(
        UUID(as_uuid=True),
        ForeignKey("EscalaCalificacion.escala_id", ondelete="CASCADE"),
        nullable=False
    )

    valor = Column(String(10), nullable=False)
    descripcion = Column(String(100), nullable=True)
    orden = Column(SmallInteger, nullable=True)

    escala = relationship("EscalaCalificacion", back_populates="valores")