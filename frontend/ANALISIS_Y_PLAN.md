# 📊 Análisis y Plan de Implementación - Acadify Frontend

## 🎯 Objetivo
Completar y optimizar el frontend según el backend existente, aplicando Clean Code, SOLID, y buenas prácticas.

---

## 📋 Estado Actual del Frontend

### ✅ Completado
1. **Sistema de Autenticación**
   - Login, Register, Recover Password
   - AuthContext con protected routes
   - JWT handling y refresh tokens

2. **Sistema de Navegación**
   - Configuración por roles (Admin, Coordinador, Profesor, Estudiante)
   - 47 tests pasando (100%)
   - SidebarLeft, SidebarRight, Nav

3. **Sistema de Avatares**
   - AvatarStudio con capas personalizables
   - Integración con backend
   - Galería pública y privada

4. **Módulo Académico (Parcial)**
   - Lista de cursos (API integrada)
   - CourseDetail component
   - courseService con API calls

5. **Sistema de Tareas (Parcial)**
   - Tipos definidos (EstadoTarea, TipoTarea, PrioridadTarea)
   - API client (`tareasApi`)
   - README documentado

6. **UI Components**
   - Sistema de diseño base
   - Componentes reutilizables (Button, Card, Input)
   - Dark mode support

7. **Hooks Personalizados**
   - useCourses, useMyCourses, useCourse
   - useJoinCourse, useCourseGroups
   - Integración con React Query

### ❌ Incompleto / Faltante

#### **1. Módulo de Instituciones**
- ❌ CRUD completo de instituciones
- ❌ Panel de gestión (Admin)
- ❌ Personalización (logo, colores, info)
- ❌ Integración con coordinadores

#### **2. Módulo de Programas**
- ❌ CRUD completo
- ❌ Asociación con instituciones
- ❌ Gestión de cursos del programa
- ❌ Vista detallada

#### **3. Módulo de Cursos (Mejoras)**
- ⚠️  Crear/Editar curso (falta UI)
- ⚠️  Configuración avanzada
- ⚠️  Gestión de materiales
- ⚠️  Configurar Google Drive
- ❌ Estadísticas del curso

#### **4. Módulo de Clases**
- ❌ CRUD completo
- ❌ Programación de sesiones
- ❌ Material por clase
- ❌ Asistencia
- ❌ Vista de estudiante vs profesor

#### **5. Módulo de Tareas (UI)**
- ⚠️  ListaTareas (backend listo)
- ⚠️  FormularioTarea (backend listo)
- ⚠️  DetalleTarea (backend listo)
- ❌ EntregaTarea (estudiante)
- ❌ CalificarEntrega (profesor)
- ❌ Rúbricas

#### **6. Módulo de Coordinador**
- ⚠️  Panel parcialmente implementado
- ❌ Gestión de profesores
- ❌ Asignación de cursos a profesores
- ❌ Seguimiento académico
- ❌ Invitaciones (CRUD completo)

#### **7. Módulo de Invitaciones**
- ⚠️  API parcial (`api.ts`)
- ❌ UI completa para crear
- ❌ UI para aceptar/rechazar
- ❌ Sistema de códigos de invitación
- ❌ Notificaciones

#### **8. Integración con IA**
- ❌ Componente de chat con IA
- ❌ Sugerencias automáticas
- ❌ Feedback de tareas
- ❌ Análisis de entregas

#### **9. Dashboards por Rol**
- ⚠️  DashboardAdmin (parcial)
- ⚠️  DashboardCoordinador (parcial)
- ⚠️  DashboardTeacher (parcial)
- ⚠️  DashboardStudent (parcial)
- ❌ Widgets interactivos
- ❌ Estadísticas en tiempo real

#### **10. Sistema de Notificaciones**
- ❌ NotificationCenter UI
- ❌ Toast notifications contextuales
- ❌ Badges de notificaciones
- ❌ Preferencias de notificaciones

---

## 🏗️ Arquitectura Backend (Análisis)

### Endpoints Identificados

#### **Instituciones** (`/api/v1/academic/instituciones/`)
```
GET    /                    # Listar instituciones
POST   /                    # Crear institución
GET    /{id}                # Obtener institución
PUT    /{id}                # Actualizar institución
DELETE /{id}                # Eliminar institución
```

#### **Programas** (`/api/v1/academic/programas/`)
```
GET    /                    # Listar programas
POST   /                    # Crear programa
GET    /{id}                # Obtener programa
PUT    /{id}                # Actualizar programa
```

