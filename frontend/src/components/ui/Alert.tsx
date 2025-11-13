import { forwardRef, HTMLAttributes, ReactNode } from 'react';
import { IconType } from 'react-icons';
import { AlertCircle, AlertTriangle, CheckCircle, Info, X } from 'lucide-react';
;

/* ==========================================================================
   ⚠️ ALERT COMPONENT
   Alert para mensajes importantes con iconos y acciones
   ========================================================================== */

export type AlertVariant = 'info' | 'success' | 'warning' | 'error';

export interface AlertProps extends Omit<HTMLAttributes<HTMLDivElement>, 'title'> {
  /** Variante del alert */
  variant?: AlertVariant;
  
  /** Título del alert */
  title?: string;
  
  /** Descripción o mensaje */
  description?: ReactNode;
  
  /** Icono personalizado */
  icon?: IconType;
  
  /** Mostrar botón de cerrar */
  closeable?: boolean;
  
  /** Callback al cerrar */
  onClose?: () => void;
  
  /** Children para contenido personalizado */
  children?: ReactNode;
}

/**
 * Obtener icono según variante
 */
const getDefaultIcon = (variant: AlertVariant): IconType => {
  const icons: Record<AlertVariant, IconType> = {
    info: Info,
    success: CheckCircle,
    warning: AlertTriangle,
    error: AlertCircle,
  };
  
  return icons[variant];
};

/**
 * Obtener clases según variante
 */
const getVariantClasses = (variant: AlertVariant): string => {
  const variants: Record<AlertVariant, string> = {
    info: [
      'bg-info-light/50 dark:bg-info/10',
      'border-info/30 dark:border-info/50',
      'text-info-dark dark:text-info',
    ].join(' '),
    
    success: [
      'bg-success-light/50 dark:bg-success/10',
      'border-success/30 dark:border-success/50',
      'text-success-dark dark:text-success',
    ].join(' '),
    
    warning: [
      'bg-warning-light/50 dark:bg-warning/10',
      'border-warning/30 dark:border-warning/50',
      'text-warning-dark dark:text-warning',
    ].join(' '),
    
    error: [
      'bg-error-light/50 dark:bg-error/10',
      'border-error/30 dark:border-error/50',
      'text-error-dark dark:text-error',
    ].join(' '),
  };
  
  return variants[variant];
};

/**
 * Alert Component
 * 
 * Alert para comunicar mensajes importantes con:
 * - 4 variantes (info, success, warning, error)
 * - Iconos automáticos o personalizados
 * - Título y descripción
 * - Botón de cerrar opcional
 * - Contenido personalizable
 * 
 * @example
 * ```tsx
 * // Básico
 * <Alert variant="success" title="Éxito" description="Tus cambios fueron guardados" />
 * 
 * // Con cierre
 * <Alert
 *   variant="warning"
 *   title="Advertencia"
 *   description="Tu sesión expirará en 5 minutos"
 *   closeable
 *   onClose={() => setShowAlert(false)}
 * />
 * 
 * // Con children personalizado
 * <Alert variant="error" title="Error">
 *   <ul className="list-disc pl-5 mt-2">
 *     <li>Campo nombre es requerido</li>
 *     <li>Email inválido</li>
 *   </ul>
 * </Alert>
 * ```
 */
export const Alert = forwardRef<HTMLDivElement, AlertProps>(
  (
    {
      variant = 'info',
      title,
      description,
      icon,
      closeable = false,
      onClose,
      children,
      className = '',
      ...props
    },
    ref
  ) => {
    const Icon = icon || getDefaultIcon(variant);
    const variantClasses = getVariantClasses(variant);
    
    return (
      <div
        ref={ref}
        role="alert"
        className={`
          relative
          rounded-lg
          border-2
          p-4
          ${variantClasses}
          ${className}
        `}
        {...props}
      >
        <div className="flex gap-3">
          {/* Icono */}
          <div className="flex-shrink-0 mt-0.5">
            <Icon className="w-5 h-5" aria-hidden="true" />
          </div>
          
          {/* Contenido */}
          <div className="flex-1 min-w-0">
            {title && (
              <h3 className="font-semibold text-sm mb-1">
                {title}
              </h3>
            )}
            
            {description && (
              <div className="text-sm opacity-90">
                {description}
              </div>
            )}
            
            {children && (
              <div className="mt-2">
                {children}
              </div>
            )}
          </div>
          
          {/* Botón cerrar */}
          {closeable && onClose && (
            <button
              onClick={onClose}
              className="flex-shrink-0 p-1 rounded-lg hover:bg-black/5 dark:hover:bg-white/5 transition-colors"
              aria-label="Cerrar alerta"
            >
              <X className="w-5 h-5" aria-hidden="true" />
            </button>
          )}
        </div>
      </div>
    );
  }
);

Alert.displayName = 'Alert';

export default Alert;
