from src.db.base_class import Base
from sqlalchemy import Column, text, ForeignKey, CheckConstraint, func
from sqlalchemy.dialects.postgresql import UUID, INTEGER, TEXT, TIMESTAMP
from sqlalchemy import func


class HistorialPuntos(Base):
    __tablename__ = "HistorialPuntos"

    __table_args__ = (CheckConstraint("cambio <> 0"),)

    historial_id = Column(
        UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
    )
    usuario_id = Column(
        UUID(as_uuid=True), ForeignKey("Usuario.usuario_id", ondelete="CASCADE")
    )
    cambio = (Column(INTEGER, nullable=False),)
    motivo = (Column(TEXT),)
    fecha = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())
