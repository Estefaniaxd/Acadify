import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { avatarAPI, UserAvatar } from './avatarAPI';
import SimpleAvatar from './SimpleAvatar';

interface PublicAvatarGalleryProps {
  className?: string;
}

const mockAvatars: UserAvatar[] = [
  {
    id: 'public-1',
    name: 'Avatar Épico',
    base_gender: 'male',
    layers: [],
    is_active: false,
    is_public: true,
    image_url: 'https://api.dicebear.com/7.x/bottts/svg?seed=epic',
    created_at: '2025-09-22T10:00:00Z',
    updated_at: '2025-09-22T10:00:00Z',
    user_id: 'user-1',
    layers_hash: 'hash1'
  },
  {
    id: 'public-2',
    name: 'Robot Futurista',
    base_gender: 'female',
    layers: [],
    is_active: false,
    is_public: true,
    image_url: 'https://api.dicebear.com/7.x/bottts/svg?seed=robot',
    created_at: '2025-09-22T11:00:00Z',
    updated_at: '2025-09-22T11:00:00Z',
    user_id: 'user-2',
    layers_hash: 'hash2'
  },
  {
    id: 'public-3',
    name: 'Aventurero',
    base_gender: 'male',
    layers: [],
    is_active: false,
    is_public: true,
    image_url: 'https://api.dicebear.com/7.x/bottts/svg?seed=adventurer',
    created_at: '2025-09-22T12:00:00Z',
    updated_at: '2025-09-22T12:00:00Z',
    user_id: 'user-3',
    layers_hash: 'hash3'
  }
];

