"""
Servicio mejorado de gestión de rachas estilo Duolingo.

Este servicio maneja toda la lógica relacionada con:
- Verificación diaria de rachas
- Incremento/pérdida/recuperación de rachas
- Sistema de congeladores (protección temporal)
- Recompensas por milestones (7, 30, 100, 365 días)
- Recompensas semanales cíclicas
- Historial completo de eventos
- Notificaciones de racha en peligro

Author: GitHub Copilot & Team
Date: 31 octubre 2025
Version: 1.0.0
"""

import logging
from datetime import datetime, date, timezone, timedelta
from typing import Dict, Any, Optional, List
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from sqlalchemy.orm import selectinload

from src.models.gamification.racha_usuario import RachaUsuario
from src.models.gamification.historial_racha import HistorialRacha
from src.models.gamification.recompensa_racha import RecompensaRacha
from src.models.gamification.usuario_puntos import UsuarioPuntos
from src.models.gamification.insignia import Insignia
from src.models.gamification.usuario_insignia import UsuarioInsignia
from src.enums.gamification.racha_enums import (
    TipoEventoRacha,
    TipoMilestone,
    TipoActividadRacha
)

logger = logging.getLogger(__name__)


class RachaService:
    """
    Servicio para gestión avanzada de rachas de actividad.
    
    Este servicio implementa un sistema estilo Duolingo con:
    - Verificación diaria automática
    - Protección con congeladores
    - Recuperación de rachas perdidas
    - Recompensas por milestones (7, 30, 100, 365 días)
    - Recompensas semanales cíclicas (aumentan progresivamente)
    - Historial completo de eventos
    - Notificaciones proactivas
    
    Attributes:
        db: Sesión de base de datos
    
    Example:
        >>> service = RachaService(db)
        >>> resultado = await service.verificar_racha_diaria(
        ...     usuario_id=user_id,
        ...     tipo_actividad=TipoActividadRacha.TAREA_COMPLETADA
        ... )
        >>> if resultado["racha_perdida"]:
        ...     await service.recuperar_racha(usuario_id)
    """
    
    # Puntos por día de la semana (aumentan progresivamente)
    PUNTOS_SEMANALES = {
        1: 10,   # Lunes
        2: 15,   # Martes
        3: 20,   # Miércoles
        4: 25,   # Jueves
        5: 30,   # Viernes
        6: 40,   # Sábado
        7: 50    # Domingo (máximo)
    }
    
    def __init__(self, db: AsyncSession):
        """
        Inicializa el servicio de rachas.
        
        Args:
            db: Sesión asíncrona de base de datos
        """
        self.db = db
        logger.info("RachaService inicializado")
    
    # =============================================================================
    # VERIFICACIÓN Y GESTIÓN DE RACHA
    # =============================================================================
    
    async def get_racha_usuario(
        self,
        usuario_id: UUID,
        crear_si_no_existe: bool = True
    ) -> Optional[RachaUsuario]:
        """
        Obtiene la racha del usuario, creándola si no existe.
        
        Args:
            usuario_id: UUID del usuario
            crear_si_no_existe: Si crear registro si no existe
        
        Returns:
            RachaUsuario o None
        """
        query = select(RachaUsuario).where(
            RachaUsuario.usuario_id == usuario_id
        )
        
        result = self.db.execute(query)
        racha = result.scalar_one_or_none()
        
        if not racha and crear_si_no_existe:
            racha = RachaUsuario(usuario_id=usuario_id)
            self.db.add(racha)
            self.db.commit()
            self.db.refresh(racha)
            
            logger.info(f"Racha creada para usuario {usuario_id}")
        
        return racha
    
    async def verificar_racha_diaria(
        self,
        usuario_id: UUID,
        tipo_actividad: TipoActividadRacha = TipoActividadRacha.TAREA_COMPLETADA
    ) -> Dict[str, Any]:
        """
        Verifica y actualiza la racha del usuario al completar una actividad.
        
        Lógica:
        1. Si es el mismo día: no hacer nada
        2. Si es día consecutivo: incrementar racha
        3. Si pasó 1 día y está protegido: usar protección
        4. Si pasó más de 1 día: perder racha
        
        Args:
            usuario_id: UUID del usuario
            tipo_actividad: Tipo de actividad completada
        
        Returns:
            Dict con resultado:
            {
                "racha_incrementada": True,
                "racha_actual": 15,
                "racha_perdida": False,
                "proteccion_usada": False,
                "puntos_otorgados": 25,
                "dia_semana": 4,
                "milestone_alcanzado": None,
                "mensaje": "¡Racha de 15 días!"
            }
        """
        racha = await self.get_racha_usuario(usuario_id)
        hoy = date.today()
        
        # Si ya completó hoy, no hacer nada
        if racha.fecha_ultimo_dia == hoy:
            return {
                "racha_incrementada": False,
                "racha_actual": racha.racha_actual,
                "racha_perdida": False,
                "mensaje": "Ya completaste tu actividad hoy",
                "puntos_otorgados": 0
            }
        
        # Calcular días desde última actividad
        if racha.fecha_ultimo_dia:
            dias_diferencia = (hoy - racha.fecha_ultimo_dia).days
        else:
            dias_diferencia = 999  # Primera vez
        
        resultado = {
            "racha_incrementada": False,
            "racha_perdida": False,
            "proteccion_usada": False,
            "puntos_otorgados": 0,
            "milestone_alcanzado": None
        }
        
        # CASO 1: Día consecutivo (ayer o hoy si es primera vez)
        if dias_diferencia == 1 or racha.fecha_ultimo_dia is None:
            racha.incrementar_racha()
            resultado["racha_incrementada"] = True
            
            # Registrar evento
            await self._registrar_evento(
                usuario_id=usuario_id,
                tipo_evento=TipoEventoRacha.INCREMENTO,
                racha_anterior=racha.racha_actual - 1,
                racha_nueva=racha.racha_actual,
                descripcion=f"Actividad completada: {tipo_actividad.value}"
            )
            
            # Calcular puntos según día de la semana
            dia_semana = racha.dia_ciclo_semanal
            puntos = self.PUNTOS_SEMANALES.get(dia_semana, 10)
            
            # Otorgar puntos
            await self._otorgar_puntos(usuario_id, puntos, "Racha diaria")
            resultado["puntos_otorgados"] = puntos
            resultado["dia_semana"] = dia_semana
            
            # Verificar milestone
            milestone = await self._verificar_milestone(usuario_id, racha.racha_actual)
            if milestone:
                resultado["milestone_alcanzado"] = milestone
            
            logger.info(
                f"Racha incrementada: Usuario {usuario_id} tiene {racha.racha_actual} días"
            )
        
        # CASO 2: Más de 1 día, verificar protección
        elif dias_diferencia > 1:
            # Verificar si está protegido
            if racha.esta_protegida:
                # Usar protección
                resultado["proteccion_usada"] = True
                resultado["racha_actual"] = racha.racha_actual
                
                await self._registrar_evento(
                    usuario_id=usuario_id,
                    tipo_evento=TipoEventoRacha.CONGELACION,
                    racha_anterior=racha.racha_actual,
                    racha_nueva=racha.racha_actual,
                    descripcion=f"Protección usada (congelada hasta {racha.racha_congelada_hasta})"
                )
                
                logger.info(
                    f"Protección usada: Usuario {usuario_id} mantuvo racha de "
                    f"{racha.racha_actual} días"
                )
            else:
                # Perder racha
                racha_anterior = racha.racha_actual
                racha.resetear_racha()
                
                resultado["racha_perdida"] = True
                resultado["racha_anterior"] = racha_anterior
                
                await self._registrar_evento(
                    usuario_id=usuario_id,
                    tipo_evento=TipoEventoRacha.PERDIDA,
                    racha_anterior=racha_anterior,
                    racha_nueva=0,
                    descripcion=f"Racha perdida por inactividad ({dias_diferencia} días)"
                )
                
                logger.warning(
                    f"Racha perdida: Usuario {usuario_id} perdió racha de "
                    f"{racha_anterior} días"
                )
        
        # Actualizar fecha
        racha.fecha_ultimo_dia = hoy
        
        self.db.commit()
        
        resultado["racha_actual"] = racha.racha_actual
        resultado["mensaje"] = self._generar_mensaje_racha(resultado)
        
        return resultado
    
    # =============================================================================
    # RECUPERACIÓN DE RACHA
    # =============================================================================
    
    async def recuperar_racha(
        self,
        usuario_id: UUID
    ) -> Dict[str, Any]:
        """
        Recupera la racha usando una recuperación disponible.
        
        Args:
            usuario_id: UUID del usuario
        
        Returns:
            Dict con resultado
        
        Raises:
            ValueError: Si no puede recuperar
        """
        racha = await self.get_racha_usuario(usuario_id)
        
        if not racha.puede_recuperar:
            raise ValueError("No tienes recuperaciones disponibles")
        
        if racha.racha_actual > 0:
            raise ValueError("Tu racha no está perdida")
        
        # Obtener última racha del historial
        query_historial = select(HistorialRacha).where(
            and_(
                HistorialRacha.usuario_id == usuario_id,
                HistorialRacha.tipo_evento == TipoEventoRacha.PERDIDA
            )
        ).order_by(HistorialRacha.timestamp.desc()).limit(1)
        
        result = self.db.execute(query_historial)
        ultimo_evento = result.scalar_one_or_none()
        
        if not ultimo_evento:
            raise ValueError("No hay racha reciente para recuperar")
        
        # Recuperar racha
        racha_recuperada = ultimo_evento.racha_anterior
        racha.usar_recuperacion()
        racha.racha_actual = racha_recuperada
        racha.fecha_ultimo_dia = date.today()
        
        # Registrar evento
        await self._registrar_evento(
            usuario_id=usuario_id,
            tipo_evento=TipoEventoRacha.RECUPERACION,
            racha_anterior=0,
            racha_nueva=racha_recuperada,
            descripcion=f"Racha recuperada con item de recuperación"
        )
        
        self.db.commit()
        
        logger.info(
            f"Racha recuperada: Usuario {usuario_id} recuperó {racha_recuperada} días. "
            f"Recuperaciones restantes: {racha.recuperaciones_disponibles}"
        )
        
        return {
            "exitosa": True,
            "racha_recuperada": racha_recuperada,
            "recuperaciones_restantes": racha.recuperaciones_disponibles,
            "mensaje": f"¡Racha de {racha_recuperada} días recuperada!"
        }
    
    # =============================================================================
    # CONGELADORES (PROTECCIÓN)
    # =============================================================================
    
    async def activar_congelador(
        self,
        usuario_id: UUID,
        dias: int = 1
    ) -> Dict[str, Any]:
        """
        Activa protección de racha por X días.
        
        Args:
            usuario_id: UUID del usuario
            dias: Días de protección (default: 1)
        
        Returns:
            Dict con resultado
        """
        racha = await self.get_racha_usuario(usuario_id)
        
        racha.activar_congelador(dias)
        
        await self._registrar_evento(
            usuario_id=usuario_id,
            tipo_evento=TipoEventoRacha.CONGELACION,
            racha_anterior=racha.racha_actual,
            racha_nueva=racha.racha_actual,
            descripcion=f"Congelador activado por {dias} días (hasta {racha.racha_congelada_hasta})"
        )
        
        self.db.commit()
        
        logger.info(
            f"Congelador activado: Usuario {usuario_id} protegido hasta "
            f"{racha.racha_congelada_hasta}"
        )
        
        return {
            "exitosa": True,
            "protegido_hasta": racha.racha_congelada_hasta,
            "dias_proteccion": dias,
            "mensaje": f"Racha protegida por {dias} días"
        }
    
    # =============================================================================
    # MILESTONES Y RECOMPENSAS
    # =============================================================================
    
    async def _verificar_milestone(
        self,
        usuario_id: UUID,
        racha_actual: int
    ) -> Optional[Dict[str, Any]]:
        """
        Verifica si se alcanzó un milestone y otorga recompensa.
        
        Args:
            usuario_id: UUID del usuario
            racha_actual: Días de racha actuales
        
        Returns:
            Dict con milestone alcanzado o None
        """
        # Buscar milestone para este número de días
        query = select(RecompensaRacha).where(
            and_(
                RecompensaRacha.dias_requeridos == racha_actual,
                RecompensaRacha.es_activa == True
            )
        )
        
        result = self.db.execute(query)
        recompensa = result.scalar_one_or_none()
        
        if not recompensa:
            return None
        
        # Verificar si ya recibió esta recompensa
        racha = await self.get_racha_usuario(usuario_id)
        if racha.ultima_recompensa_dia == racha_actual and not recompensa.es_repetible:
            return None
        
        # Otorgar puntos
        await self._otorgar_puntos(
            usuario_id,
            recompensa.puntos_recompensa,
            f"Milestone {racha_actual} días"
        )
        
        # Otorgar insignia si tiene
        if recompensa.insignia_id:
            await self._otorgar_insignia(usuario_id, recompensa.insignia_id)
        
        # Actualizar última recompensa
        racha.ultima_recompensa_dia = racha_actual
        
        # Registrar evento
        await self._registrar_evento(
            usuario_id=usuario_id,
            tipo_evento=TipoEventoRacha.MILESTONE,
            racha_anterior=racha_actual,
            racha_nueva=racha_actual,
            puntos_otorgados=recompensa.puntos_recompensa,
            descripcion=recompensa.mensaje_motivacional or f"Milestone {racha_actual} días alcanzado"
        )
        
        logger.info(
            f"Milestone alcanzado: Usuario {usuario_id} completó {racha_actual} días. "
            f"Recompensa: {recompensa.puntos_recompensa} puntos"
        )
        
        return {
            "dias": racha_actual,
            "tipo": recompensa.tipo_milestone.value,
            "puntos": recompensa.puntos_recompensa,
            "insignia": recompensa.tiene_insignia,
            "mensaje": recompensa.mensaje_motivacional
        }
    
    async def get_milestones_disponibles(self) -> List[Dict[str, Any]]:
        """
        Obtiene todos los milestones configurados.
        
        Returns:
            Lista de milestones con sus recompensas
        """
        query = select(RecompensaRacha).where(
            RecompensaRacha.es_activa == True
        ).order_by(RecompensaRacha.dias_requeridos)
        
        result = self.db.execute(query)
        recompensas = result.scalars().all()
        
        return [r.to_dict() for r in recompensas]
    
    # =============================================================================
    # HISTORIAL
    # =============================================================================
    
    async def get_historial_racha(
        self,
        usuario_id: UUID,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Obtiene el historial de eventos de racha del usuario.
        
        Args:
            usuario_id: UUID del usuario
            limit: Cantidad máxima de eventos
        
        Returns:
            Lista de eventos ordenados por fecha
        """
        query = select(HistorialRacha).where(
            HistorialRacha.usuario_id == usuario_id
        ).order_by(
            HistorialRacha.timestamp.desc()
        ).limit(limit)
        
        result = self.db.execute(query)
        eventos = result.scalars().all()
        
        return [e.to_dict() for e in eventos]
    
    # =============================================================================
    # ESTADÍSTICAS
    # =============================================================================
    
    async def get_estadisticas_racha(
        self,
        usuario_id: UUID
    ) -> Dict[str, Any]:
        """
        Obtiene estadísticas completas de la racha del usuario.
        
        Returns:
            Dict con estadísticas:
            {
                "racha_actual": 15,
                "mejor_racha": 30,
                "esta_protegida": True,
                "protegido_hasta": date,
                "recuperaciones_disponibles": 1,
                "dia_ciclo_semanal": 4,
                "puntos_hoy": 25,
                "total_incrementos": 100,
                "total_perdidas": 5,
                "milestones_alcanzados": [7, 30]
            }
        """
        racha = await self.get_racha_usuario(usuario_id)
        
        # Contar eventos por tipo
        query_eventos = select(
            HistorialRacha.tipo_evento,
            func.count(HistorialRacha.historial_id)
        ).where(
            HistorialRacha.usuario_id == usuario_id
        ).group_by(HistorialRacha.tipo_evento)
        
        result_eventos = self.db.execute(query_eventos)
        eventos_por_tipo = dict(result_eventos.all())
        
        # Milestones alcanzados
        query_milestones = select(HistorialRacha.racha_nueva).where(
            and_(
                HistorialRacha.usuario_id == usuario_id,
                HistorialRacha.tipo_evento == TipoEventoRacha.MILESTONE
            )
        ).order_by(HistorialRacha.racha_nueva)
        
        result_milestones = self.db.execute(query_milestones)
        milestones = [m[0] for m in result_milestones.all()]
        
        dia_semana = racha.dia_ciclo_semanal
        puntos_hoy = self.PUNTOS_SEMANALES.get(dia_semana, 10)
        
        return {
            "racha_actual": racha.racha_actual,
            "mejor_racha": racha.mejor_racha,
            "fecha_ultimo_dia": racha.fecha_ultimo_dia,
            "esta_protegida": racha.esta_protegida,
            "protegido_hasta": racha.racha_congelada_hasta,
            "recuperaciones_disponibles": racha.recuperaciones_disponibles,
            "dia_ciclo_semanal": dia_semana,
            "puntos_hoy": puntos_hoy,
            "total_incrementos": eventos_por_tipo.get(TipoEventoRacha.INCREMENTO, 0),
            "total_perdidas": eventos_por_tipo.get(TipoEventoRacha.PERDIDA, 0),
            "total_recuperaciones": eventos_por_tipo.get(TipoEventoRacha.RECUPERACION, 0),
            "milestones_alcanzados": milestones
        }
    
    # =============================================================================
    # HELPERS PRIVADOS
    # =============================================================================
    
    async def _registrar_evento(
        self,
        usuario_id: UUID,
        tipo_evento: TipoEventoRacha,
        racha_anterior: int,
        racha_nueva: int,
        puntos_otorgados: int = 0,
        descripcion: str = ""
    ):
        """Registra un evento en el historial de racha."""
        evento = HistorialRacha(
            usuario_id=usuario_id,
            tipo_evento=tipo_evento,
            racha_anterior=racha_anterior,
            racha_nueva=racha_nueva,
            puntos_otorgados=puntos_otorgados,
            descripcion=descripcion
        )
        self.db.add(evento)
    
    async def _otorgar_puntos(
        self,
        usuario_id: UUID,
        puntos: int,
        motivo: str
    ):
        """Otorga puntos al usuario."""
        query = select(UsuarioPuntos).where(
            UsuarioPuntos.usuario_id == usuario_id
        )
        result = self.db.execute(query)
        usuario_puntos = result.scalar_one_or_none()
        
        if usuario_puntos:
            usuario_puntos.puntos_actuales += puntos
            usuario_puntos.puntos_totales += puntos
    
    async def _otorgar_insignia(
        self,
        usuario_id: UUID,
        insignia_id: UUID
    ):
        """Otorga una insignia al usuario si no la tiene."""
        query = select(UsuarioInsignia).where(
            and_(
                UsuarioInsignia.usuario_id == usuario_id,
                UsuarioInsignia.insignia_id == insignia_id
            )
        )
        result = self.db.execute(query)
        ya_tiene = result.scalar_one_or_none()
        
        if not ya_tiene:
            usuario_insignia = UsuarioInsignia(
                usuario_id=usuario_id,
                insignia_id=insignia_id
            )
            self.db.add(usuario_insignia)
    
    def _generar_mensaje_racha(self, resultado: Dict[str, Any]) -> str:
        """Genera un mensaje motivacional basado en el resultado."""
        if resultado["racha_perdida"]:
            return f"Racha perdida 😢 ¡Pero puedes recuperarla!"
        
        if resultado["proteccion_usada"]:
            return f"¡Protección activada! Racha de {resultado['racha_actual']} días salvada 🛡️"
        
        if resultado["racha_incrementada"]:
            racha = resultado["racha_actual"]
            mensajes = {
                1: "¡Primer día! 🎯",
                3: "¡3 días seguidos! 🔥",
                7: "¡Una semana completa! 🌟",
                14: "¡2 semanas! Impresionante 💪",
                30: "¡UN MES COMPLETO! 🏆",
                100: "¡100 DÍAS! Eres una leyenda 👑",
                365: "¡UN AÑO COMPLETO! 🎉🎊🎈"
            }
            
            if racha in mensajes:
                return mensajes[racha]
            
            return f"¡Racha de {racha} días! Sigue así 🔥"
        
        return "Actividad completada"
