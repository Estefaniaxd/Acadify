"""Fixtures E2E para tests del flujo institucional completo.

Proporciona fixtures reutilizables para:
- Instituciones completas
- Coordinadores con autenticación
- Programas académicos
- Cursos con códigos de acceso
- Clases con materiales
- Grupos y estudiantes
"""

from datetime import UTC, datetime, timedelta
from uuid import uuid4

import pytest
from sqlalchemy.orm import Session

from src.enums.academic.clase_enums import EstadoClase, EstadoCodigoAcceso, TipoClase
from src.enums.academic.curso_enums import (
    CategoriaCurso,
    EstadoCurso,
    IdiomaCurso,
    NivelDificultad,
    TipoCurso,
)
from src.enums.academic.institucion_enums import (
    EstadoInstitucion,
    TipoInstitucion,
)
from src.enums.academic.programa_enums import (
    DuracionPrograma,
    EstadoPrograma,
    NivelPrograma,
    TipoPrograma,
)
from src.models.academic.clase import Clase
from src.models.academic.curso import Curso
from src.models.academic.grupo import Grupo
from src.models.academic.institucion import Institucion
from src.models.academic.programa import Programa
from src.models.users.coordinador import Coordinador
from src.models.users.docente import Docente
from src.models.users.estudiante import Estudiante
from src.models.users.usuario import Usuario


# ==================== INSTITUTION FIXTURES ====================


@pytest.fixture
def institucion_completa(db_session: Session):
    """Crea una institución completa y activa."""
    from src.enums.academic.institucion_enums import (
        NivelEducativoInstitucion,
        SectorInstitucion,
    )
    
    # Generar identificador único para evitar conflictos entre tests
    unique_id = uuid4().hex[:8]
    
    institucion = Institucion(
        institucion_id=uuid4(),
        nombre=f"Universidad E2E Test {unique_id}",
        tipo_institucion=TipoInstitucion.universidad,
        usa_programas=True,
        nivel_educativo=NivelEducativoInstitucion.superior,
        sector=SectorInstitucion.publico,
        estado="activa",
        dominio_principal=f"e2etest{unique_id}.edu.co",
        ciudad="Bogotá",
        pais="Colombia",
        correo_institucional=f"contacto{unique_id}@e2etest.edu.co",
        telefono="+57 1 234 5678",
        direccion="Calle 123 #45-67",
        logo_url="",
        modalidad_ensenanza="presencial",
    )
    db_session.add(institucion)
    db_session.commit()
    db_session.refresh(institucion)
    return institucion


@pytest.fixture
def institucion_con_coordinador(db_session: Session, institucion_completa):
    """Crea institución con coordinador asignado."""
    from src.enums.users.usuario_enums import (
        EstadoCuentaUsuario,
        RolUsuario,
        TipoDocumentoUsuario,
    )
    from src.services.auth.password_service import PasswordService
    
    password_service = PasswordService()
    
    # Crear usuario coordinador (usa correo_institucional, NO username)
    usuario = Usuario(
        usuario_id=uuid4(),
        correo_institucional="coordinador.e2e@test.com",
        username=None,
        nombres="Coordinador",
        apellidos="E2E Test",
        tipo_documento=TipoDocumentoUsuario.cc,
        numero_documento=f"{uuid4().int % 10000000000}",
        rol=RolUsuario.coordinador,
        password_hash=password_service.hash_password("Coord123!"),
        estado_cuenta=EstadoCuentaUsuario.activo,
        email_verified=True,
    )
    db_session.add(usuario)
    db_session.flush()
    
    # Crear coordinador (solo tiene coordinador_id, horario_atencion, fecha_inicio_carrera)
    from datetime import date
    coordinador = Coordinador(
        coordinador_id=usuario.usuario_id,
        horario_atencion="Lun-Vie 8:00-17:00",
        fecha_inicio_carrera=date(2024, 1, 15),
    )
    db_session.add(coordinador)
    db_session.commit()
    db_session.refresh(coordinador)
    
    return {
        "institucion": institucion_completa,
        "coordinador": coordinador,
        "usuario": usuario,
    }


# ==================== USER FIXTURES ====================


