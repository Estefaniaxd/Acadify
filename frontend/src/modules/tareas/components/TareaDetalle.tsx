/**
 * TareaDetalle Component
 * 
 * Componente para mostrar el detalle completo de una tarea.
 * Muestra toda la información, entregas de estudiantes y permite calificar.
 * 
 * Principios aplicados:
 * - Single Responsibility: Solo muestra el detalle de la tarea
 * - Open/Closed: Extensible mediante props de callbacks
 * - Separation of Concerns: Lógica de estado separada de presentación
 */

import { useState, useEffect } from 'react';
import {
  ArrowLeft,
  Calendar,
  Clock,
  Award,
  Users,
  FileText,
  AlertCircle,
  CheckCircle2,
  Sparkles,
  Download,
  Loader2,
  Edit,
  Trash2
} from 'lucide-react';
import { TareaEnriquecida, EntregaTarea, EstadoVisualizacion } from '../types';
import { apiClientTareas } from '../api';

interface TareaDetalleProps {
  tareaId: string;
  cursoId: string;
  onBack?: () => void;
  onEditar?: (tarea: TareaEnriquecida) => void;
  onEliminar?: (tareaId: string) => void;
  onCalificarEntrega?: (entrega: EntregaTarea) => void;
  onIrACalificar?: () => void;
}

/**
 * Hook personalizado para cargar datos de la tarea
 * Single Responsibility: Solo maneja la lógica de carga de datos
 */
