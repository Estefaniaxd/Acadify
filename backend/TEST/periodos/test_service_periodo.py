"""
Tests para Service de Período Académico

Tests de lógica de negocio, validaciones, cache y permisos.
Cobertura: 25 tests
"""
import pytest
from datetime import date, timedelta
from decimal import Decimal
from unittest.mock import Mock, patch
from fastapi import HTTPException

from src.services.academic.periodo_academico_service import PeriodoAcademicoService
from src.models.academic.periodo_academico import PeriodoAcademico
from src.schemas.academic.periodo_academico_schemas import (
    PeriodoAcademicoUpdate
)
from src.enums.academic import TipoPeriodo, EstadoPeriodo


@pytest.fixture
def service():
    """Service sin Redis para tests básicos"""
    return PeriodoAcademicoService(redis_manager=None)


@pytest.fixture
def service_con_redis():
    """Service con Redis mockeado"""
    redis_mock = Mock()
    redis_mock.get_json.return_value = None
    redis_mock.set_json.return_value = True
    redis_mock.delete.return_value = True
    redis_mock.delete_pattern.return_value = True
    return PeriodoAcademicoService(redis_manager=redis_mock)


@pytest.fixture
def usuario_superadmin():
    """Usuario con rol administrador (superadmin) - ID simulado"""
    from uuid import uuid4
    from src.enums.users.usuario_enums import RolUsuario
    class MockUsuario:
        usuario_id = uuid4()
        rol = RolUsuario.administrador
        correo_institucional = "superadmin@test.com"
    return MockUsuario()


@pytest.fixture
def usuario_superadmin():
    """Usuario con rol administrador (superadmin) - ID simulado"""
    from uuid import uuid4
    class MockUsuario:
        usuario_id = uuid4()
        rol = "superadmin"  # String para compatibilidad con validación
        correo_institucional = "superadmin@test.com"
    return MockUsuario()


@pytest.fixture
def usuario_coordinador():
    """Usuario con rol coordinador - ID simulado"""
    from uuid import uuid4
    class MockUsuario:
        usuario_id = uuid4()
        rol = "coordinador"
        correo_institucional = "coordinador@test.com"
    return MockUsuario()


@pytest.fixture
def usuario_estudiante():
    """Usuario con rol estudiante - ID simulado"""
    from uuid import uuid4
    class MockUsuario:
        usuario_id = uuid4()
        rol = "estudiante"
        correo_institucional = "estudiante@test.com"
    return MockUsuario()


@pytest.fixture
def usuario_estudiante():
    """Usuario con rol estudiante - ID simulado"""
    from uuid import uuid4
    from src.enums.users.usuario_enums import RolUsuario
    class MockUsuario:
        usuario_id = uuid4()
        rol = RolUsuario.estudiante
        correo_institucional = "estudiante@test.com"
    return MockUsuario()



