from src.db.base_class import Base
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import Column, ForeignKey
from sqlalchemy.orm import relationship


class AdministradorSistema(Base):
    __tablename__ = "AdministradorSistema"

    administrador_id = Column(
        UUID(as_uuid=True),
        ForeignKey("usuario.usuario_id", ondelete="CASCADE"),
        primary_key=True,
    )

    usuario = relationship(
        "usuario", back_populates="administrador_sistema", passive_deletes=True
    )

    instituciones = relationship(
        "institucion", back_populates="administrador_sistema", passive_deletes=True
    )
