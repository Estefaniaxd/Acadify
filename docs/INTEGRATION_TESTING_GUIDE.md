# 🧪 Integration Testing Guide - Tareas Module

> **Guía para probar la integración del módulo de Tareas en el detalle de Cursos**
> Fecha: 16 de noviembre de 2025

---

## 📋 Qué se Integró

### Antes (ClaseTareasPage.tsx)
```
❌ Usaba componentes antiguos (TareasList, CrearTareaModal)
❌ Navegación manual a detalle de tarea
❌ Recarga de página completa (window.location.reload)
❌ Sin estadísticas
❌ Sin filtros avanzados
❌ Interfaz básica
```

### Ahora (ClaseTareasPage.tsx - NUEVA)
```
✅ Usa componentes nuevos de PHASE 3 (TareasAccordion, TareasStatistics, TareaFormModal, TareaPreviewModal)
✅ React Query para data management
✅ Refetch automático sin reloads
✅ Estadísticas en sidebar
✅ Filtros avanzados (búsqueda, tipo, prioridad, estado)
✅ Interfaz moderna con dark mode
✅ Modal preview integrado
✅ Lazy loading de datos
```

---

## 🔧 Stack de la Integración

```
Frontend Layer:
├─ ClaseTareasPage.tsx (PAGE)
│  └─ Coordina todo
│  └─ React Query para fetch
│
├─ TareasAccordion.tsx (COMPONENT)
│  └─ Agrupa por 6 estados
│  └─ Shows 12+ tareas en acordeón
│
├─ TareasStatistics.tsx (COMPONENT)
│  └─ KPI dashboard
│  └─ Shows total/completadas/urgentes
│
├─ TareaFormModal.tsx (COMPONENT)
│  └─ Create tarea modal
│  └─ 9 fields with validation
│
└─ TareaPreviewModal.tsx (COMPONENT)
   └─ Preview tarea details
   └─ Show full info

Data Layer:
├─ apiClient (Axios)
│  └─ GET /api/cursos/{cursoId}/tareas
│  └─ POST /api/cursos/{cursoId}/tareas (en TareaFormModal)
│
└─ React Query
   └─ Caching (5min)
   └─ Auto-retry
   └─ Background refetch

Type Layer:
├─ Tarea (from modules/tareas/types)
├─ EstadoTarea enum
├─ TipoTarea enum
└─ PrioridadTarea enum
```

---

## 🚀 Cómo Probar

### **Paso 1: Verificar Backend**

```bash
cd backend

# Verificar que el endpoint existe
curl -X GET http://localhost:8000/api/cursos/1/tareas \
  -H "Authorization: Bearer YOUR_TOKEN"

# Esperado: Status 200 con array de tareas
# Si error 401: Token expirado
# Si error 404: Curso no existe
# Si error 422: Datos inválidos
```

### **Paso 2: Iniciar Frontend en Desarrollo**

```bash
cd frontend

pnpm dev
# Esperado: http://localhost:5173

# Abre Chrome DevTools (F12)
# Pestaña Network: Ve que se llame GET /api/cursos/{id}/tareas
# Pestaña Console: No debe haber errores
```

### **Paso 3: Navegar a un Curso**

```
1. Go to http://localhost:5173/dashboard
2. Click en algún curso
3. Click en pestaña "Tareas"
   Esperado: Ves el nuevo diseño con:
   - Sidebar con estadísticas (left)
   - Barra de búsqueda + filtros (top)
   - Accordion de tareas (center)
```

### **Paso 4: Probar Funcionalidades**

#### **A. Búsqueda**
```
1. En input "Buscar tareas..."
2. Escribe: "algebra"
3. Esperado: Filtra tareas que contienen "algebra"
4. Verifica que se actualicen las estadísticas
```

#### **B. Filtros**
```
Tipo:
1. Select "Tipo": Tarea → Filtra solo tareas
2. Select "Tipo": Quiz → Filtra solo quizzes
3. Select "Tipo": Proyecto → Filtra solo proyectos
4. Select "Tipo": Todos → Muestra todos

Prioridad:
1. Select "Prioridad": 🟢 Baja → Filtra solo baja prioridad
2. Select "Prioridad": 🟡 Media → Filtra solo media
3. Select "Prioridad": 🔴 Alta → Filtra solo alta
4. Select "Prioridad": Todas → Muestra todos

Estado:
1. Select "Estado": 🔵 Asignada → Filtra tareas nuevas
2. Select "Estado": 🟡 En Progreso → Filtra en progreso
3. Select "Estado": 🟣 Entregada → Filtra entregadas
4. Select "Estado": 🟢 Calificada → Filtra calificadas
5. Select "Estado": 🔴 Vencida → Filtra vencidas
6. Select "Estado": ⚫ Cerrada → Filtra cerradas
7. Select "Estado": Todos → Muestra todos
```