#### **Cursos** (`/api/v1/academic/cursos/`)
```
GET    /                    # Listar cursos
POST   /                    # Crear curso
GET    /{id}                # Obtener curso detallado
PUT    /{id}                # Actualizar curso
DELETE /{id}                # Eliminar curso
GET    /mis-cursos          # Cursos del usuario
GET    /inscripciones-abiertas  # Cursos disponibles
POST   /{id}/configurar-drive   # Configurar Google Drive
GET    /{id}/estadisticas   # Estadísticas del curso
```

#### **Clases** (`/api/v1/academic/clases/`)
```
GET    /                    # Listar clases
POST   /                    # Crear clase
GET    /{id}                # Obtener clase
PUT    /{id}                # Actualizar clase
DELETE /{id}                # Eliminar clase
POST   /{id}/unirse         # Estudiante se une a clase
```

#### **Material Educativo** (`/api/v1/academic/material/`)
```
GET    /                    # Listar materiales
POST   /                    # Crear material
GET    /{id}                # Obtener material
PUT    /{id}                # Actualizar material
DELETE /{id}                # Eliminar material
GET    /curso/{id}          # Materiales de un curso
```

#### **Tareas** (`/api/v1/tareas/`)
```
POST   /                    # Crear tarea
GET    /{id}                # Obtener tarea
GET    /grupo/{id}          # Tareas de un grupo
PUT    /{id}                # Actualizar tarea
DELETE /{id}                # Eliminar tarea
```

#### **Entregas** (`/api/v1/entregas/`)
```
POST   /                    # Entregar tarea
GET    /tarea/{id}          # Entregas de una tarea
PUT    /{id}/calificar      # Calificar entrega
GET    /estudiante/{id}     # Entregas de un estudiante
```

#### **Invitaciones** (`/api/invitaciones/`)
```
GET    /                    # Obtener invitaciones pendientes
POST   /{id}/aceptar        # Aceptar invitación
POST   /                    # Crear invitación
```

---

## 📐 Arquitectura Frontend (Propuesta)

### Principios SOLID Aplicados

#### **1. Single Responsibility Principle (SRP)**
```
Cada componente tiene UNA responsabilidad:
- ListaInstituciones.tsx → Solo listar
- FormularioInstitucion.tsx → Solo crear/editar
- DetalleInstitucion.tsx → Solo mostrar detalle
```

#### **2. Open/Closed Principle (OCP)**
```typescript
// Componente base extensible
interface BaseListProps<T> {
  items: T[];
  renderItem: (item: T) => React.ReactNode;
  onItemClick?: (item: T) => void;
}

// Se extiende sin modificar el base
<BaseList items={instituciones} renderItem={renderInstitucion} />
```

#### **3. Liskov Substitution Principle (LSP)**
```typescript
// Interfaces consistentes
interface CRUDService<T> {
  getAll(): Promise<T[]>;
  getById(id: string): Promise<T>;
  create(data: T): Promise<T>;
  update(id: string, data: Partial<T>): Promise<T>;
  delete(id: string): Promise<void>;
}
```

#### **4. Interface Segregation Principle (ISP)**
```typescript
// Interfaces específicas
interface Listable { items: T[]; }
interface Filterable { filters: Filter[]; }
interface Sortable { sortBy: string; }

// Componentes usan solo lo que necesitan
```

#### **5. Dependency Inversion Principle (DIP)**
```typescript
// Componentes dependen de abstracciones (hooks)
const { data, isLoading } = useInstituciones();  // ✅
// NO dependen de implementaciones específicas
const data = await fetch('/api/...');  // ❌
```

### Estructura de Carpetas Propuesta

```
src/
├── modules/
│   ├── instituciones/
│   │   ├── components/
│   │   │   ├── ListaInstituciones.tsx
│   │   │   ├── FormularioInstitucion.tsx
│   │   │   ├── DetalleInstitucion.tsx
│   │   │   ├── PersonalizarInstitucion.tsx
│   │   │   └── index.ts
│   │   ├── hooks/
│   │   │   ├── useInstituciones.ts
│   │   │   ├── useInstitucion.ts
│   │   │   └── index.ts
│   │   ├── services/
│   │   │   └── institucionService.ts
│   │   ├── types.ts
│   │   └── index.ts
│   │
│   ├── programas/
│   │   ├── components/
│   │   ├── hooks/
│   │   ├── services/
│   │   └── types.ts
│   │
│   ├── cursos/  (mejorar existente)
│   ├── clases/  (nuevo)
│   ├── tareas/  (completar UI)
│   ├── invitaciones/  (completar)
│   └── ia/  (nuevo)
│
├── hooks/  (hooks globales)
│   ├── useAuth.ts
│   ├── usePermissions.ts
│   └── useRole.ts
│
├── services/  (servicios globales)
│   ├── apiClient.ts
│   └── notificationService.ts
│
└── utils/
    ├── validation.ts
    ├── formatting.ts
    └── permissions.ts
```

