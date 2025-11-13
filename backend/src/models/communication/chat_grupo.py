from sqlalchemy import Column, ForeignKey, func, text
from sqlalchemy.dialects.postgresql import BOOLEAN, ENUM, INTEGER, TEXT, TIMESTAMP, UUID
from sqlalchemy.orm import relationship

from src.db.base_class import Base
from src.enums.communication.chat_grupo_enums import EstadoChatGrupo


class ChatGrupo(Base):
    __tablename__ = "ChatGrupo"

    chat_grupo_id = Column(
        UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
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

    # Relación con archivos del chat del grupo
    #     archivos = relationship("ArchivoChat", backref="chat_grupo", passive_deletes=True)

    # NOTA: ChatGrupo NO tiene relación directa con Mensaje
    # Los mensajes se relacionan con SalaChat (salas_chat), no con ChatGrupo
