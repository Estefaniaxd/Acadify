"""Excepciones personalizadas para servicios de IA.

Este módulo define una jerarquía de excepciones específicas para el sistema
de retroalimentación con IA, permitiendo un manejo de errores granular y
mensajes claros para el usuario.

Author: Gemini AI Assistant
Date: 31 octubre 2025
"""

from typing import Any


class AIServiceException(Exception):
    """Excepción base para todos los errores relacionados con servicios de IA.

    Attributes:
        message: Mensaje de error principal
        details: Detalles adicionales del error (JSON serializable)
        error_code: Código de error específico para logging/tracking
    """

    def __init__(
        self,
        message: str,
        details: dict[str, Any] | None = None,
        error_code: str | None = None,
    ) -> None:
        self.message = message
        self.details = details or {}
        self.error_code = error_code or "AI_GENERAL_ERROR"
        super().__init__(self.message)

    def to_dict(self) -> dict[str, Any]:
        """Serializa la excepción a un diccionario JSON-compatible."""
        return {
            "error": self.__class__.__name__,
            "message": self.message,
            "details": self.details,
            "error_code": self.error_code,
        }


class GeminiAPIError(AIServiceException):
    """Error al comunicarse con la API de Google Gemini.

    Ejemplos:
        - Fallo de conexión
        - Timeout
        - Rate limit excedido (HTTP 429)
        - Autenticación inválida (HTTP 401)
        - Error del servidor (HTTP 500+)
    """

    def __init__(
        self,
        message: str,
        status_code: int | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(
            message=message,
            details={**(details or {}), "status_code": status_code},
            error_code="GEMINI_API_ERROR",
        )
        self.status_code = status_code


class RateLimitExceededError(GeminiAPIError):
    """Se excedió el límite de tasa de la API de Gemini.

    Attributes:
        retry_after: Segundos hasta que se puede reintentar
    """

    def __init__(
        self,
        message: str = "Se excedió el límite de solicitudes a la API de Gemini",
        retry_after: int | None = None,
    ) -> None:
        super().__init__(
            message=message,
            status_code=429,
            details={"retry_after_seconds": retry_after},
        )
        self.retry_after = retry_after


class InvalidPromptError(AIServiceException):
    """El prompt construido es inválido o excede límites.

    Ejemplos:
        - Prompt vacío
        - Excede longitud máxima de tokens
        - Formato JSON inválido en instrucciones
    """

    def __init__(self, message: str, prompt_length: int | None = None) -> None:
        super().__init__(
            message=message,
            details={"prompt_length": prompt_length},
            error_code="INVALID_PROMPT",
        )


class FileProcessingError(AIServiceException):
    """Error al procesar un archivo para análisis con IA.

    Ejemplos:
        - Archivo corrupto
        - Formato no soportado
        - Tamaño excede límite
        - No se puede extraer texto
    """

    def __init__(
        self, message: str, file_name: str | None = None, file_type: str | None = None
    ) -> None:
        super().__init__(
            message=message,
            details={"file_name": file_name, "file_type": file_type},
            error_code="FILE_PROCESSING_ERROR",
        )


class ResponseParsingError(AIServiceException):
    """Error al parsear la respuesta de la IA.

    Ejemplos:
        - JSON inválido en respuesta
        - Estructura inesperada
        - Campos requeridos faltantes
    """

    def __init__(self, message: str, raw_response: str | None = None) -> None:
        super().__init__(
            message=message,
            details={"raw_response": raw_response[:500] if raw_response else None},
            error_code="RESPONSE_PARSING_ERROR",
        )


class TokenLimitExceededError(AIServiceException):
    """El contenido excede el límite de tokens del modelo.

    Attributes:
        current_tokens: Número de tokens del contenido
        max_tokens: Límite máximo del modelo
    """

    def __init__(self, message: str, current_tokens: int, max_tokens: int) -> None:
        super().__init__(
            message=message,
            details={
                "current_tokens": current_tokens,
                "max_tokens": max_tokens,
                "excess_tokens": current_tokens - max_tokens,
            },
            error_code="TOKEN_LIMIT_EXCEEDED",
        )
        self.current_tokens = current_tokens
        self.max_tokens = max_tokens


class ContentFilterError(AIServiceException):
    """El contenido fue bloqueado por filtros de seguridad de Gemini.

    Google Gemini tiene filtros para contenido:
    - Violento
    - Sexual
    - Odio/discriminación
    - Información peligrosa
    """

    def __init__(
        self,
        message: str = "El contenido fue bloqueado por filtros de seguridad",
        blocked_reason: str | None = None,
    ) -> None:
        super().__init__(
            message=message,
            details={"blocked_reason": blocked_reason},
            error_code="CONTENT_FILTER_BLOCKED",
        )


class ConfigurationError(AIServiceException):
    """Error en la configuración del servicio de IA.

    Ejemplos:
        - API Key faltante o inválida
        - Modelo no disponible
        - Configuración de temperatura inválida
    """

    def __init__(self, message: str, config_key: str | None = None) -> None:
        super().__init__(
            message=message,
            details={"config_key": config_key},
            error_code="CONFIGURATION_ERROR",
        )
