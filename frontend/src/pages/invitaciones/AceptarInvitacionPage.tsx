import { useState } from 'react';
import { motion } from 'framer-motion';
import { CheckCircle, Building2, AlertCircle, Loader2 } from 'lucide-react';
import { useMutation } from '@tanstack/react-query';
import axios from 'axios';

interface AceptarInvitacionData {
  codigo: string;
}

interface AceptarInvitacionResponse {
  message: string;
  access_token?: string;
  token_type?: string;
  institucion: {
    id: number;
    nombre: string;
    tipo: string;
  };
}

const aceptarInvitacion = async (data: AceptarInvitacionData): Promise<AceptarInvitacionResponse> => {
  const token = localStorage.getItem('access_token');
  
  if (!token) {
    throw new Error('No hay token de autenticación');
  }

  try {
    const response = await axios.post(
      'http://localhost:8000/api/coordinador/aceptar-codigo',
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
    // Extraer el mensaje de error del backend
    if (axios.isAxiosError(error) && error.response?.data?.detail) {
      throw new Error(error.response.data.detail);
    }
    throw error;
  }
};

export default function AceptarInvitacionPage() {
  const [codigo, setCodigo] = useState('');

  const mutation = useMutation<AceptarInvitacionResponse, Error, AceptarInvitacionData>({
    mutationFn: aceptarInvitacion,
    onSuccess: (data) => {
      // Guardar el nuevo token si el backend lo devuelve
      if (data.access_token) {
        localStorage.setItem('access_token', data.access_token);
      }
      
      // Redirigir al panel del coordinador después de 2 segundos
      setTimeout(() => {
        // Forzar recarga completa para actualizar los datos del usuario
        window.location.href = '/coordinador/institucion';
      }, 2000);
    }
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!codigo.trim()) {
      return;
    }

    mutation.mutate({ codigo: codigo.trim() });
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900 flex items-center justify-center p-4">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="w-full max-w-md"
      >
        <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-xl p-8 border border-gray-200 dark:border-gray-700">
          {/* Header */}
          <div className="text-center mb-8">
            <div className="inline-flex items-center justify-center w-16 h-16 bg-gradient-to-r from-blue-500 to-indigo-600 rounded-full mb-4">
              <Building2 className="w-8 h-8 text-white" />
            </div>
            <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
              Aceptar Invitación
            </h1>
            <p className="text-gray-600 dark:text-gray-400">
              Ingresa el código de invitación que recibiste por correo electrónico
            </p>
          </div>

          {/* Success State */}
          {mutation.isSuccess && (
            <motion.div
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              className="mb-6 p-4 bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg"
            >
              <div className="flex items-start gap-3">
                <CheckCircle className="w-5 h-5 text-green-600 dark:text-green-400 flex-shrink-0 mt-0.5" />
                <div>
                  <h3 className="font-semibold text-green-900 dark:text-green-100 mb-1">
                    ¡Invitación aceptada!
                  </h3>
                  <p className="text-sm text-green-700 dark:text-green-300">
                    Ahora eres coordinador de <strong>{mutation.data.institucion.nombre}</strong>
                  </p>
                  <p className="text-xs text-green-600 dark:text-green-400 mt-2">
                    Redirigiendo al panel...
                  </p>
                </div>
              </div>
            </motion.div>
          )}

          {/* Error State */}
          {mutation.isError && (
            <motion.div
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              className="mb-6 p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg"
            >
              <div className="flex items-start gap-3">
                <AlertCircle className="w-5 h-5 text-red-600 dark:text-red-400 flex-shrink-0 mt-0.5" />
                <div>
                  <h3 className="font-semibold text-red-900 dark:text-red-100 mb-1">
                    Error al aceptar invitación
                  </h3>
                  <p className="text-sm text-red-700 dark:text-red-300">
                    {mutation.error?.message || 'El código es inválido o ya fue utilizado'}
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
                id="codigo"
                type="text"
                value={codigo}
                onChange={(e) => setCodigo(e.target.value)}
                placeholder="Ej: INV-ABC123-XYZ789"
                disabled={mutation.isPending || mutation.isSuccess}
                className="w-full px-4 py-3 bg-gray-50 dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-lg text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400 focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:opacity-50 disabled:cursor-not-allowed transition-all text-center font-mono text-lg"
              />
              <p className="mt-2 text-xs text-gray-500 dark:text-gray-400">
                El código distingue entre mayúsculas y minúsculas
              </p>
            </div>

            <button
              type="submit"
              disabled={!codigo.trim() || mutation.isPending || mutation.isSuccess}
              className="w-full bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 text-white font-semibold py-3 px-6 rounded-lg shadow-lg hover:shadow-xl disabled:opacity-50 disabled:cursor-not-allowed transition-all flex items-center justify-center gap-2"
            >
              {mutation.isPending ? (
                <>
                  <Loader2 className="w-5 h-5 animate-spin" />
                  Verificando...
                </>
              ) : mutation.isSuccess ? (
                <>
                  <CheckCircle className="w-5 h-5" />
                  Aceptada
                </>
              ) : (
                <>
                  <CheckCircle className="w-5 h-5" />
                  Aceptar Invitación
                </>
              )}
            </button>
          </form>

          {/* Help Text */}
          <div className="mt-6 pt-6 border-t border-gray-200 dark:border-gray-700">
            <p className="text-sm text-gray-600 dark:text-gray-400 text-center">
              ¿No recibiste el código?{' '}
              <a href="/contacto" className="text-blue-600 hover:text-blue-700 dark:text-blue-400 dark:hover:text-blue-300 font-medium">
                Contacta al administrador
              </a>
            </p>
          </div>
        </div>
      </motion.div>
    </div>
  );
}
