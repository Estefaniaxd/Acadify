from sqlalchemy import Column, String, text
from sqlalchemy.dialects.postgresql import TEXT, TIMESTAMP, UUID

from src.db.base_class import Base


class FAQBot(Base):
    __tablename__ = "FAQBot"

    faq_id = Column(
        UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
    )
    pregunta = Column(TEXT, nullable=False)
    respuesta = Column(TEXT, nullable=False)
    categoria = Column(String(50), nullable=False)
    ultima_actualizacion = Column(TIMESTAMP)
