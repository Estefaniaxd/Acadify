from ...db.base_class import Base
from sqlalchemy import Column, text, ForeignKey, String, UniqueConstraint, Index, Boolean, Integer, DECIMAL, DATE
from sqlalchemy.dialects.postgresql import UUID, ENUM, TEXT, JSON, TIMESTAMP
from ...enums.academic.programa_enums import NivelPrograma, TipoPrograma, EstadoPrograma, DuracionPrograma
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func


class Programa(Base):
    """
    Modelo de Programa Académico
    
    Representa un programa académico completo con toda su información:
    - Identificación y básicos
    - Requisitos de ingreso
    - Estructura curricular (créditos, niveles)
    - Requisitos de graduación
    - Costos y financiación
    - Acreditación y registros
    - Información institucional
    """
    __tablename__ = "Programa"

    __table_args__ = (
        UniqueConstraint("institucion_id", "nombre", name="uq_programa_nombre"),
        Index("idx_programa_institucion", "institucion_id"),
        Index("idx_programa_coordinador", "coordinador_id"),
        Index("idx_programa_estado", "estado"),
        Index("idx_programa_nivel", "nivel"),
    )

    # ========================================================================
    # IDENTIFICACIÓN
    # ========================================================================
    
    programa_id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text('gen_random_uuid()'),
    )
    
    institucion_id = Column(
        UUID(as_uuid=True),
        ForeignKey("Institucion.institucion_id", ondelete="CASCADE"),
        nullable=False,
    )
    
    coordinador_id = Column(
        UUID(as_uuid=True),
        ForeignKey("Coordinador.coordinador_id", ondelete="SET NULL"),
        nullable=True,
    )
    
    # Información básica
    nombre = Column(String(100), nullable=False)
    codigo = Column(String(50), nullable=True)  # Código interno del programa
    descripcion = Column(TEXT, nullable=True)
    
    # Clasificación
    nivel = Column(
        ENUM(NivelPrograma, name="nivel_programa", create_type=False),
        nullable=False,
    )
    
    tipo = Column(
        ENUM(TipoPrograma, name="tipo_programa", create_type=False),
        nullable=False,
    )
    
    estado = Column(
        ENUM(EstadoPrograma, name="estado_programa", create_type=False),
        nullable=False,
        default=EstadoPrograma.activo,
        server_default=text("'activo'"),
    )
    
    # ========================================================================
    # MISIÓN, VISIÓN Y PERFILES
    # ========================================================================
    
    mision = Column(TEXT, nullable=True)
    vision = Column(TEXT, nullable=True)
    objetivos = Column(TEXT, nullable=True)
    perfil_profesional = Column(TEXT, nullable=True)
    perfil_egresado = Column(TEXT, nullable=True)
    campo_ocupacional = Column(TEXT, nullable=True)  # Campo laboral del egresado
    
    # ========================================================================
    # DURACIÓN Y ESTRUCTURA CURRICULAR
    # ========================================================================
    
    duracion_tipo = Column(
        ENUM(DuracionPrograma, name="duracion_programa", create_type=False),
        nullable=True,
    )
    
    duracion_periodos = Column(Integer, nullable=True)  # Número de períodos (ej: 10 semestres)
    duracion_meses = Column(Integer, nullable=True)  # Duración total en meses
    numero_niveles = Column(Integer, nullable=True)  # Número de niveles/semestres
    
    # Créditos
    creditos_totales = Column(Integer, nullable=True)
    creditos_obligatorios = Column(Integer, nullable=True)
    creditos_electivos = Column(Integer, nullable=True)
    creditos_libres = Column(Integer, nullable=True)
    
    # ========================================================================
    # REQUISITOS DE INGRESO
    # ========================================================================
    
    titulo_bachiller_requerido = Column(Boolean, default=True, nullable=True)
    puntaje_minimo_admision = Column(DECIMAL(5, 2), nullable=True)  # Puntaje de examen de estado
    requiere_examen_admision = Column(Boolean, default=False, nullable=True)
    requiere_entrevista = Column(Boolean, default=False, nullable=True)
    edad_minima_ingreso = Column(Integer, nullable=True)
    documentos_requeridos = Column(JSON, nullable=True)  # Lista de documentos necesarios
    
    # ========================================================================
    # REQUISITOS DE GRADUACIÓN
    # ========================================================================
    
    creditos_minimos_graduacion = Column(Integer, nullable=True)
    promedio_minimo_graduacion = Column(DECIMAL(3, 2), nullable=True)
    requiere_trabajo_grado = Column(Boolean, default=False, nullable=True)
    requiere_practica_profesional = Column(Boolean, default=False, nullable=True)
    horas_practica_requeridas = Column(Integer, nullable=True)
    requiere_suficiencia_idioma = Column(Boolean, default=False, nullable=True)
    idiomas_requeridos = Column(JSON, nullable=True)  # Lista de idiomas requeridos
    
    # ========================================================================
    # COSTOS Y FINANCIACIÓN
    # ========================================================================
    
    tiene_costo = Column(Boolean, default=False, nullable=True)
    costo_matricula = Column(DECIMAL(12, 2), nullable=True)
    costo_por_periodo = Column(DECIMAL(12, 2), nullable=True)
    costo_por_credito = Column(DECIMAL(10, 2), nullable=True)
    costo_total_estimado = Column(DECIMAL(12, 2), nullable=True)
    ofrece_becas = Column(Boolean, default=False, nullable=True)
    ofrece_credito_educativo = Column(Boolean, default=False, nullable=True)
    
    # ========================================================================
    # ACREDITACIÓN Y REGISTROS
    # ========================================================================
    
    esta_acreditado = Column(Boolean, default=False, nullable=True)
    fecha_acreditacion = Column(DATE, nullable=True)
    vigencia_acreditacion_hasta = Column(DATE, nullable=True)
    registro_calificado = Column(String(100), nullable=True)  # Número de registro calificado
    snies_codigo = Column(String(20), nullable=True)  # Código SNIES (Colombia)
    resolucion_aprobacion = Column(String(100), nullable=True)  # Resolución de aprobación
    
    # ========================================================================
    # CAPACIDAD Y CUPOS
    # ========================================================================
    
    cupos_por_periodo = Column(Integer, nullable=True)
    maximo_estudiantes_activos = Column(Integer, nullable=True)
    permite_inscripcion = Column(Boolean, default=True, nullable=True)
    activo = Column(Boolean, default=True, nullable=False)
    
    # ========================================================================
    # POLÍTICAS ACADÉMICAS
    # ========================================================================
    
    acepta_transferencias = Column(Boolean, default=True, nullable=True)
    acepta_homologaciones = Column(Boolean, default=True, nullable=True)
    permite_doble_titulacion = Column(Boolean, default=False, nullable=True)
    
    # ========================================================================
    # INFORMACIÓN COMPLEMENTARIA
    # ========================================================================
    
    areas_conocimiento = Column(JSON, nullable=True)  # Áreas de conocimiento que cubre
    competencias_desarrolladas = Column(JSON, nullable=True)  # Competencias que desarrolla
    plan_estudios_url = Column(String(500), nullable=True)  # URL del plan de estudios
    reglamento_url = Column(String(500), nullable=True)  # URL del reglamento
    imagen_url = Column(String(500), nullable=True)  # Imagen del programa
    video_presentacion_url = Column(String(500), nullable=True)  # Video de presentación
    tags = Column(JSON, nullable=True)  # Etiquetas para búsqueda
    
    # ========================================================================
    # FECHAS Y AUDITORÍA
    # ========================================================================
    
    fecha_apertura = Column(DATE, nullable=True)  # Fecha de apertura del programa
    fecha_cierre = Column(DATE, nullable=True)  # Fecha de cierre (si aplica)
    fecha_creacion = Column(TIMESTAMP, server_default=func.now(), nullable=False)
    fecha_actualizacion = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # ========================================================================
    # RELACIONES
    # ========================================================================
    
    institucion = relationship("Institucion", backref="programas")
    coordinador = relationship("Coordinador", backref="programas_coordinados")
    estudiantes = relationship("Estudiante", backref="programa", passive_deletes=True)
    grupos = relationship("Grupo", backref="programa")
    cursos = relationship("Curso", backref="programa")
    
    # ========================================================================
    # PROPIEDADES CALCULADAS
    # ========================================================================
    
    @property
    def duracion_total_meses(self) -> int:
        """Calcula la duración total en meses si no está especificada"""
        if self.duracion_meses:
            return self.duracion_meses
        
        if self.duracion_periodos and self.duracion_tipo:
            meses_por_periodo = {
                'semestral': 6,
                'trimestral': 3,
                'cuatrimestral': 4,
                'anual': 12,
                'bianual': 24,
            }
            return self.duracion_periodos * meses_por_periodo.get(self.duracion_tipo.value, 0)
        
        return 0
    
    @property
    def total_estudiantes_activos(self) -> int:
        """Cuenta el número total de estudiantes activos en el programa"""
        return len([e for e in self.estudiantes if e.activo])
    
    @property
    def tiene_cupos_disponibles(self) -> bool:
        """Verifica si hay cupos disponibles"""
        if not self.cupos_por_periodo:
            return True  # Sin límite de cupos
        return self.total_estudiantes_activos < self.cupos_por_periodo
    
    @property
    def esta_vigente_acreditacion(self) -> bool:
        """Verifica si la acreditación está vigente"""
        if not self.esta_acreditado or not self.vigencia_acreditacion_hasta:
            return False
        from datetime import date
        return date.today() <= self.vigencia_acreditacion_hasta
    
    def __repr__(self):
        return f"<Programa(id={self.programa_id}, nombre='{self.nombre}', nivel='{self.nivel}', institucion_id={self.institucion_id})>"
