"""
Configuración para servicios de IA (Google Gemini).

Este módulo centraliza toda la configuración relacionada con servicios de IA,
incluyendo modelos, límites, costos y parámetros de generación.

Author: Gemini AI Assistant
Date: 31 octubre 2025
"""

from typing import Dict, List, Optional
from pydantic import BaseModel, Field, validator
from enum import Enum
import os


class GeminiModel(str, Enum):
    """
    Modelos de Gemini disponibles.
    
    Referencia: https://ai.google.dev/models/gemini
    """
    FLASH_2_5 = "gemini-2.5-flash"  # Rápido y eficiente (recomendado)
    PRO_2_5 = "gemini-2.5-pro"      # Más preciso, con costo
    FLASH_2_0 = "gemini-2.0-flash"  # Versión anterior, estable
    FLASH_LATEST = "gemini-flash-latest"  # Siempre la última versión


class SafetyLevel(str, Enum):
    """
    Niveles de filtrado de contenido de seguridad.
    """
    BLOCK_NONE = "BLOCK_NONE"
    BLOCK_ONLY_HIGH = "BLOCK_ONLY_HIGH"
    BLOCK_MEDIUM_AND_ABOVE = "BLOCK_MEDIUM_AND_ABOVE"
    BLOCK_LOW_AND_ABOVE = "BLOCK_LOW_AND_ABOVE"


class AIConfig(BaseModel):
    """
    Configuración completa para servicios de IA.
    
    Esta clase usa Pydantic para validación robusta de configuración.
    Se puede cargar desde variables de entorno o archivo .env
    """
    
    # ==================== API Configuration ====================
    
    api_key: str = Field(
        default_factory=lambda: os.getenv("GEMINI_API_KEY", ""),
        description="API Key de Google Gemini (obligatoria)"
    )
    
    model: GeminiModel = Field(
        default=GeminiModel.FLASH_2_5,
        description="Modelo de Gemini a utilizar"
    )
    
    # ==================== Generation Parameters ====================
    
    temperature: float = Field(
        default=0.7,
        ge=0.0,
        le=2.0,
        description="Creatividad (0=determinístico, 2=muy creativo)"
    )
    
    top_p: float = Field(
        default=0.95,
        ge=0.0,
        le=1.0,
        description="Nucleus sampling (diversidad de tokens)"
    )
    
    top_k: int = Field(
        default=40,
        ge=1,
        le=100,
        description="Número de tokens candidatos a considerar"
    )
    
    max_output_tokens: int = Field(
        default=8192,
        ge=1,
        le=8192,
        description="Máximo de tokens en respuesta (Gemini 1.5 Flash: max 8192)"
    )
    
    # ==================== Safety Settings ====================
    
    safety_level: SafetyLevel = Field(
        default=SafetyLevel.BLOCK_MEDIUM_AND_ABOVE,
        description="Nivel de filtrado de contenido peligroso"
    )
    
    # ==================== Rate Limiting ====================
    
    max_requests_per_minute: int = Field(
        default=15,
        ge=1,
        description="Límite de requests por minuto (plan gratuito: 15 RPM)"
    )
    
    max_tokens_per_minute: int = Field(
        default=1_000_000,
        ge=1000,
        description="Límite de tokens por minuto (plan gratuito: 1M TPM)"
    )
    
    max_requests_per_day: int = Field(
        default=1500,
        ge=1,
        description="Límite de requests por día (plan gratuito: 1500 RPD)"
    )
    
    # ==================== Retry Configuration ====================
    
    max_retries: int = Field(
        default=3,
        ge=0,
        le=5,
        description="Número máximo de reintentos en caso de error"
    )
    
    retry_delay_seconds: float = Field(
        default=2.0,
        ge=0.5,
        le=30.0,
        description="Tiempo de espera entre reintentos (segundos)"
    )
    
    exponential_backoff: bool = Field(
        default=True,
        description="Usar backoff exponencial para reintentos (2s, 4s, 8s...)"
    )
    
    # ==================== Timeout Configuration ====================
    
    request_timeout_seconds: int = Field(
        default=60,
        ge=5,
        le=300,
        description="Timeout para requests a la API (segundos)"
    )
    
    # ==================== File Processing ====================
    
    supported_file_types: List[str] = Field(
        default=[
            "application/pdf",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",  # .docx
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",  # .xlsx
            "application/vnd.openxmlformats-officedocument.presentationml.presentation",  # .pptx
            "text/plain",
            "text/markdown",
            "text/csv",
            "image/jpeg",
            "image/png",
            "image/webp",
            "application/x-python-code",
            "text/x-python",
            "text/javascript",
            "application/json"
        ],
        description="Tipos MIME de archivos soportados por Gemini"
    )
    
    max_file_size_mb: int = Field(
        default=20,
        ge=1,
        le=50,
        description="Tamaño máximo de archivo (MB)"
    )
    
    # ==================== Caching Configuration ====================
    
    enable_response_cache: bool = Field(
        default=True,
        description="Cachear respuestas para prompts idénticos"
    )
    
    cache_ttl_seconds: int = Field(
        default=3600,  # 1 hora
        ge=60,
        description="Tiempo de vida del caché (segundos)"
    )
    
    # ==================== Logging ====================
    
    log_prompts: bool = Field(
        default=True,
        description="Guardar prompts enviados (útil para debugging)"
    )
    
    log_responses: bool = Field(
        default=True,
        description="Guardar respuestas de IA (útil para auditoría)"
    )
    
    log_tokens_usage: bool = Field(
        default=True,
        description="Registrar uso de tokens para tracking de costos"
    )
    
    # ==================== Validators ====================
    
    @validator("api_key")
    def validate_api_key(cls, v):
        """Valida que la API key no esté vacía."""
        if not v or v.strip() == "":
            raise ValueError(
                "GEMINI_API_KEY no configurada. "
                "Obtén tu API key en: https://makersuite.google.com/app/apikey"
            )
        return v.strip()
    
    @validator("temperature")
    def validate_temperature(cls, v):
        """
        Valida temperatura según mejores prácticas:
        - 0.0-0.3: Tareas determinísticas (corrección código, calificación)
        - 0.4-0.7: Balance creatividad/precisión (retroalimentación)
        - 0.8-2.0: Tareas creativas (sugerencias, ideas)
        """
        return round(v, 2)
    
    class Config:
        """Configuración de Pydantic."""
        use_enum_values = True
        validate_assignment = True
        
    def get_generation_config(self) -> Dict:
        """
        Retorna configuración formateada para google.generativeai.
        
        Returns:
            Dict con parámetros de generación compatible con Gemini API
        """
        return {
            "temperature": self.temperature,
            "top_p": self.top_p,
            "top_k": self.top_k,
            "max_output_tokens": self.max_output_tokens,
        }
    
    def get_safety_settings(self) -> List[Dict]:
        """
        Retorna configuración de seguridad formateada para Gemini API.
        
        Returns:
            Lista de configuraciones de seguridad por categoría
        """
        categories = [
            "HARM_CATEGORY_HARASSMENT",
            "HARM_CATEGORY_HATE_SPEECH",
            "HARM_CATEGORY_SEXUALLY_EXPLICIT",
            "HARM_CATEGORY_DANGEROUS_CONTENT",
        ]
        
        return [
            {"category": cat, "threshold": self.safety_level}
            for cat in categories
        ]


