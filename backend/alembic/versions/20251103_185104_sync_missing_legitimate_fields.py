"""Sincronización de campos legítimos faltantes

Revision ID: sync_missing_fields
Revises: 205feda16a24
Create Date: 2024-11-03 18:40:00

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'sync_missing_fields'
down_revision = '205feda16a24'
branch_labels = None
depends_on = None


def upgrade():
    """Agregar campos faltantes a las tablas"""
    
    # Helper function para agregar columnas solo si no existen
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    
    def add_column_if_not_exists(table_name, column):
        """Agrega una columna solo si no existe"""
        existing_columns = [col['name'] for col in inspector.get_columns(table_name)]
        if column.name not in existing_columns:
            op.add_column(table_name, column)
    
    # ========================================================================
    # CLASE - Sistema de código de acceso y gestión completa
    # ========================================================================
    # Sistema de código de acceso
    add_column_if_not_exists('Clase', sa.Column('codigo_acceso', sa.String(20), nullable=True))
    add_column_if_not_exists('Clase', sa.Column('estado_codigo', sa.String(20), nullable=True))
    add_column_if_not_exists('Clase', sa.Column('fecha_vencimiento_codigo', sa.DateTime(), nullable=True))
    
    # Campos de gestión básicos
    add_column_if_not_exists('Clase', sa.Column('max_estudiantes', sa.Integer(), nullable=True))
    add_column_if_not_exists('Clase', sa.Column('estado', sa.String(20), nullable=True, server_default='activo'))
    add_column_if_not_exists('Clase', sa.Column('tipo_clase', sa.String(50), nullable=True))
    add_column_if_not_exists('Clase', sa.Column('duracion_estimada', sa.Integer(), nullable=True))
    
    # Fechas de programación
    add_column_if_not_exists('Clase', sa.Column('fecha_inicio', sa.DateTime(), nullable=True))
    add_column_if_not_exists('Clase', sa.Column('fecha_fin', sa.DateTime(), nullable=True))
    
    # Relaciones adicionales
    add_column_if_not_exists('Clase', sa.Column('docente_id', postgresql.UUID(as_uuid=True), nullable=True))
    add_column_if_not_exists('Clase', sa.Column('grupo_id', postgresql.UUID(as_uuid=True), nullable=True))
    
    # Auditoría
    add_column_if_not_exists('Clase', sa.Column('fecha_creacion', sa.DateTime(), server_default=sa.text('now()'), nullable=True))
    add_column_if_not_exists('Clase', sa.Column('fecha_actualizacion', sa.DateTime(), nullable=True))
    
    # ========================================================================
    # MATERIAL EDUCATIVO - Versionado y Google Drive
    # ========================================================================
    # Sistema de versionado
    add_column_if_not_exists('MaterialEducativo', sa.Column('version', sa.String(20), nullable=True, server_default='1.0'))
    add_column_if_not_exists('MaterialEducativo', sa.Column('es_version_actual', sa.Boolean(), nullable=True, server_default='true'))
    add_column_if_not_exists('MaterialEducativo', sa.Column('material_original_id', postgresql.UUID(as_uuid=True), nullable=True))
    
    # Google Drive sync
    add_column_if_not_exists('MaterialEducativo', sa.Column('google_drive_id', sa.String(255), nullable=True))
    add_column_if_not_exists('MaterialEducativo', sa.Column('google_drive_url', sa.Text(), nullable=True))
    add_column_if_not_exists('MaterialEducativo', sa.Column('sincronizado_drive', sa.Boolean(), nullable=True, server_default='false'))
    add_column_if_not_exists('MaterialEducativo', sa.Column('fecha_ultima_sync', sa.DateTime(), nullable=True))
    
    # Organización
    add_column_if_not_exists('MaterialEducativo', sa.Column('carpeta', sa.String(255), nullable=True))
    add_column_if_not_exists('MaterialEducativo', sa.Column('tags', postgresql.JSON(), nullable=True))
    
    # Metadatos adicionales
    add_column_if_not_exists('MaterialEducativo', sa.Column('estado', sa.String(20), nullable=True, server_default='disponible'))
    add_column_if_not_exists('MaterialEducativo', sa.Column('numero_descargas', sa.Integer(), nullable=True, server_default='0'))
    add_column_if_not_exists('MaterialEducativo', sa.Column('fecha_ultimo_acceso', sa.DateTime(), nullable=True))
    add_column_if_not_exists('MaterialEducativo', sa.Column('tamano_archivo', sa.BigInteger(), nullable=True))
    add_column_if_not_exists('MaterialEducativo', sa.Column('hash_archivo', sa.String(64), nullable=True))
    
    # Autoría
    add_column_if_not_exists('MaterialEducativo', sa.Column('autor_id', postgresql.UUID(as_uuid=True), nullable=True))
    
    # Auditoría
    add_column_if_not_exists('MaterialEducativo', sa.Column('fecha_creacion', sa.DateTime(), server_default=sa.text('now()'), nullable=True))
    add_column_if_not_exists('MaterialEducativo', sa.Column('fecha_actualizacion', sa.DateTime(), nullable=True))
    
    # ========================================================================
    # TAREAS - Campos básicos faltantes
    # ========================================================================
    add_column_if_not_exists('tareas', sa.Column('archivo_adjunto', sa.String(500), nullable=True))
    add_column_if_not_exists('tareas', sa.Column('clase_id', postgresql.UUID(as_uuid=True), nullable=True))
    add_column_if_not_exists('tareas', sa.Column('permite_entregas_tardias', sa.Boolean(), nullable=True, server_default='false'))
    add_column_if_not_exists('tareas', sa.Column('fecha_modificacion', sa.DateTime(), nullable=True))
    
    # ========================================================================
    # SALAS DE CHAT - Campos de gestión
    # ========================================================================
    add_column_if_not_exists('salas_chat', sa.Column('requiere_aprobacion', sa.Boolean(), nullable=True, server_default='false'))
    add_column_if_not_exists('salas_chat', sa.Column('max_participantes', sa.Integer(), nullable=True))
    add_column_if_not_exists('salas_chat', sa.Column('esta_activa', sa.Boolean(), nullable=True, server_default='true'))
    add_column_if_not_exists('salas_chat', sa.Column('fecha_ultima_actividad', sa.DateTime(), nullable=True))
    add_column_if_not_exists('salas_chat', sa.Column('total_mensajes', sa.Integer(), nullable=True, server_default='0'))
    
    # Renombrar configuracion_json a configuracion (para coincidir con modelo)
    salas_chat_columns = [col['name'] for col in inspector.get_columns('salas_chat')]
    if 'configuracion_json' in salas_chat_columns and 'configuracion' not in salas_chat_columns:
        op.alter_column('salas_chat', 'configuracion_json', new_column_name='configuracion')
    
    # ========================================================================
    # MENSAJES - Campos faltantes
    # ========================================================================
    add_column_if_not_exists('mensajes', sa.Column('texto', sa.Text(), nullable=True))
    add_column_if_not_exists('mensajes', sa.Column('fecha_edicion', sa.DateTime(), nullable=True))
    add_column_if_not_exists('mensajes', sa.Column('editado_por', postgresql.UUID(as_uuid=True), nullable=True))
    add_column_if_not_exists('mensajes', sa.Column('es_respuesta', sa.Boolean(), nullable=True, server_default='false'))
    add_column_if_not_exists('mensajes', sa.Column('total_respuestas', sa.Integer(), nullable=True, server_default='0'))
    add_column_if_not_exists('mensajes', sa.Column('menciones', postgresql.JSON(), nullable=True))
    add_column_if_not_exists('mensajes', sa.Column('datos_adjuntos', postgresql.JSON(), nullable=True))
    add_column_if_not_exists('mensajes', sa.Column('programado_para', sa.DateTime(), nullable=True))
    
    # ========================================================================
    # NOTIFICACIONES - Campos faltantes
    # ========================================================================
    add_column_if_not_exists('notificaciones', sa.Column('tipo', sa.String(50), nullable=True))
    add_column_if_not_exists('notificaciones', sa.Column('referencia_id', postgresql.UUID(as_uuid=True), nullable=True))
    add_column_if_not_exists('notificaciones', sa.Column('referencia_tipo', sa.String(50), nullable=True))
    
    # ========================================================================
    # PARTICIPANTES SALA - Campos de gestión faltantes
    # ========================================================================
    add_column_if_not_exists('participantes_sala', sa.Column('es_moderador', sa.Boolean(), nullable=True, server_default='false'))
    add_column_if_not_exists('participantes_sala', sa.Column('es_admin', sa.Boolean(), nullable=True, server_default='false'))
    add_column_if_not_exists('participantes_sala', sa.Column('fecha_ultima_lectura', sa.DateTime(), nullable=True))
    add_column_if_not_exists('participantes_sala', sa.Column('mensajes_no_leidos', sa.Integer(), nullable=True, server_default='0'))
    add_column_if_not_exists('participantes_sala', sa.Column('sonido_activo', sa.Boolean(), nullable=True, server_default='true'))
    add_column_if_not_exists('participantes_sala', sa.Column('fecha_union', sa.DateTime(), server_default=sa.text('now()'), nullable=True))
    
    # ========================================================================
    # RUBRICAS - Agregar campos si la tabla existe
    # ========================================================================
    if 'rubricas' in inspector.get_table_names():
        add_column_if_not_exists('rubricas', sa.Column('creado_por', postgresql.UUID(as_uuid=True), nullable=True))
        add_column_if_not_exists('rubricas', sa.Column('fecha_creacion', sa.DateTime(), server_default=sa.text('now()'), nullable=True))
    
    print("✅ Migración completada: Campos legítimos sincronizados")


def downgrade():
    """Revertir cambios (eliminar campos agregados)"""
    
    # Clase
    op.drop_column('Clase', 'fecha_actualizacion')
    op.drop_column('Clase', 'fecha_creacion')
    op.drop_column('Clase', 'grupo_id')
    op.drop_column('Clase', 'docente_id')
    op.drop_column('Clase', 'fecha_fin')
    op.drop_column('Clase', 'fecha_inicio')
    op.drop_column('Clase', 'duracion_estimada')
    op.drop_column('Clase', 'tipo_clase')
    op.drop_column('Clase', 'estado')
    op.drop_column('Clase', 'max_estudiantes')
    op.drop_column('Clase', 'fecha_vencimiento_codigo')
    op.drop_column('Clase', 'estado_codigo')
    op.drop_column('Clase', 'codigo_acceso')
    
    # MaterialEducativo
    op.drop_column('MaterialEducativo', 'fecha_actualizacion')
    op.drop_column('MaterialEducativo', 'fecha_creacion')
    op.drop_column('MaterialEducativo', 'autor_id')
    op.drop_column('MaterialEducativo', 'hash_archivo')
    op.drop_column('MaterialEducativo', 'tamano_archivo')
    op.drop_column('MaterialEducativo', 'fecha_ultimo_acceso')
    op.drop_column('MaterialEducativo', 'numero_descargas')
    op.drop_column('MaterialEducativo', 'estado')
    op.drop_column('MaterialEducativo', 'tags')
    op.drop_column('MaterialEducativo', 'carpeta')
    op.drop_column('MaterialEducativo', 'fecha_ultima_sync')
    op.drop_column('MaterialEducativo', 'sincronizado_drive')
    op.drop_column('MaterialEducativo', 'google_drive_url')
    op.drop_column('MaterialEducativo', 'google_drive_id')
    op.drop_column('MaterialEducativo', 'material_original_id')
    op.drop_column('MaterialEducativo', 'es_version_actual')
    op.drop_column('MaterialEducativo', 'version')
    
    # Tareas
    op.drop_column('tareas', 'fecha_modificacion')
    op.drop_column('tareas', 'permite_entregas_tardias')
    op.drop_column('tareas', 'clase_id')
    op.drop_column('tareas', 'archivo_adjunto')
    
    # Salas chat
    op.alter_column('salas_chat', 'configuracion', new_column_name='configuracion_json')
    op.drop_column('salas_chat', 'total_mensajes')
    op.drop_column('salas_chat', 'fecha_ultima_actividad')
    op.drop_column('salas_chat', 'esta_activa')
    op.drop_column('salas_chat', 'max_participantes')
    op.drop_column('salas_chat', 'requiere_aprobacion')
    
    # Mensajes
    op.drop_column('mensajes', 'programado_para')
    op.drop_column('mensajes', 'datos_adjuntos')
    op.drop_column('mensajes', 'menciones')
    op.drop_column('mensajes', 'total_respuestas')
    op.drop_column('mensajes', 'es_respuesta')
    op.drop_column('mensajes', 'editado_por')
    op.drop_column('mensajes', 'fecha_edicion')
    op.drop_column('mensajes', 'texto')
    
    # Notificaciones
    op.drop_column('notificaciones', 'referencia_tipo')
    op.drop_column('notificaciones', 'referencia_id')
    op.drop_column('notificaciones', 'tipo')
    
    # Participantes sala
    op.drop_column('participantes_sala', 'fecha_union')
    op.drop_column('participantes_sala', 'sonido_activo')
    op.drop_column('participantes_sala', 'mensajes_no_leidos')
    op.drop_column('participantes_sala', 'fecha_ultima_lectura')
    op.drop_column('participantes_sala', 'es_admin')
    op.drop_column('participantes_sala', 'es_moderador')
    
    # Rubricas (si existe)
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    if 'rubricas' in inspector.get_table_names():
        op.drop_column('rubricas', 'fecha_creacion')
        op.drop_column('rubricas', 'creado_por')
    
    print("⚠️  Migración revertida")
