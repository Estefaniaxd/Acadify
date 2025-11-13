import { Clock, FileText, Users, Award, AlertCircle, CheckCircle2, XCircle, Calendar } from 'lucide-react';
import { TareaEnriquecida, EstadoVisualizacion } from '../types';

interface TareaCardProps {
  tarea: TareaEnriquecida;
  onClick?: () => void;
}

/**
 * Componente para mostrar una tarjeta de tarea con toda la información visual
 * Usa el sistema de tareas enriquecidas con colores, iconos y métricas
 */
export default function TareaCard({ tarea, onClick }: TareaCardProps) {
  // Función para obtener el ícono del estado
  const getEstadoIcon = () => {
    const iconos = {
      [EstadoVisualizacion.PENDIENTE]: <FileText className="w-5 h-5" />,
      [EstadoVisualizacion.PROXIMA_A_VENCER]: <AlertCircle className="w-5 h-5" />,
      [EstadoVisualizacion.VENCIDA]: <XCircle className="w-5 h-5" />,
      [EstadoVisualizacion.ENTREGADA]: <CheckCircle2 className="w-5 h-5" />,
      [EstadoVisualizacion.CALIFICADA]: <CheckCircle2 className="w-5 h-5" />,
      [EstadoVisualizacion.CERRADA]: <XCircle className="w-5 h-5" />,
    };
    return iconos[tarea.estado_visual] || iconos[EstadoVisualizacion.PENDIENTE];
  };

  // Función para obtener el color del badge del estado
  const getEstadoColor = () => {
    const colores = {
      [EstadoVisualizacion.PENDIENTE]: 'bg-gray-100 text-gray-700 dark:bg-gray-800 dark:text-gray-300',
      [EstadoVisualizacion.PROXIMA_A_VENCER]: 'bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-400',
      [EstadoVisualizacion.VENCIDA]: 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400',
      [EstadoVisualizacion.ENTREGADA]: 'bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400',
      [EstadoVisualizacion.CALIFICADA]: 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400',
      [EstadoVisualizacion.CERRADA]: 'bg-gray-100 text-gray-600 dark:bg-gray-800 dark:text-gray-400',
    };
    return colores[tarea.estado_visual] || colores[EstadoVisualizacion.PENDIENTE];
  };

  // Función para obtener el color del borde según urgencia
  const getBorderColor = () => {
    if (tarea.tiempo_restante?.es_muy_urgente) {
      return 'border-l-4 border-red-500';
    }
    if (tarea.tiempo_restante?.es_urgente) {
      return 'border-l-4 border-yellow-500';
    }
    return 'border-l-4 border-gray-200 dark:border-gray-700';
  };

  return (
    <div
      onClick={onClick}
      className={`${getBorderColor()} p-5 rounded-lg bg-white dark:bg-zinc-900 shadow-sm hover:shadow-md transition-all duration-200 cursor-pointer border border-gray-200 dark:border-gray-700 group`}
    >
      {/* Header con título y estado */}
      <div className="flex items-start justify-between mb-3">
        <div className="flex-1">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 group-hover:text-primary transition-colors">
            {tarea.titulo}
          </h3>
          {tarea.descripcion && (
            <p className="text-sm text-gray-600 dark:text-gray-400 mt-1 line-clamp-2">
              {tarea.descripcion}
            </p>
          )}
        </div>
        
        {/* Badge de estado */}
        <div className={`flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-semibold ${getEstadoColor()}`}>
          {getEstadoIcon()}
          <span>{tarea.info_estado.texto}</span>
        </div>
      </div>

      {/* Información principal */}
      <div className="grid grid-cols-2 gap-3 mb-3">
        {/* Fecha límite */}
        <div className="flex items-center gap-2 text-sm text-gray-600 dark:text-gray-400">
          <Calendar className="w-4 h-4" />
          <div>
            <div className="text-xs text-gray-500 dark:text-gray-500">Fecha límite</div>
            <div className="font-medium">
              {new Date(tarea.fecha_limite).toLocaleDateString('es-ES', { 
                day: '2-digit', 
                month: 'short',
                hour: '2-digit',
                minute: '2-digit'
              })}
            </div>
          </div>
        </div>

        {/* Tiempo restante */}
        {tarea.tiempo_restante && (
          <div className="flex items-center gap-2 text-sm text-gray-600 dark:text-gray-400">
            <Clock className="w-4 h-4" />
            <div>
              <div className="text-xs text-gray-500 dark:text-gray-500">Tiempo restante</div>
              <div className={`font-medium ${
                tarea.tiempo_restante.es_muy_urgente ? 'text-red-600 dark:text-red-400' :
                tarea.tiempo_restante.es_urgente ? 'text-yellow-600 dark:text-yellow-400' :
                'text-gray-700 dark:text-gray-300'
              }`}>
                {tarea.tiempo_restante.mensaje_tiempo}
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Métricas y estadísticas */}
      <div className="flex items-center gap-4 pt-3 border-t border-gray-100 dark:border-gray-800">
        {/* Puntos */}
        <div className="flex items-center gap-1.5 text-sm">
          <Award className="w-4 h-4 text-amber-500" />
          <span className="font-semibold text-gray-900 dark:text-gray-100">{tarea.puntuacion_maxima}</span>
          <span className="text-gray-500 dark:text-gray-400">pts</span>
        </div>

        {/* Entregas */}
        <div className="flex items-center gap-1.5 text-sm">
          <Users className="w-4 h-4 text-blue-500" />
          <span className="font-semibold text-gray-900 dark:text-gray-100">
            {tarea.metricas.entregas_realizadas}/{tarea.metricas.total_estudiantes}
          </span>
          <span className="text-gray-500 dark:text-gray-400">entregas</span>
        </div>

        {/* Progreso visual */}
        <div className="flex-1 ml-auto">
          <div className="flex items-center gap-2">
            <div className="flex-1 bg-gray-200 dark:bg-gray-700 rounded-full h-2 overflow-hidden">
              <div
                className="bg-primary h-full transition-all duration-300"
                style={{ width: `${tarea.metricas.porcentaje_completitud}%` }}
              />
            </div>
            <span className="text-xs font-semibold text-gray-600 dark:text-gray-400 min-w-[3rem] text-right">
              {Math.round(tarea.metricas.porcentaje_completitud)}%
            </span>
          </div>
        </div>
      </div>

      {/* Badges de tipo y prioridad */}
      <div className="flex items-center gap-2 mt-3">
        {/* Tipo */}
        <span className="px-2 py-1 rounded text-xs font-medium bg-primary/10 text-primary">
          {tarea.tipo}
        </span>
        
        {/* Prioridad */}
        {tarea.prioridad === 'alta' && (
          <span className="px-2 py-1 rounded text-xs font-medium bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400">
            Prioridad Alta
          </span>
        )}

        {/* IA habilitada */}
        {tarea.habilitar_retroalimentacion_ia && (
          <span className="px-2 py-1 rounded text-xs font-medium bg-purple-100 text-purple-700 dark:bg-purple-900/30 dark:text-purple-400">
            🤖 IA
          </span>
        )}
      </div>
    </div>
  );
}
