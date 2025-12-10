"""Servicio Enriquecido de Tareas - Domain-Driven Design
Aplica Clean Code, SOLID, y DDD principles.

Responsabilidades:
- Enriquecimiento de tareas con estados calculados
- Cálculo de métricas y estadísticas
- Lógica de negocio para estados visuales
- Separación de concerns entre datos y lógica
"""

from datetime import UTC, datetime, timedelta
import logging

from sqlalchemy import and_, or_, text
from sqlalchemy.orm import Session

from src.enums.academic.tareas import EstadoTarea
from src.models.academic.tarea import EntregaTarea, Tarea
from src.schemas.academic.tarea_enriched import (
    ColorEstado,
    EstadisticasCalificacion,
    EstadoVisual,
    EstadoVisualizacion,
    FiltrosTareaEnriquecida,
    IconoEstado,
    MetricasProgreso,
    RespuestaPaginada,
    TareaEnriquecida,
    TiempoRestante,
)


logger = logging.getLogger(__name__)


class EstadoCalculator:
    """Calculator para estados visuales (SRP: Single Responsibility)
    Encapsula la lógica de cálculo de estados.
    """

    # Constantes de configuración
    HORAS_PROXIMA_A_VENCER = 48
    HORAS_MUY_URGENTE = 24

    @staticmethod
    def calcular_tiempo_restante(fecha_limite: datetime) -> TiempoRestante | None:
        """Calcula el tiempo restante hasta la fecha límite.

        Args:
            fecha_limite: Fecha límite de la tarea

        Returns:
            TiempoRestante o None si ya venció
        """
        ahora = (
            datetime.now(fecha_limite.tzinfo)
            if fecha_limite.tzinfo
            else datetime.now(UTC)
        )
        delta = fecha_limite - ahora

        if delta.total_seconds() <= 0:
            return None

        dias = delta.days
        segundos_restantes = delta.seconds
        horas = segundos_restantes // 3600
        minutos = (segundos_restantes % 3600) // 60

        return TiempoRestante(
            dias_restantes=dias, horas_restantes=horas, minutos_restantes=minutos
        )

    @staticmethod
    def calcular_estado_visualizacion(
        estado_tarea: EstadoTarea,
        fecha_limite: datetime,
        tiene_entregas: bool,
        todas_calificadas: bool,
        es_tardia: bool = False,
    ) -> EstadoVisualizacion:
        """Calcula el estado de visualización basado en reglas de negocio.

        Business Rules:
        1. Si cancelada → CANCELADA
        2. Si todas calificadas → CALIFICADA
        3. Si tiene entregas pero no todas calificadas → ENTREGADA
        4. Si entrega tardía → ENTREGADA_TARDIA
        5. Si pasó fecha límite → VENCIDA
        6. Si quedan < 48h → PROXIMA_A_VENCER
        7. Default → PENDIENTE
        """
        # Rule 1: Cancelada
        if estado_tarea == EstadoTarea.CANCELADA:
            return EstadoVisualizacion.CANCELADA

        # Rule 2: Todas calificadas
        if todas_calificadas and tiene_entregas:
            return EstadoVisualizacion.CALIFICADA

        # Rule 3 & 4: Entregada
        if tiene_entregas:
            return (
                EstadoVisualizacion.ENTREGADA_TARDIA
                if es_tardia
                else EstadoVisualizacion.ENTREGADA
            )

        # Rule 5: Vencida
        tiempo_restante = EstadoCalculator.calcular_tiempo_restante(fecha_limite)
        if tiempo_restante is None:
            return EstadoVisualizacion.VENCIDA

        # Rule 6: Próxima a vencer
        if tiempo_restante.es_urgente:
            return EstadoVisualizacion.PROXIMA_A_VENCER

        # Rule 7: Default
        return EstadoVisualizacion.PENDIENTE

    @staticmethod
    def obtener_info_visual(estado: EstadoVisualizacion) -> EstadoVisual:
        """Mapea estado de visualización a información visual.
        Usa Strategy Pattern para mapeo de estados.
        """
        # Strategy Pattern: Mapping de estados a visuales
        VISUAL_MAPPING = {
            EstadoVisualizacion.PENDIENTE: EstadoVisual(
                estado=EstadoVisualizacion.PENDIENTE,
                color=ColorEstado.GRAY,
                icono=IconoEstado.CLOCK,
                texto="Pendiente",
                tooltip="Tarea sin entregas aún",
            ),
            EstadoVisualizacion.PROXIMA_A_VENCER: EstadoVisual(
                estado=EstadoVisualizacion.PROXIMA_A_VENCER,
                color=ColorEstado.YELLOW,
                icono=IconoEstado.ALERT,
                texto="Próxima a vencer",
                tooltip="Quedan menos de 48 horas",
            ),
            EstadoVisualizacion.VENCIDA: EstadoVisual(
                estado=EstadoVisualizacion.VENCIDA,
                color=ColorEstado.RED,
                icono=IconoEstado.X_CIRCLE,
                texto="Vencida",
                tooltip="Fecha límite expirada",
            ),
            EstadoVisualizacion.ENTREGADA: EstadoVisual(
                estado=EstadoVisualizacion.ENTREGADA,
                color=ColorEstado.BLUE,
                icono=IconoEstado.CHECK,
                texto="Entregada",
                tooltip="Tarea entregada a tiempo",
            ),
            EstadoVisualizacion.ENTREGADA_TARDIA: EstadoVisual(
                estado=EstadoVisualizacion.ENTREGADA_TARDIA,
                color=ColorEstado.ORANGE,
                icono=IconoEstado.ALERT,
                texto="Entregada tarde",
                tooltip="Entrega realizada después de la fecha límite",
            ),
            EstadoVisualizacion.CALIFICADA: EstadoVisual(
                estado=EstadoVisualizacion.CALIFICADA,
                color=ColorEstado.GREEN,
                icono=IconoEstado.STAR,
                texto="Calificada",
                tooltip="Todas las entregas calificadas",
            ),
            EstadoVisualizacion.CANCELADA: EstadoVisual(
                estado=EstadoVisualizacion.CANCELADA,
                color=ColorEstado.GRAY,
                icono=IconoEstado.X_CIRCLE,
                texto="Cancelada",
                tooltip="Tarea cancelada por el docente",
            ),
        }

        return VISUAL_MAPPING.get(
            estado,
            EstadoVisual(
                estado=estado,
                color=ColorEstado.GRAY,
                icono=IconoEstado.CLOCK,
                texto="Desconocido",
                tooltip=None,
            ),
        )


