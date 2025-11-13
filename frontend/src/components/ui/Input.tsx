import { forwardRef, InputHTMLAttributes, useState, useId } from 'react';
import { IconType } from 'react-icons';
import { AlertCircle, CheckCircle, Eye, EyeOff } from 'lucide-react';
;

/* ==========================================================================
   📝 INPUT COMPONENT
   Input versátil con soporte para iconos, validación y estados
   ========================================================================== */

/**
 * Tamaños de input disponibles
 */
export type InputSize = 
  | 'sm'     // Pequeño - 32px height
  | 'md'     // Mediano - 40px height (default)
  | 'lg';    // Grande - 48px height

/**
 * Props del componente Input
 */
export interface InputProps extends Omit<InputHTMLAttributes<HTMLInputElement>, 'size'> {
  /** Tamaño del input */
  size?: InputSize;
  
  /** Label del input */
  label?: string;
  
  /** Texto de ayuda debajo del input */
  helperText?: string;
  
  /** Mensaje de error */
  error?: string;
  
  /** Estado de éxito */
  success?: boolean;
  
  /** Mensaje de éxito */
  successMessage?: string;
  
  /** Icono a la izquierda */
  leftIcon?: IconType;
  
  /** Icono a la derecha */
  rightIcon?: IconType;
  
  /** Ancho completo */
  fullWidth?: boolean;
  
  /** Clases CSS adicionales para el contenedor */
  containerClassName?: string;
  
  /** Placeholder personalizado */
  placeholder?: string;
  
  /** Requerido */
  required?: boolean;
  
  /** Deshabilitar input */
  disabled?: boolean;
  
  /** Solo lectura */
  readOnly?: boolean;
}

/**
 * Obtiene las clases base del input
 */
const getBaseClasses = (): string => {
  return [
    'w-full',
    'px-4',
    'rounded-xl',
    'border-2',
    'transition-all duration-250',
    'focus-ring',
    'disabled:opacity-50 disabled:cursor-not-allowed',
    'read-only:bg-neutral-50 dark:read-only:bg-neutral-900',
    'placeholder:text-neutral-400 dark:placeholder:text-neutral-600',
  ].join(' ');
};

/**
 * Obtiene las clases según el tamaño
 */
const getSizeClasses = (size: InputSize): string => {
  const sizes: Record<InputSize, string> = {
    sm: 'h-8 text-sm',
    md: 'h-10 text-base',
    lg: 'h-12 text-lg',
  };
  
  return sizes[size];
};

/**
 * Obtiene las clases según el estado
 */
const getStateClasses = (error?: string, success?: boolean, disabled?: boolean): string => {
  if (disabled) {
    return 'border-neutral-300 dark:border-neutral-700 bg-neutral-50 dark:bg-neutral-900';
  }
  
  if (error) {
    return [
      'border-error',
      'text-error',
      'bg-error-light/10 dark:bg-error/10',
      'focus:border-error',
      'focus:ring-error/20',
    ].join(' ');
  }
  
  if (success) {
    return [
      'border-success',
      'text-success-dark',
      'bg-success-light/10 dark:bg-success/10',
      'focus:border-success',
      'focus:ring-success/20',
    ].join(' ');
  }
  
  return [
    'border-neutral-300 dark:border-neutral-700',
    'bg-white dark:bg-neutral-900',
    'text-neutral-900 dark:text-neutral-100',
    'focus:border-primary-600 dark:focus:border-primary-400',
    'focus:ring-primary-600/20',
  ].join(' ');
};

