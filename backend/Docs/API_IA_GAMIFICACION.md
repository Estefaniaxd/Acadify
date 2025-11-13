# API de IA y Gamificación - Documentación

## 📋 Índice
- [Visión General](#visión-general)
- [Endpoints Disponibles](#endpoints-disponibles)
- [Modelos de Datos](#modelos-de-datos)
- [Flujo de Uso](#flujo-de-uso)
- [Ejemplos de Uso](#ejemplos-de-uso)
- [Códigos de Error](#códigos-de-error)

---

## 🎯 Visión General

El sistema de IA y Gamificación proporciona una API completa para:

- ✅ **Análisis automático de tareas con Google Gemini AI**
- ✅ **Sistema de puntos y gamificación**
- ✅ **Rankings y leaderboards**
- ✅ **Retroalimentación detallada con IA**
- ✅ **Insignias automáticas**
- ✅ **Estadísticas para docentes**

**Tecnologías**:
- FastAPI con OpenAPI 3.0
- Google Gemini 2.5 Flash API
- PostgreSQL con JSONB
- Pydantic v2 para validación

---

## 🔌 Endpoints Disponibles

### 1. Entrega de Tareas con IA

#### `POST /api/cursos/{curso_id}/tareas/{tarea_id}/entregas`

Permite a un estudiante entregar una tarea para análisis automático con IA.

**Autenticación**: Bearer Token (Estudiante)

**Parámetros de Ruta**:
- `curso_id` (string): ID del curso
- `tarea_id` (string): ID de la tarea

**Cuerpo de la Solicitud** (multipart/form-data):
```json
{
  "contenido_texto": "string (opcional, max 50,000 caracteres)",
  "archivo": "file (opcional, max 50MB)"
}
```

**Nota**: Al menos uno de los dos (contenido_texto o archivo) debe estar presente.

**Formatos de Archivo Soportados**:
- Documentos: PDF, Word (.doc, .docx), TXT
- Hojas de cálculo: Excel (.xls, .xlsx)
- Presentaciones: PowerPoint (.ppt, .pptx)
- Imágenes: PNG, JPEG, JPG, GIF, WebP
- Código: Python, JavaScript, HTML, CSS, JSON, XML
- Comprimidos: ZIP

**Respuesta Exitosa** (201 Created):
```json
{
  "success": true,
  "message": "Entrega procesada exitosamente con IA. ¡Felicidades! Has obtenido 70 puntos.",
  "data": {
    "entrega_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
    "intentos": 1,
    "es_tardia": false,
    "fecha_entrega": "2024-01-20T15:30:00Z",
    "retroalimentacion_ia": {
      "analisis_general": "Excelente trabajo. El código está bien estructurado...",
      "calificacion": 4.2,
      "nivel_cumplimiento": "85%",
      "fortalezas": [
        "Código limpio y legible",
        "Buena documentación",
        "Uso correcto de funciones"
      ],
      "areas_mejora": [
        "Agregar más validaciones de entrada",
        "Mejorar manejo de errores"
      ],
      "sugerencias_especificas": [
        {
          "ubicacion": "Línea 25",
          "problema": "Falta validación de tipo de dato",
          "sugerencia": "Agregar verificación: if isinstance(x, int)",
          "ejemplo": "if isinstance(x, int): return x * 2"
        }
      ],
      "cumple_rubrica": {
        "Funcionalidad": {
          "puntos": 4.5,
          "comentario": "El código funciona correctamente"
        },
        "Estilo": {
          "puntos": 4.0,
          "comentario": "Buen estilo, mejorar nombres de variables"
        }
      }
    },
    "puntos": {
      "puntos_base": 50,
      "puntos_bonificacion": 20,
      "penalizacion_tardia": 0,
      "penalizacion_intentos": 0,
      "puntos_totales": 70,
      "desglose": "50 (base) + 20 (bonus excelencia)"
    },
    "gamificacion": {
      "puntos_otorgados": 70,
      "puntos_acumulados": 170,
      "nivel_actual": "Bronce II",
      "progreso_siguiente_nivel": 68.0,
      "nuevas_insignias": [
        {
          "insignia_id": "primera-entrega",
          "nombre": "Primera Entrega",
          "descripcion": "Completaste tu primera tarea",
          "imagen_url": "/assets/insignias/primera-entrega.png",
          "fecha_obtencion": "2024-01-20T15:30:00Z"
        }
      ]
    }
  }
}
```

**Errores Posibles**:
- `400 Bad Request`: Contenido vacío o datos inválidos
- `403 Forbidden`: No estás inscrito en este curso
- `404 Not Found`: Tarea no encontrada
- `413 Payload Too Large`: Archivo mayor a 50MB
- `415 Unsupported Media Type`: Tipo de archivo no soportado
- `500 Internal Server Error`: Error del servidor o API de IA

---

### 2. Obtener Retroalimentación de IA

#### `GET /api/entregas/{entrega_id}/retroalimentacion`

Obtiene la retroalimentación completa de IA para una entrega específica.

**Autenticación**: Bearer Token (Estudiante/Docente)

**Permisos**:
- Estudiantes: Solo pueden ver su propia retroalimentación
- Docentes/Coordinadores: Pueden ver cualquier retroalimentación

**Parámetros de Ruta**:
- `entrega_id` (string): ID de la entrega

**Respuesta Exitosa** (200 OK):
```json
{
  "success": true,
  "message": "Retroalimentación obtenida exitosamente",
  "data": {
    // Misma estructura que POST /entregas
  }
}
```

**Errores Posibles**:
- `403 Forbidden`: No tienes permisos para ver esta retroalimentación
- `404 Not Found`: Entrega no encontrada o sin retroalimentación

---

### 3. Obtener Puntos de Usuario

#### `GET /api/usuarios/{usuario_id}/puntos`

Obtiene información completa de gamificación de un usuario.

**Autenticación**: Bearer Token

**Permisos**:
- Estudiantes: Solo pueden ver sus propios puntos
- Docentes/Coordinadores: Pueden ver puntos de cualquier usuario

**Parámetros de Ruta**:
- `usuario_id` (string): ID del usuario

**Respuesta Exitosa** (200 OK):
```json
{
  "success": true,
  "data": {
    "puntos_acumulados": 1450,
    "nivel": "Bronce III",
    "nivel_info": {
      "nivel_actual": "Bronce III",
      "puntos_minimos_nivel": 250,
      "puntos_siguiente_nivel": 500,
      "progreso_porcentaje": 80.0,
      "puntos_para_siguiente": 50
    },
    "historial_reciente": [
      {
        "cambio": 70,
        "motivo": "Entrega de Tarea: Introducción a Python",
        "fecha": "2024-01-20T15:30:00Z"
      },
      {
        "cambio": 55,
        "motivo": "Entrega de Tarea: Variables y Tipos",
        "fecha": "2024-01-18T10:15:00Z"
      }
    ],
    "insignias": [
      {
        "insignia_id": "novato",
        "nombre": "Novato",
        "descripcion": "Has alcanzado 100 puntos",
        "imagen_url": "/assets/insignias/novato.png",
        "tipo": "PUNTOS",
        "fecha_obtencion": "2024-01-15T12:00:00Z"
      }
    ]
  }
}
```

---

### 4. Obtener Ranking Global

#### `GET /api/usuarios/ranking`

Obtiene el ranking global de usuarios ordenado por puntos.

**Autenticación**: Bearer Token

**Parámetros de Query**:
- `limite` (int, opcional): Número de usuarios a retornar (1-100, default: 10)
- `offset` (int, opcional): Posición inicial para paginación (default: 0)

**Respuesta Exitosa** (200 OK):
```json
{
  "success": true,
  "data": [
    {
      "posicion": 1,
      "usuario_id": "uuid-123",
      "nombre_completo": "María García",
      "puntos": 5250,
      "nivel": "Oro II"
    },
    {
      "posicion": 2,
      "usuario_id": "uuid-456",
      "nombre_completo": "Juan Pérez",
      "puntos": 3800,
      "nivel": "Plata III"
    }
  ],
  "total": 150
}
```

---

### 5. Obtener Mi Posición en el Ranking

#### `GET /api/usuarios/mi-ranking`

Obtiene la posición del usuario actual en el ranking global.

**Autenticación**: Bearer Token

**Respuesta Exitosa** (200 OK):
```json
{
  "success": true,
  "data": {
    "posicion": 15,
    "puntos": 1450,
    "nivel": "Bronce III",
    "puntos_hasta_anterior": 150,
    "puntos_hasta_siguiente": 50,
    "total_usuarios": 150
  }
}
```

**Explicación de Campos**:
- `posicion`: Tu posición actual en el ranking (1 = primero)
- `puntos_hasta_anterior`: Puntos que te faltan para alcanzar al usuario anterior
- `puntos_hasta_siguiente`: Ventaja de puntos sobre el siguiente usuario
- `total_usuarios`: Total de usuarios con puntos

---

### 6. Estadísticas de IA de una Tarea (Docentes)

#### `GET /api/cursos/{curso_id}/tareas/{tarea_id}/estadisticas-ia`

Obtiene estadísticas agregadas de IA para todas las entregas de una tarea.

**Autenticación**: Bearer Token (Solo Docentes/Coordinadores)

**Parámetros de Ruta**:
- `curso_id` (string): ID del curso
- `tarea_id` (string): ID de la tarea

**Respuesta Exitosa** (200 OK):
```json
{
  "success": true,
  "data": {
    "tarea_id": "uuid-tarea",
    "tarea_titulo": "Introducción a Python",
    "total_entregas": 45,
    "estadisticas": {
      "calificacion_promedio": 4.2,
      "calificacion_maxima": 5.0,
      "calificacion_minima": 2.8,
      "puntos_promedio": 62.5,
      "puntos_maximos": 70,
      "puntos_minimos": 30,
      "entregas_tardias": 5,
      "porcentaje_tardias": 11.1,
      "fortalezas_comunes": [
        {
          "texto": "Código limpio y legible",
          "frecuencia": 38
        },
        {
          "texto": "Buena documentación",
          "frecuencia": 32
        }
      ],
      "areas_mejora_comunes": [
        {
          "texto": "Agregar más validaciones",
          "frecuencia": 25
        },
        {
          "texto": "Mejorar manejo de errores",
          "frecuencia": 20
        }
      ]
    }
  }
}
```

---

### 7. Health Check

#### `GET /api/ia/health`

Verifica el estado del sistema de IA y gamificación.

**Autenticación**: No requerida

**Respuesta Exitosa** (200 OK):
```json
{
  "success": true,
  "message": "Sistema de IA y Gamificación operativo",
  "services": {
    "gemini_ai": "operativo",
    "gamificacion": "operativo",
    "puntos": "operativo"
  }
}
```

---

## 📊 Modelos de Datos

### Sistema de Niveles

El sistema tiene **12 niveles** organizados en 4 categorías:

| Nivel | Puntos Mínimos | Puntos Máximos |
|-------|---------------|----------------|
| **Bronce I** | 0 | 99 |
| **Bronce II** | 100 | 249 |
| **Bronce III** | 250 | 499 |
| **Plata I** | 500 | 749 |
| **Plata II** | 750 | 1,199 |
| **Plata III** | 1,200 | 1,999 |
| **Oro I** | 2,000 | 2,999 |
| **Oro II** | 3,000 | 3,999 |
| **Oro III** | 4,000 | 4,999 |
| **Platino I** | 5,000 | 7,499 |
| **Platino II** | 7,500 | 9,999 |
| **Platino III** | 10,000+ | ∞ |

### Insignias Automáticas

| Insignia | Requisito | Descripción |
|----------|----------|-------------|
| **Novato** | 100 pts | Primeros pasos en el aprendizaje |
| **Estudiante Dedicado** | 500 pts | Compromiso con el estudio |
| **Explorador del Conocimiento** | 1,000 pts | Curiosidad y dedicación |
| **Maestro en Progreso** | 2,000 pts | Dominio avanzado |
| **Sabio Digital** | 5,000 pts | Excelencia académica |

### Fórmula de Puntos

```
Puntos Totales = Base + Bonificación - Penalización Tardía - Penalización Intentos

Donde:
- Base: tarea.puntos_base (configurado por docente, default: 50)
- Bonificación: tarea.puntos_bonificacion si calificación >= 4.5
- Penalización Tardía: -30% de Base si entrega después del deadline
- Penalización Intentos: -10% de Base por cada intento extra (max 2 intentos)
```

**Ejemplos**:

1. **Entrega a tiempo, primera vez, calificación 4.8**:
   - Base: 50 pts
   - Bonificación: +20 pts (excelencia)
   - **Total: 70 pts**

2. **Entrega tardía, primera vez, calificación 4.2**:
   - Base: 50 pts
   - Penalización tardía: -15 pts (30%)
   - **Total: 35 pts**

3. **Entrega a tiempo, tercer intento, calificación 4.0**:
   - Base: 50 pts
   - Penalización intentos: -10 pts (2 intentos extra)
   - **Total: 40 pts**

---

## 🔄 Flujo de Uso

### Flujo del Estudiante

```mermaid
graph TD
    A[Estudiante crea entrega] --> B[POST /entregas]
    B --> C{¿Archivo o texto?}
    C -->|Archivo| D[Subir archivo multipart]
    C -->|Texto| E[Enviar contenido_texto]
    D --> F[Backend valida formato/tamaño]
    E --> F
    F --> G[GeminiService analiza contenido]
    G --> H[IA genera retroalimentación]
    H --> I[PuntosService calcula puntos]
    I --> J[Otorga puntos al usuario]
    J --> K[Verifica insignias]
    K --> L[Retorna respuesta completa]
    L --> M[Frontend muestra feedback]
```

### Flujo del Docente

```mermaid
graph TD
    A[Docente crea tarea] --> B[Configura: puntos_base, bonificación, rúbrica]
    B --> C[Habilita: habilitar_retroalimentacion_ia = true]
    C --> D[Estudiantes entregan]
    D --> E[Análisis automático de IA]
    E --> F[Docente consulta: GET /estadisticas-ia]
    F --> G[Ve: calificaciones promedio, fortalezas comunes]
    G --> H[Ajusta enseñanza basado en datos]
```

---

## 💡 Ejemplos de Uso

### Ejemplo 1: Entregar Tarea con Archivo Python

**Request**:
```bash
curl -X POST "https://api.acadify.com/api/cursos/123/tareas/456/entregas" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "contenido_texto=Mi solución al ejercicio de funciones" \
  -F "archivo=@tarea.py"
```

**Response** (201):
```json
{
  "success": true,
  "message": "Entrega procesada exitosamente con IA. ¡Felicidades! Has obtenido 70 puntos.",
  "data": {
    "entrega_id": "abc-123",
    "retroalimentacion_ia": {
      "calificacion": 4.5,
      "fortalezas": ["Código limpio"],
      "areas_mejora": ["Agregar validaciones"]
    },
    "puntos": {
      "puntos_totales": 70
    },
    "gamificacion": {
      "nivel_actual": "Bronce II",
      "nuevas_insignias": []
    }
  }
}
```

### Ejemplo 2: Ver Mi Ranking

**Request**:
```bash
curl -X GET "https://api.acadify.com/api/usuarios/mi-ranking" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Response** (200):
```json
{
  "success": true,
  "data": {
    "posicion": 15,
    "puntos": 1450,
    "nivel": "Bronce III",
    "puntos_hasta_anterior": 150
  }
}
```

### Ejemplo 3: Ver Top 10 del Ranking

**Request**:
```bash
curl -X GET "https://api.acadify.com/api/usuarios/ranking?limite=10" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Ejemplo 4: Ver Estadísticas de Tarea (Docente)

**Request**:
```bash
curl -X GET "https://api.acadify.com/api/cursos/123/tareas/456/estadisticas-ia" \
  -H "Authorization: Bearer DOCENTE_TOKEN"
```

---

## ❌ Códigos de Error

| Código | Significado | Solución |
|--------|------------|----------|
| 400 | Datos inválidos | Verifica que envías contenido_texto o archivo |
| 401 | No autenticado | Incluye token válido en Authorization header |
| 403 | Sin permisos | Verifica que estés inscrito en el curso o que tengas el rol correcto |
| 404 | Recurso no encontrado | Verifica que el tarea_id o entrega_id sean correctos |
| 413 | Archivo muy grande | Reduce el tamaño del archivo a menos de 50MB |
| 415 | Tipo de archivo no soportado | Usa formatos: PDF, Word, Excel, imágenes, código |
| 429 | Demasiadas solicitudes | Espera unos minutos antes de reintentar |
| 500 | Error del servidor | Contacta soporte o revisa logs del servidor |

---

## 🔐 Autenticación

Todos los endpoints (excepto `/ia/health`) requieren autenticación mediante **Bearer Token**.

**Header requerido**:
```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Obtener token**: `POST /auth/login`

---

## 📝 Notas Importantes

1. **Límite de tamaño de archivo**: 50MB
2. **Límite de texto**: 50,000 caracteres
3. **Rate limiting**: 1000 requests por hora por usuario
4. **Calificación de IA**: Escala de 0.0 a 5.0
5. **Puntos negativos**: No se permiten puntos acumulados negativos (mínimo: 0)
6. **Intentos**: Máximo 3 intentos con penalización
7. **Retroalimentación**: Se guarda en formato JSONB en PostgreSQL
8. **OpenAPI Docs**: Disponible en `/docs` y `/redoc`

---

## 🚀 Próximas Funcionalidades

- [ ] Filtrar ranking por institución o curso
- [ ] Exportar estadísticas a CSV/Excel
- [ ] Webhook para notificaciones en tiempo real
- [ ] Integración con sistemas de mensajería
- [ ] Análisis de plagio automático
- [ ] Feedback de voz generado por IA
- [ ] Sugerencias de mejora personalizadas

---

**Versión del Documento**: 1.0  
**Última Actualización**: 20 de Enero, 2024  
**Autor**: Acadify Team
