import { useEffect, forwardRef, useMemo, memo, useCallback } from 'react';
import { motion } from 'framer-motion';
;
import { IconType } from 'react-icons';
import { AlertCircle, AlertTriangle, CheckCircle, Info, X } from 'lucide-react';

/* ==========================================================================
   🔔 TOAST COMPONENT
   Toast notification profesional con animaciones y auto-dismiss
   
   Principios aplicados:
   - Single Responsibility: Solo maneja notificaciones toast
   - Open/Closed: Extensible vía configuración
   - Liskov Substitution: Consistente con otros componentes de feedback
   - Interface Segregation: Props específicas
   ========================================================================== */

export type ToastType = 'success' | 'error' | 'info' | 'warning';
export type ToastPosition = 'top-right' | 'top-left' | 'bottom-right' | 'bottom-left' | 'top-center' | 'bottom-center';

export interface ToastProps {
  /** ID único del toast */
  id: string;
  
  /** Tipo de toast */
  type: ToastType;
  
  /** Título del toast */
  title: string;
  
  /** Mensaje opcional */
  message?: string;
  
  /** Duración en ms (0 = no auto-close) */
  duration?: number;
  
  /** Callback al cerrar */
  onClose: (id: string) => void;
  
  /** Icono personalizado */
  icon?: IconType;
  
  /** Acción opcional */
  action?: {
    label: string;
    onClick: () => void;
  };
}

/**
 * Configuración de iconos por tipo
 * Separado para mejor mantenibilidad (Open/Closed Principle)
 */
const TOAST_ICONS: Record<ToastType, IconType> = {
  success: CheckCircle,
  error: AlertCircle,
  warning: AlertTriangle,
  info: Info,
} as const;

/**
 * Configuración de estilos por tipo
 * Usando design system tokens
 */
const TOAST_STYLES: Record<ToastType, {
  bg: string;
  border: string;
  icon: string;
  progress: string;
}> = {
  success: {
    bg: 'bg-success-light/90 dark:bg-success/20',
    border: 'border-success/40 dark:border-success/50',
    icon: 'text-success-dark dark:text-success',
    progress: 'bg-success dark:bg-success-light',
  },
  error: {
    bg: 'bg-error-light/90 dark:bg-error/20',
    border: 'border-error/40 dark:border-error/50',
    icon: 'text-error-dark dark:text-error',
    progress: 'bg-error dark:bg-error-light',
  },
  warning: {
    bg: 'bg-warning-light/90 dark:bg-warning/20',
    border: 'border-warning/40 dark:border-warning/50',
    icon: 'text-warning-dark dark:text-warning',
    progress: 'bg-warning dark:bg-warning-light',
  },
  info: {
    bg: 'bg-info-light/90 dark:bg-info/20',
    border: 'border-info/40 dark:border-info/50',
    icon: 'text-info-dark dark:text-info',
    progress: 'bg-info dark:bg-info-light',
  },
} as const;

/**
 * Configuración de animaciones
 */
const ANIMATION_CONFIG = {
  initial: { opacity: 0, x: 300, scale: 0.9 },
  animate: { opacity: 1, x: 0, scale: 1 },
  exit: { opacity: 0, x: 300, scale: 0.9 },
  transition: { 
    type: 'spring',
    stiffness: 400,
    damping: 30,
  },
} as const;

const Toast = memo(forwardRef<HTMLDivElement, ToastProps>(({
  id,
  type,
  title,
  message,
  duration = 5000,
  onClose,
  icon,
  action,
}, ref) => {
  // Callback memoizado para cerrar (Performance)
  const handleClose = useCallback(() => {
    onClose(id);
  }, [id, onClose]);
  
  // Auto-dismiss timer
  useEffect(() => {
    if (duration <= 0) return;
    
    const timer = setTimeout(handleClose, duration);
    return () => clearTimeout(timer);
  }, [duration, handleClose]);

  // Obtener configuración de estilos (memoizado)
  const styles = useMemo(() => TOAST_STYLES[type], [type]);
  const Icon = icon || TOAST_ICONS[type];

  return (
    <motion.div
      ref={ref}
      {...ANIMATION_CONFIG}
      className={`
        relative 
        flex items-start gap-3 
        p-4 pr-3
        min-w-[320px] max-w-[420px]
        ${styles.bg}
        backdrop-blur-lg
        border-2 ${styles.border}
        rounded-xl
        shadow-lg
        text-neutral-900 dark:text-neutral-100
      `}
      role="alert"
      aria-live="polite"
      aria-atomic="true"
    >
      {/* Icono */}
      <div className={`flex-shrink-0 mt-0.5 ${styles.icon}`}>
        <Icon className="w-5 h-5" aria-hidden="true" />
      </div>

      {/* Contenido */}
      <div className="flex-1 min-w-0">
        <h4 className="font-semibold text-sm leading-tight mb-1">
          {title}
        </h4>
        
        {message && (
          <p className="text-xs opacity-90 leading-relaxed">
            {message}
          </p>
        )}
        
        {/* Acción opcional */}
        {action && (
          <button
            onClick={() => {
              action.onClick();
              handleClose();
            }}
            className="
              mt-2 text-xs font-medium
              underline underline-offset-2
              hover:opacity-80
              transition-opacity
              focus:outline-none focus:ring-2 focus:ring-current focus:ring-offset-1
            "
          >
            {action.label}
          </button>
        )}
      </div>

      {/* Botón cerrar */}
      <button
        onClick={handleClose}
        className="
          flex-shrink-0 p-1.5 rounded-lg
          hover:bg-black/5 dark:hover:bg-white/5
          transition-colors duration-200
          focus:outline-none focus:ring-2 focus:ring-current
        "
        aria-label="Cerrar notificación"
        type="button"
      >
        <X className="w-4 h-4 opacity-70 hover:opacity-100 transition-opacity" aria-hidden="true" />
      </button>

      {/* Barra de progreso */}
      {duration > 0 && (
        <motion.div
          initial={{ scaleX: 1 }}
          animate={{ scaleX: 0 }}
          transition={{ duration: duration / 1000, ease: 'linear' }}
          className={`absolute bottom-0 left-0 right-0 h-1 ${styles.progress} rounded-b-xl origin-left`}
          aria-hidden="true"
        />
      )}
    </motion.div>
  );
}));

Toast.displayName = 'Toast';

export default Toast;