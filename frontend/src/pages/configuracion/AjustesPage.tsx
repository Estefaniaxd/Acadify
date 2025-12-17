import React, { useState } from 'react';
import { useAuth } from '../../context/AuthContext';
import { Shield, LogOut, AlertCircle } from 'lucide-react';

export default function AjustesPage({ theme, setTheme }: { theme: 'light' | 'dark', setTheme: (t: 'light' | 'dark') => void }) {
  const { logoutAllDevices } = useAuth();
  const [isLoggingOut, setIsLoggingOut] = useState(false);
  const [showConfirm, setShowConfirm] = useState(false);

  const handleLogoutAllDevices = async () => {
    setIsLoggingOut(true);
    try {
      await logoutAllDevices();
    } catch (error) {
      console.error('Error al cerrar sesiones:', error);
      setIsLoggingOut(false);
      setShowConfirm(false);
    }
  };

  return (
    <div className="bg-gradient-to-br from-gray-50 via-white to-gray-100 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900 p-6 mt-6">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-8">
          Configuraciones
        </h1>

        <div className="bg-white dark:bg-gray-800 rounded-xl p-8 border border-gray-200 dark:border-gray-700">
          <div className="space-y-6">
            <div>
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
                Apariencia
              </h3>
              <div className="flex items-center space-x-4">
                <button
                  onClick={() => setTheme('light')}
                  className={`px-4 py-2 rounded-lg transition-colors ${theme === 'light'
                      ? 'bg-blue-600 text-white'
                      : 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300'
                    }`}
                >
                  Claro
                </button>
                <button
                  onClick={() => setTheme('dark')}
                  className={`px-4 py-2 rounded-lg transition-colors ${theme === 'dark'
                      ? 'bg-blue-600 text-white'
                      : 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300'
                    }`}
                >
                  Oscuro
                </button>
              </div>
            </div>

            <div>
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
                Notificaciones
              </h3>
              <div className="space-y-3">
                <label className="flex items-center">
                  <input type="checkbox" defaultChecked className="mr-3" />
                  <span className="text-gray-700 dark:text-gray-300">Notificaciones por email</span>
                </label>
                <label className="flex items-center">
                  <input type="checkbox" defaultChecked className="mr-3" />
                  <span className="text-gray-700 dark:text-gray-300">Notificaciones push</span>
                </label>
                <label className="flex items-center">
                  <input type="checkbox" className="mr-3" />
                  <span className="text-gray-700 dark:text-gray-300">Recordatorios de tareas</span>
                </label>
              </div>
            </div>

            <div>
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
                Privacidad
              </h3>
              <div className="space-y-3">
                <label className="flex items-center">
                  <input type="checkbox" defaultChecked className="mr-3" />
                  <span className="text-gray-700 dark:text-gray-300">Perfil visible</span>
                </label>
                <label className="flex items-center">
                  <input type="checkbox" className="mr-3" />
                  <span className="text-gray-700 dark:text-gray-300">Mostrar actividad</span>
                </label>
              </div>
            </div>

            {/* Nueva sección de Seguridad */}
            <div className="border-t border-gray-200 dark:border-gray-700 pt-6 mt-6">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4 flex items-center gap-2">
                <Shield className="w-5 h-5" />
                Seguridad
              </h3>
              <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4">
                <div className="flex items-start gap-3">
                  <AlertCircle className="w-5 h-5 text-red-600 dark:text-red-400 mt-0.5 flex-shrink-0" />
                  <div className="flex-1">
                    <h4 className="font-semibold text-red-900 dark:text-red-100 mb-2">
                      Cerrar sesión en todos los dispositivos
                    </h4>
                    <p className="text-sm text-red-700 dark:text-red-300 mb-4">
                      Esta acción cerrará tu sesión en todos los dispositivos donde hayas iniciado sesión.
                      Tendrás que volver a iniciar sesión en este dispositivo también.
                    </p>

                    {!showConfirm ? (
                      <button
                        onClick={() => setShowConfirm(true)}
                        className="px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg transition-colors duration-200 flex items-center gap-2"
                      >
                        <LogOut className="w-4 h-4" />
                        Cerrar sesión en todos los dispositivos
                      </button>
                    ) : (
                      <div className="space-y-3">
                        <p className="text-sm font-semibold text-red-900 dark:text-red-100">
                          ¿Estás seguro? Esta acción no se puede deshacer.
                        </p>
                        <div className="flex gap-3">
                          <button
                            onClick={handleLogoutAllDevices}
                            disabled={isLoggingOut}
                            className="px-4 py-2 bg-red-600 hover:bg-red-700 disabled:bg-red-400 text-white rounded-lg transition-colors duration-200 flex items-center gap-2"
                          >
                            <LogOut className="w-4 h-4" />
                            {isLoggingOut ? 'Cerrando sesiones...' : 'Sí, cerrar todas las sesiones'}
                          </button>
                          <button
                            onClick={() => setShowConfirm(false)}
                            disabled={isLoggingOut}
                            className="px-4 py-2 bg-gray-200 hover:bg-gray-300 dark:bg-gray-700 dark:hover:bg-gray-600 text-gray-800 dark:text-gray-200 rounded-lg transition-colors duration-200"
                          >
                            Cancelar
                          </button>
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
