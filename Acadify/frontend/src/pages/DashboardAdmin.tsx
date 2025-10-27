import React, { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { useAuth } from '../context/AuthContext'
import { useNavigate } from 'react-router-dom'
import { 
  FiUsers, 
  FiSettings, 
  FiBarChart, 
  FiShield,
  FiDatabase,
  FiMonitor,
  FiActivity,
  FiTrendingUp,
  FiCheckCircle,
  FiAlertTriangle,
  FiMoreVertical,
  FiPlus
} from 'react-icons/fi'
import { HiOutlineOfficeBuilding } from 'react-icons/hi'

interface AdminStats {
  totalUsers: number
  totalInstitutions: number
  activeCoordinators: number
  systemUptime: string
}

interface SystemAlert {
  id: string
  type: 'warning' | 'error' | 'info'
  message: string
  timestamp: string
}

export default function AdminDashboard() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()
  const [activeTab, setActiveTab] = useState<'overview' | 'users' | 'institutions' | 'system'>('overview')

  const stats: AdminStats = {
    totalUsers: 1247,
    totalInstitutions: 23,
    activeCoordinators: 45,
    systemUptime: '99.9%'
  }

  const alerts: SystemAlert[] = [
    {
      id: '1',
      type: 'warning',
      message: 'Servidor de backup requiere actualización',
      timestamp: '2 horas'
    },
    {
      id: '2',
      type: 'info',
      message: 'Nueva institución registrada: Universidad Central',
      timestamp: '4 horas'
    }
  ]

  return (
    <div className="bg-gradient-to-br from-gray-50 via-white to-gray-100 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900 mt-6">
      {/* Header */}
      <div className="bg-white/80 dark:bg-gray-800/80 backdrop-blur-xl border-b border-gray-200/50 dark:border-gray-700/50 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-3">
                <div className="w-10 h-10 bg-gradient-to-r from-red-500 to-pink-600 rounded-xl flex items-center justify-center">
                  <FiShield className="w-6 h-6 text-white" />
                </div>
                <div>
                  <h1 className="text-xl font-bold text-gray-900 dark:text-white">
                    Panel de Administrador
                  </h1>
                  <p className="text-sm text-gray-500 dark:text-gray-400">
                    ¡Hola, {user?.username || 'Admin'}!
                  </p>
                </div>
              </div>
            </div>

            <div className="flex items-center space-x-4">
              <div className="flex bg-gray-100 dark:bg-gray-800 rounded-lg p-1">
                {[
                  { key: 'overview', label: 'Resumen', icon: FiTrendingUp },
                  { key: 'users', label: 'Usuarios', icon: FiUsers },
                  { key: 'institutions', label: 'Instituciones', icon: HiOutlineOfficeBuilding },
                  { key: 'system', label: 'Sistema', icon: FiMonitor }
                ].map((tab) => (
                  <button
                    key={tab.key}
                    onClick={() => setActiveTab(tab.key as any)}
                    className={`
                      flex items-center space-x-2 px-3 py-2 rounded-md text-sm font-medium transition-all duration-200
                      ${activeTab === tab.key 
                        ? 'bg-white dark:bg-gray-700 text-red-600 dark:text-red-400 shadow-sm' 
                        : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-200'
                      }
                    `}
                  >
                    <tab.icon className="w-4 h-4" />
                    <span className="hidden sm:block">{tab.label}</span>
                  </button>
                ))}
              </div>

              <button
                onClick={logout}
                className="text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 transition-colors"
              >
                Salir
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <AnimatePresence mode="wait">
          {activeTab === 'overview' && (
            <motion.div
              key="overview"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              transition={{ duration: 0.3 }}
              className="space-y-8"
            >
              {/* Quick Stats */}
              <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
                {[
                  { label: 'Total Usuarios', value: stats.totalUsers.toLocaleString(), icon: FiUsers, color: 'from-blue-500 to-indigo-600' },
                  { label: 'Instituciones', value: stats.totalInstitutions.toString(), icon: HiOutlineOfficeBuilding, color: 'from-emerald-500 to-teal-600' },
                  { label: 'Coordinadores Activos', value: stats.activeCoordinators.toString(), icon: FiSettings, color: 'from-purple-500 to-pink-600' },
                  { label: 'Tiempo Activo Sistema', value: stats.systemUptime, icon: FiActivity, color: 'from-orange-500 to-red-600' }
                ].map((stat, index) => (
                  <motion.div
                    key={stat.label}
                    initial={{ opacity: 0, scale: 0.9 }}
                    animate={{ opacity: 1, scale: 1 }}
                    transition={{ delay: index * 0.1, duration: 0.3 }}
                    className="bg-white/80 dark:bg-gray-800/80 backdrop-blur-xl rounded-2xl p-6 border border-gray-200/50 dark:border-gray-700/50"
                  >
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-sm font-medium text-gray-600 dark:text-gray-400">{stat.label}</p>
                        <p className="text-2xl font-bold text-gray-900 dark:text-white mt-1">{stat.value}</p>
                      </div>
                      <div className={`w-12 h-12 bg-gradient-to-r ${stat.color} rounded-xl flex items-center justify-center`}>
                        <stat.icon className="w-6 h-6 text-white" />
                      </div>
                    </div>
                  </motion.div>
                ))}
              </div>

              {/* System Alerts */}
              <div className="bg-white/80 dark:bg-gray-800/80 backdrop-blur-xl rounded-2xl p-6 border border-gray-200/50 dark:border-gray-700/50">
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Alertas del Sistema</h3>
                <div className="space-y-3">
                  {alerts.map((alert) => (
                    <div key={alert.id} className="flex items-center justify-between p-3 rounded-lg bg-gray-50 dark:bg-gray-700/50">
                      <div className="flex items-center space-x-3">
                        {alert.type === 'warning' && <FiAlertTriangle className="w-5 h-5 text-orange-500" />}
                        {alert.type === 'error' && <FiAlertTriangle className="w-5 h-5 text-red-500" />}
                        {alert.type === 'info' && <FiCheckCircle className="w-5 h-5 text-blue-500" />}
                        <div>
                          <p className="text-sm font-medium text-gray-900 dark:text-white">{alert.message}</p>
                          <p className="text-xs text-gray-500 dark:text-gray-400">Hace {alert.timestamp}</p>
                        </div>
                      </div>
                      <button className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300">
                        <FiMoreVertical className="w-4 h-4" />
                      </button>
                    </div>
                  ))}
                </div>
              </div>

              {/* Quick Actions */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <button 
                  onClick={() => navigate('/cursos')}
                  className="bg-gradient-to-r from-blue-500 to-indigo-600 text-white p-6 rounded-2xl hover:shadow-xl transition-all duration-300 text-left"
                >
                  <FiUsers className="w-8 h-8 mb-3" />
                  <h3 className="text-lg font-semibold mb-2">Gestionar Cursos</h3>
                  <p className="text-blue-100 text-sm">Administrar cursos y contenido académico</p>
                </button>

                <button 
                  onClick={() => navigate('/evaluaciones')}
                  className="bg-gradient-to-r from-emerald-500 to-teal-600 text-white p-6 rounded-2xl hover:shadow-xl transition-all duration-300 text-left"
                >
                  <FiBarChart className="w-8 h-8 mb-3" />
                  <h3 className="text-lg font-semibold mb-2">Evaluaciones</h3>
                  <p className="text-emerald-100 text-sm">Crear y gestionar evaluaciones</p>
                </button>

                <button 
                  onClick={() => navigate('/comunicacion')}
                  className="bg-gradient-to-r from-purple-500 to-pink-600 text-white p-6 rounded-2xl hover:shadow-xl transition-all duration-300 text-left"
                >
                  <FiBarChart className="w-8 h-8 mb-3" />
                  <h3 className="text-lg font-semibold mb-2">Comunicación</h3>
                  <p className="text-purple-100 text-sm">Centro de mensajes y chats</p>
                </button>
              </div>
            </motion.div>
          )}

          {activeTab === 'users' && (
            <motion.div
              key="users"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              transition={{ duration: 0.3 }}
              className="space-y-6"
            >
              <div className="flex items-center justify-between">
                <h2 className="text-2xl font-bold text-gray-900 dark:text-white">Gestión de Usuarios</h2>
                <button 
                  onClick={() => navigate('/admin')}
                  className="flex items-center space-x-2 px-4 py-2 bg-red-600 text-white rounded-xl hover:bg-red-700 transition-colors"
                >
                  <FiPlus className="w-4 h-4" />
                  <span>Ver Panel Completo</span>
                </button>
              </div>
              
              <div className="bg-white/80 dark:bg-gray-800/80 backdrop-blur-xl rounded-2xl p-6 border border-gray-200/50 dark:border-gray-700/50">
                <p className="text-gray-600 dark:text-gray-400">
                  Administra usuarios, coordinadores y permisos desde el panel de administración completo.
                </p>
              </div>
            </motion.div>
          )}

          {activeTab === 'institutions' && (
            <motion.div
              key="institutions"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              transition={{ duration: 0.3 }}
              className="space-y-6"
            >
              <div className="flex items-center justify-between">
                <h2 className="text-2xl font-bold text-gray-900 dark:text-white">Instituciones</h2>
                <button 
                  onClick={() => navigate('/admin')}
                  className="flex items-center space-x-2 px-4 py-2 bg-red-600 text-white rounded-xl hover:bg-red-700 transition-colors"
                >
                  <FiPlus className="w-4 h-4" />
                  <span>Ver Panel Completo</span>
                </button>
              </div>
              
              <div className="bg-white/80 dark:bg-gray-800/80 backdrop-blur-xl rounded-2xl p-6 border border-gray-200/50 dark:border-gray-700/50">
                <p className="text-gray-600 dark:text-gray-400">
                  Gestiona instituciones educativas y sus configuraciones desde el panel principal.
                </p>
              </div>
            </motion.div>
          )}

          {activeTab === 'system' && (
            <motion.div
              key="system"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              transition={{ duration: 0.3 }}
              className="space-y-6"
            >
              <div className="flex items-center justify-between">
                <h2 className="text-2xl font-bold text-gray-900 dark:text-white">Estado del Sistema</h2>
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="bg-white/80 dark:bg-gray-800/80 backdrop-blur-xl rounded-2xl p-6 border border-gray-200/50 dark:border-gray-700/50">
                  <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Estado de Servicios</h3>
                  <div className="space-y-3">
                    {[
                      { name: 'Servidor Web', status: 'online' },
                      { name: 'Base de Datos', status: 'online' },
                      { name: 'Sistema de Archivos', status: 'online' },
                      { name: 'WebSockets', status: 'online' }
                    ].map((service) => (
                      <div key={service.name} className="flex items-center justify-between">
                        <span className="text-gray-700 dark:text-gray-300">{service.name}</span>
                        <div className="flex items-center space-x-2">
                          <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                          <span className="text-sm text-green-600 dark:text-green-400">En línea</span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                <div className="bg-white/80 dark:bg-gray-800/80 backdrop-blur-xl rounded-2xl p-6 border border-gray-200/50 dark:border-gray-700/50">
                  <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Métricas del Sistema</h3>
                  <div className="space-y-3">
                    <div className="flex justify-between">
                      <span className="text-gray-700 dark:text-gray-300">Uso de CPU</span>
                      <span className="text-sm font-medium">12%</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-700 dark:text-gray-300">Uso de Memoria</span>
                      <span className="text-sm font-medium">34%</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-700 dark:text-gray-300">Espacio en Disco</span>
                      <span className="text-sm font-medium">67%</span>
                    </div>
                  </div>
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  )
}