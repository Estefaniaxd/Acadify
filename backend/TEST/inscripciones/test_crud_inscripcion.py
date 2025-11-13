"""
Tests CRUD Inscripción

Tests completos de operaciones CRUD siguiendo:
- Clean Code: nombres descriptivos, funciones pequeñas
- SOLID: SRP, DIP en estructura de tests
- DRY: fixtures reutilizables
"""
import pytest
from datetime import datetime, date, timedelta
from decimal import Decimal
from sqlalchemy.orm import Session

from src.crud.academic.crud_inscripcion import inscripcion_crud
from src.models.academic.inscripcion import Inscripcion
from src.schemas.academic.inscripcion_schemas import InscripcionCreate, InscripcionUpdate
from src.enums.academic.inscripcion_enums import (
    EstadoInscripcion,
    TipoInscripcion,
    MotivoRechazo,
    MotivoRetiro
)


@pytest.mark.inscripciones
@pytest.mark.unit
class TestInscripcionCRUDCreate:
    """Tests de creación de inscripciones"""
    
    def test_create_inscripcion_basica(
        self,
        db_session: Session,
        usuario_estudiante,
        grupo_base,
        periodo_base,
        programa_base,
        usuario_admin
    ):
        """Crea inscripción básica con campos mínimos requeridos"""
        # Arrange
        inscripcion_data = InscripcionCreate(
            estudiante_id=usuario_estudiante.usuario_id,
            grupo_id=grupo_base.grupo_id,
            periodo_academico_id=periodo_base.id,
            programa_id=programa_base.programa_id,
            tipo_inscripcion=TipoInscripcion.regular,
            fecha_solicitud=datetime.now(),
            costo_total=Decimal("0.00"),
            monto_final=Decimal("0.00")
        )
        
        # Act
        inscripcion = inscripcion_crud.create(
            db_session,
            obj_in=inscripcion_data,
            creado_por_id=usuario_admin.usuario_id
        )
        
        # Assert
        assert inscripcion.id is not None
        assert inscripcion.codigo_inscripcion is not None
        assert inscripcion.estudiante_id == usuario_estudiante.usuario_id
        assert inscripcion.grupo_id == grupo_base.grupo_id
        assert inscripcion.estado == EstadoInscripcion.pre_inscrita.value
        assert inscripcion.creado_por_id == usuario_admin.usuario_id
    
    def test_create_genera_codigo_unico(
        self,
        db_session: Session,
        usuario_estudiante,
        grupo_base,
        periodo_base,
        programa_base
    ):
        """Verifica que se genere código único automáticamente"""
        # Arrange
        inscripcion_data = InscripcionCreate(
            estudiante_id=usuario_estudiante.usuario_id,
            grupo_id=grupo_base.grupo_id,
            periodo_academico_id=periodo_base.id,
            programa_id=programa_base.programa_id,
            tipo_inscripcion=TipoInscripcion.regular,
            fecha_solicitud=datetime.now(),
            costo_total=Decimal("0.00"),
            monto_final=Decimal("0.00")
        )
        
        # Act
        inscripcion1 = inscripcion_crud.create(db_session, obj_in=inscripcion_data)
        inscripcion2 = inscripcion_crud.create(db_session, obj_in=inscripcion_data)
        
        # Assert
        assert inscripcion1.codigo_inscripcion != inscripcion2.codigo_inscripcion
        assert "INS-" in inscripcion1.codigo_inscripcion
        assert "INS-" in inscripcion2.codigo_inscripcion
    
    def test_create_con_todos_los_campos(
        self,
        db_session: Session,
        usuario_estudiante,
        grupo_base,
        periodo_base,
        programa_base,
        usuario_admin
    ):
        """Crea inscripción con todos los campos opcionales"""
        # Arrange
        inscripcion_data = InscripcionCreate(
            estudiante_id=usuario_estudiante.usuario_id,
            grupo_id=grupo_base.grupo_id,
            periodo_academico_id=periodo_base.id,
            programa_id=programa_base.programa_id,
            tipo_inscripcion=TipoInscripcion.regular,
            fecha_solicitud=datetime.now(),
            fecha_limite_pago=date.today() + timedelta(days=15),
            costo_total=Decimal("500000.00"),
            monto_final=Decimal("450000.00"),
            tiene_beca=True,
            porcentaje_beca=Decimal("10.00"),
            tipo_beca="Excelencia académica",
            creditos_inscritos=16,
            requiere_aprobacion=False,
            documentos_completos=False
        )
        
        # Act
        inscripcion = inscripcion_crud.create(
            db_session,
            obj_in=inscripcion_data,
            creado_por_id=usuario_admin.usuario_id
        )
        
        # Assert
        assert inscripcion.costo_total == Decimal("500000.00")
        assert inscripcion.tiene_beca is True
        assert inscripcion.porcentaje_beca == Decimal("10.00")
        assert inscripcion.creditos_inscritos == 16


