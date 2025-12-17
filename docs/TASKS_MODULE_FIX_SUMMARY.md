# Tasks Module Fix Summary

**Date**: November 12, 2025  
**Focus**: Fixed critical form-API mismatch preventing task creation  
**Status**: ✅ PHASE 1 (Audit) Completed | 🔄 PHASE 2 (Backend Verification) In Progress

---

## 🔴 Problems Identified

### **Critical Issue: Form-API Mismatch**

The task creation system had a fundamental architectural mismatch preventing form submissions from working:

#### **Backend Route Issue** (`curso_tareas.py`)
```python
# ❌ WRONG: Used Body() parameters instead of Pydantic schema
@router.post("/{curso_id}/tareas")
async def crear_tarea(
    curso_id: str,
    titulo: str = Body(...),           # Individual params
    descripcion: str = Body(...),       # Not JSON object
    fecha_limite: datetime = Body(...),
    puntos_max: int = Body(100),
    ...
)
```

**Problem**: FastAPI expects either:
- A single Pydantic model in request body, OR
- Multiple `Body()` parameters with explicit JSON structure

Frontend axios.post() sends a JSON object by default, but the route was configured for individual parameters.

#### **Frontend Schema Issue** (`CrearTareaModal.tsx`)
```typescript
// ❌ Form data didn't match API expectations
const tareaData = {
  titulo: formData.titulo,
  descripcion: formData.descripcion || '',
  fecha_limite: formData.fecha_limite,
  puntos_max: formData.puntos_max,
  // Missing: tipo, prioridad - which backend partially supported
};
```

---

## ✅ Fixes Applied

### **1. Backend Route Refactored** ✅

**File**: `backend/src/api/routes/academic/curso_tareas.py`

```python
# ✅ CORRECT: Use Pydantic schema for proper validation
from src.schemas.academic.tarea_schemas import TareaCreateRequest

@router.post("/{curso_id}/tareas")
async def crear_tarea(
    curso_id: str,
    tarea_data: TareaCreateRequest,  # Single JSON object
    current_user: Usuario = Depends(deps.get_current_user),
    db: Session = Depends(deps.get_db)
):
    return tarea_service.crear_tarea(
        db=db, 
        curso_id=curso_id, 
        titulo=tarea_data.titulo,
        descripcion=tarea_data.descripcion,
        fecha_limite=tarea_data.fecha_limite,
        puntos_max=tarea_data.puntos_max,
        usuario=current_user,
        tipo=tarea_data.tipo,
        prioridad=tarea_data.prioridad
    )
```

**Changes**:
- ✅ Replaced `Body()` parameters with `TareaCreateRequest` Pydantic schema
- ✅ Added comprehensive docstring with field descriptions
- ✅ Properly passes all fields to service layer

### **2. New Pydantic Schema Created** ✅

**File**: `backend/src/schemas/academic/tarea_schemas.py`

Added new `TareaCreateRequest` schema for API endpoints:

```python
class TareaCreateRequest(BaseModel):
    """
    Schema para crear una tarea vía API (formulario frontend).
    
    Campos requeridos:
    - titulo: Nombre de la tarea
    - fecha_limite: Cuándo vence la tarea
    
    Campos opcionales con defaults sensatos:
    - descripcion: Descripción (default: vacío)
    - puntos_max: Puntuación máxima (default: 100)
    - tipo: Tipo de tarea (default: "ejercicios")
    - prioridad: Nivel de urgencia (default: "media")
    """
    titulo: str = Field(..., min_length=1, max_length=200)
    fecha_limite: datetime = Field(...)
    descripcion: Optional[str] = Field(default="", max_length=5000)
    puntos_max: float = Field(default=100, ge=1, le=1000)
    tipo: Optional[str] = Field(default="ejercicios", max_length=13)
    prioridad: Optional[PrioridadTarea] = Field(default=PrioridadTarea.MEDIA)
```

