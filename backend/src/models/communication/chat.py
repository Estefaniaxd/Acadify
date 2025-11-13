"""Modelos para el sistema de comunicación y chat
Incluye: Salas de chat, mensajes, hilos de conversación, menciones y notificaciones.
"""

import enum
import uuid

from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    Text,
    Time,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship, Mapped
from sqlalchemy.sql import func

from src.db.base_class import Base


class TipoSala(str, enum.Enum):
    """Tipos de salas de chat."""

    CURSO = "curso"
    GRUPO = "grupo"
    TAREA = "tarea"
    PRIVADO = "privado"
    GENERAL = "general"


class TipoMensaje(str, enum.Enum):
    """Tipos de mensaje."""

    TEXTO = "texto"
    IMAGEN = "imagen"
    ARCHIVO = "archivo"
    AUDIO = "audio"
    VIDEO = "video"
    ENLACE = "enlace"
    SISTEMA = "sistema"  # Mensajes automáticos del sistema
    IA = "ia"  # Respuestas de Rutilio


class EstadoMensaje(str, enum.Enum):
    """Estados del mensaje."""

    ENVIADO = "enviado"
    ENTREGADO = "entregado"
    LEIDO = "leido"
    EDITADO = "editado"
    ELIMINADO = "eliminado"


class SalaChat(Base):
    """Salas de chat para diferentes contextos."""

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
    permite_menciones = Column(Boolean, default=True)
    permite_hilos = Column(Boolean, default=True)
    moderacion_activa = Column(Boolean, default=False)
    max_participantes = Column(Integer)
    tags = Column(String)

    # Metadatos
    creador_id = Column(
        UUID(as_uuid=True), ForeignKey("Usuario.usuario_id"), nullable=False
    )
    fecha_creacion = Column(DateTime, server_default=func.now())
    fecha_actualizacion = Column(DateTime, onupdate=func.now())

    # Estado
    esta_activa = Column(Boolean, default=True)
    fecha_ultima_actividad = Column(DateTime)
    ultimo_mensaje_fecha = Column(DateTime)
    total_mensajes = Column(Integer, default=0)

    # Configuración adicional en JSON
    configuracion = Column(JSON)

    # Relaciones
    participantes = relationship(
        "ParticipanteSala", back_populates="sala", cascade="all, delete-orphan"
    )
    videollamadas: Mapped[list["Videollamada"]] = relationship(back_populates="sala_chat", cascade="all, delete-orphan")
    creador = relationship("Usuario", foreign_keys=[creador_id])


class ParticipanteSala(Base):
    """Usuarios participantes en una sala de chat."""

    __tablename__ = "participantes_sala"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    sala_id = Column(UUID(as_uuid=True), ForeignKey("salas_chat.id"), nullable=False)
    usuario_id = Column(
        UUID(as_uuid=True), ForeignKey("Usuario.usuario_id"), nullable=False
    )

    # Rol en la sala
    rol = Column(String)
    es_admin = Column(Boolean, default=False)
    es_moderador = Column(Boolean, default=False)
    puede_escribir = Column(Boolean, default=True)
    puede_eliminar = Column(Boolean, default=False)
    puede_gestionar_participantes = Column(Boolean, default=False)

    # Estado del participante
    esta_activo = Column(Boolean, default=True)
    es_silenciado = Column(Boolean, default=False)
    fecha_union = Column(DateTime, server_default=func.now())
    fecha_ingreso = Column(DateTime)
    fecha_salida = Column(DateTime)
    fecha_ultima_lectura = Column(DateTime)
    mensajes_no_leidos = Column(Integer, default=0)

    # Configuración personal
    notificaciones_activas = Column(Boolean, default=True)
    sonido_activo = Column(Boolean, default=True)

    # Relaciones
    sala = relationship("SalaChat", back_populates="participantes")
    usuario = relationship("Usuario")


# NOTA: MensajeChat está DEPRECATED - Se usa el modelo Mensaje de mensaje.py
# que tiene 29 campos completos vs 18 campos básicos de MensajeChat
# class MensajeChat(Base): ...  <-- ELIMINADO para evitar duplicación de tabla 'mensajes'


