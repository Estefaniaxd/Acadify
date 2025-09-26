
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
        setAvatarUrl(null);
        setLoading(false);
        return;
      }
      try {
        const res = await avatarAPI.getMyAvatars(0, 10);
        let avatarUrl = null;
        if (res && res.avatars && res.avatars.length > 0) {
          // Try to find the active avatar
          let active = res.avatars.find(a => a.is_active);
          if (!active && res.active_avatar_id) {
            active = res.avatars.find(a => a.id === res.active_avatar_id);
          }
          if (!active) {
            // fallback to first avatar
            active = res.avatars[0];
          }
          if (active && active.image_url) {
            avatarUrl = active.image_url;
          }
        }
        setAvatarUrl(avatarUrl);
      } catch (err) {
        setAvatarUrl(null);
      } finally {
        setLoading(false);
      }
    };
    loadUserAvatar();
  }, [user]);

  const fallbackUrl = `https://api.dicebear.com/7.x/bottts/svg?seed=${user?.username || 'acadify'}`;

  return (
    <button
      className="fixed top-4 right-5 z-50 p-1 rounded-full border-2 border-primary bg-white dark:bg-[#18181b] shadow-lg hover:scale-105 transition-transform overflow-hidden"
      aria-label="Abrir perfil"
      style={{
        width: '56px',
        height: '56px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        overflow: 'hidden',
      }}
      onClick={onClick}
      disabled={loading}
    >
      {loading ? (
        <div className="w-14 h-14 rounded-full bg-gray-200 dark:bg-gray-700 animate-pulse flex items-center justify-center">
          <div className="w-5 h-5 border-2 border-primary border-t-transparent rounded-full animate-spin"></div>
        </div>
      ) : (
        <img
          src={avatarUrl || fallbackUrl}
          alt="avatar"
          className="rounded-full object-cover"
          style={{
            width: '130px',
            height: '130px',
            marginTop: '50px', // sube al máximo la imagen para mostrar solo la parte superior
            objectPosition: 'center 100%', // enfoca la parte más alta posible
            clipPath: 'circle(50% at 50% 40%)',
            transition: 'width 0.2s, height 0.2s, margin 0.2s',
          }}
          onError={(e) => {
            e.currentTarget.src = fallbackUrl;
          }}
        />
      )}
    </button>
  );
}