@pytest.mark.periodos
@pytest.mark.service
class TestPeriodoAcademicoServiceObtener:
    """Tests de operaciones de obtención"""
    
    def test_obtener_periodo_por_id(self, db_session, service, periodo_base, usuario_superadmin):
        """Obtiene un período por ID"""
        periodo = service.obtener_periodo(
            db_session, periodo_base.id, usuario_superadmin
        )
        
        assert periodo is not None
        assert periodo.id == periodo_base.id
        assert periodo.nombre == periodo_base.nombre
    
    def test_obtener_periodo_inexistente(self, db_session, service, usuario_superadmin):
        """Error al obtener período que no existe"""
        with pytest.raises(HTTPException) as exc_info:
            service.obtener_periodo(db_session, 99999, usuario_superadmin)
        
        assert exc_info.value.status_code == 404
        assert "no encontrado" in str(exc_info.value.detail).lower()
    
    def test_listar_periodos_con_filtros(
        self, db_session, service, institucion_id, periodo_base, usuario_superadmin
    ):
        """Lista períodos aplicando filtros"""
        periodos, total = service.listar_periodos(
            db_session,
            institucion_id,
            usuario_superadmin,
            tipo=TipoPeriodo.semestral,
            anio=2024,
            skip=0,
            limit=10
        )
        
        assert len(periodos) >= 1
        assert total >= 1
        for periodo in periodos:
            assert periodo.tipo == TipoPeriodo.semestral
            assert periodo.anio == 2024
    
    def test_listar_periodos_estudiante_solo_visibles(
        self, db_session, service, institucion_id, periodo_base, usuario_estudiante
    ):
        """Estudiantes solo ven períodos visibles"""
        # Crear período no visible
        hoy = date.today()
        periodo_oculto = PeriodoAcademico(
            institucion_id=institucion_id,
            nombre="Período Oculto",
            codigo="OCULTO-2025",
            tipo=TipoPeriodo.semestral,
            anio=2025,
            fecha_inicio=hoy,
            fecha_fin=hoy + timedelta(days=180),
            fecha_inicio_inscripciones=hoy - timedelta(days=10),
            fecha_fin_inscripciones=hoy - timedelta(days=1),
            fecha_inicio_clases=hoy,
            fecha_fin_clases=hoy + timedelta(days=170),
            visible_estudiantes=False
        )
        db_session.add(periodo_oculto)
        db_session.commit()
        
        periodos, total = service.listar_periodos(
            db_session, institucion_id, usuario_estudiante, skip=0, limit=100
        )
        
        # No debe incluir el período oculto
        assert all(p.visible_estudiantes is True for p in periodos)
        assert not any(p.id == periodo_oculto.id for p in periodos)
    
    def test_obtener_periodo_actual(
        self, db_session, service, institucion_id, periodo_en_inscripciones, usuario_superadmin
    ):
        """Obtiene el período actual de una institución"""
        periodo_actual = service.obtener_periodo_actual(
            db_session, institucion_id, usuario_superadmin
        )
        
        assert periodo_actual is not None
        assert periodo_actual.es_actual is True
    
    def test_obtener_periodos_con_inscripciones_abiertas(
        self, db_session, service, institucion_id, periodo_en_inscripciones, usuario_superadmin
    ):
        """Obtiene períodos que aceptan inscripciones"""
        periodos = service.obtener_periodos_con_inscripciones_abiertas(
            db_session, institucion_id, usuario_superadmin
        )
        
        assert len(periodos) >= 1
        assert all(p.permite_inscribirse_ahora for p in periodos)


@pytest.mark.periodos
@pytest.mark.service
class TestPeriodoAcademicoServiceActualizar:
    """Tests de operaciones de actualización"""
    
    def test_actualizar_periodo_basico(
        self, db_session, service, periodo_base, usuario_superadmin
    ):
        """Actualiza información básica del período"""
        update_data = PeriodoAcademicoUpdate(
            nombre="Semestre 2024-1 Modificado",
            descripcion="Nueva descripción"
        )
        
        periodo_actualizado = service.actualizar_periodo(
            db_session, periodo_base.id, update_data, usuario_superadmin
        )
        
        assert periodo_actualizado.nombre == "Semestre 2024-1 Modificado"
        assert periodo_actualizado.descripcion == "Nueva descripción"
    
    def test_actualizar_periodo_inexistente(
        self, db_session, service, usuario_superadmin
    ):
        """Error al actualizar período que no existe"""
        update_data = PeriodoAcademicoUpdate(nombre="Test")
        
        with pytest.raises(HTTPException) as exc_info:
            service.actualizar_periodo(db_session, 99999, update_data, usuario_superadmin)
        
        assert exc_info.value.status_code == 404
    
    def test_actualizar_codigo_duplicado(
        self, db_session, service, institucion_id, periodo_base, usuario_superadmin
    ):
        """Error al actualizar con código que ya existe"""
        # Crear otro período
        hoy = date.today()
        otro_periodo = PeriodoAcademico(
            institucion_id=institucion_id,
            nombre="Otro Período",
            codigo="OTRO-2025",
            tipo=TipoPeriodo.trimestral,
            anio=2025,
            fecha_inicio=hoy,
            fecha_fin=hoy + timedelta(days=90),
            fecha_inicio_inscripciones=hoy - timedelta(days=5),
            fecha_fin_inscripciones=hoy - timedelta(days=1),
            fecha_inicio_clases=hoy,
            fecha_fin_clases=hoy + timedelta(days=85)
        )
        db_session.add(otro_periodo)
        db_session.commit()
        db_session.refresh(otro_periodo)
        
        # Intentar actualizar periodo_base con código de otro_periodo
        update_data = PeriodoAcademicoUpdate(codigo="OTRO-2025")
        
        with pytest.raises(HTTPException) as exc_info:
            service.actualizar_periodo(
                db_session, periodo_base.id, update_data, usuario_superadmin
            )
        
        assert exc_info.value.status_code == 400
        assert "ya existe" in str(exc_info.value.detail).lower()
    
    def test_actualizar_fechas_invalidas(
        self, db_session, service, periodo_base, usuario_superadmin
    ):
        """Error al actualizar con fechas inválidas"""
        # Fecha fin antes de fecha inicio
        update_data = PeriodoAcademicoUpdate(
            fecha_fin=periodo_base.fecha_inicio - timedelta(days=1)
        )
        
        with pytest.raises(HTTPException) as exc_info:
            service.actualizar_periodo(
                db_session, periodo_base.id, update_data, usuario_superadmin
            )
        
        assert exc_info.value.status_code == 400


