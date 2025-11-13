from sqlalchemy import Column, ForeignKey, String, text
from sqlalchemy.dialects.postgresql import ENUM, NUMERIC, UUID
from sqlalchemy.orm import relationship

from src.db.base_class import Base
from src.enums.assessment.escala_calificacion_enums import TipoEscalafonEnum


class EscalaCalificacion(Base):
    __tablename__ = "EscalaCalificacion"

    escala_id = Column(
        UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
    )

    institucion_id = Column(
        UUID(as_uuid=True),
        ForeignKey("Institucion.institucion_id", ondelete="CASCADE"),
        nullable=False,
    )

    nombre = Column(String(50), nullable=False)

    tipo = Column(
        ENUM(TipoEscalafonEnum, name="tipo_escalafon", create_type=False),
        nullable=False,
    )

    min_valor = Column(NUMERIC(5, 2))
    max_valor = Column(NUMERIC(5, 2))

    valores = relationship("ValorCalificacion", backref="escala_calificacion")
