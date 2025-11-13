/**
 * Componente DetallePrograma
 * Vista detallada de un programa académico
 */

import { useParams, useNavigate, Link } from 'react-router-dom';
import { usePrograma, useEstadisticasPrograma } from '../hooks/useProgramas';
import { ArrowLeft, Book, Clock, Edit, GraduationCap, LineChart, School, Users } from 'lucide-react';

export function DetallePrograma() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  
  const { data: programa, isLoading, error } = usePrograma(parseInt(id!));
  const { data: estadisticas } = useEstadisticasPrograma(parseInt(id!));

  if (isLoading) {
    return (
      <div className="p-6">
        <div className="animate-pulse space-y-4">
          <div className="h-8 bg-gray-300 dark:bg-gray-600 rounded w-1/4"></div>
          <div className="h-64 bg-gray-300 dark:bg-gray-600 rounded"></div>
        </div>
      </div>
    );
  }

  if (error || !programa) {
    return (
      <div className="p-6">
        <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-6 text-center">
          <p className="text-red-800 dark:text-red-200">
            {error?.message || 'Programa no encontrado'}
          </p>
          <button
            onClick={() => navigate('/admin/programas')}
            className="mt-4 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition"
          >
            Volver a Programas
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 max-w-6xl mx-auto">
      {/* Header */}
      <div className="flex justify-between items-start mb-6">
        <button
          onClick={() => navigate('/admin/programas')}
          className="flex items-center gap-2 text-gray-600 dark:text-gray-400 hover:text-purple-600 dark:hover:text-purple-400 transition"
        >
          <ArrowLeft /> Volver
        </button>
        
        <Link
          to={`/admin/programas/${id}/editar`}
          className="flex items-center gap-2 px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition"
        >
          <Edit /> Editar
        </Link>
      </div>

      {/* Título del programa */}
      <div className="bg-gradient-to-r from-purple-600 to-indigo-600 rounded-lg p-8 mb-6 text-white">
        <div className="flex items-start justify-between">
          <div>
            <span className="text-purple-200 text-sm font-medium">{programa.codigo}</span>
            <h1 className="text-3xl font-bold mt-2">{programa.nombre}</h1>
            <div className="flex gap-4 mt-4">
              <span className="px-3 py-1 bg-white/20 backdrop-blur-sm rounded-full text-sm">
                {programa.nivel}
              </span>
              <span className="px-3 py-1 bg-white/20 backdrop-blur-sm rounded-full text-sm">
                {programa.modalidad}
              </span>
              <span className="px-3 py-1 bg-white/20 backdrop-blur-sm rounded-full text-sm">
                {programa.estado}
              </span>
            </div>
          </div>
          {programa.institucion && (
            <div className="text-right">
              <School className="text-3xl mb-2 ml-auto" />
              <p className="text-sm">{programa.institucion.nombre}</p>
            </div>
          )}
        </div>
      </div>

      {/* Grid de información */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">
        {/* Estadísticas principales */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6">
          <div className="flex items-center gap-3 mb-4">
            <Book className="text-2xl text-purple-600" />
            <div>
              <p className="text-sm text-gray-500 dark:text-gray-400">Total Cursos</p>
              <p className="text-2xl font-bold text-gray-800 dark:text-white">
                {programa.totalCursos}
              </p>
            </div>
          </div>
        </div>

        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6">
          <div className="flex items-center gap-3 mb-4">
            <Users className="text-2xl text-blue-600" />
            <div>
              <p className="text-sm text-gray-500 dark:text-gray-400">Estudiantes</p>
              <p className="text-2xl font-bold text-gray-800 dark:text-white">
                {programa.totalEstudiantes}
              </p>
            </div>
          </div>
        </div>

        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6">
          <div className="flex items-center gap-3 mb-4">
            <Clock className="text-2xl text-green-600" />
            <div>
              <p className="text-sm text-gray-500 dark:text-gray-400">Duración</p>
              <p className="text-2xl font-bold text-gray-800 dark:text-white">
                {programa.duracionSemestres} semestres
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Información del programa */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6 mb-6">
        <h2 className="text-xl font-bold text-gray-800 dark:text-white mb-4">
          Descripción
        </h2>
        <p className="text-gray-600 dark:text-gray-400">
          {programa.descripcion || 'Sin descripción'}
        </p>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mt-6">
          <div>
            <h3 className="font-semibold text-gray-800 dark:text-white mb-2">
              Requisitos Académicos
            </h3>
            <ul className="space-y-2 text-gray-600 dark:text-gray-400">
              <li>• Créditos requeridos: {programa.creditosRequeridos}</li>
              <li>• Proyecto de grado: {programa.requiereProyectoGrado ? 'Sí' : 'No'}</li>
              <li>• Prácticas: {programa.requierePracticas ? `Sí (${programa.horasPracticas} horas)` : 'No'}</li>
            </ul>
          </div>

          {estadisticas && (
            <div>
              <h3 className="font-semibold text-gray-800 dark:text-white mb-2">
                Estadísticas
              </h3>
              <ul className="space-y-2 text-gray-600 dark:text-gray-400">
                <li>• Tasa de graduación: {estadisticas.tasaGraduacion.toFixed(1)}%</li>
                <li>• Estudiantes activos: {estadisticas.estudiantesActivos}</li>
                <li>• Graduados: {estadisticas.estudiantesGraduados}</li>
              </ul>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default DetallePrograma;