@pytest.mark.inscripciones
@pytest.mark.unit
class TestInscripcionCRUDRead:
    """Tests de lectura de inscripciones"""
    
    def test_get_by_id(self, db_session: Session, inscripcion_base):
        """Obtiene inscripción por ID"""
        # Act
        inscripcion = inscripcion_crud.get(db_session, inscripcion_base.id)
        
        # Assert
        assert inscripcion is not None
        assert inscripcion.id == inscripcion_base.id
        assert inscripcion.codigo_inscripcion == inscripcion_base.codigo_inscripcion
    
    def test_get_by_codigo(self, db_session: Session, inscripcion_base):
        """Obtiene inscripción por código"""
        # Act
        inscripcion = inscripcion_crud.get_by_codigo(
            db_session,
            inscripcion_base.codigo_inscripcion
        )
        
        # Assert
        assert inscripcion is not None
        assert inscripcion.id == inscripcion_base.id
    
    def test_get_by_estudiante(
        self,
        db_session: Session,
        inscripcion_base,
        usuario_estudiante
    ):
        """Obtiene inscripciones de un estudiante"""
        # Act
        inscripciones = inscripcion_crud.get_by_estudiante(
            db_session,
            usuario_estudiante.usuario_id
        )
        
        # Assert
        assert len(inscripciones) >= 1
        assert any(i.id == inscripcion_base.id for i in inscripciones)
    
    def test_get_by_grupo(
        self,
        db_session: Session,
        inscripcion_base,
        grupo_base
    ):
        """Obtiene inscripciones de un grupo"""
        # Act
        inscripciones = inscripcion_crud.get_by_grupo(
            db_session,
            grupo_base.grupo_id
        )
        
        # Assert
        assert len(inscripciones) >= 1
        assert any(i.id == inscripcion_base.id for i in inscripciones)
    
    def test_get_by_periodo(
        self,
        db_session: Session,
        inscripcion_base,
        periodo_base
    ):
        """Obtiene inscripciones de un período"""
        # Act
        inscripciones = inscripcion_crud.get_by_periodo(
            db_session,
            periodo_base.id
        )
        
        # Assert
        assert len(inscripciones) >= 1
        assert any(i.id == inscripcion_base.id for i in inscripciones)
    
    def test_get_by_programa(
        self,
        db_session: Session,
        inscripcion_base,
        programa_base
    ):
        """Obtiene inscripciones de un programa"""
        # Act
        inscripciones = inscripcion_crud.get_by_programa(
            db_session,
            programa_base.programa_id
        )
        
        # Assert
        assert len(inscripciones) >= 1
        assert any(i.id == inscripcion_base.id for i in inscripciones)


@pytest.mark.inscripciones
@pytest.mark.unit
class TestInscripcionCRUDUpdate:
    """Tests de actualización de inscripciones"""
    
    def test_update_campos_basicos(self, db_session: Session, inscripcion_base, usuario_admin):
        """Actualiza campos básicos de inscripción"""
        # Arrange
        update_data = InscripcionUpdate(
            costo_total=Decimal("600000.00"),
            monto_final=Decimal("550000.00"),
            tiene_beca=True,
            porcentaje_beca=Decimal("8.33")
        )
        
        # Act
        inscripcion_actualizada = inscripcion_crud.update(
            db_session,
            db_obj=inscripcion_base,
            obj_in=update_data,
            modificado_por_id=usuario_admin.usuario_id
        )
        
        # Assert
        assert inscripcion_actualizada.costo_total == Decimal("600000.00")
        assert inscripcion_actualizada.tiene_beca is True
        assert inscripcion_actualizada.modificado_por_id == usuario_admin.usuario_id
    
    def test_update_parcial(self, db_session: Session, inscripcion_base):
        """Actualiza solo algunos campos sin afectar otros"""
        # Arrange
        codigo_original = inscripcion_base.codigo_inscripcion
        update_data = InscripcionUpdate(
            documentos_completos=True
        )
        
        # Act
        inscripcion_crud.update(
            db_session,
            db_obj=inscripcion_base,
            obj_in=update_data
        )
        
        # Assert
        assert inscripcion_base.documentos_completos is True
        assert inscripcion_base.codigo_inscripcion == codigo_original  # No debe cambiar


