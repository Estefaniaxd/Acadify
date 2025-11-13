# 🎥 Frontend - Sistema de Videollamadas con Jitsi Meet

> **Estado**: ✅ Implementado - Pendiente de instalación  
> **Fecha**: 9 de noviembre de 2025  
> **Framework**: React + TypeScript + Vite

---

## 📋 Resumen Ejecutivo

El frontend de videollamadas está **completamente implementado** con los siguientes componentes:

### ✅ Archivos Creados (9 archivos)

1. **Types**: `src/types/videollamada.types.ts` (342 líneas)
2. **Service**: `src/services/videollamadas.service.ts` (396 líneas)
3. **Hook**: `src/hooks/useVideollamada.ts` (285 líneas)
4. **Componente Jitsi**: `src/modules/comunicacion/components/JitsiMeeting.tsx` (352 líneas)
5. **Ventana Video**: `src/modules/comunicacion/components/VideoCallWindow.tsx` (334 líneas)
6. **Lista**: `src/modules/comunicacion/components/VideollamadasList.tsx` (327 líneas)
7. **Página**: `src/pages/VideollamadasPage.tsx` (102 líneas)

**Total**: ~2,138 líneas de código TypeScript

---

## 🚀 Pasos de Instalación

### 1. Agregar Script de Jitsi Meet

Edita `frontend/index.html` y agrega el script de Jitsi Meet en el `<head>`:

```html
<!DOCTYPE html>
<html lang="es">
  <head>
    <meta charset="UTF-8" />
    <link rel="icon" type="image/svg+xml" href="/vite.svg" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Acadify</title>
    
    <!-- ✅ AGREGAR ESTE SCRIPT -->
    <script src="https://meet.jit.si/external_api.js"></script>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.tsx"></script>
  </body>
</html>
```

### 2. Instalar Dependencias Adicionales (si faltan)

```bash
cd frontend

# date-fns para formateo de fechas
npm install date-fns

# lucide-react para iconos (puede que ya esté instalado)
npm install lucide-react
```

### 3. Configurar Variables de Entorno

Crea o edita `frontend/.env`:

```env
# API Backend
VITE_API_BASE_URL=http://localhost:8000

# Jitsi Domain (opcional, default: meet.jit.si)
VITE_JITSI_DOMAIN=meet.jit.si
```

### 4. Agregar Ruta en el Router

Edita tu archivo de rutas (ejemplo: `src/App.tsx` o donde tengas el router):

```typescript
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import VideollamadasPage from './pages/VideollamadasPage';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        {/* ... otras rutas ... */}
        
        {/* ✅ AGREGAR ESTA RUTA */}
        <Route 
          path="/videollamadas" 
          element={
            <VideollamadasPage
              currentUserName="Tu Nombre"
              currentUserEmail="tu@email.com"
            />
          } 
        />
      </Routes>
    </BrowserRouter>
  );
}
```

### 5. Configurar React Query Provider (si no está)

En `src/main.tsx`:

```typescript
import React from 'react';
import ReactDOM from 'react-dom/client';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import App from './App';
import './index.css';

// Crear cliente de React Query
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 60000, // 1 minuto
      refetchOnWindowFocus: false,
      retry: 1,
    },
  },
});

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <QueryClientProvider client={queryClient}>
      <App />
    </QueryClientProvider>
  </React.StrictMode>
);
```

### 6. Configurar Autenticación JWT

El servicio espera que el token JWT esté en `localStorage` o `sessionStorage`:

```typescript
// En tu componente de login, después de autenticar:
localStorage.setItem('authToken', jwtToken);

// O para sesión temporal:
sessionStorage.setItem('authToken', jwtToken);
```

---

## 📁 Estructura de Archivos Creada

```
frontend/src/
├── types/
│   └── videollamada.types.ts          # 16 interfaces, 6 enums
├── services/
│   └── videollamadas.service.ts       # API client + utilidades
├── hooks/
│   └── useVideollamada.ts             # 6 hooks personalizados
├── modules/
│   └── comunicacion/
│       └── components/
│           ├── JitsiMeeting.tsx       # Wrapper de Jitsi External API
│           ├── VideoCallWindow.tsx    # Ventana completa con controles
│           └── VideollamadasList.tsx  # Lista y crear videollamadas
└── pages/
    └── VideollamadasPage.tsx          # Página principal
```

---

## 🎯 Funcionalidades Implementadas

### ✅ API Client (`videollamadasAPI`)

