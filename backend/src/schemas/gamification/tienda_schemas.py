"""
Schemas de validación para el módulo de Tienda.

Este módulo define los modelos Pydantic para:
- Catálogo de items
- Compra de items
- Inventario del usuario
- Equipamiento de items
- Uso de consumibles
- Transacciones

Author: GitHub Copilot & Team
Date: 2 de noviembre de 2025
Version: 1.0.0
"""

from pydantic import BaseModel, Field, validator
from typing import List, Optional
from uuid import UUID
from datetime import datetime
from enum import Enum

from .common import BaseResponse, PaginationParams


# =============================================================================
# ENUMS
# =============================================================================

class CategoriaItem(str, Enum):
    """Categorías de items de la tienda."""
    # Avatar
    AVATAR_CABEZA = "avatar_cabeza"
    AVATAR_TORSO = "avatar_torso"
    AVATAR_PIERNAS = "avatar_piernas"
    AVATAR_ZAPATOS = "avatar_zapatos"
    AVATAR_ACCESORIOS = "avatar_accesorios"
    AVATAR_CONJUNTO = "avatar_conjunto"
    # Cosméticos
    FOTO_PERFIL = "foto_perfil"
    FOTO_PORTADA = "foto_portada"
    MARCO_PERFIL = "marco_perfil"
    EFECTO_PERFIL = "efecto_perfil"
    TEMA_CHAT = "tema_chat"
    STICKER = "sticker"
    EMOJI_PERSONALIZADO = "emoji_personalizado"
    # Funcionales
    MULTIPLICADOR_PUNTOS = "multiplicador_puntos"
    PROTECCION_RACHA = "proteccion_racha"
    DESBLOQUEAR_CONTENIDO = "desbloquear_contenido"
    BOOST_EXPERIENCIA = "boost_experiencia"
    # Especiales
    EVENTO = "evento"
    LIMITADO = "limitado"


class RarezaItem(str, Enum):
    """Niveles de rareza de items."""
    COMUN = "comun"
    RARO = "raro"
    EPICO = "epico"
    LEGENDARIO = "legendario"


class TipoItem(str, Enum):
    """Tipos de items."""
    AVATAR = "avatar"
    COSMETIC = "cosmetic"
    CONSUMIBLE = "consumible"
    PERMANENTE = "permanente"
    TEMPORAL = "temporal"


# =============================================================================
# ITEM BASE
# =============================================================================

class TiendaItemBase(BaseModel):
    """
    Información básica de un item de la tienda.
    
    Attributes:
        item_id: UUID del item
        nombre: Nombre del item
        descripcion: Descripción detallada
        categoria: Categoría del item
        tipo: Tipo de item
        rareza: Nivel de rareza
        imagen_url: URL de la imagen principal
        precio_puntos: Precio en puntos
    """
    item_id: str = Field(..., description="UUID del item")
    nombre: str = Field(..., max_length=100, description="Nombre del item")
    descripcion: Optional[str] = Field(None, max_length=500, description="Descripción")
    categoria: CategoriaItem = Field(..., description="Categoría")
    tipo: TipoItem = Field(..., description="Tipo de item")
    rareza: RarezaItem = Field(..., description="Rareza")
    imagen_url: Optional[str] = Field(None, description="URL imagen")
    precio_puntos: int = Field(..., ge=0, description="Precio en puntos")
    
    class Config:
        json_schema_extra = {
            "example": {
                "item_id": "123e4567-e89b-12d3-a456-426614174000",
                "nombre": "Cabello Azul Neon",
                "descripcion": "Peinado futurista con efecto neon",
                "categoria": "avatar_cabeza",
                "tipo": "avatar",
                "rareza": "epico",
                "imagen_url": "/assets/items/cabello_azul_neon.png",
                "precio_puntos": 800
            }
        }


# =============================================================================
# CATÁLOGO
# =============================================================================

