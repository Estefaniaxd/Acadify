/**
 * MisionesPage Component
 * 
 * @module pages/MisionesPage
 * @description Página principal del sistema de misiones con tabs para diferentes
 * frecuencias, estadísticas y gestión de progreso.
 */

import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Trophy,
  Target,
  Flame,
  Calendar,
  TrendingUp,
  CheckCircle,
  Clock,
  Award,
  Star,
} from 'lucide-react';
import MisionCard from '../components/misiones/MisionCard';
import {
  useMisionesDisponibles,
  useEstadisticasMisiones,
  useReclamarRecompensa,
  useConteoMisiones,
} from '../hooks/useMisiones';
import { FrecuenciaMision, MisionUsuarioConDetalle } from '../services/misiones.service';

type TabOption = FrecuenciaMision | 'todas';

/**
 * Página principal de misiones
 */
export default function MisionesPage() {
  const [activeTab, setActiveTab] = useState<TabOption>('diaria');

  // Queries
  const { data: misionesDisponibles, isLoading: isLoadingMisiones } = useMisionesDisponibles();
  const { data: estadisticas, isLoading: isLoadingEstadisticas } = useEstadisticasMisiones();
  const conteo = useConteoMisiones();

  // Mutations
  const reclamarMutation = useReclamarRecompensa();

  const handleReclamar = (misionUsuarioId: string) => {
    reclamarMutation.mutate(misionUsuarioId);
  };

  // Obtener misiones según tab activo
  const getMisionesActivas = () => {
    if (!misionesDisponibles) return [];

    switch (activeTab) {
      case 'diaria':
        return misionesDisponibles.diarias;
      case 'semanal':
        return misionesDisponibles.semanales;
      case 'mensual':
        return misionesDisponibles.mensuales;
      case 'unica':
        return misionesDisponibles.unicas;
      case 'todas':
        return [
          ...misionesDisponibles.diarias,
          ...misionesDisponibles.semanales,
          ...misionesDisponibles.mensuales,
          ...misionesDisponibles.unicas,
        ];
      default:
        return [];
    }
  };

  const misionesActivas = getMisionesActivas();

  // Tabs configuration
  const tabs: { value: TabOption; label: string; icon: React.ElementType; color: string }[] = [
    { value: 'diaria', label: 'Diarias', icon: Flame, color: 'text-orange-500' },
    { value: 'semanal', label: 'Semanales', icon: Calendar, color: 'text-blue-500' },
    { value: 'mensual', label: 'Mensuales', icon: Star, color: 'text-purple-500' },
    { value: 'unica', label: 'Únicas', icon: Award, color: 'text-green-500' },
    { value: 'todas', label: 'Todas', icon: Target, color: 'text-gray-600' },
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 via-blue-50 to-purple-50 p-6">
      <div className="mx-auto max-w-7xl">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-8"
        >
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-4xl font-bold text-gray-900 flex items-center gap-3">
                <Target className="h-10 w-10 text-blue-600" />
                Misiones
              </h1>
              <p className="mt-2 text-gray-600">
                Completa misiones para ganar puntos, experiencia y recompensas
              </p>
            </div>

            {/* Auto-refresh indicator */}
            {!isLoadingMisiones && (
              <motion.div
                animate={{ rotate: 360 }}
                transition={{ duration: 2, repeat: Infinity, ease: 'linear' }}
                className="text-blue-500"
              >
                <Clock className="h-6 w-6" />
              </motion.div>
            )}
          </div>
        </motion.div>

        {/* Estadísticas */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="mb-8 grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4"
        >
          {/* Total Completadas */}
          <div className="rounded-xl bg-white p-6 shadow-lg border-2 border-green-200">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Completadas</p>
                <p className="mt-2 text-3xl font-bold text-green-600">
                  {estadisticas?.total_completadas || 0}
                </p>
              </div>
              <div className="rounded-full bg-green-100 p-3">
                <CheckCircle className="h-8 w-8 text-green-600" />
              </div>
            </div>
          </div>

          {/* En Progreso */}
          <div className="rounded-xl bg-white p-6 shadow-lg border-2 border-blue-200">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">En Progreso</p>
                <p className="mt-2 text-3xl font-bold text-blue-600">
                  {conteo.enProgreso}
                </p>
              </div>
              <div className="rounded-full bg-blue-100 p-3">
                <TrendingUp className="h-8 w-8 text-blue-600" />
              </div>
            </div>
          </div>

          {/* Disponibles */}
          <div className="rounded-xl bg-white p-6 shadow-lg border-2 border-purple-200">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Disponibles</p>
                <p className="mt-2 text-3xl font-bold text-purple-600">
                  {misionesDisponibles?.total_disponibles || 0}
                </p>
              </div>
              <div className="rounded-full bg-purple-100 p-3">
                <Target className="h-8 w-8 text-purple-600" />
              </div>
            </div>
          </div>

          {/* Completadas Hoy */}
          <div className="rounded-xl bg-white p-6 shadow-lg border-2 border-orange-200">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Hoy</p>
                <p className="mt-2 text-3xl font-bold text-orange-600">
                  {misionesDisponibles?.total_completadas_hoy || 0}
                </p>
              </div>
              <div className="rounded-full bg-orange-100 p-3">
                <Flame className="h-8 w-8 text-orange-600" />
              </div>
            </div>
          </div>
        </motion.div>

        {/* Tabs */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="mb-8"
        >
          <div className="flex flex-wrap gap-2 rounded-xl bg-white p-2 shadow-lg">
            {tabs.map((tab) => {
              const Icon = tab.icon;
              const isActive = activeTab === tab.value;

              return (
                <button
                  key={tab.value}
                  onClick={() => setActiveTab(tab.value)}
                  className={`
                    relative flex items-center gap-2 rounded-lg px-4 py-3 font-semibold
                    transition-all duration-200
                    ${isActive
                      ? 'bg-gradient-to-r from-blue-500 to-blue-600 text-white shadow-lg'
                      : 'text-gray-600 hover:bg-gray-100'
                    }
                  `}
                >
                  <Icon className={`h-5 w-5 ${isActive ? 'text-white' : tab.color}`} />
                  {tab.label}

                  {/* Badge con contador */}
                  {!isActive && tab.value !== 'todas' && (
                    <span className="ml-1 rounded-full bg-gray-200 px-2 py-0.5 text-xs font-bold text-gray-700">
                      {tab.value === 'diaria' && misionesDisponibles?.diarias.length}
                      {tab.value === 'semanal' && misionesDisponibles?.semanales.length}
                      {tab.value === 'mensual' && misionesDisponibles?.mensuales.length}
                      {tab.value === 'unica' && misionesDisponibles?.unicas.length}
                    </span>
                  )}

                  {/* Indicador activo */}
                  {isActive && (
                    <motion.div
                      layoutId="activeTab"
                      className="absolute inset-0 rounded-lg bg-gradient-to-r from-blue-500 to-blue-600"
                      style={{ zIndex: -1 }}
                    />
                  )}
                </button>
              );
            })}
          </div>
        </motion.div>

        {/* Contenido - Grid de Misiones */}
        <AnimatePresence mode="wait">
          {isLoadingMisiones || isLoadingEstadisticas ? (
            <motion.div
              key="loading"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-3"
            >
              {[...Array(6)].map((_, i) => (
                <div
                  key={i}
                  className="h-80 animate-pulse rounded-xl bg-white shadow-lg"
                />
              ))}
            </motion.div>
          ) : misionesActivas.length === 0 ? (
            <motion.div
              key="empty"
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.9 }}
              className="flex flex-col items-center justify-center rounded-xl bg-white p-12 shadow-lg"
            >
              <div className="rounded-full bg-gray-100 p-6 mb-4">
                <Target className="h-16 w-16 text-gray-400" />
              </div>
              <h3 className="text-2xl font-bold text-gray-900 mb-2">
                No hay misiones disponibles
              </h3>
              <p className="text-center text-gray-600 max-w-md">
                {activeTab === 'diaria' &&
                  'Las misiones diarias se renovarán mañana. ¡Vuelve pronto!'}
                {activeTab === 'semanal' &&
                  'No hay misiones semanales activas en este momento.'}
                {activeTab === 'mensual' &&
                  'No hay misiones mensuales activas en este momento.'}
                {activeTab === 'unica' &&
                  'No hay misiones únicas disponibles. ¡Completa otras misiones para desbloquearlas!'}
                {activeTab === 'todas' &&
                  'No hay misiones disponibles en este momento.'}
              </p>
            </motion.div>
          ) : (
            <motion.div
              key={activeTab}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              className="grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-3"
            >
              {misionesActivas.map((mision: MisionUsuarioConDetalle, index: number) => (
                <motion.div
                  key={mision.mision_usuario_id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.05 }}
                >
                  <MisionCard
                    mision={mision}
                    onReclamar={handleReclamar}
                    isLoading={reclamarMutation.isPending}
                  />
                </motion.div>
              ))}
            </motion.div>
          )}
        </AnimatePresence>

        {/* Información adicional */}
        {estadisticas && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4 }}
            className="mt-8 rounded-xl bg-gradient-to-r from-blue-500 to-purple-600 p-8 text-white shadow-xl"
          >
            <div className="grid grid-cols-1 gap-6 md:grid-cols-3">
              <div className="text-center">
                <Trophy className="mx-auto mb-2 h-10 w-10" />
                <p className="text-3xl font-bold">
                  {estadisticas.puntos_ganados_misiones}
                </p>
                <p className="mt-1 text-blue-100">Puntos Totales Ganados</p>
              </div>

              <div className="text-center">
                <Flame className="mx-auto mb-2 h-10 w-10" />
                <p className="text-3xl font-bold">
                  {estadisticas.racha_actual}
                </p>
                <p className="mt-1 text-blue-100">Racha Actual</p>
              </div>

              <div className="text-center">
                <Award className="mx-auto mb-2 h-10 w-10" />
                <p className="text-3xl font-bold">
                  {estadisticas.racha_maxima}
                </p>
                <p className="mt-1 text-blue-100">Racha Máxima</p>
              </div>
            </div>
          </motion.div>
        )}
      </div>
    </div>
  );
}
