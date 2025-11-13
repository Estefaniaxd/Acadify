/**
 * Página pública para que un coordinador acepte una invitación
 * 
 * Ruta: /registro-coordinador?codigo=XXXXXX
 * 
 * Funcionalidad:
 * 1. Obtiene código de invitación de la URL
 * 2. Valida el código con el backend
 * 3. Muestra información de la institución
 * 4. Formulario de registro (nombre, apellido, password)
 * 5. Envía datos al backend para crear usuario
 * 6. Redirige al login tras éxito
 */

import { useState, useEffect, useCallback } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import { Building, User, Lock, Loader, X, Check, AlertCircle } from 'lucide-react';
import { invitacionService } from '../../modules/invitaciones/services/invitacionService';
import type { InvitacionInfo } from '../../modules/instituciones/types';

export function RegistroCoordinadorPage() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  
  const codigo = searchParams.get('codigo') || '';
  
  const [invitacionInfo, setInvitacionInfo] = useState<InvitacionInfo | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  const [formData, setFormData] = useState({
    nombre: '',
    apellido: '',
    password: '',
    confirmPassword: '',
  });

  const [submitting, setSubmitting] = useState(false);
  const [validationErrors, setValidationErrors] = useState<Record<string, string>>({});

  const validarCodigo = useCallback(async () => {
    try {
      setLoading(true);
      const data = await invitacionService.validarCodigo(codigo);
      
      if (data.valido) {
        setInvitacionInfo(data);
        setError(null);
      } else {
        setError('Código de invitación inválido o expirado');
      }
    } catch (err) {
      const error = err as Error;
      setError(error.message || 'Error al validar el código de invitación');
    } finally {
      setLoading(false);
    }
  }, [codigo]);

  useEffect(() => {
    if (codigo) {
      validarCodigo();
    } else {
      setError('No se proporcionó un código de invitación');
      setLoading(false);
    }
  }, [codigo, validarCodigo]);

  const validateForm = (): boolean => {
    const errors: Record<string, string> = {};

    if (!formData.nombre.trim()) {
      errors.nombre = 'El nombre es requerido';
    }

    if (!formData.apellido.trim()) {
      errors.apellido = 'El apellido es requerido';
    }

    if (formData.password.length < 8) {
      errors.password = 'La contraseña debe tener al menos 8 caracteres';
    }

    if (formData.password !== formData.confirmPassword) {
      errors.confirmPassword = 'Las contraseñas no coinciden';
    }

    setValidationErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!validateForm()) {
      return;
    }

    try {
      setSubmitting(true);
      setError(null);
      
      const result = await invitacionService.aceptar({
        codigo,
        nombre: formData.nombre,
        apellido: formData.apellido,
        password: formData.password,
      });

      if (result.success) {
        // Mostrar mensaje de éxito
        alert(`¡Registro exitoso! Bienvenido ${result.usuario.nombre}. Ya puedes iniciar sesión con tu correo: ${result.usuario.email}`);
        
        // Redirigir al login
        navigate('/login');
      }
    } catch (err) {
      const error = err as Error;
      setError(error.message || 'Error al completar el registro');
    } finally {
      setSubmitting(false);
    }
  };

  // Estado de carga
  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-violet-50 via-white to-purple-50 dark:from-neutral-950 dark:via-violet-950/20 dark:to-neutral-900">
        <div className="text-center">
          <Loader className="w-12 h-12 animate-spin text-blue-600 mx-auto mb-4" />
          <p className="text-gray-600 dark:text-gray-400">Validando código de invitación...</p>
        </div>
      </div>
    );
  }

  // Estado de error (código inválido)
  if (error && !invitacionInfo) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-900 p-4">
        <div className="max-w-md w-full bg-white dark:bg-gray-800 shadow-lg rounded-lg p-8">
          <div className="text-center">
            <div className="mx-auto flex items-center justify-center h-12 w-12 rounded-full bg-red-100 dark:bg-red-900/20 mb-4">
              <X className="h-6 w-6 text-red-600 dark:text-red-400" />
            </div>
            <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">
              Código Inválido
            </h2>
            <p className="text-gray-600 dark:text-gray-400 mb-6">{error}</p>
            <button
              onClick={() => navigate('/login')}
              className="w-full bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors"
            >
              Ir al Login
            </button>
          </div>
        </div>
      </div>
    );
  }

  // Formulario de registro
  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-violet-50 via-white to-purple-50 dark:from-neutral-950 dark:via-violet-950/20 dark:to-neutral-900 py-12 px-4">
      <div className="max-w-md w-full space-y-8">
        {/* Header */}
        <div className="text-center">
          <Building className="mx-auto h-12 w-12 text-blue-600" />
          <h2 className="mt-6 text-3xl font-extrabold text-gray-900 dark:text-white">
            Registro de Coordinador
          </h2>
          <p className="mt-2 text-sm text-gray-600 dark:text-gray-400">
            Has sido invitado a gestionar
          </p>
        </div>

        {/* Información de la institución */}
        {invitacionInfo && (
          <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-4">
            <h3 className="font-semibold text-lg text-blue-900 dark:text-blue-100">
              {invitacionInfo.institucion.nombre}
            </h3>
            {invitacionInfo.institucion.sigla && (
              <p className="text-sm text-blue-700 dark:text-blue-300">
                ({invitacionInfo.institucion.sigla})
              </p>
            )}
            <div className="mt-2 text-sm text-blue-600 dark:text-blue-400 space-y-1">
              {invitacionInfo.institucion.tipo_institucion && (
                <p>Tipo: {invitacionInfo.institucion.tipo_institucion}</p>
              )}
              {invitacionInfo.institucion.nivel_educativo && (
                <p>Nivel: {invitacionInfo.institucion.nivel_educativo}</p>
              )}
              {invitacionInfo.institucion.ciudad && (
                <p>
                  Ubicación: {invitacionInfo.institucion.ciudad}, {invitacionInfo.institucion.pais}
                </p>
              )}
            </div>
            <div className="mt-3 text-xs text-gray-600 dark:text-gray-400 bg-white dark:bg-gray-800 p-2 rounded">
              <p>
                <strong>Email:</strong> {invitacionInfo.invitacion.email_destino}
              </p>
              <p>
                <strong>Código:</strong> {invitacionInfo.invitacion.codigo}
              </p>
            </div>
          </div>
        )}

        {/* Formulario de registro */}
        <form className="mt-8 space-y-6" onSubmit={handleSubmit}>
          <div className="space-y-4">
            {/* Nombre */}
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Nombre(s) <span className="text-red-500">*</span>
              </label>
              <div className="relative">
                <User className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                <input
                  type="text"
                  required
                  value={formData.nombre}
                  onChange={(e) => setFormData({ ...formData, nombre: e.target.value })}
                  className={`w-full pl-10 pr-4 py-2 border ${
                    validationErrors.nombre ? 'border-red-500' : 'border-gray-300 dark:border-gray-600'
                  } rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500`}
                  placeholder="Juan Carlos"
                />
              </div>
              {validationErrors.nombre && (
                <p className="mt-1 text-sm text-red-600 dark:text-red-400">{validationErrors.nombre}</p>
              )}
            </div>

            {/* Apellido */}
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Apellido(s) <span className="text-red-500">*</span>
              </label>
              <div className="relative">
                <User className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                <input
                  type="text"
                  required
                  value={formData.apellido}
                  onChange={(e) => setFormData({ ...formData, apellido: e.target.value })}
                  className={`w-full pl-10 pr-4 py-2 border ${
                    validationErrors.apellido ? 'border-red-500' : 'border-gray-300 dark:border-gray-600'
                  } rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500`}
                  placeholder="Pérez Gómez"
                />
              </div>
              {validationErrors.apellido && (
                <p className="mt-1 text-sm text-red-600 dark:text-red-400">{validationErrors.apellido}</p>
              )}
            </div>

            {/* Contraseña */}
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Contraseña <span className="text-red-500">*</span>
              </label>
              <div className="relative">
                <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                <input
                  type="password"
                  required
                  minLength={8}
                  value={formData.password}
                  onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                  className={`w-full pl-10 pr-4 py-2 border ${
                    validationErrors.password ? 'border-red-500' : 'border-gray-300 dark:border-gray-600'
                  } rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500`}
                  placeholder="Mínimo 8 caracteres"
                />
              </div>
              {validationErrors.password && (
                <p className="mt-1 text-sm text-red-600 dark:text-red-400">{validationErrors.password}</p>
              )}
            </div>

            {/* Confirmar contraseña */}
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Confirmar Contraseña <span className="text-red-500">*</span>
              </label>
              <div className="relative">
                <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                <input
                  type="password"
                  required
                  value={formData.confirmPassword}
                  onChange={(e) => setFormData({ ...formData, confirmPassword: e.target.value })}
                  className={`w-full pl-10 pr-4 py-2 border ${
                    validationErrors.confirmPassword ? 'border-red-500' : 'border-gray-300 dark:border-gray-600'
                  } rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500`}
                  placeholder="Repite tu contraseña"
                />
              </div>
              {validationErrors.confirmPassword && (
                <p className="mt-1 text-sm text-red-600 dark:text-red-400">
                  {validationErrors.confirmPassword}
                </p>
              )}
            </div>
          </div>

          {/* Mensajes de error general */}
          {error && (
            <div className="p-3 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg flex items-start gap-2">
              <AlertCircle className="w-5 h-5 text-red-600 dark:text-red-400 flex-shrink-0 mt-0.5" />
              <p className="text-sm text-red-800 dark:text-red-200">{error}</p>
            </div>
          )}

          {/* Indicadores de validación de contraseña */}
          {formData.password && (
            <div className="text-xs text-gray-600 dark:text-gray-400 space-y-1">
              <p className={formData.password.length >= 8 ? 'text-green-600 dark:text-green-400' : ''}>
                {formData.password.length >= 8 ? '✓' : '○'} Mínimo 8 caracteres
              </p>
              <p
                className={
                  formData.password === formData.confirmPassword && formData.confirmPassword
                    ? 'text-green-600 dark:text-green-400'
                    : ''
                }
              >
                {formData.password === formData.confirmPassword && formData.confirmPassword ? '✓' : '○'}{' '}
                Las contraseñas coinciden
              </p>
            </div>
          )}

          {/* Botón submit */}
          <button
            type="submit"
            disabled={submitting}
            className="w-full flex justify-center items-center gap-2 py-3 px-4 border border-transparent text-sm font-medium rounded-lg text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            {submitting ? (
              <>
                <Loader className="w-4 h-4 animate-spin" />
                Registrando...
              </>
            ) : (
              <>
                <Check className="w-4 h-4" />
                Completar Registro
              </>
            )}
          </button>
        </form>

        {/* Link a login */}
        <div className="text-center">
          <p className="text-sm text-gray-600 dark:text-gray-400">
            ¿Ya tienes cuenta?{' '}
            <button
              onClick={() => navigate('/login')}
              className="font-medium text-blue-600 hover:text-blue-500"
            >
              Iniciar sesión
            </button>
          </p>
        </div>
      </div>
    </div>
  );
}
