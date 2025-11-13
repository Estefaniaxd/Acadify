import { useState } from 'react';
import { motion } from 'framer-motion';
import { CheckCircle, Building2, AlertCircle, Loader2, Users } from 'lucide-react';
import { useMutation } from '@tanstack/react-query';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';

interface UsarCodigoData {
  codigo_invitacion: string;
}

interface UsarCodigoResponse {
  success: boolean;
  message: string;
  data?: {
    institucion_nombre: string;
    programa_nombre?: string;
  };
}

const usarCodigoInvitacion = async (data: UsarCodigoData): Promise<UsarCodigoResponse> => {
  const token = localStorage.getItem('access_token');
  
  if (!token) {
    throw new Error('Debes iniciar sesión para usar un código de invitación');
  }

  try {
    // Endpoint para vincular por código de invitación
    const response = await axios.post(
      'http://localhost:8000/api/cursos/inscripciones/auto-vincular-estudiante',
      data,
      {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      }
    );
    
    return response.data;
  } catch (error) {
    if (axios.isAxiosError(error) && error.response?.data?.detail) {
      throw new Error(error.response.data.detail);
    }
    throw error;
  }
};

export default function UsarCodigoInvitacionPage() {
  const [codigo, setCodigo] = useState('');
  const navigate = useNavigate();

  const mutation = useMutation<UsarCodigoResponse, Error, UsarCodigoData>({
    mutationFn: usarCodigoInvitacion,
    onSuccess: () => {
      // Redirigir después de 2 segundos
      setTimeout(() => {
        navigate('/cursos');
      }, 2000);
    }
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!codigo.trim()) {
      return;
    }

    mutation.mutate({ codigo_invitacion: codigo.trim().toUpperCase() });
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900 flex items-center justify-center p-4">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="max-w-md w-full"
      >
        <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-2xl p-8">
          {/* Header */}
          <div className="text-center mb-8">
            <div className="inline-flex items-center justify-center w-16 h-16 bg-gradient-to-br from-indigo-500 to-purple-600 rounded-full mb-4">
              <Users className="w-8 h-8 text-white" />
            </div>
            <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
              Unirse a Institución
            </h1>
            <p className="text-gray-600 dark:text-gray-400">
              Ingresa el código de invitación que te proporcionó el coordinador
            </p>
          </div>

          {/* Success Message */}
          {mutation.isSuccess && (
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              className="mb-6 p-4 bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg"
            >
              <div className="flex items-start gap-3">
                <CheckCircle className="w-5 h-5 text-green-600 dark:text-green-400 flex-shrink-0 mt-0.5" />
                <div className="flex-1">
                  <h3 className="font-semibold text-green-900 dark:text-green-100 mb-1">
                    ¡Vinculación exitosa!
                  </h3>
                  <p className="text-sm text-green-800 dark:text-green-200">
                    {mutation.data?.message}
                  </p>
                  {mutation.data?.data?.institucion_nombre && (
                    <p className="text-sm text-green-700 dark:text-green-300 mt-2">
                      <Building2 className="w-4 h-4 inline mr-1" />
                      {mutation.data.data.institucion_nombre}
                    </p>
                  )}
                  <p className="text-sm text-green-600 dark:text-green-400 mt-2">
                    Redirigiendo a cursos...
                  </p>
                </div>
              </div>
            </motion.div>
          )}

          {/* Error Message */}
          {mutation.isError && (
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              className="mb-6 p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg"
            >
              <div className="flex items-start gap-3">
                <AlertCircle className="w-5 h-5 text-red-600 dark:text-red-400 flex-shrink-0 mt-0.5" />
                <div className="flex-1">
                  <h3 className="font-semibold text-red-900 dark:text-red-100 mb-1">
                    Error al usar el código
                  </h3>
                  <p className="text-sm text-red-800 dark:text-red-200">
                    {mutation.error?.message || 'Ha ocurrido un error. Verifica el código e intenta nuevamente.'}
                  </p>
                </div>
              </div>
            </motion.div>
          )}

          {/* Form */}
          <form onSubmit={handleSubmit} className="space-y-6">
            <div>
              <label htmlFor="codigo" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Código de Invitación
              </label>
              <input
                type="text"
                id="codigo"
                value={codigo}
                onChange={(e) => setCodigo(e.target.value.toUpperCase())}
                placeholder="Ej: ABC123XY"
                maxLength={8}
                className="w-full px-4 py-3 text-center text-2xl font-mono font-bold tracking-widest border-2 border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent dark:bg-gray-700 dark:text-white transition-all uppercase"
                disabled={mutation.isPending || mutation.isSuccess}
                required
              />
              <p className="mt-2 text-xs text-gray-500 dark:text-gray-400">
                El código distingue entre mayúsculas y minúsculas
              </p>
            </div>

            <button
              type="submit"
              disabled={mutation.isPending || mutation.isSuccess || !codigo.trim()}
              className="w-full bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-700 hover:to-purple-700 text-white font-semibold py-3 px-6 rounded-lg shadow-lg hover:shadow-xl transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
            >
              {mutation.isPending ? (
                <>
                  <Loader2 className="w-5 h-5 animate-spin" />
                  Verificando código...
                </>
              ) : mutation.isSuccess ? (
                <>
                  <CheckCircle className="w-5 h-5" />
                  Vinculado exitosamente
                </>
              ) : (
                <>
                  <Building2 className="w-5 h-5" />
                  Unirse a Institución
                </>
              )}
            </button>
          </form>

          {/* Info */}
          <div className="mt-8 pt-6 border-t border-gray-200 dark:border-gray-700">
            <div className="text-center text-sm text-gray-600 dark:text-gray-400">
              <p className="mb-2">¿No tienes un código?</p>
              <p>Solicítalo al coordinador de tu institución</p>
            </div>
          </div>
        </div>
      </motion.div>
    </div>
  );
}
