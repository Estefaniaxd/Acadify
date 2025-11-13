"""Servicio de gestión de puntos de gamificación.

Este servicio maneja toda la lógica relacionada con:
- Cálculo de puntos por tareas
- Otorgamiento de puntos a usuarios
- Registro en historial
- Verificación de logros/insignias

Author: GitHub Copilot & Team
Date: 31 octubre 2025
Version: 1.0.0
"""

from datetime import UTC, datetime
import logging
from typing import Any
from uuid import UUID

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.academic.tarea import Tarea
from src.models.gamification.historial_puntos import HistorialPuntos
from src.models.gamification.insignia import Insignia
from src.models.gamification.usuario_insignia import UsuarioInsignia
from src.models.gamification.usuario_puntos import UsuarioPuntos
from src.models.users.usuario import Usuario


logger = logging.getLogger(__name__)


class PuntosService:
    """Servicio para gestión de puntos de gamificación.

    Este servicio implementa la lógica de negocio para:
    - Calcular puntos basados en tareas y calificaciones
    - Otorgar puntos a usuarios
    - Registrar historial de puntos
    - Verificar y otorgar insignias automáticas

    Attributes:
        db: Sesión de base de datos

    Example:
        >>> service = PuntosService(db)
        >>> puntos = await service.calcular_puntos_tarea(
        ...     tarea=tarea_obj,
        ...     calificacion=4.5,
        ...     es_tardia=False
        ... )
        >>> await service.otorgar_puntos(
        ...     usuario_id=estudiante_id,
        ...     puntos=puntos,
        ...     motivo="Entrega de Tarea Python"
        ... )
    """

    def __init__(self, db: AsyncSession) -> None:
        """Inicializa el servicio de puntos.

        Args:
            db: Sesión asíncrona de base de datos
        """
        self.db = db
        logger.info("PuntosService inicializado")

    async def calcular_puntos_tarea(
        self,
        tarea: Tarea,
        calificacion: float,
        es_tardia: bool = False,
        intentos: int = 1,
    ) -> dict[str, Any]:
        """Calcula los puntos a otorgar por una tarea.

        Fórmula:
        - Base: tarea.puntos_base (default: 50)
        - Bonus: tarea.puntos_bonificacion si calificacion >= 4.5
        - Penalización tardía: -30% si es_tardia
        - Penalización intentos: -10% por cada intento adicional (max 2 intentos)

        Args:
            tarea: Instancia de Tarea con configuración de puntos
            calificacion: Calificación obtenida (0.0 - 5.0)
            es_tardia: Si la entrega fue después de la fecha límite
            intentos: Número de intentos realizados

        Returns:
            Dict con estructura:
            {
                "puntos_base": 50,
                "puntos_bonificacion": 20,
                "penalizacion_tardia": -15,
                "penalizacion_intentos": -5,
                "puntos_totales": 50,
                "desglose": "50 (base) + 20 (bonus) - 15 (tardía) - 5 (intentos)"
            }

        Example:
            >>> puntos = await service.calcular_puntos_tarea(
            ...     tarea=tarea_obj,
            ...     calificacion=4.8,
            ...     es_tardia=True,
            ...     intentos=2
            ... )
            >>> print(puntos["puntos_totales"])  # 45
        """
        # Puntos base de la tarea
        puntos_base = tarea.puntos_base if tarea.puntos_base else 50

        # Bonificación por excelencia (calificación >= 4.5)
        puntos_bonificacion = 0
        if calificacion >= 4.5 and tarea.puntos_bonificacion:
            puntos_bonificacion = tarea.puntos_bonificacion

        # Penalización por entrega tardía (-30%)
        penalizacion_tardia = 0
        if es_tardia:
            penalizacion_tardia = int(puntos_base * 0.30)

        # Penalización por intentos adicionales (-10% por intento extra, max 2 intentos)
        penalizacion_intentos = 0
        if intentos > 1:
            intentos_extra = min(intentos - 1, 2)  # Máximo 2 intentos extra
            penalizacion_intentos = int(puntos_base * 0.10 * intentos_extra)

        # Calcular total
        puntos_totales = (
            puntos_base
            + puntos_bonificacion
            - penalizacion_tardia
            - penalizacion_intentos
        )

        # Asegurar que no sean negativos
        puntos_totales = max(0, puntos_totales)

        # Desglose para mostrar al usuario
        desglose_partes = [f"{puntos_base} (base)"]
        if puntos_bonificacion > 0:
            desglose_partes.append(f"+ {puntos_bonificacion} (bonus excelencia)")
        if penalizacion_tardia > 0:
            desglose_partes.append(f"- {penalizacion_tardia} (entrega tardía)")
        if penalizacion_intentos > 0:
            desglose_partes.append(
                f"- {penalizacion_intentos} ({intentos-1} intento(s) extra)"
            )

        desglose = " ".join(desglose_partes)

        resultado = {
            "puntos_base": puntos_base,
            "puntos_bonificacion": puntos_bonificacion,
            "penalizacion_tardia": penalizacion_tardia,
            "penalizacion_intentos": penalizacion_intentos,
            "puntos_totales": puntos_totales,
            "desglose": desglose,
            "calificacion": calificacion,
            "es_tardia": es_tardia,
            "intentos": intentos,
        }

        logger.info(
            f"Puntos calculados para tarea {tarea.tarea_id}: "
            f"{puntos_totales} pts - {desglose}"
        )

        return resultado

    async def otorgar_puntos(
        self,
        usuario_id: UUID,
        puntos: int,
        motivo: str,
        entrega_id: UUID | None = None,
        tarea_id: UUID | None = None,
    ) -> dict[str, Any]:
        """Otorga puntos a un usuario y registra en historial.

        Este método:
        1. Actualiza UsuarioPuntos (suma acumulada)
        2. Crea registro en HistorialPuntos
        3. Verifica si desbloquea nuevas insignias

        Args:
            usuario_id: ID del usuario a quien otorgar puntos
            puntos: Cantidad de puntos (puede ser negativo para penalización)
            motivo: Descripción del motivo
            entrega_id: ID de la entrega relacionada (opcional)
            tarea_id: ID de la tarea relacionada (opcional)

        Returns:
            Dict con:
            {
                "puntos_otorgados": 50,
                "puntos_acumulados": 350,
                "nuevas_insignias": [...],
                "nivel_actual": "Bronce II"
            }

        Raises:
            ValueError: Si puntos es 0 o usuario no existe
        """
        if puntos == 0:
            msg = "Los puntos deben ser diferentes de cero"
            raise ValueError(msg)

        try:
            # 0. Verificar que el usuario existe
            stmt_usuario = select(Usuario).where(Usuario.usuario_id == usuario_id)
            result_usuario = await self.db.execute(stmt_usuario)
            usuario = result_usuario.scalar_one_or_none()

            if not usuario:
                msg = f"Usuario con ID {usuario_id} no encontrado"
                raise ValueError(msg)

            # 1. Obtener o crear registro de puntos del usuario
            stmt = select(UsuarioPuntos).where(UsuarioPuntos.usuario_id == usuario_id)
            result = await self.db.execute(stmt)
            usuario_puntos = result.scalar_one_or_none()

            if not usuario_puntos:
                # Crear registro inicial
                usuario_puntos = UsuarioPuntos(
                    usuario_id=usuario_id,
                    puntos_acumulados=0,
                    cambio=0,  # Se actualizará abajo
                    motivo="Inicialización",
                    fecha=datetime.now(UTC),
                )
                self.db.add(usuario_puntos)
                await self.db.flush()

            # 2. Actualizar puntos acumulados
            puntos_anteriores = usuario_puntos.puntos_acumulados
            usuario_puntos.puntos_acumulados += puntos
            usuario_puntos.cambio = puntos
            usuario_puntos.motivo = motivo
            usuario_puntos.fecha = datetime.now(UTC)

            # 3. Crear registro en historial
            historial = HistorialPuntos(
                usuario_id=usuario_id,
                cambio=puntos,
                motivo=motivo,
                fecha=datetime.now(UTC),
            )
            self.db.add(historial)

            # 4. Hacer commit
            await self.db.commit()
            await self.db.refresh(usuario_puntos)

            # 5. Verificar insignias desbloqueadas
            nuevas_insignias = await self._verificar_insignias(
                usuario_id=usuario_id,
                puntos_acumulados=usuario_puntos.puntos_acumulados,
            )

            # 6. Calcular nivel actual
            nivel = self._calcular_nivel(usuario_puntos.puntos_acumulados)

            logger.info(
                f"Puntos otorgados a usuario {usuario_id}: "
                f"{puntos:+d} pts (total: {usuario_puntos.puntos_acumulados}) - {motivo}"
            )

            return {
                "puntos_otorgados": puntos,
                "puntos_anteriores": puntos_anteriores,
                "puntos_acumulados": usuario_puntos.puntos_acumulados,
                "nuevas_insignias": nuevas_insignias,
                "nivel_actual": nivel,
                "motivo": motivo,
            }

        except Exception as e:
            await self.db.rollback()
            logger.exception(f"Error otorgando puntos: {e!s}")
            raise

    async def obtener_puntos_usuario(self, usuario_id: UUID) -> dict[str, Any]:
        """Obtiene información completa de puntos de un usuario.

        Args:
            usuario_id: ID del usuario

        Returns:
            Dict con información completa de puntos, nivel, insignias
        """
        # Puntos acumulados
        stmt = select(UsuarioPuntos).where(UsuarioPuntos.usuario_id == usuario_id)
        result = await self.db.execute(stmt)
        usuario_puntos = result.scalar_one_or_none()

        puntos_acumulados = usuario_puntos.puntos_acumulados if usuario_puntos else 0

        # Historial reciente (últimos 10)
        stmt_historial = (
            select(HistorialPuntos)
            .where(HistorialPuntos.usuario_id == usuario_id)
            .order_by(HistorialPuntos.fecha.desc())
            .limit(10)
        )
        result_historial = await self.db.execute(stmt_historial)
        historial = result_historial.scalars().all()

        # Insignias obtenidas
        stmt_insignias = (
            select(Insignia)
            .join(UsuarioInsignia)
            .where(UsuarioInsignia.usuario_id == usuario_id)
            .order_by(UsuarioInsignia.fecha_otorgada.desc())
        )
        result_insignias = await self.db.execute(stmt_insignias)
        insignias = result_insignias.scalars().all()

        # Nivel actual
        nivel = self._calcular_nivel(puntos_acumulados)
        nivel_info = self._info_nivel(puntos_acumulados)

        return {
            "puntos_acumulados": puntos_acumulados,
            "nivel": nivel,
            "nivel_info": nivel_info,
            "historial_reciente": [
                {"cambio": h.cambio, "motivo": h.motivo, "fecha": h.fecha.isoformat()}
                for h in historial
            ],
            "insignias": [
                {
                    "insignia_id": str(i.insignia_id),
                    "nombre": i.nombre,
                    "descripcion": i.descripcion,
                    "imagen_url": i.imagen_url,
                    "tipo": i.tipo.value,
                }
                for i in insignias
            ],
        }

    async def obtener_historial_puntos(
        self, usuario_id: UUID, limit: int = 50, offset: int = 0
    ) -> dict[str, Any]:
        """Obtiene el historial paginado de puntos de un usuario.

        Args:
            usuario_id: ID del usuario
            limit: Cantidad máxima de registros a retornar
            offset: Desplazamiento para paginación

        Returns:
            Dict con historial paginado y total de registros
        """
        # Obtener historial paginado
        stmt = (
            select(HistorialPuntos)
            .where(HistorialPuntos.usuario_id == usuario_id)
            .order_by(HistorialPuntos.fecha.desc())
            .limit(limit)
            .offset(offset)
        )
        result = await self.db.execute(stmt)
        historial = result.scalars().all()

        # Contar total de registros
        stmt_count = select(func.count(HistorialPuntos.historial_id)).where(
            HistorialPuntos.usuario_id == usuario_id
        )
        result_count = await self.db.execute(stmt_count)
        total = result_count.scalar()

        return {
            "historial": [
                {
                    "historial_id": str(h.historial_id),
                    "cambio": h.cambio,
                    "motivo": h.motivo,
                    "fecha": h.fecha.isoformat(),
                }
                for h in historial
            ],
            "total": total,
            "limit": limit,
            "offset": offset,
        }

    async def obtener_info_niveles(self) -> dict[str, Any]:
        """Obtiene información sobre el sistema de niveles.

        Returns:
            Dict con lista de niveles y sus umbrales
        """
        # Estructura de niveles con sus umbrales
        niveles_info = [
            {"nivel": "Bronce I", "puntos_minimos": 0, "puntos_requeridos": 100},
            {"nivel": "Bronce II", "puntos_minimos": 100, "puntos_requeridos": 250},
            {"nivel": "Bronce III", "puntos_minimos": 250, "puntos_requeridos": 500},
            {"nivel": "Plata I", "puntos_minimos": 500, "puntos_requeridos": 750},
            {"nivel": "Plata II", "puntos_minimos": 750, "puntos_requeridos": 1200},
            {"nivel": "Plata III", "puntos_minimos": 1200, "puntos_requeridos": 2000},
            {"nivel": "Oro I", "puntos_minimos": 2000, "puntos_requeridos": 3000},
            {"nivel": "Oro II", "puntos_minimos": 3000, "puntos_requeridos": 4000},
            {"nivel": "Oro III", "puntos_minimos": 4000, "puntos_requeridos": 5000},
            {"nivel": "Platino I", "puntos_minimos": 5000, "puntos_requeridos": 7500},
            {"nivel": "Platino II", "puntos_minimos": 7500, "puntos_requeridos": 10000},
            {
                "nivel": "Platino III",
                "puntos_minimos": 10000,
                "puntos_requeridos": None,
            },
        ]

        return {"niveles": niveles_info}

    async def _verificar_insignias(
        self, usuario_id: UUID, puntos_acumulados: int
    ) -> list[dict[str, Any]]:
        """Verifica y otorga insignias automáticas basadas en puntos.

        Args:
            usuario_id: ID del usuario
            puntos_acumulados: Puntos acumulados actuales

        Returns:
            Lista de insignias nuevas desbloqueadas
        """
        nuevas_insignias = []

        # Mapeo de umbrales de puntos a insignias
        umbrales = [
            (100, "Novato"),
            (500, "Estudiante Dedicado"),
            (1000, "Explorador del Conocimiento"),
            (2000, "Maestro en Progreso"),
            (5000, "Sabio Digital"),
        ]

        try:
            for puntos_requeridos, nombre_insignia in umbrales:
                if puntos_acumulados >= puntos_requeridos:
                    # Verificar si ya tiene la insignia
                    stmt = (
                        select(UsuarioInsignia)
                        .join(Insignia)
                        .where(
                            and_(
                                UsuarioInsignia.usuario_id == usuario_id,
                                Insignia.nombre == nombre_insignia,
                            )
                        )
                    )
                    result = await self.db.execute(stmt)
                    ya_tiene = result.scalar_one_or_none()

                    if not ya_tiene:
                        # Buscar la insignia
                        stmt_insignia = select(Insignia).where(
                            Insignia.nombre == nombre_insignia
                        )
                        result_insignia = await self.db.execute(stmt_insignia)
                        insignia = result_insignia.scalar_one_or_none()

                        if insignia:
                            # Otorgar insignia
                            usuario_insignia = UsuarioInsignia(
                                usuario_id=usuario_id,
                                insignia_id=insignia.insignia_id,
                                fecha_otorgada=datetime.now(UTC),
                            )
                            self.db.add(usuario_insignia)

                            nuevas_insignias.append(
                                {
                                    "insignia_id": str(insignia.insignia_id),
                                    "nombre": insignia.nombre,
                                    "descripcion": insignia.descripcion,
                                    "imagen_url": insignia.imagen_url,
                                }
                            )

                            logger.info(
                                f"Insignia '{nombre_insignia}' otorgada a usuario {usuario_id}"
                            )

            if nuevas_insignias:
                await self.db.commit()

        except Exception as e:
            logger.exception(f"Error verificando insignias: {e!s}")
            # No fallar la operación principal por error en insignias

        return nuevas_insignias

    def _calcular_nivel(self, puntos: int) -> str:
        """Calcula el nivel del usuario basado en puntos acumulados.

        Sistema de niveles:
        - Bronce: 0-499 pts (I, II, III)
        - Plata: 500-1999 pts (I, II, III)
        - Oro: 2000-4999 pts (I, II, III)
        - Platino: 5000+ pts (I, II, III)

        Args:
            puntos: Puntos acumulados

        Returns:
            String con el nivel (ej: "Oro II")
        """
        if puntos < 100:
            return "Bronce I"
        if puntos < 250:
            return "Bronce II"
        if puntos < 500:
            return "Bronce III"
        if puntos < 750:
            return "Plata I"
        if puntos < 1200:
            return "Plata II"
        if puntos < 2000:
            return "Plata III"
        if puntos < 3000:
            return "Oro I"
        if puntos < 4000:
            return "Oro II"
        if puntos < 5000:
            return "Oro III"
        if puntos < 7500:
            return "Platino I"
        if puntos < 10000:
            return "Platino II"
        return "Platino III"

    def _info_nivel(self, puntos: int) -> dict[str, Any]:
        """Retorna información detallada del nivel actual.

        Args:
            puntos: Puntos acumulados

        Returns:
            Dict con información del nivel (actual, siguiente, progreso)
        """
        # Umbrales de niveles
        niveles = [
            (0, "Bronce I", 100),
            (100, "Bronce II", 250),
            (250, "Bronce III", 500),
            (500, "Plata I", 750),
            (750, "Plata II", 1200),
            (1200, "Plata III", 2000),
            (2000, "Oro I", 3000),
            (3000, "Oro II", 4000),
            (4000, "Oro III", 5000),
            (5000, "Platino I", 7500),
            (7500, "Platino II", 10000),
            (10000, "Platino III", float("inf")),
        ]

        # Encontrar nivel actual
        nivel_actual = "Platino III"
        puntos_siguiente = float("inf")
        puntos_actual_min = 10000

        for _i, (min_pts, nombre, max_pts) in enumerate(niveles):
            if min_pts <= puntos < max_pts:
                nivel_actual = nombre
                puntos_actual_min = min_pts
                puntos_siguiente = max_pts
                break

        # Calcular progreso
        if puntos_siguiente != float("inf"):
            puntos_en_nivel = puntos - puntos_actual_min
            puntos_necesarios = puntos_siguiente - puntos_actual_min
            progreso_porcentaje = (puntos_en_nivel / puntos_necesarios) * 100
        else:
            progreso_porcentaje = 100.0

        return {
            "nivel_actual": nivel_actual,
            "puntos_minimos_nivel": puntos_actual_min,
            "puntos_siguiente_nivel": (
                puntos_siguiente if puntos_siguiente != float("inf") else None
            ),
            "progreso_porcentaje": round(progreso_porcentaje, 1),
            "puntos_para_siguiente": (
                max(0, puntos_siguiente - puntos)
                if puntos_siguiente != float("inf")
                else 0
            ),
        }

    async def obtener_ranking(
        self, limite: int = 10, offset: int = 0, institucion_id: UUID | None = None
    ) -> dict[str, Any]:
        """Obtiene el ranking de usuarios por puntos.

        Args:
            limite: Número máximo de usuarios a retornar
            offset: Posición inicial para paginación
            institucion_id: Filtrar por institución (opcional)

        Returns:
            Dict con:
            {
                "success": True,
                "data": [...],
                "total": 150
            }
        """
        # Contar total de usuarios con puntos
        stmt_count = select(func.count(UsuarioPuntos.usuario_id))
        result_count = await self.db.execute(stmt_count)
        total = result_count.scalar()

        # Obtener ranking con paginación
        stmt = (
            select(UsuarioPuntos)
            .order_by(UsuarioPuntos.puntos_acumulados.desc())
            .offset(offset)
            .limit(limite)
        )

        result = await self.db.execute(stmt)
        usuarios = result.scalars().all()

        ranking = []
        for posicion, usuario_puntos in enumerate(usuarios, start=offset + 1):
            nivel = self._calcular_nivel(usuario_puntos.puntos_acumulados)

            ranking.append(
                {
                    "posicion": posicion,
                    "usuario_id": str(usuario_puntos.usuario_id),
                    "nombre_completo": None,  # TODO: Join con Usuario
                    "puntos": usuario_puntos.puntos_acumulados,
                    "nivel": nivel,
                }
            )

        return {"success": True, "data": ranking, "total": total}

    async def obtener_posicion_usuario(self, usuario_id: str) -> dict[str, Any]:
        """Obtiene la posición del usuario en el ranking global.

        Args:
            usuario_id: ID del usuario

        Returns:
            Dict con posición, puntos, nivel y contexto del ranking
        """
        # Obtener puntos del usuario
        usuario_uuid = UUID(usuario_id) if isinstance(usuario_id, str) else usuario_id
        stmt = select(UsuarioPuntos).where(UsuarioPuntos.usuario_id == usuario_uuid)
        result = await self.db.execute(stmt)
        usuario_puntos = result.scalar_one_or_none()

        if not usuario_puntos:
            return {
                "posicion": None,
                "puntos": 0,
                "nivel": "Bronce I",
                "puntos_hasta_anterior": None,
                "puntos_hasta_siguiente": None,
                "total_usuarios": 0,
            }

        # Calcular posición: contar cuántos usuarios tienen más puntos
        stmt_posicion = select(func.count(UsuarioPuntos.usuario_id)).where(
            UsuarioPuntos.puntos_acumulados > usuario_puntos.puntos_acumulados
        )
        result_posicion = await self.db.execute(stmt_posicion)
        usuarios_delante = result_posicion.scalar()
        posicion = usuarios_delante + 1

        # Total de usuarios
        stmt_total = select(func.count(UsuarioPuntos.usuario_id))
        result_total = await self.db.execute(stmt_total)
        total_usuarios = result_total.scalar()

        # Usuario inmediatamente anterior (con más puntos)
        stmt_anterior = (
            select(UsuarioPuntos)
            .where(UsuarioPuntos.puntos_acumulados > usuario_puntos.puntos_acumulados)
            .order_by(UsuarioPuntos.puntos_acumulados.asc())
            .limit(1)
        )
        result_anterior = await self.db.execute(stmt_anterior)
        anterior = result_anterior.scalar_one_or_none()

        # Usuario inmediatamente siguiente (con menos puntos)
        stmt_siguiente = (
            select(UsuarioPuntos)
            .where(UsuarioPuntos.puntos_acumulados < usuario_puntos.puntos_acumulados)
            .order_by(UsuarioPuntos.puntos_acumulados.desc())
            .limit(1)
        )
        result_siguiente = await self.db.execute(stmt_siguiente)
        siguiente = result_siguiente.scalar_one_or_none()

        # Calcular diferencias
        puntos_hasta_anterior = (
            anterior.puntos_acumulados - usuario_puntos.puntos_acumulados
            if anterior
            else None
        )
        puntos_hasta_siguiente = (
            usuario_puntos.puntos_acumulados - siguiente.puntos_acumulados
            if siguiente
            else None
        )

        nivel = self._calcular_nivel(usuario_puntos.puntos_acumulados)

        return {
            "posicion": posicion,
            "puntos": usuario_puntos.puntos_acumulados,
            "nivel": nivel,
            "puntos_hasta_anterior": puntos_hasta_anterior,
            "puntos_hasta_siguiente": puntos_hasta_siguiente,
            "total_usuarios": total_usuarios,
        }
