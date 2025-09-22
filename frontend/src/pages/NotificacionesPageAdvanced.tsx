import React, { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { useToast } from '../context/ToastContext'
import { 
  FiBell, 
  FiCheck, 
  FiTrash2, 
  FiSettings, 
  FiFilter,
  FiSearch,
  FiMoreHorizontal,
  FiStar,
  FiHeart,
  FiMessageSquare,
  FiUsers,
  FiCalendar,
  FiTrendingUp,
  FiAward,
  FiBookOpen,
  FiMail,
  FiAlertCircle,
  FiInfo,
  FiCheckCircle,
  FiX,
  FiChevronDown,
  FiRefreshCw
} from 'react-icons/fi'
import { HiSparkles } from 'react-icons/hi'

interface Notification {
  id: string
  type: 'message' | 'achievement' | 'grade' | 'reminder' | 'social' | 'system' | 'announcement'
  title: string
  description: string
  timestamp: string
  read: boolean
  priority: 'low' | 'medium' | 'high'
  actionUrl?: string
  avatar?: string
  metadata?: any
}

const mockNotifications: Notification[] = [
  {
    id: '1',
    type: 'achievement',
    title: '¡Nuevo logro desbloqueado!',
    description: 'Has completado tu primera semana de estudio consecutiva. ¡Sigue así!',
    timestamp: '2025-09-21T10:30:00Z',
    read: false,
    priority: 'high',
    actionUrl: '/logros',
    metadata: { achievement: 'Racha de 7 días', points: 100 }
  },
  {
    id: '2',
    type: 'grade',
    title: 'Nueva calificación disponible',
    description: 'Tu profesor ha calificado el ensayo de Literatura Española.',
    timestamp: '2025-09-21T09:15:00Z',
    read: false,
    priority: 'high',
    actionUrl: '/cursos/literatura',
    avatar: 'Prof. Hernández',
    metadata: { grade: 92, subject: 'Literatura Española' }
  },
  {
    id: '3',
    type: 'message',
    title: 'Nuevo mensaje de Ana García',
    description: '¿Quieres formar equipo para el proyecto final de matemáticas?',
    timestamp: '2025-09-21T08:45:00Z',
    read: true,
    priority: 'medium',
    actionUrl: '/mensajes/ana-garcia',
    avatar: 'Ana García'
  },
  {
    id: '4',
    type: 'reminder',
    title: 'Recordatorio de clase',
    description: 'Tu clase de Química Orgánica comienza en 30 minutos.',
    timestamp: '2025-09-21T08:30:00Z',
    read: false,
    priority: 'high',
    actionUrl: '/clases/quimica-organica',
    metadata: { subject: 'Química Orgánica', room: 'Lab 204' }
  },
  {
    id: '5',
    type: 'social',
    title: 'Nuevo seguidor',
    description: 'Carlos López ahora te sigue. ¡Conecta con él!',
    timestamp: '2025-09-20T19:20:00Z',
    read: true,
    priority: 'low',
    actionUrl: '/perfil/carlos-lopez',
    avatar: 'Carlos López'
  },
  {
    id: '6',
    type: 'announcement',
    title: 'Actualización del sistema',
    description: 'Hemos añadido nuevas funciones de estudio colaborativo.',
    timestamp: '2025-09-20T16:00:00Z',
    read: false,
    priority: 'medium',
    actionUrl: '/novedades',
    metadata: { version: '2.1.0' }
  },
  {
    id: '7',
    type: 'system',
    title: 'Respaldo de datos completado',
    description: 'Tus datos han sido respaldados exitosamente.',
    timestamp: '2025-09-20T14:30:00Z',
    read: true,
    priority: 'low'
  }
]

export default function NotificacionesPageAdvanced() {
  const toast = useToast()
  const [notifications, setNotifications] = useState<Notification[]>(mockNotifications)
  const [filter, setFilter] = useState<'all' | 'unread' | 'read'>('all')
  const [typeFilter, setTypeFilter] = useState<string>('all')
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedNotifications, setSelectedNotifications] = useState<Set<string>>(new Set())
  const [showFilters, setShowFilters] = useState(false)

  const notificationTypes = [
    { id: 'all', label: 'Todas', icon: FiBell, color: 'text-gray-500' },
    { id: 'message', label: 'Mensajes', icon: FiMessageSquare, color: 'text-blue-500' },
    { id: 'achievement', label: 'Logros', icon: FiAward, color: 'text-yellow-500' },
    { id: 'grade', label: 'Calificaciones', icon: FiStar, color: 'text-green-500' },
    { id: 'reminder', label: 'Recordatorios', icon: FiCalendar, color: 'text-orange-500' },
    { id: 'social', label: 'Social', icon: FiUsers, color: 'text-purple-500' },
    { id: 'announcement', label: 'Anuncios', icon: FiInfo, color: 'text-indigo-500' },
    { id: 'system', label: 'Sistema', icon: FiSettings, color: 'text-gray-500' }
  ]

  const getTypeIcon = (type: string) => {
    const typeConfig = notificationTypes.find(t => t.id === type)
    return typeConfig || notificationTypes[0]
  }

  const formatTimestamp = (timestamp: string) => {
    const date = new Date(timestamp)
    const now = new Date()
    const diffInHours = Math.floor((now.getTime() - date.getTime()) / (1000 * 60 * 60))
    
    if (diffInHours < 1) return 'Hace unos minutos'
    if (diffInHours < 24) return `Hace ${diffInHours} horas`
    if (diffInHours < 48) return 'Ayer'
    return date.toLocaleDateString()
  }

  const filteredNotifications = notifications.filter(notification => {
    const matchesFilter = filter === 'all' || 
      (filter === 'read' && notification.read) || 
      (filter === 'unread' && !notification.read)
    
    const matchesType = typeFilter === 'all' || notification.type === typeFilter
    
    const matchesSearch = searchQuery === '' || 
      notification.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      notification.description.toLowerCase().includes(searchQuery.toLowerCase())
    
    return matchesFilter && matchesType && matchesSearch
  })

  const markAsRead = (id: string) => {
    setNotifications(prev => 
      prev.map(n => n.id === id ? { ...n, read: true } : n)
    )
  }

  const markAllAsRead = () => {
    setNotifications(prev => prev.map(n => ({ ...n, read: true })))
    toast.success('¡Listo!', 'Todas las notificaciones han sido marcadas como leídas.')
  }

  const deleteNotification = (id: string) => {
    setNotifications(prev => prev.filter(n => n.id !== id))
    toast.success('Eliminada', 'La notificación ha sido eliminada.')
  }

  const toggleSelection = (id: string) => {
    setSelectedNotifications(prev => {
      const newSet = new Set(prev)
      if (newSet.has(id)) {
        newSet.delete(id)
      } else {
        newSet.add(id)
      }
      return newSet
    })
  }

  const deleteSelected = () => {
    setNotifications(prev => prev.filter(n => !selectedNotifications.has(n.id)))
    setSelectedNotifications(new Set())
    toast.success('Eliminadas', `${selectedNotifications.size} notificaciones eliminadas.`)
  }

  const unreadCount = notifications.filter(n => !n.read).length

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 via-blue-50/30 to-indigo-50/50 dark:from-gray-900 dark:via-gray-900 dark:to-blue-950/30">
      {/* Header */}
      <div className="bg-white/80 dark:bg-gray-900/80 backdrop-blur-xl border-b border-gray-200/50 dark:border-gray-700/50 sticky top-0 z-40">
        <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center space-x-3">
              <div className="relative">
                <div className="w-10 h-10 bg-gradient-to-r from-blue-500 to-indigo-600 rounded-xl flex items-center justify-center">
                  <FiBell className="w-6 h-6 text-white" />
                </div>
                {unreadCount > 0 && (
                  <motion.div
                    initial={{ scale: 0 }}
                    animate={{ scale: 1 }}
                    className="absolute -top-1 -right-1 w-5 h-5 bg-red-500 rounded-full flex items-center justify-center"
                  >
                    <span className="text-xs font-bold text-white">{unreadCount}</span>
                  </motion.div>
                )}
              </div>
              <div>
                <h1 className="text-xl font-bold text-gray-900 dark:text-white">
                  Notificaciones
                </h1>
                <p className="text-sm text-gray-500 dark:text-gray-400">
                  {unreadCount > 0 ? `${unreadCount} sin leer` : 'Todo al día'}
                </p>
              </div>
            </div>

            <div className="flex items-center space-x-2">
              {selectedNotifications.size > 0 && (
                <motion.button
                  initial={{ opacity: 0, scale: 0.8 }}
                  animate={{ opacity: 1, scale: 1 }}
                  onClick={deleteSelected}
                  className="flex items-center space-x-1 px-3 py-1.5 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors text-sm"
                >
                  <FiTrash2 className="w-4 h-4" />
                  <span>Eliminar ({selectedNotifications.size})</span>
                </motion.button>
              )}
              
              {unreadCount > 0 && (
                <motion.button
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  onClick={markAllAsRead}
                  className="flex items-center space-x-1 px-3 py-1.5 bg-emerald-600 text-white rounded-lg hover:bg-emerald-700 transition-colors text-sm"
                >
                  <FiCheckCircle className="w-4 h-4" />
                  <span>Marcar todas</span>
                </motion.button>
              )}

              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={() => setShowFilters(!showFilters)}
                className="p-2 text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
              >
                <FiFilter className="w-5 h-5" />
              </motion.button>
            </div>
          </div>
        </div>
      </div>

      {/* Filters */}
      <AnimatePresence>
        {showFilters && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            className="bg-white/80 dark:bg-gray-900/80 backdrop-blur-xl border-b border-gray-200/50 dark:border-gray-700/50"
          >
            <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
              <div className="space-y-4">
                {/* Search */}
                <div className="relative">
                  <FiSearch className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
                  <input
                    type="text"
                    placeholder="Buscar notificaciones..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    className="w-full pl-10 pr-4 py-2 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>

                {/* Filter buttons */}
                <div className="flex flex-wrap gap-2">
                  <div className="flex items-center space-x-2">
                    <span className="text-sm font-medium text-gray-600 dark:text-gray-400">Estado:</span>
                    {[
                      { id: 'all', label: 'Todas' },
                      { id: 'unread', label: 'Sin leer' },
                      { id: 'read', label: 'Leídas' }
                    ].map((option) => (
                      <button
                        key={option.id}
                        onClick={() => setFilter(option.id as any)}
                        className={`px-3 py-1 text-xs rounded-full transition-colors ${
                          filter === option.id
                            ? 'bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-300'
                            : 'bg-gray-100 text-gray-600 dark:bg-gray-800 dark:text-gray-400 hover:bg-gray-200 dark:hover:bg-gray-700'
                        }`}
                      >
                        {option.label}
                      </button>
                    ))}
                  </div>

                  <div className="flex items-center space-x-2">
                    <span className="text-sm font-medium text-gray-600 dark:text-gray-400">Tipo:</span>
                    {notificationTypes.slice(0, 5).map((type) => (
                      <button
                        key={type.id}
                        onClick={() => setTypeFilter(type.id)}
                        className={`flex items-center space-x-1 px-3 py-1 text-xs rounded-full transition-colors ${
                          typeFilter === type.id
                            ? 'bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-300'
                            : 'bg-gray-100 text-gray-600 dark:bg-gray-800 dark:text-gray-400 hover:bg-gray-200 dark:hover:bg-gray-700'
                        }`}
                      >
                        <type.icon className="w-3 h-3" />
                        <span>{type.label}</span>
                      </button>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Notifications List */}
      <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {filteredNotifications.length === 0 ? (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="text-center py-16"
          >
            <div className="w-24 h-24 bg-gray-100 dark:bg-gray-800 rounded-2xl flex items-center justify-center mx-auto mb-4">
              <FiBell className="w-12 h-12 text-gray-400" />
            </div>
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
              No hay notificaciones
            </h3>
            <p className="text-gray-500 dark:text-gray-400">
              {searchQuery ? 'No se encontraron resultados para tu búsqueda.' : 'Todas tus notificaciones aparecerán aquí.'}
            </p>
          </motion.div>
        ) : (
          <div className="space-y-3">
            {filteredNotifications.map((notification, index) => {
              const typeConfig = getTypeIcon(notification.type)
              const isSelected = selectedNotifications.has(notification.id)
              
              return (
                <motion.div
                  key={notification.id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.05 }}
                  className={`bg-white/80 dark:bg-gray-800/80 backdrop-blur-xl rounded-xl border transition-all duration-200 overflow-hidden hover:shadow-lg ${
                    !notification.read 
                      ? 'border-blue-200/50 dark:border-blue-700/50 bg-blue-50/30 dark:bg-blue-900/10' 
                      : 'border-gray-200/50 dark:border-gray-700/50'
                  } ${
                    isSelected ? 'ring-2 ring-blue-500' : ''
                  }`}
                >
                  <div className="p-4">
                    <div className="flex items-start justify-between">
                      <div className="flex items-start space-x-3 flex-1">
                        {/* Selection checkbox */}
                        <input
                          type="checkbox"
                          checked={isSelected}
                          onChange={() => toggleSelection(notification.id)}
                          className="mt-1 w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                        />

                        {/* Type icon */}
                        <div className={`w-10 h-10 rounded-xl flex items-center justify-center ${
                          notification.priority === 'high' ? 'bg-red-100 dark:bg-red-900/30' :
                          notification.priority === 'medium' ? 'bg-yellow-100 dark:bg-yellow-900/30' :
                          'bg-gray-100 dark:bg-gray-800'
                        }`}>
                          <typeConfig.icon className={`w-5 h-5 ${typeConfig.color}`} />
                        </div>

                        {/* Content */}
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center space-x-2 mb-1">
                            <h4 className={`font-semibold ${
                              !notification.read ? 'text-gray-900 dark:text-white' : 'text-gray-700 dark:text-gray-300'
                            }`}>
                              {notification.title}
                            </h4>
                            {!notification.read && (
                              <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
                            )}
                            {notification.priority === 'high' && (
                              <FiAlertCircle className="w-4 h-4 text-red-500" />
                            )}
                          </div>
                          
                          <p className="text-sm text-gray-600 dark:text-gray-400 mb-2">
                            {notification.description}
                          </p>

                          {/* Metadata */}
                          {notification.metadata && (
                            <div className="flex items-center space-x-4 text-xs text-gray-500 dark:text-gray-400">
                              {notification.metadata.grade && (
                                <span className="font-medium text-emerald-600 dark:text-emerald-400">
                                  Calificación: {notification.metadata.grade}%
                                </span>
                              )}
                              {notification.metadata.points && (
                                <span className="font-medium text-amber-600 dark:text-amber-400">
                                  +{notification.metadata.points} puntos
                                </span>
                              )}
                              {notification.metadata.subject && (
                                <span>{notification.metadata.subject}</span>
                              )}
                            </div>
                          )}

                          <div className="flex items-center justify-between mt-3">
                            <span className="text-xs text-gray-400">
                              {formatTimestamp(notification.timestamp)}
                            </span>
                            
                            {notification.actionUrl && (
                              <motion.button
                                whileHover={{ scale: 1.05 }}
                                whileTap={{ scale: 0.95 }}
                                className="text-xs font-medium text-blue-600 dark:text-blue-400 hover:text-blue-700 dark:hover:text-blue-300"
                              >
                                Ver detalles →
                              </motion.button>
                            )}
                          </div>
                        </div>
                      </div>

                      {/* Actions */}
                      <div className="flex items-center space-x-1 ml-3">
                        {!notification.read && (
                          <motion.button
                            whileHover={{ scale: 1.1 }}
                            whileTap={{ scale: 0.9 }}
                            onClick={() => markAsRead(notification.id)}
                            className="p-1.5 text-gray-400 hover:text-blue-600 dark:hover:text-blue-400 rounded-lg hover:bg-blue-50 dark:hover:bg-blue-900/30 transition-colors"
                            title="Marcar como leída"
                          >
                            <FiCheck className="w-4 h-4" />
                          </motion.button>
                        )}
                        
                        <motion.button
                          whileHover={{ scale: 1.1 }}
                          whileTap={{ scale: 0.9 }}
                          onClick={() => deleteNotification(notification.id)}
                          className="p-1.5 text-gray-400 hover:text-red-600 dark:hover:text-red-400 rounded-lg hover:bg-red-50 dark:hover:bg-red-900/30 transition-colors"
                          title="Eliminar"
                        >
                          <FiTrash2 className="w-4 h-4" />
                        </motion.button>
                      </div>
                    </div>
                  </div>
                </motion.div>
              )
            })}
          </div>
        )}
      </div>
    </div>
  )
}