"""
API endpoints para el sistema de etiquetas de perfil.

Endpoints disponibles:
- GET /disponibles - Etiquetas disponibles para compra/logro
- GET /mis-etiquetas - Etiquetas del usuario
- POST /comprar - Comprar etiqueta
- POST /equipar - Equipar hasta 5 etiquetas
- POST /evolucionar - Evolucionar etiqueta
- GET /progreso/{etiqueta_id} - Ver progreso de evolución
"""

from typing import Optional, List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.core.security import get_current_user
from src.models.users.usuario import Usuario
from src.services.gamification.etiquetas_service import EtiquetasService
from src.schemas.gamification.etiquetas import (
    EtiquetaPerfilResponse,
    EtiquetaPerfilDetalle,
    ComprarEtiquetaRequest,
    CompraEtiquetaResponse,
    EquiparEtiquetasRequest,
    EquipamientoResponse,
    EvolucionarEtiquetaRequest,
    EvolucionResponse,
    UsuarioEtiquetaResponse,
    UsuarioEtiquetaDetalle,
    CatalogoEtiquetasResponse,
    MisEtiquetasResponse,
    ProgresoEvolucionResponse,
)
from src.enums.gamification import CategoriaEtiqueta, RarezaEtiqueta

router = APIRouter(prefix="/etiquetas", tags=["Etiquetas de Perfil"])


# =============================================================================
# CATÁLOGO DE ETIQUETAS
# =============================================================================

