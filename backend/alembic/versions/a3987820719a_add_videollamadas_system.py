"""add_videollamadas_system

Revision ID: a3987820719a
Revises: 0ed8379d6bb9
Create Date: 2025-11-01 17:32:57.245420

Agrega las tablas necesarias para el sistema de videollamadas:
- videollamadas: Tabla principal para gestionar llamadas de video y voz
- videollamada_participantes: Participantes en cada llamada
- videollamada_grabaciones: Grabaciones de las llamadas
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from sqlalchemy.dialects.postgresql import UUID


# revision identifiers, used by Alembic.
revision: str = 'a3987820719a'
down_revision: Union[str, Sequence[str], None] = '0ed8379d6bb9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Upgrade schema.
    
    Crea las tablas para el sistema de videollamadas con integración Jitsi:
    1. videollamadas: Gestión de llamadas (video/voz)
    2. videollamada_participantes: Seguimiento de participantes
    3. videollamada_grabaciones: Almacenamiento de grabaciones
    """
    # Tabla principal de videollamadas
    op.create_table(
        'videollamadas',
        sa.Column('id', UUID(as_uuid=True), nullable=False, 
                  server_default=sa.text('gen_random_uuid()')),
        sa.Column('jitsi_room_name', sa.String(length=255), nullable=False, 
                  comment='Nombre único de la sala Jitsi'),
        sa.Column('tipo_llamada', sa.String(length=20), nullable=False,
                  comment='Tipo de llamada: video o voz'),
        sa.Column('sala_chat_id', UUID(as_uuid=True), nullable=True,
                  comment='Sala de chat asociada (si existe)'),
        sa.Column('iniciador_id', UUID(as_uuid=True), nullable=False,
                  comment='Usuario que inició la llamada'),
        sa.Column('estado', sa.String(length=20), nullable=False,
                  comment='Estado: activa, finalizada, cancelada'),
        sa.Column('fecha_inicio', sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.text('NOW()'),
                  comment='Fecha y hora de inicio'),
        sa.Column('fecha_fin', sa.DateTime(timezone=True), nullable=True,
                  comment='Fecha y hora de finalización'),
        sa.Column('duracion_segundos', sa.Integer(), nullable=True,
                  comment='Duración total en segundos'),
        sa.Column('grabacion_url', sa.String(length=500), nullable=True,
                  comment='URL de la grabación (si existe)'),
        sa.Column('transcripcion', sa.Text(), nullable=True,
                  comment='Transcripción completa de la llamada'),
        sa.Column('resumen_ia', sa.Text(), nullable=True,
                  comment='Resumen generado por IA'),
        sa.Column('configuracion', postgresql.JSONB(astext_type=sa.Text()), nullable=True,
                  server_default='{}',
                  comment='Configuración adicional de la llamada'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.text('NOW()')),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True,
                  comment='Soft delete timestamp'),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['sala_chat_id'], ['salas_chat.id'], 
                                ondelete='CASCADE', name='fk_videollamada_sala_chat'),
        sa.ForeignKeyConstraint(['iniciador_id'], ['Usuario.usuario_id'], 
                                ondelete='CASCADE', name='fk_videollamada_iniciador'),
        sa.CheckConstraint("tipo_llamada IN ('video', 'voz')", 
                          name='ck_videollamada_tipo'),
        sa.CheckConstraint("estado IN ('activa', 'finalizada', 'cancelada')", 
                          name='ck_videollamada_estado'),
        sa.UniqueConstraint('jitsi_room_name', name='uq_videollamada_jitsi_room')
    )
    
    # Índices para optimizar consultas
    op.create_index('idx_videollamadas_sala_chat', 'videollamadas', ['sala_chat_id'])
    op.create_index('idx_videollamadas_iniciador', 'videollamadas', ['iniciador_id'])
    op.create_index('idx_videollamadas_estado', 'videollamadas', ['estado'])
    op.create_index('idx_videollamadas_fecha_inicio', 'videollamadas', ['fecha_inicio'])
    op.create_index('idx_videollamadas_deleted_at', 'videollamadas', ['deleted_at'])
    
    # Tabla de participantes
    op.create_table(
        'videollamada_participantes',
        sa.Column('id', UUID(as_uuid=True), nullable=False, 
                  server_default=sa.text('gen_random_uuid()')),
        sa.Column('videollamada_id', UUID(as_uuid=True), nullable=False,
                  comment='ID de la videollamada'),
        sa.Column('usuario_id', UUID(as_uuid=True), nullable=False,
                  comment='Usuario participante'),
        sa.Column('es_moderador', sa.Boolean(), nullable=False,
                  server_default='false',
                  comment='Indica si tiene privilegios de moderador'),
        sa.Column('fecha_union', sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.text('NOW()'),
                  comment='Momento en que se unió'),
        sa.Column('fecha_salida', sa.DateTime(timezone=True), nullable=True,
                  comment='Momento en que salió'),
        sa.Column('duracion_segundos', sa.Integer(), nullable=True,
                  comment='Duración de participación en segundos'),
        sa.Column('calidad_conexion', sa.String(length=20), nullable=True,
                  comment='Calidad de conexión: excelente, buena, regular, mala'),
        sa.Column('datos_conexion', postgresql.JSONB(astext_type=sa.Text()), nullable=True,
                  server_default='{}',
                  comment='Métricas de conexión (latencia, pérdida paquetes, etc.)'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.text('NOW()')),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['videollamada_id'], ['videollamadas.id'], 
                                ondelete='CASCADE', name='fk_participante_videollamada'),
        sa.ForeignKeyConstraint(['usuario_id'], ['Usuario.usuario_id'], 
                                ondelete='CASCADE', name='fk_participante_usuario'),
        sa.CheckConstraint("calidad_conexion IS NULL OR calidad_conexion IN ('excelente', 'buena', 'regular', 'mala')", 
                          name='ck_participante_calidad'),
        sa.UniqueConstraint('videollamada_id', 'usuario_id', 
                           name='uq_participante_videollamada_usuario')
    )
    
    # Índices para participantes
    op.create_index('idx_participantes_videollamada', 'videollamada_participantes', 
                    ['videollamada_id'])
    op.create_index('idx_participantes_usuario', 'videollamada_participantes', 
                    ['usuario_id'])
    op.create_index('idx_participantes_fecha_union', 'videollamada_participantes', 
                    ['fecha_union'])
    
    # Tabla de grabaciones
    op.create_table(
        'videollamada_grabaciones',
        sa.Column('id', UUID(as_uuid=True), nullable=False, 
                  server_default=sa.text('gen_random_uuid()')),
        sa.Column('videollamada_id', UUID(as_uuid=True), nullable=False,
                  comment='ID de la videollamada grabada'),
        sa.Column('archivo_url', sa.String(length=500), nullable=False,
                  comment='URL del archivo de grabación'),
        sa.Column('duracion_segundos', sa.Integer(), nullable=True,
                  comment='Duración de la grabación'),
        sa.Column('tamano_bytes', sa.BigInteger(), nullable=True,
                  comment='Tamaño del archivo en bytes'),
        sa.Column('formato', sa.String(length=20), nullable=True,
                  comment='Formato del archivo: mp4, webm, etc.'),
        sa.Column('thumbnail_url', sa.String(length=500), nullable=True,
                  comment='URL de la miniatura'),
        sa.Column('calidad', sa.String(length=20), nullable=True,
                  comment='Calidad de grabación: HD, FHD, 4K'),
        sa.Column('estado_procesamiento', sa.String(length=20), nullable=False,
                  server_default='pendiente',
                  comment='Estado: pendiente, procesando, completado, error'),
        sa.Column('metadatos', postgresql.JSONB(astext_type=sa.Text()), nullable=True,
                  server_default='{}',
                  comment='Metadatos adicionales de la grabación'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.text('NOW()')),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True,
                  comment='Soft delete timestamp'),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['videollamada_id'], ['videollamadas.id'], 
                                ondelete='CASCADE', name='fk_grabacion_videollamada'),
        sa.CheckConstraint("formato IS NULL OR formato IN ('mp4', 'webm', 'mkv', 'avi')", 
                          name='ck_grabacion_formato'),
        sa.CheckConstraint("calidad IS NULL OR calidad IN ('SD', 'HD', 'FHD', '4K')", 
                          name='ck_grabacion_calidad'),
        sa.CheckConstraint("estado_procesamiento IN ('pendiente', 'procesando', 'completado', 'error')", 
                          name='ck_grabacion_estado')
    )
    
    # Índices para grabaciones
    op.create_index('idx_grabaciones_videollamada', 'videollamada_grabaciones', 
                    ['videollamada_id'])
    op.create_index('idx_grabaciones_estado', 'videollamada_grabaciones', 
                    ['estado_procesamiento'])
    op.create_index('idx_grabaciones_deleted_at', 'videollamada_grabaciones', 
                    ['deleted_at'])


