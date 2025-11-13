import { forwardRef, InputHTMLAttributes, ReactNode } from 'react';
import { Check, Minus } from 'lucide-react';
;

/* ==========================================================================
   ☑️ CHECKBOX COMPONENT
   Checkbox accesible con estados indeterminado y personalización
   ========================================================================== */

export type CheckboxSize = 'sm' | 'md' | 'lg';

export interface CheckboxProps extends Omit<InputHTMLAttributes<HTMLInputElement>, 'size' | 'type'> {
  /** Tamaño del checkbox */
  size?: CheckboxSize;
  
  /** Label del checkbox */
  label?: ReactNode;
  
  /** Descripción adicional */
  description?: string;
  
  /** Estado indeterminado */
  indeterminate?: boolean;
  
  /** Mensaje de error */
  error?: string;
  
  /** Variante de color */
  variant?: 'primary' | 'success' | 'warning' | 'danger';
}

/**
 * Clases base del checkbox
 */
const getBaseClasses = (): string => {
  return [
    'rounded',
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
const getSizeClasses = (size: CheckboxSize): { checkbox: string; icon: string; label: string } => {
  const sizes = {
    sm: {
      checkbox: 'w-4 h-4',
      icon: 'w-3 h-3',
      label: 'text-sm',
    },
    md: {
      checkbox: 'w-5 h-5',
      icon: 'w-3.5 h-3.5',
      label: 'text-base',
    },
    lg: {
      checkbox: 'w-6 h-6',
      icon: 'w-4 h-4',
      label: 'text-lg',
    },
  };
  
  return sizes[size];
};

/**
 * Clases según la variante
 */
const getVariantClasses = (variant: NonNullable<CheckboxProps['variant']>, checked: boolean, indeterminate: boolean): string => {
  if (!checked && !indeterminate) {
    return 'border-neutral-300 dark:border-neutral-700 bg-white dark:bg-neutral-900 hover:border-neutral-400 dark:hover:border-neutral-600';
  }
  
  const variants = {
    primary: [
      'border-primary-600 dark:border-primary-500',
      'bg-primary-600 dark:bg-primary-500',
      'focus:ring-primary-500/20',
      'hover:bg-primary-700 dark:hover:bg-primary-600',
    ].join(' '),
    
    success: [
      'border-success dark:border-success',
      'bg-success dark:bg-success',
      'focus:ring-success/20',
      'hover:bg-success-dark dark:hover:bg-success',
    ].join(' '),
    
    warning: [
      'border-warning dark:border-warning',
      'bg-warning dark:bg-warning',
      'focus:ring-warning/20',
      'hover:bg-warning-dark dark:hover:bg-warning',
    ].join(' '),
    
    danger: [
      'border-error dark:border-error',
      'bg-error dark:bg-error',
      'focus:ring-error/20',
      'hover:bg-error-dark dark:hover:bg-error',
    ].join(' '),
  };
  
  return variants[variant];
};

/**
 * Checkbox Component
 * 
 * Checkbox accesible con:
 * - 3 tamaños
 * - Estado indeterminado
 * - 4 variantes de color
 * - Label y descripción
 * - Mensaje de error
 * 
 * @example
 * ```tsx
 * // Básico
 * <Checkbox label="Aceptar términos" required />
 * 
 * // Con descripción
 * <Checkbox
 *   label="Notificaciones por email"
 *   description="Recibir actualizaciones importantes"
 *   checked={emailNotifications}
 *   onChange={(e) => setEmailNotifications(e.target.checked)}
 * />
 * 
 * // Indeterminado (para "seleccionar todos")
 * <Checkbox
 *   label="Seleccionar todos"
 *   checked={allSelected}
 *   indeterminate={someSelected}
 *   onChange={handleSelectAll}
 * />
 * ```
 */
export const Checkbox = forwardRef<HTMLInputElement, CheckboxProps>(
  (
    {
      size = 'md',
      label,
      description,
      indeterminate = false,
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
    const variantClasses = getVariantClasses(variant, !!checked, indeterminate);
    
    const checkboxClasses = [
      getBaseClasses(),
      sizeClasses.checkbox,
      variantClasses,
      className,
    ]
      .filter(Boolean)
      .join(' ');
    
    return (
      <div className="flex items-start gap-3">
        {/* Checkbox wrapper */}
        <div className="relative flex items-center h-6">
          <input
            ref={ref}
            type="checkbox"
            checked={checked}
            disabled={disabled}
            className="sr-only peer"
            aria-invalid={!!error}
            {...props}
          />
          
          {/* Custom checkbox visual */}
          <div className={checkboxClasses}>
            {/* Check icon */}
            {checked && !indeterminate && (
              <Check
                className={`${sizeClasses.icon} text-white absolute inset-0 m-auto`}
                strokeWidth={3}
                aria-hidden="true"
              />
            )}
            
            {/* Indeterminate icon */}
            {indeterminate && (
              <Minus
                className={`${sizeClasses.icon} text-white absolute inset-0 m-auto`}
                strokeWidth={3}
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

Checkbox.displayName = 'Checkbox';

export default Checkbox;
