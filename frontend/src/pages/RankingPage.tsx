export default function RankingPage() {
  // Mock de ranking
  const ranking = [
    { id: 1, nombre: 'Esteban', puntos: 1200 },
    { id: 2, nombre: 'Ana', puntos: 1100 },
    { id: 3, nombre: 'Carlos', puntos: 950 },
  ];
  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-gray-50 dark:bg-[#18181b] p-8">
      <div className="w-full max-w-2xl bg-white dark:bg-zinc-900 rounded-xl shadow p-8 border border-gray-200 dark:border-gray-700">
        <h2 className="text-xl font-bold text-primary mb-6">Ranking global</h2>
        <ul className="flex flex-col gap-4">
          {ranking.map((r, idx) => (
            <li key={r.id} className="p-4 rounded bg-gray-100 dark:bg-zinc-800 flex items-center gap-4">
              <span className="font-bold text-2xl w-8 text-center">#{idx + 1}</span>
              <span className="font-semibold text-lg">{r.nombre}</span>
              <span className="ml-auto text-primary font-bold">{r.puntos} pts</span>
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}
