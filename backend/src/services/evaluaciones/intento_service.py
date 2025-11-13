"""Servicio de Gestión de Intentos de Evaluación.

Este servicio maneja el ciclo de vida completo de un intento:
- Iniciar intento con validaciones
- Responder preguntas con integración IA/plagiarismo
- Pausar y reanudar intentos
- Finalizar y calificar
- Integración con multimedia y anti-trampa
"""

from datetime import UTC, datetime
import logging
import random
from typing import Any
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.orm import Session


logger = logging.getLogger(__name__)

from src.models.evaluaciones.evaluacion_expandida import (
    Evaluacion,
    PreguntaEvaluacion,
    TipoPregunta,
)
from src.models.evaluaciones.intento_respuesta_gamificacion import (
    EstadoIntento,
    IntentoEvaluacion,
    RespuestaEstudiante,
)
from src.models.evaluaciones.intento_respuesta_gamificacion import (
    NivelRiesgoIntento as NivelRiesgo,
)
from src.schemas.evaluaciones.evaluacion_schemas import (
    IniciarIntentoRequest,
    ResponderPreguntaRequest,
)
from src.services.evaluaciones.evaluacion_service import EvaluacionService
from src.services.evaluaciones.grabacion_multimedia_service import (
    GrabacionMultimediaService,
)
from src.services.evaluaciones.ia_evaluacion_service import IAEvaluacionService


