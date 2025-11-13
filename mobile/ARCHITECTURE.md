# 📱 Acadify Mobile - Arquitectura y Documentación Completa

## 🏗️ Arquitectura General

La aplicación móvil de Acadify está construida siguiendo **principios SOLID**, **Clean Architecture** y **mejores prácticas de React Native**.

---

## 📐 Principios de Diseño Aplicados

### **SOLID Principles**

#### **1. Single Responsibility Principle (SRP)**
Cada módulo tiene una única responsabilidad:
- **Servicios**: Solo comunicación con API
- **Stores**: Solo gestión de estado
- **Hooks**: Solo lógica de React Query
- **Componentes UI**: Solo presentación
- **Utils**: Solo funciones auxiliares

#### **2. Open/Closed Principle (OCP)**
Los módulos están abiertos para extensión pero cerrados para modificación:
- Servicios usan clases con métodos extensibles
- Hooks aceptan opciones personalizables
- Componentes UI aceptan props opcionales

#### **3. Liskov Substitution Principle (LSP)**
Las abstracciones son intercambiables:
- Todos los servicios implementan el patrón Repository
- Todos los hooks retornan estructuras similares de React Query

#### **4. Interface Segregation Principle (ISP)**
Interfaces específicas para cada caso de uso:
- Types separados por dominio (Course, Message, User)
- Hooks específicos por funcionalidad

#### **5. Dependency Inversion Principle (DIP)**
Depende de abstracciones, no de implementaciones:
- Componentes dependen de hooks, no de servicios directamente
- Hooks dependen de servicios, no de axios directamente
- Servicios dependen de apiClient, no de fetch directamente

---

## 📂 Estructura del Proyecto

```
mobile/
├── app/                            # Expo Router (Navegación)
│   ├── _layout.tsx                # Root layout con providers
│   ├── index.tsx                  # Landing/Home
│   ├── (auth)/                    # Auth stack
│   │   ├── login.tsx
│   │   ├── register.tsx
│   │   └── forgot-password.tsx
│   └── (app)/                     # Main app (tabs)
│       ├── _layout.tsx            # Tab navigation
│       ├── index.tsx              # Dashboard
│       ├── courses.tsx            # Courses list
│       ├── messages.tsx           # Chat list
│       └── profile.tsx            # User profile
│
├── src/
│   ├── components/
│   │   └── ui/                    # Design System
│   │       ├── Button.tsx
│   │       ├── Input.tsx
│   │       ├── Card.tsx
│   │       ├── Badge.tsx
│   │       ├── Avatar.tsx
│   │       ├── Progress.tsx
│   │       ├── Checkbox.tsx
│   │       ├── Switch.tsx
│   │       ├── Modal.tsx
│   │       ├── Spinner.tsx
│   │       ├── Skeleton.tsx
│   │       ├── Toast.tsx
│   │       └── index.ts
│   │
│   ├── services/                  # API Services (Repository Pattern)
│   │   ├── auth.service.ts       # Authentication
│   │   ├── user.service.ts       # User management
│   │   ├── course.service.ts     # Courses & lessons
│   │   ├── message.service.ts    # Chat & messaging
│   │   └── index.ts
│   │
│   ├── hooks/                     # Custom React Hooks
│   │   ├── useCourses.ts         # Course data hooks
│   │   ├── useMessages.ts        # Message data hooks
│   │   ├── useUser.ts            # User data hooks
│   │   └── index.ts
│   │
│   ├── store/                     # Zustand Stores
│   │   ├── themeStore.ts         # Theme management
│   │   ├── notificationStore.ts  # Notifications
│   │   ├── courseFilterStore.ts  # Course filters
│   │   ├── websocketStore.ts     # WebSocket connection
│   │   └── index.ts
│   │
│   ├── context/
│   │   └── AuthContext.tsx       # Auth state & navigation guards
│   │
│   ├── utils/
│   │   ├── api.ts                # Axios config & interceptors
│   │   ├── auth.ts               # JWT parsing & validation
│   │   └── cn.ts                 # className utilities
│   │
│   ├── theme/
│   │   ├── colors.ts             # Color palette
│   │   ├── typography.ts         # Text styles
│   │   └── index.ts
│   │
│   └── types/                     # TypeScript types (global)
│
├── assets/                        # Images, fonts, icons
│
├── app.json                       # Expo configuration
├── babel.config.js                # Babel (NativeWind + Reanimated)
├── global.css                     # Tailwind directives
├── metro.config.js                # Metro bundler
├── tailwind.config.js             # Tailwind CSS config
└── tsconfig.json                  # TypeScript config
```

---

## 🔄 Flujo de Datos (Data Flow)

