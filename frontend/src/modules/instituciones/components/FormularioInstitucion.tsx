/**
 * FormularioInstitucion Component
 * Formulario para crear o editar instituciones
 * Principio SRP: Solo maneja el formulario, validación y envío
 */

import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useCrearInstitucion, useActualizarInstitucion, useInstitucion } from '../hooks/useInstituciones';
import FormularioInvitacion from '../../invitaciones/components/FormularioInvitacion';
import type { CrearInstitucionDTO } from '../types';
import type { Institucion } from '../types';
import { Building, Loader2, Save, Upload, X } from 'lucide-react';

interface FormularioInstitucionProps {
  institucionId?: string;
  modo?: 'crear' | 'editar';
}

export function FormularioInstitucion({ institucionId, modo = 'crear' }: FormularioInstitucionProps) {
  const navigate = useNavigate();
  
  const { data: institucion, isLoading: cargandoInstitucion } = useInstitucion(institucionId);
  const crearMutation = useCrearInstitucion();
  const actualizarMutation = useActualizarInstitucion();

  const [formData, setFormData] = useState<CrearInstitucionDTO>({
    nombre: '',
    descripcion: '',
    direccion: '',
    telefono: '',
    email: '',
    sitioWeb: '',
    colorPrimario: '#3B82F6',
    colorSecundario: '#8B5CF6',
  });

  const [logoPreview, setLogoPreview] = useState<string | null>(null);
  const [errors, setErrors] = useState<Record<string, string>>({});
  
  // Estado para el modal de invitación
  const [mostrarModalInvitacion, setMostrarModalInvitacion] = useState(false);
  const [institucionCreada, setInstitucionCreada] = useState<Institucion | null>(null);

  // Cargar datos si estamos editando
  useEffect(() => {
    if (modo === 'editar' && institucion) {
      setFormData({
        nombre: institucion.nombre,
        descripcion: institucion.descripcion || '',
        direccion: institucion.direccion || '',
        telefono: institucion.telefono || '',
        email: institucion.email || '',
        sitioWeb: institucion.sitioWeb || '',
        colorPrimario: institucion.colorPrimario || '#3B82F6',
        colorSecundario: institucion.colorSecundario || '#8B5CF6',
        logo: institucion.logo,
      });
      if (institucion.logo) {
        setLogoPreview(institucion.logo);
      }
    }
  }, [institucion, modo]);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
    
    // Limpiar error del campo
    if (errors[name]) {
      setErrors((prev) => {
        const newErrors = { ...prev };
        delete newErrors[name];
        return newErrors;
      });
    }
  };

  const handleLogoChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      // Validar tamaño (máximo 5MB)
      if (file.size > 5 * 1024 * 1024) {
        setErrors((prev) => ({ ...prev, logo: 'El logo no debe superar 5MB' }));
        return;
      }

      // Validar tipo
      if (!file.type.startsWith('image/')) {
        setErrors((prev) => ({ ...prev, logo: 'El archivo debe ser una imagen' }));
        return;
      }

      // Preview
      const reader = new FileReader();
      reader.onloadend = () => {
        setLogoPreview(reader.result as string);
      };
      reader.readAsDataURL(file);

      setFormData((prev) => ({ ...prev, logo: reader.result as string }));
    }
  };

  const validate = (): boolean => {
    const newErrors: Record<string, string> = {};

    if (!formData.nombre.trim()) {
      newErrors.nombre = 'El nombre es requerido';
    } else if (formData.nombre.length < 3) {
      newErrors.nombre = 'El nombre debe tener al menos 3 caracteres';
    }

    if (formData.email && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
      newErrors.email = 'Email inválido';
    }

    if (formData.telefono && !/^\+?[\d\s-()]+$/.test(formData.telefono)) {
      newErrors.telefono = 'Teléfono inválido';
    }

    if (formData.sitioWeb && !/^https?:\/\/.+/.test(formData.sitioWeb)) {
      newErrors.sitioWeb = 'URL inválida (debe comenzar con http:// o https://)';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!validate()) {
      return;
    }

    try {
      if (modo === 'crear') {
        const nuevaInstitucion = await crearMutation.mutateAsync(formData);
        
        // Mostrar modal para invitar coordinador
        setInstitucionCreada(nuevaInstitucion);
        setMostrarModalInvitacion(true);
      } else if (institucionId) {
        await actualizarMutation.mutateAsync({
          id: institucionId,
          data: formData,
        });
        alert('Institución actualizada exitosamente');
        navigate(`/admin/instituciones/${institucionId}`);
      }
    } catch (error: any) {
      alert(error.message || 'Error al guardar institución');
    }
  };

  const handleCerrarModalInvitacion = () => {
    setMostrarModalInvitacion(false);
    // Navegar después de cerrar el modal
    navigate('/admin/instituciones');
  };

  const isLoading = crearMutation.isPending || actualizarMutation.isPending;

  if (modo === 'editar' && cargandoInstitucion) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader2 className="w-8 h-8 animate-spin text-blue-600" />
      </div>
    );
  }

  return (
    <div className="p-6 max-w-4xl mx-auto">
      {/* Header */}
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white flex items-center gap-2">
          <Building className="w-8 h-8" />
          {modo === 'crear' ? 'Nueva Institución' : 'Editar Institución'}
        </h1>
        <p className="text-gray-600 dark:text-gray-400 mt-1">
          {modo === 'crear'
            ? 'Completa los datos para crear una nueva institución'
            : 'Actualiza la información de la institución'}
        </p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Card principal */}
        <div className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg p-6 space-y-6">
          {/* Logo */}
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Logo de la Institución
            </label>
            <div className="flex items-center gap-4">
              {logoPreview ? (
                <img
                  src={logoPreview}
                  alt="Preview"
                  className="w-24 h-24 rounded-lg object-cover border-2 border-gray-300 dark:border-gray-600"
                />
              ) : (
                <div className="w-24 h-24 rounded-lg border-2 border-dashed border-gray-300 dark:border-gray-600 flex items-center justify-center">
                  <Building className="w-12 h-12 text-gray-400" />
                </div>
              )}
              <div>
                <label className="cursor-pointer inline-flex items-center gap-2 px-4 py-2 bg-blue-50 dark:bg-blue-900/20 text-blue-600 dark:text-blue-400 rounded-lg hover:bg-blue-100 dark:hover:bg-blue-900/30 transition-colors">
                  <Upload className="w-5 h-5" />
                  Subir Logo
                  <input
                    type="file"
                    accept="image/*"
                    onChange={handleLogoChange}
                    className="hidden"
                  />
                </label>
                <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                  PNG, JPG hasta 5MB
                </p>
              </div>
            </div>
            {errors.logo && <p className="text-red-600 text-sm mt-1">{errors.logo}</p>}
          </div>

          {/* Información básica */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="md:col-span-2">
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Nombre de la Institución *
              </label>
              <input
                type="text"
                name="nombre"
                value={formData.nombre}
                onChange={handleChange}
                className={`w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 ${
                  errors.nombre
                    ? 'border-red-500'
                    : 'border-gray-300 dark:border-gray-600'
                } bg-white dark:bg-gray-700`}
                placeholder="Ej: Universidad Nacional"
              />
              {errors.nombre && <p className="text-red-600 text-sm mt-1">{errors.nombre}</p>}
            </div>

            <div className="md:col-span-2">
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Descripción
              </label>
              <textarea
                name="descripcion"
                value={formData.descripcion}
                onChange={handleChange}
                rows={3}
                className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 bg-white dark:bg-gray-700"
                placeholder="Descripción breve de la institución"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Email
              </label>
              <input
                type="email"
                name="email"
                value={formData.email}
                onChange={handleChange}
                className={`w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 ${
                  errors.email
                    ? 'border-red-500'
                    : 'border-gray-300 dark:border-gray-600'
                } bg-white dark:bg-gray-700`}
                placeholder="contacto@institucion.edu"
              />
              {errors.email && <p className="text-red-600 text-sm mt-1">{errors.email}</p>}
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Teléfono
              </label>
              <input
                type="tel"
                name="telefono"
                value={formData.telefono}
                onChange={handleChange}
                className={`w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 ${
                  errors.telefono
                    ? 'border-red-500'
                    : 'border-gray-300 dark:border-gray-600'
                } bg-white dark:bg-gray-700`}
                placeholder="+57 123 456 7890"
              />
              {errors.telefono && <p className="text-red-600 text-sm mt-1">{errors.telefono}</p>}
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Sitio Web
              </label>
              <input
                type="url"
                name="sitioWeb"
                value={formData.sitioWeb}
                onChange={handleChange}
                className={`w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 ${
                  errors.sitioWeb
                    ? 'border-red-500'
                    : 'border-gray-300 dark:border-gray-600'
                } bg-white dark:bg-gray-700`}
                placeholder="https://institucion.edu"
              />
              {errors.sitioWeb && <p className="text-red-600 text-sm mt-1">{errors.sitioWeb}</p>}
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Dirección
              </label>
              <input
                type="text"
                name="direccion"
                value={formData.direccion}
                onChange={handleChange}
                className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 bg-white dark:bg-gray-700"
                placeholder="Calle 123 #45-67"
              />
            </div>
          </div>

          {/* Personalización de colores */}
          <div>
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
              Personalización
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Color Primario
                </label>
                <div className="flex items-center gap-3">
                  <input
                    type="color"
                    name="colorPrimario"
                    value={formData.colorPrimario}
                    onChange={handleChange}
                    className="h-10 w-20 cursor-pointer rounded border border-gray-300"
                  />
                  <input
                    type="text"
                    value={formData.colorPrimario}
                    onChange={(e) => setFormData((prev) => ({ ...prev, colorPrimario: e.target.value }))}
                    className="flex-1 px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700"
                    placeholder="#3B82F6"
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Color Secundario
                </label>
                <div className="flex items-center gap-3">
                  <input
                    type="color"
                    name="colorSecundario"
                    value={formData.colorSecundario}
                    onChange={handleChange}
                    className="h-10 w-20 cursor-pointer rounded border border-gray-300"
                  />
                  <input
                    type="text"
                    value={formData.colorSecundario}
                    onChange={(e) => setFormData((prev) => ({ ...prev, colorSecundario: e.target.value }))}
                    className="flex-1 px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700"
                    placeholder="#8B5CF6"
                  />
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Acciones */}
        <div className="flex items-center justify-end gap-4">
          <button
            type="button"
            onClick={() => navigate(-1)}
            className="px-6 py-2 border border-gray-300 dark:border-gray-600 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors flex items-center gap-2"
          >
            <X className="w-5 h-5" />
            Cancelar
          </button>
          <button
            type="submit"
            disabled={isLoading}
            className="px-6 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isLoading ? (
              <Loader2 className="w-5 h-5 animate-spin" />
            ) : (
              <Save className="w-5 h-5" />
            )}
            {modo === 'crear' ? 'Crear Institución' : 'Guardar Cambios'}
          </button>
        </div>
      </form>

      {/* Modal para invitar coordinador después de crear institución */}
      {institucionCreada && (
        <FormularioInvitacion
          isOpen={mostrarModalInvitacion}
          onClose={handleCerrarModalInvitacion}
          institucionId={institucionCreada.id}
          rolPredeterminado="COORDINADOR"
        />
      )}
    </div>
  );
}
