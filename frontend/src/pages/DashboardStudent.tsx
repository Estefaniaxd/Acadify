import React, { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { useAuth } from '../context/AuthContext'
import { useNavigate } from 'react-router-dom'
import { 
  FiBookOpen, 
  FiCalendar, 
  FiTrendingUp, 
  FiAward, 
  FiClock, 
  FiFileText, 
  FiVideo, 
  FiUsers, 
  FiStar,
  FiChevronRight,
  FiPlay,
  FiDownload,
  FiMessageSquare,
  FiMoreVertical,
  FiPlus
} from 'react-icons/fi'
import { HiSparkles, HiLightningBolt } from 'react-icons/hi'

interface Course {
  id: string
  name: string
  teacher: string
  color: string
  progress: number
  nextClass?: string
  assignments: number
  newContent: boolean
}

interface Assignment {
  id: string
  title: string
  course: string
  dueDate: string
  type: 'assignment' | 'quiz' | 'project'
  priority: 'high' | 'medium' | 'low'
  completed: boolean
}

interface Activity {
  id: string
  type: 'assignment' | 'announcement' | 'material' | 'grade'
  course: string
  title: string
  time: string
  icon: any
}

export default function StudentDashboard() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()
  const [activeTab, setActiveTab] = useState<'overview' | 'courses' | 'assignments'>('overview')

  // Datos de ejemplo - en una app real vendrían de una API
  const courses: Course[] = [
    {
      id: '1',
      name: 'Matemáticas Avanzadas',
      teacher: 'Prof. García',
      color: 'from-blue-500 to-indigo-600',
      progress: 75,
      nextClass: 'Álgebra Lineal - Mañana 10:00',
      assignments: 3,
      newContent: true
    },
    {
      id: '2',
      name: 'Historia Contemporánea',
      teacher: 'Prof. Martínez',
      color: 'from-emerald-500 to-teal-600',
      progress: 82,
      nextClass: 'Guerra Fría - Viernes 14:00',
      assignments: 1,
      newContent: false
    },
    {
      id: '3',
      name: 'Ciencias Naturales',
      teacher: 'Prof. López',
      color: 'from-purple-500 to-pink-600',
      progress: 68,
      nextClass: 'Química Orgánica - Lunes 09:00',
      assignments: 5,
      newContent: true
    },
    {
      id: '4',
      name: 'Literatura Española',
      teacher: 'Prof. Hernández',
      color: 'from-amber-500 to-orange-600',
      progress: 91,
      assignments: 2,
      newContent: false
    }
  ]

  const assignments: Assignment[] = [
    {
      id: '1',
      title: 'Ensayo sobre el Romanticismo',
      course: 'Literatura Española',
      dueDate: '2025-09-23',
      type: 'assignment',
      priority: 'high',
      completed: false
    },
    {
      id: '2',
      title: 'Laboratorio de Química',
      course: 'Ciencias Naturales',
      dueDate: '2025-09-25',
      type: 'project',
      priority: 'medium',
      completed: false
    },
    {
      id: '3',
      title: 'Quiz de Derivadas',
      course: 'Matemáticas Avanzadas',
      dueDate: '2025-09-24',
      type: 'quiz',
      priority: 'high',
      completed: false
    }
  ]

  const recentActivity: Activity[] = [
    {
      id: '1',
      type: 'grade',
      course: 'Matemáticas Avanzadas',
      title: 'Calificación publicada: Examen Parcial',
      time: 'Hace 2 horas',
      icon: FiStar
    },
    {
      id: '2',
      type: 'material',
      course: 'Historia Contemporánea',
      title: 'Nuevo material: Documentales de la Guerra Fría',
      time: 'Hace 4 horas',
      icon: FiVideo
    },
    {
      id: '3',
      type: 'announcement',
      course: 'Ciencias Naturales',
      title: 'Recordatorio: Laboratorio mañana',
      time: 'Hace 6 horas',
      icon: FiMessageSquare
    }
  ]

  const getTypeIcon = (type: string) => {
    switch (type) {
      case 'assignment': return FiFileText
      case 'quiz': return FiClock
      case 'project': return FiUsers
      default: return FiFileText
    }
  }

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'high': return 'text-red-500 bg-red-500/10'
      case 'medium': return 'text-amber-500 bg-amber-500/10'
      case 'low': return 'text-emerald-500 bg-emerald-500/10'
      default: return 'text-gray-500 bg-gray-500/10'
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 via-blue-50/30 to-indigo-50/50 dark:from-gray-900 dark:via-gray-900 dark:to-indigo-950/30">
      {/* Header */}
      <div className="bg-white/80 dark:bg-gray-900/80 backdrop-blur-xl border-b border-gray-200/50 dark:border-gray-700/50 sticky top-0 z-40">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-3">
                <div className="w-10 h-10 bg-gradient-to-r from-blue-500 to-indigo-600 rounded-xl flex items-center justify-center">
                  <HiSparkles className="w-6 h-6 text-white" />
                </div>
                <div>
                  <h1 className="text-xl font-bold text-gray-900 dark:text-white">
                    Mi Aula Virtual
                  </h1>
                  <p className="text-sm text-gray-500 dark:text-gray-400">
                    ¡Hola, {user?.username || 'Estudiante'}!
                  </p>
                </div>
              </div>
            </div>

            <div className="flex items-center space-x-4">
              <div className="flex bg-gray-100 dark:bg-gray-800 rounded-lg p-1">
                {[
                  { key: 'overview', label: 'Resumen', icon: FiTrendingUp },
                  { key: 'courses', label: 'Cursos', icon: FiBookOpen },
                  { key: 'assignments', label: 'Tareas', icon: FiFileText }
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
                  { label: 'Cursos Activos', value: '4', icon: FiBookOpen, color: 'from-blue-500 to-indigo-600' },
                  { label: 'Tareas Pendientes', value: '3', icon: FiClock, color: 'from-amber-500 to-orange-600' },
                  { label: 'Progreso Promedio', value: '79%', icon: FiTrendingUp, color: 'from-emerald-500 to-teal-600' },
                  { label: 'Puntos Ganados', value: '1,247', icon: FiAward, color: 'from-purple-500 to-pink-600' }
                ].map((stat, index) => (
                  <motion.div
                    key={index}
                    initial={{ opacity: 0, scale: 0.9 }}
                    animate={{ opacity: 1, scale: 1 }}
                    transition={{ delay: index * 0.1, duration: 0.3 }}
                    className="bg-white/80 dark:bg-gray-800/80 backdrop-blur-xl rounded-2xl p-6 border border-gray-200/50 dark:border-gray-700/50 hover:shadow-xl transition-all duration-300"
                  >
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-sm font-medium text-gray-600 dark:text-gray-400 mb-1">
                          {stat.label}
                        </p>
                        <p className="text-2xl font-bold text-gray-900 dark:text-white">
                          {stat.value}
                        </p>
                      </div>
                      <div className={`w-12 h-12 bg-gradient-to-r ${stat.color} rounded-xl flex items-center justify-center`}>
                        <stat.icon className="w-6 h-6 text-white" />
                      </div>
                    </div>
                  </motion.div>
                ))}
              </div>

              {/* Recent Activity & Upcoming */}
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                {/* Recent Activity */}
                <div className="bg-white/80 dark:bg-gray-800/80 backdrop-blur-xl rounded-2xl p-6 border border-gray-200/50 dark:border-gray-700/50">
                  <div className="flex items-center justify-between mb-6">
                    <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                      Actividad Reciente
                    </h3>
                    <FiChevronRight className="w-5 h-5 text-gray-400" />
                  </div>
                  
                  <div className="space-y-4">
                    {recentActivity.map((activity, index) => (
                      <motion.div
                        key={activity.id}
                        initial={{ opacity: 0, x: -20 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: index * 0.1 }}
                        className="flex items-start space-x-3 p-3 rounded-xl hover:bg-gray-50 dark:hover:bg-gray-700/50 transition-colors"
                      >
                        <div className="w-8 h-8 bg-blue-100 dark:bg-blue-900/30 rounded-lg flex items-center justify-center">
                          <activity.icon className="w-4 h-4 text-blue-600 dark:text-blue-400" />
                        </div>
                        <div className="flex-1 min-w-0">
                          <p className="text-sm font-medium text-gray-900 dark:text-white">
                            {activity.title}
                          </p>
                          <p className="text-xs text-gray-500 dark:text-gray-400">
                            {activity.course} • {activity.time}
                          </p>
                        </div>
                      </motion.div>
                    ))}
                  </div>
                </div>

                {/* Upcoming Assignments */}
                <div className="bg-white/80 dark:bg-gray-800/80 backdrop-blur-xl rounded-2xl p-6 border border-gray-200/50 dark:border-gray-700/50">
                  <div className="flex items-center justify-between mb-6">
                    <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                      Próximas Entregas
                    </h3>
                    <FiCalendar className="w-5 h-5 text-gray-400" />
                  </div>
                  
                  <div className="space-y-4">
                    {assignments.slice(0, 3).map((assignment, index) => {
                      const Icon = getTypeIcon(assignment.type)
                      return (
                        <motion.div
                          key={assignment.id}
                          initial={{ opacity: 0, x: 20 }}
                          animate={{ opacity: 1, x: 0 }}
                          transition={{ delay: index * 0.1 }}
                          className="flex items-center justify-between p-3 rounded-xl hover:bg-gray-50 dark:hover:bg-gray-700/50 transition-colors"
                        >
                          <div className="flex items-center space-x-3">
                            <div className={`w-8 h-8 rounded-lg flex items-center justify-center ${getPriorityColor(assignment.priority)}`}>
                              <Icon className="w-4 h-4" />
                            </div>
                            <div>
                              <p className="text-sm font-medium text-gray-900 dark:text-white">
                                {assignment.title}
                              </p>
                              <p className="text-xs text-gray-500 dark:text-gray-400">
                                {assignment.course} • {assignment.dueDate}
                              </p>
                            </div>
                          </div>
                          <FiChevronRight className="w-4 h-4 text-gray-400" />
                        </motion.div>
                      )
                    })}
                  </div>
                </div>
              </div>
            </motion.div>
          )}

          {activeTab === 'courses' && (
            <motion.div
              key="courses"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              transition={{ duration: 0.3 }}
              className="space-y-6"
            >
              <div className="flex items-center justify-between">
                <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
                  Mis Cursos
                </h2>
                <button className="flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-xl hover:bg-blue-700 transition-colors">
                  <FiPlus className="w-4 h-4" />
                  <span>Unirse a Curso</span>
                </button>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {courses.map((course, index) => (
                  <motion.div
                    key={course.id}
                    initial={{ opacity: 0, scale: 0.9 }}
                    animate={{ opacity: 1, scale: 1 }}
                    transition={{ delay: index * 0.1, duration: 0.3 }}
                    className="bg-white/80 dark:bg-gray-800/80 backdrop-blur-xl rounded-2xl overflow-hidden border border-gray-200/50 dark:border-gray-700/50 hover:shadow-xl transition-all duration-300 cursor-pointer group"
                    onClick={() => navigate(`/course/${course.id}`)}
                  >
                    <div className={`h-32 bg-gradient-to-r ${course.color} relative overflow-hidden`}>
                      <div className="absolute inset-0 bg-black/10"></div>
                      <div className="absolute top-4 right-4">
                        {course.newContent && (
                          <div className="w-3 h-3 bg-red-500 rounded-full animate-pulse"></div>
                        )}
                      </div>
                      <div className="absolute bottom-4 left-4 text-white">
                        <h3 className="text-lg font-bold mb-1">{course.name}</h3>
                        <p className="text-sm opacity-90">{course.teacher}</p>
                      </div>
                    </div>
                    
                    <div className="p-6">
                      <div className="flex items-center justify-between mb-4">
                        <div className="flex items-center space-x-2">
                          <FiTrendingUp className="w-4 h-4 text-gray-500" />
                          <span className="text-sm text-gray-600 dark:text-gray-400">
                            {course.progress}% completado
                          </span>
                        </div>
                        <div className="flex items-center space-x-1">
                          <FiFileText className="w-4 h-4 text-orange-500" />
                          <span className="text-sm font-medium text-orange-600 dark:text-orange-400">
                            {course.assignments}
                          </span>
                        </div>
                      </div>
                      
                      <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2 mb-4">
                        <motion.div
                          initial={{ width: 0 }}
                          animate={{ width: `${course.progress}%` }}
                          transition={{ delay: index * 0.2, duration: 1 }}
                          className={`h-2 bg-gradient-to-r ${course.color} rounded-full`}
                        ></motion.div>
                      </div>
                      
                      {course.nextClass && (
                        <div className="flex items-center space-x-2 text-sm text-gray-600 dark:text-gray-400">
                          <FiCalendar className="w-4 h-4" />
                          <span>{course.nextClass}</span>
                        </div>
                      )}
                    </div>
                  </motion.div>
                ))}
              </div>
            </motion.div>
          )}

          {activeTab === 'assignments' && (
            <motion.div
              key="assignments"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              transition={{ duration: 0.3 }}
              className="space-y-6"
            >
              <div className="flex items-center justify-between">
                <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
                  Mis Tareas
                </h2>
                <div className="flex items-center space-x-2">
                  <button className="px-3 py-2 text-sm bg-gray-100 dark:bg-gray-800 rounded-lg hover:bg-gray-200 dark:hover:bg-gray-700 transition-colors">
                    Todas
                  </button>
                  <button className="px-3 py-2 text-sm text-gray-600 dark:text-gray-400 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors">
                    Pendientes
                  </button>
                  <button className="px-3 py-2 text-sm text-gray-600 dark:text-gray-400 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors">
                    Completadas
                  </button>
                </div>
              </div>

              <div className="bg-white/80 dark:bg-gray-800/80 backdrop-blur-xl rounded-2xl border border-gray-200/50 dark:border-gray-700/50 overflow-hidden">
                <div className="divide-y divide-gray-200 dark:divide-gray-700">
                  {assignments.map((assignment, index) => {
                    const Icon = getTypeIcon(assignment.type)
                    return (
                      <motion.div
                        key={assignment.id}
                        initial={{ opacity: 0, x: -20 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: index * 0.1 }}
                        className="flex items-center justify-between p-6 hover:bg-gray-50 dark:hover:bg-gray-700/50 transition-colors cursor-pointer group"
                      >
                        <div className="flex items-center space-x-4">
                          <div className={`w-10 h-10 rounded-xl flex items-center justify-center ${getPriorityColor(assignment.priority)}`}>
                            <Icon className="w-5 h-5" />
                          </div>
                          <div>
                            <h3 className="text-lg font-medium text-gray-900 dark:text-white group-hover:text-blue-600 dark:group-hover:text-blue-400 transition-colors">
                              {assignment.title}
                            </h3>
                            <p className="text-sm text-gray-500 dark:text-gray-400">
                              {assignment.course} • Entrega: {assignment.dueDate}
                            </p>
                          </div>
                        </div>
                        
                        <div className="flex items-center space-x-3">
                          <span className={`px-3 py-1 text-xs font-medium rounded-full ${getPriorityColor(assignment.priority)}`}>
                            {assignment.priority === 'high' && 'Alta'}
                            {assignment.priority === 'medium' && 'Media'}
                            {assignment.priority === 'low' && 'Baja'}
                          </span>
                          <FiChevronRight className="w-5 h-5 text-gray-400 group-hover:text-gray-600 dark:group-hover:text-gray-300 transition-colors" />
                        </div>
                      </motion.div>
                    )
                  })}
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  )
}