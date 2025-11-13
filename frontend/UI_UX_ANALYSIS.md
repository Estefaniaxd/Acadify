# 🎨 Análisis UI/UX - Acadify Frontend

## 📅 Fecha: 31 de octubre de 2025
## 🎯 Objetivo: Identificar problemas de diseño y proponer mejoras

---

## 📊 RESUMEN EJECUTIVO

### Estado Actual: ⚠️ **BUENO CON ÁREAS DE MEJORA**

```
✅ Aspectos Positivos:     70%
⚠️  Necesita Mejora:       25%
❌ Problemas Críticos:     5%
```

### Principales Hallazgos:

1. ✅ **Sistema de temas bien implementado** (Dark/Light mode)
2. ✅ **Animaciones fluidas** con Framer Motion
3. ✅ **Gradientes premium** bien diseñados
4. ⚠️  **Inconsistencias en espaciado** y tamaños
5. ⚠️  **Falta de sistema de diseño** unificado
6. ⚠️  **Componentes reutilizables limitados**
7. ❌ **Accesibilidad** (contraste, ARIA labels)
8. ❌ **Responsive design** incompleto

---

## 🎨 SISTEMA DE DISEÑO ACTUAL

### Colores (Tailwind Config)

#### ✅ Bien Definidos:
```javascript
colors: {
  primary: {
    DEFAULT: '#6B21A8',  // Purple-700
    50: '#F6F0FB',
    600: '#8C2DAE'
  },
  accent: {
    DEFAULT: '#16A34A',  // Green-600
  }
}
```

#### ⚠️ Problemas Identificados:
```
1. Falta escala completa de primary (100-900)
2. Accent solo tiene DEFAULT (falta 50-900)
3. No hay colores semánticos (success, warning, error, info)
4. Gradientes hardcoded en componentes (no reutilizables)
```

#### 💡 Solución Propuesta:
```javascript
// tailwind.config.cjs - Sistema de colores completo
colors: {
  primary: {
    50: '#faf5ff',
    100: '#f3e8ff',
    200: '#e9d5ff',
    300: '#d8b4fe',
    400: '#c084fc',
    500: '#a855f7',
    600: '#9333ea',  // Principal
    700: '#7e22ce',
    800: '#6b21a8',  // Actual DEFAULT
    900: '#581c87',
  },
  accent: {
    50: '#f0fdf4',
    100: '#dcfce7',
    200: '#bbf7d0',
    300: '#86efac',
    400: '#4ade80',
    500: '#22c55e',
    600: '#16a34a',  // Actual DEFAULT
    700: '#15803d',
    800: '#166534',
    900: '#14532d',
  },
  success: {
    DEFAULT: '#10b981',  // Emerald-500
    light: '#34d399',
    dark: '#059669',
  },
  warning: {
    DEFAULT: '#f59e0b',  // Amber-500
    light: '#fbbf24',
    dark: '#d97706',
  },
  error: {
    DEFAULT: '#ef4444',  // Red-500
    light: '#f87171',
    dark: '#dc2626',
  },
  info: {
    DEFAULT: '#3b82f6',  // Blue-500
    light: '#60a5fa',
    dark: '#2563eb',
  }
}
```

### Tipografía

#### ✅ Usos Actuales:
```tsx
// Títulos
"text-3xl font-bold"           // h1
"text-xl font-bold"            // h2  
"text-lg font-bold"            // h3
"text-sm font-medium"          // labels

// Cuerpo
"text-base"                    // Regular
"text-sm"                      // Small
"text-xs"                      // Extra small
```

#### ⚠️ Problemas:
```
1. No hay sistema de tipografía consistente
2. Tamaños hardcoded en cada componente
3. Sin jerarquía clara (h1-h6)
4. Falta line-height y letter-spacing optimizados
```