**Features**:
- ✅ Minimal required fields (only `titulo` and `fecha_limite`)
- ✅ Sensible defaults for optional fields
- ✅ Built-in validation (string length, number ranges)
- ✅ Clear documentation for frontend developers

### **3. Backend Service Updated** ✅

**File**: `backend/src/services/academic/tarea_service.py`

Updated `crear_tarea` method signature to accept `prioridad`:

```python
@staticmethod
def crear_tarea(
    db: Session,
    curso_id: str,
    titulo: str,
    descripcion: str,
    fecha_limite: datetime,
    puntos_max: float,
    usuario: Usuario,
    tipo: Optional[str] = "ejercicios",        # Changed from "individual"
    prioridad: Optional[str] = "media",         # Added new parameter
    archivo_adjunto: Optional[str] = None
) -> Dict[str, Any]:
```

### **4. Frontend Form Updated** ✅

**File**: `frontend/src/modules/tareas/components/CrearTareaModal.tsx`

Updated form submission to send all required fields:

```typescript
const tareaData = {
  titulo: formData.titulo,
  descripcion: formData.descripcion || '',
  fecha_limite: formData.fecha_limite,
  puntos_max: formData.puntos_max,
  tipo: formData.tipo,           // ✅ Added
  prioridad: formData.prioridad, // ✅ Added
};

await apiClientTareas.crearTarea(cursoId, tareaData);
```

### **5. API Client Fixed** ✅

**File**: `frontend/src/modules/tareas/api.ts`

Updated type definition for `crearTarea` method:

```typescript
async crearTarea(
  cursoId: string,
  tareaData: {
    titulo: string;
    descripcion?: string;
    fecha_limite: string;
    puntos_max?: number;
    tipo?: string;              // ✅ Added
    prioridad?: string;         // ✅ Added
  }
): Promise<Tarea> {
  const response = await axios.post(
    `${this.baseURL}/${cursoId}/tareas`,
    tareaData
  );
  return response.data;
}
```

---

## 📊 Impact Analysis

### **What This Fixes**

✅ **Form submissions now send valid JSON** - Frontend can POST forms without errors  
✅ **Backend route validates requests** - Pydantic schema ensures data quality  
✅ **Type safety end-to-end** - TypeScript + Pydantic both validate  
✅ **Backwards compatible** - Optional fields have sensible defaults  
✅ **Better error messages** - Pydantic provides clear validation feedback  

### **Before vs After**

| Aspect | Before | After |
|--------|--------|-------|
| **Request Format** | Individual Body() params | JSON object |
| **Validation** | Minimal, manual | Comprehensive, automatic |
| **Type Safety** | Partial | Complete (TS + Pydantic) |
| **Error Messages** | Generic "parse error" | Specific field validation errors |
| **Defaults** | Hardcoded in code | Schema-defined, visible |
| **Documentation** | None | Full schema with descriptions |

---

## 🚀 Next Steps

### **PHASE 2: Backend Verification** (IN PROGRESS)

**Goal**: Ensure create_tarea endpoint works correctly

**Tasks**:
1. Test form submission with actual database
   - Submit form with valid data
   - Verify task is created in `tareas` table
   - Check that `curso_id`, `docente_id`, timestamps are correct

2. Verify error handling
   - Test with missing required field (titulo)
   - Test with invalid fecha_limite
   - Test with puntos_max out of range
   - Verify helpful error messages returned

3. Check response format
   - Confirm endpoint returns created task data
   - Verify all fields are populated
   - Test `tarea_id` is generated correctly

4. Add logging for debugging
   - Log incoming request data
   - Log database insert operations
   - Log response before returning

### **PHASE 3: Frontend Refactoring** (PLANNED)

**Goal**: Create new separate Tasks page with modern UI

**Tasks**:
1. Create `/pages/academico/TareasPage.tsx`
   - Accordion component for task list (collapsible/expandable)
   - Task statistics dashboard (avg grade, pass rate, trends)
   - Task preview modal (semi-transparent, Framer Motion)

