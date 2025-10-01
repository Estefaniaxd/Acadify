# Sistema de Tareas y Asignaciones - Frontend

Este módulo implementa la interfaz de usuario completa para el sistema de tareas y asignaciones de la plataforma Acadify.

## 📁 Estructura del Módulo

```
/src/modules/tareas/
├── types.ts                    # Definiciones de tipos TypeScript
├── api.ts                     # Cliente API para comunicación con el backend
├── components/
│   ├── ListaTareas.tsx        # Lista de tareas con filtros
│   ├── FormularioTarea.tsx    # Formulario crear/editar tareas
│   ├── DetalleTarea.tsx       # Vista detallada de una tarea
│   └── index.ts               # Exportaciones de componentes
├── index.ts                   # Exportaciones principales del módulo
└── README.md                  # Esta documentación
```

## 🚀 Uso Básico

### Componente Principal
```tsx
import { SistemaTareas } from '../components/SistemaTareas';

// En tu componente React
<SistemaTareas
  grupoId="grupo-123"
  docenteId="docente-456" 
  esDocente={true}
  estudianteId="estudiante-789" // Opcional, solo si es estudiante
/>
```

### Componentes Individuales
```tsx
import { ListaTareas, FormularioTarea, DetalleTarea, TareasApi } from '../modules/tareas';

// Lista de tareas
<ListaTareas
  grupoId="grupo-123"
  onTareaSeleccionada={(tarea) => console.log('Tarea seleccionada:', tarea)}
  onCrearTarea={() => console.log('Crear nueva tarea')}
  filtrosIniciales={{
    solo_activas: true,
    ordenar_por: 'fecha_limite'
  }}
/>

// Formulario de tarea
<FormularioTarea
  onSubmit={async (dataTarea) => {
    const api = new TareasApi();
    await api.crearTarea(dataTarea);
  }}
  onCancel={() => console.log('Cancelar')}
  grupoId="grupo-123"
  docenteId="docente-456"
  tareaInicial={null} // Para crear nueva | tarea existente para editar
/>

// Detalle de tarea
<DetalleTarea
  tarea={tareaSeleccionada}
  onClose={() => console.log('Cerrar detalle')}
  onEdit={(tarea) => console.log('Editar tarea:', tarea)}
  onDelete={(tareaId) => console.log('Eliminar tarea:', tareaId)}
  esDocente={true}
  estudianteId="estudiante-789"
/>
```

## 📊 Características Principales

### 🎯 ListaTareas
- ✅ Visualización de tareas en formato de lista
- ✅ Filtros avanzados (estado, tipo, prioridad, fechas)
- ✅ Búsqueda en tiempo real
- ✅ Ordenamiento configurable
- ✅ Indicadores visuales de estado y prioridad
- ✅ Responsive design
- ✅ Auto-actualización cada 30 segundos

### 📝 FormularioTarea
- ✅ Formulario wizard de 4 pasos
- ✅ Validación en tiempo real
- ✅ Soporte para crear y editar tareas
- ✅ Configuración avanzada (entregas tardías, intentos, archivos)
- ✅ Vista previa antes de guardar
- ✅ Campos obligatorios y opcionales bien definidos

### 🔍 DetalleTarea
- ✅ Vista completa de información de tarea
- ✅ Progreso de entregas (solo docentes)
- ✅ Lista de entregas recientes
- ✅ Acciones contextuales (editar, eliminar)
- ✅ Información de fechas y configuración
- ✅ Recursos y criterios de evaluación

## 🏗️ Tipos de Datos

### Enums Principales
```typescript
enum EstadoTarea {
  BORRADOR = 'borrador',
  PUBLICADA = 'publicada', 
  EN_PROGRESO = 'en_progreso',
  VENCIDA = 'vencida',
  CERRADA = 'cerrada',
  ARCHIVADA = 'archivada'
}

enum TipoTarea {
  ENSAYO = 'ensayo',
  PROYECTO = 'proyecto',
  EJERCICIOS = 'ejercicios',
  INVESTIGACION = 'investigacion',
  PRESENTACION = 'presentacion',
  LABORATORIO = 'laboratorio',
  LECTURA = 'lectura',
  EXAMEN = 'examen',
  OTRO = 'otro'
}

enum PrioridadTarea {
  BAJA = 'baja',
  MEDIA = 'media', 
  ALTA = 'alta',
  URGENTE = 'urgente'
}

enum EstadoEntrega {
  BORRADOR = 'borrador',
  ENVIADA = 'enviada',
  EN_REVISION = 'en_revision',
  CALIFICADA = 'calificada',
  DEVUELTA = 'devuelta',
  RECHAZADA = 'rechazada'
}
```

