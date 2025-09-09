from src.db.base_class import Base
from sqlalchemy import (
    Column,
    ForeignKey,
    text,
    CheckConstraint,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import UUID, TEXT, TIMESTAMP, NUMERIC


class EntregarTarea(Base):
    __tablename__ = "EntregarTarea"

    __table_args__ = (
        CheckConstraint(
            "calificacion >= 0 AND calificacion <= 5", name="chk_calificacion"
        ),
        UniqueConstraint("tarea_id", "estudiante_id", name="uq_entrega"),
    )

    entrega_id = Column(
        UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
    )

    tarea_id = Column(
        UUID(as_uuid=True),
        ForeignKey("Tarea.tarea_id", ondelete="CASCADE"),
        nullable=False,
    )

    estudiante_id = Column(
        UUID(as_uuid=True),
        ForeignKey("Estudiante.estudiante_id", ondelete="CASCADE"),
        nullable=False,
    )

    archivo = Column(TEXT, nullable=False)

    fecha_envio = Column(
        TIMESTAMP(timezone=True), nullable=False, server_default=func.now()
    )

    calificacion = Column(NUMERIC(3, 1))

    fecha_revision = Column(TIMESTAMP(timezone=True))
