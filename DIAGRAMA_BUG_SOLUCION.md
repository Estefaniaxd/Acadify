# 🔄 DIAGRAMA DEL BUG Y SOLUCIÓN

---

## ❌ ANTES (Con Bug)

### Flujo Completo

```
┌─────────────────────────────────────────────────────────────────┐
│ FRONTEND - SubirTareaPage.tsx                                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Usuario sube 2 archivos:                                       │
│  ┌─────────────────────────────┐                                │
│  │ documento1.pdf              │                                │
│  │ documento2.docx             │                                │
│  └─────────────────────────────┘                                │
│                                                                 │
│  handleSubmit() crea FormData:                                  │
│  formData.append('archivos', documento1.pdf)                    │
│  formData.append('archivos', documento2.docx)                   │
│                                                                 │
└────────────────┬──────────────────────────────────────────────┘
                 │
                 │ POST /tareas/{id}/entregar
                 ▼
┌─────────────────────────────────────────────────────────────────┐
│ BACKEND - curso_tareas.py                                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  @router.post("/{tarea_id}/entregar")                           │
│  archivos: List[UploadFile] = [doc1, doc2]  ✓ 2 archivos      │
│                                                                 │
│  ✅ Loop procesa ambos:                                        │
│  archivo_urls = [                                               │
│    "/uploads/entregas/abc123.pdf",                              │
│    "/uploads/entregas/def456.docx"                              │
│  ]                                                              │
│                                                                 │
│  archivos_metadata = [                                          │
│    {url: "/uploads/.../abc123.pdf",                             │
│     nombre_original: "documento1.pdf"},                         │
│    {url: "/uploads/.../def456.docx",                            │
│     nombre_original: "documento2.docx"}                         │
│  ]                                                              │
│                                                                 │
│  ✅ Guarda en disco: /uploads/entregas/ → 2 archivos OK ✓     │
│                                                                 │
│  ❌ PERO: archivo_url = archivo_urls[0]  ← SOLO PRIMERO       │
│                                                                 │
└────────────────┬──────────────────────────────────────────────┘
                 │
                 │ Pasa a tarea_service.entregar_tarea()
                 ▼
┌─────────────────────────────────────────────────────────────────┐
│ BACKEND - tarea_service.py (entregar_tarea)                    │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ✅ Serializa archivos_metadata a JSON:                        │
│  archivos_json = {                                              │
│    "archivos": [                                                │
│      {url, nombre_original: "documento1.pdf"},                  │
│      {url, nombre_original: "documento2.docx"}                  │
│    ]                                                            │
│  }                                                              │
│                                                                 │
│  ✅ Inserta en BD:                                             │
│  INSERT INTO entregas_tareas (                                  │
│    entrega_id, tarea_id, ...                                    │
│    archivo_url = "/uploads/.../abc123.pdf",  ← PRIMER O       │
│    archivos_adicionales = '{...}'             ← JSON 2 ARCHV   │
│  )                                                              │
│                                                                 │
└────────────────┬──────────────────────────────────────────────┘
                 │
                 │ Archivos guardados en BD
                 ▼
┌─────────────────────────────────────────────────────────────────┐
│ BASE DE DATOS - entregas_tareas                                │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  archivo_url (legado):          ← "/uploads/.../abc123.pdf"    │
│  archivos_adicionales (JSON):   ← {"archivos": [2 items]}  ✓  │
│                                                                 │
└────────────────┬──────────────────────────────────────────────┘
                 │
                 │ Frontend: GET /entregas/{entrega_id}
                 ▼
┌─────────────────────────────────────────────────────────────────┐
│ BACKEND - tarea_service.py (obtener_entrega) ❌ BUG AQUÍ      │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  archivos_urls = []                                             │
│                                                                 │
│  ❌ Línea 590: Agrega archivo_url (SOLO 1)                    │
│  if entrega.get('archivo_url'):                                 │
│      archivos_urls.append("/uploads/.../abc123.pdf")  ← [1]   │
│                                                                 │
│  ❌ Línea 594: Intenta agregar de archivos_adicionales (FAIL) │
│  if entrega.get('archivos_adicionales'):                        │
│      archivos_data = json.loads(...)  → {"archivos": [2]}      │
│      for archivo in archivos_data['archivos']:  ← 2 items      │
│          if archivo['url'] not in archivos_urls:  ← FAIL!      │
│             # Comparar {"url": str} in ["/uploads/..."]        │
│             # Dict en lista de strings → INESTABLE             │
│             # A veces agrega, a veces no                       │
│             # RESULTADO: Solo 1 en la lista                    │
│                                                                 │
│  return {"archivos": ["/uploads/.../abc123.pdf"]}  ← SOLO 1 ❌│
│                                                                 │
└────────────────┬──────────────────────────────────────────────┘
                 │
                 │ Response al Frontend
                 ▼
┌─────────────────────────────────────────────────────────────────┐
│ FRONTEND - SubirTareaPage.tsx                                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  entregaExistente.archivos = [                                  │
│    "/uploads/.../abc123.pdf"  ← SOLO 1 ❌                     │
│  ]                                                              │
│                                                                 │
│  Renderiza: 1 solo archivo visible ❌                          │
│  ┌──────────────────────────────────┐                          │
│  │ 📄 documento1.pdf        [↓]      │  ← Donde está doc2? ❌ │
│  └──────────────────────────────────┘                          │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## ✅ DESPUÉS (Reparado)

### Flujo Igual hasta Backend

```
FRONTEND → BACKEND POST → DISCO: 2 archivos guardados ✓
```

### Cambio CRÍTICO en obtener_entrega()

```
┌─────────────────────────────────────────────────────────────────┐
│ BACKEND - tarea_service.py (obtener_entrega) ✅ FIX           │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  # ✅ NUEVO: Ignorar completamente archivo_url                │
│  # ✅ ÚNICO ORIGEN DE VERDAD: archivos_adicionales            │
│                                                                 │
│  archivos_lista = []                                            │
│                                                                 │
│  if entrega.get('archivos_adicionales'):  ← SOLO ESTO         │
│      try:                                                       │
│          archivos_data = json.loads(...)  ✓                   │
│          if 'archivos' in archivos_data:                        │
│              for archivo in archivos_data['archivos']:  ← 2   │
│                  if isinstance(archivo, dict) and 'url':       │
│                      archivos_lista.append({                   │
│                          "url": archivo['url'],                │
│                          "nombre": archivo.get(                │
│                              'nombre_original'                 │
│                          )                                     │
│                      })  ← AGREGA DICT COMPLETO               │
│                                                                 │
│      except JSONDecodeError:                                    │
│          # Fallback: si archivo_adicionales inválido           │
│          if entrega.get('archivo_url'):                         │
│              archivos_lista.append({...})                      │
│                                                                 │
│  return {"archivos": [                                          │
│      {"url": "/uploads/.../abc123.pdf",                        │
│       "nombre": "documento1.pdf"},  ← AMBOS ✓                 │
│      {"url": "/uploads/.../def456.docx",                       │
│       "nombre": "documento2.docx"}   ← AMBOS ✓                │
│  ]}                                                             │
│                                                                 │
└────────────────┬──────────────────────────────────────────────┘
                 │
                 │ Response al Frontend
                 ▼
