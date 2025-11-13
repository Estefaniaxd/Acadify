/**
 * CalificarEntregaModal Component
 * 
 * Modal para calificar entregas de estudiantes con soporte de IA.
 * Implementa retroalimentación automática con Rutilio.
 * 
 * Principios SOLID aplicados:
 * - Single Responsibility: Solo maneja la calificación de una entrega
 * - Open/Closed: Extensible mediante props de callbacks
 * - Dependency Inversion: Depende de abstracciones (props callbacks)
 */

import { useState } from 'react';
import { 
  X, 
  Loader2, 
  Sparkles, 
  Award, 
  MessageSquare,
  FileText,
  Download,
  AlertCircle,
  CheckCircle2,
  TrendingUp,
  Zap
} from 'lucide-react';
import { EntregaTarea, CalificacionResponse } from '../types';
import { apiClientTareas } from '../api';

interface CalificarEntregaModalProps {
  entrega: EntregaTarea;
  puntos_maximos: number;
  onClose: () => void;
  onCalificacionGuardada: (response: CalificacionResponse) => void;
}

/**
 * Hook para manejar el estado de la calificación
 * Separación de concerns: Lógica de estado separada del componente visual
 */
const useCalificacionState = (entrega: EntregaTarea) => {
  const [calificacion, setCalificacion] = useState<number>(entrega.calificacion || 0);
  const [comentarios, setComentarios] = useState<string>(entrega.comentarios_docente || '');
  const [generandoIA, setGenerandoIA] = useState(false);
  const [guardando, setGuardando] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [retroalimentacionIA, setRetroalimentacionIA] = useState<string | null>(null);

  return {
    calificacion,
    setCalificacion,
    comentarios,
    setComentarios,
    generandoIA,
    setGenerandoIA,
    guardando,
    setGuardando,
    error,
    setError,
    retroalimentacionIA,
    setRetroalimentacionIA
  };
};

/**
 * Componente para mostrar la información de la entrega
 * Single Responsibility: Solo muestra datos de la entrega
 */
const EntregaInfoSection = ({ entrega }: { entrega: EntregaTarea }) => {
  return (
    <div className="bg-gray-50 dark:bg-zinc-800/50 rounded-lg p-4 mb-6">
      <div className="flex items-start gap-3 mb-3">
        <div className="p-2 rounded-lg bg-blue-100 dark:bg-blue-900/30">
          <FileText className="w-5 h-5 text-blue-600 dark:text-blue-400" />
        </div>
        <div className="flex-1">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100">
            Entrega de {entrega.estudiante_nombre || 'Estudiante'}
          </h3>
          <div className="text-sm text-gray-600 dark:text-gray-400 mt-1">
            Entregado: {new Date(entrega.fecha_entrega || '').toLocaleString('es-ES')}
          </div>
          {entrega.es_entrega_tardia && (
            <div className="flex items-center gap-1 mt-1 text-red-600 dark:text-red-400 text-sm">
              <AlertCircle className="w-4 h-4" />
              <span>Entrega tardía</span>
            </div>
          )}
        </div>
      </div>

      {/* Contenido de la entrega */}
      {entrega.contenido_texto && (
        <div className="mt-4">
          <div className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Contenido:
          </div>
          <div className="bg-white dark:bg-zinc-900 rounded-lg p-4 border border-gray-200 dark:border-gray-700 max-h-48 overflow-y-auto">
            <p className="text-gray-700 dark:text-gray-300 whitespace-pre-wrap text-sm">
              {entrega.contenido_texto}
            </p>
          </div>
        </div>
      )}

      {/* Archivos adjuntos */}
      {entrega.archivo_url && (
        <div className="mt-4">
          <div className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Archivos adjuntos:
          </div>
          <button className="flex items-center gap-2 px-3 py-2 rounded-lg bg-white dark:bg-zinc-900 border border-gray-200 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-zinc-800 transition-colors text-sm">
            <Download className="w-4 h-4" />
            <span>Descargar archivo</span>
          </button>
        </div>
      )}
    </div>
  );
};

/**
 * Componente para el formulario de calificación
 * Single Responsibility: Solo maneja la entrada de datos
 */
