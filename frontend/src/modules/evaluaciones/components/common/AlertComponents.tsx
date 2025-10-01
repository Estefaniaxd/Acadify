import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  CheckCircleIcon, 
  ExclamationCircleIcon, 
  InformationCircleIcon,
  XMarkIcon,
  XCircleIcon
} from '@heroicons/react/24/outline';

export type AlertType = 'success' | 'error' | 'warning' | 'info';

interface AlertProps {
  type: AlertType;
  title?: string;
  message: string;
  onClose?: () => void;
  autoClose?: boolean;
  autoCloseDelay?: number;
  actions?: React.ReactNode;
  className?: string;
}

const alertStyles = {
  success: {
    container: 'bg-green-50 dark:bg-green-900/20 border-green-200 dark:border-green-800',
    icon: 'text-green-600 dark:text-green-400',
    title: 'text-green-800 dark:text-green-300',
    message: 'text-green-700 dark:text-green-400',
    closeButton: 'text-green-600 hover:text-green-800 dark:text-green-400 dark:hover:text-green-300'
  },
  error: {
    container: 'bg-red-50 dark:bg-red-900/20 border-red-200 dark:border-red-800',
    icon: 'text-red-600 dark:text-red-400',
    title: 'text-red-800 dark:text-red-300',
    message: 'text-red-700 dark:text-red-400',
    closeButton: 'text-red-600 hover:text-red-800 dark:text-red-400 dark:hover:text-red-300'
  },
  warning: {
    container: 'bg-yellow-50 dark:bg-yellow-900/20 border-yellow-200 dark:border-yellow-800',
    icon: 'text-yellow-600 dark:text-yellow-400',
    title: 'text-yellow-800 dark:text-yellow-300',
    message: 'text-yellow-700 dark:text-yellow-400',
    closeButton: 'text-yellow-600 hover:text-yellow-800 dark:text-yellow-400 dark:hover:text-yellow-300'
  },
  info: {
    container: 'bg-blue-50 dark:bg-blue-900/20 border-blue-200 dark:border-blue-800',
    icon: 'text-blue-600 dark:text-blue-400',
    title: 'text-blue-800 dark:text-blue-300',
    message: 'text-blue-700 dark:text-blue-400',
    closeButton: 'text-blue-600 hover:text-blue-800 dark:text-blue-400 dark:hover:text-blue-300'
  }
};

const iconMap = {
  success: CheckCircleIcon,
  error: XCircleIcon,
  warning: ExclamationCircleIcon,
  info: InformationCircleIcon
};

