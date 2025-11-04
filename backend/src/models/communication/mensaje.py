from ...db.base_class import Base
from sqlalchemy import Column, ForeignKey, String, Integer, Boolean
from sqlalchemy.dialects.postgresql import UUID, TIMESTAMP, TEXT, JSON
from sqlalchemy.sql import func


class Mensaje(Base):
    """
    Modelo de Mensaje de Chat
    
    Representa un mensaje dentro de una sala de chat con:
    - Contenido en texto plano y HTML
    - Archivos adjuntos y metadatos
    - Sistema de respuestas (hilos)
    - Menciones a usuarios e IA
    - Reacciones y estado
    - Programación de mensajes
    """
    __tablename__ = "mensajes"

    # ============================================
    # IDENTIFICACIÓN Y RELACIONES
    # ============================================
    id = Column(UUID(as_uuid=True), primary_key=True)
    sala_id = Column(
        UUID(as_uuid=True),
        ForeignKey("salas_chat.id", ondelete="CASCADE"),
        nullable=False,
    )
    usuario_id = Column(
        UUID(as_uuid=True),
        ForeignKey("Usuario.usuario_id", ondelete="CASCADE"),
        nullable=False,
    )

    # ============================================
    # CONTENIDO
    # ============================================
    contenido = Column(TEXT, nullable=True)  # Texto plano
    contenido_html = Column(TEXT, nullable=True)  # HTML formateado
    texto = Column(TEXT, nullable=True)  # Alias de contenido
    tipo_mensaje = Column(String(50), nullable=True)  # texto, archivo, imagen, etc.
    
    # ============================================
    # ARCHIVOS Y ADJUNTOS
    # ============================================
    archivos_urls = Column(JSON, nullable=True)  # Lista de URLs de archivos
    metadatos_archivos = Column(JSON, nullable=True)  # Metadatos de archivos (tamaño, tipo, etc)
    datos_adjuntos = Column(JSON, nullable=True)  # Datos adicionales de adjuntos
    
    # ============================================
    # SISTEMA DE RESPUESTAS (HILOS)
    # ============================================
    mensaje_padre_id = Column(
        UUID(as_uuid=True),
        ForeignKey("mensajes.id", ondelete="CASCADE"),
        nullable=True,
    )
    es_respuesta = Column(Boolean, nullable=True, default=False)
    tiene_respuestas = Column(Boolean, nullable=True, default=False)
    numero_respuestas = Column(Integer, nullable=True, default=0)
    total_respuestas = Column(Integer, nullable=True, default=0)
    
    # ============================================
    # MENCIONES
    # ============================================
    menciones_usuarios = Column(JSON, nullable=True)  # Lista de user_ids mencionados
    menciones = Column(JSON, nullable=True)  # Alias de menciones_usuarios
    menciones_ia = Column(Boolean, nullable=True, default=False)  # Si menciona al bot IA
    menciones_todos = Column(Boolean, nullable=True, default=False)  # @everyone
    
    # ============================================
    # ESTADO Y METADATOS
    # ============================================
    estado = Column(String(50), nullable=True)  # enviado, leido, eliminado, etc.
    es_importante = Column(Boolean, nullable=True, default=False)  # Mensaje destacado
    es_anuncio = Column(Boolean, nullable=True, default=False)  # Mensaje de anuncio
    reacciones = Column(JSON, nullable=True)  # {emoji: [user_ids]}
    
    # ============================================
    # FECHAS Y AUDITORÍA
    # ============================================
    fecha_creacion = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=True)
    fecha_actualizacion = Column(TIMESTAMP(timezone=True), nullable=True)
    fecha_edicion = Column(TIMESTAMP(timezone=True), nullable=True)
    fecha_eliminacion = Column(TIMESTAMP(timezone=True), nullable=True)  # Eliminación lógica
    programado_para = Column(TIMESTAMP(timezone=True), nullable=True)  # Mensajes programados
    editado_por = Column(
        UUID(as_uuid=True),
        ForeignKey("Usuario.usuario_id", ondelete="SET NULL"),
        nullable=True,
    )
