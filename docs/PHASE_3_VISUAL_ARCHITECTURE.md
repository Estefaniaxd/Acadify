# PHASE 3: Estructura Visual de Componentes

**Diagrama de la página de Tareas construida en PHASE 3**

---

## 📐 Layout General

```
┌─────────────────────────────────────────────────────────────────┐
│                      PÁGINA DE TAREAS                           │
│                                                                  │
│  Header (Título + Botón Nueva Tarea)                           │
│  Barra de búsqueda + Filtros                                   │
│                                                                  │
│  ┌────────────────────────────────────────────────────────┐   │
│  │ CONTENT AREA                                            │   │
│  │                                                         │   │
│  │ ┌─────────────────────┐  ┌────────────────────────┐  │   │
│  │ │   STATISTICS        │  │   ACCORDION            │  │   │
│  │ │   (Sidebar)         │  │   (Main Content)       │  │   │
│  │ │                     │  │                        │  │   │
│  │ │ • Total            │  │  [Asignadas] ▼ (5)    │  │   │
│  │ │ • Completadas      │  │  ├─ Tarea 1            │  │   │
│  │ │ • En Progreso      │  │  ├─ Tarea 2            │  │   │
│  │ │ • Urgentes         │  │  └─ Tarea 3            │  │   │
│  │ │                     │  │                        │  │   │
│  │ │ Progress Bar        │  │  [En Progreso] ▼ (3)  │  │   │
│  │ │ ████████░░ 65%     │  │  ├─ Tarea 4            │  │   │
│  │ │                     │  │  └─ Tarea 5            │  │   │
│  │ │ Desglose:          │  │                        │  │   │
│  │ │ • Asignada: 5      │  │  [Vencidas] ▼ (2)     │  │   │
│  │ │ • En Prog.: 3      │  │  ├─ Tarea 6            │  │   │
│  │ │ • Entregada: 2     │  │  └─ Tarea 7            │  │   │
│  │ │ • Etc...           │  │                        │  │   │
│  │ └─────────────────────┘  │  [Calificadas] ▶ (8)  │  │   │
│  │                           │  [Entregadas] ▶ (1)   │  │   │
│  │                           │  [Cerradas] ▶ (0)     │  │   │
│  │                           └────────────────────────┘  │   │
│  └────────────────────────────────────────────────────────┘   │
│                                                                 │
│  Modal: Nueva Tarea       │  Modal: Vista Previa             │
│  ┌────────────────────┐   │  ┌────────────────────────┐      │
│  │ Crear Nueva Tarea  │   │  │ 📝 Título de Tarea   │      │
│  │                    │   │  │ [Priority] [Status]   │      │
│  │ Título: [________] │   │  │                      │      │
│  │ Desc: [__________] │   │  │ 📅 Fecha Límite      │      │
│  │ Fecha: [__________]│   │  │ 🏆 Puntos: 100       │      │
│  │ Puntos: [_____]    │   │  │                      │      │
│  │ Tipo: [Proyecto ▼] │   │  │ Descripción...       │      │
│  │ Prioridad: [Alta ▼]│   │  │ Instrucciones...     │      │
│  │                    │   │  │                      │      │
│  │ [Cancelar] [Crear]│   │  │ [Cerrar] [Editar]    │      │
│  └────────────────────┘   │  └────────────────────────┘      │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🏗️ Estructura de Componentes

```
TareasPage (278 líneas)
│
├─ TareasAccordion (198 líneas)
│  │
│  ├─ EstadoSección (x6)
│  │  │
│  │  └─ TareaCardItem (172 líneas) (x N)
│  │     │
│  │     ├─ Emoji (tipoTarea)
│  │     ├─ Título
│  │     ├─ Priority Badge
│  │     ├─ Fecha
│  │     ├─ Puntos
│  │     └─ Preview Button
│  │
│  └─ Chevron (expand/collapse)
│
├─ TareasStatistics (287 líneas)
│  │
│  ├─ StatCard (x4)
│  │  ├─ Icon
│  │  ├─ Value
│  │  └─ Label
│  │
│  ├─ Progress Bar
│  │  ├─ Animated fill
│  │  └─ Percentage
│  │
│  └─ Desglose (x6 estados)
│     ├─ Dot color
│     ├─ Label
│     └─ Count
│
├─ TareaFormModal (341 líneas)
│  │
│  ├─ Header
│  ├─ Form
│  │  ├─ Título input
│  │  ├─ Descripción textarea
│  │  ├─ Instrucciones textarea
│  │  ├─ Fecha picker
│  │  ├─ Puntos input
│  │  ├─ Tipo select
│  │  ├─ Prioridad select
│  │  ├─ Checkbox: Entregas tardías
│  │  └─ Checkbox: IA feedback
│  │
│  └─ Buttons
│     ├─ Cancelar
│     └─ Crear
│
└─ TareaPreviewModal (251 líneas)
   │
   ├─ Header (badges)
   ├─ Info Grid
   │  ├─ Fecha
   │  └─ Puntos
   ├─ Descripción
   ├─ Instrucciones
   ├─ Info adicional
   └─ Buttons
      ├─ Cerrar
      └─ Editar
