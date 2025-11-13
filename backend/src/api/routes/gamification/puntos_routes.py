"""API Endpoints para el sistema de Puntos.

Endpoints:
- GET /me - Obtener puntos del usuario actual
- GET /ranking - Obtener ranking global
- GET /ranking/me - Obtener posición del usuario
- POST /otorgar - Otorgar puntos (admin)
- GET /historial - Obtener historial de puntos
- GET /nivel/info - Información de niveles

Author: GitHub Copilot & Team
Date: 2 de noviembre de 2025
Version: 1.0.0
"""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from src.api.dependencies import get_current_user, require_admin
from src.api.deps import get_db
from src.models.users.usuario import Usuario
from src.schemas.gamification import (
    ErrorResponse,
    OtorgarPuntosRequest,
    OtorgarPuntosResponse,
    PosicionRankingResponse,
    PuntosCompletoResponse,
    RankingResponse,
)
from src.services.gamification.puntos_service import PuntosService


router = APIRouter()


def get_puntos_service(db: Session = Depends(get_db)) -> PuntosService:
    """Dependency para obtener PuntosService."""
    return PuntosService(db)


@router.get(
    "/me",
    response_model=PuntosCompletoResponse,
    summary="Obtener mis puntos",
    description="Obtiene información completa de puntos del usuario actual: puntos acumulados, nivel, historial reciente e insignias.",
    responses={
        200: {
            "description": "Información de puntos obtenida exitosamente",
            "model": PuntosCompletoResponse,
        },
        401: {"description": "No autenticado", "model": ErrorResponse},
        404: {"description": "Usuario no encontrado", "model": ErrorResponse},
    },
)
async def obtener_mis_puntos(
    current_user: Usuario = Depends(get_current_user),
    service: PuntosService = Depends(get_puntos_service),
):
    """Obtener información completa de puntos del usuario actual.

    Retorna:
    - Puntos acumulados totales
    - Nivel actual y progreso
    - Historial reciente (últimos 10 movimientos)
    - Insignias obtenidas
    """
    try:
        resultado = await service.obtener_puntos_usuario(current_user.usuario_id)

        if not resultado:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No se encontraron datos de puntos para el usuario",
            )

        return resultado

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener puntos: {e!s}",
        ) from e


@router.get(
    "/ranking",
    response_model=RankingResponse,
    summary="Obtener ranking global",
    description="Obtiene el ranking global de usuarios ordenado por puntos acumulados.",
    responses={
        200: {"description": "Ranking obtenido exitosamente", "model": RankingResponse},
        401: {"description": "No autenticado", "model": ErrorResponse},
    },
)
async def obtener_ranking(
    limit: int = Query(50, ge=1, le=200, description="Cantidad de resultados"),
    offset: int = Query(0, ge=0, description="Desplazamiento para paginación"),
    institucion_id: UUID | None = Query(None, description="Filtrar por institución"),
    current_user: Usuario = Depends(get_current_user),
    service: PuntosService = Depends(get_puntos_service),
):
    """Obtener ranking global de puntos.

    Parámetros opcionales:
    - `limit`: Cantidad de resultados (1-200, default 50)
    - `offset`: Desplazamiento para paginación
    - `institucion_id`: Filtrar por institución específica

    Retorna lista paginada ordenada por puntos descendente.
    """
    try:
        resultado = await service.obtener_ranking(
            limite=limit, offset=offset, institucion_id=institucion_id
        )

        return RankingResponse(
            success=True,
            data=resultado["data"],
            total=resultado["total"],
            limit=limit,
            offset=offset,
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener ranking: {e!s}",
        ) from e


@router.get(
    "/ranking/me",
    response_model=PosicionRankingResponse,
    summary="Obtener mi posición en ranking",
    description="Obtiene la posición del usuario actual en el ranking global.",
    responses={
        200: {
            "description": "Posición obtenida exitosamente",
            "model": PosicionRankingResponse,
        },
        401: {"description": "No autenticado", "model": ErrorResponse},
        404: {
            "description": "Usuario no encontrado en ranking",
            "model": ErrorResponse,
        },
    },
)
async def obtener_mi_posicion(
    current_user: Usuario = Depends(get_current_user),
    service: PuntosService = Depends(get_puntos_service),
):
    """Obtener posición del usuario actual en el ranking.

    Retorna:
    - Posición actual
    - Puntos del usuario
    - Nivel
    - Puntos hasta posición anterior
    - Puntos hasta siguiente posición
    - Total de usuarios en ranking
    """
    try:
        resultado = await service.obtener_posicion_usuario(current_user.usuario_id)

        if not resultado:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario no encontrado en el ranking",
            )

        return resultado

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener posición: {e!s}",
        ) from e


