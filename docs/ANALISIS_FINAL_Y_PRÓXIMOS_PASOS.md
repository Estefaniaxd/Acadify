# 🎯 ANÁLISIS FINAL - PROBLEMAS REALES Y SOLUCIONES

**Fecha**: 21 de noviembre de 2025
**Estado**: Identificando problemas reales vs aparentes

---

## 📊 Análisis de Cada Problema Reportado

### **PROBLEMA #1: Color amarillo en archivos de referencia**
**Status**: ✅ **RESUELTO**
- Cambio realizado: Sustituir amber (amarillo) por blue (azul)
- Etiqueta "Archivos de entrega anterior (referencia)" removida
- Botón X para eliminar agregado

---

### **PROBLEMA #2: No se puede eliminar archivos de referencia**
**Status**: ✅ **RESUELTO**
- Botón X agregado en cada archivo de referencia
- Al hacer click, elimina de `entregaExistente.archivos` en memoria
- Permite al usuario cambiar archivo antes de entregar de nuevo

---

### **PROBLEMA #3: Solo muestra 1 archivo en lugar de N**
**Status**: ⚠️ **VERIFICAR - POSIBLES CAUSAS**

#### Escenario: Usuario cancela y entrega de nuevo
1. **Entrega inicial**: 2 archivos (doc1.pdf, doc2.docx) ✅
2. **Estado en BD**: `archivos_adicionales = {"archivos": [...2 items...]}`
3. **Cancela entrega**: Status = 'cancelada' (archivos preservados) ✅
4. **Sube nuevos**: 2 archivos (doc3.pdf, doc4.docx) ✅
5. **Entrega de nuevo**: ¿Debería mostrar 2 o 4 archivos?

**RESPUESTA LÓGICA**: Debería mostrar **SOLO LOS 2 NUEVOS**
- Los antiguos fueron reemplazados cuando se canceló
- La nueva entrega es INDEPENDIENTE

**POSIBLE CAUSA del problema**:
- Si el usuario ve "solo 1 archivo", puede ser porque:
  1. **FormData con `archivos` (plural) está mal formado** → Solo envía 1
  2. **Loop en backend no itera correctamente** → Pero vimos que SÍ itera
  3. **Frontend renderiza mal** → Vimos que renderiza el array completo
  4. **Backend retorna mal los archivos** → `archivos_metadata` podría no tener ambos

#### SOLUCIÓN: Hacer prueba de MULTIPART correcta
```typescript
// En handleSubmit:
const entregaData = new FormData();
entregaData.append('contenido', comentarios || 'Entrega de tarea');

// CORRECTO: append MÚLTIPLES veces la MISMA clave
archivos.forEach((archivo) => {
  entregaData.append('archivos', archivo.file);  // ✅ Correcto
});

// INCORRECTO sería:
// entregaData.append('archivos', archivos.map(a => a.file))  // ❌ Esto NO funciona
```

El código actual está **CORRECTO** (líneas 213-215 de SubirTareaPage.tsx).

---

### **PROBLEMA #4: Nombres muestran UUID, no nombres reales**
**Status**: ⚠️ **DEPENDE DE BACKEND**

