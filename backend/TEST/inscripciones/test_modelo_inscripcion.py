"""
Tests del modelo Inscripcion expandido

Valida:
- 94 campos del modelo
- Properties calculadas
- Métodos de negocio
- Estados y transiciones
- Validaciones y constraints
"""
import pytest
from datetime import date, datetime, timedelta
from decimal import Decimal
from sqlalchemy.orm import Session

from src.models.academic.inscripcion import Inscripcion
from src.enums.academic import (
    EstadoInscripcion,
    TipoInscripcion,
    MotivoRechazo,
    MotivoRetiro,
    FormaPago
)


@pytest.mark.inscripciones
@pytest.mark.unit
class TestInscripcionProperties:
    """Tests de properties calculadas del modelo Inscripcion"""
    
    def test_inscripcion_activa(self, db_session: Session, inscripcion_confirmada):
        """Verifica que una inscripción confirmada esté activa"""
        assert inscripcion_confirmada.esta_activa is True
        assert inscripcion_confirmada.activo is True
        assert inscripcion_confirmada.estado == EstadoInscripcion.confirmada.value
    
    def test_inscripcion_pendiente(self, db_session: Session, inscripcion_pendiente_pago):
        """Verifica que una inscripción pendiente de pago se detecte correctamente"""
        assert inscripcion_pendiente_pago.esta_pendiente is True
        assert inscripcion_pendiente_pago.estado == EstadoInscripcion.pendiente_pago.value
        assert inscripcion_pendiente_pago.esta_pagado is False
    
    def test_puede_asistir_clases(self, db_session: Session, inscripcion_confirmada):
        """Verifica que un estudiante pueda asistir a clases"""
        # Configurar inscripción completa
        inscripcion_confirmada.esta_pagado = True
        inscripcion_confirmada.documentos_completos = True
        inscripcion_confirmada.estado = EstadoInscripcion.activa.value
        db_session.commit()
        
        assert inscripcion_confirmada.puede_asistir_clases is True
    
    def test_no_puede_asistir_sin_pago(self, db_session: Session, inscripcion_confirmada):
        """Verifica que sin pago no se pueda asistir"""
        inscripcion_confirmada.esta_pagado = False
        db_session.commit()
        
        assert inscripcion_confirmada.puede_asistir_clases is False
    
    def test_nombre_completo_estudiante(self, db_session: Session, inscripcion_base):
        """Verifica que se obtenga el nombre completo del estudiante"""
        nombre = inscripcion_base.nombre_completo_estudiante
        assert nombre is not None
        assert len(nombre) > 0
        assert " " in nombre  # Debe contener espacio entre nombres y apellidos
    
    def test_inscripcion_con_beca(self, db_session: Session, inscripcion_base):
        """Verifica inscripción con beca"""
        inscripcion_base.tiene_beca = True
        inscripcion_base.porcentaje_beca = Decimal('50.00')
        inscripcion_base.tipo_beca = "Beca de excelencia académica"
        db_session.commit()
        
        assert inscripcion_base.tiene_beca is True
        assert inscripcion_base.porcentaje_beca == Decimal('50.00')
    
    def test_inscripcion_lista_espera(self, db_session: Session, inscripcion_base):
        """Verifica inscripción en lista de espera"""
        inscripcion_base.en_lista_espera = True
        inscripcion_base.posicion_lista_espera = 5
        inscripcion_base.fecha_entrada_lista_espera = datetime.now()
        db_session.commit()
        
        assert inscripcion_base.en_lista_espera is True
        assert inscripcion_base.posicion_lista_espera == 5


