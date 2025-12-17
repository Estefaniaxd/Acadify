# 🔴 PROBLEMA: Browser Cache del Frontend

## Diagnóstico

Los logs del backend muestran:
```
[DEBUG REQUEST] Content-Type: application/json - Content-Length: 113
```

Pero el código **ya fue actualizado** a usar `fetch` con FormData. Esto significa:

✅ **El código fuente está correcto**
❌ **El navegador está usando un BUNDLE VIEJO del frontend**

---

## Solución

### Opción 1: Limpiar Cache del Navegador (RÁPIDO)

1. **Abre DevTools** (F12 o Ctrl+Shift+I)
2. **Haz click derecho en el botón "Reload"** (esquina superior izquierda)
3. Selecciona **"Empty cache and hard reload"**
4. Espera a que cargue

**Resultado:**
- ✅ Borra todo el caché del navegador
- ✅ Descarga el bundle nuevo del frontend
- ✅ Los cambios deben aplicarse

---

### Opción 2: Método Nuclear (MÁS SEGURO)

```bash
# En el navegador DevTools Console:
localStorage.clear()      # Limpia tokens
sessionStorage.clear()    # Limpia sesión
location.reload()         # Recarga página
```

Luego:
1. Presiona **Ctrl+Shift+Delete** (abre limpiar datos del navegador)
2. Selecciona:
   - ✅ Cookies
   - ✅ Caché
   - ✅ Archivos almacenados (locales)
3. Rango de tiempo: **Toda la historia**
4. Click en **Limpiar datos**
5. Recarga la página (F5)

---

### Opción 3: Si Usas Vite Dev Server

Si el frontend está corriendo con `npm run dev`:

```bash
# Detén el servidor
Ctrl+C

# Limpia cache de node
rm -rf node_modules/.vite

# Inicia de nuevo
npm run dev
```

El dev server debería recompilarse automáticamente.

---

## ✅ Verificar que Funcionó

### Paso 1: Confirmar que los logs cambiaron

Abre DevTools (F12) → **Network Tab** → Haz click en "Entregar Tarea"

Busca el POST a `/api/cursos/tareas/tareas/XXX/entregar`

**Antes (❌ MALO):**
```
Content-Type: application/json
Content-Length: 113
Body: {"contenido":"..."}
```

**Después (✅ BUENO):**
```
Content-Type: multipart/form-data; boundary=----...
Content-Length: 5432
Body: [FormData con archivo]
```

### Paso 2: Confirmar logs del backend

En la consola del backend deberías ver:

**Antes (❌ MALO):**
```
[DEBUG REQUEST] Content-Type: application/json - Content-Length: 113
```

**Después (✅ BUENO):**
```
[DEBUG REQUEST] Content-Type: multipart/form-data; boundary=... - Content-Length: 5432
```

---

## 🚨 Si Aún No Funciona

Si después de limpiar caché sigue enviando `application/json`, significa que hay **otra instancia de axios o interceptor** que está interfiriendo.

Ejecuta en DevTools Console:

```javascript
// Ver qué URL se está enviando
fetch('/api/cursos/tareas/tareas/9f5df54d-983f-4885-b4e6-2209c7a23d47/entregar', {
  method: 'POST',
  headers: { 'Authorization': 'Bearer ' + localStorage.getItem('access_token') },
  body: new FormData()
})
.then(r => {
  console.log('Status:', r.status);
  console.log('Headers:', Object.fromEntries(r.headers));
  return r.json();
})
.then(d => console.log('Response:', d))
.catch(e => console.error('Error:', e));
```

Si esto funciona pero el formulario no, el problema está en cómo se construye el FormData en `SubirTareaPage.tsx`.

---

## 📋 Checklist

- [ ] Limpiaste cache del navegador (hard reload)
- [ ] Limpiaste localStorage/sessionStorage
- [ ] Recargaste la página
- [ ] Hiciste LOGIN de nuevo
- [ ] Verificaste Network tab que envía multipart/form-data
- [ ] Verificaste logs del backend que dice multipart/form-data
- [ ] Intentaste entregar archivo

---

**Después de todos estos pasos, el error 422 debería desaparecer y la entrega debería funcionar.**
