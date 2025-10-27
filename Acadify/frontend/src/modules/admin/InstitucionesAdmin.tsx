// Gestión de instituciones (mock)
import { useState } from 'react';
import InvitarCoordinador from './InvitarCoordinador';
import { registrarInstitucion } from './api';

// Simulación de instituciones y registro
export default function InstitucionesAdmin() {
  const [instituciones, setInstituciones] = useState([
    { id: 1, nombre: 'Institución A' },
    { id: 2, nombre: 'Institución B' },
  ]);
  const [nueva, setNueva] = useState('');
  const [coordinador, setCoordinador] = useState('');
  const [mensaje, setMensaje] = useState('');

  // Lógica real de registro
  const handleRegistrar = async (nombre: string, email: string) => {
    try {
      const data = await registrarInstitucion(nombre, email);
      setInstituciones([...instituciones, { id: data.id, nombre: data.nombre }]);
      setMensaje(`Institución "${data.nombre}" registrada e invitación enviada a ${email}`);
    } catch (e) {
      setMensaje('Error al registrar institución');
    }
  };

  return (
    <section className="mb-8">
      <h2 className="text-xl font-bold mb-2 text-primary">Instituciones</h2>
      <ul className="list-disc ml-6">
        {instituciones.map(i => (
          <li key={i.id}>{i.nombre} <button className="ml-2 text-xs text-blue-600 underline">Ver</button></li>
        ))}
      </ul>
      <form
        className="flex flex-col gap-2 mt-4 max-w-md"
        onSubmit={e => {
          e.preventDefault();
          if (nueva && coordinador) handleRegistrar(nueva, coordinador);
        }}
      >
        <input
          type="text"
          required
          value={nueva}
          onChange={e => setNueva(e.target.value)}
          placeholder="Nombre de la nueva institución"
          className="px-3 py-1 rounded border border-gray-300 dark:border-gray-700 bg-gray-50 dark:bg-zinc-800"
        />
        <input
          type="email"
          required
          value={coordinador}
          onChange={e => setCoordinador(e.target.value)}
          placeholder="Correo del coordinador"
          className="px-3 py-1 rounded border border-gray-300 dark:border-gray-700 bg-gray-50 dark:bg-zinc-800"
        />
        <button type="submit" className="px-4 py-1 bg-primary text-white rounded">Registrar e invitar coordinador</button>
      </form>
      {mensaje && <div className="text-green-600 mt-2">{mensaje}</div>}
    </section>
  );
}
