import React, { useEffect, forwardRef } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { FiCheckCircle, FiAlertCircle, FiInfo, FiX } from 'react-icons/fi'

export interface ToastProps {
  id: string
  type: 'success' | 'error' | 'info' | 'warning'
  title: string
  message?: string
  duration?: number
  onClose: (id: string) => void
}

const Toast = forwardRef<HTMLDivElement, ToastProps>(({
  id,
  type,
  title,
  message,
  duration = 5000,
  onClose
}, ref) => {
  useEffect(() => {
    if (duration > 0) {
      const timer = setTimeout(() => {
        onClose(id)
      }, duration)
      return () => clearTimeout(timer)
    }
  }, [id, duration, onClose])

  const getIcon = () => {
    switch (type) {
      case 'success':
        return <FiCheckCircle className="w-5 h-5" />
      case 'error':
        return <FiAlertCircle className="w-5 h-5" />
      case 'warning':
        return <FiAlertCircle className="w-5 h-5" />
      default:
        return <FiInfo className="w-5 h-5" />
    }
  }

  const getColorClasses = () => {
    switch (type) {
      case 'success':
        return 'from-emerald-500/20 to-green-500/20 border-emerald-500/30 text-emerald-100'
      case 'error':
        return 'from-red-500/20 to-rose-500/20 border-red-500/30 text-red-100'
      case 'warning':
        return 'from-amber-500/20 to-yellow-500/20 border-amber-500/30 text-amber-100'
      default:
        return 'from-blue-500/20 to-indigo-500/20 border-blue-500/30 text-blue-100'
    }
  }

  const getIconColorClasses = () => {
    switch (type) {
      case 'success':
        return 'text-emerald-400'
      case 'error':
        return 'text-red-400'
      case 'warning':
        return 'text-amber-400'
      default:
        return 'text-blue-400'
    }
  }

  return (
    <motion.div
      ref={ref}
      initial={{ opacity: 0, x: 300, scale: 0.8 }}
      animate={{ opacity: 1, x: 0, scale: 1 }}
      exit={{ opacity: 0, x: 300, scale: 0.8 }}
      transition={{ 
        type: "spring",
        stiffness: 500,
        damping: 30,
        mass: 0.5
      }}
      className={`
        relative flex items-start gap-3 p-4 min-w-[320px] max-w-[400px]
        bg-gradient-to-r ${getColorClasses()}
        backdrop-blur-xl border rounded-2xl shadow-2xl
        before:absolute before:inset-0 before:rounded-2xl 
        before:bg-gradient-to-r before:from-white/10 before:to-white/5
        before:backdrop-blur-xl before:-z-10
      `}
    >
      {/* Icono */}
      <div className={`flex-shrink-0 ${getIconColorClasses()}`}>
        {getIcon()}
      </div>

      {/* Contenido */}
      <div className="flex-1 min-w-0">
        <h4 className="font-semibold text-sm mb-1">
          {title}
        </h4>
        {message && (
          <p className="text-xs opacity-80 leading-relaxed">
            {message}
          </p>
        )}
      </div>

      {/* Botón cerrar */}
      <button
        onClick={() => onClose(id)}
        className="flex-shrink-0 p-1 rounded-lg hover:bg-white/10 transition-colors duration-200"
      >
        <FiX className="w-4 h-4 opacity-60 hover:opacity-100" />
      </button>

      {/* Barra de progreso */}
      {duration > 0 && (
        <motion.div
          initial={{ width: "100%" }}
          animate={{ width: "0%" }}
          transition={{ duration: duration / 1000, ease: "linear" }}
          className="absolute bottom-0 left-0 h-1 bg-white/30 rounded-b-2xl"
        />
      )}
    </motion.div>
  )
})

Toast.displayName = 'Toast'

export default Toast