#### **C. Estadísticas**
```
En sidebar derecho:
✓ Tarjeta "Total": Debe mostrar cantidad de tareas
✓ Tarjeta "Completadas": Debe mostrar tareas con estado calificada/cerrada
✓ Tarjeta "En Progreso": Debe mostrar en_progreso + entregada
✓ Tarjeta "Urgentes": Debe mostrar tareas con < 48h y alta prioridad
✓ Tabla desglose: Debe mostrar conteo por estado
```

#### **D. Crear Tarea**
```
1. Click en "+ Crear Tarea"
2. Esperado: Modal aparece con form
3. Llena campos:
   - Título: "Mi nueva tarea"
   - Descripción: "Descripción de prueba"
   - Tipo: "Tarea"
   - Prioridad: "Alta"
   - Estado: "Asignada"
   - Fecha límite: "2025-12-31"
4. Click "Crear Tarea"
5. Esperado:
   - Modal se cierra
   - Nueva tarea aparece en acordeón
   - Estadísticas actualizadas
   - NO hay recarga de página completa (React Query)
```

#### **E. Preview Tarea**
```
1. Click en cualquier tarjeta de tarea en acordeón
2. Esperado: Modal preview aparece con:
   - Título y descripción
   - Estado con color y emoji
   - Prioridad con color y emoji
   - Fecha límite
   - Información completa
3. Click fuera del modal → Se cierra
```

#### **F. Dark Mode**
```
1. Toggle tema oscuro (si tu app tiene botón)
2. Verifica que todos los colores se adapten:
   - Background: oscuro
   - Texto: claro
   - Modales: con dark background
   - Bordes: gray-700 instead of gray-200
```

---

## 📊 Casos de Prueba Completos

### **Test 1: Flujo Completo Docente**

```
Objetivo: Un docente crea una tarea y verifica que aparezca

Steps:
1. Go to http://localhost:5173/cursos/1 (o tu curso)
2. Click pestaña "Tareas"
3. Verifica que cargan las tareas existentes
4. Click "+ Crear Tarea"
5. Llena form (todos los campos)
6. Submit → Espera modal cierre
7. Verifica:
   ✓ Nueva tarea en acordeón
   ✓ Estadísticas actualizadas
   ✓ Sin errores en console
   ✓ Backend confirmó POST 201

Expected Output:
✅ Tarea creada y visible inmediatamente
✅ No hay recarga de página
✅ React Query cachea y refetch automático
```

### **Test 2: Filtros Funcionan Juntos**

```
Objetivo: Combinar múltiples filtros

Steps:
1. Buscar: "sql"
2. Tipo: "Tarea"
3. Prioridad: "Alta"
4. Estado: "En Progreso"
5. Esperado: Solo muestra tareas que cumplan TODOS

Example:
Si hay 10 tareas totales:
- 3 contienen "sql"
- De esas 3, solo 1 es tipo "Tarea"
- De esas 1, está en alta prioridad
- De esas 1, está en progreso
→ Muestra solo 1 tarea

Verifica que estadísticas también se recalculan.
```

### **Test 3: Performance Con Muchas Tareas**

```
Objetivo: Verificar que es rápido con 100+ tareas

Backend (opcional):
# Crear 100 tareas de prueba
for i in {1..100}; do
  curl -X POST http://localhost:8000/api/cursos/1/tareas \
    -H "Authorization: Bearer TOKEN" \
    -H "Content-Type: application/json" \
    -d "{\"titulo\":\"Tarea $i\",...}"
done

Frontend Test:
1. Go to course tareas tab
2. Espera loading
3. Verifica que carga en < 2 segundos
4. Scroll el acordeón
5. Verifica que es smooth (no lag)
6. Click + busca algo
7. Esperado: Filter instant (useMemo optimizado)
8. Open DevTools Performance
9. Scroll accordion → Timeline debe mostrar 60fps
```

### **Test 4: Error Handling**

