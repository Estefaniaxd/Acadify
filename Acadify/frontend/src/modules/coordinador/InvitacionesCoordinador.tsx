import { useState } from 'react';

// Componente para aceptar invitaciones a instituciones
export default function InvitacionesCoordinador({ invitaciones, onAceptar }: { invitaciones: { id: number, institucion: string }[], onAceptar: (id: number) => void }) {
  const [aceptadas, setAceptadas] = useState<number[]>([]);

  const aceptar = (id: number) => {
    onAceptar(id);
    setAceptadas([...aceptadas, id]);
  };

  return (
    <section className="mb-8">
      <h2 className="text-xl font-bold mb-2 text-primary">Invitaciones pendientes</h2>
      {invitaciones.length === 0 && <div className="text-gray-500">No tienes invitaciones pendientes.</div>}
      <ul className="list-disc ml-6">
        {invitaciones.map(inv => (
          <li key={inv.id} className="mb-2">
            {inv.institucion}
            {aceptadas.includes(inv.id) ? (
              <span className="ml-2 text-green-600">Aceptada</span>
            ) : (
              <button className="ml-2 px-3 py-1 bg-primary text-white rounded" onClick={() => aceptar(inv.id)}>
                Aceptar invitación
              </button>
            )}
          </li>
        ))}
      </ul>
    </section>
  );
}
