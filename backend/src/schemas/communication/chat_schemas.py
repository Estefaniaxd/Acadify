"""
Schemas Pydantic para el sistema de comunicación
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, validator
from uuid import UUID

from src.models.communication.chat import TipoSala, TipoMensaje, EstadoMensaje


# ==================== SCHEMAS DE SALA DE CHAT ====================

class SalaChatBase(BaseModel):
    """Schema base para sala de chat"""
    nombre: str = Field(..., min_length=1, max_length=255)
    descripcion: Optional[str] = None
    tipo_sala: TipoSala
    es_publica: bool = True
    permite_archivos: bool = True
    permite_menciones: bool = True
    permite_hilos: bool = True
    moderacion_activa: bool = False
    tags: Optional[str] = None


class SalaChatCreate(SalaChatBase):
    """Schema para crear sala de chat"""
    curso_id: Optional[UUID] = None
    grupo_id: Optional[UUID] = None
    tarea_id: Optional[UUID] = None
    configuracion_json: Optional[Dict[str, Any]] = None


class SalaChatUpdate(BaseModel):
    """Schema para actualizar sala de chat"""
    nombre: Optional[str] = Field(None, min_length=1, max_length=255)
    descripcion: Optional[str] = None
    es_publica: Optional[bool] = None
    permite_archivos: Optional[bool] = None
    permite_menciones: Optional[bool] = None
    permite_hilos: Optional[bool] = None
    moderacion_activa: Optional[bool] = None
    tags: Optional[str] = None
    configuracion_json: Optional[Dict[str, Any]] = None


class SalaChatResponse(SalaChatBase):
    """Schema de respuesta para sala de chat"""
    id: UUID
    curso_id: Optional[UUID] = None
    grupo_id: Optional[UUID] = None
    tarea_id: Optional[UUID] = None
    creador_id: UUID
    fecha_creacion: datetime
    fecha_actualizacion: Optional[datetime] = None
    ultimo_mensaje_fecha: Optional[datetime] = None
    configuracion_json: Optional[Dict[str, Any]] = None
    
    # Datos calculados
    total_participantes: Optional[int] = None
    mensajes_no_leidos: Optional[int] = None
    ultimo_mensaje: Optional[str] = None
    
    class Config:
        from_attributes = True


class SalaChatDetallada(SalaChatResponse):
    """Schema detallado con participantes y estadísticas"""
    participantes: Optional[List["ParticipanteSalaResponse"]] = None
    mensajes_recientes: Optional[List["MensajeResponse"]] = None
    estadisticas: Optional[Dict[str, Any]] = None


# ==================== SCHEMAS DE PARTICIPANTES ====================

class ParticipanteSalaBase(BaseModel):
    """Schema base para participante de sala"""
    es_admin: bool = False
    es_moderador: bool = False
    puede_escribir: bool = True
    notificaciones_activadas: bool = True
    sonido_activado: bool = True


class ParticipanteSalaCreate(ParticipanteSalaBase):
    """Schema para agregar participante"""
    sala_id: UUID
    usuario_id: UUID


class ParticipanteSalaUpdate(BaseModel):
    """Schema para actualizar participante"""
    es_admin: Optional[bool] = None
    es_moderador: Optional[bool] = None
    puede_escribir: Optional[bool] = None
    notificaciones_activadas: Optional[bool] = None
    sonido_activado: Optional[bool] = None


class ParticipanteSalaResponse(ParticipanteSalaBase):
    """Schema de respuesta para participante"""
    id: UUID
    sala_id: UUID
    usuario_id: UUID
    esta_activo: bool
    fecha_union: datetime
    fecha_ultima_lectura: Optional[datetime] = None
    ultimo_acceso: Optional[datetime] = None
    
    # Datos del usuario
    usuario_nombre: Optional[str] = None
    usuario_apellido: Optional[str] = None
    usuario_email: Optional[str] = None
    usuario_avatar: Optional[str] = None
    
    class Config:
        from_attributes = True


# ==================== SCHEMAS DE MENSAJES ====================

class MensajeBase(BaseModel):
    """Schema base para mensaje"""
    contenido: str = Field(..., min_length=1)
    tipo_mensaje: TipoMensaje = TipoMensaje.TEXTO
    es_importante: bool = False
    es_anuncio: bool = False


class MensajeCreate(MensajeBase):
    """Schema para crear mensaje"""
    sala_id: UUID
    mensaje_padre_id: Optional[UUID] = None
    archivos_urls: Optional[List[str]] = None
    metadatos_archivos: Optional[List[Dict[str, Any]]] = None
    menciones_usuarios: Optional[List[UUID]] = None
    menciones_ia: bool = False
    menciones_todos: bool = False


class MensajeUpdate(BaseModel):
    """Schema para actualizar mensaje"""
    contenido: Optional[str] = Field(None, min_length=1)
    es_importante: Optional[bool] = None


class MensajeResponse(MensajeBase):
    """Schema de respuesta para mensaje"""
    id: UUID
    sala_id: UUID
    usuario_id: UUID
    mensaje_padre_id: Optional[UUID] = None
    contenido_html: Optional[str] = None
    archivos_urls: Optional[List[str]] = None
    metadatos_archivos: Optional[List[Dict[str, Any]]] = None
    tiene_respuestas: bool = False
    numero_respuestas: int = 0
    menciones_usuarios: Optional[List[UUID]] = None
    menciones_ia: bool = False
    menciones_todos: bool = False
    estado: EstadoMensaje
    fecha_creacion: datetime
    fecha_actualizacion: Optional[datetime] = None
    reacciones: Optional[Dict[str, List[UUID]]] = None
    
    # Datos del usuario
    usuario_nombre: Optional[str] = None
    usuario_apellido: Optional[str] = None
    usuario_avatar: Optional[str] = None
    usuario_rol: Optional[str] = None
    
    # Estado de lectura para el usuario actual
    leido_por_usuario: Optional[bool] = None
    fecha_lectura: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class MensajeDetallado(MensajeResponse):
    """Schema detallado con respuestas y lecturas"""
    respuestas: Optional[List["MensajeResponse"]] = None
    lecturas: Optional[List["LecturaMensajeResponse"]] = None
    mensaje_padre: Optional["MensajeResponse"] = None


class ReaccionMensaje(BaseModel):
    """Schema para reacciones a mensajes"""
    mensaje_id: UUID
    emoji: str = Field(..., min_length=1, max_length=10)


# ==================== SCHEMAS DE LECTURA ====================

class LecturaMensajeResponse(BaseModel):
    """Schema para lectura de mensaje"""
    id: UUID
    mensaje_id: UUID
    usuario_id: UUID
    fecha_lectura: datetime
    usuario_nombre: Optional[str] = None
    usuario_avatar: Optional[str] = None
    
    class Config:
        from_attributes = True


class MarcarLectura(BaseModel):
    """Schema para marcar mensajes como leídos"""
    mensajes_ids: List[UUID]
    sala_id: Optional[UUID] = None


# ==================== SCHEMAS DE NOTIFICACIONES ====================

class NotificacionBase(BaseModel):
    """Schema base para notificación"""
    titulo: str = Field(..., min_length=1, max_length=255)
    mensaje: Optional[str] = None
    tipo_notificacion: str
    url_accion: Optional[str] = None
    icono: Optional[str] = None
    color: Optional[str] = Field(None, pattern=r'^#[0-9A-Fa-f]{6}$')


class NotificacionCreate(NotificacionBase):
    """Schema para crear notificación"""
    usuario_id: UUID
    sala_id: Optional[UUID] = None
    mensaje_id: Optional[UUID] = None
    tarea_id: Optional[UUID] = None
    curso_id: Optional[UUID] = None
    datos_adicionales: Optional[Dict[str, Any]] = None


class NotificacionResponse(NotificacionBase):
    """Schema de respuesta para notificación"""
    id: UUID
    usuario_id: UUID
    sala_id: Optional[UUID] = None
    mensaje_id: Optional[UUID] = None
    tarea_id: Optional[UUID] = None
    curso_id: Optional[UUID] = None
    leida: bool = False
    enviada_email: bool = False
    enviada_push: bool = False
    fecha_creacion: datetime
    fecha_lectura: Optional[datetime] = None
    datos_adicionales: Optional[Dict[str, Any]] = None
    
    class Config:
        from_attributes = True


class MarcarNotificacionLeida(BaseModel):
    """Schema para marcar notificaciones como leídas"""
    notificaciones_ids: List[UUID]


# ==================== SCHEMAS DE CONFIGURACIÓN ====================

class ConfiguracionNotificacionesBase(BaseModel):
    """Schema base para configuración de notificaciones"""
    notificaciones_activas: bool = True
    sonido_activo: bool = True
    
    # Notificaciones de tareas
    tareas_nuevas: bool = True
    tareas_vencimiento_24h: bool = True
    tareas_vencimiento_1h: bool = True
    tareas_calificadas: bool = True
    tareas_comentarios: bool = True
    
    # Notificaciones de chat
    mensajes_directos: bool = True
    menciones: bool = True
    respuestas_hilos: bool = True
    mensajes_importantes: bool = True
    
    # Notificaciones por email
    resumen_diario_email: bool = False
    urgentes_email: bool = True
    menciones_email: bool = True
    
    # Configuración de horarios
    horario_inicio: str = Field("08:00", pattern=r'^([01]\d|2[0-3]):[0-5]\d$')
    horario_fin: str = Field("22:00", pattern=r'^([01]\d|2[0-3]):[0-5]\d$')
    dias_activos: List[int] = Field(default=[1,2,3,4,5], min_items=1, max_items=7)
    
    @validator('dias_activos')
    def validar_dias(cls, v):
        if not all(1 <= dia <= 7 for dia in v):
            raise ValueError('Los días deben estar entre 1 (Lun) y 7 (Dom)')
        return v


class ConfiguracionNotificacionesUpdate(ConfiguracionNotificacionesBase):
    """Schema para actualizar configuración"""
    pass


class ConfiguracionNotificacionesResponse(ConfiguracionNotificacionesBase):
    """Schema de respuesta para configuración"""
    id: UUID
    usuario_id: UUID
    fecha_actualizacion: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# ==================== SCHEMAS DE FILTROS Y BÚSQUEDA ====================

class FiltrosSalas(BaseModel):
    """Filtros para buscar salas"""
    tipo_sala: Optional[TipoSala] = None
    es_publica: Optional[bool] = None
    curso_id: Optional[UUID] = None
    grupo_id: Optional[UUID] = None
    buscar: Optional[str] = None
    solo_participando: bool = True
    incluir_archivadas: bool = False
    ordenar_por: str = "ultimo_mensaje_fecha"
    orden_desc: bool = True
    limite: int = Field(50, le=100)
    offset: int = Field(0, ge=0)


class FiltrosMensajes(BaseModel):
    """Filtros para buscar mensajes"""
    sala_id: Optional[UUID] = None
    usuario_id: Optional[UUID] = None
    tipo_mensaje: Optional[TipoMensaje] = None
    solo_importantes: Optional[bool] = None
    solo_anuncios: Optional[bool] = None
    con_archivos: Optional[bool] = None
    menciona_usuario: Optional[UUID] = None
    menciona_ia: Optional[bool] = None
    fecha_desde: Optional[datetime] = None
    fecha_hasta: Optional[datetime] = None
    buscar: Optional[str] = None
    solo_no_leidos: bool = False
    incluir_hilos: bool = True
    ordenar_por: str = "fecha_creacion"
    orden_desc: bool = True
    limite: int = Field(50, le=100)
    offset: int = Field(0, ge=0)


class FiltrosNotificaciones(BaseModel):
    """Filtros para notificaciones"""
    tipo_notificacion: Optional[str] = None
    solo_no_leidas: bool = False
    fecha_desde: Optional[datetime] = None
    fecha_hasta: Optional[datetime] = None
    ordenar_por: str = "fecha_creacion"
    orden_desc: bool = True
    limite: int = Field(20, le=100)
    offset: int = Field(0, ge=0)


# ==================== SCHEMAS DE ESTADÍSTICAS ====================

class EstadisticasSala(BaseModel):
    """Estadísticas de una sala"""
    total_mensajes: int = 0
    total_participantes: int = 0
    mensajes_hoy: int = 0
    mensajes_semana: int = 0
    participantes_activos: int = 0
    usuario_mas_activo: Optional[str] = None
    hora_mas_activa: Optional[str] = None
    tipos_mensaje: Dict[str, int] = {}
    reacciones_populares: Dict[str, int] = {}


class EstadisticasUsuario(BaseModel):
    """Estadísticas de comunicación de un usuario"""
    mensajes_enviados: int = 0
    salas_participando: int = 0
    menciones_recibidas: int = 0
    reacciones_recibidas: int = 0
    tiempo_respuesta_promedio: Optional[float] = None  # En minutos
    dias_mas_activos: List[int] = []  # 1=Lun, 7=Dom