export default function NotificacionesPage() {
  // Mock de notificaciones
  const notificaciones = [
    { id: 1, tipo: 'logro', mensaje: '¡Obtuviste el logro "Participante"!', fecha: '2025-09-10' },
    { id: 2, tipo: 'mensaje', mensaje: 'Tienes un nuevo mensaje de Ana.', fecha: '2025-09-12' },
    { id: 3, tipo: 'invitacion', mensaje: 'Fuiste invitado a la comunidad "Frontend Masters".', fecha: '2025-09-15' },
  ];
  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-gray-50 dark:bg-[#18181b] p-8">
      <div className="w-full max-w-2xl bg-white dark:bg-zinc-900 rounded-xl shadow p-8 border border-gray-200 dark:border-gray-700">
        <h2 className="text-xl font-bold text-primary mb-6">Notificaciones</h2>
        <ul className="flex flex-col gap-4">
          {notificaciones.map(n => (
            <li key={n.id} className="p-4 rounded bg-gray-100 dark:bg-zinc-800 flex flex-col gap-1">
              <span className="font-semibold text-base">{n.mensaje}</span>
              <span className="text-xs text-gray-400">{n.fecha}</span>
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}