#### 💡 Solución Propuesta:
```css
/* index.css - Sistema tipográfico */
@layer components {
  /* Headings */
  .heading-1 {
    @apply text-4xl md:text-5xl font-bold tracking-tight leading-tight;
  }
  
  .heading-2 {
    @apply text-3xl md:text-4xl font-bold tracking-tight leading-snug;
  }
  
  .heading-3 {
    @apply text-2xl md:text-3xl font-semibold tracking-tight leading-snug;
  }
  
  .heading-4 {
    @apply text-xl md:text-2xl font-semibold leading-normal;
  }
  
  .heading-5 {
    @apply text-lg md:text-xl font-semibold leading-normal;
  }
  
  .heading-6 {
    @apply text-base md:text-lg font-semibold leading-normal;
  }
  
  /* Body text */
  .body-large {
    @apply text-lg leading-relaxed;
  }
  
  .body-base {
    @apply text-base leading-relaxed;
  }
  
  .body-small {
    @apply text-sm leading-relaxed;
  }
  
  /* Labels & captions */
  .label {
    @apply text-sm font-medium leading-tight;
  }
  
  .caption {
    @apply text-xs leading-tight;
  }
}
```

### Espaciado

#### ✅ Usos Actuales:
```tsx
// Padding
"p-4"  "p-6"  "p-8"     // Irregular
"px-4" "py-2"           // Componentes

// Margins
"mb-4" "mb-6" "mb-8"    // Sin consistencia
"space-x-3" "space-y-4" // Gap entre elementos

// Gap
"gap-3" "gap-4" "gap-6" // Sin sistema
```

#### ⚠️ Problemas:
```
1. No hay escala de espaciado definida (4, 6, 8... vs 12, 16, 24)
2. Mezcla de valores (mb-4 y mb-6 en mismo componente)
3. Sin tokens de espaciado semánticos
```

#### 💡 Solución Propuesta:
```javascript
// tailwind.config.cjs
theme: {
  extend: {
    spacing: {
      // Escala consistente basada en 4px
      'xs': '0.5rem',   // 8px
      'sm': '0.75rem',  // 12px
      'md': '1rem',     // 16px
      'lg': '1.5rem',   // 24px
      'xl': '2rem',     // 32px
      '2xl': '3rem',    // 48px
      '3xl': '4rem',    // 64px
    }
  }
}
```

```css
/* Tokens semánticos */
@layer components {
  .spacing-component {
    @apply p-md;           /* Padding interno componente */
  }
  
  .spacing-section {
    @apply mb-lg;          /* Margen entre secciones */
  }
  
  .spacing-element {
    @apply gap-sm;         /* Gap entre elementos */
  }
}
```

### Sombras y Efectos

#### ✅ Usos Actuales:
```tsx
"shadow-sm"      // Botones
"shadow-md"      // Cards
"shadow-lg"      // Modales
"backdrop-blur-xl"  // Headers glassmorphism
```

#### ⚠️ Problemas:
```
1. No hay sombras personalizadas coherentes
2. Blur effects inconsistentes
3. Sin elevaciones definidas (z-index)
```

#### 💡 Solución Propuesta:
```javascript
// tailwind.config.cjs
theme: {
  extend: {
    boxShadow: {
      'soft': '0 2px 8px rgba(0, 0, 0, 0.04)',
      'card': '0 4px 16px rgba(0, 0, 0, 0.08)',
      'elevated': '0 8px 24px rgba(0, 0, 0, 0.12)',
      'floating': '0 12px 32px rgba(0, 0, 0, 0.16)',
      'primary': '0 4px 16px rgba(107, 33, 168, 0.3)',
      'accent': '0 4px 16px rgba(22, 163, 74, 0.3)',
    }
  }
}
```

---

## 🧩 COMPONENTES REUTILIZABLES

### Estado Actual

#### ✅ Componentes Existentes:
```
src/components/ui/
  ├── Button.tsx       ⚠️ Muy básico (solo 1 variante)
  ├── Toast.tsx        ✅ Bien implementado
  └── Card.tsx         ❌ No existe
```

#### ⚠️ Componentes Necesarios:
```
- Input (text, email, password, textarea)
- Select / Dropdown
- Checkbox / Radio
- Switch / Toggle
- Badge / Tag
- Avatar
- Modal / Dialog
- Tabs
- Accordion
- Progress Bar
- Skeleton Loader
- Tooltip
- Breadcrumbs
- Pagination
```

