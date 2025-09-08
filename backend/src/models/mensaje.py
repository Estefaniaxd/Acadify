from src.db.base_class import Base
from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, TIMESTAMP, ENUM, TEXT
from sqlalchemy.sql import func
from src.enums.mensaje_enums import TipoMensaje


class Mensaje(Base):
    __tablename__ = "Mensaje"

    mensaje_id = Column(UUID(as_uuid=True), primary_key=True)
    chat_grupo_id = Column(
        UUID(as_uuid=True),
        ForeignKey("ChatGrupo.chat_grupo_id", ondelete="CASCADE"),
        nullable=False,
    )
    emisor_id = Column(
        UUID(as_uuid=True),
        ForeignKey("Usuario.usuario_id", ondelete="SET NULL"),
        nullable=True,
    )
    fecha_hora = Column(
        TIMESTAMP(timezone=True), server_default=func.now(), nullable=False
    )
    tipo = Column(
        ENUM(TipoMensaje, name="tipo_mensaje", create_type=False), nullable=False
    )
    contenido = Column(TEXT, nullable=False)
