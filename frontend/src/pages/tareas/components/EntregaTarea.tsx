import React, { useState, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Upload, File, X, Check, Clock, AlertCircle } from 'lucide-react';

// ====================================
// TIPOS
// ====================================

export interface ArchivoEntrega {
  id: string;
  nombre: string;
  tamaño: number;
  tipo: string;
  url?: string;
}

export interface EntregaData {
  archivos: ArchivoEntrega[];
  comentario: string;
  fechaEntrega: string;
}

export enum EstadoEntrega {
  PENDIENTE = 'pendiente',
  ENTREGADA = 'entregada',
  EN_REVISION = 'en_revision',
  CALIFICADA = 'calificada',
  DEVUELTA = 'devuelta',
}

interface EntregaTareaProps {
  tareaId: string;
  puntuacionMaxima: number;
  fechaLimite: string;
  estado: EstadoEntrega;
  entregaActual?: EntregaData;
  calificacion?: number;
  comentariosProfesor?: string;
  onEntregar: (data: EntregaData) => Promise<void>;
  loading?: boolean;
}

// ====================================
// HELPER FUNCTIONS
// ====================================

const formatearTamaño = (bytes: number): string => {
  if (bytes === 0) return '0 Bytes';
  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
};

const diasRestantes = (fecha: string): number => {
  const ahora = new Date();
  const vencimiento = new Date(fecha);
  return Math.ceil((vencimiento.getTime() - ahora.getTime()) / (1000 * 60 * 60 * 24));
};

// ====================================
// COMPONENTE
// ====================================