class TiendaItemCatalogo(TiendaItemBase):
    """
    Item del catálogo con información adicional.
    
    Extends TiendaItemBase con:
        es_disponible: Si está disponible para compra
        stock_disponible: Stock disponible (si es limitado)
        es_limitado: Si es de tiempo/stock limitado
        es_nuevo: Si es item nuevo
        es_destacado: Si está destacado
        descuento_porcentaje: Descuento activo (0-100)
        precio_original: Precio antes de descuento
    """
    es_disponible: bool = Field(..., description="Disponible para compra")
    stock_disponible: Optional[int] = Field(None, ge=0, description="Stock disponible")
    es_limitado: bool = Field(default=False, description="Edición limitada")
    es_nuevo: bool = Field(default=False, description="Item nuevo")
    es_destacado: bool = Field(default=False, description="Item destacado")
    descuento_porcentaje: Optional[int] = Field(None, ge=0, le=100, description="Descuento")
    precio_original: Optional[int] = Field(None, ge=0, description="Precio original")
    
    class Config:
        json_schema_extra = {
            "example": {
                "item_id": "123e4567-e89b-12d3-a456-426614174000",
                "nombre": "Cabello Azul Neon",
                "categoria": "avatar_cabeza",
                "tipo": "avatar",
                "rareza": "epico",
                "precio_puntos": 640,
                "precio_original": 800,
                "descuento_porcentaje": 20,
                "es_disponible": True,
                "es_nuevo": True,
                "es_destacado": False,
                "es_limitado": False,
                "stock_disponible": None
            }
        }


class CatalogoTiendaResponse(BaseModel):
    """
    Respuesta del catálogo de la tienda.
    
    Attributes:
        items: Lista de items
        total: Total de items que cumplen filtros
        filtros_aplicados: Resumen de filtros
    """
    items: List[TiendaItemCatalogo] = Field(..., description="Lista de items")
    total: int = Field(..., ge=0, description="Total de items")
    filtros_aplicados: dict = Field(default={}, description="Filtros aplicados")
    
    class Config:
        json_schema_extra = {
            "example": {
                "items": [
                    {
                        "item_id": "123e4567-e89b-12d3-a456-426614174000",
                        "nombre": "Cabello Azul Neon",
                        "categoria": "avatar_cabeza",
                        "rareza": "epico",
                        "precio_puntos": 640,
                        "es_nuevo": True
                    }
                ],
                "total": 78,
                "filtros_aplicados": {
                    "categoria": "avatar_cabeza",
                    "rareza": "epico"
                }
            }
        }


# =============================================================================
# COMPRA
# =============================================================================

class CompraRequest(BaseModel):
    """
    Request para comprar un item.
    
    Attributes:
        item_id: UUID del item a comprar
        cantidad: Cantidad a comprar (para consumibles)
    """
    item_id: UUID = Field(..., description="UUID del item")
    cantidad: int = Field(default=1, ge=1, le=99, description="Cantidad")
    
    @validator('cantidad')
    def validar_cantidad(cls, v):
        if v < 1:
            raise ValueError('Cantidad debe ser al menos 1')
        if v > 99:
            raise ValueError('Cantidad máxima es 99')
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "item_id": "123e4567-e89b-12d3-a456-426614174000",
                "cantidad": 1
            }
        }


class CompraResponse(BaseResponse):
    """
    Respuesta al comprar un item.
    
    Attributes:
        transaccion_id: UUID de la transacción
        item: Información del item comprado
        cantidad: Cantidad comprada
        puntos_gastados: Total de puntos gastados
        puntos_restantes: Puntos que quedan
        inventario_id: UUID del item en inventario
    """
    transaccion_id: str = Field(..., description="UUID de la transacción")
    item: TiendaItemBase = Field(..., description="Item comprado")
    cantidad: int = Field(..., ge=1, description="Cantidad comprada")
    puntos_gastados: int = Field(..., ge=0, description="Puntos gastados")
    puntos_restantes: int = Field(..., ge=0, description="Puntos restantes")
    inventario_id: str = Field(..., description="UUID en inventario")
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "¡Compraste Cabello Azul Neon!",
                "transaccion_id": "923e4567-e89b-12d3-a456-426614174000",
                "item": {
                    "nombre": "Cabello Azul Neon",
                    "rareza": "epico"
                },
                "cantidad": 1,
                "puntos_gastados": 800,
                "puntos_restantes": 1200,
                "inventario_id": "823e4567-e89b-12d3-a456-426614174000"
            }
        }


