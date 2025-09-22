export default function ComunidadesPage() {
  // Mock de comunidades
  const comunidades = [
    { id: 1, nombre: 'Gamers Acadify', miembros: 120 },
    { id: 2, nombre: 'Frontend Masters', miembros: 80 },
    { id: 3, nombre: 'Científicos de Datos', miembros: 60 },
  ];
  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-gray-50 dark:bg-[#18181b] p-8">
      <div className="w-full max-w-3xl bg-white dark:bg-zinc-900 rounded-xl shadow p-8 border border-gray-200 dark:border-gray-700">
        <h2 className="text-xl font-bold text-primary mb-6">Explora comunidades</h2>
        <ul className="flex flex-col gap-4">
          {comunidades.map(c => (
            <li key={c.id} className="p-4 rounded bg-gray-100 dark:bg-zinc-800 flex items-center justify-between">
              <span className="font-semibold text-lg">{c.nombre}</span>
              <span className="text-xs text-gray-400">{c.miembros} miembros</span>
              <button className="ml-4 px-4 py-1 rounded bg-primary text-white text-sm font-semibold hover:bg-primary/90 transition-colors">Unirse</button>
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}
