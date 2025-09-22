export default function ChatClasePage() {
  // Mock de chat
  const mensajes = [
    { id: 1, autor: 'Esteban', texto: '¡Hola a todos!', fecha: '2025-09-10' },
    { id: 2, autor: 'Ana', texto: '¿Listos para la clase?', fecha: '2025-09-10' },
  ];
  return (
    <div className="bg-gray-50 dark:bg-zinc-900 rounded-xl p-4 border border-gray-200 dark:border-gray-700">
      <h4 className="font-bold text-primary mb-2">Chat general</h4>
      <div className="flex flex-col gap-2 max-h-48 overflow-y-auto mb-2">
        {mensajes.map(m => (
          <div key={m.id} className="flex flex-col">
            <span className="font-semibold text-primary">{m.autor}</span>
            <span className="text-sm">{m.texto}</span>
            <span className="text-xs text-gray-400">{m.fecha}</span>
          </div>
        ))}
      </div>
      <form className="flex gap-2 mt-2">
        <input className="flex-1 px-3 py-2 rounded border border-gray-300 dark:border-gray-700 bg-white dark:bg-zinc-800" placeholder="Escribe un mensaje..." />
        <button className="px-4 py-2 rounded bg-primary text-white font-semibold hover:bg-primary/90 transition-colors">Enviar</button>
      </form>
    </div>
  );
}
