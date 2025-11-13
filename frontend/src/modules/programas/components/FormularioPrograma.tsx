/**
 * Componente FormularioPrograma
 * Formulario para crear/editar programas académicos
 */

import { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
;
import {
  usePrograma,
  useCrearPrograma,
  useActualizarPrograma,
} from '../hooks/useProgramas';
import { useInstituciones } from '../../instituciones/hooks/useInstituciones';
import type { CrearProgramaDTO, NivelAcademico, ModalidadEstudio } from '../types';
import { GraduationCap, Save, X } from 'lucide-react';

interface FormularioProgramaProps {
  modo?: 'crear' | 'editar';
}

export function FormularioPrograma({ modo = 'crear' }: FormularioProgramaProps) {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const esEdicion = modo === 'editar' && id;

  // Queries
  const { data: programa, isLoading: cargandoPrograma } = usePrograma(
    esEdicion ? parseInt(id!) : undefined
  );
  const { data: respuestaInstituciones } = useInstituciones({ limite: 100 });
  
  // Mutations
  const crearPrograma = useCrearPrograma();
  const actualizarPrograma = useActualizarPrograma();

  // Estado del formulario
  const [formData, setFormData] = useState<CrearProgramaDTO>({
    codigo: '',
    nombre: '',
    descripcion: '',
    nivel: 'PROFESIONAL' as NivelAcademico,
    modalidad: 'PRESENCIAL' as ModalidadEstudio,
    duracionSemestres: 10,
    creditosRequeridos: 160,
    institucionId: 0,
    requiereProyectoGrado: true,
    requierePracticas: true,
    horasPracticas: 480,
  });

  const [errores, setErrores] = useState<Record<string, string>>({});

  // Cargar datos en edición
  useEffect(() => {
    if (programa && esEdicion) {
      setFormData({
        codigo: programa.codigo,
        nombre: programa.nombre,
        descripcion: programa.descripcion || '',
        nivel: programa.nivel,
        modalidad: programa.modalidad,
        duracionSemestres: programa.duracionSemestres,
        creditosRequeridos: programa.creditosRequeridos,
        institucionId: programa.institucionId,
        requiereProyectoGrado: programa.requiereProyectoGrado,
        requierePracticas: programa.requierePracticas,
        horasPracticas: programa.horasPracticas,
      });
    }
  }, [programa, esEdicion]);

  // Validación
  const validarFormulario = (): boolean => {
    const nuevosErrores: Record<string, string> = {};

    if (!formData.codigo.trim()) {
      nuevosErrores.codigo = 'El código es requerido';
    } else if (formData.codigo.length < 3) {
      nuevosErrores.codigo = 'El código debe tener al menos 3 caracteres';
    }

    if (!formData.nombre.trim()) {
      nuevosErrores.nombre = 'El nombre es requerido';
    } else if (formData.nombre.length < 5) {
      nuevosErrores.nombre = 'El nombre debe tener al menos 5 caracteres';
    }

    if (formData.institucionId === 0) {
      nuevosErrores.institucionId = 'Debes seleccionar una institución';
    }

    if (formData.duracionSemestres < 1 || formData.duracionSemestres > 20) {
      nuevosErrores.duracionSemestres = 'La duración debe estar entre 1 y 20 semestres';
    }

    if (formData.creditosRequeridos < 1) {
      nuevosErrores.creditosRequeridos = 'Los créditos deben ser al menos 1';
    }

    if (formData.requierePracticas && (!formData.horasPracticas || formData.horasPracticas < 1)) {
      nuevosErrores.horasPracticas = 'Las horas de práctica son requeridas';
    }

    setErrores(nuevosErrores);
    return Object.keys(nuevosErrores).length === 0;
  };

  // Submit
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!validarFormulario()) {
      return;
    }

    try {
      if (esEdicion) {
        await actualizarPrograma.mutateAsync({
          id: parseInt(id!),
          data: formData,
        });
        alert('Programa actualizado exitosamente');
      } else {
        await crearPrograma.mutateAsync(formData);
        alert('Programa creado exitosamente');
      }
      navigate('/admin/programas');
    } catch (error: any) {
      alert(error.message || 'Error al guardar programa');
    }
  };

  const handleChange = (campo: string, valor: any) => {
    setFormData(prev => ({ ...prev, [campo]: valor }));
    if (errores[campo]) {
      setErrores(prev => ({ ...prev, [campo]: '' }));
    }
  };

  if (cargandoPrograma) {
    return (
      <div className="p-6">
        <div className="animate-pulse">
          <div className="h-8 bg-gray-300 dark:bg-gray-600 rounded w-1/4 mb-6"></div>
          <div className="h-64 bg-gray-300 dark:bg-gray-600 rounded"></div>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 max-w-4xl mx-auto">
      <div className="flex items-center gap-3 mb-6">
        <GraduationCap className="text-3xl text-purple-600" />
        <h1 className="text-2xl font-bold text-gray-800 dark:text-white">
          {esEdicion ? 'Editar Programa' : 'Nuevo Programa'}
        </h1>
      </div>

      <form onSubmit={handleSubmit} className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Código */}
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Código *
            </label>
            <input
              type="text"
              value={formData.codigo}
              onChange={(e) => handleChange('codigo', e.target.value)}
              className={`w-full px-4 py-2 border rounded-lg dark:bg-gray-700 dark:text-white ${
                errores.codigo ? 'border-red-500' : 'border-gray-300 dark:border-gray-600'
              }`}
              placeholder="Ej: ING-SW-001"
            />
            {errores.codigo && <p className="text-red-500 text-sm mt-1">{errores.codigo}</p>}
          </div>

          {/* Institución */}
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Institución *
            </label>
            <select
              value={formData.institucionId}
              onChange={(e) => handleChange('institucionId', parseInt(e.target.value))}
              className={`w-full px-4 py-2 border rounded-lg dark:bg-gray-700 dark:text-white ${
                errores.institucionId ? 'border-red-500' : 'border-gray-300 dark:border-gray-600'
              }`}
            >
              <option value={0}>Selecciona una institución</option>
              {respuestaInstituciones?.items.map((inst) => (
                <option key={inst.id} value={inst.id}>
                  {inst.nombre}
                </option>
              ))}
            </select>
            {errores.institucionId && <p className="text-red-500 text-sm mt-1">{errores.institucionId}</p>}
          </div>

          {/* Nombre */}
          <div className="md:col-span-2">
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Nombre del Programa *
            </label>
            <input
              type="text"
              value={formData.nombre}
              onChange={(e) => handleChange('nombre', e.target.value)}
              className={`w-full px-4 py-2 border rounded-lg dark:bg-gray-700 dark:text-white ${
                errores.nombre ? 'border-red-500' : 'border-gray-300 dark:border-gray-600'
              }`}
              placeholder="Ej: Ingeniería de Software"
            />
            {errores.nombre && <p className="text-red-500 text-sm mt-1">{errores.nombre}</p>}
          </div>

          {/* Descripción */}
          <div className="md:col-span-2">
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Descripción
            </label>
            <textarea
              value={formData.descripcion}
              onChange={(e) => handleChange('descripcion', e.target.value)}
              rows={4}
              className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg dark:bg-gray-700 dark:text-white"
              placeholder="Describe el programa académico..."
            />
          </div>

          {/* Nivel */}
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Nivel Académico *
            </label>
            <select
              value={formData.nivel}
              onChange={(e) => handleChange('nivel', e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg dark:bg-gray-700 dark:text-white"
            >
              <option value="TECNICO">Técnico</option>
              <option value="TECNOLOGO">Tecnólogo</option>
              <option value="PROFESIONAL">Profesional</option>
              <option value="ESPECIALIZACION">Especialización</option>
              <option value="MAESTRIA">Maestría</option>
              <option value="DOCTORADO">Doctorado</option>
            </select>
          </div>

          {/* Modalidad */}
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Modalidad *
            </label>
            <select
              value={formData.modalidad}
              onChange={(e) => handleChange('modalidad', e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg dark:bg-gray-700 dark:text-white"
            >
              <option value="PRESENCIAL">Presencial</option>
              <option value="VIRTUAL">Virtual</option>
              <option value="HIBRIDO">Híbrido</option>
            </select>
          </div>

          {/* Duración */}
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Duración (Semestres) *
            </label>
            <input
              type="number"
              min="1"
              max="20"
              value={formData.duracionSemestres}
              onChange={(e) => handleChange('duracionSemestres', parseInt(e.target.value))}
              className={`w-full px-4 py-2 border rounded-lg dark:bg-gray-700 dark:text-white ${
                errores.duracionSemestres ? 'border-red-500' : 'border-gray-300 dark:border-gray-600'
              }`}
            />
            {errores.duracionSemestres && <p className="text-red-500 text-sm mt-1">{errores.duracionSemestres}</p>}
          </div>

          {/* Créditos */}
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Créditos Requeridos *
            </label>
            <input
              type="number"
              min="1"
              value={formData.creditosRequeridos}
              onChange={(e) => handleChange('creditosRequeridos', parseInt(e.target.value))}
              className={`w-full px-4 py-2 border rounded-lg dark:bg-gray-700 dark:text-white ${
                errores.creditosRequeridos ? 'border-red-500' : 'border-gray-300 dark:border-gray-600'
              }`}
            />
            {errores.creditosRequeridos && <p className="text-red-500 text-sm mt-1">{errores.creditosRequeridos}</p>}
          </div>

          {/* Checkboxes */}
          <div className="md:col-span-2 space-y-3">
            <label className="flex items-center gap-2">
              <input
                type="checkbox"
                checked={formData.requiereProyectoGrado}
                onChange={(e) => handleChange('requiereProyectoGrado', e.target.checked)}
                className="w-4 h-4 text-purple-600"
              />
              <span className="text-gray-700 dark:text-gray-300">Requiere proyecto de grado</span>
            </label>

            <label className="flex items-center gap-2">
              <input
                type="checkbox"
                checked={formData.requierePracticas}
                onChange={(e) => handleChange('requierePracticas', e.target.checked)}
                className="w-4 h-4 text-purple-600"
              />
              <span className="text-gray-700 dark:text-gray-300">Requiere prácticas profesionales</span>
            </label>
          </div>

          {/* Horas de prácticas */}
          {formData.requierePracticas && (
            <div className="md:col-span-2">
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Horas de Prácticas *
              </label>
              <input
                type="number"
                min="1"
                value={formData.horasPracticas || ''}
                onChange={(e) => handleChange('horasPracticas', parseInt(e.target.value))}
                className={`w-full px-4 py-2 border rounded-lg dark:bg-gray-700 dark:text-white ${
                  errores.horasPracticas ? 'border-red-500' : 'border-gray-300 dark:border-gray-600'
                }`}
              />
              {errores.horasPracticas && <p className="text-red-500 text-sm mt-1">{errores.horasPracticas}</p>}
            </div>
          )}
        </div>

        {/* Botones */}
        <div className="flex gap-4 mt-8">
          <button
            type="submit"
            disabled={crearPrograma.isPending || actualizarPrograma.isPending}
            className="flex-1 flex items-center justify-center gap-2 px-6 py-3 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition disabled:opacity-50"
          >
            <FaSave />
            {crearPrograma.isPending || actualizarPrograma.isPending
              ? 'Guardando...'
              : esEdicion
              ? 'Guardar Cambios'
              : 'Crear Programa'}
          </button>
          
          <button
            type="button"
            onClick={() => navigate('/admin/programas')}
            className="px-6 py-3 bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-300 dark:hover:bg-gray-600 transition flex items-center gap-2"
          >
            <X /> Cancelar
          </button>
        </div>
      </form>
    </div>
  );
}

export default FormularioPrograma;
