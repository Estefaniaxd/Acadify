import React from 'react';
import { motion } from 'framer-motion';
import { Activity, Award, BarChart, BookOpen, Calendar, Target, TrendingUp, Users } from 'lucide-react';
;

// Datos mock para desarrollo
const estadisticasMock = {
  resumen: {
    profesores: 8,
    estudiantes: 90,
    clasesActivas: 6,
    puntosOtorgados: 2500
  },
  rendimiento: {
    promedioGeneral: 85.2,
    aprobacion: 92,
    participacion: 78,
    satisfaccion: 94
  },
  actividad: {
    sesionesActivas: 24,
    tareasPendientes: 12,
    examenesProgramados: 5,
    anuncios: 3
  },
  tendencias: [
    { mes: 'Ene', estudiantes: 75, promedio: 82 },
    { mes: 'Feb', estudiantes: 80, promedio: 84 },
    { mes: 'Mar', estudiantes: 85, promedio: 86 },
    { mes: 'Abr', estudiantes: 90, promedio: 85 }
  ]
};

export default function EstadisticasCoordinador() {
  const { resumen, rendimiento, actividad, tendencias } = estadisticasMock;

  const statsCards = [
    {
      title: 'Profesores',
      value: resumen.profesores,
      icon: Users,
      color: 'from-blue-500 to-blue-600',
      bgColor: 'bg-blue-50 dark:bg-blue-900/20',
      change: '+2 este mes'
    },
    {
      title: 'Estudiantes',
      value: resumen.estudiantes,
      icon: Users,
      color: 'from-emerald-500 to-emerald-600',
      bgColor: 'bg-emerald-50 dark:bg-emerald-900/20',
      change: '+5 este mes'
    },
    {
      title: 'Clases Activas',
      value: resumen.clasesActivas,
      icon: BookOpen,
      color: 'from-purple-500 to-purple-600',
      bgColor: 'bg-purple-50 dark:bg-purple-900/20',
      change: '+1 esta semana'
    },
    {
      title: 'Puntos Otorgados',
      value: resumen.puntosOtorgados.toLocaleString(),
      icon: Award,
      color: 'from-yellow-500 to-yellow-600',
      bgColor: 'bg-yellow-50 dark:bg-yellow-900/20',
      change: '+250 esta semana'
    }
  ];

  const performanceMetrics = [
    {
      label: 'Promedio General',
      value: rendimiento.promedioGeneral,
      max: 100,
      icon: TrendingUp,
      color: 'bg-blue-500'
    },
    {
      label: 'Tasa de Aprobación',
      value: rendimiento.aprobacion,
      max: 100,
      icon: Target,
      color: 'bg-green-500'
    },
    {
      label: 'Participación',
      value: rendimiento.participacion,
      max: 100,
      icon: Activity,
      color: 'bg-orange-500'
    },
    {
      label: 'Satisfacción',
      value: rendimiento.satisfaccion,
      max: 100,
      icon: Award,
      color: 'bg-purple-500'
    }
  ];

  const actividadReciente = [
    {
      label: 'Sesiones Activas',
      value: actividad.sesionesActivas,
      icon: Activity,
      color: 'text-green-600'
    },
    {
      label: 'Tareas Pendientes',
      value: actividad.tareasPendientes,
      icon: BookOpen,
      color: 'text-orange-600'
    },
    {
      label: 'Exámenes Programados',
      value: actividad.examenesProgramados,
      icon: Calendar,
      color: 'text-blue-600'
    }
  ];

  return (
    <div className="space-y-6">
      <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
              Estadísticas de la Institución
            </h2>
            <p className="text-gray-600 dark:text-gray-400">
              Resumen general del rendimiento institucional
            </p>
          </div>
          <div className="flex items-center space-x-2">
            <BarChart className="w-6 h-6 text-blue-600" />
            <span className="text-sm text-gray-500">Actualizado hace 5 min</span>
          </div>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          {statsCards.map((stat, index) => (
            <motion.div
              key={stat.title}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
              className={`${stat.bgColor} rounded-xl p-6 border border-gray-200 dark:border-gray-700`}
            >
              <div className="flex items-center justify-between mb-4">
                <div className={`w-12 h-12 bg-gradient-to-r ${stat.color} rounded-lg flex items-center justify-center`}>
                  <stat.icon className="w-6 h-6 text-white" />
                </div>
              </div>
              <div>
                <h3 className="text-2xl font-bold text-gray-900 dark:text-white mb-1">
                  {stat.value}
                </h3>
                <p className="text-gray-600 dark:text-gray-400 text-sm mb-2">
                  {stat.title}
                </p>
                <p className="text-xs text-green-600 dark:text-green-400">
                  {stat.change}
                </p>
              </div>
            </motion.div>
          ))}
        </div>

        {/* Performance Metrics */}
        <div className="bg-gray-50 dark:bg-gray-700 rounded-xl p-6 mb-6">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
            Métricas de Rendimiento
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {performanceMetrics.map((metric, index) => (
              <motion.div
                key={metric.label}
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ delay: index * 0.1 }}
                className="text-center"
              >
                <div className="flex items-center justify-center mb-3">
                  <metric.icon className="w-5 h-5 text-gray-600 dark:text-gray-400" />
                </div>
                <div className="relative w-20 h-20 mx-auto mb-3">
                  <svg className="w-20 h-20 transform -rotate-90" viewBox="0 0 36 36">
                    <path
                      d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                      fill="none"
                      stroke="currentColor"
                      strokeWidth="2"
                      className="text-gray-200 dark:text-gray-600"
                    />
                    <path
                      d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                      fill="none"
                      stroke="currentColor"
                      strokeWidth="2"
                      strokeDasharray={`${metric.value}, 100`}
                      className={metric.color.replace('bg-', 'text-')}
                    />
                  </svg>
                  <div className="absolute inset-0 flex items-center justify-center">
                    <span className="text-lg font-bold text-gray-900 dark:text-white">
                      {metric.value}%
                    </span>
                  </div>
                </div>
                <p className="text-sm text-gray-600 dark:text-gray-400">
                  {metric.label}
                </p>
              </motion.div>
            ))}
          </div>
        </div>

        {/* Recent Activity */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          
          {/* Activity Summary */}
          <div className="bg-gray-50 dark:bg-gray-700 rounded-xl p-6">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
              Actividad Reciente
            </h3>
            <div className="space-y-4">
              {actividadReciente.map((item, index) => (
                <motion.div
                  key={item.label}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: index * 0.1 }}
                  className="flex items-center justify-between p-3 bg-white dark:bg-gray-800 rounded-lg"
                >
                  <div className="flex items-center space-x-3">
                    <item.icon className={`w-5 h-5 ${item.color}`} />
                    <span className="text-gray-900 dark:text-white">{item.label}</span>
                  </div>
                  <span className="text-xl font-bold text-gray-900 dark:text-white">
                    {item.value}
                  </span>
                </motion.div>
              ))}
            </div>
          </div>

          {/* Trends Chart */}
          <div className="bg-gray-50 dark:bg-gray-700 rounded-xl p-6">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
              Tendencias (Últimos 4 meses)
            </h3>
            <div className="space-y-3">
              {tendencias.map((mes, index) => (
                <motion.div
                  key={mes.mes}
                  initial={{ opacity: 0, scaleX: 0 }}
                  animate={{ opacity: 1, scaleX: 1 }}
                  transition={{ delay: index * 0.2 }}
                  className="flex items-center justify-between"
                >
                  <span className="text-sm font-medium text-gray-600 dark:text-gray-400 w-12">
                    {mes.mes}
                  </span>
                  <div className="flex-1 mx-3">
                    <div className="flex items-center space-x-2">
                      <div className="flex-1 bg-gray-200 dark:bg-gray-600 rounded-full h-2">
                        <div
                          className="bg-blue-500 h-2 rounded-full"
                          style={{ width: `${(mes.estudiantes / 100) * 100}%` }}
                        />
                      </div>
                      <span className="text-xs text-gray-500 w-8">{mes.estudiantes}</span>
                    </div>
                  </div>
                  <div className="text-right">
                    <span className="text-sm font-medium text-gray-900 dark:text-white">
                      {mes.promedio}%
                    </span>
                  </div>
                </motion.div>
              ))}
            </div>
            <div className="mt-4 text-xs text-gray-500 dark:text-gray-400">
              <div className="flex justify-between">
                <span>Estudiantes activos</span>
                <span>Promedio general</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