@pytest.mark.inscripciones
@pytest.mark.unit
class TestInscripcionCRUDBusquedas:
    """Tests de búsquedas y filtros"""
    
    def test_get_activas(self, db_session: Session, inscripcion_confirmada):
        """Obtiene inscripciones activas"""
        # Act
        activas = inscripcion_crud.get_activas(db_session)
        
        # Assert
        assert len(activas) >= 1
        assert all(i.estado in [
            EstadoInscripcion.aprobada.value,
            EstadoInscripcion.confirmada.value,
            EstadoInscripcion.activa.value
        ] for i in activas)
    
    def test_get_pendientes_todas(self, db_session: Session, inscripcion_pendiente_pago):
        """Obtiene todas las inscripciones pendientes"""
        # Act
        pendientes = inscripcion_crud.get_pendientes(db_session)
        
        # Assert
        assert len(pendientes) >= 1
        assert any(i.id == inscripcion_pendiente_pago.id for i in pendientes)
    
    def test_get_pendientes_pago(self, db_session: Session, inscripcion_pendiente_pago):
        """Obtiene inscripciones pendientes de pago específicamente"""
        # Act
        pendientes_pago = inscripcion_crud.get_pendientes(
            db_session,
            tipo_pendiente='pago'
        )
        
        # Assert
        assert len(pendientes_pago) >= 1
        assert all(i.estado == EstadoInscripcion.pendiente_pago.value for i in pendientes_pago)
    
    def test_get_by_filtros_multiples(
        self,
        db_session: Session,
        inscripcion_base,
        usuario_estudiante,
        periodo_base
    ):
        """Búsqueda con múltiples filtros combinados"""
        # Act
        inscripciones, total = inscripcion_crud.get_by_filtros(
            db_session,
            estudiante_id=usuario_estudiante.usuario_id,
            periodo_academico_id=periodo_base.id,
            activo=True
        )
        
        # Assert
        assert total >= 1
        assert len(inscripciones) >= 1
        assert all(i.estudiante_id == usuario_estudiante.usuario_id for i in inscripciones)
        assert all(i.periodo_academico_id == periodo_base.id for i in inscripciones)


@pytest.mark.inscripciones
@pytest.mark.unit
class TestInscripcionCRUDValidaciones:
    """Tests de validaciones y conteos"""
    
    def test_existe_inscripcion_activa(
        self,
        db_session: Session,
        inscripcion_base,
        usuario_estudiante,
        grupo_base
    ):
        """Verifica existencia de inscripción activa"""
        # Act
        existe = inscripcion_crud.existe_inscripcion(
            db_session,
            usuario_estudiante.usuario_id,
            grupo_base.grupo_id
        )
        
        # Assert
        assert existe is True
    
    def test_no_existe_inscripcion(
        self,
        db_session: Session,
        usuario_estudiante,
        grupo_base
    ):
        """Verifica que no exista inscripción cuando no hay"""
        # Act
        existe = inscripcion_crud.existe_inscripcion(
            db_session,
            999999,  # ID que no existe
            grupo_base.grupo_id
        )
        
        # Assert
        assert existe is False
    
    def test_contar_inscripciones_activas_grupo(
        self,
        db_session: Session,
        inscripcion_confirmada,
        grupo_base
    ):
        """Cuenta inscripciones activas en un grupo"""
        # Act
        count = inscripcion_crud.contar_inscripciones_activas_grupo(
            db_session,
            grupo_base.grupo_id
        )
        
        # Assert
        assert count >= 1
    
    def test_contar_creditos_inscritos_periodo(
        self,
        db_session: Session,
        inscripcion_confirmada,
        usuario_estudiante,
        periodo_base
    ):
        """Suma créditos inscritos en un período"""
        # Arrange
        inscripcion_confirmada.creditos_inscritos = 16
        db_session.commit()
        
        # Act
        total_creditos = inscripcion_crud.contar_creditos_inscritos_periodo(
            db_session,
            usuario_estudiante.usuario_id,
            periodo_base.id
        )
        
        # Assert
        assert total_creditos >= 16