const useTareaData = (tareaId: string, cursoId: string) => {
  const [tarea, setTarea] = useState<TareaEnriquecida | null>(null);
  const [entregas, setEntregas] = useState<EntregaTarea[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const cargarDatos = async () => {
    try {
      setLoading(true);
      setError(null);

      // Cargar tarea (por ahora mock, luego reemplazar con API real)
      // TODO: Implementar endpoint de tarea enriquecida individual
      const tareaResponse = await apiClientTareas.obtenerTarea(tareaId);
      setTarea(tareaResponse as TareaEnriquecida);

      // Cargar entregas
      // TODO: Implementar endpoint de entregas
      // const entregasResponse = await apiClientTareas.obtenerEntregasTarea(tareaId);
      setEntregas([]);

    } catch (err) {
      console.error('Error cargando datos:', err);
      setError('Error al cargar los datos de la tarea');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    cargarDatos();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [tareaId, cursoId]);

  return { tarea, entregas, loading, error, recargar: cargarDatos };
};

/**
 * Componente para la sección de información de la tarea
 * Single Responsibility: Solo muestra la información básica
 */
const TareaInfoSection = ({ tarea }: { tarea: TareaEnriquecida }) => {
  const getEstadoBadge = () => {
    const colores = {
      [EstadoVisualizacion.PENDIENTE]: 'bg-gray-100 text-gray-700 dark:bg-gray-800 dark:text-gray-300',
      [EstadoVisualizacion.PROXIMA_A_VENCER]: 'bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-400',
      [EstadoVisualizacion.VENCIDA]: 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400',
      [EstadoVisualizacion.ENTREGADA]: 'bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400',
      [EstadoVisualizacion.CALIFICADA]: 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400',
      [EstadoVisualizacion.CERRADA]: 'bg-gray-100 text-gray-600 dark:bg-gray-800 dark:text-gray-400',
    };

    return (
      <span className={`px-3 py-1.5 rounded-full text-sm font-semibold ${colores[tarea.estado_visual]}`}>
        {tarea.info_estado.icono} {tarea.info_estado.texto}
      </span>
    );
  };

  return (
    <div className="bg-white dark:bg-zinc-900 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6">
      {/* Header */}
      <div className="flex items-start justify-between mb-4">
        <div className="flex-1">
          <h1 className="text-3xl font-bold text-gray-900 dark:text-gray-100 mb-2">
            {tarea.titulo}
          </h1>
          {tarea.descripcion && (
            <p className="text-gray-600 dark:text-gray-400 text-lg">
              {tarea.descripcion}
            </p>
          )}
        </div>
        {getEstadoBadge()}
      </div>

      {/* Badges de tipo y prioridad */}
      <div className="flex items-center gap-2 mb-6">
        <span className="px-3 py-1 rounded-lg text-sm font-medium bg-primary/10 text-primary">
          {tarea.tipo}
        </span>
        {tarea.prioridad === 'alta' && (
          <span className="px-3 py-1 rounded-lg text-sm font-medium bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400">
            Alta Prioridad
          </span>
        )}
        {tarea.habilitar_retroalimentacion_ia && (
          <span className="px-3 py-1 rounded-lg text-sm font-medium bg-purple-100 text-purple-700 dark:bg-purple-900/30 dark:text-purple-400 flex items-center gap-1.5">
            <Sparkles className="w-4 h-4" />
            IA Habilitada
          </span>
        )}
      </div>

      {/* Grid de información */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Fecha límite */}
        <div className="flex items-start gap-3">
          <div className="p-2 rounded-lg bg-blue-100 dark:bg-blue-900/30">
            <Calendar className="w-5 h-5 text-blue-600 dark:text-blue-400" />
          </div>
          <div>
            <div className="text-sm text-gray-500 dark:text-gray-400">Fecha límite</div>
            <div className="text-lg font-semibold text-gray-900 dark:text-gray-100">
              {new Date(tarea.fecha_limite).toLocaleDateString('es-ES', {
                day: '2-digit',
                month: 'long',
                year: 'numeric',
                hour: '2-digit',
                minute: '2-digit'
              })}
            </div>
          </div>
        </div>

        {/* Tiempo restante */}
        {tarea.tiempo_restante && (
          <div className="flex items-start gap-3">
            <div className={`p-2 rounded-lg ${tarea.tiempo_restante.es_muy_urgente ? 'bg-red-100 dark:bg-red-900/30' :
              tarea.tiempo_restante.es_urgente ? 'bg-yellow-100 dark:bg-yellow-900/30' :
                'bg-gray-100 dark:bg-gray-800'
              }`}>
              <Clock className={`w-5 h-5 ${tarea.tiempo_restante.es_muy_urgente ? 'text-red-600 dark:text-red-400' :
                tarea.tiempo_restante.es_urgente ? 'text-yellow-600 dark:text-yellow-400' :
                  'text-gray-600 dark:text-gray-400'
                }`} />
            </div>
            <div>
              <div className="text-sm text-gray-500 dark:text-gray-400">Tiempo restante</div>
              <div className={`text-lg font-semibold ${tarea.tiempo_restante.es_muy_urgente ? 'text-red-600 dark:text-red-400' :
                tarea.tiempo_restante.es_urgente ? 'text-yellow-600 dark:text-yellow-400' :
                  'text-gray-900 dark:text-gray-100'
                }`}>
                {tarea.tiempo_restante.mensaje_tiempo}
              </div>
            </div>
          </div>
        )}

        {/* Puntos */}
        <div className="flex items-start gap-3">
          <div className="p-2 rounded-lg bg-amber-100 dark:bg-amber-900/30">
            <Award className="w-5 h-5 text-amber-600 dark:text-amber-400" />
          </div>
          <div>
            <div className="text-sm text-gray-500 dark:text-gray-400">Puntos máximos</div>
            <div className="text-lg font-semibold text-gray-900 dark:text-gray-100">
              {tarea.puntuacion_maxima} puntos
            </div>
          </div>
        </div>
      </div>

      {/* Instrucciones */}
      {tarea.instrucciones && (
        <div className="mt-6 pt-6 border-t border-gray-200 dark:border-gray-700">
          <div className="flex items-center gap-2 mb-3">
            <FileText className="w-5 h-5 text-primary" />
            <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100">
              Instrucciones
            </h3>
          </div>
          <div className="prose dark:prose-invert max-w-none">
            <p className="text-gray-700 dark:text-gray-300 whitespace-pre-wrap">
              {tarea.instrucciones}
            </p>
          </div>
        </div>
      )}
    </div>
  );
};

/**
 * Componente para las métricas de progreso
 * Single Responsibility: Solo muestra estadísticas
 */
const MetricasSection = ({ tarea }: { tarea: TareaEnriquecida }) => {
  return (
    <div className="bg-white dark:bg-zinc-900 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6">
      <div className="flex items-center gap-2 mb-4">
        <Users className="w-5 h-5 text-primary" />
        <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100">
          Progreso de Entregas
        </h3>
      </div>

      {/* Barra de progreso */}
      <div className="mb-6">
        <div className="flex items-center justify-between mb-2">
          <span className="text-sm text-gray-600 dark:text-gray-400">Completitud</span>
          <span className="text-sm font-semibold text-gray-900 dark:text-gray-100">
            {Math.round(tarea.metricas.porcentaje_completitud)}%
          </span>
        </div>
        <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-3 overflow-hidden">
          <div
            className="bg-primary h-full transition-all duration-500"
            style={{ width: `${tarea.metricas.porcentaje_completitud}%` }}
          />
        </div>
      </div>

      {/* Grid de métricas */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="text-center p-3 rounded-lg bg-gray-50 dark:bg-zinc-800">
          <div className="text-2xl font-bold text-gray-900 dark:text-gray-100">
            {tarea.metricas.total_estudiantes}
          </div>
          <div className="text-xs text-gray-600 dark:text-gray-400">Total Estudiantes</div>
        </div>

        <div className="text-center p-3 rounded-lg bg-blue-50 dark:bg-blue-900/20">
          <div className="text-2xl font-bold text-blue-600 dark:text-blue-400">
            {tarea.metricas.entregas_realizadas}
          </div>
          <div className="text-xs text-gray-600 dark:text-gray-400">Entregas Realizadas</div>
        </div>

        <div className="text-center p-3 rounded-lg bg-green-50 dark:bg-green-900/20">
          <div className="text-2xl font-bold text-green-600 dark:text-green-400">
            {tarea.metricas.entregas_calificadas}
          </div>
          <div className="text-xs text-gray-600 dark:text-gray-400">Calificadas</div>
        </div>

        <div className="text-center p-3 rounded-lg bg-yellow-50 dark:bg-yellow-900/20">
          <div className="text-2xl font-bold text-yellow-600 dark:text-yellow-400">
            {tarea.metricas.entregas_pendientes}
          </div>
          <div className="text-xs text-gray-600 dark:text-gray-400">Pendientes</div>
        </div>
      </div>

      {/* Estadísticas de calificación */}
      {tarea.estadisticas_calificacion && (
        <div className="mt-6 pt-6 border-t border-gray-200 dark:border-gray-700">
          <h4 className="text-sm font-semibold text-gray-900 dark:text-gray-100 mb-3">
            Estadísticas de Calificación
          </h4>
          <div className="grid grid-cols-2 md:grid-cols-5 gap-3 text-sm">
            <div>
              <div className="text-gray-500 dark:text-gray-400">Promedio</div>
              <div className="font-semibold text-gray-900 dark:text-gray-100">
                {tarea.estadisticas_calificacion.promedio_calificacion.toFixed(1)}
              </div>
            </div>
            <div>
              <div className="text-gray-500 dark:text-gray-400">Máxima</div>
              <div className="font-semibold text-green-600 dark:text-green-400">
                {tarea.estadisticas_calificacion.calificacion_maxima.toFixed(1)}
              </div>
            </div>
            <div>
              <div className="text-gray-500 dark:text-gray-400">Mínima</div>
              <div className="font-semibold text-red-600 dark:text-red-400">
                {tarea.estadisticas_calificacion.calificacion_minima.toFixed(1)}
              </div>
            </div>
            <div>
              <div className="text-gray-500 dark:text-gray-400">Mediana</div>
              <div className="font-semibold text-gray-900 dark:text-gray-100">
                {tarea.estadisticas_calificacion.mediana.toFixed(1)}
              </div>
            </div>
            <div>
              <div className="text-gray-500 dark:text-gray-400">Desv. Est.</div>
              <div className="font-semibold text-gray-900 dark:text-gray-100">
                {tarea.estadisticas_calificacion.desviacion_estandar.toFixed(1)}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

/**
 * Componente para la lista de entregas
 * Single Responsibility: Solo muestra las entregas
 */
const EntregasSection = ({
  entregas,
  onCalificar
}: {
  entregas: EntregaTarea[];
  onCalificar?: (entrega: EntregaTarea) => void;
}) => {
  if (entregas.length === 0) {
    return (
      <div className="bg-white dark:bg-zinc-900 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-8 text-center">
        <FileText className="w-12 h-12 text-gray-400 dark:text-gray-500 mx-auto mb-3" />
        <p className="text-gray-600 dark:text-gray-400">
          Aún no hay entregas para esta tarea
        </p>
      </div>
    );
  }

  return (
    <div className="bg-white dark:bg-zinc-900 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100">
          Entregas de Estudiantes ({entregas.length})
        </h3>
        <button className="text-sm text-primary hover:underline flex items-center gap-1">
          <Download className="w-4 h-4" />
          Descargar todas
        </button>
      </div>

      <div className="space-y-3">
        {entregas.map((entrega) => (
          <div
            key={entrega.entrega_id}
            className="p-4 rounded-lg border border-gray-200 dark:border-gray-700 hover:border-primary/50 transition-colors"
          >
            <div className="flex items-center justify-between">
              <div className="flex-1">
                <div className="flex items-center gap-2 mb-1">
                  <span className="font-semibold text-gray-900 dark:text-gray-100">
                    {entrega.estudiante_nombre || 'Estudiante'}
                  </span>
                  {entrega.es_entrega_tardia && (
                    <span className="px-2 py-0.5 rounded text-xs font-medium bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400">
                      Tardía
                    </span>
                  )}
                  {entrega.calificacion !== null && entrega.calificacion !== undefined && (
                    <span className="px-2 py-0.5 rounded text-xs font-medium bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400">
                      <CheckCircle2 className="w-3 h-3 inline mr-1" />
                      Calificada
                    </span>
                  )}
                </div>
                <div className="text-sm text-gray-600 dark:text-gray-400">
                  Entregado: {new Date(entrega.fecha_entrega || '').toLocaleString('es-ES')}
                </div>
                {entrega.calificacion !== null && entrega.calificacion !== undefined && (
                  <div className="mt-2 text-lg font-bold text-primary">
                    {entrega.calificacion} / 100
                  </div>
                )}
              </div>

              <div className="flex items-center gap-2">
                {entrega.calificacion === null || entrega.calificacion === undefined ? (
                  <button
                    onClick={() => onCalificar?.(entrega)}
                    className="px-4 py-2 rounded-lg bg-primary text-white hover:bg-primary/90 transition-colors text-sm font-medium"
                  >
                    Calificar
                  </button>
                ) : (
                  <button
                    onClick={() => onCalificar?.(entrega)}
                    className="px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-zinc-800 transition-colors text-sm font-medium"
                  >
                    Ver Detalles
                  </button>
                )}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

/**
 * Componente principal de detalle de tarea
 * Coordina todos los subcomponentes
 */
export default function TareaDetalle({
  tareaId,
  cursoId,
  onBack,
  onEditar,
  onEliminar,
  onCalificarEntrega,
  onIrACalificar
}: TareaDetalleProps) {
  const { tarea, entregas, loading, error } = useTareaData(tareaId, cursoId);

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center py-12">
        <Loader2 className="w-8 h-8 text-primary animate-spin mb-2" />
        <p className="text-gray-600 dark:text-gray-400">Cargando detalle de la tarea...</p>
      </div>
    );
  }

  if (error || !tarea) {
    return (
      <div className="p-4 rounded-lg bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800">
        <div className="flex items-center gap-2 mb-2">
          <AlertCircle className="w-5 h-5 text-red-600 dark:text-red-400" />
          <p className="text-red-800 dark:text-red-300 font-semibold">Error al cargar la tarea</p>
        </div>
        <p className="text-red-600 dark:text-red-400 text-sm">{error}</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header con navegación */}
      <div className="flex items-center justify-between">
        <button
          onClick={onBack}
          className="flex items-center gap-2 text-gray-600 dark:text-gray-400 hover:text-primary transition-colors"
        >
          <ArrowLeft className="w-5 h-5" />
          <span>Volver a la lista</span>
        </button>

        <div className="flex items-center gap-2">
          {onIrACalificar && (
            <button
              onClick={onIrACalificar}
              className="px-4 py-2 rounded-lg bg-primary text-white hover:bg-primary/90 transition-colors flex items-center gap-2"
            >
              <Award className="w-4 h-4" />
              <span>Calificar Tarea</span>
            </button>
          )}
          {onEditar && (
            <button
              onClick={() => onEditar(tarea)}
              className="px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-zinc-800 transition-colors flex items-center gap-2"
            >
              <Edit className="w-4 h-4" />
              <span>Editar</span>
            </button>
          )}
          {onEliminar && (
            <button
              onClick={() => onEliminar(tareaId)}
              className="px-4 py-2 rounded-lg border border-red-300 dark:border-red-600 text-red-700 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-900/20 transition-colors flex items-center gap-2"
            >
              <Trash2 className="w-4 h-4" />
              <span>Eliminar</span>
            </button>
          )}
        </div>
      </div>

      {/* Información principal */}
      <TareaInfoSection tarea={tarea} />

      {/* Métricas */}
      <MetricasSection tarea={tarea} />

      {/* Entregas */}
      <EntregasSection
        entregas={entregas}
        onCalificar={onCalificarEntrega}
      />
    </div>
  );
}
