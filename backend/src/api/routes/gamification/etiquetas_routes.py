"""API Endpoints para el sistema de Etiquetas (Badges).

Endpoints:
- GET /catalogo - Obtener catálogo de etiquetas
- POST /comprar/{etiqueta_id} - Comprar etiqueta
- GET /me - Obtener mis etiquetas
- POST /equipar - Equipar etiquetas (máx 5)
- POST /desequipar/{usuario_etiqueta_id} - Desequipar etiqueta
- GET /evolucion/{usuario_etiqueta_id} - Verificar evolución
- POST /evolucionar/{usuario_etiqueta_id} - Evolucionar etiqueta
- GET /estadisticas - Obtener estadísticas

Author: GitHub Copilot & Team
Date: 2 de noviembre de 2025
Version: 1.0.0
"""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from src.api.dependencies import get_current_user
from src.api.deps import get_db
from src.models.users.usuario import Usuario
from src.schemas.gamification import (
    BaseResponse,
    CatalogoEtiquetasResponse,
    CategoriaEtiqueta,
    CompraEtiquetaResponse,
    EquiparEtiquetasRequest,
    EquiparEtiquetasResponse,
    ErrorResponse,
    EstadisticasEtiquetasResponse,
    EvolucionDisponibleResponse,
    EvolucionResponse,
    MisEtiquetasResponse,
    RarezaEtiqueta,
)
from src.services.gamification.etiquetas_service import EtiquetasService


router = APIRouter()


def get_etiquetas_service(db: Session = Depends(get_db)) -> EtiquetasService:
    """Dependency para obtener EtiquetasService."""
    return EtiquetasService(db)


@router.get(
    "/catalogo",
    response_model=CatalogoEtiquetasResponse,
    summary="Obtener catálogo de etiquetas",
    description="Obtiene el catálogo completo de etiquetas disponibles con filtros opcionales.",
    responses={
        200: {
            "description": "Catálogo obtenido exitosamente",
            "model": CatalogoEtiquetasResponse,
        },
        401: {"description": "No autenticado", "model": ErrorResponse},
    },
)
async def obtener_catalogo(
    limit: int = Query(50, ge=1, le=200, description="Cantidad de resultados"),
    offset: int = Query(0, ge=0, description="Desplazamiento para paginación"),
    categoria: CategoriaEtiqueta | None = Query(
        None, description="Filtrar por categoría"
    ),
    rareza: RarezaEtiqueta | None = Query(None, description="Filtrar por rareza"),
    es_comprable: bool | None = Query(None, description="Filtrar solo comprables"),
    buscar: str | None = Query(
        None, min_length=2, max_length=50, description="Buscar por nombre"
    ),
    current_user: Usuario = Depends(get_current_user),
    service: EtiquetasService = Depends(get_etiquetas_service),
):
    """Obtener catálogo de etiquetas con filtros.

    Filtros disponibles:
    - `categoria`: Filtrar por categoría (programacion, matematicas, etc.)
    - `rareza`: Filtrar por rareza (comun, raro, epico, legendario)
    - `es_comprable`: Solo etiquetas comprables o solo por logro
    - `buscar`: Buscar por nombre
    - `limit`: Cantidad de resultados (1-200)
    - `offset`: Paginación

    Retorna lista de etiquetas con info de precio, evolución y requisitos.
    """
    try:
        resultado = await service.obtener_catalogo(
            limit=limit,
            offset=offset,
            categoria=categoria.value if categoria else None,
            rareza=rareza.value if rareza else None,
            es_comprable=es_comprable,
            buscar=buscar,
        )

        filtros = {}
        if categoria:
            filtros["categoria"] = categoria.value
        if rareza:
            filtros["rareza"] = rareza.value
        if es_comprable is not None:
            filtros["es_comprable"] = es_comprable
        if buscar:
            filtros["buscar"] = buscar

        return CatalogoEtiquetasResponse(
            etiquetas=resultado["etiquetas"],
            total=resultado["total"],
            filtros_aplicados=filtros,
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener catálogo: {e!s}",
        ) from e