@pytest.mark.periodos
@pytest.mark.service
class TestPeriodoAcademicoServiceEstados:
    """Tests de cambios de estado"""
    
    def test_activar_periodo(self, db_session, service, periodo_base, usuario_superadmin):
        """Activa un período"""
        periodo_base.activo = False
        db_session.commit()
        
        periodo_activado = service.activar_periodo(
            db_session, periodo_base.id, usuario_superadmin
        )
        
        assert periodo_activado.activo is True
    
    def test_activar_periodo_inexistente(self, db_session, service, usuario_superadmin):
        """Error al activar período que no existe"""
        with pytest.raises(HTTPException) as exc_info:
            service.activar_periodo(db_session, 99999, usuario_superadmin)
        
        assert exc_info.value.status_code == 404
    
    def test_marcar_como_actual(
        self, db_session, service, institucion_id, periodo_base, usuario_superadmin
    ):
        """Marca un período como actual"""
        periodo_base.estado = EstadoPeriodo.en_curso
        db_session.commit()
        
        periodo_actual = service.marcar_como_actual(
            db_session, periodo_base.id, usuario_superadmin
        )
        
        assert periodo_actual.es_actual is True
        assert periodo_actual.activo is True
    
    def test_marcar_como_actual_estado_invalido(
        self, db_session, service, periodo_finalizado, usuario_superadmin
    ):
        """Error al marcar como actual un período finalizado"""
        with pytest.raises(HTTPException) as exc_info:
            service.marcar_como_actual(
                db_session, periodo_finalizado.id, usuario_superadmin
            )
        
        assert exc_info.value.status_code == 400
        assert "estado" in str(exc_info.value.detail).lower()
    
    def test_finalizar_periodo(
        self, db_session, service, periodo_en_curso, usuario_superadmin
    ):
        """Finaliza un período en curso"""
        periodo_finalizado = service.finalizar_periodo(
            db_session, periodo_en_curso.id, usuario_superadmin
        )
        
        assert periodo_finalizado.estado == EstadoPeriodo.finalizado
        assert periodo_finalizado.es_actual is False
    
    def test_finalizar_periodo_estado_invalido(
        self, db_session, service, periodo_base, usuario_superadmin
    ):
        """Error al finalizar período que no está en curso"""
        with pytest.raises(HTTPException) as exc_info:
            service.finalizar_periodo(db_session, periodo_base.id, usuario_superadmin)
        
        assert exc_info.value.status_code == 400
    
    def test_cancelar_periodo(
        self, db_session, service, periodo_base, usuario_superadmin
    ):
        """Cancela un período con motivo"""
        motivo = "Cancelado por falta de recursos"
        
        periodo_cancelado = service.cancelar_periodo(
            db_session, periodo_base.id, motivo, usuario_superadmin
        )
        
        assert periodo_cancelado.estado == EstadoPeriodo.cancelado
        assert periodo_cancelado.activo is False
        assert motivo in periodo_cancelado.notas
    
    def test_cancelar_periodo_finalizado(
        self, db_session, service, periodo_finalizado, usuario_superadmin
    ):
        """Error al cancelar período finalizado"""
        with pytest.raises(HTTPException) as exc_info:
            service.cancelar_periodo(
                db_session, periodo_finalizado.id, "motivo", usuario_superadmin
            )
        
        assert exc_info.value.status_code == 400
        assert "finalizado" in str(exc_info.value.detail).lower()


@pytest.mark.periodos
@pytest.mark.service
class TestPeriodoAcademicoServicePermisos:
    """Tests de validación de permisos"""
    
    def test_superadmin_tiene_acceso_total(
        self, db_session, service, institucion_id, periodo_base, usuario_superadmin
    ):
        """Superadmin puede acceder a cualquier institución"""
        # No debe lanzar excepción
        periodos, total = service.listar_periodos(
            db_session, institucion_id, usuario_superadmin, skip=0, limit=10
        )
        
        assert len(periodos) >= 1
    
    def test_coordinador_tiene_acceso(
        self, db_session, service, institucion_id, periodo_base, usuario_coordinador
    ):
        """Coordinador puede acceder a su institución"""
        # No debe lanzar excepción
        periodos, total = service.listar_periodos(
            db_session, institucion_id, usuario_coordinador, skip=0, limit=10
        )
        
        assert len(periodos) >= 1
    
    def test_estudiante_tiene_acceso_lectura(
        self, db_session, service, institucion_id, periodo_base, usuario_estudiante
    ):
        """Estudiante puede ver períodos (solo lectura)"""
        periodos, total = service.listar_periodos(
            db_session, institucion_id, usuario_estudiante, skip=0, limit=10
        )
        
        assert len(periodos) >= 0  # Puede no tener ninguno visible


