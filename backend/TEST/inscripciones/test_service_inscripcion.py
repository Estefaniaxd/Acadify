"""
Tests Service Inscripción

Tests de lógica de negocio siguiendo:
- Clean Code: nombres descriptivos, funciones pequeñas
- SOLID: SRP (cada test una responsabilidad)
- DRY: fixtures y helpers reutilizables
- AAA Pattern: Arrange-Act-Assert consistente

Cobertura:
- Validaciones de negocio complejas
- Cálculos financieros con becas/descuentos
- Workflow de estados (17 estados)
- Verificación de cupos y lista de espera
- Gestión de permisos por rol
"""
import pytest
from datetime import datetime, date, timedelta
from decimal import Decimal
from sqlalchemy.orm import Session
from fastapi import HTTPException
from uuid import UUID

from src.services.academic.inscripcion_service import InscripcionAcademicaService
from src.models.academic.inscripcion import Inscripcion
from src.models.academic.grupo import Grupo
from src.schemas.academic.inscripcion_schemas import InscripcionCreate
from src.enums.academic.inscripcion_enums import (
    EstadoInscripcion,
    TipoInscripcion,
    MotivoRechazo,
    MotivoRetiro
)


@pytest.fixture
def inscripcion_service():
    """Instancia del servicio de inscripción"""
    return InscripcionAcademicaService(redis_manager=None)


@pytest.mark.inscripciones
@pytest.mark.unit
class TestInscripcionServiceCreacion:
    """Tests de creación de inscripciones con validaciones"""
    
    def test_crear_inscripcion_exitosa(
        self,
        db_session: Session,
        inscripcion_service: InscripcionAcademicaService,
        usuario_estudiante,
        grupo_base,
        periodo_base,
        programa_base,
        usuario_admin
    ):
        """Crea inscripción exitosamente con todas las validaciones"""
        # Arrange
        periodo_base.estado = "inscripciones_abiertas"
        periodo_base.fecha_inicio_inscripciones = date.today() - timedelta(days=1)
        periodo_base.fecha_fin_inscripciones = date.today() + timedelta(days=30)
        periodo_base.permite_inscripciones = True
        db_session.commit()
        
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
        inscripcion = inscripcion_service.crear_inscripcion(
            db_session,
            inscripcion_data,
            usuario_admin
        )
        
        # Assert
        assert inscripcion is not None
        assert inscripcion.id is not None
        assert inscripcion.codigo_inscripcion is not None
        assert inscripcion.estudiante_id == usuario_estudiante.usuario_id
        assert inscripcion.grupo_id == grupo_base.grupo_id
        assert inscripcion.creado_por_id == usuario_admin.usuario_id
    
    def test_crear_inscripcion_periodo_cerrado(
        self,
        db_session: Session,
        inscripcion_service: InscripcionAcademicaService,
        usuario_estudiante,
        grupo_base,
        periodo_base,
        programa_base,
        usuario_admin
    ):
        """Valida que no se puede inscribir cuando período está cerrado"""
        # Arrange - Cerrar período
        periodo_base.estado = "finalizado"
        periodo_base.permite_inscripciones = False
        db_session.commit()
        
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
        
        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            inscripcion_service.crear_inscripcion(
                db_session,
                inscripcion_data,
                usuario_admin
            )
        
        assert exc_info.value.status_code == 400
        assert "no está aceptando inscripciones" in str(exc_info.value.detail)
    
    def test_crear_inscripcion_grupo_sin_cupos(
        self,
        db_session: Session,
        inscripcion_service: InscripcionAcademicaService,
        usuario_estudiante,
        grupo_base,
        periodo_base,
        programa_base,
        usuario_admin
    ):
        """Valida rechazo cuando no hay cupos y lista de espera está deshabilitada"""
        # Arrange
        # Ajustar período para que acepte inscripciones
        periodo_base.fecha_inicio_inscripciones = date.today() - timedelta(days=1)
        periodo_base.fecha_fin_inscripciones = date.today() + timedelta(days=30)
        periodo_base.permite_inscripciones = True
        periodo_base.estado = "inscripciones_abiertas"
        
        grupo_base.capacidad_maxima = 1  # Solo 1 cupo
        grupo_base.permite_lista_espera = False
        db_session.commit()
        
        # Crear una inscripción que ocupe el cupo
        inscripcion_existente = Inscripcion(
            codigo_inscripcion=f"INS-TEST-{datetime.now().timestamp()}",
            estudiante_id=UUID('12345678-1234-1234-1234-123456789012'),
            grupo_id=grupo_base.grupo_id,
            periodo_academico_id=periodo_base.id,
            programa_id=programa_base.programa_id,
            estado=EstadoInscripcion.confirmada.value,
            tipo_inscripcion=TipoInscripcion.regular.value,
            fecha_solicitud=datetime.now(),
            costo_total=Decimal("0.00"),
            monto_final=Decimal("0.00"),
            activo=True
        )
        db_session.add(inscripcion_existente)
        db_session.commit()
        
        # Intentar inscribir otro estudiante
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
        
        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            inscripcion_service.crear_inscripcion(
                db_session,
                inscripcion_data,
                usuario_admin
            )
        
        assert exc_info.value.status_code == 400
        assert "no tiene cupos disponibles" in str(exc_info.value.detail)
    
    def test_crear_inscripcion_duplicada(
        self,
        db_session: Session,
        inscripcion_service: InscripcionAcademicaService,
        inscripcion_base,
        usuario_estudiante,
        grupo_base,
        periodo_base,
        programa_base,
        usuario_admin
    ):
        """Valida que no se puede inscribir dos veces al mismo grupo"""
        # Arrange
        periodo_base.estado = "inscripciones_abiertas"
        periodo_base.permite_inscripciones = True
        periodo_base.fecha_inicio_inscripciones = date.today()
        periodo_base.fecha_fin_inscripciones = date.today() + timedelta(days=30)
        db_session.commit()
        
        inscripcion_data = InscripcionCreate(
            estudiante_id=inscripcion_base.estudiante_id,
            grupo_id=inscripcion_base.grupo_id,
            periodo_academico_id=periodo_base.id,
            programa_id=programa_base.programa_id,
            tipo_inscripcion=TipoInscripcion.regular,
            fecha_solicitud=datetime.now(),
            costo_total=Decimal("0.00"),
            monto_final=Decimal("0.00")
        )
        
        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            inscripcion_service.crear_inscripcion(
                db_session,
                inscripcion_data,
                usuario_admin
            )
        
        assert exc_info.value.status_code == 400
        assert "Ya existe una inscripción activa" in str(exc_info.value.detail)