@router.post(
    "/comprar/{etiqueta_id}",
    response_model=CompraEtiquetaResponse,
    summary="Comprar etiqueta",
    description="Compra una etiqueta del catálogo usando puntos acumulados.",
    responses={
        200: {
            "description": "Etiqueta comprada exitosamente",
            "model": CompraEtiquetaResponse,
        },
        400: {
            "description": "Puntos insuficientes o etiqueta no comprable",
            "model": ErrorResponse,
        },
        401: {"description": "No autenticado", "model": ErrorResponse},
        404: {"description": "Etiqueta no encontrada", "model": ErrorResponse},
        409: {"description": "Ya posee esta etiqueta", "model": ErrorResponse},
    },
)
async def comprar_etiqueta(
    etiqueta_id: UUID,
    current_user: Usuario = Depends(get_current_user),
    service: EtiquetasService = Depends(get_etiquetas_service),
):
    """Comprar una etiqueta del catálogo.

    Requisitos:
    - La etiqueta debe ser comprable (no solo por logro)
    - El usuario debe tener puntos suficientes
    - El usuario no debe poseer ya la etiqueta

    Retorna:
    - Información de la etiqueta comprada
    - Puntos gastados y restantes
    - Confirmación de compra
    """
    try:
        resultado = await service.comprar_etiqueta(
            usuario_id=current_user.id, etiqueta_id=etiqueta_id
        )

        if resultado.get("error"):
            if "no encontrada" in resultado["error"]:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail=resultado["error"]
                )
            if "ya posee" in resultado["error"]:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT, detail=resultado["error"]
                )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=resultado["error"]
            )

        return CompraEtiquetaResponse(
            success=True,
            message=f"¡Etiqueta '{resultado['etiqueta']['nombre']}' adquirida!",
            etiqueta=resultado["etiqueta"],
            puntos_gastados=resultado["puntos_gastados"],
            puntos_restantes=resultado["puntos_restantes"],
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al comprar etiqueta: {e!s}",
        ) from e


@router.get(
    "/me",
    response_model=MisEtiquetasResponse,
    summary="Obtener mis etiquetas",
    description="Obtiene todas las etiquetas que posee el usuario actual.",
    responses={
        200: {
            "description": "Etiquetas obtenidas exitosamente",
            "model": MisEtiquetasResponse,
        },
        401: {"description": "No autenticado", "model": ErrorResponse},
    },
)
async def obtener_mis_etiquetas(
    equipadas_solo: bool = Query(False, description="Mostrar solo equipadas"),
    current_user: Usuario = Depends(get_current_user),
    service: EtiquetasService = Depends(get_etiquetas_service),
):
    """Obtener todas las etiquetas del usuario.

    Parámetros:
    - `equipadas_solo`: Si es True, solo muestra las etiquetas equipadas

    Retorna lista con:
    - Información completa de cada etiqueta
    - Estado de equipamiento
    - Orden de visualización (1-5)
    - Fecha de obtención
    - Método de obtención (compra, logro, evolución)
    - Progreso hacia evolución (si aplica)
    """
    try:
        resultado = await service.obtener_etiquetas_usuario(
            usuario_id=current_user.id, equipadas_solo=equipadas_solo
        )

        return MisEtiquetasResponse(
            etiquetas=resultado["etiquetas"],
            total=resultado["total"],
            equipadas=resultado["equipadas"],
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener etiquetas: {e!s}",
        ) from e


@router.post(
    "/equipar",
    response_model=EquiparEtiquetasResponse,
    summary="Equipar etiquetas",
    description="Equipa hasta 5 etiquetas para mostrar en el perfil. El orden en la lista determina el orden de visualización.",
    responses={
        200: {
            "description": "Etiquetas equipadas exitosamente",
            "model": EquiparEtiquetasResponse,
        },
        400: {
            "description": "Datos inválidos o etiquetas no poseídas",
            "model": ErrorResponse,
        },
        401: {"description": "No autenticado", "model": ErrorResponse},
    },
)
async def equipar_etiquetas(
    request: EquiparEtiquetasRequest,
    current_user: Usuario = Depends(get_current_user),
    service: EtiquetasService = Depends(get_etiquetas_service),
):
    """Equipar etiquetas en el perfil (máximo 5).

    Body:
    - `etiquetas_ids`: Lista de UUIDs ordenados (1-5 items)

    El orden en la lista determina el orden de visualización:
    - Posición 0 → se muestra primera
    - Posición 1 → se muestra segunda
    - etc.

    Nota: Las etiquetas no incluidas serán desequipadas automáticamente.
    """
    try:
        resultado = await service.equipar_etiquetas(
            usuario_id=current_user.id,
            etiquetas_ids=[str(eid) for eid in request.etiquetas_ids],
        )

        if resultado.get("error"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=resultado["error"]
            )

        return EquiparEtiquetasResponse(
            success=True,
            message=f"¡{len(request.etiquetas_ids)} etiquetas equipadas!",
            etiquetas_equipadas=len(request.etiquetas_ids),
            orden=resultado["orden"],
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al equipar etiquetas: {e!s}",
        ) from e


