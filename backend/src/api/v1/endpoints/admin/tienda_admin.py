"""
API Endpoints para Panel de Administrador - Gestión de Tienda

Endpoints para que los administradores puedan:
- Crear items de tienda (ropa, accesorios, funcionales)
- Editar items existentes (precio, rareza, disponibilidad)
- Eliminar items
- Ver estadísticas de ventas
- Gestionar stock

Solo accesible para rol 'admin' o 'coordinador'
"""

from fastapi import APIRouter, Depends, HTTPException, Query, Body, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, desc
from typing import List, Optional
from uuid import UUID
from datetime import datetime

from src.api.deps import get_db, get_current_user
from src.models.users.usuario import Usuario
from src.models.gamification.tienda_item import TiendaItem
from src.models.gamification.transaccion_tienda import TransaccionTienda
from src.enums.gamification.tienda_enums import CategoriaItem, RarezaItem
from pydantic import BaseModel, Field
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/admin/tienda", tags=["Admin - Tienda"])


# ============================================
# SCHEMAS PYDANTIC
# ============================================

class CrearItemRequest(BaseModel):
    """Schema para crear un nuevo item de tienda"""
    nombre: str = Field(..., min_length=3, max_length=200, description="Nombre del item")
    descripcion: Optional[str] = Field(None, max_length=1000, description="Descripción detallada")
    categoria: CategoriaItem = Field(..., description="Categoría (CABELLO, ROPA, OJOS, etc.)")
    rareza: RarezaItem = Field(..., description="Rareza (COMUN, RARO, EPICO, LEGENDARIO)")
    
    # Precio (manual o basado en rareza)
    precio_puntos: Optional[int] = Field(None, ge=0, description="Precio manual en puntos")
    usar_precio_automatico: bool = Field(False, description="Calcular precio según rareza")
    
    # Requisitos
    nivel_minimo_requerido: int = Field(1, ge=1, le=100, description="Nivel mínimo para comprar")
    
    # Stock
    stock_limitado: bool = Field(False, description="Si tiene stock limitado")
    stock_disponible: Optional[int] = Field(None, ge=0, description="Cantidad en stock")
    
    # Consumible
    es_consumible: bool = Field(False, description="Si es item consumible (puede usarse)")
    usos_maximos: Optional[int] = Field(None, ge=1, description="Usos máximos del consumible")
    
    # Disponibilidad temporal
    disponible_desde: Optional[datetime] = Field(None, description="Fecha desde que está disponible")
    disponible_hasta: Optional[datetime] = Field(None, description="Fecha hasta que está disponible")
    
    # Estado
    activo: bool = Field(True, description="Si está activo y visible en tienda")
    
    # Apariencia (para ropa/accesorios)
    imagen_url: Optional[str] = Field(None, description="URL de la imagen del item")
    preview_url: Optional[str] = Field(None, description="URL del preview 3D")
    color_hex: Optional[str] = Field(None, pattern="^#[0-9A-Fa-f]{6}$", description="Color en formato hex")


class ActualizarItemRequest(BaseModel):
    """Schema para actualizar item existente"""
    nombre: Optional[str] = Field(None, min_length=3, max_length=200)
    descripcion: Optional[str] = Field(None, max_length=1000)
    precio_puntos: Optional[int] = Field(None, ge=0)
    rareza: Optional[RarezaItem] = None
    nivel_minimo_requerido: Optional[int] = Field(None, ge=1, le=100)
    stock_disponible: Optional[int] = Field(None, ge=0)
    disponible_desde: Optional[datetime] = None
    disponible_hasta: Optional[datetime] = None
    activo: Optional[bool] = None
    imagen_url: Optional[str] = None
    preview_url: Optional[str] = None


class ItemResponse(BaseModel):
    """Response con datos del item"""
    item_id: UUID
    nombre: str
    descripcion: Optional[str]
    categoria: str
    rareza: str
    precio_puntos: int
    nivel_minimo_requerido: int
    stock_limitado: bool
    stock_disponible: Optional[int]
    es_consumible: bool
    usos_maximos: Optional[int]
    activo: bool
    total_vendidos: int
    fecha_creacion: datetime
    
    class Config:
        from_attributes = True


