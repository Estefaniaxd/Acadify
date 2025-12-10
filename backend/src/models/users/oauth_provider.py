from sqlalchemy import Column, ForeignKey, String, UniqueConstraint, text
from sqlalchemy.dialects.postgresql import TIMESTAMP, UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from src.db.base_class import Base


class OAuthProvider(Base):
    """Modelo para vincular proveedores OAuth (Google, etc.) con usuarios."""

    __tablename__ = "OAuthProvider"
    __table_args__ = (
        UniqueConstraint("provider", "provider_user_id", name="uq_provider_user"),
    )

    oauth_provider_id = Column(
        UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
    )

    usuario_id = Column(
        UUID(as_uuid=True),
        ForeignKey("Usuario.usuario_id", ondelete="CASCADE"),
        nullable=False,
    )

    provider = Column(String(50), nullable=False)  # 'google', 'microsoft', etc.
    provider_user_id = Column(
        String(255), nullable=False
    )  # ID del usuario en el proveedor
    provider_email = Column(String(255), nullable=False)
    
    # Token storage for API access
    access_token = Column(String(2048), nullable=True)
    refresh_token = Column(String(2048), nullable=True)
    token_expiry = Column(TIMESTAMP(timezone=True), nullable=True)
    client_id = Column(String(512), nullable=True)
    client_secret = Column(String(512), nullable=True)

    fecha_vinculacion = Column(
        TIMESTAMP(timezone=True), server_default=func.now(), nullable=False
    )

    # Relationship
    usuario = relationship("Usuario", back_populates="oauth_providers")
