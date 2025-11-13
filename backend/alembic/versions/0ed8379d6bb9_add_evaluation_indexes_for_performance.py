"""add_evaluation_indexes_for_performance

Revision ID: 0ed8379d6bb9
Revises: smart_expand_eval_system
Create Date: 2025-10-31 19:15:47.391007

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0ed8379d6bb9'
down_revision: Union[str, Sequence[str], None] = 'smart_expand_eval_system'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create indexes for better query performance"""
    
    print("\n" + "="*80)
    print("🚀 CREANDO ÍNDICES PARA OPTIMIZACIÓN DE RENDIMIENTO")
    print("="*80 + "\n")
    
    # ==================== EVALUACIONES ====================
    print("📊 Índices para evaluaciones...")
    
    # Búsquedas frecuentes
    op.create_index('idx_evaluaciones_curso_id', 'evaluaciones', ['curso_id'])
    op.create_index('idx_evaluaciones_grupo_id', 'evaluaciones', ['grupo_id'])
    op.create_index('idx_evaluaciones_creador_id', 'evaluaciones', ['creador_id'])
    
    # Filtros comunes
    op.create_index('idx_evaluaciones_estado', 'evaluaciones', ['estado_examen'])
    op.create_index('idx_evaluaciones_tipo', 'evaluaciones', ['tipo_examen'])
    op.create_index('idx_evaluaciones_visibilidad', 'evaluaciones', ['visibilidad'])
    
    # Índices compuestos para queries comunes
    op.create_index('idx_evaluaciones_curso_estado', 'evaluaciones', ['curso_id', 'estado_examen'])
    op.create_index('idx_evaluaciones_fecha_inicio', 'evaluaciones', ['fecha_inicio'])
    op.create_index('idx_evaluaciones_fecha_limite', 'evaluaciones', ['fecha_limite'])
    
    # Gamificación
    op.create_index('idx_evaluaciones_otorga_puntos', 'evaluaciones', ['otorga_puntos'])
    
    print("✅ 10 índices creados en evaluaciones")
    
    # ==================== PREGUNTAS_EVALUACION ====================
    print("\n📝 Índices para preguntas_evaluacion...")
    
    # FK y ordenamiento
    op.create_index('idx_preguntas_evaluacion_id', 'preguntas_evaluacion', ['evaluacion_id'])
    op.create_index('idx_preguntas_orden', 'preguntas_evaluacion', ['evaluacion_id', 'orden'])
    
    # Búsquedas por tipo
    op.create_index('idx_preguntas_tipo', 'preguntas_evaluacion', ['tipo_pregunta'])
    op.create_index('idx_preguntas_dificultad', 'preguntas_evaluacion', ['dificultad'])
    
    # Banco de preguntas
    op.create_index('idx_preguntas_banco_id', 'preguntas_evaluacion', ['banco_pregunta_id'])
    
    print("✅ 5 índices creados en preguntas_evaluacion")
    
    # ==================== INTENTOS_EVALUACION ====================
    print("\n🎯 Índices para intentos_evaluacion...")
    
    # Búsquedas principales
    op.create_index('idx_intentos_evaluacion_id', 'intentos_evaluacion', ['evaluacion_id'])
    op.create_index('idx_intentos_estudiante_id', 'intentos_evaluacion', ['estudiante_id'])
    
    # Índice compuesto para queries frecuentes
    op.create_index('idx_intentos_eval_estudiante', 'intentos_evaluacion', ['evaluacion_id', 'estudiante_id'])
    op.create_index('idx_intentos_estudiante_estado', 'intentos_evaluacion', ['estudiante_id', 'estado_intento'])
    
    # Estado y fechas
    op.create_index('idx_intentos_estado', 'intentos_evaluacion', ['estado_intento'])
    op.create_index('idx_intentos_fecha_inicio', 'intentos_evaluacion', ['fecha_inicio'])
    op.create_index('idx_intentos_fecha_fin', 'intentos_evaluacion', ['fecha_fin'])
    
    # Anti-trampa
    op.create_index('idx_intentos_nivel_riesgo', 'intentos_evaluacion', ['nivel_riesgo'])
    op.create_index('idx_intentos_bloqueado', 'intentos_evaluacion', ['bloqueado_automaticamente'])
    
    # Gamificación y ranking
    op.create_index('idx_intentos_puntos', 'intentos_evaluacion', ['puntos_ganados'])
    op.create_index('idx_intentos_ranking', 'intentos_evaluacion', ['evaluacion_id', 'posicion_ranking'])
    
    # Evaluaciones colaborativas
    op.create_index('idx_intentos_equipo', 'intentos_evaluacion', ['equipo_id'])
    
    print("✅ 12 índices creados en intentos_evaluacion")
    
    # ==================== RESPUESTAS_ESTUDIANTE ====================
    print("\n✍️ Índices para respuestas_estudiante...")
    
    # FKs principales
    op.create_index('idx_respuestas_intento_id', 'respuestas_estudiante', ['intento_id'])
    op.create_index('idx_respuestas_pregunta_id', 'respuestas_estudiante', ['pregunta_id'])
    
    # Índice compuesto para queries frecuentes
    op.create_index('idx_respuestas_intento_pregunta', 'respuestas_estudiante', ['intento_id', 'pregunta_id'])
    
    # Calificación y revisión
    op.create_index('idx_respuestas_es_correcta', 'respuestas_estudiante', ['es_correcta'])
    op.create_index('idx_respuestas_revision_manual', 'respuestas_estudiante', ['requiere_revision_manual'])
    op.create_index('idx_respuestas_revisado_por', 'respuestas_estudiante', ['revisado_por_id'])
    
    # Detección IA/Plagio
    op.create_index('idx_respuestas_detectada_ia', 'respuestas_estudiante', ['fue_detectada_ia'])
    op.create_index('idx_respuestas_detectado_plagio', 'respuestas_estudiante', ['fue_detectado_plagio'])
    
    # Fechas
    op.create_index('idx_respuestas_fecha', 'respuestas_estudiante', ['fecha_respuesta'])
    
    print("✅ 9 índices creados en respuestas_estudiante")
    
    # ==================== CONFIGURACIONES_ANTITRAMPA ====================
    print("\n🛡️ Índices para configuraciones_antitrampa...")
    
    # Jerarquía y tipo
    op.create_index('idx_config_antitrampa_tipo', 'configuraciones_antitrampa', ['tipo'])
    op.create_index('idx_config_antitrampa_padre', 'configuraciones_antitrampa', ['padre_id'])
    
    # Referencias
    op.create_index('idx_config_antitrampa_institucion', 'configuraciones_antitrampa', ['institucion_id'])
    op.create_index('idx_config_antitrampa_curso', 'configuraciones_antitrampa', ['curso_id'])
    op.create_index('idx_config_antitrampa_examen', 'configuraciones_antitrampa', ['examen_id'])
    
    # Estado
    op.create_index('idx_config_antitrampa_activa', 'configuraciones_antitrampa', ['activa'])
    
    print("✅ 6 índices creados en configuraciones_antitrampa")
    
    # ==================== PLANTILLAS_CONFIGURACION ====================
    print("\n📋 Índices para plantillas_configuracion...")
    
    # Búsquedas comunes
    op.create_index('idx_plantillas_config_id', 'plantillas_configuracion', ['configuracion_id'])
    op.create_index('idx_plantillas_institucion', 'plantillas_configuracion', ['institucion_id'])
    op.create_index('idx_plantillas_publica', 'plantillas_configuracion', ['es_publica'])
    op.create_index('idx_plantillas_sistema', 'plantillas_configuracion', ['es_sistema'])
    
    print("✅ 4 índices creados en plantillas_configuracion")
    
    # ==================== BANCO_PREGUNTAS ====================
    print("\n📚 Índices para banco_preguntas...")
    
    # Búsquedas frecuentes
    op.create_index('idx_banco_tipo', 'banco_preguntas', ['tipo_pregunta'])
    op.create_index('idx_banco_dificultad', 'banco_preguntas', ['dificultad'])
    op.create_index('idx_banco_materia', 'banco_preguntas', ['materia'])
    op.create_index('idx_banco_tema', 'banco_preguntas', ['tema'])
    
    # Propietario
    op.create_index('idx_banco_creado_por', 'banco_preguntas', ['creado_por'])
    op.create_index('idx_banco_institucion', 'banco_preguntas', ['institucion_id'])
    
    # Visibilidad y uso
    op.create_index('idx_banco_es_publica', 'banco_preguntas', ['es_publica'])
    op.create_index('idx_banco_veces_utilizada', 'banco_preguntas', ['veces_utilizada'])
    
    print("✅ 8 índices creados en banco_preguntas")
    
    # ==================== ESTADISTICAS_EXAMEN ====================
    print("\n📈 Índices para estadisticas_examen...")
    
    op.create_index('idx_estadisticas_examen_id', 'estadisticas_examen', ['examen_id'])
    op.create_index('idx_estadisticas_fecha_calculo', 'estadisticas_examen', ['fecha_calculo'])
    
    print("✅ 2 índices creados en estadisticas_examen")
    
    print("\n" + "="*80)
    print("✅ ÍNDICES CREADOS EXITOSAMENTE")
    print(f"📊 Total: 56 índices agregados")
    print("="*80 + "\n")


