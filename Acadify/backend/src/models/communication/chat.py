"""
Modelos para el sistema de comunicación y chat
Incluye: Salas de chat, mensajes, hilos de conversación, menciones y notificaciones
"""

from sqlalchemy import Column, String, Text, DateTime, Boolean, Integer, Enum, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
import enum

from ...db.base_class import Base


class TipoSala(str, enum.Enum):
    """Tipos de salas de chat"""
    CURSO = "curso"
    GRUPO = "grupo"
    TAREA = "tarea"
    PRIVADO = "privado"
    GENERAL = "general"


class TipoMensaje(str, enum.Enum):
    """Tipos de mensaje"""
    TEXTO = "texto"
    IMAGEN = "imagen"
    ARCHIVO = "archivo"
    AUDIO = "audio"
    VIDEO = "video"
    ENLACE = "enlace"
    SISTEMA = "sistema"  # Mensajes automáticos del sistema
    IA = "ia"  # Respuestas de Rutilio


class EstadoMensaje(str, enum.Enum):
    """Estados del mensaje"""
    ENVIADO = "enviado"
    ENTREGADO = "entregado"
    LEIDO = "leido"
    EDITADO = "editado"
    ELIMINADO = "eliminado"


class SalaChat(Base):
    """Salas de chat para diferentes contextos"""
    __tablename__ = "salas_chat"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nombre = Column(String(255), nullable=False)
    descripcion = Column(Text)
    tipo_sala = Column(Enum(TipoSala), nullable=False, default=TipoSala.GENERAL)
    
    # Referencias opcionales según el tipo
    curso_id = Column(UUID(as_uuid=True))  # Si es una sala de curso
    grupo_id = Column(UUID(as_uuid=True))  # Si es una sala de grupo
    tarea_id = Column(UUID(as_uuid=True))  # Si es una sala de tarea
    
    # Configuración
    es_publica = Column(Boolean, default=True)
    requiere_aprobacion = Column(Boolean, default=False)
    permite_archivos = Column(Boolean, default=True)
    max_participantes = Column(Integer)
    
    # Metadatos
    creador_id = Column(UUID(as_uuid=True), ForeignKey("Usuario.usuario_id"), nullable=False)
    fecha_creacion = Column(DateTime, server_default=func.now())
    fecha_actualizacion = Column(DateTime, onupdate=func.now())
    
    # Estado
    esta_activa = Column(Boolean, default=True)
    fecha_ultima_actividad = Column(DateTime)
    total_mensajes = Column(Integer, default=0)
    
    # Configuración adicional en JSON
    configuracion = Column(JSON)
    
    # Relaciones
    participantes = relationship("ParticipanteSala", back_populates="sala", cascade="all, delete-orphan")
    creador = relationship("Usuario", foreign_keys=[creador_id])


class ParticipanteSala(Base):
    """Usuarios participantes en una sala de chat"""
    __tablename__ = "participantes_sala"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    sala_id = Column(UUID(as_uuid=True), ForeignKey("salas_chat.id"), nullable=False)
    usuario_id = Column(UUID(as_uuid=True), ForeignKey("Usuario.usuario_id"), nullable=False)
    
    # Rol en la sala
    es_admin = Column(Boolean, default=False)
    es_moderador = Column(Boolean, default=False)
    puede_escribir = Column(Boolean, default=True)
    
    # Estado del participante
    esta_activo = Column(Boolean, default=True)
    fecha_union = Column(DateTime, server_default=func.now())
    fecha_ultima_lectura = Column(DateTime)
    mensajes_no_leidos = Column(Integer, default=0)
    
    # Configuración personal
    notificaciones_activas = Column(Boolean, default=True)
    sonido_activo = Column(Boolean, default=True)
    
    # Relaciones
    sala = relationship("SalaChat", back_populates="participantes")
    usuario = relationship("Usuario")


