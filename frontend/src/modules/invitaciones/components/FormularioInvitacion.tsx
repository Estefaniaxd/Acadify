/**
 * FormularioInvitacion - Modal para crear invitaciones
 * Permite al admin invitar coordinadores, profesores o estudiantes
 */

import React, { useState } from 'react';
import { useForm } from 'react-hook-form';
import { X, Send, Mail, User, MessageSquare, AlertCircle, CheckCircle2 } from 'lucide-react';
import { useToast } from '../../../context/ToastContext';
import { useCrearInvitacion } from '../hooks/useInvitaciones';
import type { CrearInvitacionDTO, RolInvitacion } from '../types';

interface FormularioInvitacionProps {
  isOpen: boolean;
  onClose: () => void;
  institucionId: number;
  programaId?: number;
  rolPredeterminado?: RolInvitacion;
}

interface FormData {
  email: string;
  nombreInvitado: string;
  rol: RolInvitacion;
  mensaje?: string;
  diasExpiracion?: number;
}

export default function FormularioInvitacion({
  isOpen,
  onClose,
  institucionId,
  programaId,
  rolPredeterminado,
}: FormularioInvitacionProps) {
  const toast = useToast();
  const [codigoGenerado, setCodigoGenerado] = useState<string | null>(null);
  const [emailEnviado, setEmailEnviado] = useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors },
    reset,
    watch,
  } = useForm<FormData>({
    defaultValues: {
      rol: rolPredeterminado || 'COORDINADOR',
      diasExpiracion: 7,
    },
  });

  const crearMutation = useCrearInvitacion(toast);

  const onSubmit = async (data: FormData) => {
    const dto: CrearInvitacionDTO = {
      email: data.email,
      nombreInvitado: data.nombreInvitado,
      rol: data.rol,
      institucionId,
      programaId,
      mensaje: data.mensaje,
      diasExpiracion: data.diasExpiracion,
    };

    crearMutation.mutate(dto, {
      onSuccess: (response) => {
        setCodigoGenerado(response.invitacion.codigo);
        setEmailEnviado(response.emailEnviado);
      },
    });
  };

  const handleClose = () => {
    reset();
    setCodigoGenerado(null);
    setEmailEnviado(false);
    onClose();
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm">
      <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-2xl w-full max-w-2xl max-h-[90vh] overflow-hidden">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200 dark:border-gray-700">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-blue-100 dark:bg-blue-900/30 rounded-lg">
              <Send className="w-6 h-6 text-blue-600 dark:text-blue-400" />
            </div>
            <div>
              <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
                {codigoGenerado ? 'Invitación Creada' : 'Nueva Invitación'}
              </h2>
              <p className="text-sm text-gray-500 dark:text-gray-400">
                {codigoGenerado
                  ? 'La invitación se ha generado exitosamente'
                  : 'Invita a un usuario a unirse a la institución'}
              </p>
            </div>
          </div>
          <button
            onClick={handleClose}
            className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
          >
            <X className="w-5 h-5 text-gray-500" />
          </button>
        </div>

        {/* Content */}
        <div className="p-6 overflow-y-auto max-h-[calc(90vh-180px)]">
          {codigoGenerado ? (
            // Vista de éxito con código
            <div className="space-y-6">
              {/* Estado del envío */}
              <div
                className={`p-4 rounded-xl border-2 ${
                  emailEnviado
                    ? 'bg-green-50 dark:bg-green-900/20 border-green-200 dark:border-green-800'
                    : 'bg-yellow-50 dark:bg-yellow-900/20 border-yellow-200 dark:border-yellow-800'
                }`}
              >
                <div className="flex items-start gap-3">
                  {emailEnviado ? (
                    <CheckCircle2 className="w-6 h-6 text-green-600 dark:text-green-400 flex-shrink-0 mt-0.5" />
                  ) : (
                    <AlertCircle className="w-6 h-6 text-yellow-600 dark:text-yellow-400 flex-shrink-0 mt-0.5" />
                  )}
                  <div>
                    <p className="font-semibold text-gray-900 dark:text-white">
                      {emailEnviado
                        ? 'Email enviado correctamente'
                        : 'Email no enviado'}
                    </p>
                    <p className="text-sm text-gray-600 dark:text-gray-300 mt-1">
                      {emailEnviado
                        ? `Se ha enviado el email a ${watch('email')} con las instrucciones para aceptar la invitación.`
                        : 'No se pudo enviar el email automáticamente. Comparte el código manualmente con el usuario.'}
                    </p>
                  </div>
                </div>
              </div>

              {/* Código generado */}
              <div className="p-6 bg-gradient-to-br from-blue-50 to-indigo-50 dark:from-blue-900/20 dark:to-indigo-900/20 rounded-xl border border-blue-200 dark:border-blue-800">
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Código de Invitación
                </label>
                <div className="flex items-center gap-3">
                  <div className="flex-1 p-4 bg-white dark:bg-gray-800 rounded-lg border-2 border-blue-300 dark:border-blue-600">
                    <p className="text-3xl font-mono font-bold text-center text-blue-600 dark:text-blue-400 tracking-widest">
                      {codigoGenerado}
                    </p>
                  </div>
                  <button
                    onClick={() => {
                      navigator.clipboard.writeText(codigoGenerado);
                      toast.success('Código copiado', 'El código ha sido copiado al portapapeles');
                    }}
                    className="px-4 py-3 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors font-medium"
                  >
                    Copiar
                  </button>
                </div>
                <p className="text-xs text-gray-500 dark:text-gray-400 mt-2">
                  Este código es válido por {watch('diasExpiracion') || 7} días
                </p>
              </div>

              {/* Información del invitado */}
              <div className="grid grid-cols-2 gap-4 p-4 bg-gray-50 dark:bg-gray-700/50 rounded-lg">
                <div>
                  <p className="text-xs text-gray-500 dark:text-gray-400">Nombre</p>
                  <p className="font-medium text-gray-900 dark:text-white">
                    {watch('nombreInvitado')}
                  </p>
                </div>
                <div>
                  <p className="text-xs text-gray-500 dark:text-gray-400">Email</p>
                  <p className="font-medium text-gray-900 dark:text-white">
                    {watch('email')}
                  </p>
                </div>
                <div>
                  <p className="text-xs text-gray-500 dark:text-gray-400">Rol</p>
                  <p className="font-medium text-gray-900 dark:text-white capitalize">
                    {watch('rol')}
                  </p>
                </div>
                <div>
                  <p className="text-xs text-gray-500 dark:text-gray-400">Expira en</p>
                  <p className="font-medium text-gray-900 dark:text-white">
                    {watch('diasExpiracion')} días
                  </p>
                </div>
              </div>

              {/* Instrucciones */}
              <div className="p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg border border-blue-200 dark:border-blue-800">
                <p className="text-sm font-medium text-gray-900 dark:text-white mb-2">
                  📋 Siguiente paso:
                </p>
                <ol className="text-sm text-gray-600 dark:text-gray-300 space-y-1 ml-4 list-decimal">
                  <li>El usuario recibirá un email con el enlace de invitación</li>
                  <li>Deberá ingresar el código de 6 dígitos para validar</li>
                  <li>Completará sus datos para crear su cuenta</li>
                  <li>Una vez aceptada, tendrá acceso con el rol asignado</li>
                </ol>
              </div>
            </div>
          ) : (
            // Formulario de creación
            <form onSubmit={handleSubmit(onSubmit)} className="space-y-5">
              {/* Email */}
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1.5">
                  Email del invitado *
                </label>
                <div className="relative">
                  <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                  <input
                    type="email"
                    {...register('email', {
                      required: 'El email es obligatorio',
                      pattern: {
                        value: /^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$/i,
                        message: 'Email inválido',
                      },
                    })}
                    placeholder="ejemplo@correo.com"
                    className="w-full pl-10 pr-4 py-2.5 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-400 focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-shadow"
                  />
                </div>
                {errors.email && (
                  <p className="mt-1 text-sm text-red-600 dark:text-red-400">
                    {errors.email.message}
                  </p>
                )}
              </div>

              {/* Nombre */}
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1.5">
                  Nombre completo *
                </label>
                <div className="relative">
                  <User className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                  <input
                    type="text"
                    {...register('nombreInvitado', {
                      required: 'El nombre es obligatorio',
                      minLength: {
                        value: 3,
                        message: 'Mínimo 3 caracteres',
                      },
                    })}
                    placeholder="Juan Pérez"
                    className="w-full pl-10 pr-4 py-2.5 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-400 focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-shadow"
                  />
                </div>
                {errors.nombreInvitado && (
                  <p className="mt-1 text-sm text-red-600 dark:text-red-400">
                    {errors.nombreInvitado.message}
                  </p>
                )}
              </div>

              {/* Rol */}
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1.5">
                  Rol *
                </label>
                <select
                  {...register('rol', { required: 'Selecciona un rol' })}
                  disabled={!!rolPredeterminado}
                  className="w-full px-4 py-2.5 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-shadow disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  <option value="COORDINADOR">Coordinador</option>
                  <option value="PROFESOR">Profesor</option>
                  <option value="ESTUDIANTE">Estudiante</option>
                </select>
                {errors.rol && (
                  <p className="mt-1 text-sm text-red-600 dark:text-red-400">
                    {errors.rol.message}
                  </p>
                )}
              </div>

              {/* Días de expiración */}
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1.5">
                  Días de validez
                </label>
                <select
                  {...register('diasExpiracion')}
                  className="w-full px-4 py-2.5 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-shadow"
                >
                  <option value={3}>3 días</option>
                  <option value={7}>7 días (recomendado)</option>
                  <option value={15}>15 días</option>
                  <option value={30}>30 días</option>
                </select>
              </div>

              {/* Mensaje opcional */}
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1.5">
                  Mensaje personalizado (opcional)
                </label>
                <div className="relative">
                  <MessageSquare className="absolute left-3 top-3 w-5 h-5 text-gray-400" />
                  <textarea
                    {...register('mensaje')}
                    rows={3}
                    placeholder="Agrega un mensaje personalizado para el invitado..."
                    className="w-full pl-10 pr-4 py-2.5 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-400 focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-shadow resize-none"
                  />
                </div>
              </div>

              {/* Info box */}
              <div className="p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg border border-blue-200 dark:border-blue-800">
                <p className="text-sm text-gray-600 dark:text-gray-300">
                  💡 <strong>Nota:</strong> Se enviará automáticamente un email al usuario con el
                  código de invitación y las instrucciones para registrarse.
                </p>
              </div>
            </form>
          )}
        </div>

        {/* Footer */}
        <div className="flex items-center justify-end gap-3 p-6 border-t border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-800/50">
          {codigoGenerado ? (
            <>
              <button
                onClick={handleClose}
                className="px-6 py-2.5 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors font-medium"
              >
                Finalizar
              </button>
            </>
          ) : (
            <>
              <button
                type="button"
                onClick={handleClose}
                disabled={crearMutation.isPending}
                className="px-6 py-2.5 border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors font-medium disabled:opacity-50"
              >
                Cancelar
              </button>
              <button
                onClick={handleSubmit(onSubmit)}
                disabled={crearMutation.isPending}
                className="px-6 py-2.5 bg-blue-600 hover:bg-blue-700 disabled:bg-blue-400 text-white rounded-lg transition-colors font-medium flex items-center gap-2 disabled:cursor-not-allowed"
              >
                {crearMutation.isPending ? (
                  <>
                    <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                    Enviando...
                  </>
                ) : (
                  <>
                    <Send className="w-4 h-4" />
                    Enviar Invitación
                  </>
                )}
              </button>
            </>
          )}
        </div>
      </div>
    </div>
  );
}
