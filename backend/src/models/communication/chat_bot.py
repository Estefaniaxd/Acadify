from src.db.base_class import Base
from sqlalchemy import Column, text, String
from sqlalchemy.dialects.postgresql import UUID, TEXT, BOOLEAN, DATE
from sqlalchemy.sql import func


class ChatBot(Base):
    __tablename__ = "ChatBot"

    chat_bot_id = Column(
    UUID(as_uuid=True), primary_key=True, server_default=text('gen_random_uuid()')
    )
    nombre = Column(String(100), nullable=False, unique=True)
    descripcion = Column(TEXT, nullable=False)
    foto_perfil_url = Column(TEXT, nullable=False)
    activo = Column(BOOLEAN)
    fecha_registro = Column(DATE, server_default=func.now())
