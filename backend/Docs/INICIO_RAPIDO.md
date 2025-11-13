# 🚀 Guía de Inicio Rápido - API de IA y Gamificación

## ✅ Estado Actual

**🎉 Sistema completamente implementado y listo para usar**

- ✅ Backend: 7 endpoints RESTful funcionando
- ✅ Servicios: GeminiService, PuntosService, TareaService
- ✅ Schemas: 15+ modelos Pydantic con validación
- ✅ Tests: 13/13 pasando
- ✅ Documentación: Completa

---

## 📋 Requisitos Previos

1. Python 3.10+
2. PostgreSQL con base de datos creada
3. Redis (para caché y rate limiting)
4. Google Gemini API Key (obtener en: https://makersuite.google.com/app/apikey)

---

## 🔧 Configuración Inicial

### 1. Variables de Entorno

Edita el archivo `.env` en la carpeta `backend/`:

```env
# Base de datos
DATABASE_URL=postgresql://usuario:contraseña@localhost:5432/acadify

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0

# Google Gemini AI
GEMINI_API_KEY=tu_api_key_aqui

# JWT
SECRET_KEY=tu_secret_key_aqui
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Configuración de la aplicación
ENVIRONMENT=development
DEBUG=True
```

### 2. Instalar Dependencias

```bash
cd backend
pip install -r requirements.txt
```

### 3. Ejecutar Migraciones

```bash
alembic upgrade head
```

---

## 🚀 Iniciar el Servidor

### Opción 1: Modo Desarrollo (con auto-reload)

```bash
cd backend
python -m uvicorn src.main:app --reload --port 8000
```

### Opción 2: Modo Producción

```bash
cd backend
python -m uvicorn src.main:app --host 0.0.0.0 --port 8000 --workers 4
```

**Salida esperada**:
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [12345] using StatReload
INFO:     Started server process [12346]
INFO:     Waiting for application startup.
✅ routes/__init__.py: 8 routers cargados
✅ Router IA y Gamificación cargado con 7 rutas
INFO:     Application startup complete.
```

---

## 📖 Acceder a la Documentación

Una vez iniciado el servidor, abre tu navegador en:

### Swagger UI (Interactivo)
```
http://localhost:8000/docs
```

### ReDoc (Alternativa)
```
http://localhost:8000/redoc
```

### OpenAPI JSON
```
http://localhost:8000/openapi.json
```

---

## 🧪 Probar los Endpoints

### 1. Health Check (Sin autenticación)

```bash
curl http://localhost:8000/api/ia/health
```

**Respuesta esperada**:
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

### 2. Obtener Token de Autenticación

**Primero, necesitas crear un usuario o usar uno existente.**

```bash
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "correo_institucional": "estudiante@example.com",
    "password": "tu_password"
  }'
```

**Respuesta**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**Guarda este token para las siguientes solicitudes.**

### 3. Entregar una Tarea con IA

#### Opción A: Solo texto

```bash
curl -X POST "http://localhost:8000/api/cursos/{curso_id}/tareas/{tarea_id}/entregas" \
  -H "Authorization: Bearer TU_TOKEN_AQUI" \
  -F "contenido_texto=Mi solución al ejercicio de funciones en Python"
```

#### Opción B: Con archivo

```bash
curl -X POST "http://localhost:8000/api/cursos/{curso_id}/tareas/{tarea_id}/entregas" \
  -H "Authorization: Bearer TU_TOKEN_AQUI" \
  -F "contenido_texto=Adjunto mi solución" \
  -F "archivo=@/path/to/tarea.py"
```

**Respuesta esperada** (201 Created):
```json
{
  "success": true,
  "message": "Entrega procesada exitosamente con IA. ¡Felicidades! Has obtenido 70 puntos.",
  "data": {
    "entrega_id": "abc-123",
    "intentos": 1,
    "es_tardia": false,
    "fecha_entrega": "2024-01-20T15:30:00Z",
    "retroalimentacion_ia": {
      "analisis_general": "Excelente trabajo...",
      "calificacion": 4.5,
      "fortalezas": ["Código limpio", "Buena documentación"],
      "areas_mejora": ["Agregar validaciones"]
    },
    "puntos": {
      "puntos_base": 50,
      "puntos_bonificacion": 20,
      "puntos_totales": 70
    },
    "gamificacion": {
      "puntos_otorgados": 70,
      "puntos_acumulados": 170,
      "nivel_actual": "Bronce II",
      "nuevas_insignias": []
    }
  }
}
```

### 4. Ver Mis Puntos

```bash
curl -X GET "http://localhost:8000/api/usuarios/mi-ranking" \
  -H "Authorization: Bearer TU_TOKEN_AQUI"
```

### 5. Ver Ranking Global

```bash
curl -X GET "http://localhost:8000/api/usuarios/ranking?limite=10" \
  -H "Authorization: Bearer TU_TOKEN_AQUI"