export function Alert({
  type,
  title,
  message,
  onClose,
  autoClose = false,
  autoCloseDelay = 5000,
  actions,
  className = ''
}: AlertProps) {
  const [visible, setVisible] = React.useState(true);
  const styles = alertStyles[type];
  const IconComponent = iconMap[type];

  React.useEffect(() => {
    if (autoClose && autoCloseDelay > 0) {
      const timer = setTimeout(() => {
        handleClose();
      }, autoCloseDelay);

      return () => clearTimeout(timer);
    }
  }, [autoClose, autoCloseDelay]);

  const handleClose = () => {
    setVisible(false);
    setTimeout(() => {
      onClose?.();
    }, 150); // Esperar a que termine la animación
  };

  if (!visible) return null;

  return (
    <motion.div
      initial={{ opacity: 0, y: -10, scale: 0.95 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      exit={{ opacity: 0, y: -10, scale: 0.95 }}
      className={`
        relative rounded-lg border p-4 shadow-sm
        ${styles.container}
        ${className}
      `}
    >
      <div className="flex items-start">
        <IconComponent className={`h-5 w-5 mt-0.5 flex-shrink-0 ${styles.icon}`} />
        
        <div className="ml-3 flex-1">
          {title && (
            <h3 className={`text-sm font-medium ${styles.title}`}>
              {title}
            </h3>
          )}
          <div className={`${title ? 'mt-1' : ''} text-sm ${styles.message}`}>
            {message}
          </div>
          
          {actions && (
            <div className="mt-3">
              {actions}
            </div>
          )}
        </div>

        {onClose && (
          <button
            onClick={handleClose}
            className={`
              ml-3 flex-shrink-0 rounded-md p-1.5 transition-colors
              focus:outline-none focus:ring-2 focus:ring-offset-2
              ${styles.closeButton}
            `}
          >
            <XMarkIcon className="h-4 w-4" />
          </button>
        )}
      </div>
    </motion.div>
  );
}

interface ToastProps extends Omit<AlertProps, 'className'> {
  id: string;
  position?: 'top-right' | 'top-left' | 'bottom-right' | 'bottom-left' | 'top-center' | 'bottom-center';
}

export function Toast({
  id,
  type,
  title,
  message,
  onClose,
  autoClose = true,
  autoCloseDelay = 5000,
  actions,
  position = 'top-right'
}: ToastProps) {
  return (
    <Alert
      type={type}
      title={title}
      message={message}
      onClose={onClose}
      autoClose={autoClose}
      autoCloseDelay={autoCloseDelay}
      actions={actions}
      className="min-w-80 max-w-md shadow-lg"
    />
  );
}

interface ToastContainerProps {
  toasts: ToastProps[];
  position?: ToastProps['position'];
}

const positionClasses = {
  'top-right': 'top-4 right-4',
  'top-left': 'top-4 left-4',
  'bottom-right': 'bottom-4 right-4',
  'bottom-left': 'bottom-4 left-4',
  'top-center': 'top-4 left-1/2 -translate-x-1/2',
  'bottom-center': 'bottom-4 left-1/2 -translate-x-1/2'
};

export function ToastContainer({ toasts, position = 'top-right' }: ToastContainerProps) {
  return (
    <div className={`fixed z-50 ${positionClasses[position]} space-y-3`}>
      <AnimatePresence>
        {toasts.map((toast) => (
          <Toast key={toast.id} {...toast} />
        ))}
      </AnimatePresence>
    </div>
  );
}

// Hook para manejar toasts
interface UseToastReturn {
  toasts: ToastProps[];
  showToast: (toast: Omit<ToastProps, 'id'>) => string;
  hideToast: (id: string) => void;
  hideAllToasts: () => void;
}

export function useToast(): UseToastReturn {
  const [toasts, setToasts] = React.useState<ToastProps[]>([]);

  const showToast = React.useCallback((toast: Omit<ToastProps, 'id'>) => {
    const id = Math.random().toString(36).substr(2, 9);
    const newToast: ToastProps = {
      ...toast,
      id,
      onClose: () => hideToast(id)
    };

    setToasts(prev => [...prev, newToast]);
    return id;
  }, []);

  const hideToast = React.useCallback((id: string) => {
    setToasts(prev => prev.filter(toast => toast.id !== id));
  }, []);

  const hideAllToasts = React.useCallback(() => {
    setToasts([]);
  }, []);

  return {
    toasts,
    showToast,
    hideToast,
    hideAllToasts
  };
}

interface ConfirmDialogProps {
  isOpen: boolean;
  onClose: () => void;
  onConfirm: () => void;
  title: string;
  message: string;
  confirmText?: string;
  cancelText?: string;
  type?: AlertType;
  loading?: boolean;
}

export function ConfirmDialog({
  isOpen,
  onClose,
  onConfirm,
  title,
  message,
  confirmText = 'Confirmar',
  cancelText = 'Cancelar',
  type = 'warning',
  loading = false
}: ConfirmDialogProps) {
  const styles = alertStyles[type];
  const IconComponent = iconMap[type];

  if (!isOpen) return null;

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm"
        onClick={onClose}
      >
        <motion.div
          initial={{ scale: 0.9, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          exit={{ scale: 0.9, opacity: 0 }}
          className="relative bg-white dark:bg-gray-800 rounded-2xl shadow-2xl border border-gray-200 dark:border-gray-700 p-6 w-full max-w-md mx-4"
          onClick={(e) => e.stopPropagation()}
        >
          <div className="flex items-start">
            <div className={`flex-shrink-0 ${styles.icon}`}>
              <IconComponent className="h-6 w-6" />
            </div>
            
            <div className="ml-4 flex-1">
              <h3 className={`text-lg font-medium ${styles.title}`}>
                {title}
              </h3>
              <p className={`mt-2 text-sm ${styles.message}`}>
                {message}
              </p>
            </div>
          </div>

          <div className="mt-6 flex justify-end space-x-3">
            <button
              onClick={onClose}
              disabled={loading}
              className="px-4 py-2 text-sm font-medium text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-600 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              {cancelText}
            </button>
            <button
              onClick={onConfirm}
              disabled={loading}
              className={`
                px-4 py-2 text-sm font-medium text-white rounded-lg
                focus:outline-none focus:ring-2 focus:ring-offset-2
                disabled:opacity-50 disabled:cursor-not-allowed
                transition-colors
                ${type === 'error' ? 'bg-red-600 hover:bg-red-700 focus:ring-red-500' : ''}
                ${type === 'warning' ? 'bg-yellow-600 hover:bg-yellow-700 focus:ring-yellow-500' : ''}
                ${type === 'success' ? 'bg-green-600 hover:bg-green-700 focus:ring-green-500' : ''}
                ${type === 'info' ? 'bg-blue-600 hover:bg-blue-700 focus:ring-blue-500' : ''}
                ${loading ? 'cursor-wait' : ''}
              `}
            >
              {loading ? (
                <div className="flex items-center space-x-2">
                  <div className="w-4 h-4 border-2 border-white/20 border-t-white rounded-full animate-spin" />
                  <span>Procesando...</span>
                </div>
              ) : (
                confirmText
              )}
            </button>
          </div>
        </motion.div>
      </motion.div>
    </AnimatePresence>
  );
}