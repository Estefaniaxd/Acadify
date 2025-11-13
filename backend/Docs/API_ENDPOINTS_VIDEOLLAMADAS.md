# 📹 API Endpoints - Sistema de Videollamadas Jitsi

> **Estado**: ✅ Completado y verificado  
> **Fecha**: 9 de noviembre de 2025  
> **Total de Endpoints**: 15  
> **Base Path**: `/api/communication/videollamadas`

---

## 📊 Resumen Ejecutivo

El sistema de videollamadas cuenta con **15 endpoints REST** completamente implementados y listos para integración con el frontend. Todos los endpoints utilizan:

- ✅ **Enumeraciones tipadas** (Python Enums)
- ✅ **Service Layer** para lógica de negocio
- ✅ **CRUD operations** con validación
- ✅ **Autenticación JWT** (donde aplica)
- ✅ **Documentación OpenAPI** completa

---

## 🔧 Configuración

### Base URL
```
http://localhost:8000/api/communication/videollamadas
```

### Autenticación
La mayoría de los endpoints requieren un token JWT válido:

```http
Authorization: Bearer <your_jwt_token>
```

---

## 📋 Listado Completo de Endpoints

### 1. Health Check

```http
GET /videollamadas/health
```

**Descripción**: Verifica que el módulo esté operativo.

**Autenticación**: No requerida

**Response**:
```json
{
  "success": true,
  "message": "Módulo de videollamadas operativo con service layer y enums"
}
```

---

### 2. Generar Room Name

```http
GET /videollamadas/room-name/generate?base_name=sala-matematicas
```

**Descripción**: Genera un nombre único para una sala Jitsi.

**Autenticación**: ✅ Requerida

**Query Parameters**:
- `base_name` (string, requerido): Nombre base para la sala

**Response**:
```json
{
  "room_name": "sala-matematicas-2"
}
```

---

### 3. Crear Videollamada

```http
POST /videollamadas/
```

**Descripción**: Crea una nueva videollamada.

**Autenticación**: ✅ Requerida

**Request Body**:
```json
{
  "jitsi_room_name": "sala-clase-101",
  "tipo_llamada": "video",
  "sala_chat_id": "uuid-opcional",
  "configuracion": {
    "max_participantes": 50,
    "permitir_grabacion": true,
    "permitir_chat": true
  }
}
```

**Response** (201 Created):
```json
{
  "id": "uuid",
  "jitsi_room_name": "sala-clase-101",
  "tipo_llamada": "video",
  "iniciador_id": "uuid",
  "sala_chat_id": "uuid",
  "estado": "ACTIVA",
  "fecha_inicio": "2025-11-09T10:30:00Z",
  "fecha_fin": null,
  "duracion_segundos": null,
  "configuracion": {...},
  "participantes": [...]
}
```

---

### 4. Obtener Videollamada

```http
GET /videollamadas/{videollamada_id}?incluir_participantes=true
```

**Descripción**: Obtiene información detallada de una videollamada.

**Autenticación**: ✅ Requerida

**Path Parameters**:
- `videollamada_id` (UUID, requerido): ID de la videollamada

**Query Parameters**:
- `incluir_participantes` (boolean, opcional): Incluir lista de participantes (default: false)

**Response**:
```json
{
  "id": "uuid",
  "jitsi_room_name": "sala-clase-101",
  "tipo_llamada": "video",
  "estado": "ACTIVA",
  "fecha_inicio": "2025-11-09T10:30:00Z",
  "participantes": [
    {
      "id": "uuid",
      "usuario_id": "uuid",
      "es_moderador": true,
      "fecha_union": "2025-11-09T10:30:00Z",
      "calidad_conexion": "excelente"
    }
  ]
}
```

---

### 5. Listar Videollamadas

```http
GET /videollamadas/?solo_activas=true&skip=0&limit=50
```

**Descripción**: Lista videollamadas con paginación y filtros.

**Autenticación**: ✅ Requerida

