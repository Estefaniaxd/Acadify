# 🚀 PLAN DE IMPLEMENTACIÓN - TAREAS DETALLADAS (Parte 2)

## 📋 FASE 1: BACKEND - FUNDAMENTOS

---

### **TAREA 1.1: Migración Base de Datos - Videollamadas**

**Archivo**: `backend/alembic/versions/[timestamp]_add_videollamadas_system.py`

**Duración**: 2 horas

**Descripción**: Crear tabla `videollamadas` con todas las columnas necesarias

**Implementación**:

```python
"""add videollamadas system

Revision ID: vl001_add_videollamadas
Revises: [previous_revision]
Create Date: 2025-11-01 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision = 'vl001_add_videollamadas'
down_revision = '[previous_revision]'  # Actualizar con última migración
branch_labels = None
depends_on = None


def upgrade() -> None:
    """
    Crea la tabla videollamadas y tablas relacionadas.
    
    Incluye:
    - Tabla videollamadas
    - Tabla grabaciones_videollamadas
    - Tabla transcripciones_videollamadas
    - Tabla interacciones_ia_videollamadas
    - Tabla notificaciones_videollamadas
    - Índices para performance
    - Constraints y checks
    """
    
    # ====================================
    # 1. Crear ENUMs
    # ====================================
    tipo_llamada_enum = postgresql.ENUM(
        'video', 'audio', 'screen',
        name='tipo_llamada_enum',
        create_type=True
    )
    
    estado_videollamada_enum = postgresql.ENUM(
        'pendiente', 'activa', 'finalizada', 'cancelada', 'error',
        name='estado_videollamada_enum',
        create_type=True
    )
    
    estado_procesamiento_enum = postgresql.ENUM(
        'procesando', 'completado', 'error',
        name='estado_procesamiento_enum',
        create_type=True
    )
    
    tipo_interaccion_ia_enum = postgresql.ENUM(
        'mencion', 'pregunta', 'comando', 'respuesta',
        name='tipo_interaccion_ia_enum',
        create_type=True
    )
    
    tipo_notificacion_vl_enum = postgresql.ENUM(
        'invitacion',
        'llamada_iniciada',
        'usuario_unido',
        'llamada_finalizada',
        'grabacion_disponible',
        'transcripcion_lista',
        'resumen_disponible',
        'llamada_perdida',
        name='tipo_notificacion_vl_enum',
        create_type=True
    )
    
    # ====================================
    # 2. Tabla: videollamadas
    # ====================================
    op.create_table(
        'videollamadas',
        
        # Identificación
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('jitsi_room_name', sa.String(255), unique=True, nullable=False, index=True),
        
        # Relaciones
        sa.Column('sala_chat_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('SalaChat.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('iniciada_por_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('Usuario.id'), nullable=False, index=True),
        
        # Configuración
        sa.Column('titulo', sa.String(255)),
        sa.Column('descripcion', sa.Text),
        sa.Column('tipo_llamada', tipo_llamada_enum, nullable=False),
        
        # Estado
        sa.Column('estado', estado_videollamada_enum, nullable=False, server_default='pendiente', index=True),
        sa.Column('esta_activa', sa.Boolean, nullable=False, server_default='true'),
        
        # Participantes
        sa.Column('participantes_ids', postgresql.ARRAY(sa.String), server_default='{}'),
        sa.Column('max_participantes', sa.Integer, server_default='50'),
        sa.Column('participantes_actuales', sa.Integer, server_default='0'),
        
        # Permisos y Moderación
        sa.Column('requiere_moderador', sa.Boolean, server_default='false'),
        sa.Column('moderadores_ids', postgresql.ARRAY(sa.String), server_default='{}'),
        sa.Column('todos_pueden_compartir_pantalla', sa.Boolean, server_default='true'),
        sa.Column('todos_pueden_grabar', sa.Boolean, server_default='false'),
        
        # Seguridad
        sa.Column('requiere_password', sa.Boolean, server_default='false'),
        sa.Column('password_encriptada', sa.String(255)),
        
        # Grabación
        sa.Column('permite_grabar', sa.Boolean, server_default='false'),
        sa.Column('esta_grabando', sa.Boolean, server_default='false'),
        sa.Column('grabacion_iniciada_por_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('Usuario.id')),
        sa.Column('url_grabacion', sa.Text),
        sa.Column('duracion_grabacion_segundos', sa.Integer),
        
        # Transcripción y IA
        sa.Column('transcripcion_habilitada', sa.Boolean, server_default='true'),
        sa.Column('rutilio_habilitado', sa.Boolean, server_default='true'),
        sa.Column('rutilio_unido', sa.Boolean, server_default='false'),
        
        # Métricas
        sa.Column('fecha_inicio', sa.DateTime(timezone=True)),
        sa.Column('fecha_fin', sa.DateTime(timezone=True)),
        sa.Column('duracion_segundos', sa.Integer),
        sa.Column('pico_participantes', sa.Integer, server_default='0'),
        sa.Column('total_mensajes_chat', sa.Integer, server_default='0'),
        sa.Column('total_interacciones_ia', sa.Integer, server_default='0'),
        
        # Calidad
        sa.Column('calidad_audio_promedio', sa.Numeric(precision=3, scale=2)),
        sa.Column('calidad_video_promedio', sa.Numeric(precision=3, scale=2)),
        sa.Column('latencia_promedio_ms', sa.Integer),
        
        # Metadatos
        sa.Column('configuracion', postgresql.JSONB, server_default='{}'),
        sa.Column('estadisticas', postgresql.JSONB, server_default='{}'),
        sa.Column('metadata', postgresql.JSONB, server_default='{}'),
        
        # Auditoría
        sa.Column('fecha_creacion', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('fecha_actualizacion', sa.DateTime(timezone=True), server_default=sa.text('NOW()')),
        sa.Column('fecha_eliminacion', sa.DateTime(timezone=True)),
        
        # Constraints
        sa.CheckConstraint('duracion_segundos >= 0', name='videollamadas_duracion_check')
    )
    
    # Índices adicionales para videollamadas
    op.create_index('idx_videollamadas_activas', 'videollamadas', ['esta_activa'], postgresql_where=sa.text('esta_activa = true'))
    op.create_index('idx_videollamadas_fecha_inicio', 'videollamadas', ['fecha_inicio'])
    
    # ====================================
    # 3. Tabla: grabaciones_videollamadas
    # ====================================
    op.create_table(
        'grabaciones_videollamadas',
        
        # Identificación
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('videollamada_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('videollamadas.id', ondelete='CASCADE'), nullable=False, index=True),
        
        # Archivo
        sa.Column('nombre_archivo', sa.String(500), nullable=False),
        sa.Column('url_archivo', sa.Text, nullable=False),
        sa.Column('url_thumbnail', sa.Text),
        
        # Metadatos
        sa.Column('duracion_segundos', sa.Integer, nullable=False),
        sa.Column('tamano_bytes', sa.BigInteger, nullable=False),
        sa.Column('formato', sa.String(10), server_default='mp4'),
        sa.Column('resolucion', sa.String(20)),
        sa.Column('fps', sa.Integer),
        sa.Column('codec_video', sa.String(50)),
        sa.Column('codec_audio', sa.String(50)),
        
        # Procesamiento
        sa.Column('estado_procesamiento', estado_procesamiento_enum, server_default='procesando', index=True),
        sa.Column('progreso_procesamiento', sa.Integer, server_default='0'),
        
        # Acceso
        sa.Column('es_publica', sa.Boolean, server_default='false'),
        sa.Column('requiere_autenticacion', sa.Boolean, server_default='true'),
        sa.Column('usuarios_con_acceso', postgresql.ARRAY(sa.String), server_default='{}'),
        
        # Transcripción
        sa.Column('transcripcion_id', postgresql.UUID(as_uuid=True)),
        sa.Column('tiene_transcripcion', sa.Boolean, server_default='false'),
        
        # Analytics
        sa.Column('total_reproducciones', sa.Integer, server_default='0'),
        sa.Column('total_descargas', sa.Integer, server_default='0'),
        
        # Metadatos
        sa.Column('metadata', postgresql.JSONB, server_default='{}'),
        
        # Auditoría
        sa.Column('fecha_creacion', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('fecha_eliminacion', sa.DateTime(timezone=True)),
        sa.Column('fecha_expiracion', sa.DateTime(timezone=True)),
        
        # Constraints
        sa.CheckConstraint('duracion_segundos > 0', name='grabaciones_duracion_check'),
        sa.CheckConstraint('tamano_bytes > 0', name='grabaciones_tamano_check')
    )
    
    # ====================================
    # 4. Tabla: transcripciones_videollamadas
    # ====================================
    op.create_table(
        'transcripciones_videollamadas',
        
        # Identificación
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('videollamada_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('videollamadas.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('grabacion_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('grabaciones_videollamadas.id'), index=True),
        
        # Contenido
        sa.Column('transcripcion_completa', sa.Text, nullable=False),
        sa.Column('transcripcion_vtt', sa.Text),
        sa.Column('transcripcion_srt', sa.Text),
        sa.Column('idioma_detectado', sa.String(10), server_default='es'),
        
        # Segmentos timestamped
        sa.Column('segmentos', postgresql.JSONB, nullable=False, server_default='[]'),
        
        # Análisis IA
        sa.Column('resumen_ia', sa.Text),
        sa.Column('temas_principales', postgresql.ARRAY(sa.String)),
        sa.Column('palabras_clave', postgresql.ARRAY(sa.String)),
        sa.Column('action_items', postgresql.JSONB, server_default='[]'),
        sa.Column('decisiones_tomadas', postgresql.JSONB, server_default='[]'),
        sa.Column('participantes_mas_activos', postgresql.JSONB, server_default='[]'),
        
        # Metadatos
        sa.Column('confianza_promedio', sa.Numeric(precision=3, scale=2)),
        sa.Column('total_palabras', sa.Integer),
        sa.Column('duracion_hablada_segundos', sa.Integer),
        
        # Estado
        sa.Column('estado_procesamiento', estado_procesamiento_enum, server_default='procesando'),
        
        # Full-text search
        sa.Column('search_vector', postgresql.TSVECTOR),
        
        # Auditoría
        sa.Column('fecha_creacion', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('fecha_actualizacion', sa.DateTime(timezone=True), server_default=sa.text('NOW()')),
        
        # Constraints
        sa.CheckConstraint('confianza_promedio >= 0 AND confianza_promedio <= 1', name='transcripciones_confianza_check')
    )
    
    # Índice GIN para búsqueda full-text
    op.create_index('idx_transcripciones_search', 'transcripciones_videollamadas', ['search_vector'], postgresql_using='gin')
    
    # ====================================
    # 5. Tabla: interacciones_ia_videollamadas
    # ====================================
    op.create_table(
        'interacciones_ia_videollamadas',
        
        # Identificación
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('videollamada_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('videollamadas.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('usuario_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('Usuario.id'), nullable=False, index=True),
        
        # Interacción
        sa.Column('tipo_interaccion', tipo_interaccion_ia_enum, nullable=False),
        
        # Contenido
        sa.Column('texto_usuario', sa.Text, nullable=False),
        sa.Column('texto_ia', sa.Text, nullable=False),
        sa.Column('audio_usuario_url', sa.Text),
        sa.Column('audio_ia_url', sa.Text),
        
        # Context
        sa.Column('timestamp_llamada', sa.Interval),
        sa.Column('contexto_previo', postgresql.JSONB),
        
        # Métricas
        sa.Column('tiempo_respuesta_ms', sa.Integer),
        sa.Column('confianza_transcripcion', sa.Numeric(precision=3, scale=2)),
        sa.Column('utilidad_respuesta', sa.Integer),  # 1-5 rating
        
        # Auditoría
        sa.Column('fecha_creacion', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('NOW()'))
    )
    
    # ====================================
    # 6. Tabla: notificaciones_videollamadas
    # ====================================
    op.create_table(
        'notificaciones_videollamadas',
        
        # Identificación
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('videollamada_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('videollamadas.id', ondelete='CASCADE'), nullable=False),
        sa.Column('usuario_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('Usuario.id', ondelete='CASCADE'), nullable=False, index=True),
        
        # Contenido
        sa.Column('tipo_notificacion', tipo_notificacion_vl_enum, nullable=False),
        sa.Column('titulo', sa.String(255), nullable=False),
        sa.Column('mensaje', sa.Text, nullable=False),
        
        # Acción
        sa.Column('url_accion', sa.Text),
        sa.Column('accion_realizada', sa.Boolean, server_default='false'),
        
        # Estado
        sa.Column('es_leida', sa.Boolean, server_default='false', index=True),
        sa.Column('fecha_lectura', sa.DateTime(timezone=True)),
        
        # Auditoría
        sa.Column('fecha_creacion', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('fecha_expiracion', sa.DateTime(timezone=True))
    )


def downgrade() -> None:
    """Elimina todas las tablas creadas."""
    
    # Eliminar tablas en orden inverso (por las foreign keys)
    op.drop_table('notificaciones_videollamadas')
    op.drop_table('interacciones_ia_videollamadas')
    op.drop_table('transcripciones_videollamadas')
    op.drop_table('grabaciones_videollamadas')
    op.drop_table('videollamadas')
    
    # Eliminar ENUMs
    op.execute('DROP TYPE IF EXISTS tipo_notificacion_vl_enum')
    op.execute('DROP TYPE IF EXISTS tipo_interaccion_ia_enum')
    op.execute('DROP TYPE IF EXISTS estado_procesamiento_enum')
    op.execute('DROP TYPE IF EXISTS estado_videollamada_enum')
    op.execute('DROP TYPE IF EXISTS tipo_llamada_enum')
```

