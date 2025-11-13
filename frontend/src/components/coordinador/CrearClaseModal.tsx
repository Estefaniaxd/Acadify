import { useState } from 'react';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { X, Users } from 'lucide-react';
import axios from 'axios';

interface Grupo {
  grupo_id: string;
  nombre: string;
  jornada: string;
  programa_id?: string;
  docente_tutor_id?: string;
}

interface Programa {
  programa_id: string;
  nombre: string;
  nivel: string;
}

interface Props {
  institucionId: string;
  onClose: () => void;
  grupo?: Grupo;
}

export default function CrearClaseModal({ institucionId, onClose, grupo }: Props) {
  const queryClient = useQueryClient();
  const [formData, setFormData] = useState({
    nombre: grupo?.nombre || '',
    jornada: grupo?.jornada || 'manana',
    programa_id: grupo?.programa_id || '',
    docente_tutor_id: grupo?.docente_tutor_id || ''
  });

  // Obtener programas de la institución
  const { data: programas } = useQuery({
    queryKey: ['programas', institucionId],
    queryFn: async () => {
      const token = localStorage.getItem('access_token');
      const response = await axios.get('http://localhost:8000/api/programas/', {
        headers: { Authorization: `Bearer ${token}` },
        params: { institucion_id: institucionId }
      });
      return response.data;
    },
    enabled: !!institucionId
  });

  const mutation = useMutation({
    mutationFn: async (data: typeof formData) => {
      const token = localStorage.getItem('access_token');
      const url = grupo
        ? `http://localhost:8000/api/grupos/${grupo.grupo_id}`
        : 'http://localhost:8000/api/grupos/';
      
      // Limpiar campos vacíos
      const payload: {
        nombre: string;
        jornada: string;
        programa_id?: string;
        docente_tutor_id?: string;
      } = {
        nombre: data.nombre,
        jornada: data.jornada,
      };
      
      if (data.programa_id) {
        payload.programa_id = data.programa_id;
      }
      
      if (data.docente_tutor_id) {
        payload.docente_tutor_id = data.docente_tutor_id;
      }
      
      const method = grupo ? 'put' : 'post';
      const response = await axios[method](url, payload, {
        headers: { Authorization: `Bearer ${token}` }
      });
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['grupos'] });
      queryClient.invalidateQueries({ queryKey: ['estadisticas-institucion'] });
      onClose();
    },
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    mutation.mutate(formData);
  };

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div className="bg-white dark:bg-gray-800 rounded-lg max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        <div className="flex items-center justify-between p-6 border-b border-gray-200 dark:border-gray-700">
          <div className="flex items-center gap-3">
            <Users className="w-6 h-6 text-purple-600" />
            <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
              {grupo ? 'Editar Clase/Grupo' : 'Nueva Clase/Grupo'}
            </h2>
          </div>
          <button
            onClick={onClose}
            className="text-gray-500 hover:text-gray-700 dark:hover:text-gray-300"
          >
            <X className="w-6 h-6" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="p-6 space-y-6">
          {/* Nombre */}
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Nombre de la Clase/Grupo *
            </label>
            <input
              type="text"
              required
              value={formData.nombre}
              onChange={(e) => setFormData({ ...formData, nombre: e.target.value })}
              placeholder="Ej: Grupo A - Primer Semestre 2024"
              className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-purple-500 dark:bg-gray-700 dark:text-white"
            />
          </div>

          {/* Jornada */}
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Jornada *
            </label>
            <select
              required
              value={formData.jornada}
              onChange={(e) => setFormData({ ...formData, jornada: e.target.value })}
              className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-purple-500 dark:bg-gray-700 dark:text-white"
            >
              <option value="manana">Mañana</option>
              <option value="tarde">Tarde</option>
              <option value="nocturna">Nocturna</option>
              <option value="mixta">Mixta</option>
              <option value="completa">Completa</option>
              <option value="sabatina">Sabatina</option>
              <option value="dominical">Dominical</option>
              <option value="fin_semana">Fin de Semana</option>
              <option value="especial">Especial</option>
            </select>
          </div>

          {/* Programa */}
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Programa Asociado (Opcional)
            </label>
            <select
              value={formData.programa_id}
              onChange={(e) => setFormData({ ...formData, programa_id: e.target.value })}
              className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-purple-500 dark:bg-gray-700 dark:text-white"
            >
              <option value="">Sin programa asignado</option>
              {programas?.map((programa: Programa) => (
                <option key={programa.programa_id} value={programa.programa_id}>
                  {programa.nombre} ({programa.nivel})
                </option>
              ))}
            </select>
            <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
              Vincula esta clase a un programa académico específico
            </p>
          </div>

          {/* Docente Tutor */}
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              ID Docente Tutor (Opcional)
            </label>
            <input
              type="text"
              value={formData.docente_tutor_id}
              onChange={(e) => setFormData({ ...formData, docente_tutor_id: e.target.value })}
              placeholder="UUID del docente"
              className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-purple-500 dark:bg-gray-700 dark:text-white"
            />
            <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
              Asigna un profesor responsable de esta clase
            </p>
          </div>

          {/* Error */}
          {mutation.isError && (
            <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4">
              <p className="text-red-800 dark:text-red-200 text-sm">
                {axios.isAxiosError(mutation.error) && mutation.error.response?.data?.detail
                  ? mutation.error.response.data.detail
                  : 'Error al guardar la clase/grupo'}
              </p>
            </div>
          )}

          {/* Buttons */}
          <div className="flex gap-3 justify-end">
            <button
              type="button"
              onClick={onClose}
              className="px-6 py-2 border border-gray-300 dark:border-gray-600 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 text-gray-700 dark:text-gray-300 transition-colors"
            >
              Cancelar
            </button>
            <button
              type="submit"
              disabled={mutation.isPending}
              className="px-6 py-2 bg-purple-600 hover:bg-purple-700 disabled:bg-purple-400 text-white rounded-lg transition-colors flex items-center gap-2"
            >
              {mutation.isPending ? (
                <>
                  <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                  Guardando...
                </>
              ) : (
                grupo ? 'Actualizar' : 'Crear Clase/Grupo'
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