class MensajeChat(Base):
    """Mensajes en las salas de chat"""
    __tablename__ = "mensajes"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    sala_id = Column(UUID(as_uuid=True), ForeignKey("salas_chat.id"), nullable=False)
    usuario_id = Column(UUID(as_uuid=True), ForeignKey("Usuario.usuario_id"), nullable=False)
    
    # Contenido del mensaje
    texto = Column(Text)
    tipo_mensaje = Column(Enum(TipoMensaje), default=TipoMensaje.TEXTO)
    datos_adjuntos = Column(JSON)  # Archivos, imágenes, etc.
    
    # Metadatos
    fecha_creacion = Column(DateTime, server_default=func.now())
    fecha_edicion = Column(DateTime)
    editado_por = Column(UUID(as_uuid=True))
    estado = Column(Enum(EstadoMensaje), default=EstadoMensaje.ENVIADO)
    
    # Hilos de conversación
    mensaje_padre_id = Column(UUID(as_uuid=True), ForeignKey("mensajes.id"))
    es_respuesta = Column(Boolean, default=False)
    total_respuestas = Column(Integer, default=0)
    
    # Menciones
    menciones = Column(JSON)  # Lista de IDs de usuarios mencionados
    
    # Reacciones
    reacciones = Column(JSON)  # {emoji: [user_ids]}
    
    # Configuración especial
    es_importante = Column(Boolean, default=False)
    es_anuncio = Column(Boolean, default=False)
    programado_para = Column(DateTime)  # Para mensajes programados
    
    # Relaciones
    sala = relationship("SalaChat")
    usuario = relationship("Usuario")
    respuestas = relationship("MensajeChat", backref="mensaje_padre", remote_side=[id])
    lecturas = relationship("LecturaMensaje", back_populates="mensaje", cascade="all, delete-orphan")


class LecturaMensaje(Base):
    """Control de lectura de mensajes por usuario"""
    __tablename__ = "lecturas_mensajes"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    mensaje_id = Column(UUID(as_uuid=True), ForeignKey("mensajes.id"), nullable=False)
    usuario_id = Column(UUID(as_uuid=True), ForeignKey("Usuario.usuario_id"), nullable=False)
    
    fecha_lectura = Column(DateTime, server_default=func.now())
    
    # Relaciones
    mensaje = relationship("MensajeChat", back_populates="lecturas")
    usuario = relationship("Usuario")


class Notificacion(Base):
    """Sistema de notificaciones"""
    __tablename__ = "notificaciones"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    usuario_id = Column(UUID(as_uuid=True), ForeignKey("Usuario.usuario_id"), nullable=False)
    
    # Contenido de la notificación
    titulo = Column(String(255), nullable=False)
    mensaje = Column(Text)
    tipo = Column(String(50), nullable=False)  # mensaje, mencion, tarea, etc.
    
    # Referencias
    referencia_id = Column(UUID(as_uuid=True))  # ID del objeto relacionado
    referencia_tipo = Column(String(50))  # tipo del objeto (mensaje, tarea, etc.)
    
    # Estados
    leida = Column(Boolean, default=False)
    enviada_email = Column(Boolean, default=False)
    enviada_push = Column(Boolean, default=False)
    
    # Metadatos
    fecha_creacion = Column(DateTime, server_default=func.now())
    fecha_lectura = Column(DateTime)
    fecha_envio_email = Column(DateTime)
    
    # Datos adicionales
    datos_adicionales = Column(JSON)
    
    # Relaciones
    usuario = relationship("Usuario")


class ConfiguracionNotificaciones(Base):
    """Configuración personal de notificaciones por usuario"""
    __tablename__ = "configuracion_notificaciones"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    usuario_id = Column(UUID(as_uuid=True), ForeignKey("Usuario.usuario_id"), nullable=False, unique=True)
    
    # Configuración general
    notificaciones_activas = Column(Boolean, default=True)
    sonido_activo = Column(Boolean, default=True)
    
    # Notificaciones de tareas
    tareas_nuevas = Column(Boolean, default=True)
    tareas_vencimiento_24h = Column(Boolean, default=True)
    tareas_vencimiento_1h = Column(Boolean, default=True)
    tareas_calificadas = Column(Boolean, default=True)
    tareas_comentarios = Column(Boolean, default=True)
    
    # Notificaciones de chat
    mensajes_directos = Column(Boolean, default=True)
    menciones = Column(Boolean, default=True)
    respuestas_hilos = Column(Boolean, default=True)
    mensajes_importantes = Column(Boolean, default=True)
    
    # Notificaciones por email
    resumen_diario_email = Column(Boolean, default=False)
    urgentes_email = Column(Boolean, default=True)
    menciones_email = Column(Boolean, default=True)
    
    # Configuración de horarios
    horario_inicio = Column(String(5), default="08:00")  # HH:MM
    horario_fin = Column(String(5), default="22:00")  # HH:MM
    dias_activos = Column(JSON, default=lambda: [1,2,3,4,5])  # 1=Lun, 7=Dom
    
    # Metadatos
    fecha_actualizacion = Column(DateTime, onupdate=func.now())
    
    # Relaciones
    usuario = relationship("Usuario")