"""add_ai_gamification_fields_to_tareas_only

Añade soporte para retroalimentación con IA (Gemini 1.5 Flash) y sistema de 
gamificación a las tablas 'tareas' y 'entregas_tareas'.

Esta migración:
- Agrega campos de clasificación (tipo, prioridad, estado) a tareas
- Agrega sistema de puntos (base, bonificación, peso) a tareas
- Agrega rúbrica JSONB estructurada a tareas
- Agrega configuración de IA (habilitación, prompts) a tareas
- Agrega retroalimentación IA JSONB completa a entregas_tareas
- Agrega metadata de archivos JSONB a entregas_tareas
- Agrega sistema de intentos y entregas tardías
- Agrega constraints de validación
- Agrega índices optimizados

Autor: Sistema Acadify
Fecha: 2025-10-31
Revision ID: 71e793236241
Revises: 92ce703a9ac9
Create Date: 2025-10-31 13:52:25.374461

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = '71e793236241'
down_revision: Union[str, Sequence[str], None] = '92ce703a9ac9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Añade campos de IA y gamificación a tareas y entregas_tareas.
    
    Esta migración es COMPLETAMENTE IDEMPOTENTE: verifica la existencia de 
    cada columna antes de agregarla usando try/except.
    """
    
    # Configuración de conexión para verificaciones
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    
    # ==============================================================================
    # TABLA: tareas
    # ==============================================================================
    print("🔄 Actualizando tabla 'tareas'...")
    
    existing_cols_tareas = {col['name'] for col in inspector.get_columns('tareas')}
    
    # ------------------------------------------------------------------------------
    # SECCIÓN 1: Campos de Clasificación
    # ------------------------------------------------------------------------------
    
    # tipo: Renombrar tipo_tarea -> tipo (si es necesario)
    if 'tipo_tarea' in existing_cols_tareas and 'tipo' not in existing_cols_tareas:
        print("  ↪ Renombrando 'tipo_tarea' a 'tipo'...")
        op.alter_column('tareas', 'tipo_tarea', new_column_name='tipo')
    elif 'tipo' not in existing_cols_tareas:
        print("  ↪ Agregando columna 'tipo'...")
        op.add_column(
            'tareas',
            sa.Column(
                'tipo',
                postgresql.ENUM(
                    'ensayo', 'proyecto', 'ejercicios', 'investigacion',
                    'presentacion', 'laboratorio', 'lectura', 'examen', 'otro',
                    name='tipo_tarea',
                    create_type=False
                ),
                server_default='ejercicios',
                nullable=False,
                comment='Tipo de tarea: ensayo, proyecto, ejercicios, etc.'
            )
        )
    
    # prioridad: Ya existe, solo verificar
    if 'prioridad' not in existing_cols_tareas:
        print("  ↪ Agregando columna 'prioridad'...")
        op.add_column(
            'tareas',
            sa.Column(
                'prioridad',
                postgresql.ENUM(
                    'baja', 'media', 'alta', 'urgente',
                    name='prioridad_tarea',
                    create_type=False
                ),
                server_default='media',
                nullable=False,
                comment='Nivel de prioridad de la tarea'
            )
        )
    
    # estado: Ya existe, solo verificar
    if 'estado' not in existing_cols_tareas:
        print("  ↪ Agregando columna 'estado'...")
        op.add_column(
            'tareas',
            sa.Column(
                'estado',
                postgresql.ENUM(
                    'asignada', 'en_progreso', 'entregada', 'calificada',
                    'vencida', 'cancelada',
                    name='estado_tarea',
                    create_type=False
                ),
                server_default='asignada',
                nullable=False,
                comment='Estado actual de la tarea'
            )
        )
    
    # ------------------------------------------------------------------------------
    # SECCIÓN 2: Sistema de Gamificación (NUEVOS)
    # ------------------------------------------------------------------------------
    
    if 'puntos_base' not in existing_cols_tareas:
        print("  ↪ Agregando columna 'puntos_base'...")
        op.add_column(
            'tareas',
            sa.Column(
                'puntos_base',
                sa.Integer(),
                server_default='50',
                nullable=False,
                comment='Puntos base otorgados por completar la tarea'
            )
        )
    
    if 'puntos_bonificacion' not in existing_cols_tareas:
        print("  ↪ Agregando columna 'puntos_bonificacion'...")
        op.add_column(
            'tareas',
            sa.Column(
                'puntos_bonificacion',
                sa.Integer(),
                server_default='20',
                nullable=False,
                comment='Puntos extra por trabajo sobresaliente (>= 4.5)'
            )
        )
    
    if 'peso_calificacion' not in existing_cols_tareas:
        print("  ↪ Agregando columna 'peso_calificacion'...")
        op.add_column(
            'tareas',
            sa.Column(
                'peso_calificacion',
                sa.NUMERIC(precision=5, scale=2),
                nullable=True,
                comment='Peso en calificación final del curso (0-100%)'
            )
        )
    
    # ------------------------------------------------------------------------------
    # SECCIÓN 3: Rúbrica y Evaluación (Actualizar rubrica_id -> rubrica JSONB)
    # ------------------------------------------------------------------------------
    
    if 'rubrica' not in existing_cols_tareas:
        print("  ↪ Agregando columna 'rubrica' (JSONB)...")
        op.add_column(
            'tareas',
            sa.Column(
                'rubrica',
                postgresql.JSONB(astext_type=sa.Text()),
                nullable=True,
                comment='Criterios de evaluación: {criterios: [{nombre, peso, niveles}]}'
            )
        )
    
    if 'restricciones_archivo' not in existing_cols_tareas:
        print("  ↪ Agregando columna 'restricciones_archivo'...")
        op.add_column(
            'tareas',
            sa.Column(
                'restricciones_archivo',
                postgresql.JSONB(astext_type=sa.Text()),
                nullable=True,
                comment='Restricciones: {max_size_mb, tipos_permitidos, validaciones}'
            )
        )
    
    # ------------------------------------------------------------------------------
    # SECCIÓN 4: Configuración de IA (NUEVOS)
    # ------------------------------------------------------------------------------
    
    if 'habilitar_retroalimentacion_ia' not in existing_cols_tareas:
        print("  ↪ Agregando columna 'habilitar_retroalimentacion_ia'...")
        op.add_column(
            'tareas',
            sa.Column(
                'habilitar_retroalimentacion_ia',
                sa.BOOLEAN(),
                server_default='true',
                nullable=False,
                comment='Si debe generarse retroalimentación automática con IA'
            )
        )
    
    if 'prompt_ia_personalizado' not in existing_cols_tareas:
        print("  ↪ Agregando columna 'prompt_ia_personalizado'...")
        op.add_column(
            'tareas',
            sa.Column(
                'prompt_ia_personalizado',
                sa.TEXT(),
                nullable=True,
                comment='Instrucciones personalizadas para guiar el análisis de la IA'
            )
        )
    
    # ------------------------------------------------------------------------------
    # SECCIÓN 5: Metadata (fecha_modificacion ya existe como fecha_actualizacion)
    # ------------------------------------------------------------------------------
    
    if 'fecha_modificacion' not in existing_cols_tareas and 'fecha_actualizacion' not in existing_cols_tareas:
        print("  ↪ Agregando columna 'fecha_modificacion'...")
        op.add_column(
            'tareas',
            sa.Column(
                'fecha_modificacion',
                postgresql.TIMESTAMP(timezone=True),
                server_default=sa.text('now()'),
                nullable=True,
                comment='Fecha de última modificación'
            )
        )
    
    # ------------------------------------------------------------------------------
    # SECCIÓN 6: Constraints y Validaciones (Crear solo si no existen)
    # ------------------------------------------------------------------------------
    
    existing_constraints = {c['name'] for c in inspector.get_check_constraints('tareas')}
    
    if 'chk_tareas_puntos_base_positivos' not in existing_constraints:
        print("  ↪ Creando constraint 'chk_tareas_puntos_base_positivos'...")
        op.create_check_constraint(
            'chk_tareas_puntos_base_positivos',
            'tareas',
            'puntos_base >= 0'
        )
    
    if 'chk_tareas_puntos_bonificacion_positivos' not in existing_constraints:
        print("  ↪ Creando constraint 'chk_tareas_puntos_bonificacion_positivos'...")
        op.create_check_constraint(
            'chk_tareas_puntos_bonificacion_positivos',
            'tareas',
            'puntos_bonificacion >= 0'
        )
    
    if 'chk_tareas_peso_calificacion_valido' not in existing_constraints:
        print("  ↪ Creando constraint 'chk_tareas_peso_calificacion_valido'...")
        op.create_check_constraint(
            'chk_tareas_peso_calificacion_valido',
            'tareas',
            'peso_calificacion IS NULL OR (peso_calificacion >= 0 AND peso_calificacion <= 100)'
        )
    
    # ------------------------------------------------------------------------------
    # SECCIÓN 7: Índices Optimizados (Crear solo si no existen)
    # ------------------------------------------------------------------------------
    
    existing_indexes = {idx['name'] for idx in inspector.get_indexes('tareas')}
    
    if 'ix_tareas_estado' not in existing_indexes:
        print("  ↪ Creando índice 'ix_tareas_estado'...")
        op.create_index('ix_tareas_estado', 'tareas', ['estado'])
    
    print("✅ Tabla 'tareas' actualizada exitosamente")
    
    # ==============================================================================
    # TABLA: entregas_tareas
    # ==============================================================================
    print("🔄 Actualizando tabla 'entregas_tareas'...")
    
    existing_cols_entregas = {col['name'] for col in inspector.get_columns('entregas_tareas')}
    
    # ------------------------------------------------------------------------------
    # SECCIÓN 1: Estado y Control
    # ------------------------------------------------------------------------------
    
    # estado: Ya existe, solo verificar
    if 'estado' not in existing_cols_entregas:
        print("  ↪ Agregando columna 'estado'...")
        op.add_column(
            'entregas_tareas',
            sa.Column(
                'estado',
                postgresql.ENUM(
                    'borrador', 'entregada', 'calificada', 'devuelta', 'reentregada',
                    name='estado_entrega',
                    create_type=False
                ),
                server_default='entregada',
                nullable=False,
                comment='Estado: borrador, entregada, calificada, devuelta, reentregada'
            )
        )
    
    if 'intentos' not in existing_cols_entregas:
        print("  ↪ Agregando columna 'intentos'...")
        op.add_column(
            'entregas_tareas',
            sa.Column(
                'intentos',
                sa.Integer(),
                server_default='1',
                nullable=False,
                comment='Número de intentos de entrega realizados'
            )
        )
    
    if 'es_tardia' not in existing_cols_entregas:
        print("  ↪ Agregando columna 'es_tardia'...")
        op.add_column(
            'entregas_tareas',
            sa.Column(
                'es_tardia',
                sa.Boolean(),
                server_default='false',
                nullable=False,
                comment='True si fue entregada después de la fecha límite'
            )
        )
    
    # ------------------------------------------------------------------------------
    # SECCIÓN 2: Metadata de Archivo (NUEVO)
    # ------------------------------------------------------------------------------
    
    if 'archivo_metadata' not in existing_cols_entregas:
        print("  ↪ Agregando columna 'archivo_metadata'...")
        op.add_column(
            'entregas_tareas',
            sa.Column(
                'archivo_metadata',
                postgresql.JSONB(astext_type=sa.Text()),
                nullable=True,
                comment='Metadata: {nombre, tamaño_bytes, mime_type, hash_md5, lineas_codigo}'
            )
        )
    
    # ------------------------------------------------------------------------------
    # SECCIÓN 3: Calificaciones (NUEVO)
    # ------------------------------------------------------------------------------
    
    if 'calificacion_preliminar_ia' not in existing_cols_entregas:
        print("  ↪ Agregando columna 'calificacion_preliminar_ia'...")
        op.add_column(
            'entregas_tareas',
            sa.Column(
                'calificacion_preliminar_ia',
                sa.NUMERIC(precision=3, scale=1),
                nullable=True,
                comment='Calificación sugerida por IA (0.0 - 5.0)'
            )
        )
    
    # ------------------------------------------------------------------------------
    # SECCIÓN 4: Retroalimentación (NUEVOS)
    # ------------------------------------------------------------------------------
    
    if 'retroalimentacion_docente' not in existing_cols_entregas:
        print("  ↪ Agregando columna 'retroalimentacion_docente'...")
        op.add_column(
            'entregas_tareas',
            sa.Column(
                'retroalimentacion_docente',
                sa.TEXT(),
                nullable=True,
                comment='Retroalimentación escrita manualmente por el docente'
            )
        )
    
    if 'retroalimentacion_ia' not in existing_cols_entregas:
        print("  ↪ Agregando columna 'retroalimentacion_ia'...")
        op.add_column(
            'entregas_tareas',
            sa.Column(
                'retroalimentacion_ia',
                postgresql.JSONB(astext_type=sa.Text()),
                nullable=True,
                comment='Retroalimentación IA: {analisis, fortalezas, areas_mejora, sugerencias}'
            )
        )
    
    if 'comentarios_privados' not in existing_cols_entregas:
        print("  ↪ Agregando columna 'comentarios_privados'...")
        op.add_column(
            'entregas_tareas',
            sa.Column(
                'comentarios_privados',
                sa.TEXT(),
                nullable=True,
                comment='Notas privadas del docente (no visibles para el estudiante)'
            )
        )
    
    # ------------------------------------------------------------------------------
    # SECCIÓN 5: Gamificación (NUEVO)
    # ------------------------------------------------------------------------------
    
    if 'puntos_otorgados' not in existing_cols_entregas:
        print("  ↪ Agregando columna 'puntos_otorgados'...")
        op.add_column(
            'entregas_tareas',
            sa.Column(
                'puntos_otorgados',
                sa.Integer(),
                nullable=True,
                comment='Puntos de gamificación otorgados (base + bonificación - penalización)'
            )
        )
    
    # ------------------------------------------------------------------------------
    # SECCIÓN 6: Metadata (fecha_modificacion)
    # ------------------------------------------------------------------------------
    
    if 'fecha_modificacion' not in existing_cols_entregas and 'fecha_actualizacion' not in existing_cols_entregas:
        print("  ↪ Agregando columna 'fecha_modificacion'...")
        op.add_column(
            'entregas_tareas',
            sa.Column(
                'fecha_modificacion',
                postgresql.TIMESTAMP(timezone=True),
                server_default=sa.text('now()'),
                nullable=True,
                comment='Fecha de última modificación'
            )
        )
    
    # ------------------------------------------------------------------------------
    # SECCIÓN 7: Constraints y Validaciones (Crear solo si no existen)
    # ------------------------------------------------------------------------------
    
    existing_constraints_entregas = {c['name'] for c in inspector.get_check_constraints('entregas_tareas')}
    
    if 'chk_entregas_calificacion_ia_rango' not in existing_constraints_entregas:
        print("  ↪ Creando constraint 'chk_entregas_calificacion_ia_rango'...")
        op.create_check_constraint(
            'chk_entregas_calificacion_ia_rango',
            'entregas_tareas',
            'calificacion_preliminar_ia IS NULL OR (calificacion_preliminar_ia >= 0 AND calificacion_preliminar_ia <= 5)'
        )
    
    if 'chk_entregas_intentos_minimo' not in existing_constraints_entregas:
        print("  ↪ Creando constraint 'chk_entregas_intentos_minimo'...")
        op.create_check_constraint(
            'chk_entregas_intentos_minimo',
            'entregas_tareas',
            'intentos >= 1'
        )
    
    if 'chk_entregas_puntos_positivos' not in existing_constraints_entregas:
        print("  ↪ Creando constraint 'chk_entregas_puntos_positivos'...")
        op.create_check_constraint(
            'chk_entregas_puntos_positivos',
            'entregas_tareas',
            'puntos_otorgados IS NULL OR puntos_otorgados >= 0'
        )
    
    # ------------------------------------------------------------------------------
    # SECCIÓN 8: Índices Optimizados (Crear solo si no existen)
    # ------------------------------------------------------------------------------
    
    existing_indexes_entregas = {idx['name'] for idx in inspector.get_indexes('entregas_tareas')}
    
    if 'ix_entregas_tareas_estado' not in existing_indexes_entregas:
        print("  ↪ Creando índice 'ix_entregas_tareas_estado'...")
        op.create_index('ix_entregas_tareas_estado', 'entregas_tareas', ['estado'])
    
    print("✅ Tabla 'entregas_tareas' actualizada exitosamente")
    print("✅ Migración completada exitosamente")


