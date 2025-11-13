import { forwardRef, ReactNode, useEffect, useRef, useCallback, memo } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
;
import { useClickOutside, useKeyPress } from '../../hooks';
import { X } from 'lucide-react';

/* ==========================================================================
   🗨️ MODAL COMPONENT
   Modal accesible profesional con backdrop, animaciones y gestión de focus
   
   Principios aplicados:
   - Single Responsibility: Componente solo maneja modal UI
   - Open/Closed: Extensible vía props y sub-componentes
   - Interface Segregation: Props específicas para cada caso
   - Dependency Inversion: Usa hooks compartidos
   ========================================================================== */

export type ModalSize = 'sm' | 'md' | 'lg' | 'xl' | '2xl' | 'full';

export interface ModalProps {
  /** Si el modal está abierto */
  isOpen: boolean;
  
  /** Callback al cerrar */
  onClose: () => void;
  
  /** Título del modal */
  title?: string;
  
  /** Descripción opcional */
  description?: string;
  
  /** Tamaño del modal */
  size?: ModalSize;
  
  /** Cerrar al hacer click fuera */
  closeOnClickOutside?: boolean;
  
  /** Cerrar con tecla Escape */
  closeOnEscape?: boolean;
  
  /** Mostrar botón de cerrar */
  showClose?: boolean;
  
  /** Footer del modal */
  footer?: ReactNode;
  
  /** Children */
  children: ReactNode;
  
  /** Clase CSS adicional para el contenedor */
  className?: string;
  
  /** Clase CSS para el overlay */
  overlayClassName?: string;
  
  /** Prevenir cierre durante carga */
  preventClose?: boolean;
  
  /** ID único para ARIA */
  id?: string;
}

/**
 * Configuración de tamaños del modal
 * Separado para mejor mantenibilidad (Open/Closed Principle)
 */
const MODAL_SIZES: Record<ModalSize, string> = {
  sm: 'max-w-sm',
  md: 'max-w-md',
  lg: 'max-w-lg',
  xl: 'max-w-xl',
  '2xl': 'max-w-2xl',
  full: 'max-w-[95vw]',
} as const;

/**
 * Configuración de animaciones
 * Constantes para evitar recreación en cada render
 */
const ANIMATION_CONFIG = {
  backdrop: {
    initial: { opacity: 0 },
    animate: { opacity: 1 },
    exit: { opacity: 0 },
    transition: { duration: 0.2 },
  },
  modal: {
    initial: { opacity: 0, scale: 0.95, y: 20 },
    animate: { opacity: 1, scale: 1, y: 0 },
    exit: { opacity: 0, scale: 0.95, y: 20 },
    transition: {
      type: 'spring',
      stiffness: 300,
      damping: 30,
    },
  },
} as const;

/**
 * Selector de elementos enfocables (Focus Trap)
 */
const FOCUSABLE_ELEMENTS_SELECTOR = 
  'button:not(:disabled), [href], input:not(:disabled), select:not(:disabled), textarea:not(:disabled), [tabindex]:not([tabindex="-1"])';

/**
 * Hook personalizado para gestión de scroll lock
 * Separado para reutilización (Single Responsibility)
 */
const useScrollLock = (isLocked: boolean) => {
  useEffect(() => {
    if (!isLocked) return;

    const scrollbarWidth = window.innerWidth - document.documentElement.clientWidth;
    const originalOverflow = document.body.style.overflow;
    const originalPaddingRight = document.body.style.paddingRight;
    
    document.body.style.overflow = 'hidden';
    document.body.style.paddingRight = `${scrollbarWidth}px`;
    
    return () => {
      document.body.style.overflow = originalOverflow;
      document.body.style.paddingRight = originalPaddingRight;
    };
  }, [isLocked]);
};

/**
 * Hook personalizado para focus trap
 * Mantiene el foco dentro del modal (Accesibilidad)
 */
const useFocusTrap = (modalRef: React.RefObject<HTMLDivElement>, isOpen: boolean) => {
  useEffect(() => {
    if (!isOpen || !modalRef.current) return;

    const focusableElements = modalRef.current.querySelectorAll<HTMLElement>(
      FOCUSABLE_ELEMENTS_SELECTOR
    );
    
    const firstElement = focusableElements[0];
    const lastElement = focusableElements[focusableElements.length - 1];
    
    // Focus inicial
    firstElement?.focus();

    // Trap focus dentro del modal
    const handleTabKey = (e: KeyboardEvent) => {
      if (e.key !== 'Tab') return;

      if (e.shiftKey) {
        if (document.activeElement === firstElement) {
          e.preventDefault();
          lastElement?.focus();
        }
      } else {
        if (document.activeElement === lastElement) {
          e.preventDefault();
          firstElement?.focus();
        }
      }
    };

    document.addEventListener('keydown', handleTabKey);
    return () => document.removeEventListener('keydown', handleTabKey);
  }, [isOpen, modalRef]);
};

