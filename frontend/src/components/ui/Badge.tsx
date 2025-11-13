import { forwardRef, HTMLAttributes } from 'react';
import { IconType } from 'react-icons';

/* ==========================================================================
   🏷️ BADGE COMPONENT
   Badge versátil para etiquetas, estados y notificaciones
   ========================================================================== */

/**
 * Variantes de Badge disponibles
 */
export type BadgeVariant =
  | 'default'    // Gris neutro
  | 'primary'    // Violeta
  | 'secondary'  // Púrpura
  | 'success'    // Verde
  | 'warning'    // Ámbar
  | 'danger'     // Rojo
  | 'info';      // Azul

/**
 * Tamaños de Badge disponibles
 */
export type BadgeSize =
  | 'sm'    // Pequeño
  | 'md'    // Mediano (default)
  | 'lg';   // Grande

/**
 * Props del componente Badge
 */
export interface BadgeProps extends Omit<HTMLAttributes<HTMLSpanElement>, 'className'> {
  /** Variante visual del badge */
  variant?: BadgeVariant;
  
  /** Tamaño del badge */
  size?: BadgeSize;
  
  /** Icono a la izquierda */
  leftIcon?: IconType;
  
  /** Icono a la derecha */
  rightIcon?: IconType;
  
  /** Mostrar punto indicador */
  dot?: boolean;
  
  /** Pill shape (más redondeado) */
  pill?: boolean;
  
  /** Versión outline (solo borde) */
  outline?: boolean;
  
  /** Clases CSS adicionales */
  className?: string;
  
  /** Children */
  children?: React.ReactNode;
}

/**
 * Obtiene las clases base del badge
 */
const getBaseClasses = (pill: boolean): string => {
  return [
    'inline-flex items-center gap-1.5',
    'font-medium',
    'transition-colors duration-200',
    pill ? 'rounded-full' : 'rounded-lg',
  ].join(' ');
};

/**
 * Obtiene las clases según la variante (sólido)
 */
const getVariantClasses = (variant: BadgeVariant): string => {
  const variants: Record<BadgeVariant, string> = {
    default: [
      'bg-neutral-100 dark:bg-neutral-800',
      'text-neutral-700 dark:text-neutral-300',
    ].join(' '),
    
    primary: [
      'bg-primary-100 dark:bg-primary-950',
      'text-primary-700 dark:text-primary-300',
    ].join(' '),
    
    secondary: [
      'bg-secondary-100 dark:bg-secondary-950',
      'text-secondary-700 dark:text-secondary-300',
    ].join(' '),
    
    success: [
      'bg-success-light dark:bg-success/20',
      'text-success-dark dark:text-success',
    ].join(' '),
    
    warning: [
      'bg-warning-light dark:bg-warning/20',
      'text-warning-dark dark:text-warning',
    ].join(' '),
    
    danger: [
      'bg-error-light dark:bg-error/20',
      'text-error-dark dark:text-error',
    ].join(' '),
    
    info: [
      'bg-info-light dark:bg-info/20',
      'text-info-dark dark:text-info',
    ].join(' '),
  };
  
  return variants[variant];
};

/**
 * Obtiene las clases según la variante (outline)
 */
const getOutlineClasses = (variant: BadgeVariant): string => {
  const variants: Record<BadgeVariant, string> = {
    default: [
      'bg-transparent',
      'border-2 border-neutral-300 dark:border-neutral-700',
      'text-neutral-700 dark:text-neutral-300',
    ].join(' '),
    
    primary: [
      'bg-transparent',
      'border-2 border-primary-600 dark:border-primary-400',
      'text-primary-700 dark:text-primary-300',
    ].join(' '),
    
    secondary: [
      'bg-transparent',
      'border-2 border-secondary-600 dark:border-secondary-400',
      'text-secondary-700 dark:text-secondary-300',
    ].join(' '),
    
    success: [
      'bg-transparent',
      'border-2 border-success dark:border-success-light',
      'text-success-dark dark:text-success',
    ].join(' '),
    
    warning: [
      'bg-transparent',
      'border-2 border-warning dark:border-warning-light',
      'text-warning-dark dark:text-warning',
    ].join(' '),
    
    danger: [
      'bg-transparent',
      'border-2 border-error dark:border-error-light',
      'text-error-dark dark:text-error',
    ].join(' '),
    
    info: [
      'bg-transparent',
      'border-2 border-info dark:border-info-light',
      'text-info-dark dark:text-info',
    ].join(' '),
  };
  
  return variants[variant];
};

/**
 * Obtiene las clases según el tamaño
 */
const getSizeClasses = (size: BadgeSize): string => {
  const sizes: Record<BadgeSize, string> = {
    sm: 'px-2 py-0.5 text-xs',
    md: 'px-2.5 py-1 text-sm',
    lg: 'px-3 py-1.5 text-base',
  };
  
  return sizes[size];
};

/**
 * Obtiene el color del dot según la variante
 */
const getDotColor = (variant: BadgeVariant): string => {
  const colors: Record<BadgeVariant, string> = {
    default: 'bg-neutral-500',
    primary: 'bg-primary-600',
    secondary: 'bg-secondary-600',
    success: 'bg-success',
    warning: 'bg-warning',
    danger: 'bg-error',
    info: 'bg-info',
  };
  
  return colors[variant];
};

