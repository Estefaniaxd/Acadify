from ...db.base_class import Base
from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, DATE
from sqlalchemy.orm import relationship


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
