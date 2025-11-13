"""Parseador de respuestas de servicios de IA.

Extrae y valida la estructura JSON de las respuestas de IA,
manejando casos edge y errores de formato.

Author: Gemini AI Assistant
Date: 31 octubre 2025
"""

import json
import logging
import re
from typing import Any

from src.services.ai.exceptions import ResponseParsingError


logger = logging.getLogger(__name__)


class ResponseParser:
    """Parser robusto para respuestas de IA.

    Maneja múltiples formatos de respuesta y extrae JSON incluso
    cuando la IA incluye texto adicional o markdown.
    """

    @staticmethod
    def extraer_json(respuesta: str) -> dict[str, Any]:
        """Extrae JSON de una respuesta que puede contener texto adicional.

        Args:
            respuesta: Respuesta cruda de la IA

        Returns:
            Dict: JSON parseado y validado

        Raises:
            ResponseParsingError: Si no se puede extraer JSON válido
        """
        if not respuesta or not respuesta.strip():
            msg = "Respuesta vacía de la IA"
            raise ResponseParsingError(msg)

        # Intentar parsear directamente
        try:
            return json.loads(respuesta.strip())
        except json.JSONDecodeError:
            pass  # Continuar con métodos alternativos

        # Método 1: Buscar JSON entre bloques de código markdown
        json_match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", respuesta, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(1))
            except json.JSONDecodeError:
                pass

        # Método 2: Buscar el primer objeto JSON válido
        json_match = re.search(r"\{.*\}", respuesta, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(0))
            except json.JSONDecodeError:
                pass

        # Método 3: Limpiar texto y reintentar
        respuesta_limpia = respuesta.strip()
        # Remover markdown común
        respuesta_limpia = re.sub(r"```(?:json)?", "", respuesta_limpia)
        respuesta_limpia = re.sub(r"```", "", respuesta_limpia)

        try:
            return json.loads(respuesta_limpia)
        except json.JSONDecodeError as e:
            logger.exception(f"No se pudo parsear JSON: {e!s}")
            msg = "La respuesta de la IA no contiene JSON válido"
            raise ResponseParsingError(
                msg,
                raw_response=respuesta[:500],
            ) from None

    @staticmethod
    def validar_estructura_retroalimentacion(data: dict[str, Any]) -> dict[str, Any]:
        """Valida y normaliza la estructura de retroalimentación.

        Args:
            data: Dict parseado de la respuesta

        Returns:
            Dict: Estructura validada y normalizada

        Raises:
            ResponseParsingError: Si faltan campos obligatorios
        """
        campos_requeridos = [
            "analisis_general",
            "fortalezas",
            "areas_mejora",
            "sugerencias_especificas",
            "nivel_cumplimiento",
        ]

        campos_faltantes = [campo for campo in campos_requeridos if campo not in data]

        if campos_faltantes:
            msg = f"Faltan campos requeridos en la respuesta: {', '.join(campos_faltantes)}"
            raise ResponseParsingError(
                msg,
                raw_response=json.dumps(data, indent=2),
            )

        # Normalizar estructura
        return {
            "analisis_general": str(data["analisis_general"]),
            "fortalezas": ResponseParser._normalizar_lista(data["fortalezas"]),
            "areas_mejora": ResponseParser._normalizar_lista(data["areas_mejora"]),
            "sugerencias_especificas": ResponseParser._normalizar_sugerencias(
                data["sugerencias_especificas"]
            ),
            "nivel_cumplimiento": ResponseParser._normalizar_porcentaje(
                data["nivel_cumplimiento"]
            ),
            "cumple_rubrica": data.get("cumple_rubrica", {}),
            "puntos_clave_missing": ResponseParser._normalizar_lista(
                data.get("puntos_clave_missing", [])
            ),
            "recursos_recomendados": ResponseParser._normalizar_recursos(
                data.get("recursos_recomendados", [])
            ),
        }

    @staticmethod
    def validar_estructura_calificacion(data: dict[str, Any]) -> dict[str, Any]:
        """Valida estructura de respuesta de calificación.

        Args:
            data: Dict parseado

        Returns:
            Dict: Estructura validada

        Raises:
            ResponseParsingError: Si la estructura es inválida
        """
        if "calificacion" not in data:
            msg = "Falta campo 'calificacion' en respuesta"
            raise ResponseParsingError(msg)

        try:
            calificacion = float(data["calificacion"])
        except (ValueError, TypeError):
            msg = f"Calificación inválida: {data['calificacion']}"
            raise ResponseParsingError(msg) from None

        if not 0.0 <= calificacion <= 5.0:
            msg = f"Calificación fuera de rango (0-5): {calificacion}"
            raise ResponseParsingError(msg)

        return {
            "calificacion": round(calificacion, 1),
            "justificacion": str(data.get("justificacion", "")),
        }

    @staticmethod
    def _normalizar_lista(valor: Any) -> list[str]:
        """Normaliza un valor a lista de strings."""
        if isinstance(valor, list):
            return [str(item) for item in valor]
        if isinstance(valor, str):
            return [valor]
        return []

    @staticmethod
    def _normalizar_sugerencias(sugerencias: Any) -> list[dict[str, str]]:
        """Normaliza lista de sugerencias específicas."""
        if not isinstance(sugerencias, list):
            return []

        resultado = []
        for sug in sugerencias:
            if isinstance(sug, dict):
                resultado.append(
                    {
                        "ubicacion": str(sug.get("ubicacion", "")),
                        "problema": str(sug.get("problema", "")),
                        "sugerencia": str(sug.get("sugerencia", "")),
                        "ejemplo": str(sug.get("ejemplo", "")),
                    }
                )
            elif isinstance(sug, str):
                # Convertir string simple a estructura
                resultado.append(
                    {"ubicacion": "", "problema": sug, "sugerencia": "", "ejemplo": ""}
                )

        return resultado

    @staticmethod
    def _normalizar_recursos(recursos: Any) -> list[dict[str, str]]:
        """Normaliza lista de recursos recomendados."""
        if not isinstance(recursos, list):
            return []

        resultado = []
        for recurso in recursos:
            if isinstance(recurso, dict):
                resultado.append(
                    {
                        "titulo": str(recurso.get("titulo", "")),
                        "url": str(recurso.get("url", "")),
                        "descripcion": str(recurso.get("descripcion", "")),
                    }
                )

        return resultado

    @staticmethod
    def _normalizar_porcentaje(valor: Any) -> str:
        """Normaliza valor de porcentaje.

        Acepta:
        - "85%" -> "85%"
        - 85 -> "85%"
        - 0.85 -> "85%"
        - "85" -> "85%"
        """
        if isinstance(valor, str):
            # Ya tiene formato correcto
            if "%" in valor:
                return valor
            # Es string numérico
            try:
                num = float(valor)
                if num <= 1.0:
                    num *= 100
                return f"{int(num)}%"
            except ValueError:
                return "0%"

        elif isinstance(valor, (int, float)):
            # Convertir a porcentaje
            if valor <= 1.0:
                valor *= 100
            return f"{int(valor)}%"

        return "0%"

    @staticmethod
    def sanitizar_respuesta(respuesta: str) -> str:
        """Limpia la respuesta de caracteres problemáticos.

        Args:
            respuesta: Respuesta cruda

        Returns:
            str: Respuesta limpiada
        """
        # Remover BOM (Byte Order Mark)
        respuesta = respuesta.replace("\ufeff", "")

        # Normalizar saltos de línea
        respuesta = respuesta.replace("\r\n", "\n")

        # Remover caracteres de control excepto tabs y newlines
        respuesta = re.sub(r"[\x00-\x08\x0b-\x0c\x0e-\x1f\x7f]", "", respuesta)

        return respuesta.strip()

    @staticmethod
    def extraer_metadata(respuesta_completa: Any) -> dict[str, Any]:
        """Extrae metadata de la respuesta completa de la API.

        Args:
            respuesta_completa: Objeto de respuesta de la API de Gemini

        Returns:
            Dict con metadata relevante (tokens, modelo, etc.)
        """
        metadata = {
            "timestamp": None,
            "modelo": None,
            "tokens_prompt": 0,
            "tokens_completion": 0,
            "tokens_total": 0,
            "finish_reason": None,
        }

        try:
            # Intentar extraer de objeto google.generativeai
            if hasattr(respuesta_completa, "usage_metadata"):
                usage = respuesta_completa.usage_metadata
                metadata["tokens_prompt"] = getattr(usage, "prompt_token_count", 0)
                metadata["tokens_completion"] = getattr(
                    usage, "candidates_token_count", 0
                )
                metadata["tokens_total"] = getattr(usage, "total_token_count", 0)

            if hasattr(respuesta_completa, "model_version"):
                metadata["modelo"] = respuesta_completa.model_version

            if hasattr(respuesta_completa, "candidates"):
                if respuesta_completa.candidates:
                    metadata["finish_reason"] = getattr(
                        respuesta_completa.candidates[0], "finish_reason", None
                    )

        except Exception as e:
            logger.warning(f"No se pudo extraer metadata completa: {e}")

        return metadata
