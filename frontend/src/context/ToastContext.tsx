import React, { createContext, useContext, useState, useCallback } from 'react'
import { AnimatePresence } from 'framer-motion'
import Toast, { ToastProps } from '../components/ui/Toast'

interface ToastContextType {
  success: (title: string, message?: string, duration?: number) => void
  error: (title: string, message?: string, duration?: number) => void
  info: (title: string, message?: string, duration?: number) => void
  warning: (title: string, message?: string, duration?: number) => void
}

const ToastContext = createContext<ToastContextType | undefined>(undefined)

export const useToast = () => {
  const context = useContext(ToastContext)
  if (!context) {
    throw new Error('useToast debe usarse dentro de ToastProvider')
  }
  return context
}

interface ToastProviderProps {
  children: React.ReactNode
}

export const ToastProvider: React.FC<ToastProviderProps> = ({ children }) => {
  const [toasts, setToasts] = useState<ToastProps[]>([])

  const addToast = useCallback((
    type: ToastProps['type'],
    title: string,
    message?: string,
    duration?: number
  ) => {
    const id = Date.now().toString() + Math.random().toString(36).substr(2, 9)
    const newToast: ToastProps = {
      id,
      type,
      title,
      message,
      duration,
      onClose: removeToast
    }
    
    setToasts(prev => [...prev, newToast])
  }, [])

  const removeToast = useCallback((id: string) => {
    setToasts(prev => prev.filter(toast => toast.id !== id))
  }, [])

  const success = useCallback((title: string, message?: string, duration?: number) => {
    addToast('success', title, message, duration)
  }, [addToast])

  const error = useCallback((title: string, message?: string, duration?: number) => {
    addToast('error', title, message, duration)
  }, [addToast])

  const info = useCallback((title: string, message?: string, duration?: number) => {
    addToast('info', title, message, duration)
  }, [addToast])

  const warning = useCallback((title: string, message?: string, duration?: number) => {
    addToast('warning', title, message, duration)
  }, [addToast])

  return (
    <ToastContext.Provider value={{ success, error, info, warning }}>
      {children}
      
      {/* Contenedor de notificaciones */}
      <div className="fixed top-4 right-4 z-[9999] space-y-3">
        <AnimatePresence mode="popLayout">
          {toasts.map((toast) => (
            <Toast key={toast.id} {...toast} />
          ))}
        </AnimatePresence>
      </div>
    </ToastContext.Provider>
  )
}

export default ToastProvider