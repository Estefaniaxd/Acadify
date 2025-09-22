export default function ActividadGamificadaPage() {
  // Mock de feed gamificado
  const feed = [
    { id: 1, tipo: 'logro', mensaje: 'Obtuviste el logro "Colaborador"', fecha: '2025-09-10' },
    { id: 2, tipo: 'reto', mensaje: 'Completaste el reto diario', fecha: '2025-09-11' },
    { id: 3, tipo: 'insignia', mensaje: 'Conseguiste la insignia "Maestro"', fecha: '2025-09-12' },
  ];
  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-gray-50 dark:bg-[#18181b] p-8">
      <div className="w-full max-w-2xl bg-white dark:bg-zinc-900 rounded-xl shadow p-8 border border-gray-200 dark:border-gray-700">
        <h2 className="text-xl font-bold text-primary mb-6">Actividad gamificada</h2>
        <ul className="flex flex-col gap-4">
          {feed.map(f => (
            <li key={f.id} className="p-4 rounded bg-gray-100 dark:bg-zinc-800 flex flex-col gap-1">
              <span className="font-semibold text-base">{f.mensaje}</span>
              <span className="text-xs text-gray-400">{f.fecha}</span>
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}
