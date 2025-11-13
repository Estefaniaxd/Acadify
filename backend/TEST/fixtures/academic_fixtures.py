"""
Fixtures y factories para modelos académicos: Curso, Programa, Grupo
"""
import pytest
from datetime import date, time, timedelta
from typing import Dict, Any, List
from decimal import Decimal
from faker import Faker
import uuid
import random

from sqlalchemy.orm import Session
from src.models.academic.curso import Curso
from src.models.academic.programa import Programa
from src.models.academic.grupo import Grupo
from src.models.academic.institucion import Institucion
from src.models.users.usuario import Usuario
from src.enums.academic.curso_enums import (
    ModalidadCurso,
    NivelDificultad,
    TipoCurso,
    CategoriaCurso,
    EstadoCurso,
    IdiomaCurso
)
from src.enums.academic.programa_enums import (
    EstadoPrograma, DuracionPrograma, NivelPrograma, TipoPrograma
)
from src.enums.academic.grupo_enums import (
    EstadoGrupo,
    TipoGrupo,
    JornadaGrupo,
    ModalidadAsistencia,
    FormatoEvaluacion
)

fake = Faker(['es_ES'])
Faker.seed(12345)


# ==================== CURSO FIXTURES ====================

def crear_curso_base_data(institucion_id=None, **kwargs):
    """Genera datos base para crear un curso"""
    from uuid import uuid4
    import random
    from datetime import date, timedelta
    
    data = {
        # IDs
        "curso_id": uuid4(),
        "institucion_id": institucion_id or uuid4(),
        
        # Información básica
        "nombre": fake.catch_phrase(),
        "descripcion": fake.text(max_nb_chars=200),
        "objetivos": fake.text(max_nb_chars=150),
        "codigo_curso": f"{fake.lexify(text='???').upper()}{fake.numerify(text='###')}",
        "codigo_acceso": fake.lexify(text='??????').upper(),
        
        # Créditos y horas
        "creditos": random.randint(2, 6),
        "horas_academicas": random.randint(32, 64),
        "horas_teoricas": random.randint(16, 32),
        "horas_practicas": random.randint(8, 24),
        "horas_laboratorio": random.randint(0, 16),
        "horas_autonomas": random.randint(16, 40),
        
        # Clasificación
        "modalidad": random.choice(list(ModalidadCurso)).value,
        "nivel_dificultad": random.choice(list(NivelDificultad)).value,
        "tipo_curso": random.choice(list(TipoCurso)).value,
        "categoria_curso": random.choice(list(CategoriaCurso)).value,
        "estado": EstadoCurso.borrador.value,
        "idioma": IdiomaCurso.espanol.value,
        
        # Fechas
        "fecha_inicio": date.today() + timedelta(days=60),
        "fecha_fin": date.today() + timedelta(days=180),
        "fecha_limite_inscripcion": date.today() + timedelta(days=30),
        "fecha_inicio_retiro": date.today() + timedelta(days=90),
        "fecha_limite_retiro": date.today() + timedelta(days=150),
        
        # Cupos e inscripción
        "activo": True,
        "permite_inscripcion": True,
        "maximo_estudiantes": random.randint(35, 50),
        "minimo_estudiantes": random.randint(10, 15),
        "cupos_disponibles": random.randint(20, 40),
        "permite_lista_espera": True,
        "maximo_lista_espera": random.randint(5, 10),
        
        # Prerequisitos
        "prerequisitos_ids": None,
        "correquisitos_ids": None,
        "requiere_nivelacion": False,
        "creditos_minimos_requeridos": 0,
        "promedio_minimo_requerido": None,
        
        # Costos
        "tiene_costo": True,
        "costo_matricula": float(random.randint(100000, 500000)),
        "costo_mensual": float(random.randint(50000, 200000)),
        "costo_total": float(random.randint(300000, 1000000)),
        "permite_becas": True,
        "porcentaje_descuento": None,
        
        # Evaluación y calificación
        "calificacion_minima_aprobacion": 3.0,
        "porcentaje_asistencia_minimo": 80.0,
        "permite_recuperacion": True,
        "permite_habilitacion": True,
        "numero_maximo_faltas": random.randint(3, 5),
        
        # Permisos de material
        "permite_material_estudiantes": False,
        "requiere_aprobacion_material": True,
    }
    data.update(kwargs)
    return data


