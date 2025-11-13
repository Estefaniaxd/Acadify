# 🎓 Módulo de Programas Académicos

Módulo completo para gestión de programas académicos con arquitectura SOLID, React Query y TypeScript.

## 📋 Contenido

- [Características](#-características)
- [Estructura](#-estructura)
- [Instalación](#-instalación)
- [Uso](#-uso)
- [API](#-api)
- [Componentes](#-componentes)
- [Hooks](#-hooks)
- [Tipos](#-tipos)
- [Ejemplos](#-ejemplos)

## ✨ Características

- ✅ **CRUD Completo**: Crear, leer, actualizar y eliminar programas
- ✅ **Búsqueda en Tiempo Real**: Filtro por nombre, código o descripción
- ✅ **Filtros Avanzados**: Por institución, nivel, modalidad y estado
- ✅ **Paginación**: Navegación eficiente de grandes volúmenes de datos
- ✅ **Validación**: Formularios con validación en tiempo real
- ✅ **Caché Inteligente**: React Query para optimización de performance
- ✅ **Actualizaciones Optimistas**: UX instantánea
- ✅ **TypeScript**: 100% tipado estático
- ✅ **Responsive**: Diseño adaptable a móvil, tablet y desktop
- ✅ **Dark Mode**: Soporte completo para modo oscuro
- ✅ **Estadísticas**: Visualización de métricas del programa

## 📁 Estructura

```
src/modules/programas/
├── components/              # Componentes React
│   ├── ListaProgramas.tsx   # Lista con filtros y paginación
│   ├── FormularioPrograma.tsx # Formulario crear/editar
│   ├── DetallePrograma.tsx  # Vista detallada
│   └── index.ts             # Barrel export
├── hooks/                   # React Query hooks
│   └── useProgramas.ts      # 11 hooks personalizados
├── services/                # Capa de servicios
│   └── programaService.ts   # Cliente API REST
├── types.ts                 # Definiciones TypeScript
└── index.ts                 # Export principal
```

## 🚀 Instalación

El módulo ya está integrado en el proyecto. Las rutas disponibles son:

```typescript
/admin/programas               // Lista de programas
/admin/programas/crear         // Crear nuevo programa
/admin/programas/:id           // Ver detalle
/admin/programas/:id/editar    // Editar programa
```

## 💻 Uso

### En Rutas (App.tsx)

```tsx
import { ListaProgramas, FormularioPrograma, DetallePrograma } from './modules/programas';

// Ya están integradas en App.tsx
```

### En Componentes

```tsx
import { useProgramas, usePrograma } from '@/modules/programas';

function MiComponente() {
  // Obtener lista de programas
  const { data, isLoading } = useProgramas({
    institucionId: 1,
    nivel: 'PROFESIONAL',
    pagina: 1,
    limite: 10
  });

  // Obtener programa específico
  const { data: programa } = usePrograma(5);

  return <div>{/* ... */}</div>;
}
```

## 🌐 API

### Endpoints

Todos los endpoints están bajo `/api/v1/academic/programas`:

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| `GET` | `/` | Lista paginada con filtros |
| `GET` | `/:id` | Obtener por ID |
| `GET` | `/:id/estadisticas` | Estadísticas del programa |
| `GET` | `/:id/malla-curricular` | Malla curricular |
| `GET` | `/search?q=term` | Búsqueda por término |
| `POST` | `/` | Crear programa |
| `PUT` | `/:id` | Actualizar programa |
| `PATCH` | `/:id/estado` | Cambiar estado |
| `POST` | `/:id/cursos` | Asignar cursos |
| `DELETE` | `/:id` | Eliminar programa |

### Servicio (`programaService`)

```typescript
import { programaService } from '@/modules/programas';

// Obtener todos
const programas = await programaService.getAll({ institucionId: 1 });

// Obtener por ID
const programa = await programaService.getById(5);

// Crear
const nuevo = await programaService.create({
  codigo: 'ING-SW-001',
  nombre: 'Ingeniería de Software',
  nivel: 'PROFESIONAL',
  modalidad: 'PRESENCIAL',
  duracionSemestres: 10,
  creditosRequeridos: 160,
  institucionId: 1,
  requiereProyectoGrado: true,
  requierePracticas: true,
  horasPracticas: 480
});

// Actualizar
const actualizado = await programaService.update(5, {
  nombre: 'Nuevo Nombre'
});

// Eliminar
await programaService.delete(5);

// Cambiar estado
await programaService.cambiarEstado(5, 'INACTIVO');

// Obtener estadísticas
const stats = await programaService.getEstadisticas(5);

// Asignar cursos
await programaService.asignarCursos({
  programaId: 5,
  cursoIds: [1, 2, 3],
  nivel: 1,
  esObligatorio: true
});
```

## 🧩 Componentes

### ListaProgramas

Componente principal que muestra lista paginada con filtros.

**Props:** Ninguna (usa hooks internos)

**Features:**
- Búsqueda en tiempo real
- Filtros: nivel, modalidad, estado, ordenamiento
- Paginación
- Cards con estadísticas
- Acciones CRUD
- Loading skeletons
- Error handling

**Ejemplo:**
```tsx
<Route path="/admin/programas" element={<ListaProgramas />} />
```

### FormularioPrograma

Formulario para crear/editar programas.

**Props:**
```typescript
interface FormularioProgramaProps {
  modo?: 'crear' | 'editar';
}
```

**Features:**
- Validación en tiempo real
- Select de instituciones
- Campos numéricos con rangos
- Checkboxes para requisitos
- Manejo de errores específicos
- Loading states

**Ejemplo:**
```tsx
<FormularioPrograma modo="crear" />
<FormularioPrograma modo="editar" />
```

### DetallePrograma

Vista detallada de un programa con estadísticas.

**Props:** Ninguna (usa `useParams` para obtener ID)

**Features:**
- Información completa del programa
- Estadísticas visuales
- Requisitos académicos
- Navegación a edición
- Error handling

## 🪝 Hooks

### useProgramas

Obtiene lista paginada de programas con filtros.

```typescript
const { data, isLoading, error, refetch } = useProgramas({
  busqueda: 'ingeniería',
  institucionId: 1,
  nivel: 'PROFESIONAL',
  modalidad: 'PRESENCIAL',
  estado: 'ACTIVO',
  ordenarPor: 'nombre',
  orden: 'asc',
  pagina: 1,
  limite: 10
});

// data: RespuestaPaginada<Programa>
// data.items: Programa[]
// data.total: number
// data.totalPaginas: number
```

### usePrograma

Obtiene un programa específico por ID.

```typescript
const { data: programa, isLoading } = usePrograma(5);

// programa: Programa | undefined
```

### useProgramasPorInstitucion

Obtiene programas de una institución.

```typescript
const { data } = useProgramasPorInstitucion(1, {
  estado: 'ACTIVO'
});
```

### useEstadisticasPrograma

Obtiene estadísticas de un programa.

```typescript
const { data: stats } = useEstadisticasPrograma(5);

// stats.tasaGraduacion: number
// stats.estudiantesActivos: number
// stats.estudiantesGraduados: number
```

### useMallaCurricular

Obtiene la malla curricular.

```typescript
const { data: malla } = useMallaCurricular(5);

// malla.semestres: SemestreMalla[]
// malla.creditosTotales: number
```

### useBuscarProgramas

Búsqueda por término.

```typescript
const { data: resultados } = useBuscarProgramas('ingeniería');
```

### useCrearPrograma

Mutación para crear programa.

```typescript
const crearPrograma = useCrearPrograma();

const handleSubmit = async (data: CrearProgramaDTO) => {
  try {
    await crearPrograma.mutateAsync(data);
    alert('Programa creado');
  } catch (error) {
    alert(error.message);
  }
};
```

### useActualizarPrograma

Mutación para actualizar programa.

```typescript
const actualizarPrograma = useActualizarPrograma();

await actualizarPrograma.mutateAsync({
  id: 5,
  data: { nombre: 'Nuevo Nombre' }
});
```

### useEliminarPrograma

Mutación para eliminar programa.

```typescript
const eliminarPrograma = useEliminarPrograma();

await eliminarPrograma.mutateAsync(5);
```

### useCambiarEstadoPrograma

Mutación para cambiar estado.

```typescript
const cambiarEstado = useCambiarEstadoPrograma();

await cambiarEstado.mutateAsync({
  id: 5,
  estado: 'INACTIVO'
});
```

### useAsignarCursos

Mutación para asignar cursos.

```typescript
const asignarCursos = useAsignarCursos();

await asignarCursos.mutateAsync({
  programaId: 5,
  cursoIds: [1, 2, 3],
  nivel: 1,
  esObligatorio: true
});
```

### useProgramaOperations

Hook combinado con todas las operaciones.

```typescript
const { crear, actualizar, eliminar, cambiarEstado, asignarCursos } = useProgramaOperations();

// Usar cualquier operación
await crear.mutateAsync(data);
await actualizar.mutateAsync({ id, data });
await eliminar.mutateAsync(id);
```

## 📝 Tipos

### Programa

```typescript
interface Programa {
  id: number;
  codigo: string;
  nombre: string;
  descripcion?: string;
  nivel: NivelAcademico;
  modalidad: ModalidadEstudio;
  duracionSemestres: number;
  creditosRequeridos: number;
  estado: EstadoPrograma;
  institucionId: number;
  institucion?: InstitucionBasica;
  totalCursos: number;
  totalEstudiantes: number;
  requiereProyectoGrado: boolean;
  requierePracticas: boolean;
  horasPracticas?: number;
  fechaCreacion: string;
  fechaActualizacion: string;
}
```

### Enums

```typescript
enum NivelAcademico {
  TECNICO = 'TECNICO',
  TECNOLOGO = 'TECNOLOGO',
  PROFESIONAL = 'PROFESIONAL',
  ESPECIALIZACION = 'ESPECIALIZACION',
  MAESTRIA = 'MAESTRIA',
  DOCTORADO = 'DOCTORADO'
}

enum ModalidadEstudio {
  PRESENCIAL = 'PRESENCIAL',
  VIRTUAL = 'VIRTUAL',
  HIBRIDO = 'HIBRIDO'
}

enum EstadoPrograma {
  ACTIVO = 'ACTIVO',
  INACTIVO = 'INACTIVO',
  EN_REVISION = 'EN_REVISION',
  ARCHIVADO = 'ARCHIVADO'
}
```

## 🎯 Ejemplos Completos

### Crear Programa

```tsx
import { useCrearPrograma } from '@/modules/programas';

function CrearProgramaPage() {
  const crearPrograma = useCrearPrograma();
  
  const handleSubmit = async (e) => {
    e.preventDefault();
    
    try {
      await crearPrograma.mutateAsync({
        codigo: 'ING-SW-001',
        nombre: 'Ingeniería de Software',
        descripcion: 'Programa de ingeniería enfocado en desarrollo de software',
        nivel: 'PROFESIONAL',
        modalidad: 'PRESENCIAL',
        duracionSemestres: 10,
        creditosRequeridos: 160,
        institucionId: 1,
        requiereProyectoGrado: true,
        requierePracticas: true,
        horasPracticas: 480
      });
      
      alert('Programa creado exitosamente');
      navigate('/admin/programas');
    } catch (error) {
      alert(error.message);
    }
  };
  
  return <form onSubmit={handleSubmit}>{/* ... */}</form>;
}
```

### Lista con Filtros

```tsx
import { useProgramas } from '@/modules/programas';

function ProgramasPorInstitucion({ institucionId }) {
  const [nivel, setNivel] = useState('');
  
  const { data, isLoading } = useProgramas({
    institucionId,
    nivel: nivel || undefined,
    estado: 'ACTIVO',
    ordenarPor: 'nombre',
    orden: 'asc'
  });
  
  if (isLoading) return <Spinner />;
  
  return (
    <div>
      <select value={nivel} onChange={(e) => setNivel(e.target.value)}>
        <option value="">Todos los niveles</option>
        <option value="PROFESIONAL">Profesional</option>
        <option value="MAESTRIA">Maestría</option>
      </select>
      
      <div>
        {data?.items.map(programa => (
          <ProgramaCard key={programa.id} programa={programa} />
        ))}
      </div>
    </div>
  );
}
```

## 🏗️ Arquitectura

### Principios SOLID Aplicados

**S - Single Responsibility**
- `programaService`: Solo comunicación API
- `useProgramas`: Solo estado y caché
- Componentes: Solo UI y lógica de presentación

**O - Open/Closed**
- Filtros extensibles sin modificar código
- Tipos genéricos (`RespuestaPaginada<T>`)

**L - Liskov Substitution**
- Hooks intercambiables
- Componentes reutilizables

**I - Interface Segregation**
- DTOs específicos (Crear, Actualizar)
- Interfaces mínimas necesarias

**D - Dependency Inversion**
- Hooks dependen de abstracciones (React Query)
- Componentes dependen de hooks, no de servicio directo

## 🔧 Troubleshooting

### Error: "Programa no encontrado"
- Verifica que el ID existe
- Verifica permisos del usuario
- Revisa el token de autenticación

### Error: "Ya existe un programa con ese código"
- El código debe ser único
- Cambia el código o actualiza el existente

### Error: "No se puede eliminar programa con estudiantes activos"
- Primero reasigna los estudiantes
- O archiva el programa en lugar de eliminarlo

## 📊 Performance

- **Caché**: 5 minutos para listas, 10 minutos para estructuras estables
- **Code Splitting**: ~140KB bundle size (lazy loading)
- **Optimistic Updates**: UX instantánea en actualizaciones
- **Debounce**: Búsqueda con 300ms de retraso

## 🤝 Contribuir

Al agregar nuevas features:

1. Actualiza tipos en `types.ts`
2. Agrega método en `programaService.ts`
3. Crea hook en `useProgramas.ts`
4. Actualiza componentes si es necesario
5. Documenta en este README

## 📄 Licencia

Parte del proyecto Acadify - SENA 2025

---

**Desarrollado con ❤️ usando React, TypeScript y React Query**