# =============================================================================
# INVENTARIO
# =============================================================================

class InventarioItem(BaseModel):
    """
    Item en el inventario del usuario.
    
    Attributes:
        inventario_id: UUID del registro en inventario
        item: Información del item
        cantidad: Cantidad disponible
        esta_equipado: Si está equipado en avatar
        fecha_adquisicion: Cuándo se adquirió
        metodo_adquisicion: Cómo se adquirió
        veces_usado: Contador de usos
        disponible: Si está disponible para usar
    """
    inventario_id: str = Field(..., description="UUID en inventario")
    item: TiendaItemBase = Field(..., description="Info del item")
    cantidad: int = Field(..., ge=0, description="Cantidad disponible")
    esta_equipado: bool = Field(..., description="Si está equipado")
    fecha_adquisicion: datetime = Field(..., description="Fecha de adquisición")
    metodo_adquisicion: str = Field(..., description="Método de adquisición")
    veces_usado: int = Field(..., ge=0, description="Veces usado")
    disponible: bool = Field(..., description="Disponible para usar")
    
    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}
        json_schema_extra = {
            "example": {
                "inventario_id": "823e4567-e89b-12d3-a456-426614174000",
                "item": {
                    "nombre": "Cabello Azul Neon",
                    "categoria": "avatar_cabeza",
                    "rareza": "epico"
                },
                "cantidad": 1,
                "esta_equipado": True,
                "fecha_adquisicion": "2025-10-20T15:30:00Z",
                "metodo_adquisicion": "compra",
                "veces_usado": 5,
                "disponible": True
            }
        }


class InventarioResponse(BaseModel):
    """
    Respuesta con el inventario del usuario.
    
    Attributes:
        items: Lista de items en inventario
        total: Total de items
        equipados: Cantidad equipada
    """
    items: List[InventarioItem] = Field(..., description="Items en inventario")
    total: int = Field(..., ge=0, description="Total de items")
    equipados: int = Field(..., ge=0, description="Items equipados")
    
    class Config:
        json_schema_extra = {
            "example": {
                "items": [
                    {
                        "inventario_id": "823e4567-e89b-12d3-a456-426614174000",
                        "item": {"nombre": "Cabello Azul Neon"},
                        "cantidad": 1,
                        "esta_equipado": True
                    }
                ],
                "total": 15,
                "equipados": 5
            }
        }


# =============================================================================
# EQUIPAMIENTO
# =============================================================================

class EquiparItemRequest(BaseModel):
    """Request para equipar item (sin body, solo path param)."""
    pass


class EquiparItemResponse(BaseResponse):
    """
    Respuesta al equipar un item.
    
    Attributes:
        item_equipado: Nombre del item equipado
        categoria: Categoría del item
        item_desequipado: Nombre del item anterior (si había)
    """
    item_equipado: str = Field(..., description="Item equipado")
    categoria: str = Field(..., description="Categoría del item")
    item_desequipado: Optional[str] = Field(None, description="Item anterior desequipado")
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "¡Cabello Azul Neon equipado!",
                "item_equipado": "Cabello Azul Neon",
                "categoria": "avatar_cabeza",
                "item_desequipado": "Cabello Rojo Fuego"
            }
        }


# =============================================================================
# USO DE CONSUMIBLES
# =============================================================================

class UsarItemRequest(BaseModel):
    """Request para usar item consumible (sin body, solo path param)."""
    pass


class UsarItemResponse(BaseResponse):
    """
    Respuesta al usar un item consumible.
    
    Attributes:
        item_usado: Nombre del item usado
        efecto: Efecto aplicado
        cantidad_restante: Cantidad que queda
    """
    item_usado: str = Field(..., description="Item usado")
    efecto: dict = Field(..., description="Efecto aplicado")
    cantidad_restante: int = Field(..., ge=0, description="Cantidad restante")
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "¡Congelador de Racha usado! Racha protegida por 3 días",
                "item_usado": "Congelador de Racha 3 Días",
                "efecto": {
                    "tipo": "proteccion_racha",
                    "dias": 3,
                    "descripcion": "Tu racha está protegida"
                },
                "cantidad_restante": 0
            }
        }


