import React from 'react';
import { motion } from 'framer-motion';
import { Lightbulb, CheckCircle2, AlertCircle, BookOpen, Zap } from 'lucide-react';
import { RetroalimentacionIAData } from '@/services/iaService';

interface RetroalimentacionVisorProps {
  data: RetroalimentacionIAData;
  isLoading?: boolean;
}

/**
 * 💡 Visor de Retroalimentación IA
 * Muestra análisis de IA de manera limpia y profesional
 */
export const RetroalimentacionVisor: React.FC<RetroalimentacionVisorProps> = ({
  data,
  isLoading = false,
}) => {
  if (isLoading) {
    return (
      <div className="p-6 text-center">
        <div className="inline-block animate-spin">
          <Zap className="w-8 h-8 text-purple-600" />
        </div>
        <p className="mt-2 text-gray-600">Generando análisis con IA...</p>
      </div>
    );
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className="space-y-6 p-6 bg-gradient-to-br from-purple-50 to-blue-50 rounded-lg"
    >
      {/* Header */}
      <div className="flex items-start gap-3">
        <Lightbulb className="w-6 h-6 text-purple-600 flex-shrink-0 mt-1" />
        <div className="flex-1">
          <h3 className="font-bold text-lg text-gray-900">Análisis con IA</h3>
          <p className="text-xs text-gray-600 mt-1">
            Modelo: <span className="font-mono">{data.modelo_usado}</span>
          </p>
        </div>
      </div>

      {/* Retroalimentación Principal */}
      <div className="space-y-2">
        <p className="font-semibold text-gray-800 text-sm">📝 Análisis General</p>
        <p className="text-sm text-gray-700 leading-relaxed whitespace-pre-wrap bg-white p-4 rounded-lg border border-purple-100">
          {data.retroalimentacion_texto}
        </p>
      </div>

      {/* Fortalezas */}
      {data.fortalezas && data.fortalezas.length > 0 && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.1 }}
          className="space-y-2"
        >
          <div className="flex items-center gap-2">
            <CheckCircle2 className="w-5 h-5 text-green-600" />
            <p className="font-semibold text-gray-800 text-sm">Fortalezas</p>
          </div>
          <ul className="space-y-1">
            {data.fortalezas.map((f, i) => (
              <li
                key={i}
                className="text-sm text-gray-700 flex items-start gap-2 bg-green-50 p-2 rounded border-l-2 border-green-500"
              >
                <span className="text-green-600 font-bold">✓</span>
                <span>{f}</span>
              </li>
            ))}
          </ul>
        </motion.div>
      )}

      {/* Áreas de Mejora */}
      {data.areas_mejora && data.areas_mejora.length > 0 && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.2 }}
          className="space-y-2"
        >
          <div className="flex items-center gap-2">
            <AlertCircle className="w-5 h-5 text-orange-600" />
            <p className="font-semibold text-gray-800 text-sm">Áreas de Mejora</p>
          </div>
          <ul className="space-y-1">
            {data.areas_mejora.map((a, i) => (
              <li
                key={i}
                className="text-sm text-gray-700 flex items-start gap-2 bg-orange-50 p-2 rounded border-l-2 border-orange-500"
              >
                <span className="text-orange-600 font-bold">→</span>
                <span>{a}</span>
              </li>
            ))}
          </ul>
        </motion.div>
      )}

      {/* Recursos Recomendados */}
      {data.recursos_recomendados && data.recursos_recomendados.length > 0 && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.3 }}
          className="space-y-2"
        >
          <div className="flex items-center gap-2">
            <BookOpen className="w-5 h-5 text-blue-600" />
            <p className="font-semibold text-gray-800 text-sm">Recursos Recomendados</p>
          </div>
          <ul className="space-y-1">
            {data.recursos_recomendados.map((r, i) => (
              <li
                key={i}
                className="text-sm text-gray-700 flex items-start gap-2 bg-blue-50 p-2 rounded border-l-2 border-blue-500"
              >
                <span className="text-blue-600">📖</span>
                <span>{r}</span>
              </li>
            ))}
          </ul>
        </motion.div>
      )}

      {/* Calificación Sugerida */}
      {data.calificacion_sugerida && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.4 }}
          className="bg-gradient-to-r from-blue-500 to-indigo-600 text-white p-4 rounded-lg"
        >
          <p className="text-sm font-semibold mb-2">📊 Calificación Sugerida</p>
          <div className="flex items-baseline justify-between">
            <span className="text-3xl font-bold">{data.calificacion_sugerida.toFixed(1)}</span>
            <span className="text-sm opacity-90">/5.0</span>
          </div>
          {data.razonamiento_calificacion && (
            <p className="text-sm mt-2 opacity-90">{data.razonamiento_calificacion}</p>
          )}
        </motion.div>
      )}

      {/* Metadata */}
      <div className="text-xs text-gray-600 flex justify-between pt-3 border-t border-gray-200">
        <span>Tokens: {data.tokens_usados}</span>
        <span>Confianza: {(data.confianza * 100).toFixed(0)}%</span>
      </div>
    </motion.div>
  );
};
