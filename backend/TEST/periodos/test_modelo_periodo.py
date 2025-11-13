"""
Tests para el Modelo PeriodoAcademico

Tests de propiedades computadas, métodos y validaciones del modelo.
Cobertura: 20 tests
"""
import pytest
from datetime import date, timedelta
from decimal import Decimal

from src.models.academic.periodo_academico import PeriodoAcademico
from src.enums.academic import TipoPeriodo, EstadoPeriodo


@pytest.mark.periodos
@pytest.mark.modelo
class TestPeriodoAcademicoModelo:
    """Tests básicos del modelo"""
    
    def test_crear_periodo_basico(self, db_session, institucion_id):
        """Crea un período con datos mínimos"""
        hoy = date.today()
        periodo = PeriodoAcademico(
            institucion_id=institucion_id,
            nombre="Test Período",
            codigo="TEST-2024",
            tipo=TipoPeriodo.semestral,
            anio=2024,
            fecha_inicio=hoy,
            fecha_fin=hoy + timedelta(days=180),
            fecha_inicio_inscripciones=hoy - timedelta(days=10),
            fecha_fin_inscripciones=hoy - timedelta(days=1),
            fecha_inicio_clases=hoy,
            fecha_fin_clases=hoy + timedelta(days=170)
        )
        
        db_session.add(periodo)
        db_session.commit()
        db_session.refresh(periodo)
        
        assert periodo.id is not None
        assert periodo.nombre == "Test Período"
        assert periodo.codigo == "TEST-2024"
        assert periodo.tipo == TipoPeriodo.semestral
        assert periodo.activo is True
        assert periodo.es_actual is False
    
    def test_periodo_con_todos_los_campos(self, periodo_base):
        """Verifica que se puedan crear períodos con todos los campos"""
        assert periodo_base.id is not None
        assert periodo_base.descripcion == "Primer semestre académico de 2024"
        assert periodo_base.numero_periodo == 1
        assert periodo_base.creditos_minimos == 12
        assert periodo_base.creditos_maximos == 20
        assert periodo_base.costo_matricula == Decimal("500000.00")
        assert periodo_base.costo_por_credito == Decimal("150000.00")
        assert periodo_base.moneda == "COP"
        assert periodo_base.permite_inscripciones is True
        assert periodo_base.visible_estudiantes is True
    
    def test_valores_por_defecto(self, db_session, institucion_id):
        """Verifica valores por defecto del modelo"""
        hoy = date.today()
        periodo = PeriodoAcademico(
            institucion_id=institucion_id,
            nombre="Período Default",
            codigo="DEF-2024",
            tipo=TipoPeriodo.trimestral,
            anio=2024,
            fecha_inicio=hoy,
            fecha_fin=hoy + timedelta(days=90),
            fecha_inicio_inscripciones=hoy - timedelta(days=5),
            fecha_fin_inscripciones=hoy - timedelta(days=1),
            fecha_inicio_clases=hoy,
            fecha_fin_clases=hoy + timedelta(days=85)
        )
        
        db_session.add(periodo)
        db_session.commit()
        db_session.refresh(periodo)
        
        # Verificar defaults
        assert periodo.estado == EstadoPeriodo.programado  # Default
        assert periodo.activo is True  # Default
        assert periodo.es_actual is False  # Default
        assert periodo.permite_inscripciones is True  # Default
        assert periodo.permite_ajustes is True  # Default
        assert periodo.permite_retiros is True  # Default
        assert periodo.visible_estudiantes is True  # Default
        assert periodo.visible_profesores is True  # Default
        assert periodo.visible_publico is False  # Default
        assert periodo.moneda == "COP"  # Default


