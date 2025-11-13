/**
 * Módulo de Puntos del Usuario - Versión Mejorada
 * Con gráfico de evolución de puntos y niveles a lo largo del tiempo
 */

import { useState, useMemo } from 'react';
import { motion } from 'framer-motion';
import { 
  Star, TrendingUp, Award, Zap, 
  ChevronRight, ArrowUp, ArrowDown, 
  Trophy, Target, Clock, Calendar,
  LineChart as LineChartIcon, BarChart3
} from 'lucide-react';
import { 
  LineChart, Line, BarChart, Bar, AreaChart, Area,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend, 
  ResponsiveContainer, ReferenceLine
} from 'recharts';
import { useMisPuntos } from '../../hooks/useGamificacion';
import { obtenerColorNivel, formatearPuntos } from '../../services/gamificacion.service';
import { format, subDays, subMonths, startOfDay, endOfDay } from 'date-fns';
import { es } from 'date-fns/locale';

type TipoGrafico = 'linea' | 'area' | 'barras';
type PeriodoTiempo = '7dias' | '30dias' | '3meses' | 'todo';

// Componente de Tooltip personalizado para el gráfico
const CustomTooltip = ({ active, payload, label }: any) => {
  if (active && payload && payload.length) {
    return (
      <div className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg shadow-lg p-4">
        <p className="text-sm font-semibold text-gray-900 dark:text-white mb-2">
          {label}
        </p>
        {payload.map((entry: any, index: number) => (
          <div key={index} className="flex items-center gap-2 text-sm">
            <div 
              className="w-3 h-3 rounded-full" 
              style={{ backgroundColor: entry.color }}
            />
            <span className="text-gray-600 dark:text-gray-400">
              {entry.name}:
            </span>
            <span className="font-bold text-gray-900 dark:text-white">
              {entry.name === 'Nivel' ? entry.value : formatearPuntos(entry.value)}
            </span>
          </div>
        ))}
      </div>
    );
  }
  return null;
};

