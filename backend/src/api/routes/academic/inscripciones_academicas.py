"""API REST para gestión de Inscripciones Académicas Completas.

Sistema moderno de inscripciones con workflow completo de estados.
Reemplaza progresivamente el sistema legacy de inscripciones.py

Endpoints organizados en 6 categorías:
1. CRUD Básico (5 endpoints)
2. Operaciones de Estado (7 endpoints)
3. Consultas Especiales (5 endpoints)
4. Acciones Específicas (4 endpoints)
5. Reportes y Estadísticas (3 endpoints)
6. Operaciones Masivas (1 endpoint)

Total: 25 endpoints

Principios SOLID aplicados:
- Controllers delgados (thin controllers)
- Lógica en Service layer
- Validación en Schemas
- Separación de responsabilidades
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from src.api.dependencies import get_current_user, get_db
from src.crud.academic.crud_inscripcion import inscripcion_crud
from src.enums.academic import EstadoInscripcion, MotivoRetiro, TipoInscripcion
from src.models.users.usuario import Usuario
from src.schemas.academic.inscripcion_schemas import (
    InscripcionActualizarCalificacion,
    InscripcionActualizarDocumentos,
    InscripcionAprobar,
    InscripcionBulkCreate,
    InscripcionBulkResponse,
    InscripcionCreate,
    InscripcionEstadisticas,
    InscripcionFiltros,
    InscripcionListaEspera,
    InscripcionListResponse,
    InscripcionRechazar,
    InscripcionRegistrarPago,
    InscripcionResponse,
    InscripcionRetirar,
    InscripcionSimple,
    InscripcionUpdate,
)
from src.services.academic.inscripcion_service import inscripcion_academica_service


router = APIRouter(prefix="/inscripciones", tags=["Inscripciones Académicas"])


# ==================== CRUD Básico ====================


@router.post(
    "/",
    response_model=InscripcionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear inscripción",
    description="""
    Crea una nueva inscripción con validaciones completas:
    - Verifica cupos disponibles
    - Valida límites de créditos
    - Calcula costos con descuentos
    - Determina estado inicial automático
    - Agrega a lista de espera si no hay cupos
    """,
)
def crear_inscripcion(
    inscripcion_in: InscripcionCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
) -> InscripcionResponse:
    """Crea una nueva inscripción."""
    inscripcion = inscripcion_academica_service.crear_inscripcion(
        db, inscripcion_in, current_user
    )
    return InscripcionResponse.model_validate(inscripcion)


@router.get(
    "/{inscripcion_id}",
    response_model=InscripcionResponse,
    summary="Obtener inscripción",
    description="Obtiene una inscripción por ID con validación de permisos",
)
def obtener_inscripcion(
    inscripcion_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
) -> InscripcionResponse:
    """Obtiene una inscripción por ID."""
    inscripcion = inscripcion_academica_service.obtener_inscripcion(
        db, inscripcion_id, current_user
    )
    return InscripcionResponse.model_validate(inscripcion)


@router.get(
    "/",
    response_model=InscripcionListResponse,
    summary="Listar inscripciones",
    description="Lista inscripciones con filtros avanzados (12+ filtros combinables)",
)
def listar_inscripciones(
    estudiante_id: int | None = Query(None, description="ID del estudiante"),
    grupo_id: int | None = Query(None, description="ID del grupo"),
    periodo_id: int | None = Query(None, description="ID del período académico"),
    programa_id: int | None = Query(None, description="ID del programa"),
    estado: EstadoInscripcion | None = Query(
        None, description="Estado de la inscripción"
    ),
    tipo: TipoInscripcion | None = Query(None, description="Tipo de inscripción"),
    esta_pagado: bool | None = Query(
        None, description="Filtrar por pagadas/no pagadas"
    ),
    esta_aprobada: bool | None = Query(
        None, description="Filtrar por aprobadas/no aprobadas"
    ),
    en_lista_espera: bool | None = Query(
        None, description="Filtrar por lista de espera"
    ),
    activo: bool = Query(True, description="Filtrar por activas (soft delete)"),
    skip: int = Query(0, ge=0, description="Registros a saltar (paginación)"),
    limit: int = Query(100, ge=1, le=1000, description="Máximo de registros"),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
) -> InscripcionListResponse:
    """Lista inscripciones con filtros."""
    filtros = InscripcionFiltros(
        estudiante_id=estudiante_id,
        grupo_id=grupo_id,
        periodo_id=periodo_id,
        programa_id=programa_id,
        estado=estado,
        tipo=tipo,
        esta_pagado=esta_pagado,
        esta_aprobada=esta_aprobada,
        en_lista_espera=en_lista_espera,
        activo=activo,
    )

    inscripciones, total = inscripcion_academica_service.listar_con_filtros(
        db, filtros, current_user, skip=skip, limit=limit
    )

    return InscripcionListResponse(
        items=[InscripcionSimple.model_validate(i) for i in inscripciones],
        total=total,
        page=skip // limit + 1,
        page_size=limit,
    )


@router.put(
    "/{inscripcion_id}",
    response_model=InscripcionResponse,
    summary="Actualizar inscripción",
    description="Actualiza campos de una inscripción (solo coordinadores)",
)
def actualizar_inscripcion(
    inscripcion_id: int,
    inscripcion_in: InscripcionUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
) -> InscripcionResponse:
    """Actualiza una inscripción."""
    # Validar permisos
    if current_user.rol not in ["coordinador", "superadmin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo coordinadores pueden actualizar inscripciones",
        )

    inscripcion = inscripcion_crud.get(db, inscripcion_id)
    if not inscripcion:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Inscripción {inscripcion_id} no encontrada",
        )

    inscripcion_actualizada = inscripcion_crud.update(
        db, inscripcion, inscripcion_in, current_user.usuario_id
    )

    return InscripcionResponse.model_validate(inscripcion_actualizada)


@router.delete(
    "/{inscripcion_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar inscripción",
    description="Elimina (soft delete) una inscripción",
)
def eliminar_inscripcion(
    inscripcion_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
) -> None:
    """Elimina (cancela) una inscripción."""
    # Validar permisos
    if current_user.rol not in ["coordinador", "superadmin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo coordinadores pueden eliminar inscripciones",
        )

    inscripcion = inscripcion_crud.get(db, inscripcion_id)
    if not inscripcion:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Inscripción {inscripcion_id} no encontrada",
        )

    # Soft delete usando retirar
    inscripcion_crud.retirar(
        db,
        inscripcion_id,
        MotivoRetiro.cancelacion_administrativa,
        "Eliminada por administrador",
        False,  # No es voluntario
        current_user.usuario_id,
    )


# ==================== Operaciones de Estado ====================


@router.post(
    "/{inscripcion_id}/aprobar",
    response_model=InscripcionResponse,
    summary="Aprobar inscripción",
    description="Aprueba una inscripción pendiente (solo coordinadores)",
)
def aprobar_inscripcion(
    inscripcion_id: int,
    data: InscripcionAprobar,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
) -> InscripcionResponse:
    """Aprueba una inscripción."""
    inscripcion = inscripcion_academica_service.aprobar_inscripcion(
        db, inscripcion_id, current_user, data.comentarios
    )
    return InscripcionResponse.model_validate(inscripcion)


@router.post(
    "/{inscripcion_id}/rechazar",
    response_model=InscripcionResponse,
    summary="Rechazar inscripción",
    description="Rechaza una inscripción con motivo (solo coordinadores)",
)
def rechazar_inscripcion(
    inscripcion_id: int,
    data: InscripcionRechazar,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
) -> InscripcionResponse:
    """Rechaza una inscripción."""
    inscripcion = inscripcion_academica_service.rechazar_inscripcion(
        db, inscripcion_id, data.motivo, data.descripcion, current_user
    )
    return InscripcionResponse.model_validate(inscripcion)


@router.post(
    "/{inscripcion_id}/confirmar",
    response_model=InscripcionResponse,
    summary="Confirmar inscripción",
    description="Estudiante confirma que asistirá (solo el estudiante dueño)",
)
def confirmar_inscripcion(
    inscripcion_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
) -> InscripcionResponse:
    """Confirma una inscripción."""
    inscripcion = inscripcion_academica_service.confirmar_inscripcion(
        db, inscripcion_id, current_user
    )
    return InscripcionResponse.model_validate(inscripcion)


@router.post(
    "/{inscripcion_id}/activar",
    response_model=InscripcionResponse,
    summary="Activar inscripción",
    description="Activa una inscripción confirmada (solo coordinadores)",
)
def activar_inscripcion(
    inscripcion_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
) -> InscripcionResponse:
    """Activa una inscripción."""
    inscripcion = inscripcion_academica_service.activar_inscripcion(
        db, inscripcion_id, current_user
    )
    return InscripcionResponse.model_validate(inscripcion)


@router.post(
    "/{inscripcion_id}/retirar",
    response_model=InscripcionResponse,
    summary="Retirar inscripción",
    description="Retira una inscripción del curso",
)
def retirar_inscripcion(
    inscripcion_id: int,
    data: InscripcionRetirar,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
) -> InscripcionResponse:
    """Retira una inscripción."""
    inscripcion = inscripcion_academica_service.retirar_inscripcion(
        db,
        inscripcion_id,
        data.motivo,
        data.descripcion,
        current_user,
        data.es_voluntario,
    )
    return InscripcionResponse.model_validate(inscripcion)


@router.post(
    "/{inscripcion_id}/completar",
    response_model=InscripcionResponse,
    summary="Completar inscripción",
    description="Completa una inscripción con calificación final (solo docentes/coordinadores)",
)
def completar_inscripcion(
    inscripcion_id: int,
    data: InscripcionActualizarCalificacion,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
) -> InscripcionResponse:
    """Completa una inscripción con calificación."""
    # Validar permisos
    if current_user.rol not in ["docente", "coordinador", "superadmin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo docentes y coordinadores pueden completar inscripciones",
        )

    inscripcion = inscripcion_crud.completar(
        db,
        inscripcion_id,
        data.calificacion_final,
        data.aprobo,
        current_user.usuario_id,
    )

    return InscripcionResponse.model_validate(inscripcion)


@router.post(
    "/{inscripcion_id}/cancelar",
    response_model=InscripcionResponse,
    summary="Cancelar inscripción",
    description="Cancela una inscripción (solo coordinadores)",
)
def cancelar_inscripcion(
    inscripcion_id: int,
    motivo: str = Query(..., description="Motivo de cancelación"),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
) -> InscripcionResponse:
    """Cancela una inscripción."""
    # Validar permisos
    if current_user.rol not in ["coordinador", "superadmin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo coordinadores pueden cancelar inscripciones",
        )

    inscripcion = inscripcion_crud.retirar(
        db,
        inscripcion_id,
        MotivoRetiro.cancelacion_administrativa,
        motivo,
        False,  # No voluntario
        current_user.usuario_id,
    )

    return InscripcionResponse.model_validate(inscripcion)


# ==================== Consultas Especiales ====================


@router.get(
    "/estudiante/{estudiante_id}/",
    response_model=InscripcionListResponse,
    summary="Inscripciones del estudiante",
    description="Lista todas las inscripciones de un estudiante",
)
def listar_inscripciones_estudiante(
    estudiante_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
) -> InscripcionListResponse:
    """Lista inscripciones de un estudiante."""
    inscripciones, total = (
        inscripcion_academica_service.listar_inscripciones_estudiante(
            db, estudiante_id, current_user, skip=skip, limit=limit
        )
    )

    return InscripcionListResponse(
        items=[InscripcionSimple.model_validate(i) for i in inscripciones],
        total=total,
        page=skip // limit + 1,
        page_size=limit,
    )


@router.get(
    "/grupo/{grupo_id}/",
    response_model=InscripcionListResponse,
    summary="Inscripciones del grupo",
    description="Lista todas las inscripciones de un grupo",
)
def listar_inscripciones_grupo(
    grupo_id: int,
    solo_activas: bool = Query(False, description="Solo inscripciones activas"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
) -> InscripcionListResponse:
    """Lista inscripciones de un grupo."""
    inscripciones, total = inscripcion_academica_service.listar_inscripciones_grupo(
        db, grupo_id, current_user, solo_activas=solo_activas, skip=skip, limit=limit
    )

    return InscripcionListResponse(
        items=[InscripcionSimple.model_validate(i) for i in inscripciones],
        total=total,
        page=skip // limit + 1,
        page_size=limit,
    )


@router.get(
    "/periodo/{periodo_id}/",
    response_model=InscripcionListResponse,
    summary="Inscripciones del período",
    description="Lista todas las inscripciones de un período académico",
)
def listar_inscripciones_periodo(
    periodo_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
) -> InscripcionListResponse:
    """Lista inscripciones de un período."""
    # Validar permisos
    if current_user.rol not in ["coordinador", "superadmin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo coordinadores pueden ver inscripciones del período",
        )

    inscripciones = inscripcion_crud.get_by_periodo(
        db, periodo_id, skip=skip, limit=limit
    )

    # Contar total
    total = len(inscripcion_crud.get_by_periodo(db, periodo_id))

    return InscripcionListResponse(
        items=[InscripcionSimple.model_validate(i) for i in inscripciones],
        total=total,
        page=skip // limit + 1,
        page_size=limit,
    )


@router.get(
    "/grupo/{grupo_id}/lista-espera",
    response_model=InscripcionListResponse,
    summary="Lista de espera del grupo",
    description="Obtiene la lista de espera de un grupo ordenada por posición",
)
def obtener_lista_espera(
    grupo_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
) -> InscripcionListResponse:
    """Obtiene lista de espera de un grupo."""
    # Validar permisos
    if current_user.rol not in ["coordinador", "docente", "superadmin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tiene permisos para ver la lista de espera",
        )

    lista_espera = inscripcion_crud.get_lista_espera(db, grupo_id)

    return InscripcionListResponse(
        items=[InscripcionSimple.model_validate(i) for i in lista_espera],
        total=len(lista_espera),
        page=1,
        page_size=len(lista_espera),
    )


@router.get(
    "/pendientes/",
    response_model=InscripcionListResponse,
    summary="Inscripciones pendientes",
    description="Lista inscripciones pendientes de aprobación, pago o documentos",
)
def listar_inscripciones_pendientes(
    tipo_pendiente: str | None = Query(
        None, description="Tipo: pago, documentos, aprobacion, o todos"
    ),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
) -> InscripcionListResponse:
    """Lista inscripciones pendientes."""
    # Validar permisos
    if current_user.rol not in ["coordinador", "superadmin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo coordinadores pueden ver inscripciones pendientes",
        )

    inscripciones = inscripcion_crud.get_pendientes(
        db, tipo_pendiente=tipo_pendiente, skip=skip, limit=limit
    )

    # Contar total
    total = len(inscripcion_crud.get_pendientes(db, tipo_pendiente=tipo_pendiente))

    return InscripcionListResponse(
        items=[InscripcionSimple.model_validate(i) for i in inscripciones],
        total=total,
        page=skip // limit + 1,
        page_size=limit,
    )


# ==================== Acciones Específicas ====================


@router.post(
    "/{inscripcion_id}/registrar-pago",
    response_model=InscripcionResponse,
    summary="Registrar pago",
    description="Registra el pago de una inscripción",
)
def registrar_pago(
    inscripcion_id: int,
    data: InscripcionRegistrarPago,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
) -> InscripcionResponse:
    """Registra pago de una inscripción."""
    inscripcion = inscripcion_academica_service.registrar_pago(
        db, inscripcion_id, data.monto, data.referencia, data.forma_pago, current_user
    )
    return InscripcionResponse.model_validate(inscripcion)


@router.put(
    "/{inscripcion_id}/documentos",
    response_model=InscripcionResponse,
    summary="Actualizar documentos",
    description="Actualiza el estado de documentos de una inscripción",
)
def actualizar_documentos(
    inscripcion_id: int,
    data: InscripcionActualizarDocumentos,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
) -> InscripcionResponse:
    """Actualiza documentos de una inscripción."""
    inscripcion = inscripcion_crud.get(db, inscripcion_id)
    if not inscripcion:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Inscripción {inscripcion_id} no encontrada",
        )

    # Validar permisos
    if (
        current_user.rol == "estudiante"
        and current_user.usuario_id != inscripcion.estudiante_id
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No puede actualizar documentos de otro estudiante",
        )

    update_data = InscripcionUpdate(
        documentos_entregados=data.documentos_entregados,
        documentos_completos=data.documentos_completos,
    )

    inscripcion_actualizada = inscripcion_crud.update(
        db, inscripcion, update_data, current_user.usuario_id
    )

    return InscripcionResponse.model_validate(inscripcion_actualizada)


@router.put(
    "/{inscripcion_id}/calificacion",
    response_model=InscripcionResponse,
    summary="Actualizar calificación",
    description="Actualiza la calificación final de una inscripción (solo docentes/coordinadores)",
)
def actualizar_calificacion(
    inscripcion_id: int,
    data: InscripcionActualizarCalificacion,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
) -> InscripcionResponse:
    """Actualiza calificación de una inscripción."""
    # Validar permisos
    if current_user.rol not in ["docente", "coordinador", "superadmin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo docentes y coordinadores pueden actualizar calificaciones",
        )

    inscripcion = inscripcion_crud.get(db, inscripcion_id)
    if not inscripcion:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Inscripción {inscripcion_id} no encontrada",
        )

    update_data = InscripcionUpdate(
        calificacion_final=data.calificacion_final,
        calificacion_literal=data.calificacion_literal,
        aprobo_curso=data.aprobo,
        porcentaje_asistencia=data.porcentaje_asistencia,
    )

    inscripcion_actualizada = inscripcion_crud.update(
        db, inscripcion, update_data, current_user.usuario_id
    )

    return InscripcionResponse.model_validate(inscripcion_actualizada)


@router.post(
    "/{inscripcion_id}/lista-espera",
    response_model=InscripcionResponse,
    summary="Agregar a lista de espera",
    description="Agrega una inscripción a la lista de espera (solo coordinadores)",
)
def agregar_a_lista_espera(
    inscripcion_id: int,
    data: InscripcionListaEspera,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
) -> InscripcionResponse:
    """Agrega inscripción a lista de espera."""
    # Validar permisos
    if current_user.rol not in ["coordinador", "superadmin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo coordinadores pueden gestionar lista de espera",
        )

    inscripcion = inscripcion_crud.get(db, inscripcion_id)
    if not inscripcion:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Inscripción {inscripcion_id} no encontrada",
        )

    inscripcion.agregar_a_lista_espera(data.posicion)
    db.add(inscripcion)
    db.commit()
    db.refresh(inscripcion)

    return InscripcionResponse.model_validate(inscripcion)


# ==================== Reportes y Estadísticas ====================


@router.get(
    "/estadisticas/periodo/{periodo_id}",
    response_model=InscripcionEstadisticas,
    summary="Estadísticas del período",
    description="Obtiene estadísticas completas de inscripciones de un período",
)
def obtener_estadisticas_periodo(
    periodo_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
) -> InscripcionEstadisticas:
    """Obtiene estadísticas de inscripciones de un período."""
    stats = inscripcion_academica_service.obtener_estadisticas_periodo(
        db, periodo_id, current_user
    )
    return InscripcionEstadisticas(**stats)


@router.get(
    "/estadisticas/grupo/{grupo_id}",
    response_model=dict,
    summary="Estadísticas del grupo",
    description="Obtiene estadísticas de inscripciones y cupos de un grupo",
)
def obtener_estadisticas_grupo(
    grupo_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
) -> dict:
    """Obtiene estadísticas de un grupo."""
    return inscripcion_academica_service.obtener_estadisticas_grupo(
        db, grupo_id, current_user
    )


@router.get(
    "/dashboard/estudiante/{estudiante_id}",
    response_model=dict,
    summary="Dashboard del estudiante",
    description="Vista resumida de todas las inscripciones del estudiante",
)
def obtener_dashboard_estudiante(
    estudiante_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
) -> dict:
    """Dashboard del estudiante con resumen de inscripciones."""
    # Validar permisos
    if current_user.rol == "estudiante" and current_user.usuario_id != estudiante_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No puede ver dashboard de otro estudiante",
        )

    # Obtener todas las inscripciones
    inscripciones = inscripcion_crud.get_by_estudiante(db, estudiante_id)

    # Calcular estadísticas
    total = len(inscripciones)
    activas = len([i for i in inscripciones if i.esta_activa])
    pendientes = len([i for i in inscripciones if i.esta_pendiente])
    completadas = len(
        [i for i in inscripciones if i.estado == EstadoInscripcion.completada]
    )

    return {
        "estudiante_id": estudiante_id,
        "total_inscripciones": total,
        "inscripciones_activas": activas,
        "inscripciones_pendientes": pendientes,
        "inscripciones_completadas": completadas,
        "inscripciones_recientes": [
            InscripcionSimple.model_validate(i) for i in inscripciones[:5]
        ],
    }


# ==================== Operaciones Masivas ====================


@router.post(
    "/bulk/crear",
    response_model=InscripcionBulkResponse,
    summary="Crear inscripciones masivas",
    description="Crea múltiples inscripciones en una sola operación (solo coordinadores)",
)
def crear_inscripciones_masivas(
    data: InscripcionBulkCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
) -> InscripcionBulkResponse:
    """Crea múltiples inscripciones."""
    # Validar permisos
    if current_user.rol not in ["coordinador", "superadmin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo coordinadores pueden crear inscripciones masivas",
        )

    exitosas = []
    fallidas = []

    for inscripcion_in in data.inscripciones:
        try:
            inscripcion = inscripcion_academica_service.crear_inscripcion(
                db, inscripcion_in, current_user
            )
            exitosas.append(InscripcionSimple.model_validate(inscripcion))
        except Exception as e:
            fallidas.append(
                {
                    "estudiante_id": inscripcion_in.estudiante_id,
                    "grupo_id": inscripcion_in.grupo_id,
                    "error": str(e),
                }
            )

    return InscripcionBulkResponse(
        exitosas=len(exitosas),
        fallidas=len(fallidas),
        detalles_fallidas=fallidas,
        inscripciones_creadas=exitosas,
    )
