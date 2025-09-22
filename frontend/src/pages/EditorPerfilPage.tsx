import { useAuth } from '../context/AuthContext';

export default function EditorPerfilPage() {
  const { user } = useAuth();
  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-gray-50 dark:bg-[#18181b] p-8">
      <div className="w-full max-w-lg bg-white dark:bg-zinc-900 rounded-xl shadow p-8 border border-gray-200 dark:border-gray-700 flex flex-col items-center gap-6">
        <img src={`https://api.dicebear.com/7.x/bottts/svg?seed=${user?.username || 'user'}`} alt="avatar" className="w-24 h-24 rounded-full border-4 border-primary" />
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
