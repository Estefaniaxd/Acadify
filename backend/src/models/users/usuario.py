from sqlalchemy import (
    BOOLEAN,
    SMALLINT,
    Column,
    ForeignKey,
    String,
    text,
)
from sqlalchemy.dialects.postgresql import ENUM, TEXT, TIMESTAMP, UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from src.db.base_class import Base
from src.enums.users.usuario_enums import (
    EstadoCuentaUsuario,
    RolUsuario,
    TipoDocumentoUsuario,
)


class Usuario(Base):
    __tablename__ = "Usuario"

    # Todos los usuarios deben tener username y correo_institucional
    # No se aplica CheckConstraint restrictivo

    usuario_id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        index=True,
        server_default=text("gen_random_uuid()"),
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
        default=EstadoCuentaUsuario.activo,
        server_default=text("'activo'"),
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

    # === Sistema de Personalización de Perfil ===
    banner_activo_id = Column(
        UUID(as_uuid=True),
        ForeignKey("avatar_asset.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        doc="ID del banner actualmente activo (asset de tipo backgrounds)",
    )
    banner_url = Column(TEXT, nullable=True, doc="URL del banner de fondo del perfil")
    marco_perfil_id = Column(
        UUID(as_uuid=True),
        ForeignKey("avatar_asset.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        doc="ID del marco decorativo alrededor del avatar (asset de tipo accessories)",
    )
    foto_perfil_custom_url = Column(
        TEXT,
        nullable=True,
        doc="URL de foto de perfil personalizada (alternativa al avatar generado)",
    )
    usa_foto_custom = Column(
        BOOLEAN,
        nullable=False,
        server_default=text("false"),
        doc="True: muestra foto_perfil_custom_url | False: muestra avatar generado",
    )

    coordinador = relationship("Coordinador", backref="usuario", uselist=False)
    estudiante = relationship("Estudiante", backref="usuario", uselist=False)

    # NOTA: mensajes no tiene FK a Usuario - se relaciona con salas_chat
    # mensajes = relationship("Mensaje", backref="usuario")

    #     archivos = relationship("ArchivoChat", backref="usuario")

    usuario_insignias = relationship(
        "UsuarioInsignia",
        back_populates="usuario",
        foreign_keys="UsuarioInsignia.usuario_id",
        passive_deletes=True,
    )

    usuario_recompensas = relationship(
        "UsuarioRecompensa", back_populates="usuario", passive_deletes=True
    )

    puntos = relationship("UsuarioPuntos", backref="usuario")

    historial_puntos = relationship(
        "HistorialPuntos", backref="usuario", passive_deletes=True
    )

    misiones_usuario = relationship(
        "MisionUsuario", back_populates="usuario", passive_deletes=True
    )

    temas_personalizados = relationship(
        "TemaPersonalizado", backref="usuario", passive_deletes=True
    )
    oauth_providers = relationship(
        "OAuthProvider", back_populates="usuario", passive_deletes=True
    )

    # Comentarios del usuario
    comentarios = relationship(
        "Comentario", back_populates="autor", passive_deletes=True
    )

    # === Relaciones de Personalización ===
    banner_activo = relationship(
        "AvatarAsset",
        foreign_keys=[banner_activo_id],
        passive_deletes=True,
        doc="Asset del banner activo",
    )
    marco_perfil = relationship(
        "AvatarAsset",
        foreign_keys=[marco_perfil_id],
        passive_deletes=True,
        doc="Asset del marco decorativo del perfil",
    )