const PublicAvatarGallery: React.FC<PublicAvatarGalleryProps> = ({ className = '' }) => {
  const [avatars, setAvatars] = useState<UserAvatar[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [sortBy, setSortBy] = useState('newest');
  const [filterGender, setFilterGender] = useState<'all' | 'male' | 'female'>('all');

  // Cargar avatars públicos
  useEffect(() => {
    loadPublicAvatars();
  }, []);

  const loadPublicAvatars = async () => {
    try {
      setLoading(true);
      const publicAvatars = await avatarAPI.getPublicAvatars(0, 50);
      
      // Si no hay avatars reales, usar mock data
      if (publicAvatars.length === 0) {
        setAvatars(mockAvatars);
      } else {
        setAvatars(publicAvatars);
      }
    } catch (error) {
      console.error('Error loading public avatars:', error);
      // Fallback a datos mock en caso de error
      setAvatars(mockAvatars);
    } finally {
      setLoading(false);
    }
  };

  const filteredAndSortedAvatars = React.useMemo(() => {
    let filtered = avatars.filter((avatar: UserAvatar) =>
      avatar.name.toLowerCase().includes(searchTerm.toLowerCase())
    );

    // Filtrar por género si está seleccionado
    if (filterGender !== 'all') {
      filtered = filtered.filter((avatar: UserAvatar) => avatar.base_gender === filterGender);
    }

    // Ordenar
    if (sortBy === 'name') {
      filtered = [...filtered].sort((a, b) => a.name.localeCompare(b.name));
    } else if (sortBy === 'recent') {
      filtered = [...filtered].sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime());
    }
    return filtered;
  }, [avatars, searchTerm, sortBy, filterGender]);

  if (loading) {
    return (
      <div className={className}>
        <div className="flex items-center justify-center py-12">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-purple-600"></div>
          <span className="ml-3 text-gray-600 dark:text-gray-400">Cargando avatares públicos...</span>
        </div>
      </div>
    );
  }

  return (
    <div className={className}>
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between mb-6">
        <div>
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">🌟 Galería Pública de Avatares</h2>
          <p className="text-gray-600 dark:text-gray-400">Descubre y vota por los mejores avatares de la comunidad Acadify</p>
        </div>
        <div className="mt-4 sm:mt-0 bg-gradient-to-r from-violet-500 to-purple-600 text-white px-4 py-2 rounded-lg text-center">
          <div className="text-lg font-bold">{filteredAndSortedAvatars.length}</div>
          <div className="text-xs opacity-90">Avatares públicos</div>
        </div>
      </div>
      <div className="flex flex-col sm:flex-row gap-4 mb-6">
        <div className="flex-1">
          <div className="relative">
            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              <svg className="h-4 w-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
            </div>
            <input
              type="text"
              placeholder="Buscar avatares públicos..."
              value={searchTerm}
              onChange={e => setSearchTerm(e.target.value)}
              className="block w-full pl-10 pr-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-purple-500"
            />
          </div>
        </div>
        <div className="flex gap-2">
          {/* Filtro por género */}
          <select
            value={filterGender}
            onChange={(e) => setFilterGender(e.target.value as 'all' | 'male' | 'female')}
            className="px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-purple-500"
          >
            <option value="all">Todos</option>
            <option value="male">♂️ Masculino</option>
            <option value="female">♀️ Femenino</option>
          </select>
          
          {/* Orden */}
          <select
            value={sortBy}
            onChange={e => setSortBy(e.target.value as 'recent' | 'popular' | 'name')}
            className="px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-purple-500"
          >
            <option value="recent">Más recientes</option>
            <option value="popular">Más populares</option>
            <option value="name">Por nombre</option>
          </select>
        </div>
      </div>
      {filteredAndSortedAvatars.length === 0 ? (
        <div className="text-center py-12">
          <div className="w-24 h-24 mx-auto mb-4 bg-gray-100 dark:bg-gray-800 rounded-full flex items-center justify-center">
            <svg className="w-12 h-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
            </svg>
          </div>
          <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">No se encontraron avatares públicos</h3>
          <p className="text-gray-500 dark:text-gray-400">Prueba con diferentes términos de búsqueda.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
          {filteredAndSortedAvatars.map((avatar, index) => (
            <motion.div
              key={avatar.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1, duration: 0.3 }}
              className="group bg-white dark:bg-gray-800 rounded-xl shadow-lg hover:shadow-2xl transition-all duration-300 overflow-hidden cursor-pointer border border-gray-200 dark:border-gray-700"
            >
              <div className="relative aspect-square bg-gradient-to-br from-violet-100 to-purple-100 dark:from-violet-900/20 dark:to-purple-900/20 p-4 flex items-center justify-center">
                <SimpleAvatar 
                  imageUrl={avatar.image_url || ''}
                  name={avatar.name}
                  size="large"
                />
                <div className="absolute top-2 left-2">
                  <span className="px-2 py-1 text-xs font-medium bg-black/50 text-white rounded-full backdrop-blur-sm">
                    🔥 {Math.floor(Math.random() * 50) + 10} votos
                  </span>
                </div>
                <div className="absolute top-2 right-2">
                  <span className={`px-2 py-1 text-xs font-medium rounded-full ${
                    avatar.base_gender === 'male' 
                      ? 'bg-blue-500/20 text-blue-600' 
                      : 'bg-pink-500/20 text-pink-600'
                  }`}>
                    {avatar.base_gender === 'male' ? '♂️' : '♀️'}
                  </span>
                </div>
              </div>
              <div className="p-4">
                <div className="flex items-start justify-between mb-2">
                  <h3 className="font-medium text-gray-900 dark:text-white truncate flex-1">{avatar.name}</h3>
                </div>
                <div className="flex items-center justify-between text-xs text-gray-500 dark:text-gray-400 mb-3">
                  <div className="flex items-center gap-1">
                    <svg className="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M10 9a3 3 0 100-6 3 3 0 000 6zm-7 9a7 7 0 1114 0H3z" clipRule="evenodd" />
                    </svg>
                    <span>u/usuario{Math.floor(Math.random() * 1000)}</span>
                  </div>
                  <span>{new Date(avatar.created_at).toLocaleDateString()}</span>
                </div>
                <div className="flex gap-2">
                  <button
                    onClick={e => {
                      e.stopPropagation();
                      // TODO: Inspirarse en este avatar
                    }}
                    className="flex-1 px-3 py-1.5 text-sm font-medium text-purple-600 border border-purple-600 rounded-lg hover:bg-purple-600 hover:text-white transition-colors"
                  >
                    Inspirarme
                  </button>
                  <button
                    onClick={e => {
                      e.stopPropagation();
                      navigator.clipboard.writeText(avatar.image_url || '');
                    }}
                    className="px-3 py-1.5 text-sm font-medium text-gray-600 dark:text-gray-300 border border-gray-300 dark:border-gray-600 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
                    title="Compartir"
                  >
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8.684 13.342C8.886 12.938 9 12.482 9 12c0-.482-.114-.938-.316-1.342m0 2.684a3 3 0 110-2.684m0 2.684l6.632 3.316m-6.632-6l6.632-3.316m0 0a3 3 0 105.367-2.684 3 3 0 00-5.367-2.684zm0 9.316a3 3 0 105.367 2.684 3 3 0 00-5.367-2.684z" />
                    </svg>
                  </button>
                </div>
              </div>
            </motion.div>
          ))}
        </div>
      )}
    </div>
  );
};

export default PublicAvatarGallery;