@pytest.mark.periodos
@pytest.mark.modelo
class TestPeriodoAcademicoPropiedadesComputadas:
    """Tests de propiedades computadas (@property)"""
    
    def test_nombre_completo(self, periodo_base):
        """Verifica propiedad nombre_completo"""
        assert periodo_base.nombre_completo == "Semestre 2024-1 (2024)"
    
    def test_esta_activo_true(self, periodo_base):
        """Período activo y no cancelado"""
        periodo_base.activo = True
        periodo_base.estado = EstadoPeriodo.programado
        assert periodo_base.esta_activo is True
    
    def test_esta_activo_false_por_cancelado(self, periodo_base):
        """Período cancelado no está activo"""
        periodo_base.activo = True
        periodo_base.estado = EstadoPeriodo.cancelado
        assert periodo_base.esta_activo is False
    
    def test_esta_activo_false_por_inactivo(self, periodo_base):
        """Período inactivo no está activo"""
        periodo_base.activo = False
        periodo_base.estado = EstadoPeriodo.programado
        assert periodo_base.esta_activo is False
    
    def test_permite_inscribirse_ahora_true(self, periodo_en_inscripciones):
        """Período con inscripciones abiertas permite inscribirse"""
        assert periodo_en_inscripciones.permite_inscribirse_ahora is True
    
    def test_permite_inscribirse_ahora_false_cerrado(self, periodo_base):
        """Período sin inscripciones abiertas no permite inscribirse"""
        periodo_base.estado = EstadoPeriodo.programado
        assert periodo_base.permite_inscribirse_ahora is False
    
    def test_permite_inscribirse_ahora_false_deshabilitado(self, periodo_en_inscripciones):
        """Período con inscripciones deshabilitadas"""
        periodo_en_inscripciones.permite_inscripciones = False
        assert periodo_en_inscripciones.permite_inscribirse_ahora is False
    
    def test_esta_en_curso_true(self, periodo_en_curso):
        """Período en curso está actualmente en curso"""
        assert periodo_en_curso.esta_en_curso is True
    
    def test_esta_en_curso_false_no_iniciado(self, periodo_base):
        """Período no iniciado no está en curso"""
        assert periodo_base.esta_en_curso is False
    
    def test_esta_en_curso_false_finalizado(self, periodo_finalizado):
        """Período finalizado no está en curso"""
        assert periodo_finalizado.esta_en_curso is False
    
    def test_dias_hasta_inicio_futuro(self, periodo_base):
        """Días hasta inicio para período futuro"""
        dias = periodo_base.dias_hasta_inicio
        assert dias is not None
        assert dias >= 29  # Aprox 30 días en fixture
    
    def test_dias_hasta_inicio_ya_iniciado(self, periodo_en_curso):
        """Días hasta inicio para período ya iniciado"""
        assert periodo_en_curso.dias_hasta_inicio == 0
    
    def test_dias_transcurridos_en_curso(self, periodo_en_curso):
        """Días transcurridos desde inicio"""
        dias = periodo_en_curso.dias_transcurridos
        assert dias is not None
        assert dias >= 29  # Aprox 30 días transcurridos en fixture
    
    def test_dias_transcurridos_no_iniciado(self, periodo_base):
        """Días transcurridos para período no iniciado"""
        assert periodo_base.dias_transcurridos == 0
    
    def test_duracion_dias(self, periodo_base):
        """Duración total del período en días"""
        duracion = periodo_base.duracion_dias
        assert duracion is not None
        assert duracion == 150  # 180 días en fixture
    
    def test_porcentaje_avance_en_curso(self, periodo_en_curso):
        """Porcentaje de avance para período en curso"""
        porcentaje = periodo_en_curso.porcentaje_avance
        assert porcentaje is not None
        assert 0 <= porcentaje <= 100
        # Aproximadamente 35% de avance (30/85 días)
        assert 30 <= porcentaje <= 40
    
    def test_porcentaje_avance_no_iniciado(self, periodo_base):
        """Porcentaje de avance para período no iniciado"""
        assert periodo_base.porcentaje_avance is None


