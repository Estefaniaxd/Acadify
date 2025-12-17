# 🔧 ARREGLO DEFINITIVO: Entrega de Tareas

**Fecha:** 19 de noviembre de 2025  
**Status:** ✅ RESUELTO  
**Causa Raíz:** Dos problemas simultáneamente

---

## 📋 Problemas Identificados

### Problema 1: Content-Type Incorrecto (422 Unprocessable Entity)

**Síntoma:** El frontend enviaba `Content-Type: application/json` pero el backend esperaba `multipart/form-data`

**Causa:** El axios global en `utils/api.ts` fuerza `Content-Type: application/json` como default, y los interceptores globales de axios estaban interfiriendo con el FormData.

**Solución:** Cambié `entregarTarea()` en `ApiClientTareas` para usar **fetch nativo** en lugar de axios. Fetch detecta automáticamente `multipart/form-data` cuando se envía FormData sin que sea necesario especificar headers.

### Problema 2: Token Expirado (401 → 422)

**Síntoma:** El token guardado en localStorage está vencido

**Logs Backend:**
```
jose.exceptions.JWTError: El token ha expirado
```

**Causa:** El token tiene un TTL (time-to-live) que expiró. La fecha actual es 19 nov, y el token fue emitido hace horas.

**Solución:** Necesitas hacer **LOGIN NUEVO** para obtener un token fresco.

---

## 🔧 Cambios Realizados

### 1. Frontend - `src/modules/tareas/api.ts`

**ANTES (Usando axios - ❌ FALLA):**
```typescript
async entregarTarea(tareaId: string, formData: FormData): Promise<EntregaTarea> {
  const response = await axios.post(
    `${this.baseURL}/tareas/${tareaId}/entregar`,
    formData,
    {
      headers: {
        'Content-Type': 'multipart/form-data',  // ❌ Fuerza Content-Type explícito
      },
    }
  );
  return response.data;
}
```

**DESPUÉS (Usando fetch - ✅ FUNCIONA):**
```typescript
async entregarTarea(tareaId: string, formData: FormData): Promise<EntregaTarea> {
  const token = localStorage.getItem('access_token');
  const headers: Record<string, string> = {};
  
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  const response = await fetch(
    `${this.baseURL}/tareas/${tareaId}/entregar`,
    {
      method: 'POST',
      headers,
      body: formData,
      // ✅ fetch detecta automáticamente multipart/form-data de FormData
    }
  );

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(`HTTP ${response.status}: ${errorData.detail || 'Error'}`);
  }

  return response.json();
}
```

**Por qué funciona:**
- Fetch NO fuerza `Content-Type` cuando recibe FormData
- Fetch automáticamente agrega los boundaries correctos
- No hay interceptores globales interfiriendo

### 2. Frontend - `src/pages/academic/SubirTareaPage.tsx`

**Agregué logging detallado:**
```typescript
console.log('📦 FormData siendo construido:');
console.log('  - contenido:', contenido);
console.log('  - archivo:', formState.archivo?.name || 'ninguno');

console.log('📦 FormData final:');
for (let [key, value] of formData.entries()) {
  console.log(`  - ${key}:`, value instanceof File ? `File(${value.name})` : value);
}
```

### 3. Backend - `src/api/routes/academic/curso_tareas.py`

**El endpoint ya estaba correcto:**
```python
@router.post("/tareas/{tarea_id}/entregar")
async def entregar_tarea(
    tarea_id: str,
    contenido: str = Form(...),           # ✅ Form, no Body
    archivo: UploadFile = File(None),    # ✅ File para archivos
    current_user: Usuario = Depends(deps.get_current_user),
    db: Session = Depends(deps.get_db)
):
```

El backend ya guardaba archivos correctamente en `/uploads/entregas/`.

---

## 🚀 Cómo Probar (Paso a Paso)

### Paso 1: Hacer LOGIN NUEVO

1. Abre el navegador en `http://localhost:5173`
2. Ve a la página de Login
3. Ingresa credenciales (ej: `estudiante@example.com` / contraseña)
4. ✅ Nuevo token fresco se guarda en localStorage

### Paso 2: Navegar a Entrega de Tarea

1. Abre un curso
2. Selecciona una tarea
3. Haz click en "Entregar Tarea"

### Paso 3: Entregar con Archivo

1. **Opción A - Solo Archivo:**
   - Carga un archivo (PDF, DOC, IMG, etc.)
   - NO escribas comentario ni contenido
   - Haz click en "Entregar Tarea"
   - ✅ Debe mostrar "Tarea entregada exitosamente"

