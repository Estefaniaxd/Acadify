import React, { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { useAuth } from '../context/AuthContext'
import { useNavigate } from 'react-router-dom'
import { 
  FiUsers, 
  FiFileText, 
  FiCalendar, 
  FiTrendingUp, 
  FiPlus,
  FiEdit3,
  FiEye,
  FiClock,
  FiCheckCircle,
  FiAlertTriangle,
  FiBarChart,
  FiBookOpen,
  FiMessageSquare,
  FiSettings,
  FiChevronRight
} from 'react-icons/fi'
import { HiSparkles, HiAcademicCap } from 'react-icons/hi'

interface Course {
  id: string
  name: string
  students: number
  progress: number
  color: string
  nextClass?: string
  pendingGrades: number
  assignments: number
}

interface Assignment {
  id: string
  title: string
  course: string
  dueDate: string
  submitted: number
  total: number
  type: 'assignment' | 'quiz' | 'project'
}

interface Student {
  id: string
  name: string
  avatar: string
  course: string
  lastActivity: string
  grade: number
  status: 'active' | 'inactive' | 'struggling'
}

export default function TeacherDashboard() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()
  const [activeTab, setActiveTab] = useState<'overview' | 'courses' | 'students' | 'analytics'>('overview')

  const courses: Course[] = [
    {
      id: '1',
      name: 'Matemáticas Avanzadas 11A',
      students: 28,
      progress: 75,
      color: 'from-blue-500 to-indigo-600',
      nextClass: 'Álgebra Lineal - Mañana 10:00',
      pendingGrades: 5,
      assignments: 3
    },
    {
      id: '2',
      name: 'Cálculo Diferencial 11B',
      students: 32,
      progress: 68,
      color: 'from-emerald-500 to-teal-600',
      nextClass: 'Derivadas - Viernes 14:00',
      pendingGrades: 8,
      assignments: 2
    },
    {
      id: '3',
      name: 'Geometría Analítica 10A',
      students: 25,
      progress: 82,
      color: 'from-purple-500 to-pink-600',
      nextClass: 'Vectores - Lunes 09:00',
      pendingGrades: 2,
      assignments: 4
    }
  ]

  const assignments: Assignment[] = [
    {
      id: '1',
      title: 'Tarea de Límites',
      course: 'Cálculo Diferencial 11B',
      dueDate: '2025-09-23',
      submitted: 28,
      total: 32,
      type: 'assignment'
    },
    {
      id: '2',
      title: 'Quiz de Vectores',
      course: 'Geometría Analítica 10A',
      dueDate: '2025-09-25',
      submitted: 23,
      total: 25,
      type: 'quiz'
    },
    {
      id: '3',
      title: 'Proyecto Final',
      course: 'Matemáticas Avanzadas 11A',
      dueDate: '2025-09-30',
      submitted: 15,
      total: 28,
      type: 'project'
    }
  ]

  const recentStudents: Student[] = [
    {
      id: '1',
      name: 'Ana García',
      avatar: 'AG',
      course: 'Matemáticas Avanzadas 11A',
      lastActivity: 'Hace 2 horas',
      grade: 92,
      status: 'active'
    },
    {
      id: '2',
      name: 'Carlos López',
      avatar: 'CL',
      course: 'Cálculo Diferencial 11B',
      lastActivity: 'Hace 1 día',
      grade: 67,
      status: 'struggling'
    },
    {
      id: '3',
      name: 'María Rodríguez',
      avatar: 'MR',
      course: 'Geometría Analítica 10A',
      lastActivity: 'Hace 30 min',
      grade: 88,
      status: 'active'
    }
  ]

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return 'text-emerald-600 bg-emerald-50 dark:bg-emerald-900/20 dark:text-emerald-400'
      case 'struggling': return 'text-red-600 bg-red-50 dark:bg-red-900/20 dark:text-red-400'
      case 'inactive': return 'text-gray-600 bg-gray-50 dark:bg-gray-800 dark:text-gray-400'
      default: return 'text-gray-600 bg-gray-50 dark:bg-gray-800 dark:text-gray-400'
    }
  }

  const getTypeIcon = (type: string) => {
    switch (type) {
      case 'assignment': return FiFileText
      case 'quiz': return FiClock
      case 'project': return FiUsers
      default: return FiFileText
    }
  }

  return (
    <div className="bg-gradient-to-br from-gray-50 via-emerald-50/30 to-teal-50/50 dark:from-gray-900 dark:via-gray-900 dark:to-emerald-950/30 mt-6">
      {/* Header */}
      <div className="bg-white/80 dark:bg-gray-900/80 backdrop-blur-xl border-b border-gray-200/50 dark:border-gray-700/50 sticky top-0 z-40">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-3">
                <div className="w-10 h-10 bg-gradient-to-r from-emerald-500 to-teal-600 rounded-xl flex items-center justify-center">
                  <HiAcademicCap className="w-6 h-6 text-white" />
                </div>
                <div>
                  <h1 className="text-xl font-bold text-gray-900 dark:text-white">
                    Panel de Profesor
                  </h1>
                  <p className="text-sm text-gray-500 dark:text-gray-400">
                    ¡Hola, Prof. {user?.username || 'García'}!
                  </p>
                </div>
              </div>
            </div>

            <div className="flex items-center space-x-4">
              <div className="flex bg-gray-100 dark:bg-gray-800 rounded-lg p-1">
                {[
                  { key: 'overview', label: 'Resumen', icon: FiTrendingUp },
                  { key: 'courses', label: 'Cursos', icon: FiBookOpen },
                  { key: 'students', label: 'Estudiantes', icon: FiUsers },
                  { key: 'analytics', label: 'Análisis', icon: FiBarChart }
                ].map((tab) => (
                  <button
                    key={tab.key}
                    onClick={() => setActiveTab(tab.key as any)}
                    className={`
                      flex items-center space-x-2 px-3 py-2 rounded-md text-sm font-medium transition-all duration-200
                      ${activeTab === tab.key 
                        ? 'bg-white dark:bg-gray-700 text-emerald-600 dark:text-emerald-400 shadow-sm' 
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
                  { label: 'Cursos Activos', value: '3', icon: FiBookOpen, color: 'from-emerald-500 to-teal-600' },
                  { label: 'Total Estudiantes', value: '85', icon: FiUsers, color: 'from-blue-500 to-indigo-600' },
                  { label: 'Tareas por Revisar', value: '15', icon: FiFileText, color: 'from-amber-500 to-orange-600' },
                  { label: 'Promedio General', value: '82.5%', icon: FiTrendingUp, color: 'from-purple-500 to-pink-600' }
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

              {/* Recent Activity & Pending Tasks */}
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                {/* Recent Submissions */}
                <div className="bg-white/80 dark:bg-gray-800/80 backdrop-blur-xl rounded-2xl p-6 border border-gray-200/50 dark:border-gray-700/50">
                  <div className="flex items-center justify-between mb-6">
                    <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                      Entregas Recientes
                    </h3>
                    <FiChevronRight className="w-5 h-5 text-gray-400" />
                  </div>
                  
                  <div className="space-y-4">
                    {assignments.map((assignment, index) => {
                      const Icon = getTypeIcon(assignment.type)
                      const percentage = Math.round((assignment.submitted / assignment.total) * 100)
                      return (
                        <motion.div
                          key={assignment.id}
                          initial={{ opacity: 0, x: -20 }}
                          animate={{ opacity: 1, x: 0 }}
                          transition={{ delay: index * 0.1 }}
                          className="flex items-center justify-between p-3 rounded-xl hover:bg-gray-50 dark:hover:bg-gray-700/50 transition-colors cursor-pointer"
                        >
                          <div className="flex items-center space-x-3">
                            <div className="w-8 h-8 bg-emerald-100 dark:bg-emerald-900/30 rounded-lg flex items-center justify-center">
                              <Icon className="w-4 h-4 text-emerald-600 dark:text-emerald-400" />
                            </div>
                            <div>
                              <p className="text-sm font-medium text-gray-900 dark:text-white">
                                {assignment.title}
                              </p>
                              <p className="text-xs text-gray-500 dark:text-gray-400">
                                {assignment.course}
                              </p>
                            </div>
                          </div>
                          <div className="text-right">
                            <p className="text-sm font-medium text-gray-900 dark:text-white">
                              {assignment.submitted}/{assignment.total}
                            </p>
                            <p className="text-xs text-gray-500 dark:text-gray-400">
                              {percentage}% entregado
                            </p>
                          </div>
                        </motion.div>
                      )
                    })}
                  </div>
                </div>

                {/* Recent Students Activity */}
                <div className="bg-white/80 dark:bg-gray-800/80 backdrop-blur-xl rounded-2xl p-6 border border-gray-200/50 dark:border-gray-700/50">
                  <div className="flex items-center justify-between mb-6">
                    <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                      Actividad de Estudiantes
                    </h3>
                    <FiUsers className="w-5 h-5 text-gray-400" />
                  </div>
                  
                  <div className="space-y-4">
                    {recentStudents.map((student, index) => (
                      <motion.div
                        key={student.id}
                        initial={{ opacity: 0, x: 20 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: index * 0.1 }}
                        className="flex items-center justify-between p-3 rounded-xl hover:bg-gray-50 dark:hover:bg-gray-700/50 transition-colors cursor-pointer"
                      >
                        <div className="flex items-center space-x-3">
                          <div className="w-8 h-8 bg-gradient-to-r from-blue-500 to-indigo-600 rounded-lg flex items-center justify-center text-white text-xs font-bold">
                            {student.avatar}
                          </div>
                          <div>
                            <p className="text-sm font-medium text-gray-900 dark:text-white">
                              {student.name}
                            </p>
                            <p className="text-xs text-gray-500 dark:text-gray-400">
                              {student.lastActivity}
                            </p>
                          </div>
                        </div>
                        <div className="flex items-center space-x-2">
                          <span className={`px-2 py-1 text-xs font-medium rounded-full ${getStatusColor(student.status)}`}>
                            {student.grade}%
                          </span>
                        </div>
                      </motion.div>
                    ))}
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
                <button className="flex items-center space-x-2 px-4 py-2 bg-emerald-600 text-white rounded-xl hover:bg-emerald-700 transition-colors">
                  <FiPlus className="w-4 h-4" />
                  <span>Crear Curso</span>
                </button>
              </div>

              <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6">
                {courses.map((course, index) => (
                  <motion.div
                    key={course.id}
                    initial={{ opacity: 0, scale: 0.9 }}
                    animate={{ opacity: 1, scale: 1 }}
                    transition={{ delay: index * 0.1, duration: 0.3 }}
                    className="bg-white/80 dark:bg-gray-800/80 backdrop-blur-xl rounded-2xl overflow-hidden border border-gray-200/50 dark:border-gray-700/50 hover:shadow-xl transition-all duration-300 cursor-pointer group"
                  >
                    <div className={`h-32 bg-gradient-to-r ${course.color} relative overflow-hidden`}>
                      <div className="absolute inset-0 bg-black/10"></div>
                      <div className="absolute top-4 right-4 flex space-x-2">
                        <button className="w-8 h-8 bg-white/20 backdrop-blur-sm rounded-lg flex items-center justify-center text-white hover:bg-white/30 transition-colors">
                          <FiEdit3 className="w-4 h-4" />
                        </button>
                        <button className="w-8 h-8 bg-white/20 backdrop-blur-sm rounded-lg flex items-center justify-center text-white hover:bg-white/30 transition-colors">
                          <FiSettings className="w-4 h-4" />
                        </button>
                      </div>
                      <div className="absolute bottom-4 left-4 text-white">
                        <h3 className="text-lg font-bold mb-1">{course.name}</h3>
                        <p className="text-sm opacity-90">{course.students} estudiantes</p>
                      </div>
                    </div>
                    
                    <div className="p-6">
                      <div className="grid grid-cols-3 gap-4 mb-4">
                        <div className="text-center">
                          <p className="text-2xl font-bold text-emerald-600 dark:text-emerald-400">
                            {course.students}
                          </p>
                          <p className="text-xs text-gray-500 dark:text-gray-400">Estudiantes</p>
                        </div>
                        <div className="text-center">
                          <p className="text-2xl font-bold text-amber-600 dark:text-amber-400">
                            {course.pendingGrades}
                          </p>
                          <p className="text-xs text-gray-500 dark:text-gray-400">Por revisar</p>
                        </div>
                        <div className="text-center">
                          <p className="text-2xl font-bold text-blue-600 dark:text-blue-400">
                            {course.assignments}
                          </p>
                          <p className="text-xs text-gray-500 dark:text-gray-400">Tareas</p>
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
                        <div className="flex items-center space-x-2 text-sm text-gray-600 dark:text-gray-400 mb-4">
                          <FiCalendar className="w-4 h-4" />
                          <span>{course.nextClass}</span>
                        </div>
                      )}
                      
                      <div className="flex space-x-2">
                        <button className="flex-1 py-2 px-3 text-sm bg-emerald-600 text-white rounded-lg hover:bg-emerald-700 transition-colors">
                          Ver Curso
                        </button>
                        <button className="py-2 px-3 text-sm border border-gray-300 dark:border-gray-600 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors">
                          <FiEye className="w-4 h-4" />
                        </button>
                      </div>
                    </div>
                  </motion.div>
                ))}
              </div>
            </motion.div>
          )}

          {/* Tabs adicionales como students y analytics seguirían el mismo patrón */}
        </AnimatePresence>
      </div>
    </div>
  )
}