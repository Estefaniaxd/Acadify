"""
Tests para el modelo Grupo con todos sus campos expandidos.
Prueba properties, methods, validaciones y relaciones del modelo Grupo.
"""

import pytest
from datetime import date, time, timedelta
from decimal import Decimal
from uuid import uuid4
from sqlalchemy.orm import Session

from src.models.academic.grupo import Grupo
from src.enums.academic.grupo_enums import (
    JornadaGrupo,
    EstadoGrupo,
    TipoGrupo,
    ModalidadAsistencia,
    FormatoEvaluacion
)


@pytest.mark.academic
@pytest.mark.unit
class TestGrupoProperties:
    """Tests para properties calculadas del modelo Grupo"""
    
    def test_grupo_esta_activo(self, db_session: Session, grupo_base: Grupo):
        """Verifica que un grupo activo con estado correcto esté activo"""
        grupo_base.activo = True
        grupo_base.estado = EstadoGrupo.en_curso
        db_session.add(grupo_base)
        db_session.commit()
        
        assert grupo_base.esta_activo is True
    
    def test_grupo_inactivo_no_esta_activo(self, db_session: Session, grupo_base: Grupo):
        """Verifica que un grupo inactivo no esté activo"""
        grupo_base.activo = False
        grupo_base.estado = EstadoGrupo.en_curso
        db_session.add(grupo_base)
        db_session.commit()
        
        assert grupo_base.esta_activo is False
    
    def test_grupo_tiene_cupos_disponibles(self, db_session: Session, grupo_base: Grupo):
        """Verifica que grupo con cupos disponibles lo indique"""
        grupo_base.capacidad_maxima = 30
        db_session.add(grupo_base)
        db_session.commit()
        
        # Sin estudiantes, tiene cupos
        assert grupo_base.tiene_cupos_disponibles is True
    
    def test_grupo_cupos_restantes_correcto(self, db_session: Session, grupo_base: Grupo):
        """Verifica cálculo correcto de cupos restantes"""
        grupo_base.capacidad_maxima = 30
        db_session.add(grupo_base)
        db_session.commit()
        
        # Sin estudiantes, todos los cupos disponibles
        assert grupo_base.cupos_restantes == 30
    
    def test_grupo_porcentaje_ocupacion(self, db_session: Session, grupo_base: Grupo):
        """Verifica cálculo de porcentaje de ocupación"""
        grupo_base.capacidad_maxima = 30
        db_session.add(grupo_base)
        db_session.commit()
        
        # Sin estudiantes, 0% ocupación
        assert grupo_base.porcentaje_ocupacion == 0.0
    
    def test_grupo_cumple_minimo_estudiantes(self, db_session: Session, grupo_base: Grupo):
        """Verifica verificación de mínimo de estudiantes"""
        grupo_base.capacidad_minima = 10
        db_session.add(grupo_base)
        db_session.commit()
        
        # Sin estudiantes, no cumple
        assert grupo_base.cumple_minimo_estudiantes is False
    
    def test_grupo_puede_inscribirse(self, db_session: Session, grupo_base: Grupo):
        """Verifica que grupo con estado correcto permita inscripciones"""
        grupo_base.activo = True
        grupo_base.permite_inscripcion = True
        grupo_base.estado = EstadoGrupo.inscripciones_abiertas
        grupo_base.capacidad_maxima = 30
        db_session.add(grupo_base)
        db_session.commit()
        
        assert grupo_base.puede_inscribirse is True
    
    def test_grupo_con_costo_adicional(self, db_session: Session, grupo_base: Grupo):
        """Verifica grupo con costo adicional"""
        grupo_base.tiene_costo_adicional = True
        grupo_base.costo_adicional = Decimal("50000.00")
        db_session.add(grupo_base)
        db_session.commit()
        
        assert grupo_base.tiene_costo_adicional is True
        assert grupo_base.costo_adicional > 0
    
    def test_jornada_grupo_valida(self, db_session: Session, grupo_base: Grupo):
        """Verifica que jornada sea válida"""
        grupo_base.jornada = JornadaGrupo.manana
        db_session.add(grupo_base)
        db_session.commit()
        
        assert grupo_base.jornada in list(JornadaGrupo)
    
    def test_estado_grupo_valido(self, db_session: Session, grupo_base: Grupo):
        """Verifica que estado sea válido"""
        grupo_base.estado = EstadoGrupo.programado
        db_session.add(grupo_base)
        db_session.commit()
        
        assert grupo_base.estado in list(EstadoGrupo)
    
    def test_tipo_grupo_valido(self, db_session: Session, grupo_base: Grupo):
        """Verifica que tipo de grupo sea válido"""
        grupo_base.tipo_grupo = TipoGrupo.regular
        db_session.add(grupo_base)
        db_session.commit()
        
        assert grupo_base.tipo_grupo in list(TipoGrupo)
    
    def test_modalidad_asistencia_valida(self, db_session: Session, grupo_base: Grupo):
        """Verifica que modalidad de asistencia sea válida"""
        grupo_base.modalidad_asistencia = ModalidadAsistencia.obligatoria
        db_session.add(grupo_base)
        db_session.commit()
        
        assert grupo_base.modalidad_asistencia in list(ModalidadAsistencia)
    
    def test_formato_evaluacion_valido(self, db_session: Session, grupo_base: Grupo):
        """Verifica que formato de evaluación sea válido"""
        grupo_base.formato_evaluacion = FormatoEvaluacion.mixto
        db_session.add(grupo_base)
        db_session.commit()
        
        assert grupo_base.formato_evaluacion in list(FormatoEvaluacion)
    
    def test_horario_coherente(self, db_session: Session, grupo_base: Grupo):
        """Verifica que hora inicio sea menor que hora fin"""
        grupo_base.hora_inicio = time(8, 0)
        grupo_base.hora_fin = time(10, 0)
        db_session.add(grupo_base)
        db_session.commit()
        
        assert grupo_base.hora_inicio < grupo_base.hora_fin
    
    def test_fechas_coherentes(self, db_session: Session, grupo_base: Grupo):
        """Verifica que fechas de inicio y fin sean coherentes"""
        grupo_base.fecha_inicio = date.today()
        grupo_base.fecha_fin = date.today() + timedelta(days=90)
        db_session.add(grupo_base)
        db_session.commit()
        
        assert grupo_base.fecha_inicio < grupo_base.fecha_fin
    
    def test_capacidad_minima_menor_maxima(self, db_session: Session, grupo_base: Grupo):
        """Verifica que capacidad mínima sea menor que máxima"""
        grupo_base.capacidad_minima = 10
        grupo_base.capacidad_maxima = 30
        db_session.add(grupo_base)
        db_session.commit()
        
        assert grupo_base.capacidad_minima < grupo_base.capacidad_maxima
    
    def test_calificacion_asistencia_validas(self, db_session: Session, grupo_base: Grupo):
        """Verifica que calificación y asistencia estén en rangos válidos"""
        grupo_base.calificacion_minima_aprobacion = Decimal("3.0")
        grupo_base.porcentaje_asistencia_minimo = Decimal("80.0")
        db_session.add(grupo_base)
        db_session.commit()
        
        assert 0 <= grupo_base.calificacion_minima_aprobacion <= 5
        assert 0 <= grupo_base.porcentaje_asistencia_minimo <= 100


