# 🚀 ACCIÓN INMEDIATA - Diagnóstico 6 Archivos

**Problema**: Subes 6 archivos pero solo 1 se registra  
**Status**: Cambios aplicados, necesito que hagas testing  
**Tiempo estimado**: 15 minutos

---

## ✅ Cambios Realizados en el Backend

### 1. Sintaxis correcta de FastAPI para múltiples archivos
```python
# ANTES (incorrecto para listas):
archivos: List[UploadFile] = File(default=[])

# DESPUÉS (correcto):
archivos: List[UploadFile] = File(default=None)
```

**Por qué**: FastAPI no maneja bien `default=[]` con `List[UploadFile]`. Cambiamos a `default=None` y agregamos validación.

### 2. Logging detallado agregado
En `curso_tareas.py` agregué logs que muestran:
- ✅ Cuántos archivos recibe el backend
- ✅ Cada archivo individual (nombre, tamaño)
- ✅ Proceso de cada archivo (guardado en disco, metadata)
- ✅ Resumen final

En `tarea_service.py` agregué logs que muestran:
- ✅ Si `archivos_metadata` tiene todos los items
- ✅ Si la serialización a JSON es correcta

---

## 🎯 QUÉ NECESITO QUE HAGAS

### PASO 1: Reinicia el backend (2 min)

```bash
# Opción A: Ejecutar script
chmod +x /run/media/arch/Storage/SENA/Proyecto-Formativo/Acadify/restart_backend.sh
./restart_backend.sh

# Opción B: Manual
lsof -ti:8000 | xargs kill -9 2>/dev/null
sleep 2
cd /run/media/arch/Storage/SENA/Proyecto-Formativo/Acadify/backend
python -m uvicorn src.main:app --reload --host 127.0.0.1 --port 8000
```

**Mantén esta terminal abierta** - verás los logs aquí

### PASO 2: Upload y entrega (5 min)

1. Abre http://localhost:5173 en navegador
2. Entra a **cualquier tarea**
3. Upload **6 archivos** (pueden ser los mismos nombres repetidos):
   - archivo1.pdf
   - archivo2.pdf
   - archivo3.pdf
   - archivo4.pdf
   - archivo5.pdf
   - archivo6.pdf
4. Click "Entregar Tarea"

### PASO 3: Observa los logs (2 min)

En **la terminal del backend** verás algo como:

```
📥 POST /tareas/abc123/entregar - Usuario: user123
   ⚠️ DIAGNÓSTICO CRÍTICO:
   - Type de archivos: <class 'list'>
   - Archivos recibidos: ???  ← AQUÍ EMPIEZA EL DIAGNÓSTICO
   [1] archivo1.pdf - Size: 1024 bytes
   [2] archivo2.pdf - Size: 1024 bytes
   ...
   [6] archivo6.pdf - Size: 1024 bytes
   
   ✅ INICIANDO PROCESAMIENTO DE ARCHIVOS
   ✅ Hay ??? archivos para procesar
   
   📄 [1] Procesando archivo: archivo1.pdf
      ✅ Guardado en disco: /path/.../uuid-random-1.pdf
      ✅ Metadata guardada: archivo1.pdf
   
   📄 [2] Procesando archivo: archivo2.pdf
      ✅ Guardado en disco: /path/.../uuid-random-2.pdf
      ✅ Metadata guardada: archivo2.pdf
   
   ... (continúa para 3-6 si todo está bien)
   
   ✅ PROCESAMIENTO COMPLETADO: ??? archivos procesados
```

### PASO 4: Copia y comparte los logs

**Copia TODO lo que aparezca** desde la línea `📥 POST` hasta `PROCESAMIENTO COMPLETADO`

---

## 🔍 Interpretación de Logs

### ✅ RESULTADO ESPERADO (Si todo funciona)
```
Archivos recibidos: 6  ← PERFECTO
[1] archivo1.pdf
[2] archivo2.pdf
[3] archivo3.pdf
[4] archivo4.pdf
[5] archivo5.pdf
[6] archivo6.pdf
Hay 6 archivos para procesar
Guardado en disco: 6 veces (uno para cada archivo)
PROCESAMIENTO COMPLETADO: 6 archivos procesados
```

### ❌ POSIBLES PROBLEMAS

| Log | Significa | Solución |
|-----|-----------|----------|
| `Archivos recibidos: 1` | Frontend solo envía 1 | Revisar frontend FormData |
| `Archivos recibidos: None` | `File(default=None)` tiene problema | Cambiar sintaxis |
| `[1] archivo1.pdf` sin [2], [3], etc | Loop no itera | Error en Python loop |
| Solo 1 `Guardado en disco` | Loop se rompe en segundo archivo | Error al guardar archivo |
| 6 en disco pero DB solo 1 | Problema en service/DB | Revisar `tarea_service` |

---

## 📋 Documentos de Referencia

- `DIAGNOSTIC_DEEP_6FILES.md` - Guía completa de diagnóstico
- `BUG_FIX_SOLO_1_ARCHIVO.md` - Análisis anterior (archivos_adicionales)
- `DIAGRAMA_BUG_SOLUCION.md` - Diagramas de flujo

---

## 🆘 Si Los Logs Muestran Problema

### Problema: `Archivos recibidos: 1`

**Significa**: Frontend no está enviando 6 archivos

**Prueba en DevTools** (F12 → Network):
1. Upload 6 archivos
2. Click Entregar
3. Network → POST /tareas/.../entregar
4. Scroll a "Form Data"
5. ¿Cuántos "archivos" ves? (debe ser 6)

**Si ves solo 1**:
→ Problema en `handleSubmit()` de React
→ Ver SubirTareaPage.tsx línea 243

### Problema: `Archivos recibidos: 6` pero solo `[1] archivo1.pdf`

**Significa**: Backend recibe 6 pero no muestra los otros

**Causa probable**: El loop es:
```python
for idx, archivo in enumerate(archivos, 1):
    logger.info(f"      [{idx}] {archivo.filename}")
```

Si solo muestra [1], probablemente el `enumerate` falla. Necesitaría cambiar a:
```python
for i in range(len(archivos)):
    archivo = archivos[i]
    logger.info(f"      [{i+1}] {archivo.filename}")
```

---

## ⏱️ Timeline

```
AHORA       → Reinicia backend
+2 min      → Upload y entrega 6 archivos
+5 min      → Observa logs
+2 min      → Copia y comparte logs

Total: ~10 minutos para tener diagnóstico EXACTO
```

---

## 🎯 Qué Pasará Después

Según los logs que compartas:

**Si todo funciona**: 
→ Backend recibe, procesa y guarda 6 archivos ✓
→ Continuamos con testing de BD y frontend

**Si hay problema**:
→ Los logs lo mostrarán EXACTAMENTE
→ Podré aplicar fix específico
→ No será "a ciegas", tendremos datos

---

## 💡 Pro Tip

Si los logs son muy largos o difíciles de leer:

```bash
# En la terminal del backend, presiona Ctrl+C para parar
# Luego ejecuta:
tail -n 200 api_debug.log | grep "POST\|archivo\|Guardado\|COMPLETADO"
```

Esto te mostrará solo los logs relevantes

---

## ✨ Siguiente Paso

**Ejecuta ahora**:

```bash
chmod +x /run/media/arch/Storage/SENA/Proyecto-Formativo/Acadify/restart_backend.sh
./restart_backend.sh
```

Y luego comparte los logs que aparezcan cuando hagas upload + entrega de 6 archivos.

**Con los logs exactos, podré identificar y reparar el problema definitivamente** ✓

