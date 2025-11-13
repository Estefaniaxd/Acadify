/**
 * Modal para invitar coordinador a una institución
 * 
 * Funcionalidad:
 * - Input de email con validación
 * - Envía invitación al backend
 * - Muestra código de 6 dígitos generado
 * - Permite copiar código al portapapeles
 */

import { useState } from 'react';
import { X, Mail, Send, Copy, Check, AlertCircle } from 'lucide-react';
import { adminInstitucionService } from '../services/adminInstitucionService';
import type { Institucion } from '../types';

interface Props {
  institucion: Institucion;
  onClose: () => void;
  onSuccess?: (codigo: string) => void;
}

export function InvitarCoordinadorModal({ institucion, onClose, onSuccess }: Props) {
  const [email, setEmail] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [codigoGenerado, setCodigoGenerado] = useState<string | null>(null);
  const [copiado, setCopiado] = useState(false);
  const [fechaExpiracion, setFechaExpiracion] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);

    try {
      const resultado = await adminInstitucionService.invitarCoordinador(
        institucion.institucion_id,
        { email_destino: email }
      );
      
      // Guardar código generado
      setCodigoGenerado(resultado.codigo);
      setFechaExpiracion(resultado.fecha_expiracion);
      
      // Notificar éxito
      if (onSuccess) {
        onSuccess(resultado.codigo);
      }
    } catch (err: unknown) {
      const error = err as any;
      setError(error.response?.data?.detail || error.message || 'Error al enviar invitación');
    } finally {
      setLoading(false);
    }
  };

  const copiarCodigo = async () => {
    if (!codigoGenerado) return;

    try {
      await navigator.clipboard.writeText(codigoGenerado);
      setCopiado(true);
      setTimeout(() => setCopiado(false), 2000);
    } catch (err) {
      console.error('Error al copiar:', err);
    }
  };

  const handleClose = () => {
    if (codigoGenerado) {
      // Confirmación si ya se generó el código
      if (confirm('¿Seguro que deseas cerrar? Asegúrate de haber copiado el código.')) {
        onClose();
      }
    } else {
      onClose();
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white dark:bg-gray-800 rounded-lg max-w-md w-full mx-4 shadow-2xl">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200 dark:border-gray-700">
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
            Invitar Coordinador
          </h2>
          <button
            onClick={handleClose}
            className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
            aria-label="Cerrar"
          >
            <X className="w-5 h-5 text-gray-500 dark:text-gray-400" />
          </button>
        </div>

        <div className="p-6">
          {/* Información de la institución */}
          <div className="mb-6 p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg border border-blue-200 dark:border-blue-800">
            <p className="text-sm text-gray-600 dark:text-gray-400 mb-1">
              Institución:
            </p>
            <p className="font-semibold text-lg text-gray-900 dark:text-white">
              {institucion.nombre}
            </p>
            {institucion.sigla && (
              <p className="text-sm text-gray-500 dark:text-gray-400">
                ({institucion.sigla})
              </p>
            )}
          </div>

          {/* Si NO hay código generado: Formulario */}
          {!codigoGenerado ? (
            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Correo del Coordinador <span className="text-red-500">*</span>
                </label>
                <div className="relative">
                  <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                  <input
                    type="email"
                    required
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    className="w-full pl-10 pr-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
                    placeholder="coordinador@example.com"
                    disabled={loading}
                  />
                </div>
                <p className="mt-2 text-xs text-gray-500 dark:text-gray-400">
                  Se enviará un código de invitación de 6 dígitos a este correo.
                </p>
              </div>

              {/* Mensaje de error */}
              {error && (
                <div className="p-3 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg flex items-start gap-2">
                  <AlertCircle className="w-5 h-5 text-red-600 dark:text-red-400 flex-shrink-0 mt-0.5" />
                  <p className="text-sm text-red-800 dark:text-red-200">{error}</p>
                </div>
              )}

              {/* Botones */}
              <div className="flex gap-3 pt-2">
                <button
                  type="button"
                  onClick={handleClose}
                  className="flex-1 px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg text-gray-700 dark:text-gray-300 font-medium hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
                  disabled={loading}
                >
                  Cancelar
                </button>
                <button
                  type="submit"
                  disabled={loading || !email}
                  className="flex-1 flex items-center justify-center gap-2 px-4 py-3 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-lg disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                >
                  <Send className="w-4 h-4" />
                  {loading ? 'Enviando...' : 'Enviar Invitación'}
                </button>
              </div>
            </form>
          ) : (
            /* Si HAY código generado: Mostrar resultado */
            <div className="space-y-4">
              {/* Mensaje de éxito */}
              <div className="p-4 bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg">
                <div className="flex items-start gap-3">
                  <Check className="w-5 h-5 text-green-600 dark:text-green-400 flex-shrink-0 mt-0.5" />
                  <div>
                    <p className="font-semibold text-green-900 dark:text-green-100">
                      ¡Invitación enviada!
                    </p>
                    <p className="text-sm text-green-700 dark:text-green-300 mt-1">
                      Se ha enviado un email a <strong>{email}</strong> con el código de invitación.
                    </p>
                  </div>
                </div>
              </div>

              {/* Código generado */}
              <div className="p-4 bg-gray-50 dark:bg-gray-900/50 border border-gray-200 dark:border-gray-700 rounded-lg">
                <p className="text-sm text-gray-600 dark:text-gray-400 mb-2">
                  Código de invitación:
                </p>
                <div className="flex items-center gap-2">
                  <div className="flex-1 px-4 py-3 bg-white dark:bg-gray-800 border-2 border-blue-500 rounded-lg">
                    <p className="text-2xl font-mono font-bold text-center tracking-widest text-blue-600 dark:text-blue-400">
                      {codigoGenerado}
                    </p>
                  </div>
                  <button
                    onClick={copiarCodigo}
                    className="p-3 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors"
                    title="Copiar código"
                  >
                    {copiado ? (
                      <Check className="w-5 h-5" />
                    ) : (
                      <Copy className="w-5 h-5" />
                    )}
                  </button>
                </div>
                {copiado && (
                  <p className="text-xs text-green-600 dark:text-green-400 mt-2 text-center">
                    ✓ Código copiado al portapapeles
                  </p>
                )}
              </div>

              {/* Información adicional */}
              <div className="p-4 bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-lg">
                <p className="text-sm text-yellow-800 dark:text-yellow-200">
                  <strong>Importante:</strong> El código expira el{' '}
                  {fechaExpiracion && new Date(fechaExpiracion).toLocaleDateString('es-ES', {
                    day: 'numeric',
                    month: 'long',
                    year: 'numeric',
                    hour: '2-digit',
                    minute: '2-digit',
                  })}
                  . El coordinador debe usar este código para registrarse en la plataforma.
                </p>
              </div>

              {/* URL de registro */}
              <div className="p-4 bg-gray-50 dark:bg-gray-900/50 border border-gray-200 dark:border-gray-700 rounded-lg">
                <p className="text-sm text-gray-600 dark:text-gray-400 mb-2">
                  URL de registro:
                </p>
                <p className="text-xs font-mono text-gray-700 dark:text-gray-300 break-all">
                  {window.location.origin}/registro-coordinador?codigo={codigoGenerado}
                </p>
              </div>

              {/* Botón cerrar */}
              <button
                onClick={onClose}
                className="w-full px-4 py-3 bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600 text-gray-900 dark:text-white font-medium rounded-lg transition-colors"
              >
                Cerrar
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
