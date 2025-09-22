export default function CatalogoCursosPage() {
  // Mock de cursos
  const cursos = [
    { id: 1, nombre: 'React desde cero', categoria: 'Frontend', nivel: 'Básico' },
    { id: 2, nombre: 'Python para ciencia de datos', categoria: 'Data Science', nivel: 'Intermedio' },
    { id: 3, nombre: 'UI/UX Design', categoria: 'Diseño', nivel: 'Básico' },
  ];
  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-gray-50 dark:bg-[#18181b] p-8">
      <div className="w-full max-w-4xl bg-white dark:bg-zinc-900 rounded-xl shadow p-8 border border-gray-200 dark:border-gray-700">
        <h2 className="text-xl font-bold text-primary mb-6">Catálogo de cursos</h2>
        <ul className="flex flex-col gap-4">
          {cursos.map(c => (
            <li key={c.id} className="p-4 rounded bg-gray-100 dark:bg-zinc-800 flex flex-col md:flex-row md:items-center md:justify-between gap-2">
              <span className="font-semibold text-lg">{c.nombre}</span>
              <span className="text-xs text-gray-400">{c.categoria} • {c.nivel}</span>
              <button className="px-4 py-1 rounded bg-primary text-white text-sm font-semibold hover:bg-primary/90 transition-colors">Ver curso</button>
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}