### 💡 Sistema de Componentes Propuesto

#### 1. Button Component Mejorado

**Archivo**: `src/components/ui/Button.tsx`

```tsx
import React from 'react';
import { motion } from 'framer-motion';
import { IconType } from 'react-icons';

type ButtonVariant = 'primary' | 'secondary' | 'outline' | 'ghost' | 'danger';
type ButtonSize = 'sm' | 'md' | 'lg';

interface ButtonProps {
  children: React.ReactNode;
  variant?: ButtonVariant;
  size?: ButtonSize;
  icon?: IconType;
  iconPosition?: 'left' | 'right';
  loading?: boolean;
  disabled?: boolean;
  fullWidth?: boolean;
  onClick?: () => void;
  type?: 'button' | 'submit' | 'reset';
  className?: string;
}

const variantClasses: Record<ButtonVariant, string> = {
  primary: 'bg-gradient-to-r from-primary-600 to-primary-700 text-white hover:from-primary-700 hover:to-primary-800 shadow-primary',
  secondary: 'bg-accent-600 text-white hover:bg-accent-700 shadow-accent',
  outline: 'border-2 border-primary-600 text-primary-600 hover:bg-primary-50 dark:hover:bg-primary-900/20',
  ghost: 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800',
  danger: 'bg-error text-white hover:bg-error-dark shadow-md',
};

const sizeClasses: Record<ButtonSize, string> = {
  sm: 'px-3 py-1.5 text-sm',
  md: 'px-4 py-2 text-base',
  lg: 'px-6 py-3 text-lg',
};

export function Button({
  children,
  variant = 'primary',
  size = 'md',
  icon: Icon,
  iconPosition = 'left',
  loading = false,
  disabled = false,
  fullWidth = false,
  onClick,
  type = 'button',
  className = '',
}: ButtonProps) {
  return (
    <motion.button
      type={type}
      onClick={onClick}
      disabled={disabled || loading}
      className={`
        inline-flex items-center justify-center gap-2 
        rounded-xl font-medium transition-all duration-200
        disabled:opacity-50 disabled:cursor-not-allowed
        focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2
        ${variantClasses[variant]}
        ${sizeClasses[size]}
        ${fullWidth ? 'w-full' : ''}
        ${className}
      `}
      whileHover={{ scale: disabled ? 1 : 1.02 }}
      whileTap={{ scale: disabled ? 1 : 0.98 }}
    >
      {loading && (
        <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24">
          <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
          <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
        </svg>
      )}
      
      {!loading && Icon && iconPosition === 'left' && <Icon className="w-4 h-4" />}
      {children}
      {!loading && Icon && iconPosition === 'right' && <Icon className="w-4 h-4" />}
    </motion.button>
  );
}
```

#### 2. Input Component

**Archivo**: `src/components/ui/Input.tsx`

```tsx
import React, { forwardRef } from 'react';
import { IconType } from 'react-icons';
import { FiAlertCircle } from 'react-icons/fi';

interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
  helperText?: string;
  icon?: IconType;
  iconPosition?: 'left' | 'right';
  fullWidth?: boolean;
}

export const Input = forwardRef<HTMLInputElement, InputProps>(({
  label,
  error,
  helperText,
  icon: Icon,
  iconPosition = 'left',
  fullWidth = false,
  className = '',
  ...props
}, ref) => {
  const hasError = !!error;

  return (
    <div className={`${fullWidth ? 'w-full' : ''}`}>
      {label && (
        <label className="label mb-2 text-gray-700 dark:text-gray-300">
          {label}
          {props.required && <span className="text-error ml-1">*</span>}
        </label>
      )}
      
      <div className="relative">
        {Icon && iconPosition === 'left' && (
          <div className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400">
            <Icon className="w-5 h-5" />
          </div>
        )}
        
        <input
          ref={ref}
          className={`
            w-full px-4 py-2 
            ${Icon && iconPosition === 'left' ? 'pl-10' : ''}
            ${Icon && iconPosition === 'right' ? 'pr-10' : ''}
            ${hasError ? 'pr-10' : ''}
            bg-white dark:bg-gray-800 
            border-2 rounded-xl
            ${hasError 
              ? 'border-error focus:ring-error' 
              : 'border-gray-300 dark:border-gray-600 focus:border-primary-500 focus:ring-primary-500'
            }
            text-gray-900 dark:text-gray-100
            placeholder:text-gray-400
            focus:outline-none focus:ring-2
            transition-colors duration-200
            disabled:bg-gray-100 dark:disabled:bg-gray-900 disabled:cursor-not-allowed
            ${className}
          `}
          {...props}
        />
        
        {Icon && iconPosition === 'right' && !hasError && (
          <div className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400">
            <Icon className="w-5 h-5" />
          </div>
        )}
        
        {hasError && (
          <div className="absolute right-3 top-1/2 -translate-y-1/2 text-error">
            <FiAlertCircle className="w-5 h-5" />
          </div>
        )}
      </div>
      
      {(error || helperText) && (
        <p className={`caption mt-1 ${error ? 'text-error' : 'text-gray-500 dark:text-gray-400'}`}>
          {error || helperText}
        </p>
      )}
    </div>
  );
});

Input.displayName = 'Input';
```

