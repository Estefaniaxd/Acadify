/**
 * Página de Configuración de Notificaciones
 * 
 * @module pages/ConfiguracionNotificacionesPage
 * @description Configuración de preferencias de notificaciones del usuario
 */

import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import {
  Settings, Bell, Volume2, VolumeX, Mail, Clock,
  MessageSquare, BookOpen, Trophy, Calendar, Check
} from 'lucide-react';
import {
  useConfiguracionNotificaciones,
  useActualizarConfiguracion,
} from '../../hooks/useNotificaciones';
import { DIAS_SEMANA } from '../../services/notificaciones.service';

export default function ConfiguracionNotificacionesPage() {
  const { data: config, isLoading } = useConfiguracionNotificaciones();
  const { mutate: actualizarConfig, isPending } = useActualizarConfiguracion();

  // Estados locales para el formulario
  const [formData, setFormData] = useState({
    notificaciones_activas: true,
    sonido_activo: true,
    tareas_nuevas: true,
    tareas_vencimiento_24h: true,
    tareas_vencimiento_1h: true,
    tareas_calificadas: true,
    tareas_comentarios: true,
    mensajes_directos: true,
    menciones: true,
    respuestas_hilos: true,
    mensajes_importantes: true,
    resumen_diario_email: false,
    urgentes_email: false,
    menciones_email: false,
    horario_inicio: '08:00',
    horario_fin: '20:00',
    dias_activos: [1, 2, 3, 4, 5] as number[],
  });

  const [guardadoExitoso, setGuardadoExitoso] = useState(false);
  const [inicializado, setInicializado] = useState(false);

  // Cargar configuración cuando esté disponible (solo una vez)
  useEffect(() => {
    if (config && !inicializado) {
      setFormData({
        notificaciones_activas: config.notificaciones_activas ?? true,
        sonido_activo: config.sonido_activo ?? true,
        tareas_nuevas: config.tareas_nuevas ?? true,
        tareas_vencimiento_24h: config.tareas_vencimiento_24h ?? true,
        tareas_vencimiento_1h: config.tareas_vencimiento_1h ?? true,
        tareas_calificadas: config.tareas_calificadas ?? true,
        tareas_comentarios: config.tareas_comentarios ?? true,
        mensajes_directos: config.mensajes_directos ?? true,
        menciones: config.menciones ?? true,
        respuestas_hilos: config.respuestas_hilos ?? true,
        mensajes_importantes: config.mensajes_importantes ?? true,
        resumen_diario_email: config.resumen_diario_email ?? false,
        urgentes_email: config.urgentes_email ?? false,
        menciones_email: config.menciones_email ?? false,
        horario_inicio: config.horario_inicio || '08:00',
        horario_fin: config.horario_fin || '20:00',
        dias_activos: config.dias_activos || [1, 2, 3, 4, 5],
      });
      setInicializado(true);
    }
  }, [config, inicializado]);

  const handleToggle = (campo: keyof typeof formData) => {
    setFormData((prev) => ({
      ...prev,
      [campo]: !prev[campo],
    }));
  };

  const handleDiaToggle = (dia: number) => {
    setFormData((prev) => ({
      ...prev,
      dias_activos: prev.dias_activos.includes(dia)
        ? prev.dias_activos.filter((d) => d !== dia)
        : [...prev.dias_activos, dia].sort(),
    }));
  };

  const handleGuardar = () => {
    actualizarConfig(formData, {
      onSuccess: () => {
        setGuardadoExitoso(true);
        setTimeout(() => setGuardadoExitoso(false), 3000);
      },
    });
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900 flex items-center justify-center">
        <div className="w-12 h-12 border-4 border-violet-500 border-t-transparent rounded-full animate-spin"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      {/* Header */}
      <div className="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700">
        <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center gap-4">
            <div className="w-12 h-12 bg-gradient-to-br from-violet-500 to-purple-600 rounded-2xl flex items-center justify-center">
              <Settings className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
                Configuración de Notificaciones
              </h1>
              <p className="text-sm text-gray-600 dark:text-gray-400">
                Personaliza cómo y cuándo recibes notificaciones
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Contenido */}
      <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="space-y-6">
          {/* Configuración General */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="bg-white dark:bg-gray-800 rounded-2xl border border-gray-200 dark:border-gray-700 p-6"
          >
            <h2 className="text-lg font-bold text-gray-900 dark:text-white mb-4 flex items-center gap-2">
              <Bell className="w-5 h-5" />
              General
            </h2>

            <div className="space-y-4">
              <ToggleRow
                label="Notificaciones activas"
                description="Activa o desactiva todas las notificaciones"
                checked={formData.notificaciones_activas}
                onChange={() => handleToggle('notificaciones_activas')}
                icon={Bell}
              />
              <ToggleRow
                label="Sonido de notificaciones"
                description="Reproduce un sonido cuando recibes notificaciones"
                checked={formData.sonido_activo}
                onChange={() => handleToggle('sonido_activo')}
                icon={formData.sonido_activo ? Volume2 : VolumeX}
              />
            </div>
          </motion.div>

          {/* Notificaciones de Tareas */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="bg-white dark:bg-gray-800 rounded-2xl border border-gray-200 dark:border-gray-700 p-6"
          >
            <h2 className="text-lg font-bold text-gray-900 dark:text-white mb-4 flex items-center gap-2">
              <BookOpen className="w-5 h-5" />
              Tareas
            </h2>

            <div className="space-y-4">
              <ToggleRow
                label="Tareas nuevas"
                description="Cuando se asigna una nueva tarea"
                checked={formData.tareas_nuevas}
                onChange={() => handleToggle('tareas_nuevas')}
              />
              <ToggleRow
                label="Vencimiento en 24 horas"
                description="Recordatorio 24 horas antes del vencimiento"
                checked={formData.tareas_vencimiento_24h}
                onChange={() => handleToggle('tareas_vencimiento_24h')}
              />
              <ToggleRow
                label="Vencimiento en 1 hora"
                description="Recordatorio 1 hora antes del vencimiento"
                checked={formData.tareas_vencimiento_1h}
                onChange={() => handleToggle('tareas_vencimiento_1h')}
              />
              <ToggleRow
                label="Tareas calificadas"
                description="Cuando se califica una tarea que entregaste"
                checked={formData.tareas_calificadas}
                onChange={() => handleToggle('tareas_calificadas')}
              />
            </div>
          </motion.div>

          {/* Notificaciones de Mensajes */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="bg-white dark:bg-gray-800 rounded-2xl border border-gray-200 dark:border-gray-700 p-6"
          >
            <h2 className="text-lg font-bold text-gray-900 dark:text-white mb-4 flex items-center gap-2">
              <MessageSquare className="w-5 h-5" />
              Mensajes
            </h2>

            <div className="space-y-4">
              <ToggleRow
                label="Mensajes directos"
                description="Cuando recibes un mensaje directo"
                checked={formData.mensajes_directos}
                onChange={() => handleToggle('mensajes_directos')}
              />
              <ToggleRow
                label="Menciones"
                description="Cuando alguien te menciona con @"
                checked={formData.menciones}
                onChange={() => handleToggle('menciones')}
              />
              <ToggleRow
                label="Respuestas en hilos"
                description="Respuestas a hilos en los que participas"
                checked={formData.respuestas_hilo}
                onChange={() => handleToggle('respuestas_hilo')}
              />
              <ToggleRow
                label="Mensajes importantes"
                description="Mensajes marcados como importantes"
                checked={formData.mensajes_importantes}
                onChange={() => handleToggle('mensajes_importantes')}
              />
            </div>
          </motion.div>

          {/* Notificaciones de Cursos y Clases */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
            className="bg-white dark:bg-gray-800 rounded-2xl border border-gray-200 dark:border-gray-700 p-6"
          >
            <h2 className="text-lg font-bold text-gray-900 dark:text-white mb-4 flex items-center gap-2">
              <Calendar className="w-5 h-5" />
              Cursos y Clases
            </h2>

            <div className="space-y-4">
              <ToggleRow
                label="Cursos nuevos"
                description="Cuando te inscriben en un nuevo curso"
                checked={formData.cursos_nuevos}
                onChange={() => handleToggle('cursos_nuevos')}
              />
              <ToggleRow
                label="Clases canceladas"
                description="Cuando se cancela una clase"
                checked={formData.clases_canceladas}
                onChange={() => handleToggle('clases_canceladas')}
              />
              <ToggleRow
                label="Evaluaciones disponibles"
                description="Cuando hay una nueva evaluación disponible"
                checked={formData.evaluaciones_disponibles}
                onChange={() => handleToggle('evaluaciones_disponibles')}
              />
            </div>
          </motion.div>

          {/* Gamificación y Sistema */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4 }}
            className="bg-white dark:bg-gray-800 rounded-2xl border border-gray-200 dark:border-gray-700 p-6"
          >
            <h2 className="text-lg font-bold text-gray-900 dark:text-white mb-4 flex items-center gap-2">
              <Trophy className="w-5 h-5" />
              Gamificación y Sistema
            </h2>

            <div className="space-y-4">
              <ToggleRow
                label="Logros desbloqueados"
                description="Cuando desbloqueas un nuevo logro"
                checked={formData.logros_desbloqueados}
                onChange={() => handleToggle('logros_desbloqueados')}
              />
              <ToggleRow
                label="Notificaciones del sistema"
                description="Actualizaciones y mensajes del sistema"
                checked={formData.notificaciones_sistema}
                onChange={() => handleToggle('notificaciones_sistema')}
              />
            </div>
          </motion.div>

          {/* Resúmenes por Email */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.5 }}
            className="bg-white dark:bg-gray-800 rounded-2xl border border-gray-200 dark:border-gray-700 p-6"
          >
            <h2 className="text-lg font-bold text-gray-900 dark:text-white mb-4 flex items-center gap-2">
              <Mail className="w-5 h-5" />
              Resúmenes por Email
            </h2>

            <div className="space-y-4">
              <ToggleRow
                label="Resumen diario"
                description="Recibe un resumen diario por email"
                checked={formData.resumen_diario_email}
                onChange={() => handleToggle('resumen_diario_email')}
              />
              <ToggleRow
                label="Resumen semanal"
                description="Recibe un resumen semanal por email"
                checked={formData.resumen_semanal_email}
                onChange={() => handleToggle('resumen_semanal_email')}
              />
            </div>
          </motion.div>

          {/* Horario y Días */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.6 }}
            className="bg-white dark:bg-gray-800 rounded-2xl border border-gray-200 dark:border-gray-700 p-6"
          >
            <h2 className="text-lg font-bold text-gray-900 dark:text-white mb-4 flex items-center gap-2">
              <Clock className="w-5 h-5" />
              Horario de Notificaciones
            </h2>

            <div className="space-y-6">
              {/* Horario */}
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Recibir notificaciones entre
                </label>
                <div className="flex items-center gap-4">
                  <input
                    type="time"
                    value={formData.horario_inicio}
                    onChange={(e) =>
                      setFormData((prev) => ({ ...prev, horario_inicio: e.target.value }))
                    }
                    className="px-4 py-2 bg-gray-50 dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-xl text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-violet-500"
                  />
                  <span className="text-gray-500">y</span>
                  <input
                    type="time"
                    value={formData.horario_fin}
                    onChange={(e) =>
                      setFormData((prev) => ({ ...prev, horario_fin: e.target.value }))
                    }
                    className="px-4 py-2 bg-gray-50 dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-xl text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-violet-500"
                  />
                </div>
              </div>

              {/* Días de la semana */}
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Días activos
                </label>
                <div className="flex flex-wrap gap-2">
                  {DIAS_SEMANA.map((dia: { value: number; label: string }) => {
                    const isActive = formData.dias_activos.includes(dia.value);
                    return (
                      <button
                        key={dia.value}
                        onClick={() => handleDiaToggle(dia.value)}
                        className={`px-4 py-2 rounded-xl font-medium transition-all ${
                          isActive
                            ? 'bg-violet-500 text-white'
                            : 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600'
                        }`}
                      >
                        {dia.label.substring(0, 3)}
                      </button>
                    );
                  })}
                </div>
              </div>
            </div>
          </motion.div>

          {/* Botones de acción */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.7 }}
            className="flex items-center justify-end gap-4"
          >
            <button
              onClick={handleGuardar}
              disabled={isPending}
              className="px-6 py-3 bg-gradient-to-r from-violet-600 to-purple-600 text-white rounded-xl font-semibold hover:shadow-lg transition-all disabled:opacity-50 flex items-center gap-2"
            >
              {isPending ? (
                <>
                  <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                  Guardando...
                </>
              ) : guardadoExitoso ? (
                <>
                  <Check className="w-5 h-5" />
                  Guardado
                </>
              ) : (
                'Guardar cambios'
              )}
            </button>
          </motion.div>
        </div>
      </div>
    </div>
  );
}