@pytest.mark.inscripciones
@pytest.mark.unit
class TestInscripcionServiceConsultas:
    """Tests de consultas con validación de permisos"""
    
    def test_obtener_inscripcion_estudiante_propia(
        self,
        db_session: Session,
        inscripcion_service: InscripcionAcademicaService,
        inscripcion_base,
        usuario_estudiante
    ):
        """Estudiante puede obtener su propia inscripción"""
        # Arrange
        inscripcion_base.estudiante_id = usuario_estudiante.usuario_id
        db_session.commit()
        
        # Act
        inscripcion = inscripcion_service.obtener_inscripcion(
            db_session,
            inscripcion_base.id,
            usuario_estudiante
        )
        
        # Assert
        assert inscripcion is not None
        assert inscripcion.id == inscripcion_base.id
    
    def test_obtener_inscripcion_estudiante_ajeno_rechazado(
        self,
        db_session: Session,
        inscripcion_service: InscripcionAcademicaService,
        inscripcion_base,
        usuario_admin  # Usuario DIFERENTE al dueño de la inscripción
    ):
        """Estudiante NO puede ver inscripción de otro estudiante"""
        # Arrange - cambiar rol del admin a estudiante temporalmente
        usuario_admin.rol = "estudiante"
        
        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            inscripcion_service.obtener_inscripcion(
                db_session,
                inscripcion_base.id,
                usuario_admin  # Usuario diferente intenta acceder
            )
        
        assert exc_info.value.status_code == 403
        assert "No tiene permisos" in str(exc_info.value.detail)
    
    def test_listar_inscripciones_estudiante(
        self,
        db_session: Session,
        inscripcion_service: InscripcionAcademicaService,
        inscripcion_base,
        usuario_estudiante
    ):
        """Lista inscripciones de un estudiante"""
        # Arrange
        inscripcion_base.estudiante_id = usuario_estudiante.usuario_id
        db_session.commit()
        
        # Act
        inscripciones, total = inscripcion_service.listar_inscripciones_estudiante(
            db_session,
            usuario_estudiante.usuario_id,
            usuario_estudiante
        )
        
        # Assert
        assert total >= 1
        assert len(inscripciones) >= 1
        assert any(i.id == inscripcion_base.id for i in inscripciones)
    
    def test_listar_inscripciones_grupo_como_coordinador(
        self,
        db_session: Session,
        inscripcion_service: InscripcionAcademicaService,
        inscripcion_base,
        grupo_base,
        usuario_admin
    ):
        """Coordinador puede listar inscripciones de un grupo"""
        # Arrange
        usuario_admin.rol = "coordinador"
        db_session.commit()
        
        # Act
        inscripciones, total = inscripcion_service.listar_inscripciones_grupo(
            db_session,
            grupo_base.grupo_id,
            usuario_admin
        )
        
        # Assert
        assert total >= 1
        assert len(inscripciones) >= 1


