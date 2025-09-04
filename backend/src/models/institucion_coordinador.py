from sqlalchemy import Column, Date, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, ENUM
from sqlalchemy.orm import relationship
from src.db.base_class import Base
from src.enums.coordinador_enums import EstadoCoordinador

class InstitucionCoordinador(Base):
    __tablename__ = "InstitucionCoordinador"

    institucion_coordinador_id = Column(UUID(as_uuid=True), primary_key=True, nullable=False)
    institucion_id = Column(UUID(as_uuid=True), ForeignKey("Institucion.institucion_id"), nullable=False)
    coordinador_id = Column(UUID(as_uuid=True), ForeignKey("Coordinador.coordinador_id"), nullable=False)
    fecha_asignacion = Column(Date, nullable=False)
    estado = Column(
        ENUM(EstadoCoordinador, name="estado_coordinador", create_type=False),
        nullable=False,
        default=EstadoCoordinador.activo,
    )

    institucion = relationship("Institucion", back_populates="coordinadores")
    coordinador = relationship("Coordinador", back_populates="instituciones")