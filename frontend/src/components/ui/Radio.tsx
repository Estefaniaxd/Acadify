import { forwardRef, InputHTMLAttributes, ReactNode } from 'react';

/* ==========================================================================
   🔘 RADIO COMPONENT
   Radio button accesible con estilos personalizados
   ========================================================================== */

export type RadioSize = 'sm' | 'md' | 'lg';

export interface RadioProps extends Omit<InputHTMLAttributes<HTMLInputElement>, 'size' | 'type'> {
  /** Tamaño del radio */
  size?: RadioSize;
  
  /** Label del radio */
  label?: ReactNode;
  
  /** Descripción adicional */
  description?: string;
  
  /** Mensaje de error */
  error?: string;
  
  /** Variante de color */
  variant?: 'primary' | 'success' | 'warning' | 'danger';
}

/**
 * Clases base del radio
 */
const getBaseClasses = (): string => {
  return [
    'rounded-full',
    'border-2',
    'transition-all duration-200',
    'cursor-pointer',
    'focus:outline-none focus:ring-2 focus:ring-offset-2',
    'disabled:opacity-50 disabled:cursor-not-allowed',
  ].join(' ');
};

/**
 * Clases según el tamaño
 */
const getSizeClasses = (size: RadioSize): { radio: string; dot: string; label: string } => {
  const sizes = {
    sm: {
      radio: 'w-4 h-4',
      dot: 'w-2 h-2',
      label: 'text-sm',
    },
    md: {
      radio: 'w-5 h-5',
      dot: 'w-2.5 h-2.5',
      label: 'text-base',
    },
    lg: {
      radio: 'w-6 h-6',
      dot: 'w-3 h-3',
      label: 'text-lg',
    },
  };
  
  return sizes[size];
};

/**
 * Clases según la variante
 */
const getVariantClasses = (variant: NonNullable<RadioProps['variant']>, checked: boolean): string => {
  if (!checked) {
    return 'border-neutral-300 dark:border-neutral-700 bg-white dark:bg-neutral-900 hover:border-neutral-400 dark:hover:border-neutral-600';
  }
  
  const variants = {
    primary: [
      'border-primary-600 dark:border-primary-500',
      'bg-white dark:bg-neutral-900',
      'focus:ring-primary-500/20',
    ].join(' '),
    
    success: [
      'border-success dark:border-success',
      'bg-white dark:bg-neutral-900',
      'focus:ring-success/20',
    ].join(' '),
    
    warning: [
      'border-warning dark:border-warning',
      'bg-white dark:bg-neutral-900',
      'focus:ring-warning/20',
    ].join(' '),
    
    danger: [
      'border-error dark:border-error',
      'bg-white dark:bg-neutral-900',
      'focus:ring-error/20',
    ].join(' '),
  };
  
  return variants[variant];
};

/**
 * Clases del dot según la variante
 */
const getDotClasses = (variant: NonNullable<RadioProps['variant']>): string => {
  const variants = {
    primary: 'bg-primary-600 dark:bg-primary-500',
    success: 'bg-success dark:bg-success',
    warning: 'bg-warning dark:bg-warning',
    danger: 'bg-error dark:bg-error',
  };
  
  return variants[variant];
};

/**
 * Radio Component
 * 
 * Radio button accesible con:
 * - 3 tamaños
 * - 4 variantes de color
 * - Label y descripción
 * - Mensaje de error
 * 
 * @example
 * ```tsx
 * // Básico
 * <Radio
 *   name="plan"
 *   value="basic"
 *   label="Plan Básico"
 *   checked={plan === 'basic'}
 *   onChange={(e) => setPlan(e.target.value)}
 * />
 * 
 * // Con descripción
 * <Radio
 *   name="plan"
 *   value="pro"
 *   label="Plan Pro"
 *   description="Todas las funciones + soporte prioritario"
 *   checked={plan === 'pro'}
 *   onChange={(e) => setPlan(e.target.value)}
 * />
 * 
 * // Grupo de radios
 * <RadioGroup>
 *   {options.map(option => (
 *     <Radio key={option.value} {...option} />
 *   ))}
 * </RadioGroup>
 * ```
 */
export const Radio = forwardRef<HTMLInputElement, RadioProps>(
  (
    {
      size = 'md',
      label,
      description,
      error,
      variant = 'primary',
      disabled,
      checked,
      className = '',
      ...props
    },
    ref
  ) => {
    const sizeClasses = getSizeClasses(size);
    const variantClasses = getVariantClasses(variant, !!checked);
    const dotClasses = getDotClasses(variant);
    
    const radioClasses = [
      getBaseClasses(),
      sizeClasses.radio,
      variantClasses,
      className,
    ]
      .filter(Boolean)
      .join(' ');
    
    return (
      <div className="flex items-start gap-3">
        {/* Radio wrapper */}
        <div className="relative flex items-center h-6">
          <input
            ref={ref}
            type="radio"
            checked={checked}
            disabled={disabled}
            className="sr-only peer"
            aria-invalid={!!error}
            {...props}
          />
          
          {/* Custom radio visual */}
          <div className={radioClasses}>
            {/* Dot interior */}
            {checked && (
              <div
                className={`${sizeClasses.dot} ${dotClasses} rounded-full absolute inset-0 m-auto transition-all duration-200`}
                aria-hidden="true"
              />
            )}
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

Radio.displayName = 'Radio';

/**
 * RadioGroup - Contenedor para grupo de radios
 */
export interface RadioGroupProps {
  children: ReactNode;
  label?: string;
  error?: string;
  required?: boolean;
  className?: string;
}

export const RadioGroup = forwardRef<HTMLDivElement, RadioGroupProps>(
  ({ children, label, error, required, className = '' }, ref) => {
    return (
      <div ref={ref} className={`space-y-3 ${className}`} role="radiogroup">
        {label && (
          <div className="text-sm font-medium text-neutral-700 dark:text-neutral-300 mb-2">
            {label}
            {required && (
              <span className="text-error ml-1" aria-label="requerido">
                *
              </span>
            )}
          </div>
        )}
        
        {children}
        
        {error && (
          <p className="text-xs text-error-dark dark:text-error mt-2" role="alert">
            {error}
          </p>
        )}
      </div>
    );
  }
);

RadioGroup.displayName = 'RadioGroup';

export default Radio;
