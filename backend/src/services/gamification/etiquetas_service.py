"""
Servicio de gestión de etiquetas de perfil (badges).

Este servicio maneja toda la lógica relacionada con:
- Consulta de etiquetas disponibles
- Compra de etiquetas con puntos
- Equipamiento de etiquetas (máximo 5)
- Sistema de evolución de etiquetas
- Verificación de requisitos y progreso
- Otorgamiento automático por logros

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

from src.models.gamification.etiqueta_perfil import EtiquetaPerfil
from src.models.gamification.usuario_etiqueta import UsuarioEtiqueta
from src.models.gamification.usuario_puntos import UsuarioPuntos
from src.enums.gamification.etiqueta_enums import (
    CategoriaEtiqueta,
    RarezaEtiqueta,
    TipoRequisito
)

logger = logging.getLogger(__name__)


class EtiquetasService:
    """
    Servicio para gestión de etiquetas de perfil (badges/achievements).
    
    Este servicio implementa la lógica de negocio para:
    - Consultar catálogo de etiquetas
    - Comprar etiquetas con puntos
    - Equipar/desequipar etiquetas (máximo 5)
    - Sistema de evolución de etiquetas
    - Verificar progreso de requisitos
    - Otorgar etiquetas automáticamente por logros
    
    Attributes:
        db: Sesión de base de datos
    
    Example:
        >>> service = EtiquetasService(db)
        >>> etiquetas = await service.get_catalogo_etiquetas(
        ...     categoria=CategoriaEtiqueta.PROGRAMACION,
        ...     rareza=RarezaEtiqueta.EPICO
        ... )
        >>> await service.comprar_etiqueta(
        ...     usuario_id=user_id,
        ...     etiqueta_id=etiqueta_id
        ... )
        >>> await service.equipar_etiquetas(
        ...     usuario_id=user_id,
        ...     etiquetas_ids=[id1, id2, id3]  # Orden 1, 2, 3
        ... )
    """
    
    def __init__(self, db: AsyncSession):
        """
        Inicializa el servicio de etiquetas.
        
        Args:
            db: Sesión asíncrona de base de datos
        """
        self.db = db
        logger.info("EtiquetasService inicializado")
    
    # =============================================================================
    # CATÁLOGO Y CONSULTAS
    # =============================================================================
    
    async def get_catalogo_etiquetas(
        self,
        categoria: Optional[CategoriaEtiqueta] = None,
        rareza: Optional[RarezaEtiqueta] = None,
        solo_comprables: bool = False,
        solo_activas: bool = True,
        limit: int = 100,
        offset: int = 0
    ) -> List[EtiquetaPerfil]:
        """
        Obtiene el catálogo de etiquetas con filtros opcionales.
        
        Args:
            categoria: Filtrar por categoría
            rareza: Filtrar por rareza
            solo_comprables: Solo etiquetas comprables con puntos
            solo_activas: Solo etiquetas activas
            limit: Cantidad máxima de resultados
            offset: Offset para paginación
        
        Returns:
            Lista de EtiquetaPerfil que cumplen los criterios
        """
        query = select(EtiquetaPerfil).options(
            selectinload(EtiquetaPerfil.etiqueta_evolucion)
        )
        
        filters = []
        
        if solo_activas:
            filters.append(EtiquetaPerfil.es_activa == True)
        
        if categoria:
            filters.append(EtiquetaPerfil.categoria == categoria)
        
        if rareza:
            filters.append(EtiquetaPerfil.rareza == rareza)
        
        if solo_comprables:
            filters.append(EtiquetaPerfil.es_comprable == True)
        
        if filters:
            query = query.where(and_(*filters))
        
        # Ordenar por rareza (legendario primero) y luego por orden
        query = query.order_by(
            EtiquetaPerfil.rareza.desc(),
            EtiquetaPerfil.orden.asc()
        ).limit(limit).offset(offset)
        
        result = await self.db.execute(query)
        etiquetas = result.scalars().all()
        
        logger.info(f"Catálogo de etiquetas: {len(etiquetas)} encontradas")
        return list(etiquetas)
    
    async def get_etiqueta_by_id(
        self,
        etiqueta_id: UUID
    ) -> Optional[EtiquetaPerfil]:
        """
        Obtiene una etiqueta por su ID con todos sus detalles.
        
        Args:
            etiqueta_id: UUID de la etiqueta
        
        Returns:
            EtiquetaPerfil o None si no existe
        """
        query = select(EtiquetaPerfil).where(
            EtiquetaPerfil.etiqueta_id == etiqueta_id
        ).options(
            selectinload(EtiquetaPerfil.etiqueta_evolucion)
        )
        
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    # =============================================================================
    # COMPRA DE ETIQUETAS
    # =============================================================================
    
    async def comprar_etiqueta(
        self,
        usuario_id: UUID,
        etiqueta_id: UUID
    ) -> Dict[str, Any]:
        """
        Compra una etiqueta con puntos.
        
        Validaciones:
        1. Etiqueta existe y está activa
        2. Etiqueta es comprable
        3. Usuario tiene suficientes puntos
        4. Usuario no tiene ya la etiqueta
        
        Args:
            usuario_id: UUID del usuario
            etiqueta_id: UUID de la etiqueta
        
        Returns:
            Dict con resultado:
            {
                "exitosa": True,
                "etiqueta": {...},
                "puntos_gastados": 500,
                "puntos_restantes": 1500,
                "mensaje": "Etiqueta adquirida"
            }
        
        Raises:
            ValueError: Si la compra no puede realizarse
        """
        # 1. Obtener etiqueta
        etiqueta = await self.get_etiqueta_by_id(etiqueta_id)
        if not etiqueta:
            raise ValueError("Etiqueta no encontrada")
        
        if not etiqueta.es_activa:
            raise ValueError("Etiqueta no disponible")
        
        if not etiqueta.es_comprable:
            raise ValueError(
                "Esta etiqueta no se puede comprar, se obtiene por logro"
            )
        
        # 2. Verificar que no la tenga ya
        query_usuario_etiqueta = select(UsuarioEtiqueta).where(
            and_(
                UsuarioEtiqueta.usuario_id == usuario_id,
                UsuarioEtiqueta.etiqueta_id == etiqueta_id
            )
        )
        result = await self.db.execute(query_usuario_etiqueta)
        ya_tiene = result.scalar_one_or_none()
        
        if ya_tiene:
            raise ValueError("Ya tienes esta etiqueta")
        
        # 3. Obtener puntos del usuario
        query_puntos = select(UsuarioPuntos).where(
            UsuarioPuntos.usuario_id == usuario_id
        )
        result_puntos = await self.db.execute(query_puntos)
        usuario_puntos = result_puntos.scalar_one_or_none()
        
        if not usuario_puntos:
            raise ValueError("Usuario no tiene registro de puntos")
        
        # 4. Verificar puntos suficientes
        if usuario_puntos.puntos_actuales < etiqueta.precio_puntos:
            raise ValueError(
                f"Puntos insuficientes. Necesitas {etiqueta.precio_puntos}, "
                f"tienes {usuario_puntos.puntos_actuales}"
            )
        
        # 5. Deducir puntos
        puntos_antes = usuario_puntos.puntos_actuales
        usuario_puntos.puntos_actuales -= etiqueta.precio_puntos
        puntos_despues = usuario_puntos.puntos_actuales
        
        # 6. Agregar etiqueta al usuario
        usuario_etiqueta = UsuarioEtiqueta(
            usuario_id=usuario_id,
            etiqueta_id=etiqueta_id,
            metodo_obtencion="compra"
        )
        self.db.add(usuario_etiqueta)
        
        await self.db.commit()
        
        logger.info(
            f"Etiqueta comprada: Usuario {usuario_id} compró '{etiqueta.nombre}' "
            f"por {etiqueta.precio_puntos} puntos"
        )
        
        return {
            "exitosa": True,
            "etiqueta": etiqueta.to_dict(),
            "puntos_gastados": etiqueta.precio_puntos,
            "puntos_restantes": puntos_despues,
            "mensaje": f"¡Etiqueta '{etiqueta.nombre}' adquirida!"
        }
    
    async def otorgar_etiqueta_por_logro(
        self,
        usuario_id: UUID,
        etiqueta_id: UUID,
        motivo: str = "Logro completado"
    ) -> Dict[str, Any]:
        """
        Otorga una etiqueta automáticamente por logro.
        
        Args:
            usuario_id: UUID del usuario
            etiqueta_id: UUID de la etiqueta
            motivo: Descripción del logro
        
        Returns:
            Dict con resultado
        """
        # Verificar que no la tenga
        query_usuario_etiqueta = select(UsuarioEtiqueta).where(
            and_(
                UsuarioEtiqueta.usuario_id == usuario_id,
                UsuarioEtiqueta.etiqueta_id == etiqueta_id
            )
        )
        result = await self.db.execute(query_usuario_etiqueta)
        ya_tiene = result.scalar_one_or_none()
        
        if ya_tiene:
            return {
                "exitosa": False,
                "mensaje": "Usuario ya tiene esta etiqueta"
            }
        
        # Obtener etiqueta
        etiqueta = await self.get_etiqueta_by_id(etiqueta_id)
        if not etiqueta:
            raise ValueError("Etiqueta no encontrada")
        
        # Otorgar etiqueta
        usuario_etiqueta = UsuarioEtiqueta(
            usuario_id=usuario_id,
            etiqueta_id=etiqueta_id,
            metodo_obtencion="logro"
        )
        self.db.add(usuario_etiqueta)
        await self.db.commit()
        
        logger.info(
            f"Etiqueta otorgada: Usuario {usuario_id} recibió '{etiqueta.nombre}' "
            f"por logro: {motivo}"
        )
        
        return {
            "exitosa": True,
            "etiqueta": etiqueta.to_dict(),
            "motivo": motivo,
            "mensaje": f"¡Desbloqueaste '{etiqueta.nombre}'!"
        }
    
    # =============================================================================
    # GESTIÓN DE ETIQUETAS DEL USUARIO
    # =============================================================================
    
    async def get_etiquetas_usuario(
        self,
        usuario_id: UUID,
        solo_equipadas: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Obtiene las etiquetas del usuario.
        
        Args:
            usuario_id: UUID del usuario
            solo_equipadas: Solo etiquetas equipadas
        
        Returns:
            Lista de etiquetas con detalles:
            [{
                "usuario_etiqueta_id": UUID,
                "etiqueta": {...},
                "esta_equipada": True,
                "orden_visualizacion": 1,
                "fecha_obtencion": datetime,
                "veces_equipada": 5,
                "progreso_evolucion": {...}
            }]
        """
        query = select(UsuarioEtiqueta).where(
            UsuarioEtiqueta.usuario_id == usuario_id
        ).options(
            selectinload(UsuarioEtiqueta.etiqueta)
        )
        
        if solo_equipadas:
            query = query.where(UsuarioEtiqueta.esta_equipada == True)
        
        query = query.order_by(
            UsuarioEtiqueta.esta_equipada.desc(),
            UsuarioEtiqueta.orden_visualizacion.asc(),
            UsuarioEtiqueta.fecha_obtencion.desc()
        )
        
        result = await self.db.execute(query)
        usuario_etiquetas = result.scalars().all()
        
        return [
            {
                "usuario_etiqueta_id": ue.usuario_etiqueta_id,
                "etiqueta": ue.etiqueta.to_dict() if ue.etiqueta else {},
                "esta_equipada": ue.esta_equipada,
                "orden_visualizacion": ue.orden_visualizacion,
                "fecha_obtencion": ue.fecha_obtencion,
                "metodo_obtencion": ue.metodo_obtencion,
                "veces_equipada": ue.veces_equipada,
                "progreso_evolucion": ue.progreso_evolucion
            }
            for ue in usuario_etiquetas
        ]
    
    # =============================================================================
    # EQUIPAMIENTO (MÁXIMO 5 ETIQUETAS)
    # =============================================================================
    
    async def equipar_etiquetas(
        self,
        usuario_id: UUID,
        etiquetas_ids: List[UUID]
    ) -> Dict[str, Any]:
        """
        Equipa hasta 5 etiquetas en orden específico.
        
        Args:
            usuario_id: UUID del usuario
            etiquetas_ids: Lista de UUIDs (máximo 5), orden determina visualización
        
        Returns:
            Dict con resultado:
            {
                "exitosa": True,
                "etiquetas_equipadas": 3,
                "orden": [
                    {"orden": 1, "nombre": "Python Master"},
                    {"orden": 2, "nombre": "Estudiante del Mes"},
                    {"orden": 3, "nombre": "Racha 30 Días"}
                ]
            }
        
        Raises:
            ValueError: Si hay más de 5 etiquetas o alguna no pertenece al usuario
        """
        # Validar cantidad
        if len(etiquetas_ids) > 5:
            raise ValueError("Solo puedes equipar máximo 5 etiquetas")
        
        # Desequipar todas las etiquetas actuales
        query_desequipar = select(UsuarioEtiqueta).where(
            and_(
                UsuarioEtiqueta.usuario_id == usuario_id,
                UsuarioEtiqueta.esta_equipada == True
            )
        )
        result_desequipar = await self.db.execute(query_desequipar)
        etiquetas_actuales = result_desequipar.scalars().all()
        
        for etiqueta_actual in etiquetas_actuales:
            etiqueta_actual.desequipar()
        
        # Equipar nuevas etiquetas en orden
        etiquetas_equipadas = []
        
        for orden, etiqueta_id in enumerate(etiquetas_ids, start=1):
            # Obtener usuario_etiqueta
            query_etiqueta = select(UsuarioEtiqueta).where(
                and_(
                    UsuarioEtiqueta.usuario_id == usuario_id,
                    UsuarioEtiqueta.etiqueta_id == etiqueta_id
                )
            ).options(selectinload(UsuarioEtiqueta.etiqueta))
            
            result_etiqueta = await self.db.execute(query_etiqueta)
            usuario_etiqueta = result_etiqueta.scalar_one_or_none()
            
            if not usuario_etiqueta:
                raise ValueError(
                    f"No tienes la etiqueta con ID {etiqueta_id}"
                )
            
            # Equipar con orden
            usuario_etiqueta.equipar(orden)
            
            etiquetas_equipadas.append({
                "orden": orden,
                "nombre": usuario_etiqueta.etiqueta.nombre,
                "rareza": usuario_etiqueta.etiqueta.rareza.value
            })
        
        await self.db.commit()
        
        logger.info(
            f"Etiquetas equipadas: Usuario {usuario_id} equipó "
            f"{len(etiquetas_equipadas)} etiquetas"
        )
        
        return {
            "exitosa": True,
            "etiquetas_equipadas": len(etiquetas_equipadas),
            "orden": etiquetas_equipadas,
            "mensaje": f"¡{len(etiquetas_equipadas)} etiquetas equipadas!"
        }
    
    async def desequipar_todas_etiquetas(
        self,
        usuario_id: UUID
    ) -> Dict[str, Any]:
        """
        Desequipa todas las etiquetas del usuario.
        
        Args:
            usuario_id: UUID del usuario
        
        Returns:
            Dict con resultado
        """
        query = select(UsuarioEtiqueta).where(
            and_(
                UsuarioEtiqueta.usuario_id == usuario_id,
                UsuarioEtiqueta.esta_equipada == True
            )
        )
        result = await self.db.execute(query)
        etiquetas_equipadas = result.scalars().all()
        
        cantidad = 0
        for etiqueta in etiquetas_equipadas:
            etiqueta.desequipar()
            cantidad += 1
        
        await self.db.commit()
        
        return {
            "exitosa": True,
            "etiquetas_desequipadas": cantidad,
            "mensaje": f"{cantidad} etiquetas desequipadas"
        }
    
    # =============================================================================
    # SISTEMA DE EVOLUCIÓN
    # =============================================================================
    
    async def verificar_evolucion_disponible(
        self,
        usuario_id: UUID,
        etiqueta_id: UUID
    ) -> Dict[str, Any]:
        """
        Verifica si una etiqueta puede evolucionar.
        
        Args:
            usuario_id: UUID del usuario
            etiqueta_id: UUID de la etiqueta
        
        Returns:
            Dict con información:
            {
                "puede_evolucionar": True,
                "etiqueta_actual": {...},
                "etiqueta_evolucion": {...},
                "requisitos_cumplidos": True,
                "progreso": {...}
            }
        """
        # Obtener etiqueta del usuario
        query = select(UsuarioEtiqueta).where(
            and_(
                UsuarioEtiqueta.usuario_id == usuario_id,
                UsuarioEtiqueta.etiqueta_id == etiqueta_id
            )
        ).options(
            selectinload(UsuarioEtiqueta.etiqueta).selectinload(
                EtiquetaPerfil.etiqueta_evolucion
            )
        )
        
        result = await self.db.execute(query)
        usuario_etiqueta = result.scalar_one_or_none()
        
        if not usuario_etiqueta:
            raise ValueError("No tienes esta etiqueta")
        
        etiqueta = usuario_etiqueta.etiqueta
        
        # Verificar si tiene evolución
        if not etiqueta.puede_evolucionar:
            return {
                "puede_evolucionar": False,
                "mensaje": "Esta etiqueta no tiene evolución disponible"
            }
        
        # Verificar requisitos
        requisitos = etiqueta.requisito_evolucion or {}
        requisitos_cumplidos = await self._verificar_requisitos(
            usuario_id,
            requisitos
        )
        
        return {
            "puede_evolucionar": True,
            "requisitos_cumplidos": requisitos_cumplidos["cumplidos"],
            "etiqueta_actual": etiqueta.to_dict(),
            "etiqueta_evolucion": etiqueta.etiqueta_evolucion.to_dict(),
            "requisitos": requisitos,
            "progreso": requisitos_cumplidos["progreso"]
        }
    
    async def evolucionar_etiqueta(
        self,
        usuario_id: UUID,
        etiqueta_id: UUID
    ) -> Dict[str, Any]:
        """
        Evoluciona una etiqueta a su siguiente nivel.
        
        Args:
            usuario_id: UUID del usuario
            etiqueta_id: UUID de la etiqueta actual
        
        Returns:
            Dict con resultado
        
        Raises:
            ValueError: Si no se puede evolucionar
        """
        # Verificar si puede evolucionar
        verificacion = await self.verificar_evolucion_disponible(
            usuario_id,
            etiqueta_id
        )
        
        if not verificacion["puede_evolucionar"]:
            raise ValueError("Esta etiqueta no puede evolucionar")
        
        if not verificacion["requisitos_cumplidos"]:
            raise ValueError(
                "No cumples los requisitos para evolucionar esta etiqueta"
            )
        
        # Obtener usuario_etiqueta
        query = select(UsuarioEtiqueta).where(
            and_(
                UsuarioEtiqueta.usuario_id == usuario_id,
                UsuarioEtiqueta.etiqueta_id == etiqueta_id
            )
        ).options(
            selectinload(UsuarioEtiqueta.etiqueta).selectinload(
                EtiquetaPerfil.etiqueta_evolucion
            )
        )
        
        result = await self.db.execute(query)
        usuario_etiqueta = result.scalar_one_or_none()
        
        etiqueta_actual = usuario_etiqueta.etiqueta
        etiqueta_nueva = etiqueta_actual.etiqueta_evolucion
        
        # Verificar que no tenga ya la evolución
        query_nueva = select(UsuarioEtiqueta).where(
            and_(
                UsuarioEtiqueta.usuario_id == usuario_id,
                UsuarioEtiqueta.etiqueta_id == etiqueta_nueva.etiqueta_id
            )
        )
        result_nueva = await self.db.execute(query_nueva)
        ya_tiene_nueva = result_nueva.scalar_one_or_none()
        
        if ya_tiene_nueva:
            raise ValueError("Ya tienes la versión evolucionada de esta etiqueta")
        
        # Crear nueva etiqueta evolucionada
        usuario_etiqueta_nueva = UsuarioEtiqueta(
            usuario_id=usuario_id,
            etiqueta_id=etiqueta_nueva.etiqueta_id,
            metodo_obtencion="evolucion"
        )
        self.db.add(usuario_etiqueta_nueva)
        
        # Si la actual estaba equipada, desequipar y equipar la nueva
        orden_anterior = None
        if usuario_etiqueta.esta_equipada:
            orden_anterior = usuario_etiqueta.orden_visualizacion
            usuario_etiqueta.desequipar()
        
        await self.db.flush()
        
        if orden_anterior:
            usuario_etiqueta_nueva.equipar(orden_anterior)
        
        await self.db.commit()
        
        logger.info(
            f"Etiqueta evolucionada: Usuario {usuario_id} evolucionó "
            f"'{etiqueta_actual.nombre}' a '{etiqueta_nueva.nombre}'"
        )
        
        return {
            "exitosa": True,
            "etiqueta_anterior": etiqueta_actual.to_dict(),
            "etiqueta_nueva": etiqueta_nueva.to_dict(),
            "mensaje": f"¡'{etiqueta_actual.nombre}' evolucionó a '{etiqueta_nueva.nombre}'!"
        }
    
    async def actualizar_progreso_evolucion(
        self,
        usuario_id: UUID,
        etiqueta_id: UUID,
        progreso: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Actualiza el progreso de evolución de una etiqueta.
        
        Args:
            usuario_id: UUID del usuario
            etiqueta_id: UUID de la etiqueta
            progreso: Dict con progreso actualizado
        
        Returns:
            Dict con resultado
        """
        query = select(UsuarioEtiqueta).where(
            and_(
                UsuarioEtiqueta.usuario_id == usuario_id,
                UsuarioEtiqueta.etiqueta_id == etiqueta_id
            )
        )
        
        result = await self.db.execute(query)
        usuario_etiqueta = result.scalar_one_or_none()
        
        if not usuario_etiqueta:
            raise ValueError("No tienes esta etiqueta")
        
        usuario_etiqueta.actualizar_progreso(progreso)
        await self.db.commit()
        
        return {
            "exitosa": True,
            "progreso": usuario_etiqueta.progreso_evolucion
        }
    
    # =============================================================================
    # VERIFICACIÓN DE REQUISITOS
    # =============================================================================
    
    async def _verificar_requisitos(
        self,
        usuario_id: UUID,
        requisitos: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Verifica si un usuario cumple ciertos requisitos.
        
        Args:
            usuario_id: UUID del usuario
            requisitos: Dict con requisitos a verificar
        
        Returns:
            Dict con resultado:
            {
                "cumplidos": True,
                "progreso": {
                    "tareas_completadas": {"actual": 50, "requerido": 30, "cumplido": True},
                    "puntos_totales": {"actual": 1000, "requerido": 1500, "cumplido": False}
                }
            }
        """
        # TODO: Implementar lógica de verificación según tipo de requisito
        # Por ahora retornamos True para permitir evoluciones
        
        progreso = {}
        todos_cumplidos = True
        
        for tipo_req, valor_requerido in requisitos.items():
            # Placeholder: verificar según tipo
            if tipo_req == "puntos_totales":
                query_puntos = select(UsuarioPuntos).where(
                    UsuarioPuntos.usuario_id == usuario_id
                )
                result = await self.db.execute(query_puntos)
                usuario_puntos = result.scalar_one_or_none()
                
                actual = usuario_puntos.puntos_totales if usuario_puntos else 0
                cumplido = actual >= valor_requerido
                
                progreso[tipo_req] = {
                    "actual": actual,
                    "requerido": valor_requerido,
                    "cumplido": cumplido
                }
                
                if not cumplido:
                    todos_cumplidos = False
        
        return {
            "cumplidos": todos_cumplidos,
            "progreso": progreso
        }
    
    # =============================================================================
    # ESTADÍSTICAS
    # =============================================================================
    
    async def get_estadisticas_etiquetas(
        self,
        usuario_id: UUID
    ) -> Dict[str, Any]:
        """
        Obtiene estadísticas de etiquetas del usuario.
        
        Returns:
            Dict con estadísticas
        """
        # Etiquetas totales
        query_total = select(func.count(UsuarioEtiqueta.usuario_etiqueta_id)).where(
            UsuarioEtiqueta.usuario_id == usuario_id
        )
        result_total = await self.db.execute(query_total)
        total_etiquetas = result_total.scalar() or 0
        
        # Etiquetas equipadas
        query_equipadas = select(func.count(UsuarioEtiqueta.usuario_etiqueta_id)).where(
            and_(
                UsuarioEtiqueta.usuario_id == usuario_id,
                UsuarioEtiqueta.esta_equipada == True
            )
        )
        result_equipadas = await self.db.execute(query_equipadas)
        etiquetas_equipadas = result_equipadas.scalar() or 0
        
        # Por método de obtención
        query_metodo = select(
            UsuarioEtiqueta.metodo_obtencion,
            func.count(UsuarioEtiqueta.usuario_etiqueta_id)
        ).where(
            UsuarioEtiqueta.usuario_id == usuario_id
        ).group_by(UsuarioEtiqueta.metodo_obtencion)
        
        result_metodo = await self.db.execute(query_metodo)
        por_metodo = dict(result_metodo.all())
        
        return {
            "total_etiquetas": total_etiquetas,
            "etiquetas_equipadas": etiquetas_equipadas,
            "por_metodo": por_metodo
        }
