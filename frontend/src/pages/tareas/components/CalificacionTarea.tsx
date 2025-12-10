import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Star, AlertCircle, CheckCircle, Sparkles } from 'lucide-react';

// ====================================
// TIPOS
// ====================================

export interface CriterioRubrica {
  id: string;
  nombre: string;
  descripcion: string;
  puntosMaximos: number;
  pesoEvaluacion: number; // 0-1 (porcentaje)
}

export interface CalificacionData {
  puntuacion: number;
  comentario: string;
  criterios: Record<string, number>; // criterio_id: puntos
  retroalimentacionIA?: string;
  usarRetroalimentacionIA: boolean;
}

interface CalificacionTareaProps {
  tareaId: string;
  puntosMaximos: number;
  criterios?: CriterioRubrica[];
  usuarioId: string;
  esProfesor: boolean;
  calificacionActual?: CalificacionData;
  onCalificar: (data: CalificacionData) => Promise<void>;
  onGenerarRetroalimentacionIA?: () => Promise<string>;
  loading?: boolean;
}

// ====================================
// COMPONENTE
// ====================================

export const CalificacionTarea: React.FC<CalificacionTareaProps> = ({
  tareaId,
  puntosMaximos,
  criterios = [],
  usuarioId,
  esProfesor,
  calificacionActual,
  onCalificar,
  onGenerarRetroalimentacionIA,
  loading = false,
}) => {
  const [puntuacion, setPuntuacion] = useState(calificacionActual?.puntuacion ?? 0);
  const [comentario, setComentario] = useState(calificacionActual?.comentario ?? '');
  const [criteriosCalificados, setCriteriosCalificados] = useState<Record<string, number>>(
    calificacionActual?.criterios ?? {}
  );
  const [retroalimentacionIA, setRetroalimentacionIA] = useState(
    calificacionActual?.retroalimentacionIA ?? ''
  );
  const [usarRetroalimentacionIA, setUsarRetroalimentacionIA] = useState(
    calificacionActual?.usarRetroalimentacionIA ?? false
  );
  const [generandoIA, setGenerandoIA] = useState(false);
  const [calificando, setCalificando] = useState(false);

  // Calcular puntuación total según criterios
  const puntuacionCalculada = React.useMemo(() => {
    if (criterios.length === 0) return puntuacion;
    const total = criterios.reduce((sum, c) => {
      return sum + (criteriosCalificados[c.id] ?? 0);
    }, 0);
    return total;
  }, [criterios, criteriosCalificados, puntuacion]);

  // Porcentaje de avance visual
  const porcentaje = (puntuacionCalculada / puntosMaximos) * 100;
  const colorProgreso =
    porcentaje >= 80 ? 'bg-green-500' : porcentaje >= 60 ? 'bg-yellow-500' : 'bg-red-500';

  const handleGenerarRetroalimentacion = async () => {
    if (!onGenerarRetroalimentacionIA) return;

    try {
      setGenerandoIA(true);
      const feedback = await onGenerarRetroalimentacionIA();
      setRetroalimentacionIA(feedback);
      setUsarRetroalimentacionIA(true);
    } catch (error) {
      console.error('Error generando retroalimentación IA:', error);
      alert('Error al generar retroalimentación con IA');
    } finally {
      setGenerandoIA(false);
    }
  };

  const handleCalificar = async () => {
    try {
      setCalificando(true);
      await onCalificar({
        puntuacion: puntuacionCalculada,
        comentario,
        criterios: criteriosCalificados,
        retroalimentacionIA: usarRetroalimentacionIA ? retroalimentacionIA : undefined,
        usarRetroalimentacionIA,
      });
    } catch (error) {
      console.error('Error calificando:', error);
      alert('Error al guardar la calificación');
    } finally {
      setCalificando(false);
    }
  };

  if (!esProfesor) {
    return (
      <div className="bg-slate-50 dark:bg-slate-700/50 rounded-lg p-6 border border-slate-200 dark:border-slate-600">
        <p className="text-slate-600 dark:text-slate-300">
          Solo los profesores pueden calificar tareas.
        </p>
      </div>
    );
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="space-y-6 bg-white dark:bg-slate-800 rounded-lg p-6 border border-slate-200 dark:border-slate-700"
    >
      {/* Título */}
      <div>
        <h3 className="text-lg font-bold text-slate-900 dark:text-white mb-2">
          Calificación
        </h3>
        <p className="text-sm text-slate-600 dark:text-slate-400">
          Puntaje máximo: {puntosMaximos} puntos
        </p>
      </div>

      {/* Visualización de puntuación */}
      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <span className="text-sm font-semibold text-slate-700 dark:text-slate-300">
            Puntuación Total
          </span>
          <span className="text-2xl font-bold text-slate-900 dark:text-white">
            {puntuacionCalculada.toFixed(1)} / {puntosMaximos}
          </span>
        </div>

        {/* Barra de progreso */}
        <div className="w-full bg-slate-200 dark:bg-slate-700 rounded-full h-3 overflow-hidden">
          <motion.div
            initial={{ width: 0 }}
            animate={{ width: `${Math.min(porcentaje, 100)}%` }}
            transition={{ duration: 0.5 }}
            className={`h-full ${colorProgreso}`}
          />
        </div>

        {/* Indicador de aprobación */}
        <div className="flex items-center gap-2">
          {porcentaje >= 60 ? (
            <>
              <CheckCircle size={18} className="text-green-600 dark:text-green-400" />
              <span className="text-sm text-green-600 dark:text-green-400">Aprobado</span>
            </>
          ) : (
            <>
              <AlertCircle size={18} className="text-red-600 dark:text-red-400" />
              <span className="text-sm text-red-600 dark:text-red-400">No aprobado</span>
            </>
          )}
        </div>
      </div>

      {/* Criterios de evaluación (si existen) */}
      {criterios.length > 0 && (
        <div className="border-t border-slate-200 dark:border-slate-700 pt-6">
          <h4 className="font-semibold text-slate-900 dark:text-white mb-4">
            Criterios de Evaluación
          </h4>

          <div className="space-y-4">
            {criterios.map((criterio) => (
              <motion.div
                key={criterio.id}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                className="p-4 bg-slate-50 dark:bg-slate-700/50 rounded-lg border border-slate-200 dark:border-slate-600"
              >
                <div className="flex items-start justify-between mb-3">
                  <div>
                    <p className="font-medium text-slate-900 dark:text-white">
                      {criterio.nombre}
                    </p>
                    <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
                      {criterio.descripcion}
                    </p>
                  </div>
                  <span className="text-xs font-bold px-2 py-1 bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300 rounded">
                    Peso: {(criterio.pesoEvaluacion * 100).toFixed(0)}%
                  </span>
                </div>

                {/* Input de puntos */}
                <div className="flex items-center gap-3">
                  <input
                    type="range"
                    min="0"
                    max={criterio.puntosMaximos}
                    step="0.5"
                    value={criteriosCalificados[criterio.id] ?? 0}
                    onChange={(e) =>
                      setCriteriosCalificados({
                        ...criteriosCalificados,
                        [criterio.id]: parseFloat(e.target.value),
                      })
                    }
                    className="flex-1 cursor-pointer"
                    disabled={loading || calificando}
                  />
                  <div className="w-16 flex items-center justify-center">
                    <input
                      type="number"
                      min="0"
                      max={criterio.puntosMaximos}
                      step="0.5"
                      value={(criteriosCalificados[criterio.id] ?? 0).toFixed(1)}
                      onChange={(e) =>
                        setCriteriosCalificados({
                          ...criteriosCalificados,
                          [criterio.id]: Math.min(
                            parseFloat(e.target.value) || 0,
                            criterio.puntosMaximos
                          ),
                        })
                      }
                      className="w-full px-2 py-1 border border-slate-300 dark:border-slate-600 rounded text-center bg-white dark:bg-slate-700 text-slate-900 dark:text-white"
                      disabled={loading || calificando}
                    />
                    <span className="text-xs text-slate-500 ml-1">/{criterio.puntosMaximos}</span>
                  </div>
                </div>

                {/* Barra mini */}
                <div className="mt-2 h-1 bg-slate-200 dark:bg-slate-600 rounded-full overflow-hidden">
                  <motion.div
                    initial={{ width: 0 }}
                    animate={{
                      width: `${
                        ((criteriosCalificados[criterio.id] ?? 0) / criterio.puntosMaximos) * 100
                      }%`,
                    }}
                    className="h-full bg-blue-500"
                  />
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      )}

      {/* Comentario */}
      <div className="border-t border-slate-200 dark:border-slate-700 pt-6">
        <label className="block text-sm font-semibold text-slate-900 dark:text-white mb-3">
          Comentarios y Retroalimentación
        </label>
        <textarea
          value={comentario}
          onChange={(e) => setComentario(e.target.value)}
          placeholder="Escribe tus comentarios sobre la entrega..."
          className="w-full p-3 border border-slate-200 dark:border-slate-600 rounded-lg resize-none focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-slate-700 dark:text-white"
          rows={3}
          disabled={loading || calificando}
        />
      </div>

      {/* Retroalimentación IA */}
      {onGenerarRetroalimentacionIA && (
        <div className="border-t border-slate-200 dark:border-slate-700 pt-6">
          <div className="flex items-center gap-3 mb-4">
            <Sparkles size={20} className="text-purple-600 dark:text-purple-400" />
            <h4 className="font-semibold text-slate-900 dark:text-white">
              Retroalimentación Inteligente (IA)
            </h4>
          </div>

          {retroalimentacionIA ? (
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              className="p-4 bg-purple-50 dark:bg-purple-900/20 rounded-lg border-l-4 border-purple-500 mb-3"
            >
              <p className="text-sm text-slate-700 dark:text-slate-300 whitespace-pre-wrap">
                {retroalimentacionIA}
              </p>
            </motion.div>
          ) : null}

          <button
            onClick={handleGenerarRetroalimentacion}
            disabled={generandoIA || loading || calificando}
            className="w-full px-4 py-3 bg-purple-600 hover:bg-purple-700 disabled:opacity-50 disabled:cursor-not-allowed text-white rounded-lg transition-colors flex items-center justify-center gap-2 font-medium"
          >
            <Sparkles size={18} />
            {generandoIA ? 'Generando...' : 'Generar Retroalimentación con IA'}
          </button>

          {retroalimentacionIA && (
            <div className="mt-3 flex items-center gap-2">
              <input
                type="checkbox"
                id="usar-ia"
                checked={usarRetroalimentacionIA}
                onChange={(e) => setUsarRetroalimentacionIA(e.target.checked)}
                disabled={loading || calificando}
              />
              <label htmlFor="usar-ia" className="text-sm text-slate-700 dark:text-slate-300">
                Incluir esta retroalimentación en la calificación
              </label>
            </div>
          )}
        </div>
      )}

      {/* Botones de acción */}
      <div className="border-t border-slate-200 dark:border-slate-700 pt-6 flex gap-3">
        <button
          onClick={handleCalificar}
          disabled={loading || calificando || generandoIA}
          className="flex-1 px-6 py-3 bg-emerald-600 hover:bg-emerald-700 disabled:opacity-50 disabled:cursor-not-allowed text-white rounded-lg transition-colors font-semibold"
        >
          {calificando ? 'Guardando...' : 'Guardar Calificación'}
        </button>
      </div>
    </motion.div>
  );
};
