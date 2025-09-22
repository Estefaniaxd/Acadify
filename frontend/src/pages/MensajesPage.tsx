export default function MensajesPage() {
  // Mock de mensajes
  const mensajes = [
    { id: 1, de: 'Ana', texto: '¡Hola! ¿Listo para el reto de hoy?', fecha: '2025-09-12' },
    { id: 2, de: 'Carlos', texto: '¿Puedes ayudarme con React?', fecha: '2025-09-13' },
  ];
  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-gray-50 dark:bg-[#18181b] p-8">
      <div className="w-full max-w-2xl bg-white dark:bg-zinc-900 rounded-xl shadow p-8 border border-gray-200 dark:border-gray-700">
        <h2 className="text-xl font-bold text-primary mb-6">Mensajes directos</h2>
        <ul className="flex flex-col gap-4">
          {mensajes.map(m => (
            <li key={m.id} className="p-4 rounded bg-gray-100 dark:bg-zinc-800 flex flex-col gap-1">
              <span className="font-semibold text-base">De: {m.de}</span>
              <span className="text-sm">{m.texto}</span>
              <span className="text-xs text-gray-400">{m.fecha}</span>
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}