```
┌─────────────┐
│  Component  │ ← Vista/Pantalla
└──────┬──────┘
       │
       ├── usa hooks personalizados
       ↓
┌─────────────┐
│  Custom     │ ← useCourses, useMessages, useUser
│  Hooks      │   (React Query)
└──────┬──────┘
       │
       ├── llama servicios
       ↓
┌─────────────┐
│  Services   │ ← authService, courseService, etc.
│  (Repository)  (Patrón Repository)
└──────┬──────┘
       │
       ├── usa cliente HTTP
       ↓
┌─────────────┐
│  API Client │ ← Axios con interceptors
│  (axios)    │   (Token, Refresh, Error handling)
└──────┬──────┘
       │
       ↓
┌─────────────┐
│  Backend    │ ← FastAPI
│  API        │
└─────────────┘
```

### **Estado Global (Zustand)**

Manejo de estado que no necesita sincronización con API:

```
┌─────────────┐
│  Component  │
└──────┬──────┘
       │
       ├── usa stores
       ↓
┌─────────────┐
│  Zustand    │ ← useThemeStore, useNotificationStore
│  Stores     │   useWebSocketStore, useCourseFilterStore
└─────────────┘
```

---

## 🎯 Capa de Servicios (Services Layer)

### **Patrón Repository**

Todos los servicios siguen el patrón Repository para abstraer la lógica de acceso a datos:

```typescript
class AuthService {
  private readonly baseUrl = '/auth';

  async login(credentials: LoginRequest): Promise<LoginResponse> {
    const response = await apiClient.post(`${this.baseUrl}/login`, credentials);
    return response.data;
  }

  async register(userData: RegisterRequest): Promise<RegisterResponse> {
    const response = await apiClient.post(`${this.baseUrl}/register`, userData);
    return response.data;
  }

  // ... más métodos
}

// Exportar instancia singleton
export const authService = new AuthService();
```

**Ventajas:**
- ✅ Encapsulación de lógica de API
- ✅ Fácil de testear (mockeable)
- ✅ Reutilizable en toda la app
- ✅ TypeScript completo con tipos

### **Servicios Implementados**

#### **1. AuthService** (`auth.service.ts`)
```typescript
// Métodos
- login(credentials)
- register(userData)
- logout()
- refreshToken()
- recoverPassword(email)
- resetPassword(token, password)
- verifyOTP(code)
- enableTwoFactor()
- disableTwoFactor()
```

#### **2. UserService** (`user.service.ts`)
```typescript
// Métodos
- getProfile()
- getUserById(userId)
- updateProfile(data)
- changePassword(data)
- uploadAvatar(file)
- deleteAvatar()
- getStatistics()
- getPreferences()
- updatePreferences(preferences)
- deleteAccount(password)
```

#### **3. CourseService** (`course.service.ts`)
```typescript
// Métodos
- getCourses(filters)
- getCourseById(courseId)
- getEnrolledCourses()
- enrollCourse(courseId)
- unenrollCourse(courseId)
- getCourseLessons(courseId)
- getLessonById(courseId, lessonId)
- markLessonComplete(courseId, lessonId)
- updateLessonProgress(courseId, lessonId, progress)
- getCourseReviews(courseId)
- addCourseReview(courseId, review)
- updateCourseReview(courseId, reviewId, review)
- deleteCourseReview(courseId, reviewId)
- getCategories()
```

#### **4. MessageService** (`message.service.ts`)
```typescript
// Métodos
- getConversations()
- getConversationById(conversationId)
- createConversation(data)
- updateConversation(conversationId, data)
- deleteConversation(conversationId)
- getMessages(conversationId)
- sendMessage(data)
- sendFile(conversationId, file)
- editMessage(conversationId, messageId, content)
- deleteMessage(conversationId, messageId)
- markAsRead(conversationId)
- sendTypingIndicator(conversationId, isTyping)
- addParticipant(conversationId, userId)
- removeParticipant(conversationId, userId)
- leaveConversation(conversationId)
- searchMessages(conversationId, query)
- getUnreadCount()
```

---

## 🪝 Capa de Hooks (Hooks Layer)

### **React Query Hooks**

Abstracción de React Query para data fetching con caché inteligente:

```typescript
export function useCourses(filters?: CourseFilters) {
  return useQuery({
    queryKey: QUERY_KEYS.coursesList(filters),
    queryFn: () => courseService.getCourses(filters),
    staleTime: 1000 * 60 * 5, // 5 minutos
  });
}
```

**Ventajas:**
- ✅ Caché automático
- ✅ Refetch automático
- ✅ Loading states
- ✅ Error handling
- ✅ Optimistic updates
- ✅ Invalidación inteligente

