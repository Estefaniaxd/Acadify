import { forwardRef, InputHTMLAttributes, ReactNode } from 'react';
import { motion } from 'framer-motion';

/* ==========================================================================
   🔀 SWITCH COMPONENT
   Toggle switch animado y accesible
   ========================================================================== */

export type SwitchSize = 'sm' | 'md' | 'lg';

export interface SwitchProps extends Omit<InputHTMLAttributes<HTMLInputElement>, 'size' | 'type'> {
  /** Tamaño del switch */
  size?: SwitchSize;
  
  /** Label del switch */
  label?: ReactNode;
  
  /** Descripción adicional */
  description?: string;
  
  /** Mensaje de error */
  error?: string;
  
  /** Variante de color cuando está activo */
  variant?: 'primary' | 'success' | 'warning' | 'danger';
  
  /** Mostrar texto On/Off dentro del switch */
  showText?: boolean;
}

/**
 * Clases base del switch
 */
const getBaseClasses = (): string => {
  return [
    'relative inline-flex items-center',
    'rounded-full',
    'transition-all duration-300 ease-in-out',
    'cursor-pointer',
    'focus:outline-none focus:ring-2 focus:ring-offset-2',
    'disabled:opacity-50 disabled:cursor-not-allowed',
  ].join(' ');
};

/**
 * Clases según el tamaño
 */
const getSizeClasses = (size: SwitchSize): { track: string; thumb: string; text: string; label: string } => {
  const sizes = {
    sm: {
      track: 'w-9 h-5',
      thumb: 'w-3.5 h-3.5',
      text: 'text-[8px]',
      label: 'text-sm',
    },
    md: {
      track: 'w-11 h-6',
      thumb: 'w-4 h-4',
      text: 'text-[9px]',
      label: 'text-base',
    },
    lg: {
      track: 'w-14 h-7',
      thumb: 'w-5 h-5',
      text: 'text-[10px]',
      label: 'text-lg',
    },
  };
  
  return sizes[size];
};

/**
 * Clases según la variante
 */
const getVariantClasses = (variant: NonNullable<SwitchProps['variant']>, checked: boolean): string => {
  if (!checked) {
    return 'bg-neutral-300 dark:bg-neutral-700';
  }
  
  const variants = {
    primary: 'bg-primary-600 dark:bg-primary-500 focus:ring-primary-500/20',
    success: 'bg-success dark:bg-success focus:ring-success/20',
    warning: 'bg-warning dark:bg-warning focus:ring-warning/20',
    danger: 'bg-error dark:bg-error focus:ring-error/20',
  };
  
  return variants[variant];
};

/**
 * Switch Component
 * 
 * Toggle switch animado con:
 * - 3 tamaños
 * - 4 variantes de color
 * - Animación suave
 * - Label y descripción
 * - Texto On/Off opcional
 * 
 * @example
 * ```tsx
 * // Básico
 * <Switch
 *   label="Notificaciones"
 *   checked={notifications}
 *   onChange={(e) => setNotifications(e.target.checked)}
 * />
 * 
 * // Con descripción
 * <Switch
 *   label="Modo oscuro"
 *   description="Cambiar entre tema claro y oscuro"
 *   checked={isDark}
 *   onChange={(e) => setIsDark(e.target.checked)}
 *   variant="success"
 * />
 * 
 * // Con texto On/Off
 * <Switch
 *   label="Disponible"
 *   checked={isAvailable}
 *   onChange={(e) => setIsAvailable(e.target.checked)}
 *   showText
 *   size="lg"
 * />
 * ```
 */
export const Switch = forwardRef<HTMLInputElement, SwitchProps>(
  (
    {
      size = 'md',
      label,
      description,
      error,
      variant = 'primary',
      showText = false,
      disabled,
      checked = false,
      className = '',
      ...props
    },
    ref
  ) => {
    const sizeClasses = getSizeClasses(size);
    const variantClasses = getVariantClasses(variant, checked);
    
    const trackClasses = [
      getBaseClasses(),
      sizeClasses.track,
      variantClasses,
      className,
    ]
      .filter(Boolean)
      .join(' ');
    
    // Calcular posición del thumb
    const thumbOffset = checked
      ? size === 'sm'
        ? 16
        : size === 'lg'
        ? 26
        : 20
      : 4;
    
    return (
      <div className="flex items-start gap-3">
        {/* Switch wrapper */}
        <div className="relative flex items-center h-6">
          <input
            ref={ref}
            type="checkbox"
            checked={checked}
            disabled={disabled}
            className="sr-only peer"
            aria-invalid={!!error}
            role="switch"
            aria-checked={checked}
            {...props}
          />
          
          {/* Track */}
          <div className={trackClasses}>
            {/* Texto On/Off */}
            {showText && (
              <span
                className={`
                  ${sizeClasses.text}
                  font-bold
                  absolute inset-y-0 flex items-center
                  ${checked ? 'left-1.5' : 'right-1.5'}
                  text-white
                `}
                aria-hidden="true"
              >
                {checked ? 'ON' : 'OFF'}
              </span>
            )}
            
            {/* Thumb animado */}
            <motion.div
              className={`
                ${sizeClasses.thumb}
                bg-white
                rounded-full
                shadow-md
                absolute top-1
              `}
              animate={{ x: thumbOffset }}
              transition={{
                type: 'spring',
                stiffness: 500,
                damping: 30,
              }}
              aria-hidden="true"
            />
          </div>
        </div>
        
        {/* Label y descripción */}
        {(label || description) && (
          <div className="flex-1">
            {label && (
              <label
                htmlFor={props.id}
                className={`
                  ${sizeClasses.label}
                  font-medium
                  text-neutral-900 dark:text-neutral-100
                  cursor-pointer
                  ${disabled ? 'opacity-50 cursor-not-allowed' : ''}
                `}
              >
                {label}
                {props.required && (
                  <span className="text-error ml-1" aria-label="requerido">
                    *
                  </span>
                )}
              </label>
            )}
            
            {description && (
              <p className="text-xs text-neutral-600 dark:text-neutral-400 mt-0.5">
                {description}
              </p>
            )}
            
            {error && (
              <p className="text-xs text-error-dark dark:text-error mt-1" role="alert">
                {error}
              </p>
            )}
          </div>
        )}
      </div>
    );
  }
);

Switch.displayName = 'Switch';

export default Switch;
