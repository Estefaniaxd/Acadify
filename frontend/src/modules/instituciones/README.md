# 🏛️ Módulo de Instituciones

## 📋 Descripción
Módulo completo para la gestión de instituciones educativas en Acadify. Implementa operaciones CRUD con principios SOLID y Clean Code.

## ✨ Características

### Funcionalidades Principales
- ✅ **Lista de instituciones** con filtros avanzados
- ✅ **Crear/Editar instituciones** con validación
- ✅ **Eliminar instituciones** (con confirmación)
- ✅ **Activar/Desactivar** instituciones
- ✅ **Búsqueda** en tiempo real
- ✅ **Paginación** eficiente
- ✅ **Personalización** visual (colores, logo)
- ✅ **Estadísticas** por institución
- ✅ **Gestión de coordinadores** (próximamente)
- ✅ **Gestión de programas** (próximamente)

### Principios Implementados

#### 1. **Single Responsibility Principle (SRP)**
```
- ListaInstituciones.tsx → Solo muestra la lista
- FormularioInstitucion.tsx → Solo maneja formulario
- institucionService.ts → Solo comunica con API
- useInstituciones.ts → Solo maneja estado con React Query
```

#### 2. **Open/Closed Principle (OCP)**
El servicio es extensible sin modificar código existente:
```typescript
class InstitucionService {
  // Métodos base (cerrados)
  async getAll() {}
  async create() {}
  
  // Se pueden agregar nuevos métodos sin modificar existentes
  async getEstadisticas() {}
  async updatePersonalizacion() {}
}
```

#### 3. **Liskov Substitution Principle (LSP)**
Todas las operaciones CRUD siguen el mismo contrato:
```typescript
interface CRUDService<T> {
  getAll(): Promise<T[]>;
  getById(id: string): Promise<T>;
  create(data: T): Promise<T>;
  update(id: string, data: T): Promise<T>;
  delete(id: string): Promise<void>;
}
```

#### 4. **Interface Segregation Principle (ISP)**
Los componentes solo importan lo que necesitan:
```typescript
// Componente solo usa lo necesario
import { useInstituciones, useEliminarInstitucion } from '../hooks';
```

#### 5. **Dependency Inversion Principle (DIP)**
Los componentes dependen de abstracciones (hooks), no de implementaciones:
```typescript
// ✅ Componente depende de abstracción
const { data } = useInstituciones();

// ❌ NO depende de implementación directa
const data = await fetch('/api/instituciones');
```

## 📁 Estructura del Módulo

```
src/modules/instituciones/
├── components/
│   ├── ListaInstituciones.tsx      # Lista con filtros y paginación
│   ├── FormularioInstitucion.tsx   # Crear/Editar institución
│   └── index.ts
├── hooks/
│   ├── useInstituciones.ts         # Hooks de React Query
│   └── index.ts
├── services/
│   └── institucionService.ts       # Cliente API con axios
├── types.ts                        # Tipos TypeScript
├── index.ts                        # Exportaciones públicas
└── README.md                       # Esta documentación
```

## 🔌 API Endpoints

### Instituciones
```
GET    /api/v1/academic/instituciones/            # Listar (con filtros)
POST   /api/v1/academic/instituciones/            # Crear
GET    /api/v1/academic/instituciones/{id}        # Obtener
PUT    /api/v1/academic/instituciones/{id}        # Actualizar
DELETE /api/v1/academic/instituciones/{id}        # Eliminar
GET    /api/v1/academic/instituciones/{id}/estadisticas  # Estadísticas
POST   /api/v1/academic/instituciones/{id}/personalizacion  # Personalizar
POST   /api/v1/academic/instituciones/{id}/logo   # Subir logo
GET    /api/v1/academic/instituciones/buscar?q=   # Buscar
```

## 🎯 Uso

### Importar el módulo completo
```typescript
import { 
  ListaInstituciones, 
  FormularioInstitucion,
  useInstituciones,
  institucionService,
  type Institucion 
} from '@/modules/instituciones';
```

### Usar hooks en componentes
```typescript
function MiComponente() {
  // Obtener lista con filtros
  const { data, isLoading, error } = useInstituciones({
    busqueda: 'Universidad',
    activo: true,
    pagina: 1,
    limite: 10
  });

  // Crear institución
  const crearMutation = useCrearInstitucion();
  await crearMutation.mutateAsync({
    nombre: 'Universidad Nacional',
    email: 'contacto@un.edu.co',
    colorPrimario: '#3B82F6'
  });

  // Actualizar institución
  const actualizarMutation = useActualizarInstitucion();
  await actualizarMutation.mutateAsync({
    id: '123',
    data: { nombre: 'Nuevo Nombre' }
  });

  // Eliminar institución
  const eliminarMutation = useEliminarInstitucion();
  await eliminarMutation.mutateAsync('123');
}
```

### Usar servicio directamente (sin React Query)
```typescript
import { institucionService } from '@/modules/instituciones';

// Obtener todas las instituciones
const instituciones = await institucionService.getAll({
  activo: true,
  ordenarPor: 'nombre'
});

// Crear institución
const nueva = await institucionService.create({
  nombre: 'Mi Institución',
  descripcion: 'Descripción...'
});

// Subir logo
const logoUrl = await institucionService.uploadLogo('123', file);
```

