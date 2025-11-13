"""
Fixtures y factories para sistema de períodos académicos e inscripciones
"""
import pytest
from datetime import date, datetime, timedelta
from typing import Dict, Any, List
from faker import Faker
import uuid
import random

from sqlalchemy.orm import Session
from src.models.academic.periodo_academico import PeriodoAcademico
from src.models.academic.inscripcion import Inscripcion
from src.models.academic.programa import Programa
from src.models.academic.grupo import Grupo
from src.models.users.usuario import Usuario
from src.models.academic.institucion import Institucion

fake = Faker(['es_ES'])
Faker.seed(12345)


# ==================== PERIODO ACADÉMICO FIXTURES ====================

def crear_periodo_base_data(**kwargs) -> Dict[str, Any]:
    """Genera datos base para crear un período académico"""
    fecha_inicio = date.today() + timedelta(days=random.randint(1, 30))
    fecha_fin = fecha_inicio + timedelta(days=120)
    anio_actual = fecha_inicio.year
    
    from decimal import Decimal
    import uuid as uuid_lib
    
    # Generar código único
    codigo_unico = f"PER-{anio_actual}{random.randint(1, 2)}-{uuid_lib.uuid4().hex[:6]}"
    
    data = {
        # ID se autogenera, no lo incluimos
        "nombre": f"Período {anio_actual}-{random.randint(1, 2)}",
        "codigo": codigo_unico,
        "descripcion": fake.text(max_nb_chars=200),
        
        # Tipo y estado
        "tipo": random.choice(['semestre', 'trimestre', 'cuatrimestre', 'anual']),
        "estado": "programado",
        
        # Temporalidad
        "anio": anio_actual,
        "numero_periodo": random.randint(1, 2),
        "nivel_aplica": None,
        
        # Fechas principales
        "fecha_inicio": fecha_inicio,
        "fecha_fin": fecha_fin,
        
        # Fechas de inscripciones
        "fecha_inicio_preinscripciones": fecha_inicio - timedelta(days=40),
        "fecha_fin_preinscripciones": fecha_inicio - timedelta(days=31),
        "fecha_inicio_inscripciones": fecha_inicio - timedelta(days=30),
        "fecha_fin_inscripciones": fecha_inicio - timedelta(days=7),
        
        # Fechas de ajustes (agregar/retirar cursos)
        "fecha_inicio_ajustes": fecha_inicio,
        "fecha_fin_ajustes": fecha_inicio + timedelta(days=7),
        
        # Fechas de clases
        "fecha_inicio_clases": fecha_inicio,
        "fecha_fin_clases": fecha_fin - timedelta(days=14),
        
        # Fechas de retiro
        "fecha_limite_retiro": fecha_fin - timedelta(days=30),
        "fecha_limite_retiro_con_reembolso": fecha_inicio + timedelta(days=14),
        
        # Fechas de exámenes
        "fecha_inicio_examenes": fecha_fin - timedelta(days=14),
        "fecha_fin_examenes": fecha_fin - timedelta(days=7),
        
        # Fechas de notas
        "fecha_cierre_notas": fecha_fin - timedelta(days=3),
        "fecha_publicacion_notas": fecha_fin,
        
        # Permisos
        "permite_inscripciones": True,
        "permite_ajustes": True,
        "permite_retiros": True,
        
        # Visibilidad
        "visible_estudiantes": True,
        "visible_profesores": True,
        "visible_publico": False,
        
        # Límites académicos
        "creditos_minimos": 12,
        "creditos_maximos": 21,
        "cursos_minimos": 3,
        "cursos_maximos": 7,
        
        # Costos
        "costo_matricula": Decimal('500000.00'),
        "costo_por_credito": Decimal('50000.00'),
        "moneda": "COP",
        
        # Configuración adicional
        "dias_festivos": None,
        "vacaciones": None,
        "configuracion": None,
        "notas": None,
        
        # Estado
        "activo": True,
        "es_actual": False,
    }
    data.update(kwargs)
    return data