/**
 * Input Component
 * 
 * Campo de entrada con soporte para:
 * - 3 tamaños
 * - Iconos izquierda/derecha
 * - Estados (error, success, disabled, readonly)
 * - Label y texto de ayuda
 * - Toggle de visibilidad para passwords
 * - Accesibilidad completa
 * 
 * @example
 * ```tsx
 * // Input básico
 * <Input 
 *   label="Email" 
 *   type="email"
 *   placeholder="tu@email.com"
 * />
 * 
 * // Con error
 * <Input 
 *   label="Contraseña"
 *   type="password"
 *   error="La contraseña debe tener al menos 8 caracteres"
 * />
 * 
 * // Con icono
 * <Input 
 *   label="Buscar"
 *   leftIcon={FiSearch}
 *   placeholder="Buscar cursos..."
 * />
 * ```
 */
export const Input = forwardRef<HTMLInputElement, InputProps>(
  (
    {
      size = 'md',
      label,
      helperText,
      error,
      success,
      successMessage,
      leftIcon: LeftIcon,
      rightIcon: RightIcon,
      fullWidth = true,
      containerClassName = '',
      placeholder,
      required,
      disabled,
      readOnly,
      type = 'text',
      className = '',
      id: providedId,
      ...props
    },
    ref
  ) => {
    const [showPassword, setShowPassword] = useState(false);
    const generatedId = useId();
    const inputId = providedId || generatedId;
    const helperId = `${inputId}-helper`;
    const errorId = `${inputId}-error`;
    
    // Determinar el tipo de input (para password toggle)
    const inputType = type === 'password' && showPassword ? 'text' : type;
    
    // Determinar si hay iconos
    const hasLeftIcon = !!LeftIcon;
    const hasRightIcon = !!RightIcon || type === 'password';
    
    // Clases del contenedor
    const containerClasses = [
      fullWidth && 'w-full',
      containerClassName,
    ]
      .filter(Boolean)
      .join(' ');
    
    // Clases del input
    const inputClasses = [
      getBaseClasses(),
      getSizeClasses(size),
      getStateClasses(error, success, disabled),
      hasLeftIcon && 'pl-11',
      hasRightIcon && 'pr-11',
      className,
    ]
      .filter(Boolean)
      .join(' ');
    
    // Clases del label
    const labelClasses = [
      'block mb-1.5 text-sm font-medium',
      error 
        ? 'text-error' 
        : success
          ? 'text-success-dark'
          : 'text-neutral-700 dark:text-neutral-300',
    ].join(' ');
    
    return (
      <div className={containerClasses}>
        {/* Label */}
        {label && (
          <label htmlFor={inputId} className={labelClasses}>
            {label}
            {required && (
              <span className="text-error ml-1" aria-label="requerido">
                *
              </span>
            )}
          </label>
        )}
        
        {/* Input Container */}
        <div className="relative">
          {/* Icono izquierdo */}
          {LeftIcon && (
            <div className="absolute left-3 top-1/2 -translate-y-1/2 text-neutral-400 dark:text-neutral-600">
              <LeftIcon aria-hidden="true" />
            </div>
          )}
          
          {/* Input */}
          <input
            ref={ref}
            id={inputId}
            type={inputType}
            className={inputClasses}
            placeholder={placeholder}
            disabled={disabled}
            readOnly={readOnly}
            required={required}
            aria-invalid={!!error}
            aria-describedby={
              error 
                ? errorId 
                : helperText || successMessage
                  ? helperId
                  : undefined
            }
            {...props}
          />
          
          {/* Icono derecho o controles */}
          {hasRightIcon && (
            <div className="absolute right-3 top-1/2 -translate-y-1/2">
              {/* Password toggle */}
              {type === 'password' ? (
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="text-neutral-400 hover:text-neutral-600 dark:text-neutral-600 dark:hover:text-neutral-400 transition-colors"
                  aria-label={showPassword ? 'Ocultar contraseña' : 'Mostrar contraseña'}
                  tabIndex={-1}
                >
                  {showPassword ? (
                    <EyeOff aria-hidden="true" />
                  ) : (
                    <Eye aria-hidden="true" />
                  )}
                </button>
              ) : RightIcon ? (
                <RightIcon 
                  className="text-neutral-400 dark:text-neutral-600"
                  aria-hidden="true"
                />
              ) : null}
              
              {/* Icono de estado */}
              {(error || success) && !RightIcon && type !== 'password' && (
                <div className={error ? 'text-error' : 'text-success'}>
                  {error ? (
                    <AlertCircle aria-hidden="true" />
                  ) : (
                    <CheckCircle aria-hidden="true" />
                  )}
                </div>
              )}
            </div>
          )}
        </div>
        
        {/* Mensaje de error */}
        {error && (
          <p 
            id={errorId}
            className="mt-1.5 text-sm text-error flex items-center gap-1"
            role="alert"
          >
            <AlertCircle className="flex-shrink-0" aria-hidden="true" />
            <span>{error}</span>
          </p>
        )}
        
        {/* Mensaje de éxito */}
        {!error && successMessage && (
          <p 
            id={helperId}
            className="mt-1.5 text-sm text-success-dark flex items-center gap-1"
          >
            <CheckCircle className="flex-shrink-0" aria-hidden="true" />
            <span>{successMessage}</span>
          </p>
        )}
        
        {/* Helper text */}
        {!error && !successMessage && helperText && (
          <p 
            id={helperId}
            className="mt-1.5 text-sm text-neutral-600 dark:text-neutral-400"
          >
            {helperText}
          </p>
        )}
      </div>
    );
  }
);

