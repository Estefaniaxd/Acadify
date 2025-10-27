import ChatClasePage from './ChatClasePage';

export default function ClaseTablonPage() {
  // Mock de publicaciones
  const publicaciones = [
    { id: 1, autor: 'Profe Ana', contenido: 'Bienvenidos a la clase. ¡Aprovechen los recursos!', fecha: '2025-09-01' },
    { id: 2, autor: 'Esteban', contenido: '¿Cuándo es la próxima tarea?', fecha: '2025-09-10' },
  ];
  return (
    <div className="flex flex-col gap-6">
      <div>
        <h3 className="text-lg font-bold text-primary mb-2">Tablón de anuncios</h3>
        <ul className="flex flex-col gap-3 mb-4">
          {publicaciones.map(p => (
            <li key={p.id} className="p-4 rounded bg-gray-100 dark:bg-zinc-800">
              <div className="font-semibold text-primary">{p.autor}</div>
              <div className="text-sm mb-1">{p.contenido}</div>
              <div className="text-xs text-gray-400">{p.fecha}</div>
            </li>
          ))}
        </ul>
      </div>
      <ChatClasePage />
    </div>
  );
}
