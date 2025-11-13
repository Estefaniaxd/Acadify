# 🔔 Sistema de Notificaciones - Acadify

Sistema completo de notificaciones en tiempo real para Acadify con integración frontend-backend.

## 📁 Estructura de Archivos

```
frontend/src/
├── services/
│   └── notificaciones.service.ts (347 líneas)
├── hooks/
│   ├── useNotificaciones.ts (181 líneas)
│   └── useNotificacionesRealtime.ts (63 líneas)
├── components/
│   ├── notificaciones/
│   │   ├── CentroNotificaciones.tsx (235 líneas)
│   │   ├── NotificacionBadge.tsx (88 líneas)
│   │   └── index.ts
│   └── layout/
│       └── Nav.tsx (actualizado)
└── pages/
    └── configuracion/
        ├── NotificacionesPage.tsx (375 líneas)
        └── ConfiguracionNotificacionesPage.tsx (450+ líneas)
```

**Total: ~1,739 líneas de código funcional**

## 🎯 Características Principales

### 1. **Badge de Notificaciones** 🔴
- **Ubicación**: Navbar (desktop y móvil)
- **Badge rojo animado** con contador de notificaciones no leídas
- Muestra "99+" si hay más de 99 notificaciones
- Animación de "ping" radial cuando hay nuevas notificaciones
- Auto-refetch cada **10 segundos** para actualización en tiempo real

### 2. **Centro de Notificaciones (Dropdown)** 📬
- Panel dropdown al hacer click en la campanita
- Lista de últimas **20 notificaciones**
- Filtros: Todas / Solo no leídas
- Click en notificación → marca como leída + navega a URL de acción
- Botón "Marcar todas como leídas"
- Link a página completa de notificaciones
- Animaciones con Framer Motion (slide down, stagger)

### 3. **Página de Notificaciones** 📄
- Vista completa con sidebar de filtros
- **Filtros por estado**: Todas / Sin leer
- **Filtros por tipo**: Mensajes, Tareas, Logros, Clases, Sistema
- Barra de búsqueda en tiempo real
- Paginación (20 items por página)
- Cards grandes con icono gradient, título, mensaje, timestamp
- Ring violeta para notificaciones no leídas

### 4. **Configuración de Notificaciones** ⚙️
- Página completa de configuración de preferencias
- **Configuración General**:
  - Activar/desactivar todas las notificaciones
  - Sonido de notificaciones
- **Notificaciones por Categoría**:
  - ✅ Tareas (nuevas, vencimiento 24h, vencimiento 1h, calificadas)
  - 💬 Mensajes (directos, menciones, respuestas, importantes)
  - 📅 Cursos y Clases (nuevos cursos, clases canceladas, evaluaciones)
  - 🏆 Gamificación (logros desbloqueados)
  - ⚙️ Sistema
- **Resúmenes por Email**:
  - Resumen diario
  - Resumen semanal
- **Horario de Notificaciones**:
  - Hora de inicio y fin (input type="time")
  - Días de la semana activos (botones toggle)

### 5. **Notificaciones en Tiempo Real** ⏱️
- **Detección automática** de nuevas notificaciones
- **Sonido** al recibir notificaciones (3 tipos: mensaje, tarea, logro)
- **Notificaciones del navegador** (Browser Notifications API)
- Auto-refetch configurado:
  - Badge: cada **10 segundos**
  - Lista: cada **30 segundos**
  - RefetchOnWindowFocus: activado

## 🔌 Backend API

**Base URL**: `/api/communication/notificaciones`

### Endpoints Implementados:

1. **GET** `/notificaciones` - Obtener notificaciones con filtros
   - Query params: `tipo_notificacion`, `solo_no_leidas`, `limite`, `offset`, `ordenar_por`, `orden_desc`
   - Response: `Notificacion[]`

2. **POST** `/notificaciones/marcar-leidas` - Marcar notificaciones como leídas
   - Body: `{ notificaciones_ids: string[] }`