# ==================== Instancia Global ====================

# Configuración por defecto (se puede sobrescribir en main.py)
ai_config = AIConfig()


# ==================== Costos de Referencia ====================

GEMINI_PRICING = {
    "gemini-1.5-flash": {
        "free_tier": {
            "requests_per_minute": 15,
            "tokens_per_minute": 1_000_000,
            "requests_per_day": 1500,
        },
        "paid_tier": {
            "input_per_1m_tokens": 0.075,  # USD
            "output_per_1m_tokens": 0.30,   # USD
            "requests_per_minute": 2000,
        }
    },
    "gemini-1.5-pro": {
        "free_tier": {
            "requests_per_minute": 2,
            "tokens_per_minute": 32_000,
            "requests_per_day": 50,
        },
        "paid_tier": {
            "input_per_1m_tokens": 1.25,   # USD
            "output_per_1m_tokens": 5.00,   # USD
            "requests_per_minute": 1000,
        }
    }
}


# ==================== Prompts del Sistema ====================

SYSTEM_PROMPTS = {
    "retroalimentacion_base": """Eres un asistente educativo experto que analiza trabajos académicos de estudiantes.

Tu objetivo es proporcionar retroalimentación constructiva, específica y accionable que ayude al estudiante a mejorar.

PRINCIPIOS CLAVE:
1. **Constructivo**: Enfócate en cómo mejorar, no solo en errores
2. **Específico**: Señala líneas/secciones exactas con ejemplos concretos
3. **Balanceado**: Reconoce fortalezas Y áreas de mejora
4. **Accionable**: Da pasos claros que el estudiante puede seguir
5. **Educativo**: Explica el "por qué" detrás de tus sugerencias

FORMATO DE RESPUESTA:
Debes responder SIEMPRE en formato JSON válido con la siguiente estructura:
{
  "analisis_general": "Resumen ejecutivo del trabajo (2-3 párrafos)",
  "fortalezas": ["Aspecto positivo 1", "Aspecto positivo 2", ...],
  "areas_mejora": ["Área 1 que necesita trabajo", "Área 2", ...],
  "sugerencias_especificas": [
    {
      "ubicacion": "Línea 5 / Sección Introducción / Página 2",
      "problema": "Descripción del problema encontrado",
      "sugerencia": "Cómo mejorarlo",
      "ejemplo": "Código/texto ejemplo de solución"
    }
  ],
  "nivel_cumplimiento": "Porcentaje de cumplimiento general (ej: 85%)",
  "cumple_rubrica": {
    "Criterio1": {"puntos": 4.5, "comentario": "Explicación"},
    "Criterio2": {"puntos": 3.8, "comentario": "Explicación"}
  },
  "puntos_clave_missing": ["Concepto faltante 1", "Concepto 2"],
  "recursos_recomendados": [
    {"titulo": "Nombre del recurso", "url": "https://...", "descripcion": "Por qué es útil"}
  ]
}

NO INCLUYAS markdown ni código fuera del JSON. Solo JSON válido.
""",
    
    "calificacion_codigo": """Al calificar código, evalúa:

1. **Funcionalidad**: ¿El código hace lo que se pidió?
2. **Calidad**: ¿Es legible, mantenible, sigue buenas prácticas?
3. **Eficiencia**: ¿Usa algoritmos/estructuras de datos apropiadas?
4. **Manejo de errores**: ¿Valida inputs, maneja excepciones?
5. **Documentación**: ¿Tiene comentarios, docstrings útiles?
6. **Estilo**: ¿Sigue convenciones del lenguaje (PEP8, etc.)?
""",
    
    "calificacion_ensayo": """Al calificar ensayos/documentos, evalúa:

1. **Contenido**: Profundidad, precisión, relevancia de ideas
2. **Estructura**: Organización lógica, flujo de argumentos
3. **Argumentación**: Evidencia, ejemplos, razonamiento crítico
4. **Redacción**: Claridad, gramática, ortografía, estilo
5. **Fuentes**: Uso y citación adecuada de referencias
6. **Originalidad**: Pensamiento propio vs. paráfrasis/copia
"""
}