/**
 * Modal Component
 * 
 * Modal accesible con:
 * - 5 tamaños predefinidos
 * - Animaciones suaves
 * - Cierre con click outside o Escape
 * - Lock de scroll del body
 * - Gestión de focus automática
 * - ARIA compliant
 * 
 * @example
 * ```tsx
 * const [isOpen, setIsOpen] = useState(false);
 * 
 * <Modal
 *   isOpen={isOpen}
 *   onClose={() => setIsOpen(false)}
 *   title="Confirmar acción"
 *   description="¿Estás seguro de que deseas continuar?"
 *   footer={
 *     <div className="flex gap-2 justify-end">
 *       <Button variant="ghost" onClick={() => setIsOpen(false)}>
 *         Cancelar
 *       </Button>
 *       <Button onClick={handleConfirm}>
 *         Confirmar
 *       </Button>
 *     </div>
 *   }
 * >
 *   <p>Contenido del modal...</p>
 * </Modal>
 * ```
 */
export const Modal: React.FC<ModalProps> = memo(({
  isOpen,
  onClose,
  title,
  description,
  size = 'md',
  closeOnClickOutside = true,
  closeOnEscape = true,
  showClose = true,
  footer,
  children,
  className = '',
  overlayClassName = '',
  preventClose = false,
  id,
}) => {
  const modalRef = useRef<HTMLDivElement>(null);
  const modalId = id || `modal-${Math.random().toString(36).substr(2, 9)}`;
  
  // Callback memoizado para cierre (Performance)
  const handleClose = useCallback(() => {
    if (!preventClose) {
      onClose();
    }
  }, [onClose, preventClose]);
  
  // Cerrar con click fuera (solo si está habilitado y no está preventClose)
  useClickOutside(
    modalRef,
    handleClose,
    isOpen && closeOnClickOutside && !preventClose
  );
  
  // Cerrar con Escape (solo si está habilitado y no está preventClose)
  useKeyPress('Escape', handleClose, { 
    enabled: isOpen && closeOnEscape && !preventClose 
  });
  
  // Lock scroll del body
  useScrollLock(isOpen);
  
  // Focus trap para accesibilidad
  useFocusTrap(modalRef, isOpen);
  
  return (
    <AnimatePresence mode="wait">
      {isOpen && (
        <div
          className="fixed inset-0 z-50 flex items-center justify-center p-4"
          role="dialog"
          aria-modal="true"
          aria-labelledby={title ? `${modalId}-title` : undefined}
          aria-describedby={description ? `${modalId}-description` : undefined}
        >
          {/* Backdrop con gradiente sutil */}
          <motion.div
            {...ANIMATION_CONFIG.backdrop}
            className={`
              absolute inset-0 
              bg-gradient-to-br from-black/70 via-black/60 to-black/70 
              backdrop-blur-md
              ${overlayClassName}
            `}
            aria-hidden="true"
          />
          
          {/* Modal Container */}
          <motion.div
            ref={modalRef}
            {...ANIMATION_CONFIG.modal}
            className={`
              relative
              w-full
              ${MODAL_SIZES[size]}
              bg-white dark:bg-neutral-900
              rounded-2xl
              shadow-2xl
              border border-neutral-200/50 dark:border-neutral-800/50
              overflow-hidden
              max-h-[90vh]
              flex flex-col
              ${className}
            `}
          >
            {/* Header */}
            {(title || showClose) && (
              <div className="flex items-start justify-between gap-4 p-6 border-b border-neutral-200 dark:border-neutral-800 bg-neutral-50/50 dark:bg-neutral-800/30">
                <div className="flex-1 min-w-0">
                  {title && (
                    <h2
                      id={`${modalId}-title`}
                      className="text-xl font-semibold text-neutral-900 dark:text-neutral-100 leading-tight"
                    >
                      {title}
                    </h2>
                  )}
                  
                  {description && (
                    <p
                      id={`${modalId}-description`}
                      className="mt-1.5 text-sm text-neutral-600 dark:text-neutral-400 leading-relaxed"
                    >
                      {description}
                    </p>
                  )}
                </div>
                
                {showClose && (
                  <button
                    onClick={handleClose}
                    disabled={preventClose}
                    className="
                      flex-shrink-0 p-2 rounded-lg
                      text-neutral-500 hover:text-neutral-700
                      dark:text-neutral-400 dark:hover:text-neutral-200
                      hover:bg-neutral-200/50 dark:hover:bg-neutral-700/50
                      transition-all duration-200
                      focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2
                      disabled:opacity-50 disabled:cursor-not-allowed
                    "
                    aria-label="Cerrar modal"
                    type="button"
                  >
                    <X className="w-5 h-5" aria-hidden="true" />
                  </button>
                )}
              </div>
            )}
            
            {/* Body con scroll suave */}
            <div className="flex-1 overflow-y-auto p-6 scrollbar-thin">
              {children}
            </div>
            
            {/* Footer con mejor separación */}
            {footer && (
              <div className="p-6 border-t border-neutral-200 dark:border-neutral-800 bg-neutral-50/80 dark:bg-neutral-800/40">
                {footer}
              </div>
            )}
          </motion.div>
        </div>
      )}
    </AnimatePresence>
  );
});