def downgrade() -> None:
    """
    Downgrade schema.
    
    Elimina las tablas del sistema de videollamadas en orden inverso
    para respetar las foreign keys.
    """
    # Eliminar tablas en orden inverso
    op.drop_index('idx_grabaciones_deleted_at', table_name='videollamada_grabaciones')
    op.drop_index('idx_grabaciones_estado', table_name='videollamada_grabaciones')
    op.drop_index('idx_grabaciones_videollamada', table_name='videollamada_grabaciones')
    op.drop_table('videollamada_grabaciones')
    
    op.drop_index('idx_participantes_fecha_union', table_name='videollamada_participantes')
    op.drop_index('idx_participantes_usuario', table_name='videollamada_participantes')
    op.drop_index('idx_participantes_videollamada', table_name='videollamada_participantes')
    op.drop_table('videollamada_participantes')
    
    op.drop_index('idx_videollamadas_deleted_at', table_name='videollamadas')
    op.drop_index('idx_videollamadas_fecha_inicio', table_name='videollamadas')
    op.drop_index('idx_videollamadas_estado', table_name='videollamadas')
    op.drop_index('idx_videollamadas_iniciador', table_name='videollamadas')
    op.drop_index('idx_videollamadas_sala_chat', table_name='videollamadas')
    op.drop_table('videollamadas')
