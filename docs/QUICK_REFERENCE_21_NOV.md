# 🚀 QUICK REFERENCE - Estado Actual 21 Nov 2025

---

## 📊 PROGRESO VISUAL

```
BACKEND CHANGES        ✅✅ COMPLETADO (2/2)
├── tarea_service.py:520 (archivos_metadata)      ✅
└── tarea_service.py:700 (UPDATE vs DELETE)       ✅

FRONTEND CHANGES       ✅✅✅✅✅ COMPLETADO (5/5)  
├── handleDescargarArchivo()                      ✅
├── Referencia color: amber → blue                ✅
├── Referencia label: REMOVIDO                    ✅
├── Referencia delete (X button)                  ✅
└── Post-delivery cards design                    ✅

DOCUMENTATION         ✅ COMPLETADO
└── CHECKLIST_TESTING_COMPLETO.md                 ✅

TESTING               ⏳ PENDIENTE (0/3)
├── TEST #1: 2 files with real names              ⏳
├── TEST #2: Cancel/delete/re-deliver             ⏳
└── TEST #3: Page reload persistence              ⏳
```

---

## 📁 ARCHIVOS MODIFICADOS

| Archivo | Línea(s) | Cambio | Estado |
|---------|----------|--------|--------|
| `backend/src/services/academic/tarea_service.py` | 520 | Return `archivos_metadata` | ✅ |
| `backend/src/services/academic/tarea_service.py` | 700 | Use UPDATE not DELETE | ✅ |
| `frontend/src/pages/tareas/SubirTareaPage.tsx` | 65-80 | Add `handleDescargarArchivo()` | ✅ |
| `frontend/src/pages/tareas/SubirTareaPage.tsx` | 705-750 | Color blue + delete button | ✅ |
| `frontend/src/components/ui/ArchivoCard.tsx` | NEW | Reusable file component | ✅ |

---

## 🎯 PRÓXIMOS PASOS (3 items)

### 1️⃣ RESTART BACKEND (5 min)

```bash
# Terminal 1 - Kill old process
lsof -ti:8000 | xargs kill -9 2>/dev/null && sleep 2 && echo "✅ Port freed"

# Terminal 2 - Start backend
cd backend && python -m uvicorn src.main:app --reload --host 127.0.0.1 --port 8000
```

**✅ Señal de éxito**: 
```
Uvicorn running on http://127.0.0.1:8000
Application startup complete
```

---

### 2️⃣ RUN TEST #1 (5 min)

**Abre**: http://localhost:5173 (frontend)

**Pasos**:
1. Upload archivo1.pdf
2. Click "Agregar más"
3. Upload archivo2.docx  
4. Click "Entregar Tarea"
5. Wait para reload

**Verificar**:
- ✅ 2 archivos muestran (no 1)
- ✅ Nombres reales ("documento1.pdf", not UUID)
- ✅ Se pueden descargar
- ✅ Muestran tamaño

**Si FALLA**: Ver sección "DEBUG" en CHECKLIST_TESTING_COMPLETO.md

---

### 3️⃣ RUN TEST #2 & #3 (10 min)

Seguir pasos en CHECKLIST_TESTING_COMPLETO.md

---

## 🎨 CAMBIOS VISUALES ANTES vs DESPUÉS

### ❌ ANTES (Roto)
```
POST-ENTREGA:
┌─ Archivos de Entrega ─────────────────┐
│  Componente FEO (blue box)            │
│  - archivo1.pdf                       │
│  - archivo2.pdf                       │
│  - abc123def456.pdf (UUID! 😞)        │
└───────────────────────────────────────┘

REFERENCIA:
┌─ 📋 Archivos de entrega anterior... ──┐  ← CONFUSING
│  (amarillo/background)                │  ← UGLY COLOR
│  - archivo1.pdf                       │
│  - archivo2.pdf                       │
│  (sin botón delete X)                 │  ← CAN'T DELETE
└───────────────────────────────────────┘
```

### ✅ DESPUÉS (Fixed)
```
POST-ENTREGA:
┌─────────────────────────────────────────┐
│ 📄 documento1.pdf          0.50 MB [↓]  │  ← REAL NAME
│ 📄 documento2.docx         0.75 MB [↓]  │  ← 2 FILES
└─────────────────────────────────────────┘

REFERENCIA:
┌─────────────────────────────────────────┐
│ 📄 documento1.pdf          0.50 MB [X]  │  ← BLUE (not amber)
│ 📄 documento2.docx         0.75 MB [X]  │  ← DELETE BUTTON
└─────────────────────────────────────────┘  ← NO CONFUSING LABEL
```

