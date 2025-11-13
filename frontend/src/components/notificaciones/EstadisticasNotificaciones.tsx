/**
 * Panel de Estadísticas de Notificaciones
 * 
 * @module components/notificaciones/EstadisticasNotificaciones
 * @description Panel con estadísticas y métricas de notificaciones
 */

import { motion } from 'framer-motion';
import {
  Bell, Check, Eye, Clock, TrendingUp,
  MessageSquare, BookOpen, Trophy, Calendar
} from 'lucide-react';
import { useNotificaciones } from '../../hooks/useNotificaciones';

export default function EstadisticasNotificaciones() {
  const { data: todasNotificaciones = [] } = useNotificaciones({
    limite: 100,
    solo_no_leidas: false,
  });

  // Calcular estadísticas
  const total = todasNotificaciones.length;
  const leidas = todasNotificaciones.filter((n) => n.leida).length;
  const noLeidas = total - leidas;
  const porcentajeLeidas = total > 0 ? Math.round((leidas / total) * 100) : 0;

  // Notificaciones por tipo
  const porTipo = todasNotificaciones.reduce((acc, n) => {
    acc[n.tipo_notificacion] = (acc[n.tipo_notificacion] || 0) + 1;
    return acc;
  }, {} as Record<string, number>);

  // Top 3 tipos de notificaciones
  const topTipos = Object.entries(porTipo)
    .sort(([, a], [, b]) => b - a)
    .slice(0, 3);

  // Notificaciones de hoy
  const hoy = new Date();
  hoy.setHours(0, 0, 0, 0);
  const notificacionesHoy = todasNotificaciones.filter((n) => {
    const fecha = new Date(n.fecha_creacion);
    return fecha >= hoy;
  }).length;

  // Tasa de respuesta (notificaciones leídas en menos de 1 hora)
  const leyendasRapidas = todasNotificaciones.filter((n) => {
    if (!n.leida || !n.fecha_lectura) return false;
    const creacion = new Date(n.fecha_creacion).getTime();
    const lectura = new Date(n.fecha_lectura).getTime();
    const diferencia = lectura - creacion;
    return diferencia < 3600000; // 1 hora en ms
  }).length;
  const tasaRespuestaRapida = total > 0 ? Math.round((leyendasRapidas / total) * 100) : 0;

  const stats = [
    {
      label: 'Total Notificaciones',
      value: total,
      icon: Bell,
      color: 'from-violet-500 to-purple-600',
      change: notificacionesHoy > 0 ? `+${notificacionesHoy} hoy` : 'Sin cambios',
    },
    {
      label: 'Sin Leer',
      value: noLeidas,
      icon: Eye,
      color: 'from-red-500 to-orange-600',
      change: noLeidas > 5 ? 'Requiere atención' : 'Todo bien',
    },
    {
      label: 'Leídas',
      value: leidas,
      icon: Check,
      color: 'from-green-500 to-emerald-600',
      change: `${porcentajeLeidas}% del total`,
    },
    {
      label: 'Respuesta Rápida',
      value: `${tasaRespuestaRapida}%`,
      icon: TrendingUp,
      color: 'from-blue-500 to-cyan-600',
      change: tasaRespuestaRapida > 70 ? '¡Excelente!' : 'Puede mejorar',
    },
  ];

  const tipoIcons: Record<string, React.ElementType> = {
    mensaje_directo: MessageSquare,
    tarea_nueva: BookOpen,
    logro_desbloqueado: Trophy,
    clase_cancelada: Calendar,
  };

  return (
    <div className="space-y-6">
      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {stats.map((stat, index) => {
          const Icon = stat.icon;
          return (
            <motion.div
              key={stat.label}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
              className="bg-white dark:bg-gray-800 rounded-2xl border border-gray-200 dark:border-gray-700 p-6"
            >
              <div className="flex items-start justify-between mb-4">
                <div
                  className={`w-12 h-12 bg-gradient-to-br ${stat.color} rounded-xl flex items-center justify-center`}
                >
                  <Icon className="w-6 h-6 text-white" />
                </div>
              </div>
              <h3 className="text-2xl font-bold text-gray-900 dark:text-white mb-1">
                {stat.value}
              </h3>
              <p className="text-sm font-medium text-gray-600 dark:text-gray-400 mb-2">
                {stat.label}
              </p>
              <p className="text-xs text-gray-500 dark:text-gray-500">
                {stat.change}
              </p>
            </motion.div>
          );
        })}
      </div>

      {/* Top Tipos de Notificaciones */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.4 }}
        className="bg-white dark:bg-gray-800 rounded-2xl border border-gray-200 dark:border-gray-700 p-6"
      >
        <h3 className="text-lg font-bold text-gray-900 dark:text-white mb-6">
          Tipos Más Frecuentes
        </h3>

        {topTipos.length === 0 ? (
          <p className="text-center text-gray-600 dark:text-gray-400 py-8">
            No hay datos suficientes
          </p>
        ) : (
          <div className="space-y-4">
            {topTipos.map(([tipo, cantidad], index) => {
              const Icon = tipoIcons[tipo] || Bell;
              const porcentaje = total > 0 ? Math.round((cantidad / total) * 100) : 0;
              const nombreTipo = tipo
                .split('_')
                .map((p) => p.charAt(0).toUpperCase() + p.slice(1))
                .join(' ');

              return (
                <div key={tipo}>
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center gap-3">
                      <div className="w-8 h-8 bg-violet-100 dark:bg-violet-900/30 rounded-lg flex items-center justify-center">
                        <Icon className="w-4 h-4 text-violet-600 dark:text-violet-400" />
                      </div>
                      <div>
                        <p className="text-sm font-medium text-gray-900 dark:text-white">
                          {nombreTipo}
                        </p>
                        <p className="text-xs text-gray-500 dark:text-gray-500">
                          {cantidad} notificaciones
                        </p>
                      </div>
                    </div>
                    <span className="text-sm font-semibold text-gray-900 dark:text-white">
                      {porcentaje}%
                    </span>
                  </div>
                  {/* Barra de progreso */}
                  <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                    <motion.div
                      initial={{ width: 0 }}
                      animate={{ width: `${porcentaje}%` }}
                      transition={{ duration: 0.8, delay: index * 0.1 }}
                      className="bg-gradient-to-r from-violet-500 to-purple-600 h-2 rounded-full"
                    />
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </motion.div>

      {/* Actividad Reciente (Timeline) */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.5 }}
        className="bg-white dark:bg-gray-800 rounded-2xl border border-gray-200 dark:border-gray-700 p-6"
      >
        <div className="flex items-center gap-3 mb-6">
          <Clock className="w-5 h-5 text-violet-600 dark:text-violet-400" />
          <h3 className="text-lg font-bold text-gray-900 dark:text-white">
            Actividad de Hoy
          </h3>
        </div>

        <div className="flex items-center justify-center py-8">
          <div className="text-center">
            <div className="w-16 h-16 bg-violet-100 dark:bg-violet-900/30 rounded-full flex items-center justify-center mx-auto mb-3">
              <Bell className="w-8 h-8 text-violet-600 dark:text-violet-400" />
            </div>
            <p className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
              {notificacionesHoy}
            </p>
            <p className="text-sm text-gray-600 dark:text-gray-400">
              Notificaciones recibidas hoy
            </p>
          </div>
        </div>
      </motion.div>
    </div>
  );
}
