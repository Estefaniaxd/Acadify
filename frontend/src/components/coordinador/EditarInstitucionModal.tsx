import { useState } from 'react';
import { useMutation, useQueryClient, useQuery } from '@tanstack/react-query';
import { X, Building2, MapPin, Phone, Mail, Globe } from 'lucide-react';
import axios from 'axios';

interface Institucion {
  id: string;
  nombre: string;
  tipo: string;
  ubicacion?: string;
  estado?: string;
  created_at?: string;
}

interface InstitucionCompleta {
  institucion_id: string;
  nombre: string;
  ciudad?: string | null;
  pais?: string | null;
  telefono?: string | null;
  correo_institucional?: string | null;
  website?: string | null;
}

interface Props {
  institucion: Institucion;
  onClose: () => void;
}

export default function EditarInstitucionModal({ institucion, onClose }: Props) {
  const queryClient = useQueryClient();
  const token = localStorage.getItem('access_token');
  
  // Obtener datos completos de la institución
  const { data: institucionCompleta } = useQuery<InstitucionCompleta>({
    queryKey: ['institucion-completa', institucion.id],
    queryFn: async () => {
      const response = await axios.get(
        `http://localhost:8000/api/instituciones/${institucion.id}`,
        { headers: { Authorization: `Bearer ${token}` } }
      );
      return response.data;
    },
  });

  // Inicializar con datos disponibles - si hay institucionCompleta usa eso, sino usa institucion
  const [formData, setFormData] = useState({
    nombre: institucion.nombre || '',
    ciudad: '',
    pais: '',
    telefono: '',
    correo_institucional: '',
    website: '',
  });

  const mutation = useMutation({
    mutationFn: async (data: typeof formData) => {
      const response = await axios.put(
        `http://localhost:8000/api/instituciones/${institucion.id}`,
        data,
        { headers: { Authorization: `Bearer ${token}` } }
      );
      return response.data;
    },
    onSuccess: () => {
      // Invalidar ambas queries para refrescar los datos
      queryClient.invalidateQueries({ queryKey: ['mi-institucion'] });
      queryClient.invalidateQueries({ queryKey: ['institucion-completa', institucion.id] });
      queryClient.invalidateQueries({ queryKey: ['estadisticas-institucion'] });
      
      // Cerrar modal después de un breve delay para que el usuario vea el éxito
      setTimeout(() => onClose(), 500);
    },
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    mutation.mutate(formData);
  };

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div className="bg-white dark:bg-gray-800 rounded-lg max-w-2xl w-full max-h-[90vh] overflow-y-auto" key={institucionCompleta?.institucion_id || 'loading'}>
        <div className="flex items-center justify-between p-6 border-b border-gray-200 dark:border-gray-700">
          <div className="flex items-center gap-3">
            <Building2 className="w-6 h-6 text-blue-600" />
            <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
              Editar Institución
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
              Nombre de la Institución *
            </label>
            <input
              type="text"
              required
              value={formData.nombre}
              onChange={(e) => setFormData({ ...formData, nombre: e.target.value })}
              placeholder={institucionCompleta?.nombre || institucion.nombre}
              className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
            />
          </div>

          {/* Ubicación */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                <MapPin className="w-4 h-4 inline mr-1" />
                Ciudad
              </label>
              <input
                type="text"
                value={formData.ciudad}
                onChange={(e) => setFormData({ ...formData, ciudad: e.target.value })}
                placeholder={institucionCompleta?.ciudad || ''}
                className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                <MapPin className="w-4 h-4 inline mr-1" />
                País
              </label>
              <input
                type="text"
                value={formData.pais}
                onChange={(e) => setFormData({ ...formData, pais: e.target.value })}
                placeholder={institucionCompleta?.pais || ''}
                className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
              />
            </div>
          </div>

          {/* Contacto */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                <Phone className="w-4 h-4 inline mr-1" />
                Teléfono
              </label>
              <input
                type="tel"
                value={formData.telefono}
                onChange={(e) => setFormData({ ...formData, telefono: e.target.value })}
                className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                <Mail className="w-4 h-4 inline mr-1" />
                Email Institucional
              </label>
              <input
                type="email"
                value={formData.correo_institucional}
                onChange={(e) => setFormData({ ...formData, correo_institucional: e.target.value })}
                className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
              />
            </div>
          </div>

          {/* Sitio Web */}
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              <Globe className="w-4 h-4 inline mr-1" />
              Sitio Web
            </label>
            <input
              type="url"
              value={formData.website}
              onChange={(e) => setFormData({ ...formData, website: e.target.value })}
              placeholder="https://ejemplo.com"
              className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
            />
          </div>

          {/* Success */}
          {mutation.isSuccess && (
            <div className="bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg p-4">
              <p className="text-green-800 dark:text-green-200 text-sm font-semibold">
                ✓ Institución actualizada exitosamente
              </p>
            </div>
          )}

          {/* Error */}
          {mutation.isError && (
            <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4">
              <p className="text-red-800 dark:text-red-200 text-sm font-semibold mb-2">
                Error al actualizar la institución:
              </p>
              {axios.isAxiosError(mutation.error) && mutation.error.response?.data?.detail ? (
                Array.isArray(mutation.error.response.data.detail) ? (
                  <ul className="list-disc list-inside space-y-1 text-red-700 dark:text-red-300 text-sm">
                    {mutation.error.response.data.detail.map((err: { msg?: string; message?: string }, idx: number) => (
                      <li key={idx}>
                        {err.msg || err.message || JSON.stringify(err)}
                      </li>
                    ))}
                  </ul>
                ) : (
                  <p className="text-red-700 dark:text-red-300 text-sm">
                    {typeof mutation.error.response.data.detail === 'string'
                      ? mutation.error.response.data.detail
                      : JSON.stringify(mutation.error.response.data.detail)}
                  </p>
                )
              ) : (
                <p className="text-red-700 dark:text-red-300 text-sm">
                  {mutation.error?.message || 'Error desconocido'}
                </p>
              )}
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
              className="px-6 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-blue-400 text-white rounded-lg transition-colors flex items-center gap-2"
            >
              {mutation.isPending ? (
                <>
                  <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                  Guardando...
                </>
              ) : (
                'Guardar Cambios'
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
