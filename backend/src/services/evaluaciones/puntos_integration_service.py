"""Servicio de integración entre Evaluaciones y Sistema de Puntos.

Este servicio actúa como puente entre el sistema de evaluaciones y el sistema
de gamificación, manejando la lógica de negocio para:
- Otorgar puntos automáticamente al completar evaluaciones
- Calcular multiplicadores basados en rendimiento
- Otorgar insignias específicas de evaluaciones
- Actualizar rankings en tiempo real
- Gestionar bonificaciones y penalizaciones

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

from src.models.evaluaciones.evaluacion_expandida import Evaluacion
from src.models.evaluaciones.intento_respuesta_gamificacion import (
    IntentoEvaluacion,
    RespuestaEstudiante,
)
from src.models.gamification.insignia import Insignia
from src.models.gamification.usuario_insignia import UsuarioInsignia
from src.services.gamification.puntos_service import PuntosService


logger = logging.getLogger(__name__)


class PuntosIntegrationService:
    """Servicio de integración entre Evaluaciones y Puntos de Gamificación.

    Este servicio coordina la interacción entre ambos sistemas, aplicando
    la lógica específica de evaluaciones para el cálculo de puntos.

    Attributes:
        db: Sesión de base de datos
        puntos_service: Instancia del servicio de puntos

    Example:
        >>> service = PuntosIntegrationService(db)
        >>> resultado = await service.procesar_evaluacion_completada(
        ...     intento_id="uuid-del-intento",
        ...     estudiante_id="uuid-del-estudiante"
        ... )
        >>> print(resultado["puntos_ganados"])
    """

    def __init__(self, db: AsyncSession) -> None:
        """Inicializa el servicio de integración.

        Args:
            db: Sesión asíncrona de base de datos
        """
        self.db = db
        self.puntos_service = PuntosService(db)
        logger.info("PuntosIntegrationService inicializado")

    async def procesar_evaluacion_completada(
        self, intento_id: UUID, estudiante_id: UUID
    ) -> dict[str, Any]:
        """Procesa el completado de una evaluación y otorga puntos.

        Este método se llama cuando un estudiante finaliza una evaluación.
        Calcula y otorga los puntos correspondientes basándose en:
        - Configuración de la evaluación (otorga_puntos, puntos_base, etc.)
        - Calificación obtenida
        - Tiempo empleado
        - Racha de aciertos
        - Multiplicadores aplicables

        Args:
            intento_id: ID del intento de evaluación
            estudiante_id: ID del estudiante

        Returns:
            Dict con información completa del proceso:
            {
                "puntos_ganados": 150,
                "multiplicador_aplicado": 1.5,
                "bonus_tiempo": 20,
                "bonus_precision": 30,
                "desglose": {...},
                "nuevas_insignias": [...],
                "nivel_actual": "Oro II",
                "puntos_acumulados": 2450
            }

        Raises:
            ValueError: Si el intento no existe o no está completado
        """
        try:
            # 1. Obtener intento con evaluación
            stmt = select(IntentoEvaluacion).where(
                IntentoEvaluacion.intento_id == intento_id
            )
            result = await self.db.execute(stmt)
            intento = result.scalar_one_or_none()

            if not intento:
                msg = f"Intento {intento_id} no encontrado"
                raise ValueError(msg)

            if intento.estado_intento not in ["FINALIZADO", "CALIFICADO"]:
                msg = f"Intento {intento_id} no está completado"
                raise ValueError(msg)

            # 2. Obtener evaluación
            stmt_eval = select(Evaluacion).where(
                Evaluacion.evaluacion_id == intento.evaluacion_id
            )
            result_eval = await self.db.execute(stmt_eval)
            evaluacion = result_eval.scalar_one_or_none()

            if not evaluacion:
                msg = f"Evaluación {intento.evaluacion_id} no encontrada"
                raise ValueError(msg)

            # 3. Verificar si la evaluación otorga puntos
            if not evaluacion.otorga_puntos:
                logger.info(f"Evaluación {evaluacion.id} no otorga puntos")
                return {
                    "puntos_ganados": 0,
                    "razon": "La evaluación no está configurada para otorgar puntos",
                    "otorga_puntos": False,
                }

            # 4. Verificar si ya se otorgaron puntos (evitar duplicados)
            if intento.puntos_ganados > 0:
                logger.warning(f"Puntos ya otorgados para intento {intento_id}")
                return {
                    "puntos_ganados": intento.puntos_ganados,
                    "razon": "Puntos ya fueron otorgados previamente",
                    "ya_procesado": True,
                }

            # 5. Calcular puntos
            calculo = await self._calcular_puntos_evaluacion(
                evaluacion=evaluacion, intento=intento
            )

            # 6. Actualizar intento con puntos calculados
            intento.puntos_ganados = calculo["puntos_totales"]
            intento.multiplicador_aplicado = calculo["multiplicador_final"]
            intento.bonus_tiempo = calculo["bonus_tiempo"]
            intento.bonus_precision = calculo["bonus_precision"]

            # 7. Otorgar puntos al estudiante
            motivo = f"Evaluación completada: {evaluacion.titulo}"
            resultado_puntos = await self.puntos_service.otorgar_puntos(
                usuario_id=estudiante_id,
                puntos=calculo["puntos_totales"],
                motivo=motivo,
            )

            # 8. Verificar insignias específicas de evaluaciones
            nuevas_insignias_eval = await self._verificar_insignias_evaluacion(
                estudiante_id=estudiante_id, evaluacion=evaluacion, intento=intento
            )

            # Combinar insignias
            todas_insignias = (
                resultado_puntos["nuevas_insignias"] + nuevas_insignias_eval
            )

            # 9. Actualizar ranking si está habilitado
            if evaluacion.otorga_puntos:
                await self._actualizar_ranking_evaluacion(
                    evaluacion_id=evaluacion.id,
                    estudiante_id=estudiante_id,
                    puntos=calculo["puntos_totales"],
                )

            # 10. Commit final
            await self.db.commit()
            await self.db.refresh(intento)

            logger.info(
                f"Puntos otorgados a estudiante {estudiante_id} por evaluación "
                f"{evaluacion.titulo}: {calculo['puntos_totales']} pts"
            )

            return {
                "success": True,
                "puntos_ganados": calculo["puntos_totales"],
                "multiplicador_aplicado": calculo["multiplicador_final"],
                "bonus_tiempo": calculo["bonus_tiempo"],
                "bonus_precision": calculo["bonus_precision"],
                "desglose": calculo["desglose"],
                "nuevas_insignias": todas_insignias,
                "nivel_actual": resultado_puntos["nivel_actual"],
                "puntos_acumulados": resultado_puntos["puntos_acumulados"],
                "evaluacion_titulo": evaluacion.titulo,
                "calificacion": intento.porcentaje,
            }

        except Exception as e:
            await self.db.rollback()
            logger.exception(f"Error procesando evaluación completada: {e!s}")
            raise

    async def _calcular_puntos_evaluacion(
        self, evaluacion: Evaluacion, intento: IntentoEvaluacion
    ) -> dict[str, Any]:
        """Calcula los puntos a otorgar por una evaluación específica.

        Fórmula:
        1. Puntos Base (de la evaluación)
        2. Puntos por Acierto (por cada respuesta correcta)
        3. Bonus por Tiempo (si completa rápido)
        4. Bonus por Precisión (si calificación >= umbral)
        5. Multiplicador de Puntos (configurado en la evaluación)
        6. Multiplicador por Racha (si tiene racha activa)

        Args:
            evaluacion: Instancia de Evaluacion
            intento: Instancia de IntentoEvaluacion

        Returns:
            Dict con desglose completo de puntos
        """
        # 1. Puntos base configurados en la evaluación
        puntos_base = evaluacion.puntos_base or 100

        # 2. Calcular puntos por aciertos
        puntos_por_acierto = evaluacion.puntos_por_acierto or 10

        # Contar respuestas correctas
        stmt_correctas = select(func.count(RespuestaEstudiante.respuesta_id)).where(
            and_(
                RespuestaEstudiante.intento_id == intento.intento_id,
                RespuestaEstudiante.es_correcta,
            )
        )
        result_correctas = await self.db.execute(stmt_correctas)
        respuestas_correctas = result_correctas.scalar() or 0

        puntos_aciertos = respuestas_correctas * puntos_por_acierto

        # 3. Bonus por tiempo (si está habilitado)
        bonus_tiempo = 0
        if evaluacion.puntos_por_tiempo and intento.tiempo_total_segundos:
            # Calcular si completó en menos del 70% del tiempo límite
            tiempo_limite_segundos = evaluacion.tiempo_limite_minutos * 60
            porcentaje_tiempo_usado = (
                intento.tiempo_total_segundos / tiempo_limite_segundos
            ) * 100

            if porcentaje_tiempo_usado <= 70:
                # Bonus: 20% de puntos base si completa rápido
                bonus_tiempo = int(puntos_base * 0.20)

        # 4. Bonus por precisión (si calificación es excelente)
        bonus_precision = 0
        if intento.porcentaje and intento.porcentaje >= 90:
            # Bonus: 30% de puntos base si obtiene >= 90%
            bonus_precision = int(puntos_base * 0.30)
        elif intento.porcentaje and intento.porcentaje >= 80:
            # Bonus: 15% de puntos base si obtiene >= 80%
            bonus_precision = int(puntos_base * 0.15)

        # 5. Calcular subtotal antes de multiplicadores
        subtotal = puntos_base + puntos_aciertos + bonus_tiempo + bonus_precision

        # 6. Aplicar multiplicador de la evaluación
        multiplicador_evaluacion = evaluacion.multiplicador_puntos or 1.0

        # 7. Verificar racha del estudiante (bonus multiplicador)
        multiplicador_racha = await self._calcular_multiplicador_racha(
            intento.estudiante_id
        )

        # 8. Multiplicador final
        multiplicador_final = multiplicador_evaluacion * multiplicador_racha

        # 9. Calcular puntos finales
        puntos_totales = int(subtotal * multiplicador_final)

        # 10. Crear desglose detallado
        desglose = {
            "puntos_base": puntos_base,
            "respuestas_correctas": respuestas_correctas,
            "puntos_por_acierto": puntos_por_acierto,
            "puntos_aciertos": puntos_aciertos,
            "bonus_tiempo": bonus_tiempo,
            "bonus_precision": bonus_precision,
            "subtotal": subtotal,
            "multiplicador_evaluacion": multiplicador_evaluacion,
            "multiplicador_racha": multiplicador_racha,
            "multiplicador_final": multiplicador_final,
            "puntos_totales": puntos_totales,
            "formula": (
                f"{puntos_base} (base) + "
                f"{puntos_aciertos} ({respuestas_correctas} aciertos) + "
                f"{bonus_tiempo} (tiempo) + "
                f"{bonus_precision} (precisión) = "
                f"{subtotal} × {multiplicador_final:.2f} = {puntos_totales}"
            ),
        }

        logger.debug(f"Cálculo de puntos: {desglose['formula']}")

        return desglose

    async def _calcular_multiplicador_racha(self, estudiante_id: UUID) -> float:
        """Calcula el multiplicador por racha de evaluaciones completadas.

        Racha = número consecutivo de evaluaciones aprobadas sin fallar
        - 3+ evaluaciones: +10% (multiplicador 1.1)
        - 5+ evaluaciones: +20% (multiplicador 1.2)
        - 10+ evaluaciones: +30% (multiplicador 1.3)

        Args:
            estudiante_id: ID del estudiante

        Returns:
            Multiplicador de racha (1.0 - 1.3)
        """
        try:
            # Obtener últimos 10 intentos del estudiante
            stmt = (
                select(IntentoEvaluacion)
                .where(
                    and_(
                        IntentoEvaluacion.estudiante_id == estudiante_id,
                        IntentoEvaluacion.estado_intento.in_(
                            ["FINALIZADO", "CALIFICADO"]
                        ),
                    )
                )
                .order_by(IntentoEvaluacion.fecha_fin.desc())
                .limit(10)
            )
            result = await self.db.execute(stmt)
            intentos = result.scalars().all()

            # Contar racha actual (evaluaciones aprobadas consecutivas)
            racha = 0
            for intento in intentos:
                if intento.aprobado:
                    racha += 1
                else:
                    break  # Se rompe la racha

            # Calcular multiplicador
            if racha >= 10:
                return 1.3
            if racha >= 5:
                return 1.2
            if racha >= 3:
                return 1.1
            return 1.0

        except Exception as e:
            logger.exception(f"Error calculando multiplicador de racha: {e!s}")
            return 1.0  # Default sin bonus

    async def _verificar_insignias_evaluacion(
        self, estudiante_id: UUID, evaluacion: Evaluacion, intento: IntentoEvaluacion
    ) -> list[dict[str, Any]]:
        """Verifica y otorga insignias específicas de evaluaciones.

        Insignias disponibles:
        - "Primera Evaluación": Completar primera evaluación
        - "Perfeccionista": Obtener 100% en una evaluación
        - "Velocista": Completar evaluación en menos del 50% del tiempo
        - "Maratonista": Completar 10 evaluaciones
        - "Experto en [Tipo]": Completar 5 evaluaciones del mismo tipo

        Args:
            estudiante_id: ID del estudiante
            evaluacion: Evaluación completada
            intento: Intento del estudiante

        Returns:
            Lista de insignias nuevas otorgadas
        """
        nuevas_insignias = []

        try:
            # 1. Primera evaluación completada
            stmt_count = select(func.count(IntentoEvaluacion.intento_id)).where(
                and_(
                    IntentoEvaluacion.estudiante_id == estudiante_id,
                    IntentoEvaluacion.estado_intento.in_(["FINALIZADO", "CALIFICADO"]),
                )
            )
            result_count = await self.db.execute(stmt_count)
            total_evaluaciones = result_count.scalar()

            if total_evaluaciones == 1:
                insignia = await self._otorgar_insignia_por_nombre(
                    estudiante_id=estudiante_id, nombre="Primera Evaluación"
                )
                if insignia:
                    nuevas_insignias.append(insignia)

            # 2. Perfeccionista (100% de calificación)
            if intento.porcentaje and intento.porcentaje >= 100:
                insignia = await self._otorgar_insignia_por_nombre(
                    estudiante_id=estudiante_id, nombre="Perfeccionista"
                )
                if insignia:
                    nuevas_insignias.append(insignia)

            # 3. Velocista (completar en menos del 50% del tiempo)
            if evaluacion.tiempo_limite_minutos and intento.tiempo_total_segundos:
                tiempo_limite_segundos = evaluacion.tiempo_limite_minutos * 60
                porcentaje_tiempo = (
                    intento.tiempo_total_segundos / tiempo_limite_segundos
                ) * 100

                if porcentaje_tiempo <= 50:
                    insignia = await self._otorgar_insignia_por_nombre(
                        estudiante_id=estudiante_id, nombre="Velocista"
                    )
                    if insignia:
                        nuevas_insignias.append(insignia)

            # 4. Maratonista (10 evaluaciones completadas)
            if total_evaluaciones >= 10:
                insignia = await self._otorgar_insignia_por_nombre(
                    estudiante_id=estudiante_id, nombre="Maratonista"
                )
                if insignia:
                    nuevas_insignias.append(insignia)

            # 5. Experto en tipo de evaluación (5 del mismo tipo aprobadas)
            if evaluacion.tipo_evaluacion and intento.aprobado:
                stmt_tipo = (
                    select(func.count(IntentoEvaluacion.intento_id))
                    .join(Evaluacion)
                    .where(
                        and_(
                            IntentoEvaluacion.estudiante_id == estudiante_id,
                            IntentoEvaluacion.aprobado,
                            Evaluacion.tipo_evaluacion == evaluacion.tipo_evaluacion,
                        )
                    )
                )
                result_tipo = await self.db.execute(stmt_tipo)
                total_tipo = result_tipo.scalar()

                if total_tipo >= 5:
                    nombre_insignia = f"Experto en {evaluacion.tipo_evaluacion}"
                    insignia = await self._otorgar_insignia_por_nombre(
                        estudiante_id=estudiante_id, nombre=nombre_insignia
                    )
                    if insignia:
                        nuevas_insignias.append(insignia)

        except Exception as e:
            logger.exception(f"Error verificando insignias de evaluación: {e!s}")

        return nuevas_insignias

    async def _otorgar_insignia_por_nombre(
        self, estudiante_id: UUID, nombre: str
    ) -> dict[str, Any] | None:
        """Otorga una insignia específica a un estudiante si no la tiene.

        Args:
            estudiante_id: ID del estudiante
            nombre: Nombre de la insignia

        Returns:
            Dict con información de la insignia si fue otorgada, None si ya la tenía
        """
        try:
            # Buscar la insignia
            stmt_insignia = select(Insignia).where(Insignia.nombre == nombre)
            result = await self.db.execute(stmt_insignia)
            insignia = result.scalar_one_or_none()

            if not insignia:
                logger.warning(f"Insignia '{nombre}' no encontrada en la base de datos")
                return None

            # Verificar si ya la tiene
            stmt_tiene = select(UsuarioInsignia).where(
                and_(
                    UsuarioInsignia.usuario_id == estudiante_id,
                    UsuarioInsignia.insignia_id == insignia.insignia_id,
                )
            )
            result_tiene = await self.db.execute(stmt_tiene)
            ya_tiene = result_tiene.scalar_one_or_none()

            if ya_tiene:
                return None  # Ya la tiene

            # Otorgar insignia
            usuario_insignia = UsuarioInsignia(
                usuario_id=estudiante_id,
                insignia_id=insignia.insignia_id,
                fecha_obtencion=datetime.now(UTC),
            )
            self.db.add(usuario_insignia)
            await self.db.flush()

            logger.info(f"Insignia '{nombre}' otorgada a estudiante {estudiante_id}")

            return {
                "insignia_id": str(insignia.insignia_id),
                "nombre": insignia.nombre,
                "descripcion": insignia.descripcion,
                "imagen_url": insignia.imagen_url,
            }

        except Exception as e:
            logger.exception(f"Error otorgando insignia '{nombre}': {e!s}")
            return None

    async def _actualizar_ranking_evaluacion(
        self, evaluacion_id: UUID, estudiante_id: UUID, puntos: int
    ) -> None:
        """Actualiza el ranking específico de una evaluación.

        Calcula la posición del estudiante en el ranking de la evaluación
        basándose en los puntos obtenidos.

        Args:
            evaluacion_id: ID de la evaluación
            estudiante_id: ID del estudiante
            puntos: Puntos obtenidos
        """
        try:
            # Contar cuántos estudiantes tienen más puntos en esta evaluación
            stmt = select(func.count(IntentoEvaluacion.intento_id)).where(
                and_(
                    IntentoEvaluacion.evaluacion_id == evaluacion_id,
                    IntentoEvaluacion.puntos_ganados > puntos,
                    IntentoEvaluacion.estado_intento.in_(["FINALIZADO", "CALIFICADO"]),
                )
            )
            result = await self.db.execute(stmt)
            estudiantes_delante = result.scalar() or 0

            posicion = estudiantes_delante + 1

            # Actualizar posición en el intento
            stmt_update = (
                select(IntentoEvaluacion)
                .where(
                    and_(
                        IntentoEvaluacion.evaluacion_id == evaluacion_id,
                        IntentoEvaluacion.estudiante_id == estudiante_id,
                    )
                )
                .order_by(IntentoEvaluacion.fecha_fin.desc())
                .limit(1)
            )
            result_update = await self.db.execute(stmt_update)
            intento = result_update.scalar_one_or_none()

            if intento:
                intento.posicion_ranking = posicion
                await self.db.flush()

                logger.debug(
                    f"Ranking actualizado para estudiante {estudiante_id} "
                    f"en evaluación {evaluacion_id}: Posición {posicion}"
                )

        except Exception as e:
            logger.exception(f"Error actualizando ranking: {e!s}")

    async def obtener_ranking_evaluacion(
        self, evaluacion_id: UUID, limite: int = 10
    ) -> dict[str, Any]:
        """Obtiene el ranking de una evaluación específica.

        Args:
            evaluacion_id: ID de la evaluación
            limite: Número máximo de resultados

        Returns:
            Dict con ranking de estudiantes
        """
        stmt = (
            select(IntentoEvaluacion)
            .where(
                and_(
                    IntentoEvaluacion.evaluacion_id == evaluacion_id,
                    IntentoEvaluacion.estado_intento.in_(["FINALIZADO", "CALIFICADO"]),
                )
            )
            .order_by(
                IntentoEvaluacion.puntos_ganados.desc(),
                IntentoEvaluacion.fecha_fin.asc(),
            )
            .limit(limite)
        )

        result = await self.db.execute(stmt)
        intentos = result.scalars().all()

        ranking = []
        for posicion, intento in enumerate(intentos, start=1):
            ranking.append(
                {
                    "posicion": posicion,
                    "estudiante_id": str(intento.estudiante_id),
                    "puntos_ganados": intento.puntos_ganados,
                    "calificacion": intento.porcentaje,
                    "tiempo_segundos": intento.tiempo_total_segundos,
                    "fecha_completado": (
                        intento.fecha_fin.isoformat() if intento.fecha_fin else None
                    ),
                    "multiplicador": intento.multiplicador_aplicado,
                }
            )

        return {
            "success": True,
            "evaluacion_id": str(evaluacion_id),
            "ranking": ranking,
            "total_participantes": len(ranking),
        }

    async def otorgar_insignia_evaluacion(
        self, evaluacion_id: UUID, estudiante_id: UUID
    ) -> dict[str, Any] | None:
        """Otorga la insignia específica de una evaluación si está configurada.

        Args:
            evaluacion_id: ID de la evaluación
            estudiante_id: ID del estudiante

        Returns:
            Dict con información de la insignia otorgada o None
        """
        try:
            # Obtener evaluación
            stmt = select(Evaluacion).where(Evaluacion.evaluacion_id == evaluacion_id)
            result = await self.db.execute(stmt)
            evaluacion = result.scalar_one_or_none()

            if (
                not evaluacion
                or not evaluacion.otorga_insignia
                or not evaluacion.insignia_id
            ):
                return None

            # Verificar si ya la tiene
            stmt_tiene = select(UsuarioInsignia).where(
                and_(
                    UsuarioInsignia.usuario_id == estudiante_id,
                    UsuarioInsignia.insignia_id == evaluacion.insignia_id,
                )
            )
            result_tiene = await self.db.execute(stmt_tiene)
            ya_tiene = result_tiene.scalar_one_or_none()

            if ya_tiene:
                return None

            # Buscar la insignia
            stmt_insignia = select(Insignia).where(
                Insignia.insignia_id == evaluacion.insignia_id
            )
            result_insignia = await self.db.execute(stmt_insignia)
            insignia = result_insignia.scalar_one_or_none()

            if not insignia:
                logger.warning(f"Insignia {evaluacion.insignia_id} no encontrada")
                return None

            # Otorgar insignia
            usuario_insignia = UsuarioInsignia(
                usuario_id=estudiante_id,
                insignia_id=insignia.insignia_id,
                fecha_obtencion=datetime.now(UTC),
            )
            self.db.add(usuario_insignia)
            await self.db.commit()

            logger.info(
                f"Insignia '{insignia.nombre}' de evaluación {evaluacion.titulo} "
                f"otorgada a estudiante {estudiante_id}"
            )

            return {
                "insignia_id": str(insignia.insignia_id),
                "nombre": insignia.nombre,
                "descripcion": insignia.descripcion,
                "imagen_url": insignia.imagen_url,
                "evaluacion": evaluacion.titulo,
            }

        except Exception as e:
            await self.db.rollback()
            logger.exception(f"Error otorgando insignia de evaluación: {e!s}")
            return None