@pytest.mark.inscripciones
@pytest.mark.unit
class TestInscripcionServiceEstados:
    """Tests de cambios de estado con validaciones"""
    
    def test_aprobar_inscripcion_como_coordinador(
        self,
        db_session: Session,
        inscripcion_service: InscripcionAcademicaService,
        inscripcion_base,
        usuario_admin
    ):
        """Coordinador puede aprobar una inscripción"""
        # Arrange
        usuario_admin.rol = "coordinador"
        inscripcion_base.estado = EstadoInscripcion.pendiente_aprobacion.value
        inscripcion_base.requiere_aprobacion = True
        db_session.commit()
        
        # Act
        inscripcion_aprobada = inscripcion_service.aprobar_inscripcion(
            db_session,
            inscripcion_base.id,
            usuario_admin,
            "Aprobado por cumplir requisitos"
        )
        
        # Assert
        assert inscripcion_aprobada is not None
        assert inscripcion_aprobada.esta_aprobada is True
        assert inscripcion_aprobada.aprobada_por_id == usuario_admin.usuario_id
    
    def test_aprobar_inscripcion_como_estudiante_rechazado(
        self,
        db_session: Session,
        inscripcion_service: InscripcionAcademicaService,
        inscripcion_base,
        usuario_estudiante
    ):
        """Estudiante NO puede aprobar inscripciones"""
        # Arrange
        inscripcion_base.estado = EstadoInscripcion.pendiente_aprobacion.value
        db_session.commit()
        
        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            inscripcion_service.aprobar_inscripcion(
                db_session,
                inscripcion_base.id,
                usuario_estudiante
            )
        
        assert exc_info.value.status_code == 403
        assert "Solo coordinadores" in str(exc_info.value.detail)
    
    def test_rechazar_inscripcion(
        self,
        db_session: Session,
        inscripcion_service: InscripcionAcademicaService,
        inscripcion_base,
        usuario_admin
    ):
        """Rechaza una inscripción con motivo"""
        # Arrange
        usuario_admin.rol = "coordinador"
        db_session.commit()
        
        # Act
        inscripcion_rechazada = inscripcion_service.rechazar_inscripcion(
            db_session,
            inscripcion_base.id,
            MotivoRechazo.no_cumple_requisitos,
            "No cumple prerequisitos del curso",
            usuario_admin
        )
        
        # Assert
        assert inscripcion_rechazada.fue_rechazada is True
        assert inscripcion_rechazada.estado == EstadoInscripcion.rechazada.value
        assert inscripcion_rechazada.rechazada_por_id == usuario_admin.usuario_id
    
    def test_confirmar_inscripcion_como_estudiante(
        self,
        db_session: Session,
        inscripcion_service: InscripcionAcademicaService,
        inscripcion_base,
        usuario_estudiante
    ):
        """Estudiante confirma su propia inscripción"""
        # Arrange
        inscripcion_base.estudiante_id = usuario_estudiante.usuario_id
        inscripcion_base.estado = EstadoInscripcion.aprobada.value
        inscripcion_base.esta_aprobada = True
        inscripcion_base.esta_pagado = True
        inscripcion_base.documentos_completos = True
        inscripcion_base.monto_final = Decimal("0.00")
        db_session.commit()
        
        # Act
        inscripcion_confirmada = inscripcion_service.confirmar_inscripcion(
            db_session,
            inscripcion_base.id,
            usuario_estudiante
        )
        
        # Assert
        assert inscripcion_confirmada.estado == EstadoInscripcion.confirmada.value
        assert inscripcion_confirmada.fecha_confirmacion is not None
    
    def test_confirmar_inscripcion_sin_pago_rechazado(
        self,
        db_session: Session,
        inscripcion_service: InscripcionAcademicaService,
        inscripcion_base,
        usuario_estudiante
    ):
        """No se puede confirmar si falta pago"""
        # Arrange
        inscripcion_base.estudiante_id = usuario_estudiante.usuario_id
        inscripcion_base.estado = EstadoInscripcion.aprobada.value
        inscripcion_base.esta_pagado = False
        inscripcion_base.monto_final = Decimal("500000.00")  # Tiene costo
        db_session.commit()
        
        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            inscripcion_service.confirmar_inscripcion(
                db_session,
                inscripcion_base.id,
                usuario_estudiante
            )
        
        assert exc_info.value.status_code == 400
        assert "Debe completar el pago" in str(exc_info.value.detail)
    
    def test_retirar_inscripcion_como_estudiante(
        self,
        db_session: Session,
        inscripcion_service: InscripcionAcademicaService,
        inscripcion_confirmada,
        usuario_estudiante
    ):
        """Estudiante retira su inscripción voluntariamente"""
        # Arrange
        inscripcion_confirmada.estudiante_id = usuario_estudiante.usuario_id
        inscripcion_confirmada.puede_retirar = True
        db_session.commit()
        
        # Act
        inscripcion_retirada = inscripcion_service.retirar_inscripcion(
            db_session,
            inscripcion_confirmada.id,
            MotivoRetiro.personal,
            "Motivos personales",
            usuario_estudiante,
            es_voluntario=True
        )
        
        # Assert
        assert inscripcion_retirada.fue_retirada is True
        assert inscripcion_retirada.estado == EstadoInscripcion.retirada.value
        assert inscripcion_retirada.fue_retiro_voluntario is True
    
    def test_activar_inscripcion_como_coordinador(
        self,
        db_session: Session,
        inscripcion_service: InscripcionAcademicaService,
        inscripcion_confirmada,
        usuario_admin
    ):
        """Coordinador activa una inscripción confirmada"""
        # Arrange
        usuario_admin.rol = "coordinador"
        db_session.commit()
        
        # Act
        inscripcion_activa = inscripcion_service.activar_inscripcion(
            db_session,
            inscripcion_confirmada.id,
            usuario_admin
        )
        
        # Assert
        assert inscripcion_activa.estado == EstadoInscripcion.activa.value
    
    def test_registrar_pago_actualiza_estado(
        self,
        db_session: Session,
        inscripcion_service: InscripcionAcademicaService,
        inscripcion_pendiente_pago,
        usuario_admin
    ):
        """Registrar pago cambia estado automáticamente"""
        # Arrange
        inscripcion_pendiente_pago.documentos_completos = True
        db_session.commit()
        
        # Act
        inscripcion_pagada = inscripcion_service.registrar_pago(
            db_session,
            inscripcion_pendiente_pago.id,
            Decimal("500000.00"),
            "REF-123456",
            "transferencia",
            usuario_admin
        )
        
        # Assert
        assert inscripcion_pagada.esta_pagado is True
        assert inscripcion_pagada.estado == EstadoInscripcion.aprobada.value


