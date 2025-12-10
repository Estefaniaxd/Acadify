# 🔬 DIAGNÓSTICO PROFUNDO - 6 Archivos Pero Solo 1 Se Registra

**Fecha**: 21 de noviembre 2025  
**Caso de prueba**: 6 archivos subidos  
**Resultado**: Solo 1 se registra ❌

---

## 🎯 Hipótesis a Probar

### Hipótesis 1: Frontend no envía 6 archivos
**Síntoma**: `archivos.forEach()` solo agrega 1 vez  
**Check**: Ver en DevTools Network → FormData

### Hipótesis 2: Backend no recibe 6 archivos
**Síntoma**: `archivos: List[UploadFile]` es None o tiene 1  
**Check**: Ver logs del backend (línea LOG CRÍTICO)

### Hipótesis 3: Backend no procesa todos los archivos
**Síntoma**: Loop for solo itera 1 vez  
**Check**: Ver logs "Procesando archivo [X]"

### Hipótesis 4: Archivos se guardan en disco pero no en metadata
**Síntoma**: `/uploads/entregas/` tiene 6 pero BD tiene 1  
**Check**: Ver logs "Guardado en disco" vs "Metadata guardada"

### Hipótesis 5: Metadata se crea pero no se serializa correctamente
**Síntoma**: `archivos_metadata` tiene 6 pero JSON es inválido  
**Check**: Ver logs cuando pasa a service

### Hipótesis 6: Service recibe metadata pero no la usa
**Síntoma**: `archivos_metadata` recibido pero `archivos_json` tiene 1  
**Check**: Ver logs en `tarea_service.entregar_tarea()`

---

## 📊 ANTES DE RESTART - Cambios Hechos

### En `curso_tareas.py`
1. ✅ Cambié `File(default=[])` a `File(default=None)`
2. ✅ Agregué logging detallado en POST inicio (muestra cada archivo)
3. ✅ Agregué logging en cada paso del loop
4. ✅ Agregué manejo de `None` para archivos

### En `tarea_service.py` (ya había hecho)
1. ✅ Cambié `obtener_entrega()` para usar SOLO `archivos_adicionales`

---

## 🚀 CÓMO HACER DIAGNÓSTICO

### PASO 1: Restart Backend

```bash
lsof -ti:8000 | xargs kill -9 2>/dev/null
sleep 2
cd /run/media/arch/Storage/SENA/Proyecto-Formativo/Acadify/backend
python -m uvicorn src.main:app --reload --host 127.0.0.1 --port 8000
```

**Mantén esta terminal abierta** para ver logs en tiempo real

### PASO 2: Abre DevTools del navegador

```
Chrome/Firefox:
F12 → Network tab → XHR filter
```

### PASO 3: Upload 6 archivos

1. Abre http://localhost:5173
2. Entra a una tarea
3. Upload: doc1.pdf, doc2.pdf, doc3.pdf, doc4.pdf, doc5.pdf, doc6.pdf
4. **Verifica en DevTools**:
   - Tab Network → POST /tareas/123/entregar
   - Click → Form Data
   - ¿Cuántos `archivos` ves? (debe ser 6)

### PASO 4: Click "Entregar Tarea"

1. Observa en **terminal del backend** los logs
2. Busca estos logs en ORDEN:
   ```
   📥 POST /tareas/.../entregar - Usuario: ...
      ⚠️ DIAGNÓSTICO CRÍTICO:
      - Type de archivos: <class 'list'>
      - Archivos recibidos: 6  ← DEBERÍA SER 6
      [1] doc1.pdf - Size: ...
      [2] doc2.pdf - Size: ...
      ...
      [6] doc6.pdf - Size: ...
      
      ✅ INICIANDO PROCESAMIENTO DE ARCHIVOS
      ✅ Hay 6 archivos para procesar
      
      📄 [1] Procesando archivo: doc1.pdf
         ✅ Guardado en disco: /path/.../uuid1.pdf
         ✅ Metadata guardada: doc1.pdf
      
      📄 [2] Procesando archivo: doc2.pdf
         ✅ Guardado en disco: /path/.../uuid2.pdf
         ✅ Metadata guardada: doc2.pdf
      
      ... (continúa para 3-6)
      
      ✅ PROCESAMIENTO COMPLETADO: 6 archivos procesados
      📤 Llamando a tarea_service.entregar_tarea() con 6 archivos...
         - archivo_urls: ["/uploads/entregas/uuid1.pdf", ...]  ← 6 URLs
         - archivos_metadata: [...]  ← 6 items
   ```

