from src.db.base_class import Base
from sqlalchemy import Column, text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, TIMESTAMP
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship


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

    usuario = relationship("Usuario", back_populates="usuario_recompensas", passive_deletes=True)
    recompensa = relationship("Recompensa", back_populates="usuario_recompensas")