const CalificacionFormSection = ({
  calificacion,
  puntosMaximos,
  comentarios,
  onCalificacionChange,
  onComentariosChange,
  onGenerarIA,
  generandoIA,
  retroalimentacionIA
}: {
  calificacion: number;
  puntosMaximos: number;
  comentarios: string;
  onCalificacionChange: (value: number) => void;
  onComentariosChange: (value: string) => void;
  onGenerarIA: () => void;
  generandoIA: boolean;
  retroalimentacionIA: string | null;
}) => {
  // Calcular porcentaje y color
  const porcentaje = (calificacion / puntosMaximos) * 100;
  const getColorPorcentaje = () => {
    if (porcentaje >= 90) return 'text-green-600 dark:text-green-400';
    if (porcentaje >= 70) return 'text-blue-600 dark:text-blue-400';
    if (porcentaje >= 50) return 'text-yellow-600 dark:text-yellow-400';
    return 'text-red-600 dark:text-red-400';
  };

  return (
    <div className="space-y-5">
      {/* Calificación numérica */}
      <div>
        <div className="flex items-center justify-between mb-3">
          <label className="text-sm font-medium text-gray-700 dark:text-gray-300">
            Calificación <span className="text-red-500">*</span>
          </label>
          <div className={`text-2xl font-bold ${getColorPorcentaje()}`}>
            {calificacion} / {puntosMaximos}
          </div>
        </div>
        
        {/* Slider */}
        <input
          type="range"
          min="0"
          max={puntosMaximos}
          step="1"
          value={calificacion}
          onChange={(e) => onCalificacionChange(Number(e.target.value))}
          className="w-full h-2 bg-gray-200 dark:bg-gray-700 rounded-lg appearance-none cursor-pointer slider-thumb"
        />
        
        {/* Indicador de porcentaje */}
        <div className="flex items-center justify-between mt-2 text-xs text-gray-500 dark:text-gray-400">
          <span>0</span>
          <span className={`font-semibold ${getColorPorcentaje()}`}>
            {Math.round(porcentaje)}%
          </span>
          <span>{puntosMaximos}</span>
        </div>

        {/* Entrada directa */}
        <div className="mt-3 flex items-center gap-2">
          <label className="text-sm text-gray-600 dark:text-gray-400">
            O ingresa directamente:
          </label>
          <input
            type="number"
            min="0"
            max={puntosMaximos}
            value={calificacion}
            onChange={(e) => onCalificacionChange(Math.min(puntosMaximos, Math.max(0, Number(e.target.value))))}
            className="w-24 px-3 py-1.5 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-zinc-800 text-gray-900 dark:text-gray-100 text-center font-semibold"
          />
        </div>
      </div>

      {/* Retroalimentación con IA */}
      <div>
        <div className="flex items-center justify-between mb-2">
          <label className="text-sm font-medium text-gray-700 dark:text-gray-300 flex items-center gap-2">
            <MessageSquare className="w-4 h-4" />
            Comentarios y Retroalimentación
          </label>
          <button
            type="button"
            onClick={onGenerarIA}
            disabled={generandoIA}
            className="px-3 py-1.5 rounded-lg bg-gradient-to-r from-purple-500 to-pink-500 text-white hover:from-purple-600 hover:to-pink-600 transition-all disabled:opacity-50 flex items-center gap-2 text-sm font-medium"
          >
            {generandoIA ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin" />
                <span>Generando...</span>
              </>
            ) : (
              <>
                <Sparkles className="w-4 h-4" />
                <span>Generar con IA</span>
              </>
            )}
          </button>
        </div>

        {/* Retroalimentación de IA generada */}
        {retroalimentacionIA && (
          <div className="mb-3 p-4 rounded-lg bg-gradient-to-r from-purple-50 to-pink-50 dark:from-purple-900/20 dark:to-pink-900/20 border border-purple-200 dark:border-purple-700">
            <div className="flex items-start gap-2 mb-2">
              <Sparkles className="w-4 h-4 text-purple-600 dark:text-purple-400 mt-0.5" />
              <div className="text-sm font-medium text-purple-900 dark:text-purple-300">
                Sugerencia de Rutilio (IA):
              </div>
            </div>
            <p className="text-sm text-gray-700 dark:text-gray-300 whitespace-pre-wrap">
              {retroalimentacionIA}
            </p>
            <button
              type="button"
              onClick={() => onComentariosChange(retroalimentacionIA)}
              className="mt-2 text-xs text-purple-600 dark:text-purple-400 hover:underline"
            >
              Usar esta retroalimentación
            </button>
          </div>
        )}

        <textarea
          value={comentarios}
          onChange={(e) => onComentariosChange(e.target.value)}
          rows={6}
          placeholder="Escribe comentarios constructivos para el estudiante..."
          className="w-full px-4 py-3 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-zinc-800 text-gray-900 dark:text-gray-100 focus:ring-2 focus:ring-primary focus:border-transparent resize-none"
        />
      </div>
    </div>
  );
};