### Interfaces Principales
```typescript
interface Tarea {
  id?: string;
  titulo: string;
  descripcion?: string;
  instrucciones?: string;
  objetivos?: string;
  tipo_tarea: TipoTarea;
  prioridad: PrioridadTarea;
  estado: EstadoTarea;
  fecha_limite: string;
  puntuacion_maxima: number;
  // ... más campos
}

interface EntregaTarea {
  id?: string;
  tarea_id: string;
  estudiante_id: string;
  estudiante_nombre?: string;
  estado: EstadoEntrega;
  fecha_entrega: string;
  calificacion?: number;
  // ... más campos
}
```

## 🔌 API Client

### Métodos Disponibles
```typescript
const tareasApi = new TareasApi();

// Tareas
await tareasApi.crearTarea(dataTarea);
await tareasApi.obtenerTarea(tareaId);
await tareasApi.obtenerTareasGrupo(grupoId, filtros);
await tareasApi.actualizarTarea(tareaId, dataTarea);
await tareasApi.eliminarTarea(tareaId);

// Entregas  
await tareasApi.entregarTarea(entregaData);
await tareasApi.obtenerEntregasTarea(tareaId, filtros);
await tareasApi.calificarEntrega(entregaId, calificacion);
await tareasApi.obtenerMisEntregas(estudianteId, filtros);

// Rúbricas
await tareasApi.crearRubrica(rubricaData);
await tareasApi.obtenerRubricas(filtros);
```

## ⚙️ Configuración

### Variables de Entorno
```bash
# .env
REACT_APP_API_URL=http://localhost:8000/api
```

### Dependencias Requeridas
```json
{
  "dependencies": {
    "react": "^18.0.0",
    "axios": "^1.0.0"
  },
  "devDependencies": {
    "@types/node": "^20.0.0"
  }
}
```

## 🎨 Estilos y UX

### Principios de Diseño
- **Responsive**: Adaptable a móviles, tablets y desktop
- **Accesible**: Cumple estándares WCAG
- **Consistente**: Usa sistema de diseño unificado
- **Intuitivo**: Flujos de usuario claros y simples

### Colores de Estado
```css
/* Estados de Tarea */
.estado-borrador { @apply bg-gray-100 text-gray-800; }
.estado-publicada { @apply bg-blue-100 text-blue-800; }
.estado-en-progreso { @apply bg-yellow-100 text-yellow-800; }
.estado-vencida { @apply bg-red-100 text-red-800; }
.estado-cerrada { @apply bg-gray-100 text-gray-800; }

/* Estados de Entrega */
.entrega-enviada { @apply bg-blue-100 text-blue-800; }
.entrega-calificada { @apply bg-green-100 text-green-800; }
.entrega-devuelta { @apply bg-orange-100 text-orange-800; }
```

## 🧪 Testing

### Comandos de Prueba
```bash
# Instalar dependencias
npm install

# Compilar TypeScript  
npm run build

# Ejecutar en desarrollo
npm run dev

# Verificar tipos
npm run type-check
```

### Casos de Prueba
- ✅ Crear tarea con validación
- ✅ Editar tarea existente
- ✅ Filtrar y buscar tareas
- ✅ Ver detalle de tarea
- ✅ Eliminar tarea (con confirmación)
- ✅ Manejar estados de carga y error

## 🔄 Integración con Backend

### Endpoints Utilizados
```
POST   /api/tareas              # Crear tarea
GET    /api/tareas/{id}         # Obtener tarea
GET    /api/tareas/grupo/{id}   # Obtener tareas de grupo  
PUT    /api/tareas/{id}         # Actualizar tarea
DELETE /api/tareas/{id}         # Eliminar tarea

POST   /api/entregas            # Entregar tarea
GET    /api/entregas/tarea/{id} # Obtener entregas de tarea
PUT    /api/entregas/{id}/calificar # Calificar entrega
```

### Autenticación
Todos los requests incluyen automáticamente:
```typescript
headers: {
  'Authorization': `Bearer ${token}`,
  'Content-Type': 'application/json'
}
```

## 🚀 Próximas Funcionalidades

### En Desarrollo
- [ ] Componente para estudiantes (EntregaTarea)  
- [ ] Sistema de notificaciones push
- [ ] Comentarios en entregas
- [ ] Historial de versiones
- [ ] Integración con calendario

### Futuras Versiones
- [ ] Plantillas de tareas
- [ ] Tareas colaborativas avanzadas
- [ ] Integración con IA para feedback
- [ ] Analytics y reportes
- [ ] Exportación a PDF

## 📞 Soporte

Para problemas o dudas sobre este módulo:
1. Revisa la documentación del backend en `/backend/README.md`
2. Verifica que todos los endpoints estén funcionando  
3. Comprueba las variables de entorno
4. Consulta los logs del navegador para errores JavaScript

## 🔄 Changelog

### v1.0.0 (Actual)
- ✅ Implementación completa del sistema básico
- ✅ Componentes React funcionales
- ✅ Integración con API backend
- ✅ Validaciones y manejo de errores
- ✅ Responsive design
- ✅ TypeScript completo