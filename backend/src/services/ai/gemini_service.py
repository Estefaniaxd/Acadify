"""Servicio de retroalimentación con IA usando Google Gemini.

Este es el servicio principal que integra toda la funcionalidad de análisis
con IA para proporcionar retroalimentación educativa de alta calidad.

Author: Gemini AI Assistant
Date: 31 octubre 2025
Version: 1.0.0

Características:
- Análisis inteligente de trabajos académicos
- Soporte multi-formato (PDF, Word, Excel, código, imágenes)
- Retroalimentación estructurada y accionable
- Calificación automática sugerida
- Rate limiting inteligente
- Tracking de costos y tokens
- Manejo robusto de errores
- Logging completo

Uso:
    >>> service = GeminiService(api_key="tu_api_key")
    >>> await service.inicializar()
    >>> retroalimentacion = await service.generar_retroalimentacion(entrega, tarea)
"""

import asyncio
from datetime import datetime
import logging
import time
from typing import Any, BinaryIO


# Google Generative AI
try:
    import google.generativeai as genai

    HAS_GENAI = True
except ImportError:
    HAS_GENAI = False

from src.models.academic.tarea import EntregaTarea, Tarea
from src.services.ai.base import BaseAIService
from src.services.ai.config import AIConfig, ai_config
from src.services.ai.exceptions import (
    AIServiceException,
    ConfigurationError,
    FileProcessingError,
    GeminiAPIError,
    RateLimitExceededError,
    ResponseParsingError,
)
from src.services.ai.helpers import (
    CostTracker,
    FileProcessor,
    PromptBuilder,
    ResponseParser,
)


logger = logging.getLogger(__name__)


