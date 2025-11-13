/**
 * Componente ListaProgramas
 * 
 * Muestra lista paginada de programas académicos con capacidades de:
 * - Búsqueda en tiempo real
 * - Filtros avanzados (institución, nivel, modalidad, estado)
 * - Paginación
 * - Acciones CRUD (Ver, Editar, Eliminar, Cambiar Estado)
 * 
 * @component
 */

import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useProgramas, useProgramaOperations } from '../hooks/useProgramas';
import { NivelAcademico, ModalidadEstudio, EstadoPrograma } from '../types';
import type { FiltrosProgramas } from '../types';
import { Book, ChevronLeft, ChevronRight, Edit, Eye, Filter, GraduationCap, MoreVertical, Plus, School, Search, Users } from 'lucide-react';

/**
 * Componente principal de lista de programas
 */
export function ListaProgramas() {
  const navigate = useNavigate();
  const [busqueda, setBusqueda] = useState('');
  const [mostrarFiltros, setMostrarFiltros] = useState(false);
  const [paginaActual, setPaginaActual] = useState(1);
  
  const [filtros, setFiltros] = useState<FiltrosProgramas>({
    pagina: 1,
    limite: 9,
    ordenarPor: 'fecha',
    orden: 'desc',
  });

  // Query para obtener programas
  const {
    data: respuestaProgramas,
    isLoading,
    error,
    refetch,
  } = useProgramas({
    ...filtros,
    busqueda: busqueda || undefined,
    pagina: paginaActual,
  });

  const { eliminar, cambiarEstado } = useProgramaOperations();

  /**
   * Maneja el cambio de búsqueda con debounce implícito
   */
  const handleBusqueda = (valor: string) => {
    setBusqueda(valor);
    setPaginaActual(1); // Reset a página 1 al buscar
  };

  /**
   * Maneja el cambio de filtros
   */
  const handleFiltroChange = (campo: keyof FiltrosProgramas, valor: any) => {
    setFiltros(prev => ({ ...prev, [campo]: valor }));
    setPaginaActual(1);
  };

  /**
   * Maneja la eliminación de un programa
   */
  const handleEliminar = async (id: number, nombre: string) => {
    if (!window.confirm(`¿Estás seguro de eliminar el programa "${nombre}"? Esta acción no se puede deshacer.`)) {
      return;
    }

    try {
      await eliminar.mutateAsync(id);
      alert('Programa eliminado exitosamente');
    } catch (error: any) {
      alert(error.message || 'Error al eliminar programa');
    }
  };

  /**
   * Maneja el cambio de estado de un programa
   */
  const handleCambiarEstado = async (id: number, estadoActual: EstadoPrograma) => {
    const nuevoEstado = estadoActual === EstadoPrograma.ACTIVO 
      ? EstadoPrograma.INACTIVO 
      : EstadoPrograma.ACTIVO;
    
    try {
      await cambiarEstado.mutateAsync({ id, estado: nuevoEstado });
    } catch (error: any) {
      alert(error.message || 'Error al cambiar estado');
    }
  };

  /**
   * Obtiene la etiqueta del nivel académico
   */
  const getNivelLabel = (nivel: NivelAcademico): string => {
    const labels: Record<NivelAcademico, string> = {
      TECNICO: 'Técnico',
      TECNOLOGO: 'Tecnólogo',
      PROFESIONAL: 'Profesional',
      ESPECIALIZACION: 'Especialización',
      MAESTRIA: 'Maestría',
      DOCTORADO: 'Doctorado',
    };
    return labels[nivel];
  };

  /**
   * Obtiene el color del badge según el estado
   */
  const getEstadoColor = (estado: EstadoPrograma): string => {
    const colors: Record<EstadoPrograma, string> = {
      ACTIVO: 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200',
      INACTIVO: 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-300',
      EN_REVISION: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200',
      ARCHIVADO: 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200',
    };
    return colors[estado];
  };

  // Estados de carga
  if (isLoading) {
    return (
      <div className="p-6">
        <div className="flex justify-between items-center mb-6">
          <h1 className="text-2xl font-bold text-gray-800 dark:text-white">
            Programas Académicos
          </h1>
        </div>
        
        {/* Skeletons de carga */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {[...Array(6)].map((_, i) => (
            <div
              key={i}
              className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6 animate-pulse"
            >
              <div className="h-4 bg-gray-300 dark:bg-gray-600 rounded w-3/4 mb-4"></div>
              <div className="h-3 bg-gray-200 dark:bg-gray-700 rounded w-full mb-2"></div>
              <div className="h-3 bg-gray-200 dark:bg-gray-700 rounded w-2/3"></div>
            </div>
          ))}
        </div>
      </div>
    );
  }

  // Estado de error
  if (error) {
    return (
      <div className="p-6">
        <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-6 text-center">
          <p className="text-red-800 dark:text-red-200 mb-4">
            {error.message || 'Error al cargar programas'}
          </p>
          <button
            onClick={() => refetch()}
            className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition"
          >
            Reintentar
          </button>
        </div>
      </div>
    );
  }

  const programas = respuestaProgramas?.items || [];
  const totalPaginas = respuestaProgramas?.totalPaginas || 1;
  const total = respuestaProgramas?.total || 0;

  return (
    <div className="p-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-800 dark:text-white flex items-center gap-2">
            <GraduationCap className="text-purple-600" />
            Programas Académicos
          </h1>
          <p className="text-gray-600 dark:text-gray-400 text-sm mt-1">
            Gestiona los programas académicos de tu institución
          </p>
        </div>
        
        <Link
          to="/admin/programas/crear"
          className="flex items-center gap-2 px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition shadow-md"
        >
          <Plus /> Nuevo Programa
        </Link>
      </div>

      {/* Barra de búsqueda y filtros */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-4 mb-6">
        <div className="flex flex-col md:flex-row gap-4">
          {/* Búsqueda */}
          <div className="flex-1 relative">
            <FaSearch className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
            <input
              type="text"
              placeholder="Buscar por nombre, código o descripción..."
              value={busqueda}
              onChange={(e) => handleBusqueda(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-purple-500 dark:bg-gray-700 dark:text-white"
            />
          </div>

          {/* Botón de filtros */}
          <button
            onClick={() => setMostrarFiltros(!mostrarFiltros)}
            className={`flex items-center gap-2 px-4 py-2 rounded-lg transition ${
              mostrarFiltros
                ? 'bg-purple-600 text-white'
                : 'bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300'
            }`}
          >
            <FaFilter /> Filtros
          </button>
        </div>

        {/* Panel de filtros */}
        {mostrarFiltros && (
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mt-4 pt-4 border-t border-gray-200 dark:border-gray-700">
            {/* Filtro por Nivel */}
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Nivel Académico
              </label>
              <select
                value={filtros.nivel || ''}
                onChange={(e) => handleFiltroChange('nivel', e.target.value || undefined)}
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg dark:bg-gray-700 dark:text-white"
              >
                <option value="">Todos</option>
                <option value="TECNICO">Técnico</option>
                <option value="TECNOLOGO">Tecnólogo</option>
                <option value="PROFESIONAL">Profesional</option>
                <option value="ESPECIALIZACION">Especialización</option>
                <option value="MAESTRIA">Maestría</option>
                <option value="DOCTORADO">Doctorado</option>
              </select>
            </div>

            {/* Filtro por Modalidad */}
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Modalidad
              </label>
              <select
                value={filtros.modalidad || ''}
                onChange={(e) => handleFiltroChange('modalidad', e.target.value || undefined)}
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg dark:bg-gray-700 dark:text-white"
              >
                <option value="">Todas</option>
                <option value="PRESENCIAL">Presencial</option>
                <option value="VIRTUAL">Virtual</option>
                <option value="HIBRIDO">Híbrido</option>
              </select>
            </div>

            {/* Filtro por Estado */}
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Estado
              </label>
              <select
                value={filtros.estado || ''}
                onChange={(e) => handleFiltroChange('estado', e.target.value || undefined)}
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg dark:bg-gray-700 dark:text-white"
              >
                <option value="">Todos</option>
                <option value="ACTIVO">Activos</option>
                <option value="INACTIVO">Inactivos</option>
                <option value="EN_REVISION">En Revisión</option>
                <option value="ARCHIVADO">Archivados</option>
              </select>
            </div>

            {/* Filtro por Orden */}
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Ordenar por
              </label>
              <select
                value={`${filtros.ordenarPor}-${filtros.orden}`}
                onChange={(e) => {
                  const [ordenarPor, orden] = e.target.value.split('-');
                  setFiltros(prev => ({
                    ...prev,
                    ordenarPor: ordenarPor as any,
                    orden: orden as 'asc' | 'desc',
                  }));
                }}
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg dark:bg-gray-700 dark:text-white"
              >
                <option value="fecha-desc">Más recientes</option>
                <option value="fecha-asc">Más antiguos</option>
                <option value="nombre-asc">Nombre A-Z</option>
                <option value="nombre-desc">Nombre Z-A</option>
                <option value="estudiantes-desc">Más estudiantes</option>
                <option value="cursos-desc">Más cursos</option>
              </select>
            </div>
          </div>
        )}
      </div>

      {/* Lista de programas */}
      {programas.length === 0 ? (
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-12 text-center">
          <GraduationCap className="mx-auto text-6xl text-gray-400 mb-4" />
          <h3 className="text-xl font-semibold text-gray-800 dark:text-white mb-2">
            No hay programas
          </h3>
          <p className="text-gray-600 dark:text-gray-400 mb-6">
            Comienza creando tu primer programa académico
          </p>
          <Link
            to="/admin/programas/crear"
            className="inline-flex items-center gap-2 px-6 py-3 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition"
          >
            <Plus /> Crear Programa
          </Link>
        </div>
      ) : (
        <>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {programas.map((programa) => (
              <div
                key={programa.id}
                className="bg-white dark:bg-gray-800 rounded-lg shadow-md overflow-hidden hover:shadow-lg transition group"
              >
                {/* Header con gradiente */}
                <div className="bg-gradient-to-r from-purple-600 to-indigo-600 p-6 relative">
                  <div className="flex justify-between items-start">
                    <div className="flex-1">
                      <span className="text-purple-100 text-sm font-medium">
                        {programa.codigo}
                      </span>
                      <h3 className="text-white font-bold text-lg mt-1 line-clamp-2">
                        {programa.nombre}
                      </h3>
                    </div>
                    <span
                      className={`px-2 py-1 rounded-full text-xs font-medium ${getEstadoColor(
                        programa.estado
                      )}`}
                    >
                      {programa.estado}
                    </span>
                  </div>
                  
                  {/* Nivel y modalidad */}
                  <div className="flex gap-2 mt-3">
                    <span className="px-2 py-1 bg-white/20 backdrop-blur-sm rounded text-white text-xs">
                      {getNivelLabel(programa.nivel)}
                    </span>
                    <span className="px-2 py-1 bg-white/20 backdrop-blur-sm rounded text-white text-xs">
                      {programa.modalidad}
                    </span>
                  </div>
                </div>

                {/* Contenido */}
                <div className="p-6">
                  {/* Institución */}
                  {programa.institucion && (
                    <div className="flex items-center gap-2 text-sm text-gray-600 dark:text-gray-400 mb-3">
                      <School className="text-gray-400" />
                      <span className="truncate">{programa.institucion.nombre}</span>
                    </div>
                  )}

                  {/* Descripción */}
                  {programa.descripcion && (
                    <p className="text-gray-600 dark:text-gray-400 text-sm mb-4 line-clamp-2">
                      {programa.descripcion}
                    </p>
                  )}

                  {/* Estadísticas */}
                  <div className="grid grid-cols-3 gap-4 mb-4">
                    <div className="text-center">
                      <Book className="mx-auto text-purple-600 mb-1" />
                      <p className="text-xs text-gray-500 dark:text-gray-400">Cursos</p>
                      <p className="font-semibold text-gray-800 dark:text-white">
                        {programa.totalCursos}
                      </p>
                    </div>
                    <div className="text-center">
                      <Users className="mx-auto text-blue-600 mb-1" />
                      <p className="text-xs text-gray-500 dark:text-gray-400">Estudiantes</p>
                      <p className="font-semibold text-gray-800 dark:text-white">
                        {programa.totalEstudiantes}
                      </p>
                    </div>
                    <div className="text-center">
                      <GraduationCap className="mx-auto text-green-600 mb-1" />
                      <p className="text-xs text-gray-500 dark:text-gray-400">Semestres</p>
                      <p className="font-semibold text-gray-800 dark:text-white">
                        {programa.duracionSemestres}
                      </p>
                    </div>
                  </div>

                  {/* Acciones */}
                  <div className="flex gap-2">
                    <button
                      onClick={() => navigate(`/admin/programas/${programa.id}`)}
                      className="flex-1 flex items-center justify-center gap-2 px-3 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 transition text-sm"
                    >
                      <FaEye /> Ver
                    </button>
                    <button
                      onClick={() => navigate(`/admin/programas/${programa.id}/editar`)}
                      className="flex-1 flex items-center justify-center gap-2 px-3 py-2 bg-purple-600 text-white rounded hover:bg-purple-700 transition text-sm"
                    >
                      <Edit /> Editar
                    </button>
                    <div className="relative group/menu">
                      <button className="px-3 py-2 bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded hover:bg-gray-300 dark:hover:bg-gray-600 transition">
                        <FaEllipsisV />
                      </button>
                      
                      {/* Dropdown menu */}
                      <div className="absolute right-0 mt-2 w-48 bg-white dark:bg-gray-700 rounded-lg shadow-xl opacity-0 invisible group-hover/menu:opacity-100 group-hover/menu:visible transition z-10">
                        <button
                          onClick={() => handleCambiarEstado(programa.id, programa.estado)}
                          className="w-full text-left px-4 py-2 hover:bg-gray-100 dark:hover:bg-gray-600 text-gray-700 dark:text-gray-300"
                        >
                          {programa.estado === 'ACTIVO' ? 'Desactivar' : 'Activar'}
                        </button>
                        <button
                          onClick={() => handleEliminar(programa.id, programa.nombre)}
                          className="w-full text-left px-4 py-2 hover:bg-red-50 dark:hover:bg-red-900/20 text-red-600 rounded-b-lg"
                        >
                          Eliminar
                        </button>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>

          {/* Paginación */}
          {totalPaginas > 1 && (
            <div className="mt-8 flex flex-col sm:flex-row items-center justify-between gap-4">
              <p className="text-sm text-gray-600 dark:text-gray-400">
                Mostrando {(paginaActual - 1) * filtros.limite! + 1} -{' '}
                {Math.min(paginaActual * filtros.limite!, total)} de {total} programas
              </p>

              <div className="flex gap-2">
                <button
                  onClick={() => setPaginaActual(prev => Math.max(1, prev - 1))}
                  disabled={paginaActual === 1}
                  className="flex items-center gap-2 px-4 py-2 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded-lg disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50 dark:hover:bg-gray-700 transition"
                >
                  <FaChevronLeft /> Anterior
                </button>
                
                <span className="flex items-center px-4 py-2 bg-purple-600 text-white rounded-lg font-medium">
                  {paginaActual} / {totalPaginas}
                </span>

                <button
                  onClick={() => setPaginaActual(prev => Math.min(totalPaginas, prev + 1))}
                  disabled={paginaActual === totalPaginas}
                  className="flex items-center gap-2 px-4 py-2 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded-lg disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50 dark:hover:bg-gray-700 transition"
                >
                  Siguiente <FaChevronRight />
                </button>
              </div>
            </div>
          )}
        </>
      )}
    </div>
  );
}

export default ListaProgramas;
