# 📱 Plan de Acción: Acadify Mobile App

**Fecha:** 31 de octubre de 2025  
**Stack:** React Native + Expo + NativeWind + TypeScript  
**Objetivo:** App móvil nativa con paridad de funcionalidades del web

---

## 🎯 Estrategia de Desarrollo

### **Filosofía: Mobile-First + Code Reuse**
```
1. Reutilizar lógica del frontend web (hooks, utils, types)
2. Diseñar específicamente para móvil (no adaptar web)
3. Aprovechar capacidades nativas (cámara, push, gestos)
4. Optimizar para performance móvil
5. Offline-first cuando sea posible
```

---

## 📂 Estructura del Proyecto

```
Acadify/
├── frontend/          # Web app (React + Vite) ✅ Existente
├── backend/           # API (FastAPI + PostgreSQL) ✅ Existente
└── mobile/            # 📱 Nueva app móvil
    ├── app/           # Expo Router (file-based routing)
    │   ├── (auth)/    # Auth screens (login, register)
    │   ├── (tabs)/    # Tab navigation (home, courses, profile)
    │   ├── _layout.tsx
    │   └── index.tsx
    ├── src/
    │   ├── components/      # UI components
    │   │   ├── ui/          # Design system (Button, Input, Card...)
    │   │   ├── layout/      # Layout components
    │   │   └── features/    # Feature-specific components
    │   ├── hooks/           # 🔄 Compartidos con web
    │   ├── utils/           # 🔄 Compartidos con web
    │   ├── types/           # 🔄 Compartidos con web
    │   ├── services/        # API calls
    │   ├── store/           # State management (Zustand)
    │   ├── navigation/      # Navigation config
    │   └── theme/           # Theme config (NativeWind)
    ├── assets/
    │   ├── images/
    │   ├── icons/
    │   └── fonts/
    ├── app.json           # Expo config
    ├── package.json
    ├── tsconfig.json
    ├── tailwind.config.js # NativeWind config
    └── metro.config.js
```

---

## 🚀 Fase 1: Setup e Infraestructura (2-3 horas)

### **1.1. Inicializar Proyecto Expo**
```bash
cd Acadify
npx create-expo-app@latest mobile --template blank-typescript
cd mobile
```

### **1.2. Instalar Dependencias Core**
```bash
# Expo essentials
npx expo install expo-router expo-status-bar expo-splash-screen

# Navigation
npx expo install react-native-safe-area-context
npx expo install react-native-screens
npx expo install expo-linking expo-constants

# NativeWind (Tailwind for React Native)
npm install nativewind@^4.0.0
npm install --save-dev tailwindcss

# State Management
npm install zustand
npm install @tanstack/react-query

# Icons
npm install react-native-svg
npx expo install expo-vector-icons

# Forms
npm install react-hook-form zod @hookform/resolvers

# Animations
npm install react-native-reanimated
npm install react-native-gesture-handler

# Storage
npx expo install expo-secure-store
npx expo install @react-native-async-storage/async-storage

# Networking
npm install axios

# Utils
npm install date-fns
npm install clsx tailwind-merge
```

### **1.3. Configurar NativeWind**
```js
// tailwind.config.js
module.exports = {
  content: [
    "./app/**/*.{js,jsx,ts,tsx}",
    "./src/**/*.{js,jsx,ts,tsx}"
  ],
  presets: [require("nativewind/preset")],
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#f5f3ff',
          500: '#8b5cf6',
          600: '#7c3aed',
          700: '#6d28d9',
        },
        // ... mismo color system del web
      }
    }
  }
}
```

### **1.4. Configurar TypeScript**
```json
// tsconfig.json
{
  "extends": "expo/tsconfig.base",
  "compilerOptions": {
    "strict": true,
    "paths": {
      "@/*": ["./src/*"],
      "@components/*": ["./src/components/*"],
      "@hooks/*": ["./src/hooks/*"],
      "@utils/*": ["./src/utils/*"],
      "@services/*": ["./src/services/*"],
      "@types/*": ["./src/types/*"]
    }
  }
}
```