```

---

## 📱 Responsive Breakpoints

### Desktop (lg ≥ 1024px)
```
┌──────────────────────────────────────────────────┐
│                                                  │
│  ┌──────────────┐  ┌────────────────────────┐  │
│  │ STATISTICS   │  │     ACCORDION          │  │
│  │   (1/3)      │  │      (2/3)             │  │
│  │              │  │                        │  │
│  └──────────────┘  └────────────────────────┘  │
└──────────────────────────────────────────────────┘
   25%              75%
```

### Tablet (md = 768-1023px)
```
┌────────────────────────────────────────┐
│                                        │
│     ACCORDION (stacked)                │
│     ────────────────────────           │
│                                        │
│     STATISTICS (stacked)               │
│     ────────────────                   │
│                                        │
└────────────────────────────────────────┘
```

### Mobile (sm < 768px)
```
┌──────────────────┐
│                  │
│    ACCORDION     │
│    ──────────    │
│                  │
│  STATISTICS      │
│  ───────────     │
│                  │
└──────────────────┘
```

---

## 🎨 Color Scheme

### Estados (Acordeón)
```
🔵 ASIGNADA
   bg-blue-50 dark:bg-blue-900/20
   border-blue-200 dark:border-blue-800
   text-blue-600 dark:text-blue-400

🟡 EN PROGRESO
   bg-amber-50 dark:bg-amber-900/20
   border-amber-200 dark:border-amber-800
   text-amber-600 dark:text-amber-400

🟣 ENTREGADA
   bg-purple-50 dark:bg-purple-900/20
   border-purple-200 dark:border-purple-800
   text-purple-600 dark:text-purple-400

🟢 CALIFICADA
   bg-green-50 dark:bg-green-900/20
   border-green-200 dark:border-green-800
   text-green-600 dark:text-green-400

🔴 VENCIDA
   bg-red-50 dark:bg-red-900/20
   border-red-200 dark:border-red-800
   text-red-600 dark:text-red-400

⚫ CERRADA
   bg-slate-100 dark:bg-slate-800
   border-slate-300 dark:border-slate-700
   text-slate-600 dark:text-slate-400
```

### Prioridades (Badge)
```
🟢 BAJA
   bg-green-100 dark:bg-green-900/30
   text-green-600 dark:text-green-400

🟡 MEDIA
   bg-amber-100 dark:bg-amber-900/30
   text-amber-600 dark:text-amber-400

🔴 ALTA
   bg-red-100 dark:bg-red-900/30
   text-red-600 dark:text-red-400
```

---

## 🎬 Animaciones

### Entrada de Página
```
Initial: opacity: 0, y: -20
Animate: opacity: 1, y: 0
Duration: 0.3s
```

### Acordeón Expandible
```
Collapsed: height: 0, opacity: 0
Expanded: height: auto, opacity: 1
Duration: 0.3s
Chevron: rotate 0° → 180°
```

### Tarjetas de Tarea
```
Hover: scale 1.00 → 1.01
Tap: scale 1.00 → 0.99
Urgencia: opacity pulse (1 → 0.6 → 1)
```

### Modales
```
Initial: opacity: 0, scale: 0.95, y: 20
Animate: opacity: 1, scale: 1, y: 0
Duration: 0.2s

Backdrop:
Initial: opacity: 0
Animate: opacity: 1
```

### Progress Bar
```
Initial: width: 0
Animate: width: {percentage}%
Duration: 0.6s
Ease: easeOut
```

---

## 📊 Datos Flow

```
┌─────────────────────────────┐
│   React Query               │
│   GET /api/grupos/{id}/tareas
│   Cache: 5 minutos          │
└──────────────┬──────────────┘
               │
               ▼
        ┌──────────────┐
        │  tareas[]    │
        └──────┬───────┘
               │
    ┌──────────┴──────────┐
    │                     │
    ▼                     ▼
┌────────────────┐  ┌──────────────────┐
│ filteredTareas │  │ tareasPorEstado  │
│ useMemo()      │  │ useMemo()        │
│                │  │ {estado: []}     │
└────────┬───────┘  └────────┬─────────┘
         │                   │
         ▼                   ▼
┌─────────────────────────────────────┐
│      TareasAccordion                │
│      TareasStatistics               │
│      (Renderiza componentes)        │
└─────────────────────────────────────┘
```

---

## 🔄 Flujo de Creación de Tarea

```
1. Usuario hace click "Nueva Tarea"
   │
   ├─ showCreateModal = true
   │
   ▼
2. TareaFormModal se abre
   │
   ├─ Backdrop blur + fade in
   ├─ Form fields limpios
   ├─ Errors = {}
   │
   ▼
3. Usuario llena formulario
   │
   ├─ onChange → setState (formData)
   ├─ Validación live en campos
   │
   ▼