### **Hooks Implementados**

#### **Course Hooks** (`useCourses.ts`)
```typescript
// Queries
- useCourses(filters)              // Lista de cursos
- useCourseDetail(courseId)        // Detalle de curso
- useEnrolledCourses()             // Cursos inscritos
- useCourseLessons(courseId)       // Lecciones de curso
- useLessonDetail(courseId, lessonId)  // Detalle de lección
- useCourseReviews(courseId)       // Reseñas de curso
- useCourseCategories()            // Categorías

// Mutations
- useEnrollCourse()                // Inscribirse
- useMarkLessonComplete()          // Completar lección
- useUpdateLessonProgress()        // Actualizar progreso
- useAddCourseReview()             // Agregar reseña
- useUnenrollCourse()              // Desinscribirse
```

#### **Message Hooks** (`useMessages.ts`)
```typescript
// Queries
- useConversations()               // Lista de conversaciones
- useConversationDetail(id)        // Detalle de conversación
- useConversationMessages(id)      // Mensajes de conversación
- useUnreadMessagesCount()         // Contador de no leídos

// Mutations
- useCreateConversation()          // Crear conversación
- useSendMessage()                 // Enviar mensaje
- useSendFile()                    // Enviar archivo
- useEditMessage()                 // Editar mensaje
- useDeleteMessage()               // Eliminar mensaje
- useMarkMessagesAsRead()          // Marcar como leído
- useAddParticipant()              // Agregar participante
- useRemoveParticipant()           // Eliminar participante
- useLeaveConversation()           // Salir de conversación
```

#### **User Hooks** (`useUser.ts`)
```typescript
// Queries
- useUserProfile()                 // Perfil actual
- useUserById(userId)              // Perfil por ID
- useUserStatistics()              // Estadísticas
- useUserPreferences()             // Preferencias

// Mutations
- useUpdateProfile()               // Actualizar perfil
- useChangePassword()              // Cambiar contraseña
- useUploadAvatar()                // Subir avatar
- useDeleteAvatar()                // Eliminar avatar
- useUpdatePreferences()           // Actualizar preferencias
- useDeleteAccount()               // Eliminar cuenta
```

---

## 🗄️ Gestión de Estado (State Management)

### **Zustand Stores**

Estado global ligero y performante:

#### **1. Theme Store** (`themeStore.ts`)
```typescript
const { mode, isDark, setTheme, toggleTheme } = useThemeStore();

// Funcionalidades
- Persistencia con AsyncStorage
- Auto-detect system theme
- Toggle light/dark
- Listener a cambios del sistema
```

#### **2. Notification Store** (`notificationStore.ts`)
```typescript
const { notifications, unreadCount, addNotification, markAsRead } = useNotificationStore();

// Funcionalidades
- Agregar notificaciones
- Marcar como leído
- Contador de no leídos
- Tipos: curso, mensaje, logro, sistema
```

#### **3. Course Filter Store** (`courseFilterStore.ts`)
```typescript
const { filters, setCategory, setSearchQuery, resetFilters } = useCourseFilterStore();

// Funcionalidades
- Filtros de búsqueda
- Categoría y nivel
- Reset de filtros
- Estado activo/inactivo
```

#### **4. WebSocket Store** (`websocketStore.ts`)
```typescript
const { status, connect, send, addMessageHandler } = useWebSocketStore();

// Funcionalidades
- Conexión persistente
- Reconnection automática (exponential backoff)
- Message handlers
- Typing indicators
- Online status
- Real-time messages
```

---

## 🔐 Autenticación y Seguridad

### **AuthContext** (`AuthContext.tsx`)

Gestión centralizada de autenticación:

```typescript
const { user, isAuthenticated, isLoading, login, logout } = useAuth();

// Funcionalidades
- Parse JWT tokens
- Secure token storage (Expo SecureStore)
- Protected routes (navigation guards)
- Auto-redirect based on auth state
- Token refresh automático
```

### **Token Management**

```typescript
// Almacenamiento seguro
TokenStorage.setAccessToken(token)
TokenStorage.getAccessToken()
TokenStorage.setRefreshToken(token)
TokenStorage.clearTokens()

// Interceptor de refresh automático
apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401) {
      // Refresh token automáticamente
      // Retry request original
    }
  }
);
```

---

## 🎨 Design System

### **Componentes UI**

Todos los componentes UI son:
- ✅ **TypeScript completo**
- ✅ **Accesibles** (a11y)
- ✅ **Themeable** (light/dark)
- ✅ **Responsive**
- ✅ **Animados** (Reanimated)
- ✅ **Documentados** (JSDoc)