- ✅ Health check
- ✅ Generar room name
- ✅ Crear videollamada
- ✅ Obtener videollamada
- ✅ Listar videollamadas (con filtros)
- ✅ Unirse a videollamada
- ✅ Salir de videollamada
- ✅ Obtener participantes activos
- ✅ Actualizar calidad de conexión
- ✅ Finalizar videollamada
- ✅ Cancelar videollamada
- ✅ Agregar grabación
- ✅ Obtener grabaciones
- ✅ Actualizar transcripción
- ✅ Validar acceso
- ✅ Generar JWT para Jitsi

### ✅ Hooks Personalizados

1. **`useVideollamada(id)`**
   - Obtener datos de videollamada
   - Obtener participantes
   - Unirse, salir, finalizar
   - Auto-refetch periódico

2. **`useVideollamadas(options)`**
   - Listar videollamadas con filtros
   - Paginación
   - Crear nueva videollamada

3. **`useCalidadConexion(participanteId)`**
   - Monitorear calidad
   - Reportar métricas
   - Auto-actualización en servidor

4. **`useValidarAcceso(id)`**
   - Validar si puede unirse
   - Límite de participantes
   - Estado de videollamada

5. **`useGrabaciones(id)`**
   - Listar grabaciones
   - Descargar archivos

6. **`useJitsi(videollamada, participante)`**
   - Manejar API de Jitsi
   - Generar JWT
   - Lifecycle management

### ✅ Componentes React

1. **`<JitsiMeeting />`**
   - Wrapper de Jitsi External API
   - Manejo de eventos
   - Configuración personalizable
   - Error handling

2. **`<VideoCallWindow />`**
   - Ventana completa de videollamada
   - Panel de participantes lateral
   - Indicador de calidad de conexión
   - Contador de duración
   - Badge moderador
   - Controles integrados

3. **`<VideollamadasList />`**
   - Lista de videollamadas activas
   - Crear nueva videollamada (video/audio)
   - Filtrar por sala de chat
   - Cards con información detallada
   - Badges de estado

4. **`<VideollamadasPage />`**
   - Página principal integrada
   - Navegación entre lista y llamada
   - Info y ayuda contextual

---

## 🔧 Configuración de Jitsi

### Opción 1: Usar Jitsi.org (Gratis)

Por defecto, el sistema usa `meet.jit.si`. No requiere configuración adicional.

**Pros**:
- ✅ Gratis
- ✅ Sin configuración
- ✅ Funciona inmediatamente

**Contras**:
- ❌ Sin personalización de marca
- ❌ Límites de uso compartido
- ❌ Sin control total

### Opción 2: Self-Hosted Jitsi

Para producción, se recomienda tener tu propio servidor Jitsi.

```yaml
# docker-compose.yml
version: '3'
services:
  jitsi-web:
    image: jitsi/web:latest
    ports:
      - "8443:443"
    environment:
      - ENABLE_AUTH=1
      - ENABLE_GUESTS=1
      - ENABLE_LETSENCRYPT=0
      - DISABLE_HTTPS=0
      - JICOFO_AUTH_USER=focus
      - XMPP_DOMAIN=meet.jitsi
      - XMPP_AUTH_DOMAIN=auth.meet.jitsi
      - XMPP_BOSH_URL_BASE=http://xmpp.meet.jitsi:5280
      - XMPP_MUC_DOMAIN=muc.meet.jitsi
      - TZ=America/Bogota
      - JWT_APP_ID=acadify
      - JWT_APP_SECRET=tu_secreto_aqui
```

---

## 🎨 Estilos y UI

### Clases Tailwind Utilizadas

El sistema usa TailwindCSS para estilos. Las clases principales:

```css
/* Colores de calidad */
.text-green-600    /* Calidad excelente */
.text-blue-600     /* Calidad buena */
.text-yellow-600   /* Calidad regular */
.text-red-600      /* Calidad mala */

/* Estados */
.bg-blue-600       /* Activo, primario */
.bg-green-600      /* Éxito */
.bg-red-600        /* Error, salir */
.bg-gray-700       /* Neutro, secundario */
```

### Personalización

Para cambiar colores o estilos, edita los componentes directamente o configura Tailwind:

```javascript
// tailwind.config.js
module.exports = {
  theme: {
    extend: {
      colors: {
        'videollamada': {
          primary: '#3B82F6',
          success: '#10B981',
          danger: '#EF4444',
        }
      }
    }
  }
}
```

---

## 🧪 Testing

### Prueba Manual

1. **Iniciar Backend**:
```bash
cd backend
python -m uvicorn src.main:app --reload
```

2. **Iniciar Frontend**:
```bash
cd frontend
npm run dev
```

3. **Abrir en Navegador**:
```
http://localhost:5173/videollamadas
```

