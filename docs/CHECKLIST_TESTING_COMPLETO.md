# ✅ CHECKLIST DE IMPLEMENTACIÓN Y TESTING

**Última actualización**: 21 de noviembre de 2025 - 15:45

---

## 📋 FASE 1: VERIFICACIÓN DE CÓDIGO (Ya hecho)

- [x] Backend Cambio #1: `tarea_service.py` línea 520 retorna `archivos_metadata`
- [x] Backend Cambio #2: `tarea_service.py` línea 700 usa UPDATE en lugar de DELETE
- [x] Frontend: Color amarillo → azul en archivos de referencia
- [x] Frontend: Etiqueta "referencia" removida
- [x] Frontend: Botón X agregado en referencia (con función eliminar)
- [x] Frontend: Función `handleDescargarArchivo()` agregada
- [x] Frontend: Archivos POST-ENTREGA usan mismo diseño PRE-ENTREGA

---

## 🔧 FASE 2: INICIO DEL BACKEND (SIGUIENTE)

### Paso 1: Matar proceso viejo
```bash
lsof -ti:8000 | xargs kill -9 2>/dev/null; sleep 2; echo "✅ Puerto liberado"
```
**Esperado**: `✅ Puerto liberado`

### Paso 2: Verificar que puerto está libre
```bash
lsof -i :8000
```
**Esperado**: Nada (vacío)

### Paso 3: Iniciar backend con reload
```bash
cd /run/media/arch/Storage/SENA/Proyecto-Formativo/Acadify/backend
python -m uvicorn src.main:app --reload --host 127.0.0.1 --port 8000
```
**Esperado**: 
```
Uvicorn running on http://127.0.0.1:8000
Application startup complete
```

### Paso 4: Mantener terminal abierta
- ⚠️ NO cerrar esta terminal
- ⚠️ Los logs aparecerán aquí
- ⚠️ Si hay error, vemos aquí

---

## 🧪 FASE 3: TEST #1 - Entrega Múltiple con Nombres Reales

**Objetivo**: Verificar que POST-ENTREGA muestra 2 archivos con nombres reales

### Pre-test
- [ ] Backend está corriendo (paso anterior)
- [ ] Frontend está en `http://localhost:5173`
- [ ] Estás logueado como estudiante
- [ ] Tienes acceso a al menos una tarea

### Test Steps
1. [ ] Abre una tarea cualquiera
2. [ ] En la sección "Subir archivo", haz click
3. [ ] Selecciona **"documento1.pdf"** (o archivo que tengas)
   - Debería aparecer card con: `📄 documento1.pdf | 0.XX MB | [X]`
4. [ ] Haz click en "Agregar más archivos"
5. [ ] Selecciona **"documento2.docx"** (o segundo archivo)
   - Debería aparecer SEGUNDA card: `📄 documento2.docx | 0.XX MB | [X]`
6. [ ] Haz click en botón **"Entregar Tarea"**
   - Debería mostrar toast: "¡Tarea entregada exitosamente!"
7. [ ] Espera a que recargue

### Verificación POST-ENTREGA
- [ ] **¿Se muestran 2 archivos o solo 1?**
  - [ ] 2 archivos (✅ CORRECTO)
  - [ ] 1 archivo (❌ PROBLEMA)
  - [ ] 0 archivos (❌ PROBLEMA)

- [ ] **¿Los nombres son reales o UUIDs?**
  - [ ] "documento1.pdf" (✅ CORRECTO)
  - [ ] "abc123def456.pdf" (❌ PROBLEMA - UUID)

- [ ] **¿Se pueden descargar?**
  - Hover sobre archivo → ¿Aparece botón descarga?
  - Click descarga → ¿Se descarga el archivo?
  - [ ] SÍ descarga (✅ CORRECTO)
  - [ ] NO descarga (❌ PROBLEMA)

- [ ] **¿Se muestra tamaño del archivo?**
  - [ ] SÍ (ej: "0.50 MB") (✅ CORRECTO)
  - [ ] NO (❌ PROBLEMA)

### Si TODOS los ✅ pasan
→ Ir a **TEST #2**

### Si ALGÚN ❌ falla
→ Ver sección **"DEBUGGING"** abajo

---

## 🧪 FASE 4: TEST #2 - Cancelar y Cambiar Archivos

**Objetivo**: Verificar que se pueden eliminar archivos de referencia

### Pre-test
- [ ] TEST #1 pasó exitosamente
- [ ] Entrega está en pantalla con 2 archivos

### Test Steps
1. [ ] Haz click en botón **"Cancelar Entrega"** (debajo de archivos)
   - Debería mostrar confirm: "¿Estás seguro..."
2. [ ] Confirma
   - Debería mostrar toast: "Entrega cancelada"
3. [ ] Espera a que recargue

### Verificación ARCHIVOS DE REFERENCIA
- [ ] **¿Se muestran los 2 archivos anteriores?**
  - [ ] SÍ, 2 archivos (✅ CORRECTO)
  - [ ] NO (❌ PROBLEMA)

- [ ] **¿De qué color están?**
  - [ ] AZUL como archivos normales (✅ CORRECTO)
  - [ ] AMARILLO (❌ PROBLEMA - no se aplicó cambio)

- [ ] **¿Tienen botón X (eliminar)?**
  - Hover sobre archivo → ¿Aparece X?
  - [ ] SÍ, aparece X (✅ CORRECTO)
  - [ ] NO (❌ PROBLEMA)

- [ ] **¿Está la etiqueta "Archivos de entrega anterior (referencia):"?**
  - [ ] NO aparece (✅ CORRECTO - la removimos)
  - [ ] SÍ aparece (❌ PROBLEMA - cambio no se aplicó)

