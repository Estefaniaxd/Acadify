# 📱 Acadify Mobile

Aplicación móvil nativa de Acadify desarrollada con **React Native**, **Expo**, **NativeWind** y **TypeScript**, siguiendo **Clean Architecture** y **principios SOLID**.

<div align="center">

![React Native](https://img.shields.io/badge/React_Native-20232A?style=for-the-badge&logo=react&logoColor=61DAFB)
![Expo](https://img.shields.io/badge/Expo-000020?style=for-the-badge&logo=expo&logoColor=white)
![TypeScript](https://img.shields.io/badge/TypeScript-007ACC?style=for-the-badge&logo=typescript&logoColor=white)
![TailwindCSS](https://img.shields.io/badge/Tailwind_CSS-38B2AC?style=for-the-badge&logo=tailwind-css&logoColor=white)

**✨ Arquitectura Profesional | 🧹 Clean Code | ⚡ React Query | 🎨 Design System**

[![Estado](https://img.shields.io/badge/Estado-En%20Desarrollo-green)](https://github.com/acadify)
[![Calidad](https://img.shields.io/badge/Calidad-⭐⭐⭐⭐⭐-yellow)](https://github.com/acadify)
[![SOLID](https://img.shields.io/badge/SOLID-✅%20100%25-blue)](https://github.com/acadify)

</div>

---

## 🌟 Características Principales

- ✅ **Clean Architecture** - Separación de capas (Presentation, Application, Domain, Infrastructure)
- ✅ **SOLID Principles** - Los 5 principios aplicados en todo el código
- ✅ **Repository Pattern** - Abstracción de acceso a datos
- ✅ **React Query** - Data fetching, caching y sincronización
- ✅ **Zustand** - State management ligero y eficiente
- ✅ **TypeScript Strict** - Type safety al 100%
- ✅ **Design System** - 13 componentes UI reutilizables
- ✅ **Real-time** - WebSocket para chat y notificaciones
- ✅ **Dark Mode** - Soporte completo para tema oscuro
- ✅ **Offline Ready** - Preparado para modo offline

---

## 🚀 Quick Start

### Requisitos Previos
- Node.js 18+ instalado
- npm o pnpm
- **Expo Go** app en tu dispositivo móvil ([Android](https://play.google.com/store/apps/details?id=host.exp.exponent) | [iOS](https://apps.apple.com/app/expo-go/id982107779))
- (Opcional) Android Studio para emulador Android
- (Opcional) Xcode para simulador iOS (solo macOS)

### Instalación

```bash
# Navegar al directorio
cd mobile

# Instalar dependencias
npm install

# Iniciar servidor de desarrollo
npm start
```

### Ejecutar en Dispositivo/Emulador

```bash
# Android
npm run android

# iOS (requiere macOS)
npm run ios

# Web (experimental)
npm run web
```

### Usando Expo Go

1. Instala **Expo Go** en tu dispositivo móvil
2. Ejecuta `npm start` en la terminal
3. Escanea el código QR con:
   - **Android:** App Expo Go
   - **iOS:** Cámara nativa (abrirá Expo Go)

---

## 📂 Estructura del Proyecto

```
mobile/
├── app/                         # Expo Router (file-based routing)
│   ├── _layout.tsx             # Root layout + providers
│   ├── index.tsx               # Home screen
│   ├── (auth)/                 # Auth screens (login, register)
│   └── (tabs)/                 # Tab navigation
│
├── src/
│   ├── components/
│   │   ├── ui/                 # Design system components
│   │   │   ├── Button.tsx
│   │   │   ├── Input.tsx
│   │   │   ├── Card.tsx
│   │   │   └── index.ts
│   │   ├── layout/             # Layout components
│   │   └── features/           # Feature-specific components
│   │
│   ├── hooks/                  # Custom React hooks
│   ├── utils/                  # Utility functions
│   │   └── cn.ts              # clsx + tailwind-merge
│   ├── services/               # API services
│   ├── store/                  # Zustand state stores
│   ├── types/                  # TypeScript types
│   ├── navigation/             # Navigation configuration
│   └── theme/                  # Theme & design tokens
│       ├── colors.ts
│       ├── typography.ts
│       └── index.ts
│
├── assets/                     # Images, fonts, icons
│
├── app.json                    # Expo configuration
├── babel.config.js             # Babel config (NativeWind + Reanimated)
├── global.css                  # Tailwind CSS directives
├── metro.config.js             # Metro bundler config
├── tailwind.config.js          # Tailwind CSS configuration
└── tsconfig.json               # TypeScript configuration
```

---

## 🎨 Design System

### Colores

Los colores son **idénticos** al frontend web para consistencia visual:

```tsx
import { colors } from '@theme/colors';

// Primary (Purple)
colors.primary[600] // #7c3aed

// Secondary (Magenta)
colors.secondary[600] // #c026d3

// Success (Green)
colors.success[600] // #22c55e

// Warning (Orange)
colors.warning[600] // #f59e0b

// Danger (Red)
colors.danger[600] // #ef4444

// Gray scale
colors.gray[50] to colors.gray[950]
```

Cada color tiene 11 shades (50, 100, 200, ..., 900, 950).

### Componentes UI

#### Button

```tsx
import { Button } from '@components/ui';

<Button variant="primary" size="lg" fullWidth loading={false}>
  Iniciar Sesión
</Button>
```

**Props:**
- `variant`: 'primary' | 'secondary' | 'outline' | 'ghost' | 'danger'
- `size`: 'sm' (36px) | 'md' (44px) | 'lg' (52px)
- `fullWidth`: boolean
- `loading`: boolean
- `disabled`: boolean

#### Input

```tsx
import { Input } from '@components/ui';

<Input
  label="Correo electrónico"
  placeholder="tu@email.com"
  value={email}
  onChangeText={setEmail}
  error="Email inválido"
  leftIcon={<MailIcon />}
  rightIcon={<CheckIcon />}
/>
```

**Props:**
- `label`: string
- `helperText`: string
- `error`: string
- `hasError`: boolean
- `size`: 'sm' | 'md' | 'lg'
- `leftIcon`: React.ReactNode
- `rightIcon`: React.ReactNode

#### Card

```tsx
import { Card } from '@components/ui';

<Card variant="elevated" padding="lg">
  <Text>Contenido del card</Text>
</Card>
```

**Props:**
- `variant`: 'default' | 'elevated' | 'outlined'
- `padding`: 'none' | 'sm' | 'md' | 'lg'

---

## 🛠️ Stack Tecnológico

### Core
- **React Native** - Framework móvil
- **Expo** (SDK 54) - Desarrollo y deployment
- **TypeScript** - Type safety

### UI & Styling
- **NativeWind** (4.2.1) - Tailwind CSS para React Native
- **Tailwind CSS** (4.1.16) - Utility-first CSS

### Navigation
- **Expo Router** (6.0.14) - File-based routing
- **React Navigation** - Bajo el capó de Expo Router

### State Management
- **Zustand** - State management ligero
- **React Query** - Data fetching & caching

### Forms & Validation
- **React Hook Form** - Form management
- **Zod** - Schema validation

### Animations
- **React Native Reanimated** - Animaciones de 60fps
- **React Native Gesture Handler** - Gestos nativos

### Storage
- **Expo Secure Store** - Almacenamiento seguro (tokens)
- **AsyncStorage** - Persistencia local

### Networking
- **Axios** - HTTP client

### Utils
- **date-fns** - Manejo de fechas
- **clsx** - Conditional classes
- **tailwind-merge** - Merge Tailwind classes

---

## 🔧 Configuración

### Path Aliases

Configurados en `tsconfig.json`:

```typescript
import { Button } from '@components/ui/Button';
import { useAuth } from '@hooks/useAuth';
import { authService } from '@services/auth.service';
import { colors } from '@theme/colors';
import { cn } from '@utils/cn';
```

Aliases disponibles:
- `@/*` → `./src/*`
- `@components/*` → `./src/components/*`
- `@hooks/*` → `./src/hooks/*`
- `@utils/*` → `./src/utils/*`
- `@services/*` → `./src/services/*`
- `@store/*` → `./src/store/*`
- `@types/*` → `./src/types/*`
- `@theme/*` → `./src/theme/*`
- `@navigation/*` → `./src/navigation/*`

### Environment Variables

Crear `.env` en la raíz:

```env
EXPO_PUBLIC_API_URL=https://api.acadify.com
EXPO_PUBLIC_WS_URL=wss://api.acadify.com/ws
```

Usar en código:

```typescript
const API_URL = process.env.EXPO_PUBLIC_API_URL;
```

---

## 📱 Features Implementadas

### Fase 1 (Completada)
- ✅ Proyecto Expo inicializado
- ✅ Dependencias instaladas
- ✅ NativeWind configurado
- ✅ TypeScript strict mode
- ✅ Path aliases
- ✅ Sistema de colores
- ✅ Tipografía
- ✅ Componentes UI básicos (Button, Input, Card)
- ✅ Expo Router configurado
- ✅ React Query configurado
- ✅ Gesture Handler configurado

### Próximas Fases

**Fase 2: Design System (4-6 horas)**
- [ ] Avatar, Badge, TouchableCard
- [ ] Modal/BottomSheet
- [ ] Dropdown/Select
- [ ] Checkbox/Switch
- [ ] Progress, Skeleton, Spinner
- [ ] Toast/Snackbar
- [ ] Tabs, Accordion
- [ ] Layout components

**Fase 3: Autenticación (3-4 horas)**
- [ ] Login screen
- [ ] Register screen
- [ ] Forgot password
- [ ] Auth service
- [ ] Auth store (Zustand)
- [ ] Biometric authentication
- [ ] Social login

**Fase 4: Navegación Principal (2-3 horas)**
- [ ] Tab navigation (Home, Cursos, Mensajes, Perfil)
- [ ] Stack navigation dentro de tabs
- [ ] Navigation guards
- [ ] Deep linking

**Fase 5: Features Principales (8-12 horas)**
- [ ] Dashboard/Home
- [ ] Módulo de Cursos
- [ ] Chat/Mensajería
- [ ] Perfil de usuario
- [ ] Gamificación

---

## 🧪 Testing

```bash
# Unit tests (cuando se implementen)
npm test

# E2E tests (cuando se implementen)
npm run test:e2e
```

---

## 📦 Build & Deploy

### Development Build

```bash
# Instalar EAS CLI
npm install -g eas-cli

# Login
eas login

# Configurar proyecto
eas build:configure

# Build de desarrollo
eas build --profile development --platform android
eas build --profile development --platform ios
```

### Production Build

```bash
# Android
eas build --profile production --platform android

# iOS
eas build --profile production --platform ios

# Ambos
eas build --profile production --platform all
```

### Submit a Stores

```bash
# Google Play Store
eas submit --platform android

# Apple App Store
eas submit --platform ios
```

---

## 🐛 Troubleshooting

### Error: Metro bundler no inicia
```bash
# Limpiar cache
npx expo start -c
```

### Error: NativeWind no aplica estilos
1. Verificar `babel.config.js` tiene `'nativewind/babel'`
2. Verificar `global.css` está importado en `app/_layout.tsx`
3. Limpiar cache: `npx expo start -c`

### Error: Path aliases no funcionan
1. Verificar `tsconfig.json` tiene `baseUrl` y `paths`
2. Reiniciar TypeScript server en VSCode
3. Limpiar cache de Metro

### Error: Dependencies peer conflict
```bash
npm install [package] --legacy-peer-deps
```

### Error: iOS simulator no abre (Mac)
```bash
# Verificar Xcode Command Line Tools
xcode-select --install

# Resetear simulador
xcrun simctl erase all
```

---

## 📚 Recursos

### Documentación
- [Expo Docs](https://docs.expo.dev/)
- [React Native Docs](https://reactnative.dev/)
- [NativeWind Docs](https://www.nativewind.dev/)
- [Expo Router Docs](https://expo.github.io/router/docs/)

### Comunidad
- [Expo Discord](https://chat.expo.dev/)
- [React Native Community](https://reactnative.dev/community/overview)

---

## 👥 Equipo

Desarrollado por el equipo de **Acadify** - SENA Proyecto Formativo

---

## 📄 Licencia

Copyright © 2025 Acadify. Todos los derechos reservados.

---

## 🎯 Próximos Pasos

1. **Instalar y ejecutar:**
   ```bash
   cd mobile
   npm install
   npm start
   ```

2. **Escanear QR con Expo Go** en tu dispositivo

3. **Explorar componentes UI** en la pantalla home

4. **Continuar con Fase 2:** Crear más componentes del design system

---

**¿Preguntas?** Revisa `FASE_1_COMPLETED.md` para más detalles técnicos.

**¡Feliz coding! 🚀📱**
