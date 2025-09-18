from ...db.base_class import Base
from sqlalchemy import Column, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship


class AdministradorSistema(Base):
    __tablename__ = "AdministradorSistema"

    administrador_id = Column(
        UUID(as_uuid=True),
        ForeignKey("Usuario.usuario_id", ondelete="CASCADE"),
        primary_key=True,
    )

    instituciones = relationship(
        "Institucion", backref="administrador_sistema"
    )
