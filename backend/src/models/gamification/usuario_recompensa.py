from sqlalchemy import Column, ForeignKey, text
from sqlalchemy.dialects.postgresql import TIMESTAMP, UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from src.db.base_class import Base


class UsuarioRecompensa(Base):
    __tablename__ = "UsuarioRecompensa"

    usuario_recompensa_id = Column(
        UUID(as_uuid=True), primary_key=True, default=text("gen_random_uuid()")
    )
    usuario_id = Column(
        UUID(as_uuid=True),
        ForeignKey("Usuario.usuario_id", ondelete="CASCADE"),
    )
    recompensa_id = Column(
        UUID(as_uuid=True),
        ForeignKey("Recompensa.recompensa_id", ondelete="CASCADE"),
    )
    fecha_canje = Column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
        nullable=True,
    )

    usuario = relationship(
        "Usuario", back_populates="usuario_recompensas", passive_deletes=True
    )
    recompensa = relationship("Recompensa", back_populates="usuario_recompensas")
