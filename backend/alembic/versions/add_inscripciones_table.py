"""Add Inscripciones table - Sistema completo de inscripciones académicas

Revision ID: add_inscripciones_table
Revises: add_periodo_academico
Create Date: 2025-10-30 18:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'add_inscripciones_table'
down_revision: Union[str, Sequence[str], None] = 'add_periodo_academico'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema - Crear tabla inscripciones"""
    
    # Crear ENUMs para Inscripciones (si no existen)
    op.execute("""
        DO $$ BEGIN
            IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'estado_inscripcion') THEN
                CREATE TYPE estado_inscripcion AS ENUM (
                    'pre_inscrita', 'pendiente_pago', 'pendiente_documentos',
                    'pendiente_aprobacion', 'aprobada', 'confirmada', 'activa',
                    'completada', 'retirada', 'rechazada', 'cancelada',
                    'en_lista_espera', 'suspendida', 'congelada',
                    'reactivada', 'aplazada', 'transferida'
                );
            END IF;
        END $$;
    """)
    
    op.execute("""
        DO $$ BEGIN
            IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'tipo_inscripcion') THEN
                CREATE TYPE tipo_inscripcion AS ENUM (
                    'regular', 'primera_vez', 'reingreso', 'transferencia',
                    'convalidacion', 'homologacion', 'oyente', 'especial',
                    'prueba', 'intercambio', 'doble_titulacion', 'simultanea',
                    'extraordinaria', 'especial_verano', 'remedial'
                );
            END IF;
        END $$;
    """)
    
    op.execute("""
        DO $$ BEGIN
            IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'motivo_rechazo') THEN
                CREATE TYPE motivo_rechazo AS ENUM (
                    'no_cumple_requisitos', 'cupo_lleno', 'documentos_incompletos',
                    'pago_rechazado', 'conflicto_horario', 'prerequisitos_faltantes',
                    'sancion_disciplinaria', 'deuda_pendiente', 'otro'
                );
            END IF;
        END $$;
    """)
    
    op.execute("""
        DO $$ BEGIN
            IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'motivo_retiro') THEN
                CREATE TYPE motivo_retiro AS ENUM (
                    'voluntario', 'bajo_rendimiento', 'salud', 'financiero',
                    'familiar', 'laboral', 'cambio_programa', 'insatisfaccion',
                    'traslado', 'cancelacion_curso', 'cancelacion_administrativa', 'otro'
                );
            END IF;
        END $$;
    """)
    
    op.execute("""
        DO $$ BEGIN
            IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'forma_pago') THEN
                CREATE TYPE forma_pago AS ENUM (
                    'efectivo', 'tarjeta_credito', 'tarjeta_debito', 'transferencia',
                    'pse', 'cheque', 'credito_estudiantil', 'beca', 'patrocinio', 'otro'
                );
            END IF;
        END $$;
    """)
    
    # Crear tabla inscripciones
    op.create_table(
        'inscripciones',
        
        # ==================== 1. Identificación ====================
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('estudiante_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('grupo_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('periodo_academico_id', sa.Integer(), nullable=True),
        sa.Column('programa_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('codigo_inscripcion', sa.String(length=50), nullable=False),
        
        # ==================== 2. Tipo y Estado ====================
        sa.Column('tipo_inscripcion', sa.String(length=50), nullable=False, server_default='regular'),
        sa.Column('estado', sa.String(length=50), nullable=False, server_default='pre_inscrita'),
        
        # ==================== 3. Fechas del Proceso ====================
        sa.Column('fecha_solicitud', sa.DateTime(), nullable=True),
        sa.Column('fecha_preinscripcion', sa.DateTime(), nullable=True),
        sa.Column('fecha_inscripcion', sa.DateTime(), nullable=True),
        sa.Column('fecha_confirmacion', sa.DateTime(), nullable=True),
        sa.Column('fecha_inicio_clases', sa.DateTime(), nullable=True),
        sa.Column('fecha_finalizacion', sa.DateTime(), nullable=True),
        sa.Column('fecha_retiro', sa.DateTime(), nullable=True),
        sa.Column('fecha_cancelacion', sa.DateTime(), nullable=True),
        
        # Fechas límite
        sa.Column('fecha_limite_pago', sa.DateTime(), nullable=True),
        sa.Column('fecha_limite_documentos', sa.DateTime(), nullable=True),
        sa.Column('fecha_limite_confirmacion', sa.DateTime(), nullable=True),
        
        # ==================== 4. Información Académica ====================
        sa.Column('creditos_inscritos', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('horas_semanales', sa.Integer(), nullable=True),
        sa.Column('numero_lista', sa.Integer(), nullable=True),
        sa.Column('prioridad', sa.Integer(), nullable=True, server_default='0'),
        
        # Convalidación y homologación
        sa.Column('tiene_convalidacion', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('creditos_convalidados', sa.Integer(), nullable=True),
        sa.Column('tiene_homologacion', sa.Boolean(), nullable=False, server_default='false'),
        
        # Prerequisitos
        sa.Column('cumple_prerequisitos', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('prerequisitos_verificados', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('fecha_verificacion_prerequisitos', sa.DateTime(), nullable=True),
        
        # ==================== 5. Información Financiera ====================
        # Costos
        sa.Column('costo_total', sa.Numeric(precision=12, scale=2), nullable=True),
        sa.Column('costo_matricula', sa.Numeric(precision=12, scale=2), nullable=True),
        sa.Column('costo_curso', sa.Numeric(precision=12, scale=2), nullable=True),
        sa.Column('otros_costos', sa.Numeric(precision=12, scale=2), nullable=True),
        sa.Column('descuentos', sa.Numeric(precision=12, scale=2), nullable=True),
        sa.Column('monto_final', sa.Numeric(precision=12, scale=2), nullable=True),
        
        # Pagos
        sa.Column('forma_pago', sa.String(length=50), nullable=True),
        sa.Column('esta_pagado', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('fecha_pago', sa.DateTime(), nullable=True),
        sa.Column('referencia_pago', sa.String(length=100), nullable=True),
        
        # Becas
        sa.Column('tiene_beca', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('porcentaje_beca', sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column('tipo_beca', sa.String(length=100), nullable=True),
        
        # Crédito
        sa.Column('tiene_credito', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('entidad_credito', sa.String(length=200), nullable=True),
        
        # ==================== 6. Documentación ====================
        sa.Column('documentos_completos', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('documentos_requeridos', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('documentos_entregados', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('documentos_pendientes', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('fecha_entrega_documentos', sa.DateTime(), nullable=True),
        
        # ==================== 7. Aprobaciones y Validaciones ====================
        sa.Column('requiere_aprobacion', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('esta_aprobada', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('aprobada_por_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('fecha_aprobacion', sa.DateTime(), nullable=True),
        sa.Column('comentarios_aprobacion', sa.Text(), nullable=True),
        
        # ==================== 8. Rechazo y Cancelación ====================
        # Rechazo
        sa.Column('fue_rechazada', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('motivo_rechazo', sa.String(length=50), nullable=True),
        sa.Column('descripcion_rechazo', sa.Text(), nullable=True),
        sa.Column('rechazada_por_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('fecha_rechazo', sa.DateTime(), nullable=True),
        
        # Retiro
        sa.Column('fue_retirada', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('motivo_retiro', sa.String(length=50), nullable=True),
        sa.Column('descripcion_retiro', sa.Text(), nullable=True),
        sa.Column('fue_retiro_voluntario', sa.Boolean(), nullable=True),
        sa.Column('permite_reingreso', sa.Boolean(), nullable=False, server_default='true'),
        
        # ==================== 9. Calificaciones y Resultado ====================
        sa.Column('calificacion_final', sa.Numeric(precision=4, scale=2), nullable=True),
        sa.Column('calificacion_literal', sa.String(length=10), nullable=True),
        sa.Column('aprobo_curso', sa.Boolean(), nullable=True),
        
        # Asistencia
        sa.Column('porcentaje_asistencia', sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column('cumple_asistencia_minima', sa.Boolean(), nullable=True),
        
        # Certificación
        sa.Column('genera_certificado', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('certificado_emitido', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('fecha_emision_certificado', sa.DateTime(), nullable=True),
        sa.Column('codigo_certificado', sa.String(length=100), nullable=True),
        
        # ==================== 10. Lista de Espera ====================
        sa.Column('en_lista_espera', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('posicion_lista_espera', sa.Integer(), nullable=True),
        sa.Column('fecha_entrada_lista_espera', sa.DateTime(), nullable=True),
        sa.Column('fecha_salida_lista_espera', sa.DateTime(), nullable=True),
        sa.Column('notificado_cupo_disponible', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('fecha_notificacion_cupo', sa.DateTime(), nullable=True),
        
        # ==================== 11. Configuración y Metadata ====================
        # Permisos
        sa.Column('puede_cancelar', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('puede_retirar', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('permite_ajustes', sa.Boolean(), nullable=False, server_default='false'),
        
        # Alertas
        sa.Column('requiere_atencion', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('motivo_atencion', sa.String(length=200), nullable=True),
        sa.Column('tiene_observaciones', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('observaciones', sa.Text(), nullable=True),
        
        # Metadata
        sa.Column('metadata_adicional', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('notas_internas', sa.Text(), nullable=True),
        sa.Column('historial_cambios', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        
        # ==================== 12. Auditoría ====================
        sa.Column('creado_por_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('modificado_por_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('fecha_creacion', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('fecha_actualizacion', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('activo', sa.Boolean(), nullable=False, server_default='true'),
        
        # ==================== Constraints ====================
        sa.PrimaryKeyConstraint('id'),
        
        # Foreign Keys con CASCADE
        sa.ForeignKeyConstraint(['estudiante_id'], ['Usuario.usuario_id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['grupo_id'], ['Grupo.grupo_id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['periodo_academico_id'], ['periodos_academicos.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['programa_id'], ['Programa.programa_id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['aprobada_por_id'], ['Usuario.usuario_id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['rechazada_por_id'], ['Usuario.usuario_id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['creado_por_id'], ['Usuario.usuario_id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['modificado_por_id'], ['Usuario.usuario_id'], ondelete='SET NULL'),
        
        # Unique constraints
        sa.UniqueConstraint('codigo_inscripcion', name='uq_inscripcion_codigo'),
        
        # Check constraints
        sa.CheckConstraint('calificacion_final >= 0 AND calificacion_final <= 5', name='ck_calificacion_final_rango'),
        sa.CheckConstraint('porcentaje_asistencia >= 0 AND porcentaje_asistencia <= 100', name='ck_asistencia_rango'),
        sa.CheckConstraint('porcentaje_beca >= 0 AND porcentaje_beca <= 100', name='ck_beca_rango'),
        sa.CheckConstraint('creditos_inscritos >= 0', name='ck_creditos_positivos'),
        sa.CheckConstraint('monto_final >= 0', name='ck_monto_positivo'),
    )
    
    # ==================== Crear Índices ====================
    
    # Índices simples para búsquedas frecuentes
    op.create_index('ix_inscripciones_id', 'inscripciones', ['id'])
    op.create_index('ix_inscripciones_estudiante_id', 'inscripciones', ['estudiante_id'])
    op.create_index('ix_inscripciones_grupo_id', 'inscripciones', ['grupo_id'])
    op.create_index('ix_inscripciones_periodo_academico_id', 'inscripciones', ['periodo_academico_id'])
    op.create_index('ix_inscripciones_programa_id', 'inscripciones', ['programa_id'])
    op.create_index('ix_inscripciones_codigo_inscripcion', 'inscripciones', ['codigo_inscripcion'])
    op.create_index('ix_inscripciones_estado', 'inscripciones', ['estado'])
    op.create_index('ix_inscripciones_tipo_inscripcion', 'inscripciones', ['tipo_inscripcion'])
    op.create_index('ix_inscripciones_activo', 'inscripciones', ['activo'])
    op.create_index('ix_inscripciones_fecha_creacion', 'inscripciones', ['fecha_creacion'])
    
    # Índices para estados específicos
    op.create_index('ix_inscripciones_esta_pagado', 'inscripciones', ['esta_pagado'])
    op.create_index('ix_inscripciones_esta_aprobada', 'inscripciones', ['esta_aprobada'])
    op.create_index('ix_inscripciones_en_lista_espera', 'inscripciones', ['en_lista_espera'])
    
    # Índices compuestos para consultas complejas
    op.create_index(
        'ix_inscripciones_estudiante_activo',
        'inscripciones',
        ['estudiante_id', 'activo']
    )
    
    op.create_index(
        'ix_inscripciones_grupo_estado',
        'inscripciones',
        ['grupo_id', 'estado']
    )
    
    op.create_index(
        'ix_inscripciones_periodo_estado',
        'inscripciones',
        ['periodo_academico_id', 'estado']
    )
    
    op.create_index(
        'ix_inscripciones_estudiante_grupo',
        'inscripciones',
        ['estudiante_id', 'grupo_id']
    )
    
    op.create_index(
        'ix_inscripciones_lista_espera',
        'inscripciones',
        ['grupo_id', 'en_lista_espera', 'posicion_lista_espera']
    )
    
    # Índice para búsquedas de inscripciones activas en grupos
    op.create_index(
        'ix_inscripciones_grupo_activas',
        'inscripciones',
        ['grupo_id', 'activo', 'estado']
    )


def downgrade() -> None:
    """Downgrade schema - Eliminar tabla inscripciones"""
    
    # Eliminar índices compuestos
    op.drop_index('ix_inscripciones_grupo_activas', table_name='inscripciones')
    op.drop_index('ix_inscripciones_lista_espera', table_name='inscripciones')
    op.drop_index('ix_inscripciones_estudiante_grupo', table_name='inscripciones')
    op.drop_index('ix_inscripciones_periodo_estado', table_name='inscripciones')
    op.drop_index('ix_inscripciones_grupo_estado', table_name='inscripciones')
    op.drop_index('ix_inscripciones_estudiante_activo', table_name='inscripciones')
    
    # Eliminar índices específicos
    op.drop_index('ix_inscripciones_en_lista_espera', table_name='inscripciones')
    op.drop_index('ix_inscripciones_esta_aprobada', table_name='inscripciones')
    op.drop_index('ix_inscripciones_esta_pagado', table_name='inscripciones')
    
    # Eliminar índices simples
    op.drop_index('ix_inscripciones_fecha_creacion', table_name='inscripciones')
    op.drop_index('ix_inscripciones_activo', table_name='inscripciones')
    op.drop_index('ix_inscripciones_tipo_inscripcion', table_name='inscripciones')
    op.drop_index('ix_inscripciones_estado', table_name='inscripciones')
    op.drop_index('ix_inscripciones_codigo_inscripcion', table_name='inscripciones')
    op.drop_index('ix_inscripciones_programa_id', table_name='inscripciones')
    op.drop_index('ix_inscripciones_periodo_academico_id', table_name='inscripciones')
    op.drop_index('ix_inscripciones_grupo_id', table_name='inscripciones')
    op.drop_index('ix_inscripciones_estudiante_id', table_name='inscripciones')
    op.drop_index('ix_inscripciones_id', table_name='inscripciones')
    
    # Eliminar tabla
    op.drop_table('inscripciones')
    
    # Nota: No eliminamos los ENUMs porque pueden estar en uso en otras tablas
    # Si deseas eliminarlos, descomenta las siguientes líneas:
    # op.execute('DROP TYPE IF EXISTS forma_pago')
    # op.execute('DROP TYPE IF EXISTS motivo_retiro')
    # op.execute('DROP TYPE IF EXISTS motivo_rechazo')
    # op.execute('DROP TYPE IF EXISTS tipo_inscripcion')
    # op.execute('DROP TYPE IF EXISTS estado_inscripcion')
