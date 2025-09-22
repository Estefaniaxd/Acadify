import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { motion } from 'framer-motion';
import { 
  FiBook, FiClock, FiTrendingUp, FiTarget, FiCalendar, 
  FiAward, FiUsers, FiActivity, FiChevronRight, FiStar,
  FiBarChart, FiBookOpen, FiPlay
} from 'react-icons/fi';
import { HiSparkles } from 'react-icons/hi';

// Datos mock para el dashboard
const mockClases = [
  {
    id: 1,
    name: 'Matemáticas Avanzadas',
    professor: 'Prof. Ana García',
    progress: 75,
    nextClass: '2024-01-15 10:00',
    color: 'from-blue-500 to-cyan-500',
    students: 28,
    lastAccessed: '2024-01-14T14:30:00Z'
  },
  {
    id: 2,
    name: 'Historia Universal',
    professor: 'Prof. Luis Martínez',
    progress: 60,
    nextClass: '2024-01-15 14:00',
    color: 'from-purple-500 to-pink-500',
    students: 32,
    lastAccessed: '2024-01-14T09:15:00Z'
  },
  {
    id: 3,
    name: 'Química Orgánica',
    professor: 'Prof. María López',
    progress: 85,
    nextClass: '2024-01-16 08:00',
    color: 'from-green-500 to-emerald-500',
    students: 25,
    lastAccessed: '2024-01-13T16:45:00Z'
  }
];

const mockActivities = [
  { id: 1, type: 'assignment', title: 'Tarea de Matemáticas', subject: 'Matemáticas Avanzadas', due: '2024-01-16', priority: 'high' },
  { id: 2, type: 'exam', title: 'Examen Historia', subject: 'Historia Universal', due: '2024-01-18', priority: 'medium' },
  { id: 3, type: 'project', title: 'Proyecto Final Química', subject: 'Química Orgánica', due: '2024-01-20', priority: 'low' }
];

const mockStats = {
  totalClasses: 3,
  completedAssignments: 15,
  pendingAssignments: 4,
  averageGrade: 87,
  studyStreak: 12,
  achievements: 8
};

