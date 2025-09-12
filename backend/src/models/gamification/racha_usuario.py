from src.db.base_class import Base
from sqlalchemy import Column, ForeignKey, text
from sqlalchemy.dialects.postgresql import UUID, INTEGER, DATE

class RachaUsuario(Base):
    __tablename__ = "RachaUsuario"

    usuario_id = Column(UUID(as_uuid=True), ForeignKey("Usuario.usuario_id", ondelete="CASCADE"), primary_key=True)
    racha_actual = Column(INTEGER, nullable=False, default=0, server_default=text("0"))
    mejor_racha = Column(INTEGER, nullable=False, default=0, server_default=text("0"))
    fecha_ultimo_dia = Column(DATE)