Input.displayName = 'Input';

/**
 * Textarea Component
 * Similar al Input pero para texto multilínea
 */
export interface TextareaProps extends Omit<React.TextareaHTMLAttributes<HTMLTextAreaElement>, 'size'> {
  size?: InputSize;
  label?: string;
  helperText?: string;
  error?: string;
  fullWidth?: boolean;
  containerClassName?: string;
  required?: boolean;
}

export const Textarea = forwardRef<HTMLTextAreaElement, TextareaProps>(
  (
    {
      size = 'md',
      label,
      helperText,
      error,
      fullWidth = true,
      containerClassName = '',
      required,
      className = '',
      id: providedId,
      ...props
    },
    ref
  ) => {
    const generatedId = useId();
    const inputId = providedId || generatedId;
    const helperId = `${inputId}-helper`;
    const errorId = `${inputId}-error`;
    
    const containerClasses = [
      fullWidth && 'w-full',
      containerClassName,
    ]
      .filter(Boolean)
      .join(' ');
    
    const textareaClasses = [
      getBaseClasses(),
      'py-3 min-h-[100px] resize-y',
      getSizeClasses(size),
      getStateClasses(error, false, props.disabled),
      className,
    ]
      .filter(Boolean)
      .join(' ');
    
    const labelClasses = [
      'block mb-1.5 text-sm font-medium',
      error 
        ? 'text-error' 
        : 'text-neutral-700 dark:text-neutral-300',
    ].join(' ');
    
    return (
      <div className={containerClasses}>
        {label && (
          <label htmlFor={inputId} className={labelClasses}>
            {label}
            {required && (
              <span className="text-error ml-1" aria-label="requerido">
                *
              </span>
            )}
          </label>
        )}
        
        <textarea
          ref={ref}
          id={inputId}
          className={textareaClasses}
          required={required}
          aria-invalid={!!error}
          aria-describedby={
            error 
              ? errorId 
              : helperText
                ? helperId
                : undefined
          }
          {...props}
        />
        
        {error && (
          <p 
            id={errorId}
            className="mt-1.5 text-sm text-error flex items-center gap-1"
            role="alert"
          >
            <AlertCircle className="flex-shrink-0" aria-hidden="true" />
            <span>{error}</span>
          </p>
        )}
        
        {!error && helperText && (
          <p 
            id={helperId}
            className="mt-1.5 text-sm text-neutral-600 dark:text-neutral-400"
          >
            {helperText}
          </p>
        )}
      </div>
    );
  }
);

Textarea.displayName = 'Textarea';

export default Input;