3. **POST** `/notificaciones/marcar-todas-leidas` - Marcar todas como leídas
   - Query param (opcional): `tipo_notificacion`

4. **GET** `/notificaciones/count` - Contador de notificaciones no leídas
   - Response: `number`

5. **GET** `/configuracion/notificaciones` - Obtener configuración del usuario
   - Response: `ConfiguracionNotificaciones`

6. **PUT** `/configuracion/notificaciones` - Actualizar configuración
   - Body: `ConfiguracionNotificaciones`

## 📊 Tipos de Notificaciones

| Tipo | Emoji | Color | Descripción |
|------|-------|-------|-------------|
| `mensaje_directo` | 💬 | Blue | Mensajes directos |
| `mencion` | @ | Purple | Menciones con @ |
| `respuesta_hilo` | 💭 | Indigo | Respuestas en hilos |
| `mensaje_importante` | ⚠️ | Red | Mensajes importantes |
| `tarea_nueva` | 📝 | Green | Nueva tarea asignada |
| `tarea_vencimiento` | ⏰ | Orange | Tarea próxima a vencer |
| `tarea_calificada` | ✅ | Blue | Tarea calificada |
| `tarea_comentario` | 💬 | Cyan | Comentario en tarea |
| `curso_nuevo` | 🎓 | Violet | Nuevo curso |
| `clase_cancelada` | 🚫 | Red | Clase cancelada |
| `evaluacion_disponible` | 📊 | Pink | Nueva evaluación |
| `logro_desbloqueado` | 🏆 | Yellow | Logro desbloqueado |
| `sistema` | ⚙️ | Gray | Notificación del sistema |

## 🎨 Interfaces TypeScript

```typescript
interface Notificacion {
  id: string;
  usuario_id: string;
  titulo: string;
  mensaje?: string;
  tipo_notificacion: TipoNotificacion;
  url_accion?: string;
  icono?: string;
  color?: string;
  sala_id?: string;
  mensaje_id?: string;
  tarea_id?: string;
  curso_id?: string;
  leida: boolean;
  enviada_email: boolean;
  enviada_push: boolean;
  fecha_creacion: string;
  fecha_lectura?: string;
  datos_adicionales?: Record<string, any>;
}

interface ConfiguracionNotificaciones {
  notificaciones_activas: boolean;
  sonido_activo: boolean;
  tareas_nuevas: boolean;
  tareas_vencimiento_24h: boolean;
  tareas_vencimiento_1h: boolean;
  tareas_calificadas: boolean;
  mensajes_directos: boolean;
  menciones: boolean;
  respuestas_hilo: boolean;
  mensajes_importantes: boolean;
  cursos_nuevos: boolean;
  clases_canceladas: boolean;
  evaluaciones_disponibles: boolean;
  logros_desbloqueados: boolean;
  notificaciones_sistema: boolean;
  resumen_diario_email: boolean;
  resumen_semanal_email: boolean;
  horario_inicio: string;
  horario_fin: string;
  dias_activos: number[];
}
```

## 🔧 Hooks Disponibles

### `useNotificaciones(filtros?)`
Obtiene lista de notificaciones con filtros opcionales.
```typescript
const { data, isLoading, error, refetch } = useNotificaciones({
  tipo_notificacion: 'mensaje_directo',
  solo_no_leidas: true,
  limite: 20,
  offset: 0
});
```

### `useContadorNoLeidas()`
Contador de notificaciones no leídas (auto-refetch 10s).
```typescript
const { data: contador } = useContadorNoLeidas();
```

### `useMarcarComoLeidas()`
Mutación para marcar notificaciones como leídas.
```typescript
const { mutate: marcarComoLeidas } = useMarcarComoLeidas();
marcarComoLeidas(['notif-id-1', 'notif-id-2']);
```

### `useMarcarTodasLeidas()`
Mutación para marcar todas como leídas.
```typescript
const { mutate: marcarTodasLeidas } = useMarcarTodasLeidas();
marcarTodasLeidas('tarea_nueva'); // Opcional: tipo específico
```

