/**
 * Panel de Control de Notificaciones
 * 
 * @module pages/PanelNotificacionesPage
 * @description Dashboard completo de notificaciones con estadísticas y configuración
 */

import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Bell, Settings, TrendingUp, Filter } from 'lucide-react';
import { Link } from 'react-router-dom';
import EstadisticasNotificaciones from '../components/notificaciones/EstadisticasNotificaciones';
import NotificacionesWidget from '../components/notificaciones/NotificacionesWidget';
import { useContadorNoLeidas } from '../hooks/useNotificaciones';

export default function PanelNotificacionesPage() {
  const { data: contador = 0 } = useContadorNoLeidas();
  const [vistaActiva, setVistaActiva] = useState<'resumen' | 'estadisticas'>('resumen');

  const tabs = [
    { id: 'resumen' as const, label: 'Resumen', icon: Bell },
    { id: 'estadisticas' as const, label: 'Estadísticas', icon: TrendingUp },
  ];

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      {/* Header */}
      <div className="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <div className="w-14 h-14 bg-gradient-to-br from-violet-500 to-purple-600 rounded-2xl flex items-center justify-center relative">
                <Bell className="w-7 h-7 text-white" />
                {contador > 0 && (
                  <div className="absolute -top-2 -right-2 w-6 h-6 bg-red-500 rounded-full flex items-center justify-center">
                    <span className="text-xs font-bold text-white">
                      {contador > 9 ? '9+' : contador}
                    </span>
                  </div>
                )}
              </div>
              <div>
                <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
                  Panel de Notificaciones
                </h1>
                <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                  Gestiona y monitorea todas tus notificaciones
                </p>
              </div>
            </div>

            <div className="flex items-center gap-3">
              <Link
                to="/configuracion/notificaciones"
                className="px-4 py-2 bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-xl font-medium hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors flex items-center gap-2"
              >
                <Settings className="w-5 h-5" />
                <span className="hidden sm:inline">Configuración</span>
              </Link>
              <Link
                to="/notificaciones"
                className="px-4 py-2 bg-gradient-to-r from-violet-600 to-purple-600 text-white rounded-xl font-semibold hover:shadow-lg transition-all flex items-center gap-2"
              >
                <Filter className="w-5 h-5" />
                <span className="hidden sm:inline">Ver Todas</span>
              </Link>
            </div>
          </div>

          {/* Tabs */}
          <div className="flex gap-2 mt-6">
            {tabs.map((tab) => {
              const Icon = tab.icon;
              const isActive = vistaActiva === tab.id;
              return (
                <button
                  key={tab.id}
                  onClick={() => setVistaActiva(tab.id)}
                  className={`relative px-4 py-2 rounded-xl font-medium transition-all flex items-center gap-2 ${
                    isActive
                      ? 'bg-violet-100 dark:bg-violet-900 text-violet-700 dark:text-violet-300'
                      : 'text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-700'
                  }`}
                >
                  <Icon className="w-4 h-4" />
                  {tab.label}
                  {isActive && (
                    <motion.div
                      layoutId="activeTab"
                      className="absolute bottom-0 left-0 right-0 h-0.5 bg-violet-600 dark:bg-violet-400"
                      transition={{ type: 'spring', duration: 0.5 }}
                    />
                  )}
                </button>
              );
            })}
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <AnimatePresence mode="wait">
          {vistaActiva === 'resumen' ? (
            <motion.div
              key="resumen"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              className="grid grid-cols-1 lg:grid-cols-3 gap-6"
            >
              {/* Columna principal */}
              <div className="lg:col-span-2 space-y-6">
                {/* Cards de métricas rápidas */}
                <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                  <MetricCard
                    title="Sin Leer"
                    value={contador}
                    color="from-red-500 to-orange-600"
                    icon={Bell}
                  />
                  <MetricCard
                    title="Hoy"
                    value="12"
                    color="from-blue-500 to-cyan-600"
                    icon={TrendingUp}
                  />
                  <MetricCard
                    title="Esta Semana"
                    value="48"
                    color="from-green-500 to-emerald-600"
                    icon={TrendingUp}
                  />
                </div>

                {/* Notificaciones recientes */}
                <NotificacionesWidget />
              </div>

              {/* Sidebar */}
              <div className="space-y-6">
                {/* Accesos rápidos */}
                <motion.div
                  initial={{ opacity: 0, x: 20 }}
                  animate={{ opacity: 1, x: 0 }}
                  className="bg-white dark:bg-gray-800 rounded-2xl border border-gray-200 dark:border-gray-700 p-6"
                >
                  <h3 className="font-bold text-gray-900 dark:text-white mb-4">
                    Accesos Rápidos
                  </h3>
                  <div className="space-y-2">
                    <QuickLink
                      to="/notificaciones?filter=no-leidas"
                      label="Ver no leídas"
                      badge={contador}
                    />
                    <QuickLink
                      to="/notificaciones?filter=importantes"
                      label="Importantes"
                    />
                    <QuickLink
                      to="/notificaciones?filter=tareas"
                      label="Tareas"
                    />
                    <QuickLink
                      to="/notificaciones?filter=mensajes"
                      label="Mensajes"
                    />
                  </div>
                </motion.div>

                {/* Tips */}
                <motion.div
                  initial={{ opacity: 0, x: 20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: 0.1 }}
                  className="bg-gradient-to-br from-violet-500 to-purple-600 rounded-2xl p-6 text-white"
                >
                  <h3 className="font-bold mb-2">💡 Consejo</h3>
                  <p className="text-sm text-white/90">
                    Configura tus preferencias de notificaciones para recibir solo lo
                    que necesitas.
                  </p>
                  <Link
                    to="/configuracion/notificaciones"
                    className="mt-4 inline-block px-4 py-2 bg-white/20 hover:bg-white/30 rounded-lg text-sm font-medium transition-colors"
                  >
                    Ir a configuración →
                  </Link>
                </motion.div>
              </div>
            </motion.div>
          ) : (
            <motion.div
              key="estadisticas"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
            >
              <EstadisticasNotificaciones />
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
}

// Componentes auxiliares
interface MetricCardProps {
  title: string;
  value: number | string;
  color: string;
  icon: React.ElementType;
}

function MetricCard({ title, value, color, icon: Icon }: MetricCardProps) {
  return (
    <motion.div
      whileHover={{ scale: 1.02, y: -2 }}
      className="bg-white dark:bg-gray-800 rounded-2xl border border-gray-200 dark:border-gray-700 p-4"
    >
      <div className="flex items-start justify-between mb-3">
        <div className={`w-10 h-10 bg-gradient-to-br ${color} rounded-xl flex items-center justify-center`}>
          <Icon className="w-5 h-5 text-white" />
        </div>
      </div>
      <h3 className="text-2xl font-bold text-gray-900 dark:text-white mb-1">{value}</h3>
      <p className="text-sm text-gray-600 dark:text-gray-400">{title}</p>
    </motion.div>
  );
}

interface QuickLinkProps {
  to: string;
  label: string;
  badge?: number;
}

function QuickLink({ to, label, badge }: QuickLinkProps) {
  return (
    <Link
      to={to}
      className="flex items-center justify-between px-3 py-2 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors group"
    >
      <span className="text-sm text-gray-700 dark:text-gray-300 group-hover:text-violet-600 dark:group-hover:text-violet-400">
        {label}
      </span>
      {badge !== undefined && badge > 0 && (
        <span className="px-2 py-0.5 bg-red-100 dark:bg-red-900 text-red-700 dark:text-red-300 text-xs font-medium rounded-full">
          {badge}
        </span>
      )}
    </Link>
  );
}