@pytest.fixture
def curso_base(db_session: Session, institucion_test: Institucion) -> Curso:
    """Curso básico de prueba"""
    data = crear_curso_base_data(institucion_id=institucion_test.institucion_id)
    curso = Curso(**data)
    db_session.add(curso)
    db_session.commit()
    db_session.refresh(curso)
    return curso


@pytest.fixture
def curso_con_prerequisitos(db_session: Session, institucion_test: Institucion, curso_base: Curso) -> Curso:
    """Curso con prerequisitos definidos"""
    data = crear_curso_base_data(
        institucion_id=institucion_test.institucion_id,
        nombre="Curso Avanzado",
        prerequisitos_ids=[str(curso_base.curso_id)],
        nivel_dificultad=NivelDificultad.avanzado.value
    )
    curso = Curso(**data)
    db_session.add(curso)
    db_session.commit()
    db_session.refresh(curso)
    return curso


@pytest.fixture
def curso_inscripciones_abiertas(db_session: Session, institucion_test: Institucion) -> Curso:
    """Curso con inscripciones abiertas"""
    data = crear_curso_base_data(
        institucion_id=institucion_test.institucion_id,
        estado=EstadoCurso.inscripciones_abiertas.value,
        fecha_limite_inscripcion=date.today() + timedelta(days=15)
    )
    curso = Curso(**data)
    db_session.add(curso)
    db_session.commit()
    db_session.refresh(curso)
    return curso


@pytest.fixture
def curso_sin_cupos(db_session: Session, institucion_test: Institucion) -> Curso:
    """Curso sin cupos disponibles"""
    data = crear_curso_base_data(
        institucion_id=institucion_test.institucion_id,
        estado=EstadoCurso.inscripciones_abiertas.value,
        cupos_disponibles=0,
        maximo_estudiantes=30
    )
    curso = Curso(**data)
    db_session.add(curso)
    db_session.commit()
    db_session.refresh(curso)
    return curso


@pytest.fixture
def lista_cursos(db_session: Session, institucion_test: Institucion) -> List[Curso]:
    """Lista de 5 cursos variados"""
    cursos = []
    for i in range(5):
        data = crear_curso_base_data(
            institucion_id=institucion_test.institucion_id,
            nombre=f"Curso {i+1}: {fake.catch_phrase()}",
            codigo_curso=f"CUR-{1000+i}"
        )
        curso = Curso(**data)
        db_session.add(curso)
        cursos.append(curso)
    
    db_session.commit()
    for curso in cursos:
        db_session.refresh(curso)
    return cursos


# ==================== PROGRAMA FIXTURES ====================

