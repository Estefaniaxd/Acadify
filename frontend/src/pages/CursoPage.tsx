export default function CursoPage() {
  // Mock de curso
  const curso = {
    nombre: 'React desde cero',
    descripcion: 'Aprende React desde lo más básico hasta crear aplicaciones modernas.',
    progreso: 40,
    lecciones: [
      { id: 1, titulo: 'Introducción a React', completada: true },
      { id: 2, titulo: 'Componentes y props', completada: true },
      { id: 3, titulo: 'Estado y eventos', completada: false },
    ],
  };
  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-gray-50 dark:bg-[#18181b] p-8">
      <div className="w-full max-w-3xl bg-white dark:bg-zinc-900 rounded-xl shadow p-8 border border-gray-200 dark:border-gray-700">
        <h2 className="text-2xl font-bold text-primary mb-2">{curso.nombre}</h2>
        <div className="text-gray-500 dark:text-gray-300 mb-4">{curso.descripcion}</div>
        <div className="mb-6">
          <span className="text-sm font-semibold text-green-600">Progreso: {curso.progreso}%</span>
          <div className="w-full h-3 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden mt-1">
            <div className="h-3 bg-gradient-to-r from-green-400 to-primary" style={{ width: curso.progreso + '%' }}></div>
          </div>
        </div>
        <h3 className="text-lg font-bold text-primary mb-2">Lecciones</h3>
        <ul className="flex flex-col gap-2">
          {curso.lecciones.map(l => (
            <li key={l.id} className={`p-3 rounded ${l.completada ? 'bg-green-100 dark:bg-green-900' : 'bg-gray-100 dark:bg-zinc-800'}`}>{l.titulo}</li>
          ))}
        </ul>
      </div>
    </div>
  );
}