@pytest.fixture
def periodo_base(db_session: Session, institucion_test: Institucion, usuario_admin: Usuario) -> PeriodoAcademico:
    """Período académico básico de prueba"""
    data = crear_periodo_base_data(
        institucion_id=institucion_test.institucion_id,
        creado_por_id=usuario_admin.usuario_id
    )
    periodo = PeriodoAcademico(**data)
    db_session.add(periodo)
    db_session.commit()
    db_session.refresh(periodo)
    return periodo


@pytest.fixture
def periodo_actual(db_session: Session, institucion_test: Institucion, usuario_admin: Usuario) -> PeriodoAcademico:
    """Período académico actual activo"""
    data = crear_periodo_base_data(
        institucion_id=institucion_test.institucion_id,
        creado_por_id=usuario_admin.usuario_id,
        nombre="Período Actual 2025-1",
        codigo="PER-20251",
        fecha_inicio=date.today() - timedelta(days=30),
        fecha_fin=date.today() + timedelta(days=90),
        estado="activo",
        es_periodo_actual=True,
        permite_inscripciones=True,
        permite_retiros=False
    )
    periodo = PeriodoAcademico(**data)
    db_session.add(periodo)
    db_session.commit()
    db_session.refresh(periodo)
    return periodo


@pytest.fixture
def periodo_inscripciones_abiertas(
    db_session: Session,
    institucion_test: Institucion,
    usuario_admin: Usuario
) -> PeriodoAcademico:
    """Período con inscripciones abiertas"""
    hoy = date.today()
    data = crear_periodo_base_data(
        institucion_id=institucion_test.institucion_id,
        creado_por_id=usuario_admin.usuario_id,
        nombre="Período Inscripciones 2025-2",
        codigo="PER-20252",
        fecha_inicio=hoy + timedelta(days=30),
        fecha_fin=hoy + timedelta(days=150),
        fecha_inicio_inscripciones=hoy - timedelta(days=7),
        fecha_fin_inscripciones=hoy + timedelta(days=21),
        estado="inscripciones_abiertas",
        permite_inscripciones=True
    )
    periodo = PeriodoAcademico(**data)
    db_session.add(periodo)
    db_session.commit()
    db_session.refresh(periodo)
    return periodo


@pytest.fixture
def periodo_retiro_abierto(
    db_session: Session,
    institucion_test: Institucion,
    usuario_admin: Usuario
) -> PeriodoAcademico:
    """Período con retiro de materias abierto"""
    hoy = date.today()
    data = crear_periodo_base_data(
        institucion_id=institucion_test.institucion_id,
        creado_por_id=usuario_admin.usuario_id,
        fecha_inicio=hoy - timedelta(days=45),
        fecha_fin=hoy + timedelta(days=75),
        fecha_inicio_retiro=hoy - timedelta(days=10),
        fecha_fin_retiro=hoy + timedelta(days=20),
        estado="activo",
        permite_retiros=True
    )
    periodo = PeriodoAcademico(**data)
    db_session.add(periodo)
    db_session.commit()
    db_session.refresh(periodo)
    return periodo


@pytest.fixture
def periodo_finalizado(
    db_session: Session,
    institucion_test: Institucion,
    usuario_admin: Usuario
) -> PeriodoAcademico:
    """Período académico finalizado"""
    hoy = date.today()
    data = crear_periodo_base_data(
        institucion_id=institucion_test.institucion_id,
        creado_por_id=usuario_admin.usuario_id,
        nombre="Período Finalizado 2024-2",
        codigo="PER-20242",
        fecha_inicio=hoy - timedelta(days=180),
        fecha_fin=hoy - timedelta(days=30),
        estado="finalizado",
        permite_inscripciones=False,
        permite_retiros=False
    )
    periodo = PeriodoAcademico(**data)
    db_session.add(periodo)
    db_session.commit()
    db_session.refresh(periodo)
    return periodo


