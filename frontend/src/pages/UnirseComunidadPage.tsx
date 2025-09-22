import { useState } from 'react';

export default function UnirseComunidadPage() {
  const [correo, setCorreo] = useState('');
  const [mensaje, setMensaje] = useState('');
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setMensaje('¡Solicitud enviada! Pronto recibirás una invitación si el correo es válido.');
    setCorreo('');
  };
  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-gray-50 dark:bg-[#18181b] p-8">
      <div className="w-full max-w-md bg-white dark:bg-zinc-900 rounded-xl shadow p-8 border border-gray-200 dark:border-gray-700 flex flex-col gap-6">
        <h2 className="text-xl font-bold text-primary mb-4">Unirse a una comunidad</h2>
        <form onSubmit={handleSubmit} className="flex flex-col gap-4">
          <input
            type="email"
            required
            placeholder="Correo institucional o invitación"
            className="px-4 py-2 rounded border border-gray-300 dark:border-gray-700 bg-gray-50 dark:bg-zinc-800"
            value={correo}
            onChange={e => setCorreo(e.target.value)}
          />
          <button type="submit" className="px-6 py-2 rounded bg-primary text-white font-semibold hover:bg-primary/90 transition-colors">Unirse</button>
        </form>
        {mensaje && <div className="text-green-600 text-sm text-center">{mensaje}</div>}
      </div>
    </div>
  );
}
