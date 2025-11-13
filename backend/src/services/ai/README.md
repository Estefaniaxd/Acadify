# 🤖 Sistema de Retroalimentación con IA - GeminiService

Sistema de análisis inteligente de trabajos académicos usando **Google Gemini 1.5 Flash**, diseñado para proporcionar retroalimentación educativa estructurada, específica y accionable.

## 📋 Tabla de Contenidos

- [Características](#-características)
- [Arquitectura](#-arquitectura)
- [Instalación](#-instalación)
- [Configuración](#-configuración)
- [Uso Básico](#-uso-básico)
- [API Completa](#-api-completa)
- [Formatos Soportados](#-formatos-soportados)
- [Estructura de Retroalimentación](#-estructura-de-retroalimentación)
- [Límites y Costos](#-límites-y-costos)
- [Testing](#-testing)
- [Troubleshooting](#-troubleshooting)

---

## ✨ Características

### 🎯 Funcionalidad Principal

- ✅ **Análisis Inteligente**: Retroalimentación estructurada basada en rúbricas
- ✅ **Multi-Formato**: Soporta PDF, Word, Excel, PowerPoint, código, imágenes
- ✅ **Calificación Automática**: Sugerencia de calificación (0-5) con justificación
- ✅ **Rúbricas Personalizadas**: Evaluación según criterios definidos por docentes
- ✅ **Retroalimentación Específica**: Sugerencias con ubicación, problema y ejemplo
- ✅ **Recursos Educativos**: Recomendaciones de materiales de aprendizaje

### 🔧 Características Técnicas

- ✅ **Arquitectura SOLID**: Abstracción con `BaseAIService` (DIP)
- ✅ **Rate Limiting**: Control automático de límites por minuto/día
- ✅ **Cost Tracking**: Seguimiento de tokens y costos en tiempo real
- ✅ **Retry Automático**: Reintentos con exponential backoff
- ✅ **Logging Completo**: Trazabilidad de todas las operaciones
- ✅ **Manejo de Errores**: 8 excepciones personalizadas
- ✅ **Async/Await**: Operaciones asíncronas para alto rendimiento
- ✅ **Type Hints**: Documentación de tipos completa
- ✅ **Validaciones Robustas**: Pydantic para configuración y datos

---

## 🏗️ Arquitectura

```
src/services/ai/
├── gemini_service.py          # ⭐ Servicio principal (1000+ líneas)
├── base.py                     # Interfaz abstracta (SOLID DIP)
├── config.py                   # Configuración con Pydantic
├── exceptions.py               # 8 excepciones personalizadas
├── helpers/
│   ├── file_processor.py       # Procesamiento multi-formato
│   ├── prompt_builder.py       # Construcción inteligente de prompts
│   ├── response_parser.py      # Parseo robusto de respuestas JSON
│   └── cost_tracker.py         # Tracking de tokens y costos
└── __init__.py                 # Exports públicos
```

### 🎨 Principios de Diseño

- **Single Responsibility**: Cada clase tiene una única responsabilidad
- **Open/Closed**: Abierto a extensión (BaseAIService), cerrado a modificación
- **Dependency Inversion**: Depende de abstracciones, no de implementaciones concretas
- **Clean Code**: Nombres descriptivos, funciones pequeñas, documentación exhaustiva
- **Error Handling**: Manejo granular de errores con excepciones específicas

---

## 📦 Instalación

### 1. Instalar Dependencias

```bash
cd backend
pip install -r requirements.txt
```

**Dependencias principales**:
- `google-generativeai==0.8.3` - Google Gemini API
- `PyPDF2==3.0.1` - Procesamiento PDFs
- `python-docx==1.1.2` - Procesamiento Word (.docx)
- `openpyxl==3.1.5` - Procesamiento Excel (.xlsx)
- `python-pptx==1.0.2` - Procesamiento PowerPoint (.pptx)

### 2. Verificar Instalación

```bash
python -c "import google.generativeai as genai; print('✅ Gemini API instalada')"
```

---

## ⚙️ Configuración

### 1. Obtener API Key de Google Gemini

1. Ve a: https://makersuite.google.com/app/apikey
2. Crea o selecciona un proyecto de Google Cloud
3. Genera una API Key
4. Copia la clave

### 2. Configurar Variables de Entorno

Edita `backend/.env`:

```bash
# Google Gemini API
GEMINI_API_KEY=AIzaSy...tu_api_key_aqui...XYZ

# Configuración opcional (valores por defecto)
GEMINI_MODEL=gemini-1.5-flash
GEMINI_TEMPERATURE=0.7
GEMINI_MAX_TOKENS=8192
```

### 3. Configuración Avanzada (Opcional)

Puedes personalizar la configuración con `AIConfig`:

```python
from src.services.ai import AIConfig, GeminiService

config = AIConfig(
    api_key="tu_api_key",
    model="gemini-1.5-flash",
    temperature=0.7,  # 0=determinístico, 2=muy creativo
    max_output_tokens=4096,
    max_requests_per_minute=15,  # Plan gratuito: 15 RPM
    max_tokens_per_minute=1_000_000,  # Plan gratuito: 1M TPM
    max_requests_per_day=1500,  # Plan gratuito: 1500 RPD
    log_prompts=True,
    log_responses=True
)

service = GeminiService(config=config)
```

---

## 🚀 Uso Básico

### Ejemplo Completo

```python
import asyncio
from src.services.ai import GeminiService
from src.models.classes.tarea import Tarea
from src.models.classes.entregar_tarea import EntregarTarea

async def analizar_entrega():
    # 1. Inicializar servicio
    service = GeminiService()
    await service.inicializar()
    
    # 2. Preparar datos
    tarea = Tarea(
        titulo="Implementar algoritmo de ordenamiento",
        descripcion="Implementa QuickSort en Python",
        rubrica={
            "criterios": [
                {"nombre": "Funcionalidad", "peso": 40},
                {"nombre": "Eficiencia", "peso": 30},
                {"nombre": "Código Limpio", "peso": 20},
                {"nombre": "Documentación", "peso": 10}
            ]
        },
        habilitar_retroalimentacion_ia=True
    )
    
    entrega = EntregarTarea(
        tarea_id=tarea.tarea_id,
        estudiante_id=uuid4(),
        archivo_metadata={"nombre": "quicksort.py", "mime_type": "text/x-python"}
    )
    
    codigo = """
def quicksort(arr):
    if len(arr) <= 1:
        return arr
    pivot = arr[len(arr) // 2]
    left = [x for x in arr if x < pivot]
    middle = [x for x in arr if x == pivot]
    right = [x for x in arr if x > pivot]
    return quicksort(left) + middle + quicksort(right)
    
# Uso
numeros = [3, 6, 8, 10, 1, 2, 1]
print(quicksort(numeros))
"""
    
    # 3. Generar retroalimentación
    resultado = await service.generar_retroalimentacion(
        entrega=entrega,
        tarea=tarea,
        archivo_contenido=codigo
    )
    
    # 4. Usar resultados
    print(f"Calificación sugerida: {resultado['calificacion_sugerida']}/5.0")
    print(f"Análisis: {resultado['analisis_general']}")
    print(f"Fortalezas: {resultado['fortalezas']}")
    print(f"Áreas de mejora: {resultado['areas_mejora']}")
    
    # 5. Guardar en base de datos
    entrega.retroalimentacion_ia = resultado
    entrega.calificacion_preliminar_ia = resultado['calificacion_sugerida']
    # ... guardar con SQLAlchemy

asyncio.run(analizar_entrega())
```

### Procesar Archivo desde Disco

```python
from src.services.ai.helpers import FileProcessor

# Extraer contenido
with open("tarea_estudiante.pdf", "rb") as archivo:
    contenido = FileProcessor.extraer_contenido(
        archivo=archivo,
        nombre_archivo="tarea_estudiante.pdf",
        mime_type="application/pdf"
    )

# Generar retroalimentación
resultado = await service.generar_retroalimentacion(
    entrega=entrega,
    tarea=tarea,
    archivo_contenido=contenido
)
```

---

## 📚 API Completa

### `GeminiService`

#### `__init__(api_key, config)`
Inicializa el servicio.

**Parámetros**:
- `api_key` (str, opcional): API Key de Gemini (lee de `.env` si se omite)
- `config` (AIConfig, opcional): Configuración personalizada

#### `async inicializar()`
Inicializa la conexión con Gemini API. **Debe llamarse antes de usar el servicio**.

**Returns**: `bool` - True si la inicialización fue exitosa

**Raises**: `ConfigurationError` si la API key es inválida

#### `async generar_retroalimentacion(entrega, tarea, archivo_contenido, opciones)`
Genera retroalimentación completa para una entrega.

**Parámetros**:
- `entrega` (EntregarTarea): Entrega del estudiante
- `tarea` (Tarea): Tarea con instrucciones y rúbrica
- `archivo_contenido` (str, opcional): Contenido extraído del archivo
- `archivo_binario` (BinaryIO, opcional): Stream del archivo para procesar
- `opciones` (Dict, opcional):
  - `include_calificacion` (bool): Incluir calificación sugerida (default: True)
  - `temperature` (float): Override temperatura (0-2)
  - `max_tokens` (int): Override máximo de tokens

**Returns**: `Dict[str, Any]` - Retroalimentación estructurada completa

**Raises**:
- `AIServiceException` - Error general del servicio
- `RateLimitExceededError` - Límites de tasa excedidos
- `FileProcessingError` - Error procesando archivo
- `ResponseParsingError` - Error parseando respuesta

#### `async calcular_calificacion_sugerida(entrega, tarea, retroalimentacion)`
Calcula calificación numérica basada en retroalimentación.

**Returns**: `float` - Calificación (0.0 - 5.0)

#### `get_cost_tracker()`
Retorna el rastreador de costos para análisis.

**Returns**: `CostTracker`

---

## 📄 Formatos Soportados

| Tipo | Extensiones | MIME Type | Librería |
|------|-------------|-----------|----------|
| **Texto Plano** | `.txt`, `.md` | `text/plain`, `text/markdown` | Built-in |
| **Código** | `.py`, `.js`, `.java`, `.cpp`, `.ts`, etc. | `text/x-python`, `text/javascript`, etc. | Built-in |
| **PDF** | `.pdf` | `application/pdf` | PyPDF2 |
| **Word** | `.docx` | `application/vnd...wordprocessingml.document` | python-docx |
| **Excel** | `.xlsx`, `.csv` | `application/vnd...spreadsheetml.sheet` | openpyxl |
| **PowerPoint** | `.pptx` | `application/vnd...presentationml.presentation` | python-pptx |
| **Imágenes** | `.jpg`, `.png`, `.webp` | `image/jpeg`, `image/png`, etc. | Gemini Vision API |

### Ejemplo: Procesar PDF

```python
from src.services.ai.helpers import FileProcessor

with open("ensayo.pdf", "rb") as f:
    # Validar primero
    validacion = FileProcessor.validar_archivo(f, "ensayo.pdf", max_size_mb=20)
    
    if validacion["valido"]:
        # Extraer contenido
        f.seek(0)
        contenido = FileProcessor.extraer_contenido(f, "ensayo.pdf", "application/pdf")
        print(f"Extraídos {len(contenido)} caracteres")
    else:
        print(f"Archivo inválido: {validacion['razones']}")
```

---

## 📊 Estructura de Retroalimentación

### Respuesta Completa

```json
{
  "timestamp": "2025-10-31T10:30:00Z",
  "modelo_usado": "gemini-1.5-flash",
  
  "analisis_general": "El código implementa correctamente el algoritmo QuickSort...",
  
  "fortalezas": [
    "Implementación correcta y elegante del algoritmo QuickSort",
    "Uso apropiado de list comprehensions para legibilidad",
    "Manejo correcto del caso base (lista vacía o un elemento)"
  ],
  
  "areas_mejora": [
    "Falta validación de tipos de entrada",
    "No hay manejo de casos edge (None, tipos mixtos)",
    "Ausencia de documentación (docstrings)"
  ],
  
  "sugerencias_especificas": [
    {
      "ubicacion": "Línea 2: función quicksort",
      "problema": "No se valida el tipo del parámetro arr",
      "sugerencia": "Agregar validación para asegurar que arr es una lista",
      "ejemplo": "if not isinstance(arr, list):\n    raise TypeError('arr debe ser una lista')"
    },
    {
      "ubicacion": "Línea 1: función quicksort",
      "problema": "Falta documentación de la función",
      "sugerencia": "Agregar docstring explicando parámetros, retorno y complejidad",
      "ejemplo": "def quicksort(arr):\n    \"\"\"\n    Ordena una lista usando QuickSort.\n    \n    Complejidad: O(n log n) promedio, O(n²) peor caso\n    \"\"\""
    }
  ],
  
  "nivel_cumplimiento": "85%",
  
  "cumple_rubrica": {
    "Funcionalidad": {
      "puntos": 5.0,
      "comentario": "Implementación completamente funcional y correcta"
    },
    "Eficiencia": {
      "puntos": 4.5,
      "comentario": "Algoritmo eficiente, podría optimizarse la selección del pivot"
    },
    "Código Limpio": {
      "puntos": 4.0,
      "comentario": "Código legible pero le falta documentación"
    },
    "Documentación": {
      "puntos": 2.0,
      "comentario": "Falta docstring y comentarios explicativos"
    }
  },
  
  "puntos_clave_missing": [
    "Validación de tipos de entrada",
    "Manejo de errores para casos edge",
    "Documentación con docstrings",
    "Tests unitarios"
  ],
  
  "recursos_recomendados": [
    {
      "titulo": "Python Type Hints y Validación",
      "url": "https://docs.python.org/3/library/typing.html",
      "descripcion": "Para mejorar la validación de tipos"
    },
    {
      "titulo": "PEP 257 - Docstring Conventions",
      "url": "https://peps.python.org/pep-0257/",
      "descripcion": "Guía oficial para escribir docstrings en Python"
    }
  ],
  
  "calificacion_sugerida": 4.2,
  
  "metadata": {
    "duracion_segundos": 12.5,
    "tokens_prompt": 850,
    "tokens_completion": 420,
    "tokens_total": 1270,
    "finish_reason": "STOP",
    "version_servicio": "1.0.0"
  }
}
```

---

## 💰 Límites y Costos

### Plan Gratuito de Gemini 1.5 Flash

| Límite | Valor |
|--------|-------|
| **Requests por minuto (RPM)** | 15 |
| **Tokens por minuto (TPM)** | 1,000,000 |
| **Requests por día (RPD)** | 1,500 |
| **Costo** | **Gratis** 🎉 |

### Plan Pagado (Si se excede el gratuito)

| Tipo | Costo |
|------|-------|
| **Input** | $0.075 por 1M tokens |
| **Output** | $0.30 por 1M tokens |

### Tracking de Uso

```python
# Obtener estadísticas
tracker = service.get_cost_tracker()
stats = tracker.obtener_estadisticas(periodo_dias=7)

print(f"Requests totales: {stats['total_requests']}")
print(f"Tokens totales: {stats['total_tokens']:,}")
print(f"Promedio tokens/request: {stats['promedio_tokens_por_request']}")

# Verificar límites
limites = tracker.verificar_limites_plan_gratuito()
print(f"RPM: {limites['requests_este_minuto']}/{limites['limite_rpm']}")
print(f"RPD: {limites['requests_hoy']}/{limites['limite_rpd']}")

# Generar alerta
alerta = tracker.generar_alerta_limites()
if alerta:
    print(alerta)

# Calcular costo estimado
costo = tracker.calcular_costo_estimado(plan="paid")
print(f"Costo estimado: ${costo['costo_total']:.4f} USD")
```

---

## 🧪 Testing

### Ejecutar Tests

```bash
# Tests unitarios del GeminiService
pytest src/tests/services/ai/test_gemini_service.py -v

# Tests de helpers
pytest src/tests/services/ai/test_file_processor.py -v
pytest src/tests/services/ai/test_prompt_builder.py -v
pytest src/tests/services/ai/test_response_parser.py -v

# Tests con cobertura
pytest --cov=src/services/ai --cov-report=html
```

### Ejemplo de Test

```python
import pytest
from unittest.mock import AsyncMock, MagicMock
from src.services.ai import GeminiService

@pytest.mark.asyncio
async def test_generar_retroalimentacion_exitosa(mock_gemini_api):
    # Arrange
    service = GeminiService(api_key="test_key")
    service.model = mock_gemini_api
    await service.inicializar()
    
    # Act
    resultado = await service.generar_retroalimentacion(...)
    
    # Assert
    assert resultado["calificacion_sugerida"] >= 0
    assert resultado["calificacion_sugerida"] <= 5
    assert "fortalezas" in resultado
    assert len(resultado["fortalezas"]) > 0
```

---

## 🛠️ Troubleshooting

### Error: "GEMINI_API_KEY no configurada"

**Solución**:
1. Verifica que `.env` existe en `backend/`
2. Confirma que la línea `GEMINI_API_KEY=...` está presente
3. Reinicia el servidor FastAPI

### Error: "google-generativeai no instalado"

**Solución**:
```bash
pip install google-generativeai==0.8.3
```

### Error: "Rate limit exceeded"

**Solución**:
- **Espera 60 segundos** (límite por minuto)
- **Reduce frecuencia** de llamadas
- **Considera plan pagado** si necesitas más RPM

### Error: "Content filter blocked"

**Solución**:
- El contenido fue bloqueado por filtros de seguridad de Google
- Revisa si el contenido tiene:
  - Lenguaje violento u ofensivo
  - Información sensible o peligrosa
- Ajusta `safety_level` en `AIConfig` (no recomendado)

### Response Parsing Error

**Solución**:
- El parser intenta 3 métodos diferentes de extracción
- Si persiste, verifica `temperature` (valores muy altos causan respuestas erráticas)
- Revisa logs en `backend/logs/` para ver la respuesta cruda

---

## 📖 Recursos Adicionales

- **Documentación Gemini**: https://ai.google.dev/docs
- **API Reference**: https://ai.google.dev/api
- **Pricing**: https://ai.google.dev/pricing
- **Google AI Studio**: https://makersuite.google.com/

---

## 📝 Notas de Implementación

### Decisiones de Diseño

1. **Async/Await**: Todas las llamadas a API son asíncronas para no bloquear el event loop
2. **Retry con Backoff**: 3 reintentos automáticos con delay exponencial (2s, 4s, 8s)
3. **Type Safety**: Type hints en todos los métodos + validaciones Pydantic
4. **Separation of Concerns**: Helpers independientes (file, prompt, parser, cost)
5. **Error Granularity**: 8 excepciones específicas vs. excepciones genéricas

### Performance

- **Caché de respuestas**: Opcional (configurar `enable_response_cache=True`)
- **Timeout**: 60s por defecto (configurable)
- **Concurrencia**: Usa `asyncio.gather()` para múltiples entregas simultáneas

---

## 👨‍💻 Autor

**Gemini AI Assistant**  
Fecha: 31 octubre 2025  
Versión: 1.0.0

---

## 📄 Licencia

Este código es parte del proyecto Acadify.