### **1.5. Configurar app.json**
```json
{
  "expo": {
    "name": "Acadify",
    "slug": "acadify",
    "version": "1.0.0",
    "scheme": "acadify",
    "platforms": ["ios", "android"],
    "orientation": "portrait",
    "icon": "./assets/icon.png",
    "splash": {
      "image": "./assets/splash.png",
      "backgroundColor": "#7c3aed"
    },
    "plugins": [
      "expo-router",
      "expo-secure-store"
    ]
  }
}
```

---

## 🎨 Fase 2: Design System (4-6 horas)

### **2.1. Sistema de Colores y Tipografía**
```tsx
// src/theme/colors.ts
export const colors = {
  // Mismo del web
  primary: {
    50: '#f5f3ff',
    500: '#8b5cf6',
    600: '#7c3aed',
  },
  // ...
}

// src/theme/typography.ts
export const typography = {
  h1: 'text-4xl font-bold',
  h2: 'text-3xl font-bold',
  body: 'text-base',
  // ...
}
```

### **2.2. Componentes UI Base**
**Prioridad Alta:**
- ✅ Button (variants: primary, secondary, ghost, danger)
- ✅ Input (con validación, icons, error states)
- ✅ Card (con shadow, border, variants)
- ✅ Avatar (con fallback, size variants)
- ✅ Badge (status indicators)
- ✅ TouchableCard (con press feedback)

**Prioridad Media:**
- ✅ Modal/BottomSheet
- ✅ Dropdown/Select
- ✅ Checkbox/Switch
- ✅ Progress Bar
- ✅ Skeleton Loader

**Prioridad Baja:**
- ✅ Tabs
- ✅ Accordion
- ✅ Toast/Snackbar

### **2.3. Layout Components**
- Screen Container (con SafeArea, ScrollView, KeyboardAware)
- Header (con back button, title, actions)
- TabBar custom
- Loading States
- Empty States
- Error States

---

## 🔐 Fase 3: Autenticación (3-4 horas)

### **3.1. Auth Service**
```tsx
// src/services/auth.service.ts
export const authService = {
  login: async (email: string, password: string) => {
    // Reutilizar endpoint del backend existente
    const response = await axios.post('/auth/login', { email, password });
    await SecureStore.setItemAsync('token', response.data.access_token);
    return response.data;
  },
  // ...
}
```

### **3.2. Auth Store (Zustand)**
```tsx
// src/store/auth.store.ts
export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  isAuthenticated: false,
  login: async (email, password) => {
    const user = await authService.login(email, password);
    set({ user, isAuthenticated: true });
  },
  // ...
}));
```

### **3.3. Auth Screens**
```
app/(auth)/
├── login.tsx          # Login screen
├── register.tsx       # Register screen
├── forgot.tsx         # Forgot password
└── _layout.tsx        # Auth layout (no tabs)
```

**Features:**
- ✅ Form validation con react-hook-form + zod
- ✅ Biometric authentication (Face ID / Touch ID)
- ✅ Remember me con SecureStore
- ✅ Social login (Google, Apple)
- ✅ Error handling con toast

---

## 🏠 Fase 4: Navegación Principal (2-3 horas)

### **4.1. Tab Navigation**
```tsx
// app/(tabs)/_layout.tsx
export default function TabLayout() {
  return (
    <Tabs
      screenOptions={{
        tabBarActiveTintColor: colors.primary[600],
        tabBarStyle: {
          height: 60,
          paddingBottom: 8,
        }
      }}
    >
      <Tabs.Screen name="index" options={{ title: 'Inicio', icon: HomeIcon }} />
      <Tabs.Screen name="courses" options={{ title: 'Cursos', icon: BookIcon }} />
      <Tabs.Screen name="messages" options={{ title: 'Mensajes', icon: MessageIcon }} />
      <Tabs.Screen name="profile" options={{ title: 'Perfil', icon: UserIcon }} />
    </Tabs>
  );
}
```

