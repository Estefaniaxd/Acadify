import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Upload, CheckCircle2, AlertCircle, Clock, FileText, MessageSquare, Lightbulb } from 'lucide-react';
import { iaService, RetroalimentacionResponse } from '@/services/iaService';

interface EntregaTareaProps {
  entregaId: string;
  tareaId: string;
  titulo: string;
  descripcion?: string;
  fechaLimite?: string;
  archivosEntregados?: string[];
  estado: 'no_iniciada' | 'en_proceso' | 'completada' | 'retroalimentada' | 'rechazada';
  calificacion?: number;
  calificacionMaxima?: number;
  retroalimentacionDocente?: string;
  onArchivoSeleccionado?: (archivo: File) => void;
  onEnvio?: () => void;
}

/**
 * 📝 EntregaTarea - Interfaz de entrega de tareas para estudiantes
 * 
 * Características:
 * - Visualización de tarea asignada
 * - Carga de archivos
 * - Visor de retroalimentación IA
 * - Visor de calificación y feedback docente
 * - Estado visual de la entrega
 */
export const EntregaTarea: React.FC<EntregaTareaProps> = ({
  entregaId,
  tareaId,
  titulo,
  descripcion,
  fechaLimite,
  archivosEntregados = [],
  estado = 'no_iniciada',
  calificacion,
  calificacionMaxima = 5,
  retroalimentacionDocente,
  onArchivoSeleccionado,
  onEnvio,
}) => {
  const [retroalimentacionIA, setRetroalimentacionIA] = useState<RetroalimentacionResponse | null>(null);
  const [cargando, setCargando] = useState(false);
  const [mostrarRetroalimentacion, setMostrarRetroalimentacion] = useState(false);

  // Cargar retroalimentación al montar
  useEffect(() => {
    cargarRetroalimentacion();
  }, [entregaId]);

  const cargarRetroalimentacion = async () => {
    try {
      setCargando(true);
      const resultado = await iaService.obtenerRetroalimentacion(entregaId);
      if (resultado) {
        setRetroalimentacionIA(resultado);
        setMostrarRetroalimentacion(true);
      }
    } catch (err) {
      console.error('Error cargando retroalimentación:', err);
    } finally {
      setCargando(false);
    }
  };

  // Determinar color y ícono del estado
  const getEstadoConfig = () => {
    const configs = {
      no_iniciada: {
        color: 'bg-gray-50 border-gray-200',
        textColor: 'text-gray-600',
        badgeColor: 'bg-gray-100 text-gray-700',
        icon: AlertCircle,
        label: 'No iniciada',
      },
      en_proceso: {
        color: 'bg-blue-50 border-blue-200',
        textColor: 'text-blue-600',
        badgeColor: 'bg-blue-100 text-blue-700',
        icon: Clock,
        label: 'En proceso',
      },
      completada: {
        color: 'bg-purple-50 border-purple-200',
        textColor: 'text-purple-600',
        badgeColor: 'bg-purple-100 text-purple-700',
        icon: CheckCircle2,
        label: 'Completada',
      },
      retroalimentada: {
        color: 'bg-green-50 border-green-200',
        textColor: 'text-green-600',
        badgeColor: 'bg-green-100 text-green-700',
        icon: Lightbulb,
        label: 'Con retroalimentación',
      },
      rechazada: {
        color: 'bg-red-50 border-red-200',
        textColor: 'text-red-600',
        badgeColor: 'bg-red-100 text-red-700',
        icon: AlertCircle,
        label: 'Rechazada',
      },
    };
    return configs[estado] || configs.no_iniciada;
  };

  const estadoConfig = getEstadoConfig();
  const EstadoIcon = estadoConfig.icon;

  // Calcular si está vencida
  const estaVencida =
    fechaLimite && new Date(fechaLimite) < new Date() && estado !== 'completada' && estado !== 'retroalimentada';

  return (
    <div className={`w-full rounded-lg border-2 ${estadoConfig.color} space-y-6 p-6`}>
      {/* Header */}
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <div className="flex items-center gap-3 mb-2">
            <EstadoIcon size={20} className={estadoConfig.textColor} />
            <h2 className="text-2xl font-bold text-gray-800">{titulo}</h2>
          </div>

          <div className={`inline-flex items-center gap-2 px-3 py-1 rounded-full text-sm font-medium ${estadoConfig.badgeColor}`}>
            <span className="w-2 h-2 bg-current rounded-full"></span>
            {estadoConfig.label}
          </div>

          {estaVencida && (
            <div className="text-sm text-red-600 font-medium mt-2 flex items-center gap-1">
              <AlertCircle size={16} />
              ⏰ Plazo vencido
            </div>
          )}
        </div>

        {calificacion !== undefined && (
          <motion.div
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            className="text-center"
          >
            <div className="text-3xl font-bold text-blue-600">
              {calificacion.toFixed(1)}
            </div>
            <div className="text-xs text-gray-600">/{calificacionMaxima}</div>
          </motion.div>
        )}
      </div>

      {/* Descripción */}
      {descripcion && (
        <div className="p-4 bg-white bg-opacity-50 rounded-lg border border-gray-200">
          <p className="text-gray-700 whitespace-pre-wrap text-sm leading-relaxed">{descripcion}</p>
        </div>
      )}

      {/* Metadata */}
      <div className="grid grid-cols-3 gap-4 text-sm">
        <div className="p-3 bg-white bg-opacity-50 rounded-lg border border-gray-200">
          <p className="text-gray-600 font-medium">ID Entrega</p>
          <code className="text-xs bg-gray-100 px-2 py-1 rounded mt-1 block">{entregaId}</code>
        </div>

        <div className="p-3 bg-white bg-opacity-50 rounded-lg border border-gray-200">
          <p className="text-gray-600 font-medium">ID Tarea</p>
          <code className="text-xs bg-gray-100 px-2 py-1 rounded mt-1 block">{tareaId}</code>
        </div>

        {fechaLimite && (
          <div className="p-3 bg-white bg-opacity-50 rounded-lg border border-gray-200">
            <p className="text-gray-600 font-medium">Fecha Límite</p>
            <p className="text-xs mt-1">{new Date(fechaLimite).toLocaleDateString()}</p>
          </div>
        )}
      </div>

      {/* Archivos Entregados */}
      <div className="space-y-3">
        <h3 className="font-semibold text-gray-800 flex items-center gap-2">
          <FileText size={18} />
          Archivos Entregados ({archivosEntregados.length})
        </h3>

        {archivosEntregados.length > 0 ? (
          <div className="space-y-2">
            {archivosEntregados.map((archivo, idx) => (
              <motion.div
                key={idx}
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
                className="flex items-center gap-3 p-3 bg-white rounded-lg border border-gray-200 hover:border-blue-300 transition-colors"
              >
                <FileText size={16} className="text-blue-500" />
                <span className="flex-1 text-sm font-medium text-gray-700 truncate">{archivo}</span>
                <CheckCircle2 size={16} className="text-green-500" />
              </motion.div>
            ))}
          </div>
        ) : (
          <div className="p-4 bg-gray-100 rounded-lg text-center text-gray-600 text-sm">
            📭 No hay archivos entregados aún
          </div>
        )}

        {/* Upload Zone */}
        <div className="mt-4 p-6 border-2 border-dashed border-gray-300 rounded-lg text-center hover:border-blue-400 transition-colors cursor-pointer bg-white bg-opacity-50">
          <Upload size={24} className="mx-auto text-gray-400 mb-2" />
          <p className="text-sm font-medium text-gray-700">Selecciona archivos para entregar</p>
          <p className="text-xs text-gray-600 mt-1">Máximo 50MB por archivo</p>
          <input
            type="file"
            multiple
            onChange={(e) => {
              if (e.target.files?.[0]) {
                onArchivoSeleccionado?.(e.target.files[0]);
              }
            }}
            className="hidden"
          />
        </div>
      </div>

      {/* Retroalimentación IA */}
      {mostrarRetroalimentacion && retroalimentacionIA?.retroalimentacion && (
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          className="p-5 bg-purple-50 border border-purple-300 rounded-lg space-y-4"
        >
          <div className="flex items-center gap-2">
            <Lightbulb size={20} className="text-purple-600" />
            <h4 className="font-bold text-purple-900">💡 Retroalimentación IA</h4>
            <span className="text-xs bg-purple-200 text-purple-700 px-2 py-1 rounded ml-auto">
              {retroalimentacionIA.retroalimentacion.modelo_usado}
            </span>
          </div>

          {/* Retroalimentación Principal */}
          <div className="space-y-2">
            <p className="text-sm font-medium text-purple-900">Análisis General:</p>
            <p className="text-sm text-gray-700 bg-white p-3 rounded border border-purple-100 whitespace-pre-wrap">
              {retroalimentacionIA.retroalimentacion.retroalimentacion_texto}
            </p>
          </div>

          {/* Fortalezas */}
          {retroalimentacionIA.retroalimentacion.fortalezas?.length > 0 && (
            <div className="space-y-2">
              <p className="text-sm font-medium text-green-700">✅ Tus Fortalezas:</p>
              <ul className="space-y-1">
                {retroalimentacionIA.retroalimentacion.fortalezas.slice(0, 3).map((f, i) => (
                  <li key={i} className="text-sm text-gray-700 flex items-start gap-2">
                    <span className="text-green-600">✓</span>
                    <span>{f}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Áreas de Mejora */}
          {retroalimentacionIA.retroalimentacion.areas_mejora?.length > 0 && (
            <div className="space-y-2">
              <p className="text-sm font-medium text-orange-700">🎯 Áreas para Mejorar:</p>
              <ul className="space-y-1">
                {retroalimentacionIA.retroalimentacion.areas_mejora.slice(0, 3).map((a, i) => (
                  <li key={i} className="text-sm text-gray-700 flex items-start gap-2">
                    <span className="text-orange-600">→</span>
                    <span>{a}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Recursos Recomendados */}
          {retroalimentacionIA.retroalimentacion.recursos_recomendados?.length > 0 && (
            <div className="space-y-2">
              <p className="text-sm font-medium text-blue-700">📚 Recursos Recomendados:</p>
              <ul className="space-y-1">
                {retroalimentacionIA.retroalimentacion.recursos_recomendados.slice(0, 2).map((r, i) => (
                  <li key={i} className="text-sm text-gray-700 flex items-start gap-2">
                    <span className="text-blue-600">📖</span>
                    <span>{r}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Calificación Sugerida */}
          {retroalimentacionIA.retroalimentacion.calificacion_sugerida && (
            <div className="p-3 bg-blue-50 border border-blue-200 rounded-lg">
              <p className="text-sm font-medium text-blue-900">
                Calificación Sugerida: <span className="text-xl font-bold">{retroalimentacionIA.retroalimentacion.calificacion_sugerida.toFixed(1)}/5.0</span>
              </p>
            </div>
          )}
        </motion.div>
      )}

      {/* Retroalimentación Docente */}
      {retroalimentacionDocente && (
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          className="p-5 bg-blue-50 border border-blue-300 rounded-lg space-y-3"
        >
          <div className="flex items-center gap-2">
            <MessageSquare size={20} className="text-blue-600" />
            <h4 className="font-bold text-blue-900">📝 Feedback del Docente</h4>
          </div>

          <div className="text-sm text-gray-700 bg-white p-4 rounded border border-blue-100 whitespace-pre-wrap">
            {retroalimentacionDocente}
          </div>
        </motion.div>
      )}

      {/* Actions */}
      {estado !== 'completada' && estado !== 'retroalimentada' && (
        <motion.button
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
          onClick={onEnvio}
          className="w-full py-3 px-4 bg-blue-600 text-white font-semibold rounded-lg hover:bg-blue-700 transition-colors flex items-center justify-center gap-2"
        >
          <Upload size={18} />
          Entregar Tarea
        </motion.button>
      )}

      {/* Cargando */}
      {cargando && (
        <div className="text-center py-4 text-gray-600 text-sm">
          ⏳ Cargando retroalimentación...
        </div>
      )}
    </div>
  );
};

export default EntregaTarea;
