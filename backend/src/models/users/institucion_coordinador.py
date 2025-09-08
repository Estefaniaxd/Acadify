from src.db.base_class import Base
from sqlalchemy import Column, ForeignKey, text
from sqlalchemy.dialects.postgresql import UUID, ENUM, DATE
from src.enums.users.coordinador_enums import EstadoCoordinador
from sqlalchemy.orm import relationship


class InstitucionCoordinador(Base):
    __tablename__ = "InstitucionCoordinador"

    institucion_id = Column(
        UUID(as_uuid=True),
        ForeignKey("Institucion.institucion_id", ondelete="CASCADE"),
        primary_key=True,
        nullable=False,
    )
    coordinador_id = Column(
        UUID(as_uuid=True),
        ForeignKey("Coordinador.coordinador_id", ondelete="CASCADE"),
        primary_key=True,
        nullable=False,
    )
    fecha_asignacion = Column(DATE, nullable=False)
    estado = Column(
        ENUM(EstadoCoordinador, name="estado_coordinador", create_type=False),
        nullable=False,
        default=EstadoCoordinador.activo,
        server_default=text("'activo'"),
    )

    institucion = relationship(
        "Institucion", back_populates="institucion_coordinadores"
    )
    coordinador = relationship(
        "Coordinador", back_populates="institucion_coordinadores"
    )