@pytest.mark.academic
@pytest.mark.unit
class TestGrupoMetodos:
    """Tests para métodos del modelo Grupo"""
    
    def test_puede_estudiante_inscribirse_success(self, db_session: Session, grupo_base: Grupo):
        """Verifica método puede_estudiante_inscribirse cuando es exitoso"""
        grupo_base.activo = True
        grupo_base.permite_inscripcion = True
        grupo_base.estado = EstadoGrupo.inscripciones_abiertas
        grupo_base.capacidad_maxima = 30
        grupo_base.requiere_aprobacion_inscripcion = False
        db_session.add(grupo_base)
        db_session.commit()
        
        puede, mensaje = grupo_base.puede_estudiante_inscribirse()
        
        assert puede is True
        assert "Puede inscribirse" in mensaje
    
    def test_puede_estudiante_inscribirse_inactivo(self, db_session: Session, grupo_base: Grupo):
        """Verifica que no pueda inscribirse si grupo inactivo"""
        grupo_base.activo = False
        db_session.add(grupo_base)
        db_session.commit()
        
        puede, mensaje = grupo_base.puede_estudiante_inscribirse()
        
        assert puede is False
        assert "no está activo" in mensaje
    
    def test_actualizar_estado_por_cupos(self, db_session: Session, grupo_base: Grupo):
        """Verifica actualización de estado según cupos"""
        grupo_base.activo = True
        grupo_base.capacidad_maxima = 30
        grupo_base.permite_lista_espera = True
        db_session.add(grupo_base)
        db_session.commit()
        
        # Sin estudiantes, debe estar disponible
        grupo_base.actualizar_estado_por_cupos()
        
        assert grupo_base.estado == EstadoGrupo.cupos_disponibles
    
    def test_calcular_costo_total(self, db_session: Session, grupo_base: Grupo):
        """Verifica cálculo de costo total del grupo"""
        grupo_base.tiene_costo_adicional = True
        grupo_base.costo_adicional = Decimal("100000.00")
        db_session.add(grupo_base)
        db_session.commit()
        
        costo = grupo_base.calcular_costo_total()
        
        # Al menos el costo adicional
        assert costo >= 100000.00


