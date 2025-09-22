export default function GuardadoPage() {
  // Mock de recursos guardados
  const guardados = [
    { id: 1, tipo: 'Curso', nombre: 'React desde cero', fecha: '2025-08-20' },
    { id: 2, tipo: 'Comunidad', nombre: 'Gamers Acadify', fecha: '2025-09-01' },
  ];
  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-gray-50 dark:bg-[#18181b] p-8">
      <div className="w-full max-w-2xl bg-white dark:bg-zinc-900 rounded-xl shadow p-8 border border-gray-200 dark:border-gray-700">
        <h2 className="text-xl font-bold text-primary mb-6">Guardado</h2>
        <ul className="flex flex-col gap-4">
          {guardados.map(g => (
            <li key={g.id} className="p-4 rounded bg-gray-100 dark:bg-zinc-800 flex flex-col gap-1">
              <span className="font-semibold text-lg">{g.nombre}</span>
              <span className="text-xs text-gray-400">{g.tipo} • Guardado: {g.fecha}</span>
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}
