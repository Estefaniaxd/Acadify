# 🎯 COMANDOS LISTOS PARA COPIAR Y PEGAR

---

## 🟢 OPCIÓN 1: Script automático (RECOMENDADO)

```bash
/run/media/arch/Storage/SENA/Proyecto-Formativo/Acadify/START_BACKEND_NOW.sh
```

**Qué hace**:
- ✅ Mata backend anterior
- ✅ Reinicia backend nuevo
- ✅ Muestra instrucciones
- ✅ Los logs aparecen aquí

---

## 🔵 OPCIÓN 2: Manual (Si el script falla)

### Paso 1: Mata backend anterior
```bash
lsof -ti:8000 | xargs kill -9 2>/dev/null && sleep 2
```

### Paso 2: Inicia backend
```bash
cd /run/media/arch/Storage/SENA/Proyecto-Formativo/Acadify/backend
python -m uvicorn src.main:app --reload --host 127.0.0.1 --port 8000
```

**Espera a ver**:
```
Uvicorn running on http://127.0.0.1:8000
Application startup complete
```

---

## 📋 Después de iniciar backend

### En OTRA terminal/tab

```bash
# Abre navegador
open http://localhost:5173
# o si usas Linux
xdg-open http://localhost:5173
```

### En el navegador
1. Entra a **cualquier tarea**
2. Haz click en "Subir archivo"
3. Upload **6 archivos** (pueden ser duplicados):
   - archivo1.pdf
   - archivo2.pdf
   - archivo3.pdf
   - archivo4.pdf
   - archivo5.pdf
   - archivo6.pdf
4. Click en "ENTREGAR TAREA"

### En la terminal del backend (la 1ª)

Verás logs como:
```
📥 POST /tareas/abc-123/entregar - Usuario: user-id-123
   ⚠️ DIAGNÓSTICO CRÍTICO:
   - Type de archivos: <class 'list'>
   - Archivos recibidos: ???  ← CUENTA AQUÍ
   [1] archivo1.pdf - Size: 1024 bytes
   [2] archivo2.pdf - Size: 1024 bytes
   [3] archivo3.pdf - Size: 1024 bytes
   [4] archivo4.pdf - Size: 1024 bytes
   [5] archivo5.pdf - Size: 1024 bytes
   [6] archivo6.pdf - Size: 1024 bytes
   - Contenido recibido: 'Entrega de tarea'
   
   ✅ INICIANDO PROCESAMIENTO DE ARCHIVOS
   ✅ Hay 6 archivos para procesar
   
   📄 [1] Procesando archivo: archivo1.pdf
      ✅ Guardado en disco: /path/to/backend/uploads/entregas/uuid-1-random.pdf
      ✅ Metadata guardada: archivo1.pdf
   
   📄 [2] Procesando archivo: archivo2.pdf
      ✅ Guardado en disco: /path/to/backend/uploads/entregas/uuid-2-random.pdf
      ✅ Metadata guardada: archivo2.pdf
   
   [... continúa para 3, 4, 5, 6 ...]
   
   ✅ PROCESAMIENTO COMPLETADO: 6 archivos procesados
   📤 Llamando a tarea_service.entregar_tarea() con 6 archivos...
      - archivo_urls: ["/uploads/entregas/uuid-1.pdf", "/uploads/entregas/uuid-2.pdf", ...]
      - archivos_metadata: [{"url": "/uploads/...", "nombre_original": "archivo1.pdf", ...}, ...]
```

---

## ✅ Qué Copiar y Compartir

**Copia TODO desde la línea**:
```
📥 POST /tareas/...
```

**Hasta la línea**:
```
- archivos_metadata: [...]
```

---

## 🔍 Interpretación Rápida

| Si ves | Significa | Acción |
|--------|-----------|--------|
| `Archivos recibidos: 6` | ✅ Backend recibe 6 | Continúa |
| `Archivos recibidos: 1` | ❌ Solo se envía 1 | Revisar frontend |
| `[1] [2] [3] ... [6]` | ✅ Muestra todos los 6 | Continúa |
| `[1]` (no hay más) | ❌ Loop falla en [2] | Error en loop |
| `Guardado en disco: 6x` | ✅ Se guardan todos | Continúa |
| `Guardado en disco: 1x` | ❌ Guarda solo 1 | Error en save |
| `COMPLETADO: 6` | ✅ Procesa todos | OK |
| `COMPLETADO: 1` | ❌ Solo procesa 1 | Error |

---

## 📝 Formato para Compartir Logs

Cuando me envíes los logs, hazlo así:

```
RESULTADO DE TEST - 6 Archivos

[Pega aquí TODO desde 📥 POST hasta final de archivos_metadata]

¿Qué viste?
- Backend recibió: ??? archivos
- Se mostraron: [1], [2], ..., [6] o solo [1]?
- Se guardaron en disco: ??? veces
- Se completó: ??? archivos procesados

Pasos seguidos:
1. Ejecuté: /START_BACKEND_NOW.sh ✓
2. Upload 6 archivos ✓
3. Clickeé Entregar ✓
4. Copié logs ✓
```

---

## 🎯 Una vez Compartas Logs

**Yo haré**:
1. Leer los logs línea por línea
2. Identificar la capa exacta que falla
3. Escribir el fix específico
4. Compartirlo contigo
5. Tú ejecutas el fix
6. Verificamos que funciona

**Tiempo**: 5-10 minutos

---

## 🚨 Si El Backend No Inicia

**Verás un error tipo**:
```
error: can't listen to /ip/v4/127.0.0.1/tcp/8000
```

**Solución**:
```bash
# Mata todos los procesos en puerto 8000
lsof -ti:8000 | xargs kill -9
sleep 2
# Intenta de nuevo
```

---

## 💡 Pro Tips

### Ver logs en tiempo real (si se desplaza mucho)
```bash
# En otra terminal
tail -f /run/media/arch/Storage/SENA/Proyecto-Formativo/Acadify/backend/api_debug.log | grep "POST\|Archivos\|Guardado\|COMPLETADO"
```

### Copiar múltiples líneas en terminal
```bash
# Selecciona con ratón
# Ctrl+Shift+C (Linux/Windows)
# Cmd+C (Mac)
```

### Formato limpio en DevTools
```bash
# Si ves "Archivos recibidos: 6" en DevTools Network
# Tab: Headers
# Scroll a "Form Data"
# Cuenta cuántos "archivos" ves (debe ser 6)
```

---

## 🎬 AHORA MISMO

### Abre terminal y ejecuta:

```bash
/run/media/arch/Storage/SENA/Proyecto-Formativo/Acadify/START_BACKEND_NOW.sh
```

---

**¡Listo! Backend está corriendo con logging detallado** ✓

**Próximo**: Upload 6 archivos + Entrega + Comparte logs

