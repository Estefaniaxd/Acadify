export default function TareaPage() {
  // Mock de tarea
  const tarea = {
    titulo: 'Tarea 1: Ecuaciones',
    descripcion: 'Resuelve los ejercicios de la guía adjunta.',
    fechaEntrega: '2025-09-15',
    estado: 'Pendiente',
    archivos: [
      { nombre: 'Guía de ejercicios.pdf', url: '#' },
    ],
  };
  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-gray-50 dark:bg-[#18181b] p-8">
      <div className="w-full max-w-2xl bg-white dark:bg-zinc-900 rounded-xl shadow p-8 border border-gray-200 dark:border-gray-700 flex flex-col gap-6">
        <h2 className="text-2xl font-bold text-primary">{tarea.titulo}</h2>
        <div className="text-gray-700 dark:text-gray-200">{tarea.descripcion}</div>
        <div className="text-xs text-gray-400">Entrega: {tarea.fechaEntrega}</div>
        <div className="flex gap-2 items-center">
          <span className={`px-2 py-1 rounded text-xs font-semibold ${tarea.estado === 'Pendiente' ? 'bg-yellow-200 text-yellow-800' : 'bg-green-200 text-green-800'}`}>{tarea.estado}</span>
        </div>
        <div>
          <h4 className="font-bold text-primary mb-2">Archivos adjuntos</h4>
          <ul className="flex flex-col gap-2">
            {tarea.archivos.map((a, i) => (
              <li key={i} className="flex items-center gap-2">
                <a href={a.url} className="text-primary underline" target="_blank" rel="noopener noreferrer">{a.nombre}</a>
              </li>
            ))}
          </ul>
        </div>
        <form className="flex flex-col gap-4 mt-4">
          <label className="font-semibold">Subir entrega:</label>
          <input type="file" className="rounded border border-gray-300 dark:border-gray-700 bg-gray-50 dark:bg-zinc-800" />
          <button className="px-6 py-2 rounded bg-primary text-white font-semibold hover:bg-primary/90 transition-colors">Entregar tarea</button>
        </form>
      </div>
    </div>
  );
}
