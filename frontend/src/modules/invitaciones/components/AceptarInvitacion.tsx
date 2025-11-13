/**
 * AceptarInvitacion - Página pública para aceptar invitaciones
 * Flujo de 4 pasos: Validar token → Ingresar código → Crear cuenta → Éxito
 */

import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { 
  Mail, Lock, User, Phone, Calendar, Eye, EyeOff, 
  CheckCircle2, AlertCircle, Loader2, ArrowRight, Shield 
} from 'lucide-react';
import { useForm } from 'react-hook-form';
import { useToast } from '../../../context/ToastContext';
import { useValidarToken, useAceptarInvitacion, useRechazarInvitacion } from '../hooks/useInvitaciones';
import type { AceptarInvitacionDTO } from '../types';

type Paso = 'validando' | 'codigo' | 'formulario' | 'exito' | 'error';

interface FormDataCuenta {
  nombre: string;
  apellido: string;
  telefono?: string;
  documento?: string;
  fechaNacimiento?: string;
  password: string;
  passwordConfirm: string;
}

export default function AceptarInvitacion() {
  const { token } = useParams<{ token: string }>();
  const navigate = useNavigate();
  const toast = useToast();

  const [paso, setPaso] = useState<Paso>('validando');
  const [codigo, setCodigo] = useState(['', '', '', '', '', '']);
  const [codigoError, setCodigoError] = useState(false);
  const [mostrarPassword, setMostrarPassword] = useState(false);
  const [mostrarPasswordConfirm, setMostrarPasswordConfirm] = useState(false);

  // Queries y mutations
  const { data: validacion, isLoading: validando, error: errorValidacion } = useValidarToken(token || '');
  const aceptarMutation = useAceptarInvitacion(toast);
  const rechazarMutation = useRechazarInvitacion(toast);

  const {
    register,
    handleSubmit,
    formState: { errors },
    watch,
  } = useForm<FormDataCuenta>();

  const password = watch('password');

  // Validar token al cargar
  useEffect(() => {
    if (!token) {
      setPaso('error');
      return;
    }

    if (validacion) {
      if (validacion.valida) {
        setPaso('codigo');
      } else {
        setPaso('error');
      }
    }
  }, [token, validacion]);

  // Manejo del código de 6 dígitos
  const handleCodigoChange = (index: number, value: string) => {
    if (value.length > 1) return; // Solo un dígito
    if (!/^\d*$/.test(value)) return; // Solo números

    const nuevoCodigo = [...codigo];
    nuevoCodigo[index] = value;
    setCodigo(nuevoCodigo);
    setCodigoError(false);

    // Auto-focus al siguiente input
    if (value && index < 5) {
      const nextInput = document.getElementById(`codigo-${index + 1}`);
      nextInput?.focus();
    }
  };

  const handleCodigoKeyDown = (index: number, e: React.KeyboardEvent) => {
    if (e.key === 'Backspace' && !codigo[index] && index > 0) {
      const prevInput = document.getElementById(`codigo-${index - 1}`);
      prevInput?.focus();
    }
  };

  const handleValidarCodigo = () => {
    const codigoCompleto = codigo.join('');
    
    if (codigoCompleto.length !== 6) {
      setCodigoError(true);
      toast.error('Código incompleto', 'Ingresa los 6 dígitos del código');
      return;
    }

    // Aquí solo validamos longitud, la validación real será al enviar el formulario
    setPaso('formulario');
  };

  const onSubmit = async (data: FormDataCuenta) => {
    if (!token) return;

    const dto: AceptarInvitacionDTO = {
      token,
      codigo: codigo.join(''),
      nombre: data.nombre,
      apellido: data.apellido,
      telefono: data.telefono,
      documento: data.documento,
      fechaNacimiento: data.fechaNacimiento,
      password: data.password,
      passwordConfirm: data.passwordConfirm,
    };

    aceptarMutation.mutate(dto, {
      onSuccess: () => {
        setPaso('exito');
      },
      onError: (error: any) => {
        if (error.message.includes('código')) {
          setPaso('codigo');
          setCodigo(['', '', '', '', '', '']);
          setCodigoError(true);
        }
      },
    });
  };

  const handleRechazar = () => {
    if (!token) return;
    
    if (confirm('¿Estás seguro de que deseas rechazar esta invitación?')) {
      rechazarMutation.mutate({ token });
    }
  };

  // Renderizado según el paso
  if (paso === 'validando' || validando) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-indigo-50 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900 flex items-center justify-center p-4">
        <div className="text-center">
          <Loader2 className="w-12 h-12 text-blue-600 animate-spin mx-auto mb-4" />
          <p className="text-lg text-gray-600 dark:text-gray-400">Validando invitación...</p>
        </div>
      </div>
    );
  }

  if (paso === 'error' || errorValidacion || !validacion?.valida) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-red-50 via-white to-orange-50 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900 flex items-center justify-center p-4">
        <div className="max-w-md w-full bg-white dark:bg-gray-800 rounded-2xl shadow-2xl p-8 text-center">
          <div className="w-16 h-16 bg-red-100 dark:bg-red-900/30 rounded-full flex items-center justify-center mx-auto mb-4">
            <AlertCircle className="w-8 h-8 text-red-600 dark:text-red-400" />
          </div>
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">
            Invitación No Válida
          </h2>
          <p className="text-gray-600 dark:text-gray-400 mb-6">
            {validacion?.razon || 'Esta invitación ha expirado, fue cancelada o no existe.'}
          </p>
          <button
            onClick={() => navigate('/')}
            className="w-full px-6 py-3 bg-gray-600 hover:bg-gray-700 text-white rounded-lg transition-colors font-medium"
          >
            Volver al inicio
          </button>
        </div>
      </div>
    );
  }

  if (paso === 'exito') {
    return (
      <div className="min-h-screen bg-gradient-to-br from-green-50 via-white to-emerald-50 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900 flex items-center justify-center p-4">
        <div className="max-w-md w-full bg-white dark:bg-gray-800 rounded-2xl shadow-2xl p-8 text-center">
          <div className="w-16 h-16 bg-green-100 dark:bg-green-900/30 rounded-full flex items-center justify-center mx-auto mb-4">
            <CheckCircle2 className="w-8 h-8 text-green-600 dark:text-green-400" />
          </div>
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">
            ¡Cuenta Creada!
          </h2>
          <p className="text-gray-600 dark:text-gray-400 mb-6">
            Tu cuenta ha sido creada exitosamente. Serás redirigido al dashboard en unos segundos.
          </p>
          <div className="w-12 h-12 border-4 border-green-600 border-t-transparent rounded-full animate-spin mx-auto" />
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-indigo-50 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900 flex items-center justify-center p-4">
      <div className="max-w-2xl w-full">
        {/* Header con info de la invitación */}
        <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-2xl p-8 mb-6">
          <div className="flex items-center gap-4 mb-6">
            <div className="p-3 bg-blue-100 dark:bg-blue-900/30 rounded-xl">
              <Mail className="w-8 h-8 text-blue-600 dark:text-blue-400" />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
                Invitación de {validacion.invitacion?.institucionNombre || 'la institución'}
              </h1>
              <p className="text-gray-600 dark:text-gray-400">
                Has sido invitado como <span className="font-semibold capitalize">{validacion.invitacion?.rol.toLowerCase()}</span>
              </p>
            </div>
          </div>

          {validacion.invitacion?.mensaje && (
            <div className="p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg border border-blue-200 dark:border-blue-800 mb-6">
              <p className="text-sm text-gray-700 dark:text-gray-300">
                "{validacion.invitacion.mensaje}"
              </p>
            </div>
          )}

          {/* Progreso */}
          <div className="flex items-center justify-between mb-8">
            <div className="flex-1 flex items-center">
              <div className={`w-8 h-8 rounded-full flex items-center justify-center ${
                paso === 'codigo' || paso === 'formulario' 
                  ? 'bg-green-500 text-white' 
                  : 'bg-blue-600 text-white'
              }`}>
                {paso === 'codigo' || paso === 'formulario' ? '✓' : '1'}
              </div>
              <div className={`flex-1 h-1 mx-2 ${
                paso === 'formulario' ? 'bg-green-500' : 'bg-gray-300 dark:bg-gray-600'
              }`} />
            </div>
            <div className="flex-1 flex items-center">
              <div className={`w-8 h-8 rounded-full flex items-center justify-center ${
                paso === 'formulario' 
                  ? 'bg-green-500 text-white' 
                  : paso === 'codigo'
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-300 dark:bg-gray-600 text-gray-600'
              }`}>
                {paso === 'formulario' ? '✓' : '2'}
              </div>
            </div>
          </div>

          {/* Paso 1: Código */}
          {paso === 'codigo' && (
            <div className="space-y-6">
              <div className="text-center">
                <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">
                  Ingresa el código de verificación
                </h3>
                <p className="text-gray-600 dark:text-gray-400">
                  Hemos enviado un código de 6 dígitos a {validacion.invitacion?.email}
                </p>
              </div>

              <div className="flex gap-3 justify-center">
                {codigo.map((digit, index) => (
                  <input
                    key={index}
                    id={`codigo-${index}`}
                    type="text"
                    inputMode="numeric"
                    maxLength={1}
                    value={digit}
                    onChange={(e) => handleCodigoChange(index, e.target.value)}
                    onKeyDown={(e) => handleCodigoKeyDown(index, e)}
                    className={`w-14 h-14 text-center text-2xl font-bold border-2 rounded-lg transition-colors ${
                      codigoError
                        ? 'border-red-500 bg-red-50 dark:bg-red-900/20'
                        : 'border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 focus:border-blue-500 focus:ring-2 focus:ring-blue-500'
                    } text-gray-900 dark:text-white`}
                  />
                ))}
              </div>

              {codigoError && (
                <p className="text-center text-sm text-red-600 dark:text-red-400">
                  Código incorrecto. Por favor verifica e intenta nuevamente.
                </p>
              )}

              <div className="flex gap-3">
                <button
                  onClick={handleValidarCodigo}
                  disabled={codigo.join('').length !== 6}
                  className="flex-1 px-6 py-3 bg-blue-600 hover:bg-blue-700 disabled:bg-blue-300 text-white rounded-lg transition-colors font-medium flex items-center justify-center gap-2 disabled:cursor-not-allowed"
                >
                  Continuar
                  <ArrowRight className="w-5 h-5" />
                </button>
              </div>

              <div className="text-center">
                <button
                  onClick={handleRechazar}
                  className="text-sm text-gray-600 dark:text-gray-400 hover:text-red-600 dark:hover:text-red-400 transition-colors"
                >
                  Rechazar invitación
                </button>
              </div>
            </div>
          )}

          {/* Paso 2: Formulario de cuenta */}
          {paso === 'formulario' && (
            <form onSubmit={handleSubmit(onSubmit)} className="space-y-5">
              <div className="text-center mb-6">
                <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">
                  Completa tus datos
                </h3>
                <p className="text-gray-600 dark:text-gray-400">
                  Crea tu cuenta para acceder a la plataforma
                </p>
              </div>

              <div className="grid grid-cols-2 gap-4">
                {/* Nombre */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1.5">
                    Nombre *
                  </label>
                  <div className="relative">
                    <User className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                    <input
                      type="text"
                      {...register('nombre', {
                        required: 'El nombre es obligatorio',
                        minLength: { value: 2, message: 'Mínimo 2 caracteres' },
                      })}
                      className="w-full pl-10 pr-4 py-2.5 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500"
                    />
                  </div>
                  {errors.nombre && (
                    <p className="mt-1 text-sm text-red-600">{errors.nombre.message}</p>
                  )}
                </div>

                {/* Apellido */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1.5">
                    Apellido *
                  </label>
                  <input
                    type="text"
                    {...register('apellido', {
                      required: 'El apellido es obligatorio',
                      minLength: { value: 2, message: 'Mínimo 2 caracteres' },
                    })}
                    className="w-full px-4 py-2.5 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500"
                  />
                  {errors.apellido && (
                    <p className="mt-1 text-sm text-red-600">{errors.apellido.message}</p>
                  )}
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                {/* Teléfono */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1.5">
                    Teléfono
                  </label>
                  <div className="relative">
                    <Phone className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                    <input
                      type="tel"
                      {...register('telefono')}
                      placeholder="+57 300 123 4567"
                      className="w-full pl-10 pr-4 py-2.5 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500"
                    />
                  </div>
                </div>

                {/* Fecha nacimiento */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1.5">
                    Fecha de nacimiento
                  </label>
                  <div className="relative">
                    <Calendar className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                    <input
                      type="date"
                      {...register('fechaNacimiento')}
                      className="w-full pl-10 pr-4 py-2.5 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500"
                    />
                  </div>
                </div>
              </div>

              {/* Documento */}
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1.5">
                  Documento de identidad
                </label>
                <input
                  type="text"
                  {...register('documento')}
                  placeholder="123456789"
                  className="w-full px-4 py-2.5 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500"
                />
              </div>

              {/* Password */}
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1.5">
                  Contraseña *
                </label>
                <div className="relative">
                  <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                  <input
                    type={mostrarPassword ? 'text' : 'password'}
                    {...register('password', {
                      required: 'La contraseña es obligatoria',
                      minLength: { value: 8, message: 'Mínimo 8 caracteres' },
                      pattern: {
                        value: /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)/,
                        message: 'Debe incluir mayúscula, minúscula y número',
                      },
                    })}
                    className="w-full pl-10 pr-12 py-2.5 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500"
                  />
                  <button
                    type="button"
                    onClick={() => setMostrarPassword(!mostrarPassword)}
                    className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600"
                  >
                    {mostrarPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
                  </button>
                </div>
                {errors.password && (
                  <p className="mt-1 text-sm text-red-600">{errors.password.message}</p>
                )}
              </div>

              {/* Confirmar Password */}
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1.5">
                  Confirmar contraseña *
                </label>
                <div className="relative">
                  <Shield className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                  <input
                    type={mostrarPasswordConfirm ? 'text' : 'password'}
                    {...register('passwordConfirm', {
                      required: 'Confirma tu contraseña',
                      validate: (value) => value === password || 'Las contraseñas no coinciden',
                    })}
                    className="w-full pl-10 pr-12 py-2.5 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500"
                  />
                  <button
                    type="button"
                    onClick={() => setMostrarPasswordConfirm(!mostrarPasswordConfirm)}
                    className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600"
                  >
                    {mostrarPasswordConfirm ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
                  </button>
                </div>
                {errors.passwordConfirm && (
                  <p className="mt-1 text-sm text-red-600">{errors.passwordConfirm.message}</p>
                )}
              </div>

              <button
                type="submit"
                disabled={aceptarMutation.isPending}
                className="w-full px-6 py-3 bg-blue-600 hover:bg-blue-700 disabled:bg-blue-400 text-white rounded-lg transition-colors font-medium flex items-center justify-center gap-2 disabled:cursor-not-allowed"
              >
                {aceptarMutation.isPending ? (
                  <>
                    <Loader2 className="w-5 h-5 animate-spin" />
                    Creando cuenta...
                  </>
                ) : (
                  <>
                    <CheckCircle2 className="w-5 h-5" />
                    Crear cuenta
                  </>
                )}
              </button>
            </form>
          )}
        </div>

        {/* Footer */}
        <div className="text-center text-sm text-gray-600 dark:text-gray-400">
          ¿Necesitas ayuda? Contacta al administrador de tu institución
        </div>
      </div>
    </div>
  );
}
