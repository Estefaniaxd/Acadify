from sqlalchemy import Column, String, DateTime, Enum, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum
import uuid

from ...db.base_class import Base

class EstadoInvitacion(str, enum.Enum):
    pendiente = "pendiente"
    usado = "usado"
    expirado = "expirado"

class InvitationToken(Base):
    __tablename__ = "invitation_tokens"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    codigo = Column(String(6), unique=True, nullable=False, index=True)
    email_destino = Column(String(100), nullable=False)
    institucion_id = Column(UUID(as_uuid=True), ForeignKey("Institucion.institucion_id", ondelete="CASCADE"), nullable=False)
    estado = Column(Enum(EstadoInvitacion, name="estado_invitacion"), nullable=False, default=EstadoInvitacion.pendiente, server_default="pendiente")
    fecha_creacion = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    fecha_expiracion = Column(DateTime(timezone=True), nullable=False)
    coordinador_id = Column(UUID(as_uuid=True), ForeignKey("Usuario.usuario_id", ondelete="SET NULL"), nullable=True)
    usado_en = Column(DateTime(timezone=True), nullable=True)

    institucion = relationship("Institucion", backref="invitaciones")
    coordinador = relationship("Usuario", backref="invitaciones_aceptadas")