# =============================================================================
# TRANSACCIONES
# =============================================================================

class TransaccionHistorial(BaseModel):
    """
    Transacción en el historial.
    
    Attributes:
        transaccion_id: UUID de la transacción
        tipo: Tipo de transacción
        item: Nombre del item
        cantidad: Cantidad
        puntos: Puntos involucrados
        exitosa: Si fue exitosa
        fecha: Fecha de la transacción
        razon_fallo: Razón del fallo (si aplica)
    """
    transaccion_id: str = Field(..., description="UUID transacción")
    tipo: str = Field(..., description="Tipo de transacción")
    item: str = Field(..., description="Nombre del item")
    cantidad: int = Field(..., ge=1, description="Cantidad")
    puntos: int = Field(..., ge=0, description="Puntos")
    exitosa: bool = Field(..., description="Si fue exitosa")
    fecha: datetime = Field(..., description="Fecha")
    razon_fallo: Optional[str] = Field(None, description="Razón de fallo")
    
    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}
        json_schema_extra = {
            "example": {
                "transaccion_id": "923e4567-e89b-12d3-a456-426614174000",
                "tipo": "compra",
                "item": "Cabello Azul Neon",
                "cantidad": 1,
                "puntos": 800,
                "exitosa": True,
                "fecha": "2025-11-02T16:45:00Z",
                "razon_fallo": None
            }
        }


class HistorialTransaccionesResponse(BaseModel):
    """
    Respuesta con historial de transacciones.
    
    Attributes:
        transacciones: Lista de transacciones
        total: Total de transacciones
    """
    transacciones: List[TransaccionHistorial] = Field(..., description="Transacciones")
    total: int = Field(..., ge=0, description="Total de transacciones")
    
    class Config:
        json_schema_extra = {
            "example": {
                "transacciones": [
                    {
                        "transaccion_id": "923e4567-e89b-12d3-a456-426614174000",
                        "tipo": "compra",
                        "item": "Cabello Azul Neon",
                        "puntos": 800,
                        "exitosa": True
                    }
                ],
                "total": 25
            }
        }


# =============================================================================
# ESTADÍSTICAS
# =============================================================================

class EstadisticasTiendaResponse(BaseModel):
    """
    Estadísticas de la tienda del usuario.
    
    Attributes:
        items_poseidos: Total de items en inventario
        items_equipados: Items equipados actualmente
        puntos_gastados_total: Total de puntos gastados
        transacciones_exitosas: Número de compras exitosas
        transacciones_fallidas: Número de intentos fallidos
        por_categoria: Distribución por categoría
        por_rareza: Distribución por rareza
    """
    items_poseidos: int = Field(..., ge=0, description="Items en inventario")
    items_equipados: int = Field(..., ge=0, description="Items equipados")
    puntos_gastados_total: int = Field(..., ge=0, description="Puntos gastados")
    transacciones_exitosas: int = Field(..., ge=0, description="Compras exitosas")
    transacciones_fallidas: int = Field(..., ge=0, description="Intentos fallidos")
    por_categoria: dict = Field(default={}, description="Por categoría")
    por_rareza: dict = Field(default={}, description="Por rareza")
    
    class Config:
        json_schema_extra = {
            "example": {
                "items_poseidos": 28,
                "items_equipados": 6,
                "puntos_gastados_total": 5800,
                "transacciones_exitosas": 28,
                "transacciones_fallidas": 3,
                "por_categoria": {
                    "avatar_cabeza": 5,
                    "avatar_torso": 4,
                    "proteccion_racha": 3
                },
                "por_rareza": {
                    "comun": 12,
                    "raro": 10,
                    "epico": 5,
                    "legendario": 1
                }
            }
        }