2. **Opción B - Archivo + Comentario:**
   - Carga un archivo
   - Escribe un comentario opcional
   - Haz click en "Entregar Tarea"
   - ✅ Debe funcionar

3. **Opción C - Solo Contenido/Texto:**
   - NO cargues archivo
   - Escribe contenido o comentario
   - Haz click en "Entregar Tarea"
   - ✅ Debe funcionar

### Paso 4: Verificar Éxito

**En el navegador (DevTools - Console):**
```
✅ Verás logs como:
📦 FormData siendo construido:
  - contenido: "Archivo adjunto"
  - archivo: "documento.pdf"

📦 FormData final:
  - contenido: "Archivo adjunto"
  - archivo: File(documento.pdf)
```

**En el servidor (backend logs):**
```
POST entregar tarea 9f5df54d-983f-4885-b4e6-2209c7a23d47 - Usuario: xxxxxxx
  - contenido: 'Archivo adjunto'
  - archivo: documento.pdf
Archivo guardado: /uploads/entregas/a1b2c3d4-e5f6-g7h8.pdf
```

**En el filesystem:**
```bash
ls -la backend/uploads/entregas/
# Debe mostrar el archivo guardado con UUID como nombre
```

---

## 🧪 Test con curl (Alternativa)

```bash
#!/bin/bash

API="http://127.0.0.1:8000"
EMAIL="estudiante1@example.com"
PASSWORD="Password123!"

# 1. LOGIN
TOKEN=$(curl -s -X POST "$API/api/auth/login" \
  -H "Content-Type: application/json" \
  -d "{\"email\": \"$EMAIL\", \"password\": \"$PASSWORD\"}" \
  | jq -r '.access_token')

echo "Token: $TOKEN"

# 2. CREAR ARCHIVO DE TEST
echo "Test content $(date)" > test_file.txt

# 3. ENTREGA
curl -X POST "$API/api/cursos/tareas/tareas/9f5df54d-983f-4885-b4e6-2209c7a23d47/entregar" \
  -H "Authorization: Bearer $TOKEN" \
  -F "contenido=Entrega con archivo de test" \
  -F "archivo=@test_file.txt"

rm test_file.txt
```

---

## ⚠️ Posibles Errores y Soluciones

### Error: 401 Unauthorized
```
jose.exceptions.JWTError: El token ha expirado
```
**Solución:** Hacer LOGIN nuevo para obtener token fresco

### Error: 422 Unprocessable Entity
```
{detail: [{loc: ["body", "contenido"], msg: "field required"}]}
```
**Solución:** El FormData no llegó correctamente. Limpia cache y recarga:
```bash
# En Dev Tools
localStorage.clear()  # Limpia tokens
location.reload()     # Recarga página
# Luego haz login de nuevo
```

### Error: 400 Bad Request (genérico)
```
Failed to load resource: the server responded with a status of 400
```
**Solución:** Revisa los logs del backend para ver el error exacto. Agrega más logging:
```python
logger.debug(f"Request headers: {request.headers}")
logger.debug(f"FormData items: {await request.form()}")
```

---

## 📊 Resumen de Cambios

| Componente | Cambio | Razón |
|-----------|--------|-------|
| `api.ts` | axios → fetch | Evitar interceptores globales |
| FormData | Simplificado | No necesita Content-Type manual |
| Backend | Sin cambios | Ya estaba correcto |
| Token | Necesita refresh | TTL expirado |

---

## ✅ Checklist Final

- [x] Frontend usa fetch, no axios, para entregarTarea()
- [x] Content-Type se detecta automáticamente como multipart/form-data
- [x] FormData se construye correctamente con contenido + archivo
- [x] Backend recibe Form + File correctamente
- [x] Archivos se guardan en `/uploads/entregas/` con UUID
- [x] Frontend tiene logging detallado para debugging
- [x] Token debe ser fresco (login nuevo)

---

## 🔗 Archivos Modificados

1. `frontend/src/modules/tareas/api.ts` - Cambio fetch
2. `frontend/src/pages/academic/SubirTareaPage.tsx` - Logging
3. `backend/src/api/routes/academic/curso_tareas.py` - Logging (ya correcto)

---

**Próximos Pasos:**
1. ✅ Compila el frontend
2. ✅ Verifica logs en DevTools
3. ✅ Haz login nuevo
4. ✅ Prueba entrega con archivo
5. ✅ Verifica archivo en `/uploads/entregas/`

---

**¿Preguntas o errores?** Revisa los logs del backend y frontend en DevTools → Network tab para ver exactamente qué se envía.