```

---

## 🧪 Usar Swagger UI (Recomendado)

La forma más fácil de probar los endpoints es usando Swagger UI:

1. Abre http://localhost:8000/docs
2. Click en **"Authorize"** (candado verde)
3. Ingresa tu token: `Bearer TU_TOKEN_AQUI`
4. Click en **"Authorize"** y luego **"Close"**
5. Ahora puedes probar cualquier endpoint:
   - Click en el endpoint que quieras probar
   - Click en **"Try it out"**
   - Completa los parámetros
   - Click en **"Execute"**
   - Ve la respuesta abajo

---

## 🔍 Verificar que Todo Funciona

### Script de Verificación

```bash
cd backend
python scripts/verificar_api_sintaxis.py
```

**Salida esperada**:
```
✓ TODAS LAS VERIFICACIONES PASARON
API Routes lista para usar.
```

### Ejecutar Tests

```bash
cd backend
python scripts/test_schemas.py
python scripts/test_gemini_simple.py
python scripts/test_puntos_service.py
```

**Todos deben pasar** (✅).

---

## 📊 Estructura de los Endpoints

```
/api
├── /cursos/{curso_id}/tareas/{tarea_id}
│   ├── POST /entregas                    # Entregar tarea con IA
│   └── GET  /estadisticas-ia             # Estadísticas (docentes)
├── /entregas/{entrega_id}
│   └── GET  /retroalimentacion           # Ver feedback de IA
├── /usuarios
│   ├── GET  /{usuario_id}/puntos         # Ver puntos de usuario
│   ├── GET  /ranking                     # Ranking global
│   └── GET  /mi-ranking                  # Mi posición
└── /ia
    └── GET  /health                      # Health check
```

---

## 🎯 Flujo Típico de Uso

### Para Estudiantes:

1. **Autenticarse** → `POST /auth/login`
2. **Ver curso y tarea** → `GET /api/cursos/{id}/tareas`
3. **Entregar tarea** → `POST /api/cursos/{curso_id}/tareas/{tarea_id}/entregas`
4. **Ver retroalimentación** → `GET /api/entregas/{entrega_id}/retroalimentacion`
5. **Ver mis puntos** → `GET /api/usuarios/mi-ranking`
6. **Ver ranking** → `GET /api/usuarios/ranking`

### Para Docentes:

1. **Autenticarse** → `POST /auth/login`
2. **Crear tarea con IA habilitada** → `POST /api/cursos/{id}/tareas`
3. **Ver estadísticas de entregas** → `GET /api/cursos/{curso_id}/tareas/{tarea_id}/estadisticas-ia`
4. **Ver retroalimentación de estudiantes** → `GET /api/entregas/{entrega_id}/retroalimentacion`

---

## ⚙️ Configuración de Tareas con IA

Cuando crees una tarea, asegúrate de configurar:

```json
{
  "titulo": "Introducción a Python",
  "descripcion": "Crear un programa que...",
  "puntos_base": 50,
  "puntos_bonificacion": 20,
  "habilitar_retroalimentacion_ia": true,
  "rubrica": {
    "Funcionalidad": {
      "peso": 40,
      "descripcion": "El código funciona correctamente"
    },
    "Estilo": {
      "peso": 30,
      "descripcion": "Código limpio y legible"
    },
    "Documentación": {
      "peso": 30,
      "descripcion": "Comentarios y docstrings"
    }
  }
}
```

---

## 🐛 Troubleshooting

### Error: "GEMINI_API_KEY no configurada"

**Solución**: Agrega tu API Key en `.env`:
```env
GEMINI_API_KEY=AIza...tu_key_aqui
```

### Error: "Database connection failed"

**Solución**: Verifica que PostgreSQL esté corriendo y que `DATABASE_URL` en `.env` sea correcta.

### Error: "Redis connection failed"

**Solución**: 
- Inicia Redis: `redis-server`
- O desactiva Redis en desarrollo (edita `src/core/config.py`)

### Error: "404 Not Found" en endpoints

**Solución**: Verifica que el servidor esté corriendo y que uses el prefix correcto (`/api/...`).

### Error: "413 Request Entity Too Large"

**Solución**: El archivo es mayor a 50MB. Reduce el tamaño o comprime el archivo.

### Error: "415 Unsupported Media Type"

**Solución**: El formato de archivo no está soportado. Usa: PDF, Word, Excel, imágenes, código.

---

## 📚 Más Documentación

- **API Completa**: `backend/Docs/API_IA_GAMIFICACION.md`
- **Arquitectura Técnica**: `backend/Docs/SISTEMA_IA_GAMIFICACION.md`
- **Resumen de Implementación**: `backend/Docs/RESUMEN_IMPLEMENTACION.md`

---

## 💡 Tips

1. **Usa Swagger UI** para explorar y probar los endpoints fácilmente
2. **Revisa los logs** si algo falla: el servidor imprime mensajes detallados
3. **Los archivos grandes** tardan más en analizarse (Gemini AI puede tardar 5-10 segundos)
4. **Las estadísticas de docentes** solo se actualizan cuando hay entregas
5. **Los puntos negativos no son posibles**: el mínimo siempre es 0

---

## 🎉 ¡Listo!

Si llegaste hasta aquí y todo funciona:

```
✅ Backend funcionando
✅ Endpoints respondiendo
✅ IA analizando entregas
✅ Puntos y gamificación activos
✅ Documentación accesible
```

**¡Felicidades! El sistema está operativo. 🚀**

---

**Versión**: 1.0  
**Última actualización**: 20 de Enero, 2024  
**Soporte**: Acadify Team
