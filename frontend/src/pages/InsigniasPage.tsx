import { useNavigate } from 'react-router-dom';

const mockInsignias = [
  {
    id: 1,
    name: 'Colaborador',
    description: 'Ayudaste a otros usuarios en la plataforma',
    icon: '🤝',
    obtained: true,
  },
  {
    id: 2,
    name: 'Explorador',
    description: 'Descubriste nuevas comunidades',
    icon: '🧭',
    obtained: false,
  },
  {
    id: 3,
    name: 'Maestro',
    description: 'Completaste todos los cursos de un área',
    icon: '🎓',
    obtained: false,
  },
];

export default function InsigniasPage() {
  const navigate = useNavigate();
  return (
    <div className="min-h-screen bg-gray-50 dark:bg-[#18181b] flex flex-col">
      <header className="flex items-center gap-2 px-8 py-4 border-b border-gray-200 dark:border-gray-700 bg-white dark:bg-[#18181b]">
        <button onClick={() => navigate(-1)} className="text-2xl text-gray-500 hover:text-primary">←</button>
        <span className="text-xl font-bold text-primary">Tus insignias</span>
      </header>
      <main className="flex-1 flex flex-col items-center justify-center p-8">
        <div className="w-full max-w-2xl grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-8">
          {mockInsignias.map(i => (
            <div key={i.id} className={`flex flex-col items-center rounded-xl shadow p-6 border-2 ${i.obtained ? 'bg-white border-yellow-400 dark:bg-zinc-900' : 'bg-gray-100 border-gray-300 dark:bg-zinc-800'}`}>
              <span className={`text-5xl mb-3 ${i.obtained ? '' : 'opacity-40 grayscale'}`}>{i.icon}</span>
              <span className={`text-lg font-bold mb-1 ${i.obtained ? 'text-yellow-700 dark:text-yellow-300' : 'text-gray-400'}`}>{i.name}</span>
              <span className="text-sm text-gray-500 dark:text-gray-300 mb-2 text-center">{i.description}</span>
              <span className={`text-xs ${i.obtained ? 'text-yellow-600' : 'text-gray-400'}`}>{i.obtained ? 'Obtenida' : 'No obtenida'}</span>
            </div>
          ))}
        </div>
      </main>
    </div>
  );
}