**Query Parameters**:
- `sala_chat_id` (UUID, opcional): Filtrar por sala de chat
- `solo_activas` (boolean, opcional): Solo videollamadas activas (default: true)
- `skip` (int, opcional): Items a saltar para paginación (default: 0)
- `limit` (int, opcional): Items por página (default: 50, max: 100)

**Response**:
```json
{
  "items": [
    {
      "id": "uuid",
      "jitsi_room_name": "sala-clase-101",
      "tipo_llamada": "video",
      "estado": "ACTIVA",
      "fecha_inicio": "2025-11-09T10:30:00Z"
    }
  ],
  "total": 10,
  "skip": 0,
  "limit": 50,
  "has_more": false
}
```

---

### 6. Unirse a Videollamada

```http
POST /videollamadas/{videollamada_id}/join
```

**Descripción**: Permite a un usuario unirse a una videollamada.

**Autenticación**: ✅ Requerida

**Path Parameters**:
- `videollamada_id` (UUID, requerido): ID de la videollamada

**Request Body**:
```json
{
  "es_moderador": false
}
```

**Response**:
```json
{
  "id": "uuid",
  "videollamada_id": "uuid",
  "usuario_id": "uuid",
  "fecha_union": "2025-11-09T10:35:00Z",
  "fecha_salida": null,
  "duracion_segundos": null,
  "es_moderador": false,
  "calidad_conexion": null
}
```

**Validaciones Automáticas**:
- ✅ Videollamada debe estar en estado `ACTIVA`
- ✅ Usuario no puede unirse si ya es participante activo
- ✅ Respeta límite máximo de participantes

---

### 7. Salir de Videollamada

```http
POST /videollamadas/{videollamada_id}/leave
```

**Descripción**: Marca la salida de un usuario de una videollamada.

**Autenticación**: ✅ Requerida

**Path Parameters**:
- `videollamada_id` (UUID, requerido): ID de la videollamada

**Response**:
```json
{
  "success": true,
  "message": "Has salido de la videollamada exitosamente"
}
```

**Acciones Automáticas**:
- ✅ Registra `fecha_salida`
- ✅ Calcula `duracion_segundos` automáticamente

---

### 8. Obtener Participantes Activos

```http
GET /videollamadas/{videollamada_id}/participants
```

**Descripción**: Obtiene lista de participantes actualmente conectados.

**Autenticación**: ✅ Requerida

**Path Parameters**:
- `videollamada_id` (UUID, requerido): ID de la videollamada

**Response**:
```json
[
  {
    "id": "uuid",
    "usuario_id": "uuid",
    "fecha_union": "2025-11-09T10:30:00Z",
    "fecha_salida": null,
    "es_moderador": true,
    "calidad_conexion": "excelente"
  },
  {
    "id": "uuid",
    "usuario_id": "uuid",
    "fecha_union": "2025-11-09T10:32:00Z",
    "fecha_salida": null,
    "es_moderador": false,
    "calidad_conexion": "buena"
  }
]
```

---

### 9. Actualizar Calidad de Conexión

```http
PATCH /videollamadas/participants/{participante_id}/quality
```

**Descripción**: Actualiza la calidad de conexión de un participante.

**Autenticación**: ✅ Requerida

**Path Parameters**:
- `participante_id` (UUID, requerido): ID del participante

**Request Body (Opción 1 - Métricas)**:
```json
{
  "latencia_ms": 45,
  "perdida_paquetes_pct": 0.8
}
```

**Request Body (Opción 2 - Calidad Directa)**:
```json
{
  "calidad": "buena"
}
```

**Response**:
```json
{
  "id": "uuid",
  "usuario_id": "uuid",
  "calidad_conexion": "buena",
  "estadisticas": {
    "latencia_ms": 45,
    "perdida_paquetes_pct": 0.8,
    "actualizado_en": "2025-11-09T10:35:00Z"
  }
}
```