class EstadisticasVentasResponse(BaseModel):
    """Estadísticas de ventas de la tienda"""
    total_transacciones: int
    transacciones_exitosas: int
    transacciones_fallidas: int
    total_puntos_gastados: int
    items_mas_vendidos: List[dict]
    ventas_por_categoria: dict
    ventas_por_rareza: dict
    ingresos_ultimos_7_dias: List[dict]


# ============================================
# HELPER: Verificar permisos de admin
# ============================================

def verificar_admin(usuario: Usuario):
    """Verifica que el usuario sea admin o coordinador"""
    if usuario.rol not in ["admin", "coordinador"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo administradores pueden acceder a este endpoint"
        )


def calcular_precio_por_rareza(rareza: RarezaItem) -> int:
    """
    Calcula precio automático según rareza.
    
    Precios base:
    - COMUN: 50-150 pts
    - RARO: 200-500 pts
    - EPICO: 800-1500 pts
    - LEGENDARIO: 2000-5000 pts
    """
    precios = {
        RarezaItem.COMUN: 100,
        RarezaItem.RARO: 300,
        RarezaItem.EPICO: 1000,
        RarezaItem.LEGENDARIO: 3000
    }
    
    return precios.get(rareza, 100)


# ============================================
# ENDPOINTS: CRUD Items
# ============================================

