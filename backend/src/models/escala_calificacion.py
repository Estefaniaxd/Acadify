import uuid
from sqlalchemy import Column, String, Numeric, Enum, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from src.db.base_class import Base
from src.enums.escala_calificacion_eunms import TipoEscalafonEnum


class EscalaCalificacion(Base):
    __tablename__ = "EscalaCalificacion"

    escala_id = Column(
        UUID(as_uuid=True), 
        primary_key=True, 
        default=uuid.uuid4
    )

    institucion_id = Column(
        UUID(as_uuid=True),
        ForeignKey("Institucion.institucion_id", ondelete="CASCADE"),
        nullable=False
    )

    nombre = Column(String(50), nullable=False)

    tipo = Column(
        Enum(TipoEscalafonEnum, name="tipo_escalafon", create_type=False),
        nullable=False
    )

    min_valor = Column(Numeric(5, 2), nullable=True)
    max_valor = Column(Numeric(5, 2), nullable=True)

    institucion = relationship("Institucion", back_populates="escalas")
    
    valores = relationship(
        "ValorCalificacion",
        back_populates="escala",
        cascade="all, delete-orphan"
    )