class GeminiService(BaseAIService):
    """Servicio de retroalimentación con IA usando Google Gemini 1.5 Flash.

    Este servicio implementa la interfaz BaseAIService y proporciona
    análisis completo de trabajos académicos con retroalimentación
    estructurada, calificación sugerida y seguimiento de uso.

    Attributes:
        config: Configuración del servicio (AIConfig)
        model: Instancia del modelo de Gemini
        cost_tracker: Rastreador de uso y costos
        _rate_limiter: Datos para rate limiting

    Example:
        >>> service = GeminiService()
        >>> await service.inicializar()
        >>>
        >>> # Procesar archivo
        >>> archivo = open("tarea.py", "rb")
        >>> contenido = FileProcessor.extraer_contenido(
        ...     archivo, "tarea.py", "text/x-python"
        ... )
        >>>
        >>> # Generar retroalimentación
        >>> resultado = await service.generar_retroalimentacion(
        ...     entrega=entrega_obj,
        ...     tarea=tarea_obj,
        ...     archivo_contenido=contenido
        ... )
        >>>
        >>> print(resultado["analisis_general"])
        >>> print(f"Calificación sugerida: {resultado['calificacion_sugerida']}")
    """

    def __init__(
        self, api_key: str | None = None, config: AIConfig | None = None
    ) -> None:
        """Inicializa el servicio de Gemini.

        Args:
            api_key: API Key de Google Gemini (opcional, se lee de config)
            config: Configuración personalizada (opcional, usa default)

        Raises:
            ConfigurationError: Si la configuración es inválida
        """
        # Configuración
        if config:
            self.ai_config = config
        else:
            self.ai_config = ai_config

        # Sobrescribir API key si se proporciona
        if api_key:
            self.ai_config.api_key = api_key

        # Validar que google.generativeai esté instalado
        if not HAS_GENAI:
            msg = (
                "google-generativeai no instalado. "
                "Instala con: pip install google-generativeai"
            )
            raise ConfigurationError(msg)

        # Inicializar clase base con dict
        super().__init__(config=self.ai_config.dict())

        # Instancias auxiliares
        self.file_processor = FileProcessor()
        self.prompt_builder = PromptBuilder()
        self.response_parser = ResponseParser()
        self.cost_tracker = CostTracker(modelo=str(self.ai_config.model))

        # Rate limiting
        self._rate_limiter = {
            "requests_ultimo_minuto": [],
            "tokens_ultimo_minuto": 0,
            "requests_hoy": 0,
            "ultimo_reset_diario": datetime.utcnow().date(),
        }

        # Modelo (se inicializa en inicializar())
        self.model = None

        logger.info(f"GeminiService inicializado con modelo {self.ai_config.model}")

    async def inicializar(self) -> bool:
        """Inicializa la conexión con Gemini API.

        Este método debe llamarse antes de usar el servicio.
        Configura la API key y crea la instancia del modelo.

        Returns:
            bool: True si la inicialización fue exitosa

        Raises:
            ConfigurationError: Si la API key es inválida
        """
        try:
            # Configurar API key
            genai.configure(api_key=self.ai_config.api_key)

            # Crear modelo
            self.model = genai.GenerativeModel(
                model_name=self.ai_config.model,
                generation_config=self.ai_config.get_generation_config(),
                safety_settings=self.ai_config.get_safety_settings(),
            )

            # Verificar conectividad (opcional pero recomendado)
            if await self.verificar_disponibilidad():
                self._initialized = True
                logger.info("✅ Gemini API inicializada correctamente")
                return True
            msg = "No se pudo verificar la API de Gemini"
            raise ConfigurationError(msg)

        except Exception as e:
            logger.exception(f"Error inicializando Gemini API: {e!s}")
            msg = f"Error al inicializar Gemini: {e!s}"
            raise ConfigurationError(msg, config_key="api_key") from e

    async def generar_retroalimentacion(
        self,
        entrega: EntregaTarea,
        tarea: Tarea,
        archivo_contenido: str | None = None,
        archivo_binario: BinaryIO | None = None,
        opciones: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Genera retroalimentación completa para una entrega.

        Este es el método principal del servicio. Procesa el archivo del
        estudiante, construye un prompt contextualizado, consulta a Gemini
        y retorna retroalimentación estructurada.

        Args:
            entrega: Instancia de EntregaTarea con la entrega del estudiante
            tarea: Instancia de Tarea con instrucciones y rúbrica
            archivo_contenido: Contenido ya extraído (opcional)
            archivo_binario: Stream del archivo para procesar (opcional)
            opciones: Parámetros adicionales:
                - include_calificacion: bool (default True)
                - temperature: float (override config)
                - max_tokens: int (override config)

        Returns:
            Dict con estructura completa de retroalimentación:
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
                "recursos_recomendados": [...],
                "calificacion_sugerida": 4.2,
                "metadata": {...}
            }

        Raises:
            AIServiceException: Error general del servicio
            RateLimitExceededError: Límites de tasa excedidos
            FileProcessingError: Error procesando archivo
            ResponseParsingError: Error parseando respuesta
        """
        if not self._initialized:
            msg = "Servicio no inicializado. Llama await service.inicializar() primero"
            raise ConfigurationError(msg)

        opciones = opciones or {}
        inicio = time.time()

        # ==================== Paso 1: Extraer contenido ====================

        if archivo_contenido is None:
            if archivo_binario is None:
                msg = "Debe proporcionar archivo_contenido o archivo_binario"
                raise FileProcessingError(msg)

            # Extraer contenido del archivo
            logger.info(
                f"Extrayendo contenido de archivo para entrega {entrega.entrega_id}"
            )

            try:
                archivo_contenido = self.file_processor.extraer_contenido(
                    archivo=archivo_binario,
                    nombre_archivo=(
                        entrega.archivo_metadata.get("nombre", "archivo")
                        if entrega.archivo_metadata
                        else "archivo"
                    ),
                    mime_type=(
                        entrega.archivo_metadata.get("mime_type")
                        if entrega.archivo_metadata
                        else None
                    ),
                )
            except Exception as e:
                self.registrar_error(e)
                raise

        # ==================== Paso 2: Validar contenido ====================

        logger.debug("Validando contenido para análisis")

        validacion = await self.validar_contenido(
            contenido=archivo_contenido,
            tipo_archivo=(
                entrega.archivo_metadata.get("mime_type", "text/plain")
                if entrega.archivo_metadata
                else "text/plain"
            ),
        )

        if not validacion["valido"]:
            msg = f"Contenido no válido: {', '.join(validacion['razones'])}"
            raise FileProcessingError(msg)

        # ==================== Paso 3: Rate Limiting ====================

        await self._verificar_rate_limits()

        # ==================== Paso 4: Construir prompt ====================

        logger.debug("Construyendo prompt contextualizado")

        prompt = self.prompt_builder.construir_prompt_retroalimentacion(
            tarea=tarea,
            entrega=entrega,
            contenido=archivo_contenido,
            prompt_personalizado=tarea.prompt_ia_personalizado,
        )

        # Validar longitud del prompt
        tokens_estimados = self.estimar_tokens(prompt)
        if tokens_estimados > 30000:  # Límite conservador
            logger.warning(
                f"Prompt muy largo ({tokens_estimados} tokens), acortando contenido"
            )
            archivo_contenido = self.prompt_builder.acortar_contenido_si_necesario(
                archivo_contenido, max_tokens=25000
            )
            # Reconstruir prompt con contenido acortado
            prompt = self.prompt_builder.construir_prompt_retroalimentacion(
                tarea=tarea,
                entrega=entrega,
                contenido=archivo_contenido,
                prompt_personalizado=tarea.prompt_ia_personalizado,
            )

        # ==================== Paso 5: Llamar a Gemini API ====================

        logger.info(
            f"Generando retroalimentación con Gemini para entrega {entrega.entrega_id}"
        )

        try:
            # Aplicar overrides de opciones si existen
            generation_config = self.ai_config.get_generation_config()
            if "temperature" in opciones:
                generation_config["temperature"] = opciones["temperature"]
            if "max_tokens" in opciones:
                generation_config["max_output_tokens"] = opciones["max_tokens"]

            # Llamada a la API (con retry automático)
            respuesta = await self._llamar_api_con_retry(
                prompt=prompt,
                generation_config=generation_config,
                max_retries=self.ai_config.max_retries,
            )

            # Extraer texto de respuesta
            texto_respuesta = respuesta.text

            # Extraer metadata
            metadata_respuesta = self.response_parser.extraer_metadata(respuesta)

        except Exception as e:
            self.registrar_error(e)
            if isinstance(e, AIServiceException):
                raise
            msg = f"Error llamando a Gemini API: {e!s}"
            raise GeminiAPIError(msg) from e

        # ==================== Paso 6: Parsear respuesta ====================

        logger.debug("Parseando respuesta de IA")

        try:
            # Sanitizar y extraer JSON
            texto_limpio = self.response_parser.sanitizar_respuesta(texto_respuesta)
            datos_json = self.response_parser.extraer_json(texto_limpio)

            # Validar estructura
            retroalimentacion = (
                self.response_parser.validar_estructura_retroalimentacion(datos_json)
            )

        except ResponseParsingError as e:
            self.registrar_error(e)
            logger.exception(f"Error parseando respuesta: {e!s}")
            raise

        # ==================== Paso 7: Calcular calificación (opcional) ====================

        calificacion_sugerida = None

        if opciones.get("include_calificacion", True) and tarea.rubrica:
            try:
                logger.debug("Calculando calificación sugerida")
                calificacion_sugerida = await self.calcular_calificacion_sugerida(
                    entrega=entrega, tarea=tarea, retroalimentacion=retroalimentacion
                )
            except Exception as e:
                logger.warning(f"No se pudo calcular calificación: {e!s}")
                # No es crítico, continuar sin calificación

        # ==================== Paso 8: Consolidar resultado ====================

        duracion = time.time() - inicio

        # Registrar uso
        self.registrar_request(tokens_usados=metadata_respuesta.get("tokens_total", 0))
        self.cost_tracker.registrar_uso(
            tokens_input=metadata_respuesta.get("tokens_prompt", 0),
            tokens_output=metadata_respuesta.get("tokens_completion", 0),
            duracion_segundos=duracion,
            metadata={
                "entrega_id": str(entrega.entrega_id),
                "tarea_id": str(tarea.tarea_id),
                "estudiante_id": str(entrega.estudiante_id),
            },
        )

        resultado_final = {
            "timestamp": datetime.utcnow().isoformat(),
            "modelo_usado": self.ai_config.model,
            **retroalimentacion,
            "calificacion_sugerida": calificacion_sugerida,
            "metadata": {
                "duracion_segundos": round(duracion, 2),
                "tokens_prompt": metadata_respuesta.get("tokens_prompt", 0),
                "tokens_completion": metadata_respuesta.get("tokens_completion", 0),
                "tokens_total": metadata_respuesta.get("tokens_total", 0),
                "finish_reason": metadata_respuesta.get("finish_reason"),
                "version_servicio": "1.0.0",
            },
        }

        logger.info(
            f"✅ Retroalimentación generada exitosamente en {duracion:.2f}s "
            f"({metadata_respuesta.get('tokens_total', 0)} tokens)"
        )

        # Verificar alertas de límites
        alerta = self.cost_tracker.generar_alerta_limites()
        if alerta:
            logger.warning(f"Alerta de límites:\n{alerta}")

        return resultado_final

    async def calcular_calificacion_sugerida(
        self, entrega: EntregaTarea, tarea: Tarea, retroalimentacion: dict[str, Any]
    ) -> float:
        """Calcula calificación sugerida basada en retroalimentación.

        Args:
            entrega: Instancia de EntregaTarea
            tarea: Instancia de Tarea con rúbrica
            retroalimentacion: Dict con retroalimentación ya generada

        Returns:
            float: Calificación sugerida (0.0 - 5.0)
        """
        if not self._initialized:
            msg = "Servicio no inicializado"
            raise ConfigurationError(msg)

        # Construir prompt para calificación
        prompt = self.prompt_builder.construir_prompt_calificacion(
            tarea=tarea, retroalimentacion=retroalimentacion
        )

        try:
            # Llamar a API
            respuesta = await self._llamar_api_con_retry(
                prompt=prompt,
                generation_config={
                    "temperature": 0.2,  # Más determinístico para calificación
                    "max_output_tokens": 500,  # Respuesta corta
                },
                max_retries=2,
            )

            # Parsear respuesta
            datos = self.response_parser.extraer_json(respuesta.text)
            resultado = self.response_parser.validar_estructura_calificacion(datos)

            calificacion = resultado["calificacion"]

            logger.info(
                f"Calificación sugerida: {calificacion}/5.0 - "
                f"{resultado.get('justificacion', '')[:50]}..."
            )

            return calificacion

        except Exception as e:
            logger.exception(f"Error calculando calificación: {e!s}")
            # Fallback: calcular a partir de cumple_rubrica
            return self._calcular_calificacion_fallback(retroalimentacion)

    def _calcular_calificacion_fallback(
        self, retroalimentacion: dict[str, Any]
    ) -> float:
        """Calcula calificación como fallback si falla el método principal.

        Args:
            retroalimentacion: Dict con retroalimentación

        Returns:
            float: Calificación promedio de criterios de rúbrica
        """
        cumple_rubrica = retroalimentacion.get("cumple_rubrica", {})

        if not cumple_rubrica:
            # Parsear nivel_cumplimiento
            nivel_str = retroalimentacion.get("nivel_cumplimiento", "0%")
            porcentaje = float(nivel_str.replace("%", "")) / 100
            return round(porcentaje * 5.0, 1)

        # Promediar puntos de criterios
        puntos = [
            float(criterio.get("puntos", 0))
            for criterio in cumple_rubrica.values()
            if isinstance(criterio, dict) and "puntos" in criterio
        ]

        if puntos:
            return round(sum(puntos) / len(puntos), 1)

        return 0.0

    async def validar_contenido(
        self, contenido: str, tipo_archivo: str
    ) -> dict[str, Any]:
        """Valida que el contenido sea apropiado para análisis.

        Args:
            contenido: Contenido a validar
            tipo_archivo: MIME type del archivo

        Returns:
            Dict con resultado: {"valido": bool, "razones": [...], ...}
        """
        razones = []
        advertencias = []

        # Validación básica
        if not contenido or len(contenido.strip()) == 0:
            razones.append("El contenido está vacío")

        if len(contenido) < 50:
            advertencias.append("El contenido es muy corto (<50 caracteres)")

        if len(contenido) > 1_000_000:  # 1MB de texto
            razones.append("El contenido es demasiado largo (>1MB)")

        # Detectar si es contenido binario corrupto
        caracteres_raros = sum(
            1 for c in contenido[:1000] if ord(c) < 32 and c not in "\n\r\t"
        )
        if caracteres_raros > 50:
            razones.append("El contenido parece estar corrupto o ser binario")

        return {
            "valido": len(razones) == 0,
            "razones": razones,
            "advertencias": advertencias,
            "tipo_detectado": tipo_archivo,
        }

    def estimar_tokens(self, texto: str) -> int:
        """Estima el número de tokens en un texto.

        Args:
            texto: Texto a analizar

        Returns:
            int: Número estimado de tokens
        """
        # Estimación conservadora: 1.3 tokens por palabra
        # (Gemini usa tokenización similar a GPT)
        palabras = len(texto.split())
        return int(palabras * 1.3)

    async def verificar_disponibilidad(self) -> bool:
        """Verifica que el servicio esté disponible y configurado correctamente.

        Returns:
            bool: True si el servicio está operacional
        """
        try:
            # Simplemente verificar que el modelo existe y está configurado
            if self.model is not None:
                logger.info("✅ Modelo Gemini configurado correctamente")
                return True
            logger.error("❌ Modelo no inicializado")
            return False

        except Exception as e:
            logger.exception(f"Verificación de disponibilidad falló: {e!s}")
            return False

    # ==================== Métodos Privados ====================

    async def _llamar_api_con_retry(
        self, prompt: str, generation_config: dict[str, Any], max_retries: int = 3
    ):
        """Llama a la API de Gemini con retry automático en caso de error.

        Args:
            prompt: Prompt a enviar
            generation_config: Configuración de generación
            max_retries: Número máximo de reintentos

        Returns:
            Respuesta de la API

        Raises:
            GeminiAPIError: Si falla después de todos los reintentos
        """
        ultimo_error = None

        for intento in range(max_retries):
            try:
                # Hacer la llamada
                return self.model.generate_content(
                    prompt, generation_config=generation_config
                )

                # Si llegamos aquí, fue exitoso

            except Exception as e:
                ultimo_error = e
                error_str = str(e).lower()

                # Manejar errores específicos
                if "429" in error_str or "rate limit" in error_str:
                    # Rate limit excedido
                    retry_after = self.ai_config.retry_delay_seconds * (
                        2**intento if self.ai_config.exponential_backoff else 1
                    )

                    if intento < max_retries - 1:
                        logger.warning(
                            f"Rate limit excedido, reintentando en {retry_after}s "
                            f"(intento {intento + 1}/{max_retries})"
                        )
                        await asyncio.sleep(retry_after)
                        continue
                    raise RateLimitExceededError(retry_after=int(retry_after)) from e

                if "content filter" in error_str or "blocked" in error_str:
                    # Contenido bloqueado por filtros
                    from src.services.ai.exceptions import ContentFilterError

                    raise ContentFilterError(blocked_reason=error_str) from None

                if intento < max_retries - 1:
                    # Otros errores: reintentar con backoff
                    delay = self.ai_config.retry_delay_seconds * (
                        2**intento if self.ai_config.exponential_backoff else 1
                    )
                    logger.warning(f"Error en API, reintentando en {delay}s: {e!s}")
                    await asyncio.sleep(delay)
                    continue

        # Si llegamos aquí, fallaron todos los reintentos
        msg = f"Falló después de {max_retries} reintentos: {ultimo_error!s}"
        raise GeminiAPIError(msg)

    async def _verificar_rate_limits(self) -> None:
        """Verifica y aplica rate limiting antes de hacer un request.

        Raises:
            RateLimitExceededError: Si se exceden los límites
        """
        now = datetime.utcnow()

        # Limpiar requests antiguos (> 1 minuto)
        self._rate_limiter["requests_ultimo_minuto"] = [
            ts
            for ts in self._rate_limiter["requests_ultimo_minuto"]
            if (now - ts).total_seconds() < 60
        ]

        # Reset diario
        if now.date() > self._rate_limiter["ultimo_reset_diario"]:
            self._rate_limiter["requests_hoy"] = 0
            self._rate_limiter["ultimo_reset_diario"] = now.date()

        # Verificar límites
        if (
            len(self._rate_limiter["requests_ultimo_minuto"])
            >= self.ai_config.max_requests_per_minute
        ):
            msg = "Límite de requests por minuto excedido"
            raise RateLimitExceededError(msg, retry_after=60)

        if self._rate_limiter["requests_hoy"] >= self.ai_config.max_requests_per_day:
            msg = "Límite de requests por día excedido"
            raise RateLimitExceededError(msg, retry_after=3600)

        # Registrar este request
        self._rate_limiter["requests_ultimo_minuto"].append(now)
        self._rate_limiter["requests_hoy"] += 1

    def get_cost_tracker(self) -> CostTracker:
        """Retorna el tracker de costos para análisis externo."""
        return self.cost_tracker

    def __repr__(self) -> str:
        return (
            f"GeminiService(modelo={self.ai_config.model}, "
            f"inicializado={self._initialized}, "
            f"requests={self._request_count})"
        )