```
Objetivo: Verificar que maneja errores gracefully

Scenario A: Backend offline
1. Detén backend (Ctrl+C)
2. Recarga página
3. Esperado:
   ✓ Loading spinner
   ✓ Después timeout
   ✓ Error message: "Error al cargar las tareas"
   ✓ No console errors

Scenario B: Network error
1. Open DevTools
2. Network tab → Offline
3. Click "+ Crear Tarea"
4. Submit
5. Esperado:
   ✓ Error handling en modal
   ✓ Mensaje amigable
   ✓ Opción retry

Scenario C: Invalid token
1. Delete localStorage tokens
2. Recarga
3. Esperado:
   ✓ Redirige a login
   ✓ No 401 errors en console
```

### **Test 5: Dark Mode Consistency**

```
Objetivo: Verificar que dark mode funciona en todos lados

Steps:
1. Toggle dark mode (ctrl+shift+d o botón en navbar)
2. Verifica cada elemento:
   ✓ Page background → oscuro
   ✓ Cards → dark-gray
   ✓ Text → claro/white
   ✓ Borders → gray-700
   ✓ Inputs → dark-bg
   ✓ Modales → dark-bg
   ✓ Botones → contraste OK

Color Checks:
- Background: dark:bg-[#18181b] ✓
- Cards: dark:bg-zinc-900 ✓
- Text: dark:text-white ✓
- Borders: dark:border-gray-700 ✓
```

---

## 🔗 Dependencias Para Testing

### **Backend (Debe estar corriendo)**

```bash
cd backend

# Verificar que existe el endpoint
grep -r "GET.*tareas" src/api/routers/

# Esperado: algo como @router.get("/api/cursos/{cursoId}/tareas")

# Verificar que la ruta devuelve tareas
curl -X GET http://localhost:8000/api/cursos/1/tareas \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json"

# Si funciona, respuesta ejemplo:
# [
#   {
#     "tarea_id": 1,
#     "titulo": "Tarea 1",
#     "estado": "asignada",
#     "prioridad": "alta",
#     "tipo": "tarea",
#     "fecha_limite": "2025-12-31",
#     ...
#   }
# ]
```

### **Frontend (Debe estar corriendo)**

```bash
cd frontend

pnpm dev

# Verifica que el dev server está OK
curl http://localhost:5173

# En consola, no debe haber:
# ❌ "Cannot find module"
# ❌ "Invalid type"
# ❌ React errors
```

---

## 📋 Checklist de Integración

```
ANTES DE PROBAR:

Backend:
  ☐ Backend corriendo en 8000
  ☐ Endpoint GET /api/cursos/{id}/tareas existe
  ☐ Devuelve array de Tarea[]
  ☐ Auth funciona (JWT tokens)
  ☐ DB tiene al menos 1 tarea en BD

Frontend:
  ☐ Frontend corriendo en 5173
  ☐ npm packages instalados (pnpm install)
  ☐ No hay errores en tsconfig
  ☐ React Query configurado
  ☐ Tipos importados correctamente

DURANTE LA PRUEBA:

Core Functionality:
  ☐ Tareas cargan sin errores
  ☐ Acordeón expande/colapsa
  ☐ Estadísticas se recalculan
  ☐ Modal crear funciona
  ☐ Modal preview funciona
  ☐ Búsqueda filtra
  ☐ Select filtros filtran
  ☐ Combinación de filtros funciona

UI/UX:
  ☐ Dark mode funciona
  ☐ Responsive en mobile
  ☐ Animaciones son smooth
  ☐ Loading states muestran
  ☐ Error states muestran
  ☐ Empty state muestra

Performance:
  ☐ Carga inicial < 2s
  ☐ Crear tarea < 1s
  ☐ Filtrar es instant
  ☐ Scroll es smooth (60fps)
  ☐ No memory leaks

DESPUÉS DE PRUEBA:

Validation:
  ☐ No hay console errors
  ☐ Network tab muestra requests OK
  ☐ React Query DevTools muestra cache
  ☐ Todos los tipos TypeScript OK
  ☐ Documentación actualizada
```

---

## 🐛 Debugging Tips

### **Si tareas no cargan:**

```bash
# 1. Verifica backend está corriendo
curl http://localhost:8000/api/docs

# 2. Verifica que devuelve datos
curl -X GET http://localhost:8000/api/cursos/1/tareas \
  -H "Authorization: Bearer TOKEN"

# 3. Verifica React Query en DevTools
# Abre: https://tanstack.com/query/latest/docs/devtools
# Busca "cursoTareas" en query cache

# 4. Verifica Network tab (F12)
# GET /api/cursos/1/tareas
# Status debe ser 200
# Si 401: Token expirado
# Si 404: Curso no existe

# 5. Console logs
console.log('tareas:', tareas);
console.log('isLoading:', isLoading);
console.log('error:', error);
```

