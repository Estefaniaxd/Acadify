/**
 * Página de Notificaciones
 * 
 * @module pages/NotificacionesPage
 * @description Vista completa de notificaciones con filtros, búsqueda y paginación.
 */

import { useState } from 'react';
import { motion } from 'framer-motion';
import {
  Bell, Check, CheckCheck, Filter, Search,
  MessageSquare, BookOpen, Trophy, Calendar, AlertCircle,
  Settings, ChevronLeft, ChevronRight, X
} from 'lucide-react';
import { useNotificaciones, useMarcarComoLeidas, useMarcarTodasLeidas } from '../../hooks/useNotificaciones';
import {
  obtenerIconoNotificacion,
  obtenerColorNotificacion,
  obtenerTituloTipo,
  formatearTiempoRelativo,
  type TipoNotificacion,
  type Notificacion,
} from '../../services/notificaciones.service';
import FiltrosAvanzadosModal, { type FiltrosAvanzados } from '../../components/notificaciones/FiltrosAvanzadosModal';

export default function NotificacionesPage() {
  // Estados de filtros
  const [soloNoLeidas, setSoloNoLeidas] = useState(false);
  const [tipoSeleccionado, setTipoSeleccionado] = useState<TipoNotificacion | undefined>();
  const [busqueda, setBusqueda] = useState('');
  const [pagina, setPagina] = useState(1);
  const [modalFiltrosAbierto, setModalFiltrosAbierto] = useState(false);
  const [filtrosAvanzados, setFiltrosAvanzados] = useState<FiltrosAvanzados>({
    tipos: [],
    fechaDesde: undefined,
    fechaHasta: undefined,
    soloNoLeidas: false,
    soloImportantes: false,
    ordenarPor: 'fecha_creacion',
    ordenDesc: true,
  });
  const ITEMS_POR_PAGINA = 20;

  // Hooks de datos
  const { data: notificaciones = [], isLoading } = useNotificaciones({
    tipo_notificacion: tipoSeleccionado,
    solo_no_leidas: soloNoLeidas,
    limite: ITEMS_POR_PAGINA,
    offset: (pagina - 1) * ITEMS_POR_PAGINA,
  });

  const { mutate: marcarComoLeidas, isPending: isMarkingRead } = useMarcarComoLeidas();
  const { mutate: marcarTodasLeidas, isPending: isMarkingAll } = useMarcarTodasLeidas();

  // Tipos de notificación para filtros
  const tiposNotificacion: { value: TipoNotificacion; label: string; icon: React.ElementType }[] = [
    { value: 'mensaje_directo', label: 'Mensajes', icon: MessageSquare },
    { value: 'tarea_nueva', label: 'Tareas', icon: BookOpen },
    { value: 'logro_desbloqueado', label: 'Logros', icon: Trophy },
    { value: 'clase_cancelada', label: 'Clases', icon: Calendar },
    { value: 'sistema', label: 'Sistema', icon: AlertCircle },
  ];

  // Handlers
  const handleMarcarLeida = (id: string) => {
    marcarComoLeidas([id]);
  };

  const handleMarcarTodasLeidas = () => {
    // marcarTodasLeidas ya es la función mutate, no necesita .mutate()
    marcarTodasLeidas(undefined);
  };

  const handleClickNotificacion = (notif: Notificacion) => {
    if (!notif.leida) {
      handleMarcarLeida(notif.id);
    }
    if (notif.url_accion) {
      window.open(notif.url_accion, '_self');
    }
  };

  // Filtrar por búsqueda (frontend)
  const notificacionesFiltradas = notificaciones.filter(
    (n) =>
      !busqueda ||
      n.titulo.toLowerCase().includes(busqueda.toLowerCase()) ||
      n.mensaje?.toLowerCase().includes(busqueda.toLowerCase())
  );

  const noLeidas = notificaciones.filter((n) => !n.leida).length;

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      {/* Header */}
      <div className="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <div className="w-12 h-12 bg-gradient-to-br from-violet-500 to-purple-600 rounded-2xl flex items-center justify-center">
                <Bell className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
                  Notificaciones
                </h1>
                {noLeidas > 0 && (
                  <p className="text-sm text-violet-600 dark:text-violet-400">
                    {noLeidas} sin leer
                  </p>
                )}
              </div>
            </div>

            <div className="flex items-center gap-2">
              {noLeidas > 0 && (
                <button
                  onClick={handleMarcarTodasLeidas}
                  disabled={isMarkingAll}
                  className="px-4 py-2 bg-violet-100 dark:bg-violet-900 text-violet-700 dark:text-violet-300 rounded-xl font-medium hover:bg-violet-200 dark:hover:bg-violet-800 transition-colors disabled:opacity-50 flex items-center gap-2"
                >
                  <CheckCheck className="w-5 h-5" />
                  Marcar todas como leídas
                </button>
              )}
              <a
                href="/configuracion/notificaciones"
                className="px-4 py-2 bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-xl font-medium hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors flex items-center gap-2"
              >
                <Settings className="w-5 h-5" />
                Configurar
              </a>
            </div>
          </div>
        </div>
      </div>

      {/* Contenido */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          {/* Sidebar - Filtros */}
          <div className="lg:col-span-1">
            <div className="bg-white dark:bg-gray-800 rounded-2xl border border-gray-200 dark:border-gray-700 p-6 sticky top-6">
              <h2 className="text-lg font-bold text-gray-900 dark:text-white mb-4 flex items-center gap-2">
                <Filter className="w-5 h-5" />
                Filtros
              </h2>

              {/* Estado de lectura */}
              <div className="mb-6">
                <h3 className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">
                  Estado
                </h3>
                <div className="space-y-2">
                  <button
                    onClick={() => setSoloNoLeidas(false)}
                    className={`w-full px-3 py-2 rounded-lg text-sm font-medium text-left transition-colors ${
                      !soloNoLeidas
                        ? 'bg-violet-100 dark:bg-violet-900 text-violet-700 dark:text-violet-300'
                        : 'bg-gray-50 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-600'
                    }`}
                  >
                    Todas
                  </button>
                  <button
                    onClick={() => setSoloNoLeidas(true)}
                    className={`w-full px-3 py-2 rounded-lg text-sm font-medium text-left transition-colors ${
                      soloNoLeidas
                        ? 'bg-violet-100 dark:bg-violet-900 text-violet-700 dark:text-violet-300'
                        : 'bg-gray-50 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-600'
                    }`}
                  >
                    Sin leer
                    {noLeidas > 0 && (
                      <span className="ml-2 px-2 py-0.5 bg-violet-500 text-white text-xs rounded-full">
                        {noLeidas}
                      </span>
                    )}
                  </button>
                </div>
              </div>

              {/* Tipo de notificación */}
              <div>
                <h3 className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">
                  Tipo
                </h3>
                <div className="space-y-2">
                  <button
                    onClick={() => setTipoSeleccionado(undefined)}
                    className={`w-full px-3 py-2 rounded-lg text-sm font-medium text-left transition-colors ${
                      !tipoSeleccionado
                        ? 'bg-violet-100 dark:bg-violet-900 text-violet-700 dark:text-violet-300'
                        : 'bg-gray-50 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-600'
                    }`}
                  >
                    Todos los tipos
                  </button>
                  {tiposNotificacion.map((tipo) => {
                    const Icon = tipo.icon;
                    return (
                      <button
                        key={tipo.value}
                        onClick={() => setTipoSeleccionado(tipo.value)}
                        className={`w-full px-3 py-2 rounded-lg text-sm font-medium text-left transition-colors flex items-center gap-2 ${
                          tipoSeleccionado === tipo.value
                            ? 'bg-violet-100 dark:bg-violet-900 text-violet-700 dark:text-violet-300'
                            : 'bg-gray-50 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-600'
                        }`}
                      >
                        <Icon className="w-4 h-4" />
                        {tipo.label}
                      </button>
                    );
                  })}
                </div>
              </div>

              {/* Botón de filtros avanzados */}
              <div className="mt-6 pt-6 border-t border-gray-200 dark:border-gray-700">
                <button
                  onClick={() => setModalFiltrosAbierto(true)}
                  className="w-full px-4 py-2 bg-gradient-to-r from-violet-600 to-purple-600 text-white rounded-xl font-semibold hover:shadow-lg transition-all flex items-center justify-center gap-2"
                >
                  <Filter className="w-4 h-4" />
                  Filtros Avanzados
                </button>
              </div>
            </div>
          </div>

          {/* Lista de Notificaciones */}
          <div className="lg:col-span-3">
            {/* Barra de búsqueda */}
            <div className="bg-white dark:bg-gray-800 rounded-2xl border border-gray-200 dark:border-gray-700 p-4 mb-6">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
                <input
                  type="text"
                  placeholder="Buscar notificaciones..."
                  value={busqueda}
                  onChange={(e) => setBusqueda(e.target.value)}
                  className="w-full pl-10 pr-10 py-2 bg-gray-50 dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-xl text-gray-900 dark:text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-violet-500"
                />
                {busqueda && (
                  <button
                    onClick={() => setBusqueda('')}
                    className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
                  >
                    <X className="w-5 h-5" />
                  </button>
                )}
              </div>
            </div>

            {/* Loading */}
            {isLoading ? (
              <div className="bg-white dark:bg-gray-800 rounded-2xl border border-gray-200 dark:border-gray-700 p-12">
                <div className="flex items-center justify-center">
                  <div className="w-12 h-12 border-4 border-violet-500 border-t-transparent rounded-full animate-spin"></div>
                </div>
              </div>
            ) : notificacionesFiltradas.length === 0 ? (
              /* Empty State */
              <div className="bg-white dark:bg-gray-800 rounded-2xl border border-gray-200 dark:border-gray-700 p-12">
                <div className="flex flex-col items-center justify-center">
                  <div className="w-20 h-20 bg-gray-100 dark:bg-gray-700 rounded-full flex items-center justify-center mb-4">
                    <Bell className="w-10 h-10 text-gray-400" />
                  </div>
                  <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
                    No hay notificaciones
                  </h3>
                  <p className="text-gray-600 dark:text-gray-400 text-center">
                    {busqueda
                      ? 'No se encontraron notificaciones con esa búsqueda'
                      : soloNoLeidas
                      ? 'No tienes notificaciones sin leer'
                      : 'No tienes notificaciones en este momento'}
                  </p>
                </div>
              </div>
            ) : (
              /* Lista */
              <div className="space-y-3">
                {notificacionesFiltradas.map((notif, index) => (
                  <motion.div
                    key={notif.id}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: index * 0.05 }}
                    className={`bg-white dark:bg-gray-800 rounded-2xl border border-gray-200 dark:border-gray-700 p-6 hover:shadow-lg transition-all cursor-pointer ${
                      !notif.leida
                        ? 'ring-2 ring-violet-500 ring-offset-2 dark:ring-offset-gray-900'
                        : ''
                    }`}
                    onClick={() => handleClickNotificacion(notif)}
                  >
                    <div className="flex gap-4">
                      {/* Icono */}
                      <div
                        className={`flex-shrink-0 w-12 h-12 rounded-2xl bg-gradient-to-br ${obtenerColorNotificacion(
                          notif.tipo_notificacion
                        )} flex items-center justify-center text-white text-xl`}
                      >
                        {notif.icono || obtenerIconoNotificacion(notif.tipo_notificacion)}
                      </div>

                      {/* Contenido */}
                      <div className="flex-1 min-w-0">
                        <div className="flex items-start justify-between gap-4 mb-2">
                          <div className="flex-1">
                            <h3 className="font-semibold text-gray-900 dark:text-white text-lg mb-1">
                              {notif.titulo}
                            </h3>
                            <div className="flex items-center gap-2 text-sm text-gray-500 dark:text-gray-400">
                              <span className="px-2 py-0.5 bg-gray-100 dark:bg-gray-700 rounded-md">
                                {obtenerTituloTipo(notif.tipo_notificacion)}
                              </span>
                              <span>•</span>
                              <span>{formatearTiempoRelativo(notif.fecha_creacion)}</span>
                            </div>
                          </div>
                          {!notif.leida && (
                            <div className="flex-shrink-0 w-3 h-3 bg-violet-500 rounded-full"></div>
                          )}
                        </div>

                        {notif.mensaje && (
                          <p className="text-gray-600 dark:text-gray-400 mb-3">
                            {notif.mensaje}
                          </p>
                        )}

                        {/* Acciones */}
                        <div className="flex items-center gap-2">
                          {!notif.leida && (
                            <button
                              onClick={(e) => {
                                e.stopPropagation();
                                handleMarcarLeida(notif.id);
                              }}
                              disabled={isMarkingRead}
                              className="px-3 py-1.5 bg-violet-100 dark:bg-violet-900 text-violet-700 dark:text-violet-300 rounded-lg text-sm font-medium hover:bg-violet-200 dark:hover:bg-violet-800 transition-colors disabled:opacity-50 flex items-center gap-1"
                            >
                              <Check className="w-4 h-4" />
                              Marcar como leída
                            </button>
                          )}
                        </div>
                      </div>
                    </div>
                  </motion.div>
                ))}
              </div>
            )}

            {/* Paginación */}
            {notificacionesFiltradas.length > 0 && (
              <div className="mt-6 flex items-center justify-between">
                <button
                  onClick={() => setPagina((p) => Math.max(1, p - 1))}
                  disabled={pagina === 1}
                  className="px-4 py-2 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-xl font-medium hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
                >
                  <ChevronLeft className="w-5 h-5" />
                  Anterior
                </button>
                <span className="text-gray-600 dark:text-gray-400">
                  Página {pagina}
                </span>
                <button
                  onClick={() => setPagina((p) => p + 1)}
                  disabled={notificacionesFiltradas.length < ITEMS_POR_PAGINA}
                  className="px-4 py-2 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-xl font-medium hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
                >
                  Siguiente
                  <ChevronRight className="w-5 h-5" />
                </button>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Modal de Filtros Avanzados */}
      <FiltrosAvanzadosModal
        isOpen={modalFiltrosAbierto}
        onClose={() => setModalFiltrosAbierto(false)}
        onAplicar={(nuevosFiltros) => {
          setFiltrosAvanzados(nuevosFiltros);
          // Aplicar filtros a la consulta
          if (nuevosFiltros.tipos.length > 0) {
            setTipoSeleccionado(nuevosFiltros.tipos[0]); // Por simplicidad, usar el primero
          }
          setSoloNoLeidas(nuevosFiltros.soloNoLeidas);
          setModalFiltrosAbierto(false);
        }}
        filtrosActuales={filtrosAvanzados}
      />
    </div>
  );
}
