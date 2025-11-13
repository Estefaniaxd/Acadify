import { forwardRef, HTMLAttributes } from 'react';
import { motion, HTMLMotionProps } from 'framer-motion';

/* ==========================================================================
   🎴 CARD COMPONENT
   Tarjeta versátil con variantes glass y sombras personalizadas
   ========================================================================== */

/**
 * Variantes de Card disponibles
 */
export type CardVariant =
  | 'default'    // Card con fondo sólido
  | 'glass'      // Card con efecto glassmorphism
  | 'elevated'   // Card con sombra elevada
  | 'outlined'   // Card solo con borde
  | 'gradient';  // Card con gradiente

/**
 * Padding de Card disponible
 */
export type CardPadding =
  | 'none'   // Sin padding
  | 'sm'     // 12px
  | 'md'     // 16px (default)
  | 'lg'     // 24px
  | 'xl';    // 32px

/**
 * Props del componente Card
 */
export interface CardProps extends Omit<HTMLAttributes<HTMLDivElement>, 'className'> {
  /** Variante visual de la card */
  variant?: CardVariant;
  
  /** Padding de la card */
  padding?: CardPadding;
  
  /** Efecto hover */
  hoverable?: boolean;
  
  /** Clases CSS adicionales */
  className?: string;
  
  /** Habilitar animaciones */
  animated?: boolean;
  
  /** onClick handler - hace la card clickeable */
  onClick?: () => void;
  
  /** Children */
  children?: React.ReactNode;
}

/**
 * Obtiene las clases base de la card
 */
const getBaseClasses = (): string => {
  return [
    'rounded-2xl',
    'transition-all duration-300',
  ].join(' ');
};

/**
 * Obtiene las clases según la variante
 */
const getVariantClasses = (variant: CardVariant): string => {
  const variants: Record<CardVariant, string> = {
    default: [
      'bg-white dark:bg-neutral-900',
      'border border-neutral-200 dark:border-neutral-800',
      'shadow-sm',
    ].join(' '),
    
    glass: [
      'glass-card',
      'border border-white/10',
    ].join(' '),
    
    elevated: [
      'bg-white dark:bg-neutral-900',
      'shadow-lg',
    ].join(' '),
    
    outlined: [
      'bg-transparent',
      'border-2 border-neutral-300 dark:border-neutral-700',
    ].join(' '),
    
    gradient: [
      'gradient-primary',
      'text-white',
      'border-none',
    ].join(' '),
  };
  
  return variants[variant];
};

/**
 * Obtiene las clases de padding
 */
const getPaddingClasses = (padding: CardPadding): string => {
  const paddings: Record<CardPadding, string> = {
    none: '',
    sm: 'p-3',
    md: 'p-4',
    lg: 'p-6',
    xl: 'p-8',
  };
  
  return paddings[padding];
};

/**
 * Obtiene las clases de hover
 */
const getHoverClasses = (hoverable: boolean, variant: CardVariant): string => {
  if (!hoverable) return '';
  
  const hoverEffects: Record<CardVariant, string> = {
    default: 'hover:shadow-md hover:-translate-y-0.5 cursor-pointer',
    glass: 'hover:shadow-glass-lg hover:-translate-y-0.5 cursor-pointer',
    elevated: 'hover:shadow-xl hover:-translate-y-1 cursor-pointer',
    outlined: 'hover:border-primary-600 dark:hover:border-primary-400 cursor-pointer',
    gradient: 'hover:shadow-xl hover:-translate-y-0.5 cursor-pointer',
  };
  
  return hoverEffects[variant];
};

/**
 * Card Component
 * 
 * Tarjeta con soporte para:
 * - 5 variantes visuales
 * - 5 tamaños de padding
 * - Efectos hover opcionales
 * - Animaciones de entrada
 * - Clickeable con onClick
 * 
 * @example
 * ```tsx
 * // Card básica
 * <Card>
 *   <h3>Título</h3>
 *   <p>Contenido</p>
 * </Card>
 * 
 * // Card glassmorphism con hover
 * <Card variant="glass" hoverable>
 *   Contenido con efecto glass
 * </Card>
 * 
 * // Card clickeable
 * <Card hoverable onClick={() => console.log('clicked')}>
 *   Click me
 * </Card>
 * ```
 */
