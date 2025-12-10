# 🎯 QUICK START - PHASE 2 INTEGRATION GUIDE

**Last Updated**: 18 de Noviembre de 2025  
**Status**: ✅ Ready for Integration  
**Time to Integrate**: 1-2 hours

---

## 📋 1-MINUTE SUMMARY

✅ **Backend**: Complete (122/123 items verified)  
✅ **Frontend**: Created (5 components + 15 hooks, 2,500+ lines)  
✅ **Next**: Import components, run API tests, fix imports

---

## 🚀 QUICK START - 3 STEPS

### **Step 1: Import Components** (10 min)
Create `frontend/src/pages/academic/index.ts`:
```typescript
export { TareaEntregaPage } from './TareaEntregaPage';
export { StudentSubmissionForm } from '../components/academic/StudentSubmissionForm';
export { TeacherGradingPanel } from '../components/academic/TeacherGradingPanel';
export { EntregasList } from '../components/academic/EntregasList';
```

### **Step 2: Setup Route** (5 min)
In `frontend/src/router.tsx`:
```typescript
import { TareaEntregaPage } from '@/pages/academic';

{
  path: '/academic/tareas/:tarea_id',
  element: <TareaEntregaPage />,
  loader: () => requireAuth('ESTUDIANTE|DOCENTE')
}
```

### **Step 3: Test Real API** (20-30 min)
```bash
npm run dev  # Start frontend
pytest backend/tests/  # Run backend tests

# Navigate to http://localhost:5173/academic/tareas/1
# Test: Create → Submit → Grade workflow
```

---

## 📁 FILES CREATED

| File | Lines | Purpose |
|------|-------|---------|
| **TareaEntregaPage.tsx** | 579 | Main page (orchestrator) |
| **StudentSubmissionForm.tsx** | 420 | Student upload form |
| **TeacherGradingPanel.tsx** | 400 | Teacher grading UI |
| **EntregasList.tsx** | 410 | Submissions list |
| **useEntregaTarea.ts** | 320 | 8 Query hooks |
| **useCalificarEntrega.ts** | 400 | 7 Mutation hooks |

**Total**: 2,500+ lines of production code

---

## 🔧 FIX CHECKLIST

### **After Integration**
- [ ] Resolve import errors (@/types, @/utils/cn, @/services/apiClient)
- [ ] Setup tsconfig paths for aliases
- [ ] Create missing utility: `utils/cn.ts` (classname helper)
- [ ] Verify type definitions match backend
- [ ] Test API endpoints respond correctly
- [ ] Check authentication flows
- [ ] Test file upload with real files
- [ ] Verify late submission detection
- [ ] Test points calculation formula
- [ ] Check mobile responsiveness

### **Known Issues**
- ⚠️ Import paths use aliases (need tsconfig.json path setup)
- ⚠️ `cn` utility missing (create or import from existing)
- ⚠️ Type definitions need consolidation
- ⚠️ apiClient needs configuration

---

## 💻 COMPONENT MAP

```
TareaEntregaPage (Main Page)
├── Header (Task Title, Info)
├── Alerts (Late, Grade, Errors)
└── Grid: 2/3 + 1/3
    ├── LEFT (2/3):
    │   ├── TaskDetailsCard
    │   ├── StudentSubmissionForm (if estudiante)
    │   └── StudentSubmissionView (if already submitted)
    └── RIGHT (1/3):
        ├── StatsCard
        ├── TeacherGradingPanel (if docente)
        └── EntregasList (if docente)
```

---

## 🎯 DATA FLOW

### **Student Submission**
```
StudentSubmissionForm
  ↓ form.handleSubmit()
  ↓ useEntregarTarea.mutate()
  ↓ POST /api/academic/entregas/{entregaId}/entregar
  ↓ Backend: calificar_entrega_api()
  ↓ Response: EntregaTarea
  ↓ Cache: invalidate mi-entrega + entregas
  ↓ UI: Show success + refresh
```

### **Teacher Grading**
```
TeacherGradingPanel
  ↓ form.handleGradeSubmit()
  ↓ useCalificarEntregaConPuntos.mutate()
  ↓ POST /api/academic/entregas/{entregaId}/calificar-con-puntos
  ↓ Backend: calificar_entrega_con_puntos_api()
  ↓ Response: EntregaTarea with puntos_otorgados
  ↓ Cache: invalidate all
  ↓ UI: Auto-select next pending
```

---

## 🧪 TESTING COMMANDS

```bash
# Start backend
cd backend && uvicorn src.main:app --reload

# Start frontend
cd frontend && npm run dev

# Run backend tests
pytest backend/tests/api/test_tareas.py -v

# Test specific endpoint
curl -X POST http://localhost:8000/api/academic/tareas/1/entregas \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "archivo=@file.pdf"
```

---

## 🐛 COMMON ISSUES & FIXES

### **Issue: "Cannot find module '@/types'"**
**Fix**:
```json
// tsconfig.json
{
  "compilerOptions": {
    "baseUrl": ".",
    "paths": {
      "@/*": ["src/*"]
    }
  }
}
```

### **Issue: "cn is not defined"**
**Fix**: Create `src/utils/cn.ts`:
```typescript
import { type ClassValue, clsx } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}
```

### **Issue: "apiClient is not configured"**
**Fix**: Create/update `src/services/apiClient.ts`:
```typescript
import axios from 'axios'

export const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
})

// Add interceptors for JWT, etc.
```

### **Issue: "Types don't match backend"**
**Fix**: Run type generation from OpenAPI:
```bash
npm install openapi-typescript-fetch
npx openapi-typescript http://localhost:8000/openapi.json -o src/types/api.ts
```

---

## 📊 VERIFICATION CHECKLIST

After integration, verify:

- [ ] TareaEntregaPage loads without errors
- [ ] Can navigate to task details page
- [ ] StudentSubmissionForm displays for estudiantes
- [ ] Can upload files with validation
- [ ] Late submission is detected
- [ ] TeacherGradingPanel shows for profesores
- [ ] Can set calificación 0-5
- [ ] Points calculated correctly
- [ ] Grade saved to database
- [ ] Cache invalidation works
- [ ] Mobile view responsive
- [ ] All error messages display
- [ ] Loading states work
- [ ] Animations smooth
- [ ] No console errors

---

## 🚀 NEXT PHASE

After this integration works:

1. **Phase 2B** (2-4 hours):
   - Comments system UI
   - Real-time notifications
   - WebSocket integration

2. **Phase 3** (4-8 hours):
   - IA feedback display
   - Suggestion integration
   - Student notifications

3. **Phase 4** (Production):
   - Performance optimization
   - Accessibility audit
   - Security review
   - Deployment

---

## 📞 REFERENCE

| What | File |
|------|------|
| Architecture | FASE_2_ARQUITECTURA_FRONTEND.md |
| Full Summary | SESSION_SUMMARY_PHASE_1B_2.md |
| Backend Status | backend_verification_complete.py |
| Components | frontend/src/pages/academic/TareaEntregaPage.tsx |

---

**Ready to integrate!** 🚀

