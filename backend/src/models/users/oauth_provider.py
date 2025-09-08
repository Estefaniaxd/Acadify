from src.db.base_class import Base
from sqlalchemy import Column, text, String, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID, TIMESTAMP
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

class OAuthProvider(Base):
    """Modelo para vincular proveedores OAuth (Google, etc.) con usuarios"""
    __tablename__ = "OAuthProvider"
    __table_args__ = (
        UniqueConstraint("provider", "provider_user_id", name="uq_provider_user"),
    )
    
    oauth_provider_id = Column(
        UUID(as_uuid=True), 
        primary_key=True, 
        server_default=text("gen_random_uuid()")
    )
    
    usuario_id = Column(
        UUID(as_uuid=True),
        ForeignKey("Usuario.usuario_id", ondelete="CASCADE"),
        nullable=False,
    )
    
    provider = Column(String(50), nullable=False)  # 'google', 'microsoft', etc.
    provider_user_id = Column(String(255), nullable=False)  # ID del usuario en el proveedor
    provider_email = Column(String(255), nullable=False)
    
    fecha_vinculacion = Column(
        TIMESTAMP(timezone=True), 
        server_default=func.now(), 
        nullable=False
    )
    
    # Relationship
    usuario = relationship("Usuario", backref="oauth_providers")