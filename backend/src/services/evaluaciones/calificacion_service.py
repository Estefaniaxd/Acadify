"""Servicio de Calificación de Evaluaciones.

Este servicio especializado maneja todo lo relacionado con calificación:
- Calificación automática
- Calificación con IA
- Calificación manual
- Calificación híbrida
- Generación de feedback consolidado
- Recalificación
- Revisión de respuestas
"""

import contextlib
from datetime import datetime
from typing import Any, Literal
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import func, or_
from sqlalchemy.orm import Session, joinedload

from src.models.evaluaciones import (
    EstadoIntento,  # Agregado para el fix
    IntentoEvaluacion,
    RespuestaEstudiante,
)
from src.models.evaluaciones.evaluacion_expandida import (
    Evaluacion,
    PreguntaEvaluacion,
)
from src.models.evaluaciones.evaluacion_expandida import (
    TipoPregunta as TipoPregunta,
)
from src.services.evaluaciones.ia_evaluacion_service import IAEvaluacionService


class CalificacionService:
    """Servicio para calificación de evaluaciones."""

    def __init__(self, db: Session) -> None:
        self.db = db
        self.ia_service = IAEvaluacionService()

    # ==================== CALIFICACIÓN AUTOMÁTICA ====================

    def calificar_automaticamente(self, intento_id: UUID) -> IntentoEvaluacion:
        """Califica automáticamente todas las respuestas auto-calificables.

        Tipos auto-calificables:
        - Opción múltiple
        - Verdadero/Falso
        - Selección múltiple
        - Respuesta corta (con respuesta exacta)
        - Emparejamiento
        - Ordenamiento
        """
        intento = (
            self.db.query(IntentoEvaluacion)
            .filter(
                IntentoEvaluacion.intento_id
                == intento_id  # Cambiado de id a intento_id
            )
            .first()
        )

        if not intento:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Intento no encontrado"
            )

        # Obtener todas las respuestas del intento
        respuestas = (
            self.db.query(RespuestaEstudiante)
            .join(PreguntaEvaluacion)
            .filter(RespuestaEstudiante.intento_id == intento_id)
            .options(joinedload(RespuestaEstudiante.pregunta))
            .all()
        )

        puntuacion_total = 0
        respuestas_calificadas = 0

        for respuesta in respuestas:
            pregunta = respuesta.pregunta

            # Solo calificar si es auto-calificable y no ha sido calificada
            if (
                self._es_auto_calificable(pregunta)
                and respuesta.puntuacion_obtenida == 0
            ):
                es_correcta, puntuacion, feedback = (
                    self._calificar_respuesta_automatica(
                        pregunta, respuesta.respuesta_texto
                    )
                )

                respuesta.es_correcta = es_correcta
                respuesta.puntuacion_obtenida = puntuacion
                respuesta.feedback = feedback

                puntuacion_total += puntuacion
                respuestas_calificadas += 1

        # Actualizar puntuación del intento
        intento.puntuacion_obtenida = puntuacion_total
        intento.porcentaje = (
            (puntuacion_total / intento.puntuacion_maxima) * 100
            if intento.puntuacion_maxima > 0
            else 0
        )

        # Verificar si todas las respuestas fueron calificadas
        len(respuestas)
        # DISABLED: requiere_revision_manual field doesn't exist in model
        # if respuestas_calificadas == total_respuestas:
        #     intento.requiere_revision_manual = False

        self.db.commit()
        self.db.refresh(intento)

        return intento

    def _es_auto_calificable(self, pregunta: PreguntaEvaluacion) -> bool:
        """Determina si una pregunta puede ser calificada automáticamente."""
        tipos_auto_calificables = [
            TipoPregunta.OPCION_MULTIPLE,
            TipoPregunta.VERDADERO_FALSO,
            TipoPregunta.SELECCION_MULTIPLE,
            TipoPregunta.RESPUESTA_CORTA,
            TipoPregunta.EMPAREJAMIENTO,
            TipoPregunta.ORDENAMIENTO,
        ]
        return pregunta.tipo_pregunta in tipos_auto_calificables

    def _calificar_respuesta_automatica(
        self, pregunta: PreguntaEvaluacion, respuesta_estudiante: Any
    ) -> tuple[bool, float, str]:
        """Califica una respuesta de forma automática.

        Returns:
            Tuple con (es_correcta, puntuacion, feedback)
        """
        if pregunta.tipo_pregunta in [
            TipoPregunta.OPCION_MULTIPLE,
            TipoPregunta.VERDADERO_FALSO,
        ]:
            es_correcta = str(respuesta_estudiante) == str(pregunta.respuesta_correcta)
            puntuacion = pregunta.puntuacion if es_correcta else 0
            feedback = (
                "¡Correcto!"
                if es_correcta
                else f"Incorrecto. La respuesta correcta es: {pregunta.respuesta_correcta}"
            )
            return es_correcta, puntuacion, feedback

        if pregunta.tipo_pregunta == TipoPregunta.SELECCION_MULTIPLE:
            # Comparar conjuntos de respuestas
            respuestas_set = (
                set(respuesta_estudiante)
                if isinstance(respuesta_estudiante, list)
                else {respuesta_estudiante}
            )
            correctas_set = (
                set(pregunta.respuesta_correcta)
                if isinstance(pregunta.respuesta_correcta, list)
                else {pregunta.respuesta_correcta}
            )

            es_correcta = respuestas_set == correctas_set
            puntuacion = pregunta.puntuacion if es_correcta else 0
            feedback = (
                "¡Correcto!"
                if es_correcta
                else "Incorrecto. Revisa las opciones seleccionadas."
            )
            return es_correcta, puntuacion, feedback

        if pregunta.tipo_pregunta == TipoPregunta.RESPUESTA_CORTA:
            respuesta_str = str(respuesta_estudiante).strip().lower()
            correcta_str = str(pregunta.respuesta_correcta).strip().lower()

            es_correcta = respuesta_str == correcta_str

            # DISABLED: Verificar respuestas alternativas (campo no existe en modelo actual)
            # if not es_correcta and pregunta.respuestas_alternativas:
            #     for alt in pregunta.respuestas_alternativas:
            #         if respuesta_str == str(alt).strip().lower():
            #             es_correcta = True
            #             break

            puntuacion = pregunta.puntuacion if es_correcta else 0
            feedback = "¡Correcto!" if es_correcta else "Incorrecto."
            return es_correcta, puntuacion, feedback

        # Otros tipos requieren lógica específica
        return False, 0, "Pendiente de calificación"

    # ==================== CALIFICACIÓN CON IA ====================

    def calificar_con_ia(
        self, intento_id: UUID, solo_pendientes: bool = True
    ) -> IntentoEvaluacion:
        """Califica respuestas usando IA (Gemini).

        Args:
            intento_id: ID del intento
            solo_pendientes: Si True, solo califica respuestas sin calificar
        """
        intento = (
            self.db.query(IntentoEvaluacion)
            .options(joinedload(IntentoEvaluacion.evaluacion))
            .filter(IntentoEvaluacion.intento_id == intento_id)
            .first()
        )

        if not intento:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Intento no encontrado"
            )

        evaluacion = intento.evaluacion

        if not evaluacion.usar_ia_calificacion:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Esta evaluación no tiene habilitada la calificación con IA",
            )

        # Obtener respuestas
        query = (
            self.db.query(RespuestaEstudiante)
            .join(PreguntaEvaluacion)
            .filter(RespuestaEstudiante.intento_id == intento_id)
        )

        if solo_pendientes:
            query = query.filter(
                or_(
                    # DISABLED:                     RespuestaEstudiante.requiere_revision_manual == True,
                    RespuestaEstudiante.puntuacion_obtenida
                    == 0
                )
            )

        respuestas = query.options(joinedload(RespuestaEstudiante.pregunta)).all()

        puntuacion_total = intento.puntuacion_obtenida or 0

        for respuesta in respuestas:
            pregunta = respuesta.pregunta

            # Solo calificar con IA tipos específicos
            if pregunta.tipo_pregunta in [
                TipoPregunta.RESPUESTA_CORTA,
                TipoPregunta.ENSAYO,
                TipoPregunta.CODIGO,
            ]:
                try:
                    # Obtener contexto del estudiante
                    contexto = self._obtener_contexto_estudiante(intento.estudiante_id)

                    # Calificar con IA
                    resultado_ia = self.ia_service.calificar_respuesta_con_ia(
                        respuesta=str(respuesta.respuesta_texto),
                        pregunta=pregunta.enunciado,
                        respuesta_esperada=pregunta.explicacion,
                        rubrica=evaluacion.rubrica_ia,
                        contexto_estudiante=contexto,
                    )

                    # Convertir puntuación de 0-100 a puntuación de la pregunta
                    puntuacion_normalizada = (
                        resultado_ia["puntuacion"] / 100
                    ) * pregunta.puntuacion

                    # Restar puntuación anterior si existía
                    if respuesta.puntuacion_obtenida:
                        puntuacion_total -= respuesta.puntuacion_obtenida

                    # Aplicar nueva puntuación
                    respuesta.puntuacion_obtenida = puntuacion_normalizada
                    respuesta.feedback_ia = resultado_ia["feedback"]
                    respuesta.es_correcta = puntuacion_normalizada >= (
                        pregunta.puntuacion * 0.6
                    )
                    # DISABLED:                     respuesta.requiere_revision_manual = False

                    puntuacion_total += puntuacion_normalizada

                except Exception:
                    respuesta.feedback_ia = "Error en la calificación automática. Se requiere revisión manual."

        # Actualizar intento
        intento.puntuacion_obtenida = puntuacion_total
        intento.porcentaje = (
            (puntuacion_total / intento.puntuacion_maxima) * 100
            if intento.puntuacion_maxima > 0
            else 0
        )
        intento.aprobado = puntuacion_total >= evaluacion.puntuacion_minima_aprobacion

        # Verificar si quedan respuestas sin calificar
        (
            self.db.query(func.count(RespuestaEstudiante.respuesta_id))
            .filter(
                RespuestaEstudiante.intento_id == intento_id,
                # DISABLED:             RespuestaEstudiante.requiere_revision_manual == True
            )
            .scalar()
        )

        # DISABLED:         intento.requiere_revision_manual = pendientes > 0

        self.db.commit()
        self.db.refresh(intento)

        return intento

    # ==================== CALIFICACIÓN MANUAL ====================

    def calificar_manualmente(
        self, respuesta_id: UUID, puntuacion: float, feedback: str, revisor_id: UUID
    ) -> RespuestaEstudiante:
        """Califica manualmente una respuesta.

        Args:
            respuesta_id: ID de la respuesta
            puntuacion: Puntuación asignada
            feedback: Feedback del revisor
            revisor_id: ID del revisor (docente)
        """
        respuesta = (
            self.db.query(RespuestaEstudiante)
            .options(
                joinedload(RespuestaEstudiante.pregunta),
                joinedload(RespuestaEstudiante.intento),
            )
            .filter(RespuestaEstudiante.respuesta_id == respuesta_id)
            .first()
        )

        if not respuesta:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Respuesta no encontrada"
            )

        pregunta = respuesta.pregunta
        intento = respuesta.intento

        # Validar puntuación
        if puntuacion < 0 or puntuacion > pregunta.puntuacion:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"La puntuación debe estar entre 0 y {pregunta.puntuacion}",
            )

        # Restar puntuación anterior
        puntuacion_anterior = respuesta.puntuacion_obtenida or 0
        intento.puntuacion_obtenida -= puntuacion_anterior

        # Aplicar nueva puntuación
        respuesta.puntuacion_obtenida = puntuacion
        respuesta.feedback_manual = feedback
        respuesta.es_correcta = puntuacion >= (pregunta.puntuacion * 0.6)
        # DISABLED:         respuesta.requiere_revision_manual = False
        respuesta.calificador_id = revisor_id
        respuesta.fecha_revision = datetime.utcnow()

        # Actualizar intento
        intento.puntuacion_obtenida += puntuacion
        intento.porcentaje = (
            (intento.puntuacion_obtenida / intento.puntuacion_maxima) * 100
            if intento.puntuacion_maxima > 0
            else 0
        )

        # Verificar aprobación
        evaluacion = (
            self.db.query(Evaluacion)
            .filter(Evaluacion.evaluacion_id == intento.evaluacion_id)
            .first()
        )

        intento.aprobado = (
            intento.puntuacion_obtenida >= evaluacion.puntuacion_minima_aprobacion
        )

        # Verificar si quedan respuestas pendientes
        (
            self.db.query(func.count(RespuestaEstudiante.respuesta_id))
            .filter(
                RespuestaEstudiante.intento_id == intento.intento_id,
                # DISABLED:             RespuestaEstudiante.requiere_revision_manual == True,
                RespuestaEstudiante.respuesta_id != respuesta_id,
            )
            .scalar()
        )

        # DISABLED:         intento.requiere_revision_manual = pendientes > 0

        self.db.commit()
        self.db.refresh(respuesta)

        return respuesta

    def calificar_lote(
        self, respuestas_data: list[dict[str, Any]], revisor_id: UUID
    ) -> list[RespuestaEstudiante]:
        """Califica múltiples respuestas en lote.

        Args:
            respuestas_data: Lista de dicts con {respuesta_id, puntuacion, feedback}
            revisor_id: ID del revisor
        """
        respuestas_calificadas = []

        for data in respuestas_data:
            try:
                respuesta = self.calificar_manualmente(
                    respuesta_id=data["respuesta_id"],
                    puntuacion=data["puntuacion"],
                    feedback=data.get("feedback", ""),
                    revisor_id=revisor_id,
                )
                respuestas_calificadas.append(respuesta)
            except Exception:
                pass

        return respuestas_calificadas

    # ==================== OBTENER RESPUESTAS PENDIENTES ====================

    def obtener_intentos_pendientes_revision(
        self,
        evaluacion_id: UUID | None = None,
        curso_id: UUID | None = None,
        limite: int = 50,
    ) -> list[IntentoEvaluacion]:
        """Obtiene intentos que requieren revisión manual."""
        query = self.db.query(IntentoEvaluacion).filter(
            # DISABLED:             IntentoEvaluacion.requiere_revision_manual == True
        )

        if evaluacion_id:
            query = query.filter(IntentoEvaluacion.evaluacion_id == evaluacion_id)

        if curso_id:
            query = query.join(Evaluacion).filter(Evaluacion.curso_id == curso_id)

        query = query.order_by(IntentoEvaluacion.fecha_fin.desc())

        if limite:
            query = query.limit(limite)

        return query.all()

    def obtener_respuestas_pendientes(
        self, intento_id: UUID
    ) -> list[RespuestaEstudiante]:
        """Obtiene las respuestas pendientes de revisión de un intento."""
        return (
            self.db.query(RespuestaEstudiante)
            .options(joinedload(RespuestaEstudiante.pregunta))
            .filter(
                RespuestaEstudiante.intento_id == intento_id,
                # DISABLED:             RespuestaEstudiante.requiere_revision_manual == True
            )
            .all()
        )

    # ==================== RECALIFICACIÓN ====================

    def recalificar_intento(
        self,
        intento_id: UUID,
        metodo: Literal["automatica", "ia", "mantener_manual"] = "ia",
    ) -> IntentoEvaluacion:
        """Recalifica un intento completo.

        Args:
            intento_id: ID del intento
            metodo: Método de recalificación (automatica, ia, mantener_manual)
        """
        intento = (
            self.db.query(IntentoEvaluacion)
            .filter(IntentoEvaluacion.intento_id == intento_id)
            .first()
        )

        if not intento:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Intento no encontrado"
            )

        # Resetear puntuación
        intento.puntuacion_obtenida = 0

        # Obtener todas las respuestas
        respuestas = (
            self.db.query(RespuestaEstudiante)
            .options(joinedload(RespuestaEstudiante.pregunta))
            .filter(RespuestaEstudiante.intento_id == intento_id)
            .all()
        )

        for respuesta in respuestas:
            # Mantener calificaciones manuales si se especifica
            if metodo == "mantener_manual" and respuesta.calificador_id:
                intento.puntuacion_obtenida += respuesta.puntuacion_obtenida or 0
                continue

            pregunta = respuesta.pregunta

            # Resetear
            respuesta.puntuacion_obtenida = 0
            respuesta.feedback = None
            respuesta.feedback_ia = None
            # DISABLED:             respuesta.requiere_revision_manual = False

            if metodo == "automatica" and self._es_auto_calificable(pregunta):
                es_correcta, puntuacion, feedback = (
                    self._calificar_respuesta_automatica(
                        pregunta, respuesta.respuesta_texto
                    )
                )
                respuesta.es_correcta = es_correcta
                respuesta.puntuacion_obtenida = puntuacion
                respuesta.feedback = feedback
                intento.puntuacion_obtenida += puntuacion

            elif metodo == "ia" and pregunta.tipo_pregunta in [
                TipoPregunta.RESPUESTA_CORTA,
                TipoPregunta.ENSAYO,
                TipoPregunta.CODIGO,
            ]:
                try:
                    evaluacion = (
                        self.db.query(Evaluacion)
                        .filter(Evaluacion.evaluacion_id == intento.evaluacion_id)
                        .first()
                    )

                    contexto = self._obtener_contexto_estudiante(intento.estudiante_id)

                    resultado_ia = self.ia_service.calificar_respuesta_con_ia(
                        respuesta=str(respuesta.respuesta_texto),
                        pregunta=pregunta.enunciado,
                        respuesta_esperada=pregunta.explicacion,
                        rubrica=evaluacion.rubrica_ia,
                        contexto_estudiante=contexto,
                    )

                    puntuacion = (
                        resultado_ia["puntuacion"] / 100
                    ) * pregunta.puntuacion
                    respuesta.puntuacion_obtenida = puntuacion
                    respuesta.feedback_ia = resultado_ia["feedback"]
                    respuesta.es_correcta = puntuacion >= (pregunta.puntuacion * 0.6)
                    intento.puntuacion_obtenida += puntuacion
                except Exception:
                    pass
                    # DISABLED: respuesta.requiere_revision_manual = True
            else:
                pass  # DISABLED: respuesta.requiere_revision_manual = True

        # Actualizar intento
        intento.porcentaje = (
            (intento.puntuacion_obtenida / intento.puntuacion_maxima) * 100
            if intento.puntuacion_maxima > 0
            else 0
        )

        evaluacion = (
            self.db.query(Evaluacion)
            .filter(Evaluacion.evaluacion_id == intento.evaluacion_id)
            .first()
        )

        intento.aprobado = (
            intento.puntuacion_obtenida >= evaluacion.puntuacion_minima_aprobacion
        )

        # Verificar pendientes
        (
            self.db.query(func.count(RespuestaEstudiante.respuesta_id))
            .filter(
                RespuestaEstudiante.intento_id == intento_id,
                # DISABLED:             RespuestaEstudiante.requiere_revision_manual == True
            )
            .scalar()
        )

        # DISABLED:         intento.requiere_revision_manual = pendientes > 0

        self.db.commit()
        self.db.refresh(intento)

        return intento

    # ==================== FEEDBACK CONSOLIDADO ====================

    def generar_feedback_consolidado(
        self, intento_id: UUID, incluir_ia: bool = True
    ) -> dict[str, Any]:
        """Genera un feedback consolidado del intento completo."""
        intento = (
            self.db.query(IntentoEvaluacion)
            .options(joinedload(IntentoEvaluacion.evaluacion))
            .filter(IntentoEvaluacion.intento_id == intento_id)
            .first()
        )

        if not intento:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Intento no encontrado"
            )

        # Obtener respuestas
        respuestas = (
            self.db.query(RespuestaEstudiante)
            .options(joinedload(RespuestaEstudiante.pregunta))
            .filter(RespuestaEstudiante.intento_id == intento_id)
            .all()
        )

        # Análisis básico
        total_correctas = sum(1 for r in respuestas if r.es_correcta)
        total_incorrectas = len(respuestas) - total_correctas

        # Feedback por pregunta
        feedback_preguntas = []
        for respuesta in respuestas:
            pregunta = respuesta.pregunta
            feedback_preguntas.append(
                {
                    "pregunta_id": str(pregunta.pregunta_id),
                    "titulo": pregunta.titulo,
                    "es_correcta": respuesta.es_correcta,
                    "puntuacion": respuesta.puntuacion_obtenida,
                    "puntuacion_maxima": pregunta.puntuacion,
                    "feedback": respuesta.feedback
                    or respuesta.feedback_ia
                    or respuesta.feedback_manual,
                }
            )

        # Generar feedback con IA si está habilitado
        feedback_ia = None
        if incluir_ia and intento.evaluacion.generar_feedback_ia:
            with contextlib.suppress(Exception):
                feedback_ia = self.ia_service.generar_feedback_personalizado(
                    intento_id=intento_id,
                    estudiante_id=intento.estudiante_id,
                    puntuacion=intento.puntuacion_obtenida,
                    puntuacion_maxima=intento.puntuacion_maxima,
                    tiempo_total=intento.tiempo_total_segundos,
                )

        return {
            "intento_id": str(intento_id),
            "puntuacion_obtenida": intento.puntuacion_obtenida,
            "puntuacion_maxima": intento.puntuacion_maxima,
            "porcentaje": intento.porcentaje,
            "aprobado": intento.aprobado,
            "total_preguntas": len(respuestas),
            "correctas": total_correctas,
            "incorrectas": total_incorrectas,
            "tiempo_total_minutos": (
                intento.tiempo_total_segundos / 60
                if intento.tiempo_total_segundos
                else 0
            ),
            "feedback_preguntas": feedback_preguntas,
            "feedback_ia": feedback_ia,
            "recomendaciones": self._generar_recomendaciones(intento, respuestas),
        }

    def _generar_recomendaciones(
        self, intento: IntentoEvaluacion, respuestas: list[RespuestaEstudiante]
    ) -> list[str]:
        """Genera recomendaciones basadas en el desempeño."""
        recomendaciones = []

        # Análisis de desempeño
        if intento.porcentaje < 60:
            recomendaciones.append(
                "Se recomienda revisar el material del curso y practicar más."
            )
        elif intento.porcentaje < 80:
            recomendaciones.append("Buen trabajo, pero hay áreas que puedes mejorar.")
        else:
            recomendaciones.append("¡Excelente desempeño! Sigue así.")

        # Análisis de tiempo
        evaluacion = intento.evaluacion
        if evaluacion.tiempo_limite_minutos:
            tiempo_usado = (intento.tiempo_total_segundos or 0) / 60
            if tiempo_usado < evaluacion.tiempo_limite_minutos * 0.5:
                recomendaciones.append(
                    "Considera tomarte más tiempo para revisar tus respuestas."
                )

        # Análisis por tipo de pregunta
        tipos_dificultad = {}
        for respuesta in respuestas:
            tipo = respuesta.pregunta.tipo_pregunta
            if tipo not in tipos_dificultad:
                tipos_dificultad[tipo] = {"correctas": 0, "total": 0}
            tipos_dificultad[tipo]["total"] += 1
            if respuesta.es_correcta:
                tipos_dificultad[tipo]["correctas"] += 1

        for tipo, stats in tipos_dificultad.items():
            porcentaje = (
                (stats["correctas"] / stats["total"]) * 100 if stats["total"] > 0 else 0
            )
            if porcentaje < 50:
                recomendaciones.append(
                    f"Refuerza tus conocimientos en preguntas de tipo {tipo}."
                )

        return recomendaciones

    # ==================== UTILIDADES ====================

    def _obtener_contexto_estudiante(self, estudiante_id: UUID) -> dict[str, Any]:
        """Obtiene contexto del estudiante para IA."""
        intentos = (
            self.db.query(IntentoEvaluacion)
            .filter(IntentoEvaluacion.estudiante_id == estudiante_id)
            .order_by(IntentoEvaluacion.fecha_inicio.desc())
            .limit(10)
            .all()
        )

        if not intentos:
            return {}

        return {
            "total_evaluaciones": len(intentos),
            "promedio_general": sum(i.porcentaje for i in intentos if i.porcentaje)
            / len(intentos),
            "tasa_aprobacion": sum(1 for i in intentos if i.aprobado)
            / len(intentos)
            * 100,
        }

    def obtener_estadisticas_calificacion(self, evaluacion_id: UUID) -> dict[str, Any]:
        """Obtiene estadísticas de calificación de una evaluación."""
        # Intentos finalizados
        intentos = (
            self.db.query(IntentoEvaluacion)
            .filter(
                IntentoEvaluacion.evaluacion_id == evaluacion_id,
                IntentoEvaluacion.estado
                == EstadoIntento.FINALIZADO,  # Cambiado de estado_intento a estado
            )
            .all()
        )

        if not intentos:
            return {
                "total_intentos": 0,
                "promedio": 0,
                "mediana": 0,
                "tasa_aprobacion": 0,
            }

        calificaciones = [i.porcentaje for i in intentos if i.porcentaje is not None]
        calificaciones.sort()

        return {
            "total_intentos": len(intentos),
            "promedio": (
                sum(calificaciones) / len(calificaciones) if calificaciones else 0
            ),
            "mediana": (
                calificaciones[len(calificaciones) // 2] if calificaciones else 0
            ),
            "tasa_aprobacion": sum(1 for i in intentos if i.aprobado)
            / len(intentos)
            * 100,
            # DISABLED:             "pendientes_revision": sum(1 for i in intentos if i.requiere_revision_manual),
        }