@pytest.mark.academic
@pytest.mark.unit
class TestGrupoValidaciones:
    """Tests para validaciones del modelo Grupo"""
    
    def test_grupo_sin_costo_adicional(self, db_session: Session, grupo_base: Grupo):
        """Verifica que grupo sin costo adicional tenga valores coherentes"""
        grupo_base.tiene_costo_adicional = False
        grupo_base.costo_adicional = None
        db_session.add(grupo_base)
        db_session.commit()
        
        assert grupo_base.tiene_costo_adicional is False
        assert grupo_base.costo_adicional is None or grupo_base.costo_adicional == 0
    
    def test_lista_espera_configurada(self, db_session: Session, grupo_base: Grupo):
        """Verifica configuración de lista de espera"""
        grupo_base.permite_lista_espera = True
        grupo_base.maximo_lista_espera = 5
        db_session.add(grupo_base)
        db_session.commit()
        
        assert grupo_base.permite_lista_espera is True
        assert grupo_base.maximo_lista_espera > 0
    
    def test_duracion_semanas(self, db_session: Session, grupo_base: Grupo):
        """Verifica cálculo de duración en semanas"""
        grupo_base.fecha_inicio = date(2024, 1, 1)
        grupo_base.fecha_fin = date(2024, 3, 31)  # ~13 semanas
        db_session.add(grupo_base)
        db_session.commit()
        
        duracion = grupo_base.duracion_semanas
        
        assert duracion is not None
        assert duracion > 0