def crear_programa_base_data(**kwargs) -> Dict[str, Any]:
    """Genera datos base para crear un programa"""
    # Generar créditos coherentes
    creditos_totales = random.randint(120, 180)
    creditos_obligatorios = int(creditos_totales * 0.6)  # 60%
    creditos_electivos = int(creditos_totales * 0.25)  # 25%
    creditos_libres = creditos_totales - creditos_obligatorios - creditos_electivos  # Resto
    
    data = {
        "programa_id": uuid.uuid4(),
        "nombre": f"Programa en {fake.job()}",
        "codigo": f"PROG-{fake.random_int(100, 999)}",
        "nivel": random.choice(list(NivelPrograma)).value,
        "tipo": random.choice(list(TipoPrograma)).value,
        "descripcion": fake.text(max_nb_chars=300),
        
        # Estado y duración
        "estado": EstadoPrograma.activo.value,
        "duracion_tipo": random.choice(list(DuracionPrograma)).value,
        "duracion_periodos": random.randint(8, 12),
        "duracion_meses": random.randint(48, 72),
        
        # Créditos coherentes
        "creditos_totales": creditos_totales,
        "creditos_obligatorios": creditos_obligatorios,
        "creditos_electivos": creditos_electivos,
        "creditos_libres": creditos_libres,
        
        # Requisitos de ingreso
        "titulo_bachiller_requerido": True,
        "puntaje_minimo_admision": random.randint(250, 350),
        "requiere_examen_admision": True,
        "requiere_entrevista": False,
        "edad_minima_ingreso": 16,
        
        # Requisitos de graduación (coherente con créditos totales)
        "creditos_minimos_graduacion": creditos_totales,  # Igual a totales
        "promedio_minimo_graduacion": 3.5,
        "requiere_trabajo_grado": True,
        "requiere_practica_profesional": True,
        "horas_practica_requeridas": random.randint(480, 720),
        
        # Costos
        "tiene_costo": True,
        "costo_matricula": float(random.randint(500000, 2000000)),
        "costo_por_periodo": float(random.randint(2000000, 5000000)),
        "costo_por_credito": float(random.randint(150000, 300000)),
        "costo_total_estimado": float(random.randint(10000000, 50000000)),
        "ofrece_becas": True,
        
        # Acreditación
        "esta_acreditado": True,
        "fecha_acreditacion": date.today() - timedelta(days=365),
        "vigencia_acreditacion_hasta": date.today() + timedelta(days=365*3),
        "registro_calificado": f"RC-{fake.random_int(10000, 99999)}",
        
        # Capacidad
        "cupos_por_periodo": random.randint(40, 80),
        "maximo_estudiantes_activos": random.randint(200, 500),
        "permite_inscripcion": True,
        
        # Configuración
        "activo": True,
        "acepta_transferencias": True,
        "acepta_homologaciones": True,
        "permite_doble_titulacion": False,
        
        # Metadata
        "perfil_egresado": fake.text(max_nb_chars=300),
        "campo_ocupacional": fake.text(max_nb_chars=200)
    }
    data.update(kwargs)
    return data


@pytest.fixture
def programa_base(db_session: Session, institucion_test: Institucion) -> Programa:
    """Programa básico de prueba"""
    data = crear_programa_base_data(institucion_id=institucion_test.institucion_id)
    programa = Programa(**data)
    db_session.add(programa)
    db_session.commit()
    db_session.refresh(programa)
    return programa


@pytest.fixture
def programa_pregrado(db_session: Session, institucion_test: Institucion) -> Programa:
    """Programa de pregrado"""
    data = crear_programa_base_data(
        institucion_id=institucion_test.institucion_id,
        nombre="Ingeniería de Sistemas",
        nivel=NivelPrograma.pregrado.value,
        duracion_periodos=10,
        creditos_totales=160
    )
    programa = Programa(**data)
    db_session.add(programa)
    db_session.commit()
    db_session.refresh(programa)
    return programa


@pytest.fixture
def programa_posgrado(db_session: Session, institucion_test: Institucion) -> Programa:
    """Programa de posgrado"""
    data = crear_programa_base_data(
        institucion_id=institucion_test.institucion_id,
        nombre="Maestría en Ciencias de Datos",
        nivel=NivelPrograma.maestria.value,
        duracion_periodos=4,
        creditos_totales=48,
        requiere_trabajo_grado=True
    )
    programa = Programa(**data)
    db_session.add(programa)
    db_session.commit()
    db_session.refresh(programa)
    return programa


@pytest.fixture
def programa_gratuito(db_session: Session, institucion_test: Institucion) -> Programa:
    """Programa gratuito"""
    data = crear_programa_base_data(
        institucion_id=institucion_test.institucion_id,
        nombre="Programa Gratuito de Prueba",
        tiene_costo=False,
        costo_matricula=0,
        costo_por_periodo=0,
        costo_por_credito=0,
        costo_total_estimado=0
    )
    programa = Programa(**data)
    db_session.add(programa)
    db_session.commit()
    db_session.refresh(programa)
    return programa


@pytest.fixture
def programa_acreditado(db_session: Session, institucion_test: Institucion) -> Programa:
    """Programa acreditado con vigencia"""
    data = crear_programa_base_data(
        institucion_id=institucion_test.institucion_id,
        nombre="Programa Acreditado",
        esta_acreditado=True,
        fecha_acreditacion=date.today() - timedelta(days=365),
        vigencia_acreditacion_hasta=date.today() + timedelta(days=365*3)
    )
    programa = Programa(**data)
    db_session.add(programa)
    db_session.commit()
    db_session.refresh(programa)
    return programa