```typescript
<Button 
  variant="primary"    // primary, secondary, outline, ghost, danger
  size="lg"            // sm, md, lg
  fullWidth
  loading={isLoading}
  disabled={false}
  onPress={() => {}}
>
  Iniciar Sesión
</Button>
```

### **Tailwind CSS (NativeWind)**

Sistema de diseño consistente:

```typescript
// Colores
className="bg-primary-600 text-white"
className="border-success-500"

// Spacing
className="p-6 mb-4 gap-3"

// Typography
className="text-lg font-bold"

// Dark mode
className="bg-white dark:bg-neutral-900"
```

---

## 🧪 Testing Strategy (Recomendado)

### **Unit Tests**
```typescript
// Servicios
describe('authService', () => {
  it('should login successfully', async () => {
    const result = await authService.login({ identifier: 'test', password: 'test' });
    expect(result.access_token).toBeDefined();
  });
});

// Hooks
describe('useCourses', () => {
  it('should fetch courses', async () => {
    const { result } = renderHook(() => useCourses());
    await waitFor(() => expect(result.current.data).toBeDefined());
  });
});
```

### **Integration Tests**
```typescript
// Flujos completos
describe('Login Flow', () => {
  it('should login and navigate to dashboard', async () => {
    // Test navigation guards
    // Test auth state
  });
});
```

---

## 📊 Performance Optimizations

### **1. React Query Cache**
```typescript
// Stale times optimizados
courses: 5 minutos
messages: 30 segundos
user profile: 5 minutos
```

### **2. Memoization**
```typescript
// useMemo para cálculos costosos
const filteredCourses = useMemo(() => 
  courses.filter(c => c.categoria === selectedCategory),
  [courses, selectedCategory]
);

// useCallback para funciones
const handleSubmit = useCallback(() => {
  // ...
}, [dependencies]);
```

### **3. Lazy Loading**
```typescript
// React.lazy para pantallas grandes
const CourseDetailScreen = React.lazy(() => import('./CourseDetailScreen'));
```

### **4. FlatList Optimization**
```typescript
<FlatList
  data={courses}
  renderItem={renderCourseItem}
  keyExtractor={(item) => item.id}
  removeClippedSubviews
  maxToRenderPerBatch={10}
  updateCellsBatchingPeriod={50}
  windowSize={5}
/>
```

---

## 🚀 Deployment

### **EAS Build**
```bash
# Install EAS CLI
npm install -g eas-cli

# Login
eas login

# Configure
eas build:configure

# Build
eas build --platform ios
eas build --platform android

# Submit
eas submit --platform ios
eas submit --platform android
```

---

## 📝 Convenciones de Código

### **Naming Conventions**
```typescript
// Componentes: PascalCase
export function Button() {}

// Hooks: camelCase con prefijo 'use'
export function useCourses() {}

// Servicios: camelCase con sufijo 'Service'
export const authService = new AuthService();

// Stores: camelCase con sufijo 'Store'
export const useThemeStore = create()

// Types: PascalCase
export interface UserProfile {}

// Constants: UPPER_SNAKE_CASE
export const API_BASE_URL = '...';
```

### **File Structure**
```typescript
/**
 * Título del archivo
 * Descripción breve
 * 
 * @module path/to/file
 * @follows Principio aplicado
 */

// Imports
import { ... } from '...';

// Types
export interface MyType {}

// Constants
const CONSTANT = 'value';

// Main code
export function MyFunction() {}

// Export
export default MyFunction;
```

---

## 🎓 Mejores Prácticas Aplicadas

1. ✅ **TypeScript Strict Mode**
2. ✅ **Error Boundaries**
3. ✅ **Loading States**
4. ✅ **Empty States**
5. ✅ **Optimistic Updates**
6. ✅ **Debouncing/Throttling**
7. ✅ **Accessibility (a11y)**
8. ✅ **Dark Mode Support**
9. ✅ **Offline Support (preparado)**
10. ✅ **Code Splitting**
11. ✅ **Lazy Loading**
12. ✅ **Memoization**
13. ✅ **Clean Architecture**
14. ✅ **SOLID Principles**
15. ✅ **DRY (Don't Repeat Yourself)**

---

## 📚 Recursos y Referencias

- [React Native Docs](https://reactnative.dev/)
- [Expo Docs](https://docs.expo.dev/)
- [React Query Docs](https://tanstack.com/query)
- [Zustand Docs](https://docs.pmnd.rs/zustand)
- [NativeWind Docs](https://www.nativewind.dev/)
- [Clean Architecture](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)
- [SOLID Principles](https://en.wikipedia.org/wiki/SOLID)

---

**Creado por:** GitHub Copilot  
**Fecha:** 31 de octubre de 2025  
**Versión:** 2.0.0
