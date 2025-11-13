/**
 * ListaInvitaciones - Vista principal de gestión de invitaciones
 * Tabla con filtros, búsqueda, paginación y acciones
 */

import React, { useState } from 'react';
import { 
  Search, Filter, Mail, MailCheck, MailX, Clock, Ban, 
  Send, Eye, Trash2, RefreshCw, Calendar, Users, TrendingUp 
} from 'lucide-react';
import { useToast } from '../../../context/ToastContext';
import { 
  useInvitaciones, 
  useEstadisticasInvitaciones,
  useReenviarInvitacion,
  useCancelarInvitacion 
} from '../hooks/useInvitaciones';
import type { FiltrosInvitaciones, EstadoInvitacion, RolInvitacion } from '../types';
import FormularioInvitacion from './FormularioInvitacion';

interface ListaInvitacionesProps {
  institucionId?: number;
}

export default function ListaInvitaciones({ institucionId }: ListaInvitacionesProps) {
  const toast = useToast();
  const [mostrarFormulario, setMostrarFormulario] = useState(false);
  const [filtros, setFiltros] = useState<FiltrosInvitaciones>({
    institucionId,
    pagina: 1,
    limite: 10,
    ordenarPor: 'reciente',
  });

  // Queries
  const { data: invitaciones, isLoading } = useInvitaciones(filtros);
  const { data: estadisticas } = useEstadisticasInvitaciones(institucionId);

  // Mutations
  const reenviarMutation = useReenviarInvitacion(toast);
  const cancelarMutation = useCancelarInvitacion(toast);

  const handleBuscar = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFiltros(prev => ({ ...prev, busqueda: e.target.value, pagina: 1 }));
  };

  const handleFiltroEstado = (estado: EstadoInvitacion | undefined) => {
    setFiltros(prev => ({ ...prev, estado, pagina: 1 }));
  };

  const handleFiltroRol = (rol: RolInvitacion | undefined) => {
    setFiltros(prev => ({ ...prev, rol, pagina: 1 }));
  };

  const handleReenviar = (id: number) => {
    if (confirm('¿Reenviar esta invitación? Se generará un nuevo código.')) {
      reenviarMutation.mutate(id);
    }
  };

  const handleCancelar = (id: number) => {
    if (confirm('¿Cancelar esta invitación? El usuario no podrá aceptarla.')) {
      cancelarMutation.mutate(id);
    }
  };

  const getEstadoBadge = (estado: EstadoInvitacion) => {
    const badges = {
      PENDIENTE: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-400',
      ACEPTADA: 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400',
      RECHAZADA: 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400',
      EXPIRADA: 'bg-gray-100 text-gray-800 dark:bg-gray-900/30 dark:text-gray-400',
      CANCELADA: 'bg-orange-100 text-orange-800 dark:bg-orange-900/30 dark:text-orange-400',
    };
    return badges[estado] || badges.PENDIENTE;
  };

  const getEstadoIcon = (estado: EstadoInvitacion) => {
    const icons = {
      PENDIENTE: Clock,
      ACEPTADA: MailCheck,
      RECHAZADA: MailX,
      EXPIRADA: Calendar,
      CANCELADA: Ban,
    };
    const Icon = icons[estado] || Clock;
    return <Icon className="w-4 h-4" />;
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
            Invitaciones
          </h1>
          <p className="text-gray-600 dark:text-gray-400 mt-1">
            Gestiona las invitaciones enviadas a usuarios
          </p>
        </div>
        <button
          onClick={() => setMostrarFormulario(true)}
          className="px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white rounded-xl transition-colors font-medium flex items-center gap-2 shadow-lg shadow-blue-500/30"
        >
          <Send className="w-5 h-5" />
          Nueva Invitación
        </button>
      </div>

      {/* Estadísticas */}
      {estadisticas && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {/* Total */}
          <div className="p-6 bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 shadow-sm">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600 dark:text-gray-400">Total</p>
                <p className="text-3xl font-bold text-gray-900 dark:text-white mt-1">
                  {estadisticas.total}
                </p>
              </div>
              <div className="p-3 bg-blue-100 dark:bg-blue-900/30 rounded-lg">
                <Mail className="w-6 h-6 text-blue-600 dark:text-blue-400" />
              </div>
            </div>
          </div>

          {/* Pendientes */}
          <div className="p-6 bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 shadow-sm">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600 dark:text-gray-400">Pendientes</p>
                <p className="text-3xl font-bold text-yellow-600 dark:text-yellow-400 mt-1">
                  {estadisticas.pendientes}
                </p>
              </div>
              <div className="p-3 bg-yellow-100 dark:bg-yellow-900/30 rounded-lg">
                <Clock className="w-6 h-6 text-yellow-600 dark:text-yellow-400" />
              </div>
            </div>
          </div>

          {/* Aceptadas */}
          <div className="p-6 bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 shadow-sm">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600 dark:text-gray-400">Aceptadas</p>
                <p className="text-3xl font-bold text-green-600 dark:text-green-400 mt-1">
                  {estadisticas.aceptadas}
                </p>
              </div>
              <div className="p-3 bg-green-100 dark:bg-green-900/30 rounded-lg">
                <MailCheck className="w-6 h-6 text-green-600 dark:text-green-400" />
              </div>
            </div>
          </div>

          {/* Tasa de aceptación */}
          <div className="p-6 bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 shadow-sm">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600 dark:text-gray-400">Tasa Aceptación</p>
                <p className="text-3xl font-bold text-indigo-600 dark:text-indigo-400 mt-1">
                  {estadisticas.tasaAceptacion.toFixed(0)}%
                </p>
              </div>
              <div className="p-3 bg-indigo-100 dark:bg-indigo-900/30 rounded-lg">
                <TrendingUp className="w-6 h-6 text-indigo-600 dark:text-indigo-400" />
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Filtros y búsqueda */}
      <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-4">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          {/* Búsqueda */}
          <div className="md:col-span-2">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
              <input
                type="text"
                placeholder="Buscar por email o nombre..."
                value={filtros.busqueda || ''}
                onChange={handleBuscar}
                className="w-full pl-10 pr-4 py-2.5 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-400 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
          </div>

          {/* Filtro Estado */}
          <div>
            <select
              value={filtros.estado || ''}
              onChange={(e) => handleFiltroEstado(e.target.value as EstadoInvitacion | undefined)}
              className="w-full px-4 py-2.5 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="">Todos los estados</option>
              <option value="PENDIENTE">Pendiente</option>
              <option value="ACEPTADA">Aceptada</option>
              <option value="RECHAZADA">Rechazada</option>
              <option value="EXPIRADA">Expirada</option>
              <option value="CANCELADA">Cancelada</option>
            </select>
          </div>

          {/* Filtro Rol */}
          <div>
            <select
              value={filtros.rol || ''}
              onChange={(e) => handleFiltroRol(e.target.value as RolInvitacion | undefined)}
              className="w-full px-4 py-2.5 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="">Todos los roles</option>
              <option value="COORDINADOR">Coordinador</option>
              <option value="PROFESOR">Profesor</option>
              <option value="ESTUDIANTE">Estudiante</option>
            </select>
          </div>
        </div>
      </div>

      {/* Tabla */}
      <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 overflow-hidden">
        {isLoading ? (
          <div className="p-12 text-center">
            <div className="inline-block w-8 h-8 border-4 border-blue-600 border-t-transparent rounded-full animate-spin" />
            <p className="text-gray-600 dark:text-gray-400 mt-4">Cargando invitaciones...</p>
          </div>
        ) : !invitaciones?.items.length ? (
          <div className="p-12 text-center">
            <Mail className="w-16 h-16 text-gray-300 dark:text-gray-600 mx-auto mb-4" />
            <p className="text-xl font-medium text-gray-900 dark:text-white mb-2">
              No hay invitaciones
            </p>
            <p className="text-gray-600 dark:text-gray-400">
              {filtros.busqueda || filtros.estado || filtros.rol
                ? 'No se encontraron resultados con los filtros aplicados'
                : 'Crea tu primera invitación para comenzar'}
            </p>
          </div>
        ) : (
          <>
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-gray-50 dark:bg-gray-900/50 border-b border-gray-200 dark:border-gray-700">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                      Usuario
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                      Rol
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                      Estado
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                      Código
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                      Fecha
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                      Expira
                    </th>
                    <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                      Acciones
                    </th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-200 dark:divide-gray-700">
                  {invitaciones.items.map((invitacion) => (
                    <tr
                      key={invitacion.id}
                      className="hover:bg-gray-50 dark:hover:bg-gray-700/50 transition-colors"
                    >
                      <td className="px-6 py-4">
                        <div>
                          <p className="font-medium text-gray-900 dark:text-white">
                            {invitacion.nombreInvitado}
                          </p>
                          <p className="text-sm text-gray-500 dark:text-gray-400">
                            {invitacion.email}
                          </p>
                        </div>
                      </td>
                      <td className="px-6 py-4">
                        <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium bg-purple-100 text-purple-800 dark:bg-purple-900/30 dark:text-purple-400">
                          <Users className="w-3 h-3" />
                          {invitacion.rol}
                        </span>
                      </td>
                      <td className="px-6 py-4">
                        <span
                          className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium ${getEstadoBadge(
                            invitacion.estado
                          )}`}
                        >
                          {getEstadoIcon(invitacion.estado)}
                          {invitacion.estado}
                        </span>
                      </td>
                      <td className="px-6 py-4">
                        <code className="px-2 py-1 bg-gray-100 dark:bg-gray-700 rounded text-sm font-mono text-gray-900 dark:text-white">
                          {invitacion.codigo}
                        </code>
                      </td>
                      <td className="px-6 py-4 text-sm text-gray-600 dark:text-gray-400">
                        {new Date(invitacion.fechaCreacion).toLocaleDateString('es-ES', {
                          day: '2-digit',
                          month: 'short',
                          year: 'numeric',
                        })}
                      </td>
                      <td className="px-6 py-4 text-sm text-gray-600 dark:text-gray-400">
                        {new Date(invitacion.fechaExpiracion).toLocaleDateString('es-ES', {
                          day: '2-digit',
                          month: 'short',
                        })}
                      </td>
                      <td className="px-6 py-4">
                        <div className="flex items-center justify-end gap-2">
                          {invitacion.estado === 'PENDIENTE' && (
                            <>
                              <button
                                onClick={() => handleReenviar(invitacion.id)}
                                disabled={reenviarMutation.isPending}
                                className="p-2 hover:bg-blue-100 dark:hover:bg-blue-900/30 text-blue-600 dark:text-blue-400 rounded-lg transition-colors disabled:opacity-50"
                                title="Reenviar"
                              >
                                <RefreshCw className="w-4 h-4" />
                              </button>
                              <button
                                onClick={() => handleCancelar(invitacion.id)}
                                disabled={cancelarMutation.isPending}
                                className="p-2 hover:bg-red-100 dark:hover:bg-red-900/30 text-red-600 dark:text-red-400 rounded-lg transition-colors disabled:opacity-50"
                                title="Cancelar"
                              >
                                <Ban className="w-4 h-4" />
                              </button>
                            </>
                          )}
                          <button
                            className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 text-gray-600 dark:text-gray-400 rounded-lg transition-colors"
                            title="Ver detalles"
                          >
                            <Eye className="w-4 h-4" />
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            {/* Paginación */}
            {invitaciones.totalPaginas > 1 && (
              <div className="flex items-center justify-between px-6 py-4 border-t border-gray-200 dark:border-gray-700">
                <p className="text-sm text-gray-600 dark:text-gray-400">
                  Mostrando {((filtros.pagina || 1) - 1) * (filtros.limite || 10) + 1} -{' '}
                  {Math.min((filtros.pagina || 1) * (filtros.limite || 10), invitaciones.total)} de{' '}
                  {invitaciones.total} invitaciones
                </p>
                <div className="flex gap-2">
                  <button
                    onClick={() => setFiltros(prev => ({ ...prev, pagina: (prev.pagina || 1) - 1 }))}
                    disabled={!filtros.pagina || filtros.pagina === 1}
                    className="px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                  >
                    Anterior
                  </button>
                  <span className="px-4 py-2 text-gray-700 dark:text-gray-300">
                    {filtros.pagina || 1} / {invitaciones.totalPaginas}
                  </span>
                  <button
                    onClick={() => setFiltros(prev => ({ ...prev, pagina: (prev.pagina || 1) + 1 }))}
                    disabled={filtros.pagina === invitaciones.totalPaginas}
                    className="px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                  >
                    Siguiente
                  </button>
                </div>
              </div>
            )}
          </>
        )}
      </div>

      {/* Modal Formulario */}
      <FormularioInvitacion
        isOpen={mostrarFormulario}
        onClose={() => setMostrarFormulario(false)}
        institucionId={institucionId || 1} // TODO: Obtener de contexto/auth
      />
    </div>
  );
}