@pytest.fixture
def lista_programas(db_session: Session, institucion_test: Institucion) -> List[Programa]:
    """Lista de 3 programas variados"""
    programas = []
    for i in range(3):
        data = crear_programa_base_data(
            institucion_id=institucion_test.institucion_id,
            nombre=f"Programa {i+1}: {fake.job()}",
            codigo=f"PROG-{2000+i}"
        )
        programa = Programa(**data)
        db_session.add(programa)
        programas.append(programa)
    
    db_session.commit()
    for programa in programas:
        db_session.refresh(programa)
    return programas


# ==================== GRUPO FIXTURES ====================

def crear_grupo_base_data(**kwargs) -> Dict[str, Any]:
    """Genera datos base para crear un grupo"""
    data = {
        "grupo_id": uuid.uuid4(),
        "codigo_grupo": f"G-{fake.random_int(100, 999)}",
        "nombre": f"Grupo {fake.word().capitalize()}",
        "seccion": random.choice(['A', 'B', 'C', 'D']),
        "nivel_academico": random.randint(1, 10),
        "descripcion": fake.sentence(nb_words=15),
        
        # Estado y tipo (ENUMs)
        "estado": random.choice(list(EstadoGrupo)).value,
        "tipo_grupo": random.choice(list(TipoGrupo)).value,
        "jornada": random.choice(list(JornadaGrupo)).value,
        "modalidad_asistencia": random.choice(list(ModalidadAsistencia)).value,
        "formato_evaluacion": random.choice(list(FormatoEvaluacion)).value,
        
        # Capacidad
        "capacidad_minima": random.randint(10, 15),
        "capacidad_maxima": random.randint(30, 40),
        "cupos_disponibles": random.randint(30, 40),
        "permite_inscripcion": True,
        "permite_lista_espera": True,
        "maximo_lista_espera": random.randint(5, 10),
        
        # Fechas
        "fecha_inicio": date.today() + timedelta(days=30),
        "fecha_fin": date.today() + timedelta(days=150),
        "fecha_inicio_inscripciones": date.today() + timedelta(days=10),
        "fecha_fin_inscripciones": date.today() + timedelta(days=28),
        
        # Horarios
        "dias_semana": ["lunes", "miercoles", "viernes"],
        "hora_inicio": time(8, 0),
        "hora_fin": time(10, 0),
        
        # Espacios
        "salon": f"Salón {fake.random_int(100, 999)}",
        "edificio": fake.random_element(["A", "B", "C", "Principal"]),
        "ubicacion_virtual": f"https://meet.example.com/{fake.uuid4()}",
        
        # Académico
        "creditos": random.randint(2, 5),
        "horas_semanales": random.randint(4, 12),
        "porcentaje_asistencia_minimo": Decimal("80.0"),
        "calificacion_minima_aprobacion": Decimal("3.0"),
        "permite_recuperacion": True,
        "numero_maximo_faltas": random.randint(3, 6),
        
        # Costos
        "tiene_costo_adicional": False,
        "costo_adicional": None,
        
        # Configuración
        "requiere_aprobacion_inscripcion": False,
        "es_visible": True,
        "permite_autoregistro": False,
        "codigo_acceso": None,
        "permite_chat": True,
        "permite_foro": True,
        "permite_comentarios": True,
        "permite_material_estudiantes": False,
        
        # Metadata
        "objetivos": fake.sentence(nb_words=20),
        "notas_internas": None,
        "recursos_adicionales": None,
        "tags": None,
        "imagen_url": None,
        
        # Estados
        "activo": True
    }
    data.update(kwargs)
    return data