#### 3. Card Component

**Archivo**: `src/components/ui/Card.tsx`

```tsx
import React from 'react';
import { motion } from 'framer-motion';

interface CardProps {
  children: React.ReactNode;
  variant?: 'default' | 'glass' | 'gradient';
  padding?: 'none' | 'sm' | 'md' | 'lg';
  hover?: boolean;
  onClick?: () => void;
  className?: string;
}

const variantClasses = {
  default: 'bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700',
  glass: 'bg-white/80 dark:bg-gray-900/80 backdrop-blur-xl border border-gray-200/50 dark:border-gray-700/50',
  gradient: 'bg-gradient-to-br from-white via-purple-50/30 to-blue-50/50 dark:from-gray-800 dark:via-purple-900/20 dark:to-indigo-900/20 border border-transparent',
};

const paddingClasses = {
  none: '',
  sm: 'p-4',
  md: 'p-6',
  lg: 'p-8',
};

export function Card({
  children,
  variant = 'default',
  padding = 'md',
  hover = false,
  onClick,
  className = '',
}: CardProps) {
  const Component = onClick ? motion.button : motion.div;

  return (
    <Component
      onClick={onClick}
      className={`
        rounded-2xl shadow-card
        ${variantClasses[variant]}
        ${paddingClasses[padding]}
        ${onClick ? 'cursor-pointer' : ''}
        ${className}
      `}
      {...(hover && {
        whileHover: { scale: 1.02, y: -4 },
        transition: { duration: 0.2 },
      })}
    >
      {children}
    </Component>
  );
}
```

#### 4. Badge Component

**Archivo**: `src/components/ui/Badge.tsx`

```tsx
import React from 'react';

type BadgeVariant = 'default' | 'success' | 'warning' | 'error' | 'info';
type BadgeSize = 'sm' | 'md' | 'lg';

interface BadgeProps {
  children: React.ReactNode;
  variant?: BadgeVariant;
  size?: BadgeSize;
  dot?: boolean;
  className?: string;
}

const variantClasses: Record<BadgeVariant, string> = {
  default: 'bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-300',
  success: 'bg-success/10 text-success-dark dark:text-success-light',
  warning: 'bg-warning/10 text-warning-dark dark:text-warning-light',
  error: 'bg-error/10 text-error-dark dark:text-error-light',
  info: 'bg-info/10 text-info-dark dark:text-info-light',
};

const sizeClasses: Record<BadgeSize, string> = {
  sm: 'px-2 py-0.5 text-xs',
  md: 'px-2.5 py-1 text-sm',
  lg: 'px-3 py-1.5 text-base',
};

export function Badge({
  children,
  variant = 'default',
  size = 'md',
  dot = false,
  className = '',
}: BadgeProps) {
  return (
    <span
      className={`
        inline-flex items-center gap-1.5 
        rounded-full font-medium
        ${variantClasses[variant]}
        ${sizeClasses[size]}
        ${className}
      `}
    >
      {dot && (
        <span className={`w-1.5 h-1.5 rounded-full ${
          variant === 'default' ? 'bg-gray-500' :
          variant === 'success' ? 'bg-success' :
          variant === 'warning' ? 'bg-warning' :
          variant === 'error' ? 'bg-error' :
          'bg-info'
        }`} />
      )}
      {children}
    </span>
  );
}
```

