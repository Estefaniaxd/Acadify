from ...db.base_class import Base
from sqlalchemy import Column, text, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID, TIMESTAMP, ENUM, TEXT, BOOLEAN, INTEGER
from ...enums.communication.chat_grupo_enums import EstadoChatGrupo
from sqlalchemy.orm import relationship

class ChatGrupo(Base):
    __tablename__ = "ChatGrupo"

    chat_grupo_id = Column(
    UUID(as_uuid=True), primary_key=True, server_default=text('gen_random_uuid()')
    )
    grupo_id = Column(
        UUID(as_uuid=True),
        ForeignKey("Grupo.grupo_id", ondelete="CASCADE"),
        nullable=False,
    )
    fecha_creacion = Column(
        TIMESTAMP(timezone=True), nullable=False, server_default=func.now()
    )
    descripcion = Column(TEXT)
    foto_perfil = Column(TEXT)
    permite_archivos = Column(BOOLEAN, nullable=False, server_default=text("true"))
    capacidad_almacenamiento = Column(
        INTEGER(), nullable=False, server_default=text("52428800")
    )
    estado_chat = Column(
        ENUM(EstadoChatGrupo, name="estado_chat_grupo", create_type=False),
        nullable=False,
        default=EstadoChatGrupo.activo,
        server_default=text("'activo'"),
    )

    mensajes = relationship("Mensaje", backref="chat_grupo", passive_deletes=True)

    archivos = relationship("ArchivoChat", backref="chat_grupo", passive_deletes=True)
