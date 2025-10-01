"""Add core evaluation tables - examenes and preguntas

Revision ID: 291ba6082c35
Revises: d886690834dd
Create Date: 2025-09-26 18:53:32.992740

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '291ba6082c35'
down_revision: Union[str, Sequence[str], None] = 'd886690834dd'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create examenes table
    op.create_table(
        'examenes',
        sa.Column('examen_id', sa.String(), nullable=False),
        sa.Column('titulo', sa.String(200), nullable=False),
        sa.Column('descripcion', sa.Text(), nullable=True),
        sa.Column('tipo_examen', sa.String(50), nullable=False, server_default='evaluacion'),
        sa.Column('estado_examen', sa.String(50), nullable=False, server_default='borrador'),
        sa.Column('tiempo_limite', sa.Integer(), nullable=False, server_default='60'),
        sa.Column('fecha_inicio', sa.DateTime(timezone=True), nullable=True),
        sa.Column('fecha_limite', sa.DateTime(timezone=True), nullable=True),
        sa.Column('intentos_permitidos', sa.Integer(), nullable=True, server_default='1'),
        sa.Column('requiere_contraseña', sa.Boolean(), nullable=True, server_default='false'),
        sa.Column('contraseña_acceso', sa.String(100), nullable=True),
        sa.Column('randomizar_preguntas', sa.Boolean(), nullable=True, server_default='false'),
        sa.Column('mostrar_resultados_inmediatos', sa.Boolean(), nullable=True, server_default='true'),
        sa.Column('permitir_revision', sa.Boolean(), nullable=True, server_default='true'),
        sa.Column('mostrar_respuestas_correctas', sa.Boolean(), nullable=True, server_default='true'),
        sa.Column('modo_pantalla_completa', sa.Boolean(), nullable=True, server_default='false'),
        sa.Column('bloquear_navegacion', sa.Boolean(), nullable=True, server_default='false'),
        sa.Column('detectar_cambio_pestana', sa.Boolean(), nullable=True, server_default='false'),
        sa.Column('tiempo_maximo_inactividad', sa.Integer(), nullable=True, server_default='300'),
        sa.Column('puntuacion_total', sa.Float(), nullable=False, server_default='100.0'),
        sa.Column('puntuacion_minima_aprobacion', sa.Float(), nullable=True, server_default='60.0'),
        sa.Column('calificacion_automatica', sa.Boolean(), nullable=True, server_default='true'),
        sa.Column('curso_id', sa.String(), nullable=True),
        sa.Column('grupo_id', sa.String(), nullable=True),
        sa.Column('creado_por', sa.String(), nullable=False),
        sa.Column('fecha_creacion', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('fecha_actualizacion', sa.DateTime(timezone=True), nullable=True),
        sa.Column('configuracion_avanzada', sa.JSON(), nullable=True),
        sa.Column('instrucciones', sa.Text(), nullable=True),
        sa.Column('total_preguntas', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('total_intentos', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('promedio_calificacion', sa.Float(), nullable=True),
        sa.PrimaryKeyConstraint('examen_id')
    )

    # Create preguntas_examen table
    op.create_table(
        'preguntas_examen',
        sa.Column('pregunta_id', sa.String(), nullable=False),
        sa.Column('examen_id', sa.String(), nullable=False),
        sa.Column('titulo', sa.Text(), nullable=False),
        sa.Column('descripcion', sa.Text(), nullable=True),
        sa.Column('tipo_pregunta', sa.String(50), nullable=False),
        sa.Column('orden', sa.Integer(), nullable=False),
        sa.Column('puntuacion', sa.Float(), nullable=False, server_default='1.0'),
        sa.Column('es_obligatoria', sa.Boolean(), nullable=True, server_default='true'),
        sa.Column('tiempo_limite_segundos', sa.Integer(), nullable=True),
        sa.Column('opciones_respuesta', sa.JSON(), nullable=True),
        sa.Column('respuesta_correcta', sa.JSON(), nullable=True),
        sa.Column('explicacion', sa.Text(), nullable=True),
        sa.Column('puntos_respuesta_parcial', sa.Boolean(), nullable=True, server_default='false'),
        sa.Column('dificultad', sa.String(50), nullable=True, server_default='medio'),
        sa.Column('imagen_url', sa.String(500), nullable=True),
        sa.Column('audio_url', sa.String(500), nullable=True),
        sa.Column('video_url', sa.String(500), nullable=True),
        sa.Column('archivos_adjuntos', sa.JSON(), nullable=True),
        sa.Column('banco_pregunta_id', sa.String(), nullable=True),
        sa.Column('tags', sa.JSON(), nullable=True),
        sa.Column('fecha_creacion', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('fecha_actualizacion', sa.DateTime(timezone=True), nullable=True),
        sa.Column('veces_utilizada', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('promedio_aciertos', sa.Float(), nullable=True),
        sa.Column('tiempo_promedio_respuesta', sa.Float(), nullable=True),
        sa.PrimaryKeyConstraint('pregunta_id'),
        sa.ForeignKeyConstraint(['examen_id'], ['examenes.examen_id'], ondelete='CASCADE')
    )

    # Create banco_preguntas table
    op.create_table(
        'banco_preguntas',
        sa.Column('pregunta_id', sa.String(), nullable=False),
        sa.Column('titulo', sa.Text(), nullable=False),
        sa.Column('descripcion', sa.Text(), nullable=True),
        sa.Column('tipo_pregunta', sa.String(50), nullable=False),
        sa.Column('dificultad', sa.String(50), nullable=True, server_default='medio'),
        sa.Column('materia', sa.String(100), nullable=True),
        sa.Column('tema', sa.String(200), nullable=True),
        sa.Column('subtema', sa.String(200), nullable=True),
        sa.Column('opciones_respuesta', sa.JSON(), nullable=True),
        sa.Column('respuesta_correcta', sa.JSON(), nullable=True),
        sa.Column('explicacion', sa.Text(), nullable=True),
        sa.Column('imagen_url', sa.String(500), nullable=True),
        sa.Column('audio_url', sa.String(500), nullable=True),
        sa.Column('video_url', sa.String(500), nullable=True),
        sa.Column('archivos_adjuntos', sa.JSON(), nullable=True),
        sa.Column('creado_por', sa.String(), nullable=False),
        sa.Column('institucion_id', sa.String(), nullable=True),
        sa.Column('es_publica', sa.Boolean(), nullable=True, server_default='false'),
        sa.Column('tags', sa.JSON(), nullable=True),
        sa.Column('categoria', sa.String(100), nullable=True),
        sa.Column('nivel_educativo', sa.String(50), nullable=True),
        sa.Column('puntuacion_sugerida', sa.Float(), nullable=True, server_default='1.0'),
        sa.Column('tiempo_estimado_segundos', sa.Integer(), nullable=True),
        sa.Column('veces_utilizada', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('promedio_aciertos', sa.Float(), nullable=True),
        sa.Column('calificacion_dificultad', sa.Float(), nullable=True),
        sa.Column('fecha_creacion', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('fecha_actualizacion', sa.DateTime(timezone=True), nullable=True),
        sa.Column('ultima_vez_utilizada', sa.DateTime(timezone=True), nullable=True),
        sa.Column('revisado_por', sa.String(), nullable=True),
        sa.Column('fecha_revision', sa.DateTime(timezone=True), nullable=True),
        sa.Column('estado_revision', sa.String(50), nullable=True, server_default='pendiente'),
        sa.Column('comentarios_revision', sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint('pregunta_id')
    )

    # Create intentos_examen table  
    op.create_table(
        'intentos_examen',
        sa.Column('intento_id', sa.String(), nullable=False),
        sa.Column('examen_id', sa.String(), nullable=False),
        sa.Column('estudiante_id', sa.String(), nullable=False),
        sa.Column('numero_intento', sa.Integer(), nullable=False),
        sa.Column('estado_intento', sa.String(50), nullable=False, server_default='en_progreso'),
        sa.Column('fecha_inicio', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('fecha_fin', sa.DateTime(timezone=True), nullable=True),
        sa.Column('tiempo_total_segundos', sa.Integer(), nullable=True),
        sa.Column('tiempo_limite_vencido', sa.Boolean(), nullable=True, server_default='false'),
        sa.Column('puntuacion_obtenida', sa.Float(), nullable=True, server_default='0.0'),
        sa.Column('puntuacion_maxima', sa.Float(), nullable=False),
        sa.Column('porcentaje', sa.Float(), nullable=True),
        sa.Column('aprobado', sa.Boolean(), nullable=True),
        sa.Column('preguntas_respondidas', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('total_preguntas', sa.Integer(), nullable=False),
        sa.Column('pregunta_actual', sa.Integer(), nullable=True, server_default='1'),
        sa.Column('cambios_pestana_detectados', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('tiempo_inactividad_total', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('ip_address', sa.String(45), nullable=True),
        sa.Column('user_agent', sa.Text(), nullable=True),
        sa.Column('eventos_sospechosos', sa.JSON(), nullable=True),
        sa.Column('orden_preguntas', sa.JSON(), nullable=True),
        sa.Column('configuracion_intento', sa.JSON(), nullable=True),
        sa.Column('finalizado_por', sa.String(50), nullable=True, server_default='estudiante'),
        sa.Column('comentarios_finalizacion', sa.Text(), nullable=True),
        sa.Column('fecha_revision', sa.DateTime(timezone=True), nullable=True),
        sa.Column('revisado_por', sa.String(), nullable=True),
        sa.Column('comentarios_profesor', sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint('intento_id'),
        sa.ForeignKeyConstraint(['examen_id'], ['examenes.examen_id'], ondelete='CASCADE')
    )

    # Create respuestas_estudiante table
    op.create_table(
        'respuestas_estudiante',
        sa.Column('respuesta_id', sa.String(), nullable=False),
        sa.Column('intento_id', sa.String(), nullable=False),
        sa.Column('pregunta_id', sa.String(), nullable=False),
        sa.Column('respuesta_estudiante', sa.JSON(), nullable=True),
        sa.Column('texto_respuesta', sa.Text(), nullable=True),
        sa.Column('puntuacion_obtenida', sa.Float(), nullable=True, server_default='0.0'),
        sa.Column('puntuacion_maxima', sa.Float(), nullable=False),
        sa.Column('es_correcta', sa.Boolean(), nullable=True),
        sa.Column('calificada_automaticamente', sa.Boolean(), nullable=True, server_default='false'),
        sa.Column('fecha_respuesta', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('tiempo_empleado_segundos', sa.Integer(), nullable=True),
        sa.Column('fecha_ultima_modificacion', sa.DateTime(timezone=True), nullable=True),
        sa.Column('historial_respuestas', sa.JSON(), nullable=True),
        sa.Column('numero_modificaciones', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('feedback_automatico', sa.Text(), nullable=True),
        sa.Column('feedback_profesor', sa.Text(), nullable=True),
        sa.Column('mostrar_respuesta_correcta', sa.Boolean(), nullable=True, server_default='false'),
        sa.Column('palabras_clave_encontradas', sa.JSON(), nullable=True),
        sa.Column('similitud_respuesta_correcta', sa.Float(), nullable=True),
        sa.Column('version_pregunta', sa.String(50), nullable=True),
        sa.Column('metadata_respuesta', sa.JSON(), nullable=True),
        sa.PrimaryKeyConstraint('respuesta_id'),
        sa.ForeignKeyConstraint(['intento_id'], ['intentos_examen.intento_id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['pregunta_id'], ['preguntas_examen.pregunta_id'], ondelete='CASCADE')
    )

    # Create configuracion_evaluaciones table
    op.create_table(
        'configuracion_evaluaciones',
        sa.Column('config_id', sa.String(), nullable=False),
        sa.Column('tiempo_gracia_segundos', sa.Integer(), nullable=True, server_default='300'),
        sa.Column('maximo_intentos_globales', sa.Integer(), nullable=True, server_default='5'),
        sa.Column('tiempo_minimo_entre_intentos', sa.Integer(), nullable=True, server_default='3600'),
        sa.Column('max_cambios_pestana_permitidos', sa.Integer(), nullable=True, server_default='5'),
        sa.Column('tiempo_max_inactividad_global', sa.Integer(), nullable=True, server_default='1800'),
        sa.Column('habilitar_deteccion_copia_texto', sa.Boolean(), nullable=True, server_default='true'),
        sa.Column('habilitar_deteccion_pantalla_completa', sa.Boolean(), nullable=True, server_default='true'),
        sa.Column('algoritmo_calificacion_ensayos', sa.String(100), nullable=True, server_default='keyword_matching'),
        sa.Column('umbral_similitud_plagio', sa.Float(), nullable=True, server_default='0.8'),
        sa.Column('habilitar_feedback_automatico', sa.Boolean(), nullable=True, server_default='true'),
        sa.Column('notificar_intento_finalizado', sa.Boolean(), nullable=True, server_default='true'),
        sa.Column('notificar_resultado_disponible', sa.Boolean(), nullable=True, server_default='true'),
        sa.Column('notificar_tiempo_restante', sa.Boolean(), nullable=True, server_default='true'),
        sa.Column('tiempo_notificacion_previa_minutos', sa.Integer(), nullable=True, server_default='10'),
        sa.Column('guardar_progreso_cada_segundos', sa.Integer(), nullable=True, server_default='30'),
        sa.Column('habilitar_recuperacion_sesion', sa.Boolean(), nullable=True, server_default='true'),
        sa.Column('tiempo_expiracion_backup_horas', sa.Integer(), nullable=True, server_default='72'),
        sa.Column('institucion_id', sa.String(), nullable=True),
        sa.Column('aplicar_globalmente', sa.Boolean(), nullable=True, server_default='true'),
        sa.Column('creado_por', sa.String(), nullable=False),
        sa.Column('fecha_creacion', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('fecha_actualizacion', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('config_id')
    )

    # Create estadisticas_examen table
    op.create_table(
        'estadisticas_examen',
        sa.Column('estadistica_id', sa.String(), nullable=False),
        sa.Column('examen_id', sa.String(), nullable=False),
        sa.Column('total_estudiantes_asignados', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('total_intentos_realizados', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('total_intentos_finalizados', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('total_aprobados', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('total_reprobados', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('puntuacion_promedio', sa.Float(), nullable=True, server_default='0.0'),
        sa.Column('puntuacion_mediana', sa.Float(), nullable=True, server_default='0.0'),
        sa.Column('puntuacion_maxima_obtenida', sa.Float(), nullable=True, server_default='0.0'),
        sa.Column('puntuacion_minima_obtenida', sa.Float(), nullable=True, server_default='0.0'),
        sa.Column('desviacion_estandar', sa.Float(), nullable=True, server_default='0.0'),
        sa.Column('tiempo_promedio_minutos', sa.Float(), nullable=True, server_default='0.0'),
        sa.Column('tiempo_maximo_empleado', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('tiempo_minimo_empleado', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('estadisticas_preguntas', sa.JSON(), nullable=True),
        sa.Column('preguntas_mas_dificiles', sa.JSON(), nullable=True),
        sa.Column('preguntas_mas_faciles', sa.JSON(), nullable=True),
        sa.Column('patrones_abandono', sa.JSON(), nullable=True),
        sa.Column('tiempo_por_pregunta', sa.JSON(), nullable=True),
        sa.Column('fecha_calculo', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('fecha_ultima_actualizacion', sa.DateTime(timezone=True), nullable=True),
        sa.Column('incluir_intentos_incompletos', sa.Boolean(), nullable=True, server_default='false'),
        sa.Column('periodo_calculo', sa.String(50), nullable=True, server_default='completo'),
        sa.PrimaryKeyConstraint('estadistica_id'),
        sa.ForeignKeyConstraint(['examen_id'], ['examenes.examen_id'], ondelete='CASCADE')
    )

    # Create eventos_anti_trampa table
    op.create_table(
        'eventos_anti_trampa',
        sa.Column('evento_id', sa.String(), nullable=False),
        sa.Column('intento_id', sa.String(), nullable=False),
        sa.Column('tipo_evento', sa.String(50), nullable=False),
        sa.Column('descripcion', sa.Text(), nullable=True),
        sa.Column('datos_evento', sa.JSON(), nullable=True),
        sa.Column('ip_address', sa.String(45), nullable=True),
        sa.Column('user_agent', sa.Text(), nullable=True),
        sa.Column('timestamp', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('es_sospechoso', sa.Boolean(), nullable=True, server_default='false'),
        sa.Column('nivel_riesgo', sa.String(20), nullable=True, server_default='bajo'),
        sa.Column('requiere_revision', sa.Boolean(), nullable=True, server_default='false'),
        sa.PrimaryKeyConstraint('evento_id'),
        sa.ForeignKeyConstraint(['intento_id'], ['intentos_examen.intento_id'], ondelete='CASCADE')
    )

    # Add FK relationship from banco_preguntas to preguntas_examen
    op.create_foreign_key(
        'fk_preguntas_examen_banco_pregunta_id',
        'preguntas_examen',
        'banco_preguntas',
        ['banco_pregunta_id'],
        ['pregunta_id']
    )


def downgrade() -> None:
    """Downgrade schema."""
    # Drop tables in reverse order (due to foreign keys)
    op.drop_table('eventos_anti_trampa')
    op.drop_table('estadisticas_examen')
    op.drop_table('configuracion_evaluaciones')
    op.drop_table('respuestas_estudiante')
    op.drop_table('intentos_examen')
    op.drop_table('preguntas_examen')
    op.drop_table('banco_preguntas')
    op.drop_table('examenes')
