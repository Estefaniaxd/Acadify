from src.db.base_class import Base
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import Column, String, Text, Enum, DateTime, CheckConstraint
from src.enums.usuario_enums import (
    RolUsuario,
    TipoDocumentoUsuario,
    EstadoCuentaUsuario,
)
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship


class Usuario(Base):
    __tablename__ = "Usuario"

    __table_args__ = (
        CheckConstraint(
            "(rol = 'administrador' AND username IS NOT NULL AND correo_institucional IS NULL) "
            "OR (rol <> 'administrador' AND correo_institucional IS NOT NULL AND username IS NULL)",
            name="chk_login",
        ),
    )

    usuario_id = Column(UUID(as_uuid=True), primary_key=True, index=True)
    correo_institucional = Column(String(100), unique=True, index=True)
    username = Column(String(50), unique=True, index=True)
    nombres = Column(String(100), nullable=False)
    apellidos = Column(String(100), nullable=False)
    tipo_documento = Column(
        Enum(TipoDocumentoUsuario, name="tipo_documento_usuario"), nullable=False
    )
    numero_documento = Column(String(20), index=True, nullable=False)
    rol = Column(Enum(RolUsuario, name="rol_usuario"), nullable=False)
    password_hash = Column(String(255), nullable=False)
    estado_cuenta = Column(
        Enum(EstadoCuentaUsuario, name="estado_cuenta_usuario"),
        nullable=False,
        server_default=EstadoCuentaUsuario.activo.name,
    )
    fecha_creacion = Column(DateTime(timezone=True), server_default=func.now())
    ultimo_acceso = Column(DateTime(timezone=True), server_default=func.now())
    perfil_url = Column(Text())
    portada_url = Column(Text())
    telefono = Column(String(20))
    descripcion = Column(Text())
    
    coordinador = relationship("Coordinador", back_populates="usuario", uselist=False)
    estudiante = relationship("Estudiante", back_populates="usuario", uselist=False)

