from sqlalchemy import CheckConstraint, Column, String, text
from sqlalchemy.dialects.postgresql import ENUM, INTEGER, TEXT, UUID
from sqlalchemy.orm import relationship

from src.db.base_class import Base
from src.enums.gamification.recompensa_enums import TipoRecompensa


class Recompensa(Base):
    __tablename__ = "Recompensa"

    __table_args__ = (
        CheckConstraint("costo_puntos >= 0", name="check_costo_puntos_positivo"),
    )

    recompensa_id = Column(
        UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
    )
    nombre = Column(String(100), nullable=False)
    descripcion = Column(TEXT)
    costo_puntos = Column(INTEGER, nullable=False)

    tipo = Column(
        ENUM(TipoRecompensa, name="tipo_recompensa_enum", create_type=False),
        nullable=False,
        default=TipoRecompensa.otro,
        server_default=text("'otro'"),
    )

    usuario_recompensas = relationship("UsuarioRecompensa", back_populates="recompensa")