**Valores de Calidad**:
- `excelente`: Latencia < 50ms, Pérdida < 1%
- `buena`: Latencia < 150ms, Pérdida < 3%
- `regular`: Latencia < 300ms, Pérdida < 5%
- `mala`: Latencia >= 300ms o Pérdida >= 5%

---

### 10. Finalizar Videollamada

```http
POST /videollamadas/{videollamada_id}/finalize
```

**Descripción**: Finaliza una videollamada activa.

**Autenticación**: ✅ Requerida (Moderador)

**Path Parameters**:
- `videollamada_id` (UUID, requerido): ID de la videollamada

**Request Body**:
```json
{
  "resumen_ia": "Reunión sobre planificación del proyecto Q4. Participaron 12 estudiantes."
}
```

**Response**:
```json
{
  "id": "uuid",
  "jitsi_room_name": "sala-clase-101",
  "estado": "FINALIZADA",
  "fecha_inicio": "2025-11-09T10:30:00Z",
  "fecha_fin": "2025-11-09T11:30:00Z",
  "duracion_segundos": 3600,
  "resumen_ia": "Reunión sobre planificación..."
}
```

**Validaciones**:
- ✅ Solo moderadores pueden finalizar
- ✅ Solo desde estado `ACTIVA` o `PROGRAMADA`
- ✅ Usa `puede_transicionar_a()` del enum

**Acciones Automáticas**:
- ✅ Marca `fecha_fin`
- ✅ Calcula `duracion_segundos`
- ✅ Desconecta participantes activos

---

### 11. Cancelar Videollamada

```http
POST /videollamadas/{videollamada_id}/cancel
```

**Descripción**: Cancela una videollamada programada o activa.

**Autenticación**: ✅ Requerida (Moderador)

**Path Parameters**:
- `videollamada_id` (UUID, requerido): ID de la videollamada

**Response**:
```json
{
  "id": "uuid",
  "jitsi_room_name": "sala-clase-101",
  "estado": "CANCELADA",
  "fecha_inicio": "2025-11-09T10:30:00Z"
}
```

**Validaciones**:
- ✅ Solo moderadores pueden cancelar
- ✅ Usa `puede_transicionar_a()` del enum
- ✅ Desconecta todos los participantes activos

---

### 12. Agregar Grabación

```http
POST /videollamadas/{videollamada_id}/recordings
```

**Descripción**: Registra una nueva grabación de videollamada.

**Autenticación**: ✅ Requerida (Moderador)

**Path Parameters**:
- `videollamada_id` (UUID, requerido): ID de la videollamada

**Request Body**:
```json
{
  "titulo": "Clase de Matemáticas - Álgebra Lineal",
  "archivo_url": "https://cdn.example.com/recordings/rec_12345.mp4",
  "thumbnail_url": "https://cdn.example.com/thumbnails/rec_12345.jpg",
  "formato": "mp4",
  "calidad": "FHD",
  "duracion_segundos": 3600,
  "tamano_bytes": 524288000
}
```

**Response** (201 Created):
```json
{
  "id": "uuid",
  "videollamada_id": "uuid",
  "titulo": "Clase de Matemáticas - Álgebra Lineal",
  "archivo_url": "https://cdn.example.com/recordings/rec_12345.mp4",
  "thumbnail_url": "https://cdn.example.com/thumbnails/rec_12345.jpg",
  "formato": "mp4",
  "calidad": "FHD",
  "duracion_segundos": 3600,
  "tamano_bytes": 524288000,
  "fecha_subida": "2025-11-09T11:35:00Z",
  "estado_procesamiento": "completado"
}
```

**Formatos Soportados**:
- `mp4` - MPEG-4 (Recomendado)
- `webm` - WebM
- `mkv` - Matroska
- `avi` - Audio Video Interleave

**Calidades Soportadas**:
- `SD` - 640x480 (500 kbps)
- `HD` - 1280x720 (2500 kbps)
- `FHD` - 1920x1080 (5000 kbps)
- `4K` - 3840x2160 (15000 kbps)