@router.post("/items", response_model=ItemResponse, status_code=status.HTTP_201_CREATED)
async def crear_item(
    item_data: CrearItemRequest,
    current_user: Usuario = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    **Crear nuevo item en la tienda**
    
    **Permisos:** Solo admin/coordinador
    
    **Precio:**
    - Si `usar_precio_automatico=True`: calcula según rareza
      - COMUN: 100 pts
      - RARO: 300 pts
      - EPICO: 1,000 pts
      - LEGENDARIO: 3,000 pts
    - Si `precio_puntos` está definido: usa ese precio manual
    
    **Categorías disponibles:**
    - CABELLO, ROPA, OJOS, BOCA, NARIZ, CEJAS
    - ACCESORIO_CABEZA, ACCESORIO_CUELLO, ACCESORIO_MANOS
    - FONDO, MARCO, EFECTO
    - FUNCIONAL (congeladores, recuperadores, etc.)
    
    **Rarezas:**
    - COMUN (común, fácil de obtener)
    - RARO (poco común, requiere esfuerzo)
    - EPICO (muy raro, requiere dedicación)
    - LEGENDARIO (extremadamente raro, solo los mejores)
    
    **Ejemplos de items:**
    ```json
    {
      "nombre": "Cabello Galaxia",
      "descripcion": "Cabello con efecto de galaxia animada",
      "categoria": "CABELLO",
      "rareza": "EPICO",
      "usar_precio_automatico": true,
      "nivel_minimo_requerido": 15,
      "activo": true,
      "imagen_url": "https://cdn.acadify.com/items/cabello_galaxia.png"
    }
    ```
    """
    verificar_admin(current_user)
    
    try:
        # Determinar precio
        if item_data.usar_precio_automatico:
            precio = calcular_precio_por_rareza(item_data.rareza)
        elif item_data.precio_puntos is not None:
            precio = item_data.precio_puntos
        else:
            # Default: precio por rareza
            precio = calcular_precio_por_rareza(item_data.rareza)
        
        # Crear item
        nuevo_item = TiendaItem(
            nombre=item_data.nombre,
            descripcion=item_data.descripcion,
            categoria=item_data.categoria,
            rareza=item_data.rareza,
            precio_puntos=precio,
            nivel_minimo_requerido=item_data.nivel_minimo_requerido,
            stock_limitado=item_data.stock_limitado,
            stock_disponible=item_data.stock_disponible,
            es_consumible=item_data.es_consumible,
            usos_maximos=item_data.usos_maximos,
            disponible_desde=item_data.disponible_desde,
            disponible_hasta=item_data.disponible_hasta,
            activo=item_data.activo,
            imagen_url=item_data.imagen_url,
            preview_url=item_data.preview_url,
            color_hex=item_data.color_hex
        )
        
        db.add(nuevo_item)
        await db.commit()
        await db.refresh(nuevo_item)
        
        logger.info(f"Item creado: {nuevo_item.item_id} - {nuevo_item.nombre} por admin {current_user.usuario_id}")
        
        return ItemResponse(
            item_id=nuevo_item.item_id,
            nombre=nuevo_item.nombre,
            descripcion=nuevo_item.descripcion,
            categoria=nuevo_item.categoria.value,
            rareza=nuevo_item.rareza.value,
            precio_puntos=nuevo_item.precio_puntos,
            nivel_minimo_requerido=nuevo_item.nivel_minimo_requerido,
            stock_limitado=nuevo_item.stock_limitado,
            stock_disponible=nuevo_item.stock_disponible,
            es_consumible=nuevo_item.es_consumible,
            usos_maximos=nuevo_item.usos_maximos,
            activo=nuevo_item.activo,
            total_vendidos=0,
            fecha_creacion=nuevo_item.fecha_creacion
        )
        
    except Exception as e:
        await db.rollback()
        logger.error(f"Error creando item: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al crear item: {str(e)}"
        )


@router.get("/items", response_model=List[ItemResponse])
async def listar_items(
    categoria: Optional[CategoriaItem] = Query(None, description="Filtrar por categoría"),
    rareza: Optional[RarezaItem] = Query(None, description="Filtrar por rareza"),
    activo: Optional[bool] = Query(None, description="Filtrar por estado activo"),
    limit: int = Query(50, ge=1, le=200, description="Límite de resultados"),
    offset: int = Query(0, ge=0, description="Offset para paginación"),
    current_user: Usuario = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    **Listar todos los items de la tienda (incluye inactivos)**
    
    **Permisos:** Solo admin/coordinador
    
    **Filtros disponibles:**
    - `categoria`: Filtrar por categoría específica
    - `rareza`: Filtrar por nivel de rareza
    - `activo`: true (solo activos) / false (solo inactivos) / null (todos)
    
    **Diferencia con endpoint público:**
    - Endpoint público solo muestra items activos
    - Este endpoint muestra TODO (para gestión)
    """
    verificar_admin(current_user)
    
    try:
        # Construir query
        query = select(TiendaItem)
        
        # Aplicar filtros
        conditions = []
        if categoria:
            conditions.append(TiendaItem.categoria == categoria)
        if rareza:
            conditions.append(TiendaItem.rareza == rareza)
        if activo is not None:
            conditions.append(TiendaItem.activo == activo)
        
        if conditions:
            query = query.where(and_(*conditions))
        
        # Ordenar por fecha de creación (más recientes primero)
        query = query.order_by(desc(TiendaItem.fecha_creacion))
        
        # Paginación
        query = query.offset(offset).limit(limit)
        
        result = await db.execute(query)
        items = result.scalars().all()
        
        # Obtener total vendidos por item (subquery)
        items_response = []
        for item in items:
            vendidos_query = select(func.count(TransaccionTienda.transaccion_id)).where(
                and_(
                    TransaccionTienda.item_id == item.item_id,
                    TransaccionTienda.exitosa == True
                )
            )
            result_vendidos = await db.execute(vendidos_query)
            total_vendidos = result_vendidos.scalar() or 0
            
            items_response.append(ItemResponse(
                item_id=item.item_id,
                nombre=item.nombre,
                descripcion=item.descripcion,
                categoria=item.categoria.value,
                rareza=item.rareza.value,
                precio_puntos=item.precio_puntos,
                nivel_minimo_requerido=item.nivel_minimo_requerido,
                stock_limitado=item.stock_limitado,
                stock_disponible=item.stock_disponible,
                es_consumible=item.es_consumible,
                usos_maximos=item.usos_maximos,
                activo=item.activo,
                total_vendidos=total_vendidos,
                fecha_creacion=item.fecha_creacion
            ))
        
        return items_response
        
    except Exception as e:
        logger.error(f"Error listando items: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al listar items: {str(e)}"
        )


@router.get("/items/{item_id}", response_model=ItemResponse)
async def obtener_item(
    item_id: UUID,
    current_user: Usuario = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    **Obtener detalles de un item específico**
    
    **Permisos:** Solo admin/coordinador
    
    Incluye estadísticas de ventas
    """
    verificar_admin(current_user)
    
    try:
        # Buscar item
        query = select(TiendaItem).where(TiendaItem.item_id == item_id)
        result = await db.execute(query)
        item = result.scalar_one_or_none()
        
        if not item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Item no encontrado"
            )
        
        # Obtener total vendidos
        vendidos_query = select(func.count(TransaccionTienda.transaccion_id)).where(
            and_(
                TransaccionTienda.item_id == item_id,
                TransaccionTienda.exitosa == True
            )
        )
        result_vendidos = await db.execute(vendidos_query)
        total_vendidos = result_vendidos.scalar() or 0
        
        return ItemResponse(
            item_id=item.item_id,
            nombre=item.nombre,
            descripcion=item.descripcion,
            categoria=item.categoria.value,
            rareza=item.rareza.value,
            precio_puntos=item.precio_puntos,
            nivel_minimo_requerido=item.nivel_minimo_requerido,
            stock_limitado=item.stock_limitado,
            stock_disponible=item.stock_disponible,
            es_consumible=item.es_consumible,
            usos_maximos=item.usos_maximos,
            activo=item.activo,
            total_vendidos=total_vendidos,
            fecha_creacion=item.fecha_creacion
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error obteniendo item: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener item: {str(e)}"
        )


@router.put("/items/{item_id}", response_model=ItemResponse)
async def actualizar_item(
    item_id: UUID,
    item_data: ActualizarItemRequest,
    current_user: Usuario = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    **Actualizar item existente**
    
    **Permisos:** Solo admin/coordinador
    
    **Campos editables:**
    - Nombre, descripción
    - Precio (ajustar según demanda/economía)
    - Rareza (upgrade/downgrade)
    - Nivel mínimo requerido
    - Stock disponible
    - Disponibilidad temporal
    - Estado activo/inactivo
    - URLs de imagen/preview
    
    **Nota:** No se puede cambiar la categoría (crearía inconsistencias)
    """
    verificar_admin(current_user)
    
    try:
        # Buscar item
        query = select(TiendaItem).where(TiendaItem.item_id == item_id)
        result = await db.execute(query)
        item = result.scalar_one_or_none()
        
        if not item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Item no encontrado"
            )
        
        # Actualizar campos
        update_data = item_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(item, field, value)
        
        await db.commit()
        await db.refresh(item)
        
        logger.info(f"Item actualizado: {item_id} por admin {current_user.usuario_id}")
        
        # Obtener total vendidos
        vendidos_query = select(func.count(TransaccionTienda.transaccion_id)).where(
            and_(
                TransaccionTienda.item_id == item_id,
                TransaccionTienda.exitosa == True
            )
        )
        result_vendidos = await db.execute(vendidos_query)
        total_vendidos = result_vendidos.scalar() or 0
        
        return ItemResponse(
            item_id=item.item_id,
            nombre=item.nombre,
            descripcion=item.descripcion,
            categoria=item.categoria.value,
            rareza=item.rareza.value,
            precio_puntos=item.precio_puntos,
            nivel_minimo_requerido=item.nivel_minimo_requerido,
            stock_limitado=item.stock_limitado,
            stock_disponible=item.stock_disponible,
            es_consumible=item.es_consumible,
            usos_maximos=item.usos_maximos,
            activo=item.activo,
            total_vendidos=total_vendidos,
            fecha_creacion=item.fecha_creacion
        )
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Error actualizando item: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al actualizar item: {str(e)}"
        )


