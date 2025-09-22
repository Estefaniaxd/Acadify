import React, { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { useAuth } from '../context/AuthContext'
import { useToast } from '../context/ToastContext'
import { 
  FiUser, 
  FiShield, 
  FiBell, 
  FiGlobe,
  FiMoon,
  FiSun,
  FiMonitor,
  FiVolume2,
  FiVolumeX,
  FiLock,
  FiKey,
  FiTrash2,
  FiDownload,
  FiUpload,
  FiEye,
  FiEyeOff,
  FiMail,
  FiSmartphone,
  FiCheck,
  FiX,
  FiSettings,
  FiHelpCircle,
  FiChevronRight,
  FiToggleLeft,
  FiToggleRight
} from 'react-icons/fi'
import { HiSparkles } from 'react-icons/hi'

interface SettingsState {
  // Apariencia
  theme: 'light' | 'dark' | 'auto'
  language: string
  fontSize: 'small' | 'medium' | 'large'
  animations: boolean
  
  // Notificaciones
  emailNotifications: boolean
  pushNotifications: boolean
  soundEnabled: boolean
  marketingEmails: boolean
  weeklyDigest: boolean
  
  // Privacidad
  profileVisibility: 'public' | 'friends' | 'private'
  showOnlineStatus: boolean
  allowDirectMessages: boolean
  dataCollection: boolean
  
  // Cuenta
  twoFactorAuth: boolean
  sessionTimeout: number
  downloadData: boolean
  deleteAccount: boolean
}

export default function AjustesPageAdvanced() {
  const { user, logout } = useAuth()
  const toast = useToast()
  const [activeTab, setActiveTab] = useState<'general' | 'notifications' | 'privacy' | 'security' | 'account'>('general')
  const [settings, setSettings] = useState<SettingsState>({
    theme: 'auto',
    language: 'es',
    fontSize: 'medium',
    animations: true,
    emailNotifications: true,
    pushNotifications: true,
    soundEnabled: true,
    marketingEmails: false,
    weeklyDigest: true,
    profileVisibility: 'public',
    showOnlineStatus: true,
    allowDirectMessages: true,
    dataCollection: false,
    twoFactorAuth: false,
    sessionTimeout: 30,
    downloadData: false,
    deleteAccount: false
  })
  const [isModified, setIsModified] = useState(false)

  const tabs = [
    { id: 'general', label: 'General', icon: FiSettings, color: 'from-blue-500 to-indigo-600' },
    { id: 'notifications', label: 'Notificaciones', icon: FiBell, color: 'from-emerald-500 to-teal-600' },
    { id: 'privacy', label: 'Privacidad', icon: FiEye, color: 'from-purple-500 to-pink-600' },
    { id: 'security', label: 'Seguridad', icon: FiShield, color: 'from-amber-500 to-orange-600' },
    { id: 'account', label: 'Cuenta', icon: FiUser, color: 'from-red-500 to-rose-600' }
  ]

  const updateSetting = (key: keyof SettingsState, value: any) => {
    setSettings(prev => ({ ...prev, [key]: value }))
    setIsModified(true)
  }

  const saveSettings = () => {
    // Aquí iría la llamada a la API para guardar
    setTimeout(() => {
      toast.success('¡Configuración guardada!', 'Tus preferencias han sido actualizadas correctamente.')
      setIsModified(false)
    }, 1000)
  }

  const resetSettings = () => {
    toast.info('Configuración restaurada', 'Se han restablecido los valores predeterminados.')
    setIsModified(false)
  }

  const ToggleSwitch = ({ enabled, onChange, label, description }: {
    enabled: boolean
    onChange: (value: boolean) => void
    label: string
    description?: string
  }) => (
    <div className="flex items-center justify-between py-3">
      <div className="flex-1">
        <h4 className="text-sm font-medium text-gray-900 dark:text-white">{label}</h4>
        {description && (
          <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">{description}</p>
        )}
      </div>
      <motion.button
        whileTap={{ scale: 0.95 }}
        onClick={() => onChange(!enabled)}
        className={`relative w-12 h-6 rounded-full transition-colors duration-200 ${
          enabled ? 'bg-blue-600' : 'bg-gray-300 dark:bg-gray-600'
        }`}
      >
        <motion.div
          animate={{ x: enabled ? 24 : 4 }}
          transition={{ type: "spring", stiffness: 300, damping: 30 }}
          className="absolute top-1 w-4 h-4 bg-white rounded-full shadow-sm"
        />
      </motion.button>
    </div>
  )

  const renderTabContent = () => {
    switch (activeTab) {
      case 'general':
        return (
          <div className="space-y-8">
            {/* Tema */}
            <div>
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Apariencia</h3>
              <div className="space-y-4">
                <div>
                  <label className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2 block">
                    Tema
                  </label>
                  <div className="grid grid-cols-3 gap-3">
                    {[
                      { id: 'light', label: 'Claro', icon: FiSun },
                      { id: 'dark', label: 'Oscuro', icon: FiMoon },
                      { id: 'auto', label: 'Auto', icon: FiMonitor }
                    ].map((theme) => (
                      <motion.button
                        key={theme.id}
                        whileHover={{ scale: 1.02 }}
                        whileTap={{ scale: 0.98 }}
                        onClick={() => updateSetting('theme', theme.id)}
                        className={`flex items-center space-x-2 p-3 rounded-lg border-2 transition-all ${
                          settings.theme === theme.id
                            ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20 text-blue-700 dark:text-blue-300'
                            : 'border-gray-300 dark:border-gray-600 hover:border-blue-400'
                        }`}
                      >
                        <theme.icon className="w-4 h-4" />
                        <span className="text-sm font-medium">{theme.label}</span>
                      </motion.button>
                    ))}
                  </div>
                </div>

                <div>
                  <label className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2 block">
                    Tamaño de fuente
                  </label>
                  <select
                    value={settings.fontSize}
                    onChange={(e) => updateSetting('fontSize', e.target.value)}
                    className="w-full px-3 py-2 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  >
                    <option value="small">Pequeño</option>
                    <option value="medium">Mediano</option>
                    <option value="large">Grande</option>
                  </select>
                </div>

                <ToggleSwitch
                  enabled={settings.animations}
                  onChange={(value) => updateSetting('animations', value)}
                  label="Animaciones"
                  description="Habilitar transiciones y efectos visuales"
                />
              </div>
            </div>

            {/* Idioma */}
            <div>
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Idioma y región</h3>
              <div>
                <label className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2 block">
                  Idioma de la interfaz
                </label>
                <select
                  value={settings.language}
                  onChange={(e) => updateSetting('language', e.target.value)}
                  className="w-full px-3 py-2 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                >
                  <option value="es">Español</option>
                  <option value="en">English</option>
                  <option value="fr">Français</option>
                  <option value="pt">Português</option>
                </select>
              </div>
            </div>
          </div>
        )

      case 'notifications':
        return (
          <div className="space-y-8">
            <div>
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Preferencias de notificaciones</h3>
              <div className="space-y-1">
                <ToggleSwitch
                  enabled={settings.emailNotifications}
                  onChange={(value) => updateSetting('emailNotifications', value)}
                  label="Notificaciones por email"
                  description="Recibir alertas importantes por correo electrónico"
                />
                
                <ToggleSwitch
                  enabled={settings.pushNotifications}
                  onChange={(value) => updateSetting('pushNotifications', value)}
                  label="Notificaciones push"
                  description="Alertas en tiempo real en el navegador"
                />
                
                <ToggleSwitch
                  enabled={settings.soundEnabled}
                  onChange={(value) => updateSetting('soundEnabled', value)}
                  label="Sonidos de notificación"
                  description="Reproducir sonidos para nuevas notificaciones"
                />
                
                <ToggleSwitch
                  enabled={settings.marketingEmails}
                  onChange={(value) => updateSetting('marketingEmails', value)}
                  label="Emails promocionales"
                  description="Recibir ofertas y actualizaciones de producto"
                />
                
                <ToggleSwitch
                  enabled={settings.weeklyDigest}
                  onChange={(value) => updateSetting('weeklyDigest', value)}
                  label="Resumen semanal"
                  description="Resumen de actividad cada semana"
                />
              </div>
            </div>

            <div>
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Canales de notificación</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="flex items-center space-x-3 p-4 bg-gray-50 dark:bg-gray-800 rounded-lg">
                  <FiMail className="w-5 h-5 text-blue-500" />
                  <div>
                    <p className="font-medium text-gray-900 dark:text-white">Email</p>
                    <p className="text-sm text-gray-500 dark:text-gray-400">{user?.email}</p>
                  </div>
                </div>
                <div className="flex items-center space-x-3 p-4 bg-gray-50 dark:bg-gray-800 rounded-lg">
                  <FiSmartphone className="w-5 h-5 text-emerald-500" />
                  <div>
                    <p className="font-medium text-gray-900 dark:text-white">Navegador</p>
                    <p className="text-sm text-gray-500 dark:text-gray-400">Push notifications</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )

      case 'privacy':
        return (
          <div className="space-y-8">
            <div>
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Visibilidad del perfil</h3>
              <div className="space-y-4">
                <div>
                  <label className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2 block">
                    ¿Quién puede ver tu perfil?
                  </label>
                  <div className="space-y-2">
                    {[
                      { id: 'public', label: 'Público', description: 'Cualquiera puede ver tu perfil' },
                      { id: 'friends', label: 'Solo amigos', description: 'Solo personas que sigues y te siguen' },
                      { id: 'private', label: 'Privado', description: 'Solo tú puedes ver tu perfil' }
                    ].map((option) => (
                      <label key={option.id} className="flex items-start space-x-3 cursor-pointer">
                        <input
                          type="radio"
                          name="profileVisibility"
                          value={option.id}
                          checked={settings.profileVisibility === option.id}
                          onChange={(e) => updateSetting('profileVisibility', e.target.value)}
                          className="mt-1 w-4 h-4 text-blue-600 border-gray-300 focus:ring-blue-500"
                        />
                        <div>
                          <p className="font-medium text-gray-900 dark:text-white">{option.label}</p>
                          <p className="text-sm text-gray-500 dark:text-gray-400">{option.description}</p>
                        </div>
                      </label>
                    ))}
                  </div>
                </div>
              </div>
            </div>

            <div>
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Configuración de privacidad</h3>
              <div className="space-y-1">
                <ToggleSwitch
                  enabled={settings.showOnlineStatus}
                  onChange={(value) => updateSetting('showOnlineStatus', value)}
                  label="Mostrar estado en línea"
                  description="Otros usuarios pueden ver cuándo estás activo"
                />
                
                <ToggleSwitch
                  enabled={settings.allowDirectMessages}
                  onChange={(value) => updateSetting('allowDirectMessages', value)}
                  label="Permitir mensajes directos"
                  description="Otros usuarios pueden enviarte mensajes privados"
                />
                
                <ToggleSwitch
                  enabled={settings.dataCollection}
                  onChange={(value) => updateSetting('dataCollection', value)}
                  label="Recopilación de datos de uso"
                  description="Ayúdanos a mejorar compartiendo datos anónimos de uso"
                />
              </div>
            </div>
          </div>
        )

      case 'security':
        return (
          <div className="space-y-8">
            <div>
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Autenticación</h3>
              <div className="space-y-4">
                <ToggleSwitch
                  enabled={settings.twoFactorAuth}
                  onChange={(value) => updateSetting('twoFactorAuth', value)}
                  label="Autenticación de dos factores"
                  description="Añade una capa extra de seguridad a tu cuenta"
                />
                
                <div>
                  <label className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2 block">
                    Tiempo de sesión (minutos)
                  </label>
                  <select
                    value={settings.sessionTimeout}
                    onChange={(e) => updateSetting('sessionTimeout', parseInt(e.target.value))}
                    className="w-full px-3 py-2 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  >
                    <option value={15}>15 minutos</option>
                    <option value={30}>30 minutos</option>
                    <option value={60}>1 hora</option>
                    <option value={120}>2 horas</option>
                    <option value={0}>Sin límite</option>
                  </select>
                </div>
              </div>
            </div>

            <div>
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Gestión de contraseña</h3>
              <div className="space-y-3">
                <motion.button
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                  className="w-full flex items-center justify-between p-4 bg-gray-50 dark:bg-gray-800 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
                >
                  <div className="flex items-center space-x-3">
                    <FiKey className="w-5 h-5 text-amber-500" />
                    <div className="text-left">
                      <p className="font-medium text-gray-900 dark:text-white">Cambiar contraseña</p>
                      <p className="text-sm text-gray-500 dark:text-gray-400">Última actualización: hace 3 meses</p>
                    </div>
                  </div>
                  <FiChevronRight className="w-5 h-5 text-gray-400" />
                </motion.button>

                <motion.button
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                  className="w-full flex items-center justify-between p-4 bg-gray-50 dark:bg-gray-800 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
                >
                  <div className="flex items-center space-x-3">
                    <FiShield className="w-5 h-5 text-emerald-500" />
                    <div className="text-left">
                      <p className="font-medium text-gray-900 dark:text-white">Sesiones activas</p>
                      <p className="text-sm text-gray-500 dark:text-gray-400">Gestionar dispositivos conectados</p>
                    </div>
                  </div>
                  <FiChevronRight className="w-5 h-5 text-gray-400" />
                </motion.button>
              </div>
            </div>
          </div>
        )

      case 'account':
        return (
          <div className="space-y-8">
            <div>
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Gestión de datos</h3>
              <div className="space-y-3">
                <motion.button
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                  onClick={() => {
                    toast.info('Preparando descarga...', 'Se iniciará la descarga de tus datos en unos momentos.')
                  }}
                  className="w-full flex items-center justify-between p-4 bg-gray-50 dark:bg-gray-800 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
                >
                  <div className="flex items-center space-x-3">
                    <FiDownload className="w-5 h-5 text-blue-500" />
                    <div className="text-left">
                      <p className="font-medium text-gray-900 dark:text-white">Descargar mis datos</p>
                      <p className="text-sm text-gray-500 dark:text-gray-400">Obtén una copia de toda tu información</p>
                    </div>
                  </div>
                  <FiChevronRight className="w-5 h-5 text-gray-400" />
                </motion.button>

                <motion.button
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                  className="w-full flex items-center justify-between p-4 bg-gray-50 dark:bg-gray-800 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
                >
                  <div className="flex items-center space-x-3">
                    <FiUpload className="w-5 h-5 text-emerald-500" />
                    <div className="text-left">
                      <p className="font-medium text-gray-900 dark:text-white">Importar datos</p>
                      <p className="text-sm text-gray-500 dark:text-gray-400">Importar información desde otra plataforma</p>
                    </div>
                  </div>
                  <FiChevronRight className="w-5 h-5 text-gray-400" />
                </motion.button>
              </div>
            </div>

            <div>
              <h3 className="text-lg font-semibold text-red-600 dark:text-red-400 mb-4">Zona de peligro</h3>
              <div className="space-y-3 p-4 bg-red-50 dark:bg-red-900/20 rounded-lg border border-red-200 dark:border-red-800">
                <motion.button
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                  onClick={logout}
                  className="w-full flex items-center justify-between p-3 bg-white dark:bg-gray-800 rounded-lg hover:bg-red-50 dark:hover:bg-red-900/30 transition-colors border border-red-200 dark:border-red-800"
                >
                  <div className="flex items-center space-x-3">
                    <FiLock className="w-5 h-5 text-red-500" />
                    <div className="text-left">
                      <p className="font-medium text-red-600 dark:text-red-400">Cerrar todas las sesiones</p>
                      <p className="text-sm text-red-500 dark:text-red-400">Desconectar de todos los dispositivos</p>
                    </div>
                  </div>
                </motion.button>

                <motion.button
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                  onClick={() => {
                    toast.error('Acción peligrosa', 'Esta acción no se puede deshacer. Contacta soporte si realmente deseas eliminar tu cuenta.')
                  }}
                  className="w-full flex items-center justify-between p-3 bg-white dark:bg-gray-800 rounded-lg hover:bg-red-50 dark:hover:bg-red-900/30 transition-colors border border-red-200 dark:border-red-800"
                >
                  <div className="flex items-center space-x-3">
                    <FiTrash2 className="w-5 h-5 text-red-500" />
                    <div className="text-left">
                      <p className="font-medium text-red-600 dark:text-red-400">Eliminar cuenta</p>
                      <p className="text-sm text-red-500 dark:text-red-400">Eliminar permanentemente tu cuenta y datos</p>
                    </div>
                  </div>
                </motion.button>
              </div>
            </div>
          </div>
        )

      default:
        return null
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 via-blue-50/30 to-indigo-50/50 dark:from-gray-900 dark:via-gray-900 dark:to-blue-950/30">
      {/* Header */}
      <div className="bg-white/80 dark:bg-gray-900/80 backdrop-blur-xl border-b border-gray-200/50 dark:border-gray-700/50 sticky top-0 z-40">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-gradient-to-r from-blue-500 to-indigo-600 rounded-xl flex items-center justify-center">
                <FiSettings className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-xl font-bold text-gray-900 dark:text-white">
                  Configuración
                </h1>
                <p className="text-sm text-gray-500 dark:text-gray-400">
                  Personaliza tu experiencia
                </p>
              </div>
            </div>

            <div className="flex items-center space-x-3">
              {isModified && (
                <motion.div
                  initial={{ opacity: 0, scale: 0.8 }}
                  animate={{ opacity: 1, scale: 1 }}
                  className="flex items-center space-x-2"
                >
                  <motion.button
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                    onClick={resetSettings}
                    className="px-3 py-1.5 text-sm text-gray-600 dark:text-gray-400 hover:text-gray-800 dark:hover:text-gray-200"
                  >
                    Cancelar
                  </motion.button>
                  <motion.button
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                    onClick={saveSettings}
                    className="flex items-center space-x-1 px-4 py-1.5 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors text-sm font-medium"
                  >
                    <FiCheck className="w-4 h-4" />
                    <span>Guardar</span>
                  </motion.button>
                </motion.div>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
          
          {/* Sidebar Tabs */}
          <div className="lg:col-span-1">
            <div className="bg-white/80 dark:bg-gray-800/80 backdrop-blur-xl rounded-2xl border border-gray-200/50 dark:border-gray-700/50 overflow-hidden sticky top-24">
              <div className="p-4 border-b border-gray-200/50 dark:border-gray-700/50">
                <h3 className="font-semibold text-gray-900 dark:text-white">Categorías</h3>
              </div>
              <div className="p-2">
                {tabs.map((tab) => (
                  <motion.button
                    key={tab.id}
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                    onClick={() => setActiveTab(tab.id as any)}
                    className={`w-full flex items-center space-x-3 px-3 py-3 rounded-lg text-left transition-all duration-200 ${
                      activeTab === tab.id
                        ? 'bg-blue-50 dark:bg-blue-900/20 text-blue-700 dark:text-blue-300'
                        : 'text-gray-600 dark:text-gray-400 hover:bg-gray-50 dark:hover:bg-gray-700/50 hover:text-gray-900 dark:hover:text-gray-200'
                    }`}
                  >
                    <div className={`w-8 h-8 rounded-lg bg-gradient-to-r ${tab.color} flex items-center justify-center`}>
                      <tab.icon className="w-4 h-4 text-white" />
                    </div>
                    <span className="font-medium">{tab.label}</span>
                  </motion.button>
                ))}
              </div>
            </div>
          </div>

          {/* Content */}
          <div className="lg:col-span-3">
            <div className="bg-white/80 dark:bg-gray-800/80 backdrop-blur-xl rounded-2xl border border-gray-200/50 dark:border-gray-700/50 p-8">
              <AnimatePresence mode="wait">
                <motion.div
                  key={activeTab}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -20 }}
                  transition={{ duration: 0.2 }}
                >
                  {renderTabContent()}
                </motion.div>
              </AnimatePresence>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}