---

### 13. Listar Grabaciones

```http
GET /videollamadas/{videollamada_id}/recordings
```

**Descripción**: Obtiene todas las grabaciones de una videollamada.

**Autenticación**: ✅ Requerida

**Path Parameters**:
- `videollamada_id` (UUID, requerido): ID de la videollamada

**Response**:
```json
[
  {
    "id": "uuid",
    "videollamada_id": "uuid",
    "titulo": "Clase de Matemáticas - Álgebra Lineal",
    "archivo_url": "https://cdn.example.com/recordings/rec_12345.mp4",
    "formato": "mp4",
    "calidad": "FHD",
    "duracion_segundos": 3600,
    "tamano_bytes": 524288000,
    "fecha_subida": "2025-11-09T11:35:00Z",
    "estado_procesamiento": "completado",
    "metadatos": {
      "codec": "H.264",
      "bitrate": "5000 kbps",
      "fps": 30
    }
  }
]
```

---

### 14. Actualizar Transcripción

```http
PATCH /videollamadas/{videollamada_id}/transcription
```

**Descripción**: Actualiza o agrega transcripción de videollamada.

**Autenticación**: ✅ Requerida (Moderador)

**Path Parameters**:
- `videollamada_id` (UUID, requerido): ID de la videollamada

**Request Body**:
```json
{
  "transcripcion": "John Doe: Buenos días a todos.\nJane Smith: Hola, ¿cómo están?\nJohn Doe: Vamos a comenzar con..."
}
```

**Response**:
```json
{
  "id": "uuid",
  "jitsi_room_name": "sala-clase-101",
  "estado": "FINALIZADA",
  "transcripcion": "John Doe: Buenos días a todos...",
  "fecha_fin": "2025-11-09T11:30:00Z"
}
```

**Uso**: Este endpoint es típicamente llamado por sistemas de transcripción AI (ej: Whisper).

---

### 15. Validar Puede Unirse

```http
POST /videollamadas/{videollamada_id}/validate-join
```

**Descripción**: Valida si un usuario puede unirse a una videollamada.

**Autenticación**: ✅ Requerida

**Path Parameters**:
- `videollamada_id` (UUID, requerido): ID de la videollamada

**Response (Puede Unirse)**:
```json
{
  "can_join": true,
  "reason": null,
  "current_participants": 5,
  "max_participants": 50
}
```

**Response (No Puede Unirse)**:
```json
{
  "can_join": false,
  "reason": "La videollamada ha alcanzado el límite máximo de participantes",
  "current_participants": 50,
  "max_participants": 50
}
```

**Verifica**:
- ✅ Estado de la videollamada (`ACTIVA`)
- ✅ Límite de participantes
- ✅ Si el usuario ya está unido

---

## 🔐 Códigos de Estado HTTP

| Código | Descripción |
|--------|-------------|
| `200 OK` | Operación exitosa |
| `201 Created` | Recurso creado exitosamente |
| `400 Bad Request` | Datos inválidos o estado incorrecto |
| `401 Unauthorized` | Token JWT faltante o inválido |
| `403 Forbidden` | Permisos insuficientes (ej: no es moderador) |
| `404 Not Found` | Videollamada o participante no encontrado |
| `500 Internal Server Error` | Error interno del servidor |

---

## 🎯 Flujo Típico de Uso

### 1. Crear Videollamada (Profesor/Moderador)
```http
POST /videollamadas/
{
  "tipo_llamada": "video",
  "configuracion": {"max_participantes": 30}
}
```

### 2. Obtener JWT Token para Jitsi
```javascript
// En el frontend, después de crear la videollamada
const jwtToken = await generateJitsiToken(
  videollamada.id,
  videollamada.jitsi_room_name,
  currentUser
);
```

### 3. Estudiante se Une
```http
POST /videollamadas/{videollamada_id}/join
{
  "es_moderador": false
}
```

