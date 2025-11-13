"""
Schemas Pydantic v2 para el sistema de videollamadas con Jitsi.

Este módulo define todos los schemas de validación, serialización y 
documentación para las videollamadas, participantes y grabaciones.

Siguiendo principios:
- Single Responsibility: Cada schema tiene un propósito específico
- Open/Closed: Extensible mediante herencia sin modificar base
- Liskov Substitution: Schemas derivados sustituibles
- Interface Segregation: Schemas específicos por caso de uso
- Dependency Inversion: No dependemos de implementaciones concretas

Utiliza Python Enums para type-safety y validación de valores.
"""

from typing import Optional, List, Dict, Any, Literal
from datetime import datetime
from pydantic import (
    BaseModel, 
    Field, 
    field_validator, 
    model_validator,
    ConfigDict
)
from uuid import UUID

# Importar enums
from src.enums.communication.videollamada_enums import (
    TipoLlamada,
    EstadoVideollamada,
    CalidadConexion,
    FormatoGrabacion,
    CalidadGrabacion,
    EstadoProcesamiento,
)


# ==================== SCHEMAS BASE DE VIDEOLLAMADA ====================

class VideollamadaBase(BaseModel):
    """
    Schema base para videollamada.
    
    Contiene los campos comunes que se usan en múltiples operaciones.
    Siguiendo SRP: Solo contiene campos básicos sin lógica de negocio.
    """
    jitsi_room_name: str = Field(
        ...,
        min_length=3,
        max_length=255,
        description="Nombre único de la sala Jitsi",
        examples=["curso-matematicas-2024", "reunion-equipo-dev"]
    )
    tipo_llamada: TipoLlamada = Field(
        ...,
        description="Tipo de llamada: video o voz",
        examples=[TipoLlamada.VIDEO, TipoLlamada.VOZ]
    )
    sala_chat_id: Optional[UUID] = Field(
        None,
        description="UUID de la sala de chat asociada (opcional)"
    )
    configuracion: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Configuración adicional en formato JSON",
        examples=[{
            "max_participantes": 50,
            "permitir_grabacion": True,
            "calidad_video": "HD",
            "idioma": "es"
        }]
    )

    @field_validator('jitsi_room_name')
    @classmethod
    def validate_room_name(cls, v: str) -> str:
        """
        Valida que el nombre de sala sea alfanumérico con guiones.
        
        Args:
            v: Nombre de sala a validar
            
        Returns:
            str: Nombre validado
            
        Raises:
            ValueError: Si el formato no es válido
        """
        # Permitir letras, números, guiones y guiones bajos
        import re
        if not re.match(r'^[a-zA-Z0-9_-]+$', v):
            raise ValueError(
                "El nombre de sala debe contener solo letras, números, guiones y guiones bajos"
            )
        return v.lower()  # Normalizar a minúsculas

    @field_validator('configuracion')
    @classmethod
    def validate_configuracion(cls, v: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Valida y normaliza la configuración.
        
        Args:
            v: Configuración a validar
            
        Returns:
            Dict: Configuración validada
        """
        if v is None:
            return {}
        
        # Validar max_participantes si está presente
        if 'max_participantes' in v:
            max_part = v['max_participantes']
            if not isinstance(max_part, int) or max_part < 2 or max_part > 500:
                raise ValueError(
                    "max_participantes debe ser un entero entre 2 y 500"
                )
        
        return v


class VideollamadaCreate(VideollamadaBase):
    """
    Schema para crear una nueva videollamada.
    
    Incluye solo los campos necesarios para iniciar una llamada.
    El iniciador_id se obtiene del usuario autenticado en el endpoint.
    El jitsi_room_name es opcional - si no se provee, el service lo genera automáticamente.
    """
    # Heredamos de VideollamadaBase pero hacemos jitsi_room_name opcional
    jitsi_room_name: Optional[str] = Field(
        None,
        min_length=3,
        max_length=255,
        description="Nombre único de la sala Jitsi (opcional, se genera automáticamente si no se provee)",
        examples=["curso-matematicas-2024", "reunion-equipo-dev"]
    )
    
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "tipo_llamada": "video",
                    "sala_chat_id": "123e4567-e89b-12d3-a456-426614174000",
                    "titulo": "Clase de Matemáticas",
                    "configuracion": {
                        "max_participantes": 30,
                        "permitir_grabacion": True,
                        "calidad_video": "HD"
                    }
                },
                {
                    "jitsi_room_name": "reunion-equipo",
                    "tipo_llamada": "voz",
                    "titulo": "Reunión de Equipo",
                    "configuracion": {
                        "max_participantes": 10
                    }
                }
            ]
        }
    )


class VideollamadaUpdate(BaseModel):
    """
    Schema para actualizar una videollamada existente.
    
    Todos los campos son opcionales para permitir actualizaciones parciales.
    """
    transcripcion: Optional[str] = Field(
        None,
        description="Transcripción completa de la llamada",
        max_length=50000
    )
    resumen_ia: Optional[str] = Field(
        None,
        description="Resumen generado por IA",
        max_length=5000
    )
    grabacion_url: Optional[str] = Field(
        None,
        description="URL de la grabación principal",
        max_length=500
    )
    configuracion: Optional[Dict[str, Any]] = Field(
        None,
        description="Actualizar configuración"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "transcripcion": "Usuario 1: Hola a todos...",
                    "resumen_ia": "Se discutió sobre el proyecto X, decisiones: ..."
                }
            ]
        }
    )


class VideollamadaResponse(VideollamadaBase):
    """
    Schema de respuesta para videollamada.
    
    Incluye todos los campos del modelo, incluyendo timestamps y estado.
    """
    id: UUID = Field(..., description="UUID único de la videollamada")
    iniciador_id: UUID = Field(..., description="UUID del usuario iniciador")
    estado: EstadoVideollamada = Field(
        ...,
        description="Estado actual de la llamada"
    )
    fecha_inicio: datetime = Field(..., description="Fecha y hora de inicio")
    fecha_fin: Optional[datetime] = Field(
        None,
        description="Fecha y hora de finalización"
    )
    duracion_segundos: Optional[int] = Field(
        None,
        ge=0,
        description="Duración total en segundos"
    )
    grabacion_url: Optional[str] = Field(None, description="URL de grabación")
    transcripcion: Optional[str] = Field(None, description="Transcripción completa")
    resumen_ia: Optional[str] = Field(None, description="Resumen generado por IA")
    created_at: datetime = Field(..., description="Timestamp de creación")
    updated_at: datetime = Field(..., description="Timestamp de última actualización")
    
    # Campos opcionales calculados
    total_participantes: Optional[int] = Field(
        None,
        description="Total de participantes (calculado)"
    )
    participantes_activos: Optional[int] = Field(
        None,
        description="Participantes actualmente en la llamada (calculado)"
    )

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "examples": [
                {
                    "id": "123e4567-e89b-12d3-a456-426614174000",
                    "jitsi_room_name": "clase-matematicas-101",
                    "tipo_llamada": "video",
                    "sala_chat_id": "223e4567-e89b-12d3-a456-426614174000",
                    "iniciador_id": "323e4567-e89b-12d3-a456-426614174000",
                    "estado": "activa",
                    "fecha_inicio": "2025-11-01T14:30:00Z",
                    "fecha_fin": None,
                    "duracion_segundos": None,
                    "total_participantes": 5,
                    "participantes_activos": 5,
                    "configuracion": {"max_participantes": 30},
                    "created_at": "2025-11-01T14:30:00Z",
                    "updated_at": "2025-11-01T14:30:00Z"
                }
            ]
        }
    )


class VideollamadaDetallada(VideollamadaResponse):
    """
    Schema detallado con participantes y grabaciones cargadas.
    
    Utilizado cuando se necesita información completa de la videollamada.
    """
    participantes: List["ParticipanteResponse"] = Field(
        default_factory=list,
        description="Lista de participantes en la llamada"
    )
    grabaciones: List["GrabacionResponse"] = Field(
        default_factory=list,
        description="Lista de grabaciones disponibles"
    )
    estadisticas: Optional[Dict[str, Any]] = Field(
        None,
        description="Estadísticas adicionales de la llamada"
    )

    model_config = ConfigDict(from_attributes=True)


class VideollamadaInDB(VideollamadaResponse):
    """
    Schema para representación en base de datos.
    
    Incluye campos internos como deleted_at para soft delete.
    """
    deleted_at: Optional[datetime] = Field(
        None,
        description="Timestamp de eliminación lógica"
    )

    model_config = ConfigDict(from_attributes=True)


# ==================== SCHEMAS DE FILTROS ====================

class VideollamadaFilter(BaseModel):
    """
    Schema para filtrar videollamadas.
    
    Permite búsquedas complejas con múltiples criterios.
    """
    sala_chat_id: Optional[UUID] = Field(
        None,
        description="Filtrar por sala de chat"
    )
    iniciador_id: Optional[UUID] = Field(
        None,
        description="Filtrar por usuario iniciador"
    )
    tipo_llamada: Optional[TipoLlamada] = Field(
        None,
        description="Filtrar por tipo de llamada"
    )
    estado: Optional[EstadoVideollamada] = Field(
        None,
        description="Filtrar por estado"
    )
    fecha_inicio_desde: Optional[datetime] = Field(
        None,
        description="Fecha mínima de inicio"
    )
    fecha_inicio_hasta: Optional[datetime] = Field(
        None,
        description="Fecha máxima de inicio"
    )
    incluir_finalizadas: bool = Field(
        False,
        description="Incluir llamadas finalizadas y canceladas"
    )
    skip: int = Field(
        0,
        ge=0,
        description="Número de registros a saltar (paginación)"
    )
    limit: int = Field(
        100,
        ge=1,
        le=500,
        description="Número máximo de registros a retornar"
    )
    ordenar_por: Literal["fecha_inicio", "duracion", "participantes"] = Field(
        "fecha_inicio",
        description="Campo por el cual ordenar"
    )
    orden_desc: bool = Field(
        True,
        description="Ordenar descendente (más reciente primero)"
    )

    @model_validator(mode='after')
    def validate_date_range(self) -> 'VideollamadaFilter':
        """
        Valida que el rango de fechas sea consistente.
        
        Returns:
            VideollamadaFilter: Filtro validado
            
        Raises:
            ValueError: Si fecha_hasta es anterior a fecha_desde
        """
        if (self.fecha_inicio_desde and self.fecha_inicio_hasta and 
            self.fecha_inicio_desde > self.fecha_inicio_hasta):
            raise ValueError(
                "fecha_inicio_hasta debe ser posterior a fecha_inicio_desde"
            )
        return self

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "estado": "activa",
                    "tipo_llamada": "video",
                    "skip": 0,
                    "limit": 50,
                    "ordenar_por": "fecha_inicio",
                    "orden_desc": True
                }
            ]
        }
    )


# ==================== SCHEMAS DE PARTICIPANTES ====================

class ParticipanteBase(BaseModel):
    """
    Schema base para participante de videollamada.
    """
    es_moderador: bool = Field(
        False,
        description="Si tiene privilegios de moderador en la llamada"
    )


class ParticipanteCreate(ParticipanteBase):
    """
    Schema para agregar participante a videollamada.
    """
    videollamada_id: UUID = Field(..., description="UUID de la videollamada")
    usuario_id: UUID = Field(..., description="UUID del usuario a agregar")

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "videollamada_id": "123e4567-e89b-12d3-a456-426614174000",
                    "usuario_id": "223e4567-e89b-12d3-a456-426614174000",
                    "es_moderador": False
                }
            ]
        }
    )


class ParticipanteUpdate(BaseModel):
    """
    Schema para actualizar participante.
    """
    es_moderador: Optional[bool] = Field(
        None,
        description="Actualizar privilegios de moderador"
    )
    calidad_conexion: Optional[CalidadConexion] = Field(
        None,
        description="Actualizar calidad de conexión reportada"
    )
    datos_conexion: Optional[Dict[str, Any]] = Field(
        None,
        description="Actualizar métricas de conexión"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "calidad_conexion": "buena",
                    "datos_conexion": {
                        "latencia_ms": 45,
                        "perdida_paquetes": 0.5,
                        "bitrate_kbps": 1200
                    }
                }
            ]
        }
    )


class ParticipanteResponse(ParticipanteBase):
    """
    Schema de respuesta para participante.
    """
    id: UUID = Field(..., description="UUID del participante")
    videollamada_id: UUID = Field(..., description="UUID de la videollamada")
    usuario_id: UUID = Field(..., description="UUID del usuario")
    fecha_union: datetime = Field(..., description="Momento en que se unió")
    fecha_salida: Optional[datetime] = Field(
        None,
        description="Momento en que salió"
    )
    duracion_segundos: Optional[int] = Field(
        None,
        ge=0,
        description="Duración de participación en segundos"
    )
    calidad_conexion: Optional[CalidadConexion] = Field(
        None,
        description="Calidad de conexión"
    )
    datos_conexion: Optional[Dict[str, Any]] = Field(
        None,
        description="Métricas detalladas de conexión"
    )
    created_at: datetime = Field(..., description="Timestamp de creación")
    
    # Datos del usuario (opcionales, llenados por join)
    usuario_nombre: Optional[str] = Field(None, description="Nombre del usuario")
    usuario_apellido: Optional[str] = Field(None, description="Apellido del usuario")
    usuario_email: Optional[str] = Field(None, description="Email del usuario")
    usuario_avatar: Optional[str] = Field(None, description="URL del avatar")

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "examples": [
                {
                    "id": "323e4567-e89b-12d3-a456-426614174000",
                    "videollamada_id": "123e4567-e89b-12d3-a456-426614174000",
                    "usuario_id": "423e4567-e89b-12d3-a456-426614174000",
                    "es_moderador": True,
                    "fecha_union": "2025-11-01T14:30:00Z",
                    "fecha_salida": None,
                    "duracion_segundos": None,
                    "calidad_conexion": "excelente",
                    "usuario_nombre": "Juan",
                    "usuario_apellido": "Pérez",
                    "created_at": "2025-11-01T14:30:00Z"
                }
            ]
        }
    )


# ==================== SCHEMAS DE GRABACIONES ====================

class GrabacionBase(BaseModel):
    """
    Schema base para grabación de videollamada.
    """
    archivo_url: str = Field(
        ...,
        min_length=1,
        max_length=500,
        description="URL del archivo de grabación"
    )
    formato: Optional[FormatoGrabacion] = Field(
        None,
        description="Formato del archivo"
    )
    calidad: Optional[CalidadGrabacion] = Field(
        None,
        description="Calidad de la grabación"
    )


class GrabacionCreate(GrabacionBase):
    """
    Schema para crear grabación.
    """
    videollamada_id: UUID = Field(..., description="UUID de la videollamada")
    duracion_segundos: Optional[int] = Field(
        None,
        ge=0,
        description="Duración en segundos"
    )
    tamano_bytes: Optional[int] = Field(
        None,
        ge=0,
        description="Tamaño del archivo en bytes"
    )
    thumbnail_url: Optional[str] = Field(
        None,
        max_length=500,
        description="URL de la miniatura"
    )
    metadatos: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Metadatos adicionales"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "videollamada_id": "123e4567-e89b-12d3-a456-426614174000",
                    "archivo_url": "https://storage.example.com/recordings/call-123.mp4",
                    "formato": "mp4",
                    "duracion_segundos": 1800,
                    "tamano_bytes": 524288000,
                    "calidad": "HD",
                    "thumbnail_url": "https://storage.example.com/thumbnails/call-123.jpg",
                    "metadatos": {
                        "codec": "h264",
                        "resolution": "1920x1080",
                        "fps": 30
                    }
                }
            ]
        }
    )


class GrabacionUpdate(BaseModel):
    """
    Schema para actualizar grabación.
    """
    estado_procesamiento: Optional[EstadoProcesamiento] = Field(
        None,
        description="Actualizar estado de procesamiento"
    )
    thumbnail_url: Optional[str] = Field(
        None,
        max_length=500,
        description="Actualizar URL de thumbnail"
    )
    metadatos: Optional[Dict[str, Any]] = Field(
        None,
        description="Actualizar metadatos"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "estado_procesamiento": "completado",
                    "thumbnail_url": "https://storage.example.com/thumbnails/call-123.jpg"
                }
            ]
        }
    )


class GrabacionResponse(GrabacionBase):
    """
    Schema de respuesta para grabación.
    """
    id: UUID = Field(..., description="UUID de la grabación")
    videollamada_id: UUID = Field(..., description="UUID de la videollamada")
    duracion_segundos: Optional[int] = Field(
        None,
        description="Duración en segundos"
    )
    tamano_bytes: Optional[int] = Field(
        None,
        description="Tamaño en bytes"
    )
    thumbnail_url: Optional[str] = Field(
        None,
        description="URL de miniatura"
    )
    estado_procesamiento: EstadoProcesamiento = Field(
        ...,
        description="Estado de procesamiento"
    )
    metadatos: Optional[Dict[str, Any]] = Field(
        None,
        description="Metadatos adicionales"
    )
    created_at: datetime = Field(..., description="Timestamp de creación")
    updated_at: datetime = Field(..., description="Timestamp de actualización")
    
    # Campos calculados opcionales
    tamano_mb: Optional[float] = Field(
        None,
        description="Tamaño en MB (calculado)"
    )
    duracion_formateada: Optional[str] = Field(
        None,
        description="Duración en formato HH:MM:SS (calculado)"
    )

    @model_validator(mode='after')
    def calculate_derived_fields(self) -> 'GrabacionResponse':
        """
        Calcula campos derivados como tamaño en MB y duración formateada.
        
        Returns:
            GrabacionResponse: Respuesta con campos calculados
        """
        # Calcular tamaño en MB
        if self.tamano_bytes is not None:
            self.tamano_mb = round(self.tamano_bytes / (1024 * 1024), 2)
        
        # Formatear duración
        if self.duracion_segundos is not None:
            hours = self.duracion_segundos // 3600
            minutes = (self.duracion_segundos % 3600) // 60
            seconds = self.duracion_segundos % 60
            self.duracion_formateada = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        
        return self

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "examples": [
                {
                    "id": "523e4567-e89b-12d3-a456-426614174000",
                    "videollamada_id": "123e4567-e89b-12d3-a456-426614174000",
                    "archivo_url": "https://storage.example.com/recordings/call-123.mp4",
                    "formato": "mp4",
                    "duracion_segundos": 1800,
                    "tamano_bytes": 524288000,
                    "tamano_mb": 500.0,
                    "calidad": "HD",
                    "thumbnail_url": "https://storage.example.com/thumbnails/call-123.jpg",
                    "estado_procesamiento": "completado",
                    "duracion_formateada": "00:30:00",
                    "metadatos": {"codec": "h264"},
                    "created_at": "2025-11-01T15:00:00Z",
                    "updated_at": "2025-11-01T15:05:00Z"
                }
            ]
        }
    )


# ==================== SCHEMAS DE ESTADÍSTICAS ====================

class EstadisticasVideollamada(BaseModel):
    """
    Schema para estadísticas de una videollamada.
    """
    total_participantes: int = Field(..., description="Total de participantes")
    duracion_promedio_participante: Optional[float] = Field(
        None,
        description="Duración promedio de participación en segundos"
    )
    calidad_conexion_promedio: Optional[str] = Field(
        None,
        description="Calidad de conexión promedio"
    )
    total_grabaciones: int = Field(..., description="Total de grabaciones")
    tiene_transcripcion: bool = Field(..., description="Si tiene transcripción")
    tiene_resumen: bool = Field(..., description="Si tiene resumen IA")

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "total_participantes": 8,
                    "duracion_promedio_participante": 1650.5,
                    "calidad_conexion_promedio": "buena",
                    "total_grabaciones": 1,
                    "tiene_transcripcion": True,
                    "tiene_resumen": True
                }
            ]
        }
    )


# ==================== SCHEMAS DE RESPUESTA GENÉRICOS ====================

class VideollamadaListResponse(BaseModel):
    """
    Schema para lista paginada de videollamadas.
    """
    items: List[VideollamadaResponse] = Field(
        ...,
        description="Lista de videollamadas"
    )
    total: int = Field(..., ge=0, description="Total de registros")
    skip: int = Field(..., ge=0, description="Registros saltados")
    limit: int = Field(..., ge=1, description="Límite de registros")
    has_more: bool = Field(..., description="Si hay más registros disponibles")

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "items": [],
                    "total": 42,
                    "skip": 0,
                    "limit": 20,
                    "has_more": True
                }
            ]
        }
    )


class UnirseVideollamadaResponse(ParticipanteResponse):
    """
    Schema específico para respuesta de unirse a videollamada.
    
    Extiende ParticipanteResponse con JWT token y room name.
    """
    jwt_token: str = Field(..., description="Token JWT para autenticación en Jitsi")
    jitsi_room_name: str = Field(..., description="Nombre de la sala de Jitsi")
    
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "examples": [
                {
                    "id": "323e4567-e89b-12d3-a456-426614174000",
                    "videollamada_id": "123e4567-e89b-12d3-a456-426614174000",
                    "usuario_id": "423e4567-e89b-12d3-a456-426614174000",
                    "es_moderador": False,
                    "fecha_union": "2025-11-01T14:30:00Z",
                    "calidad_conexion": "excelente",
                    "usuario_nombre": "Ana",
                    "usuario_apellido": "López",
                    "jwt_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                    "jitsi_room_name": "clase-matematicas-101",
                    "created_at": "2025-11-01T14:30:00Z"
                }
            ]
        }
    )


class MessageResponse(BaseModel):
    """
    Schema para respuestas simples con mensaje.
    """
    message: str = Field(..., description="Mensaje de respuesta")
    success: bool = Field(True, description="Si la operación fue exitosa")
    data: Optional[Dict[str, Any]] = Field(
        None,
        description="Datos adicionales opcionales"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "message": "Videollamada finalizada exitosamente",
                    "success": True,
                    "data": {"duracion_segundos": 1800}
                }
            ]
        }
    )


# ==================== ACTUALIZAR FORWARD REFS ====================

# Necesario para referencias circulares
VideollamadaDetallada.model_rebuild()