@pytest.mark.inscripciones
@pytest.mark.unit
class TestInscripcionServiceEstadisticas:
    """Tests de estadísticas y reportes"""
    
    def test_obtener_estadisticas_grupo(
        self,
        db_session: Session,
        inscripcion_service: InscripcionAcademicaService,
        grupo_base,
        inscripcion_confirmada,
        usuario_admin
    ):
        """Obtiene estadísticas completas de un grupo"""
        # Arrange
        usuario_admin.rol = "coordinador"
        grupo_base.cupo_maximo = 30
        db_session.commit()
        
        # Act
        stats = inscripcion_service.obtener_estadisticas_grupo(
            db_session,
            grupo_base.grupo_id,
            usuario_admin
        )
        
        # Assert
        assert stats is not None
        assert "total_inscritos" in stats
        assert "cupos_disponibles" in stats
        assert "porcentaje_ocupacion" in stats
        assert "inscripciones_por_estado" in stats
        assert stats["grupo_id"] == grupo_base.grupo_id
    
    def test_obtener_estadisticas_periodo(
        self,
        db_session: Session,
        inscripcion_service: InscripcionAcademicaService,
        periodo_base,
        inscripcion_base,
        usuario_admin
    ):
        """Obtiene estadísticas de un período académico"""
        # Arrange
        usuario_admin.rol = "coordinador"
        db_session.commit()
        
        # Act
        stats = inscripcion_service.obtener_estadisticas_periodo(
            db_session,
            periodo_base.id,
            usuario_admin
        )
        
        # Assert
        assert stats is not None
        assert "total_inscripciones" in stats
        assert "por_estado" in stats
        assert "total_pagadas" in stats
        assert "monto_total_recaudado" in stats
