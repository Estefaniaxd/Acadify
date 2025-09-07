from src.db.base_class import Base
from sqlalchemy.dialects.postgresql import UUID, ENUM, NUMERIC
from sqlalchemy import Column, String, ForeignKey
from src.enums.escala_calificacion_eunms import TipoEscalafonEnum
from sqlalchemy.orm import relationship


class EscalaCalificacion(Base):
    __tablename__ = "EscalaCalificacion"

    escala_id = Column(
        UUID(as_uuid=True), primary_key=True, server_default="gen_random_uuid()"
    )

    institucion_id = Column(
        UUID(as_uuid=True),
        ForeignKey("institucion.institucion_id", ondelete="CASCADE"),
        nullable=False,
    )

    nombre = Column(String(50), nullable=False)

    tipo = Column(
        ENUM(TipoEscalafonEnum, name="tipo_escalafon", create_type=False),
        nullable=False,
    )

    min_valor = Column(NUMERIC(5, 2))
    max_valor = Column(NUMERIC(5, 2))

    institucion = relationship(
        "institucion", back_populates="escala_calificacion", passive_deletes=True
    )

    valores = relationship(
        "valor_calificacion", back_populates="escala_calificacion", passive_deletes=True
    )
