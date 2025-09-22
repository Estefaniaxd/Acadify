import { useNavigate } from 'react-router-dom';

export default function MisClasesPage() {
  const navigate = useNavigate();
  const clases = [
    { id: 1, nombre: 'Matemáticas 2025', profesor: 'Profe Ana', progreso: 60 },
    { id: 2, nombre: 'Historia Universal', profesor: 'Profe Luis', progreso: 80 },
  ];
  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-gray-50 dark:bg-[#18181b] p-8">
      <div className="w-full max-w-5xl mx-auto">
        <div className="flex justify-between items-center mb-8">
          <h2 className="text-2xl font-bold text-primary">Mis clases</h2>
          <div className="flex gap-2">
            <button className="px-4 py-2 rounded bg-primary text-white font-semibold hover:bg-primary/90" onClick={() => navigate('/unirse-clase')}>Unirse a clase</button>
            <button className="px-4 py-2 rounded bg-primary/10 text-primary font-semibold hover:bg-primary/20" onClick={() => navigate('/crear-clase')}>Crear clase</button>
          </div>
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-8">
          {clases.map(c => (
            <div key={c.id} className="bg-white dark:bg-zinc-900 rounded-xl shadow p-6 border border-gray-200 dark:border-gray-700 flex flex-col gap-3 cursor-pointer hover:shadow-lg transition" onClick={() => navigate(`/clase/${c.id}`)}>
              <div className="text-xl font-bold text-primary mb-1">{c.nombre}</div>
              <div className="text-sm text-gray-500 dark:text-gray-300 mb-2">{c.profesor}</div>
              <div className="w-full h-2 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden mb-2">
                <div className="h-2 bg-gradient-to-r from-green-400 to-primary" style={{ width: c.progreso + '%' }}></div>
              </div>
              <div className="text-xs text-gray-400">Progreso: {c.progreso}%</div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
