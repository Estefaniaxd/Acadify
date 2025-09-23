import React, { useState, useEffect } from 'react';
import { useAuth } from '../../context/AuthContext';
import { avatarAPI } from '../avatar/avatarAPI';

interface UserAvatarButtonProps {
  onClick: () => void;
}

export default function UserAvatarButton({ onClick }: UserAvatarButtonProps) {
  const { user } = useAuth();
  const [avatarUrl, setAvatarUrl] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadUserAvatar = async () => {
      if (!user) {
        setLoading(false);
        return;
      }

      // Verificar si hay token de autenticación
      const token = localStorage.getItem('access_token');
      if (!token) {
        console.log('UserAvatarButton: No auth token found, using fallback avatar');
        setAvatarUrl(`https://api.dicebear.com/7.x/bottts/svg?seed=${user.username || 'user'}`);
        setLoading(false);
        return;
      }

      try {
        const avatars = await avatarAPI.getMyAvatars();
        const activeAvatar = avatars.avatars.find(avatar => avatar.is_active);
        
        if (activeAvatar && activeAvatar.image_url) {
          setAvatarUrl(activeAvatar.image_url);
        } else {
          // Fallback a dicebear si no hay avatar activo
          setAvatarUrl(`https://api.dicebear.com/7.x/bottts/svg?seed=${user.username || 'user'}`);
        }
      } catch (error) {
        console.error('Error loading user avatar:', error);
        // Fallback a dicebear en caso de error
        setAvatarUrl(`https://api.dicebear.com/7.x/bottts/svg?seed=${user?.username || 'user'}`);
      } finally {
        setLoading(false);
      }
    };

    loadUserAvatar();
  }, [user]);

  const fallbackUrl = `https://api.dicebear.com/7.x/bottts/svg?seed=${user?.username || 'acadify'}`;

  return (
    <button
      className="fixed top-4 right-4 z-50 p-1 rounded-full border-2 border-primary bg-white dark:bg-[#18181b] shadow hover:scale-105 transition-transform"
      aria-label="Abrir perfil"
      onClick={onClick}
      disabled={loading}
    >
      {loading ? (
        <div className="w-10 h-10 rounded-full bg-gray-200 dark:bg-gray-700 animate-pulse" />
      ) : (
        <img
          src={avatarUrl || fallbackUrl}
          alt="avatar"
          className="w-10 h-10 rounded-full"
          onError={(e) => {
            // Si falla cargar el avatar del sistema, usar fallback
            e.currentTarget.src = fallbackUrl;
          }}
        />
      )}
    </button>
  );
}