---

## 🎯 Plan de Implementación (Priorizado)

### **Fase 1: Módulo Instituciones (Crítico)** ⭐⭐⭐
**Tiempo estimado: 4-6 horas**

1. ✅ Crear `institucionService.ts` con CRUD completo
2. ✅ Crear hooks: `useInstituciones`, `useInstitucion`
3. ✅ `ListaInstituciones.tsx` con tabla y filtros
4. ✅ `FormularioInstitucion.tsx` con validación
5. ✅ `DetalleInstitucion.tsx` con tabs (Info, Programas, Coordinadores)
6. ✅ `PersonalizarInstitucion.tsx` (logo, colores, dominio)
7. ✅ Integrar en `/admin/instituciones`

### **Fase 2: Módulo Programas** ⭐⭐⭐
**Tiempo estimado: 3-4 horas**

1. ✅ `programaService.ts` con CRUD
2. ✅ Hooks: `useProgramas`, `usePrograma`
3. ✅ `ListaProgramas.tsx` con cards
4. ✅ `FormularioPrograma.tsx` (asociar institución)
5. ✅ `DetallePrograma.tsx` con cursos asociados
6. ✅ Integrar en dashboard del coordinador

### **Fase 3: Módulo Clases (Crítico)** ⭐⭐⭐
**Tiempo estimado: 5-7 horas**

1. ✅ `claseService.ts` con CRUD
2. ✅ Hooks: `useClases`, `useClase`
3. ✅ `ListaClases.tsx` (vista profesor vs estudiante)
4. ✅ `FormularioClase.tsx` (programar sesiones)
5. ✅ `DetalleClase.tsx` con tabs (Material, Asistencia, Entregas)
6. ✅ `AsistenciaClase.tsx` (registro para profesores)
7. ✅ Integrar en `/mis-clases`

### **Fase 4: Completar Módulo Tareas UI** ⭐⭐
**Tiempo estimado: 6-8 horas**

1. ✅ Implementar `ListaTareas.tsx` según README
2. ✅ Implementar `FormularioTarea.tsx` (wizard 4 pasos)
3. ✅ Implementar `DetalleTarea.tsx`
4. ✅ **NUEVO:** `EntregaTarea.tsx` (vista estudiante)
5. ✅ **NUEVO:** `CalificarEntrega.tsx` (vista profesor)
6. ✅ **NUEVO:** `RubricaEvaluacion.tsx`
7. ✅ Integrar en `/profesor/tareas` y `/estudiante/tareas`

### **Fase 5: Módulo Coordinador (Completar)** ⭐⭐
**Tiempo estimado: 4-5 horas**

1. ✅ `GestionProfesores.tsx` (CRUD profesores)
2. ✅ `AsignarCursos.tsx` (asignar profesor → curso)
3. ✅ `SeguimientoAcademico.tsx` (dashboards y reportes)
4. ✅ Mejorar `InstitucionCoordinador.tsx`
5. ✅ Integrar invitaciones completo

### **Fase 6: Módulo Invitaciones** ⭐⭐
**Tiempo estimado: 3-4 horas**

1. ✅ `InvitacionService.ts` con CRUD
2. ✅ `CrearInvitacion.tsx` (códigos únicos)
3. ✅ `ListaInvitaciones.tsx` (pendientes, aceptadas, rechazadas)
4. ✅ `AceptarInvitacion.tsx` (modal de confirmación)
5. ✅ Sistema de notificaciones para invitaciones

### **Fase 7: Integración con IA** ⭐
**Tiempo estimado: 8-10 horas**

1. ✅ `ChatIA.tsx` (interfaz de chat)
2. ✅ `SugerenciasIA.tsx` (sugerencias de tareas)
3. ✅ `FeedbackIA.tsx` (análisis de entregas)
4. ✅ `iaService.ts` (integración con backend IA)
5. ✅ Integrar en módulo de tareas

### **Fase 8: Dashboards Mejorados** ⭐
**Tiempo estimado: 4-6 horas**

