"""Rutas de API para gestión de Períodos Académicos.

Thin controllers usando periodo_academico_service.
Implementa SOLID + Clean Code: Delegación total de lógica a service layer.
"""

import logging
from typing import Never

from fastapi import APIRouter, Body, Depends, Path, Query, status
from sqlalchemy.orm import Session

from src.api import deps
from src.enums.academic import EstadoPeriodo, TipoPeriodo
from src.models.users.usuario import Usuario
from src.schemas.academic.periodo_academico_schemas import (
    PeriodoAcademicoCancelar,
    PeriodoAcademicoCreate,
    PeriodoAcademicoFinalizar,
    PeriodoAcademicoListResponse,
    PeriodoAcademicoResponse,
    PeriodoAcademicoSimple,
    PeriodoAcademicoUpdate,
)
from src.services.academic.periodo_academico_service import periodo_academico_service


# Configuración
logger = logging.getLogger(__name__)
router = APIRouter(prefix="/periodos-academicos", tags=["Períodos Académicos"])


# ==================== CRUD Básico ====================


@router.post(
    "/",
    response_model=PeriodoAcademicoResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear período académico",
    description="Crea un nuevo período académico con validaciones completas",
)
async def crear_periodo(
    periodo_in: PeriodoAcademicoCreate,
    current_user: Usuario = Depends(deps.get_current_active_user),
    db: Session = Depends(deps.get_db),
):
    """Crea un nuevo período académico.

    Validaciones automáticas:
    - Código único
    - Coherencia de fechas
    - Sin conflictos con otros períodos
    - Permisos del usuario

    Requiere rol: coordinador o superadmin
    """
    logger.info(
        f"POST /periodos-academicos - Usuario: {current_user.usuario_id} "
        f"({current_user.rol}) - Institución: {periodo_in.institucion_id}"
    )

    return periodo_academico_service.crear_periodo(
        db=db, periodo_in=periodo_in, usuario=current_user
    )


@router.get(
    "/{periodo_id}",
    response_model=PeriodoAcademicoResponse,
    summary="Obtener período por ID",
    description="Obtiene detalles completos de un período académico",
)
async def obtener_periodo(
    periodo_id: int = Path(..., gt=0, description="ID del período"),
    current_user: Usuario = Depends(deps.get_current_user),
    db: Session = Depends(deps.get_db),
):
    """Obtiene un período académico por su ID.

    Retorna todos los campos incluyendo properties calculadas.
    Usa cache para mejorar performance.
    """
    logger.info(
        f"GET /periodos-academicos/{periodo_id} - Usuario: {current_user.usuario_id}"
    )

    return periodo_academico_service.obtener_periodo(
        db=db, periodo_id=periodo_id, usuario=current_user
    )


@router.get(
    "/",
    response_model=PeriodoAcademicoListResponse,
    summary="Listar períodos académicos",
    description="Lista períodos con filtros y paginación",
)
async def listar_periodos(
    institucion_id: int = Query(..., gt=0, description="ID de la institución"),
    tipo: TipoPeriodo | None = Query(None, description="Filtrar por tipo de período"),
    estado: EstadoPeriodo | None = Query(None, description="Filtrar por estado"),
    anio: int | None = Query(None, ge=2000, le=2100, description="Filtrar por año"),
    activo: bool | None = Query(None, description="Filtrar por estado activo"),
    page: int = Query(1, ge=1, description="Número de página"),
    page_size: int = Query(20, ge=1, le=100, description="Tamaño de página"),
    current_user: Usuario = Depends(deps.get_current_user),
    db: Session = Depends(deps.get_db),
):
    """Lista períodos académicos con filtros opcionales.

    Filtros disponibles:
    - tipo: Tipo de período (semestral, trimestral, etc.)
    - estado: Estado del período
    - anio: Año específico
    - activo: Solo períodos activos/inactivos

    Soporta paginación con page y page_size.
    """
    logger.info(
        f"GET /periodos-academicos - Usuario: {current_user.usuario_id} - "
        f"Institución: {institucion_id} - Filtros: tipo={tipo}, estado={estado}, anio={anio}"
    )

    skip = (page - 1) * page_size
    periodos, total = periodo_academico_service.listar_periodos(
        db=db,
        institucion_id=institucion_id,
        usuario=current_user,
        tipo=tipo,
        estado=estado,
        anio=anio,
        activo=activo,
        skip=skip,
        limit=page_size,
    )

    # Calcular total de páginas
    total_pages = (total + page_size - 1) // page_size

    return {
        "items": periodos,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages,
    }


