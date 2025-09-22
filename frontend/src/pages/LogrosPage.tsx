import { useNavigate } from 'react-router-dom';

const mockLogros = [
  {
    id: 1,
    name: 'Primer curso',
    description: 'Completaste tu primer curso en Acadify',
    img: 'https://cdn-icons-png.flaticon.com/512/3135/3135715.png',
    date: '2025-08-10',
  },
  {
    id: 2,
    name: 'Participante',
    description: 'Participaste en una comunidad',
    img: 'https://cdn-icons-png.flaticon.com/512/3135/3135789.png',
    date: '2025-08-15',
  },
  {
    id: 3,
    name: 'Comunidad',
    description: 'Te uniste a tu primera comunidad',
    img: 'https://cdn-icons-png.flaticon.com/512/3135/3135768.png',
    date: '2025-09-01',
  },
];

export default function LogrosPage() {
  const navigate = useNavigate();
  return (
    <div className="min-h-screen bg-gray-50 dark:bg-[#18181b] flex flex-col">
      <header className="flex items-center gap-2 px-8 py-4 border-b border-gray-200 dark:border-gray-700 bg-white dark:bg-[#18181b]">
        <button onClick={() => navigate(-1)} className="text-2xl text-gray-500 hover:text-primary">←</button>
        <span className="text-xl font-bold text-primary">Tus logros</span>
      </header>
      <main className="flex-1 flex flex-col items-center justify-center p-8">
        <div className="w-full max-w-2xl grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-8">
          {mockLogros.map(l => (
            <div key={l.id} className="flex flex-col items-center bg-white dark:bg-zinc-900 rounded-xl shadow p-6 border border-gray-200 dark:border-gray-700">
              <img src={l.img} alt={l.name} className="w-20 h-20 rounded-full border-4 border-primary mb-3" />
              <span className="text-lg font-bold text-primary mb-1">{l.name}</span>
              <span className="text-sm text-gray-500 dark:text-gray-300 mb-2 text-center">{l.description}</span>
              <span className="text-xs text-gray-400">Obtenido: {l.date}</span>
            </div>
          ))}
        </div>
      </main>
    </div>
  );
}
