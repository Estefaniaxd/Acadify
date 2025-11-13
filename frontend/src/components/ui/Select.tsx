import { forwardRef, SelectHTMLAttributes, ReactNode } from 'react';
import { IconType } from 'react-icons';
import { AlertCircle, CheckCircle, ChevronDown } from 'lucide-react';
;

/* ==========================================================================
   📋 SELECT COMPONENT
   Select accesible con validación y estados visuales
   ========================================================================== */

export type SelectSize = 'sm' | 'md' | 'lg';

export interface SelectOption {
  value: string;
  label: string;
  disabled?: boolean;
}

export interface SelectProps extends Omit<SelectHTMLAttributes<HTMLSelectElement>, 'size'> {
  /** Tamaño del select */
  size?: SelectSize;
  
  /** Label del campo */
  label?: string;
  
  /** Texto de ayuda */
  helperText?: string;
  
  /** Mensaje de error */
  error?: string;
  
  /** Estado de éxito */
  success?: boolean;
  
  /** Mensaje de éxito */
  successMessage?: string;
  
  /** Icono a la izquierda */
  leftIcon?: IconType;
  
  /** Opciones del select */
  options?: SelectOption[];
  
  /** Placeholder */
  placeholder?: string;
  
  /** Children para opciones personalizadas */
  children?: ReactNode;
}

/**
 * Clases base del select
 */
const getBaseClasses = (): string => {
  return [
    'w-full',
    'appearance-none',
    'rounded-lg',
    'border',
    'transition-all duration-200',
    'focus:outline-none focus:ring-2',
    'disabled:opacity-50 disabled:cursor-not-allowed disabled:bg-neutral-100 dark:disabled:bg-neutral-800',
    'cursor-pointer',
  ].join(' ');
};

/**
 * Clases según el tamaño
 */
const getSizeClasses = (size: SelectSize, hasLeftIcon: boolean): string => {
  const sizes: Record<SelectSize, string> = {
    sm: hasLeftIcon ? 'pl-10 pr-10 py-2 text-sm' : 'px-3 pr-10 py-2 text-sm',
    md: hasLeftIcon ? 'pl-11 pr-10 py-2.5 text-base' : 'px-4 pr-10 py-2.5 text-base',
    lg: hasLeftIcon ? 'pl-12 pr-11 py-3 text-lg' : 'px-5 pr-11 py-3 text-lg',
  };
  
  return sizes[size];
};

/**
 * Clases según el estado
 */
const getStateClasses = (error?: string, success?: boolean, disabled?: boolean): string => {
  if (disabled) {
    return 'border-neutral-300 dark:border-neutral-700 bg-neutral-100 dark:bg-neutral-800';
  }
  
  if (error) {
    return [
      'border-error dark:border-error',
      'bg-error-light/10 dark:bg-error/5',
      'text-error-dark dark:text-error',
      'focus:ring-error/20 focus:border-error',
    ].join(' ');
  }
  
  if (success) {
    return [
      'border-success dark:border-success',
      'bg-success-light/10 dark:bg-success/5',
      'text-success-dark dark:text-success',
      'focus:ring-success/20 focus:border-success',
    ].join(' ');
  }
  
  return [
    'border-neutral-300 dark:border-neutral-700',
    'bg-white dark:bg-neutral-900',
    'text-neutral-900 dark:text-neutral-100',
    'focus:ring-primary-500/20 focus:border-primary-500',
    'hover:border-neutral-400 dark:hover:border-neutral-600',
  ].join(' ');
};

/**
 * Select Component
 * 
 * Select accesible con:
 * - 3 tamaños
 * - Estados de validación
 * - Icono opcional
 * - Label y mensajes de ayuda
 * - Opciones como array o children
 * 
 * @example
 * ```tsx
 * // Con options array
 * <Select
 *   label="País"
 *   placeholder="Selecciona un país"
 *   options={[
 *     { value: 'co', label: 'Colombia' },
 *     { value: 'mx', label: 'México' },
 *   ]}
 *   required
 * />
 * 
 * // Con children personalizados
 * <Select label="Categoría" error={errors.category}>
 *   <option value="">Selecciona...</option>
 *   <optgroup label="Tecnología">
 *     <option value="dev">Desarrollo</option>
 *     <option value="design">Diseño</option>
 *   </optgroup>
 * </Select>
 * ```
 */
