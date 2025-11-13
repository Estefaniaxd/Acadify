"""Enums para el sistema de videollamadas.

Define los valores permitidos para estados, tipos y calidades
usando Python Enums para type-safety y prevención de errores.

Principios aplicados:
- Type Safety: Previene valores inválidos en compile-time
- Single Source of Truth: Definición centralizada de valores válidos
- Self-documenting: Nombres descriptivos y docstrings
- Inmutabilidad: Los valores no pueden ser modificados
"""

from enum import Enum


class TipoLlamada(str, Enum):
    """Tipos de llamada soportados.

    Attributes:
        VIDEO: Videollamada con audio y video
        VOZ: Llamada solo de voz (audio únicamente)
    """

    VIDEO = "video"
    VOZ = "voz"

    def __str__(self) -> str:
        return self.value

    @classmethod
    def choices(cls) -> list[str]:
        """Retorna lista de valores válidos."""
        return [item.value for item in cls]


class EstadoVideollamada(str, Enum):
    """Estados posibles de una videollamada.

    Flujo normal: PROGRAMADA → ACTIVA → FINALIZADA
    Flujo alternativo: PROGRAMADA → CANCELADA

    Attributes:
        PROGRAMADA: Llamada agendada pero no iniciada
        ACTIVA: Llamada en curso con participantes conectados
        FINALIZADA: Llamada terminada normalmente
        CANCELADA: Llamada cancelada antes de iniciar o durante ejecución
    """

    PROGRAMADA = "programada"
    ACTIVA = "activa"
    FINALIZADA = "finalizada"
    CANCELADA = "cancelada"

    def __str__(self) -> str:
        return self.value

    @classmethod
    def choices(cls) -> list[str]:
        """Retorna lista de valores válidos."""
        return [item.value for item in cls]

    def puede_transicionar_a(self, nuevo_estado: "EstadoVideollamada") -> bool:
        """Verifica si es válida la transición al nuevo estado.

        Args:
            nuevo_estado: Estado destino

        Returns:
            True si la transición es válida

        Examples:
            >>> EstadoVideollamada.PROGRAMADA.puede_transicionar_a(EstadoVideollamada.ACTIVA)
            True
            >>> EstadoVideollamada.FINALIZADA.puede_transicionar_a(EstadoVideollamada.ACTIVA)
            False
        """
        transiciones_validas = {
            self.PROGRAMADA: {self.ACTIVA, self.CANCELADA},
            self.ACTIVA: {self.FINALIZADA, self.CANCELADA},
            self.FINALIZADA: set(),  # Estado terminal
            self.CANCELADA: set(),  # Estado terminal
        }

        return nuevo_estado in transiciones_validas.get(self, set())


class CalidadConexion(str, Enum):
    """Niveles de calidad de conexión de participantes.

    Basado en métricas de latencia, pérdida de paquetes y jitter.

    Attributes:
        EXCELENTE: < 50ms latencia, < 1% pérdida paquetes
        BUENA: 50-100ms latencia, 1-3% pérdida paquetes
        REGULAR: 100-200ms latencia, 3-5% pérdida paquetes
        MALA: > 200ms latencia, > 5% pérdida paquetes
    """

    EXCELENTE = "excelente"
    BUENA = "buena"
    REGULAR = "regular"
    MALA = "mala"

    def __str__(self) -> str:
        return self.value

    @classmethod
    def choices(cls) -> list[str]:
        """Retorna lista de valores válidos."""
        return [item.value for item in cls]

    @classmethod
    def desde_metricas(
        cls, latencia_ms: float, perdida_paquetes_pct: float
    ) -> "CalidadConexion":
        """Determina la calidad basada en métricas de red.

        Args:
            latencia_ms: Latencia en milisegundos
            perdida_paquetes_pct: Porcentaje de pérdida de paquetes

        Returns:
            Nivel de calidad correspondiente

        Examples:
            >>> CalidadConexion.desde_metricas(30, 0.5)
            <CalidadConexion.EXCELENTE: 'excelente'>
            >>> CalidadConexion.desde_metricas(250, 8)
            <CalidadConexion.MALA: 'mala'>
        """
        if latencia_ms < 50 and perdida_paquetes_pct < 1:
            return cls.EXCELENTE
        if latencia_ms < 100 and perdida_paquetes_pct < 3:
            return cls.BUENA
        if latencia_ms < 200 and perdida_paquetes_pct < 5:
            return cls.REGULAR
        return cls.MALA


