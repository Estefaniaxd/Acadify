import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useAuth } from '../context/AuthContext';
import { avatarAPI, type UserAvatar } from '../components/avatar/avatarAPI';
import { useToast } from '../context/ToastContext';
import { 
  FiUser, FiSettings, FiAward, FiBarChart, FiEye, FiTrash2, 
  FiStar, FiX, FiPlus, FiEdit3, FiCheck, FiImage 
} from 'react-icons/fi';

type ProfileTab = 'perfil' | 'logros' | 'estadisticas' | 'configuracion' | 'avatares';

export default function Perfil() {
  const { user } = useAuth();
  const { success, error: showError } = useToast();
  const [activeTab, setActiveTab] = useState<ProfileTab>('perfil');
  const [avatarUrl, setAvatarUrl] = useState<string | null>(null);
  const [userAvatars, setUserAvatars] = useState<UserAvatar[]>([]);
  const [loading, setLoading] = useState(true);
  const [loadingAvatars, setLoadingAvatars] = useState(false);
  const [selectedAvatar, setSelectedAvatar] = useState<UserAvatar | null>(null);

  useEffect(() => {
    const loadUserData = async () => {
      if (!user) {
        setLoading(false);
        return;
      }

      try {
        setLoadingAvatars(true);
        const avatars = await avatarAPI.getMyAvatars();
        setUserAvatars(avatars.avatars);
        
        const activeAvatar = avatars.avatars.find(avatar => avatar.is_active);
        
        if (activeAvatar && activeAvatar.image_url) {
          setAvatarUrl(activeAvatar.image_url);
        } else {
          // Fallback a dicebear si no hay avatar activo
          setAvatarUrl(`https://api.dicebear.com/7.x/adventurer/svg?seed=${user.username || 'user'}&backgroundColor=b6e3f4,c0aede,d1d4f9`);
        }
      } catch (error) {
        console.error('Error loading user data:', error);
        // Fallback a dicebear en caso de error
        setAvatarUrl(`https://api.dicebear.com/7.x/adventurer/svg?seed=${user?.username || 'user'}&backgroundColor=b6e3f4,c0aede,d1d4f9`);
      } finally {
        setLoading(false);
        setLoadingAvatars(false);
      }
    };

    loadUserData();
  }, [user]);

  const handleActivateAvatar = async (avatar: UserAvatar) => {
    try {
      await avatarAPI.setActiveAvatar(avatar.id);
      
      // Actualizar estado local
      setUserAvatars(prev => 
        prev.map(a => ({
          ...a,
          is_active: a.id === avatar.id
        }))
      );
      
      setAvatarUrl(avatar.image_url);
      success(`Avatar "${avatar.name}" activado`);
      
      // Disparar evento para actualizar navegación
      window.dispatchEvent(new CustomEvent('avatar-updated', { 
        detail: { ...avatar, is_active: true }
      }));
      
    } catch (error) {
      console.error('Error activating avatar:', error);
      showError('Error al activar el avatar');
    }
  };

  const handleDeleteAvatar = async (avatar: UserAvatar) => {
    if (avatar.is_active) {
      showError('No puedes eliminar tu avatar activo');
      return;
    }

    try {
      await avatarAPI.deleteAvatar(avatar.id);
      setUserAvatars(prev => prev.filter(a => a.id !== avatar.id));
      success(`Avatar "${avatar.name}" eliminado`);
      setSelectedAvatar(null);
    } catch (error) {
      console.error('Error deleting avatar:', error);
      showError('Error al eliminar el avatar');
    }
  };

  const fallbackUrl = `https://api.dicebear.com/7.x/adventurer/svg?seed=${user?.username || 'user'}&backgroundColor=b6e3f4,c0aede,d1d4f9`;

  const tabs = [
    { id: 'perfil', label: 'Perfil', icon: FiUser, color: 'from-violet-500 to-purple-600' },
    { id: 'avatares', label: 'Avatares', icon: FiImage, color: 'from-blue-500 to-indigo-600' },
    { id: 'logros', label: 'Logros', icon: FiAward, color: 'from-yellow-500 to-orange-600' },
    { id: 'estadisticas', label: 'Estadísticas', icon: FiBarChart, color: 'from-emerald-500 to-teal-600' },
    { id: 'configuracion', label: 'Configuración', icon: FiSettings, color: 'from-gray-500 to-gray-600' },
  ] as const;

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 via-purple-50 to-blue-50 dark:from-gray-900 dark:via-purple-900/20 dark:to-blue-900/20 pt-20">
      <div className="container mx-auto px-4 py-8 max-w-6xl">
        {/* Header */}
        <motion.div 
          initial={{ opacity: 0, y: -30 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center mb-12"
        >
          <h1 className="text-4xl font-black bg-gradient-to-r from-purple-600 via-blue-600 to-indigo-600 bg-clip-text text-transparent mb-4">
            Mi Perfil
          </h1>
          <p className="text-gray-600 dark:text-gray-400 text-lg">
            Gestiona tu información y avatares personalizados
          </p>
        </motion.div>

        <div className="grid lg:grid-cols-4 gap-8">
          {/* Sidebar de tabs */}
          <div className="lg:col-span-1">
            <motion.div 
              initial={{ opacity: 0, x: -30 }}
              animate={{ opacity: 1, x: 0 }}
              className="bg-white/70 dark:bg-gray-800/70 backdrop-blur-xl rounded-2xl shadow-xl p-6 border border-white/20 dark:border-gray-700/30"
            >
              <div className="space-y-2">
                {tabs.map((tab, index) => {
                  const Icon = tab.icon;
                  const isActive = activeTab === tab.id;
                  
                  return (
                    <motion.button
                      key={tab.id}
                      initial={{ opacity: 0, x: -20 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: index * 0.1 }}
                      onClick={() => setActiveTab(tab.id as ProfileTab)}
                      className={`w-full text-left p-4 rounded-xl transition-all duration-300 flex items-center gap-3 ${
                        isActive
                          ? 'bg-gradient-to-r text-white shadow-lg transform scale-105'
                          : 'hover:bg-gray-100 dark:hover:bg-gray-700 text-gray-600 dark:text-gray-300'
                      }`}
                      style={isActive ? { backgroundImage: `linear-gradient(135deg, ${tab.color.split(' ')[0].replace('from-', '')}, ${tab.color.split(' ')[2].replace('to-', '')})` } : {}}
                    >
                      <Icon className="text-lg" />
                      <span className="font-medium">{tab.label}</span>
                    </motion.button>
                  );
                })}
              </div>
            </motion.div>
          </div>

          {/* Content Area */}
          <div className="lg:col-span-3">
            <motion.div 
              initial={{ opacity: 0, x: 30 }}
              animate={{ opacity: 1, x: 0 }}
              className="bg-white/70 dark:bg-gray-800/70 backdrop-blur-xl rounded-2xl shadow-xl p-8 border border-white/20 dark:border-gray-700/30 min-h-[600px]"
            >
              <AnimatePresence mode="wait">
                {activeTab === 'perfil' && (
                  <motion.div
                    key="perfil"
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -20 }}
                    className="space-y-8"
                  >
                    <div className="text-center">
                      {loading ? (
                        <div className="w-32 h-32 rounded-full bg-gray-200 dark:bg-gray-700 animate-pulse border-4 border-purple-500 mx-auto mb-6" />
                      ) : (
                        <motion.img 
                          whileHover={{ scale: 1.05 }}
                          src={avatarUrl || fallbackUrl} 
                          alt="avatar" 
                          className="w-32 h-32 rounded-full border-4 border-purple-500 mx-auto mb-6 object-cover object-top shadow-2xl"
                          style={{ 
                            objectPosition: 'center 25%',
                            clipPath: 'inset(0 0 20% 0)',
                          }}
                          onError={(e) => {
                            e.currentTarget.src = fallbackUrl;
                          }}
                        />
                      )}
                      <h2 className="text-2xl font-bold text-gray-800 dark:text-gray-200 mb-2">
                        {user?.username || 'Usuario'}
                      </h2>
                      <p className="text-gray-600 dark:text-gray-400">{user?.email}</p>
                    </div>

                    <form className="space-y-6 max-w-md mx-auto">
                      <div>
                        <label className="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">
                          Nombre de usuario
                        </label>
                        <input 
                          className="w-full px-4 py-3 rounded-xl border border-gray-200 dark:border-gray-600 bg-gray-50 dark:bg-gray-700 text-gray-800 dark:text-gray-200 focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all" 
                          placeholder="Nombre de usuario" 
                          defaultValue={user?.username} 
                        />
                      </div>
                      
                      <div>
                        <label className="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">
                          Correo electrónico
                        </label>
                        <input 
                          className="w-full px-4 py-3 rounded-xl border border-gray-200 dark:border-gray-600 bg-gray-50 dark:bg-gray-700 text-gray-800 dark:text-gray-200 focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all" 
                          placeholder="Correo" 
                          defaultValue={user?.email} 
                        />
                      </div>
                      
                      <div>
                        <label className="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">
                          Nueva contraseña
                        </label>
                        <input 
                          className="w-full px-4 py-3 rounded-xl border border-gray-200 dark:border-gray-600 bg-gray-50 dark:bg-gray-700 text-gray-800 dark:text-gray-200 focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all" 
                          placeholder="Nueva contraseña" 
                          type="password" 
                        />
                      </div>
                      
                      <motion.button 
                        whileHover={{ scale: 1.02 }}
                        whileTap={{ scale: 0.98 }}
                        className="w-full px-6 py-3 rounded-xl bg-gradient-to-r from-purple-600 to-blue-600 text-white font-semibold hover:shadow-lg transition-all"
                      >
                        Guardar cambios
                      </motion.button>
                    </form>
                  </motion.div>
                )}

                {activeTab === 'avatares' && (
                  <motion.div
                    key="avatares"
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -20 }}
                    className="space-y-6"
                  >
                    <div className="flex items-center justify-between">
                      <div>
                        <h3 className="text-2xl font-bold text-gray-800 dark:text-gray-200 mb-2">
                          Mi Galería de Avatares
                        </h3>
                        <p className="text-gray-600 dark:text-gray-400">
                          Gestiona tus avatares personalizados ({userAvatars.length}/5)
                        </p>
                      </div>
                      
                      {userAvatars.length < 5 && (
                        <motion.button
                          whileHover={{ scale: 1.05 }}
                          whileTap={{ scale: 0.95 }}
                          onClick={() => window.location.href = '/avatar'}
                          className="bg-gradient-to-r from-emerald-500 to-teal-600 text-white px-6 py-3 rounded-xl font-semibold shadow-lg hover:shadow-xl transition-all flex items-center gap-2"
                        >
                          <FiPlus className="text-lg" />
                          Crear Avatar
                        </motion.button>
                      )}
                    </div>

                    {loadingAvatars ? (
                      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                        {[...Array(3)].map((_, i) => (
                          <div key={i} className="bg-gray-200 dark:bg-gray-700 animate-pulse rounded-2xl h-64" />
                        ))}
                      </div>
                    ) : userAvatars.length === 0 ? (
                      <motion.div
                        initial={{ opacity: 0, scale: 0.9 }}
                        animate={{ opacity: 1, scale: 1 }}
                        className="text-center py-16"
                      >
                        <div className="w-24 h-24 bg-gray-200 dark:bg-gray-700 rounded-2xl flex items-center justify-center mx-auto mb-6">
                          <FiImage className="text-4xl text-gray-400" />
                        </div>
                        <h4 className="text-xl font-semibold text-gray-600 dark:text-gray-400 mb-4">
                          No tienes avatares aún
                        </h4>
                        <p className="text-gray-500 dark:text-gray-500 mb-6">
                          Crea tu primer avatar personalizado para comenzar
                        </p>
                        <motion.button
                          whileHover={{ scale: 1.05 }}
                          whileTap={{ scale: 0.95 }}
                          onClick={() => window.location.href = '/avatar'}
                          className="bg-gradient-to-r from-purple-600 to-blue-600 text-white px-8 py-3 rounded-xl font-semibold shadow-lg"
                        >
                          <FiPlus className="inline mr-2" />
                          Crear Mi Primer Avatar
                        </motion.button>
                      </motion.div>
                    ) : (
                      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                        {userAvatars.map((avatar, index) => (
                          <motion.div
                            key={avatar.id}
                            initial={{ opacity: 0, scale: 0.9 }}
                            animate={{ opacity: 1, scale: 1 }}
                            transition={{ delay: index * 0.1 }}
                            className={`relative bg-white dark:bg-gray-800 rounded-2xl shadow-lg overflow-hidden border-2 transition-all duration-300 hover:shadow-2xl group ${
                              avatar.is_active 
                                ? 'border-purple-500 ring-2 ring-purple-200 dark:ring-purple-700' 
                                : 'border-gray-200 dark:border-gray-600 hover:border-purple-300'
                            }`}
                          >
                            {/* Avatar activo badge */}
                            {avatar.is_active && (
                              <motion.div
                                initial={{ scale: 0 }}
                                animate={{ scale: 1 }}
                                className="absolute top-3 right-3 bg-purple-600 text-white px-3 py-1 rounded-full text-xs font-bold flex items-center gap-1 z-10"
                              >
                                <FiStar className="text-xs" />
                                Activo
                              </motion.div>
                            )}

                            {/* Avatar Image */}
                            <div className="relative aspect-square overflow-hidden">
                              <img
                                src={avatar.image_url}
                                alt={avatar.name}
                                className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-300"
                                onError={(e) => {
                                  e.currentTarget.src = fallbackUrl;
                                }}
                              />
                              <div className="absolute inset-0 bg-gradient-to-t from-black/30 to-transparent opacity-0 group-hover:opacity-100 transition-opacity" />
                              
                              {/* Hover controls */}
                              <div className="absolute inset-0 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity">
                                <div className="flex gap-2">
                                  <motion.button
                                    whileHover={{ scale: 1.1 }}
                                    whileTap={{ scale: 0.9 }}
                                    onClick={() => setSelectedAvatar(avatar)}
                                    className="w-10 h-10 bg-white/90 rounded-full flex items-center justify-center shadow-lg hover:bg-white transition-colors"
                                    title="Ver detalles"
                                  >
                                    <FiEye className="text-gray-700" />
                                  </motion.button>
                                  
                                  {!avatar.is_active && (
                                    <motion.button
                                      whileHover={{ scale: 1.1 }}
                                      whileTap={{ scale: 0.9 }}
                                      onClick={() => handleActivateAvatar(avatar)}
                                      className="w-10 h-10 bg-emerald-500 rounded-full flex items-center justify-center shadow-lg hover:bg-emerald-600 transition-colors"
                                      title="Activar avatar"
                                    >
                                      <FiCheck className="text-white" />
                                    </motion.button>
                                  )}
                                  
                                  {!avatar.is_active && (
                                    <motion.button
                                      whileHover={{ scale: 1.1 }}
                                      whileTap={{ scale: 0.9 }}
                                      onClick={() => handleDeleteAvatar(avatar)}
                                      className="w-10 h-10 bg-red-500 rounded-full flex items-center justify-center shadow-lg hover:bg-red-600 transition-colors"
                                      title="Eliminar avatar"
                                    >
                                      <FiTrash2 className="text-white" />
                                    </motion.button>
                                  )}
                                </div>
                              </div>
                            </div>

                            {/* Avatar Info */}
                            <div className="p-4">
                              <h4 className="font-bold text-gray-800 dark:text-gray-200 mb-1">
                                {avatar.name}
                              </h4>
                              <p className="text-sm text-gray-500 dark:text-gray-400 mb-2">
                                {avatar.layers.length} elementos
                              </p>
                              <div className="flex items-center justify-between">
                                <span className={`text-xs px-2 py-1 rounded-full ${
                                  avatar.is_public 
                                    ? 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400'
                                    : 'bg-gray-100 text-gray-700 dark:bg-gray-700 dark:text-gray-300'
                                }`}>
                                  {avatar.is_public ? 'Público' : 'Privado'}
                                </span>
                                <span className="text-xs text-gray-400">
                                  {new Date(avatar.created_at).toLocaleDateString()}
                                </span>
                              </div>
                            </div>
                          </motion.div>
                        ))}
                      </div>
                    )}
                  </motion.div>
                )}

                {/* Otros tabs placeholder */}
                {(activeTab === 'logros' || activeTab === 'estadisticas' || activeTab === 'configuracion') && (
                  <motion.div
                    key={activeTab}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -20 }}
                    className="text-center py-16"
                  >
                    <h3 className="text-2xl font-bold text-gray-800 dark:text-gray-200 mb-4 capitalize">
                      {activeTab}
                    </h3>
                    <p className="text-gray-600 dark:text-gray-400">
                      Esta sección está en desarrollo. Próximamente disponible.
                    </p>
                  </motion.div>
                )}
              </AnimatePresence>
            </motion.div>
          </div>
        </div>

        {/* Modal de detalles del avatar */}
        <AnimatePresence>
          {selectedAvatar && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4"
              onClick={() => setSelectedAvatar(null)}
            >
              <motion.div
                initial={{ scale: 0.9, opacity: 0 }}
                animate={{ scale: 1, opacity: 1 }}
                exit={{ scale: 0.9, opacity: 0 }}
                className="bg-white dark:bg-gray-800 rounded-2xl shadow-2xl max-w-md w-full overflow-hidden"
                onClick={(e) => e.stopPropagation()}
              >
                <div className="relative">
                  <img
                    src={selectedAvatar.image_url}
                    alt={selectedAvatar.name}
                    className="w-full h-64 object-cover"
                  />
                  <button
                    onClick={() => setSelectedAvatar(null)}
                    className="absolute top-4 right-4 w-8 h-8 bg-white/90 rounded-full flex items-center justify-center hover:bg-white transition-colors"
                  >
                    <FiX className="text-gray-700" />
                  </button>
                </div>
                
                <div className="p-6">
                  <h3 className="text-xl font-bold text-gray-800 dark:text-gray-200 mb-2">
                    {selectedAvatar.name}
                  </h3>
                  <p className="text-gray-600 dark:text-gray-400 mb-4">
                    Creado el {new Date(selectedAvatar.created_at).toLocaleDateString()}
                  </p>
                  
                  <div className="space-y-3">
                    <h4 className="font-semibold text-gray-800 dark:text-gray-200">
                      Elementos del avatar:
                    </h4>
                    <div className="grid grid-cols-2 gap-2">
                      {selectedAvatar.layers.map((layer, index) => (
                        <div key={index} className="bg-gray-100 dark:bg-gray-700 px-3 py-2 rounded-lg text-sm">
                          <span className="font-medium capitalize">{layer.category}:</span>
                          <br />
                          <span className="text-gray-600 dark:text-gray-400 text-xs">
                            {layer.filename}
                          </span>
                        </div>
                      ))}
                    </div>
                  </div>
                  
                  <div className="flex gap-3 mt-6">
                    {!selectedAvatar.is_active && (
                      <motion.button
                        whileHover={{ scale: 1.02 }}
                        whileTap={{ scale: 0.98 }}
                        onClick={() => {
                          handleActivateAvatar(selectedAvatar);
                          setSelectedAvatar(null);
                        }}
                        className="flex-1 bg-gradient-to-r from-emerald-500 to-teal-600 text-white py-3 px-4 rounded-xl font-semibold"
                      >
                        Activar Avatar
                      </motion.button>
                    )}
                    {!selectedAvatar.is_active && (
                      <motion.button
                        whileHover={{ scale: 1.02 }}
                        whileTap={{ scale: 0.98 }}
                        onClick={() => {
                          handleDeleteAvatar(selectedAvatar);
                          setSelectedAvatar(null);
                        }}
                        className="bg-red-500 text-white py-3 px-4 rounded-xl font-semibold hover:bg-red-600 transition-colors"
                      >
                        <FiTrash2 />
                      </motion.button>
                    )}
                  </div>
                </div>
              </motion.div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
}
