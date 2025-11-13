// Tipografía y estilos de texto para Acadify Mobile
export const typography = {
  // Headings
  h1: 'text-4xl font-bold leading-tight',
  h2: 'text-3xl font-bold leading-tight',
  h3: 'text-2xl font-semibold leading-snug',
  h4: 'text-xl font-semibold leading-snug',
  h5: 'text-lg font-semibold leading-normal',
  h6: 'text-base font-semibold leading-normal',
  
  // Body text
  bodyLarge: 'text-lg font-normal leading-relaxed',
  body: 'text-base font-normal leading-normal',
  bodySmall: 'text-sm font-normal leading-normal',
  
  // Special
  caption: 'text-xs font-normal leading-tight',
  overline: 'text-xs font-semibold uppercase tracking-wide',
  subtitle: 'text-base font-medium leading-normal',
  
  // Interactive
  button: 'text-base font-semibold leading-none',
  buttonSmall: 'text-sm font-semibold leading-none',
  link: 'text-base font-medium underline',
  
  // Code
  code: 'text-sm font-mono',
  
  // Labels
  label: 'text-sm font-medium leading-tight',
  helperText: 'text-xs font-normal leading-tight',
  errorText: 'text-xs font-medium leading-tight',
} as const;

export const fontWeights = {
  thin: '100',
  extralight: '200',
  light: '300',
  normal: '400',
  medium: '500',
  semibold: '600',
  bold: '700',
  extrabold: '800',
  black: '900',
} as const;

export const fontSize = {
  xs: 12,
  sm: 14,
  base: 16,
  lg: 18,
  xl: 20,
  '2xl': 24,
  '3xl': 30,
  '4xl': 36,
  '5xl': 48,
} as const;

export const lineHeight = {
  none: 1,
  tight: 1.25,
  snug: 1.375,
  normal: 1.5,
  relaxed: 1.625,
  loose: 2,
} as const;

export type TypographyVariant = keyof typeof typography;