@pytest.fixture
def coordinador_test(db_session: Session, institucion_completa):
    """Crea un coordinador de prueba asociado a institución."""
    from src.enums.users.usuario_enums import (
        EstadoCuentaUsuario,
        RolUsuario,
        TipoDocumentoUsuario,
    )
    from src.services.auth.password_service import PasswordService
    
    password_service = PasswordService()
    
    usuario = Usuario(
        usuario_id=uuid4(),
        correo_institucional=f"coord_{uuid4().hex[:8]}@test.com",
        username=None,
        nombres="Coordinador",
        apellidos="Fixture Test",
        tipo_documento=TipoDocumentoUsuario.cc,
        numero_documento=f"{uuid4().int % 10000000000}",
        rol=RolUsuario.coordinador,
        password_hash=password_service.hash_password("Coord123!"),
        estado_cuenta=EstadoCuentaUsuario.activo,
        email_verified=True,
    )
    db_session.add(usuario)
    db_session.flush()
    
    # Coordinador solo tiene: coordinador_id, horario_atencion, fecha_inicio_carrera
    from datetime import date
    coordinador = Coordinador(
        coordinador_id=usuario.usuario_id,
        horario_atencion="Lun-Vie 8:00-17:00",
        fecha_inicio_carrera=date(2024, 1, 15),
    )
    db_session.add(coordinador)
    db_session.commit()
    db_session.refresh(coordinador)
    
    return coordinador


@pytest.fixture
def docente_test(db_session: Session):
    """Crea un docente de prueba."""
    from src.enums.users.usuario_enums import (
        EstadoCuentaUsuario,
        RolUsuario,
        TipoDocumentoUsuario,
    )
    from src.services.auth.password_service import PasswordService
    
    password_service = PasswordService()
    
    usuario = Usuario(
        usuario_id=uuid4(),
        correo_institucional=f"docente_{uuid4().hex[:8]}@test.com",
        username=None,
        nombres="Docente",
        apellidos="Fixture Test",
        tipo_documento=TipoDocumentoUsuario.cc,
        numero_documento=f"{uuid4().int % 10000000000}",
        rol=RolUsuario.docente,
        password_hash=password_service.hash_password("Docente123!"),
        estado_cuenta=EstadoCuentaUsuario.activo,
        email_verified=True,
    )
    db_session.add(usuario)
    db_session.flush()
    
    # Docente: docente_id, area_conocimiento, fecha_vinculacion, tipo_vinculacion, etc
    from datetime import date
    from src.enums.users.docente_enums import TipoVinculacionDocente
    docente = Docente(
        docente_id=usuario.usuario_id,
        area_conocimiento="Ingeniería de Software",
        fecha_vinculacion=date(2024, 1, 15),
        tipo_vinculacion=TipoVinculacionDocente.planta,
        titulo_academico="Magister en Software",
        horas_semanales=40,
    )
    db_session.add(docente)
    db_session.commit()
    db_session.refresh(docente)
    
    return docente


@pytest.fixture
def estudiante_test(db_session: Session, institucion_completa):
    """Crea un estudiante de prueba."""
    from src.enums.users.usuario_enums import (
        EstadoCuentaUsuario,
        RolUsuario,
        TipoDocumentoUsuario,
    )
    from src.services.auth.password_service import PasswordService
    
    password_service = PasswordService()
    
    usuario = Usuario(
        usuario_id=uuid4(),
        correo_institucional=f"estudiante_{uuid4().hex[:8]}@test.com",
        username=None,
        nombres="Estudiante",
        apellidos="Fixture Test",
        tipo_documento=TipoDocumentoUsuario.cc,
        numero_documento=f"{uuid4().int % 10000000000}",
        rol=RolUsuario.estudiante,
        password_hash=password_service.hash_password("Estudiante123!"),
        estado_cuenta=EstadoCuentaUsuario.activo,
        email_verified=True,
    )
    db_session.add(usuario)
    db_session.flush()
    
    # Estudiante: estudiante_id, programa_id, fecha_ingreso, etapa_formativa, etc
    from datetime import date
    from src.enums.users.estudiante_enums import EtapaFormativaEstudiante
    estudiante = Estudiante(
        estudiante_id=usuario.usuario_id,
        programa_id=None,
        fecha_ingreso=date(2024, 1, 15),
        etapa_formativa=EtapaFormativaEstudiante.i,
        creditos_aprobados=0,
        promedio_acumulado=None,
    )
    db_session.add(estudiante)
    db_session.commit()
    db_session.refresh(estudiante)
    
    return estudiante


