export default function HistoriaPage() {
  // Mock de historial
  const historia = [
    { id: 1, accion: 'Completaste el curso "React desde cero"', fecha: '2025-08-25' },
    { id: 2, accion: 'Te uniste a la comunidad "Gamers Acadify"', fecha: '2025-09-02' },
    { id: 3, accion: 'Obtuviste la insignia "Colaborador"', fecha: '2025-09-10' },
  ];
  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-gray-50 dark:bg-[#18181b] p-8">
      <div className="w-full max-w-2xl bg-white dark:bg-zinc-900 rounded-xl shadow p-8 border border-gray-200 dark:border-gray-700">
        <h2 className="text-xl font-bold text-primary mb-6">Historial de actividad</h2>
        <ul className="flex flex-col gap-4">
          {historia.map(h => (
            <li key={h.id} className="p-4 rounded bg-gray-100 dark:bg-zinc-800 flex flex-col gap-1">
              <span className="font-semibold text-base">{h.accion}</span>
              <span className="text-xs text-gray-400">{h.fecha}</span>
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}
