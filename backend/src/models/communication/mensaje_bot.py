from src.db.base_class import Base
from sqlalchemy import Column, text, ForeignKey, Enum
from sqlalchemy.dialects.postgresql import UUID, TIMESTAMP, TEXT
from sqlalchemy.sql import func
from src.enums.communication.mensaje_bots_enum import ContextoMensaje


class MensajeBot(Base):
    __tablename__ = "MensajeBot"

    mensaje_bot_id = Column(
        UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
    )
    usuario_id = Column(
        UUID(as_uuid=True),
        ForeignKey("Usuario.usuario_id", ondelete="SET NULL"),
        nullable=True,
    )
    chat_grupo_id = Column(
        UUID(as_uuid=True),
        ForeignKey("ChatGrupo.chat_grupo_id", ondelete="CASCADE"),
        nullable=False,
    )
    referencia_material_id = Column(
        UUID(as_uuid=True),
        ForeignKey("MaterialEducativo.material_id"),
        nullable=True,
    )
    contenido = Column(TEXT, nullable=False)
    respuesta = Column(TEXT, nullable=False)
    contexto = Column(Enum(ContextoMensaje), nullable=False)
    fecha_hora = Column(TIMESTAMP, server_default=func.now(), nullable=False)
