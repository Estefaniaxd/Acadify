import { useState } from 'react';

// Componente para invitar coordinador a una institución
export default function InvitarCoordinador({ onInvitar }: { onInvitar: (email: string) => void }) {
  const [email, setEmail] = useState('');
  const [enviado, setEnviado] = useState(false);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (email) {
      onInvitar(email);
      setEnviado(true);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="flex gap-2 mt-2">
      <input
        type="email"
        required
        value={email}
        onChange={e => setEmail(e.target.value)}
        placeholder="Correo del coordinador"
        className="px-3 py-1 rounded border border-gray-300 dark:border-gray-700 bg-gray-50 dark:bg-zinc-800"
      />
      <button type="submit" className="px-4 py-1 bg-primary text-white rounded">Invitar</button>
      {enviado && <span className="text-green-600 ml-2">Invitación enviada</span>}
    </form>
  );
}
