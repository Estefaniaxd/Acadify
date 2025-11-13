"""
Tests para CRUD de Período Académico

Tests de operaciones CRUD, búsquedas, filtros y validaciones.
Cobertura: 36 tests
"""
import pytest
from datetime import date, timedelta
from decimal import Decimal

from src.crud.academic.crud_periodo_academico import periodo_academico_crud
from src.models.academic.periodo_academico import PeriodoAcademico
from src.schemas.academic.periodo_academico_schemas import PeriodoAcademicoUpdate
from src.enums.academic import TipoPeriodo, EstadoPeriodo


@pytest.mark.periodos
@pytest.mark.crud
class TestPeriodoAcademicoCRUDBasico:
    """Tests de operaciones CRUD básicas"""
    
    def test_crear_periodo(self, db_session, institucion_id, usuario_coordinador_id):
        """Crea un período académico"""
        hoy = date.today()
        # Crear directamente con el modelo (schema tiene bug con UUID)
        periodo = PeriodoAcademico(
            institucion_id=institucion_id,
            nombre="Semestre 2025-1",
            codigo="SEM-2025-1",
            tipo=TipoPeriodo.semestral,
            estado=EstadoPeriodo.programado,
            anio=2025,
            numero_periodo=1,
            fecha_inicio=hoy + timedelta(days=30),
            fecha_fin=hoy + timedelta(days=180),
            fecha_inicio_inscripciones=hoy + timedelta(days=10),
            fecha_fin_inscripciones=hoy + timedelta(days=25),
            fecha_inicio_clases=hoy + timedelta(days=30),
            fecha_fin_clases=hoy + timedelta(days=170),
            creditos_minimos=12,
            creditos_maximos=20,
            creado_por_id=usuario_coordinador_id
        )
        
        db_session.add(periodo)
        db_session.commit()
        db_session.refresh(periodo)
        
        assert periodo.id is not None
        assert periodo.nombre == "Semestre 2025-1"
        assert periodo.codigo == "SEM-2025-1"
        assert periodo.tipo == TipoPeriodo.semestral
        assert periodo.creado_por_id == usuario_coordinador_id
    
    def test_obtener_periodo_por_id(self, db_session, periodo_base):
        """Obtiene un período por ID"""
        periodo = periodo_academico_crud.get(db_session, periodo_base.id)
        
        assert periodo is not None
        assert periodo.id == periodo_base.id
        assert periodo.nombre == periodo_base.nombre
    
    def test_obtener_periodo_inexistente(self, db_session):
        """Intenta obtener un período que no existe"""
        periodo = periodo_academico_crud.get(db_session, 99999)
        
        assert periodo is None
    
    def test_obtener_multiples_periodos(self, db_session, periodo_base, periodo_en_curso):
        """Obtiene múltiples períodos con paginación"""
        # Asegurar que los fixtures están en la sesión
        db_session.flush()
        
        periodos = periodo_academico_crud.get_multi(db_session, skip=0, limit=100)
        
        # Verificar que se obtienen al menos nuestros 2 períodos de fixtures
        assert len(periodos) >= 2, f"Se esperaban al menos 2 períodos, se obtuvieron {len(periodos)}"
        
        # Verificar que nuestros períodos específicos están en la lista
        ids_periodos = [p.id for p in periodos]
        assert periodo_base.id in ids_periodos, f"periodo_base (id={periodo_base.id}) no encontrado en {ids_periodos}"
        assert periodo_en_curso.id in ids_periodos, f"periodo_en_curso (id={periodo_en_curso.id}) no encontrado en {ids_periodos}"
    
    def test_actualizar_periodo(self, db_session, periodo_base, usuario_coordinador_id):
        """Actualiza un período existente"""
        update_data = PeriodoAcademicoUpdate(
            nombre="Semestre 2024-1 Actualizado",
            descripcion="Descripción actualizada",
            creditos_maximos=22
        )
        
        periodo_actualizado = periodo_academico_crud.update(
            db_session,
            db_obj=periodo_base,
            obj_in=update_data,
            modificado_por_id=usuario_coordinador_id
        )
        
        assert periodo_actualizado.nombre == "Semestre 2024-1 Actualizado"
        assert periodo_actualizado.descripcion == "Descripción actualizada"
        assert periodo_actualizado.creditos_maximos == 22
        assert periodo_actualizado.modificado_por_id == usuario_coordinador_id
    
    def test_eliminar_periodo(self, db_session, institucion_id):
        """Elimina un período"""
        hoy = date.today()
        periodo = PeriodoAcademico(
            institucion_id=institucion_id,
            nombre="Período a Eliminar",
            codigo="DEL-2025",
            tipo=TipoPeriodo.trimestral,
            anio=2025,
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
        
        periodo_id = periodo.id
        periodo_eliminado = periodo_academico_crud.remove(db_session, periodo_id=periodo_id)
        
        assert periodo_eliminado is not None
        assert periodo_academico_crud.get(db_session, periodo_id) is None


@pytest.mark.periodos
@pytest.mark.crud
class TestPeriodoAcademicoBusquedas:
    """Tests de búsquedas específicas"""
    
    def test_buscar_por_codigo(self, db_session, periodo_base):
        """Busca un período por código único"""
        periodo = periodo_academico_crud.get_by_codigo(db_session, periodo_base.codigo)
        
        assert periodo is not None
        assert periodo.id == periodo_base.id
        assert periodo.codigo == periodo_base.codigo
    
    def test_buscar_por_codigo_inexistente(self, db_session):
        """Busca un código que no existe"""
        periodo = periodo_academico_crud.get_by_codigo(db_session, "INEXISTENTE-999")
        
        assert periodo is None
    
    def test_listar_por_institucion(self, db_session, institucion_id, periodo_base, periodo_en_curso):
        """Lista todos los períodos de una institución"""
        periodos = periodo_academico_crud.get_by_institucion(
            db_session, institucion_id, skip=0, limit=10
        )
        
        assert len(periodos) >= 2
        assert all(p.institucion_id == institucion_id for p in periodos)
        # Verificar orden: más recientes primero
        if len(periodos) >= 2:
            assert periodos[0].anio >= periodos[1].anio
    
    def test_obtener_periodo_actual(self, db_session, institucion_id, periodo_en_inscripciones):
        """Obtiene el período marcado como actual"""
        periodo_actual = periodo_academico_crud.get_periodo_actual(db_session, institucion_id)
        
        assert periodo_actual is not None
        assert periodo_actual.es_actual is True
        assert periodo_actual.activo is True
    
    def test_obtener_periodo_actual_sin_marcado(self, db_session, institucion_id):
        """Obtiene período actual por fechas cuando no hay marcado"""
        hoy = date.today()
        # Crear período que contenga hoy pero sin marcar como actual
        periodo = PeriodoAcademico(
            institucion_id=institucion_id,
            nombre="Período Actual Sin Marcar",
            codigo="ACT-SIN-MARCA",
            tipo=TipoPeriodo.semestral,
            anio=2025,
            fecha_inicio=hoy - timedelta(days=10),
            fecha_fin=hoy + timedelta(days=150),
            fecha_inicio_inscripciones=hoy - timedelta(days=20),
            fecha_fin_inscripciones=hoy - timedelta(days=15),
            fecha_inicio_clases=hoy - timedelta(days=10),
            fecha_fin_clases=hoy + timedelta(days=145),
            activo=True,
            es_actual=False
        )
        db_session.add(periodo)
        db_session.commit()
        
        periodo_actual = periodo_academico_crud.get_periodo_actual(db_session, institucion_id)
        
        assert periodo_actual is not None
        assert periodo_actual.fecha_inicio <= hoy <= periodo_actual.fecha_fin
    
    def test_listar_periodos_activos(self, db_session, institucion_id, periodo_base):
        """Lista solo períodos activos"""
        periodos = periodo_academico_crud.get_periodos_activos(
            db_session, institucion_id, skip=0, limit=10
        )
        
        assert len(periodos) >= 1
        assert all(p.activo is True for p in periodos)
        assert all(p.estado != EstadoPeriodo.cancelado for p in periodos)
    
    def test_listar_por_anio(self, db_session, institucion_id, periodo_base):
        """Lista períodos de un año específico"""
        periodos = periodo_academico_crud.get_by_anio(
            db_session, institucion_id, 2024, skip=0, limit=10
        )
        
        assert len(periodos) >= 1
        assert all(p.anio == 2024 for p in periodos)
    
    def test_listar_por_tipo(self, db_session, institucion_id, periodo_en_curso):
        """Lista períodos de un tipo específico"""
        periodos = periodo_academico_crud.get_by_tipo(
            db_session, institucion_id, TipoPeriodo.trimestral, skip=0, limit=10
        )
        
        assert len(periodos) >= 1
        assert all(p.tipo == TipoPeriodo.trimestral for p in periodos)
    
    def test_listar_por_estado(self, db_session, institucion_id, periodo_finalizado):
        """Lista períodos por estado"""
        periodos = periodo_academico_crud.get_by_estado(
            db_session, institucion_id, EstadoPeriodo.finalizado, skip=0, limit=10
        )
        
        assert len(periodos) >= 1
        assert all(p.estado == EstadoPeriodo.finalizado for p in periodos)
    
    def test_obtener_periodos_con_inscripciones_abiertas(
        self, db_session, institucion_id, periodo_en_inscripciones
    ):
        """Obtiene períodos que actualmente aceptan inscripciones"""
        periodos = periodo_academico_crud.get_periodos_con_inscripciones_abiertas(
            db_session, institucion_id
        )
        
        assert len(periodos) >= 1
        assert all(p.permite_inscripciones is True for p in periodos)
        assert all(p.estado == EstadoPeriodo.inscripciones_abiertas for p in periodos)
        
        # Verificar fechas
        hoy = date.today()
        for periodo in periodos:
            assert periodo.fecha_inicio_inscripciones <= hoy <= periodo.fecha_fin_inscripciones
    
    def test_obtener_periodos_en_curso(self, db_session, institucion_id, periodo_en_curso):
        """Obtiene períodos actualmente en curso"""
        periodos = periodo_academico_crud.get_periodos_en_curso(db_session, institucion_id)
        
        assert len(periodos) >= 1
        assert all(p.estado == EstadoPeriodo.en_curso for p in periodos)
        
        hoy = date.today()
        for periodo in periodos:
            assert periodo.fecha_inicio_clases <= hoy <= periodo.fecha_fin_clases
    
    def test_obtener_periodos_proximos(self, db_session, institucion_id, periodo_base):
        """Obtiene períodos que iniciarán pronto"""
        periodos = periodo_academico_crud.get_periodos_proximos(
            db_session, institucion_id, dias=60
        )
        
        assert len(periodos) >= 1
        
        hoy = date.today()
        fecha_limite = hoy + timedelta(days=60)
        for periodo in periodos:
            assert hoy <= periodo.fecha_inicio_clases <= fecha_limite


@pytest.mark.periodos
@pytest.mark.crud
class TestPeriodoAcademicoFiltrosAvanzados:
    """Tests de filtros combinados"""
    
    def test_filtros_multiples(self, db_session, institucion_id, periodo_base):
        """Aplica múltiples filtros simultáneamente"""
        periodos, total = periodo_academico_crud.get_by_filtros(
            db_session,
            institucion_id,
            tipo=TipoPeriodo.semestral,
            anio=2024,
            activo=True,
            skip=0,
            limit=10
        )
        
        assert total >= 1
        assert len(periodos) >= 1
        for periodo in periodos:
            assert periodo.tipo == TipoPeriodo.semestral
            assert periodo.anio == 2024
            assert periodo.activo is True
    
    def test_filtros_visible_estudiantes(self, db_session, institucion_id):
        """Filtra por visibilidad para estudiantes"""
        periodos, total = periodo_academico_crud.get_by_filtros(
            db_session,
            institucion_id,
            visible_estudiantes=True,
            skip=0,
            limit=10
        )
        
        assert all(p.visible_estudiantes is True for p in periodos)
    
    def test_busqueda_por_nombre_o_codigo(self, db_session, institucion_id, periodo_base):
        """Busca períodos por nombre o código parcial"""
        # Buscar por parte del nombre
        periodos = periodo_academico_crud.search_by_nombre_o_codigo(
            db_session, institucion_id, "2024", skip=0, limit=10
        )
        
        assert len(periodos) >= 1
        assert any("2024" in p.nombre or "2024" in p.codigo for p in periodos)
    
    def test_paginacion(self, db_session, institucion_id):
        """Verifica que la paginación funciona correctamente"""
        # Crear varios períodos para paginar
        for i in range(5):
            hoy = date.today()
            periodo = PeriodoAcademico(
                institucion_id=institucion_id,
                nombre=f"Período Paginación {i}",
                codigo=f"PAG-{i}",
                tipo=TipoPeriodo.mensual,
                anio=2025,
                numero_periodo=i+1,
                fecha_inicio=hoy + timedelta(days=30*i),
                fecha_fin=hoy + timedelta(days=30*i + 30),
                fecha_inicio_inscripciones=hoy + timedelta(days=30*i - 5),
                fecha_fin_inscripciones=hoy + timedelta(days=30*i - 1),
                fecha_inicio_clases=hoy + timedelta(days=30*i),
                fecha_fin_clases=hoy + timedelta(days=30*i + 28)
            )
            db_session.add(periodo)
        db_session.commit()
        
        # Primera página
        periodos_p1, total = periodo_academico_crud.get_by_filtros(
            db_session, institucion_id, skip=0, limit=3
        )
        
        # Segunda página
        periodos_p2, _ = periodo_academico_crud.get_by_filtros(
            db_session, institucion_id, skip=3, limit=3
        )
        
        assert len(periodos_p1) == 3
        assert len(periodos_p2) >= 2
        assert total >= 5
        # No debe haber duplicados
        ids_p1 = {p.id for p in periodos_p1}
        ids_p2 = {p.id for p in periodos_p2}
        assert len(ids_p1.intersection(ids_p2)) == 0


@pytest.mark.periodos
@pytest.mark.crud
class TestPeriodoAcademicoOperacionesEstado:
    """Tests de operaciones de cambio de estado"""
    
    def test_activar_periodo(self, db_session, periodo_base, usuario_coordinador_id):
        """Activa un período desactivado"""
        periodo_base.activo = False
        db_session.commit()
        
        periodo_activado = periodo_academico_crud.activar(
            db_session, periodo_base.id, modificado_por_id=usuario_coordinador_id
        )
        
        assert periodo_activado is not None
        assert periodo_activado.activo is True
        assert periodo_activado.modificado_por_id == usuario_coordinador_id
    
    def test_desactivar_periodo(self, db_session, periodo_base, usuario_coordinador_id):
        """Desactiva un período activo"""
        periodo_desactivado = periodo_academico_crud.desactivar(
            db_session, periodo_base.id, modificado_por_id=usuario_coordinador_id
        )
        
        assert periodo_desactivado is not None
        assert periodo_desactivado.activo is False
    
    def test_marcar_como_actual(self, db_session, institucion_id, periodo_base, usuario_coordinador_id):
        """Marca un período como actual"""
        # Crear otro período actual primero
        hoy = date.today()
        periodo_viejo = PeriodoAcademico(
            institucion_id=institucion_id,
            nombre="Período Viejo Actual",
            codigo="VIEJO-ACT",
            tipo=TipoPeriodo.semestral,
            anio=2023,
            fecha_inicio=hoy - timedelta(days=200),
            fecha_fin=hoy - timedelta(days=50),
            fecha_inicio_inscripciones=hoy - timedelta(days=220),
            fecha_fin_inscripciones=hoy - timedelta(days=205),
            fecha_inicio_clases=hoy - timedelta(days=200),
            fecha_fin_clases=hoy - timedelta(days=55),
            activo=True,
            es_actual=True
        )
        db_session.add(periodo_viejo)
        db_session.commit()
        db_session.refresh(periodo_viejo)
        
        # Marcar periodo_base como actual
        periodo_nuevo_actual = periodo_academico_crud.marcar_como_actual(
            db_session,
            periodo_base.id,
            institucion_id,
            modificado_por_id=usuario_coordinador_id
        )
        
        assert periodo_nuevo_actual.es_actual is True
        assert periodo_nuevo_actual.activo is True
        
        # Verificar que el viejo ya no es actual
        db_session.refresh(periodo_viejo)
        assert periodo_viejo.es_actual is False
    
    def test_finalizar_periodo(self, db_session, periodo_en_curso, usuario_coordinador_id):
        """Finaliza un período en curso"""
        periodo_finalizado = periodo_academico_crud.finalizar(
            db_session, periodo_en_curso.id, modificado_por_id=usuario_coordinador_id
        )
        
        assert periodo_finalizado is not None
        assert periodo_finalizado.estado == EstadoPeriodo.finalizado
        assert periodo_finalizado.es_actual is False
    
    def test_cancelar_periodo(self, db_session, periodo_base, usuario_coordinador_id):
        """Cancela un período con motivo"""
        motivo = "Cancelado por falta de recursos"
        
        periodo_cancelado = periodo_academico_crud.cancelar(
            db_session,
            periodo_base.id,
            motivo,
            modificado_por_id=usuario_coordinador_id
        )
        
        assert periodo_cancelado is not None
        assert periodo_cancelado.estado == EstadoPeriodo.cancelado
        assert periodo_cancelado.activo is False
        assert motivo in periodo_cancelado.notas


@pytest.mark.periodos
@pytest.mark.crud
class TestPeriodoAcademicoValidaciones:
    """Tests de validaciones de negocio"""
    
    def test_existe_codigo_true(self, db_session, periodo_base):
        """Verifica que detecta código existente"""
        existe = periodo_academico_crud.existe_codigo(db_session, periodo_base.codigo)
        
        assert existe is True
    
    def test_existe_codigo_false(self, db_session):
        """Verifica código inexistente"""
        existe = periodo_academico_crud.existe_codigo(db_session, "CODIGO-INEXISTENTE")
        
        assert existe is False
    
    def test_existe_codigo_con_exclusion(self, db_session, periodo_base):
        """Verifica código excluyendo un ID (para updates)"""
        existe = periodo_academico_crud.existe_codigo(
            db_session, periodo_base.codigo, excluir_id=periodo_base.id
        )
        
        assert existe is False
    
    def test_conflicto_fechas_true(self, db_session, institucion_id, periodo_base):
        """Detecta conflicto de fechas con período existente"""
        # Intentar crear período con fechas superpuestas
        conflicto = periodo_academico_crud.tiene_conflicto_fechas(
            db_session,
            institucion_id,
            periodo_base.fecha_inicio + timedelta(days=10),  # Inicia durante periodo_base
            periodo_base.fecha_fin + timedelta(days=10),
            periodo_base.tipo
        )
        
        assert conflicto is True
    
    def test_conflicto_fechas_false(self, db_session, institucion_id, periodo_base):
        """No detecta conflicto cuando las fechas no se superponen"""
        # Período completamente después
        conflicto = periodo_academico_crud.tiene_conflicto_fechas(
            db_session,
            institucion_id,
            periodo_base.fecha_fin + timedelta(days=10),
            periodo_base.fecha_fin + timedelta(days=100),
            periodo_base.tipo
        )
        
        assert conflicto is False
    
    def test_conflicto_fechas_tipo_diferente(self, db_session, institucion_id, periodo_base):
        """No detecta conflicto si el tipo de período es diferente"""
        # Mismo rango de fechas pero tipo diferente
        conflicto = periodo_academico_crud.tiene_conflicto_fechas(
            db_session,
            institucion_id,
            periodo_base.fecha_inicio,
            periodo_base.fecha_fin,
            TipoPeriodo.trimestral  # Diferente al tipo de periodo_base
        )
        
        # No debe haber conflicto porque son tipos diferentes
        assert conflicto is False


@pytest.mark.periodos
@pytest.mark.crud
class TestPeriodoAcademicoEstadisticas:
    """Tests de estadísticas y contadores"""
    
    def test_obtener_estadisticas_basicas(self, db_session, institucion_id, periodo_base):
        """Obtiene estadísticas básicas de un período"""
        stats = periodo_academico_crud.get_estadisticas(db_session, institucion_id, periodo_base.id)
        
        assert stats is not None
        assert stats["periodo_id"] == periodo_base.id
        assert stats["nombre"] == periodo_base.nombre
        assert stats["codigo"] == periodo_base.codigo
        assert "estado" in stats
        assert "tipo" in stats
        assert "activo" in stats
        assert "permite_inscribirse_ahora" in stats
    
    def test_contar_periodos_por_institucion(self, db_session, institucion_id, periodo_base, periodo_en_curso):
        """Cuenta total de períodos de una institución"""
        total = periodo_academico_crud.count_by_institucion(db_session, institucion_id)
        
        assert total >= 2
    
    def test_contar_periodos_activos(self, db_session, institucion_id, periodo_base):
        """Cuenta períodos activos"""
        total_activos = periodo_academico_crud.count_activos(db_session, institucion_id)
        
        assert total_activos >= 1
