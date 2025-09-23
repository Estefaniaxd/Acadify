import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { avatarAPI } from '../components/avatar/avatarAPI';

export default function EditorPerfilPage() {
  const { user } = useAuth();
  const [avatarUrl, setAvatarUrl] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadUserAvatar = async () => {
      if (!user) {
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

  const fallbackUrl = `https://api.dicebear.com/7.x/bottts/svg?seed=${user?.username || 'user'}`;

  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-gray-50 dark:bg-[#18181b] p-8">
      <div className="w-full max-w-lg bg-white dark:bg-zinc-900 rounded-xl shadow p-8 border border-gray-200 dark:border-gray-700 flex flex-col items-center gap-6">
        {loading ? (
          <div className="w-24 h-24 rounded-full bg-gray-200 dark:bg-gray-700 animate-pulse border-4 border-primary" />
        ) : (
          <img 
            src={avatarUrl || fallbackUrl} 
            alt="avatar" 
            className="w-24 h-24 rounded-full border-4 border-primary"
            onError={(e) => {
              e.currentTarget.src = fallbackUrl;
            }}
          />
        )}
        <form className="flex flex-col gap-4 w-full">
          <input className="px-4 py-2 rounded border border-gray-300 dark:border-gray-700 bg-gray-50 dark:bg-zinc-800" placeholder="Nombre de usuario" defaultValue={user?.username} />
          <input className="px-4 py-2 rounded border border-gray-300 dark:border-gray-700 bg-gray-50 dark:bg-zinc-800" placeholder="Correo" defaultValue={user?.email} />
          <input className="px-4 py-2 rounded border border-gray-300 dark:border-gray-700 bg-gray-50 dark:bg-zinc-800" placeholder="Nueva contraseña" type="password" />
          <button className="px-6 py-2 rounded bg-primary text-white font-semibold hover:bg-primary/90 transition-colors">Guardar cambios</button>
        </form>
        <button className="mt-2 px-6 py-2 rounded bg-primary/10 text-primary font-semibold hover:bg-primary/20 transition-colors">Galería de avatares</button>
      </div>
    </div>
  );
}
