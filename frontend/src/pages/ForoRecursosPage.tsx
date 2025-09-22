export default function ForoRecursosPage() {
  // Mock de foro y recursos
  const preguntas = [
    { id: 1, autor: 'Esteban', pregunta: '¿Cómo empiezo con React?', fecha: '2025-09-10' },
    { id: 2, autor: 'Ana', pregunta: '¿Recomiendan algún recurso de UI/UX?', fecha: '2025-09-12' },
  ];
  const recursos = [
    { id: 1, nombre: 'Guía de React', tipo: 'PDF' },
    { id: 2, nombre: 'Curso UI/UX', tipo: 'Video' },
  ];
  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-gray-50 dark:bg-[#18181b] p-8">
      <div className="w-full max-w-3xl bg-white dark:bg-zinc-900 rounded-xl shadow p-8 border border-gray-200 dark:border-gray-700">
        <h2 className="text-xl font-bold text-primary mb-6">Foro y recursos</h2>
        <div className="mb-8">
          <h3 className="text-lg font-bold text-primary mb-2">Foro</h3>
          <ul className="flex flex-col gap-2">
            {preguntas.map(p => (
              <li key={p.id} className="p-3 rounded bg-gray-100 dark:bg-zinc-800">
                <span className="font-semibold">{p.autor}:</span> {p.pregunta}
                <span className="block text-xs text-gray-400">{p.fecha}</span>
              </li>
            ))}
          </ul>
        </div>
        <div>
          <h3 className="text-lg font-bold text-primary mb-2">Recursos</h3>
          <ul className="flex flex-col gap-2">
            {recursos.map(r => (
              <li key={r.id} className="p-3 rounded bg-blue-100 dark:bg-blue-900 flex items-center justify-between">
                <span>{r.nombre}</span>
                <span className="text-blue-700 font-bold">{r.tipo}</span>
                <button className="ml-4 px-3 py-1 rounded bg-primary text-white text-sm font-semibold hover:bg-primary/90 transition-colors">Ver</button>
              </li>
            ))}
          </ul>
        </div>
      </div>
    </div>
  );
}
