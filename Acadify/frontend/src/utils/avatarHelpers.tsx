// Utilidades para manejar avatares de usuarios
import { avatarAPI } from '../components/avatar/avatarAPI';

/**
 * Obtiene la URL del avatar activo de un usuario
 * @param userId ID del usuario
 * @returns URL del avatar o null si no tiene avatar
 */
export const getUserAvatarUrl = async (userId: string): Promise<string | null> => {
  try {
    const response = await avatarAPI.getUserAvatars(userId, 0, 1);
    
    // Buscar el avatar activo
    const activeAvatar = response.avatars.find(avatar => avatar.is_active);
    
    if (activeAvatar) {
      // Usar la URL de imagen del avatar
      return activeAvatar.image_url || `/api/avatars/preview/${activeAvatar.id}`;
    }
    
    return null;
  } catch (error) {
    console.error('Error obteniendo avatar del usuario:', error);
    return null;
  }
};

/**
 * Genera una URL de avatar por defecto basada en el ID del usuario
 * @param userId ID del usuario
 * @returns URL del avatar por defecto
 */
export const getDefaultAvatarUrl = (userId: string): string => {
  return `/api/avatars/default/${userId}`;
};

/**
 * Componente de avatar que maneja la carga automática
 * @param userId ID del usuario
 * @param nombres Nombres del usuario (para fallback)
 * @param apellidos Apellidos del usuario (para fallback)
 * @param size Tamaño del avatar (opcional)
 * @param className Clases CSS adicionales
 */
export const UserAvatar: React.FC<{
  userId: string;
  nombres: string;
  apellidos: string;
  size?: 'sm' | 'md' | 'lg';
  className?: string;
}> = ({ userId, nombres, apellidos, size = 'md', className = '' }) => {
  const [avatarUrl, setAvatarUrl] = React.useState<string | null>(null);
  const [loading, setLoading] = React.useState(true);
  
  React.useEffect(() => {
    getUserAvatarUrl(userId).then(url => {
      setAvatarUrl(url);
      setLoading(false);
    });
  }, [userId]);
  
  const sizeClasses = {
    sm: 'w-8 h-8 text-xs',
    md: 'w-12 h-12 text-sm',
    lg: 'w-16 h-16 text-base'
  };
  
  const baseClasses = `${sizeClasses[size]} rounded-full object-cover ${className}`;
  
  if (loading) {
    return (
      <div className={`${baseClasses} bg-gray-300 dark:bg-gray-600 animate-pulse`}></div>
    );
  }
  
  if (avatarUrl) {
    return (
      <img
        src={avatarUrl}
        alt={`${nombres} ${apellidos}`}
        className={baseClasses}
        onError={() => setAvatarUrl(null)} // Fallback si la imagen falla
      />
    );
  }
  
  // Fallback con iniciales
  return (
    <div className={`${baseClasses} bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center text-white font-bold`}>
      {nombres.charAt(0)}{apellidos.charAt(0)}
    </div>
  );
};

import React from 'react';