**Testing**:
```bash
# Aplicar migración
alembic upgrade head

# Verificar que las tablas se crearon correctamente
psql -U postgres -d acadify_db -c "\dt *videollamadas*"

# Rollback para testing
alembic downgrade -1
```

**Acceptance Criteria**:
- ✅ Todas las tablas creadas sin errores
- ✅ Índices creados correctamente
- ✅ Foreign keys funcionando
- ✅ ENUMs creados
- ✅ Constraints aplicados
- ✅ Downgrade funciona correctamente

---

### **TAREA 1.2: Modelos SQLAlchemy**

**Archivo**: `backend/src/models/communication/videollamada.py`

**Duración**: 3 horas

**Descripción**: Crear modelos SQLAlchemy para todas las tablas relacionadas con videollamadas

**Implementación**:

```python
"""
Modelos de Base de Datos para Sistema de Videollamadas.

Este módulo contiene los modelos SQLAlchemy para:
- Videollamadas
- Grabaciones
- Transcripciones
- Interacciones con IA
- Notificaciones

Sigue principios SOLID y Clean Code.
"""

from sqlalchemy import (
    Column, String, Integer, Boolean, Text, DateTime,
    ForeignKey, CheckConstraint, Index, Numeric, BigInteger, Interval
)
from sqlalchemy.dialects.postgresql import UUID, ARRAY, JSONB, ENUM
from sqlalchemy.orm import relationship, validates
from sqlalchemy.sql import func
from datetime import datetime
from typing import Optional, List, Dict, Any
import uuid

from src.db.base_class import Base


# ====================================
# ENUMs
# ====================================

class TipoLlamada(str):
    """Enum para tipos de llamada."""
    VIDEO = "video"
    AUDIO = "audio"
    SCREEN = "screen"


class EstadoVideollamada(str):
    """Enum para estados de videollamada."""
    PENDIENTE = "pendiente"
    ACTIVA = "activa"
    FINALIZADA = "finalizada"
    CANCELADA = "cancelada"
    ERROR = "error"


class EstadoProcesamiento(str):
    """Enum para estados de procesamiento."""
    PROCESANDO = "procesando"
    COMPLETADO = "completado"
    ERROR = "error"


class TipoInteraccionIA(str):
    """Enum para tipos de interacción con IA."""
    MENCION = "mencion"
    PREGUNTA = "pregunta"
    COMANDO = "comando"
    RESPUESTA = "respuesta"


class TipoNotificacionVideollamada(str):
    """Enum para tipos de notificación de videollamadas."""
    INVITACION = "invitacion"
    LLAMADA_INICIADA = "llamada_iniciada"
    USUARIO_UNIDO = "usuario_unido"
    LLAMADA_FINALIZADA = "llamada_finalizada"
    GRABACION_DISPONIBLE = "grabacion_disponible"
    TRANSCRIPCION_LISTA = "transcripcion_lista"
    RESUMEN_DISPONIBLE = "resumen_disponible"
    LLAMADA_PERDIDA = "llamada_perdida"


# ====================================
# MODELO PRINCIPAL: Videollamada
# ====================================

class Videollamada(Base):
    """
    Modelo para videollamadas en el sistema.
    
    Una videollamada representa una sesión de comunicación en tiempo real
    que puede ser de video, solo audio, o compartición de pantalla.
    
    Attributes:
        id: Identificador único de la videollamada
        jitsi_room_name: Nombre único de la sala en Jitsi
        sala_chat_id: ID de la sala de chat asociada
        iniciada_por_id: ID del usuario que inició la llamada
        tipo_llamada: Tipo de llamada (video/audio/screen)
        estado: Estado actual de la llamada
        participantes_ids: Lista de IDs de participantes
        permite_grabar: Si se permite grabar la llamada
        transcripcion_habilitada: Si se transcribe en tiempo real
        rutilio_habilitado: Si Rutilio puede unirse cuando se menciona
        
    Relationships:
        sala_chat: Sala de chat donde se realiza la llamada
        iniciada_por: Usuario que inició la llamada
        grabaciones: Lista de grabaciones de esta llamada
        transcripciones: Lista de transcripciones
        interacciones_ia: Lista de interacciones con IA
        notificaciones: Lista de notificaciones generadas
        
    Business Rules:
        - Solo usuarios con permisos pueden iniciar llamadas
        - Una sala puede tener solo una llamada activa a la vez
        - Las grabaciones requieren permiso explícito
        - La duración debe ser >= 0
    """
    
    __tablename__ = "videollamadas"
    
    # ================================
    # IDENTIFICACIÓN
    # ================================
    
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        comment="Identificador único de la videollamada"
    )
    
    jitsi_room_name = Column(
        String(255),
        unique=True,
        nullable=False,
        index=True,
        comment="Nombre único de la sala en Jitsi Meet"
    )
    
    # ================================
    # RELACIONES
    # ================================
    
    sala_chat_id = Column(
        UUID(as_uuid=True),
        ForeignKey("SalaChat.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="ID de la sala de chat asociada"
    )
    
    iniciada_por_id = Column(
        UUID(as_uuid=True),
        ForeignKey("Usuario.id"),
        nullable=False,
        index=True,
        comment="ID del usuario que inició la llamada"
    )
    
    # ================================
    # CONFIGURACIÓN
    # ================================
    
    titulo = Column(
        String(255),
        comment="Título descriptivo de la llamada"
    )
    
    descripcion = Column(
        Text,
        comment="Descripción detallada"
    )
    
    tipo_llamada = Column(
        ENUM(
            TipoLlamada.VIDEO,
            TipoLlamada.AUDIO,
            TipoLlamada.SCREEN,
            name="tipo_llamada_enum",
            create_type=False
        ),
        nullable=False,
        comment="Tipo de llamada: video, audio o screen"
    )
    
    # ================================
    # ESTADO
    # ================================
    
    estado = Column(
        ENUM(
            EstadoVideollamada.PENDIENTE,
            EstadoVideollamada.ACTIVA,
            EstadoVideollamada.FINALIZADA,
            EstadoVideollamada.CANCELADA,
            EstadoVideollamada.ERROR,
            name="estado_videollamada_enum",
            create_type=False
        ),
        nullable=False,
        default=EstadoVideollamada.PENDIENTE,
        index=True,
        comment="Estado actual de la videollamada"
    )
    
    esta_activa = Column(
        Boolean,
        nullable=False,
        default=True,
        comment="Indica si la llamada está actualmente activa"
    )
    
    # ================================
    # PARTICIPANTES
    # ================================
    
    participantes_ids = Column(
        ARRAY(String),
        default=[],
        comment="Lista de IDs de usuarios participantes"
    )
    
    max_participantes = Column(
        Integer,
        default=50,
        comment="Máximo número de participantes permitidos"
    )
    
    participantes_actuales = Column(
        Integer,
        default=0,
        comment="Número actual de participantes conectados"
    )
    
    # ================================
    # PERMISOS Y MODERACIÓN
    # ================================
    
    requiere_moderador = Column(
        Boolean,
        default=False,
        comment="Si la llamada requiere un moderador presente"
    )
    
    moderadores_ids = Column(
        ARRAY(String),
        default=[],
        comment="Lista de IDs de usuarios moderadores"
    )
    
    todos_pueden_compartir_pantalla = Column(
        Boolean,
        default=True,
        comment="Si todos los participantes pueden compartir pantalla"
    )
    
    todos_pueden_grabar = Column(
        Boolean,
        default=False,
        comment="Si todos pueden grabar (solo moderadores si False)"
    )
    
    # ================================
    # SEGURIDAD
    # ================================
    
    requiere_password = Column(
        Boolean,
        default=False,
        comment="Si la llamada requiere contraseña para unirse"
    )
    
    password_encriptada = Column(
        String(255),
        comment="Contraseña encriptada con bcrypt"
    )
    
    # ================================
    # GRABACIÓN
    # ================================
    
    permite_grabar = Column(
        Boolean,
        default=False,
        comment="Si se permite grabar esta llamada"
    )
    
    esta_grabando = Column(
        Boolean,
        default=False,
        comment="Si actualmente se está grabando"
    )
    
    grabacion_iniciada_por_id = Column(
        UUID(as_uuid=True),
        ForeignKey("Usuario.id"),
        comment="Usuario que inició la grabación"
    )
    
    url_grabacion = Column(
        Text,
        comment="URL de la grabación (si existe)"
    )
    
    duracion_grabacion_segundos = Column(
        Integer,
        comment="Duración de la grabación en segundos"
    )
    
    # ================================
    # TRANSCRIPCIÓN Y IA
    # ================================
    
    transcripcion_habilitada = Column(
        Boolean,
        default=True,
        comment="Si la transcripción en tiempo real está habilitada"
    )
    
    rutilio_habilitado = Column(
        Boolean,
        default=True,
        comment="Si Rutilio (IA) puede unirse cuando se menciona"
    )
    
    rutilio_unido = Column(
        Boolean,
        default=False,
        comment="Si Rutilio está actualmente en la llamada"
    )
    
    # ================================
    # MÉTRICAS Y ANALYTICS
    # ================================
    
    fecha_inicio = Column(
        DateTime(timezone=True),
        comment="Fecha y hora de inicio de la llamada"
    )
    
    fecha_fin = Column(
        DateTime(timezone=True),
        comment="Fecha y hora de finalización"
    )
    
    duracion_segundos = Column(
        Integer,
        comment="Duración total en segundos"
    )
    
    pico_participantes = Column(
        Integer,
        default=0,
        comment="Número máximo de participantes simultáneos"
    )
    
    total_mensajes_chat = Column(
        Integer,
        default=0,
        comment="Total de mensajes en el chat durante la llamada"
    )
    
    total_interacciones_ia = Column(
        Integer,
        default=0,
        comment="Total de interacciones con Rutilio"
    )
    
    # ================================
    # CALIDAD DE CONEXIÓN
    # ================================
    
    calidad_audio_promedio = Column(
        Numeric(precision=3, scale=2),
        comment="Calidad promedio de audio (0.00 a 5.00)"
    )
    
    calidad_video_promedio = Column(
        Numeric(precision=3, scale=2),
        comment="Calidad promedio de video (0.00 a 5.00)"
    )
    
    latencia_promedio_ms = Column(
        Integer,
        comment="Latencia promedio en milisegundos"
    )
    
    # ================================
    # METADATOS (JSONB para flexibilidad)
    # ================================
    
    configuracion = Column(
        JSONB,
        default={},
        comment="Configuración adicional en formato JSON"
    )
    
    estadisticas = Column(
        JSONB,
        default={},
        comment="Estadísticas detalladas en formato JSON"
    )
    
    metadata = Column(
        JSONB,
        default={},
        comment="Metadatos adicionales"
    )
    
    # ================================
    # AUDITORÍA
    # ================================
    
    fecha_creacion = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        comment="Fecha de creación del registro"
    )
    
    fecha_actualizacion = Column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        comment="Fecha de última actualización"
    )
    
    fecha_eliminacion = Column(
        DateTime(timezone=True),
        comment="Fecha de eliminación lógica (soft delete)"
    )
    
    # ================================
    # RELATIONSHIPS
    # ================================
    
    sala_chat = relationship(
        "SalaChat",
        back_populates="videollamadas",
        lazy="joined"
    )
    
    iniciada_por = relationship(
        "Usuario",
        foreign_keys=[iniciada_por_id],
        lazy="joined"
    )
    
    grabacion_iniciada_por = relationship(
        "Usuario",
        foreign_keys=[grabacion_iniciada_por_id],
        lazy="joined"
    )
    
    grabaciones = relationship(
        "GrabacionVideollamada",
        back_populates="videollamada",
        cascade="all, delete-orphan",
        lazy="dynamic"
    )
    
    transcripciones = relationship(
        "TranscripcionVideollamada",
        back_populates="videollamada",
        cascade="all, delete-orphan",
        lazy="dynamic"
    )
    
    interacciones_ia = relationship(
        "InteraccionIAVideollamada",
        back_populates="videollamada",
        cascade="all, delete-orphan",
        lazy="dynamic"
    )
    
    notificaciones = relationship(
        "NotificacionVideollamada",
        back_populates="videollamada",
        cascade="all, delete-orphan",
        lazy="dynamic"
    )
    
    # ================================
    # CONSTRAINTS
    # ================================
    
    __table_args__ = (
        CheckConstraint(
            'duracion_segundos >= 0',
            name='videollamadas_duracion_check'
        ),
        Index(
            'idx_videollamadas_activas',
            'esta_activa',
            postgresql_where=(esta_activa == True)
        ),
    )
    
    # ================================
    # VALIDATIONS
    # ================================
    
    @validates('tipo_llamada')
    def validate_tipo_llamada(self, key, value):
        """Valida que el tipo de llamada sea válido."""
        valid_types = [TipoLlamada.VIDEO, TipoLlamada.AUDIO, TipoLlamada.SCREEN]
        if value not in valid_types:
            raise ValueError(f"Tipo de llamada inválido. Debe ser uno de: {valid_types}")
        return value
    
    @validates('max_participantes')
    def validate_max_participantes(self, key, value):
        """Valida que el máximo de participantes sea razonable."""
        if value < 2:
            raise ValueError("El máximo de participantes debe ser al menos 2")
        if value > 500:
            raise ValueError("El máximo de participantes no puede exceder 500")
        return value
    
    @validates('duracion_segundos')
    def validate_duracion(self, key, value):
        """Valida que la duración sea positiva."""
        if value is not None and value < 0:
            raise ValueError("La duración no puede ser negativa")
        return value
    
    # ================================
    # MÉTODOS DE INSTANCIA
    # ================================
    
    def esta_finalizada(self) -> bool:
        """
        Verifica si la videollamada ha finalizado.
        
        Returns:
            bool: True si está finalizada, False en caso contrario
        """
        return self.estado == EstadoVideollamada.FINALIZADA
    
    def puede_unirse(self, usuario_id: uuid.UUID) -> bool:
        """
        Verifica si un usuario puede unirse a la llamada.
        
        Args:
            usuario_id: ID del usuario
            
        Returns:
            bool: True si puede unirse, False en caso contrario
        """
        # No puede unirse si está finalizada o cancelada
        if self.estado in [EstadoVideollamada.FINALIZADA, EstadoVideollamada.CANCELADA]:
            return False
        
        # No puede unirse si está llena
        if self.participantes_actuales >= self.max_participantes:
            return False
        
        return True
    
    def agregar_participante(self, usuario_id: str) -> None:
        """
        Agrega un participante a la llamada.
        
        Args:
            usuario_id: ID del usuario a agregar
            
        Raises:
            ValueError: Si la llamada está llena o finalizada
        """
        if not self.puede_unirse(uuid.UUID(usuario_id)):
            raise ValueError("No se puede unir a esta llamada")
        
        if usuario_id not in self.participantes_ids:
            self.participantes_ids.append(usuario_id)
            self.participantes_actuales += 1
            
            # Actualizar pico de participantes
            if self.participantes_actuales > self.pico_participantes:
                self.pico_participantes = self.participantes_actuales
    
    def remover_participante(self, usuario_id: str) -> None:
        """
        Remueve un participante de la llamada.
        
        Args:
            usuario_id: ID del usuario a remover
        """
        if usuario_id in self.participantes_ids:
            self.participantes_ids.remove(usuario_id)
            self.participantes_actuales = max(0, self.participantes_actuales - 1)
    
    def es_moderador(self, usuario_id: str) -> bool:
        """
        Verifica si un usuario es moderador de la llamada.
        
        Args:
            usuario_id: ID del usuario
            
        Returns:
            bool: True si es moderador, False en caso contrario
        """
        return usuario_id in self.moderadores_ids or usuario_id == str(self.iniciada_por_id)
    
    def calcular_duracion_actual(self) -> Optional[int]:
        """
        Calcula la duración actual de la llamada.
        
        Si la llamada está activa, calcula desde el inicio hasta ahora.
        Si está finalizada, retorna la duración guardada.
        
        Returns:
            Optional[int]: Duración en segundos, o None si no ha iniciado
        """
        if not self.fecha_inicio:
            return None
        
        if self.fecha_fin:
            return self.duracion_segundos
        
        # Llamada activa - calcular duración actual
        delta = datetime.utcnow() - self.fecha_inicio
        return int(delta.total_seconds())
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convierte la videollamada a diccionario.
        
        Returns:
            Dict con los datos de la videollamada
        """
        return {
            "id": str(self.id),
            "jitsi_room_name": self.jitsi_room_name,
            "sala_chat_id": str(self.sala_chat_id),
            "iniciada_por_id": str(self.iniciada_por_id),
            "titulo": self.titulo,
            "tipo_llamada": self.tipo_llamada,
            "estado": self.estado,
            "esta_activa": self.esta_activa,
            "participantes_actuales": self.participantes_actuales,
            "max_participantes": self.max_participantes,
            "permite_grabar": self.permite_grabar,
            "esta_grabando": self.esta_grabando,
            "transcripcion_habilitada": self.transcripcion_habilitada,
            "rutilio_habilitado": self.rutilio_habilitado,
            "rutilio_unido": self.rutilio_unido,
            "fecha_inicio": self.fecha_inicio.isoformat() if self.fecha_inicio else None,
            "fecha_fin": self.fecha_fin.isoformat() if self.fecha_fin else None,
            "duracion_segundos": self.duracion_segundos,
            "fecha_creacion": self.fecha_creacion.isoformat()
        }
    
    def __repr__(self) -> str:
        """Representación string de la videollamada."""
        return f"<Videollamada(id={self.id}, jitsi_room={self.jitsi_room_name}, estado={self.estado})>"


# Continúa en la siguiente parte con los modelos restantes...
# GrabacionVideollamada, TranscripcionVideollamada, etc.
```

**Nota**: El archivo es extenso. Los modelos restantes seguirían el mismo patrón.

**Acceptance Criteria**:
- ✅ Modelo sigue convenciones SQLAlchemy
- ✅ Validaciones en campos críticos
- ✅ Relationships bien definidas
- ✅ Métodos de utilidad implementados
- ✅ Docstrings completos
- ✅ Type hints en todo el código
- ✅ Cumple principios SOLID

---

### **TAREA 1.3: Schemas Pydantic**

**Archivo**: `backend/src/schemas/communication/videollamada_schemas.py`

**Duración**: 2 horas

**Continúa con schemas completos...**

---

[El documento continúa con todas las 36 tareas detalladas siguiendo el mismo nivel de detalle]