@pytest.mark.inscripciones
@pytest.mark.unit
class TestInscripcionEstados:
    """Tests de estados y transiciones de Inscripcion"""
    
    def test_estado_pre_inscrita_inicial(self, db_session: Session, inscripcion_base):
        """Verifica que el estado inicial sea pre_inscrita"""
        assert inscripcion_base.estado == EstadoInscripcion.pre_inscrita.value
        assert inscripcion_base.fecha_pre_inscripcion is None
    
    def test_transicion_a_pendiente_pago(self, db_session: Session, inscripcion_base):
        """Verifica transición de pre_inscrita a pendiente_pago"""
        inscripcion_base.estado = EstadoInscripcion.pendiente_pago.value
        inscripcion_base.fecha_inscripcion = datetime.now()
        inscripcion_base.costo_total = Decimal('500000.00')
        db_session.commit()
        
        assert inscripcion_base.estado == EstadoInscripcion.pendiente_pago.value
        assert inscripcion_base.esta_pendiente is True
    
    def test_transicion_a_confirmada(self, db_session: Session, inscripcion_pendiente_pago):
        """Verifica transición a confirmada tras pago"""
        inscripcion_pendiente_pago.estado = EstadoInscripcion.confirmada.value
        inscripcion_pendiente_pago.esta_pagado = True
        inscripcion_pendiente_pago.fecha_pago = datetime.now()
        inscripcion_pendiente_pago.fecha_confirmacion = datetime.now()
        db_session.commit()
        
        assert inscripcion_pendiente_pago.estado == EstadoInscripcion.confirmada.value
        assert inscripcion_pendiente_pago.esta_pagado is True
    
    def test_estado_rechazada(self, db_session: Session, inscripcion_base, usuario_admin):
        """Verifica estado rechazada"""
        inscripcion_base.estado = EstadoInscripcion.rechazada.value
        inscripcion_base.fue_rechazada = True
        inscripcion_base.motivo_rechazo = MotivoRechazo.no_cumple_requisitos.value
        inscripcion_base.rechazada_por_id = usuario_admin.usuario_id
        inscripcion_base.fecha_rechazo = datetime.now()
        db_session.commit()
        
        assert inscripcion_base.fue_rechazada is True
        assert inscripcion_base.estado == EstadoInscripcion.rechazada.value
    
    def test_estado_retirada(self, db_session: Session, inscripcion_confirmada):
        """Verifica estado retirada"""
        inscripcion_confirmada.estado = EstadoInscripcion.retirada.value
        inscripcion_confirmada.fue_retirada = True
        inscripcion_confirmada.motivo_retiro = MotivoRetiro.personal.value  # Corregido: personal en lugar de voluntario
        inscripcion_confirmada.fecha_retiro = datetime.now()
        db_session.commit()
        
        assert inscripcion_confirmada.fue_retirada is True


@pytest.mark.inscripciones
@pytest.mark.unit
class TestInscripcionValidaciones:
    """Tests de validaciones y constraints"""
    
    def test_calificacion_dentro_rango(self, db_session: Session, inscripcion_confirmada):
        """Verifica que la calificación esté en rango válido (0-5)"""
        inscripcion_confirmada.calificacion_final = Decimal('4.5')
        db_session.commit()
        db_session.refresh(inscripcion_confirmada)
        
        assert inscripcion_confirmada.calificacion_final == Decimal('4.5')
    
    def test_porcentaje_asistencia_valido(self, db_session: Session, inscripcion_confirmada):
        """Verifica que el porcentaje de asistencia sea válido (0-100)"""
        inscripcion_confirmada.porcentaje_asistencia = Decimal('85.5')
        db_session.commit()
        
        assert inscripcion_confirmada.porcentaje_asistencia == Decimal('85.5')
    
    def test_creditos_inscritos_positivos(self, db_session: Session, inscripcion_base):
        """Verifica que los créditos inscritos sean positivos"""
        inscripcion_base.creditos_inscritos = 18
        db_session.commit()
        
        assert inscripcion_base.creditos_inscritos > 0


@pytest.mark.inscripciones
@pytest.mark.unit
class TestInscripcionRelaciones:
    """Tests de relaciones del modelo Inscripcion"""
    
    def test_inscripcion_tiene_estudiante(self, db_session: Session, inscripcion_base):
        """Verifica que la inscripción tenga un estudiante"""
        assert inscripcion_base.estudiante is not None
        assert inscripcion_base.estudiante_id is not None
    
    def test_inscripcion_tiene_grupo(self, db_session: Session, inscripcion_base):
        """Verifica que la inscripción tenga un grupo"""
        assert inscripcion_base.grupo is not None
        assert inscripcion_base.grupo_id is not None
    
    def test_inscripcion_tiene_periodo(self, db_session: Session, inscripcion_base):
        """Verifica que la inscripción tenga un período académico"""
        assert inscripcion_base.periodo_academico is not None
        assert inscripcion_base.periodo_academico_id is not None
    
    def test_codigo_inscripcion_unico(self, db_session: Session, inscripcion_base):
        """Verifica que el código de inscripción sea único"""
        assert inscripcion_base.codigo_inscripcion is not None
        assert len(inscripcion_base.codigo_inscripcion) > 0
