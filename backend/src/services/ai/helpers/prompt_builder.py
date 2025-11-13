"""Constructor inteligente de prompts para servicios de IA.

Este módulo construye prompts optimizados y contextualizados para obtener
mejores respuestas de la IA, siguiendo mejores prácticas de prompt engineering.

Author: Gemini AI Assistant
Date: 31 octubre 2025
"""

import json
from typing import Any

from src.models.academic.tarea import EntregaTarea, Tarea
from src.services.ai.config import SYSTEM_PROMPTS


class PromptBuilder:
    """Constructor de prompts estructurados y optimizados.

    Aplica técnicas de prompt engineering como:
    - Few-shot learning (ejemplos)
    - Chain-of-thought (razonamiento paso a paso)
    - Instrucciones específicas de formato
    - Contexto relevante y acotado
    """

    @staticmethod
    def construir_prompt_retroalimentacion(
        tarea: Tarea,
        entrega: EntregaTarea,
        contenido: str,
        prompt_personalizado: str | None = None,
    ) -> str:
        """Construye el prompt principal para generar retroalimentación.

        Args:
            tarea: Tarea con instrucciones y rúbrica
            entrega: Entrega del estudiante
            contenido: Contenido extraído del archivo
            prompt_personalizado: Instrucciones adicionales del docente

        Returns:
            str: Prompt completo y estructurado
        """
        # Sistema base
        prompt_partes = [
            SYSTEM_PROMPTS["retroalimentacion_base"],
            "\n" + "=" * 80 + "\n",
        ]

        # Contexto de la tarea
        prompt_partes.append("## CONTEXTO DE LA TAREA\n")
        prompt_partes.append(f"**Título**: {tarea.titulo}\n")
        prompt_partes.append(
            f"**Tipo**: {tarea.tipo.value if tarea.tipo else 'General'}\n"
        )

        if tarea.descripcion:
            prompt_partes.append(f"**Descripción**: {tarea.descripcion}\n")

        if tarea.instrucciones:
            prompt_partes.append(
                f"\n**Instrucciones específicas**:\n{tarea.instrucciones}\n"
            )

        # Rúbrica de evaluación (CRÍTICO)
        if tarea.rubrica:
            prompt_partes.append("\n## RÚBRICA DE EVALUACIÓN\n")
            prompt_partes.append("Evalúa el trabajo según estos criterios:\n\n")

            rubrica = (
                tarea.rubrica
                if isinstance(tarea.rubrica, dict)
                else json.loads(tarea.rubrica)
            )

            for idx, criterio in enumerate(rubrica.get("criterios", []), 1):
                prompt_partes.append(
                    f"**{idx}. {criterio.get('nombre', 'Criterio')}**\n"
                )
                prompt_partes.append(f"   - Peso: {criterio.get('peso', 0)}%\n")

                if "descripcion" in criterio:
                    prompt_partes.append(f"   - {criterio['descripcion']}\n")

                if "niveles" in criterio:
                    prompt_partes.append("   - Niveles de desempeño:\n")
                    for nivel in criterio["niveles"]:
                        prompt_partes.append(
                            f"     • {nivel.get('nombre', '')}: "
                            f"{nivel.get('puntos', 0)} pts - "
                            f"{nivel.get('descripcion', '')}\n"
                        )
                prompt_partes.append("\n")

        # Objetivos de aprendizaje
        if tarea.objetivos:
            prompt_partes.append("## OBJETIVOS DE APRENDIZAJE\n")
            prompt_partes.append(f"{tarea.objetivos}\n\n")

        # Instrucciones personalizadas del docente
        if prompt_personalizado:
            prompt_partes.append("## INSTRUCCIONES ADICIONALES DEL DOCENTE\n")
            prompt_partes.append(f"{prompt_personalizado}\n\n")

        # Tipo específico (código vs ensayo)
        if tarea.tipo and "codigo" in str(tarea.tipo).lower():
            prompt_partes.append(SYSTEM_PROMPTS["calificacion_codigo"] + "\n")
        elif tarea.tipo and any(
            t in str(tarea.tipo).lower() for t in ["ensayo", "investigacion"]
        ):
            prompt_partes.append(SYSTEM_PROMPTS["calificacion_ensayo"] + "\n")

        prompt_partes.append("=" * 80 + "\n\n")

        # Trabajo del estudiante
        prompt_partes.append("## TRABAJO DEL ESTUDIANTE\n\n")

        # Metadata de la entrega
        prompt_partes.append("**Información de la entrega:**\n")
        if entrega.fecha_entrega:
            prompt_partes.append(f"- Fecha de entrega: {entrega.fecha_entrega}\n")
        if entrega.es_tardia:
            prompt_partes.append("- ⚠️ **ENTREGA TARDÍA**\n")
        if entrega.intentos > 1:
            prompt_partes.append(f"- Intento #{entrega.intentos}\n")

        prompt_partes.append(f"\n**Contenido**:\n\n```\n{contenido}\n```\n\n")

        # Instrucciones finales
        prompt_partes.append("=" * 80 + "\n")
        prompt_partes.append("## TU TAREA\n\n")
        prompt_partes.append(
            "Analiza el trabajo del estudiante siguiendo la rúbrica y proporciona "
            "retroalimentación constructiva, específica y accionable.\n\n"
        )
        prompt_partes.append(
            "**IMPORTANTE**: Responde ÚNICAMENTE con un objeto JSON válido "
            "siguiendo la estructura especificada al inicio. "
            "NO incluyas markdown, explicaciones fuera del JSON, ni ningún otro texto.\n\n"
        )
        prompt_partes.append(
            "El JSON debe tener estas claves obligatorias: "
            "analisis_general, fortalezas, areas_mejora, sugerencias_especificas, "
            "nivel_cumplimiento, cumple_rubrica, puntos_clave_missing, recursos_recomendados\n"
        )

        return "".join(prompt_partes)

    @staticmethod
    def construir_prompt_calificacion(
        tarea: Tarea, retroalimentacion: dict[str, Any]
    ) -> str:
        """Construye prompt para calcular calificación numérica.

        Args:
            tarea: Tarea con criterios de evaluación
            retroalimentacion: Retroalimentación ya generada

        Returns:
            str: Prompt para calificación
        """
        prompt_partes = [
            "Eres un asistente de calificación académica.\n\n",
            "## RÚBRICA DE EVALUACIÓN\n\n",
        ]

        if tarea.rubrica:
            rubrica = (
                tarea.rubrica
                if isinstance(tarea.rubrica, dict)
                else json.loads(tarea.rubrica)
            )

            for criterio in rubrica.get("criterios", []):
                prompt_partes.append(
                    f"- {criterio.get('nombre')}: "
                    f"{criterio.get('peso')}% del total\n"
                )

        prompt_partes.append("\n## ANÁLISIS YA REALIZADO\n\n")
        prompt_partes.append(
            f"```json\n{json.dumps(retroalimentacion, indent=2, ensure_ascii=False)}\n```\n\n"
        )

        prompt_partes.append("## TAREA\n\n")
        prompt_partes.append(
            "Basándote en el análisis previo y la rúbrica, calcula una calificación "
            "numérica justa en escala de 0.0 a 5.0.\n\n"
        )
        prompt_partes.append(
            "Responde ÚNICAMENTE con un objeto JSON con esta estructura:\n"
            "{\n"
            '  "calificacion": 4.2,\n'
            '  "justificacion": "Explicación breve de por qué esta calificación"\n'
            "}\n"
        )

        return "".join(prompt_partes)

    @staticmethod
    def construir_prompt_validacion(
        contenido: str, tipo_archivo: str, max_caracteres: int = 1000
    ) -> str:
        """Construye prompt para validar contenido antes de análisis completo.

        Args:
            contenido: Contenido a validar
            tipo_archivo: MIME type del archivo
            max_caracteres: Máximo de caracteres del contenido a incluir

        Returns:
            str: Prompt de validación
        """
        contenido_muestra = contenido[:max_caracteres]
        if len(contenido) > max_caracteres:
            contenido_muestra += "\n\n... (contenido truncado para validación)"

        return f"""Eres un validador de contenido académico.

## CONTENIDO A VALIDAR

Tipo de archivo: {tipo_archivo}

Contenido (muestra):
```
{contenido_muestra}
```

## TAREA

Determina si este contenido es apropiado para análisis académico.

Responde ÚNICAMENTE con un objeto JSON:
{{
  "valido": true/false,
  "razones": ["razón 1", "razón 2"],
  "advertencias": ["advertencia 1"],
  "tipo_detectado": "codigo/ensayo/presentacion/otro"
}}

CRITERIOS DE VALIDACIÓN:
- ¿El contenido está completo o parece truncado/corrupto?
- ¿Es contenido académico legítimo?
- ¿Tiene suficiente sustancia para evaluar?
- ¿Está en un idioma comprensible?
"""

    @staticmethod
    def acortar_contenido_si_necesario(
        contenido: str, max_tokens: int = 30000, tokens_por_palabra: float = 1.3
    ) -> str:
        """Acorta el contenido si excede el límite de tokens.

        Args:
            contenido: Contenido original
            max_tokens: Máximo de tokens permitidos
            tokens_por_palabra: Factor de conversión (conservador)

        Returns:
            str: Contenido acortado si fue necesario
        """
        palabras = contenido.split()
        tokens_estimados = len(palabras) * tokens_por_palabra

        if tokens_estimados <= max_tokens:
            return contenido

        # Calcular cuántas palabras conservar
        palabras_max = int(max_tokens / tokens_por_palabra)

        # Tomar inicio y fin para mantener contexto
        palabras_inicio = palabras[: palabras_max // 2]
        palabras_fin = palabras[-palabras_max // 2 :]

        return (
            " ".join(palabras_inicio)
            + "\n\n... [CONTENIDO OMITIDO PARA CUMPLIR LÍMITE DE TOKENS] ...\n\n"
            + " ".join(palabras_fin)
        )

    @staticmethod
    def validar_prompt_length(prompt: str, max_tokens: int = 32000) -> bool:
        """Valida que el prompt no exceda el límite de tokens.

        Args:
            prompt: Prompt a validar
            max_tokens: Límite máximo de tokens

        Returns:
            bool: True si el prompt es válido
        """
        # Estimación conservadora: 1.3 tokens por palabra
        palabras = len(prompt.split())
        tokens_estimados = palabras * 1.3

        return tokens_estimados <= max_tokens