def downgrade() -> None:
    """
    Revierte los cambios de IA y gamificación.
    
    Esta migración es IDEMPOTENTE: verifica la existencia de índices, 
    constraints y columnas antes de eliminarlos.
    """
    
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    
    # ==============================================================================
    # TABLA: entregas_tareas (eliminar primero por dependencias FK)
    # ==============================================================================
    print("🔄 Revirtiendo cambios en 'entregas_tareas'...")
    
    existing_cols_entregas = {col['name'] for col in inspector.get_columns('entregas_tareas')}
    existing_indexes_entregas = {idx['name'] for idx in inspector.get_indexes('entregas_tareas')}
    existing_constraints_entregas = {c['name'] for c in inspector.get_check_constraints('entregas_tareas')}
    
    # Índices
    if 'ix_entregas_tareas_estado' in existing_indexes_entregas:
        print("  ↪ Eliminando índice 'ix_entregas_tareas_estado'...")
        op.drop_index('ix_entregas_tareas_estado', table_name='entregas_tareas')
    
    # Constraints
    if 'chk_entregas_puntos_positivos' in existing_constraints_entregas:
        print("  ↪ Eliminando constraint 'chk_entregas_puntos_positivos'...")
        op.drop_constraint('chk_entregas_puntos_positivos', 'entregas_tareas', type_='check')
    
    if 'chk_entregas_intentos_minimo' in existing_constraints_entregas:
        print("  ↪ Eliminando constraint 'chk_entregas_intentos_minimo'...")
        op.drop_constraint('chk_entregas_intentos_minimo', 'entregas_tareas', type_='check')
    
    if 'chk_entregas_calificacion_ia_rango' in existing_constraints_entregas:
        print("  ↪ Eliminando constraint 'chk_entregas_calificacion_ia_rango'...")
        op.drop_constraint('chk_entregas_calificacion_ia_rango', 'entregas_tareas', type_='check')
    
    # Columnas (solo las que agregamos)
    if 'fecha_modificacion' in existing_cols_entregas:
        print("  ↪ Eliminando columna 'fecha_modificacion'...")
        op.drop_column('entregas_tareas', 'fecha_modificacion')
    
    if 'puntos_otorgados' in existing_cols_entregas:
        print("  ↪ Eliminando columna 'puntos_otorgados'...")
        op.drop_column('entregas_tareas', 'puntos_otorgados')
    
    if 'comentarios_privados' in existing_cols_entregas:
        print("  ↪ Eliminando columna 'comentarios_privados'...")
        op.drop_column('entregas_tareas', 'comentarios_privados')
    
    if 'retroalimentacion_ia' in existing_cols_entregas:
        print("  ↪ Eliminando columna 'retroalimentacion_ia'...")
        op.drop_column('entregas_tareas', 'retroalimentacion_ia')
    
    if 'retroalimentacion_docente' in existing_cols_entregas:
        print("  ↪ Eliminando columna 'retroalimentacion_docente'...")
        op.drop_column('entregas_tareas', 'retroalimentacion_docente')
    
    if 'calificacion_preliminar_ia' in existing_cols_entregas:
        print("  ↪ Eliminando columna 'calificacion_preliminar_ia'...")
        op.drop_column('entregas_tareas', 'calificacion_preliminar_ia')
    
    if 'archivo_metadata' in existing_cols_entregas:
        print("  ↪ Eliminando columna 'archivo_metadata'...")
        op.drop_column('entregas_tareas', 'archivo_metadata')
    
    if 'es_tardia' in existing_cols_entregas:
        print("  ↪ Eliminando columna 'es_tardia'...")
        op.drop_column('entregas_tareas', 'es_tardia')
    
    if 'intentos' in existing_cols_entregas:
        print("  ↪ Eliminando columna 'intentos'...")
        op.drop_column('entregas_tareas', 'intentos')
    
    # estado: NO eliminar (ya existía antes)
    
    print("✅ Tabla 'entregas_tareas' revertida exitosamente")
    
    # ==============================================================================
    # TABLA: tareas
    # ==============================================================================
    print("🔄 Revirtiendo cambios en 'tareas'...")
    
    existing_cols_tareas = {col['name'] for col in inspector.get_columns('tareas')}
    existing_indexes_tareas = {idx['name'] for idx in inspector.get_indexes('tareas')}
    existing_constraints_tareas = {c['name'] for c in inspector.get_check_constraints('tareas')}
    
    # Índices
    if 'ix_tareas_estado' in existing_indexes_tareas:
        print("  ↪ Eliminando índice 'ix_tareas_estado'...")
        op.drop_index('ix_tareas_estado', table_name='tareas')
    
    # Constraints
    if 'chk_tareas_peso_calificacion_valido' in existing_constraints_tareas:
        print("  ↪ Eliminando constraint 'chk_tareas_peso_calificacion_valido'...")
        op.drop_constraint('chk_tareas_peso_calificacion_valido', 'tareas', type_='check')
    
    if 'chk_tareas_puntos_bonificacion_positivos' in existing_constraints_tareas:
        print("  ↪ Eliminando constraint 'chk_tareas_puntos_bonificacion_positivos'...")
        op.drop_constraint('chk_tareas_puntos_bonificacion_positivos', 'tareas', type_='check')
    
    if 'chk_tareas_puntos_base_positivos' in existing_constraints_tareas:
        print("  ↪ Eliminando constraint 'chk_tareas_puntos_base_positivos'...")
        op.drop_constraint('chk_tareas_puntos_base_positivos', 'tareas', type_='check')
    
    # Columnas (solo las que agregamos)
    if 'fecha_modificacion' in existing_cols_tareas:
        print("  ↪ Eliminando columna 'fecha_modificacion'...")
        op.drop_column('tareas', 'fecha_modificacion')
    
    if 'prompt_ia_personalizado' in existing_cols_tareas:
        print("  ↪ Eliminando columna 'prompt_ia_personalizado'...")
        op.drop_column('tareas', 'prompt_ia_personalizado')
    
    if 'habilitar_retroalimentacion_ia' in existing_cols_tareas:
        print("  ↪ Eliminando columna 'habilitar_retroalimentacion_ia'...")
        op.drop_column('tareas', 'habilitar_retroalimentacion_ia')
    
    if 'restricciones_archivo' in existing_cols_tareas:
        print("  ↪ Eliminando columna 'restricciones_archivo'...")
        op.drop_column('tareas', 'restricciones_archivo')
    
    if 'rubrica' in existing_cols_tareas:
        print("  ↪ Eliminando columna 'rubrica'...")
        op.drop_column('tareas', 'rubrica')
    
    if 'peso_calificacion' in existing_cols_tareas:
        print("  ↪ Eliminando columna 'peso_calificacion'...")
        op.drop_column('tareas', 'peso_calificacion')
    
    if 'puntos_bonificacion' in existing_cols_tareas:
        print("  ↪ Eliminando columna 'puntos_bonificacion'...")
        op.drop_column('tareas', 'puntos_bonificacion')
    
    if 'puntos_base' in existing_cols_tareas:
        print("  ↪ Eliminando columna 'puntos_base'...")
        op.drop_column('tareas', 'puntos_base')
    
    # estado, prioridad, tipo: NO eliminar (ya existían antes)
    
    # Si renombramos tipo_tarea -> tipo, revertir
    if 'tipo' in existing_cols_tareas and 'tipo_tarea' not in existing_cols_tareas:
        print("  ↪ Revirtiendo renombre: 'tipo' a 'tipo_tarea'...")
        op.alter_column('tareas', 'tipo', new_column_name='tipo_tarea')
    
    print("✅ Tabla 'tareas' revertida exitosamente")
    print("✅ Downgrade completado exitosamente")
