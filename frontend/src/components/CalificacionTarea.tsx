import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Loader2, Zap, AlertCircle, CheckCircle2, TrendingUp } from 'lucide-react';
import { iaService, RetroalimentacionResponse } from '@/services/iaService';

interface CalificacionTareaProps {
  entregaId: string;
  tareaId: string;
  calificacionDocente?: number;
  retroalimentacionDocente?: string;
  onCalificacionChange?: (calificacion: number) => void;
  onRetroalimentacionChange?: (text: string) => void;
  readOnly?: boolean;
}

/**
 * 🎯 CalificacionTarea - Interfaz de calificación con retroalimentación IA
 * 
 * Características:
 * - Botón ⚡ para generar retroalimentación con Gemini
 * - Visualización de retroalimentación generada
 * - Editor de calificación manual del docente
 * - Selector de modelo IA
 * - Indicador de nivel de detalle
 */
export const CalificacionTarea: React.FC<CalificacionTareaProps> = ({
  entregaId,
  tareaId,
  calificacionDocente = 0,
  retroalimentacionDocente = '',
  onCalificacionChange,
  onRetroalimentacionChange,
  readOnly = false,
}) => {
  const [calificacion, setCalificacion] = useState(calificacionDocente);
  const [feedback, setFeedback] = useState(retroalimentacionDocente);
  
  const [cargando, setCargando] = useState(false);
  const [retroalimentacionIA, setRetroalimentacionIA] = useState<RetroalimentacionResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [modelo, setModelo] = useState('gemini-2.5-flash');
  const [nivelDetalle, setNivelDetalle] = useState<'basico' | 'medio' | 'completo'>('completo');
  const [mostrarRetroalimentacion, setMostrarRetroalimentacion] = useState(false);

  // Cargar retroalimentación existente al montar
  useEffect(() => {
    cargarRetroalimentacionExistente();
  }, [entregaId]);

  const cargarRetroalimentacionExistente = async () => {
    try {
      const resultado = await iaService.obtenerRetroalimentacion(entregaId);
      if (resultado) {
        setRetroalimentacionIA(resultado);
        setMostrarRetroalimentacion(true);
      }
    } catch (err) {
      console.error('Error cargando retroalimentación:', err);
    }
  };

  const generarRetroalimentacionIA = async () => {
    if (cargando) return;

    setCargando(true);
    setError(null);

    try {
      console.log(`🚀 Generando retroalimentación IA para entrega ${entregaId}`);

      const resultado = await iaService.generarRetroalimentacionIndividual(
        entregaId,
        modelo,
        nivelDetalle,
        true
      );

      setRetroalimentacionIA(resultado);
      setMostrarRetroalimentacion(true);

      // Si tiene calificación sugerida, usarla
      if (resultado.retroalimentacion?.calificacion_sugerida) {
        setCalificacion(resultado.retroalimentacion.calificacion_sugerida);
        onCalificacionChange?.(resultado.retroalimentacion.calificacion_sugerida);
      }

      console.log('✅ Retroalimentación generada exitosamente');
    } catch (err: any) {
      const mensaje = err.response?.data?.detail || err.message || 'Error desconocido';
      setError(`❌ Error: ${mensaje}`);
      console.error('Error generando retroalimentación:', err);
    } finally {
      setCargando(false);
    }
  };

  const handleCalificacionChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const valor = parseFloat(e.target.value);
    setCalificacion(valor);
    onCalificacionChange?.(valor);
  };

  const handleFeedbackChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setFeedback(e.target.value);
    onRetroalimentacionChange?.(e.target.value);
  };

  return (
    <div className="w-full space-y-6 p-6 bg-gradient-to-br from-blue-50 to-purple-50 rounded-lg border border-blue-200">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-lg font-bold text-gray-800">Calificación y Retroalimentación</h3>
          <p className="text-sm text-gray-600 mt-1">
            Tarea ID: <code className="bg-gray-200 px-2 py-1 rounded">{tareaId}</code>
          </p>
        </div>

        {retroalimentacionIA?.retroalimentacion && (
          <motion.div
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            className="flex items-center gap-2 px-3 py-1 bg-green-100 text-green-700 rounded-full text-sm"
          >
            <CheckCircle2 size={16} />
            IA Completada
          </motion.div>
        )}
      </div>

      {/* Selector de Modelo y Nivel */}
      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Modelo IA
          </label>
          <select
            value={modelo}
            onChange={(e) => setModelo(e.target.value)}
            disabled={cargando || readOnly}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg bg-white text-gray-700 text-sm disabled:bg-gray-100 disabled:text-gray-500"
          >
            <option value="gemini-2.5-flash">⚡ Gemini 2.5 Flash (Rápido)</option>
            <option value="gemini-2.5-pro">🧠 Gemini 2.5 Pro (Preciso)</option>
            <option value="gemini-2.0-flash">💫 Gemini 2.0 Flash</option>
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Nivel de Detalle
          </label>
          <select
            value={nivelDetalle}
            onChange={(e) => setNivelDetalle(e.target.value as any)}
            disabled={cargando || readOnly}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg bg-white text-gray-700 text-sm disabled:bg-gray-100 disabled:text-gray-500"
          >
            <option value="basico">📋 Básico</option>
            <option value="medio">📊 Medio</option>
            <option value="completo">📈 Completo</option>
          </select>
        </div>
      </div>

      {/* Botón Generar Retroalimentación */}
      <motion.button
        whileHover={!cargando ? { scale: 1.02 } : {}}
        whileTap={!cargando ? { scale: 0.98 } : {}}
        onClick={generarRetroalimentacionIA}
        disabled={cargando || readOnly}
        className={`w-full flex items-center justify-center gap-2 px-4 py-3 rounded-lg font-medium transition-all ${
          cargando
            ? 'bg-blue-300 text-blue-800 cursor-wait'
            : readOnly
            ? 'bg-gray-300 text-gray-600 cursor-not-allowed'
            : 'bg-blue-600 text-white hover:bg-blue-700 active:bg-blue-800'
        }`}
      >
        {cargando ? (
          <>
            <Loader2 size={18} className="animate-spin" />
            Generando retroalimentación IA...
          </>
        ) : (
          <>
            <Zap size={18} />
            Generar Retroalimentación con IA
          </>
        )}
      </motion.button>

      {/* Error Message */}
      {error && (
        <motion.div
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          className="p-4 bg-red-50 border border-red-200 rounded-lg flex items-gap gap-3"
        >
          <AlertCircle size={20} className="text-red-500 flex-shrink-0" />
          <div className="text-sm text-red-700">{error}</div>
        </motion.div>
      )}

      {/* Retroalimentación IA */}
      {mostrarRetroalimentacion && retroalimentacionIA?.retroalimentacion && (
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          className="p-4 bg-purple-50 border border-purple-200 rounded-lg space-y-4"
        >
          <div className="flex items-center gap-2">
            <TrendingUp size={18} className="text-purple-600" />
            <h4 className="font-semibold text-purple-900">Análisis de IA</h4>
            <span className="text-xs bg-purple-200 text-purple-700 px-2 py-1 rounded">
              {retroalimentacionIA.retroalimentacion.modelo_usado}
            </span>
          </div>

          {/* Retroalimentación Texto */}
          <div className="space-y-2">
            <p className="text-sm font-medium text-gray-700">Análisis General:</p>
            <p className="text-sm text-gray-700 bg-white p-3 rounded border border-purple-100 whitespace-pre-wrap">
              {retroalimentacionIA.retroalimentacion.retroalimentacion_texto}
            </p>
          </div>

          {/* Fortalezas */}
          {retroalimentacionIA.retroalimentacion.fortalezas?.length > 0 && (
            <div className="space-y-2">
              <p className="text-sm font-medium text-green-700">✅ Fortalezas:</p>
              <ul className="space-y-1">
                {retroalimentacionIA.retroalimentacion.fortalezas.map((f, i) => (
                  <li key={i} className="text-sm text-gray-700 flex items-start gap-2">
                    <span className="text-green-600">•</span>
                    <span>{f}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Áreas de Mejora */}
          {retroalimentacionIA.retroalimentacion.areas_mejora?.length > 0 && (
            <div className="space-y-2">
              <p className="text-sm font-medium text-orange-700">⚠️ Áreas de Mejora:</p>
              <ul className="space-y-1">
                {retroalimentacionIA.retroalimentacion.areas_mejora.map((a, i) => (
                  <li key={i} className="text-sm text-gray-700 flex items-start gap-2">
                    <span className="text-orange-600">•</span>
                    <span>{a}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Calificación Sugerida */}
          {retroalimentacionIA.retroalimentacion.calificacion_sugerida && (
            <div className="p-3 bg-blue-50 border border-blue-200 rounded-lg">
              <p className="text-sm font-medium text-blue-900">Calificación Sugerida:</p>
              <p className="text-2xl font-bold text-blue-600">
                {retroalimentacionIA.retroalimentacion.calificacion_sugerida.toFixed(1)}/5.0
              </p>
              {retroalimentacionIA.retroalimentacion.razonamiento_calificacion && (
                <p className="text-sm text-blue-700 mt-2">
                  {retroalimentacionIA.retroalimentacion.razonamiento_calificacion}
                </p>
              )}
            </div>
          )}

          {/* Metadata */}
          <div className="text-xs text-gray-600 flex justify-between pt-2 border-t border-purple-200">
            <span>Tokens: {retroalimentacionIA.retroalimentacion.tokens_usados}</span>
            <span>Confianza: {(retroalimentacionIA.retroalimentacion.confianza * 100).toFixed(0)}%</span>
          </div>
        </motion.div>
      )}

      {/* Calificación Manual */}
      <div className="space-y-3">
        <label className="block text-sm font-medium text-gray-700">
          Calificación Docente (0-5)
        </label>
        <div className="flex items-center gap-4">
          <input
            type="range"
            min="0"
            max="5"
            step="0.1"
            value={calificacion}
            onChange={handleCalificacionChange}
            disabled={readOnly}
            className="flex-1 h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer disabled:bg-gray-100"
          />
          <div className="text-2xl font-bold text-blue-600 w-20 text-right">
            {calificacion.toFixed(1)}/5.0
          </div>
        </div>
      </div>

      {/* Retroalimentación Manual */}
      <div className="space-y-3">
        <label className="block text-sm font-medium text-gray-700">
          Retroalimentación Docente
        </label>
        <textarea
          value={feedback}
          onChange={handleFeedbackChange}
          disabled={readOnly}
          rows={6}
          placeholder="Escribe aquí tu retroalimentación personalizada para el estudiante..."
          className="w-full px-4 py-3 border border-gray-300 rounded-lg font-mono text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:bg-gray-100 disabled:text-gray-500 resize-none"
        />
      </div>

      {/* Footer */}
      <div className="text-xs text-gray-600 flex items-center justify-between pt-4 border-t border-gray-300">
        <span>📋 Entrega: {entregaId}</span>
        <span>
          {readOnly && '🔒 Modo Lectura'}
          {!readOnly && cargando && '⏳ Procesando...'}
          {!readOnly && !cargando && '✏️ Modo Edición'}
        </span>
      </div>
    </div>
  );
};

export default CalificacionTarea;