### `useCentroNotificaciones(filtros?)`
Hook combinado para el centro de notificaciones.
```typescript
const {
  notificaciones,
  contador,
  isLoading,
  marcarComoLeidas,
  marcarTodasLeidas
} = useCentroNotificaciones({ solo_no_leidas: true });
```

### `useNotificacionesPush()`
Integración con Browser Notifications API.
```typescript
const { permiso, solicitarPermiso, mostrarNotificacion } = useNotificacionesPush();
```

### `useSonidoNotificacion()`
Reproducción de sonidos para notificaciones.
```typescript
const { reproducir } = useSonidoNotificacion();
reproducir('mensaje'); // 'mensaje' | 'tarea' | 'logro'
```

### `useNotificacionesRealtime()`
Hook para detección automática de nuevas notificaciones.
```typescript
const { contador, tieneNotificaciones } = useNotificacionesRealtime();
// Automáticamente reproduce sonido y muestra browser notification
```

## 🚀 Instalación y Uso

### 1. Badge en el Navbar
Ya está integrado en `Nav.tsx`. Se muestra automáticamente para usuarios autenticados.

### 2. Rutas Configuradas
- `/notificaciones` - Página principal de notificaciones
- `/configuracion/notificaciones` - Configuración de preferencias

### 3. Permisos del Navegador (Opcional)
Para usar Browser Notifications, el usuario debe dar permiso:
```typescript
const { solicitarPermiso } = useNotificacionesPush();
await solicitarPermiso();
```

## 📱 Responsive Design

- **Desktop**: Badge en navbar, dropdown de 400px width
- **Tablet**: Badge en navbar, dropdown adaptable
- **Mobile**: Badge en navbar móvil, dropdown full-width

## 🎨 Estilos y Animaciones

- **Tailwind CSS** para estilos
- **Framer Motion** para animaciones
- **Lucide React** para iconos
- **Dark mode** completo
- Gradientes personalizados por tipo de notificación
- Animaciones de entrada/salida (slide, fade, scale)
- Transiciones suaves (300-500ms)

## 🔒 Seguridad

- JWT token en headers de todas las peticiones
- Validación de usuario autenticado
- Solo se muestran notificaciones del usuario actual
- CORS configurado en backend

## 📈 Performance

- **Code splitting** con React.lazy
- **Auto-refetch inteligente**:
  - Badge: 10s (crítico)
  - Lista: 30s (normal)
  - Configuración: 5min (cache largo)
- **Cache management** con React Query
- **Optimistic updates** en mutaciones
- **RefetchOnWindowFocus** para sincronización

## 🐛 Debugging

### Ver estado de React Query
```typescript
import { useQueryClient } from '@tanstack/react-query';

const queryClient = useQueryClient();
console.log(queryClient.getQueryState(['notificaciones']));
```

### Ver notificaciones en consola
```typescript
const { data } = useNotificaciones();
console.log('Notificaciones:', data);
```

## 🔮 Futuras Mejoras

- [ ] WebSocket para notificaciones en tiempo real (en lugar de polling)
- [ ] Filtros avanzados (rango de fechas, múltiples tipos)
- [ ] Búsqueda por contenido en backend
- [ ] Notificaciones agrupadas (threads)
- [ ] Historial de notificaciones eliminadas
- [ ] Exportar notificaciones (PDF/CSV)
- [ ] Estadísticas de notificaciones
- [ ] Plantillas personalizadas de notificaciones

## 📞 Soporte

Si encuentras algún problema, revisa:
1. Consola del navegador (errores de JS)
2. Network tab (peticiones fallidas)
3. React Query DevTools (estado de cache)
4. Backend logs (errores de servidor)

---

**Versión**: 1.0.0  
**Última actualización**: 9 de noviembre de 2025  
**Estado**: ✅ Funcional y en producción