4. **Flujo de Prueba**:
   - ✅ Crear videollamada
   - ✅ Unirse a videollamada
   - ✅ Ver participantes
   - ✅ Verificar calidad de conexión
   - ✅ Salir de videollamada

### Tests Unitarios (TODO)

```typescript
// tests/videollamadas.test.tsx
import { render, screen } from '@testing-library/react';
import { VideollamadasPage } from '../pages/VideollamadasPage';

describe('VideollamadasPage', () => {
  it('should render list of videollamadas', () => {
    render(<VideollamadasPage />);
    expect(screen.getByText(/Videollamadas/i)).toBeInTheDocument();
  });
});
```

---

## 📊 Uso de la API

### Ejemplo: Crear y Unirse a Videollamada

```typescript
import { videollamadasAPI } from './services/videollamadas.service';

// 1. Crear videollamada
const videollamada = await videollamadasAPI.crearVideollamada({
  tipo_llamada: 'video',
  configuracion: {
    max_participantes: 30,
    permitir_grabacion: true,
  }
});

// 2. Unirse
const participante = await videollamadasAPI.unirseAVideollamada(
  videollamada.id,
  false // no es moderador
);

// 3. Generar JWT para Jitsi
const { token } = await videollamadasAPI.generarJitsiToken(
  videollamada.id,
  videollamada.jitsi_room_name,
  'Juan Pérez',
  false
);

// 4. Inicializar Jitsi con JWT
// (El componente JitsiMeeting lo hace automáticamente)
```

---

## 🔐 Seguridad

### JWT Authentication

El sistema requiere JWT para todas las operaciones. El token debe incluir:

```json
{
  "sub": "usuario_id",
  "email": "usuario@example.com",
  "exp": 1699999999
}
```

### Jitsi JWT

Para autenticación con Jitsi, el backend debe generar un JWT con:

```json
{
  "context": {
    "user": {
      "id": "usuario_id",
      "name": "Nombre Usuario",
      "avatar": "https://...",
      "email": "usuario@example.com"
    }
  },
  "room": "nombre-sala",
  "moderator": false,
  "aud": "jitsi",
  "iss": "acadify",
  "sub": "meet.jit.si",
  "exp": 1699999999
}
```

---

## 🐛 Troubleshooting

### Error: "Jitsi Meet External API no está disponible"

**Solución**: Verifica que el script esté en `index.html`:
```html
<script src="https://meet.jit.si/external_api.js"></script>
```

### Error: "Cannot import videollamadasAPI"

**Solución**: Verifica la ruta de importación:
```typescript
import { videollamadasAPI } from '../services/videollamadas.service';
```

### Error: "Network Error" al llamar API

**Solución**: Verifica que el backend esté corriendo:
```bash
curl http://localhost:8000/api/communication/videollamadas/health
```

### Videollamada no se carga

**Solución**: 
1. Revisa la consola del navegador (F12)
2. Verifica que el JWT sea válido
3. Confirma que el room_name sea correcto

---

## 📚 Referencias

- **Jitsi Meet External API**: https://jitsi.github.io/handbook/docs/dev-guide/dev-guide-iframe
- **Jitsi JWT**: https://github.com/jitsi/lib-jitsi-meet/blob/master/doc/tokens.md
- **React Query**: https://tanstack.com/query/latest
- **Tailwind CSS**: https://tailwindcss.com/docs

---

## ✅ Checklist de Implementación

- [x] Types definidos (16 interfaces, 6 enums)
- [x] API Client implementado (16 métodos)
- [x] Hooks personalizados (6 hooks)
- [x] Componente JitsiMeeting
- [x] Componente VideoCallWindow
- [x] Componente VideollamadasList
- [x] Página VideollamadasPage
- [ ] Script Jitsi en index.html (pendiente)
- [ ] Dependencias instaladas (pendiente)
- [ ] Variables de entorno configuradas (pendiente)
- [ ] Ruta agregada al router (pendiente)
- [ ] React Query configurado (verificar)
- [ ] JWT almacenado en localStorage (verificar)
- [ ] Prueba end-to-end (pendiente)

---

## 🚀 Próximos Pasos

1. **Instalar dependencias**:
   ```bash
   npm install date-fns lucide-react
   ```

2. **Agregar script de Jitsi** en `index.html`

3. **Configurar rutas** en tu router

4. **Probar flujo completo**:
   - Crear videollamada
   - Unirse
   - Verificar video/audio
   - Salir

5. **Implementar grabación** (Fase 2.3)

---

**Última actualización**: 9 de noviembre de 2025  
**Versión**: 1.0.0  
**Estado**: ✅ Código completo - Pendiente de instalación y pruebas
