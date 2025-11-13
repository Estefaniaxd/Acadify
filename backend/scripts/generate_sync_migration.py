"""
Genera migración para sincronizar campos faltantes en tablas principales.

Esta migración agrega campos legítimos que faltan en BD:
- Clase: Sistema de código de acceso y control
- MaterialEducativo: Versionado y Google Drive
- Tareas: Campos básicos
- Sistema de chat: Ajustes de configuración
"""

from datetime import datetime

# Nombre del archivo de migración
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
filename = f"{timestamp}_sync_missing_legitimate_fields"

migration_content = '''"""Sincronización de campos legítimos faltantes

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
    
    # ========================================================================
    # CLASE - Sistema de código de acceso y gestión completa
    # ========================================================================
    with op.batch_alter_table('Clase', schema=None) as batch_op:
        # Sistema de código de acceso
        batch_op.add_column(sa.Column('codigo_acceso', sa.String(20), nullable=True))
        batch_op.add_column(sa.Column('estado_codigo', sa.String(20), nullable=True))
        batch_op.add_column(sa.Column('fecha_vencimiento_codigo', sa.DateTime(), nullable=True))
        
        # Campos de gestión básicos
        batch_op.add_column(sa.Column('max_estudiantes', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('estado', sa.String(20), nullable=True, server_default='activo'))
        batch_op.add_column(sa.Column('tipo_clase', sa.String(50), nullable=True))
        batch_op.add_column(sa.Column('duracion_estimada', sa.Integer(), nullable=True))
        
        # Fechas de programación
        batch_op.add_column(sa.Column('fecha_inicio', sa.DateTime(), nullable=True))
        batch_op.add_column(sa.Column('fecha_fin', sa.DateTime(), nullable=True))
        
        # Relaciones adicionales
        batch_op.add_column(sa.Column('docente_id', postgresql.UUID(as_uuid=True), nullable=True))
        batch_op.add_column(sa.Column('grupo_id', postgresql.UUID(as_uuid=True), nullable=True))
        
        # Auditoría
        batch_op.add_column(sa.Column('fecha_creacion', sa.DateTime(), server_default=sa.text('now()'), nullable=True))
        batch_op.add_column(sa.Column('fecha_actualizacion', sa.DateTime(), onupdate=sa.text('now()'), nullable=True))
    
    # ========================================================================
    # MATERIAL EDUCATIVO - Versionado y Google Drive
    # ========================================================================
    with op.batch_alter_table('MaterialEducativo', schema=None) as batch_op:
        # Sistema de versionado
        batch_op.add_column(sa.Column('version', sa.String(20), nullable=True, server_default='1.0'))
        batch_op.add_column(sa.Column('es_version_actual', sa.Boolean(), nullable=True, server_default='true'))
        batch_op.add_column(sa.Column('material_original_id', postgresql.UUID(as_uuid=True), nullable=True))
        
        # Google Drive sync
        batch_op.add_column(sa.Column('google_drive_id', sa.String(255), nullable=True))
        batch_op.add_column(sa.Column('google_drive_url', sa.Text(), nullable=True))
        batch_op.add_column(sa.Column('sincronizado_drive', sa.Boolean(), nullable=True, server_default='false'))
        batch_op.add_column(sa.Column('fecha_ultima_sync', sa.DateTime(), nullable=True))
        
        # Organización
        batch_op.add_column(sa.Column('carpeta', sa.String(255), nullable=True))
        batch_op.add_column(sa.Column('tags', postgresql.JSON(), nullable=True))
        
        # Metadatos adicionales
        batch_op.add_column(sa.Column('estado', sa.String(20), nullable=True, server_default='disponible'))
        batch_op.add_column(sa.Column('numero_descargas', sa.Integer(), nullable=True, server_default='0'))
        batch_op.add_column(sa.Column('fecha_ultimo_acceso', sa.DateTime(), nullable=True))
        batch_op.add_column(sa.Column('tamano_archivo', sa.BigInteger(), nullable=True))
        batch_op.add_column(sa.Column('hash_archivo', sa.String(64), nullable=True))
        
        # Autoría
        batch_op.add_column(sa.Column('autor_id', postgresql.UUID(as_uuid=True), nullable=True))
        
        # Auditoría
        batch_op.add_column(sa.Column('fecha_creacion', sa.DateTime(), server_default=sa.text('now()'), nullable=True))
        batch_op.add_column(sa.Column('fecha_actualizacion', sa.DateTime(), onupdate=sa.text('now()'), nullable=True))
    
    # ========================================================================
    # TAREAS - Campos básicos faltantes
    # ========================================================================
    with op.batch_alter_table('tareas', schema=None) as batch_op:
        batch_op.add_column(sa.Column('archivo_adjunto', sa.String(500), nullable=True))
        batch_op.add_column(sa.Column('clase_id', postgresql.UUID(as_uuid=True), nullable=True))
        batch_op.add_column(sa.Column('permite_entregas_tardias', sa.Boolean(), nullable=True, server_default='false'))
        batch_op.add_column(sa.Column('fecha_modificacion', sa.DateTime(), onupdate=sa.text('now()'), nullable=True))
    
    # ========================================================================
    # SALAS DE CHAT - Campos de gestión
    # ========================================================================
    with op.batch_alter_table('salas_chat', schema=None) as batch_op:
        batch_op.add_column(sa.Column('requiere_aprobacion', sa.Boolean(), nullable=True, server_default='false'))
        batch_op.add_column(sa.Column('max_participantes', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('esta_activa', sa.Boolean(), nullable=True, server_default='true'))
        batch_op.add_column(sa.Column('fecha_ultima_actividad', sa.DateTime(), nullable=True))
        batch_op.add_column(sa.Column('total_mensajes', sa.Integer(), nullable=True, server_default='0'))
        
        # Renombrar configuracion_json a configuracion (para coincidir con modelo)
        batch_op.alter_column('configuracion_json', new_column_name='configuracion')
    
    # ========================================================================
    # PARTICIPANTES SALA - Sin cambios necesarios (ya está completo)
    # ========================================================================
    
    # ========================================================================
    # MENSAJES - Campos faltantes
    # ========================================================================
    with op.batch_alter_table('mensajes', schema=None) as batch_op:
        batch_op.add_column(sa.Column('texto', sa.Text(), nullable=True))
        batch_op.add_column(sa.Column('fecha_edicion', sa.DateTime(), nullable=True))
        batch_op.add_column(sa.Column('editado_por', postgresql.UUID(as_uuid=True), nullable=True))
        batch_op.add_column(sa.Column('es_respuesta', sa.Boolean(), nullable=True, server_default='false'))
        batch_op.add_column(sa.Column('total_respuestas', sa.Integer(), nullable=True, server_default='0'))
        batch_op.add_column(sa.Column('menciones', postgresql.JSON(), nullable=True))
        batch_op.add_column(sa.Column('datos_adjuntos', postgresql.JSON(), nullable=True))
        batch_op.add_column(sa.Column('programado_para', sa.DateTime(), nullable=True))
    
    # ========================================================================
    # NOTIFICACIONES - Campos faltantes
    # ========================================================================
    with op.batch_alter_table('notificaciones', schema=None) as batch_op:
        batch_op.add_column(sa.Column('tipo', sa.String(50), nullable=True))
        batch_op.add_column(sa.Column('referencia_id', postgresql.UUID(as_uuid=True), nullable=True))
        batch_op.add_column(sa.Column('referencia_tipo', sa.String(50), nullable=True))
    
    # ========================================================================
    # PARTICIPANTES SALA - Campos de gestión faltantes
    # ========================================================================
    with op.batch_alter_table('participantes_sala', schema=None) as batch_op:
        batch_op.add_column(sa.Column('es_moderador', sa.Boolean(), nullable=True, server_default='false'))
        batch_op.add_column(sa.Column('es_admin', sa.Boolean(), nullable=True, server_default='false'))
        batch_op.add_column(sa.Column('fecha_ultima_lectura', sa.DateTime(), nullable=True))
        batch_op.add_column(sa.Column('mensajes_no_leidos', sa.Integer(), nullable=True, server_default='0'))
        batch_op.add_column(sa.Column('sonido_activo', sa.Boolean(), nullable=True, server_default='true'))
        batch_op.add_column(sa.Column('fecha_union', sa.DateTime(), server_default=sa.text('now()'), nullable=True))
    
    # ========================================================================
    # RUBRICAS - Crear tabla si no existe
    # ========================================================================
    # Nota: Si la tabla no existe, comentar este bloque y crear en migración separada
    try:
        with op.batch_alter_table('rubricas', schema=None) as batch_op:
            batch_op.add_column(sa.Column('creado_por', postgresql.UUID(as_uuid=True), nullable=True))
            batch_op.add_column(sa.Column('fecha_creacion', sa.DateTime(), server_default=sa.text('now()'), nullable=True))
    except:
        # Si la tabla no existe, skip
        pass
    
    print("✅ Migración completada: Campos legítimos sincronizados")


def downgrade():
    """Revertir cambios (eliminar campos agregados)"""
    
    # Clase
    with op.batch_alter_table('Clase', schema=None) as batch_op:
        batch_op.drop_column('fecha_actualizacion')
        batch_op.drop_column('fecha_creacion')
        batch_op.drop_column('grupo_id')
        batch_op.drop_column('docente_id')
        batch_op.drop_column('fecha_fin')
        batch_op.drop_column('fecha_inicio')
        batch_op.drop_column('duracion_estimada')
        batch_op.drop_column('tipo_clase')
        batch_op.drop_column('estado')
        batch_op.drop_column('max_estudiantes')
        batch_op.drop_column('fecha_vencimiento_codigo')
        batch_op.drop_column('estado_codigo')
        batch_op.drop_column('codigo_acceso')
    
    # MaterialEducativo
    with op.batch_alter_table('MaterialEducativo', schema=None) as batch_op:
        batch_op.drop_column('fecha_actualizacion')
        batch_op.drop_column('fecha_creacion')
        batch_op.drop_column('autor_id')
        batch_op.drop_column('hash_archivo')
        batch_op.drop_column('tamano_archivo')
        batch_op.drop_column('fecha_ultimo_acceso')
        batch_op.drop_column('numero_descargas')
        batch_op.drop_column('estado')
        batch_op.drop_column('tags')
        batch_op.drop_column('carpeta')
        batch_op.drop_column('fecha_ultima_sync')
        batch_op.drop_column('sincronizado_drive')
        batch_op.drop_column('google_drive_url')
        batch_op.drop_column('google_drive_id')
        batch_op.drop_column('material_original_id')
        batch_op.drop_column('es_version_actual')
        batch_op.drop_column('version')
    
    # Tareas
    with op.batch_alter_table('tareas', schema=None) as batch_op:
        batch_op.drop_column('fecha_modificacion')
        batch_op.drop_column('permite_entregas_tardias')
        batch_op.drop_column('clase_id')
        batch_op.drop_column('archivo_adjunto')
    
    # Salas chat
    with op.batch_alter_table('salas_chat', schema=None) as batch_op:
        batch_op.alter_column('configuracion', new_column_name='configuracion_json')
        batch_op.drop_column('total_mensajes')
        batch_op.drop_column('fecha_ultima_actividad')
        batch_op.drop_column('esta_activa')
        batch_op.drop_column('max_participantes')
        batch_op.drop_column('requiere_aprobacion')
    
    # Mensajes
    with op.batch_alter_table('mensajes', schema=None) as batch_op:
        batch_op.drop_column('programado_para')
        batch_op.drop_column('datos_adjuntos')
        batch_op.drop_column('menciones')
        batch_op.drop_column('total_respuestas')
        batch_op.drop_column('es_respuesta')
        batch_op.drop_column('editado_por')
        batch_op.drop_column('fecha_edicion')
        batch_op.drop_column('texto')
    
    # Notificaciones
    with op.batch_alter_table('notificaciones', schema=None) as batch_op:
        batch_op.drop_column('referencia_tipo')
        batch_op.drop_column('referencia_id')
        batch_op.drop_column('tipo')
    
    # Participantes sala
    with op.batch_alter_table('participantes_sala', schema=None) as batch_op:
        batch_op.drop_column('fecha_union')
        batch_op.drop_column('sonido_activo')
        batch_op.drop_column('mensajes_no_leidos')
        batch_op.drop_column('fecha_ultima_lectura')
        batch_op.drop_column('es_admin')
        batch_op.drop_column('es_moderador')
    
    print("⚠️  Migración revertida")
'''

print("📝 Generando archivo de migración...")
print(f"   Archivo: alembic/versions/{filename}.py")
print("\n" + "="*70)
print(migration_content)
print("="*70)

# Guardar el archivo
output_path = f"alembic/versions/{filename}.py"
with open(output_path, 'w', encoding='utf-8') as f:
    f.write(migration_content)

print(f"\n✅ Migración generada: {output_path}")
print("\n💡 Próximos pasos:")
print("   1. Revisa el archivo generado")
print("   2. Ejecuta: alembic upgrade head")
print("   3. Verifica: python scripts/verify_models_vs_sql.py")
