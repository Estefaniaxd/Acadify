from sqlalchemy import Column, ForeignKey, String
from sqlalchemy.dialects.postgresql import DATE, UUID
from sqlalchemy.orm import relationship

from src.db.base_class import Base


class Coordinador(Base):
    __tablename__ = "Coordinador"

    coordinador_id = Column(
        UUID(as_uuid=True),
        ForeignKey("Usuario.usuario_id", ondelete="CASCADE"),
        primary_key=True,
    )

    horario_atencion = Column(String(50))
    fecha_inicio_carrera = Column(DATE, nullable=False)

    institucion_coordinadores = relationship(
        "InstitucionCoordinador", back_populates="coordinador"
    )