@pytest.fixture
def lista_periodos(
    db_session: Session,
    institucion_test: Institucion,
    usuario_admin: Usuario
) -> List[PeriodoAcademico]:
    """Lista de 4 períodos con diferentes estados"""
    periodos = []
    estados = ['finalizado', 'activo', 'programado', 'inscripciones_abiertas']
    
    for i, estado in enumerate(estados):
        offset_dias = (i - 1) * 120
        fecha_inicio = date.today() + timedelta(days=offset_dias)
        
        data = crear_periodo_base_data(
            institucion_id=institucion_test.institucion_id,
            creado_por_id=usuario_admin.usuario_id,
            nombre=f"Período 2025-{i+1}",
            codigo=f"PER-2025{i+1}",
            fecha_inicio=fecha_inicio,
            estado=estado,
            es_periodo_actual=(estado == 'activo')
        )
        periodo = PeriodoAcademico(**data)
        db_session.add(periodo)
        periodos.append(periodo)
    
    db_session.commit()
    for periodo in periodos:
        db_session.refresh(periodo)
    return periodos


# ==================== INSCRIPCIÓN FIXTURES ====================

def crear_inscripcion_base_data(**kwargs) -> Dict[str, Any]:
    """Genera datos base para crear una inscripción según modelo real"""
    from decimal import Decimal
    
    # Generar código único de inscripción
    codigo_unico = f"INS-{datetime.now().strftime('%Y%m')}-{fake.random_int(10000, 99999)}"
    
    data = {
        # NO incluir id (se autogenera)
        "codigo_inscripcion": codigo_unico,
        
        # Tipo y Estado
        "tipo_inscripcion": "regular",  # TipoInscripcion enum
        "estado": "pre_inscrita",  # EstadoInscripcion enum
        
        # Fechas del Proceso
        "fecha_solicitud": datetime.now(),
        "fecha_pre_inscripcion": None,
        "fecha_inscripcion": None,
        "fecha_confirmacion": None,
        "fecha_inicio_clases": None,
        "fecha_finalizacion": None,
        "fecha_retiro": None,
        "fecha_cancelacion": None,
        "fecha_limite_pago": date.today() + timedelta(days=15),
        "fecha_limite_documentos": date.today() + timedelta(days=10),
        "fecha_limite_confirmacion": date.today() + timedelta(days=20),
        
        # Información Académica
        "creditos_inscritos": 0,
        "horas_semanales": 0,
        "numero_lista": None,
        "prioridad": 0,
        "tiene_convalidacion": False,
        "creditos_convalidados": 0,
        "tiene_homologacion": False,
        "cumple_prerequisitos": False,
        "prerequisitos_verificados": False,
        "fecha_verificacion_prerequisitos": None,
        
        # Información Financiera
        "costo_total": Decimal('0.00'),
        "costo_matricula": Decimal('0.00'),
        "costo_curso": Decimal('0.00'),
        "otros_costos": Decimal('0.00'),
        "descuentos": Decimal('0.00'),
        "monto_final": Decimal('0.00'),
        "forma_pago": None,
        "esta_pagado": False,
        "fecha_pago": None,
        "referencia_pago": None,
        "tiene_beca": False,
        "porcentaje_beca": Decimal('0.00'),
        "tipo_beca": None,
        "tiene_credito": False,
        "entidad_credito": None,
        
        # Documentación
        "documentos_completos": False,
        "documentos_requeridos": None,
        "documentos_entregados": None,
        "documentos_pendientes": None,
        "fecha_entrega_documentos": None,
        
        # Aprobaciones
        "requiere_aprobacion": False,
        "esta_aprobada": False,
        "aprobada_por_id": None,
        "fecha_aprobacion": None,
        "comentarios_aprobacion": None,
        
        # Rechazo y Cancelación
        "fue_rechazada": False,
        "motivo_rechazo": None,
        "descripcion_rechazo": None,
        "rechazada_por_id": None,
        "fecha_rechazo": None,
        "fue_retirada": False,
        "motivo_retiro": None,
        "descripcion_retiro": None,
        "fue_retiro_voluntario": None,
        "permite_reingreso": True,
        
        # Calificaciones
        "calificacion_final": None,
        "calificacion_literal": None,
        "aprobo_curso": None,
        "porcentaje_asistencia": None,
        "cumple_asistencia_minima": None,
        "genera_certificado": True,
        "certificado_emitido": False,
        "fecha_emision_certificado": None,
        "codigo_certificado": None,
        
        # Lista de Espera
        "en_lista_espera": False,
        "posicion_lista_espera": None,
        "fecha_entrada_lista_espera": None,
        "fecha_salida_lista_espera": None,
        "notificado_cupo_disponible": False,
        "fecha_notificacion_cupo": None,
        
        # Configuración
        "puede_cancelar": True,
        "puede_retirar": True,
        "permite_ajustes": True,
        "requiere_atencion": False,
        "motivo_atencion": None,
        "tiene_observaciones": False,
        "observaciones": None,
        
        # Metadata
        "metadata_adicional": None,
        "notas_internas": None,
        "historial_cambios": None,
        
        # Auditoría
        "activo": True,
    }
    data.update(kwargs)
    return data


