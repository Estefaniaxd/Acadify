# 🔥 DIAGNÓSTICO PROFUNDO: "Solo 1 archivo se registra de 6"

**Fecha**: 21 de noviembre 2025  
**Problema**: Upload 6 archivos → Solo 1 se registra + UUID en lugar de nombre  
**Estado**: BAJO INVESTIGACIÓN CON LOGGING DETALLADO

---

## 📋 Lo que pasó

1. ✅ Subiste 6 archivos
2. ✅ El frontend muestra 6 archivos con sus nombres reales
3. ❌ Entregas la tarea
4. ❌ Ahora solo ves 1 archivo
5. ❌ El nombre es UUID (cadena de caracteres) no el nombre real

---

## 🔍 Posibles Causas (hipótesis)

### Hipótesis 1: Frontend no envía todos en FormData
**Síntomas**: Backend recibe solo 1
**Probabilidad**: BAJA (ya verificamos el código)

### Hipótesis 2: Backend guarda solo 1 en disco
**Síntomas**: Las carpetas `/uploads/entregas` tendría solo 1 archivo
**Probabilidad**: MEDIA (pero unlikely si no hay errores)

### Hipótesis 3: Backend guarda en BD solo 1 archivo en JSON
**Síntomas**: Campo `archivos_adicionales` tendría solo 1 archivo
**Probabilidad**: ALTA (¡ESTA ES LA PROBABLE!)

### Hipótesis 4: Frontend renderiza solo 1 de los que recibe
**Síntomas**: GET retorna 6 pero UI muestra solo 1
**Probabilidad**: BAJA (hemos visto el código del map)

### Hipótesis 5: Hay conflicto con archivos de "referencia" del cancel anterior
**Síntomas**: Al cancelar, los archivos anteriores interfieren con los nuevos
**Probabilidad**: MEDIA (es un buen punto)

---

## 🛠️ Cambios Realizados para Diagnóstico

He agregado **LOGGING DETALLADO** en dos puntos críticos:

### 1️⃣ En `curso_tareas.py` - POST endpoint

**Lo que loguea ahora**:
```
📥 POST /tareas/{tarea_id}/entregar
   ⚠️ DIAGNÓSTICO CRÍTICO:
   - Type de archivos: <class 'list'> 
   - Archivos recibidos: 6  ← CUÁNTOS RECIBE
      [1] archivo_1.txt - Size: 0 bytes
      [2] archivo_2.pdf - Size: 0 bytes
      [3] archivo_3.docx - Size: 0 bytes
      [4] archivo_4.xlsx - Size: 0 bytes
      [5] archivo_5.jpg - Size: 0 bytes
      [6] archivo_6.pptx - Size: 0 bytes
   ✅ INICIANDO PROCESAMIENTO DE ARCHIVOS
   ✅ Hay 6 archivos para procesar
      📄 [1] Procesando archivo: archivo_1.txt
         ✅ Guardado en disco: /path/to/abc123.txt
         ✅ Metadata guardada: archivo_1.txt
      📄 [2] Procesando archivo: archivo_2.pdf
         ✅ Guardado en disco: /path/to/def456.pdf
         ✅ Metadata guardada: archivo_2.pdf
      ... (y así para los 6)
   ✅ PROCESAMIENTO COMPLETADO: 6 archivos procesados
📤 Llamando a tarea_service.entregar_tarea() con 6 archivos...
   - archivo_urls: [6 URLs]
   - archivos_metadata: [6 metadata objects]
```

### 2️⃣ En `tarea_service.py` - `obtener_entrega`

**Lo que loguea ahora**:
```
🔍 DIAGNÓSTICO obtener_entrega({entrega_id}):
   - archivo_url: /uploads/entregas/abc123.txt (PRIMERO, legado)
   - archivos_adicionales (raw): {"archivos": [6 items]}
   - JSON parseado OK: {"archivos": [{...}, {...}, ...]}
   - Total archivos en JSON: 6  ← CUÁNTOS HAY EN BD
     [1] tipo=dict, archivo={url: "...", nombre_original: "archivo_1.txt"}
         → Agregado como dict: nombre=archivo_1.txt
     [2] tipo=dict, archivo={url: "...", nombre_original: "archivo_2.pdf"}
         → Agregado como dict: nombre=archivo_2.pdf
     ... (así para los 6)
   ✅ Archivos procesados: 6
   📦 RESULTADO FINAL: 6 archivos retornados
```

---

## 🚀 ¿Qué Hacer Ahora?

### OPCIÓN A: Diagnóstico Rápido (RECOMENDADO)

```bash
# Ejecuta este comando:
bash /run/media/arch/Storage/SENA/Proyecto-Formativo/Acadify/DIAGNOSE_NOW.sh
```

Esto:
1. Mata el backend viejo
2. Inicia backend nuevo con logging detallado
3. Te muestra las instrucciones exactas

Luego:
1. Abre http://localhost:5173
2. Sube 6 archivos
3. Entrega la tarea
4. Mira los logs abajo (en la terminal)
5. **Copia los logs y comparte conmigo**

### OPCIÓN B: Manual

```bash
cd backend

# Mata viejo
lsof -ti:8000 | xargs kill -9 2>/dev/null || true

# Inicia nuevo
python -m uvicorn src.main:app --reload --host 127.0.0.1 --port 8000
```

Ahora prueba igual (sube 6, entrega, mira logs)

---

## 📊 Qué Ver en los Logs

Después de entregar 6 archivos, busca en los logs:

### ✅ Si FUNCIONA BIEN:
```
POST /tareas/.../entregar
   - Archivos recibidos: 6  ← DICE 6
   - [6] Procesando archivo: archivo_6.pptx
   ✅ PROCESAMIENTO COMPLETADO: 6 archivos procesados

GET /entregas/{id}
   - Total archivos en JSON: 6  ← DICE 6
   ✅ Archivos procesados: 6
   📦 RESULTADO FINAL: 6 archivos retornados
```

### ❌ Si FALLA:
```
POST /tareas/.../entregar
   - Archivos recibidos: 1  ← DICE 1 (no 6) ← PROBLEMA EN FRONTEND
   
O:

GET /entregas/{id}
   - Total archivos en JSON: 1  ← DICE 1 (no 6) ← PROBLEMA EN GUARDADO BD
```

---

## 🎯 Con Esta Info Podemos Arreglarlo

Una vez veas los logs, sabremos EXACTAMENTE dónde está el problema:

| Log dice | Problema está en |
|----------|-------------------|
| Recibidos: 1 | Frontend FormData |
| Guardado en disco: 1 | Backend route |
| JSON tiene: 1 | tarea_service.entregar_tarea() |
| Retorna: 1 | obtener_entrega() |

---

## 📝 Resumen

**Problema**: Solo 1 de 6 archivos + UUID en lugar de nombre
**Causa**: Desconocida (por eso el logging)
**Solución**: Vamos a identificarla con los logs

**Próximo paso**: Ejecuta el diagnóstico y comparte los logs

---

**Status**: 🟡 Esperando logs del usuario  
**Documentos importantes**: DIAGNOSE_NOW.sh (el script)
