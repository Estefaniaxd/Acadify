from sqlalchemy import Column, ForeignKey
from sqlalchemy.dialects.postgresql import UUID

from src.db.base_class import Base


class AdministradorSistema(Base):
    __tablename__ = "AdministradorSistema"

    administrador_id = Column(
        UUID(as_uuid=True),
        ForeignKey("Usuario.usuario_id", ondelete="CASCADE"),
        primary_key=True,
    )