/**
 * Badge Component
 * 
 * Badge con soporte para:
 * - 7 variantes de color
 * - 3 tamaños
 * - Versión solid y outline
 * - Iconos izquierda/derecha
 * - Punto indicador
 * - Forma pill
 * 
 * @example
 * ```tsx
 * // Badge básico
 * <Badge>Nuevo</Badge>
 * 
 * // Con variante y tamaño
 * <Badge variant="success" size="lg">
 *   Completado
 * </Badge>
 * 
 * // Con icono y dot
 * <Badge variant="warning" dot leftIcon={FiAlertCircle}>
 *   Pendiente
 * </Badge>
 * 
 * // Outline pill
 * <Badge variant="primary" outline pill>
 *   Premium
 * </Badge>
 * ```
 */
export const Badge = forwardRef<HTMLSpanElement, BadgeProps>(
  (
    {
      variant = 'default',
      size = 'md',
      leftIcon: LeftIcon,
      rightIcon: RightIcon,
      dot = false,
      pill = false,
      outline = false,
      className = '',
      children,
      ...props
    },
    ref
  ) => {
    // Construir clases CSS
    const classes = [
      getBaseClasses(pill),
      outline ? getOutlineClasses(variant) : getVariantClasses(variant),
      getSizeClasses(size),
      className,
    ]
      .filter(Boolean)
      .join(' ');
    
    // Tamaño del dot
    const dotSize = size === 'sm' ? 'w-1.5 h-1.5' : size === 'lg' ? 'w-2.5 h-2.5' : 'w-2 h-2';
    
    // Tamaño del icono
    const iconSize = size === 'sm' ? 'text-xs' : size === 'lg' ? 'text-lg' : 'text-sm';
    
    return (
      <span ref={ref} className={classes} {...props}>
        {/* Dot indicador */}
        {dot && (
          <span 
            className={`${dotSize} ${getDotColor(variant)} rounded-full flex-shrink-0`}
            aria-hidden="true"
          />
        )}
        
        {/* Icono izquierdo */}
        {LeftIcon && (
          <LeftIcon className={iconSize} aria-hidden="true" />
        )}
        
        {/* Contenido */}
        {children && <span>{children}</span>}
        
        {/* Icono derecho */}
        {RightIcon && (
          <RightIcon className={iconSize} aria-hidden="true" />
        )}
      </span>
    );
  }
);

Badge.displayName = 'Badge';

/**
 * BadgeCounter - Badge para contadores numéricos
 * 
 * @example
 * ```tsx
 * <BadgeCounter count={5} />
 * <BadgeCounter count={99} max={99} />
 * ```
 */
export interface BadgeCounterProps extends Omit<HTMLAttributes<HTMLSpanElement>, 'children' | 'className'> {
  /** Número a mostrar */
  count: number;
  
  /** Máximo valor antes de mostrar "+" */
  max?: number;
  
  /** Variante del badge */
  variant?: BadgeVariant;
  
  /** Mostrar cuando count es 0 */
  showZero?: boolean;
  
  /** Clases CSS adicionales */
  className?: string;
}

export const BadgeCounter = forwardRef<HTMLSpanElement, BadgeCounterProps>(
  (
    {
      count,
      max = 99,
      variant = 'danger',
      showZero = false,
      className = '',
      ...props
    },
    ref
  ) => {
    // No mostrar si count es 0 y showZero es false
    if (count === 0 && !showZero) {
      return null;
    }
    
    // Formatear número
    const displayCount = count > max ? `${max}+` : count.toString();
    
    return (
      <Badge
        ref={ref}
        variant={variant}
        size="sm"
        pill
        className={`min-w-[1.25rem] justify-center px-1.5 ${className}`}
        {...props}
      >
        {displayCount}
      </Badge>
    );
  }
);

BadgeCounter.displayName = 'BadgeCounter';

/**
 * BadgeDot - Dot indicador simple sin texto
 * 
 * @example
 * ```tsx
 * <div className="relative">
 *   <button>Notificaciones</button>
 *   <BadgeDot variant="danger" />
 * </div>
 * ```
 */
export interface BadgeDotProps extends Omit<HTMLAttributes<HTMLSpanElement>, 'children' | 'className'> {
  /** Variante del dot */
  variant?: BadgeVariant;
  
  /** Tamaño del dot */
  size?: 'sm' | 'md' | 'lg';
  
  /** Animación de pulso */
  pulse?: boolean;
  
  /** Clases CSS adicionales */
  className?: string;
}

export const BadgeDot = forwardRef<HTMLSpanElement, BadgeDotProps>(
  (
    {
      variant = 'danger',
      size = 'md',
      pulse = false,
      className = '',
      ...props
    },
    ref
  ) => {
    const sizeClasses = {
      sm: 'w-2 h-2',
      md: 'w-2.5 h-2.5',
      lg: 'w-3 h-3',
    };
    
    return (
      <span
        ref={ref}
        className={`
          ${sizeClasses[size]}
          ${getDotColor(variant)}
          rounded-full
          flex-shrink-0
          ${pulse ? 'animate-pulse' : ''}
          ${className}
        `}
        role="status"
        aria-label="indicador de estado"
        {...props}
      />
    );
  }
);

BadgeDot.displayName = 'BadgeDot';

export default Badge;
