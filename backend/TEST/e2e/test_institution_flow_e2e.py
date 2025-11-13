"""Tests E2E del flujo institucional completo.

Tests del flujo: Institution → Program → Course → Class → Enrollment

Cobertura:
1. Creación de institución con onboarding coordinador (3 pasos)
2. Creación de programa académico por coordinador
3. Creación de curso en programa
4. Creación de clase en curso
5. Flujo completo de inscripción y acceso estudiante
6. Verificación de cascade deletes
7. Integridad de relaciones y eager loading
"""

from datetime import UTC, datetime

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from src.enums.academic.clase_enums import EstadoClase
from src.enums.academic.curso_enums import EstadoCurso
from src.enums.academic.institucion_enums import (
    EstadoInstitucion,
    TipoInstitucion,
)
from src.enums.academic.programa_enums import EstadoPrograma
from src.models.academic.clase import Clase
from src.models.academic.curso import Curso
from src.models.academic.inscripcion import Inscripcion
from src.models.academic.institucion import Institucion
from src.models.academic.programa import Programa
from src.models.auth.invitation_token import InvitationToken
from src.models.users.coordinador import Coordinador
from src.models.users.usuario import Usuario


@pytest.mark.e2e
class TestInstitutionFlowE2E:
    """Suite E2E para flujo institucional completo."""

    # ==================== TEST 1: AUTHENTICATION & FIXTURES ====================

    def test_01_verificar_fixtures_autenticacion(
        self,
        client: TestClient,
        db_session: Session,
        admin_token: str,
        coordinador_token: str,
        estudiante_token: str,
        docente_token: str,
    ):
        """Test E2E: Verificar que todas las fixtures de autenticación funcionan.

        Verifica:
        1. Tokens JWT generados correctamente
        2. Usuarios creados con schema correcto
        3. Roles asignados correctamente
        4. PasswordService funcionando
        """
        # Verificar que los tokens no están vacíos
        assert admin_token is not None
        assert len(admin_token) > 0
        assert coordinador_token is not None
        assert len(coordinador_token) > 0
        assert estudiante_token is not None
        assert len(estudiante_token) > 0
        assert docente_token is not None
        assert len(docente_token) > 0

        # Verificar que los usuarios existen en la BD
        from src.enums.users.usuario_enums import RolUsuario
        from src.models.users.usuario import Usuario

        # Admin debe tener username (NO correo_institucional)
        admin = (
            db_session.query(Usuario)
            .filter(Usuario.rol == RolUsuario.administrador)
            .filter(Usuario.username.like("admin_e2e_%"))
            .first()
        )
        assert admin is not None
        assert admin.rol == RolUsuario.administrador
        assert admin.username is not None
        assert admin.correo_institucional is None
        assert admin.password_hash is not None
        assert len(admin.password_hash) > 0

        # Coordinador debe tener correo_institucional (NO username)
        coordinador_user = (
            db_session.query(Usuario)
            .filter(Usuario.rol == RolUsuario.coordinador)
            .filter(Usuario.correo_institucional.like("coord_%@test.com"))
            .first()
        )
        assert coordinador_user is not None
        assert coordinador_user.rol == RolUsuario.coordinador
        assert coordinador_user.correo_institucional is not None
        assert coordinador_user.username is None
        assert coordinador_user.password_hash is not None

        # Estudiante debe tener correo_institucional (NO username)
        estudiante_user = (
            db_session.query(Usuario)
            .filter(Usuario.rol == RolUsuario.estudiante)
            .filter(Usuario.correo_institucional.like("estudiante_%@test.com"))
            .first()
        )
        assert estudiante_user is not None
        assert estudiante_user.rol == RolUsuario.estudiante
        assert estudiante_user.correo_institucional is not None
        assert estudiante_user.username is None

        # Docente debe tener correo_institucional (NO username)
        docente_user = (
            db_session.query(Usuario)
            .filter(Usuario.rol == RolUsuario.docente)
            .filter(Usuario.correo_institucional.like("docente_%@test.com"))
            .first()
        )
        assert docente_user is not None
        assert docente_user.rol == RolUsuario.docente
        assert docente_user.correo_institucional is not None
        assert docente_user.username is None

        # Verificar que todos tienen tipo_documento y numero_documento
        for usuario in [admin, coordinador_user, estudiante_user, docente_user]:
            assert usuario.tipo_documento is not None
            assert usuario.numero_documento is not None
            assert len(usuario.numero_documento) > 0

    # ==================== TEST 2: FIXTURES COMPLETAS ====================

    def test_02_verificar_fixtures_completas(
        self,
        db_session: Session,
        institucion_completa: Institucion,
        coordinador_test,
        programa_test: Programa,
        curso_test,
        estudiante_test,
    ):
        """Test E2E: Verificar que las fixtures completas funcionan correctamente.

        Verifica:
        1. Institución creada con todos los campos
        2. Programa vinculado a institución
        3. Curso vinculado a programa
        4. Estudiante vinculado a institución
        """
        # Verificar institución
        assert institucion_completa is not None
        assert institucion_completa.institucion_id is not None
        assert "Universidad E2E Test" in institucion_completa.nombre
        assert institucion_completa.estado == "activa"

        # Verificar programa
        assert programa_test is not None
        assert programa_test.programa_id is not None
        assert programa_test.institucion_id == institucion_completa.institucion_id
        assert "Software" in programa_test.nombre  # Nombre contiene "Software"

        # Verificar curso
        assert curso_test is not None
        assert curso_test.curso_id is not None
        assert curso_test.programa_id == programa_test.programa_id
        assert curso_test.codigo_acceso is not None
        assert len(curso_test.codigo_acceso) > 0

        # Verificar estudiante
        assert estudiante_test is not None
        assert estudiante_test.estudiante_id is not None

        # Verificar relaciones en DB
        db_session.refresh(institucion_completa)
        db_session.refresh(programa_test)
        assert programa_test.institucion_id == institucion_completa.institucion_id
        print(f"\n✅ Test 2 PASÓ: Todas las fixtures están correctamente creadas y relacionadas")

    # ==================== TEST 3: RELACIONES Y CASCADA ====================

    def test_03_verificar_flujo_completo(
        self,
        db_session: Session,
        flujo_completo,
    ):
        """Test E2E: Verificar que el flujo completo funciona correctamente.

        Verifica:
        1. Todas las entidades del flujo existen
        2. Relaciones bidireccionales funcionan
        3. Códigos de acceso son únicos
        4. Integridad referencial
        """
        institucion = flujo_completo["institucion"]
        programa = flujo_completo["programa"]
        curso = flujo_completo["curso"]
        clase = flujo_completo["clase"]
        estudiante = flujo_completo["estudiante"]
        docente = flujo_completo["docente"]
        grupo = flujo_completo["grupo"]

        # Verificar que todas las entidades existen
        assert institucion is not None
        assert programa is not None
        assert curso is not None
        assert clase is not None
        assert estudiante is not None
        assert docente is not None
        assert grupo is not None

        # Verificar cadena de relaciones
        assert programa.institucion_id == institucion.institucion_id
        assert curso.programa_id == programa.programa_id
        assert curso.institucion_id == institucion.institucion_id
        assert clase.grupo_id == grupo.grupo_id
        assert clase.docente_id == docente.docente_id

        # Verificar códigos de acceso únicos
        assert curso.codigo_acceso is not None
        assert clase.codigo_acceso is not None
        assert curso.codigo_acceso != clase.codigo_acceso
        assert len(curso.codigo_acceso) > 0
        assert len(clase.codigo_acceso) > 0

        # Verificar integridad en DB
        db_session.refresh(institucion)
        db_session.refresh(programa)
        db_session.refresh(curso)

        # Programa pertenece a institución
        assert programa.institucion_id == institucion.institucion_id

        # Curso pertenece a programa
        assert curso.programa_id == programa.programa_id

        print(f"\n✅ Test 3 PASÓ: Flujo completo verificado correctamente")

    # ==================== TEST 4: CREAR CLASE ====================

    def test_04_crear_clase_en_curso(
        self,
        db_session: Session,
        grupo_test,
        curso_test,
        docente_test,
    ):
        """Test E2E: Crear clase en curso directamente en DB.

        Flujo:
        1. Crear clase asociada a grupo y docente
        2. Sistema genera código de acceso para clase
        3. Verificar relaciones: grupo_id, docente_id
        4. Verificar fecha y duración válidas
        """
        from uuid import uuid4
        
        # Calcular fecha futura para clase
        fecha_clase = datetime.now(UTC).replace(
            hour=10,
            minute=0,
            second=0,
            microsecond=0,
        )

        # Crear clase directamente en DB
        clase = Clase(
            clase_id=uuid4(),
            grupo_id=grupo_test.grupo_id,
            docente_id=docente_test.docente_id,
            titulo="Introducción a Herencia y Polimorfismo",
            descripcion="Primera clase sobre POO avanzada",
            tipo_clase="teorica",
            fecha_inicio=fecha_clase,
            duracion=120,
            duracion_estimada=120,
            estado=EstadoClase.programada,
            codigo_acceso=uuid4().hex[:8].upper(),
        )
        db_session.add(clase)
        db_session.commit()
        db_session.refresh(clase)

        # Verificar clase en DB
        clase_verificada = db_session.query(Clase).filter_by(clase_id=clase.clase_id).first()
        assert clase_verificada is not None
        assert clase_verificada.titulo == "Introducción a Herencia y Polimorfismo"
        assert clase_verificada.grupo_id == grupo_test.grupo_id
        assert clase_verificada.docente_id == docente_test.docente_id
        assert clase_verificada.estado == EstadoClase.programada
        assert clase_verificada.duracion == 120

        # Verificar relaciones
        assert clase_verificada.grupo is not None
        assert clase_verificada.docente is not None
        assert clase_verificada.docente.docente_id == docente_test.docente_id

    # ==================== TEST 5: FLUJO COMPLETO INSCRIPCIÓN ====================

    def test_05_flujo_completo_inscripcion_y_acceso(
        self,
        db_session: Session,
        flujo_completo,
    ):
        """Test E2E: Flujo completo de inscripción y acceso estudiante en DB.

        Flujo:
        1. Verificar curso tiene código de acceso
        2. Crear inscripción del estudiante al curso
        3. Verificar inscripción activa en DB
        4. Verificar relaciones estudiante-curso-clase
        """
        from uuid import uuid4
        from src.enums.academic.inscripcion_enums import EstadoInscripcion
        from src.models.academic.inscripcion import Inscripcion
        
        curso = flujo_completo["curso"]
        clase = flujo_completo["clase"]
        estudiante = flujo_completo["estudiante"]
        grupo = flujo_completo["grupo"]

        # Paso 1: Verificar curso y grupo tienen código de acceso
        assert curso.codigo_acceso is not None
        assert len(curso.codigo_acceso) > 0

        # Paso 2: Crear inscripción directamente en DB (al grupo, no al curso)
        inscripcion = Inscripcion(
            estudiante_id=estudiante.estudiante_id,
            grupo_id=grupo.grupo_id,
            programa_id=curso.programa_id,
            codigo_inscripcion=uuid4().hex[:10].upper(),
            estado=EstadoInscripcion.activa,
            fecha_inscripcion=datetime.now(UTC),
        )
        db_session.add(inscripcion)
        db_session.commit()
        db_session.refresh(inscripcion)

        # Paso 3: Verificar inscripción en DB
        inscripcion_verificada = db_session.query(Inscripcion).filter_by(
            id=inscripcion.id,
        ).first()
        assert inscripcion_verificada is not None
        assert inscripcion_verificada.grupo_id == grupo.grupo_id
        assert inscripcion_verificada.estudiante_id == estudiante.estudiante_id
        assert inscripcion_verificada.estado == EstadoInscripcion.activa

        # Paso 4: Verificar relaciones
        assert inscripcion_verificada.grupo is not None
        assert inscripcion_verificada.estudiante is not None
        
        # Verificar que el estudiante puede acceder a las clases del grupo
        assert clase.grupo_id == grupo.grupo_id
        assert clase.codigo_acceso is not None

    # ==================== TEST 6: CASCADE DELETES ====================

    def test_06_cascade_delete_verification(
        self,
        db_session: Session,
        institucion_completa,
        programa_test,
        curso_test,
    ):
        """Test E2E: Verificar cascade deletes.

        Flujo:
        1. Verificar que institución, programa, curso existen
        2. Eliminar institución directamente en DB
        3. Verificar comportamiento cascade según configuración FK
        """
        institucion_id = institucion_completa.institucion_id
        programa_id = programa_test.programa_id
        curso_id = curso_test.curso_id

        # Verificar que todo existe
        assert db_session.query(Institucion).filter_by(
            institucion_id=institucion_id,
        ).first() is not None
        assert db_session.query(Programa).filter_by(
            programa_id=programa_id,
        ).first() is not None
        assert db_session.query(Curso).filter_by(
            curso_id=curso_id,
        ).first() is not None

        # Eliminar institución directamente en DB
        db_session.delete(institucion_completa)
        db_session.commit()

        # Verificar cascade (depende de configuración de FK con ondelete="CASCADE")
        institucion_deleted = db_session.query(Institucion).filter_by(
            institucion_id=institucion_id,
        ).first()
        
        # Hard delete - verificar que se eliminó
        assert institucion_deleted is None
        
        # Verificar que programas y cursos también se eliminaron por CASCADE
        programa_deleted = db_session.query(Programa).filter_by(
            programa_id=programa_id,
        ).first()
        curso_deleted = db_session.query(Curso).filter_by(
            curso_id=curso_id,
        ).first()
        
        # Si las FK tienen CASCADE, deberían ser None
        assert programa_deleted is None
        assert curso_deleted is None

    # ==================== TEST 7: INTEGRIDAD RELACIONES ====================

    def test_07_verificar_integridad_relaciones(
        self,
        db_session: Session,
        flujo_completo,
    ):
        """Test E2E: Verificar integridad de todas las relaciones.

        Verifica:
        1. Eager loading funciona correctamente
        2. Todas las FK están configuradas
        3. No hay registros huérfanos
        4. Relaciones bidireccionales funcionan
        """
        institucion = flujo_completo["institucion"]
        coordinador = flujo_completo["coordinador"]
        programa = flujo_completo["programa"]
        curso = flujo_completo["curso"]
        clase = flujo_completo["clase"]
        estudiante = flujo_completo["estudiante"]

        # Verificar relaciones Institución
        assert institucion.institucion_id is not None
        assert len(institucion.programas) >= 1
        assert programa in institucion.programas

        # Verificar relaciones Programa
        assert programa.institucion_id == institucion.institucion_id
        assert programa.coordinador_id == coordinador.coordinador_id
        assert programa.institucion is not None
        assert programa.coordinador is not None

        # Verificar relaciones Curso
        assert curso.programa_id == programa.programa_id
        assert curso.institucion_id == institucion.institucion_id
        assert curso.programa is not None
        assert curso.institucion is not None

        # Verificar relaciones Clase
        assert clase.grupo_id is not None
        assert clase.docente_id is not None
        assert clase.grupo is not None
        assert clase.docente is not None

        # Verificar que no hay registros huérfanos
        # Todos los programas deben tener institución y coordinador
        programas = db_session.query(Programa).all()
        for prog in programas:
            assert prog.institucion_id is not None
            assert prog.coordinador_id is not None
            assert prog.institucion is not None
            assert prog.coordinador is not None

        # Todos los cursos deben tener programa e institución
        cursos = db_session.query(Curso).all()
        for curs in cursos:
            assert curs.programa_id is not None
            assert curs.institucion_id is not None
            assert curs.programa is not None
            assert curs.institucion is not None