class MetricasCalculator:
    """Calculator para métricas y estadísticas (SRP).
    Encapsula cálculos matemáticos y estadísticos.
    """

    @staticmethod
    def calcular_metricas_progreso(
        total_estudiantes: int, entregas: list[EntregaTarea]
    ) -> MetricasProgreso:
        """Calcula métricas de progreso de una tarea.

        Args:
            total_estudiantes: Total de estudiantes asignados
            entregas: Lista de entregas realizadas

        Returns:
            MetricasProgreso con cálculos realizados
        """
        entregas_realizadas = len(entregas)
        entregas_calificadas = sum(1 for e in entregas if e.calificacion is not None)
        entregas_tardias = sum(1 for e in entregas if e.es_entrega_tardia)

        return MetricasProgreso(
            total_estudiantes=total_estudiantes,
            entregas_realizadas=entregas_realizadas,
            entregas_calificadas=entregas_calificadas,
            entregas_pendientes=total_estudiantes - entregas_realizadas,
            entregas_tardias=entregas_tardias,
        )

    @staticmethod
    def calcular_estadisticas_calificacion(
        entregas: list[EntregaTarea],
    ) -> EstadisticasCalificacion | None:
        """Calcula estadísticas de calificación.

        Args:
            entregas: Lista de entregas calificadas

        Returns:
            EstadisticasCalificacion o None si no hay calificaciones
        """
        calificaciones = [
            e.calificacion for e in entregas if e.calificacion is not None
        ]

        if not calificaciones:
            return None

        # Cálculos estadísticos
        promedio = sum(calificaciones) / len(calificaciones)
        calificaciones_sorted = sorted(calificaciones)
        mediana = calificaciones_sorted[len(calificaciones_sorted) // 2]

        # Desviación estándar
        varianza = sum((x - promedio) ** 2 for x in calificaciones) / len(
            calificaciones
        )
        desviacion = varianza**0.5

        return EstadisticasCalificacion(
            promedio_calificacion=round(promedio, 2),
            calificacion_maxima=max(calificaciones),
            calificacion_minima=min(calificaciones),
            desviacion_estandar=round(desviacion, 2),
            mediana=round(mediana, 2),
        )


class TareaEnriquecidaService:
    """Servicio principal para tareas enriquecidas.
    Aplica Facade Pattern para simplificar interacciones complejas.
    """

    def __init__(self, db: Session) -> None:
        """Inicializa el servicio con dependency injection.

        Args:
            db: Sesión de base de datos (DIP: Dependency Inversion)
        """
        self.db = db
        self.estado_calculator = EstadoCalculator()
        self.metricas_calculator = MetricasCalculator()

    def obtener_tarea_enriquecida(
        self, tarea_id: str, incluir_estadisticas: bool = True
    ) -> TareaEnriquecida | None:
        """Obtiene una tarea con toda su información enriquecida.

        Args:
            tarea_id: ID de la tarea
            incluir_estadisticas: Si incluir estadísticas de calificación

        Returns:
            TareaEnriquecida o None si no existe
        """
        try:
            # 1. Obtener tarea base
            tarea = self.db.query(Tarea).filter(Tarea.tarea_id == tarea_id).first()
            if not tarea:
                return None

            # 2. Obtener entregas y estudiantes
            entregas = (
                self.db.query(EntregaTarea)
                .filter(EntregaTarea.tarea_id == tarea_id)
                .all()
            )

            # Obtener total de estudiantes del grupo
            total_estudiantes = self._obtener_total_estudiantes_grupo(tarea.grupo_id)

            # 3. Calcular estados
            tiene_entregas = len(entregas) > 0
            todas_calificadas = (
                all(e.calificacion is not None for e in entregas) if entregas else False
            )

            estado_viz = self.estado_calculator.calcular_estado_visualizacion(
                estado_tarea=tarea.estado,
                fecha_limite=tarea.fecha_limite,
                tiene_entregas=tiene_entregas,
                todas_calificadas=todas_calificadas,
            )

            estado_visual = self.estado_calculator.obtener_info_visual(estado_viz)
            tiempo_restante = self.estado_calculator.calcular_tiempo_restante(
                tarea.fecha_limite
            )

            # 4. Calcular métricas
            metricas = self.metricas_calculator.calcular_metricas_progreso(
                total_estudiantes=total_estudiantes, entregas=entregas
            )

            estadisticas_cal = None
            if incluir_estadisticas:
                estadisticas_cal = (
                    self.metricas_calculator.calcular_estadisticas_calificacion(
                        entregas
                    )
                )

            # 5. Calcular flags booleanos
            es_vencida = tiempo_restante is None
            es_proxima_a_vencer = (
                tiempo_restante.es_urgente if tiempo_restante else False
            )
            requiere_atencion = (
                es_proxima_a_vencer
                or metricas.entregas_pendientes > 0
                or (tiene_entregas and not todas_calificadas)
            )
            permite_entregas = not es_vencida or tarea.permite_entrega_tardia

            # 6. Calcular días desde asignación
            dias_desde_asignacion = (datetime.now(UTC) - tarea.fecha_asignacion).days

            # 7. Construir TareaEnriquecida
            # Build a safe dict with expected types/defaults for Pydantic
            def safe_str(v: object) -> str:
                return str(v) if v is not None else ""

            def safe_bool(v: object, default: bool = False) -> bool:
                return bool(v) if v is not None else default

            def safe_float(v: object, default: float = 0.0) -> float:
                try:
                    return float(v) if v is not None else default
                except Exception:
                    return default

            base = {
                "tarea_id": safe_str(tarea.tarea_id),
                "grupo_id": safe_str(tarea.grupo_id),
                "docente_id": safe_str(tarea.docente_id),
                "titulo": tarea.titulo or "",
                "descripcion": tarea.descripcion,
                "instrucciones": tarea.instrucciones,
                "tipo": tarea.tipo,
                "prioridad": tarea.prioridad.value if getattr(tarea, "prioridad", None) is not None else None,
                "estado": tarea.estado,
                "tags": tarea.tags,
                "fecha_limite": tarea.fecha_limite,
                "fecha_inicio_disponible": tarea.fecha_inicio_disponible,
                "tiempo_estimado": tarea.tiempo_estimado or 0,
                # Entrega config
                "permite_entrega_tardia": safe_bool(getattr(tarea, "permite_entrega_tardia", None), False),
                "penalizacion_tardia": safe_float(getattr(tarea, "penalizacion_tardia", None), 0.0),
                "intentos_maximos": int(getattr(tarea, "intentos_maximos", 1) or 1),
                "formato_entrega": tarea.formato_entrega,
                "tamano_maximo_mb": safe_float(getattr(tarea, "tamano_maximo_mb", None), 10.0),
                "puntuacion_maxima": safe_float(getattr(tarea, "puntuacion_maxima", None), 100.0),
                "peso_evaluacion": safe_float(getattr(tarea, "peso_evaluacion", None), 1.0),
                "es_grupal": safe_bool(getattr(tarea, "es_grupal", None), False),
                "es_publica": safe_bool(getattr(tarea, "es_publica", None), True),
                "requiere_aprobacion": safe_bool(getattr(tarea, "requiere_aprobacion", None), False),
                "recursos_necesarios": tarea.recursos_necesarios,
                "criterios_evaluacion": tarea.criterios_evaluacion,
                # Auditoría
                "fecha_asignacion": tarea.fecha_asignacion,
                "fecha_creacion": tarea.fecha_creacion,
                "fecha_actualizacion": tarea.fecha_actualizacion,
                "creado_por": safe_str(getattr(tarea, "creado_por", None)),
                "actualizado_por": safe_str(getattr(tarea, "actualizado_por", None)),
                "activa": safe_bool(getattr(tarea, "activa", None), False),
                # Propiedades calculadas
                "total_entregas": getattr(tarea, "total_entregas", 0) or 0,
                "entregas_pendientes": getattr(tarea, "entregas_pendientes", 0) or 0,
                "promedio_calificaciones": getattr(tarea, "promedio_calificaciones", 0.0) or 0.0,
                "esta_vencida": getattr(tarea, "esta_vencida", False) or False,
            }

            tarea_dict = {
                **base,
                # Campos enriquecidos
                "estado_visualizacion": estado_viz,
                "estado_visual": estado_visual,
                "tiempo_restante": tiempo_restante,
                "dias_desde_asignacion": dias_desde_asignacion,
                "metricas_progreso": metricas,
                "estadisticas_calificacion": estadisticas_cal,
                "es_activa": base["activa"],
                "es_vencida": es_vencida,
                "es_proxima_a_vencer": es_proxima_a_vencer,
                "requiere_atencion": requiere_atencion,
                "permite_entregas": permite_entregas,
                "peso_porcentual": round(base["peso_evaluacion"] * 100, 2),
                "puntos_disponibles": self._calcular_puntos_disponibles(
                    tarea, es_vencida
                ),
            }

            return TareaEnriquecida(**tarea_dict)

        except Exception as e:
            logger.exception(f"Error enriqueciendo tarea {tarea_id}: {e}")
            return None

    def listar_tareas_enriquecidas(
        self, filtros: FiltrosTareaEnriquecida
    ) -> RespuestaPaginada:
        """Lista tareas enriquecidas con filtros y paginación.

        Args:
            filtros: Filtros de búsqueda y paginación

        Returns:
            RespuestaPaginada con tareas enriquecidas
        """
        try:
            # 1. Construir query base
            query = self.db.query(Tarea)

            # 2. Aplicar filtros
            query = self._aplicar_filtros(query, filtros)

            # 3. Contar total
            total = query.count()

            # 4. Aplicar ordenamiento
            query = self._aplicar_ordenamiento(
                query, filtros.ordenar_por, filtros.orden_desc
            )

            # 5. Aplicar paginación
            offset = (filtros.pagina - 1) * filtros.tamaño_pagina
            tareas = query.offset(offset).limit(filtros.tamaño_pagina).all()

            # 6. Enriquecer cada tarea
            tareas_enriquecidas = []
            for tarea in tareas:
                tarea_enriquecida = self.obtener_tarea_enriquecida(
                    tarea_id=str(tarea.tarea_id),
                    incluir_estadisticas=False,  # Optimización: no incluir stats en listas
                )
                if tarea_enriquecida:
                    tareas_enriquecidas.append(tarea_enriquecida)

            # 7. Construir respuesta paginada
            total_paginas = (total + filtros.tamaño_pagina - 1) // filtros.tamaño_pagina

            return RespuestaPaginada(
                items=tareas_enriquecidas,
                total=total,
                pagina=filtros.pagina,
                tamaño_pagina=filtros.tamaño_pagina,
                total_paginas=total_paginas,
                tiene_siguiente=filtros.pagina < total_paginas,
                tiene_anterior=filtros.pagina > 1,
            )

        except Exception as e:
            logger.exception(f"Error listando tareas enriquecidas: {e}")
            return RespuestaPaginada(
                items=[],
                total=0,
                pagina=1,
                tamaño_pagina=filtros.tamaño_pagina,
                total_paginas=0,
                tiene_siguiente=False,
                tiene_anterior=False,
            )

    def _obtener_total_estudiantes_grupo(self, grupo_id: str) -> int:
        """Obtiene total de estudiantes en un grupo."""
        try:
            result = self.db.execute(
                text(
                    """
                    SELECT COUNT(DISTINCT eg.estudiante_id)
                    FROM "EstudianteGrupo" eg
                    WHERE eg.grupo_id = :grupo_id
                """
                ),
                {"grupo_id": grupo_id},
            ).scalar()
            return result or 0
        except Exception as e:
            logger.exception(f"Error obteniendo estudiantes del grupo {grupo_id}: {e}")
            return 0

    def _calcular_puntos_disponibles(self, tarea: Tarea, es_vencida: bool) -> float:
        """Calcula puntos disponibles considerando penalizaciones."""
        if not es_vencida or not tarea.permite_entrega_tardia:
            return tarea.puntuacion_maxima

        penalizacion = (tarea.penalizacion_tardia / 100) * tarea.puntuacion_maxima
        return max(0, tarea.puntuacion_maxima - penalizacion)

    def _aplicar_filtros(self, query, filtros: FiltrosTareaEnriquecida):
        """Aplica filtros a la query."""
        if filtros.grupo_id:
            query = query.filter(Tarea.grupo_id == filtros.grupo_id)

        if filtros.docente_id:
            query = query.filter(Tarea.docente_id == filtros.docente_id)

        if filtros.prioridad:
            query = query.filter(Tarea.prioridad == filtros.prioridad)

        if filtros.solo_activas:
            query = query.filter(Tarea.activa)

        if filtros.solo_proximas_a_vencer:
            fecha_limite = datetime.now(UTC) + timedelta(hours=48)
            query = query.filter(
                and_(
                    Tarea.fecha_limite <= fecha_limite,
                    Tarea.fecha_limite > datetime.now(UTC),
                )
            )

        if filtros.solo_vencidas:
            query = query.filter(Tarea.fecha_limite < datetime.now(UTC))

        if filtros.fecha_desde:
            query = query.filter(Tarea.fecha_limite >= filtros.fecha_desde)

        if filtros.fecha_hasta:
            query = query.filter(Tarea.fecha_limite <= filtros.fecha_hasta)

        if filtros.busqueda:
            busqueda_pattern = f"%{filtros.busqueda}%"
            query = query.filter(
                or_(
                    Tarea.titulo.ilike(busqueda_pattern),
                    Tarea.descripcion.ilike(busqueda_pattern),
                )
            )

        return query

    def _aplicar_ordenamiento(self, query, campo: str, desc: bool):
        """Aplica ordenamiento a la query."""
        orden_map = {
            "fecha_limite": Tarea.fecha_limite,
            "fecha_asignacion": Tarea.fecha_asignacion,
            "prioridad": Tarea.prioridad,
            "titulo": Tarea.titulo,
        }

        campo_orden = orden_map.get(campo, Tarea.fecha_limite)
        return query.order_by(campo_orden.desc() if desc else campo_orden.asc())


# Factory Pattern para crear instancias
def crear_servicio_tareas_enriquecidas(db: Session) -> TareaEnriquecidaService:
    """Factory para crear instancia del servicio.
    Facilita testing y dependency injection.
    """
    return TareaEnriquecidaService(db)
