from sqlalchemy import Column, String, DateTime, ForeignKey, Integer
from sqlalchemy.orm import relationship
from src.db.base_class import Base
from datetime import datetime

class Reaccion(Base):
    __tablename__ = "Reaccion"
    reaccion_id = Column(String, primary_key=True, index=True)
    comentario_id = Column(String, ForeignKey("Comentario.comentario_id"), nullable=False)
    usuario_id = Column(String, ForeignKey("Usuario.usuario_id"), nullable=False)
    emoji = Column(String, nullable=False)
    fecha = Column(DateTime, default=datetime.utcnow)

    usuario = relationship("Usuario")
    comentario = relationship("Comentario")
