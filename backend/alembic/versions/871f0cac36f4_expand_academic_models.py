"""expand_academic_models_curso_programa_grupo

Revision ID: 871f0cac36f4
Revises: f7e6fccee786
Create Date: 2025-10-30 19:25:00.000000

Expande los modelos Curso, Programa y Grupo con ~200 campos nuevos.
Agrega 11 nuevos ENUMs para clasificación y estados.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '871f0cac36f4'
down_revision: Union[str, Sequence[str], None] = 'f7e6fccee786'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema - Agregar campos a Curso, Programa y Grupo"""
    
    # ==================== CREAR ENUMs ====================
    # Usando DO $$ para evitar errores si ya existe
    
    # ENUMs para Curso
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE nivel_dificultad AS ENUM (
                'basico', 'intermedio', 'avanzado', 'experto'
            );
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
    """)
    
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE tipo_curso AS ENUM (
                'teorico', 'practico', 'teorico_practico', 'laboratorio', 
                'taller', 'proyecto', 'seminario', 'investigacion', 
                'practica_profesional'
            );
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
    """)
    
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE categoria_curso AS ENUM (
                'obligatorio', 'fundamental', 'profesional', 'electivo', 
                'libre', 'nivelacion', 'complementario'
            );
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
    """)
    
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE estado_curso AS ENUM (
                'borrador', 'programado', 'inscripciones_abiertas', 'proximo', 
                'en_curso', 'finalizado', 'cancelado', 'suspendido', 'archivado'
            );
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
    """)
    
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE idioma_curso AS ENUM (
                'español', 'inglés', 'francés', 'alemán', 'portugués', 
                'italiano', 'chino', 'japonés', 'otro'
            );
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
    """)
    
    # ENUMs para Programa
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE estado_programa AS ENUM (
                'activo', 'inactivo', 'en_proceso_apertura', 
                'suspendido_temporalmente', 'en_liquidacion', 'cerrado'
            );
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
    """)
    
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE duracion_programa AS ENUM (
                'semestral', 'trimestral', 'cuatrimestral', 'anual', 
                'bianual', 'modular', 'flexible', 'continuo'
            );
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
    """)
    
    # ENUMs para Grupo
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE estado_grupo AS ENUM (
                'programado', 'inscripciones_abiertas', 'cupos_disponibles', 
                'lista_espera', 'lleno', 'confirmado', 'en_curso', 
                'finalizado', 'cancelado', 'suspendido', 'cerrado'
            );
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
    """)
    
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE tipo_grupo AS ENUM (
                'regular', 'intensivo', 'nivelacion', 'recuperacion', 
                'honores', 'especial', 'virtual', 'hibrido', 'presencial', 
                'laboratorio', 'practica'
            );
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
    """)
    
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE modalidad_asistencia AS ENUM (
                'obligatoria', 'flexible', 'libre', 'mixta'
            );
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
    """)
    
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE formato_evaluacion AS ENUM (
                'examenes', 'proyectos', 'talleres', 'participacion', 
                'mixto', 'continua', 'portafolio'
            );
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
    """)
    
    # ==================== EXPANDIR TABLA CURSO ====================
    
    # Carga académica
    op.add_column('Curso', sa.Column('horas_teoricas', sa.INTEGER(), nullable=True))
    op.add_column('Curso', sa.Column('horas_practicas', sa.INTEGER(), nullable=True))
    op.add_column('Curso', sa.Column('horas_laboratorio', sa.INTEGER(), nullable=True))
    op.add_column('Curso', sa.Column('horas_autonomas', sa.INTEGER(), nullable=True))
    
    # Clasificación
    op.add_column('Curso', sa.Column('nivel_dificultad', postgresql.ENUM(name='nivel_dificultad', create_type=False), nullable=True))
    op.add_column('Curso', sa.Column('tipo_curso', postgresql.ENUM(name='tipo_curso', create_type=False), nullable=True))
    op.add_column('Curso', sa.Column('categoria_curso', postgresql.ENUM(name='categoria_curso', create_type=False), nullable=True))
    op.add_column('Curso', sa.Column('estado', postgresql.ENUM(name='estado_curso', create_type=False), nullable=False, server_default=sa.text("'borrador'")))
    op.add_column('Curso', sa.Column('idioma', postgresql.ENUM(name='idioma_curso', create_type=False), nullable=True))
    
    # Fechas extendidas
    op.add_column('Curso', sa.Column('fecha_limite_inscripcion', sa.DATE(), nullable=True))
    op.add_column('Curso', sa.Column('fecha_inicio_retiro', sa.DATE(), nullable=True))
    op.add_column('Curso', sa.Column('fecha_limite_retiro', sa.DATE(), nullable=True))
    
    # Cupos y lista de espera
    op.add_column('Curso', sa.Column('cupos_disponibles', sa.INTEGER(), nullable=True))
    op.add_column('Curso', sa.Column('permite_lista_espera', sa.Boolean(), nullable=True, server_default=sa.text('false')))
    op.add_column('Curso', sa.Column('maximo_lista_espera', sa.INTEGER(), nullable=True))
    
    # Requisitos académicos
    op.add_column('Curso', sa.Column('prerequisitos_ids', postgresql.JSON(astext_type=sa.Text()), nullable=True))
    op.add_column('Curso', sa.Column('correquisitos_ids', postgresql.JSON(astext_type=sa.Text()), nullable=True))
    op.add_column('Curso', sa.Column('requiere_nivelacion', sa.Boolean(), nullable=True, server_default=sa.text('false')))
    op.add_column('Curso', sa.Column('creditos_minimos_requeridos', sa.INTEGER(), nullable=True, server_default=sa.text('0')))
    op.add_column('Curso', sa.Column('promedio_minimo_requerido', sa.Numeric(precision=3, scale=2), nullable=True))
    
    # Costos
    op.add_column('Curso', sa.Column('tiene_costo', sa.Boolean(), nullable=True, server_default=sa.text('false')))
    op.add_column('Curso', sa.Column('costo_matricula', sa.Numeric(precision=12, scale=2), nullable=True))
    op.add_column('Curso', sa.Column('costo_mensual', sa.Numeric(precision=12, scale=2), nullable=True))
    op.add_column('Curso', sa.Column('costo_total', sa.Numeric(precision=12, scale=2), nullable=True))
    op.add_column('Curso', sa.Column('permite_becas', sa.Boolean(), nullable=True, server_default=sa.text('false')))
    op.add_column('Curso', sa.Column('porcentaje_descuento', sa.Numeric(precision=5, scale=2), nullable=True))
    
    # Evaluación y calificación
    op.add_column('Curso', sa.Column('calificacion_minima_aprobacion', sa.Numeric(precision=3, scale=2), nullable=True, server_default=sa.text('3.0')))
    op.add_column('Curso', sa.Column('porcentaje_asistencia_minimo', sa.Numeric(precision=5, scale=2), nullable=True, server_default=sa.text('80.0')))
    op.add_column('Curso', sa.Column('permite_recuperacion', sa.Boolean(), nullable=True, server_default=sa.text('true')))
    op.add_column('Curso', sa.Column('permite_habilitacion', sa.Boolean(), nullable=True, server_default=sa.text('true')))
    op.add_column('Curso', sa.Column('numero_maximo_faltas', sa.INTEGER(), nullable=True))
    
    # Configuración adicional
    op.add_column('Curso', sa.Column('permite_foros', sa.Boolean(), nullable=True, server_default=sa.text('true')))
    op.add_column('Curso', sa.Column('permite_comentarios', sa.Boolean(), nullable=True, server_default=sa.text('true')))
    op.add_column('Curso', sa.Column('permite_calificacion_entre_pares', sa.Boolean(), nullable=True, server_default=sa.text('false')))
    
    # Certificación
    op.add_column('Curso', sa.Column('genera_certificado', sa.Boolean(), nullable=True, server_default=sa.text('false')))
    op.add_column('Curso', sa.Column('requiere_trabajo_final', sa.Boolean(), nullable=True, server_default=sa.text('false')))
    op.add_column('Curso', sa.Column('tipo_trabajo_final', sa.String(length=50), nullable=True))
    
    # Metadata
    op.add_column('Curso', sa.Column('syllabus_url', sa.String(length=500), nullable=True))
    op.add_column('Curso', sa.Column('bibliografia', sa.TEXT(), nullable=True))
    op.add_column('Curso', sa.Column('recursos_adicionales', postgresql.JSON(astext_type=sa.Text()), nullable=True))
    op.add_column('Curso', sa.Column('tags', postgresql.JSON(astext_type=sa.Text()), nullable=True))
    op.add_column('Curso', sa.Column('imagen_url', sa.String(length=500), nullable=True))
    
    # Auditoría
    op.add_column('Curso', sa.Column('fecha_creacion', postgresql.TIMESTAMP(), nullable=False, server_default=sa.text('now()')))
    op.add_column('Curso', sa.Column('fecha_actualizacion', postgresql.TIMESTAMP(), nullable=False, server_default=sa.text('now()')))
    
    # Crear índices para Curso
    op.create_index('idx_curso_estado', 'Curso', ['estado'])
    op.create_index('idx_curso_nivel_dificultad', 'Curso', ['nivel_dificultad'])
    op.create_index('idx_curso_tipo', 'Curso', ['tipo_curso'])
    op.create_index('idx_curso_categoria', 'Curso', ['categoria_curso'])
    
    # ==================== EXPANDIR TABLA PROGRAMA ====================
    
    # Coordinador
    op.add_column('Programa', sa.Column('coordinador_id', postgresql.UUID(as_uuid=True), nullable=True))
    op.create_foreign_key('fk_programa_coordinador', 'Programa', 'Coordinador', ['coordinador_id'], ['coordinador_id'], ondelete='SET NULL')
    
    # Información básica extendida
    op.add_column('Programa', sa.Column('codigo', sa.String(length=50), nullable=True))
    op.add_column('Programa', sa.Column('mision', sa.TEXT(), nullable=True))
    op.add_column('Programa', sa.Column('vision', sa.TEXT(), nullable=True))
    op.add_column('Programa', sa.Column('objetivos', sa.TEXT(), nullable=True))
    op.add_column('Programa', sa.Column('perfil_profesional', sa.TEXT(), nullable=True))
    op.add_column('Programa', sa.Column('perfil_egresado', sa.TEXT(), nullable=True))
    
    # Estados y clasificación
    op.add_column('Programa', sa.Column('estado', postgresql.ENUM(name='estado_programa', create_type=False), nullable=False, server_default=sa.text("'activo'")))
    op.add_column('Programa', sa.Column('duracion_tipo', postgresql.ENUM(name='duracion_programa', create_type=False), nullable=True))
    
    # Duración y estructura
    op.add_column('Programa', sa.Column('duracion_periodos', sa.INTEGER(), nullable=True))
    op.add_column('Programa', sa.Column('duracion_meses', sa.INTEGER(), nullable=True))
    op.add_column('Programa', sa.Column('creditos_totales', sa.INTEGER(), nullable=True))
    op.add_column('Programa', sa.Column('creditos_obligatorios', sa.INTEGER(), nullable=True))
    op.add_column('Programa', sa.Column('creditos_electivos', sa.INTEGER(), nullable=True))
    op.add_column('Programa', sa.Column('creditos_libres', sa.INTEGER(), nullable=True))
    op.add_column('Programa', sa.Column('numero_niveles', sa.INTEGER(), nullable=True))
    
    # Requisitos de ingreso
    op.add_column('Programa', sa.Column('titulo_bachiller_requerido', sa.Boolean(), nullable=True, server_default=sa.text('true')))
    op.add_column('Programa', sa.Column('puntaje_minimo_admision', sa.Numeric(precision=5, scale=2), nullable=True))
    op.add_column('Programa', sa.Column('requiere_examen_admision', sa.Boolean(), nullable=True, server_default=sa.text('false')))
    op.add_column('Programa', sa.Column('requiere_entrevista', sa.Boolean(), nullable=True, server_default=sa.text('false')))
    op.add_column('Programa', sa.Column('edad_minima_ingreso', sa.INTEGER(), nullable=True))
    op.add_column('Programa', sa.Column('documentos_requeridos', postgresql.JSON(astext_type=sa.Text()), nullable=True))
    
    # Requisitos de graduación
    op.add_column('Programa', sa.Column('creditos_minimos_graduacion', sa.INTEGER(), nullable=True))
    op.add_column('Programa', sa.Column('promedio_minimo_graduacion', sa.Numeric(precision=3, scale=2), nullable=True))
    op.add_column('Programa', sa.Column('requiere_trabajo_grado', sa.Boolean(), nullable=True, server_default=sa.text('false')))
    op.add_column('Programa', sa.Column('requiere_practica_profesional', sa.Boolean(), nullable=True, server_default=sa.text('false')))
    op.add_column('Programa', sa.Column('horas_practica_requeridas', sa.INTEGER(), nullable=True))
    op.add_column('Programa', sa.Column('requiere_suficiencia_idioma', sa.Boolean(), nullable=True, server_default=sa.text('false')))
    op.add_column('Programa', sa.Column('idiomas_requeridos', postgresql.JSON(astext_type=sa.Text()), nullable=True))
    
    # Costos
    op.add_column('Programa', sa.Column('tiene_costo', sa.Boolean(), nullable=True, server_default=sa.text('false')))
    op.add_column('Programa', sa.Column('costo_matricula', sa.Numeric(precision=12, scale=2), nullable=True))
    op.add_column('Programa', sa.Column('costo_por_periodo', sa.Numeric(precision=12, scale=2), nullable=True))
    op.add_column('Programa', sa.Column('costo_por_credito', sa.Numeric(precision=12, scale=2), nullable=True))
    op.add_column('Programa', sa.Column('costo_total_estimado', sa.Numeric(precision=12, scale=2), nullable=True))
    op.add_column('Programa', sa.Column('ofrece_becas', sa.Boolean(), nullable=True, server_default=sa.text('false')))
    op.add_column('Programa', sa.Column('ofrece_credito_educativo', sa.Boolean(), nullable=True, server_default=sa.text('false')))
    
    # Acreditación
    op.add_column('Programa', sa.Column('esta_acreditado', sa.Boolean(), nullable=True, server_default=sa.text('false')))
    op.add_column('Programa', sa.Column('fecha_acreditacion', sa.DATE(), nullable=True))
    op.add_column('Programa', sa.Column('vigencia_acreditacion_hasta', sa.DATE(), nullable=True))
    op.add_column('Programa', sa.Column('registro_calificado', sa.String(length=100), nullable=True))
    op.add_column('Programa', sa.Column('snies_codigo', sa.String(length=50), nullable=True))
    op.add_column('Programa', sa.Column('resolucion_aprobacion', sa.String(length=200), nullable=True))
    
    # Capacidad
    op.add_column('Programa', sa.Column('cupos_por_periodo', sa.INTEGER(), nullable=True))
    op.add_column('Programa', sa.Column('maximo_estudiantes_activos', sa.INTEGER(), nullable=True))
    op.add_column('Programa', sa.Column('permite_inscripcion', sa.Boolean(), nullable=True, server_default=sa.text('true')))
    
    # Configuración
    op.add_column('Programa', sa.Column('activo', sa.Boolean(), nullable=False, server_default=sa.text('true')))
    op.add_column('Programa', sa.Column('acepta_transferencias', sa.Boolean(), nullable=True, server_default=sa.text('true')))
    op.add_column('Programa', sa.Column('acepta_homologaciones', sa.Boolean(), nullable=True, server_default=sa.text('true')))
    op.add_column('Programa', sa.Column('permite_doble_titulacion', sa.Boolean(), nullable=True, server_default=sa.text('false')))
    
    # Metadata
    op.add_column('Programa', sa.Column('areas_conocimiento', postgresql.JSON(astext_type=sa.Text()), nullable=True))
    op.add_column('Programa', sa.Column('competencias_desarrolladas', postgresql.JSON(astext_type=sa.Text()), nullable=True))
    op.add_column('Programa', sa.Column('campo_ocupacional', sa.TEXT(), nullable=True))
    op.add_column('Programa', sa.Column('plan_estudios_url', sa.String(length=500), nullable=True))
    op.add_column('Programa', sa.Column('reglamento_url', sa.String(length=500), nullable=True))
    op.add_column('Programa', sa.Column('imagen_url', sa.String(length=500), nullable=True))
    op.add_column('Programa', sa.Column('video_presentacion_url', sa.String(length=500), nullable=True))
    op.add_column('Programa', sa.Column('tags', postgresql.JSON(astext_type=sa.Text()), nullable=True))
    
    # Auditoría
    op.add_column('Programa', sa.Column('fecha_creacion', postgresql.TIMESTAMP(), nullable=False, server_default=sa.text('now()')))
    op.add_column('Programa', sa.Column('fecha_actualizacion', postgresql.TIMESTAMP(), nullable=False, server_default=sa.text('now()')))
    op.add_column('Programa', sa.Column('fecha_apertura', sa.DATE(), nullable=True))
    op.add_column('Programa', sa.Column('fecha_cierre', sa.DATE(), nullable=True))
    
    # Crear índices y constraints para Programa
    op.create_index('idx_programa_codigo', 'Programa', ['codigo'], unique=True)
    op.create_index('idx_programa_coordinador', 'Programa', ['coordinador_id'])
    op.create_index('idx_programa_estado', 'Programa', ['estado'])
    op.create_index('idx_programa_nivel', 'Programa', ['nivel'])
    op.create_index('idx_programa_tipo', 'Programa', ['tipo'])
    
    # ==================== EXPANDIR TABLA GRUPO ====================
    
    # Período académico y organización
    op.add_column('Grupo', sa.Column('periodo_academico_id', sa.INTEGER(), nullable=True))
    op.create_foreign_key('fk_grupo_periodo', 'Grupo', 'periodos_academicos', ['periodo_academico_id'], ['id'], ondelete='SET NULL')
    
    op.add_column('Grupo', sa.Column('codigo_grupo', sa.String(length=50), nullable=True))
    op.add_column('Grupo', sa.Column('nivel_academico', sa.INTEGER(), nullable=True))
    op.add_column('Grupo', sa.Column('seccion', sa.String(length=10), nullable=True))
    op.add_column('Grupo', sa.Column('descripcion', sa.TEXT(), nullable=True))
    
    # Clasificación
    op.add_column('Grupo', sa.Column('estado', postgresql.ENUM(name='estado_grupo', create_type=False), nullable=False, server_default=sa.text("'programado'")))
    op.add_column('Grupo', sa.Column('tipo_grupo', postgresql.ENUM(name='tipo_grupo', create_type=False), nullable=True, server_default=sa.text("'regular'")))
    op.add_column('Grupo', sa.Column('modalidad_asistencia', postgresql.ENUM(name='modalidad_asistencia', create_type=False), nullable=True, server_default=sa.text("'obligatoria'")))
    op.add_column('Grupo', sa.Column('formato_evaluacion', postgresql.ENUM(name='formato_evaluacion', create_type=False), nullable=True))
    
    # Horario
    op.add_column('Grupo', sa.Column('hora_inicio', sa.Time(), nullable=True))
    op.add_column('Grupo', sa.Column('hora_fin', sa.Time(), nullable=True))
    op.add_column('Grupo', sa.Column('dias_semana', postgresql.JSON(astext_type=sa.Text()), nullable=True))
    op.add_column('Grupo', sa.Column('salon', sa.String(length=50), nullable=True))
    op.add_column('Grupo', sa.Column('edificio', sa.String(length=100), nullable=True))
    op.add_column('Grupo', sa.Column('ubicacion_virtual', sa.String(length=500), nullable=True))
    
    # Capacidad
    op.add_column('Grupo', sa.Column('capacidad_maxima', sa.INTEGER(), nullable=True))
    op.add_column('Grupo', sa.Column('capacidad_minima', sa.INTEGER(), nullable=True, server_default=sa.text('1')))
    op.add_column('Grupo', sa.Column('cupos_disponibles', sa.INTEGER(), nullable=True))
    op.add_column('Grupo', sa.Column('permite_lista_espera', sa.Boolean(), nullable=True, server_default=sa.text('false')))
    op.add_column('Grupo', sa.Column('maximo_lista_espera', sa.INTEGER(), nullable=True))
    
    # Fechas
    op.add_column('Grupo', sa.Column('fecha_inicio', sa.DATE(), nullable=True))
    op.add_column('Grupo', sa.Column('fecha_fin', sa.DATE(), nullable=True))
    op.add_column('Grupo', sa.Column('fecha_inicio_inscripciones', sa.DATE(), nullable=True))
    op.add_column('Grupo', sa.Column('fecha_fin_inscripciones', sa.DATE(), nullable=True))
    
    # Configuración académica
    op.add_column('Grupo', sa.Column('creditos', sa.INTEGER(), nullable=True, server_default=sa.text('0')))
    op.add_column('Grupo', sa.Column('horas_semanales', sa.INTEGER(), nullable=True))
    op.add_column('Grupo', sa.Column('porcentaje_asistencia_minimo', sa.Numeric(precision=5, scale=2), nullable=True, server_default=sa.text('80.0')))
    op.add_column('Grupo', sa.Column('calificacion_minima_aprobacion', sa.Numeric(precision=3, scale=2), nullable=True, server_default=sa.text('3.0')))
    op.add_column('Grupo', sa.Column('permite_recuperacion', sa.Boolean(), nullable=True, server_default=sa.text('true')))
    op.add_column('Grupo', sa.Column('numero_maximo_faltas', sa.INTEGER(), nullable=True))
    
    # Costos adicionales
    op.add_column('Grupo', sa.Column('tiene_costo_adicional', sa.Boolean(), nullable=True, server_default=sa.text('false')))
    op.add_column('Grupo', sa.Column('costo_adicional', sa.Numeric(precision=12, scale=2), nullable=True))
    
    # Configuración de acceso
    op.add_column('Grupo', sa.Column('activo', sa.Boolean(), nullable=False, server_default=sa.text('true')))
    op.add_column('Grupo', sa.Column('permite_inscripcion', sa.Boolean(), nullable=True, server_default=sa.text('true')))
    op.add_column('Grupo', sa.Column('requiere_aprobacion_inscripcion', sa.Boolean(), nullable=True, server_default=sa.text('false')))
    op.add_column('Grupo', sa.Column('es_visible', sa.Boolean(), nullable=True, server_default=sa.text('true')))
    op.add_column('Grupo', sa.Column('permite_autoregistro', sa.Boolean(), nullable=True, server_default=sa.text('false')))
    op.add_column('Grupo', sa.Column('codigo_acceso', sa.String(length=20), nullable=True))
    
    # Configuración de interacción
    op.add_column('Grupo', sa.Column('permite_chat', sa.Boolean(), nullable=True, server_default=sa.text('true')))
    op.add_column('Grupo', sa.Column('permite_foro', sa.Boolean(), nullable=True, server_default=sa.text('true')))
    op.add_column('Grupo', sa.Column('permite_comentarios', sa.Boolean(), nullable=True, server_default=sa.text('true')))
    op.add_column('Grupo', sa.Column('permite_material_estudiantes', sa.Boolean(), nullable=True, server_default=sa.text('false')))
    
    # Metadata
    op.add_column('Grupo', sa.Column('objetivos', sa.TEXT(), nullable=True))
    op.add_column('Grupo', sa.Column('notas_internas', sa.TEXT(), nullable=True))
    op.add_column('Grupo', sa.Column('recursos_adicionales', postgresql.JSON(astext_type=sa.Text()), nullable=True))
    op.add_column('Grupo', sa.Column('tags', postgresql.JSON(astext_type=sa.Text()), nullable=True))
    op.add_column('Grupo', sa.Column('imagen_url', sa.String(length=500), nullable=True))
    
    # Auditoría
    op.add_column('Grupo', sa.Column('fecha_creacion', postgresql.TIMESTAMP(), nullable=False, server_default=sa.text('now()')))
    op.add_column('Grupo', sa.Column('fecha_actualizacion', postgresql.TIMESTAMP(), nullable=False, server_default=sa.text('now()')))
    op.add_column('Grupo', sa.Column('creado_por_id', postgresql.UUID(as_uuid=True), nullable=True))
    op.add_column('Grupo', sa.Column('modificado_por_id', postgresql.UUID(as_uuid=True), nullable=True))
    
    op.create_foreign_key('fk_grupo_creado_por', 'Grupo', 'Usuario', ['creado_por_id'], ['usuario_id'], ondelete='SET NULL')
    op.create_foreign_key('fk_grupo_modificado_por', 'Grupo', 'Usuario', ['modificado_por_id'], ['usuario_id'], ondelete='SET NULL')
    
    # Crear índices para Grupo
    op.create_index('idx_grupo_programa', 'Grupo', ['programa_id'])
    op.create_index('idx_grupo_periodo', 'Grupo', ['periodo_academico_id'])
    op.create_index('idx_grupo_docente_tutor', 'Grupo', ['docente_tutor_id'])
    op.create_index('idx_grupo_estado', 'Grupo', ['estado'])
    op.create_index('idx_grupo_jornada', 'Grupo', ['jornada'])
    op.create_index('idx_grupo_activo', 'Grupo', ['activo'])
    op.create_index('idx_grupo_tipo', 'Grupo', ['tipo_grupo'])


def downgrade() -> None:
    """Downgrade schema - Eliminar campos agregados"""
    
    # ==================== GRUPO ====================
    op.drop_index('idx_grupo_tipo', table_name='Grupo')
    op.drop_index('idx_grupo_activo', table_name='Grupo')
    op.drop_index('idx_grupo_jornada', table_name='Grupo')
    op.drop_index('idx_grupo_estado', table_name='Grupo')
    op.drop_index('idx_grupo_docente_tutor', table_name='Grupo')
    op.drop_index('idx_grupo_periodo', table_name='Grupo')
    op.drop_index('idx_grupo_programa', table_name='Grupo')
    
    op.drop_constraint('fk_grupo_modificado_por', 'Grupo', type_='foreignkey')
    op.drop_constraint('fk_grupo_creado_por', 'Grupo', type_='foreignkey')
    op.drop_constraint('fk_grupo_periodo', 'Grupo', type_='foreignkey')
    
    # Eliminar columnas de Grupo
    grupo_columns = [
        'modificado_por_id', 'creado_por_id', 'fecha_actualizacion', 'fecha_creacion',
        'imagen_url', 'tags', 'recursos_adicionales', 'notas_internas', 'objetivos',
        'permite_material_estudiantes', 'permite_comentarios', 'permite_foro', 'permite_chat',
        'codigo_acceso', 'permite_autoregistro', 'es_visible', 'requiere_aprobacion_inscripcion',
        'permite_inscripcion', 'activo', 'costo_adicional', 'tiene_costo_adicional',
        'numero_maximo_faltas', 'permite_recuperacion', 'calificacion_minima_aprobacion',
        'porcentaje_asistencia_minimo', 'horas_semanales', 'creditos',
        'fecha_fin_inscripciones', 'fecha_inicio_inscripciones', 'fecha_fin', 'fecha_inicio',
        'maximo_lista_espera', 'permite_lista_espera', 'cupos_disponibles',
        'capacidad_minima', 'capacidad_maxima', 'ubicacion_virtual', 'edificio', 'salon',
        'dias_semana', 'hora_fin', 'hora_inicio', 'formato_evaluacion',
        'modalidad_asistencia', 'tipo_grupo', 'estado', 'descripcion', 'seccion',
        'nivel_academico', 'codigo_grupo', 'periodo_academico_id'
    ]
    for col in grupo_columns:
        op.drop_column('Grupo', col)
    
    # ==================== PROGRAMA ====================
    op.drop_index('idx_programa_tipo', table_name='Programa')
    op.drop_index('idx_programa_nivel', table_name='Programa')
    op.drop_index('idx_programa_estado', table_name='Programa')
    op.drop_index('idx_programa_coordinador', table_name='Programa')
    op.drop_index('idx_programa_codigo', table_name='Programa')
    
    op.drop_constraint('fk_programa_coordinador', 'Programa', type_='foreignkey')
    
    # Eliminar columnas de Programa
    programa_columns = [
        'fecha_cierre', 'fecha_apertura', 'fecha_actualizacion', 'fecha_creacion',
        'tags', 'video_presentacion_url', 'imagen_url', 'reglamento_url',
        'plan_estudios_url', 'campo_ocupacional', 'competencias_desarrolladas',
        'areas_conocimiento', 'permite_doble_titulacion', 'acepta_homologaciones',
        'acepta_transferencias', 'activo', 'permite_inscripcion',
        'maximo_estudiantes_activos', 'cupos_por_periodo', 'resolucion_aprobacion',
        'snies_codigo', 'registro_calificado', 'vigencia_acreditacion_hasta',
        'fecha_acreditacion', 'esta_acreditado', 'ofrece_credito_educativo',
        'ofrece_becas', 'costo_total_estimado', 'costo_por_credito',
        'costo_por_periodo', 'costo_matricula', 'tiene_costo',
        'idiomas_requeridos', 'requiere_suficiencia_idioma', 'horas_practica_requeridas',
        'requiere_practica_profesional', 'requiere_trabajo_grado',
        'promedio_minimo_graduacion', 'creditos_minimos_graduacion',
        'documentos_requeridos', 'edad_minima_ingreso', 'requiere_entrevista',
        'requiere_examen_admision', 'puntaje_minimo_admision',
        'titulo_bachiller_requerido', 'numero_niveles', 'creditos_libres',
        'creditos_electivos', 'creditos_obligatorios', 'creditos_totales',
        'duracion_meses', 'duracion_periodos', 'duracion_tipo', 'estado',
        'perfil_egresado', 'perfil_profesional', 'objetivos', 'vision',
        'mision', 'codigo', 'coordinador_id'
    ]
    for col in programa_columns:
        op.drop_column('Programa', col)
    
    # ==================== CURSO ====================
    op.drop_index('idx_curso_categoria', table_name='Curso')
    op.drop_index('idx_curso_tipo', table_name='Curso')
    op.drop_index('idx_curso_nivel_dificultad', table_name='Curso')
    op.drop_index('idx_curso_estado', table_name='Curso')
    
    # Eliminar columnas de Curso
    curso_columns = [
        'fecha_actualizacion', 'fecha_creacion', 'imagen_url', 'tags',
        'recursos_adicionales', 'bibliografia', 'syllabus_url',
        'tipo_trabajo_final', 'requiere_trabajo_final', 'genera_certificado',
        'permite_calificacion_entre_pares', 'permite_comentarios', 'permite_foros',
        'numero_maximo_faltas', 'permite_habilitacion', 'permite_recuperacion',
        'porcentaje_asistencia_minimo', 'calificacion_minima_aprobacion',
        'porcentaje_descuento', 'permite_becas', 'costo_total', 'costo_mensual',
        'costo_matricula', 'tiene_costo', 'promedio_minimo_requerido',
        'creditos_minimos_requeridos', 'requiere_nivelacion', 'correquisitos_ids',
        'prerequisitos_ids', 'maximo_lista_espera', 'permite_lista_espera',
        'cupos_disponibles', 'fecha_limite_retiro', 'fecha_inicio_retiro',
        'fecha_limite_inscripcion', 'idioma', 'estado', 'categoria_curso',
        'tipo_curso', 'nivel_dificultad', 'horas_autonomas', 'horas_laboratorio',
        'horas_practicas', 'horas_teoricas'
    ]
    for col in curso_columns:
        op.drop_column('Curso', col)
    
    # ==================== ELIMINAR ENUMs ====================
    op.execute('DROP TYPE IF EXISTS formato_evaluacion')
    op.execute('DROP TYPE IF EXISTS modalidad_asistencia')
    op.execute('DROP TYPE IF EXISTS tipo_grupo')
    op.execute('DROP TYPE IF EXISTS estado_grupo')
    op.execute('DROP TYPE IF EXISTS duracion_programa')
    op.execute('DROP TYPE IF EXISTS estado_programa')
    op.execute('DROP TYPE IF EXISTS idioma_curso')
    op.execute('DROP TYPE IF EXISTS estado_curso')
    op.execute('DROP TYPE IF EXISTS categoria_curso')
    op.execute('DROP TYPE IF EXISTS tipo_curso')
    op.execute('DROP TYPE IF EXISTS nivel_dificultad')