class LecturaMensaje(Base):
    """Control de lectura de mensajes por usuario.

    Registra cuándo cada usuario lee un mensaje específico,
    útil para funcionalidades de "visto por" y notificaciones.

    Attributes:
        id: Identificador único del registro
        mensaje_id: Referencia al mensaje leído
        usuario_id: Usuario que leyó el mensaje
        fecha_lectura: Timestamp de la lectura
        dispositivo: Dispositivo desde el cual se leyó (opcional)
    """

    __tablename__ = "lecturas_mensajes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    mensaje_id = Column(
        UUID(as_uuid=True), ForeignKey("mensajes.id"), nullable=False, index=True
    )
    usuario_id = Column(
        UUID(as_uuid=True), ForeignKey("Usuario.usuario_id"), nullable=False, index=True
    )

    fecha_lectura = Column(DateTime, server_default=func.now())
    dispositivo = Column(String)

    # Relaciones - Usar Mensaje del archivo mensaje.py
    # mensaje = relationship("Mensaje", back_populates="lecturas")
    usuario = relationship("Usuario")


class Notificacion(Base):
    """Sistema de notificaciones del sistema educativo.

    Maneja todas las notificaciones para usuarios: mensajes, menciones,
    tareas, eventos académicos, etc. Soporta múltiples canales de entrega
    (in-app, email, push) y tracking detallado.

    Attributes:
        id: Identificador único de la notificación
        usuario_id: Usuario destinatario
        titulo: Título de la notificación
        mensaje: Contenido del mensaje
        tipo_notificacion: Tipo de notificación
        url_accion: URL para acción asociada
        icono: Icono para mostrar
        color: Color temático
        prioridad: Nivel de prioridad
        sala_id: Referencia a sala de chat (opcional)
        mensaje_id: Referencia a mensaje (opcional)
        tarea_id: Referencia a tarea (opcional)
        curso_id: Referencia a curso (opcional)
    """

    __tablename__ = "notificaciones"

    # Identificación
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    usuario_id = Column(
        UUID(as_uuid=True), ForeignKey("Usuario.usuario_id"), nullable=False, index=True
    )

    # Contenido de la notificación
    titulo = Column(String(255), nullable=False)
    mensaje = Column(Text)
    tipo = Column(String(50), nullable=False)  # mensaje, mencion, tarea, etc.
    tipo_notificacion = Column(String)
    url_accion = Column(String)
    icono = Column(String)
    color = Column(String)

    # Referencias generales
    referencia_id = Column(UUID(as_uuid=True))  # ID del objeto relacionado
    referencia_tipo = Column(String(50))  # tipo del objeto (mensaje, tarea, etc.)

    # Referencias específicas (para queries más eficientes)
    sala_id = Column(UUID(as_uuid=True), ForeignKey("salas_chat.id"), index=True)
    mensaje_id = Column(UUID(as_uuid=True), ForeignKey("mensajes.id"), index=True)
    tarea_id = Column(UUID(as_uuid=True))
    curso_id = Column(UUID(as_uuid=True))

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
    usuario = relationship("Usuario", foreign_keys=[usuario_id])
    sala = relationship("SalaChat", foreign_keys=[sala_id])
    # mensaje = relationship("Mensaje", foreign_keys=[mensaje_id])  # Relación con Mensaje

    @property
    def esta_leida(self) -> bool:
        """Verifica si la notificación fue leída."""
        return self.leida

    @property
    def tiene_accion(self) -> bool:
        """Verifica si la notificación tiene URL de acción."""
        return bool(self.url_accion)

    def marcar_como_leida(self) -> None:
        """Marca la notificación como leída."""
        if not self.leida:
            self.leida = True
            self.fecha_lectura = func.now()

    def to_dict(self) -> dict:
        """Serializa el modelo a diccionario."""
        return {
            "id": str(self.id),
            "usuario_id": str(self.usuario_id),
            "titulo": self.titulo,
            "mensaje": self.mensaje,
            "tipo": self.tipo,
            "tipo_notificacion": self.tipo_notificacion,
            "url_accion": self.url_accion,
            "icono": self.icono,
            "color": self.color,
            "sala_id": str(self.sala_id) if self.sala_id else None,
            "mensaje_id": str(self.mensaje_id) if self.mensaje_id else None,
            "tarea_id": str(self.tarea_id) if self.tarea_id else None,
            "curso_id": str(self.curso_id) if self.curso_id else None,
            "leida": self.leida,
            "enviada_email": self.enviada_email,
            "enviada_push": self.enviada_push,
            "fecha_creacion": (
                self.fecha_creacion.isoformat() if self.fecha_creacion else None
            ),
            "fecha_lectura": (
                self.fecha_lectura.isoformat() if self.fecha_lectura else None
            ),
            "datos_adicionales": self.datos_adicionales,
            "esta_leida": self.esta_leida,
            "tiene_accion": self.tiene_accion,
        }


