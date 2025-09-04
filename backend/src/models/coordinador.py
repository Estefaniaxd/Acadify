from sqlalchemy import Column, String, Date, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from src.db.base_class import Base


class Coordinador(Base):
    __tablename__ = "Coordinador"

    coordinador_id = Column(
        UUID(as_uuid=True),
        ForeignKey("Usuario.usuario_id"),
        primary_key=True
    )

    institucion_id = Column(
        UUID(as_uuid=True),
        ForeignKey("Institucion.institucion_id", ondelete="CASCADE"),
        nullable=False
    )

    horario_atencion = Column(String(50), nullable=True)
    fecha_inicio_carrera = Column(Date, nullable=False)

    usuario = relationship("Usuario", back_populates="coordinador")
    institucion = relationship("Institucion", back_populates="coordinadores")