### PASO 5: Interpreta los logs

**Si ves**:
- `Archivos recibidos: 6` ✅ → Backend SÍ recibe 6
- `[1] doc1.pdf`, `[2] doc2.pdf`, etc. ✅ → Backend SÍ ve los 6
- `Guardado en disco: 6 veces` ✅ → Backend SÍ guarda 6 en disco
- `PROCESAMIENTO COMPLETADO: 6 archivos` ✅ → Loop procesa los 6

**Si ves**:
- `Archivos recibidos: 1` ❌ → Frontend solo envió 1
- `[1] doc1.pdf` (no [2], [3], etc.) ❌ → Backend recibe solo 1
- `Guardado en disco: 1 vez` ❌ → Loop no itera 5 veces más
- `PROCESAMIENTO COMPLETADO: 1 archivos` ❌ → Problema en backend

---

## 🔍 Interpretación según Resultado

### Escenario A: `Archivos recibidos: 1`

**Diagnóstico**: Problema en FRONTEND o FASTAPI parsing

**Prueba**:
```python
# En DevTools Console:
const input = document.querySelector('input[type="file"]');
console.log("Files selected:", input.files.length);

# Si dice 6, pero backend recibe 1:
#   → Problema en FormData.append() o axios
```

**Solución**:
```typescript
// Debug FormData en frontend:
const formData = new FormData();
formData.append('contenido', 'test');
archivos.forEach((archivo, i) => {
    console.log(`Appending archivo ${i}: ${archivo.file.name}`);
    formData.append('archivos', archivo.file);
});
console.log("FormData entries:", Array.from(formData.entries()));
```

### Escenario B: `Archivos recibidos: 6` pero logs no muestran [2], [3], etc.

**Diagnóstico**: `for archivo in archivos:` tiene error

**Prueba**: Backend debería mostrar `[1] doc1.pdf`, `[2] doc2.pdf`, etc.

### Escenario C: `Guardado en disco: 1` aunque recibe 6

**Diagnóstico**: Error en `with open()` después de [1]

**Prueba**: Debería ver `✅ Guardado en disco` 6 veces, no 1

### Escenario D: Todo dice 6, pero BD solo tiene 1

**Diagnóstico**: Problema en `tarea_service.entregar_tarea()` o DB insert

**Prueba**: Ver logs del service (siguiente paso)

---

## 📋 Logs del Service (Si necesitas profundizar más)

Si los logs del POST dicen 6, pero BD tiene 1, necesitamos ver qué pasa en el service. Agregué logging ahí también:

En `tarea_service.py` línea 475-520, busca estos logs:

```
if archivos_metadata and len(archivos_metadata) > 0:
    # Usar metadata completa que incluye nombre original
    archivos_json = json.dumps({"archivos": archivos_metadata})
    # LOG: ¿Cuántos items en archivos_metadata?
```

---

## 📝 Plan de Acción Resumido

1. **Restart backend** con nuevo código
2. **Upload 6 archivos**
3. **Entrega tarea**
4. **Revisa terminal backend**:
   - ¿Dice `Archivos recibidos: 6`?
     - SÍ → Salta a Escenario B/C/D
     - NO → Salta a Escenario A
5. **Según resultado** → Aplica solución

---

## ⚠️ Posibles Causas Ocultas

### 1. Límite de archivos en FastAPI
FastAPI tiene un límite de request body (~16 MB default)
- 6 archivos grandes podrían exceder
- Solución: Aumentar en `main.py`

### 2. Límite en Form parsing
```python
# En main.py:
app = FastAPI()
# Agregar:
MAX_UPLOAD_SIZE = 100 * 1024 * 1024  # 100MB
```

### 3. Problema en axios/apiClient
El cliente podría estar configurado para no enviar múltiples archivos

### 4. CORS o middleware bloqueando
Rara vez, pero posible

---

## 🎯 TL;DR

**Haz esto ahora**:

```bash
# 1. Restart backend
lsof -ti:8000 | xargs kill -9 2>/dev/null; sleep 2
cd backend
python -m uvicorn src.main:app --reload --host 127.0.0.1 --port 8000

# 2. Upload 6 archivos en navegador
# 3. Entregar tarea
# 4. Copia los LOGS del terminal del backend
# 5. Envía los logs aquí
```

Los logs dirán exactamente dónde está el problema ✓

