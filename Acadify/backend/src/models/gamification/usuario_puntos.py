from ...db.base_class import Base
from sqlalchemy import Column, text, ForeignKey, CheckConstraint, func
from sqlalchemy.dialects.postgresql import UUID, INTEGER, TEXT, TIMESTAMP
from sqlalchemy.orm import relationship
from sqlalchemy import func


class UsuarioPuntos(Base):
    __tablename__ = "UsuarioPuntos"

    __table_args__ = (CheckConstraint("cambio <> 0"),)

    usuario_id = Column(
        UUID(as_uuid=True),
        ForeignKey("Usuario.usuario_id", ondelete="CASCADE"),
        primary_key=True,
    )
    puntos_acumulados = Column(
        INTEGER, nullable=False, default=0, server_default=text("0")
    )
    cambio = Column(INTEGER, nullable=False)
    motivo = Column(TEXT)
    fecha = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())