---

## 🔧 CAMBIO #1: Backend Return Format

**ANTES**:
```python
"archivos": [
    "/uploads/entregas/abc123def.pdf",
    "/uploads/entregas/xyz789abc.docx"
]
```

**DESPUÉS**:
```python
"archivos": [
    {
        "url": "/uploads/entregas/abc123def.pdf",
        "nombre_original": "documento1.pdf",
        "nombre_almacenado": "abc123def.pdf"
    },
    {
        "url": "/uploads/entregas/xyz789abc.docx",
        "nombre_original": "documento2.docx",
        "nombre_almacenado": "xyz789abc.docx"
    }
]
```

**Impacto**: Frontend now shows `nombre_original` instead of UUID

---

## 🔧 CAMBIO #2: Backend Cancel Logic

**ANTES**:
```python
# Line 700
await db.delete(entrega_bd)  # Deletes entire record
```

**DESPUÉS**:
```python
# Line 700
entrega_bd.estado = 'cancelada'  # Keep archivos_adicionales
await db.commit()
```

**Impacto**: Files preserved in `archivos_adicionales` JSON column for reference

---

## 📊 STATE MACHINE

```
┌─────────────┐
│   INICIO    │
└──────┬──────┘
       │
       ▼ (Usuario sube archivos)
┌─────────────────────────────────┐
│ PRE-DELIVERY (en sección upload) │  ← Diseño: Blue Cards
│ - documento1.pdf [X]            │
│ - documento2.docx [X]           │
└──────┬──────────────────────────┘
       │
       ▼ (Usuario clickea Entregar)
┌──────────────────────────────────┐
│ POST-DELIVERY (después submit)   │  ← Diseño: Blue Cards (mismo)
│ - documento1.pdf [↓]             │     pero sin botón [X]
│ - documento2.docx [↓]            │
│                                  │
│ [Cancelar Entrega] button        │
└──────┬───────────────┬───────────┘
       │               │
       │ (Usuario OK)  │ (Usuario cancela)
       │               ▼
       │          ┌─────────────────┐
       │          │ REFERENCE FILES │  ← Diseño: Blue Cards
       │          │ (archivos azul) │     con botón [X] para delete
       │          │ - doc1.pdf [X]  │
       │          │ - doc2.docx [X] │
       │          └────────┬────────┘
       │                   │
       │          (Elimina archivos con X o sube nuevos)
       │                   │
       │          ┌────────▼────────┐
       │          │ RE-DELIVER ZONE │
       │          │ Archivos nuevos │
       │          └────────┬────────┘
       │                   │
       └───────────┬───────┘
                   ▼
            [Entregar Tarea]
                   │
                   ▼
           ┌─────────────────┐
           │  POST-DELIVERY  │ ← Cycle repeats
           └─────────────────┘
```

---

## 🚨 CRITICAL NOTES

⚠️ **Must restart backend** - Python code changes require reload
⚠️ **Keep terminal open** - Backend logs will help debug
⚠️ **Test in order** - TEST#1 → TEST#2 → TEST#3

---

## 📞 IF SOMETHING BREAKS

| Síntoma | Causa Probable | Solución |
|---------|---|---|
| Solo veo 1 archivo | Backend no loop | Ver DEBUG #1 en CHECKLIST |
| UUID en lugar de nombre | Cambio #1 no aplicó | Reinicia backend |
| Color sigue amarillo | Cambio color no aplicó | Reinicia frontend (F5) |
| No puedo eliminar | Botón X sin handler | Ver DEBUG #3 en CHECKLIST |
| Archivos desaparecen | BD issue | Ver DEBUG #2 en CHECKLIST |

---

## ✨ EXPECTED END STATE

Después de completar los 3 tests:

✅ Upload 2 files → 2 files show with real names
✅ Cancel → See blue cards with delete buttons  
✅ Delete 1, upload new, deliver → 1 new file shows
✅ Reload page → Files still there

---

**Documento**: QUICK_REFERENCE_21_NOV.md
**Estado**: 🟡 READY FOR TESTING  
**Próximo paso**: Restart backend
**Tiempo estimado**: 20 minutos (3 tests + verification)