export const EntregaTarea: React.FC<EntregaTareaProps> = ({
  tareaId,
  puntuacionMaxima,
  fechaLimite,
  estado,
  entregaActual,
  calificacion,
  comentariosProfesor,
  onEntregar,
  loading = false,
}) => {
  const [archivos, setArchivos] = useState<ArchivoEntrega[]>(entregaActual?.archivos ?? []);
  const [comentario, setComentario] = useState(entregaActual?.comentario ?? '');
  const [entregando, setEntregando] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const dias = diasRestantes(fechaLimite);
  const vencida = dias < 0;

  const handleArchivoSeleccionado = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(e.target.files || []);
    const nuevosArchivos = files.map((file) => ({
      id: `${Date.now()}-${Math.random()}`,
      nombre: file.name,
      tamaño: file.size,
      tipo: file.type,
    }));
    setArchivos([...archivos, ...nuevosArchivos]);
  };

  const removerArchivo = (id: string) => {
    setArchivos(archivos.filter((a) => a.id !== id));
  };

  const handleEntregar = async () => {
    if (archivos.length === 0) {
      alert('Debes adjuntar al menos un archivo');
      return;
    }

    try {
      setEntregando(true);
      await onEntregar({
        archivos,
        comentario,
        fechaEntrega: new Date().toISOString(),
      });
    } catch (error) {
      console.error('Error entregando:', error);
    } finally {
      setEntregando(false);
    }
  };

  // Estado ya entregada
  if (estado === EstadoEntrega.ENTREGADA || estado === EstadoEntrega.EN_REVISION) {
    return (
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="space-y-6 bg-white dark:bg-slate-800 rounded-lg p-6 border border-slate-200 dark:border-slate-700"
      >
        <div className="flex items-center gap-3">
          <Clock className="text-blue-600 dark:text-blue-400" size={24} />
          <div>
            <h3 className="text-lg font-bold text-slate-900 dark:text-white">
              Entrega Enviada
            </h3>
            <p className="text-sm text-slate-600 dark:text-slate-400">
              {estado === EstadoEntrega.EN_REVISION
                ? 'Tu entrega está siendo revisada por el profesor'
                : 'Tu entrega ha sido registrada correctamente'}
            </p>
          </div>
        </div>

        {/* Mostrar archivos entregados */}
        {archivos.length > 0 && (
          <div>
            <h4 className="text-sm font-semibold text-slate-900 dark:text-white mb-3">
              Archivos Entregados
            </h4>
            <div className="space-y-2">
              {archivos.map((archivo) => (
                <div
                  key={archivo.id}
                  className="flex items-center gap-3 p-3 bg-slate-50 dark:bg-slate-700/50 rounded-lg"
                >
                  <File size={16} className="text-blue-600 dark:text-blue-400" />
                  <div className="flex-1">
                    <p className="text-sm font-medium text-slate-900 dark:text-white">
                      {archivo.nombre}
                    </p>
                    <p className="text-xs text-slate-500 dark:text-slate-400">
                      {formatearTamaño(archivo.tamaño)}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Mostrar comentarios */}
        {comentario && (
          <div>
            <h4 className="text-sm font-semibold text-slate-900 dark:text-white mb-2">
              Tu Comentario
            </h4>
            <p className="text-sm text-slate-700 dark:text-slate-300 italic">
              "{comentario}"
            </p>
          </div>
        )}
      </motion.div>
    );
  }

  // Estado calificada
  if (estado === EstadoEntrega.CALIFICADA) {
    return (
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="space-y-6 bg-white dark:bg-slate-800 rounded-lg p-6 border border-slate-200 dark:border-slate-700"
      >
        <div className="flex items-center gap-3">
          <Check className="text-green-600 dark:text-green-400" size={24} />
          <div>
            <h3 className="text-lg font-bold text-slate-900 dark:text-white">
              Calificación Recibida
            </h3>
            <p className="text-sm text-slate-600 dark:text-slate-400">
              Tu tarea ha sido calificada
            </p>
          </div>
        </div>

        {/* Puntuación */}
        {calificacion !== undefined && (
          <div className="p-4 bg-gradient-to-r from-green-50 to-emerald-50 dark:from-green-900/20 dark:to-emerald-900/20 rounded-lg">
            <div className="flex items-center justify-between">
              <span className="text-sm font-semibold text-slate-900 dark:text-white">
                Tu Puntuación
              </span>
              <span className="text-3xl font-bold text-green-600 dark:text-green-400">
                {calificacion}/{puntuacionMaxima}
              </span>
            </div>
            <div className="mt-3 h-2 bg-slate-200 dark:bg-slate-700 rounded-full overflow-hidden">
              <motion.div
                initial={{ width: 0 }}
                animate={{ width: `${(calificacion / puntuacionMaxima) * 100}%` }}
                transition={{ duration: 0.8 }}
                className="h-full bg-gradient-to-r from-green-500 to-emerald-500"
              />
            </div>
          </div>
        )}

        {/* Comentarios del profesor */}
        {comentariosProfesor && (
          <div>
            <h4 className="text-sm font-semibold text-slate-900 dark:text-white mb-3">
              Retroalimentación del Profesor
            </h4>
            <div className="p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg border-l-4 border-blue-500">
              <p className="text-sm text-slate-700 dark:text-slate-300 whitespace-pre-wrap">
                {comentariosProfesor}
              </p>
            </div>
          </div>
        )}

        {/* Archivos entregados */}
        {archivos.length > 0 && (
          <div>
            <h4 className="text-sm font-semibold text-slate-900 dark:text-white mb-3">
              Archivos Entregados
            </h4>
            <div className="space-y-2">
              {archivos.map((archivo) => (
                <div
                  key={archivo.id}
                  className="flex items-center gap-3 p-3 bg-slate-50 dark:bg-slate-700/50 rounded-lg"
                >
                  <File size={16} className="text-slate-600 dark:text-slate-400" />
                  <div className="flex-1">
                    <p className="text-sm font-medium text-slate-900 dark:text-white">
                      {archivo.nombre}
                    </p>
                    <p className="text-xs text-slate-500 dark:text-slate-400">
                      {formatearTamaño(archivo.tamaño)}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </motion.div>
    );
  }

  // Estado pendiente - mostrar formulario de entrega
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="space-y-6 bg-white dark:bg-slate-800 rounded-lg p-6 border border-slate-200 dark:border-slate-700"
    >
      {/* Alerta de fecha */}
      {vencida ? (
        <div className="flex items-center gap-3 p-4 bg-red-50 dark:bg-red-900/20 rounded-lg border border-red-200 dark:border-red-800">
          <AlertCircle size={20} className="text-red-600 dark:text-red-400" />
          <div>
            <p className="font-semibold text-red-900 dark:text-red-300">Tarea Vencida</p>
            <p className="text-sm text-red-700 dark:text-red-400">
              La fecha de entrega ya pasó. Puedes entregar tarde, pero tu calificación puede verse afectada.
            </p>
          </div>
        </div>
      ) : (
        <div className="flex items-center gap-3 p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg border border-blue-200 dark:border-blue-800">
          <Clock size={20} className="text-blue-600 dark:text-blue-400" />
          <div>
            <p className="font-semibold text-blue-900 dark:text-blue-300">
              {dias > 0 ? `${dias} días restantes` : 'Vence hoy'}
            </p>
            <p className="text-sm text-blue-700 dark:text-blue-400">
              Fecha de vencimiento: {new Date(fechaLimite).toLocaleDateString('es-ES')}
            </p>
          </div>
        </div>
      )}

      {/* Zona de carga de archivos */}
      <div>
        <label className="block text-sm font-semibold text-slate-900 dark:text-white mb-3">
          Archivos a Entregar
        </label>

        <motion.div
          onClick={() => fileInputRef.current?.click()}
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
          className="border-2 border-dashed border-slate-300 dark:border-slate-600 rounded-lg p-8 text-center cursor-pointer hover:border-blue-500 dark:hover:border-blue-400 transition-colors"
        >
          <Upload className="mx-auto mb-3 text-slate-400" size={32} />
          <p className="font-medium text-slate-900 dark:text-white">
            Arrastra archivos aquí o haz clic
          </p>
          <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
            Máximo 10 MB por archivo
          </p>
        </motion.div>

        <input
          ref={fileInputRef}
          type="file"
          multiple
          onChange={handleArchivoSeleccionado}
          disabled={loading || entregando}
          className="hidden"
        />

        {/* Lista de archivos */}
        <AnimatePresence>
          {archivos.length > 0 && (
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              className="mt-4 space-y-2"
            >
              {archivos.map((archivo) => (
                <motion.div
                  key={archivo.id}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  exit={{ opacity: 0, x: -20 }}
                  className="flex items-center justify-between p-3 bg-slate-50 dark:bg-slate-700/50 rounded-lg"
                >
                  <div className="flex items-center gap-3">
                    <File size={16} className="text-blue-600 dark:text-blue-400" />
                    <div>
                      <p className="text-sm font-medium text-slate-900 dark:text-white">
                        {archivo.nombre}
                      </p>
                      <p className="text-xs text-slate-500 dark:text-slate-400">
                        {formatearTamaño(archivo.tamaño)}
                      </p>
                    </div>
                  </div>
                  <button
                    onClick={() => removerArchivo(archivo.id)}
                    disabled={loading || entregando}
                    className="p-1 hover:bg-slate-200 dark:hover:bg-slate-600 rounded transition-colors"
                  >
                    <X size={16} className="text-slate-600 dark:text-slate-400" />
                  </button>
                </motion.div>
              ))}
            </motion.div>
          )}
        </AnimatePresence>
      </div>

      {/* Comentario opcional */}
      <div>
        <label className="block text-sm font-semibold text-slate-900 dark:text-white mb-3">
          Comentario (Opcional)
        </label>
        <textarea
          value={comentario}
          onChange={(e) => setComentario(e.target.value)}
          placeholder="Puedes dejar un comentario para el profesor..."
          className="w-full p-3 border border-slate-200 dark:border-slate-600 rounded-lg resize-none focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-slate-700 dark:text-white"
          rows={3}
          disabled={loading || entregando}
        />
      </div>

      {/* Botón de entrega */}
      <button
        onClick={handleEntregar}
        disabled={archivos.length === 0 || loading || entregando}
        className="w-full px-6 py-3 bg-emerald-600 hover:bg-emerald-700 disabled:opacity-50 disabled:cursor-not-allowed text-white rounded-lg transition-colors font-semibold flex items-center justify-center gap-2"
      >
        <Upload size={18} />
        {entregando ? 'Entregando...' : 'Entregar Tarea'}
      </button>
    </motion.div>
  );
};
