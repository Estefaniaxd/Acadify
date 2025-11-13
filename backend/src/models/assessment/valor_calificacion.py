from sqlalchemy import Column, ForeignKey, String, text
from sqlalchemy.dialects.postgresql import SMALLINT, UUID

from src.db.base_class import Base


class ValorCalificacion(Base):
    __tablename__ = "ValorCalificacion"

    valor_id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )

    escala_id = Column(
        UUID(as_uuid=True),
        ForeignKey("EscalaCalificacion.escala_id", ondelete="CASCADE"),
        nullable=False,
    )

    valor = Column(String(10), nullable=False)
    descripcion = Column(String(100))
    orden = Column(SMALLINT)