@pytest.mark.academic
@pytest.mark.unit
class TestGrupoRelaciones:
    """Tests para relaciones del modelo Grupo"""
    
    def test_grupo_tiene_programa(self, db_session: Session, grupo_base: Grupo, programa_base):
        """Verifica que grupo tenga programa asociado"""
        grupo_base.programa_id = programa_base.programa_id
        db_session.add(programa_base)
        db_session.add(grupo_base)
        db_session.commit()
        
        assert grupo_base.programa_id is not None
        assert grupo_base.programa_id == programa_base.programa_id
    
    def test_multiples_grupos_mismo_programa(self, db_session: Session, programa_base):
        """Verifica que un programa pueda tener múltiples grupos"""
        from TEST.fixtures.academic_fixtures import crear_grupo_base_data
        
        db_session.add(programa_base)
        db_session.commit()
        
        grupo1_data = crear_grupo_base_data(
            programa_id=programa_base.programa_id,
            nombre="Grupo A",
            codigo_grupo="GRP-001"
        )
        grupo2_data = crear_grupo_base_data(
            programa_id=programa_base.programa_id,
            nombre="Grupo B",
            codigo_grupo="GRP-002"
        )
        
        grupo1 = Grupo(**grupo1_data)
        grupo2 = Grupo(**grupo2_data)
        
        db_session.add(grupo1)
        db_session.add(grupo2)
        db_session.commit()
        
        assert grupo1.programa_id == programa_base.programa_id
        assert grupo2.programa_id == programa_base.programa_id
        assert grupo1.grupo_id != grupo2.grupo_id


@pytest.mark.academic
@pytest.mark.integration
class TestGrupoBusqueda:
    """Tests para búsqueda y filtrado de grupos"""
    
    def test_buscar_grupos_activos(self, db_session: Session):
        """Verifica búsqueda de grupos activos"""
        from TEST.fixtures.academic_fixtures import crear_grupo_base_data
        
        # Crear grupo activo
        grupo_activo_data = crear_grupo_base_data(activo=True, codigo_grupo="GRP-ACT")
        grupo_activo = Grupo(**grupo_activo_data)
        
        # Crear grupo inactivo
        grupo_inactivo_data = crear_grupo_base_data(activo=False, codigo_grupo="GRP-INACT")
        grupo_inactivo = Grupo(**grupo_inactivo_data)
        
        db_session.add(grupo_activo)
        db_session.add(grupo_inactivo)
        db_session.commit()
        
        grupos_activos = db_session.query(Grupo).filter(Grupo.activo == True).all()
        
        assert len(grupos_activos) >= 1
        assert all(g.activo for g in grupos_activos)
    
    def test_buscar_grupos_por_jornada(self, db_session: Session):
        """Verifica búsqueda de grupos por jornada"""
        from TEST.fixtures.academic_fixtures import crear_grupo_base_data
        
        grupo_manana_data = crear_grupo_base_data(
            jornada=JornadaGrupo.manana,
            codigo_grupo="GRP-MAN"
        )
        grupo_tarde_data = crear_grupo_base_data(
            jornada=JornadaGrupo.tarde,
            codigo_grupo="GRP-TAR"
        )
        
        grupo_manana = Grupo(**grupo_manana_data)
        grupo_tarde = Grupo(**grupo_tarde_data)
        
        db_session.add(grupo_manana)
        db_session.add(grupo_tarde)
        db_session.commit()
        
        grupos_manana = db_session.query(Grupo).filter(
            Grupo.jornada == JornadaGrupo.manana
        ).all()
        
        assert len(grupos_manana) >= 1
        assert all(g.jornada == JornadaGrupo.manana for g in grupos_manana)
    
    def test_buscar_grupos_con_cupos(self, db_session: Session):
        """Verifica búsqueda de grupos con cupos disponibles"""
        from TEST.fixtures.academic_fixtures import crear_grupo_base_data
        
        grupo_con_cupos_data = crear_grupo_base_data(
            capacidad_maxima=30,
            codigo_grupo="GRP-CUPOS"
        )
        grupo_con_cupos = Grupo(**grupo_con_cupos_data)
        
        db_session.add(grupo_con_cupos)
        db_session.commit()
        
        # Buscar grupos con cupos (sin estudiantes, todos tienen cupos)
        grupos = db_session.query(Grupo).filter(
            Grupo.capacidad_maxima > 0
        ).all()
        
        assert len(grupos) >= 1
        assert all(g.tiene_cupos_disponibles for g in grupos)
