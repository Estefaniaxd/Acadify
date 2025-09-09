from src.db.base_class import Base
from sqlalchemy import Column, ForeignKey, Integer, Date, func
from sqlalchemy.dialects.postgresql import UUID

class RachaUsuario(Base):
    __tablename__ = "RachaUsuario"

    usuario_id = Column(UUID(as_uuid=True), ForeignKey("Usuario.usuario_id", ondelete="CASCADE"), primary_key=True)
    racha_actual = Column(Integer, nullable=False, default=0)
    mejor_racha = Column(Integer, nullable=False, default=0)
    fecha_ultimo_dia = Column(Date, nullable=True)
