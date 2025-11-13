import { forwardRef, HTMLAttributes } from 'react';
import { motion } from 'framer-motion';

/* ==========================================================================
   📊 PROGRESS COMPONENT
   Barra de progreso animada con variantes
   ========================================================================== */

export type ProgressSize = 'sm' | 'md' | 'lg';
export type ProgressVariant = 'primary' | 'success' | 'warning' | 'danger' | 'gradient';

export interface ProgressProps extends Omit<HTMLAttributes<HTMLDivElement>, 'children'> {
  /** Valor actual (0-100) */
  value: number;
  
  /** Valor máximo (default: 100) */
  max?: number;
  
  /** Tamaño de la barra */
  size?: ProgressSize;
  
  /** Variante de color */
  variant?: ProgressVariant;
  
  /** Mostrar label con porcentaje */
  showLabel?: boolean;
  
  /** Label personalizado */
  label?: string;
  
  /** Modo indeterminado (loading) */
  indeterminate?: boolean;
  
  /** Animar el progreso */
  animated?: boolean;
}

/**
 * Clases según el tamaño
 */
const getSizeClasses = (size: ProgressSize): string => {
  const sizes = {
    sm: 'h-1',
    md: 'h-2',
    lg: 'h-3',
  };
  
  return sizes[size];
};

/**
 * Clases según la variante
 */
const getVariantClasses = (variant: ProgressVariant): string => {
  const variants = {
    primary: 'bg-primary-600 dark:bg-primary-500',
    success: 'bg-success dark:bg-success',
    warning: 'bg-warning dark:bg-warning',
    danger: 'bg-error dark:bg-error',
    gradient: 'bg-gradient-to-r from-primary-600 to-accent-500',
  };
  
  return variants[variant];
};

/**
 * Progress Component
 * 
 * Barra de progreso con:
 * - 3 tamaños
 * - 5 variantes de color
 * - Label opcional
 * - Modo indeterminado
 * - Animación suave
 * 
 * @example
 * ```tsx
 * // Básico
 * <Progress value={60} />
 * 
 * // Con label
 * <Progress
 *   value={uploadProgress}
 *   variant="success"
 *   size="lg"
 *   showLabel
 * />
 * 
 * // Indeterminado (loading)
 * <Progress indeterminate variant="gradient" />
 * 
 * // Con label personalizado
 * <Progress
 *   value={75}
 *   label="Procesando archivos..."
 * />
 * ```
 */
export const Progress = forwardRef<HTMLDivElement, ProgressProps>(
  (
    {
      value = 0,
      max = 100,
      size = 'md',
      variant = 'primary',
      showLabel = false,
      label,
      indeterminate = false,
      animated = true,
      className = '',
      ...props
    },
    ref
  ) => {
    // Normalizar valor entre 0 y 100
    const percentage = Math.min(Math.max((value / max) * 100, 0), 100);
    
    const trackClasses = [
      'w-full',
      'rounded-full',
      'bg-neutral-200 dark:bg-neutral-800',
      'overflow-hidden',
      getSizeClasses(size),
      className,
    ]
      .filter(Boolean)
      .join(' ');
    
    const barClasses = [
      'h-full',
      'rounded-full',
      'transition-all duration-300 ease-out',
      getVariantClasses(variant),
    ]
      .filter(Boolean)
      .join(' ');
    
    return (
      <div ref={ref} {...props}>
        {/* Label */}
        {(showLabel || label) && (
          <div className="flex items-center justify-between mb-2 text-sm">
            {label ? (
              <span className="font-medium text-neutral-700 dark:text-neutral-300">
                {label}
              </span>
            ) : (
              <span />
            )}
            
            {showLabel && !indeterminate && (
              <span className="font-semibold text-neutral-900 dark:text-neutral-100">
                {Math.round(percentage)}%
              </span>
            )}
          </div>
        )}
        
        {/* Track */}
        <div
          className={trackClasses}
          role="progressbar"
          aria-valuenow={indeterminate ? undefined : value}
          aria-valuemin={0}
          aria-valuemax={max}
          aria-valuetext={indeterminate ? 'Cargando...' : `${Math.round(percentage)}%`}
        >
          {/* Bar */}
          {indeterminate ? (
            <motion.div
              className={barClasses}
              style={{ width: '40%' }}
              animate={{
                x: ['-100%', '250%'],
              }}
              transition={{
                duration: 1.5,
                repeat: Infinity,
                ease: 'easeInOut',
              }}
            />
          ) : animated ? (
            <motion.div
              className={barClasses}
              initial={{ width: 0 }}
              animate={{ width: `${percentage}%` }}
              transition={{ duration: 0.5, ease: 'easeOut' }}
            />
          ) : (
            <div
              className={barClasses}
              style={{ width: `${percentage}%` }}
            />
          )}
        </div>
      </div>
    );
  }
);