### **4.2. Stack Navigation (dentro de tabs)**
```
app/(tabs)/
├── index.tsx              # Home/Dashboard
├── courses/
│   ├── index.tsx          # Courses list
│   ├── [id].tsx           # Course detail
│   └── [id]/
│       ├── lesson.tsx     # Lesson view
│       └── assignment.tsx # Assignment view
├── messages/
│   ├── index.tsx          # Conversations list
│   └── [id].tsx           # Chat screen
└── profile/
    ├── index.tsx          # Profile view
    ├── edit.tsx           # Edit profile
    └── settings.tsx       # Settings
```

---

## 📚 Fase 5: Features Principales (8-12 horas)

### **5.1. Dashboard/Home**
**Componentes:**
- Welcome header con avatar
- Quick stats (courses, tasks, points)
- Recent activity feed
- Upcoming assignments
- Achievement badges

**API Integration:**
```tsx
const { data: dashboard } = useQuery({
  queryKey: ['dashboard'],
  queryFn: () => api.get('/dashboard'),
});
```

### **5.2. Courses Module**
**Screens:**
- Courses list (con filtros, búsqueda)
- Course detail (descripción, syllabus, progress)
- Lesson viewer (video, PDF, quiz)
- Assignments list
- Assignment submission

**Features:**
- ✅ Video player (expo-av)
- ✅ PDF viewer
- ✅ File picker para subir tareas
- ✅ Progress tracking
- ✅ Offline download de materiales

### **5.3. Mensajes/Chat**
**Screens:**
- Conversations list
- Chat screen (mensajes 1-1 y grupos)
- User search

**Features:**
- ✅ Real-time con WebSocket
- ✅ Push notifications
- ✅ Image/file sharing (expo-image-picker)
- ✅ Message reactions
- ✅ Typing indicators
- ✅ Read receipts

### **5.4. Perfil**
**Screens:**
- Profile view (info, stats, badges)
- Edit profile (avatar, bio, info)
- Settings (notificaciones, tema, idioma)
- Achievements
- Points/Levels

**Features:**
- ✅ Avatar editor/upload
- ✅ Camera integration
- ✅ Dark mode toggle
- ✅ Language selector
- ✅ Logout

---

## 🎮 Fase 6: Gamificación (4-6 horas)

### **6.1. Sistema de Puntos**
```tsx
// src/components/features/PointsDisplay.tsx
<View className="flex-row items-center gap-2">
  <StarIcon className="text-yellow-500" />
  <Text className="text-2xl font-bold">{points}</Text>
  <Text className="text-gray-500">puntos</Text>
</View>
```

### **6.2. Badges/Logros**
- Badge collection grid
- Progress bars para unlock
- Animaciones con react-native-reanimated
- Confetti effect al desbloquear

### **6.3. Leaderboard**
- Ranking de estudiantes
- Filtros (clase, mes, global)
- Animated list transitions

---

## 🔔 Fase 7: Notificaciones (2-3 horas)

### **7.1. Push Notifications**
```bash
npx expo install expo-notifications
```

```tsx
// src/services/notifications.service.ts
import * as Notifications from 'expo-notifications';

export const notificationService = {
  registerForPushNotifications: async () => {
    const { status } = await Notifications.requestPermissionsAsync();
    if (status !== 'granted') return;
    
    const token = await Notifications.getExpoPushTokenAsync();
    // Enviar token al backend
    await api.post('/notifications/register', { token });
  },
  // ...
};
```

### **7.2. Local Notifications**
- Recordatorios de tareas
- Alarmas de exámenes
- Daily streak reminders

---

## 📴 Fase 8: Offline Support (3-4 horas)

### **8.1. Cache Strategy**
```tsx
// src/services/api.ts
import { QueryClient } from '@tanstack/react-query';
import NetInfo from '@react-native-community/netinfo';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 1000 * 60 * 5, // 5 min
      cacheTime: 1000 * 60 * 30, // 30 min
      retry: 3,
      networkMode: 'offlineFirst',
    }
  }
});
```

### **8.2. Offline Features**
- ✅ Ver cursos descargados
- ✅ Leer materiales offline
- ✅ Completar cuestionarios offline (sync después)
- ✅ Queue de tareas pendientes de subir

---

## 🧪 Fase 9: Testing (2-3 horas)

### **9.1. Unit Tests**
```bash
npm install --save-dev jest @testing-library/react-native
```

