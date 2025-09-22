export default function BorradoresPage() {
  // Mock de borradores
  const borradores = [
    { id: 1, titulo: 'Borrador de curso', fecha: '2025-09-10' },
    { id: 2, titulo: 'Idea de comunidad', fecha: '2025-09-15' },
  ];
  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-gray-50 dark:bg-[#18181b] p-8">
      <div className="w-full max-w-2xl bg-white dark:bg-zinc-900 rounded-xl shadow p-8 border border-gray-200 dark:border-gray-700">
        <h2 className="text-xl font-bold text-primary mb-6">Tus borradores</h2>
        <ul className="flex flex-col gap-4">
          {borradores.map(b => (
            <li key={b.id} className="p-4 rounded bg-gray-100 dark:bg-zinc-800 flex flex-col gap-1">
              <span className="font-semibold text-lg">{b.titulo}</span>
              <span className="text-xs text-gray-400">Guardado: {b.fecha}</span>
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}