@router.get("/disponibles", response_model=CatalogoEtiquetasResponse)
async def get_etiquetas_disponibles(
    categoria: Optional[CategoriaEtiqueta] = None,
    rareza: Optional[RarezaEtiqueta] = None,
    solo_comprables: bool = True,
    busqueda: Optional[str] = None,
    pagina: int = Query(1, ge=1),
    items_por_pagina: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """
    Obtener catálogo de etiquetas disponibles.
    
    Filtros:
    - categoria: MATEMATICAS, CIENCIAS, PROGRAMACION, etc.
    - rareza: COMUN, RARO, EPICO, LEGENDARIO
    - solo_comprables: Solo etiquetas que se pueden comprar con puntos
    - busqueda: Buscar por nombre o descripción
    """
    service = EtiquetasService(db)
    
    catalogo = await service.get_catalogo_etiquetas(
        categoria=categoria,
        rareza=rareza,
        solo_comprables=solo_comprables,
        solo_activas=True,
        busqueda=busqueda,
        pagina=pagina,
        items_por_pagina=items_por_pagina,
    )
    
    return catalogo


@router.get("/disponibles/{etiqueta_id}", response_model=EtiquetaPerfilDetalle)
async def get_etiqueta_detalle(
    etiqueta_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """
    Obtener detalle de una etiqueta específica.
    
    Incluye:
    - Información completa
    - Cadena de evolución
    - Requisitos
    - Total de usuarios que la tienen
    """
    service = EtiquetasService(db)
    
    etiqueta = await service.get_etiqueta_detalle(etiqueta_id)
    if not etiqueta:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Etiqueta no encontrada"
        )
    
    return etiqueta


# =============================================================================
# MIS ETIQUETAS
# =============================================================================

@router.get("/mis-etiquetas", response_model=MisEtiquetasResponse)
async def get_mis_etiquetas(
    categoria: Optional[CategoriaEtiqueta] = None,
    rareza: Optional[RarezaEtiqueta] = None,
    solo_equipadas: bool = False,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """
    Obtener todas las etiquetas del usuario actual.
    
    Filtros:
    - categoria: Filtrar por categoría
    - rareza: Filtrar por rareza
    - solo_equipadas: Solo etiquetas actualmente equipadas
    
    Incluye estadísticas agregadas.
    """
    service = EtiquetasService(db)
    
    etiquetas = await service.get_etiquetas_usuario(
        usuario_id=current_user.usuario_id,
        categoria=categoria,
        rareza=rareza,
        solo_equipadas=solo_equipadas,
    )
    
    return etiquetas


@router.get("/mis-etiquetas/equipadas", response_model=List[UsuarioEtiquetaResponse])
async def get_etiquetas_equipadas(
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """
    Obtener solo las etiquetas equipadas (visibles en el perfil).
    
    Retorna en orden de visualización (1-5).
    """
    service = EtiquetasService(db)
    
    equipadas = await service.get_etiquetas_equipadas(
        usuario_id=current_user.usuario_id
    )
    
    return equipadas


# =============================================================================
# COMPRAS
# =============================================================================

@router.post("/comprar", response_model=CompraEtiquetaResponse)
async def comprar_etiqueta(
    request: ComprarEtiquetaRequest,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """
    Comprar una etiqueta con puntos.
    
    Validaciones:
    - Etiqueta es comprable
    - Usuario tiene puntos suficientes
    - Usuario no tiene ya la etiqueta
    
    Acciones:
    - Deduce puntos
    - Agrega etiqueta al usuario
    """
    service = EtiquetasService(db)
    
    try:
        result = await service.comprar_etiqueta(
            usuario_id=current_user.usuario_id,
            etiqueta_id=request.etiqueta_id,
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
            detail=f"Error al comprar etiqueta: {str(e)}"
        )


# =============================================================================
# EQUIPAMIENTO
# =============================================================================

@router.post("/equipar", response_model=EquipamientoResponse)
async def equipar_etiquetas(
    request: EquiparEtiquetasRequest,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """
    Equipar hasta 5 etiquetas en el perfil.
    
    El orden del array determina el orden de visualización (1-5).
    
    Validaciones:
    - Máximo 5 etiquetas
    - Usuario posee todas las etiquetas
    - Sin duplicados
    
    Ejemplo:
    ```json
    {
        "etiquetas": [
            "uuid-etiqueta-1",  // Orden 1
            "uuid-etiqueta-2",  // Orden 2
            "uuid-etiqueta-3"   // Orden 3
        ]
    }
    ```
    """
    service = EtiquetasService(db)
    
    try:
        result = await service.equipar_etiquetas(
            usuario_id=current_user.usuario_id,
            etiquetas_ids=request.etiquetas,
        )
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/desequipar/{usuario_etiqueta_id}")
async def desequipar_etiqueta(
    usuario_etiqueta_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """
    Desequipar una etiqueta específica.
    
    La etiqueta permanece en el inventario pero no se muestra en el perfil.
    """
    service = EtiquetasService(db)
    
    try:
        result = await service.desequipar_etiqueta(
            usuario_etiqueta_id=usuario_etiqueta_id,
            usuario_id=current_user.usuario_id,
        )
        return {
            "success": True,
            "message": "Etiqueta desequipada exitosamente",
            "etiqueta": result
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


# =============================================================================
# EVOLUCIÓN
# =============================================================================

@router.get("/progreso/{usuario_etiqueta_id}", response_model=ProgresoEvolucionResponse)
async def get_progreso_evolucion(
    usuario_etiqueta_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """
    Ver progreso de evolución de una etiqueta.
    
    Muestra:
    - Etiqueta actual y evolución disponible
    - Requisitos necesarios
    - Progreso de cada requisito
    - Si puede evolucionar ahora
    """
    service = EtiquetasService(db)
    
    progreso = await service.get_progreso_evolucion(
        usuario_etiqueta_id=usuario_etiqueta_id,
        usuario_id=current_user.usuario_id,
    )
    
    if not progreso:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Etiqueta no encontrada o sin evolución disponible"
        )
    
    return progreso


@router.post("/evolucionar", response_model=EvolucionResponse)
async def evolucionar_etiqueta(
    request: EvolucionarEtiquetaRequest,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """
    Evolucionar una etiqueta a su siguiente nivel.
    
    Validaciones:
    - Etiqueta tiene evolución disponible
    - Usuario cumple todos los requisitos
    
    Acciones:
    - Reemplaza etiqueta actual por evolución
    - Mantiene fecha de obtención original
    - Reinicia progreso de evolución
    - Marca como nueva etiqueta si estaba equipada
    """
    service = EtiquetasService(db)
    
    try:
        result = await service.evolucionar_etiqueta(
            usuario_etiqueta_id=request.usuario_etiqueta_id,
            usuario_id=current_user.usuario_id,
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
            detail=f"Error al evolucionar etiqueta: {str(e)}"
        )


# =============================================================================
# ESTADÍSTICAS Y RANKINGS
# =============================================================================

@router.get("/top-usuarios/{etiqueta_id}")
async def get_top_usuarios_etiqueta(
    etiqueta_id: UUID,
    limite: int = Query(10, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """
    Obtener usuarios con una etiqueta específica.
    
    Útil para ver quién más tiene etiquetas raras o logros especiales.
    """
    service = EtiquetasService(db)
    
    usuarios = await service.get_usuarios_con_etiqueta(
        etiqueta_id=etiqueta_id,
        limite=limite,
    )
    
    return {
        "etiqueta_id": etiqueta_id,
        "usuarios": usuarios,
        "total": len(usuarios)
    }


@router.get("/estadisticas-categoria/{categoria}")
async def get_estadisticas_categoria(
    categoria: CategoriaEtiqueta,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """
    Estadísticas de etiquetas por categoría del usuario.
    
    Muestra progreso en categorías como:
    - MATEMATICAS, CIENCIAS, PROGRAMACION, etc.
    """
    service = EtiquetasService(db)
    
    stats = await service.get_estadisticas_categoria(
        usuario_id=current_user.usuario_id,
        categoria=categoria,
    )
    
    return stats
