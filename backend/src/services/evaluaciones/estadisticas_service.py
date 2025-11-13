"""Servicio de Estadísticas y Analytics para Evaluaciones.

Este servicio maneja:
- Estadísticas de evaluación
- Estadísticas de estudiantes
- Análisis de preguntas
- Distribuciones y tendencias
- Insights con IA
- Exportación de datos
"""

from datetime import datetime
import statistics
from typing import Any, Literal
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from src.models.evaluaciones.evaluacion_expandida import (
    Evaluacion,
    IntentoEvaluacion,
    PreguntaEvaluacion,
    RespuestaEstudiante,
)
from src.models.evaluaciones.intento_respuesta_gamificacion import EstadoIntento
from src.services.evaluaciones.ia_evaluacion_service import IAEvaluacionService


class EstadisticasService:
    """Servicio para estadísticas y analytics de evaluaciones."""

    def __init__(self, db: Session) -> None:
        self.db = db
        self.ia_service = IAEvaluacionService()

    # ==================== ESTADÍSTICAS DE EVALUACIÓN ====================

    def obtener_estadisticas_evaluacion(
        self, evaluacion_id: UUID, incluir_insights_ia: bool = True
    ) -> dict[str, Any]:
        """Obtiene estadísticas completas de una evaluación."""
        evaluacion = (
            self.db.query(Evaluacion)
            .filter(Evaluacion.evaluacion_id == evaluacion_id)
            .first()
        )

        if not evaluacion:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Evaluación no encontrada"
            )

        # Obtener intentos finalizados
        intentos = (
            self.db.query(IntentoEvaluacion)
            .filter(
                IntentoEvaluacion.evaluacion_id == evaluacion_id,
                IntentoEvaluacion.estado_intento == EstadoIntento.FINALIZADO,
            )
            .all()
        )

        if not intentos:
            return self._estadisticas_vacias()

        # Estadísticas básicas
        calificaciones = [i.porcentaje for i in intentos if i.porcentaje is not None]
        tiempos = [
            i.tiempo_total_segundos
            for i in intentos
            if i.tiempo_total_segundos is not None
        ]

        estadisticas = {
            "evaluacion_id": str(evaluacion_id),
            "titulo": evaluacion.titulo,
            "total_intentos": len(intentos),
            "intentos_completados": len(intentos),
            "tasa_completacion": 100.0,  # Todos están finalizados
            # Calificaciones
            "calificacion_promedio": (
                statistics.mean(calificaciones) if calificaciones else 0
            ),
            "calificacion_mediana": (
                statistics.median(calificaciones) if calificaciones else 0
            ),
            "calificacion_moda": (
                statistics.mode(calificaciones)
                if len(calificaciones) > 1
                else (calificaciones[0] if calificaciones else 0)
            ),
            "desviacion_estandar": (
                statistics.stdev(calificaciones) if len(calificaciones) > 1 else 0
            ),
            "calificacion_minima": min(calificaciones) if calificaciones else 0,
            "calificacion_maxima": max(calificaciones) if calificaciones else 0,
            # Aprobación
            "total_aprobados": sum(1 for i in intentos if i.aprobado),
            "total_reprobados": sum(1 for i in intentos if not i.aprobado),
            "tasa_aprobacion": (
                (sum(1 for i in intentos if i.aprobado) / len(intentos)) * 100
                if intentos
                else 0
            ),
            # Tiempo
            "tiempo_promedio_minutos": (
                (statistics.mean(tiempos) / 60) if tiempos else 0
            ),
            "tiempo_mediano_minutos": (
                (statistics.median(tiempos) / 60) if tiempos else 0
            ),
            "tiempo_minimo_minutos": (min(tiempos) / 60) if tiempos else 0,
            "tiempo_maximo_minutos": (max(tiempos) / 60) if tiempos else 0,
            # Distribución de calificaciones
            "distribucion_calificaciones": self._calcular_distribucion(calificaciones),
            # Análisis de preguntas
            "preguntas_mas_dificiles": self._obtener_preguntas_dificiles(
                evaluacion_id, limite=5
            ),
            "preguntas_mas_faciles": self._obtener_preguntas_faciles(
                evaluacion_id, limite=5
            ),
            # Anti-trampa
            "total_eventos_antitrampa": sum(
                i.total_eventos_antitrampa for i in intentos
            ),
            "intentos_con_alto_riesgo": sum(
                1 for i in intentos if i.nivel_riesgo in ["ALTO", "CRITICO"]
            ),
            "detecciones_ia": sum(i.detecciones_ia for i in intentos),
            "detecciones_plagio": sum(i.detecciones_plagio for i in intentos),
            # Revisión manual
            "intentos_pendientes_revision": sum(
                1 for i in intentos if i.requiere_revision_manual
            ),
        }

        # Insights con IA si está habilitado
        if incluir_insights_ia and evaluacion.usar_ia_calificacion:
            try:
                insights = self._generar_insights_ia(evaluacion, intentos, estadisticas)
                estadisticas["insights_ia"] = insights
            except Exception:
                estadisticas["insights_ia"] = []

        return estadisticas

    def _calcular_distribucion(self, calificaciones: list[float]) -> dict[str, int]:
        """Calcula la distribución de calificaciones en rangos."""
        if not calificaciones:
            return {}

        distribucion = {
            "0-20": 0,
            "21-40": 0,
            "41-60": 0,
            "61-80": 0,
            "81-100": 0,
        }

        for calif in calificaciones:
            if calif <= 20:
                distribucion["0-20"] += 1
            elif calif <= 40:
                distribucion["21-40"] += 1
            elif calif <= 60:
                distribucion["41-60"] += 1
            elif calif <= 80:
                distribucion["61-80"] += 1
            else:
                distribucion["81-100"] += 1

        return distribucion

    def _obtener_preguntas_dificiles(
        self, evaluacion_id: UUID, limite: int = 5
    ) -> list[dict[str, Any]]:
        """Obtiene las preguntas con menor tasa de aciertos."""
        preguntas = (
            self.db.query(
                PreguntaEvaluacion.pregunta_id,
                PreguntaEvaluacion.titulo,
                PreguntaEvaluacion.tipo_pregunta,
                PreguntaEvaluacion.promedio_aciertos,
                PreguntaEvaluacion.veces_utilizada,
            )
            .filter(
                PreguntaEvaluacion.evaluacion_id == evaluacion_id,
                PreguntaEvaluacion.veces_utilizada > 0,
            )
            .order_by(PreguntaEvaluacion.promedio_aciertos.asc())
            .limit(limite)
            .all()
        )

        return [
            {
                "pregunta_id": str(p.id),
                "titulo": p.titulo,
                "tipo": p.tipo_pregunta,
                "tasa_aciertos": p.promedio_aciertos,
                "veces_utilizada": p.veces_utilizada,
            }
            for p in preguntas
        ]

    def _obtener_preguntas_faciles(
        self, evaluacion_id: UUID, limite: int = 5
    ) -> list[dict[str, Any]]:
        """Obtiene las preguntas con mayor tasa de aciertos."""
        preguntas = (
            self.db.query(
                PreguntaEvaluacion.pregunta_id,
                PreguntaEvaluacion.titulo,
                PreguntaEvaluacion.tipo_pregunta,
                PreguntaEvaluacion.promedio_aciertos,
                PreguntaEvaluacion.veces_utilizada,
            )
            .filter(
                PreguntaEvaluacion.evaluacion_id == evaluacion_id,
                PreguntaEvaluacion.veces_utilizada > 0,
            )
            .order_by(PreguntaEvaluacion.promedio_aciertos.desc())
            .limit(limite)
            .all()
        )

        return [
            {
                "pregunta_id": str(p.id),
                "titulo": p.titulo,
                "tipo": p.tipo_pregunta,
                "tasa_aciertos": p.promedio_aciertos,
                "veces_utilizada": p.veces_utilizada,
            }
            for p in preguntas
        ]

    def _generar_insights_ia(
        self,
        evaluacion: Evaluacion,
        intentos: list[IntentoEvaluacion],
        estadisticas: dict[str, Any],
    ) -> list[str]:
        """Genera insights automáticos usando IA."""
        insights = []

        # Insight sobre dificultad general
        promedio = estadisticas["calificacion_promedio"]
        if promedio < 50:
            insights.append(
                "La evaluación parece ser muy difícil. Considera revisar el contenido o ajustar la dificultad de las preguntas."
            )
        elif promedio > 90:
            insights.append(
                "La evaluación parece ser muy fácil. Podrías aumentar la dificultad para mayor discriminación."
            )

        # Insight sobre tiempo
        tiempo_promedio = estadisticas["tiempo_promedio_minutos"]
        if evaluacion.tiempo_limite_minutos:
            ratio = (tiempo_promedio / evaluacion.tiempo_limite_minutos) * 100
            if ratio > 90:
                insights.append(
                    "Los estudiantes están usando casi todo el tiempo disponible. Considera aumentar el límite de tiempo."
                )
            elif ratio < 50:
                insights.append(
                    "Los estudiantes terminan muy rápido. La evaluación podría ser demasiado corta o fácil."
                )

        # Insight sobre anti-trampa
        if estadisticas["detecciones_ia"] > 0:
            insights.append(
                f"Se detectaron {estadisticas['detecciones_ia']} posibles casos de uso de IA. Revisa estos intentos manualmente."
            )

        if estadisticas["detecciones_plagio"] > 0:
            insights.append(
                f"Se detectaron {estadisticas['detecciones_plagio']} posibles casos de plagio. Requiere revisión."
            )

        # Insight sobre distribución
        distribucion = estadisticas["distribucion_calificaciones"]
        if distribucion.get("0-20", 0) > len(intentos) * 0.3:
            insights.append(
                "Más del 30% de estudiantes está reprobando con calificaciones muy bajas. Considera intervención académica."
            )

        return insights

    def _estadisticas_vacias(self) -> dict[str, Any]:
        """Retorna estructura de estadísticas vacía."""
        return {
            "total_intentos": 0,
            "calificacion_promedio": 0,
            "tasa_aprobacion": 0,
            "mensaje": "No hay intentos finalizados aún",
        }

    # ==================== ESTADÍSTICAS DE ESTUDIANTE ====================

    def obtener_estadisticas_estudiante(
        self,
        estudiante_id: UUID,
        evaluacion_id: UUID | None = None,
        curso_id: UUID | None = None,
    ) -> dict[str, Any]:
        """Obtiene estadísticas de desempeño de un estudiante."""
        query = self.db.query(IntentoEvaluacion).filter(
            IntentoEvaluacion.estudiante_id == estudiante_id,
            IntentoEvaluacion.estado_intento == EstadoIntento.FINALIZADO,
        )

        if evaluacion_id:
            query = query.filter(IntentoEvaluacion.evaluacion_id == evaluacion_id)

        if curso_id:
            query = query.join(Evaluacion).filter(Evaluacion.curso_id == curso_id)

        intentos = query.order_by(IntentoEvaluacion.fecha_inicio.asc()).all()

        if not intentos:
            return {
                "estudiante_id": str(estudiante_id),
                "total_evaluaciones": 0,
                "mensaje": "No hay evaluaciones completadas",
            }

        calificaciones = [i.porcentaje for i in intentos if i.porcentaje is not None]

        return {
            "estudiante_id": str(estudiante_id),
            "total_evaluaciones": len(intentos),
            "evaluaciones_aprobadas": sum(1 for i in intentos if i.aprobado),
            "evaluaciones_reprobadas": sum(1 for i in intentos if not i.aprobado),
            "tasa_aprobacion": (sum(1 for i in intentos if i.aprobado) / len(intentos))
            * 100,
            "promedio_general": (
                statistics.mean(calificaciones) if calificaciones else 0
            ),
            "calificacion_minima": min(calificaciones) if calificaciones else 0,
            "calificacion_maxima": max(calificaciones) if calificaciones else 0,
            "tendencia": self._calcular_tendencia(intentos),
            "progreso": self._calcular_progreso(intentos),
            "tiempo_promedio_minutos": (
                statistics.mean(
                    [
                        i.tiempo_total_segundos / 60
                        for i in intentos
                        if i.tiempo_total_segundos
                    ]
                )
                if intentos
                else 0
            ),
            "puntos_totales_ganados": sum(
                i.puntos_ganados for i in intentos if i.puntos_ganados
            ),
            "historial_reciente": [
                {
                    "evaluacion_id": str(i.evaluacion_id),
                    "fecha": i.fecha_inicio.isoformat(),
                    "puntuacion": i.porcentaje,
                    "aprobado": i.aprobado,
                    "tiempo_minutos": (
                        (i.tiempo_total_segundos / 60) if i.tiempo_total_segundos else 0
                    ),
                }
                for i in intentos[-10:]  # Últimas 10
            ],
            "recomendaciones": self._generar_recomendaciones_estudiante(intentos),
        }

    def _calcular_tendencia(self, intentos: list[IntentoEvaluacion]) -> str:
        """Calcula la tendencia de desempeño (mejorando, empeorando, estable)."""
        if len(intentos) < 3:
            return "insuficiente_datos"

        # Últimas 5 vs primeras 5
        recientes = intentos[-5:]
        antiguos = intentos[:5]

        promedio_reciente = statistics.mean(
            [i.porcentaje for i in recientes if i.porcentaje]
        )
        promedio_antiguo = statistics.mean(
            [i.porcentaje for i in antiguos if i.porcentaje]
        )

        diferencia = promedio_reciente - promedio_antiguo

        if diferencia > 10:
            return "mejorando"
        if diferencia < -10:
            return "empeorando"
        return "estable"

    def _calcular_progreso(self, intentos: list[IntentoEvaluacion]) -> float:
        """Calcula el porcentaje de progreso comparando primeros y últimos intentos."""
        if len(intentos) < 2:
            return 0

        primeros_3 = intentos[:3]
        ultimos_3 = intentos[-3:]

        promedio_inicial = statistics.mean(
            [i.porcentaje for i in primeros_3 if i.porcentaje]
        )
        promedio_actual = statistics.mean(
            [i.porcentaje for i in ultimos_3 if i.porcentaje]
        )

        return promedio_actual - promedio_inicial

    def _generar_recomendaciones_estudiante(
        self, intentos: list[IntentoEvaluacion]
    ) -> list[str]:
        """Genera recomendaciones personalizadas."""
        recomendaciones = []

        if not intentos:
            return recomendaciones

        # Analizar desempeño general
        promedio = statistics.mean([i.porcentaje for i in intentos if i.porcentaje])

        if promedio < 60:
            recomendaciones.append(
                "Tu promedio está por debajo del 60%. Considera buscar ayuda adicional o tutorías."
            )

        # Analizar tendencia
        tendencia = self._calcular_tendencia(intentos)
        if tendencia == "mejorando":
            recomendaciones.append(
                "¡Excelente! Tu desempeño está mejorando consistentemente. Sigue así."
            )
        elif tendencia == "empeorando":
            recomendaciones.append(
                "Tu desempeño ha disminuido recientemente. Es momento de revisar tu estrategia de estudio."
            )

        # Analizar tiempo
        tiempos = [i.tiempo_total_segundos for i in intentos if i.tiempo_total_segundos]
        if tiempos:
            tiempo_promedio = statistics.mean(tiempos) / 60
            if tiempo_promedio < 15:
                recomendaciones.append(
                    "Estás terminando muy rápido. Tómate más tiempo para revisar tus respuestas."
                )

        # Analizar intentos con riesgo
        con_riesgo = sum(1 for i in intentos if i.nivel_riesgo in ["ALTO", "CRITICO"])
        if con_riesgo > 0:
            recomendaciones.append(
                "Algunos de tus intentos tienen alertas de seguridad. Asegúrate de seguir las reglas de la evaluación."
            )

        return recomendaciones

    # ==================== ANÁLISIS DE PREGUNTAS ====================

    def analizar_pregunta(self, pregunta_id: UUID) -> dict[str, Any]:
        """Análisis detallado de una pregunta específica."""
        pregunta = (
            self.db.query(PreguntaEvaluacion)
            .filter(PreguntaEvaluacion.pregunta_id == pregunta_id)
            .first()
        )

        if not pregunta:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Pregunta no encontrada"
            )

        # Obtener todas las respuestas
        respuestas = (
            self.db.query(RespuestaEstudiante)
            .filter(RespuestaEstudiante.pregunta_id == pregunta_id)
            .all()
        )

        if not respuestas:
            return {
                "pregunta_id": str(pregunta_id),
                "veces_utilizada": 0,
                "mensaje": "No hay respuestas registradas",
            }

        correctas = sum(1 for r in respuestas if r.es_correcta)
        tiempos = [
            r.tiempo_respuesta_segundos
            for r in respuestas
            if r.tiempo_respuesta_segundos
        ]
        puntuaciones = [
            r.puntuacion_obtenida
            for r in respuestas
            if r.puntuacion_obtenida is not None
        ]

        return {
            "pregunta_id": str(pregunta_id),
            "titulo": pregunta.titulo,
            "tipo": pregunta.tipo_pregunta,
            "dificultad_configurada": pregunta.dificultad,
            "puntuacion_maxima": pregunta.puntuacion,
            "veces_utilizada": len(respuestas),
            "respuestas_correctas": correctas,
            "respuestas_incorrectas": len(respuestas) - correctas,
            "tasa_aciertos": (correctas / len(respuestas)) * 100 if respuestas else 0,
            "tiempo_promedio_segundos": statistics.mean(tiempos) if tiempos else 0,
            "tiempo_minimo_segundos": min(tiempos) if tiempos else 0,
            "tiempo_maximo_segundos": max(tiempos) if tiempos else 0,
            "puntuacion_promedio": statistics.mean(puntuaciones) if puntuaciones else 0,
            # Índice de dificultad (% que responde correctamente)
            "indice_dificultad": (correctas / len(respuestas)) if respuestas else 0,
            # Índice de discriminación (correlación con desempeño general)
            "indice_discriminacion": self._calcular_indice_discriminacion(pregunta_id),
            "recomendaciones": self._generar_recomendaciones_pregunta(
                pregunta, correctas, len(respuestas)
            ),
        }

    def _calcular_indice_discriminacion(self, pregunta_id: UUID) -> float:
        """Calcula el índice de discriminación de una pregunta.

        Mide si la pregunta diferencia bien entre estudiantes de alto y bajo rendimiento.
        Valores: -1.0 a 1.0 (>0.3 es bueno, <0.2 es malo)
        """
        # Obtener respuestas con el desempeño general del estudiante
        respuestas = (
            self.db.query(RespuestaEstudiante, IntentoEvaluacion.porcentaje)
            .join(IntentoEvaluacion)
            .filter(RespuestaEstudiante.pregunta_id == pregunta_id)
            .all()
        )

        if len(respuestas) < 10:
            return 0.0  # Insuficientes datos

        # Ordenar por desempeño general
        respuestas_ordenadas = sorted(respuestas, key=lambda x: x[1], reverse=True)

        # Grupo superior (27% mejor desempeño)
        n = len(respuestas_ordenadas)
        grupo_superior = respuestas_ordenadas[: int(n * 0.27)]
        grupo_inferior = respuestas_ordenadas[-int(n * 0.27) :]

        # Calcular aciertos en cada grupo
        aciertos_superior = sum(1 for r, _ in grupo_superior if r.es_correcta)
        aciertos_inferior = sum(1 for r, _ in grupo_inferior if r.es_correcta)

        # Índice de discriminación
        return (
            (aciertos_superior - aciertos_inferior) / len(grupo_superior)
            if grupo_superior
            else 0
        )

    def _generar_recomendaciones_pregunta(
        self, pregunta: PreguntaEvaluacion, correctas: int, total: int
    ) -> list[str]:
        """Genera recomendaciones para mejorar una pregunta."""
        recomendaciones = []

        tasa_aciertos = (correctas / total) * 100 if total > 0 else 0

        if tasa_aciertos < 20:
            recomendaciones.append(
                "La pregunta es muy difícil o confusa. Considera revisarla o proporcionar más contexto."
            )
        elif tasa_aciertos > 95:
            recomendaciones.append(
                "La pregunta es demasiado fácil. Considera aumentar la dificultad."
            )

        if pregunta.tiempo_promedio_respuesta:
            if pregunta.tiempo_promedio_respuesta > 300:  # 5 minutos
                recomendaciones.append(
                    "Los estudiantes tardan mucho en responder. La pregunta podría ser demasiado compleja o larga."
                )
            elif pregunta.tiempo_promedio_respuesta < 30:
                recomendaciones.append(
                    "Los estudiantes responden muy rápido. Podría ser una pregunta trivial."
                )

        return recomendaciones

    # ==================== EXPORTACIÓN ====================

    def exportar_resultados(
        self, evaluacion_id: UUID, formato: Literal["csv", "json", "excel"] = "csv"
    ) -> dict[str, Any]:
        """Prepara datos para exportación.

        Returns:
            Dict con los datos formateados para el formato solicitado
        """
        evaluacion = (
            self.db.query(Evaluacion)
            .filter(Evaluacion.evaluacion_id == evaluacion_id)
            .first()
        )

        if not evaluacion:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Evaluación no encontrada"
            )

        # Obtener intentos con información del estudiante
        intentos = (
            self.db.query(IntentoEvaluacion)
            .filter(
                IntentoEvaluacion.evaluacion_id == evaluacion_id,
                IntentoEvaluacion.estado_intento == EstadoIntento.FINALIZADO,
            )
            .all()
        )

        # Preparar datos
        datos = []
        for intento in intentos:
            datos.append(
                {
                    "estudiante_id": str(intento.estudiante_id),
                    "fecha_inicio": intento.fecha_inicio.isoformat(),
                    "fecha_fin": (
                        intento.fecha_fin.isoformat() if intento.fecha_fin else None
                    ),
                    "tiempo_total_minutos": (
                        (intento.tiempo_total_segundos / 60)
                        if intento.tiempo_total_segundos
                        else 0
                    ),
                    "puntuacion_obtenida": intento.puntuacion_obtenida,
                    "puntuacion_maxima": intento.puntuacion_maxima,
                    "porcentaje": intento.porcentaje,
                    "aprobado": intento.aprobado,
                    "preguntas_respondidas": intento.preguntas_respondidas,
                    "total_preguntas": intento.total_preguntas,
                    "nivel_riesgo": intento.nivel_riesgo,
                    "eventos_antitrampa": intento.total_eventos_antitrampa,
                    "requiere_revision": intento.requiere_revision_manual,
                }
            )

        return {
            "evaluacion": {
                "id": str(evaluacion.id),
                "titulo": evaluacion.titulo,
                "fecha_creacion": evaluacion.fecha_creacion.isoformat(),
            },
            "formato": formato,
            "total_registros": len(datos),
            "datos": datos,
            "fecha_exportacion": datetime.utcnow().isoformat(),
        }

    # ==================== COMPARACIÓN ====================

    def comparar_evaluaciones(self, evaluacion_ids: list[UUID]) -> dict[str, Any]:
        """Compara estadísticas entre múltiples evaluaciones."""
        if len(evaluacion_ids) < 2:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Se requieren al menos 2 evaluaciones para comparar",
            )

        comparacion = []

        for eval_id in evaluacion_ids:
            stats = self.obtener_estadisticas_evaluacion(
                eval_id, incluir_insights_ia=False
            )
            comparacion.append(
                {
                    "evaluacion_id": str(eval_id),
                    "titulo": stats.get("titulo", ""),
                    "promedio": stats.get("calificacion_promedio", 0),
                    "tasa_aprobacion": stats.get("tasa_aprobacion", 0),
                    "total_intentos": stats.get("total_intentos", 0),
                    "tiempo_promedio": stats.get("tiempo_promedio_minutos", 0),
                }
            )

        return {
            "evaluaciones_comparadas": len(evaluacion_ids),
            "comparacion": comparacion,
            "mejor_desempeno": (
                max(comparacion, key=lambda x: x["promedio"]) if comparacion else None
            ),
            "mayor_dificultad": (
                min(comparacion, key=lambda x: x["promedio"]) if comparacion else None
            ),
        }
