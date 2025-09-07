from src.db.base_class import Base
from sqlalchemy.dialects.postgresql import UUID, ENUM, DATE
from sqlalchemy import Column, ForeignKey
from src.enums.coordinador_enums import EstadoCoordinador
from sqlalchemy.orm import relationship


class InstitucionCoordinador(Base):
    __tablename__ = "InstitucionCoordinador"

    institucion_coordinador_id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default="gen_random_uuid()",
    )
    institucion_id = Column(
        UUID(as_uuid=True),
        ForeignKey("institucion.institucion_id"),
        nullable=False,
        ondelete="CASCADE",
    )
    coordinador_id = Column(
        UUID(as_uuid=True),
        ForeignKey("coordinador.coordinador_id"),
        nullable=False,
        ondelete="CASCADE",
    )
    fecha_asignacion = Column(DATE, nullable=False)
    estado = Column(
        ENUM(EstadoCoordinador, name="estado_coordinador", create_type=False),
        nullable=False,
        default=EstadoCoordinador.activo,
    )

    institucion = relationship(
        "institucion", back_populates="coordinadores", passive_deletes=True
    )
    coordinador = relationship(
        "coordinador", back_populates="instituciones", passive_deletes=True
    )
