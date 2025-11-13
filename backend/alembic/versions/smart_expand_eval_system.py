"""Expand evaluation system - Smart migration (only adds missing columns)

Revision ID: smart_expand_eval_system
Revises: fb445d277f00, 291ba6082c35
Create Date: 2025-10-31 12:00:00.000000

Esta migración inteligente:
- Verifica qué columnas existen antes de agregarlas
- Solo agrega las columnas nuevas que faltan
- Crea las 2 tablas nuevas (configuraciones_antitrampa, plantillas_configuracion)
- Renombra tablas y columnas de manera segura
- Es completamente idempotente y reversible

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from sqlalchemy import inspect

# revision identifiers, used by Alembic.
revision: str = 'smart_expand_eval_system'
# Este es un merge que fusiona ambas ramas
down_revision: Union[str, Sequence[str], None] = ('fb445d277f00', '291ba6082c35')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def column_exists(table_name: str, column_name: str) -> bool:
    """Verifica si una columna existe en una tabla"""
    bind = op.get_bind()
    inspector = inspect(bind)
    columns = [col['name'] for col in inspector.get_columns(table_name)]
    return column_name in columns


def table_exists(table_name: str) -> bool:
    """Verifica si una tabla existe"""
    bind = op.get_bind()
    inspector = inspect(bind)
    return table_name in inspector.get_table_names()


def add_column_if_not_exists(table_name: str, column: sa.Column):
    """Agrega una columna solo si no existe"""
    if not column_exists(table_name, column.name):
        op.add_column(table_name, column)
        print(f"✅ Agregada columna {column.name} a {table_name}")
    else:
        print(f"⏭️  Columna {column.name} ya existe en {table_name}")


def upgrade() -> None:
    """Upgrade schema - Only adds what's missing"""
    
    bind = op.get_bind()
    
    print("\n" + "="*80)
    print("🚀 INICIANDO MIGRACIÓN INTELIGENTE DEL SISTEMA DE EVALUACIONES")
    print("="*80 + "\n")
    
    # ==================== CREAR NUEVAS TABLAS ====================
    
    print("\n📦 PASO 1: Creando nuevas tablas...")
    print("-"*80)
    
    # 1. Tabla configuraciones_antitrampa (si no existe)
    if not table_exists('configuraciones_antitrampa'):
        print("Creando tabla: configuraciones_antitrampa...")
        op.create_table(
            'configuraciones_antitrampa',
            sa.Column('id', sa.String(36), primary_key=True),
            sa.Column('nombre', sa.String(200), nullable=False),
            sa.Column('descripcion', sa.Text, nullable=True),
            
            # Jerarquía y alcance
            sa.Column('tipo', sa.String(50), nullable=False, server_default='GLOBAL'),  # GLOBAL, INSTITUCION, CURSO, EXAMEN, ESTUDIANTE
            sa.Column('nivel_seguridad', sa.String(50), nullable=False, server_default='MEDIO'),  # BAJO, MEDIO, ALTO, MAXIMO
            sa.Column('padre_id', sa.String(36), nullable=True),  # Para heredar configuraciones
            
            # Referencias según tipo
            sa.Column('institucion_id', sa.String(36), nullable=True),
            sa.Column('curso_id', sa.String(36), nullable=True),
            sa.Column('examen_id', sa.String(36), nullable=True),
            sa.Column('estudiante_id', sa.String(36), nullable=True),
            
            # 1. DETECCIÓN DE CAMBIO DE CONTEXTO (8 campos)
            sa.Column('detectar_cambio_pestana', sa.Boolean(), server_default='false'),
            sa.Column('max_cambios_pestana', sa.Integer(), server_default='3'),
            sa.Column('accion_cambio_pestana', sa.String(50), server_default='ADVERTENCIA'),  # ADVERTENCIA, BLOQUEAR, FINALIZAR
            sa.Column('detectar_salida_pantalla_completa', sa.Boolean(), server_default='false'),
            sa.Column('forzar_pantalla_completa', sa.Boolean(), server_default='false'),
            sa.Column('detectar_cambio_ventana', sa.Boolean(), server_default='false'),
            sa.Column('detectar_cambio_aplicacion', sa.Boolean(), server_default='false'),
            sa.Column('tiempo_gracia_retorno_segundos', sa.Integer(), server_default='10'),
            
            # 2. DETECCIÓN DE INACTIVIDAD (3 campos)
            sa.Column('detectar_inactividad', sa.Boolean(), server_default='false'),
            sa.Column('tiempo_max_inactividad_segundos', sa.Integer(), server_default='300'),
            sa.Column('accion_inactividad', sa.String(50), server_default='ADVERTENCIA'),
            
            # 3. TECLAS Y ACCIONES SOSPECHOSAS (7 campos)
            sa.Column('bloquear_copiar', sa.Boolean(), server_default='true'),
            sa.Column('bloquear_pegar', sa.Boolean(), server_default='true'),
            sa.Column('bloquear_cortar', sa.Boolean(), server_default='true'),
            sa.Column('bloquear_imprimir', sa.Boolean(), server_default='true'),
            sa.Column('bloquear_captura_pantalla', sa.Boolean(), server_default='true'),
            sa.Column('bloquear_teclas_desarrollador', sa.Boolean(), server_default='true'),  # F12, Ctrl+Shift+I
            sa.Column('bloquear_clic_derecho', sa.Boolean(), server_default='true'),
            
            # 4. DETECCIÓN DE MÚLTIPLES SESIONES (4 campos)
            sa.Column('detectar_multiples_sesiones', sa.Boolean(), server_default='true'),
            sa.Column('max_sesiones_simultaneas', sa.Integer(), server_default='1'),
            sa.Column('accion_sesion_duplicada', sa.String(50), server_default='BLOQUEAR'),
            sa.Column('permitir_sesion_recuperacion', sa.Boolean(), server_default='true'),
            
            # 5. ANÁLISIS DE PATRONES DE RESPUESTA (4 campos)
            sa.Column('detectar_patron_respuesta_rapida', sa.Boolean(), server_default='false'),
            sa.Column('umbral_tiempo_respuesta_segundos', sa.Integer(), server_default='5'),
            sa.Column('detectar_patron_secuencial', sa.Boolean(), server_default='false'),
            sa.Column('detectar_respuestas_identicas', sa.Boolean(), server_default='true'),
            
            # 6. DETECCIÓN DE IA EN RESPUESTAS (4 campos)
            sa.Column('detectar_ia_respuestas', sa.Boolean(), server_default='false'),
            sa.Column('umbral_deteccion_ia', sa.Float(), server_default='0.7'),
            sa.Column('tipos_pregunta_analizar_ia', postgresql.ARRAY(sa.String()), server_default='{"DESARROLLO","ENSAYO"}'),
            sa.Column('accion_deteccion_ia', sa.String(50), server_default='MARCAR_REVISION'),
            
            # 7. DETECCIÓN DE PLAGIO (5 campos)
            sa.Column('detectar_plagio', sa.Boolean(), server_default='false'),
            sa.Column('umbral_similitud_plagio', sa.Float(), server_default='0.8'),
            sa.Column('comparar_entre_estudiantes', sa.Boolean(), server_default='true'),
            sa.Column('comparar_con_internet', sa.Boolean(), server_default='false'),
            sa.Column('comparar_con_banco_respuestas', sa.Boolean(), server_default='true'),
            
            # 8. WEBCAM Y VERIFICACIÓN FACIAL (9 campos)
            sa.Column('requerir_webcam', sa.Boolean(), server_default='false'),
            sa.Column('verificar_identidad_facial', sa.Boolean(), server_default='false'),
            sa.Column('frecuencia_verificacion_minutos', sa.Integer(), server_default='15'),
            sa.Column('capturar_foto_inicio', sa.Boolean(), server_default='true'),
            sa.Column('capturar_fotos_periodicas', sa.Boolean(), server_default='false'),
            sa.Column('frecuencia_captura_minutos', sa.Integer(), server_default='5'),
            sa.Column('detectar_multiples_personas', sa.Boolean(), server_default='false'),
            sa.Column('detectar_ausencia_persona', sa.Boolean(), server_default='false'),
            sa.Column('umbral_confianza_facial', sa.Float(), server_default='0.85'),
            
            # 9. MONITOREO DE RED Y DISPOSITIVOS (5 campos)
            sa.Column('monitorear_actividad_red', sa.Boolean(), server_default='false'),
            sa.Column('detectar_vpn', sa.Boolean(), server_default='false'),
            sa.Column('validar_ubicacion_ip', sa.Boolean(), server_default='false'),
            sa.Column('ips_permitidas', postgresql.ARRAY(sa.String()), nullable=True),
            sa.Column('rangos_ip_bloqueados', postgresql.ARRAY(sa.String()), nullable=True),
            
            # 10. DISPOSITIVOS EXTERNOS (3 campos)
            sa.Column('detectar_dispositivos_externos', sa.Boolean(), server_default='false'),
            sa.Column('bloquear_segunda_pantalla', sa.Boolean(), server_default='false'),
            sa.Column('detectar_impresoras', sa.Boolean(), server_default='false'),
            
            # 11. MONITOREO EN TIEMPO REAL (3 campos)
            sa.Column('habilitar_monitoreo_tiempo_real', sa.Boolean(), server_default='false'),
            sa.Column('frecuencia_actualizacion_segundos', sa.Integer(), server_default='5'),
            sa.Column('notificar_eventos_supervisor', sa.Boolean(), server_default='true'),
            
            # 12. PUNTUACIÓN Y PESOS DE RIESGO (8 campos)
            sa.Column('peso_cambio_pestana', sa.Float(), server_default='1.0'),
            sa.Column('peso_inactividad', sa.Float(), server_default='0.5'),
            sa.Column('peso_tecla_sospechosa', sa.Float(), server_default='0.8'),
            sa.Column('peso_sesion_multiple', sa.Float(), server_default='2.0'),
            sa.Column('peso_patron_sospechoso', sa.Float(), server_default='1.5'),
            sa.Column('peso_ia_detectada', sa.Float(), server_default='3.0'),
            sa.Column('peso_plagio_detectado', sa.Float(), server_default='3.0'),
            sa.Column('umbral_bloqueo_automatico', sa.Float(), server_default='10.0'),
            
            # 13. REPORTES Y EVIDENCIAS (3 campos)
            sa.Column('generar_reporte_integridad', sa.Boolean(), server_default='true'),
            sa.Column('incluir_capturas_webcam', sa.Boolean(), server_default='false'),
            sa.Column('incluir_log_eventos', sa.Boolean(), server_default='true'),
            
            # 14. GRABACIÓN (4 campos)
            sa.Column('grabar_pantalla', sa.Boolean(), server_default='false'),
            sa.Column('grabar_audio', sa.Boolean(), server_default='false'),
            sa.Column('grabar_teclas', sa.Boolean(), server_default='false'),
            sa.Column('tiempo_retencion_grabaciones_dias', sa.Integer(), server_default='30'),
            
            # Metadata
            sa.Column('activa', sa.Boolean(), server_default='true'),
            sa.Column('creador_id', sa.String(36), nullable=False),
            sa.Column('fecha_creacion', sa.DateTime(timezone=True), server_default=sa.text('now()')),
            sa.Column('fecha_modificacion', sa.DateTime(timezone=True), nullable=True),
        )
        print("✅ Tabla configuraciones_antitrampa creada")
    else:
        print("⏭️  Tabla configuraciones_antitrampa ya existe")
    
    # 2. Tabla plantillas_configuracion
    if not table_exists('plantillas_configuracion'):
        print("Creando tabla: plantillas_configuracion...")
        op.create_table(
            'plantillas_configuracion',
            sa.Column('id', sa.String(36), primary_key=True),
            sa.Column('nombre', sa.String(200), nullable=False),
            sa.Column('descripcion', sa.Text, nullable=True),
            sa.Column('configuracion_id', sa.String(36), nullable=False),
            sa.Column('es_sistema', sa.Boolean(), server_default='false'),
            sa.Column('es_publica', sa.Boolean(), server_default='false'),
            sa.Column('institucion_id', sa.String(36), nullable=True),
            sa.Column('creador_id', sa.String(36), nullable=False),
            sa.Column('veces_utilizada', sa.Integer(), server_default='0'),
            sa.Column('fecha_creacion', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        )
        print("✅ Tabla plantillas_configuracion creada")
    else:
        print("⏭️  Tabla plantillas_configuracion ya existe")
    
    # ==================== RENOMBRAR TABLAS ====================
    
    print("\n🔄 PASO 2: Renombrando tablas...")
    print("-"*80)
    
    if table_exists('examenes') and not table_exists('evaluaciones'):
        op.rename_table('examenes', 'evaluaciones')
        print("✅ Tabla 'examenes' renombrada a 'evaluaciones'")
    elif table_exists('evaluaciones'):
        print("⏭️  Tabla 'evaluaciones' ya existe")
    
    if table_exists('preguntas_examen') and not table_exists('preguntas_evaluacion'):
        op.rename_table('preguntas_examen', 'preguntas_evaluacion')
        print("✅ Tabla 'preguntas_examen' renombrada a 'preguntas_evaluacion'")
    elif table_exists('preguntas_evaluacion'):
        print("⏭️  Tabla 'preguntas_evaluacion' ya existe")
    
    if table_exists('intentos_examen') and not table_exists('intentos_evaluacion'):
        op.rename_table('intentos_examen', 'intentos_evaluacion')
        print("✅ Tabla 'intentos_examen' renombrada a 'intentos_evaluacion'")
    elif table_exists('intentos_evaluacion'):
        print("⏭️  Tabla 'intentos_evaluacion' ya existe")
    
    # ==================== RENOMBRAR COLUMNAS - EVALUACIONES ====================
    
    print("\n📝 PASO 3: Renombrando columnas en evaluaciones...")
    print("-"*80)
    
    tabla_actual = 'evaluaciones' if table_exists('evaluaciones') else 'examenes'
    
    if column_exists(tabla_actual, 'examen_id') and not column_exists(tabla_actual, 'id'):
        op.alter_column(tabla_actual, 'examen_id', new_column_name='id')
        print("✅ Columna 'examen_id' renombrada a 'id'")
    
    if column_exists(tabla_actual, 'tiempo_limite') and not column_exists(tabla_actual, 'tiempo_limite_minutos'):
        op.alter_column(tabla_actual, 'tiempo_limite', new_column_name='tiempo_limite_minutos')
        print("✅ Columna 'tiempo_limite' renombrada a 'tiempo_limite_minutos'")
    
    if column_exists(tabla_actual, 'creado_por') and not column_exists(tabla_actual, 'creador_id'):
        op.alter_column(tabla_actual, 'creado_por', new_column_name='creador_id')
        print("✅ Columna 'creado_por' renombrada a 'creador_id'")
    
    if column_exists(tabla_actual, 'fecha_actualizacion') and not column_exists(tabla_actual, 'fecha_modificacion'):
        op.alter_column(tabla_actual, 'fecha_actualizacion', new_column_name='fecha_modificacion')
        print("✅ Columna 'fecha_actualizacion' renombrada a 'fecha_modificacion'")
    
    # ==================== AGREGAR NUEVAS COLUMNAS - EVALUACIONES ====================
    
    print("\n➕ PASO 4: Agregando nuevas columnas a evaluaciones...")
    print("-"*80)
    
    # Usar la tabla correcta (evaluaciones si existe, sino examenes)
    tabla_eval = 'evaluaciones' if table_exists('evaluaciones') else tabla_actual
    
    # TIPOS Y VISIBILIDAD (tipo_examen ya existe, así que estos son adicionales)
    add_column_if_not_exists(tabla_eval, sa.Column('tipo_evaluacion', sa.String(50), server_default='EVALUACION'))
    add_column_if_not_exists(tabla_eval, sa.Column('visibilidad', sa.String(50), server_default='PRIVADA'))
    add_column_if_not_exists(tabla_eval, sa.Column('modo_evaluacion', sa.String(50), server_default='STANDARD'))
    add_column_if_not_exists(tabla_eval, sa.Column('estado', sa.String(50), server_default='BORRADOR'))
    
    # FECHAS ADICIONALES
    add_column_if_not_exists(tabla_eval, sa.Column('fecha_apertura', sa.DateTime(timezone=True), nullable=True))
    add_column_if_not_exists(tabla_eval, sa.Column('fecha_cierre', sa.DateTime(timezone=True), nullable=True))
    add_column_if_not_exists(tabla_eval, sa.Column('fecha_publicacion', sa.DateTime(timezone=True), nullable=True))
    add_column_if_not_exists(tabla_eval, sa.Column('fecha_publicacion_resultados', sa.DateTime(timezone=True), nullable=True))
    
    # CONFIGURACIÓN DE PREGUNTAS
    add_column_if_not_exists(tabla_eval, sa.Column('num_preguntas_mostrar', sa.Integer(), nullable=True))
    add_column_if_not_exists(tabla_eval, sa.Column('randomizar_opciones', sa.Boolean(), server_default='false'))
    add_column_if_not_exists(tabla_eval, sa.Column('una_pregunta_por_vez', sa.Boolean(), server_default='false'))
    add_column_if_not_exists(tabla_eval, sa.Column('permitir_navegar_atras', sa.Boolean(), server_default='true'))
    add_column_if_not_exists(tabla_eval, sa.Column('mostrar_progreso', sa.Boolean(), server_default='true'))
    
    # TIEMPO Y CONTROL
    add_column_if_not_exists(tabla_eval, sa.Column('permitir_pausar', sa.Boolean(), server_default='false'))
    add_column_if_not_exists(tabla_eval, sa.Column('max_pausas', sa.Integer(), nullable=True))
    add_column_if_not_exists(tabla_eval, sa.Column('tiempo_entre_intentos_minutos', sa.Integer(), nullable=True))
    add_column_if_not_exists(tabla_eval, sa.Column('advertencia_tiempo_restante', sa.Boolean(), server_default='true'))
    add_column_if_not_exists(tabla_eval, sa.Column('minutos_advertencia', sa.Integer(), server_default='5'))
    
    # ACCESO Y SEGURIDAD
    add_column_if_not_exists(tabla_eval, sa.Column('codigo_acceso', sa.String(20), nullable=True))
    add_column_if_not_exists(tabla_eval, sa.Column('contrasena', sa.String(255), nullable=True))
    add_column_if_not_exists(tabla_eval, sa.Column('configuracion_antitrampa_id', sa.String(36), nullable=True))
    
    # CALIFICACIÓN E IA
    add_column_if_not_exists(tabla_eval, sa.Column('tipo_calificacion', sa.String(50), server_default='AUTOMATICA'))
    add_column_if_not_exists(tabla_eval, sa.Column('usar_ia_calificacion', sa.Boolean(), server_default='false'))
    add_column_if_not_exists(tabla_eval, sa.Column('rubrica_ia', postgresql.JSON, nullable=True))
    add_column_if_not_exists(tabla_eval, sa.Column('generar_feedback_ia', sa.Boolean(), server_default='false'))
    add_column_if_not_exists(tabla_eval, sa.Column('feedback_personalizado', sa.Boolean(), server_default='false'))
    
    # MULTIMEDIA Y VERIFICACIÓN
    add_column_if_not_exists(tabla_eval, sa.Column('requerir_camara', sa.Boolean(), server_default='false'))
    add_column_if_not_exists(tabla_eval, sa.Column('grabar_camara_continuo', sa.Boolean(), server_default='false'))
    add_column_if_not_exists(tabla_eval, sa.Column('verificar_identidad_facial', sa.Boolean(), server_default='false'))
    add_column_if_not_exists(tabla_eval, sa.Column('requerir_microfono', sa.Boolean(), server_default='false'))
    add_column_if_not_exists(tabla_eval, sa.Column('grabar_audio_continuo', sa.Boolean(), server_default='false'))
    add_column_if_not_exists(tabla_eval, sa.Column('permitir_grabacion_pantalla', sa.Boolean(), server_default='false'))
    
    # GAMIFICACIÓN
    add_column_if_not_exists(tabla_eval, sa.Column('otorga_puntos', sa.Boolean(), server_default='false'))
    add_column_if_not_exists(tabla_eval, sa.Column('puntos_base', sa.Integer(), server_default='100'))
    add_column_if_not_exists(tabla_eval, sa.Column('puntos_por_acierto', sa.Integer(), server_default='10'))
    add_column_if_not_exists(tabla_eval, sa.Column('puntos_por_tiempo', sa.Boolean(), server_default='false'))
    add_column_if_not_exists(tabla_eval, sa.Column('multiplicador_puntos', sa.Float(), server_default='1.0'))
    add_column_if_not_exists(tabla_eval, sa.Column('otorga_insignia', sa.Boolean(), server_default='false'))
    add_column_if_not_exists(tabla_eval, sa.Column('insignia_id', sa.String(36), nullable=True))
    
    # EVALUACIONES INNOVADORAS
    add_column_if_not_exists(tabla_eval, sa.Column('es_adaptativa', sa.Boolean(), server_default='false'))
    add_column_if_not_exists(tabla_eval, sa.Column('nivel_dificultad_inicial', sa.String(50), nullable=True))
    add_column_if_not_exists(tabla_eval, sa.Column('es_colaborativa', sa.Boolean(), server_default='false'))
    add_column_if_not_exists(tabla_eval, sa.Column('max_miembros_equipo', sa.Integer(), nullable=True))
    add_column_if_not_exists(tabla_eval, sa.Column('permitir_peer_review', sa.Boolean(), server_default='false'))
    add_column_if_not_exists(tabla_eval, sa.Column('num_peer_reviews_requeridos', sa.Integer(), nullable=True))
    
    # ESTADÍSTICAS AVANZADAS
    add_column_if_not_exists(tabla_eval, sa.Column('total_completados', sa.Integer(), server_default='0'))
    add_column_if_not_exists(tabla_eval, sa.Column('tasa_completacion', sa.Float(), nullable=True))
    add_column_if_not_exists(tabla_eval, sa.Column('tasa_aprobacion', sa.Float(), nullable=True))
    add_column_if_not_exists(tabla_eval, sa.Column('tiempo_promedio_minutos', sa.Float(), nullable=True))
    add_column_if_not_exists(tabla_eval, sa.Column('distribucion_calificaciones', postgresql.JSON, nullable=True))
    
    # ==================== AGREGAR NUEVAS COLUMNAS - PREGUNTAS ====================
    
    print("\n➕ PASO 5: Agregando nuevas columnas a preguntas_evaluacion...")
    print("-"*80)
    
    tabla_preg = 'preguntas_evaluacion' if table_exists('preguntas_evaluacion') else 'preguntas_examen'
    
    # Renombrar columnas primero
    if column_exists(tabla_preg, 'pregunta_id') and not column_exists(tabla_preg, 'id'):
        op.alter_column(tabla_preg, 'pregunta_id', new_column_name='id')
        print("✅ Columna 'pregunta_id' renombrada a 'id'")
    
    if column_exists(tabla_preg, 'examen_id') and not column_exists(tabla_preg, 'evaluacion_id'):
        op.alter_column(tabla_preg, 'examen_id', new_column_name='evaluacion_id')
        print("✅ Columna 'examen_id' renombrada a 'evaluacion_id'")
    
    # Intercambio especial: titulo ↔ descripcion
    # titulo (actual) debe ser enunciado (largo)
    # descripcion (actual) debe ser titulo (corto)
    if column_exists(tabla_preg, 'titulo') and column_exists(tabla_preg, 'descripcion'):
        if not column_exists(tabla_preg, 'enunciado'):
            # Crear columna temporal para el swap
            op.add_column(tabla_preg, sa.Column('enunciado', sa.Text, nullable=True))
            bind = op.get_bind()
            bind.execute(sa.text(f'UPDATE {tabla_preg} SET enunciado = titulo'))
            bind.execute(sa.text(f'UPDATE {tabla_preg} SET titulo = descripcion'))
            bind.execute(sa.text(f'UPDATE {tabla_preg} SET descripcion = enunciado'))
            op.drop_column(tabla_preg, 'enunciado')
            print("✅ Intercambiadas columnas titulo ↔ descripcion")
    
    # Nuevas columnas para preguntas
    add_column_if_not_exists(tabla_preg, sa.Column('enunciado', sa.Text, nullable=True))
    add_column_if_not_exists(tabla_preg, sa.Column('respuestas_alternativas', postgresql.JSON, nullable=True))
    add_column_if_not_exists(tabla_preg, sa.Column('configuracion_ia', postgresql.JSON, nullable=True))
    add_column_if_not_exists(tabla_preg, sa.Column('criterios_evaluacion_ia', postgresql.JSON, nullable=True))
    
    # Soporte para código
    add_column_if_not_exists(tabla_preg, sa.Column('lenguaje_codigo', sa.String(50), nullable=True))
    add_column_if_not_exists(tabla_preg, sa.Column('plantilla_codigo', sa.Text, nullable=True))
    add_column_if_not_exists(tabla_preg, sa.Column('tests_unitarios', postgresql.JSON, nullable=True))
    add_column_if_not_exists(tabla_preg, sa.Column('solucion_referencia', sa.Text, nullable=True))
    
    # Soporte para matemáticas
    add_column_if_not_exists(tabla_preg, sa.Column('formula_latex', sa.Text, nullable=True))
    add_column_if_not_exists(tabla_preg, sa.Column('variables_formula', postgresql.JSON, nullable=True))
    add_column_if_not_exists(tabla_preg, sa.Column('tolerancia_numerica', sa.Float(), nullable=True))
    
    # Preguntas interactivas
    add_column_if_not_exists(tabla_preg, sa.Column('configuracion_interactiva', postgresql.JSON, nullable=True))
    add_column_if_not_exists(tabla_preg, sa.Column('tipo_interaccion', sa.String(50), nullable=True))
    
    # Metadata adicional
    add_column_if_not_exists(tabla_preg, sa.Column('etiquetas', postgresql.JSON, nullable=True))
    add_column_if_not_exists(tabla_preg, sa.Column('feedback_correcto', sa.Text, nullable=True))
    add_column_if_not_exists(tabla_preg, sa.Column('feedback_incorrecto', sa.Text, nullable=True))
    add_column_if_not_exists(tabla_preg, sa.Column('metadata', postgresql.JSON, nullable=True))
    
    # ==================== AGREGAR NUEVAS COLUMNAS - INTENTOS ====================
    
    print("\n➕ PASO 6: Agregando nuevas columnas a intentos_evaluacion...")
    print("-"*80)
    
    tabla_int = 'intentos_evaluacion' if table_exists('intentos_evaluacion') else 'intentos_examen'
    
    # Renombrar columnas
    if column_exists(tabla_int, 'intento_id') and not column_exists(tabla_int, 'id'):
        op.alter_column(tabla_int, 'intento_id', new_column_name='id')
        print("✅ Columna 'intento_id' renombrada a 'id'")
    
    if column_exists(tabla_int, 'examen_id') and not column_exists(tabla_int, 'evaluacion_id'):
        op.alter_column(tabla_int, 'examen_id', new_column_name='evaluacion_id')
        print("✅ Columna 'examen_id' renombrada a 'evaluacion_id'")
    
    if column_exists(tabla_int, 'pregunta_actual') and not column_exists(tabla_int, 'pregunta_actual_orden'):
        op.alter_column(tabla_int, 'pregunta_actual', new_column_name='pregunta_actual_orden')
        print("✅ Columna 'pregunta_actual' renombrada a 'pregunta_actual_orden'")
    
    # Progreso detallado
    add_column_if_not_exists(tabla_int, sa.Column('progreso_actual', sa.Float(), server_default='0.0'))
    add_column_if_not_exists(tabla_int, sa.Column('tiempo_activo_segundos', sa.Integer(), server_default='0'))
    add_column_if_not_exists(tabla_int, sa.Column('tiempo_pausado_segundos', sa.Integer(), server_default='0'))
    add_column_if_not_exists(tabla_int, sa.Column('numero_pausas', sa.Integer(), server_default='0'))
    
    # IA y Calificación
    add_column_if_not_exists(tabla_int, sa.Column('requiere_revision_manual', sa.Boolean(), server_default='false'))
    add_column_if_not_exists(tabla_int, sa.Column('calificado_por_ia', sa.Boolean(), server_default='false'))
    add_column_if_not_exists(tabla_int, sa.Column('feedback_ia', sa.Text, nullable=True))
    add_column_if_not_exists(tabla_int, sa.Column('feedback_manual', sa.Text, nullable=True))
    add_column_if_not_exists(tabla_int, sa.Column('confianza_calificacion_ia', sa.Float(), nullable=True))
    add_column_if_not_exists(tabla_int, sa.Column('recomendaciones_ia', postgresql.JSON, nullable=True))
    
    # Anti-trampa y detección
    add_column_if_not_exists(tabla_int, sa.Column('nivel_riesgo', sa.String(50), server_default='BAJO'))
    add_column_if_not_exists(tabla_int, sa.Column('puntuacion_riesgo', sa.Float(), server_default='0.0'))
    add_column_if_not_exists(tabla_int, sa.Column('total_eventos_antitrampa', sa.Integer(), server_default='0'))
    add_column_if_not_exists(tabla_int, sa.Column('detecciones_ia', sa.Integer(), server_default='0'))
    add_column_if_not_exists(tabla_int, sa.Column('detecciones_plagio', sa.Integer(), server_default='0'))
    add_column_if_not_exists(tabla_int, sa.Column('eventos_detallados', postgresql.JSON, nullable=True))
    add_column_if_not_exists(tabla_int, sa.Column('bloqueado_automaticamente', sa.Boolean(), server_default='false'))
    add_column_if_not_exists(tabla_int, sa.Column('razon_bloqueo', sa.Text, nullable=True))
    
    # Multimedia y verificación
    add_column_if_not_exists(tabla_int, sa.Column('sesion_grabacion_id', sa.String(100), nullable=True))
    add_column_if_not_exists(tabla_int, sa.Column('total_capturas_webcam', sa.Integer(), server_default='0'))
    add_column_if_not_exists(tabla_int, sa.Column('capturas_con_anomalias', sa.Integer(), server_default='0'))
    add_column_if_not_exists(tabla_int, sa.Column('verificacion_identidad_exitosa', sa.Boolean(), nullable=True))
    add_column_if_not_exists(tabla_int, sa.Column('url_grabacion_video', sa.String(500), nullable=True))
    add_column_if_not_exists(tabla_int, sa.Column('url_grabacion_audio', sa.String(500), nullable=True))
    add_column_if_not_exists(tabla_int, sa.Column('capturas_urls', postgresql.JSON, nullable=True))
    
    # Gamificación
    add_column_if_not_exists(tabla_int, sa.Column('puntos_ganados', sa.Integer(), server_default='0'))
    add_column_if_not_exists(tabla_int, sa.Column('multiplicador_aplicado', sa.Float(), server_default='1.0'))
    add_column_if_not_exists(tabla_int, sa.Column('bonus_tiempo', sa.Integer(), server_default='0'))
    add_column_if_not_exists(tabla_int, sa.Column('bonus_precision', sa.Integer(), server_default='0'))
    add_column_if_not_exists(tabla_int, sa.Column('insignias_ganadas', postgresql.JSON, nullable=True))
    add_column_if_not_exists(tabla_int, sa.Column('logros_desbloqueados', postgresql.JSON, nullable=True))
    add_column_if_not_exists(tabla_int, sa.Column('posicion_ranking', sa.Integer(), nullable=True))
    
    # Evaluaciones adaptativas
    add_column_if_not_exists(tabla_int, sa.Column('dificultad_inicial', sa.String(50), nullable=True))
    add_column_if_not_exists(tabla_int, sa.Column('dificultad_actual', sa.String(50), nullable=True))
    add_column_if_not_exists(tabla_int, sa.Column('ajustes_dificultad', postgresql.JSON, nullable=True))
    add_column_if_not_exists(tabla_int, sa.Column('nivel_habilidad_estimado', sa.Float(), nullable=True))
    
    # Evaluaciones colaborativas
    add_column_if_not_exists(tabla_int, sa.Column('equipo_id', sa.String(36), nullable=True))
    add_column_if_not_exists(tabla_int, sa.Column('equipo_ids', postgresql.JSON, nullable=True))
    add_column_if_not_exists(tabla_int, sa.Column('es_lider_equipo', sa.Boolean(), server_default='false'))
    add_column_if_not_exists(tabla_int, sa.Column('contribucion_equipo', postgresql.JSON, nullable=True))
    
    # ==================== AGREGAR NUEVAS COLUMNAS - RESPUESTAS ====================
    
    print("\n➕ PASO 7: Agregando nuevas columnas a respuestas_estudiante...")
    print("-"*80)
    
    tabla_resp = 'respuestas_estudiante'
    
    # Renombrar
    if column_exists(tabla_resp, 'respuesta_id') and not column_exists(tabla_resp, 'id'):
        op.alter_column(tabla_resp, 'respuesta_id', new_column_name='id')
        print("✅ Columna 'respuesta_id' renombrada a 'id'")
    
    if column_exists(tabla_resp, 'tiempo_empleado_segundos') and not column_exists(tabla_resp, 'tiempo_respuesta_segundos'):
        op.alter_column(tabla_resp, 'tiempo_empleado_segundos', new_column_name='tiempo_respuesta_segundos')
        print("✅ Columna 'tiempo_empleado_segundos' renombrada a 'tiempo_respuesta_segundos'")
    
    # Feedback mejorado
    add_column_if_not_exists(tabla_resp, sa.Column('feedback', sa.Text, nullable=True))
    add_column_if_not_exists(tabla_resp, sa.Column('feedback_ia', sa.Text, nullable=True))
    add_column_if_not_exists(tabla_resp, sa.Column('feedback_manual', sa.Text, nullable=True))
    add_column_if_not_exists(tabla_resp, sa.Column('explicacion', sa.Text, nullable=True))
    add_column_if_not_exists(tabla_resp, sa.Column('sugerencias_mejora', sa.Text, nullable=True))
    
    # Detección IA
    add_column_if_not_exists(tabla_resp, sa.Column('fue_detectada_ia', sa.Boolean(), server_default='false'))
    add_column_if_not_exists(tabla_resp, sa.Column('probabilidad_ia', sa.Float(), nullable=True))
    add_column_if_not_exists(tabla_resp, sa.Column('indicadores_ia', postgresql.JSON, nullable=True))
    add_column_if_not_exists(tabla_resp, sa.Column('modelo_ia_usado', sa.String(100), nullable=True))
    
    # Detección plagio
    add_column_if_not_exists(tabla_resp, sa.Column('fue_detectado_plagio', sa.Boolean(), server_default='false'))
    add_column_if_not_exists(tabla_resp, sa.Column('similitud_plagio', sa.Float(), nullable=True))
    add_column_if_not_exists(tabla_resp, sa.Column('fuentes_plagio', postgresql.JSON, nullable=True))
    add_column_if_not_exists(tabla_resp, sa.Column('tipo_plagio', sa.String(50), nullable=True))
    
    # Revisión manual
    add_column_if_not_exists(tabla_resp, sa.Column('requiere_revision_manual', sa.Boolean(), server_default='false'))
    add_column_if_not_exists(tabla_resp, sa.Column('revisado_por_id', sa.String(36), nullable=True))
    add_column_if_not_exists(tabla_resp, sa.Column('fecha_revision', sa.DateTime(timezone=True), nullable=True))
    add_column_if_not_exists(tabla_resp, sa.Column('notas_revision', sa.Text, nullable=True))
    
    # Ejecución de código
    add_column_if_not_exists(tabla_resp, sa.Column('codigo_ejecutado', sa.Text, nullable=True))
    add_column_if_not_exists(tabla_resp, sa.Column('resultado_ejecucion', postgresql.JSON, nullable=True))
    add_column_if_not_exists(tabla_resp, sa.Column('tests_pasados', sa.Integer(), nullable=True))
    add_column_if_not_exists(tabla_resp, sa.Column('tests_fallados', sa.Integer(), nullable=True))
    add_column_if_not_exists(tabla_resp, sa.Column('cobertura_codigo', sa.Float(), nullable=True))
    
    # Multimedia
    add_column_if_not_exists(tabla_resp, sa.Column('audio_url', sa.String(500), nullable=True))
    add_column_if_not_exists(tabla_resp, sa.Column('video_url', sa.String(500), nullable=True))
    add_column_if_not_exists(tabla_resp, sa.Column('archivo_url', sa.String(500), nullable=True))
    add_column_if_not_exists(tabla_resp, sa.Column('dibujo_url', sa.String(500), nullable=True))
    
    # ==================== FOREIGN KEYS ====================
    
    print("\n🔗 PASO 8: Agregando foreign keys...")
    print("-"*80)
    
    # Solo agregar FK si las tablas existen
    if table_exists('evaluaciones') and table_exists('configuraciones_antitrampa'):
        try:
            op.create_foreign_key(
                'fk_evaluaciones_configuracion_antitrampa',
                'evaluaciones', 'configuraciones_antitrampa',
                ['configuracion_antitrampa_id'], ['id'],
                ondelete='SET NULL'
            )
            print("✅ Foreign key evaluaciones → configuraciones_antitrampa creada")
        except Exception as e:
            print(f"⏭️  Foreign key ya existe o error: {str(e)[:100]}")
    
    if table_exists('plantillas_configuracion') and table_exists('configuraciones_antitrampa'):
        try:
            op.create_foreign_key(
                'fk_plantillas_configuracion',
                'plantillas_configuracion', 'configuraciones_antitrampa',
                ['configuracion_id'], ['id'],
                ondelete='CASCADE'
            )
            print("✅ Foreign key plantillas → configuraciones creada")
        except Exception as e:
            print(f"⏭️  Foreign key ya existe o error: {str(e)[:100]}")
    
    print("\n" + "="*80)
    print("✅ MIGRACIÓN COMPLETADA EXITOSAMENTE")
    print("="*80 + "\n")


def downgrade() -> None:
    """Downgrade schema - Revert changes"""
    
    print("\n" + "="*80)
    print("⏪ REVIRTIENDO MIGRACIÓN")
    print("="*80 + "\n")
    
    # Drop foreign keys
    if table_exists('evaluaciones'):
        try:
            op.drop_constraint('fk_evaluaciones_configuracion_antitrampa', 'evaluaciones', type_='foreignkey')
        except:
            pass
    
    if table_exists('plantillas_configuracion'):
        try:
            op.drop_constraint('fk_plantillas_configuracion', 'plantillas_configuracion', type_='foreignkey')
        except:
            pass
    
    # Drop new tables
    if table_exists('plantillas_configuracion'):
        op.drop_table('plantillas_configuracion')
        print("✅ Tabla plantillas_configuracion eliminada")
    
    if table_exists('configuraciones_antitrampa'):
        op.drop_table('configuraciones_antitrampa')
        print("✅ Tabla configuraciones_antitrampa eliminada")
    
    # Revertir nombres de tablas
    if table_exists('evaluaciones'):
        op.rename_table('evaluaciones', 'examenes')
        print("✅ Tabla 'evaluaciones' revertida a 'examenes'")
    
    if table_exists('preguntas_evaluacion'):
        op.rename_table('preguntas_evaluacion', 'preguntas_examen')
        print("✅ Tabla 'preguntas_evaluacion' revertida a 'preguntas_examen'")
    
    if table_exists('intentos_evaluacion'):
        op.rename_table('intentos_evaluacion', 'intentos_examen')
        print("✅ Tabla 'intentos_evaluacion' revertida a 'intentos_examen'")
    
    # Nota: No eliminamos las columnas agregadas en el downgrade para evitar pérdida de datos
    # Si se requiere un downgrade completo, se debe hacer manualmente
    
    print("\n⚠️  NOTA: Las columnas agregadas NO se eliminaron para preservar datos")
    print("    Si necesitas un downgrade completo, hazlo manualmente\n")
    
    print("="*80)
    print("✅ DOWNGRADE COMPLETADO")
    print("="*80 + "\n")
