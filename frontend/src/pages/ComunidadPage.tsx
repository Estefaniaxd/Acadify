export default function ComunidadPage() {
  // Mock de comunidad individual
  const comunidad = {
    nombre: 'Gamers Acadify',
    descripcion: 'Comunidad para gamers y entusiastas de la tecnología.',
    miembros: 120,
    publicaciones: [
      { id: 1, autor: 'Esteban', contenido: '¡Bienvenidos a la comunidad!', fecha: '2025-09-01' },
      { id: 2, autor: 'Ana', contenido: '¿Alguien para jugar esta noche?', fecha: '2025-09-10' },
    ],
  };
  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-gray-50 dark:bg-[#18181b] p-8">
      <div className="w-full max-w-3xl bg-white dark:bg-zinc-900 rounded-xl shadow p-8 border border-gray-200 dark:border-gray-700">
        <h2 className="text-2xl font-bold text-primary mb-2">{comunidad.nombre}</h2>
        <div className="text-gray-500 dark:text-gray-300 mb-4">{comunidad.descripcion}</div>
        <div className="mb-6 text-xs text-gray-400">{comunidad.miembros} miembros</div>
        <h3 className="text-lg font-bold text-primary mb-2">Publicaciones</h3>
        <ul className="flex flex-col gap-4 mb-6">
          {comunidad.publicaciones.map(p => (
            <li key={p.id} className="p-4 rounded bg-gray-100 dark:bg-zinc-800">
              <div className="font-semibold text-primary">{p.autor}</div>
              <div className="text-sm mb-1">{p.contenido}</div>
              <div className="text-xs text-gray-400">{p.fecha}</div>
            </li>
          ))}
        </ul>
        <button className="px-6 py-2 rounded bg-primary text-white font-semibold hover:bg-primary/90 transition-colors">Unirse al chat</button>
      </div>
    </div>
  );
}