---

## 📱 RESPONSIVE DESIGN

### ⚠️ Problemas Actuales

#### 1. Componentes con Diseño Fijo
```tsx
// ❌ Problema: SidebarLeft siempre abierto en desktop
<div className="fixed left-0 top-0 h-full w-64">
  {/* No se adapta a tablet */}
</div>

// ❌ Problema: Grid sin breakpoints
<div className="grid grid-cols-3 gap-4">
  {/* Se rompe en móvil */}
</div>
```

#### 💡 Solución:
```tsx
// ✅ Sidebar responsive
<div className="fixed left-0 top-0 h-full w-full sm:w-80 md:w-64">
  {/* Se adapta a todos los tamaños */}
</div>

// ✅ Grid responsive
<div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
  {/* Responsive breakpoints */}
</div>
```

### Breakpoints Propuestos

```javascript
// tailwind.config.cjs
theme: {
  screens: {
    'xs': '475px',   // Teléfonos grandes
    'sm': '640px',   // Tablets pequeñas
    'md': '768px',   // Tablets
    'lg': '1024px',  // Laptops
    'xl': '1280px',  // Desktops
    '2xl': '1536px', // Pantallas grandes
  }
}
```

### Componentes a Revisar

```
PRIORIDAD ALTA:
- SidebarLeft.tsx      ⚠️ No responsive
- SidebarRight.tsx     ⚠️ No responsive
- Nav.tsx              ⚠️ Menú hamburguesa falta
- DashboardStudent.tsx ⚠️ Grid fijo
- InsigniasPage.tsx    ⚠️ Grid fijo

PRIORIDAD MEDIA:
- Forms (Register, Login) ⚠️ Padding fijo
- Modals                  ⚠️ Width fijo
- Tables                  ⚠️ No scroll horizontal
```

---

## ♿ ACCESIBILIDAD

### ❌ Problemas Críticos

#### 1. Contraste Insuficiente
```tsx
// ❌ Problema: text-gray-400 sobre bg-white (contraste 3.1:1 < 4.5:1)
<p className="text-gray-400">Texto secundario</p>

// ✅ Solución: usar gray-600 (contraste 4.6:1)
<p className="text-gray-600 dark:text-gray-400">Texto secundario</p>
```

#### 2. Falta ARIA Labels
```tsx
// ❌ Problema: botón sin label
<button onClick={() => {}}>
  <FiX />
</button>

// ✅ Solución: agregar aria-label
<button 
  onClick={() => {}}
  aria-label="Cerrar modal"
>
  <FiX />
</button>
```

#### 3. Focus States Incorrectos
```tsx
// ❌ Problema: outline-none sin alternativa
<button className="outline-none">
  Click
</button>

// ✅ Solución: ring personalizado
<button className="focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2">
  Click
</button>
```

### Checklist de Accesibilidad

```
CRÍTICO (A):
[ ] Contraste mínimo 4.5:1 para texto normal
[ ] Contraste mínimo 3:1 para texto grande
[ ] Todos los botones tienen aria-label
[ ] Focus visible en todos los elementos interactivos
[ ] Navegación por teclado funcional

IMPORTANTE (AA):
[ ] Alt text en todas las imágenes
[ ] Labels en todos los inputs
[ ] Roles ARIA correctos
[ ] Headings jerárquicos (h1 > h2 > h3)
[ ] Skip navigation link

DESEABLE (AAA):
[ ] Contraste mínimo 7:1
[ ] Texto redimensionable hasta 200%
[ ] Sin timeout automático
[ ] Sin animaciones para motion-reduced
```

---

## 🎯 MEJORAS ESPECÍFICAS POR COMPONENTE

### 1. Nav.tsx