export const Card = forwardRef<HTMLDivElement, CardProps>(
  (
    {
      variant = 'default',
      padding = 'md',
      hoverable = false,
      className = '',
      animated = false,
      onClick,
      children,
      ...props
    },
    ref
  ) => {
    // Construir clases CSS
    const classes = [
      getBaseClasses(),
      getVariantClasses(variant),
      getPaddingClasses(padding),
      getHoverClasses(hoverable || !!onClick, variant),
      className,
    ]
      .filter(Boolean)
      .join(' ');
    
    // Props comunes
    const cardProps = {
      ref,
      className: classes,
      onClick,
      role: onClick ? 'button' : undefined,
      tabIndex: onClick ? 0 : undefined,
      onKeyDown: onClick 
        ? (e: React.KeyboardEvent) => {
            if (e.key === 'Enter' || e.key === ' ') {
              e.preventDefault();
              onClick();
            }
          }
        : undefined,
      ...props,
    };
    
    // Renderizar con animación opcional
    if (animated) {
      return (
        <motion.div
          {...(cardProps as HTMLMotionProps<'div'>)}
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3 }}
        >
          {children}
        </motion.div>
      );
    }
    
    return <div {...cardProps}>{children}</div>;
  }
);

Card.displayName = 'Card';

/**
 * CardHeader - Encabezado de card
 */
export interface CardHeaderProps extends HTMLAttributes<HTMLDivElement> {
  className?: string;
  children?: React.ReactNode;
}

export const CardHeader = forwardRef<HTMLDivElement, CardHeaderProps>(
  ({ className = '', children, ...props }, ref) => {
    return (
      <div
        ref={ref}
        className={`mb-4 ${className}`}
        {...props}
      >
        {children}
      </div>
    );
  }
);

CardHeader.displayName = 'CardHeader';

/**
 * CardTitle - Título de card
 */
export interface CardTitleProps extends HTMLAttributes<HTMLHeadingElement> {
  className?: string;
  children?: React.ReactNode;
}

export const CardTitle = forwardRef<HTMLHeadingElement, CardTitleProps>(
  ({ className = '', children, ...props }, ref) => {
    return (
      <h3
        ref={ref}
        className={`text-xl font-semibold text-neutral-900 dark:text-neutral-100 ${className}`}
        {...props}
      >
        {children}
      </h3>
    );
  }
);

CardTitle.displayName = 'CardTitle';

/**
 * CardDescription - Descripción de card
 */
export interface CardDescriptionProps extends HTMLAttributes<HTMLParagraphElement> {
  className?: string;
  children?: React.ReactNode;
}

export const CardDescription = forwardRef<HTMLParagraphElement, CardDescriptionProps>(
  ({ className = '', children, ...props }, ref) => {
    return (
      <p
        ref={ref}
        className={`text-sm text-neutral-600 dark:text-neutral-400 ${className}`}
        {...props}
      >
        {children}
      </p>
    );
  }
);

CardDescription.displayName = 'CardDescription';

/**
 * CardContent - Contenido principal de card
 */
export interface CardContentProps extends HTMLAttributes<HTMLDivElement> {
  className?: string;
  children?: React.ReactNode;
}

export const CardContent = forwardRef<HTMLDivElement, CardContentProps>(
  ({ className = '', children, ...props }, ref) => {
    return (
      <div
        ref={ref}
        className={className}
        {...props}
      >
        {children}
      </div>
    );
  }
);

CardContent.displayName = 'CardContent';

/**
 * CardFooter - Footer de card
 */
export interface CardFooterProps extends HTMLAttributes<HTMLDivElement> {
  className?: string;
  children?: React.ReactNode;
}

export const CardFooter = forwardRef<HTMLDivElement, CardFooterProps>(
  ({ className = '', children, ...props }, ref) => {
    return (
      <div
        ref={ref}
        className={`mt-4 flex items-center gap-2 ${className}`}
        {...props}
      >
        {children}
      </div>
    );
  }
);

CardFooter.displayName = 'CardFooter';

export default Card;