def downgrade() -> None:
    """Remove indexes"""
    
    print("\n⏪ ELIMINANDO ÍNDICES...\n")
    
    # Evaluaciones
    op.drop_index('idx_evaluaciones_curso_id')
    op.drop_index('idx_evaluaciones_grupo_id')
    op.drop_index('idx_evaluaciones_creador_id')
    op.drop_index('idx_evaluaciones_estado')
    op.drop_index('idx_evaluaciones_tipo')
    op.drop_index('idx_evaluaciones_visibilidad')
    op.drop_index('idx_evaluaciones_curso_estado')
    op.drop_index('idx_evaluaciones_fecha_inicio')
    op.drop_index('idx_evaluaciones_fecha_limite')
    op.drop_index('idx_evaluaciones_otorga_puntos')
    
    # Preguntas
    op.drop_index('idx_preguntas_evaluacion_id')
    op.drop_index('idx_preguntas_orden')
    op.drop_index('idx_preguntas_tipo')
    op.drop_index('idx_preguntas_dificultad')
    op.drop_index('idx_preguntas_banco_id')
    
    # Intentos
    op.drop_index('idx_intentos_evaluacion_id')
    op.drop_index('idx_intentos_estudiante_id')
    op.drop_index('idx_intentos_eval_estudiante')
    op.drop_index('idx_intentos_estudiante_estado')
    op.drop_index('idx_intentos_estado')
    op.drop_index('idx_intentos_fecha_inicio')
    op.drop_index('idx_intentos_fecha_fin')
    op.drop_index('idx_intentos_nivel_riesgo')
    op.drop_index('idx_intentos_bloqueado')
    op.drop_index('idx_intentos_puntos')
    op.drop_index('idx_intentos_ranking')
    op.drop_index('idx_intentos_equipo')
    
    # Respuestas
    op.drop_index('idx_respuestas_intento_id')
    op.drop_index('idx_respuestas_pregunta_id')
    op.drop_index('idx_respuestas_intento_pregunta')
    op.drop_index('idx_respuestas_es_correcta')
    op.drop_index('idx_respuestas_revision_manual')
    op.drop_index('idx_respuestas_revisado_por')
    op.drop_index('idx_respuestas_detectada_ia')
    op.drop_index('idx_respuestas_detectado_plagio')
    op.drop_index('idx_respuestas_fecha')
    
    # Configuraciones antitrampa
    op.drop_index('idx_config_antitrampa_tipo')
    op.drop_index('idx_config_antitrampa_padre')
    op.drop_index('idx_config_antitrampa_institucion')
    op.drop_index('idx_config_antitrampa_curso')
    op.drop_index('idx_config_antitrampa_examen')
    op.drop_index('idx_config_antitrampa_activa')
    
    # Plantillas
    op.drop_index('idx_plantillas_config_id')
    op.drop_index('idx_plantillas_institucion')
    op.drop_index('idx_plantillas_publica')
    op.drop_index('idx_plantillas_sistema')
    
    # Banco preguntas
    op.drop_index('idx_banco_tipo')
    op.drop_index('idx_banco_dificultad')
    op.drop_index('idx_banco_materia')
    op.drop_index('idx_banco_tema')
    op.drop_index('idx_banco_creado_por')
    op.drop_index('idx_banco_institucion')
    op.drop_index('idx_banco_es_publica')
    op.drop_index('idx_banco_veces_utilizada')
    
    # Estadísticas
    op.drop_index('idx_estadisticas_examen_id')
    op.drop_index('idx_estadisticas_fecha_calculo')
    
    print("✅ Índices eliminados\n")