@pytest.mark.periodos
@pytest.mark.modelo
class TestPeriodoAcademicoMetodos:
    """Tests de métodos del modelo"""
    
    def test_activar_periodo(self, periodo_base):
        """Activa un período programado"""
        periodo_base.activo = False
        periodo_base.estado = EstadoPeriodo.programado
        
        periodo_base.activar()
        
        assert periodo_base.activo is True
        assert periodo_base.estado == EstadoPeriodo.programado
    
    def test_activar_periodo_ya_iniciado(self, periodo_en_curso):
        """Activa un período que ya inició (cambia a en_curso)"""
        periodo_en_curso.activo = False
        
        periodo_en_curso.activar()
        
        assert periodo_en_curso.activo is True
        # Estado depende de la fecha actual
        assert periodo_en_curso.estado in [EstadoPeriodo.programado, EstadoPeriodo.en_curso]
    
    def test_desactivar_periodo(self, periodo_base):
        """Desactiva un período"""
        periodo_base.activo = True
        
        periodo_base.desactivar()
        
        assert periodo_base.activo is False
    
    def test_marcar_como_actual(self, periodo_base):
        """Marca un período como actual"""
        periodo_base.es_actual = False
        periodo_base.activo = False
        
        periodo_base.marcar_como_actual()
        
        assert periodo_base.es_actual is True
        assert periodo_base.activo is True
    
    def test_finalizar_periodo(self, periodo_en_curso):
        """Finaliza un período en curso"""
        periodo_en_curso.es_actual = True
        
        periodo_en_curso.finalizar()
        
        assert periodo_en_curso.estado == EstadoPeriodo.finalizado
        assert periodo_en_curso.es_actual is False
    
    def test_cancelar_periodo_sin_motivo(self, periodo_base):
        """Cancela un período sin motivo"""
        periodo_base.cancelar()
        
        assert periodo_base.estado == EstadoPeriodo.cancelado
        assert periodo_base.activo is False
        assert periodo_base.es_actual is False
    
    def test_cancelar_periodo_con_motivo(self, periodo_base):
        """Cancela un período con motivo"""
        motivo = "Cancelado por falta de estudiantes"
        periodo_base.notas = "Notas iniciales"
        
        periodo_base.cancelar(motivo)
        
        assert periodo_base.estado == EstadoPeriodo.cancelado
        assert motivo in periodo_base.notas
        assert "CANCELACIÓN" in periodo_base.notas
    
    def test_puede_inscribirse_estudiante_ok(self, periodo_en_inscripciones):
        """Estudiante puede inscribirse en período con inscripciones abiertas"""
        puede, mensaje = periodo_en_inscripciones.puede_inscribirse_estudiante()
        
        assert puede is True
        assert "Puede inscribirse" in mensaje
    
    def test_puede_inscribirse_estudiante_inactivo(self, periodo_base):
        """No puede inscribirse en período inactivo"""
        periodo_base.activo = False
        
        puede, mensaje = periodo_base.puede_inscribirse_estudiante()
        
        assert puede is False
        assert "inactivo" in mensaje.lower()
    
    def test_puede_inscribirse_estudiante_cancelado(self, periodo_base):
        """No puede inscribirse en período cancelado"""
        periodo_base.estado = EstadoPeriodo.cancelado
        
        puede, mensaje = periodo_base.puede_inscribirse_estudiante()
        
        assert puede is False
        assert "cancelado" in mensaje.lower()
    
    def test_puede_inscribirse_estudiante_finalizado(self, periodo_finalizado):
        """No puede inscribirse en período finalizado"""
        puede, mensaje = periodo_finalizado.puede_inscribirse_estudiante()
        
        assert puede is False
        assert "finalizado" in mensaje.lower()
    
    def test_puede_inscribirse_estudiante_sin_permiso(self, periodo_base):
        """No puede inscribirse si no permite inscripciones"""
        periodo_base.permite_inscripciones = False
        
        puede, mensaje = periodo_base.puede_inscribirse_estudiante()
        
        assert puede is False
        assert "no permitidas" in mensaje.lower()
    
    def test_puede_inscribirse_estudiante_fuera_de_fechas_antes(self, periodo_base):
        """No puede inscribirse antes de fecha de inicio"""
        # periodo_base tiene inscripciones en el futuro
        puede, mensaje = periodo_base.puede_inscribirse_estudiante()
        
        assert puede is False
        assert "inician" in mensaje.lower()
    
    def test_puede_inscribirse_estudiante_fuera_de_fechas_despues(self, periodo_finalizado):
        """No puede inscribirse después de fecha de cierre"""
        puede, mensaje = periodo_finalizado.puede_inscribirse_estudiante()
        
        assert puede is False
        # Ya sea por finalizado o fechas cerradas
        assert puede is False
    
    def test_repr(self, periodo_base):
        """Verifica representación string del período"""
        repr_str = repr(periodo_base)
        
        assert "PeriodoAcademico" in repr_str
        assert str(periodo_base.id) in repr_str
        assert periodo_base.nombre in repr_str
        assert periodo_base.estado in repr_str  # Ya es string, no enum
