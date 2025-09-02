from sqlalchemy import Column, String, Text, Boolean
from .base import BaseModel

class Platform(BaseModel):
    """Modelo para plataformas educativas"""
    __tablename__ = "platforms"
    
    name = Column(String(255), nullable=False)
    description = Column(Text)
    url = Column(String(500))
    api_key = Column(String(255))
    is_active = Column(Boolean, default=True)
    version = Column(String(50))
    
    # Configuraciones adicionales como JSON
    configuration = Column(Text)  # JSON string
    
    def __repr__(self):
        return f"<Platform(id={self.id}, name={self.name})>"