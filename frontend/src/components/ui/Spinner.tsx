import { HTMLAttributes } from 'react';
import { motion } from 'framer-motion';

/* ==========================================================================
   ⏳ SPINNER COMPONENT
   Spinner animado para estados de carga
   ========================================================================== */

export type SpinnerSize = 'xs' | 'sm' | 'md' | 'lg' | 'xl';
export type SpinnerVariant = 'primary' | 'secondary' | 'success' | 'warning' | 'danger' | 'white';

export interface SpinnerProps extends HTMLAttributes<HTMLDivElement> {
  /** Tamaño del spinner */
  size?: SpinnerSize;
  
  /** Variante de color */
  variant?: SpinnerVariant;
  
  /** Label accesible */
  label?: string;
  
  /** Mostrar label visualmente */
  showLabel?: boolean;
}

/**
 * Clases según el tamaño
 */
const getSizeClasses = (size: SpinnerSize): string => {
  const sizes = {
    xs: 'w-3 h-3',
    sm: 'w-4 h-4',
    md: 'w-6 h-6',
    lg: 'w-8 h-8',
    xl: 'w-12 h-12',
  };
  
  return sizes[size];
};

/**
 * Clases según la variante
 */
const getVariantClasses = (variant: SpinnerVariant): string => {
  const variants = {
    primary: 'border-primary-600 dark:border-primary-500',
    secondary: 'border-secondary-600 dark:border-secondary-500',
    success: 'border-success dark:border-success',
    warning: 'border-warning dark:border-warning',
    danger: 'border-error dark:border-error',
    white: 'border-white',
  };
  
  return variants[variant];
};

/**
 * Spinner Component
 * 
 * Spinner animado para estados de carga con:
 * - 5 tamaños (xs a xl)
 * - 6 variantes de color
 * - Label accesible
 * - Animación suave
 * 
 * @example
 * ```tsx
 * // Básico
 * <Spinner />
 * 
 * // Con tamaño y color
 * <Spinner size="lg" variant="primary" />
 * 
 * // Con label visible
 * <Spinner
 *   size="xl"
 *   variant="success"
 *   label="Cargando datos..."
 *   showLabel
 * />
 * 
 * // En botón
 * <Button disabled>
 *   <Spinner size="sm" variant="white" />
 *   Guardando...
 * </Button>
 * ```
 */
export const Spinner: React.FC<SpinnerProps> = ({
  size = 'md',
  variant = 'primary',
  label = 'Cargando',
  showLabel = false,
  className = '',
  ...props
}) => {
  const sizeClasses = getSizeClasses(size);
  const variantClasses = getVariantClasses(variant);
  
  return (
    <div
      className={`inline-flex items-center gap-2 ${className}`}
      role="status"
      aria-label={label}
      {...props}
    >
      {/* Spinner circular */}
      <motion.div
        className={`
          ${sizeClasses}
          border-2
          ${variantClasses}
          border-t-transparent
          rounded-full
        `}
        animate={{ rotate: 360 }}
        transition={{
          duration: 0.8,
          repeat: Infinity,
          ease: 'linear',
        }}
        aria-hidden="true"
      />
      
      {/* Label */}
      {showLabel && (
        <span className="text-sm font-medium text-neutral-700 dark:text-neutral-300">
          {label}
        </span>
      )}
      
      {/* Label oculto para screen readers */}
      {!showLabel && <span className="sr-only">{label}</span>}
    </div>
  );
};

/**
 * SpinnerDots - Spinner de puntos animados
 */
export interface SpinnerDotsProps {
  size?: SpinnerSize;
  variant?: SpinnerVariant;
}

export const SpinnerDots: React.FC<SpinnerDotsProps> = ({
  size = 'md',
  variant = 'primary',
}) => {
  const dotSizes = {
    xs: 'w-1 h-1',
    sm: 'w-1.5 h-1.5',
    md: 'w-2 h-2',
    lg: 'w-2.5 h-2.5',
    xl: 'w-3 h-3',
  };
  
  const dotSize = dotSizes[size];
  const variantClasses = getVariantClasses(variant).replace('border-', 'bg-');
  
  return (
    <div className="inline-flex items-center gap-1" role="status" aria-label="Cargando">
      {[0, 1, 2].map((i) => (
        <motion.div
          key={i}
          className={`${dotSize} ${variantClasses} rounded-full`}
          animate={{
            scale: [1, 1.2, 1],
            opacity: [0.5, 1, 0.5],
          }}
          transition={{
            duration: 0.8,
            repeat: Infinity,
            delay: i * 0.15,
          }}
          aria-hidden="true"
        />
      ))}
      <span className="sr-only">Cargando</span>
    </div>
  );
};

/**
 * SpinnerPulse - Spinner de pulso
 */
export interface SpinnerPulseProps {
  size?: SpinnerSize;
  variant?: SpinnerVariant;
}

export const SpinnerPulse: React.FC<SpinnerPulseProps> = ({
  size = 'md',
  variant = 'primary',
}) => {
  const sizeClasses = getSizeClasses(size);
  const variantClasses = getVariantClasses(variant).replace('border-', 'bg-');
  
  return (
    <div className="relative inline-flex" role="status" aria-label="Cargando">
      {/* Círculo exterior pulsante */}
      <motion.div
        className={`${sizeClasses} ${variantClasses} rounded-full opacity-75`}
        animate={{
          scale: [1, 2],
          opacity: [0.75, 0],
        }}
        transition={{
          duration: 1,
          repeat: Infinity,
          ease: 'easeOut',
        }}
        aria-hidden="true"
      />
      
      {/* Círculo interior */}
      <div
        className={`${sizeClasses} ${variantClasses} rounded-full absolute inset-0`}
        aria-hidden="true"
      />
      
      <span className="sr-only">Cargando</span>
    </div>
  );
};

Spinner.displayName = 'Spinner';
SpinnerDots.displayName = 'SpinnerDots';
SpinnerPulse.displayName = 'SpinnerPulse';

export default Spinner;