@pytest.mark.inscripciones
@pytest.mark.unit
class TestInscripcionCRUDEstados:
    """Tests de cambios de estado"""
    
    def test_aprobar_inscripcion(
        self,
        db_session: Session,
        inscripcion_base,
        usuario_admin
    ):
        """Aprueba una inscripción"""
        # Arrange
        inscripcion_base.requiere_aprobacion = True
        inscripcion_base.estado = EstadoInscripcion.pendiente_aprobacion.value
        db_session.commit()
        
        # Act
        inscripcion = inscripcion_crud.aprobar(
            db_session,
            inscripcion_base.id,
            usuario_admin.usuario_id,
            "Aprobado por cumplir requisitos"
        )
        
        # Assert
        assert inscripcion is not None
        assert inscripcion.esta_aprobada is True
        assert inscripcion.aprobada_por_id == usuario_admin.usuario_id
    
    def test_rechazar_inscripcion(
        self,
        db_session: Session,
        inscripcion_base,
        usuario_admin
    ):
        """Rechaza una inscripción"""
        # Act
        inscripcion = inscripcion_crud.rechazar(
            db_session,
            inscripcion_base.id,
            MotivoRechazo.no_cumple_requisitos,
            "No cumple prerequisitos del curso",
            usuario_admin.usuario_id
        )
        
        # Assert
        assert inscripcion is not None
        assert inscripcion.fue_rechazada is True
        assert inscripcion.estado == EstadoInscripcion.rechazada.value
        assert inscripcion.rechazada_por_id == usuario_admin.usuario_id
    
    def test_confirmar_inscripcion(
        self,
        db_session: Session,
        inscripcion_pendiente_pago,
        usuario_admin
    ):
        """Confirma una inscripción tras pago"""
        # Arrange
        inscripcion_pendiente_pago.esta_pagado = True
        db_session.commit()
        
        # Act
        inscripcion = inscripcion_crud.confirmar(
            db_session,
            inscripcion_pendiente_pago.id,
            usuario_admin.usuario_id
        )
        
        # Assert
        assert inscripcion is not None
        assert inscripcion.estado == EstadoInscripcion.confirmada.value
        assert inscripcion.fecha_confirmacion is not None
    
    def test_retirar_inscripcion(
        self,
        db_session: Session,
        inscripcion_confirmada,
        usuario_estudiante
    ):
        """Retira una inscripción"""
        # Act
        inscripcion = inscripcion_crud.retirar(
            db_session,
            inscripcion_confirmada.id,
            MotivoRetiro.personal,
            "Motivos personales",
            True,  # es_voluntario
            usuario_estudiante.usuario_id
        )
        
        # Assert
        assert inscripcion is not None
        assert inscripcion.fue_retirada is True
        assert inscripcion.estado == EstadoInscripcion.retirada.value
        assert inscripcion.fue_retiro_voluntario is True  # Nombre correcto del campo


@pytest.mark.inscripciones
@pytest.mark.unit
class TestInscripcionCRUDEstadisticas:
    """Tests de estadísticas y reportes"""
    
    def test_estadisticas_periodo(
        self,
        db_session: Session,
        inscripcion_base,
        inscripcion_confirmada,
        periodo_base
    ):
        """Obtiene estadísticas completas de un período"""
        # Act
        stats = inscripcion_crud.get_estadisticas_periodo(
            db_session,
            periodo_base.id
        )
        
        # Assert
        assert stats is not None
        assert "total_inscripciones" in stats
        assert "por_estado" in stats
        assert "total_pagadas" in stats
        assert "monto_total_recaudado" in stats
        assert stats["total_inscripciones"] >= 2
        assert isinstance(stats["por_estado"], dict)
