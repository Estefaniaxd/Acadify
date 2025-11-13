"""Clase base abstracta para servicios de IA.

Define la interfaz común que deben implementar todos los servicios de IA
(Gemini, OpenAI, Claude, etc.) para facilitar la intercambiabilidad.

Author: Gemini AI Assistant
Date: 31 octubre 2025
"""

from abc import ABC, abstractmethod
from datetime import datetime
import logging
from typing import Any

from src.models.academic.tarea import EntregaTarea, Tarea


logger = logging.getLogger(__name__)


class BaseAIService(ABC):
    """Interfaz abstracta para servicios de retroalimentación con IA.

    Esta clase define el contrato que debe cumplir cualquier implementación
    de servicio de IA, siguiendo el principio de Dependency Inversion (SOLID).

    Attributes:
        config: Configuración del servicio
        _initialized: Flag de inicialización correcta
    """

    def __init__(self, config: dict[str, Any]) -> None:
        """Inicializa el servicio base.

        Args:
            config: Diccionario de configuración específico del proveedor
        """
        self.config = config
        self._initialized = False
        self._request_count = 0
        self._token_count = 0
        self._error_count = 0
        self._last_request_time: datetime | None = None

        logger.info(f"Inicializando {self.__class__.__name__}")

    @abstractmethod
    async def generar_retroalimentacion(
        self,
        entrega: EntregaTarea,
        tarea: Tarea,
        archivo_contenido: str | None = None,
        opciones: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Genera retroalimentación estructurada para una entrega.

        Este es el método principal que deben implementar todos los servicios.

        Args:
            entrega: Instancia de EntregaTarea con la entrega del estudiante
            tarea: Instancia de Tarea con las instrucciones y rúbrica
            archivo_contenido: Contenido extraído del archivo (texto plano)
            opciones: Parámetros adicionales (temperatura, max_tokens, etc.)

        Returns:
            Dict con estructura de retroalimentación:
            {
                "timestamp": "2025-10-31T10:30:00Z",
                "modelo_usado": "gemini-1.5-flash",
                "analisis_general": "...",
                "fortalezas": [...],
                "areas_mejora": [...],
                "sugerencias_especificas": [...],
                "nivel_cumplimiento": "85%",
                "cumple_rubrica": {...},
                "puntos_clave_missing": [...],
                "recursos_recomendados": [...]
            }

        Raises:
            AIServiceException: Error general del servicio
            RateLimitExceededError: Límite de tasa excedido
            FileProcessingError: Error procesando archivo
        """

    @abstractmethod
    async def calcular_calificacion_sugerida(
        self, entrega: EntregaTarea, tarea: Tarea, retroalimentacion: dict[str, Any]
    ) -> float:
        """Calcula una calificación sugerida basada en la retroalimentación.

        Args:
            entrega: Instancia de EntregaTarea
            tarea: Instancia de Tarea con criterios de evaluación
            retroalimentacion: Dict con retroalimentación ya generada

        Returns:
            float: Calificación sugerida (0.0 - 5.0)

        Note:
            La calificación final SIEMPRE debe ser aprobada por el docente.
            Este es solo un valor preliminar sugerido por la IA.
        """

    @abstractmethod
    async def validar_contenido(
        self, contenido: str, tipo_archivo: str
    ) -> dict[str, Any]:
        """Valida que el contenido sea apropiado para análisis.

        Args:
            contenido: Contenido a validar
            tipo_archivo: MIME type del archivo

        Returns:
            Dict con resultado de validación:
            {
                "valido": bool,
                "razones": ["razón1", "razón2"],
                "advertencias": ["advertencia1"]
            }
        """

    @abstractmethod
    def estimar_tokens(self, texto: str) -> int:
        """Estima el número de tokens en un texto.

        Args:
            texto: Texto a analizar

        Returns:
            int: Número estimado de tokens

        Note:
            La estimación puede no ser exacta, pero debe ser conservadora
            (preferir sobrestimar que subestimar).
        """

    @abstractmethod
    async def verificar_disponibilidad(self) -> bool:
        """Verifica que el servicio esté disponible y configurado correctamente.

        Returns:
            bool: True si el servicio está operacional

        Raises:
            ConfigurationError: Si la configuración es inválida
        """

    # ==================== Métodos Comunes (No Abstractos) ====================

    def registrar_request(self, tokens_usados: int = 0) -> None:
        """Registra estadísticas de un request.

        Args:
            tokens_usados: Número de tokens consumidos
        """
        self._request_count += 1
        self._token_count += tokens_usados
        self._last_request_time = datetime.utcnow()

        logger.debug(
            f"Request #{self._request_count} | "
            f"Tokens: {tokens_usados} | "
            f"Total acumulado: {self._token_count}"
        )

    def registrar_error(self, error: Exception) -> None:
        """Registra un error ocurrido.

        Args:
            error: Excepción capturada
        """
        self._error_count += 1
        logger.error(
            f"Error #{self._error_count} en {self.__class__.__name__}: "
            f"{error.__class__.__name__}: {error!s}"
        )

    def get_estadisticas(self) -> dict[str, Any]:
        """Retorna estadísticas de uso del servicio.

        Returns:
            Dict con métricas de uso
        """
        return {
            "servicio": self.__class__.__name__,
            "requests_totales": self._request_count,
            "tokens_totales": self._token_count,
            "errores_totales": self._error_count,
            "ultimo_request": (
                self._last_request_time.isoformat() if self._last_request_time else None
            ),
            "inicializado": self._initialized,
        }

    def reiniciar_estadisticas(self) -> None:
        """Reinicia contadores de estadísticas."""
        self._request_count = 0
        self._token_count = 0
        self._error_count = 0
        self._last_request_time = None
        logger.info(f"Estadísticas de {self.__class__.__name__} reiniciadas")

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"requests={self._request_count}, "
            f"tokens={self._token_count}, "
            f"errors={self._error_count})"
        )