# ==================== ACADEMIC FIXTURES ====================


@pytest.fixture
def programa_test(db_session: Session, institucion_completa, coordinador_test):
    """Crea un programa académico de prueba."""
    programa = Programa(
        programa_id=uuid4(),
        institucion_id=institucion_completa.institucion_id,
        coordinador_id=coordinador_test.coordinador_id,
        nombre="Ingeniería de Software E2E",
        codigo=f"SOFT{uuid4().hex[:6].upper()}",
        descripcion="Programa de prueba para tests E2E",
        nivel=NivelPrograma.pregrado,
        tipo=TipoPrograma.presencial,
        estado=EstadoPrograma.activo,
        duracion_tipo=DuracionPrograma.semestral,
        duracion_periodos=10,
        duracion_meses=60,
        numero_niveles=10,
        creditos_totales=160,
        creditos_obligatorios=120,
        creditos_electivos=30,
        creditos_libres=10,
        cupos_por_periodo=50,
        permite_inscripcion=True,
        activo=True,
        fecha_creacion=datetime.now(UTC),
    )
    db_session.add(programa)
    db_session.commit()
    db_session.refresh(programa)
    
    return programa


@pytest.fixture
def curso_test(
    db_session: Session,
    institucion_completa,
    coordinador_test,
    programa_test,
):
    """Crea un curso de prueba asociado a programa."""
    codigo_acceso = f"TEST{uuid4().hex[:6].upper()}"
    
    from src.enums.academic.curso_enums import ModalidadCurso
    curso = Curso(
        curso_id=uuid4(),
        institucion_id=institucion_completa.institucion_id,
        coordinador_id=coordinador_test.coordinador_id,
        programa_id=programa_test.programa_id,
        codigo_acceso=codigo_acceso,
        nombre="Programación Avanzada E2E",
        descripcion="Curso de prueba para tests E2E",
        codigo_curso="PROG101",
        nivel_dificultad=NivelDificultad.intermedio,
        tipo_curso=TipoCurso.teorico_practico,
        categoria_curso=CategoriaCurso.obligatorio,
        modalidad=ModalidadCurso.semestral,
        estado=EstadoCurso.en_curso,
        idioma=IdiomaCurso.espanol,
        creditos=4,
        horas_academicas=96,
        cupos_disponibles=30,
        maximo_estudiantes=30,
        permite_inscripcion=True,
        activo=True,
    )
    db_session.add(curso)
    db_session.commit()
    db_session.refresh(curso)
    
    return curso


@pytest.fixture
def grupo_test(db_session: Session):
    """Crea un grupo de prueba."""
    from src.enums.academic.grupo_enums import EstadoGrupo, JornadaGrupo
    grupo = Grupo(
        grupo_id=uuid4(),
        nombre=f"Grupo E2E {uuid4().hex[:6].upper()}",
        codigo_grupo=f"G{uuid4().hex[:6].upper()}",
        jornada=JornadaGrupo.manana,
        capacidad_maxima=30,
        capacidad_minima=10,
        cupos_disponibles=30,
        estado=EstadoGrupo.en_curso,
        permite_inscripcion=True,
    )
    db_session.add(grupo)
    db_session.commit()
    db_session.refresh(grupo)
    
    return grupo


@pytest.fixture
def clase_test(db_session: Session, grupo_test, docente_test):
    """Crea una clase de prueba."""
    codigo_acceso = f"{uuid4().hex[:4].upper()}{uuid4().hex[:4]}"
    fecha_clase = datetime.now(UTC) + timedelta(days=2)
    
    clase = Clase(
        clase_id=uuid4(),
        grupo_id=grupo_test.grupo_id,
        docente_id=docente_test.docente_id,
        titulo="Introducción a Python E2E",
        descripcion="Clase de prueba para tests E2E",
        tipo_clase=TipoClase.teorica,
        estado=EstadoClase.programada,
        fecha_inicio=fecha_clase,
        fecha_fin=fecha_clase + timedelta(hours=2),
        duracion=120,  # minutos
        duracion_estimada=120,
        codigo_acceso=codigo_acceso,
        estado_codigo=EstadoCodigoAcceso.activo,
    )
    db_session.add(clase)
    db_session.commit()
    db_session.refresh(clase)
    
    return clase