class ConfiguracionNotificaciones(Base):
    """Configuración personal de notificaciones por usuario.

    Permite a cada usuario configurar sus preferencias de notificaciones
    para mensajes, menciones, respuestas y reacciones en el sistema de chat.
    Incluye configuraciones de sonido, vibración, previsualizaciones y modo no molestar.

    Attributes:
        id: Identificador único de la configuración
        usuario_id: Usuario propietario de la configuración
        notif_mensajes_directos: Notificaciones para mensajes directos
        notif_menciones: Notificaciones cuando es mencionado
        notif_respuestas: Notificaciones para respuestas a sus mensajes
        notif_reacciones: Notificaciones para reacciones a sus mensajes
        sonido_activo: Reproducir sonido en notificaciones
        vibration_activa: Vibración en notificaciones móviles
        preview_mensajes: Mostrar preview del contenido
        modo_no_molestar: Modo no molestar activado
        hora_inicio_no_molestar: Hora de inicio del modo no molestar
        hora_fin_no_molestar: Hora de fin del modo no molestar
    """

    __tablename__ = "configuracion_notificaciones"

    # Identificación
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    usuario_id = Column(
        UUID(as_uuid=True),
        ForeignKey("Usuario.usuario_id"),
        nullable=False,
        unique=True,
        index=True,
    )

    # Configuración de notificaciones de chat
    notif_mensajes_directos = Column(Boolean, default=True)
    notif_menciones = Column(Boolean, default=True)
    notif_respuestas = Column(Boolean, default=True)
    notif_reacciones = Column(Boolean, default=True)

    # Configuración de presentación
    sonido_activo = Column(Boolean, default=True)
    vibration_activa = Column(Boolean, default=True)
    preview_mensajes = Column(Boolean, default=True)

    # Modo no molestar
    modo_no_molestar = Column(Boolean, default=False)
    hora_inicio_no_molestar = Column(Time)
    hora_fin_no_molestar = Column(Time)

    # Metadatos
    fecha_creacion = Column(DateTime, server_default=func.now())
    fecha_actualizacion = Column(DateTime, onupdate=func.now())

    # Relaciones
    usuario = relationship("Usuario", foreign_keys=[usuario_id])

    @property
    def notificaciones_activas(self) -> bool:
        """Verifica si alguna notificación está activa."""
        return any(
            [
                self.notif_mensajes_directos,
                self.notif_menciones,
                self.notif_respuestas,
                self.notif_reacciones,
            ]
        )

    @property
    def en_modo_no_molestar(self) -> bool:
        """Verifica si está en modo no molestar."""
        if not self.modo_no_molestar:
            return False

        if not self.hora_inicio_no_molestar or not self.hora_fin_no_molestar:
            return self.modo_no_molestar

        from datetime import UTC, datetime

        hora_actual = datetime.now(UTC).time()

        # Si hora_inicio < hora_fin (mismo día)
        if self.hora_inicio_no_molestar < self.hora_fin_no_molestar:
            return (
                self.hora_inicio_no_molestar <= hora_actual <= self.hora_fin_no_molestar
            )
        # Si hora_inicio > hora_fin (cruza medianoche)
        return (
            hora_actual >= self.hora_inicio_no_molestar
            or hora_actual <= self.hora_fin_no_molestar
        )

    def to_dict(self) -> dict:
        """Serializa el modelo a diccionario."""
        return {
            "id": str(self.id),
            "usuario_id": str(self.usuario_id),
            "notif_mensajes_directos": self.notif_mensajes_directos,
            "notif_menciones": self.notif_menciones,
            "notif_respuestas": self.notif_respuestas,
            "notif_reacciones": self.notif_reacciones,
            "sonido_activo": self.sonido_activo,
            "vibration_activa": self.vibration_activa,
            "preview_mensajes": self.preview_mensajes,
            "modo_no_molestar": self.modo_no_molestar,
            "hora_inicio_no_molestar": (
                str(self.hora_inicio_no_molestar)
                if self.hora_inicio_no_molestar
                else None
            ),
            "hora_fin_no_molestar": (
                str(self.hora_fin_no_molestar) if self.hora_fin_no_molestar else None
            ),
            "fecha_creacion": (
                self.fecha_creacion.isoformat() if self.fecha_creacion else None
            ),
            "fecha_actualizacion": (
                self.fecha_actualizacion.isoformat()
                if self.fecha_actualizacion
                else None
            ),
            "notificaciones_activas": self.notificaciones_activas,
            "en_modo_no_molestar": self.en_modo_no_molestar,
        }