### **9.2. E2E Tests**
```bash
npm install --save-dev detox
```

### **9.3. Coverage**
- Componentes UI: 80%+
- Services: 90%+
- Utils: 95%+

---

## 🚢 Fase 10: Build & Deploy (2-3 horas)

### **10.1. Configuración EAS Build**
```bash
npm install -g eas-cli
eas login
eas build:configure
```

### **10.2. Builds**
```bash
# Android
eas build --platform android --profile production

# iOS
eas build --platform ios --profile production
```

### **10.3. App Stores**
- Google Play Store setup
- Apple App Store setup
- Screenshots y metadata
- Privacy policy

---

## 📊 Estimación de Tiempo Total

| Fase | Tiempo | Prioridad |
|------|--------|-----------|
| 1. Setup | 2-3h | P0 |
| 2. Design System | 4-6h | P0 |
| 3. Auth | 3-4h | P0 |
| 4. Navigation | 2-3h | P0 |
| 5. Features | 8-12h | P0 |
| 6. Gamificación | 4-6h | P1 |
| 7. Notifications | 2-3h | P1 |
| 8. Offline | 3-4h | P1 |
| 9. Testing | 2-3h | P2 |
| 10. Deploy | 2-3h | P2 |
| **TOTAL** | **32-47h** | **~1 semana** |

---

## 🎯 Criterios de Éxito

### **Performance:**
- ✅ App inicia en <2s
- ✅ Transiciones <16ms (60fps)
- ✅ API calls <500ms
- ✅ Bundle <50MB

### **UX:**
- ✅ Gestos nativos (swipe, pull-to-refresh)
- ✅ Haptic feedback
- ✅ Smooth animations
- ✅ Keyboard handling perfecto
- ✅ Dark mode completo

### **Code Quality:**
- ✅ TypeScript strict mode
- ✅ 0 console.log en producción
- ✅ ESLint + Prettier
- ✅ Componentes reutilizables
- ✅ Documentación inline

---

## 🔄 Reutilización de Código del Web

### **Compartir entre Web y Mobile:**
```
Acadify/
├── shared/           # 🆕 Código compartido
│   ├── hooks/        # useAuth, useForm, useDebounce
│   ├── utils/        # formatDate, validation, api
│   ├── types/        # User, Course, Message types
│   └── constants/    # API endpoints, colors
├── frontend/         # Web (importa desde shared/)
├── mobile/           # Mobile (importa desde shared/)
└── backend/          # API
```

**Setup con pnpm workspaces:**
```json
// Acadify/package.json
{
  "name": "acadify-monorepo",
  "private": true,
  "workspaces": [
    "shared",
    "frontend",
    "mobile"
  ]
}
```

---

## 🚀 Próximos Pasos Inmediatos

### **1. Crear estructura del proyecto**
```bash
cd /run/media/arch/Storage/SENA/Proyecto-Formativo/Acadify
npx create-expo-app@latest mobile --template blank-typescript
```

### **2. Instalar dependencias**
```bash
cd mobile
npm install [todas las deps de arriba]
```

### **3. Configurar NativeWind + TypeScript**

### **4. Crear primer componente (Button)**

### **5. Crear auth screens**

---

## 💡 Mejores Prácticas Específicas Mobile

### **1. Performance:**
- useCallback/useMemo para prevenir re-renders
- FlatList con getItemLayout para listas grandes
- Image optimization con expo-image
- Lazy load de screens

### **2. UX Nativa:**
- SafeAreaView en todas las screens
- KeyboardAvoidingView en formularios
- Pull-to-refresh en listas
- Swipe gestures donde tenga sentido
- Haptic feedback en acciones importantes

### **3. Seguridad:**
- SecureStore para tokens
- SSL Pinning para API
- Ofuscar código en producción
- No console.log de data sensible

### **4. Testing:**
- Probar en Android + iOS
- Diferentes tamaños de pantalla
- Modo oscuro
- Rotación
- Conexión lenta/offline

---

**🎉 Con este plan, tendremos una app móvil profesional y escalable que complementa perfectamente el web app existente!**