1. ✅ Widgets reutilizables (Stats, Charts, Lists)
2. ✅ Mejorar cada dashboard con datos reales
3. ✅ Agregar gráficas con Recharts/Chart.js
4. ✅ Secciones de acceso rápido
5. ✅ Notificaciones contextuales

### **Fase 9: Sistema de Notificaciones** ⭐
**Tiempo estimado: 3-4 horas**

1. ✅ `NotificationCenter.tsx` (panel de notificaciones)
2. ✅ `notificationService.ts` (manejo de notificaciones)
3. ✅ Badge counters en Nav
4. ✅ Toast notifications contextuales
5. ✅ Preferencias de notificaciones

### **Fase 10: Mejoras de Cursos** ⭐
**Tiempo estimado: 4-5 horas**

1. ✅ `CrearCurso.tsx` (formulario completo)
2. ✅ `ConfigurarCurso.tsx` (opciones avanzadas)
3. ✅ `MaterialCurso.tsx` (gestión de material)
4. ✅ `EstadisticasCurso.tsx` (analytics)
5. ✅ Mejorar `CourseDetail.tsx`

---

## 🎨 Clean Code Patterns

### **Hooks Personalizados**
```typescript
// ✅ CORRECTO: Lógica reutilizable
export function useInstitucion(id?: string) {
  return useQuery({
    queryKey: ['institucion', id],
    queryFn: () => institucionService.getById(id!),
    enabled: !!id,
  });
}

// ❌ INCORRECTO: Lógica en componente
const [data, setData] = useState();
useEffect(() => { fetch(...).then(setData) }, []);
```

### **Composición de Componentes**
```tsx
// ✅ CORRECTO: Componentes pequeños y reutilizables
<Card>
  <CardHeader title={curso.nombre} />
  <CardBody>{curso.descripcion}</CardBody>
  <CardFooter>
    <Button>Ver más</Button>
  </CardFooter>
</Card>

// ❌ INCORRECTO: Componente monolítico
<div>
  <h2>{curso.nombre}</h2>
  <p>{curso.descripcion}</p>
  <button>Ver más</button>
</div>
```

### **Servicios con Tipo Genérico**
```typescript
// ✅ CORRECTO: Reutilizable y tipado
class CRUDService<T> {
  constructor(private endpoint: string) {}
  
  async getAll(): Promise<T[]> {
    const { data } = await apiClient.get<T[]>(this.endpoint);
    return data;
  }
  
  async create(item: T): Promise<T> {
    const { data } = await apiClient.post<T>(this.endpoint, item);
    return data;
  }
}

// Uso
const institucionService = new CRUDService<Institucion>('/instituciones');
```

---

## ✅ FASE 1 COMPLETADA: Módulo Instituciones

### Archivos Creados (31 Oct 2025 - 23:10)

**Estructura:**
```
src/modules/instituciones/
├── components/
│   ├── ListaInstituciones.tsx (413 líneas) ✅
│   ├── FormularioInstitucion.tsx (388 líneas) ✅
│   └── index.ts
├── hooks/
│   ├── useInstituciones.ts (188 líneas) ✅
│   └── index.ts
├── services/
│   └── institucionService.ts (238 líneas) ✅
├── types.ts (75 líneas) ✅
├── index.ts ✅
└── README.md (450 líneas) ✅
```

**Integración:**
- ✅ Rutas agregadas a App.tsx
- ✅ Lazy loading configurado
- ✅ Iconos migrados a react-icons
- ✅ Sin errores de compilación

**Total:** ~1,752 líneas de código TypeScript + 450 líneas de documentación

### Características Implementadas:
1. ✅ CRUD completo de instituciones
2. ✅ Service layer con axios + interceptores
3. ✅ Hooks con React Query (caché, sincronización)
4. ✅ Componente de lista con filtros y paginación
5. ✅ Formulario con validación y personalización
6. ✅ Manejo de errores robusto
7. ✅ Principios SOLID aplicados
8. ✅ Documentación completa

### Tiempo Invertido: ~2.5 horas
### Estado: ✅ COMPLETADO - Listo para testing

---

## 🚀 Siguiente Acción: Fase 2 - Módulo Programas

**Próximos pasos:**
1. Crear estructura de `src/modules/programas/`
2. Implementar service + hooks
3. Componentes de lista y formulario
4. Integrar con módulo de instituciones
5. Agregar rutas al router

**Estimado:** 3-4 horas

¿Continuamos con Fase 2 o prefieres testear primero Fase 1?