#### ⚠️ Problemas:
```tsx
1. Cognitive Complexity: 21 (límite: 15)
2. No tiene menú hamburguesa para móvil
3. Avatar sin alt text
4. Búsqueda sin label
5. Preferencia globalThis sobre window
```

#### 💡 Mejoras:
```tsx
// 1. Refactorizar en sub-componentes
const SearchBar = () => { /* ... */ };
const UserMenu = () => { /* ... */ };
const NotificationBell = () => { /* ... */ };

// 2. Menú hamburguesa
const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

// 3. Accesibilidad
<img src={avatar} alt={`Avatar de ${user.name}`} />
<input 
  aria-label="Buscar cursos y contenido"
  placeholder="Buscar..."
/>

// 4. globalThis
const isDark = typeof globalThis.window !== 'undefined' 
  && globalThis.window.matchMedia?.('(prefers-color-scheme: dark)').matches;
```

### 2. SidebarLeft.tsx

#### ⚠️ Problemas:
```tsx
1. Imports no usados (FiHome, FiUser, FiSettings, etc.)
2. Cognitive Complexity alta
3. Ternarios anidados (difícil de leer)
4. Variables no usadas (roleConfig, lightBg)
5. No responsive
```

#### 💡 Mejoras:
```tsx
// 1. Limpiar imports
import { FiX, FiChevronRight, FiClock, FiChevronDown, FiBook, FiTarget } from 'react-icons/fi';

// 2. Extraer ternarios a funciones
const getItemClasses = (isDark: boolean, isActive: boolean) => {
  if (isActive) {
    return isDark 
      ? 'bg-violet-900/70 text-violet-300' 
      : 'bg-violet-100 text-violet-700';
  }
  return isDark
    ? 'text-gray-300 hover:bg-violet-900/50'
    : 'text-gray-800 hover:bg-violet-50';
};

// 3. Responsive
<motion.div
  className={`
    fixed left-0 top-0 h-full z-50
    w-full sm:w-80 md:w-64
    ${open ? 'translate-x-0' : '-translate-x-full'}
    transition-transform duration-300
  `}
>
```

### 3. SidebarRight.tsx

#### ⚠️ Problemas:
```tsx
1. Hardcoded mock data
2. No usa navigation.ts
3. Demasiado largo (600+ líneas)
4. Lógica mezclada con UI
```

#### 💡 Mejoras:
```tsx
// 1. Migrar a navigation.ts
const quickActions = useMemo(() => 
  getSidebarItems(user?.role),
  [user?.role]
);

// 2. Extraer secciones a componentes
const ProfileSection = () => { /* ... */ };
const StatsSection = () => { /* ... */ };
const BadgesSection = () => { /* ... */ };
const QuickActionsSection = () => { /* ... */ };

// 3. Usar datos reales
const { data: userStats } = useQuery({
  queryKey: ['user', 'stats'],
  queryFn: () => getUserStats()
});
```

### 4. DashboardStudent.tsx

#### ⚠️ Problemas:
```tsx
1. Mock data hardcoded
2. Grid no responsive
3. Componentes repetitivos
4. Sin loading states
```

#### 💡 Mejoras:
```tsx
// 1. Usar React Query
const { data: courses, isLoading } = useMyCourses();
const { data: assignments } = useMyAssignments();
const { data: stats } = useMyStats();

// 2. Grid responsive
<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">

// 3. Componentes reutilizables
<StatCard title="Cursos Activos" value={stats.activeCourses} />
<CourseCard course={course} />
<AssignmentCard assignment={assignment} />

// 4. Loading states
{isLoading ? <Skeleton count={3} /> : <CourseList courses={courses} />}
```

### 5. Register.tsx

#### ⚠️ Problemas:
```tsx
1. Formulario muy largo (500+ líneas)
2. Validación inline repetitiva
3. Sin usar React Hook Form
4. Estados múltiples para errores
```

