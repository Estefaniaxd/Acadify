"""add_communication_system_basic

Revision ID: d886690834dd
Revises: cd29dc7eaca3
Create Date: 2025-09-26 17:53:06.592576

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
import uuid


# revision identifiers, used by Alembic.
revision: str = 'd886690834dd'
down_revision: Union[str, Sequence[str], None] = 'cd29dc7eaca3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Crear tablas básicas del sistema de comunicación"""
    
    # Crear ENUM types solo si no existen
    op.execute("""
        DO $$
        BEGIN
            IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'tiposala') THEN
                CREATE TYPE tiposala AS ENUM ('curso', 'grupo', 'tarea', 'privado', 'general');
            END IF;
        END$$;
    """)
    
    op.execute("""
        DO $$
        BEGIN
            IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'tipomensaje') THEN
                CREATE TYPE tipomensaje AS ENUM ('texto', 'imagen', 'archivo', 'audio', 'video', 'enlace', 'sistema', 'ia');
            END IF;
        END$$;
    """)
    
    op.execute("""
        DO $$
        BEGIN
            IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'estadomensaje') THEN
                CREATE TYPE estadomensaje AS ENUM ('enviado', 'entregado', 'leido', 'editado', 'eliminado');
            END IF;
        END$$;
    """)
    
    # Tabla salas_chat (sin foreign keys complejas por ahora)
    op.create_table(
        'salas_chat',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('nombre', sa.String(255), nullable=False),
        sa.Column('descripcion', sa.Text),
        sa.Column('tipo_sala', sa.String(50), nullable=False),  # Usando string en lugar de enum para evitar conflictos
        
        # Referencias contextuales (sin FK por ahora)
        sa.Column('curso_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('grupo_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('tarea_id', postgresql.UUID(as_uuid=True), nullable=True),
        
        # Configuración de la sala
        sa.Column('es_publica', sa.Boolean, default=True),
        sa.Column('permite_archivos', sa.Boolean, default=True),
        sa.Column('permite_menciones', sa.Boolean, default=True),
        sa.Column('permite_hilos', sa.Boolean, default=True),
        sa.Column('moderacion_activa', sa.Boolean, default=False),
        
        # Metadatos (sin FK por ahora)
        sa.Column('creador_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('fecha_creacion', sa.DateTime, server_default=sa.func.now()),
        sa.Column('fecha_actualizacion', sa.DateTime, onupdate=sa.func.now()),
        sa.Column('ultimo_mensaje_fecha', sa.DateTime),
        
        # Configuración avanzada
        sa.Column('configuracion_json', postgresql.JSON),
        sa.Column('tags', sa.String(500)),
    )
    
    # Tabla mensajes
    op.create_table(
        'mensajes',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('sala_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('usuario_id', postgresql.UUID(as_uuid=True), nullable=False),
        
        # Contenido del mensaje
        sa.Column('contenido', sa.Text),
        sa.Column('contenido_html', sa.Text),
        sa.Column('tipo_mensaje', sa.String(50), default='texto'),  # Usando string
        
        # Archivos adjuntos
        sa.Column('archivos_urls', postgresql.JSON),
        sa.Column('metadatos_archivos', postgresql.JSON),
        
        # Hilos de conversación
        sa.Column('mensaje_padre_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('tiene_respuestas', sa.Boolean, default=False),
        sa.Column('numero_respuestas', sa.Integer, default=0),
        
        # Menciones y referencias
        sa.Column('menciones_usuarios', postgresql.JSON),
        sa.Column('menciones_ia', sa.Boolean, default=False),
        sa.Column('menciones_todos', sa.Boolean, default=False),
        
        # Estado y metadatos
        sa.Column('estado', sa.String(50), default='enviado'),  # Usando string
        sa.Column('fecha_creacion', sa.DateTime, server_default=sa.func.now()),
        sa.Column('fecha_actualizacion', sa.DateTime, onupdate=sa.func.now()),
        sa.Column('fecha_eliminacion', sa.DateTime),
        
        # Reacciones y engagement
        sa.Column('reacciones', postgresql.JSON),
        sa.Column('es_importante', sa.Boolean, default=False),
        sa.Column('es_anuncio', sa.Boolean, default=False),
        
        # Foreign keys
        sa.ForeignKeyConstraint(['sala_id'], ['salas_chat.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['mensaje_padre_id'], ['mensajes.id'], ondelete='CASCADE'),
    )
    
    # Tabla notificaciones
    op.create_table(
        'notificaciones',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('usuario_id', postgresql.UUID(as_uuid=True), nullable=False),
        
        # Contenido de la notificación
        sa.Column('titulo', sa.String(255), nullable=False),
        sa.Column('mensaje', sa.Text),
        sa.Column('tipo_notificacion', sa.String(50)),
        
        # Referencias contextuales (sin FK complejas)
        sa.Column('sala_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('mensaje_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('tarea_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('curso_id', postgresql.UUID(as_uuid=True), nullable=True),
        
        # Estado de la notificación
        sa.Column('leida', sa.Boolean, default=False),
        sa.Column('enviada_email', sa.Boolean, default=False),
        sa.Column('enviada_push', sa.Boolean, default=False),
        
        # Metadatos
        sa.Column('fecha_creacion', sa.DateTime, server_default=sa.func.now()),
        sa.Column('fecha_lectura', sa.DateTime),
        sa.Column('fecha_envio_email', sa.DateTime),
        
        # Datos adicionales
        sa.Column('datos_adicionales', postgresql.JSON),
        sa.Column('url_accion', sa.String(500)),
        sa.Column('icono', sa.String(100)),
        sa.Column('color', sa.String(7)),
        
        # Foreign keys limitadas
        sa.ForeignKeyConstraint(['sala_id'], ['salas_chat.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['mensaje_id'], ['mensajes.id'], ondelete='CASCADE'),
    )
    
    print("✅ Sistema de comunicación básico creado exitosamente")


def downgrade() -> None:
    """Eliminar tablas del sistema de comunicación"""
    
    # Eliminar tablas en orden inverso
    op.drop_table('notificaciones')
    op.drop_table('mensajes')
    op.drop_table('salas_chat')
    
    # Eliminar ENUM types
    op.execute("DROP TYPE IF EXISTS estadomensaje")
    op.execute("DROP TYPE IF EXISTS tipomensaje")
    op.execute("DROP TYPE IF EXISTS tiposala")
    
    print("❌ Sistema de comunicación eliminado")