Progress.displayName = 'Progress';

/**
 * CircularProgress - Progreso circular
 */
export interface CircularProgressProps {
  /** Valor actual (0-100) */
  value?: number;
  
  /** Tamaño en píxeles */
  size?: number;
  
  /** Grosor del círculo */
  thickness?: number;
  
  /** Variante de color */
  variant?: ProgressVariant;
  
  /** Modo indeterminado */
  indeterminate?: boolean;
  
  /** Mostrar label con porcentaje */
  showLabel?: boolean;
}

export const CircularProgress: React.FC<CircularProgressProps> = ({
  value = 0,
  size = 64,
  thickness = 4,
  variant = 'primary',
  indeterminate = false,
  showLabel = false,
}) => {
  const percentage = Math.min(Math.max(value, 0), 100);
  const radius = (size - thickness) / 2;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference - (percentage / 100) * circumference;
  
  const colorClasses = {
    primary: 'stroke-primary-600 dark:stroke-primary-500',
    success: 'stroke-success dark:stroke-success',
    warning: 'stroke-warning dark:stroke-warning',
    danger: 'stroke-error dark:stroke-error',
    gradient: 'stroke-primary-600',
  };
  
  return (
    <div className="relative inline-flex items-center justify-center">
      <svg
        width={size}
        height={size}
        className="-rotate-90"
      >
        {/* Track */}
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke="currentColor"
          strokeWidth={thickness}
          className="text-neutral-200 dark:text-neutral-800"
        />
        
        {/* Progress */}
        {indeterminate ? (
          <motion.circle
            cx={size / 2}
            cy={size / 2}
            r={radius}
            fill="none"
            strokeWidth={thickness}
            strokeLinecap="round"
            className={colorClasses[variant]}
            strokeDasharray={circumference}
            animate={{
              strokeDashoffset: [circumference, 0],
              rotate: [0, 360],
            }}
            transition={{
              strokeDashoffset: {
                duration: 1.5,
                repeat: Infinity,
                ease: 'easeInOut',
              },
              rotate: {
                duration: 2,
                repeat: Infinity,
                ease: 'linear',
              },
            }}
          />
        ) : (
          <motion.circle
            cx={size / 2}
            cy={size / 2}
            r={radius}
            fill="none"
            strokeWidth={thickness}
            strokeLinecap="round"
            className={colorClasses[variant]}
            strokeDasharray={circumference}
            initial={{ strokeDashoffset: circumference }}
            animate={{ strokeDashoffset: offset }}
            transition={{ duration: 0.5, ease: 'easeOut' }}
          />
        )}
      </svg>
      
      {/* Label */}
      {showLabel && !indeterminate && (
        <div className="absolute inset-0 flex items-center justify-center text-sm font-semibold text-neutral-900 dark:text-neutral-100">
          {Math.round(percentage)}%
        </div>
      )}
    </div>
  );
};

CircularProgress.displayName = 'CircularProgress';

export default Progress;