// Componente auxiliar para filas de toggle
interface ToggleRowProps {
  label: string;
  description: string;
  checked: boolean;
  onChange: () => void;
  icon?: React.ElementType;
}

function ToggleRow({ label, description, checked, onChange, icon: Icon }: ToggleRowProps) {
  return (
    <div className="flex items-start justify-between py-3">
      <div className="flex items-start gap-3 flex-1">
        {Icon && (
          <div className="w-10 h-10 bg-violet-50 dark:bg-violet-900/30 rounded-xl flex items-center justify-center flex-shrink-0">
            <Icon className="w-5 h-5 text-violet-600 dark:text-violet-400" />
          </div>
        )}
        <div className="flex-1">
          <p className="font-medium text-gray-900 dark:text-white">{label}</p>
          <p className="text-sm text-gray-600 dark:text-gray-400">{description}</p>
        </div>
      </div>
      <button
        onClick={onChange}
        className={`relative inline-flex h-6 w-11 flex-shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none focus:ring-2 focus:ring-violet-500 focus:ring-offset-2 ${
          checked ? 'bg-violet-600' : 'bg-gray-200 dark:bg-gray-700'
        }`}
      >
        <span
          className={`inline-block h-5 w-5 transform rounded-full bg-white shadow ring-0 transition duration-200 ease-in-out ${
            checked ? 'translate-x-5' : 'translate-x-0'
          }`}
        />
      </button>
    </div>
  );
}
