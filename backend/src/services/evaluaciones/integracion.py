"""Servicio de integración y utilidades para el sistema de evaluaciones
Coordina operaciones complejas entre diferentes componentes.
"""

from datetime import datetime, timedelta
from typing import Any

from sqlalchemy import and_
from sqlalchemy.orm import Session

from src.models.evaluaciones import (
    BancoPregunta,
    EstadoExamen,
    EstadoIntento,
    EventoAntiTrampa,
    Examen,
    IntentoExamen,
    PreguntaExamen,
    RespuestaEstudiante,
    TipoExamen,
)

from .anti_trampa import detector_anti_trampa
from .calificador import calificador_automatico
from .estadisticas import servicio_estadisticas


class ServicioIntegracionExamenes:
    """Servicio principal para coordinar operaciones complejas del sistema de evaluaciones."""

    def __init__(self) -> None:
        self.calificador = calificador_automatico
        self.detector_trampa = detector_anti_trampa
        self.estadisticas = servicio_estadisticas

    def procesar_intento_completo(
        self,
        db: Session,
        intento_id: int,
        respuestas_finales: list[dict[str, Any]],
        eventos_finales: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        """Procesar un intento completo: calificar todas las respuestas,
        analizar integridad, generar estadísticas.
        """
        # Obtener intento
        intento = (
            db.query(IntentoExamen)
            .filter(IntentoExamen.intento_id == intento_id)
            .first()
        )

        if not intento:
            return {"error": "Intento no encontrado"}

        # Obtener examen y preguntas
        db.query(Examen).filter(Examen.examen_id == intento.examen_id).first()
        preguntas = (
            db.query(PreguntaExamen)
            .filter(PreguntaExamen.examen_id == intento.examen_id)
            .order_by(PreguntaExamen.orden)
            .all()
        )

        resultado_procesamiento = {
            "intento_id": intento_id,
            "examen_id": intento.examen_id,
            "estudiante_id": intento.estudiante_id,
            "timestamp_procesamiento": datetime.utcnow().isoformat(),
            "calificacion": {},
            "integridad": {},
            "estadisticas": {},
            "alertas": [],
            "recomendaciones": [],
        }

        try:
            # 1. Calificar todas las respuestas
            resultado_calificacion = self._calificar_intento_completo(
                db, intento, preguntas, respuestas_finales
            )
            resultado_procesamiento["calificacion"] = resultado_calificacion

            # 2. Análisis de integridad anti-trampa
            if eventos_finales:
                for evento in eventos_finales:
                    self.detector_trampa.registrar_evento(
                        db=db,
                        intento_id=intento_id,
                        tipo_evento=evento["tipo"],
                        datos_evento=evento.get("datos", {}),
                        ip_address=evento.get("ip_address"),
                        user_agent=evento.get("user_agent"),
                    )

            reporte_integridad = self.detector_trampa.generar_reporte_integridad(
                db, intento_id
            )
            resultado_procesamiento["integridad"] = reporte_integridad

            # 3. Actualizar intento con resultados finales
            self._finalizar_intento(
                db, intento, resultado_calificacion, reporte_integridad
            )

            # 4. Generar estadísticas actualizadas del examen
            estadisticas_examen = self.estadisticas.generar_estadisticas_examen(
                db, intento.examen_id, incluir_intentos_incompletos=False
            )
            resultado_procesamiento["estadisticas"] = estadisticas_examen

            # 5. Generar alertas y recomendaciones
            alertas_recomendaciones = self._generar_alertas_recomendaciones(
                resultado_calificacion, reporte_integridad, estadisticas_examen
            )
            resultado_procesamiento.update(alertas_recomendaciones)

            # 6. Notificar si es necesario
            if self._requiere_notificacion(resultado_procesamiento):
                self._programar_notificacion(db, resultado_procesamiento)

            return resultado_procesamiento

        except Exception as e:
            db.rollback()
            return {
                "error": f"Error procesando intento: {e!s}",
                "intento_id": intento_id,
            }

    def crear_examen_desde_banco(
        self,
        db: Session,
        titulo: str,
        descripcion: str,
        clase_id: int,
        creado_por: int,
        configuracion_examen: dict[str, Any],
        criterios_seleccion: dict[str, Any],
    ) -> dict[str, Any]:
        """Crear un examen seleccionando preguntas automáticamente del banco."""
        try:
            # 1. Seleccionar preguntas del banco según criterios
            preguntas_seleccionadas = self._seleccionar_preguntas_banco(
                db, criterios_seleccion
            )

            if not preguntas_seleccionadas:
                return {
                    "error": "No se encontraron preguntas que cumplan los criterios"
                }

            # 2. Crear el examen
            nuevo_examen = Examen(
                titulo=titulo,
                descripcion=descripcion,
                clase_id=clase_id,
                creado_por=creado_por,
                tipo_examen=TipoExamen(
                    configuracion_examen.get("tipo_examen", "EVALUACION")
                ),
                tiempo_limite=configuracion_examen.get("tiempo_limite", 60),
                intentos_permitidos=configuracion_examen.get("intentos_permitidos", 1),
                mostrar_resultados_inmediatos=configuracion_examen.get(
                    "mostrar_resultados", True
                ),
                barajar_preguntas=configuracion_examen.get("barajar_preguntas", True),
                configuracion_anti_trampa=configuracion_examen.get("anti_trampa", {}),
                fecha_creacion=datetime.utcnow(),
                estado_examen=EstadoExamen.BORRADOR,
            )

            db.add(nuevo_examen)
            db.flush()  # Para obtener el ID

            # 3. Crear preguntas del examen basadas en las seleccionadas
            puntuacion_total = 0
            for i, pregunta_banco in enumerate(preguntas_seleccionadas):
                pregunta_examen = PreguntaExamen(
                    examen_id=nuevo_examen.examen_id,
                    texto_pregunta=pregunta_banco.texto_pregunta,
                    tipo_pregunta=pregunta_banco.tipo_pregunta,
                    opciones=pregunta_banco.opciones,
                    respuesta_correcta=pregunta_banco.respuesta_correcta,
                    explicacion=pregunta_banco.explicacion,
                    puntuacion=pregunta_banco.puntuacion_sugerida,
                    dificultad=pregunta_banco.dificultad,
                    orden=i + 1,
                    tiempo_estimado=pregunta_banco.tiempo_estimado,
                    puntos_respuesta_parcial=configuracion_examen.get(
                        "puntos_parciales", True
                    ),
                    configuracion_avanzada={
                        "banco_pregunta_id": pregunta_banco.banco_pregunta_id,
                        "seleccionada_automaticamente": True,
                    },
                )

                db.add(pregunta_examen)
                puntuacion_total += pregunta_banco.puntuacion_sugerida

            # 4. Actualizar puntuación total del examen
            nuevo_examen.puntuacion_total = puntuacion_total

            # 5. Configurar fechas si se especificaron
            if "fecha_inicio" in configuracion_examen:
                nuevo_examen.fecha_inicio = configuracion_examen["fecha_inicio"]
            if "fecha_limite" in configuracion_examen:
                nuevo_examen.fecha_limite = configuracion_examen["fecha_limite"]

            db.commit()

            # 6. Generar reporte de creación
            reporte_creacion = {
                "examen_id": nuevo_examen.examen_id,
                "titulo": titulo,
                "total_preguntas": len(preguntas_seleccionadas),
                "puntuacion_total": puntuacion_total,
                "preguntas_por_tipo": self._contar_preguntas_por_tipo(
                    preguntas_seleccionadas
                ),
                "preguntas_por_dificultad": self._contar_preguntas_por_dificultad(
                    preguntas_seleccionadas
                ),
                "tiempo_estimado_total": sum(
                    p.tiempo_estimado or 0 for p in preguntas_seleccionadas
                ),
                "criterios_utilizados": criterios_seleccion,
            }

            return {
                "success": True,
                "examen": nuevo_examen,
                "reporte_creacion": reporte_creacion,
            }

        except Exception as e:
            db.rollback()
            return {"error": f"Error creando examen: {e!s}"}

    def clonar_examen(
        self,
        db: Session,
        examen_id: int,
        nuevo_titulo: str,
        creado_por: int,
        modificaciones: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Clonar un examen existente con posibles modificaciones."""
        try:
            # Obtener examen original
            examen_original = (
                db.query(Examen).filter(Examen.examen_id == examen_id).first()
            )

            if not examen_original:
                return {"error": "Examen original no encontrado"}

            # Obtener preguntas originales
            preguntas_originales = (
                db.query(PreguntaExamen)
                .filter(PreguntaExamen.examen_id == examen_id)
                .order_by(PreguntaExamen.orden)
                .all()
            )

            # Crear nuevo examen (clon)
            examen_clonado = Examen(
                titulo=nuevo_titulo,
                descripcion=f"Copia de: {examen_original.descripcion}",
                clase_id=examen_original.clase_id,
                creado_por=creado_por,
                tipo_examen=examen_original.tipo_examen,
                tiempo_limite=examen_original.tiempo_limite,
                intentos_permitidos=examen_original.intentos_permitidos,
                mostrar_resultados_inmediatos=examen_original.mostrar_resultados_inmediatos,
                barajar_preguntas=examen_original.barajar_preguntas,
                puntuacion_total=examen_original.puntuacion_total,
                configuracion_anti_trampa=examen_original.configuracion_anti_trampa,
                fecha_creacion=datetime.utcnow(),
                estado_examen=EstadoExamen.BORRADOR,
            )

            # Aplicar modificaciones si se especificaron
            if modificaciones:
                for campo, valor in modificaciones.items():
                    if hasattr(examen_clonado, campo):
                        setattr(examen_clonado, campo, valor)

            db.add(examen_clonado)
            db.flush()

            # Clonar preguntas
            for pregunta_original in preguntas_originales:
                pregunta_clonada = PreguntaExamen(
                    examen_id=examen_clonado.examen_id,
                    texto_pregunta=pregunta_original.texto_pregunta,
                    tipo_pregunta=pregunta_original.tipo_pregunta,
                    opciones=pregunta_original.opciones,
                    respuesta_correcta=pregunta_original.respuesta_correcta,
                    explicacion=pregunta_original.explicacion,
                    puntuacion=pregunta_original.puntuacion,
                    dificultad=pregunta_original.dificultad,
                    orden=pregunta_original.orden,
                    tiempo_estimado=pregunta_original.tiempo_estimado,
                    puntos_respuesta_parcial=pregunta_original.puntos_respuesta_parcial,
                    configuracion_avanzada={
                        "clonada_de": pregunta_original.pregunta_id,
                        "fecha_clonacion": datetime.utcnow().isoformat(),
                    },
                )

                db.add(pregunta_clonada)

            db.commit()

            return {
                "success": True,
                "examen_original_id": examen_id,
                "examen_clonado_id": examen_clonado.examen_id,
                "titulo_nuevo": nuevo_titulo,
                "total_preguntas_clonadas": len(preguntas_originales),
            }

        except Exception as e:
            db.rollback()
            return {"error": f"Error clonando examen: {e!s}"}

    def generar_reporte_comparativo(
        self, db: Session, examenes_ids: list[int], incluir_detalles: bool = True
    ) -> dict[str, Any]:
        """Generar reporte comparativo entre múltiples exámenes."""
        examenes_data = []

        for examen_id in examenes_ids:
            # Obtener estadísticas de cada examen
            stats = self.estadisticas.generar_estadisticas_examen(
                db, examen_id, incluir_intentos_incompletos=False
            )

            if "error" not in stats:
                examenes_data.append(stats)

        if not examenes_data:
            return {"error": "No se pudieron obtener estadísticas de ningún examen"}

        # Generar comparación
        comparacion = {
            "examenes_comparados": len(examenes_data),
            "fecha_reporte": datetime.utcnow().isoformat(),
            "resumen_comparativo": {
                "promedio_mas_alto": max(
                    e["metricas_generales"]["promedio_calificaciones"]
                    for e in examenes_data
                ),
                "promedio_mas_bajo": min(
                    e["metricas_generales"]["promedio_calificaciones"]
                    for e in examenes_data
                ),
                "mejor_tasa_aprobacion": max(
                    e["metricas_generales"]["tasa_aprobacion"] for e in examenes_data
                ),
                "peor_tasa_aprobacion": min(
                    e["metricas_generales"]["tasa_aprobacion"] for e in examenes_data
                ),
                "mayor_participacion": max(
                    e["metadata"]["total_intentos_analizados"] for e in examenes_data
                ),
            },
            "rankings": {
                "por_promedio": sorted(
                    examenes_data,
                    key=lambda x: x["metricas_generales"]["promedio_calificaciones"],
                    reverse=True,
                ),
                "por_dificultad": sorted(
                    examenes_data,
                    key=lambda x: x["metricas_generales"]["promedio_calificaciones"],
                ),
                "por_participacion": sorted(
                    examenes_data,
                    key=lambda x: x["metadata"]["total_intentos_analizados"],
                    reverse=True,
                ),
            },
        }

        if incluir_detalles:
            comparacion["detalles_examenes"] = examenes_data

        return comparacion

    def ejecutar_mantenimiento_sistema(
        self, db: Session, operaciones: list[str] | None = None
    ) -> dict[str, Any]:
        """Ejecutar operaciones de mantenimiento del sistema."""
        if operaciones is None:
            operaciones = [
                "limpiar_intentos_abandonados",
                "actualizar_estadisticas_desactualizadas",
                "revisar_eventos_anti_trampa",
                "optimizar_banco_preguntas",
            ]

        resultados_mantenimiento = {
            "fecha_ejecucion": datetime.utcnow().isoformat(),
            "operaciones_ejecutadas": [],
            "errores": [],
            "estadisticas_limpieza": {},
        }

        try:
            for operacion in operaciones:
                if operacion == "limpiar_intentos_abandonados":
                    resultado = self._limpiar_intentos_abandonados(db)
                    resultados_mantenimiento["operaciones_ejecutadas"].append(resultado)

                elif operacion == "actualizar_estadisticas_desactualizadas":
                    resultado = self._actualizar_estadisticas_desactualizadas(db)
                    resultados_mantenimiento["operaciones_ejecutadas"].append(resultado)

                elif operacion == "revisar_eventos_anti_trampa":
                    resultado = self._revisar_eventos_anti_trampa(db)
                    resultados_mantenimiento["operaciones_ejecutadas"].append(resultado)

                elif operacion == "optimizar_banco_preguntas":
                    resultado = self._optimizar_banco_preguntas(db)
                    resultados_mantenimiento["operaciones_ejecutadas"].append(resultado)

            db.commit()

        except Exception as e:
            db.rollback()
            resultados_mantenimiento["errores"].append(f"Error en mantenimiento: {e!s}")

        return resultados_mantenimiento

    # Métodos auxiliares privados

    def _calificar_intento_completo(
        self,
        db: Session,
        intento: IntentoExamen,
        preguntas: list[PreguntaExamen],
        respuestas_datos: list[dict[str, Any]],
    ) -> dict[str, Any]:
        """Calificar todas las respuestas de un intento."""
        resultados_calificacion = {
            "puntuacion_total": 0,
            "puntuacion_maxima": sum(p.puntuacion for p in preguntas),
            "preguntas_calificadas": [],
            "resumen": {"correctas": 0, "incorrectas": 0, "parciales": 0},
        }

        # Crear o actualizar respuestas en la base de datos
        for _i, (pregunta, respuesta_data) in enumerate(
            zip(preguntas, respuestas_datos, strict=False)
        ):
            # Buscar respuesta existente o crear nueva
            respuesta_existente = (
                db.query(RespuestaEstudiante)
                .filter(
                    and_(
                        RespuestaEstudiante.intento_id == intento.intento_id,
                        RespuestaEstudiante.pregunta_id == pregunta.pregunta_id,
                    )
                )
                .first()
            )

            if respuesta_existente:
                respuesta = respuesta_existente
                # Actualizar datos
                respuesta.respuesta_estudiante = respuesta_data.get(
                    "respuesta_estudiante"
                )
                respuesta.texto_respuesta = respuesta_data.get("texto_respuesta")
                respuesta.tiempo_respuesta = respuesta_data.get("tiempo_respuesta")
            else:
                respuesta = RespuestaEstudiante(
                    intento_id=intento.intento_id,
                    pregunta_id=pregunta.pregunta_id,
                    respuesta_texto=respuesta_data.get("respuesta_estudiante"),
                    texto_respuesta=respuesta_data.get("texto_respuesta"),
                    tiempo_respuesta=respuesta_data.get("tiempo_respuesta"),
                    fecha_respuesta=datetime.utcnow(),
                )
                db.add(respuesta)

            # Calificar la respuesta
            resultado_calificacion = self.calificador.calificar_respuesta(
                pregunta, respuesta, algoritmo="combined_analysis"
            )

            # Actualizar respuesta con los resultados
            respuesta.es_correcta = resultado_calificacion["es_correcta"]
            respuesta.puntuacion_obtenida = resultado_calificacion[
                "puntuacion_obtenida"
            ]
            respuesta.feedback_automatico = resultado_calificacion[
                "feedback_automatico"
            ]
            respuesta.detalles_calificacion = resultado_calificacion[
                "detalles_calificacion"
            ]

            # Acumular puntuación
            resultados_calificacion["puntuacion_total"] += resultado_calificacion[
                "puntuacion_obtenida"
            ]

            # Clasificar resultado
            if resultado_calificacion["es_correcta"]:
                resultados_calificacion["resumen"]["correctas"] += 1
            elif resultado_calificacion["puntuacion_obtenida"] > 0:
                resultados_calificacion["resumen"]["parciales"] += 1
            else:
                resultados_calificacion["resumen"]["incorrectas"] += 1

            # Añadir al detalle
            resultados_calificacion["preguntas_calificadas"].append(
                {
                    "pregunta_id": pregunta.pregunta_id,
                    "orden": pregunta.orden,
                    "puntuacion_obtenida": resultado_calificacion[
                        "puntuacion_obtenida"
                    ],
                    "puntuacion_maxima": pregunta.puntuacion,
                    "es_correcta": resultado_calificacion["es_correcta"],
                    "confianza_calificacion": resultado_calificacion[
                        "confianza_calificacion"
                    ],
                }
            )

        # Calcular porcentaje final
        if resultados_calificacion["puntuacion_maxima"] > 0:
            resultados_calificacion["porcentaje"] = round(
                (
                    resultados_calificacion["puntuacion_total"]
                    / resultados_calificacion["puntuacion_maxima"]
                )
                * 100,
                2,
            )
        else:
            resultados_calificacion["porcentaje"] = 0

        return resultados_calificacion

    def _finalizar_intento(
        self,
        db: Session,
        intento: IntentoExamen,
        resultado_calificacion: dict[str, Any],
        reporte_integridad: dict[str, Any],
    ) -> None:
        """Finalizar un intento con todos los resultados."""
        intento.fecha_finalizacion = datetime.utcnow()
        intento.estado_intento = EstadoIntento.FINALIZADO
        intento.puntuacion_obtenida = resultado_calificacion["puntuacion_total"]

        # Actualizar datos adicionales con información de integridad
        intento.datos_adicionales = intento.datos_adicionales or {}
        intento.datos_adicionales.update(
            {
                "integridad_resultado": reporte_integridad.get("resultado_integridad"),
                "puntuacion_integridad": reporte_integridad.get(
                    "metricas_generales", {}
                ).get("puntuacion_integridad"),
                "eventos_criticos": reporte_integridad.get(
                    "metricas_generales", {}
                ).get("eventos_criticos"),
                "calificacion_automatica": {
                    "porcentaje": resultado_calificacion["porcentaje"],
                    "preguntas_correctas": resultado_calificacion["resumen"][
                        "correctas"
                    ],
                    "preguntas_parciales": resultado_calificacion["resumen"][
                        "parciales"
                    ],
                },
            }
        )

        db.commit()

    def _generar_alertas_recomendaciones(
        self,
        resultado_calificacion: dict[str, Any],
        reporte_integridad: dict[str, Any],
        estadisticas_examen: dict[str, Any],
    ) -> dict[str, Any]:
        """Generar alertas y recomendaciones basadas en los resultados."""
        alertas = []
        recomendaciones = []

        # Alertas de integridad
        integridad = reporte_integridad.get("resultado_integridad", "ALTA")
        if integridad in ["BAJA", "MUY_BAJA"]:
            alertas.append(
                {
                    "tipo": "integridad_baja",
                    "prioridad": "alta",
                    "mensaje": f"Integridad del intento: {integridad}",
                    "accion_requerida": reporte_integridad.get("recomendacion_accion"),
                }
            )

        # Alertas de rendimiento
        porcentaje = resultado_calificacion.get("porcentaje", 0)
        if porcentaje < 40:
            alertas.append(
                {
                    "tipo": "rendimiento_bajo",
                    "prioridad": "media",
                    "mensaje": f"Calificación muy baja: {porcentaje}%",
                    "accion_requerida": "Considerar apoyo adicional al estudiante",
                }
            )

        # Recomendaciones basadas en estadísticas del examen
        if "metricas_generales" in estadisticas_examen:
            promedio_examen = estadisticas_examen["metricas_generales"].get(
                "promedio_calificaciones", 0
            )
            if porcentaje < promedio_examen - 20:  # 20 puntos por debajo del promedio
                recomendaciones.append(
                    "Estudiante significativamente por debajo del promedio de la clase"
                )

        # Recomendaciones de calificación
        preguntas_baja_confianza = [
            p
            for p in resultado_calificacion["preguntas_calificadas"]
            if p.get("confianza_calificacion", 1.0) < 0.7
        ]

        if preguntas_baja_confianza:
            recomendaciones.append(
                f"Revisar manualmente {len(preguntas_baja_confianza)} preguntas con baja confianza de calificación"
            )

        return {"alertas": alertas, "recomendaciones": recomendaciones}

    def _seleccionar_preguntas_banco(
        self, db: Session, criterios: dict[str, Any]
    ) -> list[BancoPregunta]:
        """Seleccionar preguntas del banco según criterios específicos."""
        query = db.query(BancoPregunta)

        # Filtros básicos
        if "temas" in criterios:
            # Asumiendo que hay una relación o campo de tema
            pass  # Implementar filtro por temas

        if "dificultades" in criterios:
            query = query.filter(
                BancoPregunta.dificultad.in_(criterios["dificultades"])
            )

        if "tipos_pregunta" in criterios:
            query = query.filter(
                BancoPregunta.tipo_pregunta.in_(criterios["tipos_pregunta"])
            )

        if "puntuacion_minima" in criterios:
            query = query.filter(
                BancoPregunta.puntuacion_sugerida >= criterios["puntuacion_minima"]
            )

        # Filtro por calidad (basado en estadísticas de uso)
        if criterios.get("solo_preguntas_probadas", False):
            query = query.filter(BancoPregunta.veces_utilizada > 0)

        # Obtener preguntas disponibles
        preguntas_disponibles = query.all()

        # Aplicar lógica de selección
        total_preguntas = criterios.get("total_preguntas", 10)

        if len(preguntas_disponibles) <= total_preguntas:
            return preguntas_disponibles

        # Selección balanceada por dificultad si se especifica
        if criterios.get("balancear_dificultad", False):
            return self._seleccionar_preguntas_balanceadas(
                preguntas_disponibles, total_preguntas
            )

        # Selección aleatoria simple
        import random

        return random.sample(preguntas_disponibles, total_preguntas)

    def _seleccionar_preguntas_balanceadas(
        self, preguntas: list[BancoPregunta], total: int
    ) -> list[BancoPregunta]:
        """Seleccionar preguntas manteniendo balance entre dificultades."""
        from collections import defaultdict
        import random

        # Agrupar por dificultad
        por_dificultad = defaultdict(list)
        for pregunta in preguntas:
            por_dificultad[pregunta.dificultad].append(pregunta)

        # Calcular cuántas preguntas tomar de cada dificultad
        dificultades = list(por_dificultad.keys())
        preguntas_por_dificultad = total // len(dificultades)
        restantes = total % len(dificultades)

        seleccionadas = []

        for i, dificultad in enumerate(dificultades):
            cantidad = preguntas_por_dificultad
            if i < restantes:
                cantidad += 1

            disponibles = por_dificultad[dificultad]
            cantidad = min(cantidad, len(disponibles))

            seleccionadas.extend(random.sample(disponibles, cantidad))

        return seleccionadas

    def _contar_preguntas_por_tipo(
        self, preguntas: list[BancoPregunta]
    ) -> dict[str, int]:
        """Contar preguntas agrupadas por tipo."""
        contador = {}
        for pregunta in preguntas:
            tipo = pregunta.tipo_pregunta.value
            contador[tipo] = contador.get(tipo, 0) + 1
        return contador

    def _contar_preguntas_por_dificultad(
        self, preguntas: list[BancoPregunta]
    ) -> dict[str, int]:
        """Contar preguntas agrupadas por dificultad."""
        contador = {}
        for pregunta in preguntas:
            dificultad = pregunta.dificultad.value
            contador[dificultad] = contador.get(dificultad, 0) + 1
        return contador

    def _requiere_notificacion(self, resultado_procesamiento: dict[str, Any]) -> bool:
        """Determinar si el resultado requiere notificación."""
        # Notificar si hay alertas de alta prioridad
        alertas_altas = [
            a
            for a in resultado_procesamiento.get("alertas", [])
            if a.get("prioridad") == "alta"
        ]

        return len(alertas_altas) > 0

    def _programar_notificacion(self, db: Session, resultado: dict[str, Any]) -> None:
        """Programar notificación (placeholder para implementación futura)."""
        # TODO: Implementar sistema de notificaciones

    def _limpiar_intentos_abandonados(self, db: Session) -> dict[str, Any]:
        """Limpiar intentos abandonados hace más de 24 horas."""
        limite_abandono = datetime.utcnow() - timedelta(hours=24)

        intentos_abandonados = (
            db.query(IntentoExamen)
            .filter(
                and_(
                    IntentoExamen.estado_intento == EstadoIntento.EN_PROGRESO,
                    IntentoExamen.fecha_inicio < limite_abandono,
                    IntentoExamen.fecha_finalizacion.is_(None),
                )
            )
            .all()
        )

        count_limpiados = 0
        for intento in intentos_abandonados:
            intento.estado_intento = EstadoIntento.ABANDONADO
            intento.fecha_finalizacion = datetime.utcnow()
            count_limpiados += 1

        return {
            "operacion": "limpiar_intentos_abandonados",
            "intentos_limpiados": count_limpiados,
            "limite_tiempo": limite_abandono.isoformat(),
        }

    def _actualizar_estadisticas_desactualizadas(self, db: Session) -> dict[str, Any]:
        """Actualizar estadísticas de exámenes que están desactualizadas."""
        # Buscar exámenes con estadísticas antiguas o sin estadísticas
        examenes_actualizar = (
            db.query(Examen)
            .filter(Examen.estado_examen == EstadoExamen.ACTIVO)
            .limit(50)
            .all()
        )  # Limitar para no sobrecargar

        count_actualizados = 0
        for examen in examenes_actualizar:
            try:
                self.estadisticas.generar_estadisticas_examen(
                    db, examen.examen_id, incluir_intentos_incompletos=False
                )
                count_actualizados += 1
            except Exception:
                continue

        return {
            "operacion": "actualizar_estadisticas_desactualizadas",
            "examenes_actualizados": count_actualizados,
        }

    def _revisar_eventos_anti_trampa(self, db: Session) -> dict[str, Any]:
        """Revisar y limpiar eventos anti-trampa antiguos."""
        limite_antiguedad = datetime.utcnow() - timedelta(days=90)

        eventos_antiguos = (
            db.query(EventoAntiTrampa)
            .filter(EventoAntiTrampa.timestamp < limite_antiguedad)
            .count()
        )

        # Por ahora solo contamos, en una implementación real podríamos archivar
        return {
            "operacion": "revisar_eventos_anti_trampa",
            "eventos_antiguos_detectados": eventos_antiguos,
            "accion": "conteo_solamente",
        }

    def _optimizar_banco_preguntas(self, db: Session) -> dict[str, Any]:
        """Optimizar y limpiar el banco de preguntas."""
        # Identificar preguntas duplicadas o con problemas
        total_preguntas = db.query(BancoPregunta).count()
        preguntas_sin_usar = (
            db.query(BancoPregunta).filter(BancoPregunta.veces_utilizada == 0).count()
        )

        return {
            "operacion": "optimizar_banco_preguntas",
            "total_preguntas": total_preguntas,
            "preguntas_sin_usar": preguntas_sin_usar,
            "recomendacion": "Revisar preguntas sin usar para posible eliminación",
        }


# Instancia global del servicio
servicio_integracion = ServicioIntegracionExamenes()