/**
 * Componente para mostrar preview de gamificación
 * Single Responsibility: Solo muestra información de puntos
 */
const GamificacionPreview = ({ 
  calificacion, 
  puntosMaximos,
  esTardia 
}: { 
  calificacion: number;
  puntosMaximos: number;
  esTardia: boolean;
}) => {
  // Cálculo simple de puntos (el backend hace el cálculo real)
  const puntosBase = Math.round((calificacion / puntosMaximos) * 100);
  const bonoCalidad = calificacion >= puntosMaximos * 0.9 ? 20 : 0;
  const penalizacionTardia = esTardia ? -10 : 0;
  const puntosEstimados = puntosBase + bonoCalidad + penalizacionTardia;

  return (
    <div className="bg-gradient-to-r from-amber-50 to-yellow-50 dark:from-amber-900/20 dark:to-yellow-900/20 rounded-lg p-4 border border-amber-200 dark:border-amber-700">
      <div className="flex items-center gap-2 mb-3">
        <Award className="w-5 h-5 text-amber-600 dark:text-amber-400" />
        <h4 className="text-sm font-semibold text-gray-900 dark:text-gray-100">
          Vista Previa de Gamificación
        </h4>
      </div>

      <div className="space-y-2 text-sm">
        <div className="flex items-center justify-between">
          <span className="text-gray-600 dark:text-gray-400">Puntos base</span>
          <span className="font-semibold text-gray-900 dark:text-gray-100">+{puntosBase}</span>
        </div>
        {bonoCalidad > 0 && (
          <div className="flex items-center justify-between text-green-600 dark:text-green-400">
            <span className="flex items-center gap-1">
              <TrendingUp className="w-3 h-3" />
              Bono por calidad
            </span>
            <span className="font-semibold">+{bonoCalidad}</span>
          </div>
        )}
        {penalizacionTardia < 0 && (
          <div className="flex items-center justify-between text-red-600 dark:text-red-400">
            <span>Penalización por tardía</span>
            <span className="font-semibold">{penalizacionTardia}</span>
          </div>
        )}
        <div className="flex items-center justify-between pt-2 border-t border-amber-200 dark:border-amber-700 text-base font-bold">
          <span className="text-gray-900 dark:text-gray-100">Total estimado</span>
          <span className="text-amber-600 dark:text-amber-400 flex items-center gap-1">
            <Zap className="w-4 h-4" />
            {puntosEstimados} pts
          </span>
        </div>
      </div>

      <p className="mt-3 text-xs text-gray-500 dark:text-gray-400 italic">
        * Los puntos finales pueden variar según rachas y logros del estudiante
      </p>
    </div>
  );
};

/**
 * Componente principal del modal de calificación
 */