export const Select = forwardRef<HTMLSelectElement, SelectProps>(
  (
    {
      size = 'md',
      label,
      helperText,
      error,
      success = false,
      successMessage,
      leftIcon: LeftIcon,
      options,
      placeholder,
      disabled,
      required,
      className = '',
      children,
      ...props
    },
    ref
  ) => {
    // ID único para accesibilidad
    const id = props.id || `select-${Math.random().toString(36).substr(2, 9)}`;
    const helperTextId = `${id}-helper`;
    const errorId = `${id}-error`;
    const successId = `${id}-success`;
    
    // Construir clases CSS
    const selectClasses = [
      getBaseClasses(),
      getSizeClasses(size, !!LeftIcon),
      getStateClasses(error, success, disabled),
      className,
    ]
      .filter(Boolean)
      .join(' ');
    
    // Tamaño del icono
    const iconSize = size === 'sm' ? 'text-sm' : size === 'lg' ? 'text-xl' : 'text-base';
    
    return (
      <div className="w-full">
        {/* Label */}
        {label && (
          <label
            htmlFor={id}
            className="block text-sm font-medium text-neutral-700 dark:text-neutral-300 mb-1.5"
          >
            {label}
            {required && (
              <span className="text-error ml-1" aria-label="requerido">
                *
              </span>
            )}
          </label>
        )}
        
        {/* Container del select */}
        <div className="relative">
          {/* Icono izquierdo */}
          {LeftIcon && (
            <div className="absolute left-3 top-1/2 -translate-y-1/2 text-neutral-500 dark:text-neutral-400 pointer-events-none">
              <LeftIcon className={iconSize} aria-hidden="true" />
            </div>
          )}
          
          {/* Select */}
          <select
            ref={ref}
            id={id}
            disabled={disabled}
            required={required}
            className={selectClasses}
            aria-invalid={!!error}
            aria-describedby={
              error ? errorId : success && successMessage ? successId : helperText ? helperTextId : undefined
            }
            {...props}
          >
            {/* Placeholder */}
            {placeholder && (
              <option value="" disabled>
                {placeholder}
              </option>
            )}
            
            {/* Opciones desde array */}
            {options?.map((option) => (
              <option
                key={option.value}
                value={option.value}
                disabled={option.disabled}
              >
                {option.label}
              </option>
            ))}
            
            {/* Opciones desde children */}
            {children}
          </select>
          
          {/* Icono chevron */}
          <div className="absolute right-3 top-1/2 -translate-y-1/2 text-neutral-500 dark:text-neutral-400 pointer-events-none">
            <ChevronDown className={iconSize} aria-hidden="true" />
          </div>
          
          {/* Icono de estado derecho */}
          {(error || success) && (
            <div className="absolute right-10 top-1/2 -translate-y-1/2">
              {error ? (
                <AlertCircle className={`${iconSize} text-error`} aria-hidden="true" />
              ) : success ? (
                <CheckCircle className={`${iconSize} text-success`} aria-hidden="true" />
              ) : null}
            </div>
          )}
        </div>
        
        {/* Helper text */}
        {helperText && !error && !successMessage && (
          <p
            id={helperTextId}
            className="mt-1.5 text-xs text-neutral-600 dark:text-neutral-400"
          >
            {helperText}
          </p>
        )}
        
        {/* Error message */}
        {error && (
          <p
            id={errorId}
            className="mt-1.5 text-xs text-error-dark dark:text-error flex items-center gap-1"
            role="alert"
          >
            <AlertCircle className="flex-shrink-0" aria-hidden="true" />
            {error}
          </p>
        )}
        
        {/* Success message */}
        {success && successMessage && (
          <p
            id={successId}
            className="mt-1.5 text-xs text-success-dark dark:text-success flex items-center gap-1"
          >
            <CheckCircle className="flex-shrink-0" aria-hidden="true" />
            {successMessage}
          </p>
        )}
      </div>
    );
  }
);

Select.displayName = 'Select';

export default Select;
