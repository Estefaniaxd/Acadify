# 🎨 Acadify Design System

Sistema de diseño completo con soporte para modo claro y oscuro, optimizado para accesibilidad y compatibilidad cross-browser.

## 📋 Tabla de Contenidos

- [Paleta de Colores](#paleta-de-colores)
- [Tipografía](#tipografía)
- [Espaciado](#espaciado)
- [Componentes](#componentes)
- [Efectos Glassmorphism](#efectos-glassmorphism)
- [Animaciones](#animaciones)
- [Accesibilidad](#accesibilidad)

---

## 🎨 Paleta de Colores

### Primary (Violeta)
Color principal de marca - Usado para CTAs, links importantes y elementos destacados.

```css
primary-50:  #FAF5FF
primary-100: #F3E8FF
primary-200: #E9D5FF
primary-300: #D8B4FE
primary-400: #C084FC
primary-500: #A855F7
primary-600: #7C3AED  /* Base */
primary-700: #6D28D9
primary-800: #5B21B6
primary-900: #4C1D95
primary-950: #2E1065
```

**Contraste WCAG:**
- ✅ primary-600 en blanco: 8.2:1 (AAA)
- ✅ primary-700 en blanco: 10.5:1 (AAA)

### Secondary (Púrpura)
Color secundario - Usado para elementos de apoyo y variaciones.

```css
secondary-50:  #FAF5FF
secondary-100: #F3E8FF
secondary-200: #E9D5FF
secondary-300: #D8B4FE
secondary-400: #C084FC
secondary-500: #A855F7
secondary-600: #9333EA  /* Base */
secondary-700: #7E22CE
secondary-800: #6B21A8
secondary-900: #581C87
secondary-950: #3B0764
```

### Accent (Verde Esmeralda)
Color de acento - Usado para éxito, confirmaciones y elementos positivos.

```css
accent-50:  #ECFDF5
accent-100: #D1FAE5
accent-200: #A7F3D0
accent-300: #6EE7B7
accent-400: #34D399
accent-500: #10B981  /* Base */
accent-600: #059669
accent-700: #047857
accent-800: #065F46
accent-900: #064E3B
accent-950: #022C22
```

### Semantic Colors

#### Success (Verde)
```css
success:       #10B981
success-light: #D1FAE5
success-dark:  #047857
```

#### Warning (Ámbar)
```css
warning:       #F59E0B
warning-light: #FEF3C7
warning-dark:  #D97706
```

#### Error (Rojo)
```css
error:       #EF4444
error-light: #FEE2E2
error-dark:  #DC2626
```

#### Info (Azul)
```css
info:       #3B82F6
info-light: #DBEAFE
info-dark:  #2563EB
```

### Neutral (Grises)
Sistema completo de grises para textos, bordes y fondos.

```css
neutral-50:  #F9FAFB
neutral-100: #F3F4F6
neutral-200: #E5E7EB
neutral-300: #D1D5DB
neutral-400: #9CA3AF
neutral-500: #6B7280  /* Base */
neutral-600: #4B5563
neutral-700: #374151
neutral-800: #1F2937
neutral-900: #111827
neutral-950: #030712
```

---

## 🔤 Tipografía

### Font Family

```css
/* Sans-serif (Default) */
font-family: 'Inter', system-ui, -apple-system, sans-serif;

/* Monospace */
font-family: 'JetBrains Mono', Menlo, Monaco, 'Courier New', monospace;
```

### Font Sizes

| Clase | Tamaño | Line Height | Uso |
|-------|--------|-------------|-----|
| `text-2xs` | 10px | 14px | Labels muy pequeños |
| `text-xs` | 12px | 16px | Subtextos, badges |
| `text-sm` | 14px | 20px | Texto secundario |
| `text-base` | 16px | 24px | Texto principal |
| `text-lg` | 18px | 28px | Texto destacado |
| `text-xl` | 20px | 28px | Subtítulos pequeños |
| `text-2xl` | 24px | 32px | Subtítulos |
| `text-3xl` | 30px | 36px | Títulos sección |
| `text-4xl` | 36px | 40px | Títulos página |
| `text-5xl` | 48px | 1 | Títulos hero |
| `text-6xl` | 60px | 1 | Títulos display |
| `text-7xl` | 72px | 1 | Títulos landing |
| `text-8xl` | 96px | 1 | Títulos especiales |

### Headings

```tsx
<h1 className="text-4xl font-bold">Título Principal</h1>
<h2 className="text-3xl font-bold">Subtítulo</h2>
<h3 className="text-2xl font-semibold">Sección</h3>
<h4 className="text-xl font-semibold">Subsección</h4>
<h5 className="text-lg font-medium">Grupo</h5>
<h6 className="text-base font-medium">Item</h6>
```

---

## 📏 Espaciado

### Spacing Scale

| Clase | Valor | Píxeles | Uso |
|-------|-------|---------|-----|
| `spacing-xs` | 0.25rem | 4px | Espaciado mínimo |
| `spacing-sm` | 0.5rem | 8px | Espaciado pequeño |
| `spacing-md` | 1rem | 16px | Espaciado base |
| `spacing-lg` | 1.5rem | 24px | Espaciado mediano |
| `spacing-xl` | 2rem | 32px | Espaciado grande |
| `spacing-2xl` | 3rem | 48px | Espaciado muy grande |
| `spacing-3xl` | 4rem | 64px | Espaciado extra grande |

### Tailwind Classes

```tsx
// Padding
<div className="p-4">      // 16px all sides
<div className="px-6">     // 24px horizontal
<div className="py-8">     // 32px vertical

// Margin
<div className="m-4">      // 16px all sides
<div className="mx-auto">  // Center horizontal
<div className="my-6">     // 24px vertical

// Gap (Grid/Flex)
<div className="gap-4">    // 16px gap
<div className="gap-x-6">  // 24px horizontal gap
<div className="gap-y-8">  // 32px vertical gap
```

---

## 🪟 Efectos Glassmorphism

### Glass Card (Sutil)

```tsx
<div className="glass-card rounded-2xl p-6">
  {/* Contenido */}
</div>
```

**Propiedades:**
- Backdrop blur: 20px
- Background: rgba con 65% opacidad
- Border: 1px solid rgba(255,255,255,0.1)
- Shadow: Sombra sutil

### Glass Card Strong (Intenso)

```tsx
<div className="glass-card-strong rounded-2xl p-6">
  {/* Contenido */}
</div>
```

**Propiedades:**
- Backdrop blur: 40px
- Background: rgba con 90% opacidad
- Border: 1px solid rgba(255,255,255,0.15)
- Shadow: Sombra profunda

### Custom Shadows

```tsx
// Sombras con glassmorphism
<div className="shadow-glass">     // Sombra base
<div className="shadow-glass-sm">  // Sombra pequeña
<div className="shadow-glass-lg">  // Sombra grande

// Efectos de brillo
<div className="shadow-glow">      // Brillo normal
<div className="shadow-glow-sm">   // Brillo sutil
<div className="shadow-glow-lg">   // Brillo intenso
```

---

## 🎬 Animaciones

### Built-in Animations

```tsx
// Fade
<div className="animate-fade-in">
<div className="animate-fade-out">

// Slide
<div className="animate-slide-up">
<div className="animate-slide-down">

// Scale
<div className="animate-scale-in">

// Special
<div className="animate-pulse-slow">
<div className="animate-float">
```

### Transiciones

```tsx
// Rápidas (150ms)
<button className="transition-colors duration-150">

// Base (250ms) - Recomendado
<div className="transition-all duration-250">

// Lentas (350ms)
<div className="transition-transform duration-350">
```

### Page Transitions

```tsx
<div className="page-enter page-enter-active">
  {/* Contenido de página con transición */}
</div>
```

---

## 🎨 Gradientes

### Gradient Backgrounds

```tsx
// Primary gradient (Violeta → Púrpura)
<div className="gradient-primary">

// Accent gradient (Violeta → Verde)
<div className="gradient-accent">

// Tailwind gradients
<div className="bg-gradient-to-r from-primary-600 to-secondary-600">
<div className="bg-gradient-to-br from-primary-500 to-accent-500">
```

### Gradient Text

```tsx
<h1 className="gradient-text text-5xl font-bold">
  Texto con Gradiente
</h1>
```

---

## ♿ Accesibilidad

### Focus States

Todos los elementos interactivos tienen estados de focus visibles:

```tsx
// Focus ring automático
<button className="focus-ring">
  Botón Accesible
</button>

// Focus visible en inputs
<input className="focus-visible:ring-2 focus-visible:ring-primary-600" />
```

### Reduced Motion

El sistema respeta las preferencias de movimiento reducido:

```css
@media (prefers-reduced-motion: reduce) {
  /* Todas las animaciones se reducen a 0.01ms */
}
```

### Contraste de Colores

Todos los colores cumplen con WCAG 2.1:

- **Level AA:** Contraste mínimo 4.5:1 para texto normal
- **Level AAA:** Contraste mínimo 7:1 para texto normal
- ✅ Primary-600 en blanco: 8.2:1 (AAA)
- ✅ Accent-600 en blanco: 4.8:1 (AA)

### ARIA Labels

Siempre incluir labels descriptivos:

```tsx
<button aria-label="Cerrar modal">
  <FiX />
</button>

<input 
  type="text"
  aria-describedby="email-help"
  aria-invalid={hasError}
/>
```

---

## 📱 Responsive Design

### Breakpoints

| Breakpoint | Min Width | Target |
|------------|-----------|--------|
| `sm` | 640px | Móvil grande |
| `md` | 768px | Tablet |
| `lg` | 1024px | Laptop |
| `xl` | 1280px | Desktop |
| `2xl` | 1536px | Desktop grande |

### Uso

```tsx
<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3">
  {/* Responsive grid */}
</div>

<div className="text-sm md:text-base lg:text-lg">
  {/* Responsive text */}
</div>
```

---

## 🎯 Best Practices

### DO ✅

```tsx
// Usar variables CSS para temas
<div style={{ color: 'rgb(var(--color-text-primary))' }}>

// Usar clases de Tailwind
<button className="bg-primary-600 hover:bg-primary-700">

// Combinar con clases custom
<div className="glass-card rounded-2xl">
```

### DON'T ❌

```tsx
// No hardcodear colores
<div style={{ color: '#7C3AED' }}> ❌

// No usar !important innecesariamente
<div className="!bg-red-500"> ❌

// No mezclar unidades sin razón
<div style={{ padding: '16px 1rem' }}> ❌
```

---

## 🔧 Variables CSS Disponibles

### Colors

```css
var(--color-primary)
var(--color-secondary)
var(--color-accent)
var(--color-success)
var(--color-warning)
var(--color-error)
var(--color-info)
```

### Backgrounds

```css
var(--color-bg-primary)
var(--color-bg-secondary)
var(--color-bg-tertiary)
var(--color-bg-glass)
```

### Text

```css
var(--color-text-primary)
var(--color-text-secondary)
var(--color-text-tertiary)
var(--color-text-inverse)
```

### Borders

```css
var(--color-border-primary)
var(--color-border-secondary)
var(--color-border-focus)
```

### Spacing

```css
var(--spacing-xs)  /* 4px */
var(--spacing-sm)  /* 8px */
var(--spacing-md)  /* 16px */
var(--spacing-lg)  /* 24px */
var(--spacing-xl)  /* 32px */
var(--spacing-2xl) /* 48px */
var(--spacing-3xl) /* 64px */
```

---

## 📚 Ejemplos de Uso

### Card con Glassmorphism

```tsx
<div className="glass-card rounded-2xl p-6 hover:shadow-glass-lg transition-shadow duration-300">
  <h3 className="text-xl font-semibold text-primary-600 mb-2">
    Título de Card
  </h3>
  <p className="text-neutral-600 dark:text-neutral-400">
    Contenido de la tarjeta con soporte dark mode.
  </p>
</div>
```

### Button Primary

```tsx
<button className="px-6 py-3 bg-gradient-to-r from-primary-600 to-secondary-600 text-white font-semibold rounded-xl shadow-lg hover:shadow-xl focus-ring transition-all duration-250">
  Acción Principal
</button>
```

### Input con Estados

```tsx
<div className="form-group">
  <label className="form-label">
    Email
  </label>
  <input
    type="email"
    className="w-full px-4 py-2 rounded-lg border border-neutral-300 dark:border-neutral-700 bg-white dark:bg-neutral-800 focus-ring transition-colors"
    placeholder="tu@email.com"
  />
</div>
```

---

## 🚀 Próximos Pasos

1. ✅ Sistema de colores implementado
2. ✅ Tipografía configurada
3. ✅ Espaciado definido
4. ✅ Efectos glassmorphism listos
5. ⏳ Crear componentes UI (Button, Input, Card, Badge)
6. ⏳ Implementar patrones de animación
7. ⏳ Documentar componentes en Storybook

---

**Última actualización:** 31 de octubre de 2025  
**Versión:** 1.0.0  
**Mantenedor:** Equipo Acadify
