"""API Endpoints para el sistema de Tienda e Inventario.

Endpoints:
- GET /catalogo - Obtener catálogo de items
- POST /comprar - Comprar item
- GET /inventario - Obtener inventario del usuario
- POST /equipar/{inventario_id} - Equipar item
- POST /desequipar/{inventario_id} - Desequipar item
- POST /usar/{inventario_id} - Usar item consumible
- GET /transacciones - Historial de transacciones
- GET /estadisticas - Estadísticas de la tienda

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
    CatalogoTiendaResponse,
    CategoriaItem,
    CompraRequest,
    CompraResponse,
    EquiparItemResponse,
    ErrorResponse,
    EstadisticasTiendaResponse,
    HistorialTransaccionesResponse,
    InventarioResponse,
    RarezaItem,
    TipoItem,
    UsarItemResponse,
)
from src.services.gamification.tienda_service import TiendaService


router = APIRouter()


def get_tienda_service(db: Session = Depends(get_db)) -> TiendaService:
    """Dependency para obtener TiendaService."""
    return TiendaService(db)


@router.get(
    "/catalogo",
    response_model=CatalogoTiendaResponse,
    summary="Obtener catálogo de la tienda",
    description="Obtiene el catálogo completo de items disponibles con filtros opcionales.",
    responses={
        200: {
            "description": "Catálogo obtenido exitosamente",
            "model": CatalogoTiendaResponse,
        },
        401: {"description": "No autenticado", "model": ErrorResponse},
    },
)
async def obtener_catalogo(
    limit: int = Query(50, ge=1, le=200, description="Cantidad de resultados"),
    offset: int = Query(0, ge=0, description="Desplazamiento para paginación"),
    categoria: CategoriaItem | None = Query(None, description="Filtrar por categoría"),
    tipo: TipoItem | None = Query(None, description="Filtrar por tipo"),
    rareza: RarezaItem | None = Query(None, description="Filtrar por rareza"),
    solo_nuevos: bool = Query(False, description="Solo items nuevos"),
    solo_destacados: bool = Query(False, description="Solo items destacados"),
    precio_min: int | None = Query(None, ge=0, description="Precio mínimo"),
    precio_max: int | None = Query(None, ge=0, description="Precio máximo"),
    buscar: str | None = Query(
        None, min_length=2, max_length=50, description="Buscar por nombre"
    ),
    current_user: Usuario = Depends(get_current_user),
    service: TiendaService = Depends(get_tienda_service),
):
    """Obtener catálogo de la tienda con filtros.

    Filtros disponibles:
    - `categoria`: Avatar, cosmético, consumible, etc.
    - `tipo`: Avatar, cosmetic, consumible, permanente, temporal
    - `rareza`: Común, raro, épico, legendario
    - `solo_nuevos`: Items agregados recientemente
    - `solo_destacados`: Items destacados
    - `precio_min/max`: Rango de precios
    - `buscar`: Buscar por nombre
    - `limit/offset`: Paginación

    Retorna lista con:
    - Info completa del item
    - Precio (con descuento si aplica)
    - Disponibilidad y stock
    - Badges (nuevo, destacado, limitado)
    """
    try:
        resultado = await service.obtener_catalogo(
            limit=limit,
            offset=offset,
            categoria=categoria.value if categoria else None,
            tipo=tipo.value if tipo else None,
            rareza=rareza.value if rareza else None,
            solo_nuevos=solo_nuevos,
            solo_destacados=solo_destacados,
            precio_min=precio_min,
            precio_max=precio_max,
            buscar=buscar,
        )

        filtros = {}
        if categoria:
            filtros["categoria"] = categoria.value
        if tipo:
            filtros["tipo"] = tipo.value
        if rareza:
            filtros["rareza"] = rareza.value
        if solo_nuevos:
            filtros["solo_nuevos"] = True
        if solo_destacados:
            filtros["solo_destacados"] = True
        if precio_min is not None:
            filtros["precio_min"] = precio_min
        if precio_max is not None:
            filtros["precio_max"] = precio_max
        if buscar:
            filtros["buscar"] = buscar

        return CatalogoTiendaResponse(
            items=resultado["items"],
            total=resultado["total"],
            filtros_aplicados=filtros,
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener catálogo: {e!s}",
        ) from e


@router.post(
    "/comprar",
    response_model=CompraResponse,
    summary="Comprar item",
    description="Compra uno o más items de la tienda usando puntos acumulados.",
    responses={
        200: {"description": "Item comprado exitosamente", "model": CompraResponse},
        400: {
            "description": "Puntos insuficientes o datos inválidos",
            "model": ErrorResponse,
        },
        401: {"description": "No autenticado", "model": ErrorResponse},
        404: {"description": "Item no encontrado", "model": ErrorResponse},
        409: {"description": "Stock insuficiente", "model": ErrorResponse},
    },
)
async def comprar_item(
    request: CompraRequest,
    current_user: Usuario = Depends(get_current_user),
    service: TiendaService = Depends(get_tienda_service),
):
    """Comprar un item de la tienda.

    Body:
    - `item_id`: UUID del item
    - `cantidad`: Cantidad a comprar (1-99, default 1)

    Requisitos:
    - Item debe estar disponible
    - Usuario debe tener puntos suficientes
    - Stock debe ser suficiente (si es limitado)

    Retorna:
    - Información del item comprado
    - ID de transacción
    - Puntos gastados y restantes
    - ID del item en inventario
    """
    try:
        resultado = await service.comprar_item(
            usuario_id=current_user.id,
            item_id=request.item_id,
            cantidad=request.cantidad,
        )

        if resultado.get("error"):
            error_msg = resultado["error"]
            if "no encontrado" in error_msg:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail=error_msg
                )
            if "stock" in error_msg.lower():
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT, detail=error_msg
                )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=error_msg
            )

        return CompraResponse(
            success=True,
            message=f"¡Compraste {resultado['item']['nombre']}!",
            transaccion_id=resultado["transaccion_id"],
            item=resultado["item"],
            cantidad=resultado["cantidad"],
            puntos_gastados=resultado["puntos_gastados"],
            puntos_restantes=resultado["puntos_restantes"],
            inventario_id=resultado["inventario_id"],
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al comprar item: {e!s}",
        ) from e


@router.get(
    "/inventario",
    response_model=InventarioResponse,
    summary="Obtener inventario",
    description="Obtiene todos los items en el inventario del usuario.",
    responses={
        200: {
            "description": "Inventario obtenido exitosamente",
            "model": InventarioResponse,
        },
        401: {"description": "No autenticado", "model": ErrorResponse},
    },
)
async def obtener_inventario(
    categoria: CategoriaItem | None = Query(None, description="Filtrar por categoría"),
    tipo: TipoItem | None = Query(None, description="Filtrar por tipo"),
    equipados_solo: bool = Query(False, description="Solo items equipados"),
    current_user: Usuario = Depends(get_current_user),
    service: TiendaService = Depends(get_tienda_service),
):
    """Obtener inventario del usuario.

    Filtros:
    - `categoria`: Filtrar por categoría
    - `tipo`: Filtrar por tipo
    - `equipados_solo`: Solo mostrar equipados

    Retorna lista con:
    - Info completa del item
    - Cantidad disponible
    - Estado de equipamiento
    - Fecha de adquisición
    - Método de obtención
    - Veces usado
    - Disponibilidad para usar
    """
    try:
        resultado = await service.obtener_inventario(
            usuario_id=current_user.id,
            categoria=categoria.value if categoria else None,
            tipo=tipo.value if tipo else None,
            equipados_solo=equipados_solo,
        )

        return InventarioResponse(
            items=resultado["items"],
            total=resultado["total"],
            equipados=resultado["equipados"],
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener inventario: {e!s}",
        ) from e


@router.post(
    "/equipar/{inventario_id}",
    response_model=EquiparItemResponse,
    summary="Equipar item",
    description="Equipa un item del inventario (avatar, cosmético, etc.).",
    responses={
        200: {
            "description": "Item equipado exitosamente",
            "model": EquiparItemResponse,
        },
        400: {"description": "Item no equipable", "model": ErrorResponse},
        401: {"description": "No autenticado", "model": ErrorResponse},
        404: {
            "description": "Item no encontrado en inventario",
            "model": ErrorResponse,
        },
    },
)
async def equipar_item(
    inventario_id: UUID,
    current_user: Usuario = Depends(get_current_user),
    service: TiendaService = Depends(get_tienda_service),
):
    """Equipar un item del inventario.

    - Items de avatar reemplazan el item equipado en esa categoría
    - Items cosméticos se aplican al perfil
    - Solo un item por categoría puede estar equipado

    Si ya hay un item equipado en esa categoría, se desequipa automáticamente.
    """
    try:
        resultado = await service.equipar_item(
            usuario_id=current_user.id, inventario_id=inventario_id
        )

        if resultado.get("error"):
            if "no encontrado" in resultado["error"]:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail=resultado["error"]
                )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=resultado["error"]
            )

        return EquiparItemResponse(
            success=True,
            message=f"¡{resultado['item_equipado']} equipado!",
            item_equipado=resultado["item_equipado"],
            categoria=resultado["categoria"],
            item_desequipado=resultado.get("item_desequipado"),
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al equipar item: {e!s}",
        ) from e


@router.post(
    "/desequipar/{inventario_id}",
    response_model=BaseResponse,
    summary="Desequipar item",
    description="Desequipa un item específico.",
    responses={
        200: {"description": "Item desequipado exitosamente", "model": BaseResponse},
        401: {"description": "No autenticado", "model": ErrorResponse},
        404: {"description": "Item no encontrado", "model": ErrorResponse},
    },
)
async def desequipar_item(
    inventario_id: UUID,
    current_user: Usuario = Depends(get_current_user),
    service: TiendaService = Depends(get_tienda_service),
):
    """Desequipar un item específico.

    El item permanece en el inventario pero deja de estar equipado.
    """
    try:
        resultado = await service.desequipar_item(
            usuario_id=current_user.id, inventario_id=inventario_id
        )

        if resultado.get("error"):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=resultado["error"]
            )

        return BaseResponse(success=True, message="¡Item desequipado!")

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al desequipar item: {e!s}",
        ) from e


@router.post(
    "/usar/{inventario_id}",
    response_model=UsarItemResponse,
    summary="Usar item consumible",
    description="Usa un item consumible del inventario (protección racha, multiplicador, etc.).",
    responses={
        200: {"description": "Item usado exitosamente", "model": UsarItemResponse},
        400: {
            "description": "Item no usable o cantidad insuficiente",
            "model": ErrorResponse,
        },
        401: {"description": "No autenticado", "model": ErrorResponse},
        404: {"description": "Item no encontrado", "model": ErrorResponse},
    },
)
async def usar_item(
    inventario_id: UUID,
    current_user: Usuario = Depends(get_current_user),
    service: TiendaService = Depends(get_tienda_service),
):
    """Usar un item consumible.

    Items consumibles incluyen:
    - Protección de racha
    - Multiplicadores de puntos
    - Boosts de experiencia
    - Desbloqueadores de contenido

    Al usar:
    - Se aplica el efecto
    - Se reduce la cantidad (o se elimina si es único)
    - Se registra el uso

    Retorna:
    - Confirmación de uso
    - Efecto aplicado
    - Cantidad restante
    """
    try:
        resultado = await service.usar_item(
            usuario_id=current_user.id, inventario_id=inventario_id
        )

        if resultado.get("error"):
            if "no encontrado" in resultado["error"]:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail=resultado["error"]
                )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=resultado["error"]
            )

        return UsarItemResponse(
            success=True,
            message=resultado["mensaje"],
            item_usado=resultado["item_usado"],
            efecto=resultado["efecto"],
            cantidad_restante=resultado["cantidad_restante"],
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al usar item: {e!s}",
        ) from e


@router.get(
    "/transacciones",
    response_model=HistorialTransaccionesResponse,
    summary="Historial de transacciones",
    description="Obtiene el historial completo de transacciones de la tienda.",
    responses={
        200: {
            "description": "Historial obtenido exitosamente",
            "model": HistorialTransaccionesResponse,
        },
        401: {"description": "No autenticado", "model": ErrorResponse},
    },
)
async def obtener_transacciones(
    limit: int = Query(50, ge=1, le=200, description="Cantidad de resultados"),
    offset: int = Query(0, ge=0, description="Desplazamiento para paginación"),
    solo_exitosas: bool | None = Query(None, description="Filtrar por estado"),
    current_user: Usuario = Depends(get_current_user),
    service: TiendaService = Depends(get_tienda_service),
):
    """Obtener historial de transacciones.

    Parámetros:
    - `limit/offset`: Paginación
    - `solo_exitosas`: True = solo exitosas, False = solo fallidas, None = todas

    Retorna lista con:
    - ID de transacción
    - Tipo (compra, uso)
    - Item involucrado
    - Cantidad
    - Puntos
    - Estado (exitosa/fallida)
    - Fecha
    - Razón de fallo (si aplica)
    """
    try:
        resultado = await service.obtener_historial_transacciones(
            usuario_id=current_user.id,
            limit=limit,
            offset=offset,
            solo_exitosas=solo_exitosas,
        )

        return HistorialTransaccionesResponse(
            transacciones=resultado["transacciones"], total=resultado["total"]
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener transacciones: {e!s}",
        ) from e


@router.get(
    "/estadisticas",
    response_model=EstadisticasTiendaResponse,
    summary="Estadísticas de la tienda",
    description="Obtiene estadísticas sobre compras y uso de la tienda.",
    responses={
        200: {
            "description": "Estadísticas obtenidas exitosamente",
            "model": EstadisticasTiendaResponse,
        },
        401: {"description": "No autenticado", "model": ErrorResponse},
    },
)
async def obtener_estadisticas(
    current_user: Usuario = Depends(get_current_user),
    service: TiendaService = Depends(get_tienda_service),
):
    """Obtener estadísticas de la tienda.

    Retorna:
    - Total de items en inventario
    - Items equipados actualmente
    - Total de puntos gastados
    - Transacciones exitosas/fallidas
    - Distribución por categoría
    - Distribución por rareza
    """
    try:
        resultado = await service.obtener_estadisticas(usuario_id=current_user.id)

        return EstadisticasTiendaResponse(**resultado)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener estadísticas: {e!s}",
        ) from e