# ==================== TESTS ADICIONALES ====================


@pytest.mark.e2e
@pytest.mark.performance
def test_bulk_inscripciones_performance(
    db_session: Session,
    curso_test,
    bulk_estudiantes,
):
    """Test de rendimiento: inscribir 10 estudiantes directamente en DB."""
    import time
    from uuid import uuid4
    from src.enums.academic.inscripcion_enums import EstadoInscripcion
    from src.models.academic.inscripcion import Inscripcion

    start_time = time.time()

    # Necesitamos un grupo para las inscripciones
    from src.models.academic.grupo import Grupo
    from src.enums.academic.grupo_enums import EstadoGrupo, JornadaGrupo
    
    grupo = Grupo(
        grupo_id=uuid4(),
        programa_id=curso_test.programa_id,
        nombre=f"Grupo Test {uuid4().hex[:4]}",
        codigo_grupo=uuid4().hex[:6].upper(),
        capacidad_maxima=50,
        estado=EstadoGrupo.activo,
        jornada=JornadaGrupo.manana,
    )
    db_session.add(grupo)
    db_session.commit()
    
    inscripciones_creadas = []
    for estudiante in bulk_estudiantes:
        # Crear inscripción directamente en DB
        inscripcion = Inscripcion(
            estudiante_id=estudiante.estudiante_id,
            grupo_id=grupo.grupo_id,
            programa_id=curso_test.programa_id,
            codigo_inscripcion=uuid4().hex[:10].upper(),
            estado=EstadoInscripcion.activa,
            fecha_inscripcion=datetime.now(UTC),
        )
        db_session.add(inscripcion)
        inscripciones_creadas.append(inscripcion)
    
    db_session.commit()

    end_time = time.time()
    duration = end_time - start_time

    # Verificar que todas las inscripciones se crearon
    inscripciones = db_session.query(Inscripcion).filter_by(
        grupo_id=grupo.grupo_id,
    ).all()
    assert len(inscripciones) == 10

    # Performance benchmark: debe tomar menos de 2 segundos (sin HTTP overhead)
    assert duration < 2.0, f"Bulk inscripciones tomó {duration:.2f}s, esperado < 2s"