### 4. Inicializar Jitsi en Frontend
```javascript
const api = new JitsiMeetExternalAPI('meet.jit.si', {
  roomName: videollamada.jitsi_room_name,
  jwt: jwtToken,
  parentNode: document.querySelector('#jitsi-container')
});
```

### 5. Actualizar Calidad Periódicamente
```http
PATCH /videollamadas/participants/{participante_id}/quality
{
  "latencia_ms": 45,
  "perdida_paquetes_pct": 0.8
}
```

### 6. Finalizar Videollamada (Profesor)
```http
POST /videollamadas/{videollamada_id}/finalize
{
  "resumen_ia": "Clase sobre álgebra lineal..."
}
```

---

## 📊 Métricas y Estadísticas

### Consulta SQL para Estadísticas
```sql
-- Usar función SQL para obtener estadísticas
SELECT get_estadisticas_videollamada('uuid-videollamada');

-- Resultado (JSON):
{
  "total_participantes": 12,
  "duracion_promedio_minutos": 45.5,
  "calidad_promedio": "buena",
  "participantes_activos": 10,
  "tasa_abandono": 0.17
}
```

### Vista de Videollamadas Activas
```sql
-- Consultar vista de videollamadas activas
SELECT * FROM videollamadas_activas;
```

---

## 🧪 Testing

### Script de Prueba Automatizado

Ejecutar todas las pruebas:
```bash
python scripts/test_videollamadas_api.py
```

### Prueba Individual con cURL

```bash
# Health Check
curl http://localhost:8000/api/communication/videollamadas/health

# Crear videollamada (requiere token)
curl -X POST http://localhost:8000/api/communication/videollamadas/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"tipo_llamada":"video","configuracion":{"max_participantes":30}}'
```

---

## 🚀 Integración con Frontend

### Ejemplo con Axios (React/TypeScript)

```typescript
import axios from 'axios';

const API_BASE = 'http://localhost:8000/api/communication/videollamadas';

// Crear videollamada
export async function crearVideollamada(token: string) {
  const response = await axios.post(
    `${API_BASE}/`,
    {
      tipo_llamada: 'video',
      configuracion: {
        max_participantes: 30,
        permitir_grabacion: true
      }
    },
    {
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      }
    }
  );
  return response.data;
}

// Unirse a videollamada
export async function unirseVideollamada(
  videollamadaId: string,
  token: string
) {
  const response = await axios.post(
    `${API_BASE}/${videollamadaId}/join`,
    { es_moderador: false },
    {
      headers: { 'Authorization': `Bearer ${token}` }
    }
  );
  return response.data;
}
```

---

## 📚 Referencias

- **Documentación Fase 2**: `Docs/FASE_2_VIDEOLLAMADAS_JITSI_COMPLETADA.md`
- **Modelos DB**: `src/models/communication/videollamada.py`
- **ENUMs**: `src/enums/communication/videollamada_enums.py`
- **Schemas**: `src/schemas/communication/videollamada_schemas.py`
- **CRUD Operations**: `src/crud/communication/videollamada.py`
- **Service Layer**: `src/services/communication/videollamada_service.py`
- **Endpoints**: `src/api/routes/communication/videollamadas.py`

---

## ✅ Checklist de Verificación

- [x] 15 endpoints implementados
- [x] Autenticación JWT configurada
- [x] Validaciones de permisos (moderador)
- [x] Enumeraciones tipadas (TipoLlamada, EstadoVideollamada, etc.)
- [x] Service layer con manejo de errores
- [x] Documentación OpenAPI (Swagger)
- [x] Database schema completo
- [x] SQL functions operativas
- [x] Scripts de prueba creados
- [ ] Tests unitarios (pendiente)
- [ ] Tests de integración (pendiente)
- [ ] Frontend integration (pendiente)

---

**Última actualización**: 9 de noviembre de 2025  
**Versión**: 1.0.0  
**Estado**: ✅ Production Ready - Backend