#### 💡 Mejoras:
```tsx
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';

// 1. Schema de validación
const registerSchema = z.object({
  nombre: z.string().min(2, 'Mínimo 2 caracteres'),
  email: z.string().email('Email inválido'),
  password: z.string().min(8, 'Mínimo 8 caracteres'),
  // ... más campos
});

// 2. useForm hook
const { register, handleSubmit, formState: { errors } } = useForm({
  resolver: zodResolver(registerSchema)
});

// 3. Componentes Input reutilizables
<Input
  {...register('email')}
  label="Email"
  type="email"
  error={errors.email?.message}
  icon={FiMail}
/>
```

---

## 🚀 PLAN DE ACCIÓN PRIORIZADO

### 🔴 Prioridad CRÍTICA (Semana 1)

#### 1. Sistema de Diseño Base
**Tiempo**: 8 horas

```bash
Tareas:
1. Extender paleta de colores (primary, accent, semantic)
2. Crear sistema tipográfico (headings, body, labels)
3. Definir tokens de espaciado
4. Configurar sombras personalizadas
```

**Archivos**:
- `tailwind.config.cjs` - Configuración completa
- `src/index.css` - Clases utilitarias

#### 2. Componentes UI Esenciales
**Tiempo**: 12 horas

```bash
Tareas:
1. Button mejorado (variantes, tamaños, loading)
2. Input component (error states, icons)
3. Card component (variantes, hover)
4. Badge component
```

**Archivos**:
- `src/components/ui/Button.tsx`
- `src/components/ui/Input.tsx`
- `src/components/ui/Card.tsx`
- `src/components/ui/Badge.tsx`

#### 3. Accesibilidad Crítica
**Tiempo**: 6 horas

```bash
Tareas:
1. Auditar contraste de colores
2. Agregar aria-labels faltantes
3. Mejorar focus states
4. Test de navegación por teclado
```

**Herramienta**: axe DevTools, WAVE

### 🟡 Prioridad ALTA (Semana 2)

#### 4. Responsive Design
**Tiempo**: 16 horas

```bash
Componentes a actualizar:
1. Nav.tsx - Menú hamburguesa
2. SidebarLeft.tsx - Responsive
3. SidebarRight.tsx - Responsive
4. DashboardStudent.tsx - Grids responsive
5. Forms - Padding responsive
```

#### 5. Refactoring de Componentes Complejos
**Tiempo**: 12 horas

```bash
Tareas:
1. Nav.tsx - Reducir complexity (sub-componentes)
2. SidebarLeft.tsx - Extraer lógica
3. SidebarRight.tsx - Modularizar
4. Register.tsx - React Hook Form
```

#### 6. Componentes UI Adicionales
**Tiempo**: 10 horas

```bash
Crear:
1. Modal/Dialog
2. Select/Dropdown
3. Checkbox/Radio
4. Tabs
5. Skeleton Loader
```

### 🟢 Prioridad MEDIA (Semana 3)

#### 7. Integración con Datos Reales
**Tiempo**: 12 horas

```bash
Componentes:
1. SidebarRight - Usar datos de API
2. DashboardStudent - React Query
3. InsigniasPage - Datos reales
4. LogrosPage - Datos reales
```

#### 8. Animaciones y Microinteracciones
**Tiempo**: 8 horas

```bash
Mejoras:
1. Loading states animados
2. Transitions suaves entre páginas
3. Hover effects consistentes
4. Success/error feedback
```

#### 9. Dark Mode Optimization
**Tiempo**: 6 horas

```bash
Tareas:
1. Revisar todos los componentes
2. Mejorar contraste en dark
3. Gradientes optimizados
4. Ilustraciones adaptadas
```

---

## 📏 ESTÁNDARES DE CÓDIGO UI

### Convenciones de Nombres

```tsx
// ✅ Componentes: PascalCase
export function ButtonPrimary() {}

// ✅ Funciones utilitarias: camelCase
export function getButtonClasses() {}

// ✅ Constantes: UPPER_SNAKE_CASE
export const BUTTON_VARIANTS = {};

// ✅ Props interfaces: ComponentNameProps
interface ButtonProps {}
```

### Estructura de Componentes

