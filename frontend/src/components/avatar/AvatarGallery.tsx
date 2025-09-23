import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useToast } from '../../context/ToastContext';
import { useUserAvatars } from './useAvatar';
import { UserAvatar } from './avatarAPI';

interface AvatarGalleryProps {
  onEditAvatar?: (avatar: UserAvatar) => void;
  onSelectAvatar?: (avatar: UserAvatar) => void;
  className?: string;
}

export const AvatarGallery: React.FC<AvatarGalleryProps> = ({
  onEditAvatar,
  onSelectAvatar,
  className = ''
}) => {
  const toast = useToast();
  const { avatars: userAvatarsList, deleteAvatar, setActiveAvatar, isLoading, loadAvatars } = useUserAvatars();
  const [avatars, setAvatars] = useState<UserAvatar[]>([]);
  const [selectedAvatar, setSelectedAvatar] = useState<UserAvatar | null>(null);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState<UserAvatar | null>(null);
  const [sortBy, setSortBy] = useState<'created' | 'name' | 'active'>('created');
  const [filterBy, setFilterBy] = useState<'all' | 'active' | 'public' | 'private'>('all');
  const [searchTerm, setSearchTerm] = useState('');

  // Sincronizar avatares del hook con estado local
  useEffect(() => {
    setAvatars(userAvatarsList);
  }, [userAvatarsList]);

  // Filtrar y ordenar avatares
  const filteredAndSortedAvatars = React.useMemo(() => {
    let filtered = avatars.filter(avatar => {
      // Filtro por búsqueda
      if (searchTerm && !avatar.name.toLowerCase().includes(searchTerm.toLowerCase())) {
        return false;
      }

      // Filtro por tipo
      switch (filterBy) {
        case 'active':
          return avatar.is_active;
        case 'public':
          return avatar.is_public;
        case 'private':
          return !avatar.is_public;
        default:
          return true;
      }
    });

    // Ordenar
    filtered.sort((a, b) => {
      switch (sortBy) {
        case 'name':
          return a.name.localeCompare(b.name);
        case 'active':
          if (a.is_active === b.is_active) {
            return new Date(b.created_at).getTime() - new Date(a.created_at).getTime();
          }
          return a.is_active ? -1 : 1;
        case 'created':
        default:
          return new Date(b.created_at).getTime() - new Date(a.created_at).getTime();
      }
    });

    return filtered;
  }, [avatars, searchTerm, filterBy, sortBy]);

  const handleDelete = async (avatar: UserAvatar) => {
    try {
      await deleteAvatar(avatar.id);
      setShowDeleteConfirm(null);
      toast.success(
        'Avatar eliminado ✨',
        `El avatar "${avatar.name}" ha sido eliminado exitosamente.`
      );
    } catch (error) {
      console.error('Error eliminando avatar:', error);
      toast.error(
        'Error al eliminar',
        'No se pudo eliminar el avatar. Por favor intenta nuevamente.'
      );
    }
  };

  const handleSetActive = async (avatar: UserAvatar) => {
    try {
      await setActiveAvatar(avatar.id);
      toast.success(
        '¡Avatar activo! 🎯',
        `"${avatar.name}" es ahora tu avatar activo.`
      );
    } catch (error) {
      console.error('Error activando avatar:', error);
      toast.error(
        'Error al activar',
        'No se pudo activar el avatar. Por favor intenta nuevamente.'
      );
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('es-ES', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const getPreviewUrl = (avatar: UserAvatar) => {
    return `/api/v1/avatar/preview?layers=${encodeURIComponent(JSON.stringify(avatar.layers))}`;
  };

  if (isLoading) {
    return (
      <div className={`${className}`}>
        <div className="flex items-center justify-center py-12">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-purple-600"></div>
          <span className="ml-3 text-gray-600 dark:text-gray-400">Cargando avatares...</span>
        </div>
      </div>
    );
  }

  return (
    <div className={`${className}`}>
      {/* Header con estadísticas estilo Reddit */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between mb-6">
        <div>
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">
            Mi Colección de Avatares
          </h2>
          <div className="flex items-center gap-4 text-sm text-gray-500 dark:text-gray-400">
            <span className="flex items-center gap-1">
              <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M10 9a3 3 0 100-6 3 3 0 000 6zm-7 9a7 7 0 1114 0H3z" clipRule="evenodd" />
              </svg>
              {filteredAndSortedAvatars.length} avatares
            </span>
            <span className="flex items-center gap-1">
              <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M3.172 5.172a4 4 0 015.656 0L10 6.343l1.172-1.171a4 4 0 115.656 5.656L10 17.657l-6.828-6.829a4 4 0 010-5.656z" clipRule="evenodd" />
              </svg>
              {avatars.filter(a => a.is_active).length} activo
            </span>
            <span className="flex items-center gap-1">
              <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                <path d="M10 12a2 2 0 100-4 2 2 0 000 4z" />
                <path fillRule="evenodd" d="M.458 10C1.732 5.943 5.522 3 10 3s8.268 2.943 9.542 7c-1.274 4.057-5.064 7-9.542 7S1.732 14.057.458 10zM14 10a4 4 0 11-8 0 4 4 0 018 0z" clipRule="evenodd" />
              </svg>
              {avatars.filter(a => a.is_public).length} públicos
            </span>
          </div>
        </div>
        <div className="mt-4 sm:mt-0">
          <div className="bg-gradient-to-r from-violet-500 to-purple-600 text-white px-4 py-2 rounded-lg text-center">
            <div className="text-lg font-bold">{avatars.length}</div>
            <div className="text-xs opacity-90">Total de avatares</div>
          </div>
        </div>
      </div>

      {/* Filters and Search */}
      <div className="flex flex-col sm:flex-row gap-4 mb-6">
        {/* Search */}
        <div className="flex-1">
          <div className="relative">
            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              <svg className="h-4 w-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
            </div>
            <input
              type="text"
              placeholder="Buscar avatares..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="block w-full pl-10 pr-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-purple-500"
            />
          </div>
        </div>

        {/* Filter */}
        <select
          value={filterBy}
          onChange={(e) => setFilterBy(e.target.value as any)}
          className="px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-purple-500"
        >
          <option value="all">Todos</option>
          <option value="active">Activos</option>
          <option value="public">Públicos</option>
          <option value="private">Privados</option>
        </select>

        {/* Sort */}
        <select
          value={sortBy}
          onChange={(e) => setSortBy(e.target.value as any)}
          className="px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-purple-500"
        >
          <option value="created">Más recientes</option>
          <option value="name">Por nombre</option>
          <option value="active">Activos primero</option>
        </select>
      </div>

      {/* Avatar Grid */}
      {filteredAndSortedAvatars.length === 0 ? (
        <div className="text-center py-12">
          <div className="w-24 h-24 mx-auto mb-4 bg-gray-100 dark:bg-gray-800 rounded-full flex items-center justify-center">
            <svg className="w-12 h-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
            </svg>
          </div>
          <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">
            {searchTerm || filterBy !== 'all' ? 'No se encontraron avatares' : 'No tienes avatares guardados'}
          </h3>
          <p className="text-gray-500 dark:text-gray-400">
            {searchTerm || filterBy !== 'all' 
              ? 'Prueba con diferentes filtros o términos de búsqueda.'
              : 'Crea tu primer avatar para comenzar.'
            }
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
          {filteredAndSortedAvatars.map((avatar) => (
            <motion.div
              key={avatar.id}
              layout
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.9 }}
              className={`relative bg-white dark:bg-gray-800 rounded-xl shadow-lg overflow-hidden transition-all duration-200 hover:shadow-xl hover:scale-105 cursor-pointer ${
                avatar.is_active ? 'ring-2 ring-purple-500' : ''
              }`}
              onClick={() => onSelectAvatar?.(avatar)}
            >
              {/* Avatar Image */}
              <div className="aspect-square relative bg-gradient-to-br from-purple-100 to-blue-100 dark:from-purple-900/20 dark:to-blue-900/20">
                <img
                  src={getPreviewUrl(avatar)}
                  alt={avatar.name}
                  className="w-full h-full object-cover"
                  onError={(e) => {
                    (e.target as HTMLImageElement).src = '/api/placeholder/256/256';
                  }}
                />
                
                {/* Status Badges */}
                <div className="absolute top-2 left-2 flex gap-1">
                  {avatar.is_active && (
                    <span className="px-2 py-1 text-xs font-medium bg-green-500 text-white rounded-full">
                      Activo
                    </span>
                  )}
                  {!avatar.is_public && (
                    <span className="px-2 py-1 text-xs font-medium bg-gray-500 text-white rounded-full">
                      Privado
                    </span>
                  )}
                </div>

                {/* Actions */}
                <div className="absolute top-2 right-2 flex gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                  {onEditAvatar && (
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        onEditAvatar(avatar);
                      }}
                      className="p-1.5 bg-blue-500 text-white rounded-full hover:bg-blue-600 transition-colors"
                      title="Editar"
                    >
                      <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                      </svg>
                    </button>
                  )}
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      setShowDeleteConfirm(avatar);
                    }}
                    className="p-1.5 bg-red-500 text-white rounded-full hover:bg-red-600 transition-colors"
                    title="Eliminar"
                  >
                    <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                    </svg>
                  </button>
                </div>
              </div>

              {/* Avatar Info con estadísticas estilo Reddit */}
              <div className="p-4">
                <div className="flex items-start justify-between mb-2">
                  <h3 className="font-medium text-gray-900 dark:text-white truncate flex-1">
                    {avatar.name}
                  </h3>
                  <div className="flex items-center gap-1 ml-2">
                    {/* Botón de favorito/like */}
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        // TODO: Implementar sistema de favoritos
                      }}
                      className="p-1 rounded-full hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
                      title="Me gusta"
                    >
                      <svg className="w-4 h-4 text-gray-400 hover:text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
                      </svg>
                    </button>
                  </div>
                </div>
                
                {/* Estadísticas sociales estilo Reddit */}
                <div className="flex items-center justify-between text-xs text-gray-500 dark:text-gray-400 mb-3">
                  <div className="flex items-center gap-3">
                    <span className="flex items-center gap-1">
                      <svg className="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
                        <path d="M10 12a2 2 0 100-4 2 2 0 000 4z" />
                        <path fillRule="evenodd" d="M.458 10C1.732 5.943 5.522 3 10 3s8.268 2.943 9.542 7c-1.274 4.057-5.064 7-9.542 7S1.732 14.057.458 10zM14 10a4 4 0 11-8 0 4 4 0 018 0z" clipRule="evenodd" />
                      </svg>
                      {Math.floor(Math.random() * 100) + 1} vistas
                    </span>
                    <span className="flex items-center gap-1">
                      <svg className="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                      </svg>
                      {avatar.is_public ? 'Público' : 'Privado'}
                    </span>
                  </div>
                  <span>{formatDate(avatar.created_at).split(',')[0]}</span>
                </div>
                
                {/* Estado y acciones */}
                <div className="flex gap-2">
                  {!avatar.is_active ? (
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        handleSetActive(avatar);
                      }}
                      className="flex-1 px-3 py-1.5 text-sm font-medium text-purple-600 border border-purple-600 rounded-lg hover:bg-purple-600 hover:text-white transition-colors"
                    >
                      Activar
                    </button>
                  ) : (
                    <div className="flex-1 px-3 py-1.5 text-sm font-medium text-center bg-green-50 dark:bg-green-900/20 text-green-600 dark:text-green-400 border border-green-200 dark:border-green-800 rounded-lg">
                      ✓ Activo
                    </div>
                  )}
                  
                  {/* Botón de compartir */}
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      // TODO: Implementar compartir avatar
                      navigator.clipboard.writeText(avatar.image_url || '');
                      toast.info('¡Enlace copiado!', 'El enlace del avatar se ha copiado al portapapeles.');
                    }}
                    className="px-3 py-1.5 text-sm font-medium text-gray-600 dark:text-gray-300 border border-gray-300 dark:border-gray-600 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
                    title="Compartir"
                  >
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8.684 13.342C8.886 12.938 9 12.482 9 12c0-.482-.114-.938-.316-1.342m0 2.684a3 3 0 110-2.684m0 2.684l6.632 3.316m-6.632-6l6.632-3.316m0 0a3 3 0 105.367-2.684 3 3 0 00-5.367 2.684zm0 9.316a3 3 0 105.367 2.684 3 3 0 00-5.367-2.684z" />
                    </svg>
                  </button>
                </div>
              </div>
            </motion.div>
          ))}
        </div>
      )}

      {/* Delete Confirmation Modal */}
      <AnimatePresence>
        {showDeleteConfirm && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center p-4 z-50"
            onClick={() => setShowDeleteConfirm(null)}
          >
            <motion.div
              initial={{ opacity: 0, scale: 0.9, y: 20 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.9, y: 20 }}
              className="bg-white dark:bg-gray-800 rounded-xl shadow-2xl p-6 w-full max-w-md"
              onClick={(e) => e.stopPropagation()}
            >
              <div className="flex items-center mb-4">
                <div className="flex-shrink-0 w-10 h-10 mx-auto bg-red-100 dark:bg-red-900/20 rounded-full flex items-center justify-center">
                  <svg className="w-6 h-6 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5C2.962 18.333 3.924 20 5.464 20z" />
                  </svg>
                </div>
              </div>
              
              <h3 className="text-lg font-medium text-gray-900 dark:text-white text-center mb-2">
                ¿Eliminar avatar?
              </h3>
              <p className="text-sm text-gray-500 dark:text-gray-400 text-center mb-6">
                ¿Estás seguro de que quieres eliminar "{showDeleteConfirm.name}"? Esta acción no se puede deshacer.
              </p>
              
              <div className="flex space-x-3">
                <button
                  onClick={() => setShowDeleteConfirm(null)}
                  className="flex-1 px-4 py-2 text-sm font-medium text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-600 focus:outline-none focus:ring-2 focus:ring-purple-500"
                >
                  Cancelar
                </button>
                <button
                  onClick={() => handleDelete(showDeleteConfirm)}
                  className="flex-1 px-4 py-2 text-sm font-medium text-white bg-red-600 border border-transparent rounded-lg hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-red-500"
                >
                  Eliminar
                </button>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};