#### Flujo actual:
1. **Frontend sube archivos**: FormData con `archivo.filename` = "documento.pdf"
2. **Backend recibe**: `archivo.filename = "documento.pdf"` ✅
3. **Backend guarda en disco**: UUID (abc123.pdf) ✅
4. **Backend crea metadata**: `nombre_original = "documento.pdf"` ✅
5. **Backend serializa JSON**: `{"url": "/uploads/...", "nombre_original": "documento.pdf"}`  ✅
6. **Backend retorna en POST**: `archivos: archivos_metadata or []`  ✅ (Cambio #1)
7. **Frontend recibe**: Debería tener `archivo.nombre_original = "documento.pdf"`
8. **Frontend renderiza**: Extrae `archivo.nombre || archivo.nombre_original || ...`

#### SOLUCIÓN: Verificar qué retorna el backend en POST

El frontend espera:
```json
{
  "archivos": [
    {
      "url": "/uploads/entregas/abc123.pdf",
      "nombre_original": "documento.pdf",
      "nombre_almacenado": "abc123.pdf"
    }
  ]
}
```

Pero probablemente retorna solo URLs:
```json
{
  "archivos": [
    "/uploads/entregas/abc123.pdf"
  ]
}
```

**CAUSA**: El cambio Cambio #1 (línea 520 de tarea_service.py) intenta arreglar esto, pero hay que **VERIFICAR QUE SE APLICÓ CORRECTAMENTE**.

---

### **PROBLEMA #5: Al recargar, archivos desaparecen**
**Status**: ✅ **DEBERÍA FUNCIONAR**

#### Flujo:
1. Usuario entrega tarea
2. Recarga página (F5)
3. Frontend llama `cargarDatosTarea()` en useEffect
4. `cargarDatosTarea()` obtiene `mi_entrega_id` del endpoint `obtenerTarea()`
5. Llama `obtenerEntrega(mi_entrega_id)`
6. Backend retorna entrega con `archivos` desde BD
7. Frontend renderiza

**POSIBLE PROBLEMA**: 
- `obtenerTarea()` podría NO retornar `mi_entrega_id` correctamente
- O `obtenerEntrega()` podría retornar array vacío

---

## 🔍 VERIFICACIONES NECESARIAS

### **Verificación #1: ¿Qué retorna backend en POST?**
```bash
# Entrega tarea con 2 archivos
# Ver respuesta en console.log del frontend
Response: {
  "success": true,
  "data": {
    "archivos": ???  # ← ¿Qué es esto?
  }
}
```

**Esperado**:
```json
"archivos": [
  {"url": "/uploads/...", "nombre_original": "doc1.pdf", ...},
  {"url": "/uploads/...", "nombre_original": "doc2.pdf", ...}
]
```

**Si es así**: ✅ Cambio #1 funcionó
**Si no es así**: ❌ Cambio #1 no se aplicó o hay otro problema

---

### **Verificación #2: ¿BD guarda ambos archivos?**
```bash
psql -U postgres -d acadify_db

SELECT 
  entrega_id,
  archivos_adicionales,
  json_array_length(CAST(archivos_adicionales ->'archivos' AS json))
FROM entregas_tareas
WHERE estudiante_id = 'USER_ID'
LIMIT 1;
```

**Esperado**:
```
entrega_id          | archivos_adicionales
─────────────────────────────────────────────────────────────────
abc123-abc123-...   | {"archivos": [{...}, {...}]}
                    | 2 items
```

---

### **Verificación #3: ¿Frontend renderiza ambos?**
```typescript
// En browser console, después de entregar
console.log(entregaExistente?.archivos)
// Debería mostrar array con 2 elementos
```

---

## ✅ RESUMEN DE CAMBIOS REALIZADOS

| # | Qué | Estado | Archivo |
|---|-----|--------|---------|
| 1 | Retornar archivos_metadata en POST | ✅ HECHO | tarea_service.py:520 |
| 2 | Cambiar DELETE a UPDATE en cancelar | ✅ HECHO | tarea_service.py:700 |
| 3 | Color azul en referencia (no amarillo) | ✅ HECHO | SubirTareaPage.tsx:710 |
| 4 | Remover etiqueta "referencia" | ✅ HECHO | SubirTareaPage.tsx:710 |
| 5 | Botón X para eliminar referencia | ✅ HECHO | SubirTareaPage.tsx:720 |
| 6 | Función handleDescargarArchivo() | ✅ HECHO | SubirTareaPage.tsx:65 |
| 7 | Importar ArchivoCard component | ✅ HECHO | SubirTareaPage.tsx:28 |

---

## 🚀 PRÓXIMOS PASOS (EN ORDEN)

### 1. **REINICIAR BACKEND** (CRÍTICO)
```bash
# Matar proceso anterior
lsof -ti:8000 | xargs kill -9 2>/dev/null

# Reiniciar
cd backend
python -m uvicorn src.main:app --reload --host 127.0.0.1 --port 8000
```

### 2. **TEST: Entrega con 2 archivos**
```
Pasos:
1. Ir a una tarea
2. Subir "documento1.pdf"
3. Subir "documento2.pdf"
4. Entregar
5. Verificar:
   - Frontend muestra AMBOS archivos
   - Nombres son "documento1.pdf", "documento2.pdf" (NO UUIDs)
   - Se pueden descargar ambos
6. Abrir console.log para ver qué retorna backend
```

### 3. **TEST: Cancelar y entregar de nuevo**
```
Pasos:
1. Tarea entregada con 2 archivos ✅
2. Cancelar
3. Verificar:
   - Archivos de referencia aparecen en AZUL
   - Tienen botón X
4. Eliminar archivo de referencia (click X)
5. Subir "documento3.pdf"
6. Entregar
7. Verificar:
   - Solo "documento3.pdf" se muestra (referencia fue eliminada)
   - Nombre es real, no UUID
```

### 4. **TEST: Recarga persiste archivos**
```
Pasos:
1. Entrega con archivos ✅
2. Recarga página (F5)
3. Verificar:
   - Archivos siguen mostrándose
   - Nombres correctos
```

---

## 🎯 DIAGRAMA DEL FLUJO CORRECTO

```
┌─────────────────────────────────────────────────────────┐
│ USUARIO                                                 │
└────────────────────┬────────────────────────────────────┘
                     │
          Sube "doc.pdf" + "tarea.docx"
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│ FRONTEND (SubirTareaPage.tsx)                           │
│ - archivos = [{file: doc.pdf, ...}, {file: tarea.docx}]│
│ - handleSubmit() crea FormData                          │
│ - append('archivos', doc.pdf)                           │
│ - append('archivos', tarea.docx)  ← 2 veces            │
│ - POST /entregar                                        │
└────────────────────┬────────────────────────────────────┘
                     │
          FormData: archivos[0]=doc.pdf
                          archivos[1]=tarea.docx
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│ BACKEND (curso_tareas.py)                               │
│ - Recibe List[UploadFile] = [doc.pdf, tarea.docx]      │
│ - Loop: for archivo in archivos:                        │
│   - Guarda doc.pdf → /uploads/entregas/abc123.pdf      │
│   - Guarda tarea.docx → /uploads/entregas/def456.docx  │
│   - Crea metadata: [{url, nombre_original}, {...}]     │
│ - Pasa archivos_metadata a service                      │
└────────────────────┬────────────────────────────────────┘
                     │
          archivos_metadata = [
            {url: "/uploads/entregas/abc123.pdf", nombre_original: "doc.pdf"},
            {url: "/uploads/entregas/def456.docx", nombre_original: "tarea.docx"}
          ]
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│ BACKEND (tarea_service.py - entregar_tarea())           │
│ - Serializa: json.dumps({"archivos": archivos_metadata})│
│ - Guarda en BD: archivos_adicionales = JSON             │
│ - Retorna: {archivos: archivos_metadata}  ← CAMBIO #1   │
└────────────────────┬────────────────────────────────────┘
                     │
          Response: {
            "archivos": [
              {url, nombre_original: "doc.pdf"},
              {url, nombre_original: "tarea.docx"}
            ]
          }
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│ FRONTEND (handleSubmit() callback)                       │
│ - toast.success('Entregada')                            │
│ - cargarDatosTarea()  ← RECARGA DESDE BD                │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│ FRONTEND (cargarDatosTarea())                            │
│ - GET /tareas/{id}  → obtiene mi_entrega_id             │
│ - GET /entregas/{entrega_id}                            │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│ BACKEND (obtener_entrega())                              │
│ - SELECT archivos_adicionales FROM BD                   │
│ - JSON tiene: {"archivos": [{...}, {...}]}              │
│ - Parsea JSON                                           │
│ - Retorna: entrega['archivos'] = [{url, nombre}, {...}] │
└────────────────────┬────────────────────────────────────┘
                     │
          entrega: {
            entrega_id: "abc",
            archivos: [
              {url: "/uploads/...", nombre: "doc.pdf"},
              {url: "/uploads/...", nombre: "tarea.docx"}
            ]
          }
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│ FRONTEND (renderiza POST-ENTREGA)                        │
│ - entregaExistente.archivos = 2 items                   │
│ - Renderiza 2 cards:                                    │
│   Card 1: doc.pdf (con botón descargar)                │
│   Card 2: tarea.docx (con botón descargar)             │
│ - ✅ RESULTADO: Usuario ve ambos archivos con nombres   │
└─────────────────────────────────────────────────────────┘
```

---

## 🔴 PUNTO CRÍTICO

**SI DESPUÉS DE REINICIAR EL BACKEND AÚN VES SOLO 1 ARCHIVO O UUIDs**, SIGNIFICA:

1. **Cambio #1 NO se aplicó correctamente** → Verificar línea 520 de tarea_service.py
2. **O el backend no está usando el código nuevo** → Asegurar que reiniciaste correctamente
3. **O hay otro problema en `obtener_entrega()`** → Verificar BD directamente

---

**PRÓXIMA ACCIÓN**: REINICIAR BACKEND Y HACER TEST #1
