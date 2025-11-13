import { forwardRef, ButtonHTMLAttributes } from 'react';
import { motion, HTMLMotionProps } from 'framer-motion';
import { IconType } from 'react-icons';

/* ==========================================================================
   🔘 BUTTON COMPONENT
   Botón versátil con soporte completo de variantes, tamaños y estados
   ========================================================================== */

/**
 * Variantes de botón disponibles
 */
export type ButtonVariant = 
  | 'primary'      // Acción principal - Gradiente violeta/púrpura
  | 'secondary'    // Acción secundaria - Outline con primary
  | 'success'      // Acción positiva - Verde
  | 'warning'      // Advertencia - Ámbar
  | 'danger'       // Acción destructiva - Rojo
  | 'ghost'        // Sutil - Solo texto con hover
  | 'link'         // Como enlace - Sin fondo ni border
  | 'glass';       // Glassmorphism

/**
 * Tamaños de botón disponibles
 */
export type ButtonSize = 
  | 'xs'     // Extra pequeño - 28px height
  | 'sm'     // Pequeño - 32px height
  | 'md'     // Mediano - 40px height (default)
  | 'lg'     // Grande - 48px height
  | 'xl';    // Extra grande - 56px height

/**
 * Props del componente Button
 */
export interface ButtonProps extends Omit<ButtonHTMLAttributes<HTMLButtonElement>, 'className'> {
  /** Variante visual del botón */
  variant?: ButtonVariant;
  
  /** Tamaño del botón */
  size?: ButtonSize;
  
  /** Estado de carga - Muestra spinner */
  isLoading?: boolean;
  
  /** Deshabilitar botón */
  disabled?: boolean;
  
  /** Ancho completo */
  fullWidth?: boolean;
  
  /** Icono a la izquierda del texto */
  leftIcon?: IconType;
  
  /** Icono a la derecha del texto */
  rightIcon?: IconType;
  
  /** Solo icono - Sin texto */
  iconOnly?: boolean;
  
  /** Clases CSS adicionales */
  className?: string;
  
  /** Habilitar animaciones de Framer Motion */
  animated?: boolean;
  
  /** Children - Contenido del botón */
  children?: React.ReactNode;
}

/**
 * Obtiene las clases CSS base del botón
 */
const getBaseClasses = (): string => {
  return [
    'inline-flex items-center justify-center gap-2',
    'font-medium',
    'rounded-xl',
    'transition-all duration-250',
    'focus-ring',
    'disabled:opacity-50 disabled:cursor-not-allowed disabled:pointer-events-none',
    'relative overflow-hidden',
  ].join(' ');
};

/**
 * Obtiene las clases según la variante
 */
const getVariantClasses = (variant: ButtonVariant): string => {
  const variants: Record<ButtonVariant, string> = {
    primary: [
      'bg-gradient-to-r from-primary-600 to-secondary-600',
      'text-white',
      'shadow-lg hover:shadow-xl',
      'hover:from-primary-700 hover:to-secondary-700',
      'active:from-primary-800 active:to-secondary-800',
      'dark:from-primary-500 dark:to-secondary-500',
    ].join(' '),
    
    secondary: [
      'bg-transparent',
      'border-2 border-primary-600',
      'text-primary-600 dark:text-primary-400',
      'hover:bg-primary-50 dark:hover:bg-primary-950',
      'active:bg-primary-100 dark:active:bg-primary-900',
    ].join(' '),
    
    success: [
      'bg-accent-600',
      'text-white',
      'shadow-md hover:shadow-lg',
      'hover:bg-accent-700',
      'active:bg-accent-800',
    ].join(' '),
    
    warning: [
      'bg-warning text-white',
      'shadow-md hover:shadow-lg',
      'hover:bg-warning-dark',
      'active:brightness-90',
    ].join(' '),
    
    danger: [
      'bg-error text-white',
      'shadow-md hover:shadow-lg',
      'hover:bg-error-dark',
      'active:brightness-90',
    ].join(' '),
    
    ghost: [
      'bg-transparent',
      'text-neutral-700 dark:text-neutral-300',
      'hover:bg-neutral-100 dark:hover:bg-neutral-800',
      'active:bg-neutral-200 dark:active:bg-neutral-700',
    ].join(' '),
    
    link: [
      'bg-transparent',
      'text-primary-600 dark:text-primary-400',
      'hover:text-primary-700 dark:hover:text-primary-300',
      'active:text-primary-800 dark:active:text-primary-200',
      'hover:underline',
      'p-0',
    ].join(' '),
    
    glass: [
      'glass-card',
      'text-neutral-900 dark:text-neutral-100',
      'hover:shadow-glass-lg',
      'backdrop-blur-xl',
    ].join(' '),
  };
  
  return variants[variant];
};

/**
 * Obtiene las clases según el tamaño
 */