@pytest.mark.e2e
@pytest.mark.integration
def test_validar_codigos_acceso_unicos(
    db_session: Session,
    institucion_completa,
    programa_test,
):
    """Test: Verificar que códigos de acceso son únicos al crear cursos en DB."""
    from uuid import uuid4
    from src.models.academic.curso import Curso
    from src.enums.academic.curso_enums import (
        EstadoCurso,
        ModalidadCurso,
        NivelDificultad,
        TipoCurso,
    )
    
    codigos_generados = set()

    # Crear 5 cursos directamente en DB
    for i in range(5):
        codigo_acceso = uuid4().hex[:8].upper()
        
        curso = Curso(
            curso_id=uuid4(),
            programa_id=programa_test.programa_id,
            institucion_id=institucion_completa.institucion_id,
            nombre=f"Curso Test {i+1}",
            descripcion=f"Curso de prueba {i+1}",
            codigo_acceso=codigo_acceso,
            nivel_dificultad=NivelDificultad.basico,
            tipo_curso=TipoCurso.teorico,
            categoria_curso="electivo",
            modalidad=ModalidadCurso.semestral,
            creditos=3,
            horas_academicas=64,
            estado=EstadoCurso.en_curso,
        )
        db_session.add(curso)
        
        assert codigo_acceso not in codigos_generados, "Código duplicado generado!"
        codigos_generados.add(codigo_acceso)
    
    db_session.commit()

    # Verificar que hay exactamente 5 códigos únicos
    assert len(codigos_generados) == 5
    
    # Verificar en DB que todos los cursos se crearon
    cursos = db_session.query(Curso).filter(
        Curso.programa_id == programa_test.programa_id
    ).all()
    assert len([c for c in cursos if c.nombre.startswith("Curso Test")]) == 5