@router.put(
    "/{periodo_id}",
    response_model=PeriodoAcademicoResponse,
    summary="Actualizar período académico",
    description="Actualiza campos de un período existente",
)
async def actualizar_periodo(
    periodo_id: int = Path(..., gt=0, description="ID del período"),
    periodo_update: PeriodoAcademicoUpdate = Body(...),
    current_user: Usuario = Depends(deps.get_current_active_user),
    db: Session = Depends(deps.get_db),
):
    """Actualiza un período académico.

    Todos los campos son opcionales.
    Validaciones automáticas de coherencia.

    Requiere rol: coordinador o superadmin
    """
    logger.info(
        f"PUT /periodos-academicos/{periodo_id} - Usuario: {current_user.usuario_id}"
    )

    return periodo_academico_service.actualizar_periodo(
        db=db,
        periodo_id=periodo_id,
        periodo_update=periodo_update,
        usuario=current_user,
    )


@router.delete(
    "/{periodo_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar período académico",
    description="Elimina un período (solo si no tiene datos asociados)",
)
async def eliminar_periodo(
    periodo_id: int = Path(..., gt=0, description="ID del período"),
    current_user: Usuario = Depends(deps.get_current_active_user),
    db: Session = Depends(deps.get_db),
) -> Never:
    """Elimina un período académico.

    PRECAUCIÓN: Solo eliminar períodos sin inscripciones/cursos asociados.
    En producción, considerar soft delete.

    Requiere rol: superadmin
    """
    # TODO: Implementar cuando se tenga lógica de eliminación segura
    logger.warning(
        f"DELETE /periodos-academicos/{periodo_id} - Usuario: {current_user.usuario_id} "
        "(ENDPOINT NO IMPLEMENTADO)"
    )

    from fastapi import HTTPException

    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Eliminación de períodos no implementada aún. Use cancelación en su lugar.",
    )


# ==================== Consultas Especiales ====================


@router.get(
    "/institucion/{institucion_id}/actual",
    response_model=PeriodoAcademicoResponse,
    summary="Obtener período actual",
    description="Obtiene el período académico que está en curso actualmente",
)
async def obtener_periodo_actual(
    institucion_id: int = Path(..., gt=0, description="ID de la institución"),
    current_user: Usuario = Depends(deps.get_current_user),
    db: Session = Depends(deps.get_db),
):
    """Obtiene el período académico actual de una institución.

    Busca primero el marcado como 'es_actual=True'.
    Si no hay, busca el que contenga la fecha actual.

    Usa cache agresivo (se consulta frecuentemente).
    """
    logger.info(
        f"GET /periodos-academicos/institucion/{institucion_id}/actual - "
        f"Usuario: {current_user.usuario_id}"
    )

    periodo = periodo_academico_service.obtener_periodo_actual(
        db=db, institucion_id=institucion_id, usuario=current_user
    )

    if not periodo:
        from fastapi import HTTPException

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No hay período académico actual para la institución {institucion_id}",
        )

    return periodo


@router.get(
    "/institucion/{institucion_id}/inscripciones-abiertas",
    response_model=list[PeriodoAcademicoSimple],
    summary="Períodos con inscripciones abiertas",
    description="Obtiene períodos que actualmente aceptan inscripciones",
)
async def obtener_periodos_inscripciones_abiertas(
    institucion_id: int = Path(..., gt=0, description="ID de la institución"),
    current_user: Usuario = Depends(deps.get_current_user),
    db: Session = Depends(deps.get_db),
):
    """Obtiene períodos con inscripciones abiertas.

    Verifica automáticamente:
    - Estado sea 'inscripciones_abiertas'
    - Fecha actual esté en rango de inscripciones
    - Período esté activo

    Útil para estudiantes que quieren inscribirse.
    """
    logger.info(
        f"GET /periodos-academicos/institucion/{institucion_id}/inscripciones-abiertas - "
        f"Usuario: {current_user.usuario_id}"
    )

    return periodo_academico_service.obtener_periodos_con_inscripciones_abiertas(
        db=db, institucion_id=institucion_id, usuario=current_user
    )


# ==================== Operaciones de Estado ====================


@router.post(
    "/{periodo_id}/activar",
    response_model=PeriodoAcademicoResponse,
    summary="Activar período",
    description="Activa un período académico",
)
async def activar_periodo(
    periodo_id: int = Path(..., gt=0, description="ID del período"),
    current_user: Usuario = Depends(deps.get_current_active_user),
    db: Session = Depends(deps.get_db),
):
    """Activa un período académico.

    Cambia activo=True y ajusta el estado según fechas.

    Requiere rol: coordinador o superadmin
    """
    logger.info(
        f"POST /periodos-academicos/{periodo_id}/activar - "
        f"Usuario: {current_user.usuario_id}"
    )

    return periodo_academico_service.activar_periodo(
        db=db, periodo_id=periodo_id, usuario=current_user
    )


