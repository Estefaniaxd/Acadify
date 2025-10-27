import React, { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { useAuth } from '../context/AuthContext'
import { useNavigate } from 'react-router-dom'
import { 
  FiUsers, 
  FiSettings, 
  FiBarChart, 
  FiBookOpen,
  FiUserCheck,
  FiTrendingUp,
  FiCalendar,
  FiMoreVertical,
  FiPlus,
  FiEye,
  FiEdit3
} from 'react-icons/fi'
import { HiOutlineOfficeBuilding, HiAcademicCap } from 'react-icons/hi'

interface CoordinatorStats {
  totalTeachers: number
  activeClasses: number
  totalStudents: number
  institutionName: string
}

interface Teacher {
  id: string
  name: string
  email: string
  subject: string
  studentsCount: number
  status: 'active' | 'inactive'
}

interface Class {
  id: string
  name: string
  teacher: string
  studentsCount: number
  nextSession: string
  status: 'active' | 'completed' | 'scheduled'
}

export default function CoordinatorDashboard() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()
  const [activeTab, setActiveTab] = useState<'overview' | 'teachers' | 'classes' | 'institution'>('overview')

  const stats: CoordinatorStats = {
    totalTeachers: 12,
    activeClasses: 28,
    totalStudents: 340,
    institutionName: 'Instituto Educativo San José'
  }

  const teachers: Teacher[] = [
    {
      id: '1',
      name: 'Ana García',
      email: 'ana.garcia@instituto.edu',
      subject: 'Matemáticas',
      studentsCount: 85,
      status: 'active'
    },
    {
      id: '2',
      name: 'Luis Rodríguez',
      email: 'luis.rodriguez@instituto.edu',
      subject: 'Historia',
      studentsCount: 72,
      status: 'active'
    },
    {
      id: '3',
      name: 'María López',
      email: 'maria.lopez@instituto.edu',
      subject: 'Ciencias',
      studentsCount: 90,
      status: 'inactive'
    }
  ]

  const classes: Class[] = [
    {
      id: '1',
      name: 'Matemáticas 11A',
      teacher: 'Ana García',
      studentsCount: 28,
      nextSession: 'Mañana 10:00',
      status: 'active'
    },
    {
      id: '2',
      name: 'Historia 10B',
      teacher: 'Luis Rodríguez',
      studentsCount: 24,
      nextSession: 'Viernes 14:00',
      status: 'active'
    },
    {
      id: '3',
      name: 'Ciencias 9A',
      teacher: 'María López',
      studentsCount: 26,
      nextSession: 'Lunes 08:00',
      status: 'scheduled'
    }
  ]

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-indigo-100 dark:from-gray-900 dark:via-gray-800 dark:to-blue-900">
      {/* Header */}
      <div className="bg-white/80 dark:bg-gray-800/80 backdrop-blur-xl border-b border-gray-200/50 dark:border-gray-700/50 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-3">
                <div className="w-10 h-10 bg-gradient-to-r from-blue-500 to-indigo-600 rounded-xl flex items-center justify-center">
                  <HiAcademicCap className="w-6 h-6 text-white" />
                </div>
                <div>
                  <h1 className="text-xl font-bold text-gray-900 dark:text-white">
                    Panel de Coordinador
                  </h1>
                  <p className="text-sm text-gray-500 dark:text-gray-400">
                    {stats.institutionName} - ¡Hola, {user?.username || 'Coordinador'}!
                  </p>
                </div>
              </div>
            </div>

            <div className="flex items-center space-x-4">
              <div className="flex bg-gray-100 dark:bg-gray-800 rounded-lg p-1">
                {[
                  { key: 'overview', label: 'Resumen', icon: FiTrendingUp },
                  { key: 'teachers', label: 'Profesores', icon: FiUserCheck },
                  { key: 'classes', label: 'Clases', icon: FiBookOpen },
                  { key: 'institution', label: 'Institución', icon: HiOutlineOfficeBuilding }
                ].map((tab) => (
                  <button
                    key={tab.key}
                    onClick={() => setActiveTab(tab.key as any)}
                    className={`
                      flex items-center space-x-2 px-3 py-2 rounded-md text-sm font-medium transition-all duration-200
                      ${activeTab === tab.key 
                        ? 'bg-white dark:bg-gray-700 text-blue-600 dark:text-blue-400 shadow-sm' 
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
                  { label: 'Total Profesores', value: stats.totalTeachers.toString(), icon: FiUserCheck, color: 'from-blue-500 to-indigo-600' },
                  { label: 'Clases Activas', value: stats.activeClasses.toString(), icon: FiBookOpen, color: 'from-emerald-500 to-teal-600' },
                  { label: 'Total Estudiantes', value: stats.totalStudents.toLocaleString(), icon: FiUsers, color: 'from-purple-500 to-pink-600' },
                  { label: 'Mi Institución', value: '1', icon: HiOutlineOfficeBuilding, color: 'from-orange-500 to-red-600' }
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

              {/* Quick Actions */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <button 
                  onClick={() => navigate('/cursos')}
                  className="bg-gradient-to-r from-blue-500 to-indigo-600 text-white p-6 rounded-2xl hover:shadow-xl transition-all duration-300 text-left"
                >
                  <FiUserCheck className="w-8 h-8 mb-3" />
                  <h3 className="text-lg font-semibold mb-2">Gestionar Cursos</h3>
                  <p className="text-blue-100 text-sm">Administrar cursos y contenido académico</p>
                </button>

                <button 
                  onClick={() => navigate('/evaluaciones')}
                  className="bg-gradient-to-r from-emerald-500 to-teal-600 text-white p-6 rounded-2xl hover:shadow-xl transition-all duration-300 text-left"
                >
                  <FiBookOpen className="w-8 h-8 mb-3" />
                  <h3 className="text-lg font-semibold mb-2">Supervisar Evaluaciones</h3>
                  <p className="text-emerald-100 text-sm">Crear y monitorear evaluaciones</p>
                </button>

                <button 
                  onClick={() => navigate('/comunicacion')}
                  className="bg-gradient-to-r from-purple-500 to-pink-600 text-white p-6 rounded-2xl hover:shadow-xl transition-all duration-300 text-left"
                >
                  <FiBarChart className="w-8 h-8 mb-3" />
                  <h3 className="text-lg font-semibold mb-2">Centro de Comunicación</h3>
                  <p className="text-purple-100 text-sm">Mensajes y chats institucionales</p>
                </button>
              </div>

              {/* Recent Activities */}
              <div className="bg-white/80 dark:bg-gray-800/80 backdrop-blur-xl rounded-2xl p-6 border border-gray-200/50 dark:border-gray-700/50">
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Actividad Reciente</h3>
                <div className="space-y-3">
                  {[
                    { action: 'Nuevo profesor registrado', detail: 'Ana García - Matemáticas', time: '2 horas' },
                    { action: 'Clase completada', detail: 'Historia 10B - 28 estudiantes', time: '3 horas' },
                    { action: 'Evaluación creada', detail: 'Examen de Ciencias - 9A', time: '5 horas' }
                  ].map((activity, index) => (
                    <div key={index} className="flex items-center justify-between p-3 rounded-lg bg-gray-50 dark:bg-gray-700/50">
                      <div>
                        <p className="text-sm font-medium text-gray-900 dark:text-white">{activity.action}</p>
                        <p className="text-xs text-gray-500 dark:text-gray-400">{activity.detail}</p>
                      </div>
                      <span className="text-xs text-gray-500 dark:text-gray-400">Hace {activity.time}</span>
                    </div>
                  ))}
                </div>
              </div>
            </motion.div>
          )}

          {activeTab === 'teachers' && (
            <motion.div
              key="teachers"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              transition={{ duration: 0.3 }}
              className="space-y-6"
            >
              <div className="flex items-center justify-between">
                <h2 className="text-2xl font-bold text-gray-900 dark:text-white">Profesores</h2>
                <button 
                  onClick={() => navigate('/coordinador')}
                  className="flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-xl hover:bg-blue-700 transition-colors"
                >
                  <FiPlus className="w-4 h-4" />
                  <span>Ver Panel Completo</span>
                </button>
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {teachers.map((teacher) => (
                  <div key={teacher.id} className="bg-white/80 dark:bg-gray-800/80 backdrop-blur-xl rounded-2xl p-6 border border-gray-200/50 dark:border-gray-700/50">
                    <div className="flex items-center justify-between mb-4">
                      <div className="flex items-center space-x-3">
                        <div className="w-10 h-10 bg-gradient-to-r from-blue-500 to-indigo-600 rounded-full flex items-center justify-center">
                          <FiUserCheck className="w-5 h-5 text-white" />
                        </div>
                        <div>
                          <p className="font-semibold text-gray-900 dark:text-white">{teacher.name}</p>
                          <p className="text-sm text-gray-500 dark:text-gray-400">{teacher.subject}</p>
                        </div>
                      </div>
                      <div className={`w-2 h-2 rounded-full ${teacher.status === 'active' ? 'bg-green-500' : 'bg-gray-400'}`}></div>
                    </div>
                    
                    <p className="text-sm text-gray-600 dark:text-gray-400 mb-2">{teacher.email}</p>
                    <p className="text-sm font-medium text-gray-900 dark:text-white">{teacher.studentsCount} estudiantes</p>
                  </div>
                ))}
              </div>
            </motion.div>
          )}

          {activeTab === 'classes' && (
            <motion.div
              key="classes"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              transition={{ duration: 0.3 }}
              className="space-y-6"
            >
              <div className="flex items-center justify-between">
                <h2 className="text-2xl font-bold text-gray-900 dark:text-white">Clases</h2>
                <button 
                  onClick={() => navigate('/coordinador')}
                  className="flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-xl hover:bg-blue-700 transition-colors"
                >
                  <FiEye className="w-4 h-4" />
                  <span>Ver Todas</span>
                </button>
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {classes.map((clase) => (
                  <div key={clase.id} className="bg-white/80 dark:bg-gray-800/80 backdrop-blur-xl rounded-2xl p-6 border border-gray-200/50 dark:border-gray-700/50">
                    <div className="flex items-center justify-between mb-4">
                      <h3 className="font-semibold text-gray-900 dark:text-white">{clase.name}</h3>
                      <div className={`px-2 py-1 rounded-full text-xs font-medium ${
                        clase.status === 'active' ? 'bg-green-100 text-green-700 dark:bg-green-800 dark:text-green-300' :
                        clase.status === 'scheduled' ? 'bg-blue-100 text-blue-700 dark:bg-blue-800 dark:text-blue-300' :
                        'bg-gray-100 text-gray-700 dark:bg-gray-800 dark:text-gray-300'
                      }`}>
                        {clase.status === 'active' ? 'Activa' : clase.status === 'scheduled' ? 'Programada' : 'Completada'}
                      </div>
                    </div>
                    
                    <p className="text-sm text-gray-600 dark:text-gray-400 mb-2">Prof. {clase.teacher}</p>
                    <p className="text-sm text-gray-600 dark:text-gray-400 mb-2">{clase.studentsCount} estudiantes</p>
                    <p className="text-sm font-medium text-gray-900 dark:text-white">{clase.nextSession}</p>
                  </div>
                ))}
              </div>
            </motion.div>
          )}

          {activeTab === 'institution' && (
            <motion.div
              key="institution"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              transition={{ duration: 0.3 }}
              className="space-y-6"
            >
              <div className="flex items-center justify-between">
                <h2 className="text-2xl font-bold text-gray-900 dark:text-white">Mi Institución</h2>
                <button 
                  onClick={() => navigate('/coordinador')}
                  className="flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-xl hover:bg-blue-700 transition-colors"
                >
                  <FiEdit3 className="w-4 h-4" />
                  <span>Gestionar</span>
                </button>
              </div>
              
              <div className="bg-white/80 dark:bg-gray-800/80 backdrop-blur-xl rounded-2xl p-6 border border-gray-200/50 dark:border-gray-700/50">
                <div className="flex items-center space-x-4 mb-6">
                  <div className="w-16 h-16 bg-gradient-to-r from-blue-500 to-indigo-600 rounded-2xl flex items-center justify-center">
                    <HiOutlineOfficeBuilding className="w-8 h-8 text-white" />
                  </div>
                  <div>
                    <h3 className="text-xl font-bold text-gray-900 dark:text-white">{stats.institutionName}</h3>
                    <p className="text-gray-600 dark:text-gray-400">Institución Educativa</p>
                  </div>
                </div>
                
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                  <div className="text-center">
                    <div className="text-2xl font-bold text-blue-600 dark:text-blue-400">{stats.totalTeachers}</div>
                    <div className="text-sm text-gray-600 dark:text-gray-400">Profesores</div>
                  </div>
                  <div className="text-center">
                    <div className="text-2xl font-bold text-emerald-600 dark:text-emerald-400">{stats.activeClasses}</div>
                    <div className="text-sm text-gray-600 dark:text-gray-400">Clases Activas</div>
                  </div>
                  <div className="text-center">
                    <div className="text-2xl font-bold text-purple-600 dark:text-purple-400">{stats.totalStudents}</div>
                    <div className="text-sm text-gray-600 dark:text-gray-400">Estudiantes</div>
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