@router.post(
    "/otorgar",
    response_model=OtorgarPuntosResponse,
    summary="Otorgar puntos a usuario",
    description="Permite a un administrador otorgar o quitar puntos a un usuario. Requiere rol de administrador.",
    dependencies=[Depends(require_admin())],
    responses={
        200: {
            "description": "Puntos otorgados exitosamente",
            "model": OtorgarPuntosResponse,
        },
        400: {"description": "Datos inválidos", "model": ErrorResponse},
        401: {"description": "No autenticado", "model": ErrorResponse},
        403: {"description": "Sin permisos (requiere admin)", "model": ErrorResponse},
        404: {"description": "Usuario no encontrado", "model": ErrorResponse},
    },
)
async def otorgar_puntos(
    request: OtorgarPuntosRequest,
    current_admin: Usuario = Depends(require_admin()),
    service: PuntosService = Depends(get_puntos_service),
):
    """Otorgar o quitar puntos a un usuario (solo administradores).

    Body:
    - `usuario_id`: UUID del usuario
    - `puntos`: Cantidad (positivo = otorgar, negativo = quitar)
    - `motivo`: Razón del cambio (5-500 caracteres)

    Retorna confirmación con:
    - Puntos otorgados
    - Puntos anteriores y nuevos
    - Nuevas insignias obtenidas (si aplica)
    - Nivel actual
    """
    try:
        resultado = await service.otorgar_puntos(
            usuario_id=request.usuario_id, puntos=request.puntos, motivo=request.motivo
        )

        if not resultado:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado"
            )

        mensaje = f"{'Otorgados' if request.puntos > 0 else 'Descontados'} {abs(request.puntos)} puntos"

        return OtorgarPuntosResponse(success=True, message=mensaje, **resultado)

    except HTTPException:
        raise
    except ValueError as e:
        error_msg = str(e)
        # If the error is about user not found, return 404
        if "no encontrado" in error_msg.lower() or "not found" in error_msg.lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=error_msg
            ) from e
        # Otherwise, it's a validation error, return 400
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=error_msg
        ) from e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al otorgar puntos: {e!s}",
        ) from e


@router.get(
    "/historial",
    response_model=dict,
    summary="Obtener historial de puntos",
    description="Obtiene el historial completo de movimientos de puntos del usuario.",
    responses={
        200: {"description": "Historial obtenido exitosamente"},
        401: {"description": "No autenticado", "model": ErrorResponse},
    },
)
async def obtener_historial(
    limit: int = Query(50, ge=1, le=200, description="Cantidad de resultados"),
    offset: int = Query(0, ge=0, description="Desplazamiento para paginación"),
    current_user: Usuario = Depends(get_current_user),
    service: PuntosService = Depends(get_puntos_service),
):
    """Obtener historial completo de puntos del usuario.

    Retorna lista paginada de todos los movimientos de puntos:
    - Fecha y hora
    - Cambio (positivo o negativo)
    - Motivo
    - Balance resultante
    """
    try:
        resultado = await service.obtener_historial_puntos(
            usuario_id=current_user.usuario_id, limit=limit, offset=offset
        )

        return {
            "success": True,
            "historial": resultado["historial"],
            "total": resultado["total"],
            "limit": limit,
            "offset": offset,
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener historial: {e!s}",
        ) from e


@router.get(
    "/nivel/info",
    response_model=dict,
    summary="Información de niveles",
    description="Obtiene información sobre el sistema de niveles y umbrales.",
    responses={
        200: {"description": "Información obtenida exitosamente"},
        401: {"description": "No autenticado", "model": ErrorResponse},
    },
)
async def obtener_info_niveles(
    current_user: Usuario = Depends(get_current_user),
    service: PuntosService = Depends(get_puntos_service),
):
    """Obtener información del sistema de niveles.

    Retorna:
    - Lista de todos los niveles
    - Puntos requeridos para cada nivel
    - Nivel actual del usuario
    - Progreso hacia siguiente nivel
    """
    try:
        resultado = await service.obtener_info_niveles()

        return {
            "success": True,
            "niveles": resultado["niveles"],
            "nivel_actual": resultado.get("nivel_usuario"),
            "progreso": resultado.get("progreso"),
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener información de niveles: {e!s}",
        ) from e
