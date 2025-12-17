# 🚀 PRÓXIMO PASO: FASE 2 - FRONTEND

**Después de Fase 1B Completada**

---

## 📋 TABLA DE CONTENIDOS

1. [Estado Actual](#estado-actual)
2. [Archivos a Crear/Modificar](#archivos-a-crearmodificar)
3. [Componentes Requeridos](#componentes-requeridos)
4. [Hooks Personalizados](#hooks-personalizados)
5. [Ruta Implementación](#ruta-implementación)
6. [Checklist Fase 2](#checklist-fase-2)

---

## 🎯 Estado Actual

✅ **Backend COMPLETO**:
- Seguridad integral (Phase 1A)
- Gamificación implementada (Phase 1B)
- API endpoints listos
- BD verificada (81 campos)
- Tests scenarios creados

⏳ **Frontend BLOQUEADOR**:
- No existe `TareaEntregaPage.tsx`
- Falta integración con API de calificación
- Sin componentes de entrega
- Sin display de puntos

**CRÍTICO**: Sin Fase 2 Frontend, todo el backend de Phase 1B es invisible al usuario.

---

## 📁 Archivos a Crear/Modificar

### Nuevos Archivos (CREAR)

```
frontend/src/
├── modules/tareas/
│   ├── pages/
│   │   └── TareaEntregaPage.tsx ⭐ CRÍTICO
│   ├── components/
│   │   ├── TareaSubmissionForm.tsx
│   │   ├── TareaGradingPanel.tsx
│   │   ├── TareaCommentSection.tsx
│   │   ├── PointsDisplay.tsx
│   │   ├── GradingRubric.tsx
│   │   ├── SubmissionList.tsx
│   │   └── UploadArea.tsx
│   └── hooks/
│       ├── useEntregaTarea.ts
│       ├── useCalificarEntrega.ts
│       └── useGeminiReview.ts
├── types/
│   ├── entrega.types.ts ← NUEVA PARTE
│   └── gamification.types.ts ← NUEVA
└── services/
    ├── tareaService.ts ← ACTUALIZAR
    └── gamificationService.ts ← NUEVA
```

### Archivos a Modificar (ACTUALIZAR)

```
frontend/src/
├── router/
│   └── index.ts ← AGREGAR RUTA /tareas/:tarea_id/entregar
├── types/index.ts ← AGREGAR tipos gamification
├── services/apiClient.ts ← VERIFICAR endpoints
└── components/
    └── layout/Sidebar.tsx ← AGREGAR link a entregas
```

---

## 🧩 Componentes Requeridos

### 1. TareaEntregaPage.tsx (CRÍTICO)

```typescript
// frontend/src/modules/tareas/pages/TareaEntregaPage.tsx
// ≈ 300-400 líneas

// Features:
// - Mostrar detalles de la tarea
// - Vista de estudiante: Formulario de entrega
// - Vista de docente: Panel de calificación
// - Historial de entregas
// - Integración con API backend

// Estructura:
interface TareaEntregaPageProps {
  readonly tareaId: string;
  readonly modo: 'student' | 'teacher';
}

// Lógica:
// 1. Cargar tarea por ID
// 2. Cargar entregas del estudiante (si student)
// 3. Si teacher: cargar entregas de todo el grupo
// 4. Mostrar componente correspondiente
// 5. Manejar calificación + puntos
```

### 2. TareaSubmissionForm.tsx (Para estudiantes)

```typescript
// frontend/src/modules/tareas/components/TareaSubmissionForm.tsx
// ≈ 200-300 líneas

// Features:
// - Upload de archivos con drag & drop
// - Contador de intentos
// - Timer (tiempo empleado)
// - Editor de texto para comentarios
// - Validación de restricciones

// Campos:
// - Archivo principal
// - Archivos adicionales
// - Comentarios estudiante
// - Links externos (opcional)
```

### 3. TareaGradingPanel.tsx (Para docentes)

```typescript
// frontend/src/modules/tareas/components/TareaGradingPanel.tsx
// ≈ 250-350 líneas

// Features:
// - Input de calificación (0-5)
// - Editor de retroalimentación
// - Display de fórmula puntos
// - Checkbox "requiere revisión"
// - Vista previa de puntos calculados
// - Botón Submit

// Visualización:
// Calificación: [4.8/5.0]
// Puntos Base: 50
// Bonus (≥4.5): +20
// Late Penalty: -15
// Attempt Penalty: -10
// TOTAL: 45 puntos ✅
```

### 4. PointsDisplay.tsx

```typescript
// frontend/src/modules/tareas/components/PointsDisplay.tsx
// ≈ 100-150 líneas

// Mostra la fórmula de puntos desglosada
// Props:
// - basePuntos: number
// - bonus: number
// - latePenalty: number
// - attemptPenalty: number
// - totalPuntos: number

// Render:
// ┌─ Base: 50 pts
// ├─ + Bonus (grade ≥4.5): 20 pts
// ├─ - Late Penalty (tardío): 15 pts
// ├─ - Attempt Penalty (3 intentos): 10 pts
// └─ = TOTAL: 45 pts ✅
```

### 5. TareaCommentSection.tsx

```typescript
// frontend/src/modules/tareas/components/TareaCommentSection.tsx
// ≈ 200-250 líneas

// Features:
// - Comentarios estudiante (display)
// - Comentarios docente (display/edit si es docente)
// - Thread de comentarios
// - Timestamps y autores
// - Markdown support (opcional Phase 3)
```

### 6. SubmissionList.tsx

```typescript
// frontend/src/modules/tareas/components/SubmissionList.tsx
// ≈ 150-200 líneas

// Features:
// - Lista de entregas anteriores
// - Calificación por intento
// - Puntos por intento
// - Estado (pendiente/calificada/revisión)
// - Click para ver detalle
```

---

## 🎣 Hooks Personalizados

### useEntregaTarea.ts

```typescript
// frontend/src/modules/tareas/hooks/useEntregaTarea.ts

export function useEntregaTarea(entregaId: string) {
  const { data, isLoading, error } = useQuery({
    queryKey: ['entregas', entregaId],
    queryFn: () => apiClient.get(`/api/entregas/${entregaId}`),
  });
  
  return { entrega: data, isLoading, error };
}

// Uso:
// const { entrega } = useEntregaTarea(entregaId);
// Renderiza: calificación, puntos, comentarios, etc.
```

### useCalificarEntrega.ts

```typescript
// frontend/src/modules/tareas/hooks/useCalificarEntrega.ts

export function useCalificarEntrega() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async (data: CalificarEntregaInput) =>
      apiClient.patch(
        `/api/entregas/${data.entregaId}/calificar`,
        {
          calificacion: data.calificacion,
          comentarios_docente: data.comentarios,
          requiere_revision: data.requiereRevision,
        }
      ),
    onSuccess: (result) => {
      // Mostrar puntos calculados
      console.log(`Puntos otorgados: ${result.puntos_otorgados}`);
      console.log(`Fórmula: ${result.formula_aplicada}`);
      
      // Invalidar cache
      queryClient.invalidateQueries({ 
        queryKey: ['entregas'] 
      });
    },
  });
}

// Uso:
// const { mutate: calificar } = useCalificarEntrega();
// calificar({ entregaId, calificacion: 4.8, ... });
```

### useGeminiReview.ts

```typescript
// frontend/src/modules/tareas/hooks/useGeminiReview.ts

export function useGeminiReview(entregaId: string) {
  // Para Phase 3 - IA feedback
  // Llamar endpoint IA
  // Mostrar sugerencias
}
```

---

## 🗺️ Ruta Implementación

### Paso 1: Crear tipos (30 min)

```typescript
// frontend/src/types/entrega.types.ts

export interface EntregaTarea {
  entrega_id: string;
  tarea_id: string;
  estudiante_id: string;
  calificacion?: number;
  calificacion_letras?: string;
  puntos_otorgados?: number; // ← NUEVA
  estado: 'PENDIENTE' | 'CALIFICADA' | 'DEVUELTA';
  comentarios_docente?: string;
  fecha_calificacion?: string;
  intentos: number;
  es_tardia: boolean;
  requiere_revision?: boolean;
  // ... más campos
}

export interface CalificarEntregaInput {
  entregaId: string;
  calificacion: number;
  comentarios?: string;
  requiereRevision?: boolean;
}

export interface CalificarEntregaResponse extends EntregaTarea {
  puntos_otorgados: number;
  formula_aplicada: string; // "50 + 20 - 15 - 10"
}
```

### Paso 2: Crear hooks (1 hora)

```typescript
// frontend/src/modules/tareas/hooks/

// useEntregaTarea.ts
// useCalificarEntrega.ts
// useGeminiReview.ts (para Phase 3)
```

### Paso 3: Crear componentes (2-3 horas)

```typescript
// ORDEN RECOMENDADO:
// 1. PointsDisplay.tsx (simple, independiente)
// 2. UploadArea.tsx (upload con validaciones)
// 3. TareaCommentSection.tsx (display comments)
// 4. SubmissionList.tsx (lista entregas)
// 5. TareaSubmissionForm.tsx (entrega estudiante)
// 6. TareaGradingPanel.tsx (calificación docente)
```

### Paso 4: Crear página principal (1-2 horas)

```typescript
// frontend/src/modules/tareas/pages/TareaEntregaPage.tsx

// Estructura:
// 1. Load tarea by ID
// 2. Check user role (student vs teacher)
// 3. Si student: mostrar TareaSubmissionForm
// 4. Si teacher: mostrar TareaGradingPanel
// 5. Siempre: mostrar SubmissionList (historial)
```

### Paso 5: Actualizar routing (30 min)

```typescript
// frontend/src/router/index.ts

// Agregar ruta:
{
  path: '/tareas/:tareaId/entregar',
  element: <TareaEntregaPage />,
  requiresAuth: true,
}

// Alternativa (nested):
{
  path: '/tareas',
  element: <TareasLayout />,
  children: [
    {
      path: ':tareaId/entregar',
      element: <TareaEntregaPage />,
    }
  ]
}
```

### Paso 6: Test E2E (1 hora)

```typescript
// Flujo completo:
// 1. Student: Click en tarea
// 2. Student: Upload archivo
// 3. Student: Submit entrega
// 4. Teacher: Navegar a calificación
// 5. Teacher: Ver entrega
// 6. Teacher: Ingresar calificación 4.8
// 7. Teacher: Ver puntos calculados (45 pts)
// 8. Teacher: Submit calificación
// 9. Student: Ver puntos en historial
// 10. Ambos: Ver fórmula breakdown
```

---

## ✅ Checklist Fase 2

### Creación de Archivos

- [ ] `types/entrega.types.ts` - Interfaces
- [ ] `types/gamification.types.ts` - Gamification types
- [ ] `modules/tareas/hooks/useEntregaTarea.ts`
- [ ] `modules/tareas/hooks/useCalificarEntrega.ts`
- [ ] `modules/tareas/hooks/useGeminiReview.ts` (Phase 3)
- [ ] `modules/tareas/components/PointsDisplay.tsx`
- [ ] `modules/tareas/components/UploadArea.tsx`
- [ ] `modules/tareas/components/TareaCommentSection.tsx`
- [ ] `modules/tareas/components/SubmissionList.tsx`
- [ ] `modules/tareas/components/TareaSubmissionForm.tsx`
- [ ] `modules/tareas/components/TareaGradingPanel.tsx`
- [ ] `modules/tareas/pages/TareaEntregaPage.tsx`
- [ ] `services/gamificationService.ts` (si necesario)

### Modificaciones de Archivos

- [ ] `router/index.ts` - Agregar ruta `/tareas/:id/entregar`
- [ ] `types/index.ts` - Export nuevos tipos
- [ ] `components/layout/Sidebar.tsx` - Link a entregas
- [ ] `services/apiClient.ts` - Verificar endpoints

### Testing

- [ ] Test unitario: PointsDisplay
- [ ] Test unitario: UploadArea
- [ ] Test integración: useCalificarEntrega
- [ ] Test E2E: Flujo completo estudiante
- [ ] Test E2E: Flujo completo docente
- [ ] Test: Cálculo puntos correcto
- [ ] Test: Error handling

### Documentación

- [ ] README.md actualizado (Fase 2 features)
- [ ] CHANGELOG.md (nuevos componentes)
- [ ] Docstrings en componentes
- [ ] Comments en hooks

### Validaciones

- [ ] Validación de archivo en frontend
- [ ] Mostrar error si tamaño excede
- [ ] Mostrar error si tipo de archivo inválido
- [ ] Validación de calificación (0-5)
- [ ] Verificación de permisos (student vs teacher)

### UX/UI

- [ ] Spinner mientras carga datos
- [ ] Error boundaries si falla API
- [ ] Toast notifications (éxito/error)
- [ ] Loading state durante upload
- [ ] Feedback visual de puntos calculados
- [ ] Responsive design (mobile + desktop)

---

## ⏱️ Timeline Estimado

```
Paso 1 (Tipos):              30 min   ✅ Quick
Paso 2 (Hooks):             1.0 hr   ⏳ Moderate
Paso 3 (Componentes):       2.5 hrs  ⏳ Main work
Paso 4 (Página):            1.5 hrs  ⏳ Integration
Paso 5 (Routing):           0.5 hrs  ✅ Quick
Paso 6 (Testing):           1.5 hrs  ⏳ Critical

TOTAL ESTIMADO:            ~7-8 horas
                          (1 sesión de desarrollo)
```

---

## 🎁 Bonus: Características Phase 2+

### Phase 2 Essentials
- [ ] Entrega básica
- [ ] Calificación
- [ ] Puntos display
- [ ] Comentarios

### Phase 2.5 (Nice to Have)
- [ ] Drag & drop upload
- [ ] Preview de archivos
- [ ] Timeline de entregas
- [ ] Badges visuales

### Phase 3 (IA Integration)
- [ ] IA Feedback display
- [ ] Sugerencias automáticas
- [ ] Análisis de entrega
- [ ] Real-time feedback

### Phase 4 (Comments)
- [ ] Threaded comments
- [ ] Mentions (@user)
- [ ] Markdown support
- [ ] Notifications

---

## 📞 Soporte & Debugging

### Si falla API call:
```typescript
// Verificar:
1. Token JWT válido
2. Usuario autenticado
3. Backend corriendo
4. Endpoint existe
5. Method correcto (PATCH vs POST)
6. Headers correctos
```

### Si puntos no se calculan:
```typescript
// Verificar:
1. formula_aplicada en response
2. puntos_otorgados es número
3. Base + bonus - penalties = total
4. No negative (max 0)
5. Log en backend: logger.info()
```

### Si upload no funciona:
```typescript
// Verificar:
1. File size < 10MB
2. MIME type permitido
3. Extension en whitelist
4. FormData enviado correctamente
5. Backend recibió archivo
```

---

## 🚀 Comando Para Empezar

```bash
# 1. Navegar a frontend
cd frontend/src

# 2. Crear estructura
mkdir -p modules/tareas/{pages,components,hooks}

# 3. Crear types
touch types/entrega.types.ts types/gamification.types.ts

# 4. Crear hooks
touch modules/tareas/hooks/{useEntregaTarea,useCalificarEntrega,useGeminiReview}.ts

# 5. Comenzar con component simple
# touch modules/tareas/components/PointsDisplay.tsx
```

---

## ✨ Resumen

**Phase 1B**: ✅ Backend LISTO  
**Phase 2**: ⏳ Frontend CRÍTICO - EMPEZAR AHORA  
**Bloqueador**: Sin TareaEntregaPage, todo el trabajo Phase 1B es invisible

**Prioridad Máxima**: Crear TareaEntregaPage.tsx + useCalificarEntrega hook

**Tiempo Estimado**: 7-8 horas (1 sesión concentrada)

---

**¿Listo para comenzar Phase 2? 🚀**

Próximo comando:
```bash
npm start  # Iniciar dev server
# Y crear TareaEntregaPage.tsx
```