@pytest.fixture
def inscripcion_base(
    db_session: Session,
    usuario_estudiante: Usuario,
    grupo_base: Grupo,
    programa_base: Programa,
    periodo_base: PeriodoAcademico,
    usuario_admin: Usuario
) -> Inscripcion:
    """Inscripción básica en estado pre_inscrita"""
    from decimal import Decimal
    data = crear_inscripcion_base_data(
        estudiante_id=usuario_estudiante.usuario_id,
        grupo_id=grupo_base.grupo_id,
        programa_id=programa_base.programa_id,
        periodo_academico_id=periodo_base.id,  # Integer
        creado_por_id=usuario_admin.usuario_id,
        estado="pre_inscrita"
    )
    inscripcion = Inscripcion(**data)
    db_session.add(inscripcion)
    db_session.commit()
    db_session.refresh(inscripcion)
    return inscripcion


@pytest.fixture
def inscripcion_pendiente_pago(
    db_session: Session,
    usuario_estudiante: Usuario,
    grupo_base: Grupo,
    programa_base: Programa,
    periodo_base: PeriodoAcademico,
    usuario_admin: Usuario
) -> Inscripcion:
    """Inscripción pendiente de pago"""
    from decimal import Decimal
    data = crear_inscripcion_base_data(
        estudiante_id=usuario_estudiante.usuario_id,
        grupo_id=grupo_base.grupo_id,
        programa_id=programa_base.programa_id,
        periodo_academico_id=periodo_base.id,  # Integer
        creado_por_id=usuario_admin.usuario_id,
        estado="pendiente_pago",
        costo_total=Decimal('500000.00'),
        monto_final=Decimal('500000.00'),
        esta_pagado=False
    )
    inscripcion = Inscripcion(**data)
    db_session.add(inscripcion)
    db_session.commit()
    db_session.refresh(inscripcion)
    return inscripcion


@pytest.fixture
def inscripcion_confirmada(
    db_session: Session,
    usuario_estudiante: Usuario,
    grupo_base: Grupo,
    programa_base: Programa,
    periodo_base: PeriodoAcademico,
    usuario_admin: Usuario
) -> Inscripcion:
    """Inscripción confirmada y pagada"""
    from decimal import Decimal
    data = crear_inscripcion_base_data(
        estudiante_id=usuario_estudiante.usuario_id,
        grupo_id=grupo_base.grupo_id,
        programa_id=programa_base.programa_id,
        periodo_academico_id=periodo_base.id,  # Integer
        creado_por_id=usuario_admin.usuario_id,
        estado="confirmada",
        esta_pagado=True,
        fecha_pago=datetime.now(),
        fecha_confirmacion=datetime.now(),
        documentos_completos=True
    )
    inscripcion = Inscripcion(**data)
    db_session.add(inscripcion)
    db_session.commit()
    db_session.refresh(inscripcion)
    return inscripcion


