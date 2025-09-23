import React, { useState, useRef, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { useAuth } from '../context/AuthContext'
import { useToast } from '../context/ToastContext'
import { avatarAPI } from '../components/avatar/avatarAPI'
import { useNavigate } from 'react-router-dom'
import {
  FiEdit3,
  FiCamera,
  FiSave,
  FiUser,
  FiMail,
  FiPhone,
  FiMapPin,
  FiCalendar,
  FiGlobe,
  FiGithub,
  FiLinkedin,
  FiTwitter,
  FiInstagram,
  FiSettings,
  FiShield,
  FiStar,
  FiTrendingUp,
  FiAward,
  FiBookOpen,
  FiClock,
  FiCheckCircle,
  FiX,
  FiPlus
} from 'react-icons/fi'
import { HiSparkles, HiLightningBolt } from 'react-icons/hi'

interface UserProfile {
  username: string
  email: string
  firstName: string
  lastName: string
  phone: string
  location: string
  website: string
  bio: string
  birthDate: string
  role: string
  joinDate: string
  avatar: string
  socialLinks: {
    github?: string
    linkedin?: string
    twitter?: string
    instagram?: string
  }
  stats: {
    courses: number
    achievements: number
    points: number
    level: number
    streakDays: number
  }
  achievements: Array<{
    id: string
    name: string
    description: string
    icon: string
    color: string
    unlockedAt: string
  }>
  preferences: {
    emailNotifications: boolean
    pushNotifications: boolean
    publicProfile: boolean
    showStats: boolean
  }
}

export default function ProfilePage() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()
  const toast = useToast()
  const fileInputRef = useRef<HTMLInputElement>(null)
  const [isEditing, setIsEditing] = useState(false)
  const [activeTab, setActiveTab] = useState('personal')
  const [avatarUrl, setAvatarUrl] = useState<string | null>(null)
  const [loadingAvatar, setLoadingAvatar] = useState(true)
  const [profile, setProfile] = useState<UserProfile>({
    username: user?.username || 'usuario',
    email: user?.email || 'email@ejemplo.com',
    firstName: 'Estudiante',
    lastName: 'Ejemplo',
    phone: '+1 (555) 123-4567',
    location: 'Ciudad, País',
    website: 'https://miportfolio.com',
    bio: '¡Hola! Soy un estudiante apasionado por aprender cosas nuevas todos los días. Me encanta la tecnología y siempre estoy buscando nuevos desafíos.',
    birthDate: '1995-06-15',
    role: user?.role || 'estudiante',
    joinDate: '2024-01-15',
    avatar: avatarUrl || `https://api.dicebear.com/7.x/adventurer/svg?seed=${user?.username || 'user'}&backgroundColor=b6e3f4,c0aede,d1d4f9&accessories=glasses&accessoriesProbability=30`,
    socialLinks: {
      github: 'https://github.com/usuario',
      linkedin: 'https://linkedin.com/in/usuario',
      twitter: 'https://twitter.com/usuario',
      instagram: 'https://instagram.com/usuario'
    },
    stats: {
      courses: 8,
      achievements: 24,
      points: 2847,
      level: 12,
      streakDays: 15
    },
    achievements: [
      {
        id: '1',
        name: 'Primer Paso',
        description: 'Completaste tu primer curso',
        icon: '🎯',
        color: 'from-blue-500 to-indigo-600',
        unlockedAt: '2024-02-01'
      },
      {
        id: '2',
        name: 'Racha de Fuego',
        description: '7 días consecutivos estudiando',
        icon: '🔥',
        color: 'from-orange-500 to-red-600',
        unlockedAt: '2024-02-15'
      },
      {
        id: '3',
        name: 'Estudiante Estrella',
        description: 'Obtuviste calificación perfecta en 5 exámenes',
        icon: '⭐',
        color: 'from-yellow-500 to-amber-600',
        unlockedAt: '2024-03-01'
      },
      {
        id: '4',
        name: 'Colaborador',
        description: 'Ayudaste a 10 compañeros en el foro',
        icon: '🤝',
        color: 'from-emerald-500 to-teal-600',
        unlockedAt: '2024-03-10'
      }
    ],
    preferences: {
      emailNotifications: true,
      pushNotifications: true,
      publicProfile: true,
      showStats: true
    }
  })

  const handleSave = () => {
    // Aquí iría la lógica para guardar en el servidor
    setIsEditing(false)
    toast.success('¡Perfil actualizado!', 'Tus cambios han sido guardados correctamente.')
  }

  // Cargar avatar del usuario
  useEffect(() => {
    const loadUserAvatar = async () => {
      if (!user) {
        console.log('🔍 Profile: No user found');
        setLoadingAvatar(false);
        return;
      }

      // Verificar si hay token de autenticación
      const token = localStorage.getItem('access_token');
      if (!token) {
        console.log('🔍 Profile: No auth token found, cannot load avatar');
        setLoadingAvatar(false);
        return;
      }

      console.log('🔍 Profile: Loading avatar for user:', user.username);

      try {
        const avatars = await avatarAPI.getMyAvatars();
        console.log('🔍 Profile: Avatars response:', avatars);
        
        const activeAvatar = avatars.avatars.find(avatar => avatar.is_active);
        console.log('🔍 Profile: Active avatar:', activeAvatar);
        
        if (activeAvatar && activeAvatar.image_url) {
          console.log('🔍 Profile: Setting avatar URL:', activeAvatar.image_url);
          setAvatarUrl(activeAvatar.image_url);
          // Actualizar también el perfil inmediatamente
          setProfile(prev => ({
            ...prev,
            avatar: activeAvatar.image_url
          }));
        }
      } catch (error) {
        console.error('🔍 Profile: Error loading user avatar:', error);
        // Si es error 401, mostrar mensaje de relogin
        if (error instanceof Error && error.message.includes('401')) {
          console.log('🔍 Profile: Auth error, user needs to login again');
        }
      } finally {
        setLoadingAvatar(false);
      }
    };

    loadUserAvatar();
  }, [user]);

  // Escuchar actualizaciones de avatar
  useEffect(() => {
    const handleAvatarUpdate = (event: CustomEvent) => {
      console.log('🔍 Profile: Avatar update event received:', event.detail);
      const avatarData = event.detail;
      if (avatarData && avatarData.image_url) {
        console.log('🔍 Profile: Updating avatar URL from event:', avatarData.image_url);
        setAvatarUrl(avatarData.image_url);
        // Actualizar también el perfil
        setProfile(prev => ({
          ...prev,
          avatar: avatarData.image_url
        }));
        toast.success('¡Avatar actualizado!', 'Tu nuevo avatar se ve genial.');
      }
    };

    window.addEventListener('avatar-updated', handleAvatarUpdate as EventListener);
    
    return () => {
      window.removeEventListener('avatar-updated', handleAvatarUpdate as EventListener);
    };
  }, []);

  const handleAvatarChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (file) {
      // Aquí iría la lógica para subir la imagen
      const reader = new FileReader()
      reader.onload = (e) => {
        setProfile(prev => ({ ...prev, avatar: e.target?.result as string }))
      }
      reader.readAsDataURL(file)
      toast.success('¡Avatar actualizado!', 'Tu nueva foto se ve genial.')
    }
  }

  const getLevelProgress = () => {
    const currentLevelPoints = profile.stats.points % 250
    const nextLevelPoints = 250
    return (currentLevelPoints / nextLevelPoints) * 100
  }

  const tabs = [
    { id: 'profile', name: 'Perfil', icon: FiUser, color: 'from-blue-500 to-indigo-600' },
    { id: 'achievements', name: 'Logros', icon: FiAward, color: 'from-yellow-500 to-amber-600' },
    { id: 'stats', name: 'Estadísticas', icon: FiTrendingUp, color: 'from-emerald-500 to-teal-600' },
    { id: 'settings', name: 'Configuración', icon: FiSettings, color: 'from-purple-500 to-pink-600' }
  ]

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 via-blue-50/30 to-purple-50/50 dark:from-gray-900 dark:via-gray-900 dark:to-purple-950/30">
      {/* Header */}
      <div className="bg-white/80 dark:bg-gray-900/80 backdrop-blur-xl border-b border-gray-200/50 dark:border-gray-700/50 sticky top-0 z-40">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center space-x-3">
              <button
                onClick={() => navigate(-1)}
                className="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
              >
                <FiX className="w-5 h-5 text-gray-500 dark:text-gray-400" />
              </button>
              <h1 className="text-xl font-bold text-gray-900 dark:text-white">
                Mi Perfil
              </h1>
            </div>

            <div className="flex items-center space-x-2">
              {isEditing ? (
                <>
                  <button
                    onClick={() => setIsEditing(false)}
                    className="px-4 py-2 text-gray-600 dark:text-gray-400 hover:text-gray-800 dark:hover:text-gray-200 transition-colors"
                  >
                    Cancelar
                  </button>
                  <button
                    onClick={handleSave}
                    className="flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                  >
                    <FiSave className="w-4 h-4" />
                    <span>Guardar</span>
                  </button>
                </>
              ) : (
                <button
                  onClick={() => setIsEditing(true)}
                  className="flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                >
                  <FiEdit3 className="w-4 h-4" />
                  <span>Editar</span>
                </button>
              )}
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          
          {/* Sidebar with Avatar and Basic Info */}
          <div className="lg:col-span-1">
            <div className="bg-white/80 dark:bg-gray-800/80 backdrop-blur-xl rounded-2xl p-6 border border-gray-200/50 dark:border-gray-700/50 sticky top-24">
              
              {/* Avatar Section */}
              <div className="text-center mb-6">
                <div className="relative inline-block">
                  <div className="w-32 h-32 rounded-full overflow-hidden border-4 border-white shadow-2xl bg-gradient-to-r from-blue-500 to-purple-600 p-1">
                    {loadingAvatar ? (
                      <div className="w-full h-full rounded-full bg-gray-200 dark:bg-gray-700 animate-pulse flex items-center justify-center">
                        <div className="w-8 h-8 border-2 border-violet-600 border-t-transparent rounded-full animate-spin"></div>
                      </div>
                    ) : (
                      <img
                        src={profile.avatar}
                        alt="Avatar"
                        className="w-full h-full rounded-full object-cover bg-white"
                        onError={(e) => {
                          // Fallback a dicebear en caso de error
                          e.currentTarget.src = `https://api.dicebear.com/7.x/bottts/svg?seed=${user?.username || 'user'}`;
                        }}
                      />
                    )}
                  </div>
                  {isEditing && (
                    <button
                      onClick={() => fileInputRef.current?.click()}
                      className="absolute -bottom-2 -right-2 w-10 h-10 bg-blue-600 text-white rounded-full flex items-center justify-center shadow-lg hover:bg-blue-700 transition-colors"
                    >
                      <FiCamera className="w-4 h-4" />
                    </button>
                  )}
                  <input
                    ref={fileInputRef}
                    type="file"
                    accept="image/*"
                    onChange={handleAvatarChange}
                    className="hidden"
                  />
                </div>
                
                <h2 className="text-2xl font-bold text-gray-900 dark:text-white mt-4">
                  {profile.firstName} {profile.lastName}
                </h2>
                <p className="text-gray-600 dark:text-gray-400">@{profile.username}</p>
                <div className="flex items-center justify-center space-x-2 mt-2">
                  <div className={`px-3 py-1 rounded-full text-xs font-medium ${
                    profile.role === 'estudiante' ? 'bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400' :
                    profile.role === 'profesor' ? 'bg-emerald-100 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-400' :
                    'bg-purple-100 text-purple-700 dark:bg-purple-900/30 dark:text-purple-400'
                  }`}>
                    {profile.role.charAt(0).toUpperCase() + profile.role.slice(1)}
                  </div>
                </div>
              </div>

              {/* Quick Stats */}
              <div className="grid grid-cols-2 gap-4 mb-6">
                <div className="text-center p-3 bg-gray-50 dark:bg-gray-700/50 rounded-xl">
                  <div className="text-2xl font-bold text-blue-600 dark:text-blue-400">
                    {profile.stats.level}
                  </div>
                  <div className="text-xs text-gray-500 dark:text-gray-400">Nivel</div>
                </div>
                <div className="text-center p-3 bg-gray-50 dark:bg-gray-700/50 rounded-xl">
                  <div className="text-2xl font-bold text-emerald-600 dark:text-emerald-400">
                    {profile.stats.points}
                  </div>
                  <div className="text-xs text-gray-500 dark:text-gray-400">Puntos</div>
                </div>
                <div className="text-center p-3 bg-gray-50 dark:bg-gray-700/50 rounded-xl">
                  <div className="text-2xl font-bold text-amber-600 dark:text-amber-400">
                    {profile.stats.achievements}
                  </div>
                  <div className="text-xs text-gray-500 dark:text-gray-400">Logros</div>
                </div>
                <div className="text-center p-3 bg-gray-50 dark:bg-gray-700/50 rounded-xl">
                  <div className="text-2xl font-bold text-red-600 dark:text-red-400">
                    {profile.stats.streakDays}
                  </div>
                  <div className="text-xs text-gray-500 dark:text-gray-400">Racha</div>
                </div>
              </div>

              {/* Level Progress */}
              <div className="mb-6">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
                    Progreso al Nivel {profile.stats.level + 1}
                  </span>
                  <span className="text-xs text-gray-500 dark:text-gray-400">
                    {Math.round(getLevelProgress())}%
                  </span>
                </div>
                <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                  <motion.div
                    initial={{ width: 0 }}
                    animate={{ width: `${getLevelProgress()}%` }}
                    transition={{ duration: 1, ease: "easeOut" }}
                    className="h-2 bg-gradient-to-r from-blue-500 to-purple-600 rounded-full"
                  />
                </div>
              </div>

              {/* Quick Actions */}
              <div className="space-y-2">
                <button 
                  onClick={() => navigate('/avatar')}
                  className="w-full flex items-center space-x-2 p-3 text-left hover:bg-gray-50 dark:hover:bg-gray-700/50 rounded-lg transition-colors"
                >
                  <HiSparkles className="w-5 h-5 text-purple-500" />
                  <span className="text-gray-700 dark:text-gray-300">Personalizar Avatar</span>
                </button>
                <button className="w-full flex items-center space-x-2 p-3 text-left hover:bg-gray-50 dark:hover:bg-gray-700/50 rounded-lg transition-colors">
                  <FiShield className="w-5 h-5 text-green-500" />
                  <span className="text-gray-700 dark:text-gray-300">Privacidad</span>
                </button>
                <button 
                  onClick={logout}
                  className="w-full flex items-center space-x-2 p-3 text-left hover:bg-red-50 dark:hover:bg-red-900/20 rounded-lg transition-colors text-red-600 dark:text-red-400"
                >
                  <FiX className="w-5 h-5" />
                  <span>Cerrar Sesión</span>
                </button>
              </div>
            </div>
          </div>

          {/* Main Content */}
          <div className="lg:col-span-2">
            {/* Tabs */}
            <div className="bg-white/80 dark:bg-gray-800/80 backdrop-blur-xl rounded-2xl border border-gray-200/50 dark:border-gray-700/50 overflow-hidden">
              <div className="border-b border-gray-200/50 dark:border-gray-700/50">
                <div className="flex overflow-x-auto">
                  {tabs.map((tab) => (
                    <motion.button
                      key={tab.id}
                      whileHover={{ scale: 1.02 }}
                      whileTap={{ scale: 0.98 }}
                      onClick={() => setActiveTab(tab.id as any)}
                      className={`flex items-center space-x-2 px-6 py-4 text-sm font-medium whitespace-nowrap border-b-2 transition-all duration-200 ${
                        activeTab === tab.id
                          ? 'border-blue-500 text-blue-600 dark:text-blue-400 bg-blue-50/50 dark:bg-blue-900/20'
                          : 'border-transparent text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-200 hover:border-gray-300'
                      }`}
                    >
                      <div className={`w-8 h-8 rounded-lg bg-gradient-to-r ${tab.color} flex items-center justify-center`}>
                        <tab.icon className="w-4 h-4 text-white" />
                      </div>
                      <span>{tab.name}</span>
                    </motion.button>
                  ))}
                </div>
              </div>

              {/* Tab Content */}
              <div className="p-6">
                <AnimatePresence mode="wait">
                  {activeTab === 'profile' && (
                    <motion.div
                      key="profile"
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      exit={{ opacity: 0, y: -20 }}
                      transition={{ duration: 0.3 }}
                      className="space-y-6"
                    >
                      {/* Bio Section */}
                      <div>
                        <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-3">
                          Biografía
                        </h3>
                        {isEditing ? (
                          <textarea
                            value={profile.bio}
                            onChange={(e) => setProfile(prev => ({ ...prev, bio: e.target.value }))}
                            className="w-full p-3 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white resize-none"
                            rows={4}
                            placeholder="Cuéntanos algo sobre ti..."
                          />
                        ) : (
                          <p className="text-gray-600 dark:text-gray-400 leading-relaxed">
                            {profile.bio}
                          </p>
                        )}
                      </div>

                      {/* Contact Information */}
                      <div>
                        <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
                          Información de Contacto
                        </h3>
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                          <div className="flex items-center space-x-3">
                            <FiMail className="w-5 h-5 text-gray-400" />
                            {isEditing ? (
                              <input
                                type="email"
                                value={profile.email}
                                onChange={(e) => setProfile(prev => ({ ...prev, email: e.target.value }))}
                                className="flex-1 p-2 border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
                              />
                            ) : (
                              <span className="text-gray-600 dark:text-gray-400">{profile.email}</span>
                            )}
                          </div>
                          
                          <div className="flex items-center space-x-3">
                            <FiPhone className="w-5 h-5 text-gray-400" />
                            {isEditing ? (
                              <input
                                type="tel"
                                value={profile.phone}
                                onChange={(e) => setProfile(prev => ({ ...prev, phone: e.target.value }))}
                                className="flex-1 p-2 border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
                              />
                            ) : (
                              <span className="text-gray-600 dark:text-gray-400">{profile.phone}</span>
                            )}
                          </div>

                          <div className="flex items-center space-x-3">
                            <FiMapPin className="w-5 h-5 text-gray-400" />
                            {isEditing ? (
                              <input
                                type="text"
                                value={profile.location}
                                onChange={(e) => setProfile(prev => ({ ...prev, location: e.target.value }))}
                                className="flex-1 p-2 border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
                              />
                            ) : (
                              <span className="text-gray-600 dark:text-gray-400">{profile.location}</span>
                            )}
                          </div>

                          <div className="flex items-center space-x-3">
                            <FiGlobe className="w-5 h-5 text-gray-400" />
                            {isEditing ? (
                              <input
                                type="url"
                                value={profile.website}
                                onChange={(e) => setProfile(prev => ({ ...prev, website: e.target.value }))}
                                className="flex-1 p-2 border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
                              />
                            ) : (
                              <a 
                                href={profile.website} 
                                target="_blank" 
                                rel="noopener noreferrer"
                                className="text-blue-600 dark:text-blue-400 hover:underline"
                              >
                                {profile.website}
                              </a>
                            )}
                          </div>
                        </div>
                      </div>

                      {/* Social Links */}
                      <div>
                        <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
                          Redes Sociales
                        </h3>
                        <div className="grid grid-cols-2 gap-4">
                          {[
                            { key: 'github', icon: FiGithub, name: 'GitHub', color: 'text-gray-700' },
                            { key: 'linkedin', icon: FiLinkedin, name: 'LinkedIn', color: 'text-blue-600' },
                            { key: 'twitter', icon: FiTwitter, name: 'Twitter', color: 'text-blue-400' },
                            { key: 'instagram', icon: FiInstagram, name: 'Instagram', color: 'text-pink-600' }
                          ].map(social => (
                            <div key={social.key} className="flex items-center space-x-3">
                              <social.icon className={`w-5 h-5 ${social.color}`} />
                              {isEditing ? (
                                <input
                                  type="url"
                                  value={profile.socialLinks[social.key as keyof typeof profile.socialLinks] || ''}
                                  onChange={(e) => setProfile(prev => ({
                                    ...prev,
                                    socialLinks: {
                                      ...prev.socialLinks,
                                      [social.key]: e.target.value
                                    }
                                  }))}
                                  placeholder={`Tu perfil de ${social.name}`}
                                  className="flex-1 p-2 border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
                                />
                              ) : (
                                <span className="text-gray-600 dark:text-gray-400">
                                  {profile.socialLinks[social.key as keyof typeof profile.socialLinks] || `No configurado`}
                                </span>
                              )}
                            </div>
                          ))}
                        </div>
                      </div>
                    </motion.div>
                  )}

                  {activeTab === 'achievements' && (
                    <motion.div
                      key="achievements"
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      exit={{ opacity: 0, y: -20 }}
                      transition={{ duration: 0.3 }}
                      className="space-y-6"
                    >
                      <div className="flex items-center justify-between">
                        <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                          Mis Logros ({profile.achievements.length})
                        </h3>
                        <div className="text-sm text-gray-500 dark:text-gray-400">
                          {profile.stats.points} puntos totales
                        </div>
                      </div>

                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        {profile.achievements.map((achievement, index) => (
                          <motion.div
                            key={achievement.id}
                            initial={{ opacity: 0, scale: 0.9 }}
                            animate={{ opacity: 1, scale: 1 }}
                            transition={{ delay: index * 0.1, duration: 0.3 }}
                            className="p-4 bg-gray-50 dark:bg-gray-700/50 rounded-xl hover:shadow-lg transition-all duration-300"
                          >
                            <div className="flex items-start space-x-3">
                              <div className={`w-12 h-12 bg-gradient-to-r ${achievement.color} rounded-xl flex items-center justify-center text-2xl shadow-lg`}>
                                {achievement.icon}
                              </div>
                              <div className="flex-1">
                                <h4 className="font-semibold text-gray-900 dark:text-white mb-1">
                                  {achievement.name}
                                </h4>
                                <p className="text-sm text-gray-600 dark:text-gray-400 mb-2">
                                  {achievement.description}
                                </p>
                                <div className="flex items-center text-xs text-gray-500 dark:text-gray-400">
                                  <FiCalendar className="w-3 h-3 mr-1" />
                                  {new Date(achievement.unlockedAt).toLocaleDateString()}
                                </div>
                              </div>
                            </div>
                          </motion.div>
                        ))}
                      </div>
                    </motion.div>
                  )}

                  {activeTab === 'stats' && (
                    <motion.div
                      key="stats"
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      exit={{ opacity: 0, y: -20 }}
                      transition={{ duration: 0.3 }}
                      className="space-y-6"
                    >
                      <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                        Estadísticas de Aprendizaje
                      </h3>

                      {/* Main Stats */}
                      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                        {[
                          { label: 'Cursos Completados', value: profile.stats.courses, icon: FiBookOpen, color: 'from-blue-500 to-indigo-600' },
                          { label: 'Horas de Estudio', value: '127h', icon: FiClock, color: 'from-emerald-500 to-teal-600' },
                          { label: 'Calificación Promedio', value: '94%', icon: FiStar, color: 'from-amber-500 to-orange-600' }
                        ].map((stat, index) => (
                          <motion.div
                            key={index}
                            initial={{ opacity: 0, scale: 0.9 }}
                            animate={{ opacity: 1, scale: 1 }}
                            transition={{ delay: index * 0.1, duration: 0.3 }}
                            className="p-6 bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 shadow-sm"
                          >
                            <div className="flex items-center justify-between">
                              <div>
                                <p className="text-sm font-medium text-gray-600 dark:text-gray-400 mb-1">
                                  {stat.label}
                                </p>
                                <p className="text-3xl font-bold text-gray-900 dark:text-white">
                                  {stat.value}
                                </p>
                              </div>
                              <div className={`w-14 h-14 bg-gradient-to-r ${stat.color} rounded-xl flex items-center justify-center`}>
                                <stat.icon className="w-7 h-7 text-white" />
                              </div>
                            </div>
                          </motion.div>
                        ))}
                      </div>

                      {/* Activity Chart Placeholder */}
                      <div className="p-6 bg-gray-50 dark:bg-gray-700/50 rounded-xl">
                        <h4 className="font-semibold text-gray-900 dark:text-white mb-4">
                          Actividad Reciente
                        </h4>
                        <div className="h-32 flex items-center justify-center text-gray-500 dark:text-gray-400">
                          <FiTrendingUp className="w-8 h-8 mr-2" />
                          <span>Gráfico de actividad (próximamente)</span>
                        </div>
                      </div>
                    </motion.div>
                  )}

                  {activeTab === 'settings' && (
                    <motion.div
                      key="settings"
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      exit={{ opacity: 0, y: -20 }}
                      transition={{ duration: 0.3 }}
                      className="space-y-6"
                    >
                      <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                        Configuración de Cuenta
                      </h3>

                      {/* Preferences */}
                      <div className="space-y-4">
                        {[
                          { key: 'emailNotifications', label: 'Notificaciones por Email', description: 'Recibir actualizaciones y recordatorios por correo' },
                          { key: 'pushNotifications', label: 'Notificaciones Push', description: 'Notificaciones en tiempo real en el navegador' },
                          { key: 'publicProfile', label: 'Perfil Público', description: 'Permitir que otros vean tu perfil y logros' },
                          { key: 'showStats', label: 'Mostrar Estadísticas', description: 'Hacer visibles tus estadísticas de aprendizaje' }
                        ].map((setting) => (
                          <div key={setting.key} className="flex items-center justify-between p-4 bg-gray-50 dark:bg-gray-700/50 rounded-xl">
                            <div>
                              <h4 className="font-medium text-gray-900 dark:text-white">
                                {setting.label}
                              </h4>
                              <p className="text-sm text-gray-600 dark:text-gray-400">
                                {setting.description}
                              </p>
                            </div>
                            <button
                              onClick={() => setProfile(prev => ({
                                ...prev,
                                preferences: {
                                  ...prev.preferences,
                                  [setting.key]: !prev.preferences[setting.key as keyof typeof prev.preferences]
                                }
                              }))}
                              className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                                profile.preferences[setting.key as keyof typeof profile.preferences]
                                  ? 'bg-blue-600'
                                  : 'bg-gray-200 dark:bg-gray-700'
                              }`}
                            >
                              <span
                                className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                                  profile.preferences[setting.key as keyof typeof profile.preferences]
                                    ? 'translate-x-6'
                                    : 'translate-x-1'
                                }`}
                              />
                            </button>
                          </div>
                        ))}
                      </div>

                      {/* Danger Zone */}
                      <div className="border-t border-gray-200 dark:border-gray-700 pt-6">
                        <h4 className="text-lg font-semibold text-red-600 dark:text-red-400 mb-4">
                          Zona de Peligro
                        </h4>
                        <div className="space-y-3">
                          <button className="w-full p-3 border border-red-300 dark:border-red-700 text-red-600 dark:text-red-400 rounded-lg hover:bg-red-50 dark:hover:bg-red-900/20 transition-colors">
                            Eliminar todos los datos
                          </button>
                          <button className="w-full p-3 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors">
                            Eliminar cuenta permanentemente
                          </button>
                        </div>
                      </div>
                    </motion.div>
                  )}
                </AnimatePresence>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}