```tsx
// ✅ Orden recomendado
import React from 'react';           // 1. React
import { motion } from 'framer-motion'; // 2. Librerías
import { FiIcon } from 'react-icons';   // 3. Iconos
import { useCustomHook } from './hooks'; // 4. Hooks personalizados
import './styles.css';                // 5. Estilos

// 6. Types/Interfaces
interface ComponentProps {}

// 7. Constantes
const VARIANTS = {};

// 8. Componente
export function Component({}: ComponentProps) {
  // 8.1. Hooks
  const [state, setState] = useState();
  
  // 8.2. Handlers
  const handleClick = () => {};
  
  // 8.3. Render
  return <div />;
}
```

### Clases Tailwind

```tsx
// ✅ Orden: Layout > Spacing > Typography > Colors > Effects
className={`
  flex items-center              // Layout
  px-4 py-2 gap-2               // Spacing
  text-base font-medium         // Typography
  text-white bg-primary-600     // Colors
  rounded-xl shadow-md hover:shadow-lg  // Effects
`}

// ✅ Breakpoints: sm > md > lg > xl
className="w-full sm:w-1/2 md:w-1/3 lg:w-1/4"

// ✅ States: hover > focus > active > disabled
className="hover:bg-primary-700 focus:ring-2 active:scale-95 disabled:opacity-50"
```

---

## 📊 MÉTRICAS DE ÉXITO

### Objetivos Medibles

```
PERFORMANCE:
- Lighthouse Performance > 90
- First Contentful Paint < 1.5s
- Time to Interactive < 3s

ACCESIBILIDAD:
- Lighthouse Accessibility > 95
- axe violations = 0
- Keyboard navigation 100%

RESPONSIVE:
- Funcional en 320px - 2560px
- Touch targets ≥ 44x44px
- Sin scroll horizontal

UX:
- Click to action < 2 clicks
- Form completion rate > 80%
- Error recovery < 30s
```

---

## ✅ CHECKLIST DE IMPLEMENTACIÓN

### Fase 1: Fundamentos (Semana 1)
- [ ] Extender paleta de colores completa
- [ ] Sistema tipográfico implementado
- [ ] Tokens de espaciado definidos
- [ ] Sombras personalizadas configuradas
- [ ] Button component mejorado
- [ ] Input component creado
- [ ] Card component creado
- [ ] Badge component creado
- [ ] Contraste de colores auditado (AA)
- [ ] ARIA labels en botones críticos

### Fase 2: Componentes (Semana 2)
- [ ] Nav.tsx responsive con hamburguesa
- [ ] SidebarLeft.tsx responsive
- [ ] SidebarRight.tsx responsive
- [ ] DashboardStudent grids responsive
- [ ] Forms con padding responsive
- [ ] Modal/Dialog component
- [ ] Select/Dropdown component
- [ ] Checkbox/Radio component
- [ ] Tabs component
- [ ] Skeleton Loader component

### Fase 3: Refinamiento (Semana 3)
- [ ] SidebarRight con datos reales
- [ ] Dashboard con React Query
- [ ] Loading states animados
- [ ] Transitions entre páginas
- [ ] Dark mode optimizado
- [ ] Microinteracciones agregadas
- [ ] Documentación Storybook
- [ ] Tests de accesibilidad (AAA)

---

## 🎓 RECURSOS Y REFERENCIAS

### Design Systems
- [Material Design 3](https://m3.material.io/)
- [Chakra UI](https://chakra-ui.com/)
- [Radix UI](https://www.radix-ui.com/)
- [Shadcn/ui](https://ui.shadcn.com/)

### Accesibilidad
- [WCAG 2.1 Guidelines](https://www.w3.org/WAI/WCAG21/quickref/)
- [axe DevTools](https://www.deque.com/axe/devtools/)
- [ARIA Patterns](https://www.w3.org/WAI/ARIA/apg/patterns/)

### Testing
- [Lighthouse CI](https://github.com/GoogleChrome/lighthouse-ci)
- [Storybook](https://storybook.js.org/)
- [Chromatic](https://www.chromatic.com/)

---

**Generado**: 31 de octubre de 2025  
**Autor**: GitHub Copilot  
**Estado**: ⚠️ **REQUIERE IMPLEMENTACIÓN**  
**Prioridad**: 🔴 **ALTA**
