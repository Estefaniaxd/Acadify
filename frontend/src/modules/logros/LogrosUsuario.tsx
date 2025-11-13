/**
 * Módulo de Logros del Usuario - Versión Mejorada
 * Con tabs funcionales, filtros, paginación y vistas alternativas
 */

import { useState, useMemo } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Trophy, Target, Star, Lock, Check, TrendingUp, Users, BookOpen, Zap, Heart,
  Filter, Search, Grid, List, ChevronLeft, ChevronRight, X
} from 'lucide-react';
import { useMisLogros } from '../../hooks/useGamificacion';
import { obtenerColorRareza, obtenerBgRareza, formatearPuntos } from '../../services/gamificacion.service';
import type { Logro, RarezaLogro } from '../../services/gamificacion.service';

// Iconos por tipo de logro
const iconosPorTipo: Record<string, any> = {
  tarea: BookOpen,
  participacion: Users,
  racha: Zap,
  examen: Target,
  social: Heart,
};

type TabType = 'todos' | 'completados' | 'en-progreso';
type VistaType = 'grid' | 'list';

export default function LogrosUsuarioMejorado() {
  const { data: logros, isLoading, isError } = useMisLogros();
  
  // Estados
  const [tabActual, setTabActual] = useState<TabType>('todos');
  const [vista, setVista] = useState<VistaType>('grid');
  const [busqueda, setBusqueda] = useState('');
  const [rarezaFiltro, setRarezaFiltro] = useState<RarezaLogro | 'todas'>('todas');
  const [tipoFiltro, setTipoFiltro] = useState<string>('todos');
  const [paginaActual, setPaginaActual] = useState(1);
  const [mostrarFiltros, setMostrarFiltros] = useState(false);
  const logrosPorPagina = 9;

  // Filtrar logros según tab activo
  const logrosFiltradosPorTab = useMemo(() => {
    if (!logros) return [];
    
    switch (tabActual) {
      case 'completados':
        return logros.filter(l => l.completado);
      case 'en-progreso':
        return logros.filter(l => !l.completado && l.progreso_actual > 0);
      default:
        return logros;
    }
  }, [logros, tabActual]);

  // Aplicar filtros adicionales
  const logrosFiltrados = useMemo(() => {
    let resultado = [...logrosFiltradosPorTab];

    // Filtro de búsqueda
    if (busqueda) {
      const busquedaLower = busqueda.toLowerCase();
      resultado = resultado.filter(l => 
        l.nombre.toLowerCase().includes(busquedaLower) ||
        l.descripcion.toLowerCase().includes(busquedaLower)
      );
    }

    // Filtro de rareza
    if (rarezaFiltro !== 'todas') {
      resultado = resultado.filter(l => l.rareza === rarezaFiltro);
    }

    // Filtro de tipo
    if (tipoFiltro !== 'todos') {
      resultado = resultado.filter(l => l.tipo === tipoFiltro);
    }

    return resultado;
  }, [logrosFiltradosPorTab, busqueda, rarezaFiltro, tipoFiltro]);

  // Paginación
  const totalPaginas = Math.ceil(logrosFiltrados.length / logrosPorPagina);
  const logrosPaginados = useMemo(() => {
    const inicio = (paginaActual - 1) * logrosPorPagina;
    const fin = inicio + logrosPorPagina;
    return logrosFiltrados.slice(inicio, fin);
  }, [logrosFiltrados, paginaActual, logrosPorPagina]);

  // Estadísticas
  const logrosCompletados = logros?.filter(l => l.completado) || [];
  const logrosEnProgreso = logros?.filter(l => !l.completado && l.progreso_actual > 0) || [];
  const porcentajeCompletado = logros && logros.length > 0 
    ? Math.round((logrosCompletados.length / logros.length) * 100)
    : 0;

  // Tipos únicos
  const tiposDisponibles = useMemo(() => {
    if (!logros) return [];
    const tipos = new Set(logros.map(l => l.tipo));
    return Array.from(tipos);
  }, [logros]);

  // Reset paginación cuando cambian filtros
  const cambiarFiltro = (fn: () => void) => {
    fn();
    setPaginaActual(1);
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-violet-50 via-white to-purple-50 dark:from-gray-900 dark:via-gray-800 dark:to-purple-900 flex items-center justify-center">
        <div className="text-center">
          <div className="w-16 h-16 border-4 border-violet-500 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-gray-600 dark:text-gray-400">Cargando logros...</p>
        </div>
      </div>
    );
  }

  if (isError || !logros) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-violet-50 via-white to-purple-50 dark:from-gray-900 dark:via-gray-800 dark:to-purple-900 flex items-center justify-center">
        <div className="text-center">
          <div className="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <span className="text-2xl">❌</span>
          </div>
          <p className="text-red-600">Error al cargar los logros</p>
        </div>
      </div>
    );
  }

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
            <Trophy className="w-10 h-10 text-yellow-500" />
            Mis Logros
          </h1>
          <p className="text-gray-600 dark:text-gray-400">
            Desbloquea logros completando actividades y desafíos
          </p>
        </motion.div>

        {/* Estadísticas Generales */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8"
        >
          <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-lg p-6 border border-gray-200 dark:border-gray-700">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600 dark:text-gray-400 mb-1">
                  Logros Completados
                </p>
                <p className="text-3xl font-bold text-green-600 dark:text-green-400">
                  {logrosCompletados.length}
                </p>
              </div>
              <div className="w-16 h-16 bg-gradient-to-br from-green-500 to-emerald-600 rounded-xl flex items-center justify-center">
                <Check className="w-8 h-8 text-white" />
              </div>
            </div>
          </div>

          <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-lg p-6 border border-gray-200 dark:border-gray-700">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600 dark:text-gray-400 mb-1">
                  En Progreso
                </p>
                <p className="text-3xl font-bold text-blue-600 dark:text-blue-400">
                  {logrosEnProgreso.length}
                </p>
              </div>
              <div className="w-16 h-16 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-xl flex items-center justify-center">
                <TrendingUp className="w-8 h-8 text-white" />
              </div>
            </div>
          </div>

          <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-lg p-6 border border-gray-200 dark:border-gray-700">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600 dark:text-gray-400 mb-1">
                  Progreso Total
                </p>
                <p className="text-3xl font-bold text-violet-600 dark:text-violet-400">
                  {porcentajeCompletado}%
                </p>
              </div>
              <div className="w-16 h-16 bg-gradient-to-br from-violet-500 to-purple-600 rounded-xl flex items-center justify-center">
                <Star className="w-8 h-8 text-white" />
              </div>
            </div>
          </div>
        </motion.div>

        {/* Tabs */}
        <div className="mb-6">
          <div className="flex flex-wrap gap-4 border-b border-gray-200 dark:border-gray-700">
            <button
              onClick={() => cambiarFiltro(() => setTabActual('todos'))}
              className={`px-6 py-3 font-semibold transition-colors ${
                tabActual === 'todos'
                  ? 'text-violet-600 dark:text-violet-400 border-b-2 border-violet-600 dark:border-violet-400'
                  : 'text-gray-600 dark:text-gray-400 hover:text-violet-600 dark:hover:text-violet-400'
              }`}
            >
              Todos ({logros.length})
            </button>
            <button
              onClick={() => cambiarFiltro(() => setTabActual('completados'))}
              className={`px-6 py-3 font-semibold transition-colors ${
                tabActual === 'completados'
                  ? 'text-violet-600 dark:text-violet-400 border-b-2 border-violet-600 dark:border-violet-400'
                  : 'text-gray-600 dark:text-gray-400 hover:text-violet-600 dark:hover:text-violet-400'
              }`}
            >
              Completados ({logrosCompletados.length})
            </button>
            <button
              onClick={() => cambiarFiltro(() => setTabActual('en-progreso'))}
              className={`px-6 py-3 font-semibold transition-colors ${
                tabActual === 'en-progreso'
                  ? 'text-violet-600 dark:text-violet-400 border-b-2 border-violet-600 dark:border-violet-400'
                  : 'text-gray-600 dark:text-gray-400 hover:text-violet-600 dark:hover:text-violet-400'
              }`}
            >
              En Progreso ({logrosEnProgreso.length})
            </button>
          </div>
        </div>

        {/* Barra de herramientas */}
        <div className="mb-6 flex flex-col md:flex-row gap-4">
          {/* Búsqueda */}
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
            <input
              type="text"
              placeholder="Buscar logros..."
              value={busqueda}
              onChange={(e) => cambiarFiltro(() => setBusqueda(e.target.value))}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:ring-2 focus:ring-violet-500 outline-none"
            />
            {busqueda && (
              <button
                onClick={() => cambiarFiltro(() => setBusqueda(''))}
                className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600"
              >
                <X className="w-4 h-4" />
              </button>
            )}
          </div>

          {/* Botón de filtros */}
          <button
            onClick={() => setMostrarFiltros(!mostrarFiltros)}
            className={`px-4 py-2 rounded-lg font-medium transition-colors flex items-center gap-2 ${
              mostrarFiltros || rarezaFiltro !== 'todas' || tipoFiltro !== 'todos'
                ? 'bg-violet-600 text-white'
                : 'bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-300 border border-gray-300 dark:border-gray-600'
            }`}
          >
            <Filter className="w-5 h-5" />
            Filtros
            {(rarezaFiltro !== 'todas' || tipoFiltro !== 'todos') && (
              <span className="bg-white/20 px-2 py-0.5 rounded-full text-xs">
                {[rarezaFiltro !== 'todas' ? 1 : 0, tipoFiltro !== 'todos' ? 1 : 0].reduce((a, b) => a + b, 0)}
              </span>
            )}
          </button>

          {/* Cambiar vista */}
          <div className="flex gap-2 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded-lg p-1">
            <button
              onClick={() => setVista('grid')}
              className={`p-2 rounded ${
                vista === 'grid'
                  ? 'bg-violet-600 text-white'
                  : 'text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-700'
              }`}
            >
              <Grid className="w-5 h-5" />
            </button>
            <button
              onClick={() => setVista('list')}
              className={`p-2 rounded ${
                vista === 'list'
                  ? 'bg-violet-600 text-white'
                  : 'text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-700'
              }`}
            >
              <List className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* Panel de filtros expandido */}
        <AnimatePresence>
          {mostrarFiltros && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              exit={{ opacity: 0, height: 0 }}
              className="mb-6 overflow-hidden"
            >
              <div className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg p-6">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  {/* Filtro de rareza */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      Rareza
                    </label>
                    <select
                      value={rarezaFiltro}
                      onChange={(e) => cambiarFiltro(() => setRarezaFiltro(e.target.value as RarezaLogro | 'todas'))}
                      className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-violet-500 outline-none"
                    >
                      <option value="todas">Todas las rarezas</option>
                      <option value="común">Común</option>
                      <option value="raro">Raro</option>
                      <option value="épico">Épico</option>
                      <option value="legendario">Legendario</option>
                    </select>
                  </div>

                  {/* Filtro de tipo */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      Tipo
                    </label>
                    <select
                      value={tipoFiltro}
                      onChange={(e) => cambiarFiltro(() => setTipoFiltro(e.target.value))}
                      className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-violet-500 outline-none"
                    >
                      <option value="todos">Todos los tipos</option>
                      {tiposDisponibles.map(tipo => (
                        <option key={tipo} value={tipo} className="capitalize">
                          {tipo}
                        </option>
                      ))}
                    </select>
                  </div>
                </div>

                {/* Botón para limpiar filtros */}
                {(rarezaFiltro !== 'todas' || tipoFiltro !== 'todos') && (
                  <button
                    onClick={() => {
                      cambiarFiltro(() => {
                        setRarezaFiltro('todas');
                        setTipoFiltro('todos');
                      });
                    }}
                    className="mt-4 text-sm text-violet-600 dark:text-violet-400 hover:underline"
                  >
                    Limpiar filtros
                  </button>
                )}
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Resultado de búsqueda/filtros */}
        {logrosFiltrados.length === 0 ? (
          <div className="text-center py-12">
            <div className="w-24 h-24 bg-gray-100 dark:bg-gray-800 rounded-full flex items-center justify-center mx-auto mb-4">
              <Search className="w-12 h-12 text-gray-400" />
            </div>
            <p className="text-gray-600 dark:text-gray-400 text-lg mb-2">
              No se encontraron logros
            </p>
            <p className="text-gray-500 dark:text-gray-500 text-sm">
              Intenta ajustar tus filtros o búsqueda
            </p>
          </div>
        ) : (
          <>
            {/* Vista Grid */}
            {vista === 'grid' && (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
                {logrosPaginados.map((logro, idx) => (
                  <LogroCardGrid key={logro.id} logro={logro} idx={idx} />
                ))}
              </div>
            )}

            {/* Vista Lista */}
            {vista === 'list' && (
              <div className="space-y-4 mb-8">
                {logrosPaginados.map((logro, idx) => (
                  <LogroCardList key={logro.id} logro={logro} idx={idx} />
                ))}
              </div>
            )}

            {/* Paginación */}
            {totalPaginas > 1 && (
              <div className="flex items-center justify-center gap-2">
                <button
                  onClick={() => setPaginaActual(prev => Math.max(1, prev - 1))}
                  disabled={paginaActual === 1}
                  className="p-2 rounded-lg bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
                >
                  <ChevronLeft className="w-5 h-5" />
                </button>

                {Array.from({ length: totalPaginas }, (_, i) => i + 1).map(pagina => (
                  <button
                    key={pagina}
                    onClick={() => setPaginaActual(pagina)}
                    className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                      pagina === paginaActual
                        ? 'bg-violet-600 text-white'
                        : 'bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-300 border border-gray-300 dark:border-gray-600 hover:bg-gray-50 dark:hover:bg-gray-700'
                    }`}
                  >
                    {pagina}
                  </button>
                ))}

                <button
                  onClick={() => setPaginaActual(prev => Math.min(totalPaginas, prev + 1))}
                  disabled={paginaActual === totalPaginas}
                  className="p-2 rounded-lg bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
                >
                  <ChevronRight className="w-5 h-5" />
                </button>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
}

// Componente Card en vista Grid
function LogroCardGrid({ logro, idx }: { logro: Logro; idx: number }) {
  const IconoTipo = iconosPorTipo[logro.tipo] || Target;
  const progresoPorcentaje = logro.objetivo > 0 
    ? Math.min(100, Math.round((logro.progreso_actual / logro.objetivo) * 100))
    : 0;

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ delay: 0.05 * idx }}
      whileHover={{ scale: 1.02 }}
      className={`relative bg-white dark:bg-gray-800 rounded-2xl shadow-lg p-6 border-2 transition-all duration-300 ${
        logro.completado
          ? 'border-green-500 dark:border-green-600'
          : 'border-gray-200 dark:border-gray-700'
      }`}
    >
      {/* Badge de completado */}
      {logro.completado && (
        <div className="absolute -top-3 -right-3 w-12 h-12 bg-gradient-to-br from-green-500 to-emerald-600 rounded-full flex items-center justify-center shadow-lg">
          <Check className="w-6 h-6 text-white" />
        </div>
      )}

      {/* Badge de rareza */}
      <div className={`absolute top-4 right-4 px-3 py-1 rounded-full text-xs font-bold ${obtenerColorRareza(logro.rareza)} ${obtenerBgRareza(logro.rareza)}`}>
        {logro.rareza}
      </div>

      {/* Icono del logro */}
      <div className={`w-20 h-20 mb-4 rounded-2xl flex items-center justify-center ${
        logro.completado
          ? 'bg-gradient-to-br from-violet-500 to-purple-600'
          : 'bg-gray-100 dark:bg-gray-700'
      }`}>
        {logro.completado ? (
          <span className="text-4xl">{logro.icono}</span>
        ) : (
          <Lock className="w-10 h-10 text-gray-400" />
        )}
      </div>

      {/* Título y descripción */}
      <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-2">
        {logro.nombre}
      </h3>
      <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">
        {logro.descripcion}
      </p>

      {/* Progreso */}
      {!logro.completado && (
        <div className="mb-4">
          <div className="flex items-center justify-between text-sm mb-2">
            <span className="text-gray-600 dark:text-gray-400">Progreso</span>
            <span className="font-semibold text-violet-600 dark:text-violet-400">
              {logro.progreso_actual} / {logro.objetivo}
            </span>
          </div>
          <div className="h-2 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
            <motion.div
              initial={{ width: 0 }}
              animate={{ width: `${progresoPorcentaje}%` }}
              className="h-full bg-gradient-to-r from-violet-500 to-purple-600 rounded-full"
            />
          </div>
        </div>
      )}

      {/* Footer */}
      <div className="flex items-center justify-between pt-4 border-t border-gray-200 dark:border-gray-700">
        <div className="flex items-center gap-2 text-sm text-gray-600 dark:text-gray-400">
          <IconoTipo className="w-4 h-4" />
          <span className="capitalize">{logro.tipo}</span>
        </div>
        <div className="flex items-center gap-1 text-yellow-600 dark:text-yellow-400">
          <Star className="w-4 h-4 fill-current" />
          <span className="font-semibold">{formatearPuntos(logro.puntos_recompensa)}</span>
        </div>
      </div>
    </motion.div>
  );
}

// Componente Card en vista Lista
function LogroCardList({ logro, idx }: { logro: Logro; idx: number }) {
  const IconoTipo = iconosPorTipo[logro.tipo] || Target;
  const progresoPorcentaje = logro.objetivo > 0 
    ? Math.min(100, Math.round((logro.progreso_actual / logro.objetivo) * 100))
    : 0;

  return (
    <motion.div
      initial={{ opacity: 0, x: -20 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ delay: 0.03 * idx }}
      className={`bg-white dark:bg-gray-800 rounded-xl shadow-md p-4 border-l-4 ${
        logro.completado
          ? 'border-green-500'
          : 'border-gray-300 dark:border-gray-600'
      }`}
    >
      <div className="flex items-center gap-4">
        {/* Icono */}
        <div className={`w-16 h-16 rounded-xl flex items-center justify-center flex-shrink-0 ${
          logro.completado
            ? 'bg-gradient-to-br from-violet-500 to-purple-600'
            : 'bg-gray-100 dark:bg-gray-700'
        }`}>
          {logro.completado ? (
            <span className="text-3xl">{logro.icono}</span>
          ) : (
            <Lock className="w-8 h-8 text-gray-400" />
          )}
        </div>

        {/* Contenido */}
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-1">
            <h3 className="text-lg font-bold text-gray-900 dark:text-white truncate">
              {logro.nombre}
            </h3>
            <div className={`px-2 py-0.5 rounded-full text-xs font-bold ${obtenerColorRareza(logro.rareza)} ${obtenerBgRareza(logro.rareza)}`}>
              {logro.rareza}
            </div>
            {logro.completado && (
              <div className="w-6 h-6 bg-green-500 rounded-full flex items-center justify-center">
                <Check className="w-4 h-4 text-white" />
              </div>
            )}
          </div>
          <p className="text-sm text-gray-600 dark:text-gray-400 mb-2">
            {logro.descripcion}
          </p>

          {/* Progreso */}
          {!logro.completado && (
            <div className="flex items-center gap-3">
              <div className="flex-1">
                <div className="h-2 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
                  <div
                    style={{ width: `${progresoPorcentaje}%` }}
                    className="h-full bg-gradient-to-r from-violet-500 to-purple-600 rounded-full"
                  />
                </div>
              </div>
              <span className="text-sm font-semibold text-violet-600 dark:text-violet-400">
                {logro.progreso_actual} / {logro.objetivo}
              </span>
            </div>
          )}
        </div>

        {/* Info adicional */}
        <div className="flex flex-col items-end gap-2">
          <div className="flex items-center gap-1 text-yellow-600 dark:text-yellow-400">
            <Star className="w-4 h-4 fill-current" />
            <span className="font-semibold">{formatearPuntos(logro.puntos_recompensa)}</span>
          </div>
          <div className="flex items-center gap-1 text-sm text-gray-600 dark:text-gray-400">
            <IconoTipo className="w-4 h-4" />
            <span className="capitalize">{logro.tipo}</span>
          </div>
        </div>
      </div>
    </motion.div>
  );
}