@pytest.fixture
def grupo_base(
    db_session: Session,
    programa_base,
    periodo_base
) -> Grupo:
    """Grupo básico de prueba"""
    data = crear_grupo_base_data(
        programa_id=programa_base.programa_id,
        periodo_academico_id=periodo_base.id  # Ahora funciona correctamente (Integer)
    )
    grupo = Grupo(**data)
    db_session.add(grupo)
    db_session.commit()
    db_session.refresh(grupo)
    return grupo


@pytest.fixture
def grupo_inscripciones_abiertas(
    db_session: Session,
    programa_base,
    periodo_base
) -> Grupo:
    """Grupo con inscripciones abiertas"""
    data = crear_grupo_base_data(
        programa_id=programa_base.programa_id,
        periodo_academico_id=periodo_base.id,  # Ahora funciona correctamente (Integer)
        estado=EstadoGrupo.inscripciones_abiertas.value,
        permite_inscripcion=True,
        cupos_disponibles=25
    )
    grupo = Grupo(**data)
    db_session.add(grupo)
    db_session.commit()
    db_session.refresh(grupo)
    return grupo


@pytest.fixture
def grupo_lleno(
    db_session: Session,
    programa_base,
    periodo_base
) -> Grupo:
    """Grupo sin cupos disponibles"""
    capacidad_max = 30
    data = crear_grupo_base_data(
        programa_id=programa_base.programa_id,
        periodo_academico_id=periodo_base.id,  # Ahora funciona correctamente (Integer)
        capacidad_maxima=capacidad_max,
        cupos_disponibles=0
    )
    grupo = Grupo(**data)
    db_session.add(grupo)
    db_session.commit()
    db_session.refresh(grupo)
    return grupo


@pytest.fixture
def lista_grupos(
    db_session: Session,
    programa_base,
    periodo_base
) -> List[Grupo]:
    """Lista de múltiples grupos de prueba"""
    grupos = []
    for i, seccion in enumerate(['A', 'B', 'C']):
        data = crear_grupo_base_data(
            programa_id=programa_base.programa_id,
            periodo_academico_id=periodo_base.id,  # Ahora funciona correctamente (Integer)
            seccion=seccion,
            codigo_grupo=f"G-{100+i}"
        )
        grupo = Grupo(**data)
        db_session.add(grupo)
        grupos.append(grupo)
    
    db_session.commit()
    for grupo in grupos:
        db_session.refresh(grupo)
    return grupos


@pytest.fixture
def grupo_inscripciones_abiertas(
    db_session: Session,
    programa_base,
    periodo_base
) -> Grupo:
    """Grupo con inscripciones abiertas"""
    data = crear_grupo_base_data(
        programa_id=programa_base.programa_id,
        periodo_academico_id=periodo_base.id,  # ID INTEGER
        estado=EstadoGrupo.inscripciones_abiertas.value,
        permite_inscripcion=True,
        cupos_disponibles=25
    )
    grupo = Grupo(**data)
    db_session.add(grupo)
    db_session.commit()
    db_session.refresh(grupo)
    return grupo


@pytest.fixture
def grupo_lleno(
    db_session: Session,
    programa_base,
    periodo_base
) -> Grupo:
    """Grupo sin cupos disponibles"""
    capacidad_max = 30
    data = crear_grupo_base_data(
        programa_id=programa_base.programa_id,
        periodo_academico_id=periodo_base.id,  # ID INTEGER
        capacidad_maxima=capacidad_max,
        cupos_disponibles=0
    )
    grupo = Grupo(**data)
    db_session.add(grupo)
    db_session.commit()
    db_session.refresh(grupo)
    return grupo


@pytest.fixture
def lista_grupos(
    db_session: Session,
    programa_base,
    periodo_base
) -> List[Grupo]:
    """Lista de 3 grupos variados"""
    grupos = []
    for i, seccion in enumerate(['A', 'B', 'C']):
        data = crear_grupo_base_data(
            programa_id=programa_base.programa_id,
            periodo_academico_id=periodo_base.id,  # ID INTEGER
            seccion=seccion,
            codigo_grupo=f"G-{100+i}"
        )
        grupo = Grupo(**data)
        db_session.add(grupo)
        grupos.append(grupo)
    
    db_session.commit()
    for grupo in grupos:
        db_session.refresh(grupo)
    return grupos
