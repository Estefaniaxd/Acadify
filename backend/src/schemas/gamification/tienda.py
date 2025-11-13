"""
Schemas para el sistema de tienda virtual.

Define los schemas de validación para:
- Items de tienda
- Inventario de usuario
- Transacciones
- Compras y equipamiento
"""

from datetime import datetime, date
from typing import Optional, Dict, Any, List
from uuid import UUID
from pydantic import BaseModel, Field, field_validator

from src.enums.gamification import (
    CategoriaItem, RarezaItem, MetodoAdquisicion, TipoTransaccion
)


# =============================================================================
# TIENDA ITEM SCHEMAS
# =============================================================================

class TiendaItemBase(BaseModel):
    """Schema base para items de tienda."""
    nombre: str = Field(..., min_length=1, max_length=100)
    descripcion: Optional[str] = Field(None, max_length=500)
    categoria: CategoriaItem
    subcategoria: Optional[str] = Field(None, max_length=50)
    rareza: RarezaItem
    precio_puntos: int = Field(..., ge=0)
    nivel_minimo_requerido: int = Field(default=1, ge=1)
    es_limitado: bool = Field(default=False)
    stock_disponible: Optional[int] = Field(None, ge=0)
    es_funcional: bool = Field(default=False)
    efecto_json: Optional[Dict[str, Any]] = None
    disponible_desde: Optional[datetime] = None
    disponible_hasta: Optional[datetime] = None


class TiendaItemCreate(TiendaItemBase):
    """Schema para crear item de tienda."""
    asset_id: Optional[UUID] = None


class TiendaItemUpdate(BaseModel):
    """Schema para actualizar item de tienda."""
    nombre: Optional[str] = Field(None, min_length=1, max_length=100)
    descripcion: Optional[str] = Field(None, max_length=500)
    precio_puntos: Optional[int] = Field(None, ge=0)
    es_activo: Optional[bool] = None
    stock_disponible: Optional[int] = Field(None, ge=0)
    disponible_desde: Optional[datetime] = None
    disponible_hasta: Optional[datetime] = None


class TiendaItemResponse(TiendaItemBase):
    """Schema de respuesta para item de tienda."""
    item_id: UUID
    asset_id: Optional[UUID]
    es_activo: bool
    fecha_creacion: datetime
    fecha_actualizacion: datetime
    
    # Propiedades computadas
    esta_disponible: bool
    tiene_stock: bool

    class Config:
        from_attributes = True


class TiendaItemDetalle(TiendaItemResponse):
    """Schema detallado con información del asset."""
    asset_url: Optional[str] = None
    total_compras: int = 0
    usuarios_con_item: int = 0


# =============================================================================
# INVENTARIO SCHEMAS
# =============================================================================

class InventarioUsuarioBase(BaseModel):
    """Schema base para inventario."""
    cantidad: int = Field(default=1, ge=1)


class ComprarItemRequest(BaseModel):
    """Request para comprar un item."""
    item_id: UUID
    cantidad: int = Field(default=1, ge=1, le=100)


class EquiparItemRequest(BaseModel):
    """Request para equipar un item."""
    inventario_id: UUID


class UsarItemRequest(BaseModel):
    """Request para usar un item consumible."""
    inventario_id: UUID
    cantidad: int = Field(default=1, ge=1)


class InventarioUsuarioResponse(BaseModel):
    """Schema de respuesta para item en inventario."""
    inventario_id: UUID
    usuario_id: UUID
    item_id: UUID
    fecha_adquisicion: datetime
    metodo_adquisicion: MetodoAdquisicion
    precio_pagado: Optional[int]
    cantidad: int
    esta_equipado: bool
    metadata_json: Optional[Dict[str, Any]]
    fecha_ultimo_uso: Optional[datetime]
    veces_usado: int
    
    # Información del item
    item_nombre: str
    item_categoria: CategoriaItem
    item_rareza: RarezaItem
    item_descripcion: Optional[str]
    
    # Propiedades computadas
    esta_disponible: bool

    class Config:
        from_attributes = True


class InventarioDetalleResponse(InventarioUsuarioResponse):
    """Schema detallado del inventario con asset."""
    asset_url: Optional[str] = None
    es_consumible: bool = False
    efecto_json: Optional[Dict[str, Any]] = None


# =============================================================================
# TRANSACCIÓN SCHEMAS
# =============================================================================

class TransaccionTiendaResponse(BaseModel):
    """Schema de respuesta para transacción."""
    transaccion_id: UUID
    usuario_id: UUID
    item_id: UUID
    tipo_transaccion: TipoTransaccion
    cantidad: int
    puntos: int
    puntos_antes: int
    puntos_despues: int
    exitosa: bool
    razon_fallo: Optional[str]
    fecha_transaccion: datetime
    ip_usuario: Optional[str]
    
    # Información del item
    item_nombre: str
    item_categoria: CategoriaItem
    item_rareza: RarezaItem

    class Config:
        from_attributes = True


# =============================================================================
# RESPONSE SCHEMAS COMPUESTOS
# =============================================================================

class CatalogoResponse(BaseModel):
    """Response para catálogo de tienda."""
    items: List[TiendaItemResponse]
    total: int
    pagina: int
    items_por_pagina: int
    total_paginas: int


class InventarioResponse(BaseModel):
    """Response para inventario completo del usuario."""
    items: List[InventarioDetalleResponse]
    total_items: int
    items_equipados: int
    items_consumibles: int


class EstadisticasTiendaResponse(BaseModel):
    """Estadísticas de compras del usuario."""
    total_compras: int
    total_gastado: int
    items_unicos: int
    items_por_rareza: Dict[str, int]
    items_por_categoria: Dict[str, int]
    item_mas_caro: Optional[TiendaItemResponse]
    ultima_compra: Optional[TransaccionTiendaResponse]


class CompraResponse(BaseModel):
    """Response después de comprar."""
    success: bool
    message: str
    transaccion: TransaccionTiendaResponse
    inventario_item: InventarioUsuarioResponse
    puntos_restantes: int