export default function CalificarEntregaModal({
  entrega,
  puntos_maximos,
  onClose,
  onCalificacionGuardada
}: CalificarEntregaModalProps) {
  const {
    calificacion,
    setCalificacion,
    comentarios,
    setComentarios,
    generandoIA,
    setGenerandoIA,
    guardando,
    setGuardando,
    error,
    setError,
    retroalimentacionIA,
    setRetroalimentacionIA
  } = useCalificacionState(entrega);

  // Generar retroalimentación con IA
  const handleGenerarIA = async () => {
    try {
      setGenerandoIA(true);
      setError(null);

      // TODO: Implementar llamada real a la API de IA
      // Simulación por ahora
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      const retroalimentacion = `Excelente trabajo en general. Has demostrado comprensión de los conceptos principales. 

Fortalezas:
- Buena estructura y organización del contenido
- Ejemplos claros y bien explicados
- Cumplimiento de los objetivos planteados

Áreas de mejora:
- Podrías profundizar más en algunos conceptos
- Considera agregar más referencias bibliográficas
- Revisa la ortografía y redacción en algunas secciones

Recomendaciones:
- Sigue practicando con ejercicios similares
- Consulta los materiales complementarios del curso
- No dudes en hacer preguntas en clase

¡Sigue así!`;

      setRetroalimentacionIA(retroalimentacion);
    } catch (err) {
      console.error('Error generando retroalimentación:', err);
      setError('Error al generar retroalimentación con IA');
    } finally {
      setGenerandoIA(false);
    }
  };

  // Guardar calificación
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (calificacion < 0 || calificacion > puntos_maximos) {
      setError(`La calificación debe estar entre 0 y ${puntos_maximos}`);
      return;
    }

    try {
      setGuardando(true);
      setError(null);

      const response = await apiClientTareas.calificarEntrega(
        entrega.entrega_id,
        {
          calificacion,
          comentarios: comentarios || undefined
        }
      );

      onCalificacionGuardada(response);
    } catch (err) {
      console.error('Error guardando calificación:', err);
      setError('Error al guardar la calificación. Por favor intenta de nuevo.');
    } finally {
      setGuardando(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4 overflow-y-auto">
      <div className="bg-white dark:bg-zinc-900 rounded-xl shadow-2xl max-w-3xl w-full my-8">
        {/* Header */}
        <div className="sticky top-0 bg-white dark:bg-zinc-900 border-b border-gray-200 dark:border-gray-700 px-6 py-4 flex items-center justify-between rounded-t-xl">
          <h2 className="text-2xl font-bold text-gray-900 dark:text-gray-100">
            Calificar Entrega
          </h2>
          <button
            onClick={onClose}
            className="p-2 hover:bg-gray-100 dark:hover:bg-zinc-800 rounded-lg transition-colors"
            disabled={guardando}
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="p-6">
          {/* Error */}
          {error && (
            <div className="mb-4 p-3 rounded-lg bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 text-red-800 dark:text-red-300 text-sm flex items-start gap-2">
              <AlertCircle className="w-4 h-4 mt-0.5 flex-shrink-0" />
              <span>{error}</span>
            </div>
          )}

          {/* Información de la entrega */}
          <EntregaInfoSection entrega={entrega} />

          {/* Formulario de calificación */}
          <CalificacionFormSection
            calificacion={calificacion}
            puntosMaximos={puntos_maximos}
            comentarios={comentarios}
            onCalificacionChange={setCalificacion}
            onComentariosChange={setComentarios}
            onGenerarIA={handleGenerarIA}
            generandoIA={generandoIA}
            retroalimentacionIA={retroalimentacionIA}
          />

          {/* Preview de gamificación */}
          <div className="mt-6">
            <GamificacionPreview
              calificacion={calificacion}
              puntosMaximos={puntos_maximos}
              esTardia={entrega.es_entrega_tardia}
            />
          </div>

          {/* Botones */}
          <div className="flex items-center gap-3 mt-6">
            <button
              type="button"
              onClick={onClose}
              disabled={guardando}
              className="flex-1 px-4 py-2.5 rounded-lg border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-zinc-800 transition-colors disabled:opacity-50 font-medium"
            >
              Cancelar
            </button>
            <button
              type="submit"
              disabled={guardando}
              className="flex-1 px-4 py-2.5 rounded-lg bg-primary text-white hover:bg-primary/90 transition-colors disabled:opacity-50 flex items-center justify-center gap-2 font-medium"
            >
              {guardando ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  <span>Guardando...</span>
                </>
              ) : (
                <>
                  <CheckCircle2 className="w-4 h-4" />
                  <span>Guardar Calificación</span>
                </>
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
