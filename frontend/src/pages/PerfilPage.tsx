import { useAuth } from '../context/AuthContext';

export default function PerfilPage() {
  const { user } = useAuth();
  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-gray-50 dark:bg-[#18181b] p-8">
      <div className="w-full max-w-lg bg-white dark:bg-zinc-900 rounded-xl shadow p-8 border border-gray-200 dark:border-gray-700 flex flex-col items-center gap-6">
        <img src={`https://api.dicebear.com/7.x/bottts/svg?seed=${user?.username || 'user'}`} alt="avatar" className="w-24 h-24 rounded-full border-4 border-primary" />
        <div className="text-center">
          <div className="text-2xl font-bold text-primary mb-1">{user?.username || 'Usuario'}</div>
          <div className="text-sm text-gray-500 dark:text-gray-300 mb-2">{user?.email}</div>
          <div className="text-xs text-gray-400">Rol: {user?.role}</div>
        </div>
        <button className="px-6 py-2 rounded bg-primary text-white font-semibold hover:bg-primary/90 transition-colors">Editar perfil</button>
      </div>
    </div>
  );
}