export default function PuntosUsuarioMejorado() {
  const { data: puntos, isLoading, isError } = useMisPuntos();
  const [tipoGrafico, setTipoGrafico] = useState<TipoGrafico>('area');
  const [periodo, setPeriodo] = useState<PeriodoTiempo>('30dias');

  // Generar datos de evolución (simulados - en producción vendrían del backend)
  const datosEvolucion = useMemo(() => {
    if (!puntos) return [];

    const hoy = new Date();
    let dias = 30;
    
    switch (periodo) {
      case '7dias':
        dias = 7;
        break;
      case '30dias':
        dias = 30;
        break;
      case '3meses':
        dias = 90;
        break;
      case 'todo':
        dias = 180; // 6 meses
        break;
    }

    // Generar datos simulados de evolución
    const datos = [];
    const puntosActuales = puntos.puntos_acumulados;
    const puntosPorDia = Math.floor(puntosActuales / dias);

    for (let i = dias - 1; i >= 0; i--) {
      const fecha = subDays(hoy, i);
      const puntosDelDia = puntosPorDia * (dias - i);
      const nivel = Math.floor(puntosDelDia / 100) + 1; // Nivel estimado
      
      datos.push({
        fecha: format(fecha, periodo === '7dias' || periodo === '30dias' ? 'd MMM' : 'MMM yyyy', { locale: es }),
        puntos: puntosDelDia + Math.floor(Math.random() * puntosPorDia * 0.2), // Variación
        nivel: Math.min(nivel, 50), // Máximo nivel 50
        puntosGanados: Math.floor(Math.random() * 100) + 20,
      });
    }

    return datos;
  }, [puntos, periodo]);

  // Calcular estadísticas del periodo
  const estadisticasPeriodo = useMemo(() => {
    if (datosEvolucion.length === 0) return null;

    const puntosInicio = datosEvolucion[0].puntos;
    const puntosFin = datosEvolucion[datosEvolucion.length - 1].puntos;
    const diferencia = puntosFin - puntosInicio;
    const porcentajeCambio = puntosInicio > 0 ? (diferencia / puntosInicio) * 100 : 0;
    
    const promedioGanado = datosEvolucion.reduce((sum, d) => sum + d.puntosGanados, 0) / datosEvolucion.length;
    const maxPuntosGanados = Math.max(...datosEvolucion.map(d => d.puntosGanados));
    const minPuntosGanados = Math.min(...datosEvolucion.map(d => d.puntosGanados));

    return {
      diferencia,
      porcentajeCambio,
      promedioGanado,
      maxPuntosGanados,
      minPuntosGanados,
    };
  }, [datosEvolucion]);

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-violet-50 via-white to-purple-50 dark:from-gray-900 dark:via-gray-800 dark:to-purple-900 flex items-center justify-center">
        <div className="text-center">
          <div className="w-16 h-16 border-4 border-violet-500 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-gray-600 dark:text-gray-400">Cargando puntos...</p>
        </div>
      </div>
    );
  }

  if (isError || !puntos) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-violet-50 via-white to-purple-50 dark:from-gray-900 dark:via-gray-800 dark:to-purple-900 flex items-center justify-center">
        <div className="text-center">
          <div className="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <span className="text-2xl">❌</span>
          </div>
          <p className="text-red-600">Error al cargar los puntos</p>
        </div>
      </div>
    );
  }

  const { puntos_acumulados, nivel_actual, nivel_info, historial_reciente, insignias_obtenidas } = puntos;

  return (
    <div className="min-h-screen bg-gradient-to-br from-violet-50 via-white to-purple-50 dark:from-gray-900 dark:via-gray-800 dark:to-purple-900 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-8"
        >
          <h1 className="text-4xl font-bold text-gray-900 dark:text-white mb-2 flex items-center gap-3">
            <Star className="w-10 h-10 text-yellow-500" />
            Mis Puntos
          </h1>
          <p className="text-gray-600 dark:text-gray-400">
            Consulta tus puntos acumulados, nivel actual y evolución en el tiempo
          </p>
        </motion.div>

        {/* Grid principal */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
          {/* Card de Puntos Totales */}
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            className="lg:col-span-1"
          >
            <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-lg p-6 border border-gray-200 dark:border-gray-700">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-lg font-semibold text-gray-900 dark:text-white">
                  Puntos Totales
                </h2>
                <div className="w-12 h-12 bg-gradient-to-br from-yellow-500 to-orange-600 rounded-xl flex items-center justify-center">
                  <Star className="w-6 h-6 text-white" />
                </div>
              </div>
              <p className="text-5xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-yellow-600 to-orange-600 mb-2">
                {formatearPuntos(puntos_acumulados)}
              </p>
              <p className="text-sm text-gray-600 dark:text-gray-400">
                Puntos acumulados
              </p>
              
              {/* Cambio en el periodo */}
              {estadisticasPeriodo && (
                <div className={`flex items-center gap-2 mt-4 px-3 py-2 rounded-lg ${
                  estadisticasPeriodo.diferencia >= 0 
                    ? 'bg-green-50 dark:bg-green-900/20' 
                    : 'bg-red-50 dark:bg-red-900/20'
                }`}>
                  {estadisticasPeriodo.diferencia >= 0 ? (
                    <ArrowUp className="w-4 h-4 text-green-600 dark:text-green-400" />
                  ) : (
                    <ArrowDown className="w-4 h-4 text-red-600 dark:text-red-400" />
                  )}
                  <span className={`text-sm font-semibold ${
                    estadisticasPeriodo.diferencia >= 0 
                      ? 'text-green-600 dark:text-green-400' 
                      : 'text-red-600 dark:text-red-400'
                  }`}>
                    {estadisticasPeriodo.diferencia >= 0 ? '+' : ''}
                    {formatearPuntos(Math.abs(estadisticasPeriodo.diferencia))} pts
                  </span>
                  <span className="text-xs text-gray-600 dark:text-gray-400">
                    ({estadisticasPeriodo.porcentajeCambio.toFixed(1)}%)
                  </span>
                </div>
              )}
            </div>
          </motion.div>

          {/* Card de Nivel Actual */}
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.1 }}
            className="lg:col-span-2"
          >
            <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-lg p-6 border border-gray-200 dark:border-gray-700">
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-3">
                  <div className={`w-16 h-16 bg-gradient-to-br ${obtenerColorNivel(nivel_actual)} rounded-xl flex items-center justify-center`}>
                    <Trophy className="w-8 h-8 text-white" />
                  </div>
                  <div>
                    <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
                      {nivel_info.nombre}
                    </h2>
                    <p className="text-sm text-gray-600 dark:text-gray-400">
                      Nivel {nivel_info.numero}
                    </p>
                  </div>
                </div>
                <div className="text-right">
                  <p className="text-sm text-gray-600 dark:text-gray-400">
                    Progreso al siguiente nivel
                  </p>
                  <p className="text-2xl font-bold text-violet-600 dark:text-violet-400">
                    {nivel_info.progreso_porcentaje}%
                  </p>
                </div>
              </div>

              {/* Barra de progreso */}
              <div className="relative w-full h-4 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
                <motion.div
                  initial={{ width: 0 }}
                  animate={{ width: `${nivel_info.progreso_porcentaje}%` }}
                  transition={{ duration: 1, ease: 'easeOut' }}
                  className={`h-full bg-gradient-to-r ${obtenerColorNivel(nivel_actual)} rounded-full`}
                />
              </div>

              <div className="flex items-center justify-between mt-2">
                <p className="text-sm text-gray-600 dark:text-gray-400">
                  {formatearPuntos(nivel_info.puntos_minimos)} pts
                </p>
                <p className="text-sm font-semibold text-violet-600 dark:text-violet-400">
                  {formatearPuntos(nivel_info.puntos_para_siguiente)} pts para subir
                </p>
                <p className="text-sm text-gray-600 dark:text-gray-400">
                  {formatearPuntos(nivel_info.puntos_maximos)} pts
                </p>
              </div>
            </div>
          </motion.div>
        </div>

        {/* Gráfico de Evolución */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="mb-8"
        >
          <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-lg p-6 border border-gray-200 dark:border-gray-700">
            {/* Header del gráfico */}
            <div className="flex flex-col md:flex-row items-start md:items-center justify-between mb-6 gap-4">
              <div>
                <h2 className="text-2xl font-bold text-gray-900 dark:text-white flex items-center gap-2 mb-2">
                  <LineChartIcon className="w-6 h-6 text-violet-600" />
                  Evolución de Puntos
                </h2>
                {estadisticasPeriodo && (
                  <div className="flex items-center gap-4 text-sm">
                    <div className="flex items-center gap-2">
                      <span className="text-gray-600 dark:text-gray-400">Promedio diario:</span>
                      <span className="font-semibold text-blue-600 dark:text-blue-400">
                        {formatearPuntos(Math.round(estadisticasPeriodo.promedioGanado))} pts
                      </span>
                    </div>
                    <div className="flex items-center gap-2">
                      <span className="text-gray-600 dark:text-gray-400">Máximo:</span>
                      <span className="font-semibold text-green-600 dark:text-green-400">
                        {formatearPuntos(estadisticasPeriodo.maxPuntosGanados)} pts
                      </span>
                    </div>
                  </div>
                )}
              </div>

              <div className="flex flex-wrap items-center gap-3">
                {/* Selector de periodo */}
                <div className="flex gap-2 bg-gray-100 dark:bg-gray-700 rounded-lg p-1">
                  {[
                    { value: '7dias', label: '7D' },
                    { value: '30dias', label: '30D' },
                    { value: '3meses', label: '3M' },
                    { value: 'todo', label: 'Todo' },
                  ].map((p) => (
                    <button
                      key={p.value}
                      onClick={() => setPeriodo(p.value as PeriodoTiempo)}
                      className={`px-3 py-1.5 rounded-md text-sm font-medium transition-colors ${
                        periodo === p.value
                          ? 'bg-violet-600 text-white'
                          : 'text-gray-600 dark:text-gray-400 hover:bg-gray-200 dark:hover:bg-gray-600'
                      }`}
                    >
                      {p.label}
                    </button>
                  ))}
                </div>

                {/* Selector de tipo de gráfico */}
                <div className="flex gap-2 bg-gray-100 dark:bg-gray-700 rounded-lg p-1">
                  <button
                    onClick={() => setTipoGrafico('linea')}
                    className={`p-2 rounded-md transition-colors ${
                      tipoGrafico === 'linea'
                        ? 'bg-violet-600 text-white'
                        : 'text-gray-600 dark:text-gray-400 hover:bg-gray-200 dark:hover:bg-gray-600'
                    }`}
                    title="Línea"
                  >
                    <TrendingUp className="w-4 h-4" />
                  </button>
                  <button
                    onClick={() => setTipoGrafico('area')}
                    className={`p-2 rounded-md transition-colors ${
                      tipoGrafico === 'area'
                        ? 'bg-violet-600 text-white'
                        : 'text-gray-600 dark:text-gray-400 hover:bg-gray-200 dark:hover:bg-gray-600'
                    }`}
                    title="Área"
                  >
                    <LineChartIcon className="w-4 h-4" />
                  </button>
                  <button
                    onClick={() => setTipoGrafico('barras')}
                    className={`p-2 rounded-md transition-colors ${
                      tipoGrafico === 'barras'
                        ? 'bg-violet-600 text-white'
                        : 'text-gray-600 dark:text-gray-400 hover:bg-gray-200 dark:hover:bg-gray-600'
                    }`}
                    title="Barras"
                  >
                    <BarChart3 className="w-4 h-4" />
                  </button>
                </div>
              </div>
            </div>

            {/* Gráfico */}
            <div className="h-80">
              <ResponsiveContainer width="100%" height="100%">
                {tipoGrafico === 'linea' ? (
                  <LineChart data={datosEvolucion}>
                    <CartesianGrid strokeDasharray="3 3" className="stroke-gray-300 dark:stroke-gray-600" />
                    <XAxis 
                      dataKey="fecha" 
                      className="text-gray-600 dark:text-gray-400"
                      tick={{ fill: 'currentColor' }}
                    />
                    <YAxis 
                      yAxisId="left"
                      className="text-gray-600 dark:text-gray-400"
                      tick={{ fill: 'currentColor' }}
                    />
                    <YAxis 
                      yAxisId="right"
                      orientation="right"
                      className="text-gray-600 dark:text-gray-400"
                      tick={{ fill: 'currentColor' }}
                    />
                    <Tooltip content={<CustomTooltip />} />
                    <Legend />
                    <Line 
                      yAxisId="left"
                      type="monotone" 
                      dataKey="puntos" 
                      stroke="#8b5cf6" 
                      strokeWidth={3}
                      dot={{ r: 4, fill: '#8b5cf6' }}
                      activeDot={{ r: 6 }}
                      name="Puntos Totales"
                    />
                    <Line 
                      yAxisId="right"
                      type="monotone" 
                      dataKey="nivel" 
                      stroke="#f59e0b" 
                      strokeWidth={2}
                      dot={{ r: 3, fill: '#f59e0b' }}
                      name="Nivel"
                    />
                  </LineChart>
                ) : tipoGrafico === 'area' ? (
                  <AreaChart data={datosEvolucion}>
                    <defs>
                      <linearGradient id="colorPuntos" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#8b5cf6" stopOpacity={0.8}/>
                        <stop offset="95%" stopColor="#8b5cf6" stopOpacity={0.1}/>
                      </linearGradient>
                      <linearGradient id="colorNivel" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#f59e0b" stopOpacity={0.8}/>
                        <stop offset="95%" stopColor="#f59e0b" stopOpacity={0.1}/>
                      </linearGradient>
                    </defs>
                    <CartesianGrid strokeDasharray="3 3" className="stroke-gray-300 dark:stroke-gray-600" />
                    <XAxis 
                      dataKey="fecha" 
                      className="text-gray-600 dark:text-gray-400"
                      tick={{ fill: 'currentColor' }}
                    />
                    <YAxis 
                      yAxisId="left"
                      className="text-gray-600 dark:text-gray-400"
                      tick={{ fill: 'currentColor' }}
                    />
                    <YAxis 
                      yAxisId="right"
                      orientation="right"
                      className="text-gray-600 dark:text-gray-400"
                      tick={{ fill: 'currentColor' }}
                    />
                    <Tooltip content={<CustomTooltip />} />
                    <Legend />
                    <Area 
                      yAxisId="left"
                      type="monotone" 
                      dataKey="puntos" 
                      stroke="#8b5cf6" 
                      strokeWidth={2}
                      fill="url(#colorPuntos)"
                      name="Puntos Totales"
                    />
                    <Area 
                      yAxisId="right"
                      type="monotone" 
                      dataKey="nivel" 
                      stroke="#f59e0b" 
                      strokeWidth={2}
                      fill="url(#colorNivel)"
                      name="Nivel"
                    />
                  </AreaChart>
                ) : (
                  <BarChart data={datosEvolucion}>
                    <CartesianGrid strokeDasharray="3 3" className="stroke-gray-300 dark:stroke-gray-600" />
                    <XAxis 
                      dataKey="fecha" 
                      className="text-gray-600 dark:text-gray-400"
                      tick={{ fill: 'currentColor' }}
                    />
                    <YAxis 
                      className="text-gray-600 dark:text-gray-400"
                      tick={{ fill: 'currentColor' }}
                    />
                    <Tooltip content={<CustomTooltip />} />
                    <Legend />
                    <Bar 
                      dataKey="puntosGanados" 
                      fill="#8b5cf6" 
                      radius={[8, 8, 0, 0]}
                      name="Puntos Ganados"
                    />
                  </BarChart>
                )}
              </ResponsiveContainer>
            </div>
          </div>
        </motion.div>

        {/* Grid secundario: Insignias e Historial */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Insignias Recientes */}
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.3 }}
          >
            <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-lg p-6 border border-gray-200 dark:border-gray-700">
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-xl font-bold text-gray-900 dark:text-white flex items-center gap-2">
                  <Award className="w-6 h-6 text-violet-600" />
                  Insignias Recientes
                </h2>
                <span className="px-3 py-1 bg-violet-100 dark:bg-violet-900 text-violet-700 dark:text-violet-300 rounded-full text-sm font-semibold">
                  {insignias_obtenidas.length} total
                </span>
              </div>

              {insignias_obtenidas.length > 0 ? (
                <div className="space-y-3">
                  {insignias_obtenidas.slice(0, 5).map((insignia, idx) => (
                    <motion.div
                      key={insignia.id}
                      initial={{ opacity: 0, y: 10 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ delay: 0.1 * idx }}
                      className="flex items-center gap-4 p-3 rounded-xl hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors duration-200"
                    >
                      <div className="text-3xl">{insignia.icono}</div>
                      <div className="flex-1">
                        <h3 className="font-semibold text-gray-900 dark:text-white">
                          {insignia.nombre}
                        </h3>
                        <p className="text-sm text-gray-600 dark:text-gray-400">
                          {insignia.descripcion}
                        </p>
                      </div>
                      <span className="px-2 py-1 bg-yellow-100 dark:bg-yellow-900 text-yellow-700 dark:text-yellow-300 rounded-lg text-xs font-semibold">
                        {insignia.rareza}
                      </span>
                    </motion.div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-8">
                  <div className="w-16 h-16 bg-gray-100 dark:bg-gray-700 rounded-full flex items-center justify-center mx-auto mb-3">
                    <Award className="w-8 h-8 text-gray-400" />
                  </div>
                  <p className="text-gray-600 dark:text-gray-400">
                    Aún no has obtenido insignias
                  </p>
                  <p className="text-sm text-gray-500 dark:text-gray-500 mt-1">
                    ¡Completa actividades para desbloquearlas!
                  </p>
                </div>
              )}
            </div>
          </motion.div>

          {/* Historial Reciente */}
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.4 }}
          >
            <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-lg p-6 border border-gray-200 dark:border-gray-700">
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-xl font-bold text-gray-900 dark:text-white flex items-center gap-2">
                  <Clock className="w-6 h-6 text-blue-600" />
                  Actividad Reciente
                </h2>
              </div>

              {historial_reciente.length > 0 ? (
                <div className="space-y-3">
                  {historial_reciente.map((cambio, idx) => (
                    <motion.div
                      key={cambio.id}
                      initial={{ opacity: 0, y: 10 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ delay: 0.1 * idx }}
                      className="flex items-center gap-4 p-3 rounded-xl hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors duration-200"
                    >
                      <div className={`w-10 h-10 rounded-full flex items-center justify-center ${
                        cambio.tipo === 'ganado' 
                          ? 'bg-green-100 dark:bg-green-900' 
                          : 'bg-red-100 dark:bg-red-900'
                      }`}>
                        {cambio.tipo === 'ganado' ? (
                          <ArrowUp className="w-5 h-5 text-green-600 dark:text-green-400" />
                        ) : (
                          <ArrowDown className="w-5 h-5 text-red-600 dark:text-red-400" />
                        )}
                      </div>
                      <div className="flex-1">
                        <p className="font-semibold text-gray-900 dark:text-white">
                          {cambio.tipo === 'ganado' ? '+' : '-'}{formatearPuntos(Math.abs(cambio.puntos))} pts
                        </p>
                        <p className="text-sm text-gray-600 dark:text-gray-400">
                          {cambio.razon}
                        </p>
                        <p className="text-xs text-gray-500 dark:text-gray-500 mt-1">
                          {format(new Date(cambio.fecha), "d 'de' MMMM, HH:mm", { locale: es })}
                        </p>
                      </div>
                    </motion.div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-8">
                  <div className="w-16 h-16 bg-gray-100 dark:bg-gray-700 rounded-full flex items-center justify-center mx-auto mb-3">
                    <TrendingUp className="w-8 h-8 text-gray-400" />
                  </div>
                  <p className="text-gray-600 dark:text-gray-400">
                    No hay actividad reciente
                  </p>
                </div>
              )}
            </div>
          </motion.div>
        </div>
      </div>
    </div>
  );
}
