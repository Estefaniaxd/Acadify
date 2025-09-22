import { useNavigate } from 'react-router-dom';

export default function AjustesPage({ theme, setTheme }: { theme: 'light' | 'dark', setTheme: (t: 'light' | 'dark') => void }) {
  const navigate = useNavigate();
  return (
    <div className="min-h-screen bg-gray-50 dark:bg-[#18181b] flex flex-col">
      <header className="flex items-center gap-2 px-8 py-4 border-b border-gray-200 dark:border-gray-700 bg-white dark:bg-[#18181b]">
        <button onClick={() => navigate(-1)} className="text-2xl text-gray-500 hover:text-primary">←</button>
        <span className="text-xl font-bold text-primary">Ajustes</span>
      </header>
      <main className="flex-1 flex flex-col items-center justify-center p-8">
        <div className="w-full max-w-lg bg-white dark:bg-zinc-900 rounded-xl shadow p-8 border border-gray-200 dark:border-gray-700 flex flex-col gap-8">
          <div>
            <span className="block text-lg font-bold mb-2 text-primary">Tema</span>
            <div className="flex gap-4">
              <button
                className={`px-4 py-2 rounded ${theme === 'light' ? 'bg-primary text-white' : 'bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-200'}`}
                onClick={() => setTheme('light')}
              >
                Claro
              </button>
              <button
                className={`px-4 py-2 rounded ${theme === 'dark' ? 'bg-primary text-white' : 'bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-200'}`}
                onClick={() => setTheme('dark')}
              >
                Oscuro
              </button>
            </div>
          </div>
          <div>
            <span className="block text-lg font-bold mb-2 text-primary">Idioma</span>
            <select className="w-full px-4 py-2 rounded border border-gray-300 dark:border-gray-700 bg-gray-50 dark:bg-zinc-800">
              <option>Español</option>
              <option>Inglés</option>
            </select>
          </div>
          <div>
            <span className="block text-lg font-bold mb-2 text-primary">Notificaciones</span>
            <label className="flex items-center gap-2">
              <input type="checkbox" className="form-checkbox" />
              Recibir notificaciones por email
            </label>
          </div>
        </div>
      </main>
    </div>
  );
}