@pytest.fixture
def inscripcion_activa(
    db_session: Session,
    usuario_estudiante: Usuario,
    grupo_inscripciones_abiertas: Grupo,
    programa_base: Programa,
    periodo_actual: PeriodoAcademico,
    usuario_admin: Usuario
) -> Inscripcion:
    """Inscripción activa y confirmada"""
    data = crear_inscripcion_base_data(
        estudiante_id=usuario_estudiante.usuario_id,
        grupo_id=grupo_inscripciones_abiertas.grupo_id,
        programa_id=programa_base.programa_id,
        periodo_academico_id=periodo_actual.periodo_academico_id,
        creado_por_id=usuario_admin.usuario_id,
        estado="activa",
        fecha_aprobacion=datetime.now() - timedelta(days=10),
        aprobada_por_id=usuario_admin.usuario_id,
        estado_pago="pagado",
        fecha_pago=datetime.now() - timedelta(days=5)
    )
    inscripcion = Inscripcion(**data)
    db_session.add(inscripcion)
    db_session.commit()
    db_session.refresh(inscripcion)
    return inscripcion


@pytest.fixture
def inscripcion_rechazada(
    db_session: Session,
    usuario_estudiante: Usuario,
    grupo_inscripciones_abiertas: Grupo,
    programa_base: Programa,
    periodo_inscripciones_abiertas: PeriodoAcademico,
    usuario_admin: Usuario
) -> Inscripcion:
    """Inscripción rechazada"""
    data = crear_inscripcion_base_data(
        estudiante_id=usuario_estudiante.usuario_id,
        grupo_id=grupo_inscripciones_abiertas.grupo_id,
        programa_id=programa_base.programa_id,
        periodo_academico_id=periodo_inscripciones_abiertas.periodo_academico_id,
        creado_por_id=usuario_admin.usuario_id,
        estado="rechazada",
        fecha_rechazo=datetime.now() - timedelta(days=2),
        rechazada_por_id=usuario_admin.usuario_id,
        motivo_rechazo="No cumple prerequisitos"
    )
    inscripcion = Inscripcion(**data)
    db_session.add(inscripcion)
    db_session.commit()
    db_session.refresh(inscripcion)
    return inscripcion


@pytest.fixture
def lista_inscripciones_estudiante(
    db_session: Session,
    usuario_estudiante: Usuario,
    lista_grupos: List[Grupo],
    programa_base: Programa,
    periodo_actual: PeriodoAcademico,
    usuario_admin: Usuario
) -> List[Inscripcion]:
    """Lista de 3 inscripciones de un estudiante"""
    inscripciones = []
    estados = ['pendiente', 'aprobada', 'activa']
    
    for i, (grupo, estado) in enumerate(zip(lista_grupos[:3], estados)):
        data = crear_inscripcion_base_data(
            estudiante_id=usuario_estudiante.usuario_id,
            grupo_id=grupo.grupo_id,
            programa_id=programa_base.programa_id,
            periodo_academico_id=periodo_actual.periodo_academico_id,
            creado_por_id=usuario_admin.usuario_id,
            estado=estado
        )
        inscripcion = Inscripcion(**data)
        db_session.add(inscripcion)
        inscripciones.append(inscripcion)
    
    db_session.commit()
    for inscripcion in inscripciones:
        db_session.refresh(inscripcion)
    return inscripciones


# ==================== FIXTURES COMBINADOS ====================

@pytest.fixture
def escenario_inscripcion_completo(
    db_session: Session,
    institucion_test: Institucion,
    programa_pregrado: Programa,
    curso_inscripciones_abiertas,
    grupo_inscripciones_abiertas: Grupo,
    periodo_inscripciones_abiertas: PeriodoAcademico,
    usuario_estudiante: Usuario,
    usuario_admin: Usuario
):
    """Escenario completo listo para proceso de inscripción"""
    return {
        "institucion": institucion_test,
        "programa": programa_pregrado,
        "curso": curso_inscripciones_abiertas,
        "grupo": grupo_inscripciones_abiertas,
        "periodo": periodo_inscripciones_abiertas,
        "estudiante": usuario_estudiante,
        "admin": usuario_admin,
        "db": db_session
    }