### **Si modal no aparece:**

```typescript
// Verifica state
console.log('mostrarFormModal:', mostrarFormModal);

// Verifica onClick
<button onClick={() => {
  console.log('Clicked!');
  setMostrarFormModal(true);
}}>
  + Crear Tarea
</button>

// Verifica renderizado condicional
{mostrarFormModal && (
  <div>Modal should appear here</div>
)}
```

### **Si filtros no funcionan:**

```typescript
// Añade logs a la función filter
const filteredTareas = tareas.filter((tarea: Tarea) => {
  const matchSearch = tarea.titulo.toLowerCase().includes(searchTerm.toLowerCase());
  console.log(`${tarea.titulo}: matchSearch=${matchSearch}, searchTerm=${searchTerm}`);
  
  const matchTipo = filtroTipo === 'todos' || tarea.tipo === filtroTipo;
  console.log(`${tarea.titulo}: matchTipo=${matchTipo}, filtroTipo=${filtroTipo}, tarea.tipo=${tarea.tipo}`);
  
  return matchSearch && matchTipo;
});

console.log('filteredTareas count:', filteredTareas.length);
```

---

## 📊 Expected Network Flow

```
Client (Frontend)              Server (Backend)
================================
GET /api/cursos/1/tareas ──────→
(with Auth header)
                              ↓ Fetch from DB
                              ↓ Filter by curso_id=1
                              ↓ Serialize Tarea objects
                    ←────── [Tarea[]]
                             Status 200
                             
[React Query]
    ↓ Cache 5min
    ↓ Parse types
    ↓ Update state
    
[UI Re-render]
    ↓ TareasAccordion shows tareas
    ↓ TareasStatistics calculates stats
    ↓ Loading spinner disappears
    
[User interaction]
POST /api/cursos/1/tareas ─────→
{titulo, descripcion, ...}    
(with Auth header)
                              ↓ Validate Pydantic
                              ↓ Insert into DB
                              ↓ Return created Tarea
                    ←────── {Tarea + ID}
                             Status 201
                             
[React Query]
    ↓ Auto-invalidate cursoTareas
    ↓ Auto-refetch
    ↓ Update cache
    
[UI Re-render]
    ↓ Modal closes
    ↓ New tarea appears in accordion
    ↓ Statistics update
```

---

## ✅ Success Criteria

```
La integración es EXITOSA cuando:

✅ Tareas cargan en < 2 segundos
✅ Filtros funcionan combinados
✅ Crear tarea es seamless (sin recarga)
✅ Modales son fluidos y hermosos
✅ Dark mode se ve bien
✅ Responsive en mobile
✅ No hay errores en console
✅ Network requests son eficientes
✅ React Query cachea correctamente
✅ Animaciones son smooth (60fps)

La integración es PRONTA SI:

❌ Tareas tardan > 5 segundos
❌ Filtros están lentos (lag)
❌ Crear tarea requiere refresh
❌ Modales son clunkier
❌ Dark mode está roto
❌ No funciona en mobile
❌ Muchos errores en console
❌ Network requests duplicados
❌ React Query deshabilitado
❌ Animaciones jerky (< 30fps)
```

---

## 📝 Próximos Pasos

Después de que esta integración funcione 100%:

1. **PHASE 4** (Design Polish - 1h)
   - Fine-tune colores en modales
   - Optimizar sombras (shadow-lg)
   - Verificar tipografía
   - Pulir hover/focus states

2. **PHASE 5** (AI Architecture - 0.5h)
   - Agregar hooks para AI feedback
   - Estructura para LLM integration
   - No AI real aún

3. **PHASE 6** (E2E Testing - 0.5h)
   - Tests con Playwright/Puppeteer
   - Validar flujos completos
   - Performance benchmarks

4. **PHASE 7** (Production)
   - Deploy a production
   - Monitor metrics
   - Collect user feedback

---

## 📞 Need Help?

```
Si algo no funciona:

1. Revisa console errors (F12)
2. Revisa Network tab (F12)
3. Verifica backend está corriendo
4. Revisa tipos TypeScript (red squiggles)
5. Intenta pnpm install (dependencies)
6. Limpia React Query cache (DevTools)
7. Hard reload (Ctrl+Shift+R)
8. Reinicia dev servers
```

---

**Created**: 16 de noviembre de 2025  
**Component Status**: ✅ INTEGRATED & READY FOR TESTING  
**Next Phase**: PHASE 4 - Design Polish  

