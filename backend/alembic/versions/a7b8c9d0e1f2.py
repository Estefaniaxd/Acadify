"""add_tareas_system_tables

Revision ID: a7b8c9d0e1f2
Revises: fc4e3b4225a5
Create Date: 2025-09-26 15:30:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'a7b8c9d0e1f2'
down_revision = 'fc4e3b4225a5'
branch_labels = None
depends_on = None

def upgrade():
    # Crear enums solo si no existen
    op.execute("""
        DO $$
        BEGIN
            IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'estado_tarea') THEN
                CREATE TYPE estado_tarea AS ENUM ('asignada', 'en_progreso', 'entregada', 'calificada', 'vencida', 'cancelada');
            END IF;
        END$$;
    """)
    
    op.execute("""
        DO $$
        BEGIN
            IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'tipo_tarea') THEN
                CREATE TYPE tipo_tarea AS ENUM ('ensayo', 'proyecto', 'ejercicios', 'investigacion', 'presentacion', 'laboratorio', 'lectura', 'examen', 'otro');
            END IF;
        END$$;
    """)
    
    op.execute("""
        DO $$
        BEGIN
            IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'prioridad_tarea') THEN
                CREATE TYPE prioridad_tarea AS ENUM ('baja', 'media', 'alta', 'urgente');
            END IF;
        END$$;
    """)
    
    op.execute("""
        DO $$
        BEGIN
            IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'estado_entrega') THEN
                CREATE TYPE estado_entrega AS ENUM ('borrador', 'entregada', 'calificada', 'devuelta', 'reentregada');
            END IF;
        END$$;
    """)
    
    # Crear tabla rubricas
    op.create_table('rubricas',
        sa.Column('rubrica_id', sa.String(), nullable=False),
        sa.Column('nombre', sa.String(length=200), nullable=False),
        sa.Column('descripcion', sa.Text(), nullable=True),
        sa.Column('criterios', sa.JSON(), nullable=False),
        sa.Column('puntuacion_total', sa.Float(), nullable=False, default=100.0),
        sa.Column('es_publica', sa.Boolean(), nullable=True, default=True),
        sa.Column('es_plantilla', sa.Boolean(), nullable=True, default=False),
        sa.Column('activa', sa.Boolean(), nullable=True, default=True),
        sa.Column('fecha_creacion', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('fecha_actualizacion', sa.DateTime(timezone=True), nullable=True),
        sa.Column('creado_por', sa.String(), nullable=False),
        # sa.ForeignKeyConstraint(['creado_por'], ['usuarios.usuario_id'], ),  # Comentado temporalmente
        sa.PrimaryKeyConstraint('rubrica_id')
    )
    
    # Crear tabla tareas
    op.create_table('tareas',
        sa.Column('tarea_id', sa.String(), nullable=False),
        sa.Column('grupo_id', sa.String(), nullable=False),
        sa.Column('docente_id', sa.String(), nullable=False),
        sa.Column('titulo', sa.String(length=200), nullable=False),
        sa.Column('descripcion', sa.Text(), nullable=True),
        sa.Column('instrucciones', sa.Text(), nullable=True),
        sa.Column('objetivos', sa.Text(), nullable=True),
        sa.Column('tipo_tarea', sa.Enum('ensayo', 'proyecto', 'ejercicios', 'investigacion', 'presentacion', 'laboratorio', 'lectura', 'examen', 'otro', name='tipo_tarea'), nullable=False, default='ensayo'),
        sa.Column('prioridad', sa.Enum('baja', 'media', 'alta', 'urgente', name='prioridad_tarea'), nullable=False, default='media'),
        sa.Column('categoria', sa.String(length=100), nullable=True),
        sa.Column('tags', sa.String(length=500), nullable=True),
        sa.Column('fecha_asignacion', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('fecha_limite', sa.DateTime(timezone=True), nullable=False),
        sa.Column('fecha_inicio_disponible', sa.DateTime(timezone=True), nullable=True),
        sa.Column('tiempo_estimado', sa.Integer(), nullable=True),
        sa.Column('permite_entrega_tardia', sa.Boolean(), nullable=True, default=False),
        sa.Column('penalizacion_tardia', sa.Float(), nullable=True, default=0.0),
        sa.Column('intentos_maximos', sa.Integer(), nullable=True, default=1),
        sa.Column('formato_entrega', sa.String(length=200), nullable=True),
        sa.Column('tamano_maximo_mb', sa.Float(), nullable=True, default=10.0),
        sa.Column('puntuacion_maxima', sa.Float(), nullable=False, default=100.0),
        sa.Column('peso_evaluacion', sa.Float(), nullable=True, default=1.0),
        sa.Column('rubrica_id', sa.String(), nullable=True),
        sa.Column('estado', sa.Enum('asignada', 'en_progreso', 'entregada', 'calificada', 'vencida', 'cancelada', name='estado_tarea'), nullable=False, default='asignada'),
        sa.Column('es_grupal', sa.Boolean(), nullable=True, default=False),
        sa.Column('es_publica', sa.Boolean(), nullable=True, default=True),
        sa.Column('requiere_aprobacion', sa.Boolean(), nullable=True, default=False),
        sa.Column('configuracion_json', sa.JSON(), nullable=True),
        sa.Column('recursos_necesarios', sa.Text(), nullable=True),
        sa.Column('criterios_evaluacion', sa.Text(), nullable=True),
        sa.Column('activa', sa.Boolean(), nullable=True, default=True),
        sa.Column('fecha_creacion', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('fecha_actualizacion', sa.DateTime(timezone=True), nullable=True),
        sa.Column('creado_por', sa.String(), nullable=True),
        sa.Column('actualizado_por', sa.String(), nullable=True),
        sa.ForeignKeyConstraint(['creado_por'], ['usuarios.usuario_id'], ),
        sa.ForeignKeyConstraint(['actualizado_por'], ['usuarios.usuario_id'], ),
        sa.ForeignKeyConstraint(['docente_id'], ['usuarios.usuario_id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['grupo_id'], ['grupos.grupo_id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['rubrica_id'], ['rubricas.rubrica_id'], ),
        sa.PrimaryKeyConstraint('tarea_id')
    )
    
    # Crear tabla entregas_tareas
    op.create_table('entregas_tareas',
        sa.Column('entrega_id', sa.String(), nullable=False),
        sa.Column('tarea_id', sa.String(), nullable=False),
        sa.Column('estudiante_id', sa.String(), nullable=False),
        sa.Column('titulo_entrega', sa.String(length=200), nullable=True),
        sa.Column('descripcion_entrega', sa.Text(), nullable=True),
        sa.Column('comentarios_estudiante', sa.Text(), nullable=True),
        sa.Column('archivo_url', sa.String(length=500), nullable=True),
        sa.Column('archivos_adicionales', sa.JSON(), nullable=True),
        sa.Column('contenido_texto', sa.Text(), nullable=True),
        sa.Column('enlaces_externos', sa.JSON(), nullable=True),
        sa.Column('fecha_entrega', sa.DateTime(timezone=True), nullable=True),
        sa.Column('fecha_limite_original', sa.DateTime(timezone=True), nullable=True),
        sa.Column('numero_intento', sa.Integer(), nullable=True, default=1),
        sa.Column('es_entrega_tardia', sa.Boolean(), nullable=True, default=False),
        sa.Column('calificacion', sa.Float(), nullable=True),
        sa.Column('calificacion_letras', sa.String(length=5), nullable=True),
        sa.Column('comentarios_docente', sa.Text(), nullable=True),
        sa.Column('rubrica_calificacion', sa.JSON(), nullable=True),
        sa.Column('estado', sa.String(length=50), nullable=True, default='borrador'),
        sa.Column('es_final', sa.Boolean(), nullable=True, default=False),
        sa.Column('requiere_revision', sa.Boolean(), nullable=True, default=False),
        sa.Column('tiempo_empleado', sa.Integer(), nullable=True),
        sa.Column('dificultad_percibida', sa.Integer(), nullable=True),
        sa.Column('satisfaccion_estudiante', sa.Integer(), nullable=True),
        sa.Column('fecha_creacion', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('fecha_actualizacion', sa.DateTime(timezone=True), nullable=True),
        sa.Column('calificado_por', sa.String(), nullable=True),
        sa.Column('fecha_calificacion', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['calificado_por'], ['usuarios.usuario_id'], ),
        sa.ForeignKeyConstraint(['estudiante_id'], ['usuarios.usuario_id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['tarea_id'], ['tareas.tarea_id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('entrega_id')
    )
    
    # Crear índices para optimizar consultas
    op.create_index('idx_tareas_grupo_id', 'tareas', ['grupo_id'])
    op.create_index('idx_tareas_docente_id', 'tareas', ['docente_id'])
    op.create_index('idx_tareas_fecha_limite', 'tareas', ['fecha_limite'])
    op.create_index('idx_tareas_estado', 'tareas', ['estado'])
    op.create_index('idx_entregas_tarea_id', 'entregas_tareas', ['tarea_id'])
    op.create_index('idx_entregas_estudiante_id', 'entregas_tareas', ['estudiante_id'])
    op.create_index('idx_entregas_estado', 'entregas_tareas', ['estado'])


def downgrade():
    # Eliminar índices
    op.drop_index('idx_entregas_estado', table_name='entregas_tareas')
    op.drop_index('idx_entregas_estudiante_id', table_name='entregas_tareas')
    op.drop_index('idx_entregas_tarea_id', table_name='entregas_tareas')
    op.drop_index('idx_tareas_estado', table_name='tareas')
    op.drop_index('idx_tareas_fecha_limite', table_name='tareas')
    op.drop_index('idx_tareas_docente_id', table_name='tareas')
    op.drop_index('idx_tareas_grupo_id', table_name='tareas')
    
    # Eliminar tablas
    op.drop_table('entregas_tareas')
    op.drop_table('tareas')
    op.drop_table('rubricas')
    
    # Eliminar enums
    postgresql.ENUM(name='estado_entrega').drop(op.get_bind())
    postgresql.ENUM(name='prioridad_tarea').drop(op.get_bind())
    postgresql.ENUM(name='tipo_tarea').drop(op.get_bind())
    postgresql.ENUM(name='estado_tarea').drop(op.get_bind())