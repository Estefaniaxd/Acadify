"""Servicio de IA para Evaluaciones usando Google Gemini 2.0 Flash.
Funcionalidades:
- Calificación automática inteligente con retroalimentación
- Detección de respuestas generadas por IA
- Detección de plagio y similitud
- Análisis de comportamiento del estudiante
- Generación de preguntas inteligentes
- Sugerencias de mejora personalizadas.
"""

from datetime import datetime
from difflib import SequenceMatcher
import json
import re
from typing import Any

import google.generativeai as genai

from src.core.config import settings


class IAEvaluacionService:
    """Servicio de IA para evaluaciones con Gemini 2.0 Flash."""

    def __init__(self) -> None:
        """Inicializa el servicio con Gemini."""
        genai.configure(api_key=settings.GEMINI_API_KEY)
        self.model = genai.GenerativeModel("gemini-2.0-flash-exp")

    # ==========================================
    # CALIFICACIÓN AUTOMÁTICA CON IA
    # ==========================================

    async def calificar_respuesta_ensayo(
        self,
        pregunta: str,
        respuesta_estudiante: str,
        respuesta_esperada: str | None = None,
        rubrica: dict[str, Any] | None = None,
        contexto: str | None = None,
    ) -> dict[str, Any]:
        """Califica una respuesta de ensayo usando IA.

        Args:
            pregunta: La pregunta del examen
            respuesta_estudiante: La respuesta del estudiante
            respuesta_esperada: Respuesta modelo (opcional)
            rubrica: Criterios de evaluación (opcional)
            contexto: Contexto adicional del curso (opcional)

        Returns:
            {
                "puntuacion": 0-100,
                "feedback": "...",
                "fortalezas": [...],
                "areas_mejora": [...],
                "criterios_evaluados": {...},
                "sugerencias": [...]
            }
        """
        prompt = self._construir_prompt_calificacion(
            pregunta=pregunta,
            respuesta_texto=respuesta_estudiante,
            respuesta_esperada=respuesta_esperada,
            rubrica=rubrica,
            contexto=contexto,
        )

        try:
            response = self.model.generate_content(prompt)
            resultado = self._parsear_respuesta_calificacion(response.text)

            return {
                "puntuacion": resultado.get("puntuacion", 0),
                "feedback": resultado.get("feedback", ""),
                "fortalezas": resultado.get("fortalezas", []),
                "areas_mejora": resultado.get("areas_mejora", []),
                "criterios_evaluados": resultado.get("criterios", {}),
                "sugerencias": resultado.get("sugerencias", []),
                "calificado_con_ia": True,
                "timestamp": datetime.utcnow().isoformat(),
            }
        except Exception as e:
            return {
                "error": str(e),
                "puntuacion": 0,
                "feedback": "Error al calificar con IA",
                "calificado_con_ia": False,
            }

    def _construir_prompt_calificacion(
        self,
        pregunta: str,
        respuesta_estudiante: str,
        respuesta_esperada: str | None,
        rubrica: dict[str, Any] | None,
        contexto: str | None,
    ) -> str:
        """Construye el prompt para calificación."""
        prompt = f"""Eres un profesor experto evaluando la respuesta de un estudiante.

PREGUNTA:
{pregunta}

RESPUESTA DEL ESTUDIANTE:
{respuesta_estudiante}
"""

        if respuesta_esperada:
            prompt += f"\n\nRESPUESTA ESPERADA/MODELO:\n{respuesta_esperada}"

        if rubrica:
            prompt += f"\n\nRÚBRICA DE EVALUACIÓN:\n{json.dumps(rubrica, indent=2, ensure_ascii=False)}"

        if contexto:
            prompt += f"\n\nCONTEXTO DEL CURSO:\n{contexto}"

        prompt += """

TAREA:
Evalúa la respuesta del estudiante considerando:
1. Corrección conceptual
2. Claridad y coherencia
3. Profundidad del análisis
4. Uso de ejemplos y evidencia
5. Gramática y ortografía

DEVUELVE TU EVALUACIÓN EN FORMATO JSON:
{
  "puntuacion": <número de 0 a 100>,
  "feedback": "<retroalimentación constructiva y detallada>",
  "fortalezas": ["<fortaleza 1>", "<fortaleza 2>", ...],
  "areas_mejora": ["<área 1>", "<área 2>", ...],
  "criterios": {
    "correccion_conceptual": <0-100>,
    "claridad": <0-100>,
    "profundidad": <0-100>,
    "evidencia": <0-100>,
    "gramatica": <0-100>
  },
  "sugerencias": ["<sugerencia 1>", "<sugerencia 2>", ...]
}

Sé justo, constructivo y específico en tu retroalimentación.
"""
        return prompt

    def _parsear_respuesta_calificacion(self, respuesta_texto: str) -> dict[str, Any]:
        """Parsea la respuesta JSON de Gemini."""
        try:
            # Extraer JSON del texto
            json_match = re.search(r"\{.*\}", respuesta_texto, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            return {"puntuacion": 50, "feedback": respuesta_texto}
        except:
            return {"puntuacion": 50, "feedback": respuesta_texto}

    # ==========================================
    # DETECCIÓN DE IA EN RESPUESTAS
    # ==========================================

    async def detectar_ia_en_respuesta(
        self, respuesta: str, contexto_estudiante: str | None = None
    ) -> dict[str, Any]:
        """Detecta si una respuesta fue generada por IA (ChatGPT, etc.).

        Returns:
            {
                "es_ia": bool,
                "probabilidad": 0.0-1.0,
                "indicadores": [...],
                "confianza": "baja|media|alta",
                "detalles": "..."
            }
        """
        prompt = f"""Eres un detector experto de texto generado por IA (ChatGPT, Claude, etc.).

TEXTO A ANALIZAR:
{respuesta}
"""

        if contexto_estudiante:
            prompt += f"\n\nCONTEXTO DEL ESTUDIANTE (escritura previa):\n{contexto_estudiante}"

        prompt += """

TAREA:
Analiza el texto y determina si fue generado por IA considerando:
1. Estructura demasiado perfecta y uniforme
2. Uso de frases genéricas típicas de IA
3. Falta de voz personal o estilo único
4. Transiciones artificialmente suaves
5. Vocabulario inusualmente sofisticado o formal
6. Ausencia de errores naturales humanos
7. Patrones de ChatGPT como listas numeradas excesivas

INDICADORES COMUNES DE IA:
- "Es importante destacar que..."
- "Cabe señalar que..."
- "En conclusión, podemos afirmar..."
- Estructura excesivamente simétrica
- Respuestas excesivamente exhaustivas

DEVUELVE EN JSON:
{
  "es_ia": <true|false>,
  "probabilidad": <0.0 a 1.0>,
  "confianza": "<baja|media|alta>",
  "indicadores": ["<indicador 1>", "<indicador 2>", ...],
  "detalles": "<explicación detallada>",
  "recomendacion": "<aprobar|revisar_manual|rechazar>"
}

Sé preciso y fundamenta tu análisis.
"""

        try:
            response = self.model.generate_content(prompt)
            resultado = self._parsear_respuesta_json(response.text)

            return {
                "es_ia": resultado.get("es_ia", False),
                "probabilidad": resultado.get("probabilidad", 0.0),
                "confianza": resultado.get("confianza", "baja"),
                "indicadores": resultado.get("indicadores", []),
                "detalles": resultado.get("detalles", ""),
                "recomendacion": resultado.get("recomendacion", "revisar_manual"),
                "timestamp": datetime.utcnow().isoformat(),
            }
        except Exception as e:
            return {"error": str(e), "es_ia": False, "probabilidad": 0.0}

    # ==========================================
    # DETECCIÓN DE PLAGIO
    # ==========================================

    def detectar_plagio_similitud(
        self,
        respuesta_actual: str,
        respuestas_comparar: list[str],
        umbral_similitud: float = 0.75,
    ) -> dict[str, Any]:
        """Detecta plagio comparando con otras respuestas usando algoritmo de similitud.

        Returns:
            {
                "es_plagio": bool,
                "similitud_maxima": 0.0-1.0,
                "respuestas_similares": [...],
                "fragmentos_copiados": [...]
            }
        """
        similitudes = []

        for i, respuesta_comparacion in enumerate(respuestas_comparar):
            similitud = self._calcular_similitud(
                respuesta_actual, respuesta_comparacion
            )

            if similitud >= umbral_similitud:
                similitudes.append(
                    {
                        "indice": i,
                        "similitud": similitud,
                        "fragmentos": self._encontrar_fragmentos_comunes(
                            respuesta_actual, respuesta_comparacion
                        ),
                    }
                )

        similitudes.sort(key=lambda x: x["similitud"], reverse=True)

        return {
            "es_plagio": len(similitudes) > 0,
            "similitud_maxima": similitudes[0]["similitud"] if similitudes else 0.0,
            "num_respuestas_similares": len(similitudes),
            "respuestas_similares": similitudes[:5],  # Top 5
            "umbral_usado": umbral_similitud,
            "timestamp": datetime.utcnow().isoformat(),
        }

    def _calcular_similitud(self, texto1: str, texto2: str) -> float:
        """Calcula similitud entre dos textos usando SequenceMatcher."""
        return SequenceMatcher(None, texto1.lower(), texto2.lower()).ratio()

    def _encontrar_fragmentos_comunes(
        self, texto1: str, texto2: str, min_longitud: int = 30
    ) -> list[str]:
        """Encuentra fragmentos de texto comunes entre dos textos."""
        matcher = SequenceMatcher(None, texto1, texto2)
        fragmentos = []

        for match in matcher.get_matching_blocks():
            if match.size >= min_longitud:
                fragmento = texto1[match.a : match.a + match.size]
                fragmentos.append(fragmento.strip())

        return fragmentos

    async def analizar_plagio_con_ia(
        self, respuesta_actual: str, respuestas_similares: list[str]
    ) -> dict[str, Any]:
        """Usa IA para analizar si la similitud es plagio o coincidencia natural."""
        prompt = f"""Eres un experto en detección de plagio académico.

RESPUESTA ACTUAL:
{respuesta_actual}

RESPUESTAS SIMILARES ENCONTRADAS:
"""

        for i, resp in enumerate(respuestas_similares[:3], 1):
            prompt += f"\n{i}. {resp}\n"

        prompt += """

TAREA:
Determina si la similitud detectada constituye plagio o es coincidencia natural.
Considera:
1. ¿Las ideas son idénticas o solo el tema?
2. ¿Hay frases copiadas textualmente?
3. ¿El estilo de escritura es sospechosamente similar?
4. ¿Podría ser coincidencia dado el tema?

DEVUELVE EN JSON:
{
  "es_plagio_confirmado": <true|false>,
  "nivel_sospecha": "<bajo|medio|alto|critico>",
  "explicacion": "<análisis detallado>",
  "evidencia": ["<evidencia 1>", ...],
  "recomendacion": "<aprobar|revisar_con_estudiante|penalizar>"
}
"""

        try:
            response = self.model.generate_content(prompt)
            return self._parsear_respuesta_json(response.text)
        except Exception as e:
            return {"error": str(e), "es_plagio_confirmado": False}

    # ==========================================
    # ANÁLISIS DE COMPORTAMIENTO
    # ==========================================

    async def analizar_comportamiento_estudiante(
        self,
        tiempo_respuestas: list[float],  # Tiempos en segundos
        patron_respuestas: list[bool],  # Correctas/Incorrectas
        eventos_anti_trampa: list[dict[str, Any]],
        contexto_examen: dict[str, Any],
    ) -> dict[str, Any]:
        """Analiza el comportamiento del estudiante durante el examen.
        Detecta patrones anómalos, posible trampa, estrés, etc.

        Returns:
            {
                "nivel_anomalia": "normal|sospechoso|muy_sospechoso",
                "comportamientos_detectados": [...],
                "recomendaciones": [...],
                "metricas": {...}
            }
        """
        # Análisis estadístico básico
        tiempo_promedio = (
            sum(tiempo_respuestas) / len(tiempo_respuestas) if tiempo_respuestas else 0
        )
        varianza_tiempo = self._calcular_varianza(tiempo_respuestas)

        # Detectar patrones
        respuestas_muy_rapidas = [t for t in tiempo_respuestas if t < 5]
        respuestas_muy_lentas = [t for t in tiempo_respuestas if t > 300]

        # Analizar con IA
        prompt = f"""Analiza el comportamiento de un estudiante durante un examen:

DATOS DEL EXAMEN:
- Tipo: {contexto_examen.get('tipo', 'general')}
- Duración total: {contexto_examen.get('duracion_minutos', 'N/A')} minutos
- Número de preguntas: {len(tiempo_respuestas)}

MÉTRICAS DE TIEMPO:
- Tiempo promedio por pregunta: {tiempo_promedio:.2f} segundos
- Respuestas < 5 segundos: {len(respuestas_muy_rapidas)}
- Respuestas > 5 minutos: {len(respuestas_muy_lentas)}
- Varianza de tiempo: {varianza_tiempo:.2f}

PATRÓN DE ACIERTOS:
- Total correctas: {sum(patron_respuestas)}
- Total incorrectas: {len(patron_respuestas) - sum(patron_respuestas)}
- Patrón: {patron_respuestas}

EVENTOS ANTI-TRAMPA DETECTADOS:
{json.dumps(eventos_anti_trampa, indent=2, ensure_ascii=False)}

TAREA:
Analiza si hay comportamientos anómalos que sugieran:
1. Uso de ayuda externa (búsquedas, ChatGPT, etc.)
2. Copia de otro estudiante
3. Respuestas al azar
4. Estrés o problemas técnicos
5. Comportamiento normal

DEVUELVE EN JSON:
{
  "nivel_anomalia": "<normal|leve|moderado|alto|critico>",
  "confianza_analisis": <0.0-1.0>,
  "comportamientos_detectados": [
    {
      "tipo": "<tipo_comportamiento>",
      "severidad": "<baja|media|alta>",
      "descripcion": "...",
      "evidencia": "..."
    }
  ],
  "metricas_clave": {
    "consistencia_tiempo": <0-100>,
    "patron_respuestas_logico": <0-100>,
    "nivel_concentracion": <0-100>
  },
  "recomendaciones": ["<recomendación 1>", ...],
  "accion_sugerida": "<ninguna|revisar|entrevistar|invalidar>"
}
"""

        try:
            response = self.model.generate_content(prompt)
            resultado = self._parsear_respuesta_json(response.text)

            return {
                **resultado,
                "metricas_calculadas": {
                    "tiempo_promedio": tiempo_promedio,
                    "respuestas_muy_rapidas": len(respuestas_muy_rapidas),
                    "respuestas_muy_lentas": len(respuestas_muy_lentas),
                    "varianza_tiempo": varianza_tiempo,
                },
                "timestamp": datetime.utcnow().isoformat(),
            }
        except Exception as e:
            return {
                "error": str(e),
                "nivel_anomalia": "error",
                "comportamientos_detectados": [],
            }

    def _calcular_varianza(self, valores: list[float]) -> float:
        """Calcula la varianza de una lista de valores."""
        if not valores:
            return 0.0
        media = sum(valores) / len(valores)
        return sum((x - media) ** 2 for x in valores) / len(valores)

    # ==========================================
    # GENERACIÓN DE PREGUNTAS CON IA
    # ==========================================

    async def generar_preguntas_inteligentes(
        self,
        tema: str,
        tipo_pregunta: str,
        dificultad: str,
        num_preguntas: int,
        contexto_curso: str | None = None,
        objetivos_aprendizaje: list[str] | None = None,
    ) -> list[dict[str, Any]]:
        """Genera preguntas automáticamente usando IA.

        Returns:
            Lista de preguntas con sus respuestas y metadatos
        """
        prompt = f"""Eres un profesor experto creando preguntas de evaluación.

REQUERIMIENTOS:
- Tema: {tema}
- Tipo de pregunta: {tipo_pregunta}
- Nivel de dificultad: {dificultad}
- Número de preguntas: {num_preguntas}
"""

        if contexto_curso:
            prompt += f"\n\nCONTEXTO DEL CURSO:\n{contexto_curso}"

        if objetivos_aprendizaje:
            prompt += "\n\nOBJETIVOS DE APRENDIZAJE:\n" + "\n".join(
                f"- {obj}" for obj in objetivos_aprendizaje
            )

        prompt += f"""

TAREA:
Genera {num_preguntas} preguntas de tipo "{tipo_pregunta}" sobre "{tema}".

Para cada pregunta incluye:
1. Enunciado claro y preciso
2. Opciones de respuesta (si aplica)
3. Respuesta correcta
4. Explicación de la respuesta
5. Puntos sugeridos
6. Tiempo estimado de respuesta

DEVUELVE EN JSON:
{{
  "preguntas": [
    {{
      "enunciado": "...",
      "tipo": "{tipo_pregunta}",
      "opciones": ["A", "B", "C", "D"],  # Si aplica
      "respuesta_correcta": "...",
      "explicacion": "...",
      "puntos_sugeridos": <número>,
      "tiempo_estimado_segundos": <número>,
      "dificultad": "{dificultad}",
      "etiquetas": ["tag1", "tag2"]
    }}
  ]
}}

Asegúrate de que las preguntas sean:
- Relevantes al tema
- Clara y sin ambigüedades
- Apropiadas al nivel de dificultad
- Evaluativas (no triviales)
"""

        try:
            response = self.model.generate_content(prompt)
            resultado = self._parsear_respuesta_json(response.text)
            return resultado.get("preguntas", [])
        except Exception as e:
            return [{"error": str(e)}]

    # ==========================================
    # FEEDBACK PERSONALIZADO
    # ==========================================

    async def generar_feedback_personalizado(
        self,
        estudiante_nombre: str,
        desempeno_examen: dict[str, Any],
        historial: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        """Genera feedback personalizado e inteligente para el estudiante."""
        prompt = f"""Eres un tutor experto generando retroalimentación personalizada.

ESTUDIANTE: {estudiante_nombre}

DESEMPEÑO EN ESTE EXAMEN:
{json.dumps(desempeno_examen, indent=2, ensure_ascii=False)}
"""

        if historial:
            prompt += f"\n\nHISTORIAL PREVIO:\n{json.dumps(historial[-3:], indent=2, ensure_ascii=False)}"

        prompt += """

TAREA:
Genera retroalimentación personalizada, motivadora y constructiva que incluya:
1. Reconocimiento de logros
2. Áreas de mejora específicas
3. Comparación con desempeño previo (si aplica)
4. Recomendaciones de estudio
5. Próximos pasos sugeridos

DEVUELVE EN JSON:
{
  "mensaje_principal": "<mensaje personalizado y motivador>",
  "logros": ["<logro 1>", "<logro 2>", ...],
  "areas_mejora": [
    {
      "area": "...",
      "sugerencia": "...",
      "recursos": ["recurso 1", ...]
    }
  ],
  "comparacion_historica": "<análisis de progreso>",
  "recomendaciones": ["<recomendación 1>", ...],
  "motivacion": "<mensaje motivacional>",
  "proximos_objetivos": ["<objetivo 1>", ...]
}

Sé empático, específico y orientado a la acción.
"""

        try:
            response = self.model.generate_content(prompt)
            return self._parsear_respuesta_json(response.text)
        except Exception as e:
            return {"error": str(e), "mensaje_principal": "Feedback no disponible"}

    # ==========================================
    # UTILIDADES
    # ==========================================

    def _parsear_respuesta_json(self, respuesta_texto: str) -> dict[str, Any]:
        """Parsea respuesta JSON de Gemini."""
        try:
            # Buscar JSON en el texto
            json_match = re.search(r"\{.*\}", respuesta_texto, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            return {"raw_response": respuesta_texto}
        except Exception as e:
            return {
                "error": f"Error parseando JSON: {e!s}",
                "raw_response": respuesta_texto,
            }

    # ==========================================
    # SUGERENCIAS INTELIGENTES PARA PROFESORES
    # ==========================================

    async def analizar_efectividad_pregunta(
        self, pregunta: str, estadisticas: dict[str, Any]
    ) -> dict[str, Any]:
        """Analiza la efectividad de una pregunta basándose en estadísticas.
        Sugiere mejoras si es necesario.
        """
        prompt = f"""Analiza la efectividad de una pregunta de evaluación:

PREGUNTA:
{pregunta}

ESTADÍSTICAS:
- Veces utilizada: {estadisticas.get('veces_utilizada', 0)}
- Tasa de acierto: {estadisticas.get('tasa_acierto', 0)}%
- Tiempo promedio de respuesta: {estadisticas.get('tiempo_promedio', 0)} segundos
- Índice de discriminación: {estadisticas.get('indice_discriminacion', 0)}

El índice de discriminación mide si los estudiantes con mejor desempeño general
aciertan más esta pregunta (bueno) o si no hay diferencia (malo).

TAREA:
Evalúa si la pregunta es efectiva y sugiere mejoras.

DEVUELVE EN JSON:
{
  "es_efectiva": <true|false>,
  "calidad": "<excelente|buena|regular|mala>",
  "problemas_identificados": ["<problema 1>", ...],
  "sugerencias_mejora": ["<sugerencia 1>", ...],
  "pregunta_mejorada": "<versión mejorada de la pregunta>",
  "explicacion": "..."
}
"""

        try:
            response = self.model.generate_content(prompt)
            return self._parsear_respuesta_json(response.text)
        except Exception as e:
            return {"error": str(e), "es_efectiva": True}


# Singleton para usar en toda la aplicación
ia_evaluacion_service = IAEvaluacionService()
