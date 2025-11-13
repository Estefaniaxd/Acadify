import { useState } from 'react';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { X, BookOpen } from 'lucide-react';
import axios from 'axios';

interface Curso {
  curso_id: string;
  nombre: string;
  descripcion?: string;
  modalidad: string;
  creditos?: number;
  horas_academicas?: number;
  fecha_inicio?: string;
  fecha_fin?: string;
  maximo_estudiantes?: number;
  minimo_estudiantes?: number;
  permite_inscripcion?: boolean;
  programa_id?: string;
}

interface Programa {
  programa_id: string;
  nombre: string;
  nivel: string;
}

interface Props {
  institucionId: string;
  onClose: () => void;
  curso?: Curso;
}

export default function CrearCursoModal({ institucionId, onClose, curso }: Props) {
  const queryClient = useQueryClient();
  const [formData, setFormData] = useState({
    nombre: curso?.nombre || '',
    descripcion: curso?.descripcion || '',
    modalidad: curso?.modalidad || 'semestral',
    creditos: curso?.creditos || 0,
    horas_academicas: curso?.horas_academicas || 0,
    fecha_inicio: curso?.fecha_inicio || '',
    fecha_fin: curso?.fecha_fin || '',
    maximo_estudiantes: curso?.maximo_estudiantes || 30,
    minimo_estudiantes: curso?.minimo_estudiantes || 5,
    permite_inscripcion: curso?.permite_inscripcion ?? true,
    programa_id: curso?.programa_id || ''
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
      const url = curso
        ? `http://localhost:8000/api/cursos/${curso.curso_id}`
        : 'http://localhost:8000/api/cursos/';
      
      // Preparar payload
      const payload: {
        nombre: string;
        descripcion: string | null;
        modalidad: string;
        creditos: number;
        horas_academicas: number;
        fecha_inicio: string | null;
        fecha_fin: string | null;
        maximo_estudiantes: number | null;
        minimo_estudiantes: number;
        permite_inscripcion: boolean;
        institucion_id: string;
        programa_id?: string;
      } = {
        nombre: data.nombre,
        descripcion: data.descripcion || null,
        modalidad: data.modalidad,
        creditos: Number(data.creditos),
        horas_academicas: Number(data.horas_academicas),
        fecha_inicio: data.fecha_inicio || null,
        fecha_fin: data.fecha_fin || null,
        maximo_estudiantes: data.maximo_estudiantes ? Number(data.maximo_estudiantes) : null,
        minimo_estudiantes: Number(data.minimo_estudiantes),
        permite_inscripcion: data.permite_inscripcion,
        institucion_id: institucionId
      };

      if (data.programa_id) {
        payload.programa_id = data.programa_id;
      }
      
      const method = curso ? 'put' : 'post';
      const response = await axios[method](url, payload, {
        headers: { Authorization: `Bearer ${token}` }
      });
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['cursos'] });
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
      <div className="bg-white dark:bg-gray-800 rounded-lg max-w-3xl w-full max-h-[90vh] overflow-y-auto">
        <div className="flex items-center justify-between p-6 border-b border-gray-200 dark:border-gray-700">
          <div className="flex items-center gap-3">
            <BookOpen className="w-6 h-6 text-green-600" />
            <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
              {curso ? 'Editar Curso' : 'Nuevo Curso'}
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
              Nombre del Curso *
            </label>
            <input
              type="text"
              required
              value={formData.nombre}
              onChange={(e) => setFormData({ ...formData, nombre: e.target.value })}
              placeholder="Ej: Introducción a la Programación"
              className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-green-500 dark:bg-gray-700 dark:text-white"
            />
          </div>

          {/* Descripción */}
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Descripción
            </label>
            <textarea
              value={formData.descripcion}
              onChange={(e) => setFormData({ ...formData, descripcion: e.target.value })}
              rows={3}
              placeholder="Describe el contenido y objetivos del curso..."
              className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-green-500 dark:bg-gray-700 dark:text-white resize-none"
            />
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* Modalidad */}
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Modalidad (Duración) *
              </label>
              <select
                required
                value={formData.modalidad}
                onChange={(e) => setFormData({ ...formData, modalidad: e.target.value })}
                className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-green-500 dark:bg-gray-700 dark:text-white"
              >
                <option value="anual">Anual</option>
                <option value="semestral">Semestral</option>
                <option value="trimestral">Trimestral</option>
                <option value="cuatrimestral">Cuatrimestral</option>
                <option value="bimestral">Bimestral</option>
                <option value="mensual">Mensual</option>
                <option value="modular">Modular</option>
                <option value="flexible">Flexible</option>
                <option value="intensivo">Intensivo</option>
                <option value="otro">Otro</option>
              </select>
            </div>

            {/* Programa */}
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Programa (Opcional)
              </label>
              <select
                value={formData.programa_id}
                onChange={(e) => setFormData({ ...formData, programa_id: e.target.value })}
                className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-green-500 dark:bg-gray-700 dark:text-white"
              >
                <option value="">Sin programa</option>
                {programas?.map((programa: Programa) => (
                  <option key={programa.programa_id} value={programa.programa_id}>
                    {programa.nombre}
                  </option>
                ))}
              </select>
            </div>

            {/* Créditos */}
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Créditos
              </label>
              <input
                type="number"
                min="0"
                max="20"
                value={formData.creditos}
                onChange={(e) => setFormData({ ...formData, creditos: e.target.value === '' ? 0 : Number(e.target.value) })}
                className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-green-500 dark:bg-gray-700 dark:text-white"
              />
            </div>

            {/* Horas Académicas */}
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Horas Académicas
              </label>
              <input
                type="number"
                min="0"
                max="200"
                value={formData.horas_academicas}
                onChange={(e) => setFormData({ ...formData, horas_academicas: e.target.value === '' ? 0 : Number(e.target.value) })}
                className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-green-500 dark:bg-gray-700 dark:text-white"
              />
            </div>

            {/* Fecha Inicio */}
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Fecha Inicio
              </label>
              <input
                type="date"
                value={formData.fecha_inicio}
                onChange={(e) => setFormData({ ...formData, fecha_inicio: e.target.value })}
                className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-green-500 dark:bg-gray-700 dark:text-white"
              />
            </div>

            {/* Fecha Fin */}
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Fecha Fin
              </label>
              <input
                type="date"
                value={formData.fecha_fin}
                onChange={(e) => setFormData({ ...formData, fecha_fin: e.target.value })}
                className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-green-500 dark:bg-gray-700 dark:text-white"
              />
            </div>

            {/* Mínimo Estudiantes */}
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Mínimo Estudiantes
              </label>
              <input
                type="number"
                min="1"
                max="100"
                value={formData.minimo_estudiantes}
                onChange={(e) => setFormData({ ...formData, minimo_estudiantes: e.target.value === '' ? 1 : Number(e.target.value) })}
                className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-green-500 dark:bg-gray-700 dark:text-white"
              />
            </div>

            {/* Máximo Estudiantes */}
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Máximo Estudiantes
              </label>
              <input
                type="number"
                min="1"
                max="500"
                value={formData.maximo_estudiantes}
                onChange={(e) => setFormData({ ...formData, maximo_estudiantes: e.target.value === '' ? 1 : Number(e.target.value) })}
                className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-green-500 dark:bg-gray-700 dark:text-white"
              />
            </div>
          </div>

          {/* Permite Inscripción */}
          <div className="flex items-center gap-2">
            <input
              type="checkbox"
              id="permite_inscripcion"
              checked={formData.permite_inscripcion}
              onChange={(e) => setFormData({ ...formData, permite_inscripcion: e.target.checked })}
              className="w-4 h-4 text-green-600 border-gray-300 rounded focus:ring-green-500"
            />
            <label htmlFor="permite_inscripcion" className="text-sm text-gray-700 dark:text-gray-300">
              Permitir inscripciones
            </label>
          </div>

          {/* Error */}
          {mutation.isError && (
            <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4">
              <p className="text-red-800 dark:text-red-200 text-sm font-semibold mb-2">
                Error al guardar el curso
              </p>
              {axios.isAxiosError(mutation.error) && mutation.error.response?.data?.detail && (
                <p className="text-red-700 dark:text-red-300 text-sm">
                  {typeof mutation.error.response.data.detail === 'string' 
                    ? mutation.error.response.data.detail 
                    : JSON.stringify(mutation.error.response.data.detail)}
                </p>
              )}
              {axios.isAxiosError(mutation.error) && Array.isArray(mutation.error.response?.data) && (
                <ul className="list-disc list-inside text-red-700 dark:text-red-300 text-sm space-y-1">
                  {mutation.error.response.data.map((err: {loc?: string[]; msg?: string}, idx: number) => (
                    <li key={idx}>
                      {err.loc ? `${err.loc.join('.')}: ` : ''}{err.msg || JSON.stringify(err)}
                    </li>
                  ))}
                </ul>
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
              className="px-6 py-2 bg-green-600 hover:bg-green-700 disabled:bg-green-400 text-white rounded-lg transition-colors flex items-center gap-2"
            >
              {mutation.isPending ? (
                <>
                  <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                  Guardando...
                </>
              ) : (
                curso ? 'Actualizar' : 'Crear Curso'
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
