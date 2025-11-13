# NOTA: Este modelo está deshabilitado temporalmente porque hace referencia
# a la tabla 'ChatGrupo' que no existe en los modelos activos.
# Se debe revisar y actualizar cuando se implemente el sistema de chat completo.

# from ...db.base_class import Base
# from sqlalchemy import Column, text, ForeignKey
# from sqlalchemy.dialects.postgresql import UUID, TIMESTAMP, TEXT
# from sqlalchemy.sql import func

# class ArchivoChat(Base):
#     __tablename__ = "ArchivoChat"

#     archivo_id = Column(
#     UUID(as_uuid=True), primary_key=True, server_default=text('gen_random_uuid()')
#     )
#     chat_grupo_id = Column(
#         UUID(as_uuid=True),
#         ForeignKey("ChatGrupo.chat_grupo_id", ondelete="CASCADE"),
#         nullable=False,
#     )
#     usuario_id = Column(
#         UUID(as_uuid=True),
#         ForeignKey("Usuario.usuario_id", ondelete="SET NULL"),
#         nullable=True,
#     )
#     nombre_archivo = Column(TEXT, nullable=False)
#     url_archivo = Column(TEXT, nullable=False)
#     fecha_envio = Column(
#         TIMESTAMP(timezone=True), server_default=func.now(), nullable=False
#     )
#     tipo_archivo = Column(TEXT)
