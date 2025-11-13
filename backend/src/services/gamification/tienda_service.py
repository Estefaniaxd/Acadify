"""
Servicio de gestión de tienda virtual de gamificación.

Este servicio maneja toda la lógica relacionada con:
- Consulta de catálogo de items
- Compra de items con puntos
- Gestión de inventario del usuario
- Equipamiento de items (avatar/perfil)
- Uso de items consumibles
- Registro de transacciones

Author: GitHub Copilot & Team
Date: 31 octubre 2025
Version: 1.0.0
"""

import logging
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from sqlalchemy.orm import selectinload

from src.models.gamification.tienda_item import TiendaItem
from src.models.gamification.inventario_usuario import InventarioUsuario
from src.models.gamification.transaccion_tienda import TransaccionTienda
from src.models.gamification.usuario_puntos import UsuarioPuntos
from src.models.avatar.avatar_asset import AvatarAsset
from src.models.avatar.user_avatar import UserAvatar
from src.enums.gamification.tienda_enums import (
    CategoriaItem, 
    RarezaItem, 
    MetodoAdquisicion
)

logger = logging.getLogger(__name__)


class TiendaService:
    """
    Servicio para gestión de tienda virtual y economía de items.
    
    Este servicio implementa la lógica de negocio para:
    - Consultar catálogo filtrado (categoría, rareza, disponibilidad)
    - Validar y procesar compras con puntos
    - Gestionar inventario del usuario
    - Equipar/desequipar items en avatar
    - Usar items consumibles
    - Auditar transacciones
    
    Attributes:
        db: Sesión de base de datos
    
    Example:
        >>> service = TiendaService(db)
        >>> items = await service.get_catalogo(
        ...     categoria=CategoriaItem.ROPA_SUPERIOR,
        ...     rareza=RarezaItem.RARO
        ... )
        >>> resultado = await service.comprar_item(
        ...     usuario_id=user_id,
        ...     item_id=item_id,
        ...     cantidad=1
        ... )
    """
    
    def __init__(self, db: AsyncSession):
        """
        Inicializa el servicio de tienda.
        
        Args:
            db: Sesión asíncrona de base de datos
        """
        self.db = db
        logger.info("TiendaService inicializado")
    
    # =============================================================================
    # CATÁLOGO Y CONSULTAS
    # =============================================================================
    
    async def get_catalogo(
        self,
        categoria: Optional[CategoriaItem] = None,
        rareza: Optional[RarezaItem] = None,
        es_funcional: Optional[bool] = None,
        nivel_minimo: Optional[int] = None,
        precio_max: Optional[int] = None,
        solo_disponibles: bool = True,
        limit: int = 100,
        offset: int = 0
    ) -> List[TiendaItem]:
        """
        Obtiene el catálogo de items con filtros opcionales.
        
        Args:
            categoria: Filtrar por categoría
            rareza: Filtrar por rareza
            es_funcional: Filtrar items funcionales (congeladores, etc)
            nivel_minimo: Filtrar por nivel mínimo requerido
            precio_max: Precio máximo en puntos
            solo_disponibles: Solo items activos y con stock
            limit: Cantidad máxima de resultados
            offset: Offset para paginación
        
        Returns:
            Lista de TiendaItem que cumplen los criterios
        """
        query = select(TiendaItem).options(
            selectinload(TiendaItem.avatar_asset)
        )
        
        # Filtros
        filters = []
        
        if solo_disponibles:
            filters.append(TiendaItem.es_activo == True)
            filters.append(
                or_(
                    TiendaItem.es_limitado == False,
                    and_(
                        TiendaItem.es_limitado == True,
                        TiendaItem.stock_disponible > 0
                    )
                )
            )
        
        if categoria:
            filters.append(TiendaItem.categoria == categoria)
        
        if rareza:
            filters.append(TiendaItem.rareza == rareza)
        
        if es_funcional is not None:
            filters.append(TiendaItem.es_funcional == es_funcional)
        
        if nivel_minimo is not None:
            filters.append(TiendaItem.nivel_minimo_requerido <= nivel_minimo)
        
        if precio_max is not None:
            filters.append(TiendaItem.precio_puntos <= precio_max)
        
        if filters:
            query = query.where(and_(*filters))
        
        # Ordenar por rareza (legendario primero) y luego por precio
        query = query.order_by(
            TiendaItem.rareza.desc(),
            TiendaItem.precio_puntos.desc()
        ).limit(limit).offset(offset)
        
        result = await self.db.execute(query)
        items = result.scalars().all()
        
        logger.info(f"Catálogo consultado: {len(items)} items encontrados")
        return list(items)
    
    async def get_item_by_id(self, item_id: UUID) -> Optional[TiendaItem]:
        """
        Obtiene un item por su ID con todos sus detalles.
        
        Args:
            item_id: UUID del item
        
        Returns:
            TiendaItem o None si no existe
        """
        query = select(TiendaItem).where(
            TiendaItem.item_id == item_id
        ).options(
            selectinload(TiendaItem.avatar_asset)
        )
        
        result = await self.db.execute(query)
        item = result.scalar_one_or_none()
        
        return item
    
    # =============================================================================
    # COMPRAS Y TRANSACCIONES
    # =============================================================================
    
    async def comprar_item(
        self,
        usuario_id: UUID,
        item_id: UUID,
        cantidad: int = 1,
        ip_usuario: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Procesa la compra de un item.
        
        Validaciones:
        1. Item existe y está activo
        2. Item está disponible (fecha, stock)
        3. Usuario tiene suficientes puntos
        4. Usuario cumple nivel mínimo
        5. Stock suficiente si es limitado
        
        Args:
            usuario_id: UUID del usuario comprador
            item_id: UUID del item a comprar
            cantidad: Cantidad a comprar (para consumibles)
            ip_usuario: IP para auditoría
        
        Returns:
            Dict con resultado:
            {
                "exitosa": True,
                "transaccion_id": UUID,
                "puntos_gastados": 150,
                "puntos_restantes": 850,
                "inventario_id": UUID,
                "mensaje": "Compra exitosa"
            }
        
        Raises:
            ValueError: Si la compra no puede realizarse
        """
        # 1. Obtener item
        item = await self.get_item_by_id(item_id)
        if not item:
            raise ValueError(f"Item {item_id} no encontrado")
        
        if not item.es_activo:
            raise ValueError(f"Item '{item.nombre}' no está disponible")
        
        # 2. Verificar disponibilidad temporal y stock
        if not item.esta_disponible:
            raise ValueError(
                f"Item '{item.nombre}' no disponible en estas fechas"
            )
        
        if not item.tiene_stock:
            raise ValueError(f"Item '{item.nombre}' agotado")
        
        if item.es_limitado and item.stock_disponible < cantidad:
            raise ValueError(
                f"Stock insuficiente. Disponible: {item.stock_disponible}"
            )
        
        # 3. Obtener puntos del usuario
        query_puntos = select(UsuarioPuntos).where(
            UsuarioPuntos.usuario_id == usuario_id
        )
        result = await self.db.execute(query_puntos)
        usuario_puntos = result.scalar_one_or_none()
        
        if not usuario_puntos:
            raise ValueError("Usuario no tiene registro de puntos")
        
        # 4. Calcular costo total
        costo_total = item.precio_puntos * cantidad
        
        # 5. Verificar puntos suficientes
        if usuario_puntos.puntos_actuales < costo_total:
            raise ValueError(
                f"Puntos insuficientes. Necesitas {costo_total}, "
                f"tienes {usuario_puntos.puntos_actuales}"
            )
        
        # 6. Verificar nivel si es requerido
        if item.nivel_minimo_requerido and usuario_puntos.nivel < item.nivel_minimo_requerido:
            raise ValueError(
                f"Nivel insuficiente. Necesitas nivel {item.nivel_minimo_requerido}, "
                f"tienes nivel {usuario_puntos.nivel}"
            )
        
        # 7. Verificar si ya tiene el item (para items únicos)
        if not item.es_funcional:  # Items de avatar son únicos
            query_inventario = select(InventarioUsuario).where(
                and_(
                    InventarioUsuario.usuario_id == usuario_id,
                    InventarioUsuario.item_id == item_id
                )
            )
            result_inv = await self.db.execute(query_inventario)
            item_existente = result_inv.scalar_one_or_none()
            
            if item_existente:
                raise ValueError(
                    f"Ya posees el item '{item.nombre}'"
                )
        
        # 8. Deducir puntos
        puntos_antes = usuario_puntos.puntos_actuales
        usuario_puntos.puntos_actuales -= costo_total
        puntos_despues = usuario_puntos.puntos_actuales
        
        # 9. Agregar a inventario o actualizar cantidad
        query_inv = select(InventarioUsuario).where(
            and_(
                InventarioUsuario.usuario_id == usuario_id,
                InventarioUsuario.item_id == item_id
            )
        )
        result_inv = await self.db.execute(query_inv)
        inventario = result_inv.scalar_one_or_none()
        
        if inventario:
            # Item ya existe, aumentar cantidad (consumibles)
            inventario.cantidad += cantidad
            inventario_id = inventario.inventario_id
        else:
            # Crear nuevo registro en inventario
            inventario = InventarioUsuario(
                usuario_id=usuario_id,
                item_id=item_id,
                metodo_adquisicion=MetodoAdquisicion.COMPRA,
                precio_pagado=item.precio_puntos,
                cantidad=cantidad
            )
            self.db.add(inventario)
            await self.db.flush()
            inventario_id = inventario.inventario_id
        
        # 10. Reducir stock si es limitado
        if item.es_limitado:
            item.stock_disponible -= cantidad
        
        # 11. Registrar transacción exitosa
        transaccion = TransaccionTienda(
            usuario_id=usuario_id,
            item_id=item_id,
            tipo_transaccion="compra",
            cantidad=cantidad,
            puntos=costo_total,
            puntos_antes=puntos_antes,
            puntos_despues=puntos_despues,
            exitosa=True,
            ip_usuario=ip_usuario
        )
        self.db.add(transaccion)
        
        # 12. Commit
        await self.db.commit()
        
        logger.info(
            f"Compra exitosa: Usuario {usuario_id} compró {cantidad}x "
            f"'{item.nombre}' por {costo_total} puntos"
        )
        
        return {
            "exitosa": True,
            "transaccion_id": transaccion.transaccion_id,
            "puntos_gastados": costo_total,
            "puntos_restantes": puntos_despues,
            "inventario_id": inventario_id,
            "item": {
                "nombre": item.nombre,
                "rareza": item.rareza.value,
                "categoria": item.categoria.value
            },
            "mensaje": f"¡Compraste {cantidad}x {item.nombre}!"
        }
    
    async def _registrar_transaccion_fallida(
        self,
        usuario_id: UUID,
        item_id: UUID,
        cantidad: int,
        puntos: int,
        razon_fallo: str,
        ip_usuario: Optional[str] = None
    ):
        """
        Registra una transacción fallida para auditoría.
        
        Args:
            usuario_id: UUID del usuario
            item_id: UUID del item
            cantidad: Cantidad intentada
            puntos: Puntos que se iban a gastar
            razon_fallo: Motivo del fallo
            ip_usuario: IP del usuario
        """
        transaccion = TransaccionTienda(
            usuario_id=usuario_id,
            item_id=item_id,
            tipo_transaccion="compra",
            cantidad=cantidad,
            puntos=puntos,
            exitosa=False,
            razon_fallo=razon_fallo,
            ip_usuario=ip_usuario
        )
        self.db.add(transaccion)
        await self.db.commit()
    
    # =============================================================================
    # INVENTARIO
    # =============================================================================
    
    async def get_inventario_usuario(
        self,
        usuario_id: UUID,
        categoria: Optional[CategoriaItem] = None,
        solo_equipados: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Obtiene el inventario completo del usuario.
        
        Args:
            usuario_id: UUID del usuario
            categoria: Filtrar por categoría
            solo_equipados: Solo items equipados
        
        Returns:
            Lista de items con detalles:
            [{
                "inventario_id": UUID,
                "item": TiendaItem,
                "cantidad": 1,
                "esta_equipado": True,
                "fecha_adquisicion": datetime,
                "veces_usado": 5
            }]
        """
        query = select(InventarioUsuario).where(
            InventarioUsuario.usuario_id == usuario_id
        ).options(
            selectinload(InventarioUsuario.item).selectinload(TiendaItem.avatar_asset)
        )
        
        if solo_equipados:
            query = query.where(InventarioUsuario.esta_equipado == True)
        
        if categoria:
            query = query.join(TiendaItem).where(
                TiendaItem.categoria == categoria
            )
        
        query = query.order_by(
            InventarioUsuario.esta_equipado.desc(),
            InventarioUsuario.fecha_adquisicion.desc()
        )
        
        result = await self.db.execute(query)
        inventario_items = result.scalars().all()
        
        return [
            {
                "inventario_id": inv.inventario_id,
                "item": inv.item.to_dict() if inv.item else {},
                "cantidad": inv.cantidad,
                "esta_equipado": inv.esta_equipado,
                "fecha_adquisicion": inv.fecha_adquisicion,
                "metodo_adquisicion": inv.metodo_adquisicion.value,
                "veces_usado": inv.veces_usado,
                "disponible": inv.esta_disponible
            }
            for inv in inventario_items
        ]
    
    # =============================================================================
    # EQUIPAMIENTO
    # =============================================================================
    
    async def equipar_item(
        self,
        usuario_id: UUID,
        inventario_id: UUID
    ) -> Dict[str, Any]:
        """
        Equipa un item del inventario en el avatar del usuario.
        
        Solo se puede equipar un item por categoría (ej: un cabello, una camisa)
        
        Args:
            usuario_id: UUID del usuario
            inventario_id: UUID del item en inventario
        
        Returns:
            Dict con resultado:
            {
                "exitosa": True,
                "item_equipado": "Cabello Azul",
                "categoria": "cabello",
                "item_desequipado": "Cabello Rojo" (si había otro)
            }
        
        Raises:
            ValueError: Si el item no puede equiparse
        """
        # 1. Obtener item del inventario
        query = select(InventarioUsuario).where(
            and_(
                InventarioUsuario.inventario_id == inventario_id,
                InventarioUsuario.usuario_id == usuario_id
            )
        ).options(selectinload(InventarioUsuario.item))
        
        result = await self.db.execute(query)
        inventario = result.scalar_one_or_none()
        
        if not inventario:
            raise ValueError("Item no encontrado en tu inventario")
        
        if not inventario.esta_disponible:
            raise ValueError("Item no disponible (consumido o sin stock)")
        
        item = inventario.item
        
        # 2. Verificar que no sea funcional (solo cosméticos se equipan)
        if item.es_funcional:
            raise ValueError(
                "Los items funcionales no se equipan, se usan con usar_item()"
            )
        
        # 3. Desequipar item anterior de la misma categoría
        query_equipado = select(InventarioUsuario).where(
            and_(
                InventarioUsuario.usuario_id == usuario_id,
                InventarioUsuario.esta_equipado == True
            )
        ).options(selectinload(InventarioUsuario.item))
        
        result_equipado = await self.db.execute(query_equipado)
        items_equipados = result_equipado.scalars().all()
        
        item_desequipado = None
        for inv_equipado in items_equipados:
            if inv_equipado.item.categoria == item.categoria:
                inv_equipado.esta_equipado = False
                item_desequipado = inv_equipado.item.nombre
        
        # 4. Equipar nuevo item
        inventario.esta_equipado = True
        inventario.fecha_ultimo_uso = datetime.now(timezone.utc)
        inventario.veces_usado += 1
        
        await self.db.commit()
        
        logger.info(
            f"Item equipado: Usuario {usuario_id} equipó '{item.nombre}' "
            f"(categoría: {item.categoria.value})"
        )
        
        return {
            "exitosa": True,
            "item_equipado": item.nombre,
            "categoria": item.categoria.value,
            "item_desequipado": item_desequipado,
            "mensaje": f"¡{item.nombre} equipado!"
        }
    
    async def desequipar_item(
        self,
        usuario_id: UUID,
        inventario_id: UUID
    ) -> Dict[str, Any]:
        """
        Desequipa un item del avatar.
        
        Args:
            usuario_id: UUID del usuario
            inventario_id: UUID del item en inventario
        
        Returns:
            Dict con resultado
        """
        query = select(InventarioUsuario).where(
            and_(
                InventarioUsuario.inventario_id == inventario_id,
                InventarioUsuario.usuario_id == usuario_id
            )
        ).options(selectinload(InventarioUsuario.item))
        
        result = await self.db.execute(query)
        inventario = result.scalar_one_or_none()
        
        if not inventario:
            raise ValueError("Item no encontrado en tu inventario")
        
        if not inventario.esta_equipado:
            raise ValueError("Este item no está equipado")
        
        inventario.esta_equipado = False
        await self.db.commit()
        
        return {
            "exitosa": True,
            "item_desequipado": inventario.item.nombre,
            "mensaje": f"{inventario.item.nombre} desequipado"
        }
    
    # =============================================================================
    # ITEMS FUNCIONALES (CONSUMIBLES)
    # =============================================================================
    
    async def usar_item_consumible(
        self,
        usuario_id: UUID,
        inventario_id: UUID
    ) -> Dict[str, Any]:
        """
        Usa un item funcional/consumible (congelador racha, recuperación, etc).
        
        Args:
            usuario_id: UUID del usuario
            inventario_id: UUID del item en inventario
        
        Returns:
            Dict con resultado:
            {
                "exitosa": True,
                "item_usado": "Congelador de Racha",
                "efecto": {...},
                "cantidad_restante": 0,
                "mensaje": "Efecto aplicado"
            }
        
        Raises:
            ValueError: Si el item no puede usarse
        """
        query = select(InventarioUsuario).where(
            and_(
                InventarioUsuario.inventario_id == inventario_id,
                InventarioUsuario.usuario_id == usuario_id
            )
        ).options(selectinload(InventarioUsuario.item))
        
        result = await self.db.execute(query)
        inventario = result.scalar_one_or_none()
        
        if not inventario:
            raise ValueError("Item no encontrado en tu inventario")
        
        item = inventario.item
        
        if not item.es_funcional:
            raise ValueError(
                "Este item no es funcional. Usa equipar_item() para items cosméticos"
            )
        
        if inventario.cantidad <= 0:
            raise ValueError("No tienes unidades disponibles de este item")
        
        # Usar item (reduce cantidad)
        resultado = inventario.usar_item()
        
        # Aplicar efecto según el tipo de item
        efecto_aplicado = item.efecto_json or {}
        
        await self.db.commit()
        
        logger.info(
            f"Item usado: Usuario {usuario_id} usó '{item.nombre}'. "
            f"Cantidad restante: {inventario.cantidad}"
        )
        
        return {
            "exitosa": True,
            "item_usado": item.nombre,
            "efecto": efecto_aplicado,
            "cantidad_restante": inventario.cantidad,
            "mensaje": f"¡{item.nombre} usado! {efecto_aplicado.get('descripcion', '')}"
        }
    
    # =============================================================================
    # TRANSACCIONES Y ESTADÍSTICAS
    # =============================================================================
    
    async def get_historial_transacciones(
        self,
        usuario_id: UUID,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Obtiene el historial de transacciones del usuario.
        
        Args:
            usuario_id: UUID del usuario
            limit: Cantidad máxima de transacciones
        
        Returns:
            Lista de transacciones con detalles
        """
        query = select(TransaccionTienda).where(
            TransaccionTienda.usuario_id == usuario_id
        ).options(
            selectinload(TransaccionTienda.item)
        ).order_by(
            TransaccionTienda.fecha_transaccion.desc()
        ).limit(limit)
        
        result = await self.db.execute(query)
        transacciones = result.scalars().all()
        
        return [
            {
                "transaccion_id": t.transaccion_id,
                "tipo": t.tipo_transaccion.value,
                "item": t.item.nombre if t.item else "Desconocido",
                "cantidad": t.cantidad,
                "puntos": t.puntos,
                "exitosa": t.exitosa,
                "fecha": t.fecha_transaccion,
                "razon_fallo": t.razon_fallo
            }
            for t in transacciones
        ]
    
    async def get_estadisticas_tienda(
        self,
        usuario_id: UUID
    ) -> Dict[str, Any]:
        """
        Obtiene estadísticas de la tienda para el usuario.
        
        Returns:
            Dict con estadísticas:
            {
                "items_poseidos": 15,
                "items_equipados": 5,
                "puntos_gastados_total": 2500,
                "transacciones_exitosas": 15,
                "transacciones_fallidas": 2,
                "item_mas_caro": {...},
                "rareza_mas_comun": "RARO"
            }
        """
        # Items poseídos
        query_inv = select(func.count(InventarioUsuario.inventario_id)).where(
            InventarioUsuario.usuario_id == usuario_id
        )
        result_count = await self.db.execute(query_inv)
        items_poseidos = result_count.scalar() or 0
        
        # Items equipados
        query_equipados = select(func.count(InventarioUsuario.inventario_id)).where(
            and_(
                InventarioUsuario.usuario_id == usuario_id,
                InventarioUsuario.esta_equipado == True
            )
        )
        result_equipados = await self.db.execute(query_equipados)
        items_equipados = result_equipados.scalar() or 0
        
        # Puntos gastados (transacciones exitosas)
        query_puntos = select(func.sum(TransaccionTienda.puntos)).where(
            and_(
                TransaccionTienda.usuario_id == usuario_id,
                TransaccionTienda.exitosa == True
            )
        )
        result_puntos = await self.db.execute(query_puntos)
        puntos_gastados = result_puntos.scalar() or 0
        
        # Transacciones
        query_exitosas = select(func.count(TransaccionTienda.transaccion_id)).where(
            and_(
                TransaccionTienda.usuario_id == usuario_id,
                TransaccionTienda.exitosa == True
            )
        )
        result_exitosas = await self.db.execute(query_exitosas)
        transacciones_exitosas = result_exitosas.scalar() or 0
        
        query_fallidas = select(func.count(TransaccionTienda.transaccion_id)).where(
            and_(
                TransaccionTienda.usuario_id == usuario_id,
                TransaccionTienda.exitosa == False
            )
        )
        result_fallidas = await self.db.execute(query_fallidas)
        transacciones_fallidas = result_fallidas.scalar() or 0
        
        return {
            "items_poseidos": items_poseidos,
            "items_equipados": items_equipados,
            "puntos_gastados_total": int(puntos_gastados),
            "transacciones_exitosas": transacciones_exitosas,
            "transacciones_fallidas": transacciones_fallidas
        }