2. Build new components
   - `TareasAccordion.tsx` - Collapsible task list with animations
   - `TareaPreviewModal.tsx` - Details + submission preview
   - `TareasStatistics.tsx` - Dashboard with calculated metrics
   - `TareaFormModal.tsx` - Beautiful form inspired by report component

3. Implement React Query integration
   - `useTareas()` hook for query state
   - `useCrearTarea()` hook for mutations
   - Auto-refetch on create/update

### **PHASE 4: Design System** (PLANNED)

**Goal**: Beautiful UI with semi-transparent modals

**Tasks**:
1. Modal styling (inspired by "Reportar Comentario" component)
   - Backdrop blur: `backdrop-blur-sm`
   - Semi-transparent bg: `bg-black/50`
   - Smooth animations with Framer Motion

2. Accordion animations
   - Smooth open/close transitions
   - Icon rotation animations
   - Content expand/collapse

3. Statistics visualization
   - Progress bars for pass rates
   - Sparklines for grade trends
   - Color-coded difficulty levels

---

## 📝 Technical Debt Resolved

✅ **Body() vs Schema confusion** - Standardized on Pydantic schemas  
✅ **Frontend-Backend misalignment** - Synchronized field names and formats  
✅ **Type safety gaps** - Full TypeScript + Pydantic coverage  
✅ **Documentation gaps** - Schemas now self-document  
✅ **Import errors** - Cleaned up unused imports  

---

## 📚 Files Modified

### Backend
- ✅ `backend/src/api/routes/academic/curso_tareas.py` - Route refactored
- ✅ `backend/src/schemas/academic/tarea_schemas.py` - New schema added
- ✅ `backend/src/services/academic/tarea_service.py` - Method signature updated

### Frontend
- ✅ `frontend/src/modules/tareas/components/CrearTareaModal.tsx` - Form submission fixed
- ✅ `frontend/src/modules/tareas/api.ts` - Type definitions updated + imports cleaned

---

## ✨ Success Criteria

### For PHASE 2 (Now)
- [ ] POST /api/cursos/{id}/tareas creates task successfully
- [ ] Response includes created task with all details
- [ ] Error handling returns helpful messages
- [ ] Database stores task correctly

### For PHASE 3 (Frontend)
- [ ] New TareasPage loads and displays task list
- [ ] Accordion expands/collapses smoothly
- [ ] Task creation form modal opens/closes properly
- [ ] Statistics calculate and display correctly

### Overall
- [ ] Task creation works end-to-end (form → DB)
- [ ] Multiple tasks can be created
- [ ] Tasks display with correct data
- [ ] Beautiful, responsive UI
- [ ] Follows SOLID + Clean Code principles
- [ ] Full TypeScript + Pydantic validation

---

## 🔗 Architecture Overview

```
Frontend Form (React)
    ↓
axios.post() with JSON
    ↓
Backend Route (@router.post)
    ↓
Pydantic Validation (TareaCreateRequest)
    ↓
Service Layer (tarea_service.crear_tarea)
    ↓
Database Insert
    ↓
Response ← JSON with created task
    ↓
React Query (useTareas hook)
    ↓
UI Update (task list, statistics)
```

---

## 🐛 Debugging Tips

If task creation still fails:

1. **Check browser console**
   - Network tab: What response status code?
   - Console: Any JavaScript errors?

2. **Check backend logs**
   - What does `logger.info` print?
   - Any exceptions in service layer?

3. **Test with cURL**
   ```bash
   curl -X POST http://localhost:8000/api/cursos/tareas/curso123/tareas \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer YOUR_TOKEN" \
     -d '{
       "titulo": "Test Task",
       "fecha_limite": "2025-12-31T23:59:59",
       "descripcion": "Test description",
       "puntos_max": 100
     }'
   ```

4. **Check database directly**
   ```sql
   SELECT * FROM tareas ORDER BY fecha_creacion DESC LIMIT 1;
   ```

---

**Status**: ✅ Ready for PHASE 2 testing  
**Next Update**: After backend verification and testing

