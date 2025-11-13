import { useState } from 'react';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { X, GraduationCap } from 'lucide-react';
import axios from 'axios';

interface Props {
  institucionId: string;
  onClose: () => void;
  programa?: any; // Para editar
}

export default function CrearProgramaModal({ institucionId, onClose, programa }: Props) {
  const queryClient = useQueryClient();
  const [formData, setFormData] = useState({
    nombre: programa?.nombre || '',
    nivel: programa?.nivel || '',
    tipo: programa?.tipo || '',
    descripcion: programa?.descripcion || ''
  });

  const mutation = useMutation({
    mutationFn: async (data: typeof formData) => {
      const token = localStorage.getItem('access_token');
      const url = programa
        ? `http://localhost:8000/api/programas/${programa.programa_id}`
        : 'http://localhost:8000/api/programas/';
      
      const payload = programa
        ? data  // Para PUT solo enviamos los campos a actualizar
        : { ...data, institucion_id: institucionId };  // Para POST incluimos institucion_id
      
      const method = programa ? 'put' : 'post';
      const response = await axios[method](url, payload, {
        headers: { Authorization: `Bearer ${token}` }
      });
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['programas'] });
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
            <GraduationCap className="w-6 h-6 text-blue-600" />
            <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
              {programa ? 'Editar Programa' : 'Nuevo Programa Académico'}
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
              Nombre del Programa *
            </label>
            <input
              type="text"
              required
              value={formData.nombre}
              onChange={(e) => setFormData({ ...formData, nombre: e.target.value })}
              placeholder="Ej: Ingeniería de Sistemas"
              className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
            />
          </div>

          {/* Nivel */}
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Nivel Académico *
            </label>
            <select
              required
              value={formData.nivel}
              onChange={(e) => setFormData({ ...formData, nivel: e.target.value })}
              className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
            >
              <option value="">Seleccionar nivel</option>
              <option value="preescolar">Preescolar</option>
              <option value="primaria">Primaria</option>
              <option value="secundaria">Secundaria</option>
              <option value="media">Media</option>
              <option value="bachillerato">Bachillerato</option>
              <option value="tecnico_laboral">Técnico Laboral</option>
              <option value="tecnico_profesional">Técnico Profesional</option>
              <option value="tecnologico">Tecnológico</option>
              <option value="pregrado">Pregrado</option>
              <option value="profesional">Profesional</option>
              <option value="licenciatura">Licenciatura</option>
              <option value="especializacion">Especialización</option>
              <option value="maestria">Maestría</option>
              <option value="doctorado">Doctorado</option>
              <option value="postdoctorado">Postdoctorado</option>
              <option value="diplomado">Diplomado</option>
              <option value="certificacion">Certificación</option>
              <option value="curso_corto">Curso Corto</option>
              <option value="bootcamp">Bootcamp</option>
              <option value="otro">Otro</option>
            </select>
          </div>

          {/* Tipo */}
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Modalidad *
            </label>
            <select
              required
              value={formData.tipo}
              onChange={(e) => setFormData({ ...formData, tipo: e.target.value })}
              className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
            >
              <option value="">Seleccionar modalidad</option>
              <option value="presencial">Presencial</option>
              <option value="virtual">Virtual</option>
              <option value="hibrido">Híbrido</option>
              <option value="mixto">Mixto</option>
              <option value="a_distancia">A Distancia</option>
              <option value="dual">Dual</option>
              <option value="por_ciclos">Por Ciclos</option>
              <option value="continuo">Continuo</option>
              <option value="semipresencial">Semipresencial</option>
              <option value="otro">Otro</option>
            </select>
          </div>

          {/* Descripción */}
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Descripción
            </label>
            <textarea
              value={formData.descripcion}
              onChange={(e) => setFormData({ ...formData, descripcion: e.target.value })}
              rows={4}
              className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white resize-none"
              placeholder="Describe el programa académico, sus objetivos y competencias..."
            />
          </div>

          {/* Error */}
          {mutation.isError && (
            <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4">
              <p className="text-red-800 dark:text-red-200 text-sm">
                {axios.isAxiosError(mutation.error) && mutation.error.response?.data?.detail
                  ? mutation.error.response.data.detail
                  : 'Error al guardar el programa'}
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
              className="px-6 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-blue-400 text-white rounded-lg transition-colors flex items-center gap-2"
            >
              {mutation.isPending ? (
                <>
                  <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                  Guardando...
                </>
              ) : (
                programa ? 'Actualizar' : 'Crear Programa'
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
