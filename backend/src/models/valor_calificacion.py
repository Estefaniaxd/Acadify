from src.db.base_class import Base
from sqlalchemy.dialects.postgresql import UUID, SMALLINT
from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.orm import relationship


class ValorCalificacion(Base):
    __tablename__ = "ValorCalificacion"

    valor_id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default="gen_random_uuid()",
    )

    escala_id = Column(
        UUID(as_uuid=True),
        ForeignKey("escala_calificacion.escala_id", ondelete="CASCADE"),
        nullable=False,
    )

    valor = Column(String(10), nullable=False)
    descripcion = Column(String(100))
    orden = Column(SMALLINT)

    escala = relationship("escala_calificacion", back_populates="valor_calificacion", passive_deletes=True)