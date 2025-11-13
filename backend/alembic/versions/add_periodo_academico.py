"""Add PeriodoAcademico table

Revision ID: add_periodo_academico
Revises: fc4e3b4225a5
Create Date: 2025-10-30 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'add_periodo_academico'
down_revision: Union[str, Sequence[str], None] = 'fc4e3b4225a5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema - Crear tabla periodos_academicos"""
    
    # Crear ENUMs para PeriodoAcademico
    op.execute("""
        DO $$ BEGIN
            IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'tipo_periodo') THEN
                CREATE TYPE tipo_periodo AS ENUM (
                    'semestral', 'trimestral', 'cuatrimestral', 'bimestral',
                    'mensual', 'modular', 'anual', 'continuo',
                    'intersemestral', 'intensivo'
                );
            END IF;
        END $$;
    """)
    
    op.execute("""
        DO $$ BEGIN
            IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'estado_periodo') THEN
                CREATE TYPE estado_periodo AS ENUM (
                    'programado', 'preinscripciones', 'inscripciones_abiertas',
                    'en_curso', 'evaluaciones', 'finalizado', 'cancelado'
                );
            END IF;
        END $$;
    """)
    
    # Crear tabla periodos_academicos
    op.create_table(
        'periodos_academicos',
        
        # Identificación
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('institucion_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('nombre', sa.String(length=200), nullable=False),
        sa.Column('codigo', sa.String(length=50), nullable=False),
        sa.Column('descripcion', sa.Text(), nullable=True),
        
        # Tipo y clasificación
        sa.Column('tipo', sa.String(length=50), nullable=False),
        sa.Column('estado', sa.String(length=50), nullable=False, server_default='programado'),
        sa.Column('anio', sa.Integer(), nullable=False),
        sa.Column('numero_periodo', sa.Integer(), nullable=True),
        sa.Column('nivel_aplica', sa.String(length=100), nullable=True),
        
        # Fechas del período
        sa.Column('fecha_inicio', sa.Date(), nullable=False),
        sa.Column('fecha_fin', sa.Date(), nullable=False),
        
        # Fechas de inscripciones
        sa.Column('fecha_inicio_preinscripciones', sa.Date(), nullable=True),
        sa.Column('fecha_fin_preinscripciones', sa.Date(), nullable=True),
        sa.Column('fecha_inicio_inscripciones', sa.Date(), nullable=False),
        sa.Column('fecha_fin_inscripciones', sa.Date(), nullable=False),
        
        # Fechas de ajustes
        sa.Column('fecha_inicio_ajustes', sa.Date(), nullable=True),
        sa.Column('fecha_fin_ajustes', sa.Date(), nullable=True),
        
        # Fechas de clases
        sa.Column('fecha_inicio_clases', sa.Date(), nullable=False),
        sa.Column('fecha_fin_clases', sa.Date(), nullable=False),
        
        # Fechas de retiros
        sa.Column('fecha_limite_retiro', sa.Date(), nullable=True),
        sa.Column('fecha_limite_retiro_con_reembolso', sa.Date(), nullable=True),
        
        # Fechas de evaluaciones
        sa.Column('fecha_inicio_examenes', sa.Date(), nullable=True),
        sa.Column('fecha_fin_examenes', sa.Date(), nullable=True),
        
        # Fechas de calificaciones
        sa.Column('fecha_cierre_notas', sa.Date(), nullable=True),
        sa.Column('fecha_publicacion_notas', sa.Date(), nullable=True),
        
        # Configuración - Capacidades
        sa.Column('permite_inscripciones', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('permite_ajustes', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('permite_retiros', sa.Boolean(), nullable=False, server_default='true'),
        
        # Configuración - Visibilidad
        sa.Column('visible_estudiantes', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('visible_profesores', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('visible_publico', sa.Boolean(), nullable=False, server_default='false'),
        
        # Límites académicos
        sa.Column('creditos_minimos', sa.Integer(), nullable=True),
        sa.Column('creditos_maximos', sa.Integer(), nullable=True),
        sa.Column('cursos_minimos', sa.Integer(), nullable=True),
        sa.Column('cursos_maximos', sa.Integer(), nullable=True),
        
        # Costos
        sa.Column('costo_matricula', sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column('costo_por_credito', sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column('moneda', sa.String(length=10), nullable=False, server_default='COP'),
        
        # Metadata
        sa.Column('dias_festivos', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('vacaciones', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('configuracion', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('notas', sa.Text(), nullable=True),
        
        # Estado y control
        sa.Column('activo', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('es_actual', sa.Boolean(), nullable=False, server_default='false'),
        
        # Auditoría
        sa.Column('creado_por_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('modificado_por_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('fecha_creacion', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('fecha_actualizacion', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        
        # Constraints
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['institucion_id'], ['Institucion.institucion_id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['creado_por_id'], ['Usuario.usuario_id'], ),
        sa.ForeignKeyConstraint(['modificado_por_id'], ['Usuario.usuario_id'], ),
        sa.UniqueConstraint('codigo', name='uq_periodo_codigo')
    )
    
    # Crear índices para mejorar performance
    op.create_index('ix_periodos_academicos_id', 'periodos_academicos', ['id'])
    op.create_index('ix_periodos_academicos_institucion_id', 'periodos_academicos', ['institucion_id'])
    op.create_index('ix_periodos_academicos_anio', 'periodos_academicos', ['anio'])
    op.create_index('ix_periodos_academicos_fecha_inicio', 'periodos_academicos', ['fecha_inicio'])
    op.create_index('ix_periodos_academicos_fecha_fin', 'periodos_academicos', ['fecha_fin'])
    op.create_index('ix_periodos_academicos_activo', 'periodos_academicos', ['activo'])
    op.create_index('ix_periodos_academicos_es_actual', 'periodos_academicos', ['es_actual'])
    
    # Índice compuesto para búsquedas frecuentes
    op.create_index(
        'ix_periodos_academicos_institucion_activo',
        'periodos_academicos',
        ['institucion_id', 'activo']
    )
    
    op.create_index(
        'ix_periodos_academicos_institucion_anio',
        'periodos_academicos',
        ['institucion_id', 'anio']
    )


def downgrade() -> None:
    """Downgrade schema - Eliminar tabla periodos_academicos"""
    
    # Eliminar índices
    op.drop_index('ix_periodos_academicos_institucion_anio', table_name='periodos_academicos')
    op.drop_index('ix_periodos_academicos_institucion_activo', table_name='periodos_academicos')
    op.drop_index('ix_periodos_academicos_es_actual', table_name='periodos_academicos')
    op.drop_index('ix_periodos_academicos_activo', table_name='periodos_academicos')
    op.drop_index('ix_periodos_academicos_fecha_fin', table_name='periodos_academicos')
    op.drop_index('ix_periodos_academicos_fecha_inicio', table_name='periodos_academicos')
    op.drop_index('ix_periodos_academicos_anio', table_name='periodos_academicos')
    op.drop_index('ix_periodos_academicos_institucion_id', table_name='periodos_academicos')
    op.drop_index('ix_periodos_academicos_id', table_name='periodos_academicos')
    
    # Eliminar tabla
    op.drop_table('periodos_academicos')
    
    # Eliminar ENUMs (comentado porque pueden estar en uso)
    # op.execute('DROP TYPE IF EXISTS estado_periodo')
    # op.execute('DROP TYPE IF EXISTS tipo_periodo')