const getSizeClasses = (size: ButtonSize, iconOnly: boolean): string => {
  if (iconOnly) {
    const iconSizes: Record<ButtonSize, string> = {
      xs: 'h-7 w-7 text-sm',
      sm: 'h-8 w-8 text-base',
      md: 'h-10 w-10 text-lg',
      lg: 'h-12 w-12 text-xl',
      xl: 'h-14 w-14 text-2xl',
    };
    return iconSizes[size];
  }
  
  const sizes: Record<ButtonSize, string> = {
    xs: 'h-7 px-3 text-xs',
    sm: 'h-8 px-4 text-sm',
    md: 'h-10 px-6 text-base',
    lg: 'h-12 px-8 text-lg',
    xl: 'h-14 px-10 text-xl',
  };
  
  return sizes[size];
};

/**
 * Componente Spinner para estado de carga
 */
const Spinner = ({ size = 'md' }: { size?: ButtonSize }) => {
  const sizeMap = {
    xs: 'w-3 h-3',
    sm: 'w-4 h-4',
    md: 'w-5 h-5',
    lg: 'w-6 h-6',
    xl: 'w-7 h-7',
  };
  
  return (
    <svg
      className={`animate-spin ${sizeMap[size]}`}
      xmlns="http://www.w3.org/2000/svg"
      fill="none"
      viewBox="0 0 24 24"
      aria-hidden="true"
    >
      <circle
        className="opacity-25"
        cx="12"
        cy="12"
        r="10"
        stroke="currentColor"
        strokeWidth="4"
      />
      <path
        className="opacity-75"
        fill="currentColor"
        d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
      />
    </svg>
  );
};

/**
 * Button Component
 * 
 * Botón altamente personalizable con soporte para:
 * - 8 variantes visuales
 * - 5 tamaños
 * - Estado de carga con spinner
 * - Iconos izquierda/derecha
 * - Modo solo icono
 * - Animaciones opcionales
 * - Accesibilidad completa
 * 
 * @example
 * ```tsx
 * // Botón primario básico
 * <Button variant="primary">Guardar</Button>
 * 
 * // Con icono y carga
 * <Button 
 *   variant="success" 
 *   leftIcon={FiCheck}
 *   isLoading={isSubmitting}
 * >
 *   Confirmar
 * </Button>
 * 
 * // Solo icono
 * <Button iconOnly leftIcon={FiX} aria-label="Cerrar" />
 * ```
 */
export const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  (
    {
      variant = 'primary',
      size = 'md',
      isLoading = false,
      disabled = false,
      fullWidth = false,
      leftIcon: LeftIcon,
      rightIcon: RightIcon,
      iconOnly = false,
      className = '',
      animated = true,
      children,
      type = 'button',
      ...props
    },
    ref
  ) => {
    // Construir clases CSS
    const classes = [
      getBaseClasses(),
      getVariantClasses(variant),
      getSizeClasses(size, iconOnly),
      fullWidth && 'w-full',
      className,
    ]
      .filter(Boolean)
      .join(' ');
    
    // Determinar si debe estar deshabilitado
    const isDisabled = disabled || isLoading;
    
    // Props comunes del botón
    const buttonProps = {
      ref,
      type,
      className: classes,
      disabled: isDisabled,
      'aria-disabled': isDisabled,
      'aria-busy': isLoading,
      ...props,
    };
    
    // Contenido del botón
    const content = (
      <>
        {/* Icono izquierdo o spinner */}
        {isLoading ? (
          <Spinner size={size} />
        ) : (
          LeftIcon && <LeftIcon aria-hidden="true" />
        )}
        
        {/* Texto del botón */}
        {!iconOnly && children && (
          <span className={isLoading ? 'opacity-0' : ''}>
            {children}
          </span>
        )}
        
        {/* Icono derecho */}
        {!isLoading && RightIcon && !iconOnly && (
          <RightIcon aria-hidden="true" />
        )}
        
        {/* Spinner absoluto cuando hay texto */}
        {isLoading && !iconOnly && children && (
          <span className="absolute inset-0 flex items-center justify-center">
            <Spinner size={size} />
          </span>
        )}
      </>
    );
    
    // Renderizar con o sin animaciones
    if (animated && !isDisabled) {
      return (
        <motion.button
          {...(buttonProps as HTMLMotionProps<'button'>)}
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
          transition={{ duration: 0.15 }}
        >
          {content}
        </motion.button>
      );
    }
    
    return <button {...buttonProps}>{content}</button>;
  }
);

Button.displayName = 'Button';

/**
 * ButtonGroup - Agrupa botones relacionados
 * 
 * @example
 * ```tsx
 * <ButtonGroup>
 *   <Button>Cancelar</Button>
 *   <Button variant="primary">Guardar</Button>
 * </ButtonGroup>
 * ```
 */
export const ButtonGroup = ({ 
  children,
  className = '',
}: { 
  children: React.ReactNode;
  className?: string;
}) => {
  return (
    <div className={`inline-flex gap-2 ${className}`}>
      {children}
    </div>
  );
};

ButtonGroup.displayName = 'ButtonGroup';

export default Button;