@router.delete("/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def eliminar_item(
    item_id: UUID,
    forzar: bool = Query(False, description="Forzar eliminación aunque tenga ventas"),
    current_user: Usuario = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    **Eliminar item de la tienda**
    
    **Permisos:** Solo admin/coordinador
    
    **Comportamiento:**
    - Por defecto: Solo elimina items sin ventas
    - Con `forzar=true`: Elimina incluso si tiene ventas (¡Cuidado!)
    
    **Recomendación:**
    - En lugar de eliminar, mejor desactivar (`activo=false`)
    - Mantiene historial de transacciones íntegro
    """
    verificar_admin(current_user)
    
    try:
        # Buscar item
        query = select(TiendaItem).where(TiendaItem.item_id == item_id)
        result = await db.execute(query)
        item = result.scalar_one_or_none()
        
        if not item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Item no encontrado"
            )
        
        # Verificar si tiene ventas
        if not forzar:
            ventas_query = select(func.count(TransaccionTienda.transaccion_id)).where(
                and_(
                    TransaccionTienda.item_id == item_id,
                    TransaccionTienda.exitosa == True
                )
            )
            result_ventas = await db.execute(ventas_query)
            tiene_ventas = result_ventas.scalar() > 0
            
            if tiene_ventas:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="No se puede eliminar item con ventas. Usa forzar=true o mejor desactívalo."
                )
        
        # Eliminar item
        await db.delete(item)
        await db.commit()
        
        logger.warning(f"Item eliminado: {item_id} por admin {current_user.usuario_id} (forzar={forzar})")
        
        return None
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Error eliminando item: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al eliminar item: {str(e)}"
        )


# ============================================
# ENDPOINTS: Estadísticas
# ============================================

@router.get("/estadisticas", response_model=EstadisticasVentasResponse)
async def obtener_estadisticas_ventas(
    current_user: Usuario = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    **Obtener estadísticas completas de ventas de la tienda**
    
    **Permisos:** Solo admin/coordinador
    
    **Incluye:**
    - Total de transacciones (exitosas/fallidas)
    - Total de puntos gastados
    - Items más vendidos (top 10)
    - Ventas por categoría
    - Ventas por rareza
    - Ingresos de últimos 7 días
    
    **Útil para:**
    - Ajustar precios según demanda
    - Identificar items populares
    - Balancear economía
    - Crear nuevos items basados en tendencias
    """
    verificar_admin(current_user)
    
    try:
        # Total transacciones
        total_query = select(func.count(TransaccionTienda.transaccion_id))
        result_total = await db.execute(total_query)
        total_transacciones = result_total.scalar() or 0
        
        # Transacciones exitosas
        exitosas_query = select(func.count(TransaccionTienda.transaccion_id)).where(
            TransaccionTienda.exitosa == True
        )
        result_exitosas = await db.execute(exitosas_query)
        transacciones_exitosas = result_exitosas.scalar() or 0
        
        # Fallidas
        transacciones_fallidas = total_transacciones - transacciones_exitosas
        
        # Total puntos gastados
        puntos_query = select(func.sum(TransaccionTienda.puntos_gastados)).where(
            TransaccionTienda.exitosa == True
        )
        result_puntos = await db.execute(puntos_query)
        total_puntos_gastados = result_puntos.scalar() or 0
        
        # Items más vendidos (top 10)
        # TODO: Implementar query compleja con join
        items_mas_vendidos = []
        
        # Ventas por categoría
        # TODO: Implementar
        ventas_por_categoria = {}
        
        # Ventas por rareza
        # TODO: Implementar
        ventas_por_rareza = {}
        
        # Ingresos últimos 7 días
        # TODO: Implementar
        ingresos_ultimos_7_dias = []
        
        return EstadisticasVentasResponse(
            total_transacciones=total_transacciones,
            transacciones_exitosas=transacciones_exitosas,
            transacciones_fallidas=transacciones_fallidas,
            total_puntos_gastados=int(total_puntos_gastados),
            items_mas_vendidos=items_mas_vendidos,
            ventas_por_categoria=ventas_por_categoria,
            ventas_por_rareza=ventas_por_rareza,
            ingresos_ultimos_7_dias=ingresos_ultimos_7_dias
        )
        
    except Exception as e:
        logger.error(f"Error obteniendo estadísticas: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener estadísticas: {str(e)}"
        )