# ==================== COMPLETE FLOW FIXTURES ====================


@pytest.fixture
def flujo_completo(
    db_session: Session,
    institucion_completa,
    coordinador_test,
    programa_test,
    curso_test,
    grupo_test,
    clase_test,
    docente_test,
    estudiante_test,
):
    """Fixture con todo el flujo configurado.
    
    Proporciona:
    - Institución activa
    - Coordinador asignado
    - Programa académico
    - Curso con código de acceso
    - Grupo
    - Clase programada
    - Docente asignado
    - Estudiante registrado
    """
    return {
        "institucion": institucion_completa,
        "coordinador": coordinador_test,
        "programa": programa_test,
        "curso": curso_test,
        "grupo": grupo_test,
        "clase": clase_test,
        "docente": docente_test,
        "estudiante": estudiante_test,
    }


# ==================== PERIODO ACADEMICO FIXTURES ====================


@pytest.fixture
def periodo_academico_test(db_session: Session, institucion_completa):
    """Crea un período académico de prueba."""
    from src.models.academic.periodo_academico import PeriodoAcademico
    
    fecha_inicio = datetime.now(UTC).date()
    fecha_fin = (datetime.now(UTC) + timedelta(days=180)).date()
    
    periodo = PeriodoAcademico(
        institucion_id=institucion_completa.institucion_id,
        nombre="2024-2 E2E Test",
        codigo=f"2024-2-{uuid4().hex[:6].upper()}",
        fecha_inicio=fecha_inicio,
        fecha_fin=fecha_fin,
        estado="activo",
        activo=True,
        fecha_creacion=datetime.now(UTC),
    )
    db_session.add(periodo)
    db_session.commit()
    db_session.refresh(periodo)
    
    return periodo


# ==================== HELPER FUNCTIONS ====================


def create_bulk_estudiantes(
    db_session: Session,
    institucion_id,
    cantidad: int = 5,
):
    """Crea múltiples estudiantes para pruebas de carga."""
    from src.enums.users.usuario_enums import (
        EstadoCuentaUsuario,
        RolUsuario,
        TipoDocumentoUsuario,
    )
    from src.services.auth.password_service import PasswordService
    
    password_service = PasswordService()
    estudiantes = []
    
    for i in range(cantidad):
        usuario = Usuario(
            usuario_id=uuid4(),
            correo_institucional=f"bulk_est_{i+1}_{uuid4().hex[:6]}@test.com",
            username=None,
            nombres=f"Estudiante{i+1}",
            apellidos="Bulk Test",
            tipo_documento=TipoDocumentoUsuario.cc,
            numero_documento=f"{(uuid4().int % 10000000000) + i}",
            rol=RolUsuario.estudiante,
            password_hash=password_service.hash_password("Estudiante123!"),
            estado_cuenta=EstadoCuentaUsuario.activo,
            email_verified=True,
        )
        db_session.add(usuario)
        db_session.flush()
        
        # Estudiante: estudiante_id, programa_id, fecha_ingreso, etapa_formativa, etc
        from datetime import date
        from src.enums.users.estudiante_enums import EtapaFormativaEstudiante
        estudiante = Estudiante(
            estudiante_id=usuario.usuario_id,
            programa_id=None,
            fecha_ingreso=date(2024, 1, 15),
            etapa_formativa=EtapaFormativaEstudiante.i,
            creditos_aprobados=0,
            promedio_acumulado=None,
        )
        db_session.add(estudiante)
        estudiantes.append(estudiante)
    
    db_session.commit()
    
    for estudiante in estudiantes:
        db_session.refresh(estudiante)
    
    return estudiantes


@pytest.fixture
def bulk_estudiantes(db_session: Session, institucion_completa):
    """Fixture que crea 10 estudiantes de prueba."""
    return create_bulk_estudiantes(
        db_session,
        institucion_completa.institucion_id,
        cantidad=10,
    )
