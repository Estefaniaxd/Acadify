import React from 'react';
import { motion } from 'framer-motion';
import { BarChart, TrendingUp, Users, BookOpen, Calendar, Activity } from 'lucide-react';

export default function AdminReportesPage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 via-white to-gray-100 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900 p-6">
      <div className="max-w-7xl mx-auto space-y-6">
        <motion.div initial={{ opacity: 0, y: -20 }} animate={{ opacity: 1, y: 0 }}>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white flex items-center gap-3">
            <BarChart className="w-8 h-8 text-blue-600" />
            Reportes y Análisis
          </h1>
          <p className="text-gray-600 dark:text-gray-400 mt-1">
            Estadísticas y métricas del sistema
          </p>
        </motion.div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {[
            { icon: Users, title: 'Usuarios Activos', value: '1,247', change: '+12%', color: 'blue' },
            { icon: BookOpen, title: 'Cursos Activos', value: '156', change: '+8%', color: 'green' },
            { icon: Calendar, title: 'Sesiones Hoy', value: '3,421', change: '+15%', color: 'purple' },
            { icon: Activity, title: 'Tasa de Finalización', value: '87%', change: '+5%', color: 'orange' },
            { icon: TrendingUp, title: 'Crecimiento Mensual', value: '23%', change: '+3%', color: 'pink' },
            { icon: BarChart, title: 'Satisfacción', value: '4.8/5', change: '+0.2', color: 'indigo' },
          ].map((stat, index) => (
            <motion.div
              key={stat.title}
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: index * 0.1 }}
              className="bg-white dark:bg-gray-800 rounded-2xl shadow-lg p-6 border border-gray-200 dark:border-gray-700"
            >
              <div className="flex items-start justify-between">
                <div>
                  <stat.icon className={`w-8 h-8 text-${stat.color}-600 mb-3`} />
                  <h3 className="text-sm font-medium text-gray-600 dark:text-gray-400">{stat.title}</h3>
                  <p className="text-3xl font-bold text-gray-900 dark:text-white mt-2">{stat.value}</p>
                </div>
                <span className="px-2 py-1 bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-300 rounded-lg text-xs font-medium">
                  {stat.change}
                </span>
              </div>
            </motion.div>
          ))}
        </div>

        <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-lg p-6 border border-gray-200 dark:border-gray-700">
          <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-4">
            Gráficas de Rendimiento
          </h2>
          <div className="h-64 flex items-center justify-center text-gray-400">
            <p>📊 Aquí irían gráficas interactivas (Chart.js / Recharts)</p>
          </div>
        </div>
      </div>
    </div>
  );
}
