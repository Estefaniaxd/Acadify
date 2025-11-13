"""
API endpoints para el sistema de rachas estilo Duolingo.

Endpoints disponibles:
- GET /mi-racha - Ver racha actual completa
- POST /verificar - Verificar racha diaria
- POST /recuperar - Recuperar racha perdida
- POST /congelar - Activar congelador
- GET /historial - Ver historial de eventos
- GET /milestones - Ver milestones disponibles
- GET /estadisticas - Estadísticas completas
"""

from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.core.security import get_current_user
from src.models.users.usuario import Usuario
from src.services.gamification.racha_service import RachaService
from src.schemas.gamification.rachas import (
    RachaUsuarioResponse,
    VerificarRachaRequest,
    VerificarRachaResponse,
    RecuperarRachaRequest,
    RecuperarRachaResponse,
    ActivarCongeladorRequest,
    ActivarCongeladorResponse,
    HistorialRachaListResponse,
    MilestonesResponse,
    EstadisticasRachaResponse,
)

router = APIRouter(prefix="/rachas", tags=["Rachas"])


# =============================================================================
# MI RACHA
# =============================================================================

@router.get("/mi-racha", response_model=RachaUsuarioResponse)
async def get_mi_racha(
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """
    Obtener racha actual del usuario.
    
    Incluye:
    - Racha actual y mejor racha
    - Estado de protección (congelador activo)
    - Recuperaciones disponibles
    - Puntos del día actual
    - Próximo milestone
    """
    service = RachaService(db)
    
    racha = await service.get_racha_usuario(current_user.usuario_id)
    
    if not racha:
        # Crear racha nueva si no existe
        racha = await service.crear_racha_usuario(current_user.usuario_id)
    
    return racha


# =============================================================================
# VERIFICACIÓN DIARIA
# =============================================================================

@router.post("/verificar", response_model=VerificarRachaResponse)
async def verificar_racha_diaria(
    request: VerificarRachaRequest,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """
    Verificar y actualizar racha diaria del usuario.
    
    Llama a este endpoint cuando el usuario complete una actividad (tarea, examen, etc.)
    
    Lógica:
    - Si es el mismo día: No hace nada
    - Si es día consecutivo: Incrementa racha y otorga puntos
    - Si pasó más de 1 día SIN protección: Resetea a 1
    - Si pasó 1 día CON protección: Consume congelador y mantiene racha
    
    Otorga:
    - Puntos según día de semana (ciclo de 7 días, 10-50 puntos)
    - Puntos extra en milestones (7, 30, 100, 365 días)
    - Insignias en milestones especiales
    """
    service = RachaService(db)
    
    try:
        result = await service.verificar_racha_diaria(
            usuario_id=current_user.usuario_id,
            tipo_actividad=request.tipo_actividad,
            actividad_id=request.actividad_id,
            metadata=request.metadata,
        )
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al verificar racha: {str(e)}"
        )


# =============================================================================
# RECUPERACIÓN DE RACHA
# =============================================================================

@router.post("/recuperar", response_model=RecuperarRachaResponse)
async def recuperar_racha(
    request: RecuperarRachaRequest,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """
    Recuperar racha perdida usando un item de recuperación.
    
    Requisitos:
    - Usuario tiene recuperaciones disponibles (recuperaciones_disponibles > 0)
    - Racha se perdió recientemente (puede recuperar la última racha del historial)
    
    Acciones:
    - Restaura la racha anterior
    - Consume 1 recuperación
    - Registra evento en historial
    
    Nota: Las recuperaciones se obtienen como items de la tienda o por logros.
    """
    service = RachaService(db)
    
    try:
        result = await service.recuperar_racha(
            usuario_id=current_user.usuario_id
        )
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al recuperar racha: {str(e)}"
        )


# =============================================================================
# CONGELADOR DE RACHA
# =============================================================================

@router.post("/congelar", response_model=ActivarCongeladorResponse)
async def activar_congelador(
    request: ActivarCongeladorRequest,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """
    Activar congelador de racha por X días.
    
    Protege la racha de romperse si el usuario no completa actividades.
    
    Parámetros:
    - dias: Días de protección (1-7)
    
    Nota: Los congeladores se obtienen como items de la tienda.
    Este endpoint solo activa la protección, el item debe comprarse primero.
    """
    service = RachaService(db)
    
    try:
        result = await service.activar_congelador(
            usuario_id=current_user.usuario_id,
            dias=request.dias,
        )
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al activar congelador: {str(e)}"
        )


# =============================================================================
# HISTORIAL
# =============================================================================

@router.get("/historial", response_model=HistorialRachaListResponse)
async def get_historial_racha(
    tipo_evento: Optional[str] = None,
    limite: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """
    Obtener historial completo de eventos de racha.
    
    Filtros:
    - tipo_evento: INCREMENTO, PERDIDA, RECUPERACION, CONGELACION, MILESTONE, RECORD_PERSONAL
    - limite: Máximo de eventos a retornar
    - offset: Offset para paginación
    
    Cada evento incluye:
    - Racha anterior y nueva
    - Puntos otorgados
    - Tipo de evento
    - Descripción
    - Metadata adicional
    """
    service = RachaService(db)
    
    historial = await service.get_historial_racha(
        usuario_id=current_user.usuario_id,
        tipo_evento=tipo_evento,
        limite=limite,
        offset=offset,
    )
    
    return historial


# =============================================================================
# MILESTONES
# =============================================================================

@router.get("/milestones", response_model=MilestonesResponse)
async def get_milestones(
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """
    Obtener milestones de racha disponibles.
    
    Milestones típicos:
    - 7 días: "Primera Semana" - 100 puntos
    - 30 días: "Un Mes Consistente" - 500 puntos + insignia
    - 100 días: "Centenario" - 2000 puntos + insignia especial
    - 365 días: "Año Completo" - 10000 puntos + insignia legendaria
    
    Muestra:
    - Milestones completados
    - Próximo milestone por alcanzar
    - Días restantes
    """
    service = RachaService(db)
    
    milestones = await service.get_milestones_disponibles(
        usuario_id=current_user.usuario_id
    )
    
    return milestones


# =============================================================================
# ESTADÍSTICAS
# =============================================================================

@router.get("/estadisticas", response_model=EstadisticasRachaResponse)
async def get_estadisticas_racha(
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """
    Obtener estadísticas completas de racha.
    
    Incluye:
    - Total de días activos
    - Recuperaciones y congeladores usados
    - Milestones completados
    - Total de puntos ganados por rachas
    - Promedio de puntos por día
    - Record personal y fecha
    """
    service = RachaService(db)
    
    estadisticas = await service.get_estadisticas_racha(
        usuario_id=current_user.usuario_id
    )
    
    return estadisticas


# =============================================================================
# RANKINGS
# =============================================================================

@router.get("/ranking-global")
async def get_ranking_global(
    limite: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """
    Obtener ranking global de rachas.
    
    Ordena por:
    1. Racha actual (descendente)
    2. Mejor racha (descendente)
    
    Incluye posición del usuario actual.
    """
    service = RachaService(db)
    
    ranking = await service.get_ranking_global(limite=limite)
    
    # Encontrar posición del usuario actual
    posicion_usuario = None
    for idx, item in enumerate(ranking, 1):
        if item['usuario_id'] == current_user.usuario_id:
            posicion_usuario = idx
            break
    
    return {
        "ranking": ranking,
        "total": len(ranking),
        "mi_posicion": posicion_usuario,
    }


@router.get("/mi-posicion")
async def get_mi_posicion_ranking(
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """
    Obtener posición del usuario en el ranking de rachas.
    """
    service = RachaService(db)
    
    posicion = await service.get_posicion_usuario(current_user.usuario_id)
    
    return {
        "usuario_id": current_user.usuario_id,
        "posicion": posicion,
        "total_usuarios": await service.get_total_usuarios_con_racha(),
    }