@router.post(
    "/desequipar/{usuario_etiqueta_id}",
    response_model=BaseResponse,
    summary="Desequipar etiqueta",
    description="Desequipa una etiqueta específica del perfil.",
    responses={
        200: {
            "description": "Etiqueta desequipada exitosamente",
            "model": BaseResponse,
        },
        401: {"description": "No autenticado", "model": ErrorResponse},
        404: {"description": "Etiqueta no encontrada", "model": ErrorResponse},
    },
)
async def desequipar_etiqueta(
    usuario_etiqueta_id: UUID,
    current_user: Usuario = Depends(get_current_user),
    service: EtiquetasService = Depends(get_etiquetas_service),
):
    """Desequipar una etiqueta específica.

    La etiqueta permanece en el inventario pero deja de mostrarse en el perfil.
    """
    try:
        resultado = await service.desequipar_etiqueta(
            usuario_id=current_user.id, usuario_etiqueta_id=usuario_etiqueta_id
        )

        if resultado.get("error"):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=resultado["error"]
            )

        return BaseResponse(success=True, message="¡Etiqueta desequipada!")

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al desequipar etiqueta: {e!s}",
        ) from e


@router.get(
    "/evolucion/{usuario_etiqueta_id}",
    response_model=EvolucionDisponibleResponse,
    summary="Verificar evolución disponible",
    description="Verifica si una etiqueta puede evolucionar y muestra los requisitos.",
    responses={
        200: {
            "description": "Información de evolución obtenida",
            "model": EvolucionDisponibleResponse,
        },
        401: {"description": "No autenticado", "model": ErrorResponse},
        404: {"description": "Etiqueta no encontrada", "model": ErrorResponse},
    },
)
async def verificar_evolucion(
    usuario_etiqueta_id: UUID,
    current_user: Usuario = Depends(get_current_user),
    service: EtiquetasService = Depends(get_etiquetas_service),
):
    """Verificar si una etiqueta puede evolucionar.

    Retorna:
    - Si tiene evolución disponible
    - Si cumple los requisitos
    - Información de etiqueta actual y evolución
    - Requisitos necesarios
    - Progreso actual del usuario
    """
    try:
        resultado = await service.verificar_evolucion(
            usuario_id=current_user.id, usuario_etiqueta_id=usuario_etiqueta_id
        )

        if resultado.get("error"):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=resultado["error"]
            )

        return EvolucionDisponibleResponse(**resultado)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al verificar evolución: {e!s}",
        ) from e


@router.post(
    "/evolucionar/{usuario_etiqueta_id}",
    response_model=EvolucionResponse,
    summary="Evolucionar etiqueta",
    description="Evoluciona una etiqueta a su siguiente nivel si cumple los requisitos.",
    responses={
        200: {
            "description": "Etiqueta evolucionada exitosamente",
            "model": EvolucionResponse,
        },
        400: {"description": "No cumple requisitos", "model": ErrorResponse},
        401: {"description": "No autenticado", "model": ErrorResponse},
        404: {"description": "Etiqueta no encontrada", "model": ErrorResponse},
    },
)
async def evolucionar_etiqueta(
    usuario_etiqueta_id: UUID,
    current_user: Usuario = Depends(get_current_user),
    service: EtiquetasService = Depends(get_etiquetas_service),
):
    """Evolucionar una etiqueta al siguiente nivel.

    Requisitos:
    - La etiqueta debe tener evolución disponible
    - El usuario debe cumplir todos los requisitos

    Al evolucionar:
    - Se reemplaza por la versión evolucionada
    - Se mantiene el historial
    - Se otorgan recompensas adicionales (si aplica)
    """
    try:
        resultado = await service.evolucionar_etiqueta(
            usuario_id=current_user.id, usuario_etiqueta_id=usuario_etiqueta_id
        )

        if resultado.get("error"):
            if "no encontrada" in resultado["error"]:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail=resultado["error"]
                )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=resultado["error"]
            )

        return EvolucionResponse(
            success=True,
            message=f"¡'{resultado['etiqueta_anterior']['nombre']}' evolucionó a '{resultado['etiqueta_nueva']['nombre']}'!",
            etiqueta_anterior=resultado["etiqueta_anterior"],
            etiqueta_nueva=resultado["etiqueta_nueva"],
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al evolucionar etiqueta: {e!s}",
        ) from e


@router.get(
    "/estadisticas",
    response_model=EstadisticasEtiquetasResponse,
    summary="Obtener estadísticas de etiquetas",
    description="Obtiene estadísticas sobre las etiquetas del usuario.",
    responses={
        200: {
            "description": "Estadísticas obtenidas exitosamente",
            "model": EstadisticasEtiquetasResponse,
        },
        401: {"description": "No autenticado", "model": ErrorResponse},
    },
)
async def obtener_estadisticas(
    current_user: Usuario = Depends(get_current_user),
    service: EtiquetasService = Depends(get_etiquetas_service),
):
    """Obtener estadísticas de etiquetas del usuario.

    Retorna:
    - Total de etiquetas
    - Etiquetas equipadas actualmente
    - Distribución por método de obtención (compra, logro, evolución)
    - Distribución por rareza (común, raro, épico, legendario)
    - Distribución por categoría temática
    """
    try:
        resultado = await service.obtener_estadisticas(usuario_id=current_user.id)

        return EstadisticasEtiquetasResponse(**resultado)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener estadísticas: {e!s}",
        ) from e
