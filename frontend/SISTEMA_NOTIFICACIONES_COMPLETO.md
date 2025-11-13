# 📬 Sistema de Notificaciones - Documentación Completa

## 🎯 Descripción General

Sistema completo de notificaciones en tiempo real con múltiples vistas, filtros avanzados, estadísticas detalladas y configuración personalizable. Incluye panel de control, widgets, notificaciones push del navegador y más.

---

## 📋 Tabla de Contenidos

1. [Características Principales](#características-principales)
2. [Arquitectura del Sistema](#arquitectura-del-sistema)
3. [Componentes](#componentes)
4. [Páginas](#páginas)
5. [Hooks Personalizados](#hooks-personalizados)
6. [Servicios API](#servicios-api)
7. [Guía de Uso](#guía-de-uso)
8. [Configuración](#configuración)
9. [Tipos de Notificaciones](#tipos-de-notificaciones)

---

## ✨ Características Principales

### 🔔 Notificaciones en Tiempo Real
- **Auto-refresh**: Actualización automática cada 10-30 segundos
- **Detección en tiempo real**: Hook `useNotificacionesRealtime` para detectar nuevas notificaciones
- **Contador de no leídas**: Badge animado en el navbar
- **Sonido opcional**: Reproducción de sonido al recibir notificaciones

### 📊 Panel de Control Completo
- **Dashboard unificado**: Vista general con métricas y accesos rápidos
- **Estadísticas detalladas**: Gráficos de actividad, tasas de lectura, tipos más frecuentes
- **Widgets reutilizables**: Componentes modulares para dashboards
- **Vista de resumen**: Últimas notificaciones y métricas clave

### 🔍 Filtros Avanzados
- **13 tipos de notificación**: Todos los tipos soportados por el backend
- **Rango de fechas**: Filtrar por período específico
- **Estados**: Solo no leídas, solo importantes
- **Ordenamiento**: Por fecha de creación o lectura, ascendente/descendente
- **Búsqueda**: Buscar en títulos y mensajes

### ⚙️ Configuración Personalizable
- **Preferencias por tipo**: Activar/desactivar cada tipo de notificación
- **Canales de notificación**: In-app, email, push del navegador
- **Horario de no molestar**: Configurar horas sin notificaciones
- **Frecuencia de resumen**: Configurar envío de resúmenes por email
- **Sonidos**: Activar/desactivar efectos de sonido

### 🎨 UI/UX de Calidad
- **Diseño moderno**: UI limpia con Tailwind CSS
- **Dark mode**: Soporte completo para modo oscuro
- **Animaciones fluidas**: Framer Motion para transiciones suaves
- **Responsive**: Optimizado para móvil, tablet y desktop
- **Accesibilidad**: Iconos descriptivos y navegación por teclado

---

## 🏗️ Arquitectura del Sistema

```
frontend/src/
├── services/
│   └── notificaciones.service.ts        # Cliente API y utilidades
├── hooks/
│   ├── useNotificaciones.ts             # 9 hooks personalizados
│   └── useNotificacionesRealtime.ts     # Detección en tiempo real
├── components/notificaciones/
│   ├── NotificacionBadge.tsx            # Badge con contador (Navbar)
│   ├── CentroNotificaciones.tsx         # Dropdown con últimas 20
│   ├── NotificacionesWidget.tsx         # Widget para dashboards (5 recientes)
│   ├── EstadisticasNotificaciones.tsx   # Panel de estadísticas
│   ├── FiltrosAvanzadosModal.tsx        # Modal de filtros avanzados
│   └── index.ts                         # Exportaciones
└── pages/
    ├── PanelNotificacionesPage.tsx      # Panel de control principal ⭐ NUEVO
    ├── configuracion/
    │   ├── NotificacionesPage.tsx       # Vista completa con filtros
    │   └── ConfiguracionNotificacionesPage.tsx  # Configuración
```

### Flujo de Datos

```
Backend API
    ↓
notificaciones.service.ts (Axios client)
    ↓
useNotificaciones.ts (React Query hooks)
    ↓
Components & Pages (UI)
```

---

## 🧩 Componentes

### 1. NotificacionBadge
**Ubicación**: `components/notificaciones/NotificacionBadge.tsx`

Badge con contador de notificaciones no leídas para el navbar.

**Props**:
```typescript
interface NotificacionBadgeProps {
  className?: string;
}
```

**Características**:
- Icono de campana con gradiente violeta
- Contador animado (número o "9+" si hay más de 9)
- Animación de "ring" al recibir nuevas notificaciones
- Actualización automática cada 30s
- Click abre el dropdown `CentroNotificaciones`

**Uso**:
```tsx
import { NotificacionBadge } from '@/components/notificaciones';

<NotificacionBadge />
```

---

### 2. CentroNotificaciones
**Ubicación**: `components/notificaciones/CentroNotificaciones.tsx`

Dropdown panel que muestra las últimas 20 notificaciones.

**Props**:
```typescript
interface CentroNotificacionesProps {
  isOpen: boolean;
  onClose: () => void;
  onClickOutside: () => void;
}
```

**Características**:
- Lista de últimas 20 notificaciones
- Cada notificación: icono, título, mensaje, tiempo relativo
- Indicador visual de no leída (fondo violeta suave)
- Click en notificación: marca como leída + navega a URL
- Botón "Marcar todas como leídas"
- Link a página completa
- Loading states
- Empty state

**Uso**:
```tsx
import { CentroNotificaciones } from '@/components/notificaciones';

const [isOpen, setIsOpen] = useState(false);

<CentroNotificaciones
  isOpen={isOpen}
  onClose={() => setIsOpen(false)}
  onClickOutside={() => setIsOpen(false)}
/>
```

---

### 3. NotificacionesWidget ⭐ NUEVO
**Ubicación**: `components/notificaciones/NotificacionesWidget.tsx`

Widget compacto para mostrar en dashboards.

**Características**:
- Muestra últimas 5 notificaciones
- Contador de no leídas en el header
- Diseño compacto tipo card
- Click en notificación navega a URL
- Link "Ver todas" a página completa
- Loading y empty states

**Uso**:
```tsx
import { NotificacionesWidget } from '@/components/notificaciones';

// En tu dashboard:
<div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
  <NotificacionesWidget />
  {/* Otros widgets */}
</div>
```

---

### 4. EstadisticasNotificaciones ⭐ NUEVO
**Ubicación**: `components/notificaciones/EstadisticasNotificaciones.tsx`

Panel de estadísticas con métricas detalladas.

**Características**:
- **4 Cards de métricas**:
  - Total de notificaciones
  - Sin leer (con porcentaje)
  - Leídas (con porcentaje)
  - Tasa de respuesta rápida (leídas en <1 hora)
- **Top 3 tipos más frecuentes**: Con barras de progreso animadas
- **Actividad de hoy**: Contador de notificaciones recibidas hoy
- Cálculos en tiempo real
- Animaciones suaves

**Uso**:
```tsx
import { EstadisticasNotificaciones } from '@/components/notificaciones';

<EstadisticasNotificaciones />
```

---

### 5. FiltrosAvanzadosModal ⭐ NUEVO
**Ubicación**: `components/notificaciones/FiltrosAvanzadosModal.tsx`

Modal full-screen con filtros avanzados.

**Props**:
```typescript
interface FiltrosAvanzadosModalProps {
  isOpen: boolean;
  onClose: () => void;
  onAplicar: (filtros: FiltrosAvanzados) => void;
  filtrosActuales: FiltrosAvanzados;
}

interface FiltrosAvanzados {
  tipos: TipoNotificacion[];
  fechaDesde?: string;
  fechaHasta?: string;
  soloNoLeidas: boolean;
  soloImportantes: boolean;
  ordenarPor: 'fecha_creacion' | 'fecha_lectura';
  ordenDesc: boolean;
}
```

**Características**:
- Grid de 13 tipos de notificación con emojis
- Botones "Seleccionar todas" y "Limpiar"
- Date pickers para rango de fechas
- Toggles para "Solo no leídas" y "Solo importantes"
- Radio buttons para ordenamiento
- Toggle para orden descendente
- Botones: Reset, Cancelar, Aplicar
- Validación y estado local
- Animaciones de entrada/salida

**Uso**:
```tsx
import FiltrosAvanzadosModal, { type FiltrosAvanzados } from '@/components/notificaciones/FiltrosAvanzadosModal';

const [filtros, setFiltros] = useState<FiltrosAvanzados>({
  tipos: [],
  soloNoLeidas: false,
  soloImportantes: false,
  ordenarPor: 'fecha_creacion',
  ordenDesc: true
});
const [modalOpen, setModalOpen] = useState(false);

<FiltrosAvanzadosModal
  isOpen={modalOpen}
  onClose={() => setModalOpen(false)}
  onAplicar={(nuevosFiltros) => {
    setFiltros(nuevosFiltros);
    // Aplicar filtros...
  }}
  filtrosActuales={filtros}
/>
```

---

## 📄 Páginas

### 1. PanelNotificacionesPage ⭐ NUEVO (Página Principal)
**Ubicación**: `pages/PanelNotificacionesPage.tsx`
**Ruta**: `/panel-notificaciones`

Dashboard completo de notificaciones con vista de resumen y estadísticas.

**Características**:
- **Header**: Título, contador de no leídas, botones de configuración y ver todas
- **Tabs**: Resumen | Estadísticas
- **Vista Resumen**:
  - 3 cards de métricas rápidas (Sin leer, Hoy, Esta semana)
  - Widget de notificaciones recientes
  - Sidebar con accesos rápidos (No leídas, Importantes, Tareas, Mensajes)
  - Card con tip y link a configuración
- **Vista Estadísticas**:
  - Componente `EstadisticasNotificaciones`
  - Métricas detalladas y gráficos
- Animaciones entre tabs con AnimatePresence
- Responsive design (3 columnas en desktop, 1 en móvil)

**Uso recomendado**: Página principal del sistema de notificaciones.

---

### 2. NotificacionesPage
**Ubicación**: `pages/configuracion/NotificacionesPage.tsx`
**Ruta**: `/notificaciones`

Vista completa de todas las notificaciones con filtros y búsqueda.

**Características**:
- **Header**: Título, contador no leídas, botón "Marcar todas como leídas"
- **Sidebar de filtros**:
  - Estado: Todas | Sin leer
  - Tipo: Todos | Mensajes | Tareas | Logros | Clases | Sistema
  - Botón de "Filtros Avanzados" ⭐ NUEVO
- **Lista de notificaciones**:
  - Barra de búsqueda
  - Lista paginada (20 por página)
  - Cada notificación: icono, título, mensaje, tiempo
  - Click para marcar como leída y navegar
  - Indicador visual de no leída
- **Paginación**: Anterior | Página X | Siguiente
- **Modal de filtros avanzados** ⭐ NUEVO

---

### 3. ConfiguracionNotificacionesPage
**Ubicación**: `pages/configuracion/ConfiguracionNotificacionesPage.tsx`
**Ruta**: `/configuracion/notificaciones`

Configuración completa de preferencias de notificaciones.

**Características**:
- **Secciones**:
  1. **Tipos de Notificación**: Activar/desactivar cada tipo (13 tipos)
  2. **Canales**: In-app, Email, Push del navegador
  3. **Horario de No Molestar**: Hora inicio y fin
  4. **Frecuencia de Resúmenes**: Diario, Semanal, Mensual, Nunca
  5. **Preferencias Adicionales**: Sonido, agrupación, resumen automático
- Formulario con validación
- Botones: Guardar cambios, Restaurar valores por defecto
- Loading states
- Toasts de confirmación
- Test de notificación push del navegador
- Sincronización con backend

---

## 🪝 Hooks Personalizados

Ubicación: `hooks/useNotificaciones.ts`

### 1. useNotificaciones
Obtiene lista de notificaciones con filtros.

```typescript
const { data, isLoading, error } = useNotificaciones({
  tipo_notificacion?: TipoNotificacion;
  solo_no_leidas?: boolean;
  limite?: number;
  offset?: number;
});
```

**Características**:
- React Query con cache
- Auto-refetch cada 30s
- Manejo de errores

---

### 2. useContadorNoLeidas
Obtiene el contador de notificaciones no leídas.

```typescript
const { data: contador } = useContadorNoLeidas();
// contador: number
```

**Características**:
- Auto-refetch cada 10s (más frecuente)
- Usado en el badge del navbar

---

### 3. useNotificacion
Obtiene una notificación específica por ID.

```typescript
const { data: notificacion } = useNotificacion(id);
```

---

### 4. useCrearNotificacion
Crea una notificación nueva.

```typescript
const { mutate: crear, isPending } = useCrearNotificacion();

crear({
  usuario_id: '123',
  tipo_notificacion: 'mensaje_directo',
  titulo: 'Nuevo mensaje',
  mensaje: 'Tienes un mensaje nuevo',
  url_accion: '/mensajes/456'
});
```

---

### 5. useMarcarComoLeidas
Marca notificaciones como leídas.

```typescript
const { mutate: marcarLeidas } = useMarcarComoLeidas();

marcarLeidas(['id1', 'id2', 'id3']);
```

---

### 6. useMarcarTodasLeidas
Marca todas las notificaciones como leídas.

```typescript
const { mutate: marcarTodas } = useMarcarTodasLeidas();

marcarTodas(undefined);
```

---

### 7. useEliminarNotificacion
Elimina una notificación.

```typescript
const { mutate: eliminar } = useEliminarNotificacion();

eliminar('notif-id');
```

---

### 8. useConfiguracionNotificaciones
Obtiene la configuración de notificaciones del usuario.

```typescript
const { data: config } = useConfiguracionNotificaciones();
```

---

### 9. useActualizarConfiguracion
Actualiza la configuración de notificaciones.

```typescript
const { mutate: actualizar } = useActualizarConfiguracion();

actualizar({
  recibir_notificaciones_in_app: true,
  recibir_notificaciones_email: false,
  recibir_notificaciones_push: true,
  frecuencia_resumen: 'semanal',
  // ... más opciones
});
```

---

### 10. useNotificacionesRealtime
Hook para detección en tiempo real de nuevas notificaciones.

Ubicación: `hooks/useNotificacionesRealtime.ts`

```typescript
const { hayNuevas, ultimoContador } = useNotificacionesRealtime({
  habilitado: true,
  intervalo: 10000, // 10 segundos
  onNuevasNotificaciones: (cantidad) => {
    console.log(`${cantidad} notificaciones nuevas`);
    // Reproducir sonido, mostrar toast, etc.
  }
});
```

**Características**:
- Polling inteligente
- Callback cuando hay nuevas
- Control de habilitación

---

## 🔌 Servicios API

Ubicación: `services/notificaciones.service.ts`

### Cliente API

```typescript
// Obtener notificaciones
notificacionesApi.obtenerNotificaciones(filtros);

// Contador no leídas
notificacionesApi.contadorNoLeidas();

// Marcar como leída
notificacionesApi.marcarComoLeida(id);

// Marcar varias
notificacionesApi.marcarComoLeidas(ids);

// Marcar todas
notificacionesApi.marcarTodasLeidas();

// Obtener configuración
notificacionesApi.obtenerConfiguracion();

// Actualizar configuración
notificacionesApi.actualizarConfiguracion(config);
```

### Interfaces

```typescript
interface Notificacion {
  id: string;
  usuario_id: string;
  tipo_notificacion: TipoNotificacion;
  titulo: string;
  mensaje?: string;
  leida: boolean;
  importante: boolean;
  url_accion?: string;
  metadatos?: Record<string, any>;
  fecha_creacion: string;
  fecha_lectura?: string;
}

type TipoNotificacion =
  | 'mensaje_directo'
  | 'tarea_nueva'
  | 'tarea_vencimiento'
  | 'evaluacion_disponible'
  | 'evaluacion_calificada'
  | 'clase_cancelada'
  | 'clase_recordatorio'
  | 'logro_desbloqueado'
  | 'insignia_obtenida'
  | 'subida_nivel'
  | 'comentario'
  | 'mencion'
  | 'sistema';
```

### Utilidades

```typescript
// Obtener icono para tipo de notificación
const Icon = obtenerIconoNotificacion(tipo);

// Obtener color (Tailwind class)
const color = obtenerColorNotificacion(tipo);

// Obtener título legible
const titulo = obtenerTituloTipo(tipo);

// Formatear tiempo relativo
const tiempo = formatearTiempoRelativo(fecha);
// Ejemplos: "Hace 5 minutos", "Hace 2 horas", "Hace 3 días"
```

---

## 📖 Guía de Uso

### Integración en tu aplicación

#### 1. Agregar el badge al Navbar

```tsx
// components/layout/Nav.tsx
import { NotificacionBadge } from '@/components/notificaciones';

export default function Nav() {
  return (
    <nav>
      {/* ... otros elementos ... */}
      <NotificacionBadge />
    </nav>
  );
}
```

#### 2. Agregar widget al Dashboard

```tsx
// pages/dashboard/DashboardStudent.tsx
import { NotificacionesWidget } from '@/components/notificaciones';

export default function DashboardStudent() {
  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <NotificacionesWidget />
      {/* Otros widgets */}
    </div>
  );
}
```

#### 3. Configurar rutas

```tsx
// App.tsx
const PanelNotificacionesPage = lazy(() => import('./pages/PanelNotificacionesPage'));
const NotificacionesPage = lazy(() => import('./pages/configuracion/NotificacionesPage'));
const ConfiguracionNotificacionesPage = lazy(() => import('./pages/configuracion/ConfiguracionNotificacionesPage'));

// En tus rutas:
<Route path="/panel-notificaciones" element={<PanelNotificacionesPage />} />
<Route path="/notificaciones" element={<NotificacionesPage />} />
<Route path="/configuracion/notificaciones" element={<ConfiguracionNotificacionesPage />} />
```

#### 4. Uso básico de hooks

```tsx
import { useNotificaciones, useMarcarComoLeidas } from '@/hooks/useNotificaciones';

function MiComponente() {
  const { data: notificaciones = [], isLoading } = useNotificaciones({
    solo_no_leidas: true,
    limite: 10
  });
  
  const { mutate: marcarLeida } = useMarcarComoLeidas();
  
  const handleClick = (id: string) => {
    marcarLeida([id]);
  };
  
  if (isLoading) return <div>Cargando...</div>;
  
  return (
    <div>
      {notificaciones.map(n => (
        <div key={n.id} onClick={() => handleClick(n.id)}>
          {n.titulo}
        </div>
      ))}
    </div>
  );
}
```

---

## ⚙️ Configuración

### Variables de Entorno

```env
# Backend API URL
VITE_API_URL=http://localhost:8000/api
```

### Configuración de React Query

```tsx
// main.tsx
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000, // 5 minutos
      refetchInterval: 30000, // 30 segundos
    },
  },
});
```

### Configuración de Notificaciones Push

Para habilitar notificaciones push del navegador:

1. Usuario debe dar permiso en `/configuracion/notificaciones`
2. Hacer clic en "Probar notificación"
3. El navegador pedirá permiso
4. Una vez otorgado, las notificaciones se mostrarán automáticamente

---

## 🔔 Tipos de Notificaciones

| Tipo | Emoji | Descripción | Color |
|------|-------|-------------|-------|
| `mensaje_directo` | 💬 | Mensaje directo de otro usuario | Violeta |
| `tarea_nueva` | 📝 | Nueva tarea asignada | Azul |
| `tarea_vencimiento` | ⏰ | Tarea próxima a vencer | Naranja |
| `evaluacion_disponible` | 📋 | Evaluación disponible | Cyan |
| `evaluacion_calificada` | ✅ | Evaluación calificada | Verde |
| `clase_cancelada` | ❌ | Clase cancelada | Rojo |
| `clase_recordatorio` | 📅 | Recordatorio de clase | Azul |
| `logro_desbloqueado` | 🏆 | Nuevo logro desbloqueado | Amarillo |
| `insignia_obtenida` | 🏅 | Nueva insignia obtenida | Dorado |
| `subida_nivel` | ⬆️ | Subiste de nivel | Púrpura |
| `comentario` | 💬 | Comentario en publicación | Violeta |
| `mencion` | @️⃣ | Te mencionaron | Violeta |
| `sistema` | ⚙️ | Notificación del sistema | Gris |

---

## 🎨 Personalización

### Colores

El sistema usa Tailwind CSS con la paleta violeta como color principal:

```css
/* Principales */
--color-primary: violet-600
--color-primary-hover: violet-700
--color-primary-light: violet-100
--color-primary-dark: violet-900

/* Estados */
--color-unread: violet-50
--color-read: gray-50
```

### Iconos

Los iconos provienen de `lucide-react`. Para cambiar un icono:

```tsx
import { Bell, MessageSquare, BookOpen } from 'lucide-react';

// Mapeo en obtenerIconoNotificacion()
const iconos: Record<TipoNotificacion, React.ElementType> = {
  mensaje_directo: MessageSquare,
  tarea_nueva: BookOpen,
  // ...
};
```

### Animaciones

Todas las animaciones usan Framer Motion:

```tsx
<motion.div
  initial={{ opacity: 0, y: 20 }}
  animate={{ opacity: 1, y: 0 }}
  transition={{ duration: 0.3 }}
>
  {/* Contenido */}
</motion.div>
```

---

## 📱 Soporte de Dispositivos

- **Desktop**: Diseño completo con sidebar y múltiples columnas
- **Tablet**: Layout responsive con 2 columnas
- **Móvil**: Stack vertical, menús colapsables, gestos táctiles

---

## 🚀 Rendimiento

### Optimizaciones implementadas:

1. **Lazy loading**: Todas las páginas y componentes pesados se cargan bajo demanda
2. **React Query cache**: Las notificaciones se cachean y reusan
3. **Virtualización**: (Opcional) Para listas grandes, considerar `react-window`
4. **Memoización**: Componentes memorizados con `React.memo`
5. **Debounce en búsqueda**: Evita llamadas excesivas al buscar
6. **Paginación**: Solo se cargan 20 notificaciones a la vez

---

## 🐛 Troubleshooting

### No aparece el contador de no leídas
- Verificar que el backend esté corriendo
- Verificar la URL del API en `.env`
- Revisar errores en la consola del navegador

### Las notificaciones no se actualizan
- Verificar la configuración de refetch en React Query
- Comprobar que el usuario tenga sesión activa
- Revisar los logs del backend

### No funciona el modal de filtros
- Verificar que `AnimatePresence` esté importado
- Comprobar que `isOpen` y `onClose` se pasen correctamente

---

## 📚 Recursos Adicionales

- [React Query Docs](https://tanstack.com/query/latest/docs/react/overview)
- [Framer Motion Docs](https://www.framer.com/motion/)
- [Tailwind CSS Docs](https://tailwindcss.com/docs)
- [Lucide React Icons](https://lucide.dev/icons/)

---

## 👥 Créditos

Sistema desarrollado para **Acadify** - Plataforma educativa completa.

---

## 📄 Licencia

Propietario - Todos los derechos reservados.
