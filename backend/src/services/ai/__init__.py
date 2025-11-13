"""Servicios de IA para retroalimentación educativa.

Este módulo proporciona servicios de análisis con IA para generar
retroalimentación estructurada y calificaciones sugeridas de trabajos
académicos usando Google Gemini.

Módulos principales:
    - gemini_service: Implementación con Google Gemini 1.5 Flash
    - base: Interfaz abstracta para servicios de IA
    - config: Configuración y parámetros
    - exceptions: Excepciones personalizadas
    - helpers: Utilidades (procesamiento archivos, prompts, parseo, costos)

Uso rápido:
    >>> from src.services.ai import GeminiService
    >>>
    >>> service = GeminiService(api_key="tu_api_key")
    >>> await service.inicializar()
    >>>
    >>> retroalimentacion = await service.generar_retroalimentacion(
    ...     entrega=entrega_obj,
    ...     tarea=tarea_obj,
    ...     archivo_contenido=contenido
    ... )

Author: Gemini AI Assistant
Date: 31 octubre 2025
Version: 1.0.0
"""

from src.services.ai.base import BaseAIService
from src.services.ai.config import AIConfig, GeminiModel, ai_config
from src.services.ai.exceptions import (
    AIServiceException,
    ConfigurationError,
    ContentFilterError,
    FileProcessingError,
    GeminiAPIError,
    InvalidPromptError,
    RateLimitExceededError,
    ResponseParsingError,
    TokenLimitExceededError,
)
from src.services.ai.gemini_service import GeminiService


__version__ = "1.0.0"
__author__ = "Gemini AI Assistant"

__all__ = [
    "AIConfig",
    # Excepciones
    "AIServiceException",
    # Base y configuración
    "BaseAIService",
    "ConfigurationError",
    "ContentFilterError",
    "FileProcessingError",
    "GeminiAPIError",
    "GeminiModel",
    # Servicio principal
    "GeminiService",
    "InvalidPromptError",
    "RateLimitExceededError",
    "ResponseParsingError",
    "TokenLimitExceededError",
    "ai_config",
]