Modal.displayName = 'Modal';

/**
 * ModalHeader - Header reutilizable para modales personalizados
 * Componente de composición (Open/Closed Principle)
 */
export interface ModalHeaderProps {
  title: string;
  description?: string;
  onClose?: () => void;
  showClose?: boolean;
}

export const ModalHeader = memo(forwardRef<HTMLDivElement, ModalHeaderProps>(
  ({ title, description, onClose, showClose = true }, ref) => (
    <div ref={ref} className="flex items-start justify-between gap-4 p-6 border-b border-neutral-200 dark:border-neutral-800 bg-neutral-50/50 dark:bg-neutral-800/30">
      <div className="flex-1 min-w-0">
        <h2 className="text-xl font-semibold text-neutral-900 dark:text-neutral-100 leading-tight">
          {title}
        </h2>
        
        {description && (
          <p className="mt-1.5 text-sm text-neutral-600 dark:text-neutral-400 leading-relaxed">
            {description}
          </p>
        )}
      </div>
      
      {showClose && onClose && (
        <button
          onClick={onClose}
          className="
            flex-shrink-0 p-2 rounded-lg
            text-neutral-500 hover:text-neutral-700
            dark:text-neutral-400 dark:hover:text-neutral-200
            hover:bg-neutral-200/50 dark:hover:bg-neutral-700/50
            transition-all duration-200
            focus:outline-none focus:ring-2 focus:ring-primary-500
          "
          aria-label="Cerrar"
          type="button"
        >
          <X className="w-5 h-5" aria-hidden="true" />
        </button>
      )}
    </div>
  )
));

ModalHeader.displayName = 'ModalHeader';

/**
 * ModalBody - Body reutilizable con scroll optimizado
 */
export interface ModalBodyProps {
  children: ReactNode;
  className?: string;
  noPadding?: boolean;
}

export const ModalBody = memo(forwardRef<HTMLDivElement, ModalBodyProps>(
  ({ children, className = '', noPadding = false }, ref) => (
    <div 
      ref={ref} 
      className={`
        ${noPadding ? '' : 'p-6'}
        ${className}
      `}
    >
      {children}
    </div>
  )
));

ModalBody.displayName = 'ModalBody';

/**
 * ModalFooter - Footer reutilizable con mejor layout
 */
export interface ModalFooterProps {
  children: ReactNode;
  className?: string;
  align?: 'left' | 'center' | 'right' | 'between';
}

export const ModalFooter = memo(forwardRef<HTMLDivElement, ModalFooterProps>(
  ({ children, className = '', align = 'right' }, ref) => {
    const alignClasses = {
      left: 'justify-start',
      center: 'justify-center',
      right: 'justify-end',
      between: 'justify-between',
    };
    
    return (
      <div
        ref={ref}
        className={`
          flex items-center gap-3
          ${alignClasses[align]}
          p-6 
          border-t border-neutral-200 dark:border-neutral-800 
          bg-neutral-50/80 dark:bg-neutral-800/40
          ${className}
        `}
      >
        {children}
      </div>
    );
  }
));

ModalFooter.displayName = 'ModalFooter';

export default Modal;