class IntentoService:
    """Servicio para gestión de intentos de evaluación."""

    def __init__(self, db: Session) -> None:
        self.db = db
        self.evaluacion_service = EvaluacionService(db)
        self.ia_service = IAEvaluacionService()
        self.multimedia_service = GrabacionMultimediaService(db)

    # ==================== INICIAR INTENTO ====================

    def iniciar_intento(
        self, request: IniciarIntentoRequest, estudiante_id: UUID
    ) -> IntentoEvaluacion:
        """Inicia un nuevo intento de evaluación con todas las validaciones.

        Proceso:
        1. Validar acceso del estudiante
        2. Crear intento
        3. Generar orden de preguntas (randomizado si aplica)
        4. Iniciar grabación multimedia si aplica
        5. Configurar anti-trampa
        """
        evaluacion = self.evaluacion_service.obtener_evaluacion(
            request.evaluacion_id, incluir_preguntas=True
        )

        # Validar acceso
        puede_acceder, mensaje_error = (
            self.evaluacion_service.validar_acceso_estudiante(
                request.evaluacion_id,
                estudiante_id,
                request.codigo_acceso,
                request.contrasena,
            )
        )

        if not puede_acceder:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail=mensaje_error
            )

        # Validar si es colaborativa y necesita equipo
        if evaluacion.es_colaborativa:
            if not request.equipo_ids or len(request.equipo_ids) < 2:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Esta evaluación requiere un equipo de al menos 2 miembros",
                )

            if (
                evaluacion.max_miembros_equipo
                and len(request.equipo_ids) > evaluacion.max_miembros_equipo
            ):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"El equipo no puede tener más de {evaluacion.max_miembros_equipo} miembros",
                )

        # Obtener preguntas
        preguntas = (
            self.db.query(PreguntaEvaluacion)
            .filter(PreguntaEvaluacion.evaluacion_id == request.evaluacion_id)
            .order_by(PreguntaEvaluacion.orden)
            .all()
        )

        if not preguntas:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La evaluación no tiene preguntas configuradas",
            )

        # Determinar preguntas a mostrar
        num_preguntas_mostrar = evaluacion.num_preguntas_mostrar or len(preguntas)

        if num_preguntas_mostrar < len(preguntas):
            # Seleccionar aleatoriamente
            preguntas = random.sample(preguntas, num_preguntas_mostrar)

        # Randomizar orden si aplica
        if evaluacion.randomizar_preguntas:
            random.shuffle(preguntas)
            orden_preguntas = [str(p.pregunta_id) for p in preguntas]
        else:
            orden_preguntas = [
                str(p.pregunta_id) for p in sorted(preguntas, key=lambda x: x.orden)
            ]

        # Determinar dificultad inicial para evaluaciones adaptativas
        if evaluacion.es_adaptativa:
            # Calcular basado en historial del estudiante
            intentos_previos = (
                self.db.query(IntentoEvaluacion)
                .filter(
                    IntentoEvaluacion.estudiante_id == estudiante_id,
                    IntentoEvaluacion.evaluacion_id != request.evaluacion_id,
                )
                .order_by(IntentoEvaluacion.fecha_inicio.desc())
                .limit(5)
                .all()
            )

            if intentos_previos:
                promedio = sum(
                    i.porcentaje for i in intentos_previos if i.porcentaje
                ) / len(intentos_previos)
                if promedio >= 80 or promedio >= 60:
                    pass
                else:
                    pass
            else:
                pass

        # Crear intento
        intento = IntentoEvaluacion(
            evaluacion_id=request.evaluacion_id,
            estudiante_id=estudiante_id,
            estado=EstadoIntento.INICIADO,
            fecha_inicio=datetime.now(UTC),
            orden_preguntas=orden_preguntas,
            preguntas_respondidas=0,
            pregunta_actual=1,
            puntuacion_maxima=evaluacion.puntuacion_total,
            puntuacion_obtenida=0.0,
            ip_address=request.ip_address,
            user_agent=request.user_agent,
            numero_intento=1,
        )

        # Configurar equipo si es colaborativa
        if evaluacion.es_colaborativa and request.equipo_ids:
            intento.equipo_ids = request.equipo_ids

        self.db.add(intento)
        self.db.flush()  # Para obtener el ID

        # Iniciar grabación multimedia si aplica
        if evaluacion.requerir_camara or evaluacion.grabar_camara_continuo:
            try:
                sesion_id = self.multimedia_service.iniciar_grabacion_continua(
                    intento_id=intento.intento_id,
                    grabar_video=evaluacion.grabar_camara_continuo,
                    grabar_audio=evaluacion.grabar_audio_continuo,
                )
                intento.sesion_grabacion_id = sesion_id
            except Exception:
                # Log error pero no detener el proceso
                pass

        # Cambiar estado a EN_PROGRESO
        intento.estado = EstadoIntento.EN_PROGRESO

        self.db.commit()
        self.db.refresh(intento)

        # Actualizar estadísticas de la evaluación
        self.evaluacion_service.actualizar_estadisticas(request.evaluacion_id)

        return intento

    # ==================== RESPONDER PREGUNTAS ====================

    def responder_pregunta(
        self, request: ResponderPreguntaRequest, estudiante_id: UUID
    ) -> RespuestaEstudiante:
        """Registra la respuesta a una pregunta con análisis completo.

        Proceso:
        1. Validar intento y pregunta
        2. Calificar respuesta (automática, IA o manual)
        3. Detectar IA/plagio si aplica
        4. Capturar multimedia si aplica
        5. Actualizar progreso
        """
        # Obtener intento
        intento = (
            self.db.query(IntentoEvaluacion)
            .filter(IntentoEvaluacion.intento_id == request.intento_id)
            .first()
        )

        if not intento:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Intento no encontrado"
            )

        # Validar que el intento pertenece al estudiante
        if intento.estudiante_id != estudiante_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Este intento no te pertenece",
            )

        # Validar estado del intento
        if intento.estado != EstadoIntento.EN_PROGRESO:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"El intento está en estado {intento.estado}, no se pueden agregar respuestas",
            )

        # Obtener pregunta
        pregunta = (
            self.db.query(PreguntaEvaluacion)
            .filter(PreguntaEvaluacion.pregunta_id == request.pregunta_id)
            .first()
        )

        if not pregunta:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Pregunta no encontrada"
            )

        # Validar que la pregunta pertenece a la evaluación
        if pregunta.evaluacion_id != intento.evaluacion_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La pregunta no pertenece a esta evaluación",
            )

        # Validar que no se haya respondido antes
        respuesta_existente = (
            self.db.query(RespuestaEstudiante)
            .filter(
                RespuestaEstudiante.intento_id == request.intento_id,
                RespuestaEstudiante.pregunta_id == request.pregunta_id,
            )
            .first()
        )

        if respuesta_existente:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Esta pregunta ya fue respondida",
            )

        # Obtener evaluación
        evaluacion = self.evaluacion_service.obtener_evaluacion(intento.evaluacion_id)

        # Crear respuesta
        respuesta = RespuestaEstudiante(
            intento_id=request.intento_id,
            pregunta_id=request.pregunta_id,
            respuesta_texto=request.respuesta,
            tiempo_empleado_segundos=request.tiempo_respuesta_segundos,
            puntuacion_maxima=pregunta.puntuacion,
        )

        # Calificar según tipo
        es_correcta, puntuacion, feedback = self._calificar_respuesta(
            pregunta=pregunta,
            respuesta_estudiante=request.respuesta,
            evaluacion=evaluacion,
            intento=intento,
        )

        respuesta.es_correcta = es_correcta
        respuesta.puntuacion_obtenida = puntuacion
        respuesta.feedback = feedback

        # Detectar IA si está configurado
        if evaluacion.usar_ia_calificacion and pregunta.tipo_pregunta in [
            TipoPregunta.RESPUESTA_CORTA,
            TipoPregunta.ENSAYO,
        ]:
            try:
                resultado_ia = self.ia_service.detectar_ia_en_respuesta(
                    str(request.respuesta)
                )
                respuesta.fue_detectada_ia = resultado_ia["es_ia_generada"]
                respuesta.probabilidad_ia = resultado_ia["probabilidad"]

                if resultado_ia["es_ia_generada"]:
                    intento.detecciones_ia += 1
                    self._registrar_evento_antitrampa(
                        intento=intento,
                        tipo="ia_detectada",
                        gravedad="ALTA",
                        detalles=resultado_ia,
                    )
            except Exception:
                pass

        # Detectar plagio si está configurado (campo no disponible en modelo actual)
        if (
            hasattr(evaluacion, "detectar_plagio")
            and evaluacion.detectar_plagio
            and pregunta.tipo_pregunta
            in [
                TipoPregunta.RESPUESTA_CORTA,
                TipoPregunta.ENSAYO,
            ]
        ):
            try:
                # Obtener otras respuestas para comparar
                otras_respuestas = (
                    self.db.query(RespuestaEstudiante)
                    .filter(
                        RespuestaEstudiante.pregunta_id == request.pregunta_id,
                        RespuestaEstudiante.intento_id != request.intento_id,
                    )
                    .limit(50)
                    .all()
                )

                textos_comparar = [
                    str(r.respuesta_estudiante) for r in otras_respuestas
                ]

                resultado_plagio = self.ia_service.detectar_plagio(
                    texto_estudiante=str(request.respuesta),
                    textos_referencia=textos_comparar,
                )

                respuesta.fue_detectado_plagio = resultado_plagio["es_plagio"]
                respuesta.similitud_plagio = resultado_plagio["similitud_maxima"]
                respuesta.fuentes_plagio = resultado_plagio["fuentes_detectadas"]

                if resultado_plagio["es_plagio"]:
                    intento.detecciones_plagio += 1
                    self._registrar_evento_antitrampa(
                        intento=intento,
                        tipo="plagio_detectado",
                        gravedad="ALTA",
                        detalles=resultado_plagio,
                    )
            except Exception:
                pass

        # Capturar multimedia si aplica (campo opcional)
        if (
            hasattr(request, "captura_webcam_base64")
            and request.captura_webcam_base64
            and evaluacion.captura_periodica_webcam
        ):
            try:
                captura_info = self.multimedia_service.capturar_webcam(
                    intento_id=request.intento_id,
                    imagen_base64=request.captura_webcam_base64,
                    evento="respuesta_pregunta",
                )
                intento.total_capturas_webcam += 1

                # Verificar identidad si aplica
                if evaluacion.verificar_identidad_facial:
                    if not captura_info.get("identidad_verificada", True):
                        intento.verificacion_identidad_exitosa = False
                        self._registrar_evento_antitrampa(
                            intento=intento,
                            tipo="identidad_no_verificada",
                            gravedad="CRITICA",
                            detalles=captura_info,
                        )

                # Detectar anomalías
                if captura_info.get("anomalias_detectadas"):
                    intento.capturas_con_anomalias += 1
                    self._registrar_evento_antitrampa(
                        intento=intento,
                        tipo="anomalia_webcam",
                        gravedad="MEDIA",
                        detalles=captura_info,
                    )
            except Exception:
                pass

        # Guardar archivos multimedia de la respuesta
        if request.audio_url:
            respuesta.audio_url = request.audio_url
        if request.video_url:
            respuesta.video_url = request.video_url
        if request.archivo_url:
            respuesta.archivo_url = request.archivo_url

        # Determinar si requiere revisión manual
        if pregunta.tipo_pregunta in [
            TipoPregunta.ENSAYO,
            TipoPregunta.CODIGO,
        ]:
            respuesta.requiere_revision_manual = True

        # Guardar respuesta
        self.db.add(respuesta)

        # Actualizar progreso del intento
        intento.preguntas_respondidas += 1
        total_preguntas = len(intento.orden_preguntas) if intento.orden_preguntas else 1
        intento.progreso_actual = (
            (intento.preguntas_respondidas / total_preguntas) * 100
            if total_preguntas > 0
            else 0
        )
        intento.puntuacion_obtenida += puntuacion

        # Actualizar pregunta actual
        if intento.pregunta_actual < total_preguntas:
            intento.pregunta_actual += 1

        # Actualizar tiempo activo
        if intento.fecha_inicio:
            tiempo_transcurrido = (
                datetime.now(UTC) - intento.fecha_inicio
            ).total_seconds()
            intento.tiempo_activo_segundos = int(tiempo_transcurrido)
            intento.tiempo_total_segundos = int(tiempo_transcurrido)

        # Si es adaptativa, ajustar dificultad
        if evaluacion.es_adaptativa:
            self._ajustar_dificultad_adaptativa(intento, es_correcta)

        # Calcular nivel de riesgo
        self._calcular_nivel_riesgo(intento)

        self.db.commit()
        self.db.refresh(respuesta)

        # Actualizar estadísticas de la pregunta
        self._actualizar_estadisticas_pregunta(
            pregunta, es_correcta, request.tiempo_respuesta_segundos
        )

        return respuesta

    def _calificar_respuesta(
        self,
        pregunta: PreguntaEvaluacion,
        respuesta_estudiante: Any,
        evaluacion: Evaluacion,
        intento: IntentoEvaluacion,
    ) -> tuple[bool, float, str]:
        """Califica una respuesta según el tipo de pregunta y configuración.

        Returns:
            Tuple con (es_correcta, puntuacion, feedback)
        """
        # Preguntas de calificación automática
        if pregunta.tipo_pregunta in [
            TipoPregunta.OPCION_MULTIPLE,
            TipoPregunta.VERDADERO_FALSO,
            TipoPregunta.SELECCION_MULTIPLE,
        ]:
            es_correcta = str(respuesta_estudiante) == str(pregunta.respuesta_correcta)

            if es_correcta:
                puntuacion = pregunta.puntuacion
                feedback = "¡Respuesta correcta!"
            else:
                if evaluacion.penalizacion_respuesta_incorrecta:
                    puntuacion = -evaluacion.penalizacion_respuesta_incorrecta
                else:
                    puntuacion = 0
                feedback = f"Respuesta incorrecta. La respuesta correcta es: {pregunta.respuesta_correcta}"

            return es_correcta, puntuacion, feedback

        # Respuestas cortas con coincidencia
        if pregunta.tipo_pregunta == TipoPregunta.RESPUESTA_CORTA:
            respuesta_str = str(respuesta_estudiante).strip().lower()
            correcta_str = str(pregunta.respuesta_correcta).strip().lower()

            es_correcta = respuesta_str == correcta_str

            # Verificar respuestas alternativas
            if not es_correcta and pregunta.respuestas_alternativas:
                for alt in pregunta.respuestas_alternativas:
                    if respuesta_str == str(alt).strip().lower():
                        es_correcta = True
                        break

            if es_correcta:
                puntuacion = pregunta.puntuacion
                feedback = "¡Correcto!"
            # Calificar con IA si está configurado
            elif evaluacion.usar_ia_calificacion:
                try:
                    resultado_ia = self.ia_service.calificar_respuesta_con_ia(
                        respuesta=respuesta_str,
                        pregunta=pregunta.enunciado,
                        respuesta_correcta=correcta_str,
                        rubrica=evaluacion.rubrica_ia,
                    )
                    puntuacion = (
                        resultado_ia["puntuacion"] / 100
                    ) * pregunta.puntuacion
                    feedback = resultado_ia["feedback"]
                    es_correcta = puntuacion >= (pregunta.puntuacion * 0.7)
                except:
                    puntuacion = 0
                    feedback = "Respuesta incorrecta"
            else:
                puntuacion = 0
                feedback = "Respuesta incorrecta"

            return es_correcta, puntuacion, feedback

        # Ensayos y código - requieren revisión manual o IA
        if pregunta.tipo_pregunta in [
            TipoPregunta.ENSAYO,
            TipoPregunta.CODIGO,
        ]:
            if evaluacion.usar_ia_calificacion:
                try:
                    resultado_ia = self.ia_service.calificar_respuesta_con_ia(
                        respuesta=str(respuesta_estudiante),
                        pregunta=pregunta.enunciado,
                        rubrica=evaluacion.rubrica_ia,
                        contexto_estudiante=self._obtener_contexto_estudiante(
                            intento.estudiante_id
                        ),
                    )
                    puntuacion = (
                        resultado_ia["puntuacion"] / 100
                    ) * pregunta.puntuacion
                    feedback = resultado_ia["feedback"]
                    es_correcta = puntuacion >= (pregunta.puntuacion * 0.6)
                except Exception:
                    puntuacion = 0
                    feedback = "Pendiente de revisión manual"
                    es_correcta = False
            else:
                puntuacion = 0
                feedback = "Pendiente de revisión manual"
                es_correcta = False

            return es_correcta, puntuacion, feedback

        # Otros tipos - puntuación parcial por defecto
        if evaluacion.permitir_puntuacion_parcial and pregunta.puntos_respuesta_parcial:
            puntuacion = pregunta.puntos_respuesta_parcial
        else:
            puntuacion = 0
        feedback = "Respuesta registrada"
        es_correcta = False

        return es_correcta, puntuacion, feedback

    # ==================== PAUSAR Y REANUDAR ====================

    def pausar_intento(
        self, intento_id: UUID, estudiante_id: UUID, razon: str | None = None
    ) -> IntentoEvaluacion:
        """Pausa un intento en progreso."""
        intento = self._obtener_intento_validado(intento_id, estudiante_id)

        if intento.estado != EstadoIntento.EN_PROGRESO:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Solo se pueden pausar intentos en progreso",
            )

        evaluacion = self.evaluacion_service.obtener_evaluacion(intento.evaluacion_id)

        if not evaluacion.permitir_pausar:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Esta evaluación no permite pausas",
            )

        intento.estado = EstadoIntento.PAUSADO

        # Actualizar tiempo activo
        if intento.fecha_inicio:
            tiempo_transcurrido = (
                datetime.now(UTC) - intento.fecha_inicio
            ).total_seconds()
            intento.tiempo_activo_segundos = int(
                tiempo_transcurrido - (intento.tiempo_pausado_segundos or 0)
            )

        self.db.commit()
        self.db.refresh(intento)

        return intento

    def reanudar_intento(
        self, intento_id: UUID, estudiante_id: UUID
    ) -> IntentoEvaluacion:
        """Reanuda un intento pausado."""
        intento = self._obtener_intento_validado(intento_id, estudiante_id)

        if intento.estado != EstadoIntento.PAUSADO:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Solo se pueden reanudar intentos pausados",
            )

        intento.estado = EstadoIntento.EN_PROGRESO

        self.db.commit()
        self.db.refresh(intento)

        return intento

    # ==================== FINALIZAR ====================

    def finalizar_intento(
        self, intento_id: UUID, estudiante_id: UUID, forzar: bool = False
    ) -> IntentoEvaluacion:
        """Finaliza un intento y ejecuta el proceso de calificación completo.

        Proceso:
        1. Validar estado
        2. Calcular puntuación final
        3. Determinar aprobación
        4. Generar feedback con IA
        5. Detener grabaciones
        6. Otorgar puntos/insignias
        """
        intento = self._obtener_intento_validado(intento_id, estudiante_id)

        if intento.estado not in [EstadoIntento.EN_PROGRESO, EstadoIntento.PAUSADO]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"No se puede finalizar un intento en estado {intento.estado}",
            )

        evaluacion = self.evaluacion_service.obtener_evaluacion(intento.evaluacion_id)

        # Validar que se respondieron todas las preguntas obligatorias
        if not forzar:
            preguntas_obligatorias = (
                self.db.query(PreguntaEvaluacion)
                .filter(
                    PreguntaEvaluacion.evaluacion_id == intento.evaluacion_id,
                    PreguntaEvaluacion.es_obligatoria,
                )
                .count()
            )

            respuestas_obligatorias = (
                self.db.query(RespuestaEstudiante)
                .join(PreguntaEvaluacion)
                .filter(
                    RespuestaEstudiante.intento_id == intento_id,
                    PreguntaEvaluacion.es_obligatoria,
                )
                .count()
            )

            if respuestas_obligatorias < preguntas_obligatorias:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Debes responder todas las preguntas obligatorias. Respondidas: {respuestas_obligatorias}/{preguntas_obligatorias}",
                )

        # Actualizar estado
        intento.estado = EstadoIntento.FINALIZADO
        intento.fecha_fin = datetime.now(UTC)

        # Calcular tiempo total
        if intento.fecha_inicio:
            tiempo_total = (intento.fecha_fin - intento.fecha_inicio).total_seconds()
            intento.tiempo_total_segundos = int(tiempo_total)

        # Calcular porcentaje
        intento.porcentaje = (
            (intento.puntuacion_obtenida / intento.puntuacion_maxima) * 100
            if intento.puntuacion_maxima > 0
            else 0
        )

        # Determinar aprobación
        intento.aprobado = (
            intento.puntuacion_obtenida >= evaluacion.puntuacion_minima_aprobacion
        )

        # Generar feedback con IA si está configurado
        if evaluacion.generar_feedback_ia and evaluacion.usar_ia_calificacion:
            try:
                feedback_ia = self.ia_service.generar_feedback_personalizado(
                    intento_id=intento_id,
                    estudiante_id=estudiante_id,
                    puntuacion=intento.puntuacion_obtenida,
                    puntuacion_maxima=intento.puntuacion_maxima,
                    tiempo_total=intento.tiempo_total_segundos,
                )
                intento.feedback_ia = feedback_ia
            except Exception:
                pass

        # Detener grabaciones multimedia
        if intento.sesion_grabacion_id:
            try:
                # Aquí se detendría la grabación y se almacenarían las URLs
                pass
            except Exception:
                pass

        self.db.commit()
        self.db.refresh(intento)

        # ========== INTEGRACIÓN CON SISTEMA DE PUNTOS ==========
        # Otorgar puntos automáticamente si la evaluación lo permite
        # TODO: Convertir esta función a async para poder usar await
        if False:  # Temporalmente deshabilitado por await en función sync
            try:
                from src.services.evaluaciones.puntos_integration_service import (
                    PuntosIntegrationService,
                )

                PuntosIntegrationService(self.db)
                # resultado_puntos = await puntos_service.procesar_evaluacion_completada(
                #     intento_id=intento_id,
                #     estudiante_id=estudiante_id
                # )
                resultado_puntos = {}

                # Actualizar intento con insignias ganadas (si las hay)
                if resultado_puntos.get("nuevas_insignias"):
                    if not intento.insignias_ganadas:
                        intento.insignias_ganadas = []
                    intento.insignias_ganadas.extend(
                        resultado_puntos["nuevas_insignias"]
                    )

                # Guardar logros desbloqueados
                if resultado_puntos.get("nuevas_insignias"):
                    if not intento.logros_desbloqueados:
                        intento.logros_desbloqueados = []
                    for insignia in resultado_puntos["nuevas_insignias"]:
                        intento.logros_desbloqueados.append(
                            {
                                "tipo": "insignia",
                                "nombre": insignia["nombre"],
                                "timestamp": datetime.now(UTC).isoformat(),
                            }
                        )

                self.db.commit()

                logger.info(
                    f"Puntos otorgados exitosamente: {resultado_puntos.get('puntos_ganados', 0)} pts "
                    f"para estudiante {estudiante_id} en evaluación {evaluacion.titulo}"
                )

            except Exception as e:
                logger.exception(f"Error otorgando puntos de evaluación: {e!s}")
                # No detener el proceso si falla la gamificación
                # La evaluación ya fue finalizada correctamente

        # Actualizar estadísticas de la evaluación
        self.evaluacion_service.actualizar_estadisticas(intento.evaluacion_id)

        return intento

    # ==================== UTILIDADES ====================

    def _obtener_intento_validado(
        self, intento_id: UUID, estudiante_id: UUID
    ) -> IntentoEvaluacion:
        """Obtiene un intento y valida que pertenece al estudiante."""
        intento = (
            self.db.query(IntentoEvaluacion)
            .filter(IntentoEvaluacion.intento_id == intento_id)
            .first()
        )

        if not intento:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Intento no encontrado"
            )

        if intento.estudiante_id != estudiante_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Este intento no te pertenece",
            )

        return intento

    def _registrar_evento_antitrampa(
        self,
        intento: IntentoEvaluacion,
        tipo: str,
        gravedad: str,
        detalles: dict[str, Any],
    ) -> None:
        """Registra un evento de anti-trampa."""
        if not intento.eventos_detallados:
            intento.eventos_detallados = []

        evento = {
            "tipo": tipo,
            "gravedad": gravedad,
            "timestamp": datetime.now(UTC).isoformat(),
            "detalles": detalles,
        }

        intento.eventos_detallados.append(evento)
        intento.total_eventos_antitrampa += 1

    def _calcular_nivel_riesgo(self, intento: IntentoEvaluacion) -> None:
        """Calcula el nivel de riesgo basado en eventos de anti-trampa."""
        puntuacion = 0

        # Peso por detecciones de IA
        puntuacion += (getattr(intento, "detecciones_ia", 0) or 0) * 20

        # Peso por detecciones de plagio
        puntuacion += (getattr(intento, "detecciones_plagio", 0) or 0) * 25

        # Peso por anomalías en webcam
        puntuacion += (getattr(intento, "capturas_con_anomalias", 0) or 0) * 10

        # Peso por identidad no verificada
        if not (getattr(intento, "verificacion_identidad_exitosa", True) or False):
            puntuacion += 30

        intento.puntuacion_riesgo = min(puntuacion, 100)

        # Determinar nivel
        if puntuacion >= 80:
            intento.nivel_riesgo = NivelRiesgo.CRITICO
        elif puntuacion >= 60:
            intento.nivel_riesgo = NivelRiesgo.ALTO
        elif puntuacion >= 40:
            intento.nivel_riesgo = NivelRiesgo.MEDIO
        elif puntuacion >= 20:
            intento.nivel_riesgo = NivelRiesgo.BAJO
        else:
            intento.nivel_riesgo = NivelRiesgo.NINGUNO

    def _ajustar_dificultad_adaptativa(
        self, intento: IntentoEvaluacion, respuesta_correcta: bool
    ) -> None:
        """Ajusta la dificultad para evaluaciones adaptativas."""
        if not intento.ajustes_dificultad:
            intento.ajustes_dificultad = []

        # Lógica simple de ajuste
        if respuesta_correcta:
            # Aumentar dificultad
            if intento.dificultad_actual == "FACIL":
                intento.dificultad_actual = "MEDIA"
            elif intento.dificultad_actual == "MEDIA":
                intento.dificultad_actual = "DIFICIL"
        # Disminuir dificultad
        elif intento.dificultad_actual == "DIFICIL":
            intento.dificultad_actual = "MEDIA"
        elif intento.dificultad_actual == "MEDIA":
            intento.dificultad_actual = "FACIL"

        ajuste = {
            "timestamp": datetime.now(UTC).isoformat(),
            "nueva_dificultad": intento.dificultad_actual,
            "razon": (
                "respuesta_correcta" if respuesta_correcta else "respuesta_incorrecta"
            ),
        }
        intento.ajustes_dificultad.append(ajuste)

    def _actualizar_estadisticas_pregunta(
        self, pregunta: PreguntaEvaluacion, es_correcta: bool, tiempo_respuesta: int
    ) -> None:
        """Actualiza las estadísticas de una pregunta."""
        # Solo actualizar si los campos existen en el modelo
        if not hasattr(pregunta, "veces_utilizada"):
            return

        pregunta.veces_utilizada += 1

        # Actualizar promedio de aciertos
        total_respuestas = pregunta.veces_utilizada
        aciertos_actuales = (pregunta.promedio_aciertos or 0) * (total_respuestas - 1)

        if es_correcta:
            aciertos_actuales += 1

        pregunta.promedio_aciertos = (aciertos_actuales / total_respuestas) * 100

        # Actualizar tiempo promedio
        if tiempo_respuesta:
            tiempo_acumulado = (pregunta.tiempo_promedio_respuesta or 0) * (
                total_respuestas - 1
            )
            pregunta.tiempo_promedio_respuesta = (
                tiempo_acumulado + tiempo_respuesta
            ) / total_respuestas

        self.db.commit()

    def _obtener_contexto_estudiante(self, estudiante_id: UUID) -> dict[str, Any]:
        """Obtiene contexto del estudiante para personalización de IA."""
        # Obtener historial de intentos
        intentos_previos = (
            self.db.query(IntentoEvaluacion)
            .filter(IntentoEvaluacion.estudiante_id == estudiante_id)
            .order_by(IntentoEvaluacion.fecha_inicio.desc())
            .limit(10)
            .all()
        )

        if not intentos_previos:
            return {}

        return {
            "total_evaluaciones": len(intentos_previos),
            "promedio_general": sum(
                i.porcentaje for i in intentos_previos if i.porcentaje
            )
            / len(intentos_previos),
            "tasa_aprobacion": sum(1 for i in intentos_previos if i.aprobado)
            / len(intentos_previos)
            * 100,
        }
