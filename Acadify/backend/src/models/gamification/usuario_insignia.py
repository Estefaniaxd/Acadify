from ...db.base_class import Base
from sqlalchemy import Column, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, TIMESTAMP
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship


class UsuarioInsignia(Base):
    __tablename__ = "UsuarioInsignia"

    usuario_id = Column(
        UUID(as_uuid=True),
        ForeignKey("Usuario.usuario_id", ondelete="CASCADE"),
        primary_key=True,
    )
    insignia_id = Column(
        UUID(as_uuid=True),
        ForeignKey("Insignia.insignia_id", ondelete="CASCADE"),
        primary_key=True,
    )
    otorgada_por = Column(
        UUID(as_uuid=True),
        ForeignKey("Usuario.usuario_id", ondelete="SET NULL"),
        nullable=True,
    )
    fecha_otorgada = Column(
        TIMESTAMP(timezone=True), server_default=func.now(), nullable=False
    )

    usuario = relationship(
        "Usuario",
        back_populates="usuario_insignias",
        foreign_keys=[usuario_id],
        passive_deletes=True
    )
    otorgante = relationship(
        "Usuario",
        foreign_keys=[otorgada_por],
        passive_deletes=True
    )
    insignia = relationship("Insignia", back_populates="usuario_insignias")
