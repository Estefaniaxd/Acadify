from sqlalchemy import Column, String, text
from sqlalchemy.dialects.postgresql import BOOLEAN, ENUM, TEXT, UUID
from sqlalchemy.orm import relationship

from src.db.base_class import Base
from src.enums.gamification.insignia_enums import TipoInsignia


class Insignia(Base):
    __tablename__ = "Insignia"

    insignia_id = Column(
        UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
    )
    nombre = Column(String(100), nullable=False, unique=True)
    descripcion = Column(TEXT)
    imagen_url = Column(TEXT)
    tipo = Column(
        ENUM(TipoInsignia, name="tipo_insignia", create_type=False),
        nullable=False,
        default=TipoInsignia.manual,
        server_default=text("'manual'"),
    )
    es_unica = Column(BOOLEAN, nullable=False)

    usuario_insignias = relationship("UsuarioInsignia", back_populates="insignia")