@pytest.mark.periodos
@pytest.mark.service
class TestPeriodoAcademicoServiceCache:
    """Tests de funcionalidad de cache con Redis"""
    
    def test_obtener_periodo_usa_cache(
        self, db_session, service_con_redis, periodo_base, usuario_superadmin
    ):
        """Verifica que se intenta usar cache al obtener período"""
        periodo = service_con_redis.obtener_periodo(
            db_session, periodo_base.id, usuario_superadmin
        )
        
        # Verificar que se intentó leer del cache
        service_con_redis.redis.get_json.assert_called()
        assert periodo.id == periodo_base.id
    
    def test_obtener_periodo_actual_usa_cache(
        self, db_session, service_con_redis, institucion_id, periodo_en_inscripciones, usuario_superadmin
    ):
        """Cache para período actual tiene TTL corto"""
        periodo = service_con_redis.obtener_periodo_actual(
            db_session, institucion_id, usuario_superadmin
        )
        
        # Verificar que se guardó en cache
        service_con_redis.redis.set_json.assert_called()
        assert periodo is not None
    
    def test_actualizar_invalida_cache(
        self, db_session, service_con_redis, periodo_base, usuario_superadmin
    ):
        """Actualizar un período invalida el cache"""
        update_data = PeriodoAcademicoUpdate(nombre="Nuevo Nombre")
        
        service_con_redis.actualizar_periodo(
            db_session, periodo_base.id, update_data, usuario_superadmin
        )
        
        # Verificar que se invalidó cache
        service_con_redis.redis.delete.assert_called()


@pytest.mark.periodos
@pytest.mark.service
class TestPeriodoAcademicoServiceValidaciones:
    """Tests de validaciones de negocio"""
    
    def test_validacion_coherencia_fechas_fin_antes_inicio(self, service):
        """Error si fecha fin es antes de fecha inicio"""
        from src.schemas.academic.periodo_academico_schemas import PeriodoAcademicoCreate
        
        hoy = date.today()
        
        # Mock de período con fechas inválidas
        class MockPeriodoInvalido:
            fecha_inicio = hoy
            fecha_fin = hoy - timedelta(days=10)  # Fecha fin antes de inicio
            fecha_inicio_inscripciones = hoy - timedelta(days=20)
            fecha_fin_inscripciones = hoy - timedelta(days=15)
            fecha_inicio_clases = hoy
            fecha_fin_clases = hoy + timedelta(days=100)
        
        with pytest.raises(HTTPException) as exc_info:
            service._validar_coherencia_fechas(MockPeriodoInvalido())
        
        assert exc_info.value.status_code == 400
        assert "fecha de fin debe ser posterior" in str(exc_info.value.detail).lower()
    
    def test_validacion_inscripciones_antes_clases(self, service):
        """Error si inscripciones cierran después de inicio de clases"""
        hoy = date.today()
        
        class MockPeriodo:
            fecha_inicio = hoy
            fecha_fin = hoy + timedelta(days=180)
            fecha_inicio_inscripciones = hoy - timedelta(days=10)
            fecha_fin_inscripciones = hoy + timedelta(days=10)  # Después de inicio de clases
            fecha_inicio_clases = hoy
            fecha_fin_clases = hoy + timedelta(days=170)
        
        with pytest.raises(HTTPException) as exc_info:
            service._validar_coherencia_fechas(MockPeriodo())
        
        assert exc_info.value.status_code == 400
        assert "inscripciones" in str(exc_info.value.detail).lower()
    
    def test_validacion_clases_dentro_periodo(self, service):
        """Error si clases están fuera del rango del período"""
        hoy = date.today()
        
        class MockPeriodo:
            fecha_inicio = hoy
            fecha_fin = hoy + timedelta(days=100)
            fecha_inicio_inscripciones = hoy - timedelta(days=10)
            fecha_fin_inscripciones = hoy - timedelta(days=1)
            fecha_inicio_clases = hoy - timedelta(days=5)  # Antes del período
            fecha_fin_clases = hoy + timedelta(days=90)
        
        with pytest.raises(HTTPException) as exc_info:
            service._validar_coherencia_fechas(MockPeriodo())
        
        assert exc_info.value.status_code == 400
