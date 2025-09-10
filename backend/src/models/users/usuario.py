from src.db.base_class import Base
from sqlalchemy import Column, String, CheckConstraint, BOOLEAN, SMALLINT, text
from sqlalchemy.dialects.postgresql import UUID, ENUM, TIMESTAMP, TEXT
from src.enums.users.usuario_enums import (
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

    usuario_id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        index=True,
    server_default=text('gen_random_uuid()'),
    )
    correo_institucional = Column(String(100), unique=True, index=True)
    username = Column(String(50), unique=True, index=True)
    nombres = Column(String(100), nullable=False)
    apellidos = Column(String(100), nullable=False)
    tipo_documento = Column(
        ENUM(TipoDocumentoUsuario, name="tipo_documento_usuario", create_type=False),
        nullable=False,
    )
    numero_documento = Column(String(20), index=True, nullable=False)
    rol = Column(
        ENUM(RolUsuario, name="rol_usuario", create_type=False),
        nullable=False,
    )
    password_hash = Column(String(255), nullable=False)
    estado_cuenta = Column(
        ENUM(EstadoCuentaUsuario, name="estado_cuenta_usuario", create_type=False),
        nullable=False,
        server_default=EstadoCuentaUsuario.activo.name,
    )
    fecha_creacion = Column(TIMESTAMP(timezone=True), server_default=func.now())
    ultimo_acceso = Column(TIMESTAMP(timezone=True), server_default=func.now())
    perfil_url = Column(TEXT)
    portada_url = Column(TEXT)
    telefono = Column(String(20))
    descripcion = Column(TEXT)
    email_verified = Column(BOOLEAN, nullable=False, server_default=text("false"))
    failed_login_attempts = Column(SMALLINT, nullable=False, server_default=text("0"))
    locked_until = Column(TIMESTAMP(timezone=True), nullable=True)
    twofa_enabled = Column(BOOLEAN, nullable=False, server_default=text("false"))
    twofa_secret = Column(String(32), nullable=True)
    administrador = relationship(
        "AdministradorSistema", backref="usuario", uselist=False
    )
    coordinador = relationship("Coordinador", backref="usuario", uselist=False)
    estudiante = relationship("Estudiante", backref="usuario", uselist=False)

    mensajes = relationship("Mensaje", backref="usuario")

    archivos = relationship("ArchivoChat", backref="usuario")

    usuario_insignias = relationship(
        "UsuarioInsignia",
        back_populates="usuario",
        foreign_keys="UsuarioInsignia.usuario_id",
        passive_deletes=True
    )

    usuario_recompensas = relationship("UsuarioRecompensa", back_populates="usuario", passive_deletes=True)

    puntos = relationship("UsuarioPuntos", backref="usuario")

    historial_puntos = relationship("HistorialPuntos", backref="usuario", passive_deletes=True)

    temas_personalizados = relationship("TemaPersonalizado", backref="usuario", passive_deletes=True)
    oauth_providers = relationship("OAuthProvider", back_populates="usuario", passive_deletes=True)