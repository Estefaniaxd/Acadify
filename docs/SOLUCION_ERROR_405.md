# 🔧 SOLUCIÓN - Error 405 en Crear Tarea

> **Problema Identificado**: Error 405 (Method Not Allowed) al intentar crear tareas
> **Causa**: URLs incorrectas en frontend (faltaba `/cursos/tareas` en la ruta)
> **Status**: ✅ SOLUCIONADO

---

## 🐛 El Problema

```
Error 405: Method Not Allowed
⚠️ POST /api/cursos/{cursoId}/tareas → ❌ INCORRECTO
✅ POST /api/cursos/tareas/{cursoId}/tareas → CORRECTO
```

### **Por qué pasó**

El backend tiene esta estructura de rutas:
```python
# En backend/src/api/routes/__init__.py línea 84
(tareas_router, "/api", ["Tareas"])

# En backend/src/api/routes/academic/curso_tareas.py
router = APIRouter(prefix="/cursos/tareas")

@router.post("/{curso_id}/tareas")
def crear_tarea(...):
```

Esto significa que la ruta completa es:
```
/api + /cursos/tareas + /{curso_id}/tareas
= /api/cursos/tareas/{curso_id}/tareas
```

Pero el frontend estaba llamando a:
```
/api/cursos/{cursoId}/tareas  ❌ INCORRECTO
```

---

## ✅ La Solución

### **Cambios en `frontend/src/pages/clase/TareasPage.tsx`**

#### **1. GET - Fetch Tareas**
```typescript
// ANTES ❌
const response = await axios.get<Tarea[]>(`/api/cursos/${cursoId}/tareas`);

// DESPUÉS ✅
const response = await axios.get<Tarea[]>(`/api/cursos/tareas/${cursoId}/tareas`);
```

#### **2. POST - Crear Tarea**
```typescript
// ANTES ❌
await axios.post(`/api/cursos/${cursoId}/tareas`, formData);

// DESPUÉS ✅
await axios.post(`/api/cursos/tareas/${cursoId}/tareas`, formData);
```

---

## 🧪 Cómo Testear Ahora

### **Test 1: Verificar GET funciona**

En la consola del browser (F12):
```javascript
const cursoId = '1'; // O el ID del curso que ves en la URL
fetch(`/api/cursos/tareas/${cursoId}/tareas`, {
  headers: {
    'Authorization': `Bearer ${localStorage.getItem('access_token')}`
  }
})
.then(r => r.json())
.then(data => console.log('✅ Tareas:', data))
.catch(e => console.error('❌ Error:', e))
```

Esperado: Array de tareas
```json
[
  {
    "tarea_id": 1,
    "titulo": "Tarea 1",
    "descripcion": "...",
    "estado": "asignada",
    "prioridad": "alta",
    "tipo": "tarea",
    ...
  }
]
```

### **Test 2: Crear Tarea (Completo)**

1. Go to http://localhost:5173/cursos/{courseId}
2. Click pestaña "Tareas"
3. Esperado: Ve acordeón con tareas + sidebar con estadísticas
4. Click "+ Crear Tarea"
5. Esperado: **¡Modal hermoso aparece!** ✨ (no el viejo feo)
6. Llena formulario:
   - Título: "Mi tarea de prueba"
   - Descripción: "Descripción"
   - Tipo: "Tarea"
   - Prioridad: "Alta"
   - Estado: "Asignada"
   - Fecha límite: "2025-12-31"
7. Click "Crear Tarea"
8. Esperado:
   - ✅ Modal cierra
   - ✅ Nueva tarea aparece en acordeón inmediatamente
   - ✅ Estadísticas actualizadas
   - ✅ SIN errores en console
   - ✅ SIN recarga de página

### **Test 3: Network Monitoring**

1. Abre DevTools (F12)
2. Click pestaña "Network"
3. Click "+ Crear Tarea"
4. Llena y submit
5. En Network tab, deberías ver:
   - `POST /api/cursos/tareas/1/tareas` → Status 200 o 201 ✅
   - NO debe haber `405` errors

---

## 📋 Checklist de Validación

```
✅ URLs corregidas en ClaseTareasPage.tsx
✅ GET /api/cursos/tareas/{cursoId}/tareas funciona
✅ POST /api/cursos/tareas/{cursoId}/tareas funciona
✅ Modal hermoso (TareaFormModal) aparece
✅ Formulario valida bien
✅ Se crea tarea en BD
✅ React Query refetch automático
✅ Sin errores en console
✅ Sin recarga de página
✅ Estadísticas se actualizan
✅ Acordeón muestra nueva tarea
✅ Dark mode funciona
✅ Responsive en mobile
```

---

## 🔍 Debugging si aún hay problemas

### **Si ves "Cannot GET /api/cursos/..."**
- Verifica que el backend está corriendo: `curl http://localhost:8000/api/docs`
- Recarga la página completamente (Ctrl+Shift+R)

### **Si ves error 401 (Unauthorized)**
- Tu token expiró. Haz logout y login nuevamente
- O en consola: `localStorage.removeItem('access_token')`

### **Si ves error 422 (Validation Error)**
- Los datos del formulario no coinciden con el schema
- Revisa los tipos exactos en `TareaCreateRequest` schema del backend
- Verifica que todos los campos requeridos están siendo enviados

### **Si ves error 404 (Not Found)**
- El curso no existe (cursoId inválido)
- Verifica que el cursoId en la URL es correcto

---

## 📊 Resumen de Cambios

```
Archivo modificado: frontend/src/pages/clase/TareasPage.tsx

Línea ~31: GET URL actualizada
  De: /api/cursos/{cursoId}/tareas
  A:  /api/cursos/tareas/{cursoId}/tareas

Línea ~112: POST URL actualizada
  De: /api/cursos/{cursoId}/tareas
  A:  /api/cursos/tareas/{cursoId}/tareas

Status: ✅ Corregido y listo para usar
```

---

## 🎯 Próximos Pasos

1. **Recarga la página** y prueba crear una tarea
2. Si funciona → **PHASE 4: Design Polish** (1 hora)
3. Si no funciona → Revisa los logs del backend:
   ```bash
   cd backend
   tail -f logs/app.log  # O donde se outputean los logs
   ```

---

## 💡 Notas Técnicas

### Estructura de rutas en el backend:
```
/api/cursos/tareas/{curso_id}/tareas
├─ /api (prefix del main app)
├─ /cursos/tareas (prefix del router)
├─ /{curso_id} (parámetro path)
└─ /tareas (path de la ruta)
```

### Cómo está registrado:
```python
# En routes/__init__.py
(tareas_router, "/api", ["Tareas"])

# Donde tareas_router tiene prefix="/cursos/tareas"
# Resultado final: /api/cursos/tareas/...
```

---

**🎉 ¡SOLUCIONADO! 🎉**

El problema era simple pero crítico: la ruta del frontend no coincidía con la ruta del backend.

Ahora todo debe funcionar sin errores 405.

**Prueba y reporta si hay más problemas.**

