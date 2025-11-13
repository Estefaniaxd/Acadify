"""
API endpoints para el sistema de tienda virtual.

Endpoints disponibles:
- GET /items - Catálogo de items
- GET /items/{item_id} - Detalle de item
- POST /comprar - Comprar item
- GET /inventario - Ver inventario propio
- POST /equipar - Equipar item
- POST /usar - Usar item consumible
- GET /transacciones - Historial de transacciones
- GET /estadisticas - Estadísticas de compras
"""

from typing import Optional, List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.core.security import get_current_user
from src.models.users.usuario import Usuario
from src.services.gamification.tienda_service import TiendaService
from src.schemas.gamification.tienda import (
    TiendaItemResponse,
    TiendaItemDetalle,
    ComprarItemRequest,
    CompraResponse,
    EquiparItemRequest,
    UsarItemRequest,
    InventarioResponse,
    InventarioDetalleResponse,
    TransaccionTiendaResponse,
    CatalogoResponse,
    EstadisticasTiendaResponse,
)
from src.enums.gamification import CategoriaItem, RarezaItem

router = APIRouter(prefix="/tienda", tags=["Tienda Virtual"])


# =============================================================================
# CATÁLOGO DE ITEMS
# =============================================================================

@router.get("/items", response_model=CatalogoResponse)
async def get_catalogo_items(
    categoria: Optional[CategoriaItem] = None,
    rareza: Optional[RarezaItem] = None,
    precio_min: Optional[int] = Query(None, ge=0),
    precio_max: Optional[int] = Query(None, ge=0),
    solo_disponibles: bool = True,
    busqueda: Optional[str] = None,
    pagina: int = Query(1, ge=1),
    items_por_pagina: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """
    Obtener catálogo de items de la tienda.
    
    Filtros disponibles:
    - categoria: Filtrar por categoría (CABELLO, ROPA_SUPERIOR, etc.)
    - rareza: Filtrar por rareza (COMUN, RARO, EPICO, LEGENDARIO)
    - precio_min/precio_max: Rango de precios
    - solo_disponibles: Solo items activos y disponibles
    - busqueda: Buscar por nombre o descripción
    - pagina: Número de página
    - items_por_pagina: Items por página (máx 100)
    """
    service = TiendaService(db)
    
    items = await service.get_catalogo_items(
        categoria=categoria,
        rareza=rareza,
        precio_min=precio_min,
        precio_max=precio_max,
        solo_disponibles=solo_disponibles,
        busqueda=busqueda,
        nivel_usuario=current_user.nivel if hasattr(current_user, 'nivel') else 1,
        pagina=pagina,
        items_por_pagina=items_por_pagina,
    )
    
    return items


@router.get("/items/{item_id}", response_model=TiendaItemDetalle)
async def get_item_detalle(
    item_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """
    Obtener detalle de un item específico.
    
    Incluye:
    - Información completa del item
    - URL del asset si existe
    - Estadísticas (total compras, usuarios con item)
    """
    service = TiendaService(db)
    
    item = await service.get_item_detalle(item_id)
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item no encontrado"
        )
    
    return item


# =============================================================================
# COMPRAS
# =============================================================================

@router.post("/comprar", response_model=CompraResponse)
async def comprar_item(
    request: ComprarItemRequest,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """
    Comprar un item de la tienda.
    
    Validaciones:
    - Usuario tiene puntos suficientes
    - Item está disponible
    - Item tiene stock (si es limitado)
    - Usuario cumple nivel mínimo
    
    Acciones:
    - Deduce puntos del usuario
    - Agrega item al inventario
    - Reduce stock (si aplica)
    - Registra transacción
    """
    service = TiendaService(db)
    
    try:
        result = await service.comprar_item(
            usuario_id=current_user.usuario_id,
            item_id=request.item_id,
            cantidad=request.cantidad,
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
            detail=f"Error al comprar item: {str(e)}"
        )


# =============================================================================
# INVENTARIO
# =============================================================================

@router.get("/inventario", response_model=InventarioResponse)
async def get_mi_inventario(
    categoria: Optional[CategoriaItem] = None,
    solo_equipados: bool = False,
    solo_consumibles: bool = False,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """
    Obtener inventario del usuario actual.
    
    Filtros:
    - categoria: Filtrar por categoría de item
    - solo_equipados: Solo items equipados
    - solo_consumibles: Solo items con cantidad > 1
    """
    service = TiendaService(db)
    
    inventario = await service.get_inventario_usuario(
        usuario_id=current_user.usuario_id,
        categoria=categoria,
        solo_equipados=solo_equipados,
        solo_consumibles=solo_consumibles,
    )
    
    return inventario


@router.get("/inventario/{inventario_id}", response_model=InventarioDetalleResponse)
async def get_item_inventario(
    inventario_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """
    Obtener detalle de un item específico del inventario.
    """
    service = TiendaService(db)
    
    item = await service.get_item_inventario_detalle(
        inventario_id=inventario_id,
        usuario_id=current_user.usuario_id,
    )
    
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item no encontrado en tu inventario"
        )
    
    return item


# =============================================================================
# EQUIPAMIENTO
# =============================================================================

@router.post("/equipar")
async def equipar_item(
    request: EquiparItemRequest,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """
    Equipar un item del inventario.
    
    Solo se puede equipar un item de cada categoría visual.
    """
    service = TiendaService(db)
    
    try:
        result = await service.equipar_item(
            inventario_id=request.inventario_id,
            usuario_id=current_user.usuario_id,
        )
        return {
            "success": True,
            "message": "Item equipado exitosamente",
            "item": result
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/desequipar/{inventario_id}")
async def desequipar_item(
    inventario_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """
    Desequipar un item del inventario.
    """
    service = TiendaService(db)
    
    try:
        result = await service.desequipar_item(
            inventario_id=inventario_id,
            usuario_id=current_user.usuario_id,
        )
        return {
            "success": True,
            "message": "Item desequipado exitosamente",
            "item": result
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


# =============================================================================
# ITEMS CONSUMIBLES
# =============================================================================

@router.post("/usar")
async def usar_item_consumible(
    request: UsarItemRequest,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """
    Usar un item consumible del inventario.
    
    Reduce la cantidad del item. Si llega a 0, se elimina del inventario.
    """
    service = TiendaService(db)
    
    try:
        result = await service.usar_item_consumible(
            inventario_id=request.inventario_id,
            usuario_id=current_user.usuario_id,
            cantidad=request.cantidad,
        )
        return {
            "success": True,
            "message": f"Item usado {request.cantidad} vez/veces",
            "item": result,
            "cantidad_restante": result.cantidad if result else 0
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


# =============================================================================
# TRANSACCIONES
# =============================================================================

@router.get("/transacciones", response_model=List[TransaccionTiendaResponse])
async def get_mis_transacciones(
    solo_exitosas: bool = True,
    limite: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """
    Obtener historial de transacciones del usuario.
    
    Parámetros:
    - solo_exitosas: Solo transacciones exitosas (default: true)
    - limite: Máximo de transacciones a retornar
    - offset: Offset para paginación
    """
    service = TiendaService(db)
    
    transacciones = await service.get_transacciones_usuario(
        usuario_id=current_user.usuario_id,
        solo_exitosas=solo_exitosas,
        limite=limite,
        offset=offset,
    )
    
    return transacciones


# =============================================================================
# ESTADÍSTICAS
# =============================================================================

@router.get("/estadisticas", response_model=EstadisticasTiendaResponse)
async def get_mis_estadisticas(
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """
    Obtener estadísticas de compras del usuario.
    
    Incluye:
    - Total de compras y puntos gastados
    - Items únicos adquiridos
    - Distribución por rareza y categoría
    - Item más caro comprado
    - Última compra
    """
    service = TiendaService(db)
    
    estadisticas = await service.get_estadisticas_usuario(
        usuario_id=current_user.usuario_id
    )
    
    return estadisticas
