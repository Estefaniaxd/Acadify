from src.db.base_class import Base
from sqlalchemy import Column, String, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship


class Tema(Base):
    __tablename__ = "Tema"

    tema_id = Column(
        UUID(as_uuid=True),
        primary_key=True,
    server_default=text('gen_random_uuid()')
    )
    nombre = Column(String(100), nullable=False)
    emoji = Column(String(8), nullable=False)
    
    tema_predefinido = relationship("TemaPredefinido", backref="tema")