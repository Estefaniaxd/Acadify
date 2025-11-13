"""Servicio de calificación automática para el sistema de evaluaciones
Incluye algoritmos para diferentes tipos de preguntas y análisis de texto.
"""

from datetime import datetime
from difflib import SequenceMatcher
import re
from typing import Any

from src.models.evaluaciones import (
    PreguntaExamen,
    RespuestaEstudiante,
    TipoPregunta as TipoPreguntaExpandido,  # Alias para compatibilidad
)


class CalificadorAutomatico:
    """Servicio para calificación automática de respuestas."""

    def __init__(self) -> None:
        self.algoritmos_ensayo = {
            "keyword_matching": self._calificar_ensayo_keywords,
            "similarity_analysis": self._calificar_ensayo_similitud,
            "combined_analysis": self._calificar_ensayo_combinado,
        }

    def calificar_respuesta(
        self,
        pregunta: PreguntaExamen,
        respuesta: RespuestaEstudiante,
        algoritmo: str = "combined_analysis",
    ) -> dict[str, Any]:
        """Calificar una respuesta automáticamente según el tipo de pregunta.

        Returns:
            Dict con puntuación, si es correcta, feedback y detalles del análisis
        """
        resultado = {
            "puntuacion_obtenida": 0.0,
            "es_correcta": False,
            "feedback_automatico": "",
            "detalles_calificacion": {},
            "confianza_calificacion": 0.0,  # 0-1, qué tan confiable es la calificación
        }

        if pregunta.tipo_pregunta == TipoPreguntaExpandido.OPCION_MULTIPLE:
            resultado = self._calificar_opcion_multiple(pregunta, respuesta)

        elif pregunta.tipo_pregunta == TipoPreguntaExpandido.VERDADERO_FALSO:
            resultado = self._calificar_verdadero_falso(pregunta, respuesta)

        elif pregunta.tipo_pregunta == TipoPreguntaExpandido.COMPLETAR:
            resultado = self._calificar_completar(pregunta, respuesta)

        elif pregunta.tipo_pregunta == TipoPreguntaExpandido.EMPAREJAMIENTO:
            resultado = self._calificar_emparejamiento(pregunta, respuesta)

        elif pregunta.tipo_pregunta == TipoPreguntaExpandido.ORDENAMIENTO:
            resultado = self._calificar_ordenamiento(pregunta, respuesta)

        elif pregunta.tipo_pregunta in [
            TipoPreguntaExpandido.ENSAYO,
            TipoPreguntaExpandido.RESPUESTA_CORTA,
        ]:
            if algoritmo in self.algoritmos_ensayo:
                resultado = self.algoritmos_ensayo[algoritmo](pregunta, respuesta)
            else:
                resultado = self._calificar_ensayo_combinado(pregunta, respuesta)

        # Aplicar restricciones de puntuación
        resultado["puntuacion_obtenida"] = max(
            0, min(resultado["puntuacion_obtenida"], pregunta.puntuacion)
        )

        return resultado

    def _calificar_opcion_multiple(
        self, pregunta: PreguntaExamen, respuesta: RespuestaEstudiante
    ) -> dict[str, Any]:
        """Calificar pregunta de opción múltiple."""
        resultado = {
            "puntuacion_obtenida": 0.0,
            "es_correcta": False,
            "feedback_automatico": "",
            "detalles_calificacion": {},
            "confianza_calificacion": 1.0,  # Máxima confianza en preguntas objetivas
        }

        if not pregunta.respuesta_correcta or not respuesta.respuesta_estudiante:
            resultado["feedback_automatico"] = "Respuesta no proporcionada"
            return resultado

        respuesta_correcta = pregunta.respuesta_correcta
        respuesta_estudiante = respuesta.respuesta_estudiante

        # Verificar si es opción múltiple con varias respuestas correctas
        if isinstance(respuesta_correcta.get("respuestas_correctas"), list):
            resultado = self._calificar_multiple_correctas(
                pregunta, respuesta_correcta, respuesta_estudiante
            )
        else:
            # Una sola respuesta correcta
            opcion_correcta = respuesta_correcta.get("opcion_correcta")
            opcion_seleccionada = respuesta_estudiante.get("opcion_seleccionada")

            if opcion_correcta == opcion_seleccionada:
                resultado["puntuacion_obtenida"] = pregunta.puntuacion
                resultado["es_correcta"] = True
                resultado["feedback_automatico"] = "¡Correcto!"
            else:
                resultado["feedback_automatico"] = (
                    f"Incorrecto. La respuesta correcta era: {opcion_correcta}"
                )

            resultado["detalles_calificacion"] = {
                "opcion_correcta": opcion_correcta,
                "opcion_seleccionada": opcion_seleccionada,
            }

        # Añadir explicación si existe
        if pregunta.explicacion:
            resultado["feedback_automatico"] += f" Explicación: {pregunta.explicacion}"

        return resultado

    def _calificar_multiple_correctas(
        self,
        pregunta: PreguntaExamen,
        respuesta_correcta: dict[str, Any],
        respuesta_estudiante: dict[str, Any],
    ) -> dict[str, Any]:
        """Calificar pregunta con múltiples respuestas correctas."""
        correctas = set(respuesta_correcta["respuestas_correctas"])
        seleccionadas = set(respuesta_estudiante.get("opciones_multiples", []))

        resultado = {
            "puntuacion_obtenida": 0.0,
            "es_correcta": False,
            "feedback_automatico": "",
            "detalles_calificacion": {
                "correctas_esperadas": list(correctas),
                "seleccionadas": list(seleccionadas),
                "correctas_acertadas": list(correctas.intersection(seleccionadas)),
                "incorrectas_seleccionadas": list(seleccionadas - correctas),
                "correctas_omitidas": list(correctas - seleccionadas),
            },
            "confianza_calificacion": 1.0,
        }

        if correctas == seleccionadas:
            # Respuesta perfecta
            resultado["puntuacion_obtenida"] = pregunta.puntuacion
            resultado["es_correcta"] = True
            resultado["feedback_automatico"] = (
                "¡Perfecto! Seleccionaste todas las opciones correctas."
            )

        elif pregunta.puntos_respuesta_parcial:
            # Puntuación parcial
            interseccion = correctas.intersection(seleccionadas)
            puntos_por_correcta = pregunta.puntuacion / len(correctas)
            puntos_por_incorrecta = puntos_por_correcta * 0.3  # Penalización reducida

            puntos_ganados = len(interseccion) * puntos_por_correcta
            puntos_perdidos = len(seleccionadas - correctas) * puntos_por_incorrecta

            resultado["puntuacion_obtenida"] = max(0, puntos_ganados - puntos_perdidos)
            resultado["es_correcta"] = len(interseccion) == len(correctas) and len(
                seleccionadas
            ) == len(correctas)

            # Feedback detallado
            feedback_parts = []
            if interseccion:
                feedback_parts.append(
                    f"Acertaste {len(interseccion)} de {len(correctas)} opciones correctas."
                )
            if seleccionadas - correctas:
                feedback_parts.append(
                    f"Seleccionaste {len(seleccionadas - correctas)} opciones incorrectas."
                )
            if correctas - seleccionadas:
                feedback_parts.append(
                    f"Te faltaron {len(correctas - seleccionadas)} opciones correctas."
                )

            resultado["feedback_automatico"] = " ".join(feedback_parts)

        else:
            resultado["feedback_automatico"] = (
                "Incorrecto. Debes seleccionar todas las opciones correctas."
            )

        return resultado

    def _calificar_verdadero_falso(
        self, pregunta: PreguntaExamen, respuesta: RespuestaEstudiante
    ) -> dict[str, Any]:
        """Calificar pregunta de verdadero/falso."""
        resultado = {
            "puntuacion_obtenida": 0.0,
            "es_correcta": False,
            "feedback_automatico": "",
            "detalles_calificacion": {},
            "confianza_calificacion": 1.0,
        }

        if not pregunta.respuesta_correcta or not respuesta.respuesta_estudiante:
            resultado["feedback_automatico"] = "Respuesta no proporcionada"
            return resultado

        respuesta_correcta = pregunta.respuesta_correcta.get("respuesta")
        respuesta_estudiante = respuesta.respuesta_estudiante.get("respuesta")

        resultado["detalles_calificacion"] = {
            "respuesta_correcta": respuesta_correcta,
            "respuesta_estudiante": respuesta_estudiante,
        }

        if respuesta_correcta == respuesta_estudiante:
            resultado["puntuacion_obtenida"] = pregunta.puntuacion
            resultado["es_correcta"] = True
            resultado["feedback_automatico"] = "¡Correcto!"
        else:
            resultado["feedback_automatico"] = (
                f"Incorrecto. La respuesta correcta era: {'Verdadero' if respuesta_correcta else 'Falso'}"
            )

        # Añadir explicación si existe
        if pregunta.explicacion:
            resultado["feedback_automatico"] += f" Explicación: {pregunta.explicacion}"

        return resultado

    def _calificar_completar(
        self, pregunta: PreguntaExamen, respuesta: RespuestaEstudiante
    ) -> dict[str, Any]:
        """Calificar pregunta de completar espacios."""
        resultado = {
            "puntuacion_obtenida": 0.0,
            "es_correcta": False,
            "feedback_automatico": "",
            "detalles_calificacion": {},
            "confianza_calificacion": 0.9,  # Alta confianza pero puede haber variaciones en texto
        }

        if not pregunta.respuesta_correcta or not respuesta.respuesta_estudiante:
            resultado["feedback_automatico"] = "Respuestas no proporcionadas"
            return resultado

        respuestas_correctas = pregunta.respuesta_correcta.get("respuestas", {})
        respuestas_estudiante = respuesta.respuesta_estudiante.get("respuestas", {})

        total_huecos = len(respuestas_correctas)
        huecos_correctos = 0
        detalles_huecos = {}

        for hueco, respuesta_correcta in respuestas_correctas.items():
            respuesta_est = respuestas_estudiante.get(hueco, "").strip()

            # Permitir múltiples respuestas correctas separadas por |
            opciones_correctas = [
                opt.strip() for opt in str(respuesta_correcta).split("|")
            ]

            # Comparación flexible (ignorar mayúsculas/minúsculas y espacios extra)
            respuesta_est_norm = respuesta_est.lower().strip()
            opciones_norm = [opt.lower().strip() for opt in opciones_correctas]

            es_correcto = respuesta_est_norm in opciones_norm
            if es_correcto:
                huecos_correctos += 1

            detalles_huecos[hueco] = {
                "respuesta_estudiante": respuesta_est,
                "respuestas_correctas": opciones_correctas,
                "es_correcto": es_correcto,
                "similitud": (
                    max(
                        [
                            SequenceMatcher(None, respuesta_est_norm, opcion).ratio()
                            for opcion in opciones_norm
                        ]
                    )
                    if opciones_norm
                    else 0
                ),
            }

        resultado["detalles_calificacion"] = {
            "total_huecos": total_huecos,
            "huecos_correctos": huecos_correctos,
            "detalles_por_hueco": detalles_huecos,
        }

        # Calcular puntuación
        if pregunta.puntos_respuesta_parcial and total_huecos > 0:
            proporcion = huecos_correctos / total_huecos
            resultado["puntuacion_obtenida"] = pregunta.puntuacion * proporcion
            resultado["es_correcta"] = huecos_correctos == total_huecos
            resultado["feedback_automatico"] = (
                f"Completaste correctamente {huecos_correctos} de {total_huecos} espacios."
            )
        elif huecos_correctos == total_huecos:
            resultado["puntuacion_obtenida"] = pregunta.puntuacion
            resultado["es_correcta"] = True
            resultado["feedback_automatico"] = (
                "¡Perfecto! Completaste todos los espacios correctamente."
            )
        else:
            resultado["feedback_automatico"] = (
                f"Incorrecto. Completaste {huecos_correctos} de {total_huecos} espacios correctamente."
            )

        return resultado

    def _calificar_emparejamiento(
        self, pregunta: PreguntaExamen, respuesta: RespuestaEstudiante
    ) -> dict[str, Any]:
        """Calificar pregunta de emparejamiento."""
        resultado = {
            "puntuacion_obtenida": 0.0,
            "es_correcta": False,
            "feedback_automatico": "",
            "detalles_calificacion": {},
            "confianza_calificacion": 1.0,
        }

        if not pregunta.respuesta_correcta or not respuesta.respuesta_estudiante:
            resultado["feedback_automatico"] = "Emparejamientos no proporcionados"
            return resultado

        emparejamientos_correctos = pregunta.respuesta_correcta.get(
            "emparejamientos", {}
        )
        emparejamientos_estudiante = respuesta.respuesta_estudiante.get(
            "emparejamientos", {}
        )

        total_emparejamientos = len(emparejamientos_correctos)
        emparejamientos_correctos_count = 0
        detalles_emparejamientos = {}

        for item, match_correcto in emparejamientos_correctos.items():
            match_estudiante = emparejamientos_estudiante.get(item)
            es_correcto = match_correcto == match_estudiante

            if es_correcto:
                emparejamientos_correctos_count += 1

            detalles_emparejamientos[item] = {
                "match_correcto": match_correcto,
                "match_estudiante": match_estudiante,
                "es_correcto": es_correcto,
            }

        resultado["detalles_calificacion"] = {
            "total_emparejamientos": total_emparejamientos,
            "emparejamientos_correctos": emparejamientos_correctos_count,
            "detalles_por_item": detalles_emparejamientos,
        }

        # Calcular puntuación
        if pregunta.puntos_respuesta_parcial and total_emparejamientos > 0:
            proporcion = emparejamientos_correctos_count / total_emparejamientos
            resultado["puntuacion_obtenida"] = pregunta.puntuacion * proporcion
            resultado["es_correcta"] = (
                emparejamientos_correctos_count == total_emparejamientos
            )
            resultado["feedback_automatico"] = (
                f"Emparejaste correctamente {emparejamientos_correctos_count} de {total_emparejamientos} elementos."
            )
        elif emparejamientos_correctos_count == total_emparejamientos:
            resultado["puntuacion_obtenida"] = pregunta.puntuacion
            resultado["es_correcta"] = True
            resultado["feedback_automatico"] = (
                "¡Perfecto! Todos los emparejamientos son correctos."
            )
        else:
            resultado["feedback_automatico"] = (
                f"Incorrecto. {emparejamientos_correctos_count} de {total_emparejamientos} emparejamientos son correctos."
            )

        return resultado

    def _calificar_ordenamiento(
        self, pregunta: PreguntaExamen, respuesta: RespuestaEstudiante
    ) -> dict[str, Any]:
        """Calificar pregunta de ordenamiento."""
        resultado = {
            "puntuacion_obtenida": 0.0,
            "es_correcta": False,
            "feedback_automatico": "",
            "detalles_calificacion": {},
            "confianza_calificacion": 1.0,
        }

        if not pregunta.respuesta_correcta or not respuesta.respuesta_estudiante:
            resultado["feedback_automatico"] = "Orden no proporcionado"
            return resultado

        orden_correcto = pregunta.respuesta_correcta.get("orden", [])
        orden_estudiante = respuesta.respuesta_estudiante.get("orden", [])

        resultado["detalles_calificacion"] = {
            "orden_correcto": orden_correcto,
            "orden_estudiante": orden_estudiante,
            "posiciones_correctas": [],
        }

        if orden_correcto == orden_estudiante:
            resultado["puntuacion_obtenida"] = pregunta.puntuacion
            resultado["es_correcta"] = True
            resultado["feedback_automatico"] = (
                "¡Perfecto! El orden es completamente correcto."
            )

        elif pregunta.puntos_respuesta_parcial:
            # Calcular puntuación basada en posiciones correctas
            posiciones_correctas = 0
            total_items = len(orden_correcto)
            posiciones_correctas_lista = []

            for i, item in enumerate(orden_correcto):
                if i < len(orden_estudiante) and orden_estudiante[i] == item:
                    posiciones_correctas += 1
                    posiciones_correctas_lista.append(i + 1)

            resultado["detalles_calificacion"][
                "posiciones_correctas"
            ] = posiciones_correctas_lista

            if total_items > 0:
                proporcion = posiciones_correctas / total_items
                resultado["puntuacion_obtenida"] = pregunta.puntuacion * proporcion
                resultado["es_correcta"] = posiciones_correctas == total_items
                resultado["feedback_automatico"] = (
                    f"Ordenaste correctamente {posiciones_correctas} de {total_items} elementos en sus posiciones correctas."
                )

        else:
            resultado["feedback_automatico"] = (
                "Incorrecto. El orden no es completamente correcto."
            )

        return resultado

    def _calificar_ensayo_keywords(
        self, pregunta: PreguntaExamen, respuesta: RespuestaEstudiante
    ) -> dict[str, Any]:
        """Calificar ensayo basado en palabras clave."""
        resultado = {
            "puntuacion_obtenida": 0.0,
            "es_correcta": False,
            "feedback_automatico": "",
            "detalles_calificacion": {},
            "confianza_calificacion": 0.6,  # Confianza moderada para ensayos
        }

        if not respuesta.texto_respuesta:
            resultado["feedback_automatico"] = "No se proporcionó respuesta de texto"
            return resultado

        # Extraer palabras clave de la respuesta correcta o configuración
        palabras_clave = self._extraer_palabras_clave(pregunta)
        if not palabras_clave:
            resultado["confianza_calificacion"] = 0.3
            resultado["feedback_automatico"] = (
                "No hay criterios de evaluación específicos configurados"
            )
            return resultado

        texto = respuesta.texto_respuesta.lower()
        palabras_encontradas = []
        palabras_pesos = {}

        # Buscar palabras clave con diferentes pesos
        for palabra_info in palabras_clave:
            if isinstance(palabra_info, dict):
                palabra = palabra_info.get("palabra", "").lower()
                peso = palabra_info.get("peso", 1.0)
            else:
                palabra = str(palabra_info).lower()
                peso = 1.0

            if palabra in texto:
                palabras_encontradas.append(palabra)
                palabras_pesos[palabra] = peso

        # Calcular puntuación basada en palabras encontradas
        total_peso = sum(
            info.get("peso", 1.0) if isinstance(info, dict) else 1.0
            for info in palabras_clave
        )
        peso_encontrado = sum(palabras_pesos.values())

        proporcion_palabras = peso_encontrado / total_peso if total_peso > 0 else 0

        # Factor adicional: longitud del texto
        longitud_minima = (
            pregunta.configuracion_avanzada.get("longitud_minima", 50)
            if pregunta.configuracion_avanzada
            else 50
        )
        longitud_texto = len(respuesta.texto_respuesta)
        factor_longitud = (
            min(longitud_texto / longitud_minima, 1.0) if longitud_minima > 0 else 1.0
        )

        # Puntuación final combinada
        peso_palabras = 0.7
        peso_longitud = 0.3

        puntuacion_final = pregunta.puntuacion * (
            (proporcion_palabras * peso_palabras) + (factor_longitud * peso_longitud)
        )

        resultado["puntuacion_obtenida"] = round(puntuacion_final, 2)
        resultado["es_correcta"] = resultado["puntuacion_obtenida"] >= (
            pregunta.puntuacion * 0.6
        )

        resultado["detalles_calificacion"] = {
            "palabras_clave_esperadas": [
                info.get("palabra") if isinstance(info, dict) else str(info)
                for info in palabras_clave
            ],
            "palabras_encontradas": palabras_encontradas,
            "proporcion_palabras": round(proporcion_palabras, 2),
            "factor_longitud": round(factor_longitud, 2),
            "longitud_texto": longitud_texto,
            "longitud_minima": longitud_minima,
        }

        resultado["feedback_automatico"] = (
            f"Se encontraron {len(palabras_encontradas)} de {len(palabras_clave)} conceptos clave esperados. "
            f"Longitud del texto: {longitud_texto} caracteres."
        )

        return resultado

    def _calificar_ensayo_similitud(
        self, pregunta: PreguntaExamen, respuesta: RespuestaEstudiante
    ) -> dict[str, Any]:
        """Calificar ensayo basado en similitud con respuesta modelo."""
        resultado = {
            "puntuacion_obtenida": 0.0,
            "es_correcta": False,
            "feedback_automatico": "",
            "detalles_calificacion": {},
            "confianza_calificacion": 0.5,  # Confianza moderada-baja para similitud de texto
        }

        if not respuesta.texto_respuesta:
            resultado["feedback_automatico"] = "No se proporcionó respuesta de texto"
            return resultado

        # Obtener respuesta modelo
        respuesta_modelo = None
        if pregunta.respuesta_correcta and isinstance(
            pregunta.respuesta_correcta, dict
        ):
            respuesta_modelo = pregunta.respuesta_correcta.get("respuesta_modelo")

        if not respuesta_modelo:
            resultado["confianza_calificacion"] = 0.2
            resultado["feedback_automatico"] = "No hay respuesta modelo para comparar"
            return resultado

        # Calcular similitud
        similitud = SequenceMatcher(
            None,
            respuesta.texto_respuesta.lower().strip(),
            respuesta_modelo.lower().strip(),
        ).ratio()

        # Ajustar puntuación basada en similitud
        pregunta.puntuacion * similitud

        # Aplicar curva de puntuación
        if similitud >= 0.8:
            puntuacion_final = pregunta.puntuacion
        elif similitud >= 0.6:
            puntuacion_final = pregunta.puntuacion * 0.8
        elif similitud >= 0.4:
            puntuacion_final = pregunta.puntuacion * 0.6
        elif similitud >= 0.2:
            puntuacion_final = pregunta.puntuacion * 0.4
        else:
            puntuacion_final = pregunta.puntuacion * 0.2

        resultado["puntuacion_obtenida"] = round(puntuacion_final, 2)
        resultado["es_correcta"] = similitud >= 0.6

        resultado["detalles_calificacion"] = {
            "similitud_texto": round(similitud, 3),
            "respuesta_modelo_longitud": len(respuesta_modelo),
            "respuesta_estudiante_longitud": len(respuesta.texto_respuesta),
        }

        resultado["feedback_automatico"] = (
            f"Similitud con respuesta modelo: {round(similitud * 100, 1)}%. "
            "Nota: Esta es una evaluación automática preliminar."
        )

        return resultado

    def _calificar_ensayo_combinado(
        self, pregunta: PreguntaExamen, respuesta: RespuestaEstudiante
    ) -> dict[str, Any]:
        """Calificar ensayo usando análisis combinado."""
        resultado_keywords = self._calificar_ensayo_keywords(pregunta, respuesta)
        resultado_similitud = self._calificar_ensayo_similitud(pregunta, respuesta)

        # Combinar resultados con pesos
        peso_keywords = 0.6
        peso_similitud = 0.4

        puntuacion_combinada = (
            resultado_keywords["puntuacion_obtenida"] * peso_keywords
            + resultado_similitud["puntuacion_obtenida"] * peso_similitud
        )

        confianza_combinada = (
            resultado_keywords["confianza_calificacion"] * peso_keywords
            + resultado_similitud["confianza_calificacion"] * peso_similitud
        )

        resultado = {
            "puntuacion_obtenida": round(puntuacion_combinada, 2),
            "es_correcta": puntuacion_combinada >= (pregunta.puntuacion * 0.6),
            "feedback_automatico": "",
            "detalles_calificacion": {
                "analisis_keywords": resultado_keywords["detalles_calificacion"],
                "analisis_similitud": resultado_similitud["detalles_calificacion"],
                "peso_keywords": peso_keywords,
                "peso_similitud": peso_similitud,
            },
            "confianza_calificacion": round(confianza_combinada, 2),
        }

        # Generar feedback combinado
        feedback_parts = [
            "Evaluación automática combinada:",
            f"• Conceptos clave: {len(resultado_keywords['detalles_calificacion'].get('palabras_encontradas', []))} encontrados",
        ]

        if "similitud_texto" in resultado_similitud["detalles_calificacion"]:
            similitud = resultado_similitud["detalles_calificacion"]["similitud_texto"]
            feedback_parts.append(
                f"• Similitud con modelo: {round(similitud * 100, 1)}%"
            )

        feedback_parts.append(
            "IMPORTANTE: Esta es una calificación automática preliminar que requiere revisión manual."
        )

        resultado["feedback_automatico"] = " ".join(feedback_parts)

        return resultado

    def _extraer_palabras_clave(self, pregunta: PreguntaExamen) -> list[Any]:
        """Extraer palabras clave de la configuración de la pregunta."""
        palabras_clave = []

        # Buscar en respuesta_correcta
        if pregunta.respuesta_correcta and isinstance(
            pregunta.respuesta_correcta, dict
        ):
            if "palabras_clave" in pregunta.respuesta_correcta:
                palabras_clave = pregunta.respuesta_correcta["palabras_clave"]
            elif "conceptos_clave" in pregunta.respuesta_correcta:
                palabras_clave = pregunta.respuesta_correcta["conceptos_clave"]

        # Buscar en configuración avanzada
        if not palabras_clave and pregunta.configuracion_avanzada:
            if "palabras_clave" in pregunta.configuracion_avanzada:
                palabras_clave = pregunta.configuracion_avanzada["palabras_clave"]

        # Extraer de la explicación si no hay palabras clave específicas
        if not palabras_clave and pregunta.explicacion:
            # Extraer palabras importantes de la explicación
            palabras_importantes = self._extraer_palabras_importantes(
                pregunta.explicacion
            )
            palabras_clave = palabras_importantes[:10]  # Limitar a 10 palabras

        return palabras_clave or []

    def _extraer_palabras_importantes(self, texto: str) -> list[str]:
        """Extraer palabras importantes de un texto."""
        # Palabras a ignorar (stop words básicas en español)
        stop_words = {
            "el",
            "la",
            "de",
            "que",
            "y",
            "a",
            "en",
            "un",
            "es",
            "se",
            "no",
            "te",
            "lo",
            "le",
            "da",
            "su",
            "por",
            "son",
            "con",
            "para",
            "al",
            "del",
            "los",
            "las",
            "una",
            "sobre",
            "todo",
            "también",
            "después",
            "muy",
            "sin",
            "como",
            "entre",
            "durante",
            "tanto",
            "antes",
            "bajo",
            "hasta",
            "desde",
            "cuando",
            "donde",
            "este",
            "esta",
            "estos",
            "estas",
            "ese",
            "esa",
            "esos",
            "esas",
            "aquel",
            "aquella",
            "aquellos",
            "aquellas",
            "mi",
            "tu",
            "nuestro",
            "vuestro",
            "mio",
            "tuyo",
            "suyo",
            "nuestros",
            "vuestros",
        }

        # Limpiar y dividir el texto
        palabras = re.findall(r"\b[a-záéíóúüñ]{3,}\b", texto.lower())

        # Filtrar stop words y contar frecuencias
        frecuencias = {}
        for palabra in palabras:
            if palabra not in stop_words:
                frecuencias[palabra] = frecuencias.get(palabra, 0) + 1

        # Ordenar por frecuencia y devolver las más importantes
        return sorted(frecuencias.keys(), key=lambda k: frecuencias[k], reverse=True)

    def generar_reporte_calificacion(
        self,
        pregunta: PreguntaExamen,
        respuesta: RespuestaEstudiante,
        resultado_calificacion: dict[str, Any],
    ) -> dict[str, Any]:
        """Generar un reporte detallado de la calificación."""
        reporte = {
            "pregunta_id": pregunta.pregunta_id,
            "tipo_pregunta": pregunta.tipo_pregunta.value,
            "puntuacion_maxima": pregunta.puntuacion,
            "puntuacion_obtenida": resultado_calificacion["puntuacion_obtenida"],
            "porcentaje": round(
                (resultado_calificacion["puntuacion_obtenida"] / pregunta.puntuacion)
                * 100,
                2,
            ),
            "es_correcta": resultado_calificacion["es_correcta"],
            "confianza_calificacion": resultado_calificacion["confianza_calificacion"],
            "requiere_revision_manual": resultado_calificacion["confianza_calificacion"]
            < 0.8,
            "feedback_automatico": resultado_calificacion["feedback_automatico"],
            "detalles_analisis": resultado_calificacion["detalles_calificacion"],
            "timestamp": datetime.utcnow().isoformat(),
            "recomendaciones": [],
        }

        # Añadir recomendaciones basadas en el tipo y resultado
        if pregunta.tipo_pregunta in [
            TipoPreguntaExpandido.ENSAYO,
            TipoPreguntaExpandido.RESPUESTA_CORTA,
        ]:
            reporte["recomendaciones"].append(
                "Se recomienda revisión manual para preguntas de texto libre"
            )

            if resultado_calificacion["confianza_calificacion"] < 0.6:
                reporte["recomendaciones"].append(
                    "Baja confianza en calificación automática - revisión manual necesaria"
                )

        if not resultado_calificacion["es_correcta"] and pregunta.tipo_pregunta in [
            TipoPreguntaExpandido.OPCION_MULTIPLE,
            TipoPreguntaExpandido.VERDADERO_FALSO,
        ]:
            reporte["recomendaciones"].append(
                "Considerar proporcionar retroalimentación adicional al estudiante"
            )

        return reporte


# Instancia global del servicio
calificador_automatico = CalificadorAutomatico()