## 🧪 Testing (Próximamente)

### Unit Tests
```typescript
describe('institucionService', () => {
  it('debe crear una institución', async () => {
    const institucion = await institucionService.create({
      nombre: 'Test Universidad'
    });
    expect(institucion).toBeDefined();
    expect(institucion.nombre).toBe('Test Universidad');
  });
});
```

### Integration Tests
```typescript
describe('useInstituciones hook', () => {
  it('debe obtener lista de instituciones', async () => {
    const { result } = renderHook(() => useInstituciones());
    await waitFor(() => expect(result.current.isLoading).toBe(false));
    expect(result.current.data).toBeDefined();
  });
});
```

## 🎨 Componentes UI

### ListaInstituciones
**Props:** Ninguno (usa state interno)

**Características:**
- Grid responsivo (1-3 columnas)
- Búsqueda en tiempo real
- Filtros: Estado (activo/inactivo), Ordenar por (nombre/fecha/estudiantes)
- Paginación
- Acciones: Ver, Editar, Activar/Desactivar, Eliminar
- Loading skeletons
- Empty states
- Error handling con retry

### FormularioInstitucion
**Props:**
```typescript
interface Props {
  institucionId?: string;        // Para editar
  modo?: 'crear' | 'editar';    // Modo del formulario
}
```

**Características:**
- Validación en tiempo real
- Upload de logo (max 5MB, preview)
- Color pickers para personalización
- Auto-guardado en caché
- Error messages específicos
- Loading states
- Navegación con confirmación

## 🔐 Permisos por Rol

| Acción               | Admin | Coordinador | Profesor | Estudiante |
|---------------------|-------|-------------|----------|------------|
| Ver lista           | ✅    | ✅          | ❌       | ❌         |
| Ver detalle         | ✅    | ✅ (solo asignada) | ❌       | ❌         |
| Crear               | ✅    | ❌          | ❌       | ❌         |
| Editar              | ✅    | ⚠️ (limitado) | ❌       | ❌         |
| Eliminar            | ✅    | ❌          | ❌       | ❌         |
| Activar/Desactivar  | ✅    | ❌          | ❌       | ❌         |
| Personalizar        | ✅    | ⚠️ (limitado) | ❌       | ❌         |

## 📊 Tipos de Datos

### Institucion
```typescript
interface Institucion {
  id: string;
  nombre: string;
  descripcion?: string;
  logo?: string;
  colorPrimario?: string;
  colorSecundario?: string;
  dominio?: string;
  direccion?: string;
  telefono?: string;
  email?: string;
  sitioWeb?: string;
  activo: boolean;
  fechaCreacion: string;
  fechaActualizacion?: string;
  coordinadores?: Coordinador[];
  programas?: ProgramaBasico[];
  estadisticas?: EstadisticasInstitucion;
}
```

### Filtros
```typescript
interface FiltrosInstitucion {
  busqueda?: string;
  activo?: boolean;
  ordenarPor?: 'nombre' | 'fecha' | 'estudiantes';
  orden?: 'asc' | 'desc';
  pagina?: number;
  limite?: number;
}
```

## 🚀 Próximas Características

### En desarrollo
- [ ] Componente `DetalleInstitucion.tsx`
- [ ] Gestión de coordinadores
- [ ] Gestión de programas
- [ ] Estadísticas avanzadas
- [ ] Exportar a PDF/Excel
- [ ] Historial de cambios
- [ ] Modo bulk (crear/editar múltiples)

### Planeado
- [ ] Integración con Google Workspace
- [ ] Multi-tenancy
- [ ] White label por institución
- [ ] API de invitaciones
- [ ] Onboarding wizard

## 📝 Notas de Desarrollo

### Convenciones
- Todos los archivos usan **TypeScript strict mode**
- Nombres de archivos en **PascalCase** para componentes
- Nombres de archivos en **camelCase** para servicios/hooks
- **ESLint** + **Prettier** configurados
- Commits siguen **Conventional Commits**

### Performance
- **Code splitting** automático con lazy loading
- **React Query** cache configurado (5 min stale time)
- **Optimistic updates** en mutaciones
- **Debounce** en búsqueda (300ms)

### Accesibilidad
- **ARIA labels** en todos los botones
- **Keyboard navigation** completa
- **Screen reader** friendly
- **Focus management** correcto

## 🐛 Troubleshooting

### Error: "Cannot find module '@/utils/api'"
**Solución:** Verifica que tsconfig.json tenga configurado el alias `@`:
```json
{
  "compilerOptions": {
    "paths": {
      "@/*": ["./src/*"]
    }
  }
}
```

### Error: "401 Unauthorized"
**Solución:** El token expiró. El interceptor redirige automáticamente a `/login`.

### Logo no se muestra
**Solución:** Verifica que el backend esté sirviendo archivos estáticos correctamente.

## 📚 Referencias

- [React Query Documentation](https://tanstack.com/query/latest)
- [Axios Documentation](https://axios-http.com/)
- [SOLID Principles](https://en.wikipedia.org/wiki/SOLID)
- [Clean Code](https://www.amazon.com/Clean-Code-Handbook-Software-Craftsmanship/dp/0132350882)

---

**Autor:** Acadify Team  
**Versión:** 1.0.0  
**Última actualización:** 31 de octubre de 2025
