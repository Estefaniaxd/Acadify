from src.db.base_class import Base
from sqlalchemy.dialects.postgresql import UUID, DATE
from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.orm import relationship


class Coordinador(Base):
    __tablename__ = "Coordinador"

    coordinador_id = Column(
        UUID(as_uuid=True),
        ForeignKey("usuario.usuario_id", ondelete="CASCADE"),
        primary_key=True,
    )

    institucion_id = Column(
        UUID(as_uuid=True),
        ForeignKey("institucion.institucion_id", ondelete="CASCADE"),
        nullable=False,
    )

    horario_atencion = Column(String(50))
    fecha_inicio_carrera = Column(DATE, nullable=False)

    usuario = relationship(
        "usuario", back_populates="coordinador", passive_deletes=True
    )
    institucion = relationship(
        "institucion", back_populates="coordinador", passive_deletes=True
    )
