# 🔍 Instrucciones para Debuggear "Entregar Tarea"

**Última actualización**: 19 de noviembre 2025  
**Problema**: El endpoint devuelve 422 cuando se intenta entregar una tarea  
**Síntoma**: `Content-Type: text/plain;charset=UTF-8` en lugar de `multipart/form-data`

## 📋 Pasos

### 1. **Hard Refresh del Frontend** (limpiar cache compilado)

```bash
# En el navegador:
Ctrl + Shift + R  (Windows/Linux)
Cmd + Shift + R   (Mac)
```

O en DevTools:
- F12 → Settings → Network → ✅ "Disable cache (while DevTools is open)"

### 2. **Login fresco**

- Ve a http://localhost:5173
- Login con: `seed_a99e64_a3008df6@test.unan.local` / `password123`
- Espera a que cargue el dashboard

### 3. **Abre DevTools console**

```
F12 → Console tab
```

### 4. **Navega a la página de "Entregar Tarea"**

- Busca un curso
- Abre una tarea
- Click en "Entregar Tarea"

### 5. **Selecciona un archivo y haz submit**

- Selecciona un archivo pequeño (PDF, txt, doc, etc.)
- Click en "Entregar Tarea"

### 6. **Copia los logs del navegador**

En DevTools Console, busca los mensajes que empiezan con:
- `🔍 ENTREGAR TAREA - ANTES DE FETCH:`
- `🔍 FETCH CONFIG:`
- `🔍 RESPONSE STATUS:`

Copia TODO eso.

### 7. **Copia los logs del backend**

En la terminal donde corre el backend, busca logs con:
- `🔍 ENTREGAR TAREA - ENDPOINT RECIBIDO:`
- `🔍 PARÁMETRO CONTENIDO`
- `🔍 PARÁMETRO ARCHIVO`
- `✅ Archivo guardado:` o `❌ Error guardando archivo:`

Copia TODO eso también.

### 8. **Pega ambos logs en tu respuesta**

Estructura:

```
FRONTEND LOGS:
🔍 ENTREGAR TAREA - ANTES DE FETCH:
...

BACKEND LOGS:
2025-11-19 XX:XX:XX - 🔍 ENTREGAR TAREA - ENDPOINT RECIBIDO:
...
```

## 🎯 Qué estamos buscando

| Problema | Síntoma | Solución |
|----------|---------|----------|
| FormData se convierte a JSON | `Content-Type: application/json` | Debug en fetch |
| FormData se envía como texto | `Content-Type: text/plain` | Ver por qué |
| Archivo no se incluye | `archivo is None` en backend | Verificar FormData append |
| Backend no recibe contenido | `contenido` vacío | Verificar field names |

## 🛠️ URLs Clave

- Frontend: http://localhost:5173
- Backend: http://localhost:8000
- API Endpoint: `POST /api/cursos/tareas/{tarea_id}/entregar`

## 📝 Notas

- El endpoint espera **FormData** con:
  - `contenido` (string, requerido)
  - `archivo` (File, opcional)
- NO debe enviarse `application/json`
- fetch() debe detectar automáticamente `multipart/form-data`

---

**Si todo funciona**: Verás `✅ Archivo guardado:` en los logs del backend y `HTTP 200` o `HTTP 201` en el frontend.

**Si sigue fallando**: Los logs te dirán exactamente en qué punto se pierde el FormData.