4. Usuario hace submit
   │
   ├─ validateForm()
   ├─ Si errores → mostrar messages
   ├─ Si OK → isSubmitting = true
   │
   ▼
5. onSubmit(submitData)
   │
   ├─ Crea objeto TareaCreateRequest
   ├─ POST /api/cursos/{id}/tareas
   │
   ▼
6. Backend valida + crea
   │
   ├─ 201 Created ✅
   ├─ Retorna Tarea
   │
   ▼
7. Frontend actualiza
   │
   ├─ showCreateModal = false
   ├─ refetch() React Query
   ├─ Accordion se actualiza
   ├─ Statistics se recalculan
   │
   ▼
8. Usuario ve nueva tarea
   │
   └─ En el acordeón correcto
```

---

## 📈 Cálculos de Estadísticas

```typescript
Total = tareas.length

Completadas = calificadas + cerradas

PorcentajeCompletitud = (completadas / total) * 100

PromedioPuntos = sum(puntuacion_maxima) / total

Urgentes = tareas where (
  fecha_limite <= hoy + 2 días
  AND fecha_limite > hoy
)

TareasVencidas = tareas where (
  fecha_limite < hoy
)

Desglose = {
  asignada: count,
  en_progreso: count,
  entregada: count,
  calificada: count,
  vencida: count,
  cerrada: count
}
```

---

## 🔍 Búsqueda y Filtros

```
Búsqueda (título)
├─ Input text
├─ Case-insensitive
└─ Real-time match

Tipo (9 opciones)
├─ ensayo
├─ proyecto
├─ ejercicios
├─ investigacion
├─ presentacion
├─ laboratorio
├─ lectura
├─ examen
└─ otro

Prioridad (3 niveles)
├─ baja
├─ media
└─ alta

Estado (6 estados)
├─ asignada
├─ en_progreso
├─ entregada
├─ calificada
├─ vencida
└─ cerrada

Lógica: AND (todos deben coincidir)
```

---

## 🎯 Indicadores Visuales

### Tarjeta de Tarea

```
📝 Título de tarea importante     [Priority Badge]
Descripción breve de la tarea...

📅 Fecha: Mañana (1 día) • ⭐ 100 pts  [👁️]
```

### Cuando está próxima a vencer (< 48h)

```
border-red-300 dark:border-red-700
bg-red-50/50 dark:bg-red-900/10
Parpadeo rojo en esquina superior
```

### En estado URGENTE

```
Pulsea continuamente
opacity: 1 → 0.6 → 1
Cada 2 segundos
```

---

## 💾 Estado Local (TareasPage)

```typescript
interface TareasPageState {
  showCreateModal: boolean;        // Modal visible?
  showPreviewModal: boolean;       // Preview visible?
  selectedTarea: Tarea | null;     // Tarea seleccionada
  searchTerm: string;              // Búsqueda activa
  filterType: TipoTarea | "all";   // Tipo seleccionado
  filterPriority: PrioridadTarea | "all";  // Prioridad
  filterStatus: EstadoTarea | "all";      // Estado
}
```

---

## 🎬 Transiciones Detalladas

### Modal Aparición
```
Timing secuencial:
1. Backdrop fade in        (0.0s)
2. Modal scale + fade      (0.0s - 0.2s)
3. Header content fade     (0.1s - 0.2s)
4. Form fields fade        (0.2s - 0.4s)
```

### Acordeón Expansión
```
1. Header click → toggle state
2. Chevron rotar 180°
3. Content slideDown con fade
4. Cards fade in secuencialmente
```

### Progress Bar Llenado
```
Initial: width 0
Target: width {percentage}%
Duration: 0.6s
Ease: easeOut
```

---

## 📐 Dimensiones

### TareasPage
```
max-w-7xl
mx-auto
padding: p-6
```

### Sidebar (Statistics)
```
lg:col-span-1  (desktop)
width: ~25%
```

### Main (Accordion)
```
lg:col-span-2  (desktop)
width: ~75%
```

### Modal
```
max-w-2xl
w-full
max-h-[90vh]
overflow-y-auto
```

### Tarjeta
```
p-3 (pequeña padding)
rounded-lg
border-2
hover: scale 1.01
```

---

## 🎨 Tipografía

### Títulos
```
H1: text-4xl font-bold
H2: text-2xl font-bold
H3: text-xl font-bold
Labels: text-sm font-semibold
```

### Texto
```
Body: text-slate-900 dark:text-white
Secondary: text-slate-600 dark:text-slate-400
Tertiary: text-xs text-slate-500
```

---

## ✅ Este es el PHASE 3 Completado

**Componentes listos para producción**:
- ✅ TareasPage
- ✅ TareasAccordion
- ✅ TareaCardItem
- ✅ TareasStatistics
- ✅ TareaFormModal
- ✅ TareaPreviewModal

**Próximo**: PHASE 4 - Design System refinement

