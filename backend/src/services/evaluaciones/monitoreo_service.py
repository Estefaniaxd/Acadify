"""Servicio de Monitoreo en Tiempo Real.

Este servicio maneja:
- Estado en vivo de intentos activos
- Alertas y notificaciones
- Eventos de anti-trampa en tiempo real
- Broadcasting vía WebSocket
- Dashboard de supervisión
"""

from datetime import datetime
import json
from typing import Any
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from src.models.evaluaciones.evaluacion_expandida import (
    Evaluacion,
    IntentoEvaluacion,
    RespuestaEstudiante,
)
from src.models.evaluaciones.intento_respuesta_gamificacion import (
    EstadoIntento,
    NivelRiesgo,
)


class MonitoreoService:
    """Servicio para monitoreo en tiempo real de evaluaciones."""

    def __init__(self, db: Session) -> None:
        self.db = db
        # En producción, esto sería un manager de WebSocket real
        self.active_connections: dict[str, set[Any]] = {}

    # ==================== ESTADO EN VIVO ====================

    def obtener_estado_tiempo_real(self, evaluacion_id: UUID) -> dict[str, Any]:
        """Obtiene el estado actual de una evaluación en tiempo real.

        Returns:
            Estado completo con todos los estudiantes activos
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

        # Obtener todos los intentos activos
        intentos_activos = (
            self.db.query(IntentoEvaluacion)
            .filter(
                IntentoEvaluacion.evaluacion_id == evaluacion_id,
                IntentoEvaluacion.estado_intento.in_(
                    [
                        EstadoIntento.INICIADO,
                        EstadoIntento.EN_PROGRESO,
                        EstadoIntento.PAUSADO,
                    ]
                ),
            )
            .all()
        )

        # Obtener intentos finalizados
        intentos_finalizados = (
            self.db.query(IntentoEvaluacion)
            .filter(
                IntentoEvaluacion.evaluacion_id == evaluacion_id,
                IntentoEvaluacion.estado_intento == EstadoIntento.FINALIZADO,
            )
            .count()
        )

        # Procesar estudiantes activos
        estudiantes_activos = []
        alertas_activas = []

        for intento in intentos_activos:
            # Calcular tiempo transcurrido
            tiempo_transcurrido = 0
            if intento.fecha_inicio:
                tiempo_transcurrido = (
                    datetime.utcnow() - intento.fecha_inicio
                ).total_seconds()

            # Calcular tiempo restante
            tiempo_restante = None
            if evaluacion.tiempo_limite_minutos:
                tiempo_limite_segundos = evaluacion.tiempo_limite_minutos * 60
                tiempo_restante = max(0, tiempo_limite_segundos - tiempo_transcurrido)

            estudiante_info = {
                "intento_id": str(intento.intento_id),
                "estudiante_id": str(intento.estudiante_id),
                "estado": intento.estado_intento,
                "fecha_inicio": intento.fecha_inicio.isoformat(),
                "tiempo_transcurrido_minutos": tiempo_transcurrido / 60,
                "tiempo_restante_minutos": (
                    (tiempo_restante / 60) if tiempo_restante else None
                ),
                "progreso_porcentaje": intento.progreso_actual,
                "preguntas_respondidas": intento.preguntas_respondidas,
                "total_preguntas": intento.total_preguntas,
                "pregunta_actual": intento.pregunta_actual_orden,
                "nivel_riesgo": intento.nivel_riesgo,
                "puntuacion_riesgo": intento.puntuacion_riesgo,
                "eventos_antitrampa": intento.total_eventos_antitrampa,
                "ultima_actividad": self._obtener_ultima_actividad(intento),
            }

            estudiantes_activos.append(estudiante_info)

            # Generar alertas si es necesario
            alertas = self._generar_alertas(
                intento, evaluacion, tiempo_transcurrido, tiempo_restante
            )
            alertas_activas.extend(alertas)

        # Estadísticas generales
        return {
            "evaluacion_id": str(evaluacion_id),
            "titulo": evaluacion.titulo,
            "estado_evaluacion": evaluacion.estado,
            "fecha_apertura": (
                evaluacion.fecha_apertura.isoformat()
                if evaluacion.fecha_apertura
                else None
            ),
            "fecha_cierre": (
                evaluacion.fecha_cierre.isoformat() if evaluacion.fecha_cierre else None
            ),
            "tiempo_limite_minutos": evaluacion.tiempo_limite_minutos,
            "total_estudiantes_activos": len(intentos_activos),
            "total_finalizados": intentos_finalizados,
            "total_intentos": len(intentos_activos) + intentos_finalizados,
            "estudiantes_activos": estudiantes_activos,
            "alertas_activas": alertas_activas,
            "distribucion_progreso": self._calcular_distribucion_progreso(
                intentos_activos
            ),
            "distribucion_riesgo": self._calcular_distribucion_riesgo(intentos_activos),
            "ultima_actualizacion": datetime.utcnow().isoformat(),
        }

    def _obtener_ultima_actividad(self, intento: IntentoEvaluacion) -> str | None:
        """Obtiene la última actividad registrada del intento."""
        ultima_respuesta = (
            self.db.query(RespuestaEstudiante)
            .filter(RespuestaEstudiante.intento_id == intento.id)
            .order_by(RespuestaEstudiante.respuesta_id.desc())
            .first()
        )

        if ultima_respuesta:
            # Calcular hace cuánto tiempo
            datetime.utcnow()
            # Nota: RespuestaEstudiante necesitaría un campo fecha_creacion
            # Por ahora retornamos un placeholder
            return "Hace unos momentos"

        return None

    def _generar_alertas(
        self,
        intento: IntentoEvaluacion,
        evaluacion: Evaluacion,
        tiempo_transcurrido: float,
        tiempo_restante: float | None,
    ) -> list[dict[str, Any]]:
        """Genera alertas basadas en el estado del intento."""
        alertas = []

        # Alerta de riesgo alto
        if intento.nivel_riesgo in [NivelRiesgo.ALTO, NivelRiesgo.CRITICO]:
            alertas.append(
                {
                    "tipo": "riesgo_alto",
                    "gravedad": (
                        "alta"
                        if intento.nivel_riesgo == NivelRiesgo.ALTO
                        else "critica"
                    ),
                    "intento_id": str(intento.intento_id),
                    "estudiante_id": str(intento.estudiante_id),
                    "mensaje": f"Nivel de riesgo {intento.nivel_riesgo} detectado",
                    "puntuacion_riesgo": intento.puntuacion_riesgo,
                    "eventos": intento.total_eventos_antitrampa,
                }
            )

        # Alerta de tiempo
        if tiempo_restante is not None and tiempo_restante < 300:  # Menos de 5 minutos
            alertas.append(
                {
                    "tipo": "tiempo_limite",
                    "gravedad": "media",
                    "intento_id": str(intento.intento_id),
                    "estudiante_id": str(intento.estudiante_id),
                    "mensaje": f"Quedan {int(tiempo_restante / 60)} minutos",
                    "tiempo_restante_segundos": tiempo_restante,
                }
            )

        # Alerta de inactividad
        if intento.estado_intento == EstadoIntento.PAUSADO:
            alertas.append(
                {
                    "tipo": "inactividad",
                    "gravedad": "baja",
                    "intento_id": str(intento.intento_id),
                    "estudiante_id": str(intento.estudiante_id),
                    "mensaje": "Intento pausado",
                }
            )

        # Alerta de detección de IA/plagio
        if intento.detecciones_ia > 0:
            alertas.append(
                {
                    "tipo": "deteccion_ia",
                    "gravedad": "alta",
                    "intento_id": str(intento.intento_id),
                    "estudiante_id": str(intento.estudiante_id),
                    "mensaje": f"Detectadas {intento.detecciones_ia} respuestas con IA",
                    "detecciones": intento.detecciones_ia,
                }
            )

        if intento.detecciones_plagio > 0:
            alertas.append(
                {
                    "tipo": "deteccion_plagio",
                    "gravedad": "alta",
                    "intento_id": str(intento.intento_id),
                    "estudiante_id": str(intento.estudiante_id),
                    "mensaje": f"Detectados {intento.detecciones_plagio} casos de plagio",
                    "detecciones": intento.detecciones_plagio,
                }
            )

        # Alerta de verificación de identidad fallida
        if not intento.verificacion_identidad_exitosa:
            alertas.append(
                {
                    "tipo": "identidad_no_verificada",
                    "gravedad": "critica",
                    "intento_id": str(intento.intento_id),
                    "estudiante_id": str(intento.estudiante_id),
                    "mensaje": "Verificación de identidad facial fallida",
                }
            )

        return alertas

    def _calcular_distribucion_progreso(
        self, intentos: list[IntentoEvaluacion]
    ) -> dict[str, int]:
        """Calcula la distribución de progreso de los estudiantes."""
        if not intentos:
            return {}

        distribucion = {
            "0-25%": 0,
            "26-50%": 0,
            "51-75%": 0,
            "76-100%": 0,
        }

        for intento in intentos:
            progreso = intento.progreso_actual or 0
            if progreso <= 25:
                distribucion["0-25%"] += 1
            elif progreso <= 50:
                distribucion["26-50%"] += 1
            elif progreso <= 75:
                distribucion["51-75%"] += 1
            else:
                distribucion["76-100%"] += 1

        return distribucion

    def _calcular_distribucion_riesgo(
        self, intentos: list[IntentoEvaluacion]
    ) -> dict[str, int]:
        """Calcula la distribución de niveles de riesgo."""
        if not intentos:
            return {}

        distribucion = {
            "NINGUNO": 0,
            "BAJO": 0,
            "MEDIO": 0,
            "ALTO": 0,
            "CRITICO": 0,
        }

        for intento in intentos:
            nivel = intento.nivel_riesgo or "NINGUNO"
            distribucion[nivel] += 1

        return distribucion

    # ==================== EVENTOS DE ANTI-TRAMPA ====================

    def registrar_evento_antitrampa(
        self,
        intento_id: UUID,
        tipo_evento: str,
        gravedad: str,
        detalles: dict[str, Any],
    ) -> dict[str, Any]:
        """Registra un evento de anti-trampa en tiempo real.

        Args:
            intento_id: ID del intento
            tipo_evento: Tipo de evento (cambio_pestana, ia_detectada, etc.)
            gravedad: BAJA, MEDIA, ALTA, CRITICA
            detalles: Información adicional del evento
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

        # Crear evento
        evento = {
            "tipo": tipo_evento,
            "gravedad": gravedad,
            "timestamp": datetime.utcnow().isoformat(),
            "detalles": detalles,
        }

        # Agregar a eventos detallados
        if not intento.eventos_detallados:
            intento.eventos_detallados = []

        intento.eventos_detallados.append(evento)
        intento.total_eventos_antitrampa += 1

        # Actualizar puntuación de riesgo
        pesos = {
            "BAJA": 5,
            "MEDIA": 15,
            "ALTA": 30,
            "CRITICA": 50,
        }

        intento.puntuacion_riesgo += pesos.get(gravedad, 10)
        intento.puntuacion_riesgo = min(intento.puntuacion_riesgo, 100)

        # Actualizar nivel de riesgo
        if intento.puntuacion_riesgo >= 80:
            intento.nivel_riesgo = NivelRiesgo.CRITICO
        elif intento.puntuacion_riesgo >= 60:
            intento.nivel_riesgo = NivelRiesgo.ALTO
        elif intento.puntuacion_riesgo >= 40:
            intento.nivel_riesgo = NivelRiesgo.MEDIO
        elif intento.puntuacion_riesgo >= 20:
            intento.nivel_riesgo = NivelRiesgo.BAJO
        else:
            intento.nivel_riesgo = NivelRiesgo.NINGUNO

        self.db.commit()

        # Broadcast evento a supervisores conectados
        self._broadcast_evento(
            intento.evaluacion_id,
            {
                "tipo": "evento_antitrampa",
                "intento_id": str(intento_id),
                "estudiante_id": str(intento.estudiante_id),
                "evento": evento,
                "nuevo_nivel_riesgo": intento.nivel_riesgo,
                "nueva_puntuacion_riesgo": intento.puntuacion_riesgo,
            },
        )

        return evento

    def obtener_eventos_intento(
        self,
        intento_id: UUID,
        tipo_evento: str | None = None,
        desde: datetime | None = None,
    ) -> list[dict[str, Any]]:
        """Obtiene los eventos de anti-trampa de un intento."""
        intento = (
            self.db.query(IntentoEvaluacion)
            .filter(IntentoEvaluacion.intento_id == intento_id)
            .first()
        )

        if not intento:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Intento no encontrado"
            )

        eventos = intento.eventos_detallados or []

        # Filtrar por tipo
        if tipo_evento:
            eventos = [e for e in eventos if e.get("tipo") == tipo_evento]

        # Filtrar por fecha
        if desde:
            eventos = [
                e
                for e in eventos
                if datetime.fromisoformat(e.get("timestamp", "")) >= desde
            ]

        return eventos

    # ==================== ACCIONES DE SUPERVISIÓN ====================

    def pausar_intento_supervisor(
        self, intento_id: UUID, supervisor_id: UUID, razon: str
    ) -> IntentoEvaluacion:
        """Permite al supervisor pausar un intento activo."""
        intento = (
            self.db.query(IntentoEvaluacion)
            .filter(IntentoEvaluacion.intento_id == intento_id)
            .first()
        )

        if not intento:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Intento no encontrado"
            )

        if intento.estado_intento != EstadoIntento.EN_PROGRESO:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Solo se pueden pausar intentos en progreso",
            )

        intento.estado_intento = EstadoIntento.PAUSADO

        # Registrar evento
        self.registrar_evento_antitrampa(
            intento_id=intento_id,
            tipo_evento="pausa_supervisor",
            gravedad="ALTA",
            detalles={"supervisor_id": str(supervisor_id), "razon": razon},
        )

        self.db.commit()
        self.db.refresh(intento)

        return intento

    def finalizar_intento_supervisor(
        self, intento_id: UUID, supervisor_id: UUID, razon: str
    ) -> IntentoEvaluacion:
        """Permite al supervisor finalizar un intento forzosamente."""
        intento = (
            self.db.query(IntentoEvaluacion)
            .filter(IntentoEvaluacion.intento_id == intento_id)
            .first()
        )

        if not intento:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Intento no encontrado"
            )

        if intento.estado_intento == EstadoIntento.FINALIZADO:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El intento ya está finalizado",
            )

        intento.estado_intento = EstadoIntento.FINALIZADO
        intento.fecha_fin = datetime.utcnow()

        # Registrar evento
        self.registrar_evento_antitrampa(
            intento_id=intento_id,
            tipo_evento="finalizacion_supervisor",
            gravedad="CRITICA",
            detalles={"supervisor_id": str(supervisor_id), "razon": razon},
        )

        self.db.commit()
        self.db.refresh(intento)

        return intento

    def enviar_mensaje_estudiante(
        self, intento_id: UUID, supervisor_id: UUID, mensaje: str
    ) -> dict[str, Any]:
        """Permite al supervisor enviar un mensaje al estudiante durante la evaluación."""
        intento = (
            self.db.query(IntentoEvaluacion)
            .filter(IntentoEvaluacion.intento_id == intento_id)
            .first()
        )

        if not intento:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Intento no encontrado"
            )

        notificacion = {
            "tipo": "mensaje_supervisor",
            "timestamp": datetime.utcnow().isoformat(),
            "supervisor_id": str(supervisor_id),
            "mensaje": mensaje,
        }

        # Broadcast mensaje al estudiante
        self._broadcast_to_student(intento.estudiante_id, notificacion)

        return notificacion

    # ==================== WEBSOCKET MANAGEMENT ====================

    def _broadcast_evento(self, evaluacion_id: UUID, data: dict[str, Any]) -> None:
        """Envía un evento a todos los supervisores conectados a una evaluación.

        Nota: En producción, esto usaría un WebSocket manager real
        """
        room = f"evaluacion_{evaluacion_id}"
        if room in self.active_connections:
            json.dumps(
                {
                    "tipo": "broadcast",
                    "timestamp": datetime.utcnow().isoformat(),
                    "data": data,
                }
            )
            # Aquí se enviaría a todas las conexiones WebSocket
            # for connection in self.active_connections[room]:
            #     await connection.send_text(mensaje)

    def _broadcast_to_student(self, estudiante_id: UUID, data: dict[str, Any]) -> None:
        """Envía un evento a un estudiante específico."""
        room = f"estudiante_{estudiante_id}"
        if room in self.active_connections:
            json.dumps(
                {
                    "tipo": "notificacion",
                    "timestamp": datetime.utcnow().isoformat(),
                    "data": data,
                }
            )
            # Aquí se enviaría a la conexión WebSocket del estudiante

    async def conectar_supervisor(self, evaluacion_id: UUID, connection: Any) -> None:
        """Registra una nueva conexión WebSocket de supervisor."""
        room = f"evaluacion_{evaluacion_id}"
        if room not in self.active_connections:
            self.active_connections[room] = set()
        self.active_connections[room].add(connection)

    async def desconectar_supervisor(
        self, evaluacion_id: UUID, connection: Any
    ) -> None:
        """Elimina una conexión WebSocket de supervisor."""
        room = f"evaluacion_{evaluacion_id}"
        if room in self.active_connections:
            self.active_connections[room].discard(connection)
            if not self.active_connections[room]:
                del self.active_connections[room]

    # ==================== DASHBOARD DE SUPERVISIÓN ====================

    def obtener_dashboard_supervisor(
        self, curso_id: UUID | None = None, institucion_id: UUID | None = None
    ) -> dict[str, Any]:
        """Obtiene datos para el dashboard del supervisor.

        Muestra todas las evaluaciones activas con estudiantes en progreso
        """
        query = self.db.query(Evaluacion).filter(Evaluacion.estado == "ACTIVA")

        if curso_id:
            query = query.filter(Evaluacion.curso_id == curso_id)

        if institucion_id:
            query = query.filter(Evaluacion.institucion_id == institucion_id)

        evaluaciones_activas = query.all()

        dashboard = {
            "total_evaluaciones_activas": len(evaluaciones_activas),
            "evaluaciones": [],
            "resumen": {
                "total_estudiantes_activos": 0,
                "total_alertas_criticas": 0,
                "total_alertas_altas": 0,
            },
        }

        for evaluacion in evaluaciones_activas:
            # Obtener estado de cada evaluación
            estado = self.obtener_estado_tiempo_real(evaluacion.id)

            dashboard["evaluaciones"].append(
                {
                    "evaluacion_id": str(evaluacion.id),
                    "titulo": evaluacion.titulo,
                    "estudiantes_activos": estado["total_estudiantes_activos"],
                    "estudiantes_finalizados": estado["total_finalizados"],
                    "alertas_criticas": sum(
                        1
                        for a in estado["alertas_activas"]
                        if a.get("gravedad") == "critica"
                    ),
                    "alertas_altas": sum(
                        1
                        for a in estado["alertas_activas"]
                        if a.get("gravedad") == "alta"
                    ),
                }
            )

            dashboard["resumen"]["total_estudiantes_activos"] += estado[
                "total_estudiantes_activos"
            ]
            dashboard["resumen"]["total_alertas_criticas"] += sum(
                1 for a in estado["alertas_activas"] if a.get("gravedad") == "critica"
            )
            dashboard["resumen"]["total_alertas_altas"] += sum(
                1 for a in estado["alertas_activas"] if a.get("gravedad") == "alta"
            )

        dashboard["ultima_actualizacion"] = datetime.utcnow().isoformat()

        return dashboard

    # ==================== HISTORIAL DE ACTIVIDAD ====================

    def obtener_historial_actividad(
        self, intento_id: UUID, tipo_actividad: str | None = None
    ) -> list[dict[str, Any]]:
        """Obtiene el historial completo de actividad de un intento.

        Incluye: respuestas, eventos anti-trampa, pausas, capturas multimedia
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

        historial = []

        # Agregar inicio
        historial.append(
            {
                "tipo": "inicio",
                "timestamp": intento.fecha_inicio.isoformat(),
                "descripcion": "Intento iniciado",
            }
        )

        # Agregar respuestas
        respuestas = (
            self.db.query(RespuestaEstudiante)
            .filter(RespuestaEstudiante.intento_id == intento_id)
            .all()
        )

        for respuesta in respuestas:
            # Nota: RespuestaEstudiante necesitaría campo fecha_creacion
            historial.append(
                {
                    "tipo": "respuesta",
                    "timestamp": intento.fecha_inicio.isoformat(),  # Placeholder
                    "descripcion": "Pregunta respondida",
                    "pregunta_id": str(respuesta.pregunta_id),
                    "es_correcta": respuesta.es_correcta,
                }
            )

        # Agregar eventos anti-trampa
        for evento in intento.eventos_detallados or []:
            historial.append(
                {
                    "tipo": "evento_antitrampa",
                    "timestamp": evento.get("timestamp"),
                    "descripcion": f"Evento: {evento.get('tipo')}",
                    "gravedad": evento.get("gravedad"),
                    "detalles": evento.get("detalles"),
                }
            )

        # Agregar finalización
        if intento.fecha_fin:
            historial.append(
                {
                    "tipo": "finalizacion",
                    "timestamp": intento.fecha_fin.isoformat(),
                    "descripcion": "Intento finalizado",
                }
            )

        # Ordenar por timestamp
        historial.sort(key=lambda x: x.get("timestamp", ""))

        # Filtrar por tipo si se especifica
        if tipo_actividad:
            historial = [h for h in historial if h["tipo"] == tipo_actividad]

        return historial
