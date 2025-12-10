import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Zap, ChevronDown, AlertCircle, CheckCircle2, Loader2 } from 'lucide-react';
import { BulkIAFeedbackModal } from './BulkIAFeedbackModal';

interface EntregasListProps {
  entregas: any[];
  cargando?: boolean;
  onGenerarIndividual?: (entregaId: string) => Promise<void>;
  onOpenEntrega?: (entregaId: string) => void;
  onBulkComplete?: () => void;
}

/**
 * 📋 Lista de Entregas con opciones de IA
 * Permite ver entregas y generar retroalimentación masiva
 */
export const EntregasList: React.FC<EntregasListProps> = ({ entregas, cargando = false, onGenerarIndividual, onOpenEntrega, onBulkComplete }) => {
  const [expandido, setExpandido] = useState<string | null>(null);
  const [modalBulkAbierto, setModalBulkAbierto] = useState(false);
  const [entregasSeleccionadas, setEntregasSeleccionadas] = useState<string[]>([]);

  const handleSeleccionar = (entregaId: string) => {
    setEntregasSeleccionadas((prev) =>
      prev.includes(entregaId) ? prev.filter((id) => id !== entregaId) : [...prev, entregaId]
    );
  };

  const handleSeleccionarTodas = () => {
    if (entregasSeleccionadas.length === entregas.length) {
      setEntregasSeleccionadas([]);
    } else {
      setEntregasSeleccionadas(entregas.map((e) => e.id));
    }
  };

  const handleGenerarMasiva = () => {
    if (entregasSeleccionadas.length > 0) {
      setModalBulkAbierto(true);
    }
  };

  if (cargando) {
    return (
      <div className="p-8 text-center">
        <div className="inline-block animate-spin">
          <Zap className="w-8 h-8 text-blue-600" />
        </div>
        <p className="mt-2 text-gray-600">Cargando entregas...</p>
      </div>
    );
  }

  if (!entregas || entregas.length === 0) {
    return (
      <div className="p-8 text-center text-gray-500">
        <p>No hay entregas disponibles</p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* Toolbar */}
      <div className="flex items-center justify-between p-4 bg-blue-50 rounded-lg border border-blue-200">
        <label className="flex items-center gap-2 cursor-pointer">
          <input
            type="checkbox"
            checked={entregasSeleccionadas.length === entregas.length && entregas.length > 0}
            onChange={handleSeleccionarTodas}
            className="w-4 h-4 rounded"
          />
          <span className="text-sm font-medium text-gray-700">
            Seleccionar todas ({entregasSeleccionadas.length}/{entregas.length})
          </span>
        </label>

        {entregasSeleccionadas.length > 0 && (
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={handleGenerarMasiva}
            className="flex items-center gap-2 px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors"
          >
            <Zap size={18} />
            Generar Retroalimentación ({entregasSeleccionadas.length})
          </motion.button>
        )}
      </div>

      {/* Lista de Entregas */}
      <div className="space-y-2">
        {entregas.map((entrega) => (
          <motion.div
            key={entrega.id}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            className="border border-gray-200 rounded-lg overflow-hidden hover:shadow-md transition-shadow"
          >
            <div className="flex items-center gap-4 p-4 bg-white hover:bg-gray-50">
              <label className="flex items-center gap-2 cursor-pointer">
                <input
                  type="checkbox"
                  checked={entregasSeleccionadas.includes(entrega.id)}
                  onChange={() => handleSeleccionar(entrega.id)}
                  className="w-4 h-4 rounded"
                />
              </label>

              <button
                onClick={() => setExpandido(expandido === entrega.id ? null : entrega.id)}
                className="flex-1 text-left hover:opacity-80"
              >
                <div className="flex items-center justify-between">
                  <div className="flex-1">
                    <h3 className="font-semibold text-gray-900">{entrega.estudiante_nombre}</h3>
                    <p className="text-xs text-gray-600">Entrega ID: {entrega.id}</p>
                  </div>

                  {entrega.retroalimentacion_ia && (
                    <span className="px-2 py-1 bg-green-100 text-green-700 text-xs rounded-full flex items-center gap-1">
                      <CheckCircle2 size={14} />
                      Con IA
                    </span>
                  )}

                  <ChevronDown
                    size={18}
                    className={`transition-transform ${expandido === entrega.id ? 'rotate-180' : ''}`}
                  />
                </div>
              </button>
            </div>

            {/* Detalles expandidos */}
            {expandido === entrega.id && (
              <motion.div
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: 'auto' }}
                exit={{ opacity: 0, height: 0 }}
                className="px-4 py-3 bg-gray-50 border-t border-gray-200 space-y-3"
              >
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <p className="text-gray-600">Fecha de Entrega</p>
                    <p className="font-semibold">{new Date(entrega.fecha_entrega).toLocaleDateString()}</p>
                  </div>
                  <div>
                    <p className="text-gray-600">Estado</p>
                    <p className="font-semibold capitalize">{entrega.estado}</p>
                  </div>
                </div>

                {entrega.retroalimentacion_ia && (
                  <div className="p-3 bg-purple-50 border border-purple-200 rounded-lg">
                    <p className="text-xs text-purple-600 font-semibold mb-2">📊 Retroalimentación IA</p>
                    <p className="text-sm text-gray-700 line-clamp-3">
                      {entrega.retroalimentacion_ia.retroalimentacion_texto}
                    </p>
                  </div>
                )}

                <div className="flex gap-2">
                  <button
                    onClick={() => onOpenEntrega ? onOpenEntrega(entrega.id) : null}
                    className="flex-1 px-3 py-2 bg-blue-600 text-white text-sm rounded hover:bg-blue-700"
                  >
                    Ver Detalles
                  </button>
                  {!entrega.retroalimentacion_ia && (
                    <GenerarIndividualButton entregaId={entrega.id} onGenerar={onGenerarIndividual} />
                  )}
                </div>
              </motion.div>
            )}
          </motion.div>
        ))}
      </div>

      {/* Modal para procesamiento masivo */}
      <BulkIAFeedbackModal
        isOpen={modalBulkAbierto}
        tareas={entregasSeleccionadas.map((id) => ({
          id,
          titulo: entregas.find((e) => e.id === id)?.estudiante_nombre || 'Desconocido',
        }))}
        onClose={() => {
          setModalBulkAbierto(false);
          setEntregasSeleccionadas([]);
        }}
        onComplete={() => {
          setModalBulkAbierto(false);
          setEntregasSeleccionadas([]);
          if (onBulkComplete) onBulkComplete();
        }}
      />
    </div>
  );
};

// Small helper button component that calls parent handler and shows temporary loading
function GenerarIndividualButton({ entregaId, onGenerar }: { entregaId: string; onGenerar?: (id: string) => Promise<void> }) {
  const [loading, setLoading] = React.useState(false);

  const handleClick = async () => {
    if (!onGenerar) return;
    setLoading(true);
    try {
      await onGenerar(entregaId);
    } catch (e) {
      console.error('Error generando IA individual:', e);
      alert('Error generando retroalimentación IA. Ver consola para más detalles.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <button
      onClick={handleClick}
      disabled={loading}
      className={`flex-1 px-3 py-2 ${loading ? 'bg-gray-400' : 'bg-purple-600 hover:bg-purple-700'} text-white text-sm rounded flex items-center justify-center gap-1`}
    >
      {loading ? (
        <Loader2 className="w-4 h-4 animate-spin" />
      ) : (
        <>
          <Zap size={14} />
          Generar IA
        </>
      )}
    </button>
  );
}