@router.post(
    "/{periodo_id}/marcar-actual",
    response_model=PeriodoAcademicoResponse,
    summary="Marcar como período actual",
    description="Marca un período como el actual (desmarca otros)",
)
async def marcar_como_actual(
    periodo_id: int = Path(..., gt=0, description="ID del período"),
    current_user: Usuario = Depends(deps.get_current_active_user),
    db: Session = Depends(deps.get_db),
):
    """Marca un período como el actual.

    Automáticamente:
    - Desmarca cualquier otro período como actual
    - Activa el período
    - Invalida cache

    Solo un período puede ser actual a la vez.

    Requiere rol: coordinador o superadmin
    """
    logger.info(
        f"POST /periodos-academicos/{periodo_id}/marcar-actual - "
        f"Usuario: {current_user.usuario_id}"
    )

    return periodo_academico_service.marcar_como_actual(
        db=db, periodo_id=periodo_id, usuario=current_user
    )


@router.post(
    "/{periodo_id}/finalizar",
    response_model=PeriodoAcademicoResponse,
    summary="Finalizar período",
    description="Finaliza un período académico en curso",
)
async def finalizar_periodo(
    periodo_id: int = Path(..., gt=0, description="ID del período"),
    datos: PeriodoAcademicoFinalizar = Body(default=PeriodoAcademicoFinalizar()),
    current_user: Usuario = Depends(deps.get_current_active_user),
    db: Session = Depends(deps.get_db),
):
    """Finaliza un período académico.

    Cambia estado a 'finalizado' y marca como no actual.
    Solo puede finalizar períodos en estado 'en_curso' o 'evaluaciones'.

    Requiere rol: coordinador o superadmin
    """
    logger.info(
        f"POST /periodos-academicos/{periodo_id}/finalizar - "
        f"Usuario: {current_user.usuario_id}"
    )

    return periodo_academico_service.finalizar_periodo(
        db=db, periodo_id=periodo_id, usuario=current_user
    )


@router.post(
    "/{periodo_id}/cancelar",
    response_model=PeriodoAcademicoResponse,
    summary="Cancelar período",
    description="Cancela un período académico (requiere motivo)",
)
async def cancelar_periodo(
    periodo_id: int = Path(..., gt=0, description="ID del período"),
    datos: PeriodoAcademicoCancelar = Body(...),
    current_user: Usuario = Depends(deps.get_current_active_user),
    db: Session = Depends(deps.get_db),
):
    """Cancela un período académico.

    Requiere motivo (mínimo 10 caracteres).
    Marca el período como cancelado e inactivo.

    No se puede cancelar un período finalizado.

    Requiere rol: coordinador o superadmin
    """
    logger.warning(
        f"POST /periodos-academicos/{periodo_id}/cancelar - "
        f"Usuario: {current_user.usuario_id} - Motivo: {datos.motivo[:50]}..."
    )

    return periodo_academico_service.cancelar_periodo(
        db=db, periodo_id=periodo_id, motivo=datos.motivo, usuario=current_user
    )


# ==================== Estadísticas ====================


@router.get(
    "/{periodo_id}/estadisticas",
    response_model=dict,
    summary="Estadísticas del período",
    description="Obtiene estadísticas completas de un período académico",
)
async def obtener_estadisticas_periodo(
    periodo_id: int = Path(..., gt=0, description="ID del período"),
    current_user: Usuario = Depends(deps.get_current_user),
    db: Session = Depends(deps.get_db),
):
    """Obtiene estadísticas de un período académico.

    Incluye (cuando estén implementados):
    - Total de inscripciones
    - Total de grupos/secciones
    - Total de cursos ofrecidos
    - Total de estudiantes
    - Total de profesores
    - Porcentaje de avance
    - Etc.

    Por ahora retorna estadísticas básicas del período.
    """
    logger.info(
        f"GET /periodos-academicos/{periodo_id}/estadisticas - "
        f"Usuario: {current_user.usuario_id}"
    )

    from src.crud.academic.crud_periodo_academico import periodo_academico_crud

    periodo = periodo_academico_service.obtener_periodo(
        db=db, periodo_id=periodo_id, usuario=current_user
    )

    return periodo_academico_crud.get_estadisticas(
        db=db, institucion_id=periodo.institucion_id, periodo_id=periodo_id
    )