┌─────────────────────────────────────────────────────────────────┐
│ FRONTEND - SubirTareaPage.tsx                                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  entregaExistente.archivos = [                                  │
│    {url: "/uploads/.../abc123.pdf", nombre: "documento1.pdf"},  │
│    {url: "/uploads/.../def456.docx", nombre: "documento2.docx"} │
│  ]  ✅ LOS 2 ARCHIVOS                                          │
│                                                                 │
│  Renderiza: 2 archivos visibles ✅                            │
│  ┌────────────────────────────────────────┐                    │
│  │ 📄 documento1.pdf          [↓]         │                    │
│  │ 📄 documento2.docx         [↓]         │  ✅ Ambos!         │
│  └────────────────────────────────────────┘                    │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🔀 Comparación Lado a Lado

### Lógica ANTES ❌

```python
archivos_urls = []
if archivo_url:
    archivos_urls.append(archivo_url)  # STRING

if archivos_adicionales:
    for archivo in archivos:
        if archivo['url'] not in archivos_urls:  # DICT in LIST
            archivos_urls.append({"url": ...})   # DICT

# Resultado: MIX de tipos → INESTABLE
```

### Lógica DESPUÉS ✅

```python
archivos_lista = []

if archivos_adicionales:  # ← ÚNICA FUENTE
    for archivo in archivos:
        archivos_lista.append({  # Siempre DICT
            "url": archivo['url'],
            "nombre": archivo.get('nombre_original')
        })

# Resultado: CONSISTENTE, PREDECIBLE
```

---

## 📊 Estadísticas

| Métrica | Antes | Después |
|---------|-------|---------|
| **Archivos retornados** | 1 ❌ | 2+ ✅ |
| **Confiabilidad** | Inestable | Predecible |
| **Líneas código** | 27 confusas | 21 claras |
| **Comparaciones tipo** | 3 problemáticas | 0 |
| **Fuentes de datos** | 2 conflictivas | 1 única |
| **Fallback** | Inexistente | Presente ✓ |

---

## 🎯 El Principio Clave

**Antes**: "Usa ambos campos, pero dame solo el que concuerde"  
**Después**: "Usa SOLO el campo correcto, descarta el legado"

Mucho más simple = Mucho menos bugs ✓