class FormatoGrabacion(str, Enum):
    """Formatos de archivo soportados para grabaciones.

    Attributes:
        MP4: MPEG-4 (recomendado, mejor compatibilidad)
        WEBM: WebM (eficiente para web)
        MKV: Matroska (alta calidad)
        AVI: Audio Video Interleave (legacy)
    """

    MP4 = "mp4"
    WEBM = "webm"
    MKV = "mkv"
    AVI = "avi"

    def __str__(self) -> str:
        return self.value

    @classmethod
    def choices(cls) -> list[str]:
        """Retorna lista de valores válidos."""
        return [item.value for item in cls]

    @property
    def mime_type(self) -> str:
        """Retorna el MIME type correspondiente."""
        mime_types = {
            self.MP4: "video/mp4",
            self.WEBM: "video/webm",
            self.MKV: "video/x-matroska",
            self.AVI: "video/x-msvideo",
        }
        return mime_types[self]


class CalidadGrabacion(str, Enum):
    """Niveles de calidad para grabaciones de video.

    Attributes:
        SD: Standard Definition (480p)
        HD: High Definition (720p)
        FHD: Full HD (1080p)
        UHD_4K: Ultra HD 4K (2160p)
    """

    SD = "SD"
    HD = "HD"
    FHD = "FHD"
    UHD_4K = "4K"

    def __str__(self) -> str:
        return self.value

    @classmethod
    def choices(cls) -> list[str]:
        """Retorna lista de valores válidos."""
        return [item.value for item in cls]

    @property
    def resolucion(self) -> tuple[int, int]:
        """Retorna la resolución en píxeles (ancho, alto)."""
        resoluciones = {
            self.SD: (720, 480),
            self.HD: (1280, 720),
            self.FHD: (1920, 1080),
            self.UHD_4K: (3840, 2160),
        }
        return resoluciones[self]

    @property
    def bitrate_recomendado_kbps(self) -> int:
        """Retorna el bitrate recomendado en kbps."""
        bitrates = {
            self.SD: 1000,
            self.HD: 2500,
            self.FHD: 5000,
            self.UHD_4K: 15000,
        }
        return bitrates[self]


class EstadoProcesamiento(str, Enum):
    """Estados del procesamiento de grabaciones.

    Flujo: PENDIENTE → PROCESANDO → COMPLETADO
    Alternativo: PENDIENTE/PROCESANDO → ERROR

    Attributes:
        PENDIENTE: Grabación subida, esperando procesamiento
        PROCESANDO: Procesamiento en curso (codificación, thumbnails, etc.)
        COMPLETADO: Procesamiento exitoso, listo para usar
        ERROR: Error durante procesamiento
    """

    PENDIENTE = "pendiente"
    PROCESANDO = "procesando"
    COMPLETADO = "completado"
    ERROR = "error"

    def __str__(self) -> str:
        return self.value

    @classmethod
    def choices(cls) -> list[str]:
        """Retorna lista de valores válidos."""
        return [item.value for item in cls]

    @property
    def es_final(self) -> bool:
        """Indica si es un estado terminal (no cambiará)."""
        return self in {self.COMPLETADO, self.ERROR}

    @property
    def es_exitoso(self) -> bool:
        """Indica si el procesamiento fue exitoso."""
        return self == self.COMPLETADO


# Exports para fácil importación
__all__ = [
    "CalidadConexion",
    "CalidadGrabacion",
    "EstadoProcesamiento",
    "EstadoVideollamada",
    "FormatoGrabacion",
    "TipoLlamada",
]
