export default function ClaseMaterialesPage() {
  // Mock de materiales
  const materiales = [
    { id: 1, nombre: 'Guía de ejercicios', tipo: 'PDF', url: '#' },
    { id: 2, nombre: 'Video explicativo', tipo: 'Video', url: '#' },
  ];
  return (
    <div>
      <h3 className="text-lg font-bold text-primary mb-4">Materiales</h3>
      <ul className="flex flex-col gap-4">
        {materiales.map(m => (
          <li key={m.id} className="p-4 rounded bg-gray-100 dark:bg-zinc-800 flex justify-between items-center">
            <div>
              <div className="font-semibold text-primary">{m.nombre}</div>
              <div className="text-xs text-gray-400">{m.tipo}</div>
            </div>
            <a href={m.url} className="px-3 py-1 rounded bg-primary text-white text-xs font-semibold hover:bg-primary/90 transition-colors" target="_blank" rel="noopener noreferrer">Ver</a>
          </li>
        ))}
      </ul>
    </div>
  );
}
