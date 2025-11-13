/**
 * ListaInstituciones Component
 * Muestra todas las instituciones con filtros, búsqueda y paginación
 * Principio SRP: Solo se encarga de mostrar la lista
 */

import { useState } from 'react';
import { Link } from 'react-router-dom';
import { useInstituciones, useEliminarInstitucion, useToggleActivoInstitucion } from '../hooks/useInstituciones';
import type { FiltrosInstitucion } from '../types';
import { Book, Building, Edit, Eye, Filter, MoreVertical, Plus, Search, ToggleLeft, ToggleRight, Trash, Users } from 'lucide-react';

export function ListaInstituciones() {
  const [filtros, setFiltros] = useState<FiltrosInstitucion>({
    busqueda: '',
    activo: undefined,
    ordenarPor: 'nombre',
    orden: 'asc',
    pagina: 1,
    limite: 10,
  });

  const [mostrarFiltros, setMostrarFiltros] = useState(false);
  const [institucionSeleccionada, setInstitucionSeleccionada] = useState<string | null>(null);

  const { data, isLoading, error, refetch } = useInstituciones(filtros);
  const eliminarMutation = useEliminarInstitucion();
  const toggleActivoMutation = useToggleActivoInstitucion();

  const handleBuscar = (termino: string) => {
    setFiltros((prev) => ({ ...prev, busqueda: termino, pagina: 1 }));
  };

  const handleEliminar = async (id: string) => {
    if (confirm('¿Estás seguro de eliminar esta institución? Esta acción no se puede deshacer.')) {
      try {
        await eliminarMutation.mutateAsync(id);
        alert('Institución eliminada exitosamente');
      } catch (error: any) {
        alert(error.message || 'Error al eliminar institución');
      }
    }
  };

  const handleToggleActivo = async (id: string, activo: boolean) => {
    try {
      await toggleActivoMutation.mutateAsync({ id, activo: !activo });
    } catch (error: any) {
      alert(error.message || 'Error al cambiar estado');
    }
  };

  const handleCambiarPagina = (nuevaPagina: number) => {
    setFiltros((prev) => ({ ...prev, pagina: nuevaPagina }));
  };

  if (error) {
    return (
      <div className="p-6">
        <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4">
          <p className="text-red-800 dark:text-red-200">
            Error al cargar instituciones: {error.message}
          </p>
          <button
            onClick={() => refetch()}
            className="mt-2 text-red-600 dark:text-red-400 hover:underline"
          >
            Reintentar
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white flex items-center gap-2">
            <Building className="w-8 h-8" />
            Instituciones
          </h1>
          <p className="text-gray-600 dark:text-gray-400 mt-1">
            Gestiona las instituciones educativas del sistema
          </p>
        </div>
        <Link
          to="/admin/instituciones/crear"
          className="flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors"
        >
          <Plus className="w-5 h-5" />
          Nueva Institución
        </Link>
      </div>

      {/* Barra de búsqueda y filtros */}
      <div className="flex items-center gap-4">
        <div className="flex-1 relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
          <input
            type="text"
            placeholder="Buscar instituciones..."
            value={filtros.busqueda}
            onChange={(e) => handleBuscar(e.target.value)}
            className="w-full pl-10 pr-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500"
          />
        </div>
        <button
          onClick={() => setMostrarFiltros(!mostrarFiltros)}
          className="flex items-center gap-2 px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors"
        >
          <Filter className="w-5 h-5" />
          Filtros
        </button>
      </div>

      {/* Panel de filtros */}
      {mostrarFiltros && (
        <div className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg p-4 space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Estado
              </label>
              <select
                value={filtros.activo === undefined ? 'todos' : filtros.activo ? 'activo' : 'inactivo'}
                onChange={(e) => {
                  const valor = e.target.value === 'todos' ? undefined : e.target.value === 'activo';
                  setFiltros((prev) => ({ ...prev, activo: valor, pagina: 1 }));
                }}
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700"
              >
                <option value="todos">Todos</option>
                <option value="activo">Activos</option>
                <option value="inactivo">Inactivos</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Ordenar por
              </label>
              <select
                value={filtros.ordenarPor}
                onChange={(e) => setFiltros((prev) => ({ ...prev, ordenarPor: e.target.value as any }))}
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700"
              >
                <option value="nombre">Nombre</option>
                <option value="fecha">Fecha de creación</option>
                <option value="estudiantes">Estudiantes</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Orden
              </label>
              <select
                value={filtros.orden}
                onChange={(e) => setFiltros((prev) => ({ ...prev, orden: e.target.value as any }))}
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700"
              >
                <option value="asc">Ascendente</option>
                <option value="desc">Descendente</option>
              </select>
            </div>
          </div>
        </div>
      )}

      {/* Grid de instituciones */}
      {isLoading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {[1, 2, 3, 4, 5, 6].map((i) => (
            <div key={i} className="bg-white dark:bg-gray-800 rounded-lg p-6 animate-pulse">
              <div className="h-16 w-16 bg-gray-300 dark:bg-gray-700 rounded-lg mb-4" />
              <div className="h-6 bg-gray-300 dark:bg-gray-700 rounded mb-2" />
              <div className="h-4 bg-gray-300 dark:bg-gray-700 rounded w-2/3" />
            </div>
          ))}
        </div>
      ) : data?.items.length === 0 ? (
        <div className="text-center py-12">
          <Building className="w-16 h-16 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">
            No hay instituciones
          </h3>
          <p className="text-gray-600 dark:text-gray-400">
            Comienza creando tu primera institución
          </p>
        </div>
      ) : (
        <>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {data?.items.map((institucion) => (
              <div
                key={institucion.id}
                className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg overflow-hidden hover:shadow-lg transition-shadow"
              >
                {/* Header con logo */}
                <div className="relative h-32 bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center">
                  {institucion.logo ? (
                    <img
                      src={institucion.logo}
                      alt={institucion.nombre}
                      className="w-20 h-20 rounded-lg object-cover bg-white"
                    />
                  ) : (
                    <Building className="w-20 h-20 text-white opacity-80" />
                  )}
                  
                  {/* Badge de estado */}
                  <div className="absolute top-3 right-3">
                    <span
                      className={`px-2 py-1 text-xs font-medium rounded-full ${
                        institucion.activo
                          ? 'bg-green-100 text-green-800'
                          : 'bg-gray-100 text-gray-800'
                      }`}
                    >
                      {institucion.activo ? 'Activo' : 'Inactivo'}
                    </span>
                  </div>
                </div>

                {/* Contenido */}
                <div className="p-6">
                  <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-2">
                    {institucion.nombre}
                  </h3>
                  {institucion.descripcion && (
                    <p className="text-gray-600 dark:text-gray-400 text-sm mb-4 line-clamp-2">
                      {institucion.descripcion}
                    </p>
                  )}

                  {/* Estadísticas */}
                  {institucion.estadisticas && (
                    <div className="grid grid-cols-2 gap-4 mb-4">
                      <div className="flex items-center gap-2 text-sm">
                        <Book className="w-4 h-4 text-blue-500" />
                        <span className="text-gray-600 dark:text-gray-400">
                          {institucion.estadisticas.totalCursos} cursos
                        </span>
                      </div>
                      <div className="flex items-center gap-2 text-sm">
                        <Users className="w-4 h-4 text-green-500" />
                        <span className="text-gray-600 dark:text-gray-400">
                          {institucion.estadisticas.totalEstudiantes} estudiantes
                        </span>
                      </div>
                    </div>
                  )}

                  {/* Acciones */}
                  <div className="flex items-center gap-2">
                    <Link
                      to={`/admin/instituciones/${institucion.id}`}
                      className="flex-1 flex items-center justify-center gap-2 px-3 py-2 bg-blue-50 dark:bg-blue-900/20 text-blue-600 dark:text-blue-400 rounded-lg hover:bg-blue-100 dark:hover:bg-blue-900/30 transition-colors"
                    >
                      <Eye className="w-4 h-4" />
                      Ver
                    </Link>
                    <Link
                      to={`/admin/instituciones/${institucion.id}/editar`}
                      className="flex-1 flex items-center justify-center gap-2 px-3 py-2 bg-purple-50 dark:bg-purple-900/20 text-purple-600 dark:text-purple-400 rounded-lg hover:bg-purple-100 dark:hover:bg-purple-900/30 transition-colors"
                    >
                      <Edit className="w-4 h-4" />
                      FaEditar
                    </Link>
                    
                    {/* Menú de opciones */}
                    <div className="relative">
                      <button
                        onClick={() => setInstitucionSeleccionada(
                          institucionSeleccionada === institucion.id ? null : institucion.id
                        )}
                        className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
                      >
                        <MoreVertical className="w-5 h-5" />
                      </button>
                      
                      {institucionSeleccionada === institucion.id && (
                        <div className="absolute right-0 mt-2 w-48 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg shadow-lg z-10">
                          <button
                            onClick={() => {
                              handleToggleActivo(institucion.id, institucion.activo);
                              setInstitucionSeleccionada(null);
                            }}
                            className="w-full flex items-center gap-2 px-4 py-2 text-sm hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
                          >
                            {institucion.activo ? (
                              <>
                                <ToggleRight className="w-4 h-4" />
                                Desactivar
                              </>
                            ) : (
                              <>
                                <ToggleLeft className="w-4 h-4" />
                                Activar
                              </>
                            )}
                          </button>
                          <button
                            onClick={() => {
                              handleEliminar(institucion.id);
                              setInstitucionSeleccionada(null);
                            }}
                            className="w-full flex items-center gap-2 px-4 py-2 text-sm text-red-600 hover:bg-red-50 dark:hover:bg-red-900/20 transition-colors"
                          >
                            <Trash className="w-4 h-4" />
                            Eliminar
                          </button>
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>

          {/* Paginación */}
          {data && data.totalPaginas > 1 && (
            <div className="flex items-center justify-between">
              <p className="text-sm text-gray-600 dark:text-gray-400">
                Mostrando {((filtros.pagina || 1) - 1) * (filtros.limite || 10) + 1} -{' '}
                {Math.min((filtros.pagina || 1) * (filtros.limite || 10), data.total)} de{' '}
                {data.total} instituciones
              </p>
              <div className="flex gap-2">
                <button
                  onClick={() => handleCambiarPagina((filtros.pagina || 1) - 1)}
                  disabled={filtros.pagina === 1}
                  className="px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50 dark:hover:bg-gray-800"
                >
                  Anterior
                </button>
                <button
                  onClick={() => handleCambiarPagina((filtros.pagina || 1) + 1)}
                  disabled={filtros.pagina === data.totalPaginas}
                  className="px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50 dark:hover:bg-gray-800"
                >
                  Siguiente
                </button>
              </div>
            </div>
          )}
        </>
      )}
    </div>
  );
}