### Continuar Test
4. [ ] Haz click en botón X del PRIMER archivo
   - Debería mostrar toast: "Archivo eliminado"
5. [ ] Verifica que queda 1 solo archivo
   - [ ] 1 archivo (✅ CORRECTO)

6. [ ] En sección "Subir archivo", agrega nuevo: **"documento3.pdf"**
   - Debería aparecer en cards: "documento3.pdf"

7. [ ] Haz click **"Entregar Tarea"**

### Verificación POST-REENTREGA
- [ ] **¿Se muestra 1 archivo (documento3.pdf)?**
  - [ ] SÍ (✅ CORRECTO)
  - [ ] 2 archivos (❌ PROBLEMA - no eliminó referencia)
  - [ ] UUID (❌ PROBLEMA - nombres reales)

### Si TODOS los ✅ pasan
→ Ir a **TEST #3**

---

## 🧪 FASE 5: TEST #3 - Persistencia en Recarga

**Objetivo**: Verificar que archivos persisten al recargar página

### Pre-test
- [ ] TEST #2 pasó exitosamente
- [ ] Entrega en pantalla con 1 archivo (documento3.pdf)

### Test Steps
1. [ ] Recarga página (F5 o Ctrl+R)
2. [ ] Espera a que cargue

### Verificación
- [ ] **¿Se muestra el archivo (documento3.pdf)?**
  - [ ] SÍ (✅ CORRECTO)
  - [ ] NO (❌ PROBLEMA - no persiste)

- [ ] **¿El nombre es "documento3.pdf" (no UUID)?**
  - [ ] SÍ (✅ CORRECTO)
  - [ ] UUID (❌ PROBLEMA)

- [ ] **¿Se puede descargar?**
  - [ ] SÍ (✅ CORRECTO)
  - [ ] NO (❌ PROBLEMA)

### Si TODOS los ✅ pasan
→ **🎉 TODOS LOS TESTS PASARON**

---

## 🚨 DEBUGGING - Si algo falla

### Problema: "Solo veo 1 archivo en lugar de 2"

**Causa probable**: Backend solo guarda 1 archivo

**Verificación**:
1. Abre **Developer Tools** (F12)
2. Ve a **Console**
3. Después de entregar, busca logs
4. Verifica respuesta del POST:
   ```
   Response JSON:
   {
     "data": {
       "archivos": [...]  ← ¿Cuántos items?
     }
   }
   ```

**Solución**:
- Si `archivos` tiene solo 1 item → Problema en backend
- Si `archivos` tiene 2 items pero frontend muestra 1 → Problema en frontend renderizado

---

### Problema: "Los nombres son UUID, no reales"

**Causa probable**: Cambio #1 (línea 520) no se aplicó

**Verificación**:
```bash
# Terminal backend:
grep -n "archivos_metadata or" backend/src/services/academic/tarea_service.py
```
**Esperado**:
```
520:                    "archivos": archivos_metadata or []
```

**Si no está**:
1. Abre archivo manualmente
2. Busca línea ~520
3. Verifica que dice `archivos_metadata or []` (no `archivo_urls`)
4. Si está `archivo_urls`, cambia manualmente
5. Reinicia backend

---

### Problema: "Color de referencia sigue siendo AMARILLO"

**Causa probable**: Cambio en línea 710 no se aplicó

**Verificación**:
```bash
# Terminal:
grep -n "bg-blue-50\|bg-amber-50" frontend/src/pages/tareas/SubirTareaPage.tsx | grep -A2 -B2 "referencia"
```

**Si dice `bg-amber-50`**:
1. Abre archivo
2. Busca "archivos de entrega anterior"
3. Cambia `amber` por `blue` en los 4 lugares:
   - `bg-amber-50` → `bg-blue-50`
   - `bg-amber-900/10` → `bg-blue-900/10`
   - `border-amber-200` → `border-blue-200`
   - `border-amber-800/40` → `border-blue-800/40`
   - `text-amber-600` → `text-blue-600`
4. Recarga página

---

### Problema: "No puedo eliminar archivo con X"

**Causa probable**: Botón X no tiene onClick handler

**Verificación**:
```bash
# Terminal:
grep -A5 "onClick={() => {" frontend/src/pages/tareas/SubirTareaPage.tsx | grep -B2 -A2 "nuevosArchivos"
```

**Si no aparece**:
1. Busca la sección de referencia en SubirTareaPage.tsx
2. En el botón X, verifica que tenga:
   ```typescript
   onClick={() => {
     const nuevosArchivos = entregaExistente.archivos.filter(...);
     setEntregaExistente({...});
     toast.success('Archivo eliminado');
   }}
   ```

---

## 📊 Tabla de Resultados

Después de completar los 3 tests, llena esta tabla:

| Test | Objetivo | Resultado | Notas |
|------|----------|-----------|-------|
| #1 | 2 archivos con nombres reales | ✅ / ❌ | |
| #1 | Descargas funcionan | ✅ / ❌ | |
| #2 | Archivos referencia en azul | ✅ / ❌ | |
| #2 | Botón X elimina | ✅ / ❌ | |
| #2 | Reentrega solo nuevo archivo | ✅ / ❌ | |
| #3 | Recarga persiste archivos | ✅ / ❌ | |
| #3 | Nombres reales después recarga | ✅ / ❌ | |

---

## 🎯 Esperado FINAL

✅ TEST 1: "Entrego 2 archivos, veo 2 archivos con nombres reales"
✅ TEST 2: "Cancelo, veo azul, elimino 1, entrego nuevo, veo solo el nuevo"
✅ TEST 3: "Recargo página, archivos siguen ahí"

---

**Estado**: 🟡 EN PROGRESO - Esperando backend restart y testing
**Responsable**: Usuario
**Tiempo estimado**: 15 minutos
