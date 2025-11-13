/**
 * Módulo de Niveles y Ranking - Versión Mejorada
 * Con paginación, filtros por nivel/programa y búsqueda de usuarios
 */

import { useState, useMemo } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Trophy, TrendingUp, Medal, Crown, 
  ChevronUp, ChevronDown, Award, Users,
  Star, Target, Zap, Search, Filter, X,
  ChevronLeft, ChevronRight
} from 'lucide-react';
import { useRanking, useMiPosicionRanking } from '../../hooks/useGamificacion';
import { obtenerColorNivel, formatearPuntos } from '../../services/gamificacion.service';

// Iconos para el podio
const iconosPodio = {
  1: <Crown className="w-8 h-8 text-yellow-500" />,
  2: <Medal className="w-7 h-7 text-gray-400" />,
  3: <Medal className="w-6 h-6 text-orange-600" />,
};

export default function NivelesUsuarioMejorado() {
  // Estados base
  const [limite] = useState(100); // Traemos más datos para filtrar localmente
  const [offset] = useState(0);
  
  // Estados de UI
  const [busqueda, setBusqueda] = useState('');
  const [nivelFiltro, setNivelFiltro] = useState<string>('todos');
  const [programaFiltro, setProgramaFiltro] = useState<string>('todos');
  const [mostrarFiltros, setMostrarFiltros] = useState(false);
  const [paginaActual, setPaginaActual] = useState(1);
  const usuariosPorPagina = 20;
  
  const { data: ranking, isLoading: isLoadingRanking, isError: isErrorRanking } = useRanking(limite, offset);
  const { data: miPosicion, isLoading: isLoadingPosicion, isError: isErrorPosicion } = useMiPosicionRanking();

  const isLoading = isLoadingRanking || isLoadingPosicion;
  const isError = isErrorRanking || isErrorPosicion;

  // Extraer niveles y programas únicos
  const nivelesDisponibles = useMemo(() => {
    if (!ranking?.usuarios) return [];
    const niveles = new Set(ranking.usuarios.map(u => u.nivel));
    return Array.from(niveles).sort();
  }, [ranking]);

  const programasDisponibles = useMemo(() => {
    if (!ranking?.usuarios) return [];
    // Asumiendo que tienes programa en el usuario, si no, puedes simularlo o remover este filtro
    const programas = new Set(ranking.usuarios.map(u => u.programa || 'General'));
    return Array.from(programas).sort();
  }, [ranking]);

  // Filtrar usuarios
  const usuariosFiltrados = useMemo(() => {
    if (!ranking?.usuarios) return [];
    
    let resultado = [...ranking.usuarios];

    // Filtro de búsqueda
    if (busqueda) {
      const busquedaLower = busqueda.toLowerCase();
      resultado = resultado.filter(u => 
        `${u.nombre} ${u.apellido}`.toLowerCase().includes(busquedaLower)
      );
    }

    // Filtro de nivel
    if (nivelFiltro !== 'todos') {
      resultado = resultado.filter(u => u.nivel === nivelFiltro);
    }

    // Filtro de programa
    if (programaFiltro !== 'todos') {
      resultado = resultado.filter(u => (u.programa || 'General') === programaFiltro);
    }

    return resultado;
  }, [ranking, busqueda, nivelFiltro, programaFiltro]);

  // Paginación
  const totalPaginas = Math.ceil(usuariosFiltrados.length / usuariosPorPagina);
  const usuariosPaginados = useMemo(() => {
    const inicio = (paginaActual - 1) * usuariosPorPagina;
    const fin = inicio + usuariosPorPagina;
    return usuariosFiltrados.slice(inicio, fin);
  }, [usuariosFiltrados, paginaActual, usuariosPorPagina]);

  // Reset paginación cuando cambian filtros
  const cambiarFiltro = (fn: () => void) => {
    fn();
    setPaginaActual(1);
  };

  // Top 3 del ranking filtrado
  const top3 = usuariosFiltrados.slice(0, 3);

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-violet-50 via-white to-purple-50 dark:from-gray-900 dark:via-gray-800 dark:to-purple-900 flex items-center justify-center">
        <div className="text-center">
          <div className="w-16 h-16 border-4 border-violet-500 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-gray-600 dark:text-gray-400">Cargando ranking...</p>
        </div>
      </div>
    );
  }

  if (isError || !ranking || !miPosicion) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-violet-50 via-white to-purple-50 dark:from-gray-900 dark:via-gray-800 dark:to-purple-900 flex items-center justify-center">
        <div className="text-center">
          <div className="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <span className="text-2xl">❌</span>
          </div>
          <p className="text-red-600">Error al cargar el ranking</p>
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
            Ranking Global
          </h1>
          <p className="text-gray-600 dark:text-gray-400">
            Compite con otros estudiantes y sube de nivel
          </p>
        </motion.div>

        {/* Mi Posición */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-8"
        >
          <div className="bg-gradient-to-r from-violet-500 to-purple-600 rounded-2xl shadow-lg p-6 text-white">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-6">
                <div className="w-20 h-20 bg-white/20 backdrop-blur-sm rounded-xl flex items-center justify-center">
                  <span className="text-3xl font-bold">#{miPosicion.posicion}</span>
                </div>
                <div>
                  <p className="text-white/80 text-sm mb-1">Tu Posición</p>
                  <h2 className="text-3xl font-bold mb-1">{formatearPuntos(miPosicion.puntos)} puntos</h2>
                  <p className="text-white/90 font-medium">{miPosicion.nivel}</p>
                </div>
              </div>
              
              <div className="text-right">
                <div className="flex items-center gap-4 mb-2">
                  {miPosicion.puntos_hasta_anterior > 0 && (
                    <div className="flex items-center gap-1 bg-white/20 px-3 py-1 rounded-lg">
                      <ChevronUp className="w-4 h-4" />
                      <span className="text-sm font-semibold">
                        -{formatearPuntos(miPosicion.puntos_hasta_anterior)} pts
                      </span>
                    </div>
                  )}
                  {miPosicion.puntos_hasta_siguiente > 0 && (
                    <div className="flex items-center gap-1 bg-white/20 px-3 py-1 rounded-lg">
                      <ChevronDown className="w-4 h-4" />
                      <span className="text-sm font-semibold">
                        +{formatearPuntos(miPosicion.puntos_hasta_siguiente)} pts
                      </span>
                    </div>
                  )}
                </div>
                <p className="text-white/80 text-sm">
                  de {miPosicion.total_usuarios} estudiantes
                </p>
              </div>
            </div>
          </div>
        </motion.div>

        {/* Podio Top 3 */}
        {top3.length >= 3 && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="mb-8"
          >
            <div className="grid grid-cols-3 gap-4 max-w-4xl mx-auto">
              {/* 2do Lugar */}
              <motion.div
                initial={{ opacity: 0, y: 40 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.2 }}
                className="flex flex-col items-center pt-8"
              >
                <div className="relative mb-4">
                  <div className="w-20 h-20 bg-gradient-to-br from-gray-300 to-gray-500 rounded-full flex items-center justify-center">
                    <span className="text-3xl">🥈</span>
                  </div>
                  <div className="absolute -bottom-2 left-1/2 transform -translate-x-1/2 w-10 h-10 bg-gray-500 rounded-full flex items-center justify-center text-white font-bold">
                    2
                  </div>
                </div>
                <h3 className="font-bold text-gray-900 dark:text-white mb-1 text-center">
                  {top3[1].nombre} {top3[1].apellido}
                </h3>
                <p className="text-sm text-gray-600 dark:text-gray-400 mb-2">
                  {top3[1].nivel}
                </p>
                <div className="flex items-center gap-1 px-3 py-1 bg-yellow-100 dark:bg-yellow-900 rounded-lg">
                  <Star className="w-4 h-4 text-yellow-600 dark:text-yellow-400" />
                  <span className="font-bold text-yellow-700 dark:text-yellow-300">
                    {formatearPuntos(top3[1].puntos)}
                  </span>
                </div>
              </motion.div>

              {/* 1er Lugar */}
              <motion.div
                initial={{ opacity: 0, y: 40 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.1 }}
                className="flex flex-col items-center"
              >
                <div className="relative mb-4">
                  <div className="w-28 h-28 bg-gradient-to-br from-yellow-300 to-yellow-600 rounded-full flex items-center justify-center shadow-lg">
                    <span className="text-5xl">👑</span>
                  </div>
                  <div className="absolute -bottom-3 left-1/2 transform -translate-x-1/2 w-12 h-12 bg-yellow-500 rounded-full flex items-center justify-center text-white font-bold text-lg shadow-lg">
                    1
                  </div>
                </div>
                <h3 className="font-bold text-xl text-gray-900 dark:text-white mb-1 text-center">
                  {top3[0].nombre} {top3[0].apellido}
                </h3>
                <p className="text-sm text-gray-600 dark:text-gray-400 mb-2">
                  {top3[0].nivel}
                </p>
                <div className="flex items-center gap-1 px-4 py-2 bg-yellow-100 dark:bg-yellow-900 rounded-lg">
                  <Star className="w-5 h-5 text-yellow-600 dark:text-yellow-400" />
                  <span className="font-bold text-lg text-yellow-700 dark:text-yellow-300">
                    {formatearPuntos(top3[0].puntos)}
                  </span>
                </div>
              </motion.div>

              {/* 3er Lugar */}
              <motion.div
                initial={{ opacity: 0, y: 40 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.3 }}
                className="flex flex-col items-center pt-12"
              >
                <div className="relative mb-4">
                  <div className="w-20 h-20 bg-gradient-to-br from-orange-400 to-orange-700 rounded-full flex items-center justify-center">
                    <span className="text-3xl">🥉</span>
                  </div>
                  <div className="absolute -bottom-2 left-1/2 transform -translate-x-1/2 w-10 h-10 bg-orange-600 rounded-full flex items-center justify-center text-white font-bold">
                    3
                  </div>
                </div>
                <h3 className="font-bold text-gray-900 dark:text-white mb-1 text-center">
                  {top3[2].nombre} {top3[2].apellido}
                </h3>
                <p className="text-sm text-gray-600 dark:text-gray-400 mb-2">
                  {top3[2].nivel}
                </p>
                <div className="flex items-center gap-1 px-3 py-1 bg-yellow-100 dark:bg-yellow-900 rounded-lg">
                  <Star className="w-4 h-4 text-yellow-600 dark:text-yellow-400" />
                  <span className="font-bold text-yellow-700 dark:text-yellow-300">
                    {formatearPuntos(top3[2].puntos)}
                  </span>
                </div>
              </motion.div>
            </div>
          </motion.div>
        )}

        {/* Barra de herramientas */}
        <div className="mb-6 flex flex-col md:flex-row gap-4">
          {/* Búsqueda */}
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
            <input
              type="text"
              placeholder="Buscar por nombre..."
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
              mostrarFiltros || nivelFiltro !== 'todos' || programaFiltro !== 'todos'
                ? 'bg-violet-600 text-white'
                : 'bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-300 border border-gray-300 dark:border-gray-600'
            }`}
          >
            <Filter className="w-5 h-5" />
            Filtros
            {(nivelFiltro !== 'todos' || programaFiltro !== 'todos') && (
              <span className="bg-white/20 px-2 py-0.5 rounded-full text-xs">
                {[nivelFiltro !== 'todos' ? 1 : 0, programaFiltro !== 'todos' ? 1 : 0].reduce((a, b) => a + b, 0)}
              </span>
            )}
          </button>
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
                  {/* Filtro de nivel */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      Nivel
                    </label>
                    <select
                      value={nivelFiltro}
                      onChange={(e) => cambiarFiltro(() => setNivelFiltro(e.target.value))}
                      className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-violet-500 outline-none"
                    >
                      <option value="todos">Todos los niveles</option>
                      {nivelesDisponibles.map(nivel => (
                        <option key={nivel} value={nivel}>
                          {nivel}
                        </option>
                      ))}
                    </select>
                  </div>

                  {/* Filtro de programa */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      Programa
                    </label>
                    <select
                      value={programaFiltro}
                      onChange={(e) => cambiarFiltro(() => setProgramaFiltro(e.target.value))}
                      className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-violet-500 outline-none"
                    >
                      <option value="todos">Todos los programas</option>
                      {programasDisponibles.map(programa => (
                        <option key={programa} value={programa}>
                          {programa}
                        </option>
                      ))}
                    </select>
                  </div>
                </div>

                {/* Botón para limpiar filtros */}
                {(nivelFiltro !== 'todos' || programaFiltro !== 'todos') && (
                  <button
                    onClick={() => {
                      cambiarFiltro(() => {
                        setNivelFiltro('todos');
                        setProgramaFiltro('todos');
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
        <div className="mb-4">
          <p className="text-sm text-gray-600 dark:text-gray-400">
            Mostrando {usuariosPaginados.length} de {usuariosFiltrados.length} usuarios
          </p>
        </div>

        {/* Lista del Ranking */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
        >
          <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-lg border border-gray-200 dark:border-gray-700 overflow-hidden">
            <div className="p-6 border-b border-gray-200 dark:border-gray-700">
              <h2 className="text-2xl font-bold text-gray-900 dark:text-white flex items-center gap-2">
                <Users className="w-6 h-6 text-violet-600" />
                Ranking Completo
              </h2>
            </div>

            {usuariosPaginados.length > 0 ? (
              <div className="divide-y divide-gray-200 dark:divide-gray-700">
                {usuariosPaginados.map((usuario, idx) => {
                  // Calcular posición real en ranking filtrado
                  const posicionReal = usuariosFiltrados.findIndex(u => u.usuario_id === usuario.usuario_id) + 1;
                  const esTop3 = posicionReal <= 3;
                  
                  return (
                    <motion.div
                      key={usuario.usuario_id}
                      initial={{ opacity: 0, x: -20 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: 0.03 * idx }}
                      className={`p-4 transition-colors duration-200 ${
                        esTop3 
                          ? 'bg-yellow-50 dark:bg-yellow-900/10 hover:bg-yellow-100 dark:hover:bg-yellow-900/20' 
                          : 'hover:bg-gray-50 dark:hover:bg-gray-700'
                      }`}
                    >
                      <div className="flex items-center gap-4">
                        <div className={`w-12 h-12 rounded-xl flex items-center justify-center ${
                          esTop3
                            ? 'bg-gradient-to-br from-yellow-400 to-orange-600'
                            : 'bg-gradient-to-br from-gray-200 to-gray-300 dark:from-gray-700 dark:to-gray-600'
                        }`}>
                          <span className={`font-bold ${
                            esTop3 ? 'text-white' : 'text-gray-700 dark:text-gray-300'
                          }`}>
                            #{posicionReal}
                          </span>
                        </div>

                        <div className="flex-1">
                          <h3 className="font-semibold text-gray-900 dark:text-white">
                            {usuario.nombre} {usuario.apellido}
                          </h3>
                          <div className="flex items-center gap-2 text-sm text-gray-600 dark:text-gray-400">
                            <span>{usuario.nivel}</span>
                            {usuario.programa && (
                              <>
                                <span>•</span>
                                <span>{usuario.programa}</span>
                              </>
                            )}
                          </div>
                        </div>

                        <div className="flex items-center gap-4">
                          {usuario.insignias_count > 0 && (
                            <div className="flex items-center gap-1 px-2 py-1 bg-purple-100 dark:bg-purple-900 rounded-lg">
                              <Award className="w-4 h-4 text-purple-600 dark:text-purple-400" />
                              <span className="text-sm font-semibold text-purple-700 dark:text-purple-300">
                                {usuario.insignias_count}
                              </span>
                            </div>
                          )}

                          <div className="flex items-center gap-1 px-3 py-1 bg-yellow-100 dark:bg-yellow-900 rounded-lg">
                            <Star className="w-4 h-4 text-yellow-600 dark:text-yellow-400" />
                            <span className="font-bold text-yellow-700 dark:text-yellow-300">
                              {formatearPuntos(usuario.puntos)}
                            </span>
                          </div>
                        </div>
                      </div>
                    </motion.div>
                  );
                })}
              </div>
            ) : (
              <div className="text-center py-12">
                <div className="w-24 h-24 bg-gray-100 dark:bg-gray-800 rounded-full flex items-center justify-center mx-auto mb-4">
                  <Search className="w-12 h-12 text-gray-400" />
                </div>
                <p className="text-gray-600 dark:text-gray-400 text-lg mb-2">
                  No se encontraron usuarios
                </p>
                <p className="text-gray-500 dark:text-gray-500 text-sm">
                  Intenta ajustar tus filtros o búsqueda
                </p>
              </div>
            )}
          </div>

          {/* Paginación */}
          {totalPaginas > 1 && usuariosPaginados.length > 0 && (
            <div className="flex items-center justify-center gap-2 mt-6">
              <button
                onClick={() => setPaginaActual(prev => Math.max(1, prev - 1))}
                disabled={paginaActual === 1}
                className="p-2 rounded-lg bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
              >
                <ChevronLeft className="w-5 h-5" />
              </button>

              {Array.from({ length: Math.min(totalPaginas, 10) }, (_, i) => {
                // Mostrar primeras 3, últimas 3 y alrededor de la actual
                const pagina = i + 1;
                const mostrar = pagina <= 3 || 
                               pagina >= totalPaginas - 2 || 
                               Math.abs(pagina - paginaActual) <= 1;
                
                if (!mostrar && (i === 3 || i === totalPaginas - 4)) {
                  return <span key={i} className="px-2">...</span>;
                }
                
                if (!mostrar) return null;

                return (
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
                );
              })}

              <button
                onClick={() => setPaginaActual(prev => Math.min(totalPaginas, prev + 1))}
                disabled={paginaActual === totalPaginas}
                className="p-2 rounded-lg bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
              >
                <ChevronRight className="w-5 h-5" />
              </button>
            </div>
          )}
        </motion.div>
      </div>
    </div>
  );
}