export default function DashboardPage() {
  const navigate = useNavigate();
  const { user } = useAuth();

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        duration: 0.6,
        staggerChildren: 0.1
      }
    }
  };

  const itemVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: {
      opacity: 1,
      y: 0,
      transition: { duration: 0.6, ease: "easeOut" }
    }
  };

  return (
    <motion.div
      variants={containerVariants}
      initial="hidden"
      animate="visible"
      className="min-h-screen bg-gradient-to-br from-violet-50 via-purple-50 to-indigo-100 dark:from-gray-900 dark:via-purple-900/20 dark:to-indigo-900/20 p-6"
    >
      <div className="max-w-7xl mx-auto">
        {/* Header de bienvenida */}
        <motion.div
          variants={itemVariants}
          className="mb-8"
        >
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
                ¡Bienvenido de vuelta, {user?.username || 'Estudiante'}! 
                <motion.span
                  className="inline-block ml-2"
                  animate={{ rotate: [0, 15, 0] }}
                  transition={{ duration: 1, repeat: Infinity, repeatDelay: 3 }}
                >
                  👋
                </motion.span>
              </h1>
              <p className="text-gray-600 dark:text-gray-300">
                Aquí tienes un resumen de tu progreso académico
              </p>
            </div>
            <motion.div
              className="flex items-center gap-2 px-4 py-2 rounded-xl bg-gradient-to-r from-violet-600 to-purple-600 text-white shadow-lg"
              whileHover={{ scale: 1.05 }}
            >
              <HiSparkles className="w-5 h-5" />
              <span className="font-semibold">{mockStats.studyStreak} días</span>
              <span className="text-sm opacity-90">de estudio</span>
            </motion.div>
          </div>
        </motion.div>

        {/* Estadísticas rápidas */}
        <motion.div
          variants={itemVariants}
          className="grid grid-cols-2 md:grid-cols-4 gap-6 mb-8"
        >
          {[
            { icon: FiBook, label: 'Clases', value: mockStats.totalClasses, color: 'text-blue-600' },
            { icon: FiTarget, label: 'Tareas Completadas', value: mockStats.completedAssignments, color: 'text-green-600' },
            { icon: FiTrendingUp, label: 'Promedio', value: `${mockStats.averageGrade}%`, color: 'text-purple-600' },
            { icon: FiAward, label: 'Logros', value: mockStats.achievements, color: 'text-orange-600' }
          ].map((stat, idx) => (
            <motion.div
              key={idx}
              className="relative p-6 rounded-2xl bg-white/80 dark:bg-gray-800/80 backdrop-blur-sm border border-white/50 dark:border-gray-700/50 shadow-lg overflow-hidden"
              whileHover={{ y: -2, scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
            >
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600 dark:text-gray-400 font-medium">{stat.label}</p>
                  <p className="text-2xl font-bold text-gray-900 dark:text-white mt-1">{stat.value}</p>
                </div>
                <stat.icon className={`w-8 h-8 ${stat.color}`} />
              </div>
              {/* Efecto de brillo */}
              <motion.div
                className="absolute top-0 right-0 w-16 h-16 bg-gradient-to-bl from-white/20 to-transparent rounded-bl-full"
                whileHover={{ scale: 1.2, opacity: 0.8 }}
              />
            </motion.div>
          ))}
        </motion.div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Clase más reciente y acciones rápidas */}
          <motion.div
            variants={itemVariants}
            className="lg:col-span-2 space-y-6"
          >
            {/* Clase más reciente */}
            <div className="p-6 rounded-2xl bg-white/90 dark:bg-gray-800/90 backdrop-blur-sm border border-white/50 dark:border-gray-700/50 shadow-lg">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-xl font-bold text-gray-900 dark:text-white flex items-center gap-2">
                  <FiClock className="w-5 h-5 text-violet-600" />
                  Continuar Estudiando
                </h2>
                <motion.button
                  className="text-sm text-violet-600 hover:text-violet-700 font-medium flex items-center gap-1"
                  onClick={() => navigate('/mis-clases')}
                  whileHover={{ x: 2 }}
                >
                  Ver todas <FiChevronRight className="w-4 h-4" />
                </motion.button>
              </div>
              
              {(() => {
                const mostRecent = mockClases.sort((a, b) => 
                  new Date(b.lastAccessed).getTime() - new Date(a.lastAccessed).getTime()
                )[0];
                
                return (
                  <motion.div
                    className="relative p-6 rounded-2xl shadow-md overflow-hidden cursor-pointer"
                    style={{
                      background: 'linear-gradient(135deg, rgba(255, 255, 255, 0.9) 0%, rgba(248, 250, 252, 0.95) 100%)',
                      border: '1px solid rgba(139, 92, 246, 0.1)'
                    }}
                    onClick={() => navigate(`/clase/${mostRecent.id}`)}
                    whileHover={{ y: -2, scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                  >
                    <div className={`absolute top-0 left-0 w-full h-1 bg-gradient-to-r ${mostRecent.color}`} />
                    
                    <div className="flex items-center justify-between">
                      <div className="flex-1">
                        <h3 className="text-lg font-bold text-gray-900 mb-1">{mostRecent.name}</h3>
                        <p className="text-sm text-gray-600 mb-3">{mostRecent.professor}</p>
                        
                        {/* Barra de progreso */}
                        <div className="w-full bg-gray-200 rounded-full h-2 mb-2">
                          <motion.div 
                            className={`h-2 bg-gradient-to-r ${mostRecent.color} rounded-full`}
                            initial={{ width: 0 }}
                            animate={{ width: `${mostRecent.progress}%` }}
                            transition={{ duration: 1.5, ease: "easeOut" }}
                          />
                        </div>
                        <p className="text-xs text-gray-500">{mostRecent.progress}% completado</p>
                      </div>
                      
                      <div className="flex flex-col items-center gap-3">
                        <motion.div
                          className={`w-16 h-16 rounded-2xl bg-gradient-to-br ${mostRecent.color} flex items-center justify-center shadow-lg`}
                          whileHover={{ rotate: 10, scale: 1.1 }}
                        >
                          <FiPlay className="w-6 h-6 text-white" />
                        </motion.div>
                        <motion.button
                          className="px-4 py-2 rounded-xl bg-violet-600 text-white text-sm font-medium shadow-md"
                          whileHover={{ scale: 1.05 }}
                          whileTap={{ scale: 0.95 }}
                          onClick={(e) => {
                            e.stopPropagation();
                            navigate(`/clase/${mostRecent.id}`)
                          }}
                        >
                          Continuar
                        </motion.button>
                      </div>
                    </div>
                  </motion.div>
                );
              })()}
            </div>

            {/* Próximas clases */}
            <div className="p-6 rounded-2xl bg-white/90 dark:bg-gray-800/90 backdrop-blur-sm border border-white/50 dark:border-gray-700/50 shadow-lg">
              <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-4 flex items-center gap-2">
                <FiCalendar className="w-5 h-5 text-indigo-600" />
                Próximas Clases
              </h2>
              <div className="space-y-3">
                {mockClases.slice(0, 3).map((clase, idx) => (
                  <motion.div
                    key={clase.id}
                    className="flex items-center justify-between p-4 rounded-xl bg-gray-50/80 dark:bg-gray-700/50 border border-gray-200/50 dark:border-gray-600/50"
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: 0.1 * idx }}
                    whileHover={{ x: 4 }}
                  >
                    <div className="flex items-center gap-3">
                      <div className={`w-3 h-3 rounded-full bg-gradient-to-r ${clase.color}`} />
                      <div>
                        <p className="font-semibold text-gray-900 dark:text-white text-sm">{clase.name}</p>
                        <p className="text-xs text-gray-600 dark:text-gray-400">{clase.professor}</p>
                      </div>
                    </div>
                    <div className="text-right">
                      <p className="text-sm font-medium text-gray-900 dark:text-white">
                        {new Date(clase.nextClass).toLocaleTimeString('es-ES', { 
                          hour: '2-digit', 
                          minute: '2-digit'
                        })}
                      </p>
                      <p className="text-xs text-gray-500">
                        {new Date(clase.nextClass).toLocaleDateString('es-ES', { 
                          month: 'short', 
                          day: 'numeric'
                        })}
                      </p>
                    </div>
                  </motion.div>
                ))}
              </div>
            </div>
          </motion.div>

          {/* Sidebar derecho */}
          <motion.div
            variants={itemVariants}
            className="space-y-6"
          >
            {/* Actividades pendientes */}
            <div className="p-6 rounded-2xl bg-white/90 dark:bg-gray-800/90 backdrop-blur-sm border border-white/50 dark:border-gray-700/50 shadow-lg">
              <h2 className="text-lg font-bold text-gray-900 dark:text-white mb-4 flex items-center gap-2">
                <FiActivity className="w-5 h-5 text-red-600" />
                Actividades Pendientes
              </h2>
              <div className="space-y-3">
                {mockActivities.map((activity, idx) => (
                  <motion.div
                    key={activity.id}
                    className={`p-3 rounded-xl border-l-4 ${
                      activity.priority === 'high' ? 'border-red-500 bg-red-50/50 dark:bg-red-900/20' :
                      activity.priority === 'medium' ? 'border-yellow-500 bg-yellow-50/50 dark:bg-yellow-900/20' :
                      'border-green-500 bg-green-50/50 dark:bg-green-900/20'
                    }`}
                    initial={{ opacity: 0, x: 20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: 0.1 * idx }}
                    whileHover={{ x: -2 }}
                  >
                    <p className="font-semibold text-gray-900 dark:text-white text-sm">{activity.title}</p>
                    <p className="text-xs text-gray-600 dark:text-gray-400">{activity.subject}</p>
                    <p className="text-xs text-gray-500 mt-1">
                      Vence: {new Date(activity.due).toLocaleDateString('es-ES')}
                    </p>
                  </motion.div>
                ))}
              </div>
            </div>

            {/* Progreso general */}
            <div className="p-6 rounded-2xl bg-white/90 dark:bg-gray-800/90 backdrop-blur-sm border border-white/50 dark:border-gray-700/50 shadow-lg">
              <h2 className="text-lg font-bold text-gray-900 dark:text-white mb-4 flex items-center gap-2">
                <FiBarChart className="w-5 h-5 text-emerald-600" />
                Progreso General
              </h2>
              <div className="space-y-4">
                {mockClases.map((clase, idx) => (
                  <div key={clase.id} className="space-y-2">
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-700 dark:text-gray-300">{clase.name}</span>
                      <span className="font-semibold text-gray-900 dark:text-white">{clase.progress}%</span>
                    </div>
                    <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                      <motion.div
                        className={`h-2 bg-gradient-to-r ${clase.color} rounded-full`}
                        initial={{ width: 0 }}
                        animate={{ width: `${clase.progress}%` }}
                        transition={{ duration: 1, delay: 0.2 * idx }}
                      />
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Acciones rápidas */}
            <div className="p-6 rounded-2xl bg-white/90 dark:bg-gray-800/90 backdrop-blur-sm border border-white/50 dark:border-gray-700/50 shadow-lg">
              <h2 className="text-lg font-bold text-gray-900 dark:text-white mb-4">Acciones Rápidas</h2>
              <div className="space-y-3">
                {[
                  { icon: FiUsers, label: 'Unirse a Clase', action: () => navigate('/unirse-clase'), color: 'text-blue-600' },
                  { icon: FiBookOpen, label: 'Ver Todas las Clases', action: () => navigate('/mis-clases'), color: 'text-purple-600' },
                  { icon: FiStar, label: 'Ver Logros', action: () => navigate('/logros'), color: 'text-yellow-600' }
                ].map((item, idx) => (
                  <motion.button
                    key={idx}
                    className="w-full flex items-center gap-3 p-3 rounded-xl bg-gray-50/80 dark:bg-gray-700/50 border border-gray-200/50 dark:border-gray-600/50 hover:bg-gray-100/80 dark:hover:bg-gray-600/50 transition-colors"
                    onClick={item.action}
                    whileHover={{ x: 4, scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                  >
                    <item.icon className={`w-5 h-5 ${item.color}`} />
                    <span className="text-sm font-medium text-gray-700 dark:text-gray-300">{item.label}</span>
                    <FiChevronRight className="w-4 h-4 text-gray-400 ml-auto" />
                  </motion.button>
                ))}
              </div>
            </div>
          </motion.div>
        </div>
      </div>
    </motion.div>
  );
}