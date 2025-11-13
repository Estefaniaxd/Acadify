from sqlalchemy import Column, ForeignKey, text
from sqlalchemy.dialects.postgresql import ENUM, UUID

from src.db.base_class import Base
from src.enums.classes.asistencia_enums import EstadoAsistencia


class Asistencia(Base):
    __tablename__ = "Asistencia"

    asistencia_id = Column(
        UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
    )

    clase_id = Column(
        UUID(as_uuid=True),
        ForeignKey("Clase.clase_id", ondelete="CASCADE"),
        nullable=False,
    )

    estudiante_id = Column(
        UUID(as_uuid=True),
        ForeignKey("Estudiante.estudiante_id", ondelete="CASCADE"),
        nullable=False,
    )

    estado = Column(
        ENUM(EstadoAsistencia, name="estado_asistencia", create_type=False),
        nullable=False,
    )
